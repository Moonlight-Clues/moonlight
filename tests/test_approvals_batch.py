"""Ticket 2.30. Approvals by hand, second batch.

Kashish and Shreshth, 23 Nov:

1. Three more entries in moonlight/approvals.json, dated 2026-11-23, each id
   found from Open Targets, not guessed:
     - daratumumab for AL amyloidosis (MONDO_0019438)
     - atrasentan for IgA glomerulonephritis (MONDO_0005342)
     - sibeprenlimab for IgA glomerulonephritis (MONDO_0005342)
2. An entry whose medicine is on left_out.json for that disease is not
   added.

Saved files only. The two diseases' own medicine lists are in
fixtures/approvals_by_hand/disease_drugs/, asked live on 2026-11-23 with
fetch.py's own question. The pages of ticket 2.26 are read from the answers
that ticket saved. No network.
"""

import json
import pathlib
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from moonlight import api, engine
from moonlight.engine import sort_into_tabs
from moonlight.fetch import fetch_approved, fetch_listed_medicines, fetch_withdrawn
from moonlight.filter import sort_paths
from moonlight.records import Disease

import test_approvals_by_hand as first_batch

ROOT = pathlib.Path(__file__).resolve().parent.parent
APPROVALS_FILE = ROOT / "moonlight" / "approvals.json"
CORRECTIONS_FILE = ROOT / "moonlight" / "corrections.json"
LEFT_OUT_FILE = ROOT / "moonlight" / "left_out.json"
SAVED_LISTS = ROOT / "fixtures" / "approvals_by_hand" / "disease_drugs"

LINE = "This approval is missing from the database. We added it from the official label."
THE_DAY = "2026-11-23"

AL_AMYLOIDOSIS = "MONDO_0019438"
IGA = "MONDO_0005342"
DARATUMUMAB = "CHEMBL1743007"
ATRASENTAN = "CHEMBL9194"
SIBEPRENLIMAB = "CHEMBL4594614"
DARATUMUMAB_LABEL = ("https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm"
                     "?setid=4bb241af-4299-4373-8762-2d6709515db0")
ATRASENTAN_LABEL = ("https://www.accessdata.fda.gov/drugsatfda_docs/label/2026/"
                    "219208Orig1s001Correctedlbl.pdf")
SIBEPRENLIMAB_LABEL = ("https://www.accessdata.fda.gov/drugsatfda_docs/label/2025/"
                       "761434s000lbl.pdf")

SECOND_BATCH = [
    {"medicine_id": DARATUMUMAB, "name": "Daratumumab", "disease_id": AL_AMYLOIDOSIS,
     "date": THE_DAY, "label": DARATUMUMAB_LABEL},
    {"medicine_id": ATRASENTAN, "name": "Atrasentan", "disease_id": IGA,
     "date": THE_DAY, "label": ATRASENTAN_LABEL},
    {"medicine_id": SIBEPRENLIMAB, "name": "Sibeprenlimab", "disease_id": IGA,
     "date": THE_DAY, "label": SIBEPRENLIMAB_LABEL},
]


def load(file):
    return json.loads(file.read_text(encoding="utf-8"))


def saved_rows(disease_id):
    answer = load(SAVED_LISTS / f"{disease_id}.response.json")
    assert answer["data"]["disease"]["id"] == disease_id
    return answer["data"]["disease"]["drugAndClinicalCandidates"]["rows"]


def left_out(medicine_id, disease_id):
    return {"medicine_id": medicine_id, "disease_id": disease_id, "date": THE_DAY}


@pytest.fixture(autouse=True)
def offline():
    """Real HTTP is an error. Every question is answered from saved files."""
    api.forget_visitors()
    with patch("requests.request", side_effect=AssertionError("network used")), \
            patch("requests.post", side_effect=AssertionError("network used")), \
            patch("requests.get", side_effect=AssertionError("network used")), \
            patch("requests.sessions.Session.request",
                  side_effect=AssertionError("network used")), \
            patch("moonlight.fetch._post_json", side_effect=first_batch.saved_post_json):
        yield
    api.forget_visitors()


