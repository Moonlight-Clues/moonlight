"""Ticket 2.43. Leave out blood thinners (haemophilia A), cortisol-lowering
clues (Addison's) and imaging agents. List entries only: moonlight/left_out.json.

Decisions spoken on 24 Nov 2026 (to be signed on the next sheet):
  R1: blood thinners are not clues on the haemophilia A page, and medicines
      that lower or block cortisol are not clues on the Addison's page.
  R6: imaging tracers and contrast agents are not in the medicine lists.

The list takes a medicine out of New clues and out of the two trials boxes.
It never touches the Approved tab, or the "Already being studied" list.

Saved files only: fixtures/left_out_r1_r6/<page>.cards.json holds every card
of each page, tab by tab, as the live /api/clues on main answered on
2026-11-24 (Open Targets data 26.09). The tests build each page from those
cards and ask the real /api/clues, with the real left-out file. No network.
"""

import json
import pathlib
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from moonlight import api, engine
from moonlight.engine import TrialMedicine
from moonlight.filter import sort_paths
from moonlight.records import Disease, Medicine, MedicineForm, Path, Target

ROOT = pathlib.Path(__file__).resolve().parent.parent
LEFT_OUT_FILE = ROOT / "moonlight" / "left_out.json"
SAVED = ROOT / "fixtures" / "left_out_r1_r6"
THE_DAY = "2026-11-24"

HAEMOPHILIA_A = "MONDO_0010602"  # hemophilia A
ADDISON = "MONDO_0015129"  # chronic primary adrenal insufficiency, also called "Addison disease"
PROSTATE = "MONDO_0008315"  # prostate cancer
SPINAL_CORD = "MONDO_0043797"  # spinal cord injury
GRAVES = "MONDO_0005364"  # Graves disease

# The new entries, page by page, in the ticket's order. Names are for the
# reader; they are not in the file.
NEW = {
    HAEMOPHILIA_A: [
        "CHEMBL198362",   # rivaroxaban
        "CHEMBL231779",   # apixaban
        "CHEMBL1269025",  # edoxaban
        "CHEMBL4650299",  # heparin
        "CHEMBL1201657",  # heparin sodium (its own card)
        "CHEMBL1201513",  # heparin calcium (its own card)
        "CHEMBL1201476",  # enoxaparin sodium
        "CHEMBL1201460",  # dalteparin sodium
        "CHEMBL1201414",  # tinzaparin sodium
        "CHEMBL1201202",  # fondaparinux
    ],
    ADDISON: [
        "CHEMBL1276308",  # mifepristone
    ],
    PROSTATE: [
        "CHEMBL4650356",  # "Fapi GA-68"
        "CHEMBL3578202",  # gozetotide: "Gallium Ga 68 Gozetotide"
        "CHEMBL539",      # acetic acid: its only form here is "Acetic Acid C-11"
        "CHEMBL4297855",  # "Technetium TC-99M Trofolastat Chloride"
        "CHEMBL4650432",  # "Zirconium ZR-89-DESFERRIOXAMINE-IAB22M2C"
    ],
}
NEW_ENTRIES = [{"medicine_id": medicine_id, "disease_id": disease_id, "date": THE_DAY}
               for disease_id, ids in NEW.items() for medicine_id in ids]

# Named in the ticket, but on the APPROVED tab: the list cannot touch them,
# so no entry. Reported for tomorrow's code change.
ON_APPROVED_TAB = {
    PROSTATE: {"CHEMBL920": "approved",           # choline C-11
               "CHEMBL1908917": "approved",       # fluciclovine F18
               "CHEMBL4299851": "wider_group"},   # piflufolastat F18 (not named, imaging)
    SPINAL_CORD: {"CHEMBL951": "approved"},       # iophendylate
    GRAVES: {"CHEMBL1201243": "approved"},        # ipodate
}
# Named in the ticket, already left out on 19 Nov: not on the page.
ADDISON_ALREADY = {"CHEMBL295698", "CHEMBL1670", "CHEMBL3099695", "CHEMBL934"}

PROTEIN = Target("ENSG00000000001", "ABC1", "test protein", 0.8)
CLUE_TABS = ("new_clues",)
TRIAL_BOXES = ("more_in_trials", "new_in_trials")


