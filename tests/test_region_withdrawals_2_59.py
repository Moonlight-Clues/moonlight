"""Ticket 2.59, batch 1: two US region withdrawals on type 2 diabetes.

MAIN 4 read both Federal Register notices by hand on 25 Nov. Tolazamide
(CHEMBL817) and tolbutamide (CHEMBL782) are on the main Approved list of
type 2 diabetes (MONDO_0005148) with no database withdrawal line, so each
card shows the US sentence (ticket 3.19), once, and stays on the main list.
No other card changes. Saved answers only (old_flag_saved.py). No network.
"""

import json
import pathlib
from unittest.mock import patch

import pytest

from moonlight import engine

import old_flag_saved as saved

ROOT = pathlib.Path(__file__).resolve().parent.parent
FILE = ROOT / "moonlight" / "withdrawals.json"

T2D = "MONDO_0005148"
TOLAZAMIDE, TOLBUTAMIDE = "CHEMBL817", "CHEMBL782"
US_LINE = "Its approval was withdrawn in the US. It may still be sold elsewhere."
FR = "https://www.federalregister.gov/documents/"
SOURCES = {
    TOLAZAMIDE: FR + "2009/05/19/E9-11628/novartis-pharmaceuticals-corp-et-al-"
                     "withdrawal-of-approval-of-92-new-drug-applications-and-49",
    TOLBUTAMIDE: FR + "2007/11/07/E7-21886/lederle-laboratories-et-al-"
                      "withdrawal-of-approval-of-73-new-drug-applications-and-62-abbreviated-new",
}


def entries():
    return json.loads(FILE.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def with_entries():
    return saved.page_answer(T2D)


@pytest.fixture(scope="module")
def without_entries():
    keep = [e for e in entries() if e["medicine_id"] not in SOURCES]
    with patch.object(engine, "_read_withdrawals", return_value=keep):
        return saved.page_answer(T2D)


def test_the_file_has_the_two_us_entries_at_the_end():
    for entry, medicine_id in zip(entries()[-2:], (TOLAZAMIDE, TOLBUTAMIDE)):
        assert entry == {"medicine_id": medicine_id, "disease_id": T2D, "region": "US",
                         "date": "2026-11-26", "source": SOURCES[medicine_id]}


@pytest.mark.parametrize("medicine_id", [TOLAZAMIDE, TOLBUTAMIDE])
def test_the_card_shows_the_us_sentence_exactly_once(with_entries, without_entries, medicine_id):
    (card,) = [c for c in with_entries["approved"] if c["id"] == medicine_id]
    assert card["withdrawal_note"] == US_LINE
    assert json.dumps(with_entries).count(US_LINE) == 2  # one per card, nowhere else
    (before,) = [c for c in without_entries["approved"] if c["id"] == medicine_id]
    assert "withdrawal_note" not in before
    assert {k: v for k, v in card.items() if k != "withdrawal_note"} == before


@pytest.mark.parametrize("medicine_id", [TOLAZAMIDE, TOLBUTAMIDE])
def test_the_card_stays_on_the_main_list(with_entries, without_entries, medicine_id):
    ids = [c["id"] for c in with_entries["approved"]]
    assert ids == [c["id"] for c in without_entries["approved"]]  # same cards, same order
    for part in ("wrong_approvals_box", "no_regulator_box"):
        assert medicine_id not in json.dumps(with_entries.get(part, []))


def test_no_other_card_or_part_of_the_page_changes(with_entries, without_entries):
    changed = [a["id"] for a, b in zip(with_entries["approved"], without_entries["approved"])
               if a != b]
    assert changed == [TOLAZAMIDE, TOLBUTAMIDE]
    rest = {k: v for k, v in with_entries.items() if k != "approved"}
    assert rest == {k: v for k, v in without_entries.items() if k != "approved"}
