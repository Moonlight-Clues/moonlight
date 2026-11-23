"""Ticket 2.32. Approvals by hand, third batch.

The ticket named four medicines. One is added here. Three hit the
ticket's STOP AND ASK rules and wait for Kashish:

  - valbenazine for Huntington disease (MONDO_0007739): ADDED.
  - deutetrabenazine for Huntington disease: LEFT OUT. The database already
    records the approval on that disease's list, so the line would be
    untrue. It is on the page today, as a form inside Tetrabenazine's card.
  - ravulizumab (NMOSD) and avapritinib (systemic mastocytosis): NOT ADDED
    YET. Each disease has more than one entry on Open Targets. Kashish
    picks the entry.

Saved files only. Huntington disease: the whole search ticket 2.17 saved in
fixtures/no_regulator/. Its own list and the list of its wider group,
movement disorder, are letter for letter the live answers of 2026-11-23
(Open Targets data 26.09), so nothing was saved again. No network.
"""

import json
import pathlib
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from moonlight import api, engine

import test_approvals_batch as second_batch
import test_approvals_by_hand as first_batch
import test_no_regulator_line as huntington_page

ROOT = pathlib.Path(__file__).resolve().parent.parent
APPROVALS_FILE = ROOT / "moonlight" / "approvals.json"
CORRECTIONS_FILE = ROOT / "moonlight" / "corrections.json"
LEFT_OUT_FILE = ROOT / "moonlight" / "left_out.json"
SAVED_LISTS = ROOT / "fixtures" / "no_regulator" / "disease_drugs"  # ticket 2.17's
SAVED_FAMILY = ROOT / "fixtures" / "no_regulator" / "family"

LINE = "This approval is missing from the database. We added it from the official label."
THE_DAY = "2026-11-23"

HUNTINGTON = "MONDO_0007739"
MOVEMENT_DISORDER = "MONDO_0005395"  # the wider group the database puts Huntington disease in
VALBENAZINE = "CHEMBL2364639"
VALBENAZINE_TABLET = "CHEMBL3707248"  # valbenazine tosylate
VALBENAZINE_LABEL = ("https://www.accessdata.fda.gov/drugsatfda_docs/label/2025/"
                     "209241s029lbl.pdf")
TETRABENAZINE = "CHEMBL117785"
DEUTETRABENAZINE = "CHEMBL3137326"

THIRD_BATCH = [
    {"medicine_id": VALBENAZINE, "name": "Valbenazine", "disease_id": HUNTINGTON,
     "date": THE_DAY, "label": VALBENAZINE_LABEL},
]
FIRST_FIVE = first_batch.FIRST_ENTRIES + second_batch.SECOND_BATCH

# The card, exactly as /api/clues must send it. Everything but the last two
# lines is what the page already knew about valbenazine.
VALBENAZINE_CARD = {
    "id": VALBENAZINE,
    "medicine": "Valbenazine",
    "forms": ["Valbenazine", "Valbenazine Tosylate"],
    "proteins": [{"symbol": "SLC18A2", "points": 59, "direction": "down", "machine": 1,
                  "piece_of_machine": False}],
    "reports": 31,
    "source": VALBENAZINE_LABEL,
    "proof_note": LINE,
}


def load(file):
    return json.loads(file.read_text(encoding="utf-8"))


def saved_rows(disease_id):
    answer = load(SAVED_LISTS / f"{disease_id}.response.json")
    assert answer["data"]["disease"]["id"] == disease_id
    return answer["data"]["disease"]["drugAndClinicalCandidates"]["rows"]


@pytest.fixture(autouse=True)
def offline():
    """Real HTTP is an error. Every question is answered from ticket 2.17's saved files."""
    api.forget_visitors()
    with patch("requests.request", side_effect=AssertionError("network used")), \
            patch("requests.post", side_effect=AssertionError("network used")), \
            patch("requests.get", side_effect=AssertionError("network used")), \
            patch("requests.sessions.Session.request",
                  side_effect=AssertionError("network used")), \
            patch("moonlight.fetch._post_json", side_effect=huntington_page.saved_post_json):
        yield
    api.forget_visitors()


def page(entries):
    """What /api/clues sends for Huntington disease with these hand-written approvals."""
    api.forget_visitors()
    with patch.object(engine, "_read_approvals", return_value=entries):
        response = TestClient(api.app).get("/api/clues", params={"disease_id": HUNTINGTON})
    assert response.status_code == 200
    return response.json()


# ---- the hand-written file, entry for entry ----

def test_the_real_file_holds_the_first_five_entries_then_the_new_one():
    assert load(APPROVALS_FILE) == FIRST_FIVE + THIRD_BATCH


def test_the_engine_reads_the_new_entry():
    assert engine.approvals_by_hand()[5:] == [
        engine.HandApproval(VALBENAZINE, "Valbenazine", HUNTINGTON, VALBENAZINE_LABEL)]


def test_the_new_entry_is_handed_only_to_its_own_disease():
    assert [entry.medicine_id for entry in engine.added_by_hand(HUNTINGTON)] == [VALBENAZINE]
    for other in (MOVEMENT_DISORDER, second_batch.IGA, second_batch.AL_AMYLOIDOSIS):
        assert VALBENAZINE not in [entry.medicine_id for entry in engine.added_by_hand(other)]


