"""Ticket 2.39. Huntington's cards carry the "only some people" line.

Kashish's answer A to question 3 of the sheet signed on 24 Nov 2026: on the
Huntington disease page (MONDO_0007739) the two cards whose official label
covers chorea only, and not the whole disease, carry her line of 23 Nov:

    The label covers only some people with this disease.

  - Valbenazine (CHEMBL2364639) is added from the hand-written list,
    moonlight/approvals.json. Its entry gains "limited": true (part A).
  - Tetrabenazine (CHEMBL117785) is on the database's own list. A new
    hand-written list, moonlight/limits.json, marks it (part B).

The line only ever comes from engine.LIMITED_LINE. Moonlight never writes
which people a label covers.

Saved files only: the Huntington page saved for tickets 2.13 and 2.32
(fixtures/approval_proof/MONDO_0007739/), read through the same helper as
ticket 2.27's tests. No network.
"""

import json
import pathlib
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from moonlight import api, engine
from moonlight.fetch import Listed, OnList
from moonlight.filter import sort_paths
from moonlight.records import Disease, Medicine, MedicineForm, Path, Target

import test_wrong_approvals_box as box_tests

ROOT = pathlib.Path(__file__).resolve().parent.parent
APPROVALS_FILE = ROOT / "moonlight" / "approvals.json"
LIMITS_FILE = ROOT / "moonlight" / "limits.json"
PAGE = (ROOT / "web" / "index.html").read_text(encoding="utf-8")

# Kashish's words, exactly.
LINE = "The label covers only some people with this disease."
KEY = "limit_note"

HUNTINGTON = "MONDO_0007739"
TETRABENAZINE = "CHEMBL117785"
VALBENAZINE = "CHEMBL2364639"
TETRABENAZINE_LABEL = ("https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm"
                       "?setid=18909efa-de8a-42f1-a641-aa0319d71c35")
VALBENAZINE_LABEL = ("https://www.accessdata.fda.gov/drugsatfda_docs/label/2025/"
                     "209241s029lbl.pdf")

# The one entry of limits.json, exactly as the ticket writes it.
TETRABENAZINE_ENTRY = {"medicine_id": TETRABENAZINE, "disease_id": HUNTINGTON,
                       "date": "2026-11-24", "label": TETRABENAZINE_LABEL}
# The valbenazine entry of approvals.json: as it was on main, and "limited".
VALBENAZINE_BEFORE = {"medicine_id": VALBENAZINE, "name": "Valbenazine",
                      "disease_id": HUNTINGTON, "date": "2026-11-23",
                      "label": VALBENAZINE_LABEL}


