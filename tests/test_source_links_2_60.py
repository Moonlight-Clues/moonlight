"""Ticket 2.60 (MAIN 4, 26 Nov). Two Source record links on the audited diseases.

Product's Task 3 (task3_26nov_90cards.csv) found on the main Approved lists of
the ten audited diseases:
  * row 46, type 2 diabetes, rosiglitazone (CHEMBL121): the Source record
    opened AVANDAMET, a combination product. It now opens the 2019 FDA label
    of AVANDIA (rosiglitazone maleate tablets), through source_overrides.json.
  * row 90, haemophilia A, valoctocogene roxaparvovec (CHEMBL4297579): the
    link in limits.json ended in "?attachment" and was reported as a 404.
    It is now https://www.fda.gov/media/169937/download. limits.json only
    holds the hand-read record; the card's Source record came from Open
    Targets' own link (also "?attachment"), so MAIN 4 approved (26 Nov, 7:35
    am) a second source_overrides.json row for the card. The label prints
    only "Revised: 06/2023", so its date, 2023-06-01, is a placeholder day.

Lists only. Saved answers only, no network. The row count of
source_overrides.json is checked against c5cb017 (the base) in
fixtures/source_overrides/source_overrides_c5cb017.json.
"""

import json
import pathlib
from unittest.mock import patch

import pytest

from moonlight import engine

# Ticket 2.62: the signed rows of tests/test_red_warnings_2_62.py (delete a row there and these follow).
from test_red_warnings_2_62 import LIMIT_ROWS, RED_ROWS  # noqa: E402

import old_flag_saved as t2d_saved
import test_withdrawal_line as hem_a_saved

ROOT = pathlib.Path(__file__).resolve().parent.parent
OVERRIDES_FILE = ROOT / "moonlight" / "source_overrides.json"
LIMITS_FILE = ROOT / "moonlight" / "limits.json"
WITHDRAWALS_FILE = ROOT / "moonlight" / "withdrawals.json"
BASE_OVERRIDES = ROOT / "fixtures" / "source_overrides" / "source_overrides_c5cb017.json"

T2D, HAEMOPHILIA_A = "MONDO_0005148", "MONDO_0010602"
ROSIGLITAZONE, ROCTAVIAN = "CHEMBL121", "CHEMBL4297579"

AVANDIA_PDF = "https://www.accessdata.fda.gov/drugsatfda_docs/label/2019/021071s052lbl.pdf"
AVANDAMET = ("https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm"
             "?setid=0789dc6b-db34-44a6-8a5d-fdcc8e4ce8fd")
# Section 1 of that PDF, word for word.
AVANDIA_SENTENCE = ("AVANDIA is a thiazolidinedione antidiabetic agent indicated as an adjunct "
                    "to diet and exercise to improve glycemic control in adults with type 2 "
                    "diabetes mellitus.")
ROW_AVANDIA = {"medicine_id": ROSIGLITAZONE, "disease_id": T2D, "url": AVANDIA_PDF,
       "date": "2019-02-05", "note": AVANDIA_SENTENCE,
       "evidence_file": "task3_26nov_90cards.csv"}

ROCTAVIAN_LINK = "https://www.fda.gov/media/169937/download"
ROCTAVIAN_SENTENCE = ("ROCTAVIAN is an adeno-associated virus vector-based gene therapy indicated "
                      "for the treatment of adults with severe hemophilia A (congenital factor VIII "
                      "deficiency with factor VIII activity < 1 IU/dL) without antibodies to "
                      "adeno-associated virus serotype 5 (AAV5) detected by an FDA-approved test.")
ROW_ROCTAVIAN = {"medicine_id": ROCTAVIAN, "disease_id": HAEMOPHILIA_A, "url": ROCTAVIAN_LINK,
                 "date": "2023-06-01", "note": ROCTAVIAN_SENTENCE,
                 "evidence_file": "task3_26nov_90cards.csv"}
ROCTAVIAN_OLD_LINK = ROCTAVIAN_LINK + "?attachment"
LIMITED_LINE = "The label covers only some people with this disease."
ROCTAVIAN_WITHDRAWAL_LINE = "The maker or a regulator has withdrawn this medicine from the market."  # withdrawals.json, ticket 2.51
ROSIGLITAZONE_WITHDRAWAL_LINE = ("The database records a withdrawal for this medicine in some "
                                 "country or region.")


def load(file):
    return json.loads(file.read_text(encoding="utf-8"))


def by_id(cards):
    return {card["id"]: card for card in cards}


# ---- source_overrides.json: one more row than on c5cb017, none lost ----

def test_the_base_copy_is_the_54_rows_of_c5cb017():
    assert len(load(BASE_OVERRIDES)) == 54


def test_the_file_is_the_base_plus_exactly_two_rows_at_the_end():
    base, now = load(BASE_OVERRIDES), load(OVERRIDES_FILE)
    # Ticket 2.61 (26 Nov) added one row after these (givosiran): 57 rows.
    assert len(now) == len(base) + 3 == 57
    assert now[:54] == base  # no row lost, none changed, same order
    assert now[54:56] == [ROW_AVANDIA, ROW_ROCTAVIAN]


def test_each_new_pair_is_written_once_and_the_engine_reads_both_links():
    pairs = [(e["medicine_id"], e["disease_id"]) for e in load(OVERRIDES_FILE)]
    assert pairs.count((ROSIGLITAZONE, T2D)) == 1
    assert pairs.count((ROCTAVIAN, HAEMOPHILIA_A)) == 1
    found = engine.source_overrides()
    assert found[(ROSIGLITAZONE, T2D)] == AVANDIA_PDF
    assert found[(ROCTAVIAN, HAEMOPHILIA_A)] == ROCTAVIAN_LINK


