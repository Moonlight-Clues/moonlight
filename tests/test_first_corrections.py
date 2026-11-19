"""Ticket 2.15. The first corrections, and "Listed A to Z".

Kashish's decisions, 17 Nov:

1. Four medicines are on the corrections list for three diseases, so their
   Approved cards show the red warning. A pair is on the list only when the
   saved answer shows that medicine as approved for that disease.
2. The Approved tab's top line ends with "Listed A to Z."

Saved files only (fixtures/approval_proof/). No network. Every id here is
read from those files. None is written by hand.
"""

import json
import re

import pytest
from fastapi.testclient import TestClient

from moonlight import api, engine

import test_approval_proof
from test_approval_proof import ALZHEIMER, ECZEMA, HUNTINGTON, PAH, PROOF, ROOT
from test_approval_proof import NOTE, THE_FOUR, WARNING, load
from test_approval_proof import offline, saved_tabs  # noqa: F401  (fixtures)

THE_THREE = [ALZHEIMER, HUNTINGTON, ECZEMA]
THE_DAY = "2026-11-16"  # the day the doctor answered
FILE = ROOT / "moonlight" / "corrections.json"
PAGE = (ROOT / "web" / "index.html").read_text(encoding="utf-8")

TOP_LINE = ("Already approved for this disease in at least one country, according to "
            "the database. Nothing here says how well any of them works. Listed A to Z.")


def real_entries():
    return json.loads(FILE.read_text(encoding="utf-8"))


def saved_pairs():
    """(medicine id, disease id) for each of the four that the saved answer
    shows as approved for one of the three diseases. A tablet form counts
    for its medicine, and the id is the medicine's own, as on its card."""
    pairs = {}
    for disease in THE_THREE:
        answer = load(PROOF / disease.id / "disease_drugs" / f"own_{disease.id}.response.json")
        listed = answer["data"]["disease"]
        assert listed["id"] == disease.id
        for row in listed["drugAndClinicalCandidates"]["rows"]:
            medicine = row["drug"]["parentMolecule"] or row["drug"]
            if medicine["name"] in THE_FOUR and row["maxClinicalStage"] == "APPROVAL":
                pairs[(medicine["id"], disease.id)] = medicine["name"]
    return pairs


@pytest.fixture
def client():
    return TestClient(api.app)


def clues_json(client, disease, corrections):
    return test_approval_proof.clues_json(client, disease, corrections)


def approved_cards(data):
    return data["approved"] + data.get("narrower", []) + data["wider_group"]


# ---- Part 1: the corrections file ----

def test_the_saved_answers_show_all_four_medicines_approved_for_all_three_diseases():
    pairs = saved_pairs()
    assert len(pairs) == 12
    for disease in THE_THREE:
        names = sorted(name for (_, listed_for), name in pairs.items() if listed_for == disease.id)
        assert names == THE_FOUR


def test_the_file_holds_exactly_the_pairs_the_saved_answers_show_and_no_other():
    entries = real_entries()
    in_file = [(entry["medicine_id"], entry["disease_id"]) for entry in entries]
    assert len(in_file) == len(set(in_file))  # no pair twice
    assert set(in_file) == set(saved_pairs())
    assert engine.corrections() == set(saved_pairs())


def test_example_5_every_entry_holds_only_the_four_keys_and_no_persons_name():
    entries = real_entries()
    assert entries
    medicine_ids = {medicine_id for medicine_id, _ in saved_pairs()}
    disease_ids = {disease.id for disease in THE_THREE}
    for entry in entries:
        assert set(entry) == {"medicine_id", "disease_id", "date", "note"}
        # Each value is an id from the saved files, the day, or the note.
        # That leaves no room for anybody's name.
        assert entry["medicine_id"] in medicine_ids
        assert entry["disease_id"] in disease_ids
        assert entry["date"] == THE_DAY
        assert entry["note"] == NOTE == engine.CORRECTION_NOTE
    # The whole file, read as plain text: nothing is left once the keys, the
    # ids, the day and the note are taken away.
    text = FILE.read_text(encoding="utf-8")
    for known in ["medicine_id", "disease_id", "date", "note", NOTE, THE_DAY,
                  *sorted(medicine_ids, key=len, reverse=True), *disease_ids]:
        text = text.replace(f'"{known}"', "")
    assert re.sub(r"[\s\[\]{}:,]", "", text) == ""


# ---- Example 1: the warning is on each card, and the card keeps its place ----

