"""Ticket 2.32. Approvals by hand, third batch.

The ticket named four medicines. Three are added, in the ticket's order:

  - ravulizumab for neuromyelitis optica (MONDO_0019100). Kashish picked
    this entry on 23 Nov: it is the one the search for "neuromyelitis
    optica spectrum disorder" finds.
  - avapritinib for systemic mastocytosis (MONDO_0016586). Kashish picked
    this entry on 23 Nov, not one of its sub-forms.
  - valbenazine for Huntington disease (MONDO_0007739).

One is left out (Kashish, 23 Nov): deutetrabenazine for Huntington disease.
The database already records the approval on that disease's list, so the
line would be untrue. It stays as a form inside Tetrabenazine's card.

Saved files only. Neuromyelitis optica and systemic mastocytosis: each
disease's own list, asked live on 2026-11-23 (Open Targets data 26.09) with
fetch.py's own question, in fixtures/approvals_by_hand/disease_drugs/.
Huntington disease: the whole search ticket 2.17 saved in
fixtures/no_regulator/. Its own list and the list of its wider group,
movement disorder, are letter for letter the live answers of 2026-11-23, so
they were not saved again. No network.
"""

import json
import pathlib
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from moonlight import api, engine

# Ticket 2.62 part 3 row 8 (daratumumab marked limited); empty ROW8_PAIRS there to undo it.
from test_red_warnings_2_62 import ROW8_PAIRS, mark_row8, unmark_row8, without_row8_line  # noqa: E402

import test_approvals_batch as second_batch
import test_approvals_by_hand as first_batch
import test_no_regulator_line as huntington_page

ROOT = pathlib.Path(__file__).resolve().parent.parent
APPROVALS_FILE = ROOT / "moonlight" / "approvals.json"
CORRECTIONS_FILE = ROOT / "moonlight" / "corrections.json"
LEFT_OUT_FILE = ROOT / "moonlight" / "left_out.json"
OLD_LISTS = ROOT / "fixtures" / "no_regulator" / "disease_drugs"  # ticket 2.17's
NEW_LISTS = ROOT / "fixtures" / "approvals_by_hand" / "disease_drugs"
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

NMO = "MONDO_0019100"  # neuromyelitis optica
MASTOCYTOSIS = "MONDO_0016586"  # systemic mastocytosis
RAVULIZUMAB = "CHEMBL3989986"
AVAPRITINIB = "CHEMBL4204794"
RAVULIZUMAB_LABEL = ("https://www.accessdata.fda.gov/drugsatfda_docs/label/2024/"
                     "761108s037lbl.pdf")
AVAPRITINIB_LABEL = ("https://www.accessdata.fda.gov/drugsatfda_docs/label/2024/"
                     "212608s020lbl.pdf")
SAVED_LISTS = {NMO: NEW_LISTS, MASTOCYTOSIS: NEW_LISTS,
               HUNTINGTON: OLD_LISTS, MOVEMENT_DISORDER: OLD_LISTS}

ON_OWN_LIST = [  # the two whose disease's own list holds them
    {"medicine_id": RAVULIZUMAB, "name": "Ravulizumab", "disease_id": NMO,
     "date": THE_DAY, "label": RAVULIZUMAB_LABEL},
    {"medicine_id": AVAPRITINIB, "name": "Avapritinib", "disease_id": MASTOCYTOSIS,
     "date": THE_DAY, "label": AVAPRITINIB_LABEL},
]
THIRD_BATCH = ON_OWN_LIST + [
    {"medicine_id": VALBENAZINE, "name": "Valbenazine", "disease_id": HUNTINGTON,
     "date": THE_DAY, "label": VALBENAZINE_LABEL},
]
FIRST_FIVE = first_batch.FIRST_ENTRIES + second_batch.SECOND_BATCH
# Ticket 2.39 (Kashish's answer A to question 3, 24 Nov): the valbenazine
# entry gained "limited": true, and nothing else. THIRD_BATCH stays as it
# was written on 23 Nov. LIMITED_LINE is the line its card gained.
LIMITED_LINE = "The label covers only some people with this disease."


