"""Ticket 2.61 (MAIN 4, 26 Nov). Givosiran on acute hepatic porphyria.

Product's Task 20 (task20_label_reads.csv, 26 Nov): on the page "Acute hepatic
porphyria" (Orphanet_95157) givosiran (CHEMBL4297760) sat in the no-regulator
box with a ClinicalTrials.gov source, although both current labels name the
disease. The FDA label (DailyMed setid 167e663c-..., 10 Sep 2025) was opened
once in the session and the sentence below confirmed word for word.

Lists only: one row in confirmed.json, one row in source_overrides.json.
Not in this ticket: givosiran on acute intermittent porphyria (MONDO_0008294)
and the second card, Givosiran Sodium (CHEMBL4594265, error E52).

Saved answers only, no network. The two lists on main 4283400 are saved in
fixtures/givosiran_2_61/ so "one row more, none lost" can be checked.
"""

import json
import pathlib
from unittest.mock import patch

import pytest

from moonlight import api, engine

import test_approvals_batch as second_batch
import test_approvals_by_hand as first_batch

ROOT = pathlib.Path(__file__).resolve().parent.parent
SAVED = ROOT / "fixtures" / "givosiran_2_61"
CONFIRMED_FILE = ROOT / "moonlight" / "confirmed.json"
OVERRIDES_FILE = ROOT / "moonlight" / "source_overrides.json"
AIP_LISTS = ROOT / "fixtures" / "labels_read" / "2.46" / "disease_drugs"

GIVOSIRAN, GIVOSIRAN_SODIUM = "CHEMBL4297760", "CHEMBL4594265"
AHP, AIP = "Orphanet_95157", "MONDO_0008294"
LABEL = ("https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm"
         "?setid=167e663c-11e1-497b-a3fc-951d65d58eaa")
OLD_TRIAL = "https://clinicaltrials.gov/study/NCT04056481"
FDA_SENTENCE = "GIVLAARI is indicated for the treatment of adults with acute hepatic porphyria (AHP)."
NO_REGULATOR_LINE = "The database lists this as approved, but gives no regulator record for it."

CONFIRMED_ROW = {"medicine_id": GIVOSIRAN, "disease_id": AHP, "date": "2026-11-26", "label": LABEL}
OVERRIDE_ROW = {"medicine_id": GIVOSIRAN, "disease_id": AHP, "url": LABEL, "date": "2025-09-10",
                "note": FDA_SENTENCE, "evidence_file": "task20_label_reads.csv"}


def load(file):
    return json.loads(file.read_text(encoding="utf-8"))


def saved_post_json(body):
    """Stands in for fetch._post_json: each disease's own saved list."""
    assert set(body) == {"query", "variables"}
    asked = body["variables"]["diseaseId"]
    for folder in (first_batch.REUSED, first_batch.SAVED, AIP_LISTS):
        file = folder / "disease_drugs" / f"{asked}.response.json" if folder != AIP_LISTS \
            else folder / f"{asked}.response.json"
        if file.exists():
            return load(file)
    raise AssertionError(f"no saved list for {asked}")


@pytest.fixture(autouse=True)
def offline():
    api.forget_visitors()
    with patch("requests.request", side_effect=AssertionError("network used")), \
            patch("requests.post", side_effect=AssertionError("network used")), \
            patch("requests.get", side_effect=AssertionError("network used")), \
            patch("requests.sessions.Session.request", side_effect=AssertionError("network used")), \
            patch("moonlight.fetch._post_json", side_effect=saved_post_json):
        yield
    api.forget_visitors()