# ---- the hand-written file ----

def test_the_real_file_holds_the_first_two_entries_then_the_three_new_ones():
    assert load(APPROVALS_FILE) == first_batch.FIRST_ENTRIES + SECOND_BATCH


def test_the_engine_reads_the_three_new_entries():
    assert engine.approvals_by_hand()[2:] == [
        engine.HandApproval(DARATUMUMAB, "Daratumumab", AL_AMYLOIDOSIS, DARATUMUMAB_LABEL),
        engine.HandApproval(ATRASENTAN, "Atrasentan", IGA, ATRASENTAN_LABEL),
        engine.HandApproval(SIBEPRENLIMAB, "Sibeprenlimab", IGA, SIBEPRENLIMAB_LABEL),
    ]


def test_each_new_entry_is_handed_only_to_its_own_disease():
    assert [entry.medicine_id for entry in engine.added_by_hand(AL_AMYLOIDOSIS)] == [DARATUMUMAB]
    assert [entry.medicine_id for entry in engine.added_by_hand(IGA)] == [
        ATRASENTAN, SIBEPRENLIMAB]


# ---- "Find each id from Open Targets; do not guess." ----

@pytest.mark.parametrize("disease_id, medicine_id, name", [
    (AL_AMYLOIDOSIS, DARATUMUMAB, "DARATUMUMAB"),
    (IGA, ATRASENTAN, "ATRASENTAN"),
    (IGA, SIBEPRENLIMAB, "SIBEPRENLIMAB"),
])
def test_the_ids_are_the_ones_open_targets_uses_in_the_saved_answers(
        disease_id, medicine_id, name):
    drugs = [row["drug"] for row in saved_rows(disease_id) if row["drug"]["id"] == medicine_id]
    assert [drug["name"] for drug in drugs] == [name]
    assert drugs[0]["parentMolecule"] is None  # it is the medicine, not a tablet form


@pytest.mark.parametrize("entry", SECOND_BATCH, ids=lambda entry: entry["name"])
def test_the_database_does_not_record_the_approval_so_the_line_is_true(entry):
    stages = [row["maxClinicalStage"] for row in saved_rows(entry["disease_id"])
              if row["drug"]["id"] == entry["medicine_id"]]
    assert stages == ["PHASE_3"]


@pytest.mark.parametrize("entry", SECOND_BATCH, ids=lambda entry: entry["name"])
def test_the_new_entries_clash_with_no_existing_rule(entry):
    pair = (entry["medicine_id"], entry["disease_id"])
    assert pair not in {(wrong["medicine_id"], wrong["disease_id"])
                        for wrong in load(CORRECTIONS_FILE)}
    assert pair not in {(out["medicine_id"], out["disease_id"]) for out in load(LEFT_OUT_FILE)}
    warnings = [warning["warningType"].lower()
                for row in saved_rows(entry["disease_id"])
                if row["drug"]["id"] == entry["medicine_id"]
                for drug in [row["drug"]] + row["drug"]["childMolecules"]
                for warning in drug["drugWarnings"]]
    assert "withdrawn" not in warnings


# ---- the EXAMPLE: the three medicines on their diseases' own saved lists ----

def tabs_for(disease_id, hand):
    """The tabs from the disease's own saved list alone (no protein search)."""
    disease = Disease(disease_id, "the disease")
    return sort_into_tabs(sort_paths([]), fetch_approved(disease),
                          withdrawn_listed=fetch_withdrawn(disease),
                          on_list=fetch_listed_medicines(disease), by_hand=hand)


@pytest.mark.parametrize("disease_id, medicine_ids", [
    (AL_AMYLOIDOSIS, [DARATUMUMAB]),
    (IGA, [ATRASENTAN, SIBEPRENLIMAB]),
])
def test_before_each_medicine_was_in_a_trials_box_and_not_under_approved(
        disease_id, medicine_ids):
    places = first_batch.everywhere(tabs_for(disease_id, []))
    for medicine_id in medicine_ids:
        assert medicine_id not in places["approved"]
        assert [place for place, ids in places.items() if medicine_id in ids] in (
            ["more_in_trials"], ["new_in_trials"])


