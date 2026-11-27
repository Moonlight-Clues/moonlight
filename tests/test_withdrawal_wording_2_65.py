"""Ticket 2.65. Withdrawal wording (sheet W4, W5, folded boxes).

Decisions (Kashish's sheet of 26 Nov, answers given in the ticket session):

  1. W4, a region line from withdrawals.json ("Its approval was withdrawn in
     the US. ..."), is a fact about the medicine, not the page. Any card of
     the Approved tab, on the main list or in a folded box (narrower,
     wider group), on any page, carries it: "the same medicine should say
     the same thing wherever it shows". The database's own line still wins
     on a card that has one, as before (ticket 2.51). An entry with no
     region is as it was: its own disease's main list only.
  2. W5, a hand list moonlight/discontinued.json {medicine_id, date,
     source}. Every Approved-tab card of such a medicine, on every page,
     shows DISCONTINUED_LINE in place of any other withdrawal line, even
     where the database had none. Clue and In trials cards stay as they are.
     The file ships empty: no entry goes in before a person has read its
     source. The tests below use test entries.
  3. A medicine on discontinued.json and on withdrawals.json at once: the
     app refuses to start.

Saved answers only (old_flag_saved.py: nine diseases, Open Targets 26.09).
No network. fixtures/withdrawal_wording_2_65/withdrawal_lines_before_2.65.json
is every Approved-tab card's withdrawal line on those nine pages, made by
main a8eb384 before this ticket.
"""

import json
import pathlib
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from moonlight import api, engine

import old_flag_saved as saved

ROOT = pathlib.Path(__file__).resolve().parent.parent
DISCONTINUED_FILE = ROOT / "moonlight" / "discontinued.json"
WITHDRAWALS_FILE = ROOT / "moonlight" / "withdrawals.json"
BEFORE = ROOT / "fixtures" / "withdrawal_wording_2_65" / "withdrawal_lines_before_2.65.json"

# Kashish's signed words (26 Nov sheet), exactly.
W5 = "The maker stopped selling it. Its approval was never withdrawn."
DATABASE_LINE = "The database records a withdrawal for this medicine in some country or region."
US_LINE = "Its approval was withdrawn in the US. It may still be sold elsewhere."
EU_LINE = "Its approval was withdrawn in the EU. It may still be sold elsewhere."

DEPRESSION, ASTHMA, T2D = "MONDO_0002050", "MONDO_0004979", "MONDO_0005148"
RA, CUSHING, HYPERTENSION = "MONDO_0008383", "MONDO_0018912", "MONDO_0005044"
PAGES = ["MONDO_0002050", "MONDO_0004979", "MONDO_0005027", "MONDO_0005148",
         "MONDO_0005180", "MONDO_0008383", "MONDO_0011996", "MONDO_0018874",
         "MONDO_0018912"]
APPROVED_PARTS = ("approved", "narrower", "wider_group")

# Cards on the saved pages (ids from the saved answers).
TOLAZAMIDE = "CHEMBL817"  # T2D main list, US line from withdrawals.json
METFORMIN = "CHEMBL1431"  # T2D main list, the database's line
ACARBOSE = "CHEMBL404271"  # T2D main list, no line
AMLODIPINE = "CHEMBL1491"  # T2D wider-group box, no line
INSULIN_ASPART = "CHEMBL1201496"  # T2D wider-group box, the database's line
DEPRESSION_NARROW = "CHEMBL107360"  # depressive disorder narrower box, no line
DEPRESSION_NARROW_DB = "CHEMBL10878"  # depressive disorder narrower box, database's line
EVERYWHERE = "CHEMBL635"  # asthma main, RA main, Cushing wider-group box; no line on any

SOURCE = "https://example.org/test-source"


def real_withdrawals():
    return json.loads(WITHDRAWALS_FILE.read_text(encoding="utf-8"))


