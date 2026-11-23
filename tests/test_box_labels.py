"""Ticket 2.16, part 1. Clearer labels in the two folded boxes.

Kashish's decisions, 18 Nov. Two readers took a card in a folded box as
approved for their own disease. So both labels now start with the
important part:

  narrower box: Not listed as approved for this exact disease. Approved for
                <names>, which the database lists under this disease.
  wider box:    Not listed as approved for this exact disease. Approved for
                <names>, a wider group the database puts this disease in.
                ("wider groups" when there are two or more names.)

Only the first sentence is new. No card moves, and the safety line and the
Approved tab's top line stay as they are.

Saved files only: fixtures/narrower_box/ and fixtures/family/. No network.
tests/cards_before_2.16.json holds where every card sat before this ticket,
written by the code as it was on main (825bbd3).
"""

import json
import pathlib
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from moonlight import api, explain, fetch
from moonlight.engine import sort_into_tabs
from moonlight.filter import sort_paths

import test_family
import test_narrower_box
from test_family import AMYLOIDOSIS, ECZEMA, PRE_B_ALL, child, parent
from test_narrower_box import ALL, listed, names, saved_post_json, whole_search

ROOT = pathlib.Path(__file__).resolve().parent.parent
PAGE = (ROOT / "web" / "index.html").read_text(encoding="utf-8")
BEFORE = json.loads(
    (ROOT / "tests" / "cards_before_2.16.json").read_text(encoding="utf-8"))

# Kashish's words, exactly.
FIRST = "Not listed as approved for this exact disease. "
WIDER_ALL = (
    "Not listed as approved for this exact disease. Approved for acute "
    "lymphoblastic leukemia, a wider group the database puts this disease in."
)
NARROWER_CLL = (
    "Not listed as approved for this exact disease. Approved for B-cell "
    "chronic lymphocytic leukemia, which the database lists under this disease."
)
NARROWER_TWO_NAMES = (
    "Not listed as approved for this exact disease. Approved for T-cell acute "
    "lymphoblastic leukemia and precursor T-cell acute lymphoblastic leukemia, "
    "which the database lists under this disease."
)
SAFETY_LINE = (
    "For learning and research exploration, not medical advice. Never start, "
    "stop or change any medicine without a doctor."
)
APPROVED_TOP_LINE = (
    "Already approved for this disease in at least one country, according to "
    "the database. Nothing here says how well any of them works. Listed A to Z."
)


@pytest.fixture(autouse=True)
def offline():
    """Saved files instead of Open Targets. Real HTTP is an error."""
    explain.forget_everything()
    api.forget_visitors()
    with patch("moonlight.fetch._post_json", side_effect=saved_post_json), \
            patch("requests.request", side_effect=AssertionError("network used")), \
            patch("requests.post", side_effect=AssertionError("network used")), \
            patch("requests.get", side_effect=AssertionError("network used")), \
            patch("requests.sessions.Session.request",
                  side_effect=AssertionError("network used")):
        yield
    explain.forget_everything()


def family_tabs(disease):
    """The tabs of a disease saved by ticket 2.12 (fixtures/family/)."""
    with patch("moonlight.fetch._post_json", side_effect=test_family.family_post_json):
        return test_family.tabs_for(disease, True)


def narrower_box_tabs(disease_id):
    """The tabs of a disease saved by ticket 2.14 (fixtures/narrower_box/)."""
    return whole_search(fetch.fetch_disease(disease_id))


def tabs_of(disease_id):
    for disease in (AMYLOIDOSIS, PRE_B_ALL, ECZEMA):
        if disease.id == disease_id:
            return family_tabs(disease)
    return narrower_box_tabs(disease_id)


@pytest.fixture
def all_json():
    """What the API sends the page for acute lymphoblastic leukemia."""
    answer = TestClient(api.app).get("/api/clues", params={"disease_id": ALL.id})
    assert answer.status_code == 200
    return answer.json()


# ---- EXAMPLE 1: a card in the wider-group box ----

def test_example_1_a_wider_group_card_carries_the_new_label_exactly():
    tabs = family_tabs(PRE_B_ALL)
    assert len(tabs.wider_group) == 15
    assert {medicine.label for medicine in tabs.wider_group} == {WIDER_ALL}


def test_example_1_the_api_sends_the_new_wider_group_label(all_json):
    assert len(all_json["wider_group"]) == 12
    for item in all_json["wider_group"]:
        assert item["label"].startswith(FIRST + "Approved for ")
        assert item["label"].endswith(" the database puts this disease in.")
        assert item["label"].count(FIRST) == 1


def test_example_1_with_two_wider_groups_only_the_first_sentence_is_new():
    tabs = sort_into_tabs(sort_paths([]), [], (), [
        parent(test_family.WIDE, approved=[listed("TWOMIL")]),
        parent(test_family.WIDER, approved=[listed("TWOMIL")])])
    assert tabs.wider_group[0].label == (
        "Not listed as approved for this exact disease. Approved for wide "
        "disease and another wide disease, wider groups the database puts "
        "this disease in.")


# ---- EXAMPLE 2: a card in the narrower-disease box ----

def test_example_2_a_narrower_card_carries_the_new_label_exactly():
    tabs = narrower_box_tabs(ALL.id)
    assert test_family.named(tabs.narrower, "IBRUTINIB").label == NARROWER_CLL