def as_written_now(entries):
    """The entries as the file holds them since ticket 2.39."""
    return mark_row8([dict(entry, limited=True)
                      if (entry["medicine_id"], entry["disease_id"]) == (VALBENAZINE, HUNTINGTON)
                      else entry for entry in entries])  # ticket 2.62 row 8: daratumumab too


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
VALBENAZINE_CARD_NOW = dict(VALBENAZINE_CARD, limit_note=LIMITED_LINE)  # ticket 2.39


def load(file):
    return json.loads(file.read_text(encoding="utf-8"))


def saved_rows(disease_id):
    answer = load(SAVED_LISTS[disease_id] / f"{disease_id}.response.json")
    assert answer["data"]["disease"]["id"] == disease_id
    return answer["data"]["disease"]["drugAndClinicalCandidates"]["rows"]


@pytest.fixture(autouse=True)
def offline():
    """Real HTTP is an error. Every question is answered from saved files."""
    api.forget_visitors()
    with patch("requests.request", side_effect=AssertionError("network used")), \
            patch("requests.post", side_effect=AssertionError("network used")), \
            patch("requests.get", side_effect=AssertionError("network used")), \
            patch("requests.sessions.Session.request",
                  side_effect=AssertionError("network used")), \
            patch("moonlight.fetch._post_json", side_effect=saved_post_json):
        yield
    api.forget_visitors()


def saved_post_json(body):
    """Stands in for fetch._post_json: ticket 2.17's saved answers, and the two new lists."""
    try:
        return huntington_page.saved_post_json(body)
    except FileNotFoundError:
        return first_batch.saved_post_json(body)


def page(entries):
    """What /api/clues sends for Huntington disease with these hand-written approvals."""
    api.forget_visitors()
    with patch.object(engine, "_read_approvals", return_value=entries):
        response = TestClient(api.app).get("/api/clues", params={"disease_id": HUNTINGTON})
    assert response.status_code == 200
    return response.json()


# ---- the hand-written file, entry for entry ----

def test_the_real_file_holds_the_first_five_entries_then_the_three_new_ones():
    # Ticket 2.33 added two after. Ticket 2.39 marked valbenazine "limited".
    assert load(APPROVALS_FILE)[:8] == as_written_now(FIRST_FIVE + THIRD_BATCH)


def test_the_engine_reads_the_three_new_entries():
    assert engine.approvals_by_hand()[5:8] == [  # ticket 2.33 added two after these
        engine.HandApproval(RAVULIZUMAB, "Ravulizumab", NMO, RAVULIZUMAB_LABEL),
        engine.HandApproval(AVAPRITINIB, "Avapritinib", MASTOCYTOSIS, AVAPRITINIB_LABEL),
        engine.HandApproval(VALBENAZINE, "Valbenazine", HUNTINGTON, VALBENAZINE_LABEL,
                            limited=True)]  # ticket 2.39


def test_each_new_entry_is_handed_only_to_its_own_disease():
    assert [entry.medicine_id for entry in engine.added_by_hand(NMO)] == [RAVULIZUMAB]
    assert [entry.medicine_id for entry in engine.added_by_hand(MASTOCYTOSIS)] == [
        AVAPRITINIB, "CHEMBL941"]  # ticket 2.33 added imatinib
    assert [entry.medicine_id for entry in engine.added_by_hand(HUNTINGTON)] == [VALBENAZINE]
    new = {RAVULIZUMAB, AVAPRITINIB, VALBENAZINE}
    # Not to a sub-form, a wider group, or another batch's disease.
    for other in (MOVEMENT_DISORDER, "EFO_0009584", "EFO_0009585", "MONDO_0020334",
                  "MONDO_0007950", second_batch.IGA, second_batch.AL_AMYLOIDOSIS):
        assert not new & {entry.medicine_id for entry in engine.added_by_hand(other)}


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


