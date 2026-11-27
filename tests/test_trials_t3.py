"""Ticket T3. API: trials on trial cards.

THE TICKET
  Each trial card in /api/clues carries up to 3 trials (newest first), the
  trial total, and the checked date. New fields: studies[], study_total,
  trials_checked. Old fields unchanged. moonlight/trials.sqlite is opened
  once, at start. File missing: serve as today, and log it.
  MAIN 5 (26 Nov 23:11 IST): a start date before 1950, or more than 10 years
  ahead, counts as unknown and sorts last.

HOW IT IS READ (the ticket does not spell these out; each is a choice, and is
asked about in the session report)
  * "Trial card" = a card on the In trials tab: the main list (being_studied)
    and the two folded boxes under it (more_in_trials, new_in_trials).
  * Which trials belong to a card: the card's own trial links for THIS disease
    (engine.studies_for_this_disease, ticket 3.11). trials.sqlite holds the
    studies, not which disease a medicine was tested for, so the file is only
    used to look those NCT numbers up.
  * study_total: how many of those NCT numbers are in the file.
  * trials_checked: the file's run_date, as written by scripts/build_trials.py.
  * A trial is what moonlight/ctgov.py (ticket T1) reads: nct_id, status, end,
    phases, role.

No network. Small trial files are built here with scripts/build_trials.py's
own writer. The ADPKD page is the saved one (test_opposite_way_box).
"""

import datetime
import importlib.util
import json
import logging
import pathlib
import sqlite3
from unittest.mock import patch

import pytest
from urllib.parse import quote
from fastapi.testclient import TestClient

from moonlight import api, ctgov
from moonlight import trials as trials_module

import test_opposite_way_box as adpkd_page

ROOT = pathlib.Path(__file__).resolve().parent.parent
REAL_FILE = ROOT / "moonlight" / "trials.sqlite"
TODAY = datetime.date(2026, 11, 26)
# ticket T4: each trial also has its "url", and each card "studies_url" (the API sends the links)
NEW_KEYS = {"studies", "study_total", "trials_checked", "studies_url"}
TRIAL_KEYS = {"nct_id", "status", "end", "phases", "role", "url"}
LINK = "https://clinicaltrials.gov/study/"