def discontinued(*medicine_ids):
    return [{"medicine_id": m, "date": "2026-11-26", "source": SOURCE} for m in medicine_ids]


def region(medicine_id, disease_id, where="US"):
    return {"medicine_id": medicine_id, "disease_id": disease_id, "region": where,
            "date": "2026-11-26", "source": SOURCE}


def page(disease_id, withdrawals=None, stopped=None):
    """The saved page, with the real lists unless a test hands in its own."""
    patches = []
    if withdrawals is not None:
        patches.append(patch.object(engine, "_read_withdrawals", return_value=withdrawals))
    if stopped is not None:
        patches.append(patch.object(engine, "_read_discontinued", return_value=stopped))
    for p in patches:
        p.start()
    try:
        api.forget_answers()
        return saved.page_answer(disease_id)
    finally:
        for p in patches:
            p.stop()
        api.forget_answers()


def card(answer, part, medicine_id):
    (found,) = [c for c in answer.get(part, []) if c["id"] == medicine_id]
    return found


def not_approved_parts(answer):
    return {k: v for k, v in answer.items() if k not in APPROVED_PARTS}


def changed_cards(after, before):
    out = []
    for part in APPROVED_PARTS:
        a, b = after.get(part, []), before.get(part, [])
        assert [c["id"] for c in a] == [c["id"] for c in b], part  # nothing moves
        out += [(part, x["id"]) for x, y in zip(a, b) if x != y]
    return out


# ---- the hand list itself ----

def test_the_real_discontinued_list_ships_empty():
    assert json.loads(DISCONTINUED_FILE.read_text(encoding="utf-8")) == []
    assert engine.discontinued_by_hand() == []


def test_the_engine_reads_a_test_entry():
    with patch.object(engine, "_read_discontinued", return_value=discontinued(ACARBOSE)):
        (entry,) = engine.discontinued_by_hand()
    assert entry.medicine_id == ACARBOSE and entry.source == SOURCE


GOOD = {"medicine_id": ACARBOSE, "date": "2026-11-26", "source": SOURCE}


@pytest.mark.parametrize("bad", [
    {k: v for k, v in GOOD.items() if k != "source"},  # no source
    {**GOOD, "source": "http://example.org/x"},  # not https
    {**GOOD, "source": ""},
    {**GOOD, "date": "26 Nov"},  # not a real date
    {**GOOD, "medicine_id": ""},
    {**GOOD, "disease_id": T2D},  # no disease: it is about the medicine
    {**GOOD, "note": "anything"},
    "CHEMBL404271",
])
def test_an_entry_not_written_the_right_way_is_refused(bad):
    with patch.object(engine, "_read_discontinued", return_value=[bad]):
        with pytest.raises(ValueError):
            engine.discontinued_by_hand()


def test_the_same_medicine_written_twice_is_refused():
    with patch.object(engine, "_read_discontinued", return_value=[GOOD, dict(GOOD)]):
        with pytest.raises(ValueError):
            engine.discontinued_by_hand()


def test_a_list_that_is_not_a_list_is_refused():
    with patch.object(engine, "_read_discontinued", return_value={"a": GOOD}):
        with pytest.raises(ValueError):
            engine.discontinued_by_hand()


# ---- 3. on both lists: the app refuses to start ----

def test_a_medicine_on_both_lists_is_refused():
    assert TOLAZAMIDE in {e["medicine_id"] for e in real_withdrawals()}
    with patch.object(engine, "_read_discontinued", return_value=discontinued(TOLAZAMIDE)):
        with pytest.raises(ValueError, match="withdrawals.json"):
            engine.discontinued_by_hand()


def test_the_app_refuses_to_start_if_a_medicine_is_on_both_lists():
    with patch.object(engine, "_read_discontinued", return_value=discontinued(TOLAZAMIDE)):
        with pytest.raises(ValueError, match="withdrawals.json"):
            with TestClient(api.app):
                pass