def test_the_new_entries_clash_with_no_existing_rule():
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


# ---- ravulizumab and avapritinib, on their diseases' own saved lists ----

@pytest.mark.parametrize("entry, name", [(ON_OWN_LIST[0], "RAVULIZUMAB"),
                                         (ON_OWN_LIST[1], "AVAPRITINIB")],
                         ids=["Ravulizumab", "Avapritinib"])
def test_the_ids_are_the_ones_open_targets_uses_in_the_saved_lists(entry, name):
    drugs = [row["drug"] for row in saved_rows(entry["disease_id"])
             if row["drug"]["id"] == entry["medicine_id"]]
    assert [drug["name"] for drug in drugs] == [name]
    assert drugs[0]["parentMolecule"] is None  # it is the medicine, not a tablet form
    assert drugs[0]["childMolecules"] == []  # and it has no tablet form
    assert "withdrawn" not in [warning["warningType"].lower()
                               for warning in drugs[0]["drugWarnings"]]


@pytest.mark.parametrize("entry, stage", [(ON_OWN_LIST[0], "PHASE_3"),
                                          (ON_OWN_LIST[1], "PHASE_2")],
                         ids=["Ravulizumab", "Avapritinib"])
def test_the_database_lists_them_only_as_in_trials_so_the_line_is_true(entry, stage):
    rows = [row for row in saved_rows(entry["disease_id"])
            if row["drug"]["id"] == entry["medicine_id"]]
    assert [row["maxClinicalStage"] for row in rows] == [stage]
    assert "APPROVAL" not in [report["clinicalStage"] for report in rows[0]["clinicalReports"]]


@pytest.mark.parametrize("entry", ON_OWN_LIST, ids=lambda entry: entry["name"])
def test_before_each_was_in_the_more_in_trials_box_and_not_under_approved(entry):
    places = first_batch.everywhere(second_batch.tabs_for(entry["disease_id"], []))
    assert [place for place, ids in places.items() if entry["medicine_id"] in ids] == [
        "more_in_trials"]


@pytest.mark.parametrize("entry", ON_OWN_LIST, ids=lambda entry: entry["name"])
def test_each_is_now_only_under_approved_with_the_line_and_its_label(entry):
    disease_id = entry["disease_id"]
    before = second_batch.tabs_for(disease_id, [])
    # Ticket 2.33 gave systemic mastocytosis a second entry: only this one is asked about.
    tabs = second_batch.tabs_for(disease_id, [
        hand for hand in engine.added_by_hand(disease_id)
        if hand.medicine_id == entry["medicine_id"]])
    assert first_batch.only_under_approved(tabs, entry["medicine_id"])
    card = [medicine for medicine in tabs.approved if medicine.id == entry["medicine_id"]][0]
    assert card.name == entry["name"]
    assert card.proof_note == LINE
    assert card.source_record == entry["label"]
    assert card.label is None  # the main list, not a folded box
    assert len(tabs.approved) == len(before.approved) + 1
    names = [medicine.name.lower() for medicine in tabs.approved]
    assert names == sorted(names)  # A to Z, as the list already was
    # Every other card stays where it was.
    for place, ids in first_batch.everywhere(before).items():
        if place != "approved":
            assert first_batch.everywhere(tabs)[place] == [
                i for i in ids if i != entry["medicine_id"]]


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
    assert new["approved"][-1] == VALBENAZINE_CARD_NOW  # ticket 2.39: one more line


def test_valbenazine_is_nowhere_else_on_the_page_and_nothing_else_changes():
    old = page(FIRST_FIVE)
    new = page(load(APPROVALS_FILE))
    assert [key for key, _ in first_batch.cards_naming(new, "valbenazine")] == ["approved"]
    expected = dict(old, approved=old["approved"] + [VALBENAZINE_CARD_NOW],  # ticket 2.39
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