def _builder():
    spec = importlib.util.spec_from_file_location("build_trials", ROOT / "scripts" / "build_trials.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


bt = _builder()


def study(nct, start=None, status="COMPLETED", phases=("PHASE2",), medicine="Sirolimus",
          arm="EXPERIMENTAL", end=("2020-05", "ACTUAL")):
    """A saved study in the shape build_trials stores."""
    state = {"overallStatus": status}
    if start is not None:
        state["startDateStruct"] = {"date": start, "type": "ACTUAL"}
    if end is not None:
        state["completionDateStruct"] = {"date": end[0], "type": end[1]}
    return nct, {"protocolSection": {
        "identificationModule": {"nctId": nct, "briefTitle": "A study " + nct},
        "statusModule": state,
        "designModule": {"studyType": "INTERVENTIONAL", "phases": list(phases)},
        "armsInterventionsModule": {
            "armGroups": [{"label": "A", "type": arm, "interventionNames": [medicine]}],
            "interventions": [{"name": medicine, "type": "DRUG", "armGroupLabels": ["A"]}]}}}


def make_file(path, rows, run_date="2026-11-26"):
    rows = sorted(rows, key=lambda row: row[0])
    bt.write_sqlite(path, rows, {"run_date": run_date, "counts": {"kept_interventional": len(rows)},
                                 "ctgov_api_version": "2.0.5",
                                 "ctgov_data_timestamp": "2026-11-25T10:00:05"})
    return path


def open_file(path):
    found = trials_module.Trials.open(path)
    assert found is not None
    return found


def ids(items):
    return [item["nct_id"] for item in items]


# ------------------------------------------------ up to 3, newest first, total

def test_three_newest_first_and_the_total(tmp_path):
    path = make_file(tmp_path / "t.sqlite", [
        study("NCT00000001", "2005-03-01"), study("NCT00000002", "2019-07-15"),
        study("NCT00000003", "2012-01"), study("NCT00000004", "2022-11-30"),
        study("NCT00000005", "2001")])
    found = open_file(path)
    links = {LINK + "NCT0000000" + n for n in "12345"}
    shown, total = found.for_card(links, ["Sirolimus"], today=TODAY)
    assert ids(shown) == ["NCT00000004", "NCT00000002", "NCT00000003"]
    assert total == 5


def test_a_trial_has_exactly_the_ctgov_reader_fields(tmp_path):
    path = make_file(tmp_path / "t.sqlite", [
        study("NCT00000001", "2019-07-15", status="RECRUITING", phases=("PHASE1", "PHASE2"),
              end=("2027-01", "ESTIMATED"))])
    shown, _ = open_file(path).for_card({LINK + "NCT00000001"}, ["Sirolimus"], today=TODAY)
    assert shown == [{"nct_id": "NCT00000001", "status": "Recruiting", "end": "Expected to end 2027",
                      "phases": ["PHASE1", "PHASE2"], "role": "Being tested",
                      "url": "https://clinicaltrials.gov/study/NCT00000001"}]
    assert set(shown[0]) == TRIAL_KEYS
    json.dumps(shown)  # plain JSON: no tuples or dataclasses left in it


def test_fewer_than_three_shows_them_all(tmp_path):
    path = make_file(tmp_path / "t.sqlite", [study("NCT00000001", "2005"), study("NCT00000002", "2006")])
    shown, total = open_file(path).for_card({LINK + "NCT00000001", LINK + "NCT00000002"},
                                            ["Sirolimus"], today=TODAY)
    assert ids(shown) == ["NCT00000002", "NCT00000001"] and total == 2


def test_no_links_means_no_trials_and_a_total_of_zero(tmp_path):
    path = make_file(tmp_path / "t.sqlite", [study("NCT00000001", "2005")])
    assert open_file(path).for_card(set(), ["Sirolimus"], today=TODAY) == ([], 0)


def test_a_number_not_in_the_file_or_not_a_trial_link_is_not_counted(tmp_path):
    path = make_file(tmp_path / "t.sqlite", [study("NCT00000001", "2005")])
    links = {LINK + "NCT00000001", LINK + "NCT99999999", "https://example.org/not-a-study",
             "https://ttd.idrblab.cn/data/drug/details/D0PN8H"}
    shown, total = open_file(path).for_card(links, ["Sirolimus"], today=TODAY)
    assert ids(shown) == ["NCT00000001"] and total == 1


def test_link_case_does_not_matter(tmp_path):
    path = make_file(tmp_path / "t.sqlite", [study("NCT00000001", "2005")])
    shown, total = open_file(path).for_card({"https://clinicaltrials.gov/study/nct00000001"},
                                            ["Sirolimus"], today=TODAY)
    assert ids(shown) == ["NCT00000001"] and total == 1


def test_a_big_list_of_links_is_looked_up(tmp_path):
    rows = [study(f"NCT{n:08d}", f"{1990 + n % 30}-01-01") for n in range(1, 2001)]
    path = make_file(tmp_path / "t.sqlite", rows)
    links = {LINK + f"NCT{n:08d}" for n in range(1, 2001)}
    shown, total = open_file(path).for_card(links, ["Sirolimus"], today=TODAY)
    assert total == 2000 and len(shown) == 3


def test_same_start_date_breaks_the_tie_the_same_way_every_time(tmp_path):
    path = make_file(tmp_path / "t.sqlite", [study(f"NCT0000000{n}", "2010-05-05") for n in range(1, 6)])
    links = {LINK + f"NCT0000000{n}" for n in range(1, 6)}
    found = open_file(path)
    first = ids(found.for_card(links, ["Sirolimus"], today=TODAY)[0])
    assert first == ["NCT00000005", "NCT00000004", "NCT00000003"]
    assert ids(found.for_card(set(reversed(sorted(links))), ["Sirolimus"], today=TODAY)[0]) == first


# ---------------------------------------- MAIN 5: odd start dates sort last

def test_before_1950_or_more_than_ten_years_ahead_is_unknown_and_last(tmp_path):
    path = make_file(tmp_path / "t.sqlite", [
        study("NCT00000001", "1949-12-31"),   # before 1950: unknown
        study("NCT00000002", "2036-11-27"),   # one day over ten years: unknown
        study("NCT00000003", None),           # no start date: unknown
        study("NCT00000004", "1950-01-01"),   # the first day that counts
        study("NCT00000005", "2036-11-26"),   # exactly ten years ahead: counts, and is newest
        study("NCT00000006", "2003-06")])
    found = open_file(path)
    links = {LINK + "NCT0000000" + n for n in "123456"}
    every = found.for_card(links, ["Sirolimus"], today=TODAY, limit=6)[0]
    assert ids(every)[:3] == ["NCT00000005", "NCT00000006", "NCT00000004"]
    assert sorted(ids(every)[3:]) == ["NCT00000001", "NCT00000002", "NCT00000003"]
    assert found.for_card(links, ["Sirolimus"], today=TODAY)[1] == 6  # unknown ones still count


def test_unknown_dates_fill_the_list_only_after_every_known_one(tmp_path):
    path = make_file(tmp_path / "t.sqlite", [
        study("NCT00000001", "1900"), study("NCT00000002", "2090-01-01"), study("NCT00000003", "1960")])
    links = {LINK + "NCT0000000" + n for n in "123"}
    shown, total = open_file(path).for_card(links, ["Sirolimus"], today=TODAY)
    assert ids(shown)[0] == "NCT00000003" and total == 3


def test_a_date_that_is_not_a_date_is_unknown(tmp_path):
    path = make_file(tmp_path / "t.sqlite", [
        study("NCT00000001", "soon"), study("NCT00000002", "2015-13"), study("NCT00000003", "2015-02-30"),
        study("NCT00000004", "2000")])
    links = {LINK + "NCT0000000" + n for n in "1234"}
    assert ids(open_file(path).for_card(links, ["Sirolimus"], today=TODAY)[0])[0] == "NCT00000004"


def test_ten_years_ahead_is_counted_to_the_day(tmp_path):
    path = make_file(tmp_path / "t.sqlite", [study("NCT00000001", "2036-02-28"), study("NCT00000002", "2036-03-02")])
    links = {LINK + "NCT00000001", LINK + "NCT00000002"}
    shown, _ = open_file(path).for_card(links, ["Sirolimus"], today=datetime.date(2026, 2, 28))
    assert ids(shown) == ["NCT00000001", "NCT00000002"]  # the 28th counts, the 2nd of March is over


def test_the_date_rule_reads_the_real_clock_when_no_day_is_given(tmp_path):
    year = datetime.date.today().year
    path = make_file(tmp_path / "t.sqlite", [study("NCT00000001", f"{year + 40}-01-01"),
                                             study("NCT00000002", f"{year - 3}-01-01")])
    shown, _ = open_file(path).for_card({LINK + "NCT00000001", LINK + "NCT00000002"}, ["Sirolimus"])
    assert ids(shown) == ["NCT00000002", "NCT00000001"]


# ------------------------------------------------------------- the role

def test_the_role_is_read_for_the_card_s_medicine_or_one_of_its_forms(tmp_path):
    path = make_file(tmp_path / "t.sqlite", [study("NCT00000001", "2015", medicine="Imatinib Mesylate")])
    found = open_file(path)
    links = {LINK + "NCT00000001"}
    assert found.for_card(links, ["Imatinib", "Imatinib Mesylate"], today=TODAY)[0][0]["role"] == "Was tested"  # ticket 3.26: the study is over
    assert found.for_card(links, ["Imatinib"], today=TODAY)[0][0]["role"] == ctgov.ROLE_NOT_STATED


def test_a_comparison_only_medicine_says_so(tmp_path):
    path = make_file(tmp_path / "t.sqlite", [study("NCT00000001", "2015", arm="ACTIVE_COMPARATOR")])
    assert open_file(path).for_card({LINK + "NCT00000001"}, ["Sirolimus"], today=TODAY)[0][0]["role"] \
        == ctgov.WAS_USED_FOR_COMPARISON  # ticket 3.26: the study is over


# ------------------------------------------------- opening, once, and the date

def test_the_checked_date_is_the_files_run_date(tmp_path):
    path = make_file(tmp_path / "t.sqlite", [study("NCT00000001", "2015")], run_date="2026-11-20")
    assert open_file(path).checked == "2026-11-20"


def test_a_missing_file_gives_none_and_is_logged(tmp_path, caplog):
    with caplog.at_level(logging.WARNING):
        assert trials_module.Trials.open(tmp_path / "nope.sqlite") is None
    assert "trials" in caplog.text.lower() and "nope.sqlite" in caplog.text
    assert not (tmp_path / "nope.sqlite").exists()  # opening never creates a file


def test_a_file_that_is_not_a_trials_file_gives_none_and_is_logged(tmp_path, caplog):
    bad = tmp_path / "bad.sqlite"
    bad.write_bytes(b"this is not a database")
    with caplog.at_level(logging.WARNING):
        assert trials_module.Trials.open(bad) is None
    assert "bad.sqlite" in caplog.text
    empty = tmp_path / "empty.sqlite"
    sqlite3.connect(empty).close()
    assert trials_module.Trials.open(empty) is None


def test_the_file_is_opened_read_only(tmp_path):
    path = make_file(tmp_path / "t.sqlite", [study("NCT00000001", "2015")])
    before = path.read_bytes()
    found = open_file(path)
    found.for_card({LINK + "NCT00000001"}, ["Sirolimus"], today=TODAY)
    with pytest.raises(sqlite3.OperationalError):
        found._con.execute("DELETE FROM studies")
    found.close()
    assert path.read_bytes() == before


def test_it_can_be_read_from_other_threads(tmp_path):
    from concurrent.futures import ThreadPoolExecutor
    path = make_file(tmp_path / "t.sqlite", [study(f"NCT{n:08d}", "2015") for n in range(1, 40)])
    found = open_file(path)
    links = {LINK + f"NCT{n:08d}" for n in range(1, 40)}
    with ThreadPoolExecutor(8) as pool:
        results = list(pool.map(lambda _: found.for_card(links, ["Sirolimus"], today=TODAY), range(32)))
    assert all(total == 39 and len(shown) == 3 for shown, total in results)


# ---------------------------------------------------------------- the API

def saved_page(disease_id=adpkd_page.ADPKD):
    api.forget_answers()
    with patch("moonlight.fetch._post_json", side_effect=adpkd_page.saved_post_json):
        return TestClient(api.app).get("/api/clues", params={"disease_id": disease_id}).json()


@pytest.fixture
def before():
    """The saved ADPKD page with no trials file, as it was before this ticket."""
    with patch.object(trials_module, "TRIALS_PATH", pathlib.Path("/nonexistent/trials.sqlite")):
        with TestClient(api.app):
            return saved_page()


def trial_cards(answer):
    return (answer["being_studied"] + answer.get("more_in_trials", [])
            + answer.get("new_in_trials", []))


def families_links():
    """Family id -> its trial links for ADPKD, from the same saved page."""
    with patch("moonlight.fetch._post_json", side_effect=adpkd_page.saved_post_json):
        return {key: sorted(value) for key, value in api._find(adpkd_page.ADPKD).studies.items()}


def small_file(tmp_path):
    """A trials file with every NCT number ADPKD's trial cards link, one study
    each, a different start year each, except those named in `missing`."""
    links = families_links()
    numbers = sorted({link.rsplit("/", 1)[1] for group in links.values() for link in group})
    rows = [study(number, f"{1990 + position % 35}-06-01") for position, number in enumerate(numbers)]
    return make_file(tmp_path / "small.sqlite", rows, run_date="2026-11-24"), links, numbers


def test_example_old_fields_are_unchanged_and_each_trial_card_gains_three(tmp_path, before):
    path, links, _ = small_file(tmp_path)
    with patch.object(trials_module, "TRIALS_PATH", path), TestClient(api.app):
        after = saved_page()
    assert set(after) == set(before)
    for key in before:
        if key in ("being_studied", "more_in_trials", "new_in_trials"):
            assert len(after[key]) == len(before[key])
            # Ticket 3.31 re-sorts the two folded boxes (newest trial first), so
            # cards are paired by id, not by place. Nothing else is relaxed.
            if key != "being_studied":
                assert sorted(c["id"] for c in after[key]) == sorted(c["id"] for c in before[key])
            else:
                assert [c["id"] for c in after[key]] == [c["id"] for c in before[key]]
            old_by_id = {c["id"]: c for c in before[key]}
            for new in after[key]:
                old = old_by_id[new["id"]]
                assert set(new) - set(old) == NEW_KEYS
                assert {k: v for k, v in new.items() if k not in NEW_KEYS} == old
        else:
            assert after[key] == before[key]
    assert len(before["being_studied"]) >= 5 and "more_in_trials" in before and "new_in_trials" in before


def test_example_every_trial_card_has_its_trials_total_and_date(tmp_path, before):
    path, links, _ = small_file(tmp_path)
    with patch.object(trials_module, "TRIALS_PATH", path), TestClient(api.app):
        after = saved_page()
    for card in trial_cards(after):
        own = links.get(card["id"], [])
        assert card["trials_checked"] == "2026-11-24"
        assert card["study_total"] == len(own)
        assert len(card["studies"]) == min(3, len(own))
        assert all(set(item) == TRIAL_KEYS for item in card["studies"])
        assert len(set(ids(card["studies"]))) == len(card["studies"])
    sirolimus = next(card for card in after["being_studied"] if card["id"] == "CHEMBL413")
    assert sirolimus["study_total"] == 7 and len(sirolimus["studies"]) == 3


def test_example_the_three_shown_are_the_newest_of_that_cards_own_links(tmp_path):
    path, links, _ = small_file(tmp_path)
    with patch.object(trials_module, "TRIALS_PATH", path), TestClient(api.app):
        after = saved_page()
    card = next(card for card in after["being_studied"] if card["id"] == "CHEMBL413")
    own = [link.rsplit("/", 1)[1] for link in links["CHEMBL413"]]
    found = trials_module.Trials.open(path)
    expected = ids(found.for_card(set(links["CHEMBL413"]), ["Sirolimus"], today=datetime.date.today())[0])
    assert ids(card["studies"]) == expected
    assert set(ids(card["studies"])) <= set(own)


def test_example_a_card_with_no_trials_in_the_file_says_zero(tmp_path, before):
    path = make_file(tmp_path / "other.sqlite", [study("NCT99999990", "2015")])
    with patch.object(trials_module, "TRIALS_PATH", path), TestClient(api.app):
        after = saved_page()
    for card in trial_cards(after):
        assert card["studies"] == [] and card["study_total"] == 0
        assert card["trials_checked"] == "2026-11-26"


def test_example_cards_that_are_not_trial_cards_get_no_new_fields(tmp_path):
    path, _, _ = small_file(tmp_path)
    with patch.object(trials_module, "TRIALS_PATH", path), TestClient(api.app):
        after = saved_page()
    for key in ("approved", "new_clues", "narrower", "wider_group"):
        for card in after.get(key, []):
            assert not NEW_KEYS & set(card)


def test_example_missing_file_serves_exactly_as_today_and_logs_it(tmp_path, caplog, before):
    missing = tmp_path / "gone.sqlite"
    with caplog.at_level(logging.WARNING):
        with patch.object(trials_module, "TRIALS_PATH", missing), TestClient(api.app):
            answer = saved_page()
    assert answer == before
    assert not any(NEW_KEYS & set(card) for card in trial_cards(answer))
    assert "gone.sqlite" in caplog.text


def test_example_the_file_is_opened_once_at_start_not_once_a_request(tmp_path):
    path, _, _ = small_file(tmp_path)
    opened = []
    real_open = trials_module.Trials.open

    def counting_open(*args, **kwargs):
        opened.append(1)
        return real_open(*args, **kwargs)

    with patch.object(trials_module, "TRIALS_PATH", path), \
            patch.object(trials_module.Trials, "open", side_effect=counting_open):
        with TestClient(api.app) as client:
            for _ in range(3):
                api.forget_answers()
                with patch("moonlight.fetch._post_json", side_effect=adpkd_page.saved_post_json):
                    assert client.get("/api/clues", params={"disease_id": adpkd_page.ADPKD}).status_code == 200
    assert opened == [1]


def test_example_without_the_app_starting_nothing_is_added(before):
    """A TestClient that never starts the app (as every old test does) sees today's page."""
    assert api._trials is None
    assert not any(NEW_KEYS & set(card) for card in trial_cards(before))


def test_example_the_file_is_closed_when_the_app_stops(tmp_path):
    path, _, _ = small_file(tmp_path)
    with patch.object(trials_module, "TRIALS_PATH", path):
        with TestClient(api.app):
            assert api._trials is not None
        assert api._trials is None


def test_example_a_broken_lookup_serves_the_page_as_today(tmp_path, caplog, before):
    path, _, _ = small_file(tmp_path)
    with patch.object(trials_module, "TRIALS_PATH", path), TestClient(api.app):
        with patch.object(trials_module.Trials, "for_card", side_effect=sqlite3.DatabaseError("broken")):
            with caplog.at_level(logging.WARNING):
                answer = saved_page()
    assert answer == before
    assert "broken" in caplog.text or "trials" in caplog.text.lower()


# ------------------------------------------------------------ the size check

@pytest.mark.skipif(not REAL_FILE.exists(), reason="no moonlight/trials.sqlite")
def test_example_the_real_file_on_the_saved_adpkd_page_grows_the_answer_by_under_30_kb(before):
    with TestClient(api.app):
        assert api._trials is not None, "the real moonlight/trials.sqlite did not open"
        after = saved_page()
    grew = len(json.dumps(after)) - len(json.dumps(before))
    assert 0 < grew < 30 * 1024, grew
    assert all("trials_checked" in card for card in trial_cards(after))
    assert any(card["study_total"] > 0 for card in trial_cards(after))


# ------------------------------------------------ ticket T4: the API sends the links

def test_t4_each_trial_has_its_clinicaltrials_page(tmp_path):
    path = make_file(tmp_path / "t.sqlite", [study("NCT00000001", "2019-07-15"), study("NCT00000002", "2020")])
    shown, _ = open_file(path).for_card({LINK + "NCT00000001", LINK + "NCT00000002"}, ["Sirolimus"], today=TODAY)
    assert [item["url"] for item in shown] == ["https://clinicaltrials.gov/study/NCT00000002",
                                               "https://clinicaltrials.gov/study/NCT00000001"]


def test_t4_studies_url_is_the_register_search_for_the_disease_and_the_medicine(tmp_path):
    path = make_file(tmp_path / "t.sqlite", [study("NCT00000001", "2019")])
    found = open_file(path).for_cards([({LINK + "NCT00000001"}, ["Sirolimus", "Sirolimus tablet"])],
                                      today=TODAY, disease_name="polycystic kidney disease, autosomal dominant")
    assert found[0]["studies_url"] == ("https://clinicaltrials.gov/search?cond="
                                       "polycystic%20kidney%20disease%2C%20autosomal%20dominant&intr=Sirolimus")


def test_t4_without_a_disease_name_there_is_no_studies_url(tmp_path):
    path = make_file(tmp_path / "t.sqlite", [study("NCT00000001", "2019")])
    found = open_file(path).for_cards([({LINK + "NCT00000001"}, ["Sirolimus"])], today=TODAY)
    assert "studies_url" not in found[0]


def test_t4_the_api_gives_every_trial_card_a_studies_url_with_the_pages_disease(tmp_path, before):
    path, _, _ = small_file(tmp_path)
    with patch.object(trials_module, "TRIALS_PATH", path), TestClient(api.app):
        after = saved_page()
    name = after["disease"]["name"]
    for card in trial_cards(after):
        assert card["studies_url"].startswith("https://clinicaltrials.gov/search?cond=" + quote(name, safe="") + "&intr=")
        assert card["studies_url"].endswith("&intr=" + quote(card["medicine"], safe=""))
        assert all(item["url"] == LINK + item["nct_id"] for item in card["studies"])
