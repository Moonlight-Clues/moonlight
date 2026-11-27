"""Ticket 3.31. The two folded trial boxes, newest trial first.

THE TICKET
  "More medicines in trials" and "New medicines being tested" are sorted by
  the start date of each card's newest trial, newest first. The unknown-date
  rules are trials.py's: missing, before 1950 or more than 10 years from today
  is unknown. Ties keep today's order (highest phase, then A to Z); cards with
  no known date go last, in today's order; the sort is stable. With no
  trials file the order is unchanged. The main In trials list and the
  "Found only on ClinicalTrials.gov" box are not touched. The date is
  internal: no card carries it.

HOW THESE TESTS WORK (no network)
  * PAH: the two boxes of the saved answer of ticket 2.52 (fixtures/labels_read),
    in the order the answer holds them. Each card gets a pretend trial in a
    small trials file built with scripts/build_trials.py's own writer, with
    start dates that are known, tied, missing, too old and too far ahead.
    `_add_trials` is the real function.
  * The saved answer has no trial links, so the PAH cards' links are made up
    here: one trial per card (two for some, so "newest of all" is tested).
  * Whole-page order on the saved ADPKD page is checked in test_trials_t3.py.
  * PSC: there is no saved PSC answer in fixtures/. It is only in the live check.
"""

import copy
import datetime
import importlib.util
import json
import pathlib
import sqlite3
from unittest.mock import patch

import pytest

from moonlight import api
from moonlight import trials as trials_module

ROOT = pathlib.Path(__file__).resolve().parent.parent
PAH_FILE = ROOT / "fixtures" / "labels_read" / "2.52" / "page_answers" / "MONDO_0015924.clues.json"
PAH = json.loads(PAH_FILE.read_text(encoding="utf-8"))
TODAY = datetime.date.today()
LINK = "https://clinicaltrials.gov/study/"


