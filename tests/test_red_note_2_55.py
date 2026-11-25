"""Ticket 2.55, Parts A and C. Two corrections entries, list and words only.

PART A. Kashish's signed answer Q10 (25 Nov, answer A): the corrections list
accepts a third note, word for word, "A blood thinner cannot be a treatment
for a bleeding disease." Dicumarol (CHEMBL1466) on haemophilia A
(MONDO_0010602) carries it. MAIN 4's answer of 25 Nov: no rule change, so
the card keeps its place in the wider-group box and shows the red sentence
on the card there. (Whether red cards inside folded boxes should move to the
red box is a new rule for Kashish's next sheet.)

PART C. Kashish's signed answer Q22: a combination pill's label does not
count for one of its parts. Sodium phenylbutyrate (CHEMBL1469) on
amyotrophic lateral sclerosis (MONDO_0004976) gets the second note. Its card
sat in the "no regulator record" box; the red box wins (ticket 2.42), so it
moves to the red box.

The two older notes, and every card that uses them, stay exactly as they are.

Part B (Source record order) waits for ticket 2.56. No network.
"""

import hashlib
import json
import pathlib
from unittest.mock import patch

import pytest

from moonlight import api, engine
from moonlight.engine import ApprovedMedicine

import test_withdrawal_line as hem_a_page

ROOT = pathlib.Path(__file__).resolve().parent.parent
CORRECTIONS_FILE = ROOT / "moonlight" / "corrections.json"
SAVED = ROOT / "fixtures" / "sheet_25_nov"

# Kashish's words, exactly.
FIRST_NOTE = "A doctor confirmed this looks wrong."
FIRST_WARNING = "A doctor has told us this looks like a mistake in the database."
SECOND_NOTE = ("This looks like a mistake in the database. The official label is for "
               "a different disease.")
THIRD_NOTE = "A blood thinner cannot be a treatment for a bleeding disease."

THE_DAY = "2026-11-25"
HEM_A, DICUMAROL = "MONDO_0010602", "CHEMBL1466"
ALS, PHENYLBUTYRATE = "MONDO_0004976", "CHEMBL1469"
NEW = [
    {"medicine_id": DICUMAROL, "disease_id": HEM_A, "date": THE_DAY, "note": THIRD_NOTE},
    {"medicine_id": PHENYLBUTYRATE, "disease_id": ALS, "date": THE_DAY, "note": SECOND_NOTE},
]
# The 111 entries that were there before this ticket, exactly as they were.
OLD_111_SHA256 = "38f19927efc2a1835141b15751979af3d7258081c9844842b3ecb22a713d6633"


def load(file):
    return json.loads(file.read_text(encoding="utf-8"))


def old_entries():
    # Ticket 2.56 (signed rule Q22) added five entries after the two of this
    # ticket, so "without this ticket's entries" is no longer "all but the last two".
    entries = load(CORRECTIONS_FILE)
    # Ticket 3.10 (MAIN 4, Q14) deleted mannitol's entry before them, so each moved up one.
    return entries[:110] + entries[112:]


# ---- the words ----

def test_the_third_note_is_kashishs_sentence_word_for_word():
    assert engine.THIRD_NOTE == THIRD_NOTE
    assert engine.CORRECTION_NOTES == (FIRST_NOTE, SECOND_NOTE, THIRD_NOTE)
    assert engine.RED_WORDS[THIRD_NOTE] == THIRD_NOTE  # the card shows the note itself


def test_the_two_older_notes_and_their_red_words_are_unchanged():
    assert engine.RED_WORDS[FIRST_NOTE] == FIRST_WARNING
    assert engine.RED_WORDS[SECOND_NOTE] == SECOND_NOTE


@pytest.mark.parametrize("almost", [
    THIRD_NOTE.lower(),
    THIRD_NOTE[:-1],  # no full stop
    THIRD_NOTE + " Kashish said so.",
    "A blood thinner cannot be a treatment for a bleeding disease ",
])
def test_a_note_that_is_almost_the_third_one_is_refused(almost):
    entries = [{"medicine_id": "C1", "disease_id": "D1", "date": THE_DAY, "note": almost}]
    with patch.object(engine, "_read_corrections", return_value=entries):
        with pytest.raises(ValueError):
            engine.corrections()


# ---- the file ----

def test_the_file_holds_the_old_111_unchanged_then_the_two_new_entries():
    entries = load(CORRECTIONS_FILE)
    # ticket 2.56 added five after these; ticket 3.10 (MAIN 4, Q14) deleted mannitol's red entry on asthma
    assert len(entries) == 117
    # The old 111 are the first 110 with mannitol's entry back in its old place, unchanged otherwise.
    mannitol = {"medicine_id": "CHEMBL689", "disease_id": "MONDO_0004979", "date": "2026-11-25",
                "note": "This looks like a mistake in the database. The official label is for a "
                        "different disease."}
    old = entries[:57] + [mannitol] + entries[57:110]
    assert hashlib.sha256(json.dumps(old, sort_keys=True).encode()).hexdigest() == \
        OLD_111_SHA256
    assert entries[110:112] == NEW
    assert all(list(entry) == ["medicine_id", "disease_id", "date", "note"] for entry in NEW)


