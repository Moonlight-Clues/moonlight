"""Ticket R1. Snapshot: each trial's diseases and countries.

THE TICKET
  1. Read protocolSection.contactsLocationsModule.locations.country too. Store
     per study a sorted list of distinct country names, spelled as the
     registry spells them. No sites, cities or contacts.
  2. Table study_diseases (disease_id, nct_id) from the Open Targets 26.09
     clinical_report rows the build already reads: one row per disease id the
     report gives a trial. Exact ids only. Indexed by disease_id.
  3. The meta row holds the date the registry was read.
  4. Rebuild trials.sqlite: the same 161,149 studies, every old field unchanged.
  5. trials.recruiting_for(disease_id): studies linked to that disease whose
     overallStatus is exactly RECRUITING, as {nct_id, title, phases,
     countries, url}, newest start first by for_card's rules.

No network. Small files are built with scripts/build_trials.py's own writer.
fixtures/trials_r1/ctgov_countries.response.json is a live API v2 answer
(27 Nov 2026) with the builder's own fields= list, new field included.
fixtures/trials_r1/old_sample.json is 50 studies read from trials.sqlite
before the rebuild.
"""

import datetime
import hashlib
import importlib.util
import json
import pathlib
import sqlite3
import zlib

import pytest

from moonlight import trials as trials_module

ROOT = pathlib.Path(__file__).resolve().parent.parent
FIXTURES = ROOT / "fixtures" / "trials_r1"
REAL_FILE = ROOT / "moonlight" / "trials.sqlite"
TODAY = datetime.date(2026, 11, 27)

PAH = "MONDO_0015924"
PSC = "MONDO_0018646"
ITEM_KEYS = {"nct_id", "title", "phases", "countries", "url"}