def _builder():
    spec = importlib.util.spec_from_file_location("build_trials", ROOT / "scripts" / "build_trials.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


bt = _builder()


def study(nct, start):
    state = {"overallStatus": "COMPLETED"}
    if start is not None:
        state["startDateStruct"] = {"date": start, "type": "ACTUAL"}
    return nct, {"protocolSection": {
        "identificationModule": {"nctId": nct, "briefTitle": "A study " + nct},
        "statusModule": state,
        "designModule": {"studyType": "INTERVENTIONAL", "phases": ["PHASE2"]},
        "armsInterventionsModule": {
            "armGroups": [{"label": "A", "type": "EXPERIMENTAL", "interventionNames": ["X"]}],
            "interventions": [{"name": "X", "type": "DRUG", "armGroupLabels": ["A"]}]}}}


def make_file(path, rows):
    rows = sorted(rows, key=lambda row: row[0])
    bt.write_sqlite(path, rows, {"run_date": "2026-11-26", "counts": {"kept_interventional": len(rows)},
                                 "ctgov_api_version": "2.0.5",
                                 "ctgov_data_timestamp": "2026-11-25T10:00:05"})
    return path


def card(card_id, name, **extra):
    return {"id": card_id, "medicine": name, "forms": [], "trial_phase": "Phase 2", **extra}


def run(boxes, links, rows, tmp_path, listed=None):
    """Run the real _add_trials on boxes (a dict name -> list of cards)."""
    path = make_file(tmp_path / "t.sqlite", rows)
    opened = trials_module.Trials.open(path)
    every = listed if listed is not None else [c for box in boxes.values() for c in box]
    try:
        with patch.object(api, "_trials", opened):
            api._add_trials(every, links, "a disease", boxes=list(boxes.values()))
    finally:
        opened.close()


def names(box):
    return [c["medicine"] for c in box]


# ------------------------------------------------ the sort, on small boxes

def test_newest_trial_first_and_ties_keep_the_old_order(tmp_path):
    box = [card("A", "Alpha"), card("B", "Beta"), card("C", "Gamma"), card("D", "Delta")]
    links = {"A": {LINK + "NCT00000001"}, "B": {LINK + "NCT00000002"},
             "C": {LINK + "NCT00000003"}, "D": {LINK + "NCT00000004"}}
    rows = [study("NCT00000001", "2015-01-01"), study("NCT00000002", "2023-05"),
            study("NCT00000003", "2023-05-01"), study("NCT00000004", "2019")]
    run({"new": box}, links, rows, tmp_path)
    # Beta and Gamma tie (2023-05-01), so Beta stays before Gamma.
    assert names(box) == ["Beta", "Gamma", "Delta", "Alpha"]


def test_a_tie_keeps_phase_then_a_to_z_order(tmp_path):
    box = [card("A", "Alpha", trial_phase="Phase 3"), card("B", "Bravo", trial_phase="Phase 3"),
           card("C", "Charlie", trial_phase="Phase 2"), card("D", "Delta", trial_phase="Phase 1")]
    links = {key: {LINK + "NCT0000000" + str(n)} for n, key in enumerate("ABCD", 1)}
    rows = [study("NCT0000000" + str(n), "2024-03-10") for n in range(1, 5)]
    before = names(box)
    run({"new": box}, links, rows, tmp_path)
    assert names(box) == before == ["Alpha", "Bravo", "Charlie", "Delta"]


def test_the_newest_of_all_a_cards_trials_counts_not_only_the_three_shown(tmp_path):
    box = [card("A", "Alpha"), card("B", "Beta")]
    links = {"A": {LINK + "NCT0000000" + str(n) for n in range(1, 6)}, "B": {LINK + "NCT00000009"}}
    rows = [study("NCT00000001", "2001"), study("NCT00000002", "2002"), study("NCT00000003", "2003"),
            study("NCT00000004", "2004"), study("NCT00000005", "2025-06"),
            study("NCT00000009", "2020")]
    run({"new": box}, links, rows, tmp_path)
    assert names(box) == ["Alpha", "Beta"]
    box = [card("B", "Beta"), card("A", "Alpha")]
    run({"new": box}, links, rows, tmp_path)
    assert names(box) == ["Alpha", "Beta"]


def test_unknown_dates_go_last_in_the_old_order(tmp_path):
    far = str(TODAY.year + 11) + "-01-01"
    box = [card("A", "Alpha"), card("B", "Beta"), card("C", "Gamma"), card("D", "Delta"),
           card("E", "Epsilon"), card("F", "Zeta")]
    links = {key: {LINK + "NCT0000000" + str(n)} for n, key in enumerate("ABCDE", 1)}
    # F has no trial in the file at all.
    rows = [study("NCT00000001", None),            # missing
            study("NCT00000002", "1949-12-31"),    # before 1950
            study("NCT00000003", far),             # more than 10 years ahead
            study("NCT00000004", "2010"),
            study("NCT00000005", "not a date")]
    run({"new": box}, links, rows, tmp_path)
    assert names(box) == ["Delta", "Alpha", "Beta", "Gamma", "Epsilon", "Zeta"]


def test_the_date_is_internal_and_never_on_a_card(tmp_path):
    box = [card("A", "Alpha")]
    run({"new": box}, {"A": {LINK + "NCT00000001"}}, [study("NCT00000001", "2020")], tmp_path)
    assert "newest_start" not in box[0]
    assert set(box[0]) - {"id", "medicine", "forms", "trial_phase"} == {
        "studies", "study_total", "trials_checked", "studies_url"}


def test_the_main_list_and_other_cards_are_not_sorted(tmp_path):
    main = [card("A", "Alpha"), card("B", "Beta")]
    box = [card("C", "Gamma"), card("D", "Delta")]
    links = {"A": {LINK + "NCT00000001"}, "B": {LINK + "NCT00000002"},
             "C": {LINK + "NCT00000003"}, "D": {LINK + "NCT00000004"}}
    rows = [study("NCT00000001", "2001"), study("NCT00000002", "2025"),
            study("NCT00000003", "2001"), study("NCT00000004", "2025")]
    run({"new": box}, links, rows, tmp_path, listed=main + box)
    assert names(main) == ["Alpha", "Beta"]  # main In trials list: highest phase first, as before
    assert names(box) == ["Delta", "Gamma"]
    assert all("studies" in c for c in main)


def test_with_no_trials_file_the_order_is_unchanged():
    box = [card("A", "Alpha"), card("B", "Beta"), card("C", "Gamma")]
    with patch.object(api, "_trials", None):
        api._add_trials(box, {}, "a disease", boxes=[box])
    assert names(box) == ["Alpha", "Beta", "Gamma"]
    assert all("studies" not in c for c in box)


def test_a_file_that_cannot_be_read_keeps_the_order_and_adds_nothing(tmp_path):
    box = [card("A", "Alpha"), card("B", "Beta")]
    path = make_file(tmp_path / "t.sqlite", [study("NCT00000001", "2001"), study("NCT00000002", "2025")])
    opened = trials_module.Trials.open(path)
    opened._con.close()  # damaged: every read now raises sqlite3.Error
    with patch.object(api, "_trials", opened):
        api._add_trials(box, {"A": {LINK + "NCT00000001"}, "B": {LINK + "NCT00000002"}}, "d", boxes=[box])
    assert names(box) == ["Alpha", "Beta"]
    assert all("studies" not in c for c in box)


# ------------------------------------------------ the PAH boxes (saved answer, 2.52)

def pah_boxes():
    return copy.deepcopy(PAH["more_in_trials"]), copy.deepcopy(PAH["new_in_trials"])


def pah_world():
    """One pretend trial per card in order of position; start dates repeat
    every 7th card (ties), every 5th card is missing and every 11th too old."""
    more, new = pah_boxes()
    links, rows, serial = {}, [], 0
    for box in (more, new):
        for position, one in enumerate(box):
            serial += 1
            nct = f"NCT{serial:08d}"
            links[one["id"]] = {LINK + nct}
            if position % 5 == 4:
                start = None
            elif position % 11 == 10:
                start = "1949-06"
            else:
                start = f"{2000 + (position * 7) % 25}-0{1 + position % 7}"
            rows.append(study(nct, start))
    return more, new, links, rows


def start_of(one, links, rows):
    nct = next(iter(links[one["id"]])).rsplit("/", 1)[1]
    start = dict(rows)[nct]["protocolSection"]["statusModule"].get("startDateStruct", {}).get("date")
    return trials_module.start_key(start, TODAY)


@pytest.mark.parametrize("which", [0, 1])
def test_pah_boxes_dates_never_rise_and_undated_cards_come_last_in_the_old_order(tmp_path, which):
    more, new, links, rows = pah_world()
    old = [names(more), names(new)]
    assert len(new) == 27 and len(more) > 0
    run({"more": more, "new": new}, links, rows, tmp_path)
    box = (more, new)[which]
    dates = [start_of(one, links, rows) for one in box]
    known_dates = [d for d in dates if d is not None]
    assert known_dates and len(known_dates) < len(dates)  # the data holds both kinds
    assert known_dates == sorted(known_dates, reverse=True)
    first_unknown = dates.index(None)
    assert all(d is None for d in dates[first_unknown:])  # no dated card after an undated one
    undated = [one["medicine"] for one in box if start_of(one, links, rows) is None]
    assert undated == [name for name in old[which] if name in undated]  # today's order
    dated_tie = {}
    for one in box:
        day = start_of(one, links, rows)
        if day is not None:
            dated_tie.setdefault(day, []).append(one["medicine"])
    for same in dated_tie.values():
        assert same == [name for name in old[which] if name in same]  # ties keep today's order
    assert sorted(names(box)) == sorted(old[which])  # nothing added, nothing lost


def test_pah_without_the_file_both_boxes_keep_todays_order_exactly():
    more, new = pah_boxes()
    old_more, old_new = copy.deepcopy(more), copy.deepcopy(new)
    with patch.object(api, "_trials", None):
        api._add_trials(more + new, {}, "pulmonary arterial hypertension", boxes=[more, new])
    assert more == old_more and new == old_new


def test_pah_first_twenty_of_the_new_box_are_the_twenty_newest(tmp_path):
    more, new, links, rows = pah_world()
    run({"more": more, "new": new}, links, rows, tmp_path)
    days = [start_of(one, links, rows) for one in new]
    shown = [d for d in days[:20]]
    rest = [d for d in days[20:]]
    newest_known_in_rest = max((d for d in rest if d is not None), default=None)
    if newest_known_in_rest is not None:
        assert all(d is not None and d >= newest_known_in_rest for d in shown)
    assert len(new) == 27  # "Show all 27" still has 27 to show


# ------------------------------------------------ through the whole API (saved ADPKD page)

def test_the_api_sorts_both_boxes_and_leaves_the_main_list_alone(tmp_path):
    import test_trials_t3 as t3
    with patch.object(trials_module, "TRIALS_PATH", pathlib.Path("/nonexistent/trials.sqlite")):
        with t3.TestClient(api.app):
            before = t3.saved_page()
    path, links, numbers = t3.small_file(tmp_path)
    with patch.object(trials_module, "TRIALS_PATH", path), t3.TestClient(api.app):
        after = t3.saved_page()
    # small_file gives each NCT number a start year by its position in the sorted numbers.
    year = {number: 1990 + position % 35 for position, number in enumerate(numbers)}

    def newest(one):
        return max(year[link.rsplit("/", 1)[1]] for link in links[one["id"]]
                   if link.rsplit("/", 1)[1] in year)

    assert [c["id"] for c in after["being_studied"]] == [c["id"] for c in before["being_studied"]]
    for key in ("more_in_trials", "new_in_trials"):
        old_ids = [c["id"] for c in before[key]]
        got = after[key]
        assert sorted(c["id"] for c in got) == sorted(old_ids) and len(got) > 1
        years = [newest(c) for c in got]
        assert years == sorted(years, reverse=True)
        for same in set(years):  # ties keep today's order
            ids_here = [c["id"] for c in got if newest(c) == same]
            assert ids_here == [i for i in old_ids if i in ids_here]
        assert not any("newest_start" in c for c in got)