def load(file):
    return json.loads(file.read_text(encoding="utf-8"))


def saved(disease_id):
    cards = load(SAVED / f"{disease_id}.cards.json")
    assert cards["disease"]["id"] == disease_id
    return cards


def ids(cards, tabs):
    return [medicine_id for tab in tabs for medicine_id, _ in cards.get(tab, [])]


@pytest.fixture(autouse=True)
def offline():
    """Real HTTP is an error."""
    api.forget_visitors()
    with patch("requests.request", side_effect=AssertionError("network used")), \
            patch("requests.post", side_effect=AssertionError("network used")), \
            patch("requests.get", side_effect=AssertionError("network used")), \
            patch("requests.sessions.Session.request",
                  side_effect=AssertionError("network used")):
        yield
    api.forget_visitors()


def clue_path(name, medicine_id, disease):
    form = MedicineForm(medicine_id, name, best_stage="APPROVAL", disease_stage=None,
                        withdrawn=False)
    return Path(Medicine(name, (form,)), PROTEIN, disease, ("INHIBITOR",), PROTEIN.score,
                (f"https://example.org/{medicine_id}",))


def trial(name, medicine_id):
    return TrialMedicine(medicine_id, name, (name,), "PHASE_2",
                         (f"https://example.org/{medicine_id}",))


def page(disease_id, entries=None):
    """The saved page's New clues and both trials boxes, through the real
    /api/clues, with the REAL left-out file or with these entries."""
    cards = saved(disease_id)
    disease = Disease(disease_id, cards["disease"]["name"])
    paths = [clue_path(name, medicine_id, disease) for medicine_id, name in cards["new_clues"]]
    found = api._Found(disease, sort_paths(paths), [], [], [])
    found.more_in_trials = [trial(name, i) for i, name in cards["more_in_trials"]]
    found.new_in_trials = [trial(name, i) for i, name in cards["new_in_trials"]]
    with patch.object(api, "_find", return_value=found), \
            patch.object(engine, "_read_corrections", return_value=[]):
        if entries is None:
            response = TestClient(api.app).get("/api/clues", params={"disease_id": disease_id})
        else:
            with patch.object(engine, "_read_left_out", return_value=entries):
                response = TestClient(api.app).get("/api/clues",
                                                   params={"disease_id": disease_id})
    assert response.status_code == 200
    return response.json()


def shown(answer, tabs):
    return [card["id"] for tab in tabs for card in answer.get(tab, [])]


# ---- the file ----

def test_the_file_holds_the_37_old_entries_then_the_new_ones():
    entries = load(LEFT_OUT_FILE)
    assert len(entries) == 37 + 16
    assert entries[37:] == NEW_ENTRIES
    assert all(entry["date"] < THE_DAY for entry in entries[:37])


def test_no_pair_is_written_twice():
    pairs = [(entry["medicine_id"], entry["disease_id"]) for entry in load(LEFT_OUT_FILE)]
    assert len(pairs) == len(set(pairs))


def test_the_engine_reads_each_pages_new_entries():
    assert engine.pushes_wrong_way(HAEMOPHILIA_A) == set(NEW[HAEMOPHILIA_A])
    assert engine.pushes_wrong_way(ADDISON) == ADDISON_ALREADY | set(NEW[ADDISON])
    assert engine.pushes_wrong_way(PROSTATE) == set(NEW[PROSTATE])
    assert engine.pushes_wrong_way(SPINAL_CORD) == set()
    assert engine.pushes_wrong_way(GRAVES) == set()


# ---- every entry is a card that was a new clue or in a trials box ----

@pytest.mark.parametrize("disease_id", list(NEW))
def test_each_new_entry_was_on_its_page_as_a_new_clue_or_in_a_trials_box(disease_id):
    cards = saved(disease_id)
    for medicine_id in NEW[disease_id]:
        places = [tab for tab in ("approved", "narrower", "wider_group", "being_studied",
                                  "new_clues", "more_in_trials", "new_in_trials")
                  if medicine_id in ids(cards, (tab,))]
        assert len(places) == 1 and places[0] in CLUE_TABS + TRIAL_BOXES, medicine_id