def test_example_2_two_names_are_joined_with_and_as_today():
    tabs = narrower_box_tabs(ALL.id)
    assert test_family.named(tabs.narrower, "NELARABINE").label == NARROWER_TWO_NAMES


def test_example_2_every_narrower_card_has_the_new_first_sentence_once(all_json):
    assert len(all_json["narrower"]) == 13
    for item in all_json["narrower"]:
        assert item["label"].startswith(FIRST + "Approved for ")
        assert item["label"].endswith(", which the database lists under this disease.")
        assert item["label"].count(FIRST) == 1
    labels = {item["medicine"].upper(): item["label"] for item in all_json["narrower"]}
    assert labels["IBRUTINIB"] == NARROWER_CLL
    assert labels["NELARABINE"] == NARROWER_TWO_NAMES


def test_example_2_three_names_keep_the_comma_and_one_and():
    tabs = sort_into_tabs(sort_paths([]), [], (), [
        child(d, approved=[listed("MANYMIL")])
        for d in (test_family.NARROW, test_family.SLIM, test_family.THIN)])
    assert tabs.narrower[0].label == (
        "Not listed as approved for this exact disease. Approved for narrow "
        "disease, slim disease and thin disease, which the database lists "
        "under this disease.")


# ---- EXAMPLE 3: a card in the main Approved list ----

def test_example_3_a_main_list_card_has_no_label(all_json):
    tabs = narrower_box_tabs(ALL.id)
    assert len(tabs.approved) == 15
    assert all(medicine.label is None for medicine in tabs.approved)
    assert len(all_json["approved"]) == 15
    assert all("label" not in item for item in all_json["approved"])


def test_example_3_the_new_first_sentence_is_only_ever_on_a_boxed_card():
    for disease_id in BEFORE:
        tabs = tabs_of(disease_id)
        assert all(medicine.label is None for medicine in tabs.approved)
        for medicine in tabs.narrower + tabs.wider_group:
            assert medicine.label.startswith(FIRST)


# ---- EXAMPLE 5: no card moved ----

@pytest.mark.parametrize("disease_id", sorted(BEFORE))
def test_example_5_no_card_moved(disease_id):
    before, tabs = BEFORE[disease_id], tabs_of(disease_id)
    assert names(tabs.approved) == before["approved"]
    assert names(tabs.narrower) == before["narrower"]
    assert names(tabs.wider_group) == before["wider_group"]
    # In trials and New clues, in their ranked order, too.
    assert [clue.medicine.name for clue in tabs.being_studied] == before["being_studied"]
    assert [clue.medicine.name for clue in tabs.new_clues] == before["new_clues"]


def test_example_5_the_before_picture_holds_all_seven_saved_diseases():
    assert len(BEFORE) == 7
    assert sum(len(saved["narrower"]) for saved in BEFORE.values()) == 25
    assert sum(len(saved["wider_group"]) for saved in BEFORE.values()) == 101


# ---- EXAMPLE 6: the safety line and the Approved tab's top line ----

def test_example_6_the_safety_line_is_unchanged():
    assert PAGE.count(SAFETY_LINE) == 1
    assert 'data-slot="safety-line"' in PAGE[: PAGE.index(SAFETY_LINE)]


def test_example_6_the_approved_tabs_top_line_is_unchanged():
    assert PAGE.count(f'<p class="tab-words">{APPROVED_TOP_LINE}</p>') == 1
    panel = PAGE[PAGE.index('id="panel-approved"'):PAGE.index('id="panel-trials"')]
    assert panel.count(APPROVED_TOP_LINE) == 1
    assert panel.count("Talk to your doctor before changing any medicine.") == 3


def test_the_box_titles_and_their_order_are_unchanged():
    panel = PAGE[PAGE.index('id="panel-approved"'):PAGE.index('id="panel-trials"')]
    assert panel.index("Approved for a narrower disease (") < panel.index(
        "Approved for a wider group (")


# ---- PART 2, EXAMPLE 4: the In trials tab's line ----
# Kashish's words, 18 Nov. She chose a sentence with no number: Moonlight
# asks for 25 proteins, but some diseases have fewer.

TRIALS_LINE = (
    "Approved for another disease and now being tested for this one. A "
    "separate research category, not a prediction of effectiveness. Not "
    "every trial is listed."
)


def test_example_4_the_page_holds_the_new_in_trials_line_exactly_once():
    assert PAGE.count(TRIALS_LINE) == 1
    assert PAGE.count(f'<p class="section-desc">{TRIALS_LINE}</p>') == 1


def test_example_4_the_line_is_under_the_real_in_trials_tab():
    panel = PAGE[PAGE.index('id="panel-trials"'):PAGE.index('id="panel-clues"')]
    assert panel.count(TRIALS_LINE) == 1
    assert panel.index("Already being studied for this disease") < panel.index(TRIALS_LINE)
    assert panel.index(TRIALS_LINE) < panel.index('id="studied-cards"')


def test_example_4_the_old_words_are_all_still_there_and_said_once():
    for words in ("now being tested for this one.", "not a prediction of effectiveness.",
                  "Not every trial is listed."):
        assert PAGE.count(words) == 1