def test_the_clash_is_found_whichever_way_it_is_written():
    # An entry without a region counts too: any withdrawal clashes.
    plain = {"medicine_id": ACARBOSE, "disease_id": RA, "date": "2026-11-26", "source": SOURCE}
    with patch.object(engine, "_read_withdrawals", return_value=[plain]), \
            patch.object(engine, "_read_discontinued", return_value=discontinued(ACARBOSE)):
        with pytest.raises(ValueError, match="withdrawals.json"):
            with TestClient(api.app):
                pass


def test_the_app_starts_with_the_real_lists():
    with TestClient(api.app) as client:
        assert client.get("/api/version").status_code == 200


# ---- 2. W5 on every Approved-tab card, every page ----

@pytest.fixture(scope="module")
def t2d_plain():
    return page(T2D)


@pytest.fixture(scope="module")
def t2d_w5():
    return page(T2D, stopped=discontinued(METFORMIN, ACARBOSE, INSULIN_ASPART))


def test_w5_replaces_the_database_line_on_the_main_list(t2d_w5, t2d_plain):
    assert card(t2d_plain, "approved", METFORMIN)["withdrawal_note"] == DATABASE_LINE
    shown = card(t2d_w5, "approved", METFORMIN)
    assert shown["withdrawal_note"] == W5
    assert DATABASE_LINE not in json.dumps(shown)


def test_w5_shows_even_where_the_database_had_no_line(t2d_w5, t2d_plain):
    assert "withdrawal_note" not in card(t2d_plain, "approved", ACARBOSE)
    assert card(t2d_w5, "approved", ACARBOSE)["withdrawal_note"] == W5


def test_w5_shows_in_the_wider_group_box(t2d_w5, t2d_plain):
    assert card(t2d_plain, "wider_group", INSULIN_ASPART)["withdrawal_note"] == DATABASE_LINE
    assert card(t2d_w5, "wider_group", INSULIN_ASPART)["withdrawal_note"] == W5


def test_w5_shows_in_the_narrower_box():
    plain = page(DEPRESSION)
    after = page(DEPRESSION, stopped=discontinued(DEPRESSION_NARROW, DEPRESSION_NARROW_DB))
    assert "withdrawal_note" not in card(plain, "narrower", DEPRESSION_NARROW)
    assert card(after, "narrower", DEPRESSION_NARROW)["withdrawal_note"] == W5
    assert card(after, "narrower", DEPRESSION_NARROW_DB)["withdrawal_note"] == W5
    assert sorted(changed_cards(after, plain)) == sorted([("narrower", DEPRESSION_NARROW),
                                                          ("narrower", DEPRESSION_NARROW_DB)])


@pytest.mark.parametrize("disease_id, part", [(ASTHMA, "approved"), (RA, "approved"),
                                              (CUSHING, "wider_group")])
def test_w5_says_the_same_on_every_page(disease_id, part):
    after = page(disease_id, stopped=discontinued(EVERYWHERE))
    assert card(after, part, EVERYWHERE)["withdrawal_note"] == W5


def test_w5_changes_only_the_named_cards_and_only_their_line(t2d_w5, t2d_plain):
    changed = changed_cards(t2d_w5, t2d_plain)
    assert sorted(changed) == sorted([("approved", METFORMIN), ("approved", ACARBOSE),
                                      ("wider_group", INSULIN_ASPART)])
    for part, medicine_id in changed:
        a, b = card(t2d_w5, part, medicine_id), card(t2d_plain, part, medicine_id)
        assert {k: v for k, v in a.items() if k != "withdrawal_note"} == \
            {k: v for k, v in b.items() if k != "withdrawal_note"}
    assert not_approved_parts(t2d_w5) == not_approved_parts(t2d_plain)  # clues, trials, boxes
    assert json.dumps(t2d_w5).count(W5) == 3


