"""Ticket 2.51: withdrawals written by hand. A grey line when the maker or a
regulator says so (decision of 25 Nov, Shreshth, option A).

moonlight/withdrawals.json is a hand-written list in the form of limits.json:
{"medicine_id", "disease_id", "date", "source"}. A card on the main Approved
list that matches an entry carries one more grey line, HAND_WITHDRAWAL_LINE,
in the same place as WITHDRAWAL_LINE (the card's "withdrawal_note"). The card
is not hidden, moved, re-counted or re-ordered. A card that already carries
WITHDRAWAL_LINE shows only that one.

Saved files only (fixtures/labels_read/2.50/). No network.
"""

import copy
import json
import pathlib
import shutil
import subprocess
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from moonlight import api, engine

import test_print_page as print_tests
import test_withdrawal_line as hem_a_page

ROOT = pathlib.Path(__file__).resolve().parent.parent
FILE = ROOT / "moonlight" / "withdrawals.json"
README = ROOT / "fixtures" / "labels_read" / "2.50" / "README.md"

HAEMOPHILIA_A = "MONDO_0010602"
ROCTAVIAN = "CHEMBL4297579"
OCTOCOG_ALFA = "CHEMBL4297873"  # Open Targets already records a withdrawal for it
BIOMARIN = ("https://www.biomarin.com/news/company-statements/"
            "biomarin-voluntarily-withdraws-roctavian-from-the-market/")
HAND_LINE = "The maker or a regulator has withdrawn this medicine from the market."
WITHDRAWAL_LINE = "The database records a withdrawal for this medicine in some country or region."
LIMITED_LINE = "The label covers only some people with this disease."

ENTRY = {"medicine_id": ROCTAVIAN, "disease_id": HAEMOPHILIA_A,
         "date": "2026-11-25", "source": BIOMARIN}


def page(entries):
    """Haemophilia A's page with the real limits file and these withdrawals."""
    limits = json.loads((ROOT / "moonlight" / "limits.json").read_text(encoding="utf-8"))
    with hem_a_page.left_out_before_2_43():
        return hem_a_page.page_answer(limits=limits, withdrawals=entries)


def card(answer, medicine_id):
    (found,) = [item for item in answer["approved"] if item["id"] == medicine_id]
    return found


@pytest.fixture(scope="module")
def with_entry():
    return page([ENTRY])


@pytest.fixture(scope="module")
def without_entry():
    return page([])


# ---- the list ----

def test_the_file_holds_the_one_entry():
    # Ticket 2.54, signed answer Q14: Relyvrio on ALS (CHEMBL1469) is the second entry.
    # Ticket 2.57 (approved 25 Nov, Shreshth): aducanumab on Alzheimer disease is the
    # third and last entry; tests/test_aducanumab_2_57.py holds it.
    assert json.loads(FILE.read_text(encoding="utf-8"))[0] == ENTRY
    assert len(json.loads(FILE.read_text(encoding="utf-8"))) == 5  # ticket 2.59 adds two
    assert engine.withdrawals_by_hand()[0] == engine.HandWithdrawal(
        ROCTAVIAN, HAEMOPHILIA_A, BIOMARIN)


def test_the_source_is_the_link_written_in_the_2_50_readme():
    assert BIOMARIN in README.read_text(encoding="utf-8")


def test_the_words_are_one_constant():
    assert engine.HAND_WITHDRAWAL_LINE == HAND_LINE


def read(entries):
    with patch.object(engine, "_read_withdrawals", return_value=entries):
        return engine.withdrawals_by_hand()


@pytest.mark.parametrize("key", sorted(ENTRY))
def test_a_missing_key_is_refused(key):
    entry = {k: v for k, v in ENTRY.items() if k != key}
    with pytest.raises(ValueError):
        read([entry])


def test_an_extra_key_is_refused():
    with pytest.raises(ValueError):
        read([{**ENTRY, "reason": "news"}])


@pytest.mark.parametrize("source", ["http://www.biomarin.com/x", "biomarin.com", "", None, 5])
def test_a_source_that_is_not_an_https_link_is_refused(source):
    with pytest.raises(ValueError):
        read([{**ENTRY, "source": source}])