# ---- "Find each id on Open Targets. Use the parent medicine's id, not a salt form's." ----

def test_the_id_is_the_one_open_targets_uses_in_a_saved_answer():
    # Valbenazine has no row on Huntington disease's own list. Its id is read
    # from the saved list of movement disorder, which the saved family answer
    # names as a parent of Huntington disease.
    family = load(SAVED_FAMILY / f"{HUNTINGTON}.response.json")["data"]["disease"]
    assert MOVEMENT_DISORDER in [parent["id"] for parent in family["parents"]]
    drugs = {row["drug"]["id"]: row["drug"] for row in saved_rows(MOVEMENT_DISORDER)}
    assert drugs[VALBENAZINE]["name"] == "VALBENAZINE"
    assert drugs[VALBENAZINE]["parentMolecule"] is None  # the medicine, not a tablet form
    assert [form["id"] for form in drugs[VALBENAZINE]["childMolecules"]] == [VALBENAZINE_TABLET]
    assert drugs[VALBENAZINE_TABLET]["parentMolecule"]["id"] == VALBENAZINE


def test_the_database_does_not_record_the_approval_so_the_line_is_true():
    # Not a row for valbenazine or its tablet form on Huntington disease's own list.
    listed = [row["drug"]["id"] for row in saved_rows(HUNTINGTON)]
    assert len(listed) == 62
    assert VALBENAZINE not in listed
    assert VALBENAZINE_TABLET not in listed


def test_the_new_entry_clashes_with_no_existing_rule():
    for entry in THIRD_BATCH:
        pair = (entry["medicine_id"], entry["disease_id"])
        assert pair not in {(wrong["medicine_id"], wrong["disease_id"])
                            for wrong in load(CORRECTIONS_FILE)}
        assert pair not in {(out["medicine_id"], out["disease_id"])
                            for out in load(LEFT_OUT_FILE)}
    assert engine.approvals_left_out() == []
    warnings = [warning["warningType"].lower()
                for row in saved_rows(MOVEMENT_DISORDER)
                if row["drug"]["id"] in (VALBENAZINE, VALBENAZINE_TABLET)
                for drug in [row["drug"]] + row["drug"]["childMolecules"]
                for warning in drug["drugWarnings"]]
    assert warnings  # it has warnings (black box), and none is a withdrawal
    assert "withdrawn" not in warnings


# ---- the EXAMPLE on the whole saved page: valbenazine for Huntington disease ----

def test_before_valbenazine_was_only_in_the_wider_group_box_of_huntington_disease():
    old = page(FIRST_FIVE)
    assert [card["medicine"] for card in old["approved"]] == [
        "Atomoxetine", "Guanfacine", "Lisdexamfetamine", "Methylphenidate", "Tetrabenazine"]
    assert [key for key, _ in first_batch.cards_naming(old, "valbenazine")] == ["wider_group"]


def test_valbenazine_is_on_the_approved_list_a_to_z_with_the_line_and_its_label():
    new = page(load(APPROVALS_FILE))
    assert new["disease"] == {"id": HUNTINGTON, "name": "Huntington disease"}
    assert [card["medicine"] for card in new["approved"]] == [
        "Atomoxetine", "Guanfacine", "Lisdexamfetamine", "Methylphenidate", "Tetrabenazine",
        "Valbenazine"]
    assert new["approved"][-1] == VALBENAZINE_CARD


def test_valbenazine_is_nowhere_else_on_the_page_and_nothing_else_changes():
    old = page(FIRST_FIVE)
    new = page(load(APPROVALS_FILE))
    assert [key for key, _ in first_batch.cards_naming(new, "valbenazine")] == ["approved"]
    expected = dict(old, approved=old["approved"] + [VALBENAZINE_CARD],
                    wider_group=[card for card in old["wider_group"]
                                 if card["id"] != VALBENAZINE])
    assert new == expected


# ---- STOP AND ASK: "If the database already records an approval ... leave that
# ---- entry out and say so." Deutetrabenazine for Huntington disease.

def test_the_database_already_records_deutetrabenazines_approval_for_huntington_disease():
    rows = [row for row in saved_rows(HUNTINGTON) if row["drug"]["id"] == DEUTETRABENAZINE]
    assert [row["maxClinicalStage"] for row in rows] == ["APPROVAL"]
    assert ("APPROVAL", "DailyMed") in {(report["clinicalStage"], report["source"])
                                        for report in rows[0]["clinicalReports"]}
    # The database files it as a form of tetrabenazine.
    assert rows[0]["drug"]["parentMolecule"]["id"] == TETRABENAZINE


def test_so_deutetrabenazine_has_no_entry_in_the_hand_written_file():
    for entry in load(APPROVALS_FILE):
        assert entry["medicine_id"] not in (DEUTETRABENAZINE, TETRABENAZINE)


def test_deutetrabenazine_is_under_approved_already_inside_tetrabenazines_card():
    new = page(load(APPROVALS_FILE))
    assert [key for key, _ in first_batch.cards_naming(new, "deutetrabenazine")] == ["approved"]
    card = [card for card in new["approved"] if card["id"] == TETRABENAZINE][0]
    assert card["forms"] == ["Tetrabenazine", "Deutetrabenazine"]
    assert "proof_note" not in card  # the database's own approval, not a hand-added one