def test_w5_is_never_on_a_clue_or_in_trials_card(t2d_w5):
    for part in ("being_studied", "new_clues", "more_in_trials", "new_in_trials"):
        assert W5 not in json.dumps(t2d_w5.get(part, []))


# ---- 1. W4 wherever the medicine shows on the Approved tab ----

def test_w4_shows_in_the_wider_group_box_on_another_page():
    entries = real_withdrawals() + [region(AMLODIPINE, HYPERTENSION, "EU")]
    plain = page(T2D)
    after = page(T2D, withdrawals=entries)
    assert "withdrawal_note" not in card(plain, "wider_group", AMLODIPINE)
    assert card(after, "wider_group", AMLODIPINE)["withdrawal_note"] == EU_LINE
    assert changed_cards(after, plain) == [("wider_group", AMLODIPINE)]
    assert not_approved_parts(after) == not_approved_parts(plain)


def test_w4_shows_in_the_narrower_box_on_another_page():
    entries = real_withdrawals() + [region(DEPRESSION_NARROW, T2D)]
    plain = page(DEPRESSION)
    after = page(DEPRESSION, withdrawals=entries)
    assert card(after, "narrower", DEPRESSION_NARROW)["withdrawal_note"] == US_LINE
    assert changed_cards(after, plain) == [("narrower", DEPRESSION_NARROW)]


def test_w4_shows_on_the_main_list_of_another_page():
    entries = real_withdrawals() + [region(ACARBOSE, HYPERTENSION)]
    after = page(T2D, withdrawals=entries)
    assert card(after, "approved", ACARBOSE)["withdrawal_note"] == US_LINE


@pytest.mark.parametrize("disease_id, part", [(ASTHMA, "approved"), (RA, "approved"),
                                              (CUSHING, "wider_group")])
def test_w4_says_the_same_on_every_page(disease_id, part):
    entries = real_withdrawals() + [region(EVERYWHERE, HYPERTENSION)]
    after = page(disease_id, withdrawals=entries)
    assert card(after, part, EVERYWHERE)["withdrawal_note"] == US_LINE


def test_the_database_line_still_wins_over_w4_in_a_box():
    entries = real_withdrawals() + [region(INSULIN_ASPART, HYPERTENSION)]
    after = page(T2D, withdrawals=entries)
    assert card(after, "wider_group", INSULIN_ASPART)["withdrawal_note"] == DATABASE_LINE


def test_an_entry_without_a_region_still_names_its_own_main_list_only():
    plain_entry = {"medicine_id": AMLODIPINE, "disease_id": T2D, "date": "2026-11-26",
                   "source": SOURCE}
    after = page(T2D, withdrawals=real_withdrawals() + [plain_entry])
    assert "withdrawal_note" not in card(after, "wider_group", AMLODIPINE)


def test_w5_wins_over_w4():
    entries = [e for e in real_withdrawals()] + [region(ACARBOSE, HYPERTENSION)]
    # Not a clash at start-up only because this test hands the engine both lists
    # without asking it to check them: the page itself must still show W5.
    with patch.object(engine, "_check_no_clash", return_value=None):
        after = page(T2D, withdrawals=entries, stopped=discontinued(ACARBOSE))
    assert card(after, "approved", ACARBOSE)["withdrawal_note"] == W5


# ---- with the real lists, no card's withdrawal line changes ----

@pytest.mark.parametrize("disease_id", PAGES)
def test_every_card_keeps_its_withdrawal_line_with_the_real_lists(disease_id):
    before = json.loads(BEFORE.read_text(encoding="utf-8"))[disease_id]
    after = page(disease_id)
    now = {part: {c["id"]: c.get("withdrawal_note") for c in after.get(part, [])}
           for part in APPROVED_PARTS}
    assert now == before


def test_the_real_w4_cards_are_as_before(t2d_plain):
    assert card(t2d_plain, "approved", TOLAZAMIDE)["withdrawal_note"] == US_LINE
    assert json.dumps(t2d_plain).count(US_LINE) == 2
