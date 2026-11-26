"""Ticket 2.68, part B. Japan cards link the PMDA English summary.

A card on the main Approved list whose only proof today is Japan's general
list (JAPAN_LINE) and that moonlight/pmda_summaries.json names for its page:
  * shows "Approved in Japan (English summary, {year}). The full label is in
    Japanese." instead of JAPAN_LINE, {year} being the year of the entry's
    summary_date;
  * opens the entry's link as its Source record;
  * leaves the Japan folded box (no_regulator_box) for the main list.
A card with no entry keeps JAPAN_LINE. No other card changes.

Shreshth's words of 26 Nov (Kashish signs 27 Nov).

Saved answers only, no network. The type 2 diabetes page is built from
fixtures/gene_evidence/ (as tests/test_gene_evidence.py does), with the real
hand-written files. The entries in the page tests below are made up for the
test: their links and dates are NOT the real PMDA ones. The real file is
checked in the last section.
"""

import copy
import datetime
import json
import pathlib
import urllib.parse
from unittest.mock import patch

import pytest

from moonlight import engine
from moonlight.engine import ApprovedMedicine

import test_gene_evidence as t2d_files

ROOT = pathlib.Path(__file__).resolve().parent.parent
REAL_FILE = ROOT / "moonlight" / "pmda_summaries.json"

T2D = "MONDO_0005148"
TRELAGLIPTIN = "CHEMBL1650443"
OMARIGLIPTIN = "CHEMBL2105762"
VOGLIBOSE = "CHEMBL476960"
LINAGLIPTIN = "CHEMBL237500"  # a card with a US label: out of scope

JAPAN_LIST = ("https://www.pmda.go.jp/english/review-services/reviews/"
              "approved-information/drugs/0001.html")
# Kashish's words of 16 Nov, exactly. Kept for a card with no entry.
JAPAN_LINE = ("Approved in Japan, according to the database. Moonlight could not "
              "find the exact record for this disease.")
NO_REGULATOR_LINE = "The database lists this as approved, but gives no regulator record for it."
ADDED_LINE = "This approval is missing from the database. We added it from the official label."

# Made up for the tests: not real PMDA pages.
TEST_LINK_A = "https://www.pmda.go.jp/files/000000001.pdf"
TEST_LINK_B = "https://www.pmda.go.jp/files/000000002.pdf"


def line(year):
    """The ticket's sentence, written out here by hand, letter for letter."""
    return f"Approved in Japan (English summary, {year}). The full label is in Japanese."


def entry(medicine_id, disease_id=T2D, summary_date="2015-03-26", link=TEST_LINK_A, **extra):
    row = {"medicine_id": medicine_id, "disease_id": disease_id, "date": "2026-11-27",
           "summary_date": summary_date, "link": link}
    row.update(extra)
    return row


def with_entries(entries):
    return patch.object(engine, "_read_pmda_summaries", return_value=entries)


# ---- 1. the engine, with cards made in the test ----

def card(medicine_id, name="X", *, approval=(JAPAN_LIST,), regulator=None, added=None,
         confirmed=None):
    return ApprovedMedicine(id=medicine_id, name=name, forms=(name,), clue=None,
                            listed_sources=approval, approval_sources=approval,
                            regulator_record=regulator, added_from_label=added,
                            confirmed_from_label=confirmed)


def test_the_line_is_the_tickets_sentence_with_the_year():
    assert engine.pmda_line("2012") == line(2012)
    assert engine.pmda_line("2012") == (
        "Approved in Japan (English summary, 2012). The full label is in Japanese.")


def test_the_japan_line_itself_is_not_changed():
    assert engine.JAPAN_LINE == JAPAN_LINE


def test_a_japan_card_with_an_entry_carries_the_exact_line_and_link():
    with with_entries([entry("A", summary_date="2012-09-28")]):
        [done] = engine.link_pmda_summaries([card("A")], T2D)
    assert done.proof_note == line(2012)
    assert done.source_record == TEST_LINK_A


