"""Ticket 2.19. Kashish's second red warning on deferoxamine for hemochromatosis.

Kashish's decision, 22 Nov: deferoxamine sits under Approved for
hemochromatosis (EFO_1000642). Its own label says it is not for primary
hemochromatosis. She chose: keep the card, add the red sticker.

One new entry at the end of moonlight/corrections.json does it. No code
changes. No other card on any page changes.

No network. The real corrections file is read as it is. The card is a
hand-built record, as in test_second_warning.py: api._find is swapped for it.
The ids were checked against the saved answer on branch probe-key-diseases
(fixtures/probe_p6/results/EFO_1000642.json): the card's id is CHEMBL556.
"""

import json

from hand_ids import without_correction_id
import pathlib
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from moonlight import api, engine
from moonlight.filter import sort_paths
from moonlight.records import Disease, Medicine, MedicineForm, Path, Target

ROOT = pathlib.Path(__file__).resolve().parent.parent
CORRECTIONS_FILE = ROOT / "moonlight" / "corrections.json"

DEFEROXAMINE = "CHEMBL556"
HEMOCHROMATOSIS = "EFO_1000642"
TYPE_1 = "MONDO_0021001"  # "hemochromatosis type 1": another page, out of scope
THE_DAY = "2026-11-22"
# Kashish's words of 19 Nov, exactly (ticket 2.18).
SECOND_NOTE = ("This looks like a mistake in the database. The official label is "
               "for a different disease.")
THE_ENTRY = {"medicine_id": DEFEROXAMINE, "disease_id": HEMOCHROMATOSIS,
             "date": THE_DAY, "note": SECOND_NOTE}

PROTEIN = Target("ENSG00000000001", "ABC1", "test protein", 0.8)


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


def real_corrections():
    return without_correction_id(json.loads(CORRECTIONS_FILE.read_text(encoding="utf-8")))


def approved_path(name, medicine_id, disease):
    """One hand-built path: a medicine approved for this disease."""
    form = MedicineForm(medicine_id, name, best_stage="APPROVAL", disease_stage="APPROVAL",
                        withdrawn=False)
    return Path(Medicine(name, (form,)), PROTEIN, disease, ("INHIBITOR",), PROTEIN.score,
                (f"https://example.org/{medicine_id}",))


def approved_cards(disease_id):
    """What /api/clues sends for a page holding a hand-built deferoxamine
    card and one other card, with the REAL corrections file."""
    disease = Disease(disease_id, "test page")
    paths = [approved_path("DEFEROXAMINE", DEFEROXAMINE, disease),
             approved_path("OTHERMEDICINE", "CHEMBL8002", disease)]
    found = api._Found(disease, sort_paths(paths), [], [], [])
    with patch.object(api, "_find", return_value=found):
        response = TestClient(api.app).get("/api/clues", params={"disease_id": disease_id})
    assert response.status_code == 200
    return {card["id"]: card for card in response.json()["approved"]}


def test_the_note_is_the_engines_second_note_exactly():
    assert engine.SECOND_NOTE == SECOND_NOTE


def test_the_new_entry_is_in_the_real_file():
    # Kashish, 23 Nov (ticket 2.25): in the file, not last. Later entries follow it.
    bare = lambda entry: {k: v for k, v in entry.items() if k != "label"}
    assert THE_ENTRY in [bare(entry) for entry in real_corrections()]


def test_it_is_the_only_entry_of_that_day_and_the_only_one_for_deferoxamine():
    entries = real_corrections()
    bare = lambda entry: {k: v for k, v in entry.items() if k != "label"}
    assert [bare(entry) for entry in entries if entry["date"] == THE_DAY] == [THE_ENTRY]
    assert [bare(entry) for entry in entries if entry["medicine_id"] == DEFEROXAMINE] == [THE_ENTRY]
    assert [bare(entry) for entry in entries if entry["disease_id"] == HEMOCHROMATOSIS] == [THE_ENTRY]


def test_the_engine_gives_the_hemochromatosis_page_the_second_words_for_deferoxamine_only():
    assert engine.looks_wrong(HEMOCHROMATOSIS) == {DEFEROXAMINE}
    assert engine.warning_words(HEMOCHROMATOSIS) == {DEFEROXAMINE: SECOND_NOTE}


def test_the_deferoxamine_card_shows_the_red_words_and_the_card_beside_it_does_not():
    cards = approved_cards(HEMOCHROMATOSIS)
    assert cards[DEFEROXAMINE]["warning"] == SECOND_NOTE
    assert "warning" not in cards["CHEMBL8002"]
    # The card is kept: still in Approved, still A to Z.
    assert list(cards) == [DEFEROXAMINE, "CHEMBL8002"]


def test_hemochromatosis_type_1_is_another_page_and_gets_no_warning():
    assert engine.warning_words(TYPE_1) == {}
    assert "warning" not in approved_cards(TYPE_1)[DEFEROXAMINE]