def test_a_list_that_is_not_a_list_and_a_pair_written_twice_are_refused():
    with pytest.raises(ValueError):
        read({"medicine_id": ROCTAVIAN})
    with pytest.raises(ValueError):
        read([ENTRY, copy.deepcopy(ENTRY)])


def test_a_bad_file_stops_the_app_at_start_up():
    bad = [{k: v for k, v in ENTRY.items() if k != "source"}]
    with patch.object(engine, "_read_withdrawals", return_value=bad):
        with pytest.raises(ValueError):
            with TestClient(api.app):
                pass


# ---- the card ----

def test_roctavians_card_carries_both_lines_on_the_main_list(with_entry, without_entry):
    roctavian = card(with_entry, ROCTAVIAN)
    assert roctavian["withdrawal_note"] == HAND_LINE
    assert roctavian["limit_note"] == LIMITED_LINE
    assert roctavian["source"] == "https://www.fda.gov/media/169937/download"  # ticket 2.60: source_overrides.json, was "?attachment" from Open Targets
    # Not hidden, moved, re-counted or re-ordered: the same ids in the same order.
    assert [i["id"] for i in with_entry["approved"]] == [i["id"] for i in without_entry["approved"]]
    assert len(with_entry["approved"]) == len(without_entry["approved"])
    assert "withdrawal_note" not in card(without_entry, ROCTAVIAN)


def test_only_roctavians_card_changes(with_entry, without_entry):
    changed = [a["id"] for a, b in zip(with_entry["approved"], without_entry["approved"]) if a != b]
    assert changed == [ROCTAVIAN]
    rest = {k: v for k, v in with_entry.items() if k != "approved"}
    assert rest == {k: v for k, v in without_entry.items() if k != "approved"}
    after, before = card(with_entry, ROCTAVIAN), card(without_entry, ROCTAVIAN)
    assert {k: v for k, v in after.items() if k != "withdrawal_note"} == before


def test_a_card_with_an_open_targets_withdrawal_shows_only_that_line(without_entry):
    assert card(without_entry, OCTOCOG_ALFA)["withdrawal_note"] == WITHDRAWAL_LINE
    both = page([ENTRY, {**ENTRY, "medicine_id": OCTOCOG_ALFA}])
    assert card(both, OCTOCOG_ALFA)["withdrawal_note"] == WITHDRAWAL_LINE
    assert HAND_LINE not in json.dumps(card(both, OCTOCOG_ALFA))
    assert card(both, ROCTAVIAN)["withdrawal_note"] == HAND_LINE


def test_an_entry_for_a_medicine_not_on_the_page_changes_nothing(without_entry):
    other = page([{**ENTRY, "medicine_id": "CHEMBL25"}])  # aspirin: not on this page
    assert other == without_entry


def test_an_entry_for_another_disease_changes_nothing(without_entry):
    other = page([{**ENTRY, "disease_id": "MONDO_0005148"}])
    assert other == without_entry


# ---- the printed page ----

def test_the_print_page_shows_the_line(with_entry, tmp_path):
    node = shutil.which("node")
    if not node or subprocess.run(
            [node, "-e", "require('playwright')"], capture_output=True).returncode:
        pytest.skip("needs node with playwright to open a real browser")
    answers = tmp_path / "answers.json"
    answers.write_text(json.dumps({"hem_a": with_entry}), encoding="utf-8")
    run = subprocess.run(
        [node, "-e", print_tests.BROWSER_SCRIPT, str(print_tests.PAGE_FILE), str(answers)],
        capture_output=True, text=True, timeout=240, cwd=str(ROOT))
    assert run.returncode == 0, run.stderr[-3000:]
    seen = json.loads(run.stdout)["hem_a"]
    (on_screen,) = [c for c in seen["screen"]["main"] if c["name"] == "Valoctocogene Roxaparvovec"]
    (printed,) = [c for c in seen["register"]["main"] if c["name"] == "Valoctocogene Roxaparvovec"]
    assert HAND_LINE in on_screen["lines"] and LIMITED_LINE in on_screen["lines"]
    assert HAND_LINE in printed["notes"] and LIMITED_LINE in printed["notes"]
    assert seen["errors"] == []