def load(file):
    return json.loads(file.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def huntington():
    return box_tests.page_answer(HUNTINGTON, box_tests.huntington_files.saved_post_json)


XENAZINE_LABEL = ("https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm"
                  "?setid=ac768bab-8afa-4446-bc7f-caeeffec0cda")


def back_to_limits_label(cards):
    """Ticket 2.54, signed answer Q3 (item 12): confirmed.json now sends the tetrabenazine
    card's Source record to XENAZINE. Put the old link back, as it was on main before."""
    return [dict(card, source=TETRABENAZINE_LABEL) if card.get("id") == TETRABENAZINE
            else card for card in cards]


def without_line(cards):
    return [{key: value for key, value in card.items() if key != KEY} for card in cards]


# ---- the words ----

def test_the_line_is_kashishs_words_and_unchanged():
    assert engine.LIMITED_LINE == LINE


def test_the_words_are_typed_nowhere_but_the_engine():
    for file in [ROOT / "moonlight" / "api.py", ROOT / "web" / "index.html",
                 LIMITS_FILE, APPROVALS_FILE]:
        assert LINE not in file.read_text(encoding="utf-8"), file.name


# ---- part A: valbenazine ----

def test_part_a_the_valbenazine_entry_gains_limited_and_nothing_else():
    entries = [entry for entry in load(APPROVALS_FILE)
               if entry["medicine_id"] == VALBENAZINE and entry["disease_id"] == HUNTINGTON]
    assert entries == [dict(VALBENAZINE_BEFORE, limited=True)]


# ---- part B: the new list ----

def test_part_b_the_list_holds_exactly_the_one_entry():
    # Ticket 2.50 adds a second entry, for another disease (Roctavian,
    # haemophilia A; tests/test_roctavian_2_50.py). Huntington's is still one.
    assert [e for e in load(LIMITS_FILE) if e["disease_id"] == HUNTINGTON] == [TETRABENAZINE_ENTRY]
    assert [hand for hand in engine.limits_by_hand() if hand.disease_id == HUNTINGTON] == [
        engine.HandLimit(TETRABENAZINE, HUNTINGTON, TETRABENAZINE_LABEL)]


def test_part_b_the_entry_link_is_the_cards_own_source_link(huntington):
    # STOP AND ASK 1: the link must be the card's own source, as saved.
    card = {card["id"]: card for card in huntington["approved"]}[TETRABENAZINE]
    # Ticket 2.54, signed answer Q3 (item 12): the Source record is now XENAZINE's label
    # (confirmed.json), not the limits label below it.
    assert card["source"] == XENAZINE_LABEL != TETRABENAZINE_ENTRY["label"]


def read_limits(entries, approvals=None):
    guards = [patch.object(engine, "_read_limits", return_value=entries)]
    if approvals is not None:
        guards.append(patch.object(engine, "_read_approvals", return_value=approvals))
    for guard in guards:
        guard.start()
    try:
        return engine.limits_by_hand()
    finally:
        for guard in guards:
            guard.stop()


def test_guard_a_good_list_is_read():
    assert read_limits([TETRABENAZINE_ENTRY]) == [
        engine.HandLimit(TETRABENAZINE, HUNTINGTON, TETRABENAZINE_LABEL)]
    assert read_limits([]) == []


@pytest.mark.parametrize("more", [{"name": "Tetrabenazine"}, {"limited": True},
                                  {"people": "adults with chorea"}, {"note": "x"}],
                         ids=lambda more: "+".join(more))
def test_guard_an_unknown_key_is_refused(more):
    with pytest.raises(ValueError):
        read_limits([dict(TETRABENAZINE_ENTRY, **more)])


@pytest.mark.parametrize("missing", ["medicine_id", "disease_id", "date", "label"])
def test_guard_a_missing_key_is_refused(missing):
    entry = {key: value for key, value in TETRABENAZINE_ENTRY.items() if key != missing}
    with pytest.raises(ValueError):
        read_limits([entry])


@pytest.mark.parametrize("date", ["2026-11-31", "24 Nov 2026", "", "2026/11/24", None])
def test_guard_a_bad_date_is_refused(date):
    with pytest.raises(ValueError):
        read_limits([dict(TETRABENAZINE_ENTRY, date=date)])


@pytest.mark.parametrize("label", ["", "http://example.org/label", None, "dailymed"])
def test_guard_a_label_that_is_not_an_https_link_is_refused(label):
    with pytest.raises(ValueError):
        read_limits([dict(TETRABENAZINE_ENTRY, label=label)])


def test_guard_two_entries_for_the_same_pair_are_refused_even_when_alike():
    with pytest.raises(ValueError):
        read_limits([TETRABENAZINE_ENTRY, dict(TETRABENAZINE_ENTRY)])
    with pytest.raises(ValueError):
        read_limits([TETRABENAZINE_ENTRY, dict(TETRABENAZINE_ENTRY, date="2026-11-25")])


def test_guard_a_list_that_is_not_a_list_is_refused():
    with pytest.raises(ValueError):
        read_limits({"medicine_id": TETRABENAZINE})


def test_guard_a_pair_also_in_approvals_is_refused():
    # One place per card: valbenazine is marked in approvals.json.
    clash = dict(TETRABENAZINE_ENTRY, medicine_id=VALBENAZINE, label=VALBENAZINE_LABEL)
    with pytest.raises(ValueError, match="approvals.json"):
        read_limits([clash])
    # The same pair for another disease is not a clash.
    assert read_limits([dict(clash, disease_id="MONDO_0000001")])


def test_guard_a_bad_list_stops_the_app_from_starting():
    with patch.object(engine, "_read_limits", return_value=[{"medicine_id": TETRABENAZINE}]):
        with pytest.raises(ValueError):
            with TestClient(api.app):
                pass
    with TestClient(api.app):  # the real files start the app
        pass


# ---- the engine, with hand-built cards ----

DISEASE = Disease("TEST_0000001", "test disease")
PROTEIN = Target("ENSG00000000001", "ABC1", "test protein", 0.8)
PARENT_ID, SALT_ID = "CHEMBL9001", "CHEMBL9002"


def approved_path(name, forms):
    made = tuple(MedicineForm(form_id, form_name, best_stage="APPROVAL",
                              disease_stage="APPROVAL", withdrawn=False,
                              parent_id=PARENT_ID if form_id != PARENT_ID else None)
                 for form_id, form_name in forms)
    return Path(Medicine(name, made), PROTEIN, DISEASE, ("INHIBITOR",), PROTEIN.score,
                ("https://example.org/a",))


def limit(medicine_id, disease_id=DISEASE.id):
    return {"medicine_id": medicine_id, "disease_id": disease_id, "date": "2026-11-24",
            "label": "https://example.org/label"}


def notes_for(tabs, entries, listed=(), on_list=()):
    with patch.object(engine, "_read_limits", return_value=entries):
        return engine.limit_notes(tabs, DISEASE.id, listed, on_list)


def path_tabs():
    path = approved_path("ALPHAMIL", [(PARENT_ID, "ALPHAMIL"), (SALT_ID, "ALPHAMIL SALT")])
    return engine.sort_into_tabs(sort_paths([path]), [])


def test_engine_the_card_id_matches():
    assert notes_for(path_tabs(), [limit(PARENT_ID)]) == {PARENT_ID: LINE}


def test_engine_a_form_on_a_path_matches():
    assert notes_for(path_tabs(), [limit(SALT_ID)]) == {PARENT_ID: LINE}


def test_engine_a_form_on_the_diseases_own_list_matches():
    listed = Listed(PARENT_ID, "ALPHAMIL", ((PARENT_ID, "ALPHAMIL"), (SALT_ID, "ALPHAMIL SALT")),
                    ("https://example.org/a",))
    tabs = engine.sort_into_tabs({}, [listed])
    assert [medicine.id for medicine in tabs.approved] == [PARENT_ID]
    assert notes_for(tabs, [limit(SALT_ID)], [listed]) == {PARENT_ID: LINE}


def test_engine_a_form_named_only_in_on_list_matches():
    listed = Listed(PARENT_ID, "ALPHAMIL", ((PARENT_ID, "ALPHAMIL"),), ("https://example.org/a",))
    salt = MedicineForm(SALT_ID, "ALPHAMIL SALT", best_stage="APPROVAL",
                        disease_stage="APPROVAL", withdrawn=False, parent_id=PARENT_ID)
    on_list = OnList(Medicine("ALPHAMIL", (salt,)), (("https://example.org/a", "APPROVAL"),))
    tabs = engine.sort_into_tabs({}, [listed])
    assert notes_for(tabs, [limit(SALT_ID)], [listed], [on_list]) == {PARENT_ID: LINE}


def test_engine_an_entry_for_another_disease_does_nothing():
    assert notes_for(path_tabs(), [limit(PARENT_ID, "TEST_0000002")]) == {}


def test_engine_no_entry_means_no_line():
    assert notes_for(path_tabs(), []) == {}


def test_engine_boxes_and_other_tabs_are_never_named():
    tabs = path_tabs()
    card = tabs.approved[0]
    moved = engine.Tabs(approved=[], being_studied=[], new_clues=[], left_out={},
                        wider_group=[card], narrower=[card])
    assert notes_for(moved, [limit(PARENT_ID)]) == {}


def test_engine_a_database_card_still_has_no_limit_note_of_its_own():
    # The line comes from limit_notes, beside the card, as the withdrawal
    # line does. The card's own property is as ticket 2.33 left it.
    assert path_tabs().approved[0].limit_note is None


# ---- the Huntington page ----

def test_example_both_cards_carry_the_line(huntington):
    cards = {card["id"]: card for card in huntington["approved"]}
    assert cards[TETRABENAZINE][KEY] == LINE
    assert cards[VALBENAZINE][KEY] == LINE


def test_example_no_other_card_on_the_page_carries_the_line(huntington):
    for part, cards in huntington.items():
        if isinstance(cards, list):
            for card in cards:
                if isinstance(card, dict) and card.get("id") not in (TETRABENAZINE, VALBENAZINE):
                    assert KEY not in card, (part, card.get("medicine"))


def test_example_the_two_cards_change_only_by_the_line(huntington):
    # Without the new key, the Approved list is letter for letter what main
    # sent before this ticket: same cards, same places, same sources and lines.
    assert box_tests.fingerprint(without_line(back_to_limits_label(huntington["approved"]))) == \
        box_tests.MAIN_SENT[HUNTINGTON]["approved"]
    cards = {card["id"]: card for card in huntington["approved"]}
    assert cards[TETRABENAZINE]["source"] == XENAZINE_LABEL  # Ticket 2.54, signed answer Q3
    assert "proof_note" not in cards[TETRABENAZINE]
    assert cards[VALBENAZINE]["source"] == VALBENAZINE_LABEL
    assert cards[VALBENAZINE]["proof_note"] == box_tests.VALBENAZINE_LINE


def test_example_the_four_red_warning_cards_are_untouched(huntington):
    boxed = huntington["wrong_approvals_box"]
    assert [medicine_id for medicine_id, _ in box_tests.HUNTINGTON_BOX_4] == boxed
    for card in huntington["approved"]:
        if card["id"] in boxed:
            assert KEY not in card and "warning" in card


def test_example_every_other_part_is_what_main_sent(huntington):
    for part, print_ in box_tests.MAIN_SENT[HUNTINGTON].items():
        if part != "approved":
            assert box_tests.fingerprint(huntington[part]) == print_, part


def test_example_needs_no_more_requests():
    asked = []

    def counting(body):
        asked.append(body)
        return box_tests.huntington_files.saved_post_json(body)

    with patch.object(engine, "_read_limits", return_value=[]):
        box_tests.page_answer(HUNTINGTON, counting)
    without = len(asked)
    del asked[:]
    box_tests.page_answer(HUNTINGTON, counting)
    assert len(asked) == without


# ---- the page ----

def test_the_page_draws_limit_note_on_any_approved_card():
    # STOP AND ASK 3: the page needs no change. approvedCard draws the key
    # for whichever card carries it, hand-added or not.
    start = PAGE.index("function approvedCard(")
    body = PAGE[start:PAGE.index("\n  }\n", start)]
    assert 'if (medicine.limit_note) {' in body
    assert 'slot(el, "limit-note").textContent = medicine.limit_note;' in body
    assert "added_from_label" not in body