def _builder():
    spec = importlib.util.spec_from_file_location("build_trials", ROOT / "scripts" / "build_trials.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


bt = _builder()
LIVE = json.loads((FIXTURES / "ctgov_countries.response.json").read_text(encoding="utf-8"))
OLD = json.loads((FIXTURES / "old_sample.json").read_text(encoding="utf-8"))
OT_ROWS = json.loads((ROOT / "fixtures" / "trials_t2" / "ot_clinical_report_rows.json")
                     .read_text(encoding="utf-8"))
VERSION = {"apiVersion": "2.0.5", "dataTimestamp": "2026-11-27T10:00:05"}


def _live(nct):
    for found in LIVE["studies"]:
        if found["protocolSection"]["identificationModule"]["nctId"] == nct:
            return found
    raise KeyError(nct)


def study(nct, start=None, status="RECRUITING", phases=("PHASE2",), locations=None):
    """A v2 study as ClinicalTrials.gov sends it, builder's fields only."""
    state = {"overallStatus": status}
    if start is not None:
        state["startDateStruct"] = {"date": start, "type": "ACTUAL"}
    section = {
        "identificationModule": {"nctId": nct, "briefTitle": "A study " + nct},
        "statusModule": state,
        "designModule": {"studyType": "INTERVENTIONAL", "phases": list(phases)},
        "armsInterventionsModule": {
            "interventions": [{"name": "Sirolimus", "type": "DRUG"}]}}
    if locations is not None:
        section["contactsLocationsModule"] = {"locations": [{"country": c} for c in locations]}
    return {"protocolSection": section}


def report(nct, *disease_ids):
    return {"id": nct.lower(), "source": "ClinicalTrials.gov",
            "diseases": [{"diseaseFromSource": "x", "diseaseId": d} for d in disease_ids]}


def build(tmp_path, studies, rows, name="t.sqlite", run_date="2026-11-27", **kw):
    ids, counts = bt.nct_ids_from_reports(rows)
    out = tmp_path / name
    bt.build(ids, counts, studies, VERSION, out, run_date,
             links=bt.disease_links_from_reports(rows), **kw)
    return out


def opened(path):
    found = trials_module.Trials.open(path)
    assert found is not None
    return found


# ----------------------------------------------------------- 1. countries

def test_country_field_is_asked_for():
    assert "protocolSection.contactsLocationsModule.locations.country" in bt.FIELDS


def test_countries_sorted_distinct_as_spelled_from_a_live_answer():
    assert bt.countries(_live("NCT04280705")) == [
        "Denmark", "Germany", "Greece", "Japan", "Mexico", "Singapore", "South Korea",
        "Spain", "United Kingdom", "United States"]
    assert bt.countries(_live("NCT00785291")) == ["Puerto Rico", "United States"]


def test_countries_missing_or_blank_give_an_empty_list():
    assert bt.countries(study("NCT1")) == []
    assert bt.countries(study("NCT1", locations=[])) == []
    odd = study("NCT1", locations=["Côte D'Ivoire", "", "Côte D'Ivoire", "Brazil"])
    odd["protocolSection"]["contactsLocationsModule"]["locations"].append({"city": "Paris"})
    assert bt.countries(odd) == ["Brazil", "Côte D'Ivoire"]


def test_project_still_keeps_no_sites_cities_or_contacts():
    # The stored study JSON is the same as before: countries live in their own column.
    assert "contactsLocationsModule" not in bt.project(_live("NCT04280705"))["protocolSection"]


# ------------------------------------------------------- 2. study_diseases

def test_disease_links_exact_ids_one_row_each():
    rows = OT_ROWS + [report("NCT00000821", "MONDO_0005109", "EFO_0000764"),
                      {"id": "x", "source": "DailyMed", "diseases": [{"diseaseId": "EFO_1"}]}]
    assert bt.disease_links_from_reports(rows) == [
        ("EFO_0000764", "NCT00000821"),
        ("MONDO_0004992", "NCT00000105"),
        ("MONDO_0005109", "NCT00000821"),
        ("MONDO_0005112", "NCT00040625"),
        ("MONDO_0007254", "NCT00785291"),
        ("MONDO_0100096", "NCT04280705")]


def test_file_has_study_diseases_for_stored_studies_indexed_by_disease(tmp_path):
    rows = [report("NCT00000001", "MONDO_A", "MONDO_B"), report("NCT00000002", "MONDO_A"),
            report("NCT00000003", "MONDO_A")]
    studies = [study("NCT00000001", locations=["Spain", "France", "Spain"]),
               study("NCT00000002"), {"protocolSection": {
                   "identificationModule": {"nctId": "NCT00000003"},
                   "designModule": {"studyType": "OBSERVATIONAL"}}}]
    out = build(tmp_path, studies, rows)
    con = sqlite3.connect(str(out))
    links = con.execute("SELECT disease_id, nct_id FROM study_diseases").fetchall()
    plan = " ".join(r[-1] for r in con.execute(
        "EXPLAIN QUERY PLAN SELECT nct_id FROM study_diseases WHERE disease_id = 'MONDO_A'"))
    countries = dict(con.execute("SELECT nct_id, countries FROM studies"))
    con.close()
    # The observational study is not stored, so it is not linked either.
    assert sorted(links) == [("MONDO_A", "NCT00000001"), ("MONDO_A", "NCT00000002"),
                             ("MONDO_B", "NCT00000001")]
    # A look-up by disease uses the index (here, the primary key that starts with disease_id).
    assert "SEARCH study_diseases USING" in plan and "(disease_id=?)" in plan
    assert json.loads(countries["NCT00000001"]) == ["France", "Spain"]
    assert json.loads(countries["NCT00000002"]) == []


# -------------------------------------------------------------- 3. meta

def test_meta_says_when_the_registry_was_read(tmp_path):
    out = build(tmp_path, [study("NCT00000001")], [report("NCT00000001", "MONDO_A")])
    con = sqlite3.connect(str(out))
    con.row_factory = sqlite3.Row
    row = con.execute("SELECT * FROM meta").fetchone()
    con.close()
    assert row["run_date"] == "2026-11-27"
    assert row["ctgov_data_timestamp"] == "2026-11-27T10:00:05"
    assert row["countries_read_date"] == "2026-11-27"
    assert row["countries_data_timestamp"] == "2026-11-27T10:00:05"


def test_still_byte_identical_on_the_same_input(tmp_path):
    rows = [report("NCT00000001", "MONDO_A"), report("NCT00000002", "MONDO_B")]
    studies = [study("NCT00000001", locations=["Spain"]), study("NCT00000002")]
    a = build(tmp_path, studies, rows, "a.sqlite")
    b = build(tmp_path, list(reversed(studies)), list(reversed(rows)), "b.sqlite")
    assert a.read_bytes() == b.read_bytes()


# ------------------------------------- 4. rebuild keeping the old rows exactly

def test_keep_from_copies_old_rows_and_meta_byte_for_byte(tmp_path):
    rows = [report("NCT00000001", "MONDO_A"), report("NCT00000002", "MONDO_A")]
    old_studies = [study("NCT00000001", "2020-01-01", status="RECRUITING"),
                   study("NCT00000002", "2021-01-01", status="COMPLETED")]
    old = tmp_path / "old.sqlite"
    ids, counts = bt.nct_ids_from_reports(rows)
    bt.build(ids, counts, old_studies, {"apiVersion": "2.0.5",
                                        "dataTimestamp": "2026-11-25T10:00:05"},
             old, "2026-11-26")
    # A newer read: the registry changed a status and added countries.
    new_studies = [study("NCT00000001", "2020-01-01", status="COMPLETED", locations=["Peru"]),
                   study("NCT00000002", "2021-01-01", status="COMPLETED", locations=["Chile"])]
    out = build(tmp_path, new_studies, rows, "new.sqlite", keep_from=old)
    con_old, con_new = sqlite3.connect(str(old)), sqlite3.connect(str(out))
    q = "SELECT nct_id, start_date, last_update, study FROM studies ORDER BY nct_id"
    assert con_old.execute(q).fetchall() == con_new.execute(q).fetchall()
    q = ("SELECT run_date, ot_release, ot_source, ctgov_api_version, ctgov_data_timestamp, "
         "compression, counts, zdict FROM meta")
    assert con_old.execute(q).fetchall() == con_new.execute(q).fetchall()
    meta = con_new.execute("SELECT countries_read_date, countries_data_timestamp FROM meta").fetchone()
    countries = dict(con_new.execute("SELECT nct_id, countries FROM studies"))
    con_old.close(), con_new.close()
    assert meta == ("2026-11-27", "2026-11-27T10:00:05")
    assert json.loads(countries["NCT00000001"]) == ["Peru"]
    # The old status is what the file holds: it is still RECRUITING there.
    found = opened(out).recruiting_for("MONDO_A", today=TODAY)
    assert [item["nct_id"] for item in found] == ["NCT00000001"]


# --------------------------------------------------- 5. recruiting_for

def test_recruiting_for_items_filter_and_order(tmp_path):
    rows = [report(f"NCT0000000{n}", "MONDO_A") for n in range(1, 8)] + \
           [report("NCT00000009", "MONDO_B")]
    studies = [
        study("NCT00000001", "2019-07-15", phases=("PHASE1", "PHASE2"),
              locations=["United States", "Canada"]),
        study("NCT00000002", "2022-11-30"),
        study("NCT00000003", None),                       # unknown date: last
        study("NCT00000004", "2022-11-30"),               # tie with 2: higher NCT first
        study("NCT00000005", "2024-01-01", status="NOT_YET_RECRUITING"),
        study("NCT00000006", "2023-01-01", status="Recruiting"),  # not exactly RECRUITING
        study("NCT00000007", "1890-01-01"),               # before 1950: unknown
        study("NCT00000009", "2025-01-01"),               # another disease
    ]
    found = opened(build(tmp_path, studies, rows)).recruiting_for("MONDO_A", today=TODAY)
    assert [item["nct_id"] for item in found] == [
        "NCT00000004", "NCT00000002", "NCT00000001", "NCT00000007", "NCT00000003"]
    first = found[2]
    assert first == {"nct_id": "NCT00000001", "title": "A study NCT00000001",
                     "phases": ["PHASE1", "PHASE2"], "countries": ["Canada", "United States"],
                     "url": "https://clinicaltrials.gov/study/NCT00000001#contacts-and-locations"}
    assert all(set(item) == ITEM_KEYS for item in found)
    json.dumps(found)


def test_recruiting_for_a_disease_with_no_trial_is_empty(tmp_path):
    out = build(tmp_path, [study("NCT00000001")], [report("NCT00000001", "MONDO_A")])
    assert opened(out).recruiting_for("MONDO_NOTHING", today=TODAY) == []


def test_recruiting_for_a_damaged_file_raises(tmp_path):
    out = build(tmp_path, [study("NCT00000001")], [report("NCT00000001", "MONDO_A")])
    found = opened(out)
    found._con.close()
    damaged = sqlite3.connect(":memory:", check_same_thread=False)
    damaged.execute("CREATE TABLE studies (nct_id, start_date, study, countries)")
    damaged.execute("CREATE TABLE study_diseases (disease_id, nct_id)")
    damaged.execute("INSERT INTO studies VALUES ('NCT00000001', NULL, x'00ff', '[]')")
    damaged.execute("INSERT INTO study_diseases VALUES ('MONDO_A', 'NCT00000001')")
    found._con = damaged
    with pytest.raises(zlib.error):
        found.recruiting_for("MONDO_A", today=TODAY)


def test_recruiting_for_a_file_without_the_new_table_raises(tmp_path):
    out = tmp_path / "old.sqlite"
    bt.write_sqlite(out, [("NCT00000001", study("NCT00000001"))],
                    {"run_date": "2026-11-26", "counts": {}})
    con = sqlite3.connect(str(out))
    con.execute("DROP TABLE study_diseases")
    con.commit()
    con.close()
    with pytest.raises(sqlite3.Error):
        opened(out).recruiting_for("MONDO_A", today=TODAY)


# ------------------------------------------------------ the real file

def _real():
    return opened(REAL_FILE)


def _status_in_file(found, nct):
    return found._study(nct)["protocolSection"]["statusModule"]["overallStatus"]


def test_real_file_holds_the_same_studies_and_old_fields():
    con = sqlite3.connect(f"file:{REAL_FILE}?mode=ro", uri=True)
    try:
        assert con.execute("SELECT COUNT(*) FROM studies").fetchone()[0] == OLD["study_count"] == 161149
        zdict = con.execute("SELECT zdict FROM meta").fetchone()[0]
        assert hashlib.sha256(zdict).hexdigest() == OLD["zdict_sha256"]
        meta = con.execute("SELECT run_date, ot_release, ot_source, ctgov_api_version, "
                           "ctgov_data_timestamp, compression, counts FROM meta").fetchone()
        assert list(meta) == [OLD["meta"][k] for k in ("run_date", "ot_release", "ot_source",
                                                       "ctgov_api_version", "ctgov_data_timestamp",
                                                       "compression", "counts")]
        assert len(OLD["studies"]) == 50
        for old in OLD["studies"]:
            start, last, blob, countries = con.execute(
                "SELECT start_date, last_update, study, countries FROM studies WHERE nct_id = ?",
                (old["nct_id"],)).fetchone()
            assert (start, last) == (old["start_date"], old["last_update"])
            assert hashlib.sha256(blob).hexdigest() == old["blob_sha256"]
            d = zlib.decompressobj(zdict=zdict)
            assert json.loads(d.decompress(blob) + d.flush()) == old["study"]
            assert isinstance(json.loads(countries), list)
    finally:
        con.close()


def test_real_file_checked_date_is_when_the_statuses_were_read():
    # The checked date (meta run_date, Trials.checked) is the date the stored
    # overallStatus values were read: the 26 Nov build. The countries were
    # read later, and that date is kept separately.
    con = sqlite3.connect(f"file:{REAL_FILE}?mode=ro", uri=True)
    try:
        row = con.execute("SELECT run_date, ctgov_data_timestamp, countries_read_date, "
                          "countries_data_timestamp FROM meta").fetchone()
    finally:
        con.close()
    assert row == (OLD["meta"]["run_date"], OLD["meta"]["ctgov_data_timestamp"],
                   "2026-11-27", "2026-11-27T10:00:05")
    assert OLD["meta"]["run_date"] == "2026-11-26"
    assert _real().checked == "2026-11-26"


@pytest.mark.parametrize("disease_id", [PAH, PSC])
def test_real_file_recruiting_for_pah_and_psc(disease_id):
    found = _real()
    con = found._con
    # Every study linked to the disease, by the number today's rows show
    # (ClinicalTrials.gov's own nctId, as for_card shows it).
    linked = {}
    for nct, start in con.execute(
            "SELECT s.nct_id, s.start_date FROM study_diseases d JOIN studies s "
            "ON s.nct_id = d.nct_id WHERE d.disease_id = ?", (disease_id,)):
        saved = found._study(nct)["protocolSection"]
        linked[saved["identificationModule"]["nctId"]] = (
            nct, saved["statusModule"].get("overallStatus"), start)
    items = found.recruiting_for(disease_id, today=TODAY)
    assert items, disease_id
    keys = []
    for item in items:
        assert set(item) == ITEM_KEYS
        nct, status, start = linked[item["nct_id"]]
        assert status == "RECRUITING"
        assert isinstance(item["countries"], list)
        assert item["countries"] == sorted(set(item["countries"]))
        assert all(isinstance(c, str) and c for c in item["countries"])
        assert isinstance(item["title"], str) and item["title"]
        assert item["url"] == f"https://clinicaltrials.gov/study/{item['nct_id']}#contacts-and-locations"
        keys.append((trials_module.start_key(start, TODAY), nct))
    # Known dates newest first, ties to the higher NCT number, unknown dates last.
    for (day_a, nct_a), (day_b, nct_b) in zip(keys, keys[1:]):
        if day_a is None:
            assert day_b is None and nct_a > nct_b
        elif day_b is not None:
            assert day_a > day_b or (day_a == day_b and nct_a > nct_b)
    # Every recruiting study linked to the disease is there, and nothing else.
    assert sorted(item["nct_id"] for item in items) == sorted(
        shown for shown, (_, status, _) in linked.items() if status == "RECRUITING")