def page(disease_id, confirmed=None, overrides=None):
    """What the page's Approved tab is built from, as api.py builds it:
    the tabs, then confirm_by_label, then override_sources. Optionally with
    the lists as they were on 4283400."""
    guards = []
    if confirmed is not None:
        guards.append(patch.object(engine, "_read_confirmed", return_value=confirmed))
    if overrides is not None:
        guards.append(patch.object(engine, "_read_source_overrides", return_value=overrides))
    for guard in guards:
        guard.start()
    try:
        tabs = second_batch.tabs_for(disease_id, engine.added_by_hand(disease_id))
        main = engine.override_sources(engine.confirm_by_label(tabs.approved, disease_id),
                                       disease_id)
        box = [m.id for m in engine.no_regulator_box(main, disease_id)]
        cards = {m.id: api._approved_json(m) for m in main}
    finally:
        for guard in guards:
            guard.stop()
    return {"main": [m.id for m in main if m.id not in box], "box": box, "cards": cards}


BASE_CONFIRMED = load(SAVED / "confirmed_4283400.json")
BASE_OVERRIDES = load(SAVED / "source_overrides_4283400.json")


@pytest.fixture(scope="module")
def before():
    return page(AHP, BASE_CONFIRMED, BASE_OVERRIDES)


@pytest.fixture(scope="module")
def now():
    return page(AHP)


# ---- the two lists: exactly one row more each ----

def test_confirmed_json_is_the_base_plus_exactly_one_row_at_the_end():
    now = load(CONFIRMED_FILE)
    assert len(BASE_CONFIRMED) == 33
    assert len(now) == 34
    assert now[:33] == BASE_CONFIRMED  # none lost, none changed, same order
    assert now[33:] == [CONFIRMED_ROW]


def test_source_overrides_json_is_the_base_plus_exactly_one_row_at_the_end():
    now = load(OVERRIDES_FILE)
    assert len(BASE_OVERRIDES) == 56
    assert len(now) == 57
    assert now[:56] == BASE_OVERRIDES
    assert now[56:] == [OVERRIDE_ROW]


def test_the_engine_reads_both_new_rows_once():
    assert engine.confirmed_by_label()[(GIVOSIRAN, AHP)] == LABEL
    assert engine.source_overrides()[(GIVOSIRAN, AHP)] == LABEL
    pairs = [(e["medicine_id"], e["disease_id"]) for e in load(OVERRIDES_FILE)]
    assert pairs.count((GIVOSIRAN, AHP)) == 1


# ---- acute hepatic porphyria ----

def test_before_givosiran_was_in_the_no_regulator_box_with_a_trial_source(before):
    assert GIVOSIRAN in before["box"]
    assert GIVOSIRAN not in before["main"]
    assert before["cards"][GIVOSIRAN]["source"] == OLD_TRIAL
    assert before["cards"][GIVOSIRAN]["proof_note"] == NO_REGULATOR_LINE


def test_givosiran_is_on_the_main_list_not_in_the_no_regulator_box(now):
    assert GIVOSIRAN in now["main"]
    assert GIVOSIRAN not in now["box"]


def test_givosirans_source_record_is_the_dailymed_link(now):
    assert now["cards"][GIVOSIRAN]["source"] == LABEL


def test_givosiran_has_no_no_regulator_line(now):
    assert "proof_note" not in now["cards"][GIVOSIRAN]


def test_every_other_card_keeps_its_seat_and_its_source_record(before, now):
    others = [i for i in before["cards"] if i != GIVOSIRAN]
    assert others == [GIVOSIRAN_SODIUM]  # the whole list has two cards
    assert now["cards"][GIVOSIRAN_SODIUM] == before["cards"][GIVOSIRAN_SODIUM]
    assert GIVOSIRAN_SODIUM in now["main"] and GIVOSIRAN_SODIUM in before["main"]
    assert set(now["cards"]) == set(before["cards"])


# ---- acute intermittent porphyria: unchanged ----

def test_acute_intermittent_porphyria_is_unchanged():
    new = page(AIP)
    old = page(AIP, BASE_CONFIRMED, BASE_OVERRIDES)
    assert new == old
    assert GIVOSIRAN not in new["cards"]
