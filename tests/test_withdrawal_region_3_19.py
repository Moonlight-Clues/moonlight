"""Ticket 3.19, Q15: a sentence for "withdrawn in one region".

Decision of 25 Nov (Shreshth with Kashish's counsel; signed sheet 26 Nov).
An entry of moonlight/withdrawals.json may carry one more key, "region",
that is exactly "US" or "EU". Its card's grey line then says, word for word:

  US: "Its approval was withdrawn in the US. It may still be sold elsewhere."
  EU: "Its approval was withdrawn in the EU. It may still be sold elsewhere."

An entry with no region keeps today's sentence (HAND_WITHDRAWAL_LINE). A
region entry changes only the grey line: the card stays in its list or box,
nothing moves, nothing turns red.

Saved files only: fixtures/withdrawal_region/entries.json holds the two
test-only entries; the page is haemophilia A from the saved answers of
tests/test_withdrawal_line.py. No network.
"""

import json
import pathlib
from unittest.mock import patch

import pytest

from moonlight import engine
from moonlight.engine import ApprovedMedicine, Tabs

import test_withdrawal_line as hem_a_page

ROOT = pathlib.Path(__file__).resolve().parent.parent
FILE = ROOT / "moonlight" / "withdrawals.json"
TEST_ENTRIES = ROOT / "fixtures" / "withdrawal_region" / "entries.json"

# The signed words, exactly.
US_LINE = "Its approval was withdrawn in the US. It may still be sold elsewhere."
EU_LINE = "Its approval was withdrawn in the EU. It may still be sold elsewhere."
HAND_LINE = "The maker or a regulator has withdrawn this medicine from the market."
WITHDRAWAL_LINE = "The database records a withdrawal for this medicine in some country or region."

HAEMOPHILIA_A, ALS = "MONDO_0010602", "MONDO_0004976"
ROCTAVIAN, RELYVRIO = "CHEMBL4297579", "CHEMBL1469"
EMICIZUMAB, TRANEXAMIC_ACID = "CHEMBL3833393", "CHEMBL877"  # the test-only entries
OCTOCOG_ALFA = "CHEMBL4297873"  # Open Targets already records a withdrawal for it


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def page(entries):
    """Haemophilia A's page with the real limits file and these withdrawals."""
    limits = load(ROOT / "moonlight" / "limits.json")
    with hem_a_page.left_out_before_2_43():
        return hem_a_page.page_answer(limits=limits, withdrawals=entries)


def card(answer, medicine_id):
    (found,) = [item for item in answer["approved"] if item["id"] == medicine_id]
    return found


def read(entries):
    with patch.object(engine, "_read_withdrawals", return_value=entries):
        return engine.withdrawals_by_hand()


@pytest.fixture(scope="module")
def with_regions():
    return page(load(TEST_ENTRIES))


@pytest.fixture(scope="module")
def without():
    return page([])


# ---- the words ----

def test_the_region_sentences_are_the_signed_words():
    assert engine.REGION_LINES == {"US": US_LINE, "EU": EU_LINE}


def test_the_sentence_with_no_region_is_unchanged():
    assert engine.HAND_WITHDRAWAL_LINE == HAND_LINE


# ---- the list ----

def test_the_test_entries_are_one_us_and_one_eu():
    assert [e["region"] for e in load(TEST_ENTRIES)] == ["US", "EU"]
    assert [w.region for w in read(load(TEST_ENTRIES))] == ["US", "EU"]


def test_the_real_file_has_no_region_and_does_not_change():
    entries = load(FILE)
    assert [(e["medicine_id"], e["disease_id"]) for e in entries] == [
        (ROCTAVIAN, HAEMOPHILIA_A), (RELYVRIO, ALS)]
    assert all(list(e) == ["medicine_id", "disease_id", "date", "source"] for e in entries)
    assert [w.region for w in engine.withdrawals_by_hand()] == [None, None]


@pytest.mark.parametrize("region", ["us", "Eu", "UK", "", None, 1, ["US"], "US "])
def test_a_region_that_is_not_exactly_us_or_eu_is_refused(region):
    entry = {**load(TEST_ENTRIES)[0], "region": region}
    with pytest.raises(ValueError):
        read([entry])


def test_any_other_extra_key_is_still_refused():
    entry = {**load(TEST_ENTRIES)[0], "country": "US"}
    with pytest.raises(ValueError):
        read([entry])


# ---- the cards ----

def test_the_us_and_eu_cards_show_the_exact_sentences(with_regions):
    assert card(with_regions, EMICIZUMAB)["withdrawal_note"] == US_LINE
    assert card(with_regions, TRANEXAMIC_ACID)["withdrawal_note"] == EU_LINE


def test_only_the_grey_line_changes(with_regions, without):
    # Same cards, same order, same boxes: no move.
    assert [c["id"] for c in with_regions["approved"]] == [c["id"] for c in without["approved"]]
    rest = {k: v for k, v in with_regions.items() if k != "approved"}
    assert rest == {k: v for k, v in without.items() if k != "approved"}
    changed = [a["id"] for a, b in zip(with_regions["approved"], without["approved"]) if a != b]
    assert changed == [EMICIZUMAB, TRANEXAMIC_ACID]
    for medicine_id in changed:
        after, before = card(with_regions, medicine_id), card(without, medicine_id)
        assert "withdrawal_note" not in before
        # No red: nothing but the grey line is added.
        assert {k: v for k, v in after.items() if k != "withdrawal_note"} == before
        assert medicine_id not in with_regions.get("wrong_approvals_box", [])


def test_the_databases_line_still_wins_over_a_region_entry(without):
    entry = {**load(TEST_ENTRIES)[0], "medicine_id": OCTOCOG_ALFA}
    assert card(page([entry]), OCTOCOG_ALFA)["withdrawal_note"] == WITHDRAWAL_LINE


# ---- Roctavian and Relyvrio are unchanged ----

def test_roctavian_keeps_todays_sentence():
    answer = page(load(FILE))
    assert card(answer, ROCTAVIAN)["withdrawal_note"] == HAND_LINE


def test_relyvrio_keeps_todays_sentence():
    relyvrio = ApprovedMedicine(RELYVRIO, "Sodium Phenylbutyrate", ("Sodium Phenylbutyrate",),
                                None, ())
    tabs = Tabs(approved=[relyvrio], being_studied=[], new_clues=[], left_out={})
    assert engine.hand_withdrawal_notes(tabs, ALS) == {RELYVRIO: HAND_LINE}
