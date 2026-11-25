"""Ticket 2.50: Roctavian (valoctocogene roxaparvovec, CHEMBL4297579) for
haemophilia A (MONDO_0010602). Reported error E36.

One change, under an existing rule (Kashish, signed 24 Nov): the FDA label
covers only adults with severe haemophilia A WITHOUT antibodies to AAV5
"detected by an FDA-approved test". A test result is required, so the card,
which the database itself records, goes in moonlight/limits.json (ticket
2.39's list). The card then carries "The label covers only some people with
this disease."

Reported, not changed: the maker (23 Feb 2026) and the European Commission
(decision of 30 Apr 2026, from 29 May 2026) record a withdrawal. The
withdrawal line (ticket 2.31) comes only from Open Targets data, and Open
Targets 26.09 holds no withdrawal for Roctavian. So no withdrawal line.

Saved files only: fixtures/labels_read/2.50/ and fixtures/withdrawal_reports/.
No network.
"""

import json
import pathlib

import pytest

from moonlight import engine

import test_withdrawal_line as hem_a_page

ROOT = pathlib.Path(__file__).resolve().parent.parent
LIMITS_FILE = ROOT / "moonlight" / "limits.json"
APPROVALS_FILE = ROOT / "moonlight" / "approvals.json"
FOLDER = ROOT / "fixtures" / "labels_read" / "2.50"
README = FOLDER / "README.md"

HAEMOPHILIA_A = "MONDO_0010602"
ROCTAVIAN = "CHEMBL4297579"
FDA_INSERT = "https://www.fda.gov/media/169937/download?attachment"
LIMITED_LINE = "The label covers only some people with this disease."
WITHDRAWAL_LINE = "The database records a withdrawal for this medicine in some country or region."

ENTRY = {"medicine_id": ROCTAVIAN, "disease_id": HAEMOPHILIA_A,
         "date": "2026-11-25", "label": FDA_INSERT}

INDICATION = ("ROCTAVIAN is an adeno-associated virus vector-based gene therapy indicated "
              "for the treatment of adults with severe hemophilia A (congenital factor VIII "
              "deficiency with factor VIII activity < 1 IU/dL) without antibodies to "
              "adeno-associated virus serotype 5 (AAV5) detected by an FDA-approved test.")


def load(file):
    return json.loads(file.read_text(encoding="utf-8"))


def text(*parts):
    return FOLDER.joinpath(*parts).read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def page():
    with hem_a_page.left_out_before_2_43():
        return hem_a_page.page_answer(limits=load(LIMITS_FILE))  # the real limits file


def roctavian_card(answer):
    (card,) = [item for item in answer["approved"] if item["id"] == ROCTAVIAN]
    return card


# ---- the change: limits.json ----

def test_limits_json_holds_the_roctavian_entry_once():
    assert [e for e in load(LIMITS_FILE) if e["medicine_id"] == ROCTAVIAN] == [ENTRY]
    assert engine.HandLimit(ROCTAVIAN, HAEMOPHILIA_A, FDA_INSERT) in engine.limits_by_hand()


def test_roctavian_is_not_also_in_approvals_json():
    # The card comes from the database, so it is marked in limits.json only.
    assert ROCTAVIAN not in {e["medicine_id"] for e in load(APPROVALS_FILE)}


def test_the_saved_label_requires_a_test_result():
    saved = text("labels", "roctavian-fda-package-insert.txt")
    assert saved.splitlines()[0] == FDA_INSERT
    assert INDICATION in saved
    assert "detected by an FDA-approved test" in INDICATION


def test_the_card_carries_the_limited_line_and_keeps_its_place(page):
    card = roctavian_card(page)
    assert card["limit_note"] == LIMITED_LINE
    assert card["source"] == FDA_INSERT == ENTRY["label"]  # the card's own source link
    others = [item for item in page["approved"] if item["id"] != ROCTAVIAN]
    assert all("limit_note" not in item for item in others)


# ---- reported, not changed: the withdrawal ----

def test_open_targets_today_has_no_withdrawal_for_roctavian():
    rows = load(FOLDER / "disease_drugs" / f"{HAEMOPHILIA_A}.response.json")
    rows = rows["data"]["disease"]["drugAndClinicalCandidates"]["rows"]
    (row,) = [r for r in rows if r["drug"]["id"] == ROCTAVIAN]
    assert row["drug"]["drugWarnings"] == []
    assert "WITHDRAWAL" not in {report["clinicalStage"] for report in row["clinicalReports"]}


def test_the_card_has_no_withdrawal_line(page):
    assert "withdrawal_note" not in roctavian_card(page)
    assert WITHDRAWAL_LINE not in json.dumps(roctavian_card(page))


def test_the_regulator_and_maker_statements_are_saved():
    commission = text("withdrawal", "european-commission-decision-c-2026-3038.txt")
    assert "shall be applicable with effect from 29 May 2026" in commission
    maker = text("withdrawal", "biomarin-statement-2026-02-23.txt")
    assert "will voluntarily remove ROCTAVIAN" in maker


# ---- the README line ----

def test_readme_has_one_line_for_the_card():
    lines = [line for line in README.read_text(encoding="utf-8").splitlines()
             if line.startswith("Roctavian") and line.count(" | ") == 4]
    assert len(lines) == 1
    card, shows, quoted, link, change = lines[0].split(" | ")
    assert ROCTAVIAN in card and HAEMOPHILIA_A in card
    assert quoted == INDICATION
    assert link == FDA_INSERT
    assert "limits.json" in change