# ---- type 2 diabetes ----

@pytest.fixture(scope="module")
def t2d_now():
    return t2d_saved.page_answer(T2D)


@pytest.fixture(scope="module")
def t2d_before():
    base = load(BASE_OVERRIDES)
    with patch.object(engine, "_read_source_overrides", return_value=base):
        return t2d_saved.page_answer(T2D)


def test_before_this_ticket_rosiglitazone_opened_avandamet(t2d_before):
    assert by_id(t2d_before["approved"])[ROSIGLITAZONE]["source"] == AVANDAMET


def test_rosiglitazones_source_record_is_the_2019_avandia_pdf(t2d_now):
    assert by_id(t2d_now["approved"])[ROSIGLITAZONE]["source"] == AVANDIA_PDF


def test_rosiglitazone_keeps_its_withdrawal_line_and_stays_on_the_main_list(t2d_now, t2d_before):
    now = by_id(t2d_now["approved"])[ROSIGLITAZONE]
    assert now["withdrawal_note"] == ROSIGLITAZONE_WITHDRAWAL_LINE
    assert [c["id"] for c in t2d_now["approved"]] == [c["id"] for c in t2d_before["approved"]]


def test_every_other_card_and_part_of_the_page_is_unchanged(t2d_now, t2d_before):
    assert len(t2d_now["approved"]) == len(t2d_before["approved"])
    changed = [a["id"] for a, b in zip(t2d_now["approved"], t2d_before["approved"]) if a != b]
    assert changed == [ROSIGLITAZONE]
    now = by_id(t2d_now["approved"])[ROSIGLITAZONE]
    before = by_id(t2d_before["approved"])[ROSIGLITAZONE]
    assert {k: v for k, v in now.items() if k != "source"} == \
           {k: v for k, v in before.items() if k != "source"}
    assert {k: v for k, v in t2d_now.items() if k != "approved"} == \
           {k: v for k, v in t2d_before.items() if k != "approved"}


# ---- haemophilia A ----

def hem_a_page(overrides):
    return hem_a_saved.page_answer(
        HAEMOPHILIA_A, limits=load(LIMITS_FILE), withdrawals=load(WITHDRAWALS_FILE))


@pytest.fixture(scope="module")
def hem_a_now():
    return hem_a_page(None)


@pytest.fixture(scope="module")
def hem_a_before():
    with patch.object(engine, "_read_source_overrides", return_value=load(BASE_OVERRIDES)):
        return hem_a_page(None)


def roctavian_entries():
    return [e for e in load(LIMITS_FILE) if e["medicine_id"] == ROCTAVIAN]


def test_the_limits_row_has_the_link_without_attachment_and_nothing_else_changed():
    (row,) = roctavian_entries()
    assert row == {"medicine_id": ROCTAVIAN, "disease_id": HAEMOPHILIA_A,
                   "date": "2026-11-25", "label": ROCTAVIAN_LINK}
    assert "?attachment" not in LIMITS_FILE.read_text(encoding="utf-8")


def test_only_that_one_line_of_limits_json_differs_from_c5cb017():
    import subprocess
    old = subprocess.run(["git", "show", "c5cb017:moonlight/limits.json"], cwd=ROOT,
                         capture_output=True, text=True, check=True).stdout
    now = LIMITS_FILE.read_text(encoding="utf-8")
    # Ticket 2.62 appended LIMIT_ROWS (one line each) at the end of the list: take them off.
    lines = now.rstrip().split("\n")
    if LIMIT_ROWS:
        keep = lines[:-1 - len(LIMIT_ROWS)]
        keep[-1] = keep[-1].rstrip(",")
        now = "\n".join(keep + [lines[-1]]) + "\n"
    assert now == old.replace(ROCTAVIAN_OLD_LINK, ROCTAVIAN_LINK)


def test_before_this_ticket_the_roctavian_card_opened_the_attachment_link(hem_a_before):
    assert by_id(hem_a_before["approved"])[ROCTAVIAN]["source"] == ROCTAVIAN_OLD_LINK


def test_the_roctavian_cards_source_record_is_the_new_link(hem_a_now):
    assert by_id(hem_a_now["approved"])[ROCTAVIAN]["source"] == ROCTAVIAN_LINK


def test_its_limit_line_and_withdrawal_line_are_unchanged(hem_a_now, hem_a_before):
    now = by_id(hem_a_now["approved"])[ROCTAVIAN]
    before = by_id(hem_a_before["approved"])[ROCTAVIAN]
    assert now["limit_note"] == before["limit_note"] == LIMITED_LINE
    assert now["withdrawal_note"] == before["withdrawal_note"] == ROCTAVIAN_WITHDRAWAL_LINE
    assert {k: v for k, v in now.items() if k != "source"} == \
           {k: v for k, v in before.items() if k != "source"}


def test_no_other_card_or_part_of_the_haemophilia_a_page_changes(hem_a_now, hem_a_before):
    assert len(hem_a_now["approved"]) == len(hem_a_before["approved"])
    changed = [a["id"] for a, b in zip(hem_a_now["approved"], hem_a_before["approved"]) if a != b]
    assert changed == [ROCTAVIAN]
    assert {k: v for k, v in hem_a_now.items() if k != "approved"} == \
           {k: v for k, v in hem_a_before.items() if k != "approved"}