def test_the_year_is_the_year_of_summary_date_not_of_date():
    with with_entries([entry("A", summary_date="2015-03-26")]):
        [done] = engine.link_pmda_summaries([card("A")], T2D)
    assert done.proof_note == line(2015)


def test_a_japan_card_with_no_entry_keeps_the_japan_line_and_link():
    with with_entries([entry("A")]):
        [_, kept] = engine.link_pmda_summaries([card("A"), card("B")], T2D)
    assert kept == card("B")
    assert kept.proof_note == JAPAN_LINE
    assert kept.source_record == JAPAN_LIST


def test_an_entry_works_only_for_its_own_disease():
    with with_entries([entry("A", disease_id="MONDO_0000001")]):
        [kept] = engine.link_pmda_summaries([card("A")], T2D)
    assert kept == card("A")
    assert kept.proof_note == JAPAN_LINE


def test_an_entry_does_nothing_to_a_card_without_the_japan_line():
    others = [
        card("A", approval=("https://www.accessdata.fda.gov/x.pdf",), regulator=True),
        card("A", approval=(), regulator=False),  # NO_REGULATOR_LINE
        card("A", added="https://dailymed.nlm.nih.gov/x"),  # ADDED_LINE
        card("A", confirmed="https://dailymed.nlm.nih.gov/y"),  # no line
    ]
    with with_entries([entry("A")]):
        done = engine.link_pmda_summaries(others, T2D)
    assert done == others


def test_the_order_is_kept_and_nothing_is_added_or_taken_off():
    cards = [card("C"), card("A"), card("B")]
    with with_entries([entry("A"), entry("Z")]):
        done = engine.link_pmda_summaries(cards, T2D)
    assert [medicine.id for medicine in done] == ["C", "A", "B"]


def test_a_card_with_an_entry_leaves_the_japan_box():
    with with_entries([entry("A")]), \
            patch.object(engine, "_read_corrections", return_value=[]):
        cards = engine.link_pmda_summaries([card("A"), card("B")], T2D)
        assert [medicine.id for medicine in engine.no_regulator_box(cards, T2D)] == ["B"]


# ---- 2. the file is checked ----

@pytest.mark.parametrize("change", [
    {"summary_date": ""},                       # a summary with no approval date
    {"summary_date": None},
    {"summary_date": "2012"},                   # not YYYY-MM-DD
    {"summary_date": "28 Sep 2012"},
    {"summary_date": "2012-13-01"},
    {"date": "yesterday"},
    {"link": "http://www.pmda.go.jp/files/1.pdf"},   # not https
    {"link": "https://www.pmda.go.jp.example.com/1.pdf"},  # not on pmda.go.jp
    {"link": "https://www.fda.gov/1.pdf"},
    {"link": JAPAN_LIST},                       # the general list is not a summary
    {"link": ""},
    {"medicine_id": ""},
    {"disease_id": ""},
    {"date_source": ""},
    {"date_source": 7},
    {"doctor": "someone"},
])
def test_an_entry_not_written_properly_is_refused(change):
    row = entry("A")
    row.update(change)
    with with_entries([row]):
        with pytest.raises(ValueError):
            engine.pmda_summaries()


@pytest.mark.parametrize("missing", ["medicine_id", "disease_id", "date", "summary_date", "link"])
def test_an_entry_with_a_piece_missing_is_refused(missing):
    row = entry("A")
    del row[missing]
    with with_entries([row]):
        with pytest.raises(ValueError):
            engine.pmda_summaries()


def test_an_entry_may_say_where_its_date_came_from():
    with with_entries([entry("A", date_source="the summary's approval line")]):
        assert engine.pmda_summaries() == {("A", T2D): (TEST_LINK_A, "2015")}


def test_a_file_that_is_not_a_list_is_refused():
    with with_entries({"medicine_id": "A"}):
        with pytest.raises(ValueError):
            engine.pmda_summaries()