@pytest.mark.parametrize("disease", THE_THREE, ids=lambda disease: disease.name)
def test_example_1_each_added_card_has_the_warning_and_keeps_its_place(client, disease):
    plain = clues_json(client, disease, [])
    data = clues_json(client, disease, real_entries())
    expected = {medicine_id for medicine_id, listed_for in saved_pairs() if listed_for == disease.id}
    assert len(expected) == 4
    warned = [item for item in approved_cards(data) if "warning" in item]
    assert {item["id"] for item in warned} == expected
    assert all(item["warning"] == WARNING == engine.WRONG_WARNING for item in warned)
    assert sorted(item["medicine"].upper() for item in warned) == THE_FOUR
    # All four are in the main Approved list, in the same places as before.
    assert all(item in data["approved"] for item in warned)
    assert [item["id"] for item in data["approved"]] == [item["id"] for item in plain["approved"]]
    names = [item["medicine"] for item in data["approved"]]
    assert names == sorted(names, key=str.casefold)  # A to Z
    # The warning is the only thing added to a card.
    for before, after in zip(plain["approved"], data["approved"]):
        assert {key: value for key, value in after.items() if key != "warning"} == before


# ---- Example 2: no warning under any other disease ----

def test_example_2_the_real_file_warns_under_the_three_diseases_only():
    three = {disease.id for disease in THE_THREE}
    assert {listed_for for _, listed_for in engine.corrections()} == three
    # Every other disease in the saved files: the one step up and one step
    # down entries of the three, and pulmonary arterial hypertension.
    others = {load(file)["data"]["disease"]["id"]
              for file in PROOF.glob("*/disease_drugs/*.response.json")} - three
    others.add(PAH.id)
    assert len(others) == 18
    for other in others:
        assert engine.looks_wrong(other) == set()


def test_example_2_the_same_four_cards_under_another_disease_carry_no_warning(saved_tabs):
    cards = [medicine for medicine in saved_tabs(ALZHEIMER).approved if medicine.name in THE_FOUR]
    assert sorted(medicine.name for medicine in cards) == THE_FOUR
    for medicine in cards:
        # Under Alzheimer disease the card is warned. The very same card,
        # shown under pulmonary arterial hypertension, is not.
        assert api._approved_json(medicine, engine.looks_wrong(ALZHEIMER.id))["warning"] == WARNING
        assert "warning" not in api._approved_json(medicine, engine.looks_wrong(PAH.id))


# ---- Example 3: no Approved card disappears ----

@pytest.mark.parametrize("disease", THE_THREE, ids=lambda disease: disease.name)
def test_example_3_the_approved_lists_hold_the_same_medicines_as_before(client, disease):
    plain = clues_json(client, disease, [])
    data = clues_json(client, disease, real_entries())
    for box in ("approved", "narrower", "wider_group"):
        before, after = plain.get(box, []), data.get(box, [])
        assert [item["id"] for item in after] == [item["id"] for item in before]
        assert [item["medicine"] for item in after] == [item["medicine"] for item in before]
    assert len(data["approved"]) == len(plain["approved"]) > 0
    # In trials and New clues are not touched at all.
    assert data["being_studied"] == plain["being_studied"]
    assert [{**card, "proteins": [{key: value for key, value in protein.items() if key != "opposite_way"} for protein in card["proteins"]]} for card in data["new_clues"]] == [{**card, "proteins": [{key: value for key, value in protein.items() if key != "opposite_way"} for protein in card["proteins"]]} for card in plain["new_clues"]]


# ---- Part 2, example 4: the top line of the Approved tab ----

def test_example_4_the_page_holds_the_new_top_line_exactly_once():
    assert PAGE.count(TOP_LINE) == 1
    assert PAGE.count(f'<p class="tab-words">{TOP_LINE}</p>') == 1  # one line on the page
    panel = PAGE[PAGE.index('id="panel-approved"'):PAGE.index('id="panel-trials"')]
    assert panel.count(TOP_LINE) == 1
    assert panel.count("Listed A to Z.") == 1


def test_the_safety_lines_are_still_on_the_page():
    panel = PAGE[PAGE.index('id="panel-approved"'):PAGE.index('id="panel-trials"')]
    assert panel.count("Talk to your doctor before changing any medicine.") == 3
    assert ("For learning and research exploration, not medical advice. Never start, "
            "stop or change any medicine without a doctor.") in PAGE