@pytest.mark.parametrize("disease_id, entries", [
    (AL_AMYLOIDOSIS, SECOND_BATCH[:1]),
    (IGA, SECOND_BATCH[1:]),
])
def test_each_medicine_is_now_only_under_approved_with_the_line_and_its_label(
        disease_id, entries):
    before = tabs_for(disease_id, [])
    tabs = tabs_for(disease_id, engine.added_by_hand(disease_id))
    for entry in entries:
        assert first_batch.only_under_approved(tabs, entry["medicine_id"])
        card = [medicine for medicine in tabs.approved if medicine.id == entry["medicine_id"]][0]
        assert card.name == entry["name"]
        assert card.proof_note == LINE
        assert card.source_record == entry["label"]
        assert card.label is None  # the main list, not a folded box
    assert len(tabs.approved) == len(before.approved) + len(entries)
    names = [medicine.name.lower() for medicine in tabs.approved]
    assert names == sorted(names)  # A to Z, as the list already was
    # Every other card stays where it was.
    moved = {entry["medicine_id"] for entry in entries}
    for place, ids in first_batch.everywhere(before).items():
        if place != "approved":
            assert first_batch.everywhere(tabs)[place] == [i for i in ids if i not in moved]


# ---- "An entry whose medicine is on left_out.json for that disease is not added." ----

def test_no_entry_in_the_real_files_clashes():
    out = {(entry["medicine_id"], entry["disease_id"]) for entry in load(LEFT_OUT_FILE)}
    for entry in load(APPROVALS_FILE):
        assert (entry["medicine_id"], entry["disease_id"]) not in out
    assert engine.approvals_left_out() == []


def test_an_entry_on_the_left_out_list_for_its_disease_is_not_added():
    with patch.object(engine, "_read_left_out",
                      return_value=[left_out(ATRASENTAN, IGA)]):
        assert [entry.medicine_id for entry in engine.added_by_hand(IGA)] == [SIBEPRENLIMAB]
        assert [entry.medicine_id for entry in engine.added_by_hand(AL_AMYLOIDOSIS)] == [
            DARATUMUMAB]
        tabs = tabs_for(IGA, engine.added_by_hand(IGA))
    assert ATRASENTAN not in first_batch.everywhere(tabs)["approved"]
    assert first_batch.only_under_approved(tabs, SIBEPRENLIMAB)


def test_the_clash_is_reported():
    with patch.object(engine, "_read_left_out",
                      return_value=[left_out(ATRASENTAN, IGA)]):
        assert engine.approvals_left_out() == [
            engine.HandApproval(ATRASENTAN, "Atrasentan", IGA, ATRASENTAN_LABEL)]


def test_left_out_for_another_disease_does_not_stop_the_entry():
    with patch.object(engine, "_read_left_out",
                      return_value=[left_out(ATRASENTAN, AL_AMYLOIDOSIS)]):
        assert [entry.medicine_id for entry in engine.added_by_hand(IGA)] == [
            ATRASENTAN, SIBEPRENLIMAB]
        assert engine.approvals_left_out() == []


def test_the_whole_page_is_as_it_was_before_the_entry():
    # Ticket 2.26's saved page: propranolol for essential tremor.
    clash = [left_out(first_batch.PROPRANOLOL, first_batch.ESSENTIAL_TREMOR)]
    with patch.object(engine, "_read_left_out", return_value=clash):
        response = TestClient(api.app).get(
            "/api/clues", params={"disease_id": first_batch.ESSENTIAL_TREMOR})
    assert response.status_code == 200
    assert response.json() == first_batch.before(first_batch.ESSENTIAL_TREMOR)


def test_a_left_out_list_that_is_not_written_properly_is_still_refused():
    with patch.object(engine, "_read_left_out", return_value=[{"medicine_id": ATRASENTAN}]):
        with pytest.raises(ValueError):
            engine.added_by_hand(IGA)