def test_the_same_pair_written_twice_is_refused():
    with with_entries([entry("A"), entry("A", link=TEST_LINK_B)]):
        with pytest.raises(ValueError):
            engine.pmda_summaries()


# ---- 3. the type 2 diabetes page, from saved answers ----

def page(entries):
    with with_entries(entries):
        return t2d_files.page_answer(T2D)


@pytest.fixture(scope="module")
def before():
    return page([])


@pytest.fixture(scope="module")
def after():
    return page([entry(TRELAGLIPTIN, summary_date="2015-03-26", link=TEST_LINK_A),
                 entry(OMARIGLIPTIN, summary_date="2015-09-28", link=TEST_LINK_B)])


def the_card(answer, medicine_id):
    [found] = [c for c in answer["approved"] if c["id"] == medicine_id]
    return found


def test_before_the_two_cards_carry_the_japan_line_and_sit_in_the_japan_box(before):
    for medicine_id in (TRELAGLIPTIN, OMARIGLIPTIN, VOGLIBOSE):
        assert the_card(before, medicine_id)["proof_note"] == JAPAN_LINE
        assert the_card(before, medicine_id)["source"] == JAPAN_LIST
        assert medicine_id in before["no_regulator_box"]


def test_each_entrys_card_carries_the_exact_line_and_link(after):
    trelagliptin, omarigliptin = the_card(after, TRELAGLIPTIN), the_card(after, OMARIGLIPTIN)
    assert trelagliptin["proof_note"] == line(2015)
    assert trelagliptin["source"] == TEST_LINK_A
    assert omarigliptin["proof_note"] == line(2015)
    assert omarigliptin["source"] == TEST_LINK_B


def test_each_entrys_card_moves_to_the_main_list(after):
    assert TRELAGLIPTIN not in after["no_regulator_box"]
    assert OMARIGLIPTIN not in after["no_regulator_box"]
    assert TRELAGLIPTIN not in after["wrong_approvals_box"]


def test_a_card_without_an_entry_keeps_the_japan_line_and_box(after):
    voglibose = the_card(after, VOGLIBOSE)
    assert voglibose["proof_note"] == JAPAN_LINE
    assert voglibose["source"] == JAPAN_LIST
    assert VOGLIBOSE in after["no_regulator_box"]


def test_no_other_card_and_nothing_else_on_the_page_changes(before, after):
    """Put back exactly the two cards' line and link, and their box places:
    the rest of the page must then be the same, letter for letter."""
    back = copy.deepcopy(after)
    for medicine_id in (TRELAGLIPTIN, OMARIGLIPTIN):
        moved = the_card(back, medicine_id)
        moved["proof_note"] = JAPAN_LINE
        moved["source"] = JAPAN_LIST
    assert back["no_regulator_box"] != before["no_regulator_box"]
    back["no_regulator_box"] = [medicine_id for medicine_id in before["no_regulator_box"]]
    assert set(before["no_regulator_box"]) - set(after["no_regulator_box"]) == {
        TRELAGLIPTIN, OMARIGLIPTIN}
    assert back == before


def test_a_card_with_a_us_label_is_not_touched_even_with_an_entry(before):
    changed = page([entry(LINAGLIPTIN)])
    assert the_card(changed, LINAGLIPTIN) == the_card(before, LINAGLIPTIN)


def test_the_words_verified_on_full_label_appear_nowhere(after):
    assert "verified on full label" not in json.dumps(after).lower()


# ---- 4. the real file (New Bot's part A) ----

@pytest.mark.pmda_summaries
def test_the_engine_reads_the_real_file_without_complaint():
    assert engine.pmda_summaries()


@pytest.mark.pmda_summaries
def test_every_real_entry_has_an_approval_date_and_a_pmda_link():
    for row in json.loads(REAL_FILE.read_text(encoding="utf-8")):
        datetime.date.fromisoformat(row["summary_date"])
        address = urllib.parse.urlsplit(row["link"])
        assert address.scheme == "https", row
        assert address.hostname == "pmda.go.jp" or address.hostname.endswith(".pmda.go.jp"), row


