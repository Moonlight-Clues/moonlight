"""Ticket T2 (fuller trials): scripts/build_trials.py, the trial details file.

No network: the ClinicalTrials.gov answer is fixtures/trials_t2/ctgov_batch.response.json
(saved from the live API v2 on 2026-11-26 with the builder's own fields= list)
and the Open Targets rows are fixtures/trials_t2/ot_clinical_report_rows.json
(rows of the 26.09 clinical_report parquet: id, source, diseases).
"""

import copy
import gzip
import hashlib
import importlib.util
import json
import pathlib
import sqlite3
import urllib.parse

import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent
FIXTURES = ROOT / "fixtures" / "trials_t2"


def _load_builder():
    spec = importlib.util.spec_from_file_location("build_trials", ROOT / "scripts" / "build_trials.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


bt = _load_builder()
RESPONSE = json.loads((FIXTURES / "ctgov_batch.response.json").read_text(encoding="utf-8"))
OT_ROWS = json.loads((FIXTURES / "ot_clinical_report_rows.json").read_text(encoding="utf-8"))
VERSION = {"apiVersion": "2.0.5", "dataTimestamp": "2026-11-25T10:00:05"}
IDS = ["NCT00000105", "NCT00000821", "NCT00040625", "NCT00785291", "NCT04280705"]


def _study(nct):
    for study in RESPONSE["studies"]:
        if study["protocolSection"]["identificationModule"]["nctId"] == nct:
            return copy.deepcopy(study)
    raise KeyError(nct)


def _sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


# ------------------------------------------------------------ Open Targets ids

def test_ot_ids_are_clinicaltrials_reports_linked_to_a_disease():
    ids, counts = bt.nct_ids_from_reports(OT_ROWS)
    # nct00000110 has no diseases, nct00000130 only an unmapped one (diseaseId
    # null), the DailyMed row is not a trial. All three are left out.
    assert ids == IDS
    assert counts == {"ot_ctgov_reports": 7, "ot_nct_linked_to_disease": 5,
                      "ot_nct_without_disease": 2}


def test_ot_ids_upper_cased_deduplicated_and_sorted():
    rows = [{"id": "nct2", "source": "ClinicalTrials.gov", "diseases": [{"diseaseId": "D"}]},
            {"id": "NCT1", "source": "ClinicalTrials.gov", "diseases": [{"diseaseId": "D"}]},
            {"id": "nct2", "source": "ClinicalTrials.gov", "diseases": [{"diseaseId": "E"}]}]
    assert bt.nct_ids_from_reports(rows)[0] == ["NCT1", "NCT2"]


def test_ot_ids_saved_in_cache_are_reused_without_parquet(tmp_path, monkeypatch):
    monkeypatch.setattr(bt, "read_ot_parquet", lambda path: OT_ROWS)
    first = bt.ot_ids(tmp_path, pathlib.Path("unused.parquet"))
    monkeypatch.setattr(bt, "read_ot_parquet", lambda path: pytest.fail("parquet read again"))
    assert bt.ot_ids(tmp_path, None) == first
    saved = json.loads((tmp_path / "ot_nct_ids.json").read_text(encoding="utf-8"))
    assert saved["release"] == "26.09"


# --------------------------------------------------------------- the request

def test_batch_url_uses_filter_ids_page_size_and_fields():
    url = bt.batch_url(IDS)
    query = urllib.parse.parse_qs(urllib.parse.urlsplit(url).query)
    assert url.startswith("https://clinicaltrials.gov/api/v2/studies?")
    assert query["filter.ids"] == [",".join(IDS)]
    assert query["pageSize"] == ["1000"]
    assert query["fields"][0].split(",") == list(bt.FIELDS)


def test_batches_of_500_keep_order():
    ids = [f"NCT{n:08d}" for n in range(1201)]
    groups = bt.batches(ids)
    assert [len(g) for g in groups] == [500, 500, 201]
    assert sum(groups, []) == ids


# ------------------------------------------------------------------ parsing

def test_project_keeps_only_t1_fields():
    study = bt.project(_study("NCT04280705"))
    section = study["protocolSection"]
    assert set(section) == {"identificationModule", "statusModule", "designModule",
                            "armsInterventionsModule"}
    assert section["identificationModule"] == {
        "nctId": "NCT04280705", "briefTitle": "Adaptive COVID-19 Treatment Trial (ACTT)"}
    assert section["statusModule"]["overallStatus"] == "COMPLETED"
    assert section["statusModule"]["completionDateStruct"] == {"date": "2020-05-21", "type": "ACTUAL"}
    assert set(section["statusModule"]) <= {"overallStatus", "startDateStruct",
                                            "completionDateStruct", "lastUpdatePostDateStruct"}
    assert section["designModule"] == {"studyType": "INTERVENTIONAL", "phases": ["PHASE3"]}
    arms = section["armsInterventionsModule"]
    assert {"label": "Remdesivir", "type": "EXPERIMENTAL",
            "interventionNames": ["Drug: Remdesivir"]} in arms["armGroups"]
    assert all(set(arm) <= {"label", "type", "interventionNames"} for arm in arms["armGroups"])
    assert all(set(item) <= {"name", "type", "otherNames", "armGroupLabels"}
               for item in arms["interventions"])


def test_project_drops_extra_fields_ctgov_might_send():
    study = _study("NCT04280705")
    section = study["protocolSection"]
    section["statusModule"]["whyStopped"] = "x"
    section["armsInterventionsModule"]["armGroups"][0]["description"] = "long text"
    section["eligibilityModule"] = {"sex": "ALL"}
    section["identificationModule"]["nctIdAliases"] = ["NCT00000001"]
    projected = bt.project(study)["protocolSection"]
    assert "whyStopped" not in projected["statusModule"]
    assert "description" not in projected["armsInterventionsModule"]["armGroups"][0]
    assert "eligibilityModule" not in projected
    assert "nctIdAliases" not in projected["identificationModule"]


def test_project_leaves_missing_modules_missing():
    # NCT00000821 has interventions but no arm groups and no start date.
    section = bt.project(_study("NCT00000821"))["protocolSection"]
    assert "armGroups" not in section["armsInterventionsModule"]
    assert "startDateStruct" not in section["statusModule"]
    bare = {"protocolSection": {"identificationModule": {"nctId": "NCT1"},
                                "designModule": {"studyType": "INTERVENTIONAL"}}}
    assert "armsInterventionsModule" not in bt.project(bare)["protocolSection"]


# ---------------------------------------------------------------- filtering

def test_only_interventional_kept_and_drops_counted():
    rows, counts = bt.sort_rows(IDS + ["NCT00000000"], RESPONSE["studies"])
    assert [nct for nct, _ in rows] == ["NCT00000821", "NCT00785291", "NCT04280705"]
    assert counts == {"requested": 6, "found": 5, "not_found": 1, "found_under_newer_nct": 0,
                      "kept_interventional": 3, "dropped_observational": 1,
                      "dropped_expanded_access": 1, "dropped_other_or_missing_study_type": 0}


def test_missing_study_type_is_dropped():
    study = _study("NCT04280705")
    del study["protocolSection"]["designModule"]["studyType"]
    rows, counts = bt.sort_rows(["NCT04280705"], [study])
    assert rows == [] and counts["dropped_other_or_missing_study_type"] == 1


def test_study_found_under_newer_number_is_kept_under_open_targets_number():
    study = _study("NCT04280705")
    study["protocolSection"]["identificationModule"]["nctIdAliases"] = ["NCT00000001"]
    rows, counts = bt.sort_rows(["NCT00000001"], [study])
    assert [nct for nct, _ in rows] == ["NCT00000001"]
    assert rows[0][1]["protocolSection"]["identificationModule"]["nctId"] == "NCT04280705"
    assert counts["found_under_newer_nct"] == 1 and counts["not_found"] == 0


# ------------------------------------------------------------- the file

def _build(tmp_path, name="trials.sqlite", run_date="2026-11-26", studies=None):
    out = tmp_path / name
    ids, ot_counts = bt.nct_ids_from_reports(OT_ROWS)
    meta = bt.build(ids, ot_counts, RESPONSE["studies"] if studies is None else studies,
                    VERSION, out, run_date)
    return out, meta


def test_file_rows_round_trip_with_standard_library(tmp_path):
    out, _ = _build(tmp_path)
    for nct in ("NCT00000821", "NCT00785291", "NCT04280705"):
        assert bt.read_study(out, nct) == bt.project(_study(nct))
    assert bt.read_study(out, "NCT00000105") is None  # observational, left out
    assert bt.read_study(out, "NCT00040625") is None  # expanded access, left out
    # And by hand, as the docstring shows, with sqlite3, zlib and json only.
    import zlib
    con = sqlite3.connect(str(out))
    zdict = con.execute("SELECT zdict FROM meta").fetchone()[0]
    blob, start, last = con.execute("SELECT study, start_date, last_update FROM studies "
                                    "WHERE nct_id = 'NCT04280705'").fetchone()
    con.close()
    d = zlib.decompressobj(zdict=zdict)
    assert json.loads(d.decompress(blob) + d.flush())["protocolSection"]["identificationModule"][
        "nctId"] == "NCT04280705"
    assert (start, last) == ("2020-02-21", "2022-03-14")


def test_meta_row(tmp_path):
    out, meta = _build(tmp_path)
    con = sqlite3.connect(str(out))
    con.row_factory = sqlite3.Row
    rows = con.execute("SELECT * FROM meta").fetchall()
    con.close()
    assert len(rows) == 1
    row = rows[0]
    assert row["run_date"] == "2026-11-26"
    assert row["ot_release"] == "26.09"
    assert row["ctgov_api_version"] == "2.0.5"
    assert row["compression"] == bt.COMPRESSION
    counts = json.loads(row["counts"])
    assert counts["ot_nct_linked_to_disease"] == 5
    assert counts["kept_interventional"] == 3
    assert list(counts) == sorted(counts)
    assert counts == meta["counts"]


def test_two_builds_on_same_input_are_byte_identical(tmp_path):
    first, _ = _build(tmp_path, "a.sqlite")
    shuffled = list(reversed(RESPONSE["studies"]))  # order of the answers does not matter
    second, _ = _build(tmp_path, "b.sqlite", studies=shuffled)
    assert first.read_bytes() == second.read_bytes()
    assert _sha(first) == _sha(second)


def test_run_date_is_the_only_date_written(tmp_path):
    first, _ = _build(tmp_path, "a.sqlite", run_date="2026-11-26")
    second, _ = _build(tmp_path, "b.sqlite", run_date="2026-12-01")
    assert first.read_bytes() != second.read_bytes()
    third, _ = _build(tmp_path, "c.sqlite", run_date="2026-11-26")
    assert first.read_bytes() == third.read_bytes()


def test_bad_run_date_refused(tmp_path):
    with pytest.raises(ValueError):
        _build(tmp_path, run_date="26 Nov")


# ----------------------------------------------------- fetching, cache, limits

class FakeNet:
    def __init__(self, answers):
        self.answers = list(answers)
        self.urls = []
        self.slept = []
        self.now = 0.0

    def get(self, url):
        self.urls.append(url)
        status, body = self.answers.pop(0)
        return status, json.dumps(body).encode() if isinstance(body, dict) else body

    def sleep(self, seconds):
        self.slept.append(seconds)
        self.now += seconds

    def clock(self):
        return self.now


def _fetcher(net, backoff=(1, 2)):
    return bt.Fetcher(get=net.get, sleep=net.sleep, clock=net.clock, gap=2.0, backoff=backoff)


def test_fetch_saves_answers_and_rebuilds_offline(tmp_path):
    net = FakeNet([(200, VERSION), (200, RESPONSE)])
    studies, version = bt.fetch_all(IDS, tmp_path, offline=False, fetcher=_fetcher(net))
    assert len(net.urls) == 2 and version == VERSION
    saved = tmp_path / "ctgov" / "batch_00000.json.gz"
    with gzip.open(saved) as file:
        assert json.loads(file.read())["ids"] == IDS
    offline = bt.fetch_all(IDS, tmp_path, offline=True,
                           fetcher=_fetcher(FakeNet([])))  # no answers: any call would fail
    assert offline == (studies, version)


def test_offline_without_cache_fails(tmp_path):
    with pytest.raises(FileNotFoundError):
        bt.fetch_all(IDS, tmp_path, offline=True, fetcher=_fetcher(FakeNet([])))


def test_cached_batch_for_other_ids_is_fetched_again(tmp_path):
    bt.fetch_all(IDS, tmp_path, offline=False, fetcher=_fetcher(FakeNet([(200, VERSION), (200, RESPONSE)])))
    net = FakeNet([(200, {"studies": []})])
    bt.fetch_all(IDS[:2], tmp_path, offline=False, fetcher=_fetcher(net))
    assert len(net.urls) == 1


def test_gap_between_calls():
    net = FakeNet([(200, {"studies": []})] * 3)
    fetcher = _fetcher(net)
    for _ in range(3):
        fetcher.json("u")
    assert net.slept == [2.0, 2.0]


def test_429_waits_then_succeeds():
    net = FakeNet([(429, b"slow down"), (200, {"studies": []})])
    fetcher = _fetcher(net)
    assert fetcher.json("u") == {"studies": []}
    assert 1 in net.slept and fetcher.refusals == 1 and fetcher.calls == 2


def test_keeps_refusing_stops_and_asks():
    net = FakeNet([(429, b"no")] * 3)
    with pytest.raises(bt.StopAndAsk):
        _fetcher(net).json("u")
    assert len(net.urls) == 3


def test_403_stops_at_once():
    net = FakeNet([(403, b"blocked"), (200, {"studies": []})])
    with pytest.raises(bt.StopAndAsk):
        _fetcher(net).json("u")
    assert len(net.urls) == 1


def test_next_page_token_followed():
    net = FakeNet([(200, {"studies": [1], "nextPageToken": "abc"}), (200, {"studies": [2]})])
    assert _fetcher(net).batch(["NCT1"]) == {"studies": [1, 2]}
    assert "pageToken=abc" in net.urls[1]


def test_main_offline_end_to_end_and_deterministic(tmp_path, monkeypatch):
    cache = tmp_path / "cache"
    monkeypatch.setattr(bt, "read_ot_parquet", lambda path: OT_ROWS)
    bt.fetch_all(IDS, cache, offline=False,
                 fetcher=_fetcher(FakeNet([(200, VERSION), (200, RESPONSE)])))
    a, b = tmp_path / "a.sqlite", tmp_path / "b.sqlite"
    assert bt.main(["--ot-parquet", "x.parquet", "--cache", str(cache), "--offline",
                    "--run-date", "2026-11-26", "--out", str(a)]) == 0
    assert bt.main(["--cache", str(cache), "--offline", "--run-date", "2026-11-26",
                    "--out", str(b)]) == 0
    assert _sha(a) == _sha(b)