def test_the_blood_thinners_were_new_clues_and_mifepristone_too():
    for disease_id in (HAEMOPHILIA_A, ADDISON):
        assert set(NEW[disease_id]) <= set(ids(saved(disease_id), CLUE_TABS))


def test_each_imaging_card_names_an_imaging_isotope():
    names = dict(saved(PROSTATE)["more_in_trials"] + saved(PROSTATE)["new_in_trials"])
    assert [names[medicine_id] for medicine_id in NEW[PROSTATE]] == [
        "Fapi GA-68", "Gozetotide", "Acetic Acid",
        "Technetium TC-99M Trofolastat Chloride",
        "Zirconium ZR-89-DESFERRIOXAMINE-IAB22M2C"]


@pytest.mark.parametrize("disease_id", list(ON_APPROVED_TAB))
def test_the_named_medicines_on_the_approved_tab_get_no_entry(disease_id):
    cards = saved(disease_id)
    for medicine_id, tab in ON_APPROVED_TAB[disease_id].items():
        assert medicine_id in ids(cards, (tab,))
        assert medicine_id not in engine.pushes_wrong_way(disease_id)


def test_the_four_already_left_out_for_addisons_are_not_on_the_saved_page():
    cards = saved(ADDISON)
    every = ids(cards, ("approved", "narrower", "wider_group", "being_studied",
                        "new_clues", "more_in_trials", "new_in_trials"))
    assert not ADDISON_ALREADY & set(every)
    assert cards["wrong_way_line"] == (
        "4 medicines left out because they push the wrong way for this disease.")


# ---- the pages, through the real /api/clues ----

@pytest.mark.parametrize("disease_id", list(NEW))
def test_before_the_named_medicines_were_on_the_page(disease_id):
    old = [entry for entry in load(LEFT_OUT_FILE) if entry["date"] < THE_DAY]
    answer = page(disease_id, old)
    assert set(NEW[disease_id]) <= set(shown(answer, CLUE_TABS + TRIAL_BOXES))


@pytest.mark.parametrize("disease_id", list(NEW))
def test_now_they_are_gone_from_new_clues_and_both_trials_boxes(disease_id):
    answer = page(disease_id)
    assert not set(NEW[disease_id]) & set(shown(answer, CLUE_TABS + TRIAL_BOXES))


@pytest.mark.parametrize("disease_id", list(NEW))
def test_every_other_card_stays_in_its_order(disease_id):
    cards = saved(disease_id)
    answer = page(disease_id)
    for tab in CLUE_TABS + TRIAL_BOXES:
        expected = [i for i in ids(cards, (tab,)) if i not in NEW[disease_id]]
        assert sorted(shown(answer, (tab,))) == sorted(expected)
    for tab in TRIAL_BOXES:  # the boxes keep their order
        assert shown(answer, (tab,)) == [i for i in ids(cards, (tab,))
                                          if i not in NEW[disease_id]]


@pytest.mark.parametrize("disease_id, count", [(HAEMOPHILIA_A, 10), (ADDISON, 1),
                                               (PROSTATE, 0)])
def test_the_wrong_way_line_counts_only_the_new_clues_taken_out(disease_id, count):
    """The line counts new clues only. Mifepristone is the one new clue on
    the saved Addison's page; the four of 19 Nov were already off it."""
    answer = page(disease_id)
    if count:
        assert answer["wrong_way_line"] == engine.wrong_way_line(count)
        assert answer["wrong_way_line"].startswith(f"{count} medicine")
    else:
        assert "wrong_way_line" not in answer


@pytest.mark.parametrize("disease_id", [SPINAL_CORD, GRAVES])
def test_spinal_cord_injury_and_graves_disease_pages_are_unchanged(disease_id):
    cards = saved(disease_id)
    answer = page(disease_id)
    for tab in CLUE_TABS + TRIAL_BOXES:
        assert sorted(shown(answer, (tab,))) == sorted(ids(cards, (tab,)))


def test_the_same_medicines_stay_on_other_pages():
    for disease_id, medicine_ids in NEW.items():
        for other in (HAEMOPHILIA_A, ADDISON, PROSTATE, "MONDO_0015128", "MONDO_0005159"):
            if other != disease_id:
                assert not set(medicine_ids) & engine.pushes_wrong_way(other)