def test_no_pair_is_written_twice():
    pairs = [(e["medicine_id"], e["disease_id"]) for e in load(CORRECTIONS_FILE)]
    assert len(set(pairs)) == len(pairs)


def test_every_card_using_the_older_notes_keeps_its_words():
    with patch.object(engine, "_read_corrections", return_value=old_entries()):
        before = {d: engine.warning_words(d) for d in {e["disease_id"] for e in old_entries()}}
    for disease_id, words in before.items():
        now = engine.warning_words(disease_id)
        for entry in NEW:
            if entry["disease_id"] == disease_id:
                now.pop(entry["medicine_id"])
        assert now == words


# ---- Part A: dicumarol on haemophilia A ----

def test_the_engine_gives_dicumarol_the_third_note_on_haemophilia_a_only():
    assert engine.warning_words(HEM_A)[DICUMAROL] == THIRD_NOTE
    for disease_id in {e["disease_id"] for e in load(CORRECTIONS_FILE)} - {HEM_A}:
        assert DICUMAROL not in engine.warning_words(disease_id)


def hem_a(entries):
    with hem_a_page.left_out_before_2_43():
        return hem_a_page.page_answer(wrong=entries)


@pytest.fixture(scope="module")
def pages():
    return hem_a(old_entries()), hem_a(load(CORRECTIONS_FILE))


def dicumarol(page):
    (card,) = [c for c in page["wider_group"] if c["id"] == DICUMAROL]
    return card


def test_before_dicumarol_sat_in_the_wider_group_box_with_no_warning(pages):
    before, _ = pages
    assert "warning" not in dicumarol(before)
    assert DICUMAROL not in before.get("wrong_approvals_box", [])


def test_after_dicumarol_stays_in_the_wider_group_box_with_the_red_sentence(pages):
    before, after = pages
    assert dicumarol(after)["warning"] == THIRD_NOTE
    # MAIN 4, 25 Nov: no rule change. It keeps its place, in the same A to Z order.
    assert [c["id"] for c in after["wider_group"]] == [c["id"] for c in before["wider_group"]]
    assert DICUMAROL not in after.get("wrong_approvals_box", [])
    assert all(c["id"] != DICUMAROL for c in after["approved"] + after.get("narrower", []))


def test_nothing_else_on_the_haemophilia_a_page_changes(pages):
    before, after = pages
    changed = dicumarol(after)
    changed.pop("warning")
    assert after == before


# ---- Part C: sodium phenylbutyrate on ALS ----

def phenylbutyrate_card():
    """The ALS card as the saved page of 25 Nov shows it: on the main
    Approved list, no regulator record, so in the box above the red box."""
    return ApprovedMedicine(
        id=PHENYLBUTYRATE, name="Phenylbutanoic Acid", forms=("Sodium Phenylbutyrate",),
        clue=None, listed_sources=("https://clinicaltrials.gov/study/NCT05286372",),
        regulator_record=False)


def test_the_saved_als_page_had_it_in_the_no_regulator_box_and_no_red_box():
    after_2_54 = load(SAVED / "after" / f"{ALS}.clues.json")
    assert PHENYLBUTYRATE in after_2_54["no_regulator_box"]
    assert "wrong_approvals_box" not in after_2_54
    (card,) = [c for c in after_2_54["approved"] if c["id"] == PHENYLBUTYRATE]
    assert card["proof_note"] == engine.NO_REGULATOR_LINE


def test_before_the_entry_the_card_is_in_the_no_regulator_box():
    card = phenylbutyrate_card()
    assert card.proof_note == engine.NO_REGULATOR_LINE
    with patch.object(engine, "_read_corrections", return_value=old_entries()):
        assert engine.no_regulator_box([card], ALS) == [card]
        assert engine.wrong_approvals_box([card], ALS) == []


def test_after_the_entry_the_red_box_wins():
    card = phenylbutyrate_card()
    assert engine.warning_words(ALS)[PHENYLBUTYRATE] == SECOND_NOTE
    assert engine.wrong_approvals_box([card], ALS) == [card]
    assert engine.no_regulator_box([card], ALS) == []
    sent = api._approved_json(card, engine.looks_wrong(ALS), engine.warning_words(ALS))
    assert sent["warning"] == SECOND_NOTE
    assert sent["proof_note"] == engine.NO_REGULATOR_LINE  # the grey line stays; the card only moves
