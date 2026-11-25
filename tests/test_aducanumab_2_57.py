"""Ticket 2.57: aducanumab (Aduhelm, CHEMBL3039540) on Alzheimer disease
(MONDO_0004975) gets the existing withdrawal sentence, from the hand-written
list moonlight/withdrawals.json. The FDA's list of withdrawn accelerated
approvals has "Aduhelm (aducanumab-avwa) | 6/7/2021 | 11/1/2024". No new
wording and no engine change: the sentence is engine.HAND_WITHDRAWAL_LINE.

Saved files only (fixtures/approval_proof/MONDO_0004975). No network.
"""

import json
import pathlib

import pytest

from moonlight import engine

import test_approval_proof as proof
import test_withdrawal_line as pages

ROOT = pathlib.Path(__file__).resolve().parent.parent
FILE = ROOT / "moonlight" / "withdrawals.json"

ALZHEIMER = "MONDO_0004975"
ADUCANUMAB = "CHEMBL3039540"
LINE = "The maker or a regulator has withdrawn this medicine from the market."
FDA = ("https://www.fda.gov/drugs/accelerated-approval-program/"
       "withdrawn-non-malignant-hematological-neurological-and-other-disorder-"
       "indications-accelerated")
ENTRY = {"medicine_id": ADUCANUMAB, "disease_id": ALZHEIMER,
         "date": "2026-11-25", "source": FDA}


def post_json(body):
    proof._searched["id"] = ALZHEIMER
    return proof.proof_post_json(body)


def page(entries):
    return pages.page_answer(ALZHEIMER, post_json=post_json, withdrawals=entries)


def card(answer):
    (found,) = [c for c in answer["approved"] if c["id"] == ADUCANUMAB]
    return found


@pytest.fixture(scope="module")
def with_entry():
    return page([ENTRY])


@pytest.fixture(scope="module")
def without_entry():
    return page([])


def test_the_file_ends_with_the_aducanumab_entry():
    entries = json.loads(FILE.read_text(encoding="utf-8"))
    # Ticket 2.59 adds two entries (tolazamide, tolbutamide) after this one.
    assert entries[-3] == ENTRY
    assert engine.withdrawals_by_hand()[-3] == engine.HandWithdrawal(ADUCANUMAB, ALZHEIMER, FDA)


def test_the_words_are_the_existing_sentence():
    assert engine.HAND_WITHDRAWAL_LINE == LINE


def test_the_aducanumab_card_shows_the_withdrawal_sentence(with_entry, without_entry):
    assert card(with_entry)["withdrawal_note"] == LINE
    assert "withdrawal_note" not in card(without_entry)


def test_no_other_card_on_the_page_changes(with_entry, without_entry):
    assert [c["id"] for c in with_entry["approved"]] == [c["id"] for c in without_entry["approved"]]
    changed = [a["id"] for a, b in zip(with_entry["approved"], without_entry["approved"]) if a != b]
    assert changed == [ADUCANUMAB]
    after, before = card(with_entry), card(without_entry)
    assert {k: v for k, v in after.items() if k != "withdrawal_note"} == before
    rest = {k: v for k, v in with_entry.items() if k != "approved"}
    assert rest == {k: v for k, v in without_entry.items() if k != "approved"}