@pytest.mark.pmda_summaries
def test_no_real_entry_is_for_a_red_card():
    """STOP AND ASK: a medicine that is also red, or in corrections.json."""
    red = {(row["medicine_id"], row["disease_id"])
           for row in json.loads((ROOT / "moonlight" / "corrections.json").read_text("utf-8"))}
    for row in json.loads(REAL_FILE.read_text(encoding="utf-8")):
        assert (row["medicine_id"], row["disease_id"]) not in red, row


@pytest.mark.pmda_summaries
def test_no_real_entry_is_for_a_card_with_its_own_us_or_eu_label():
    """Out of scope: cards with a US or EU label (source_overrides.json,
    confirmed.json, approvals.json)."""
    labelled = set()
    for name in ("source_overrides.json", "confirmed.json", "approvals.json"):
        for row in json.loads((ROOT / "moonlight" / name).read_text("utf-8")):
            labelled.add((row["medicine_id"], row["disease_id"]))
    for row in json.loads(REAL_FILE.read_text(encoding="utf-8")):
        assert (row["medicine_id"], row["disease_id"]) not in labelled, row
        assert (row["medicine_id"], engine.EVERY_PAGE) not in labelled, row


@pytest.mark.pmda_summaries
def test_on_the_saved_t2d_page_each_real_entry_is_a_japan_card_and_gets_its_line():
    rows = [row for row in json.loads(REAL_FILE.read_text(encoding="utf-8"))
            if row["disease_id"] == T2D]
    plain = page([])
    real = t2d_files.page_answer(T2D)
    for row in rows:
        assert the_card(plain, row["medicine_id"])["proof_note"] == JAPAN_LINE, row
        shown = the_card(real, row["medicine_id"])
        assert shown["proof_note"] == line(row["summary_date"][:4]), row
        assert shown["source"] == row["link"], row
        assert row["medicine_id"] not in real["no_regulator_box"], row


# ---- 5. an entry for a card in the narrower or wider box (MAIN 5, 26 Nov) ----
# Main list only. Such a card is left untouched; the app logs the entry and
# skips it, and never refuses to start.

def test_a_boxed_card_with_an_entry_is_logged_and_skipped(caplog):
    boxed = [card("N"), card("M")]
    with with_entries([entry("N")]), caplog.at_level("WARNING", logger="moonlight.engine"):
        skipped = engine.skip_boxed_pmda_summaries(boxed, T2D)
    assert skipped == ["N"]
    assert boxed == [card("N"), card("M")]  # nothing on the cards changes
    assert any("N" in message and T2D in message for message in caplog.messages)


def test_a_boxed_card_without_an_entry_is_not_logged(caplog):
    with with_entries([entry("A")]), caplog.at_level("WARNING", logger="moonlight.engine"):
        assert engine.skip_boxed_pmda_summaries([card("N")], T2D) == []
    assert not caplog.messages


@pytest.mark.parametrize("box", ["narrower", "wider_group"])
def test_on_a_page_a_boxed_card_with_an_entry_keeps_the_japan_line(box, caplog):
    """Cards made here, put through the same api step the page uses
    (api._Found), so the box card and the main-list card are both seen."""
    from moonlight import api
    boxed = card("N")
    tabs = engine.Tabs(approved=[card("A")], being_studied=[], new_clues=[], left_out={},
                       **{box: [boxed]})
    with with_entries([entry("N"), entry("A")]), \
            patch.object(api, "sort_into_tabs", return_value=tabs), \
            patch.object(engine, "_read_corrections", return_value=[]), \
            caplog.at_level("WARNING", logger="moonlight.engine"):
        found = api._Found(engine.Disease(T2D, "type 2 diabetes"), {}, [])
    [kept] = getattr(found, box)
    assert kept.proof_note == JAPAN_LINE
    assert kept.source_record == JAPAN_LIST
    [main] = found.approved
    assert main.proof_note == line(2015)
    assert any("N" in message for message in caplog.messages)
