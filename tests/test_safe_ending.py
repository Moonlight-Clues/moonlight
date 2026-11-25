"""Ticket 3.6. A safer ending on clue cards.

A tester found that a person already taking a medicine their doctor
prescribed could read "It is not a treatment. Do not try it." on its card
and stop taking it. Kashish approved new safety wording on 18 Nov 2026.

The two sentences "It is not a treatment. Do not try it." become the one
sentence "Never start, stop or change any medicine without a doctor."
That sentence is the second half of the page's own safety line, word for
word. Nothing else in the ending changes.

Kashish corrected the sentence on 18 Nov, the same day. The ticket first
said "Do not try it unless your doctor has asked you to take it." These
tests were first written with that sentence and then changed to hers.
Example 4 now also checks that the earlier sentence is nowhere.

One test or more for each of the ticket's six EXAMPLES. Nothing here
touches the network: Open Targets is read from the saved files in
fixtures/ and Gemini is swapped for a fake.
"""

import json
import re
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from moonlight import api, explain

from test_api import (  # noqa: F401  (the two fixtures are used by pytest)
    FIVE, GOOD_ANSWER, GUCY1, PAH_ID, SAFETY_LINE,
    clue_named, clues_json, gemini_says, gemini_unreachable, guide_of,
    offline, plain, pretend_data_version_and_throwaway_folder,
    with_saved_targets, with_targets,
)

# The new ending, word for word from the ticket. One paragraph.
NEW_ENDING = (
    "But there is a catch. Nobody knows from our information if the disease "
    "needs this protein turned up or down. So this is a clue to read about. "
    "Never start, stop or change any medicine without a doctor."
)
NEW_ENDING_MANY = (
    "But there is a catch. Nobody knows from our information if the disease "
    "needs these proteins turned up or down. So this is a clue to read about. "
    "Never start, stop or change any medicine without a doctor."
)
NEW_LAST_SENTENCE = "Never start, stop or change any medicine without a doctor."
# Example 4, as Kashish corrected it: none of these in any card ending.
GONE = ("It is not a treatment", "Do not try it", "unless your doctor has asked you")


@pytest.fixture
def client():
    return TestClient(api.app)


@pytest.fixture
def page(client):
    return client.get("/").text


def explained(client, group, name, gemini, *symbols):
    """The card for one medicine, and its explanation from /api/explain."""
    card = clue_named(clues_json(client, *symbols)[group], name)
    with with_targets(*symbols), \
            patch("moonlight.explain._gemini_request", side_effect=gemini):
        answer = client.get(
            "/api/explain", params={"disease_id": PAH_ID, "clue_id": card["id"]}
        )
    assert answer.status_code == 200
    return card, answer.json()


def every_clue_card(client):
    """Every New clues and In trials card for all the saved proteins."""
    with with_saved_targets():
        response = client.get("/api/clues", params={"disease_id": PAH_ID})
    assert response.status_code == 200
    data = response.json()
    assert data["new_clues"] and data["being_studied"]
    return data


# ---- EXAMPLE 1: a New clues card's ending is exactly the new paragraph ----

def test_1_the_ending_in_the_code_is_the_new_paragraph_word_for_word():
    assert explain.ENDING == NEW_ENDING
    assert "\n" not in explain.ENDING  # one paragraph


def test_1_a_new_clues_card_has_exactly_the_new_ending(client):
    card = clue_named(clues_json(client, *FIVE)["new_clues"], "Sevoflurane")
    assert card["ending"] == NEW_ENDING


def test_1_a_new_clues_explanation_from_gemini_ends_with_the_new_ending(client):
    _, answer = explained(client, "new_clues", "Sevoflurane",
                          gemini_says(GOOD_ANSWER), *FIVE)
    assert answer["source"] == "gemini"
    assert answer["text"] == GOOD_ANSWER + " " + NEW_ENDING


def test_1_a_new_clues_explanation_from_the_template_ends_with_the_new_ending(client):
    _, answer = explained(client, "new_clues", "Sevoflurane", gemini_unreachable, *FIVE)
    assert answer["source"] == "template"
    assert answer["text"].endswith(" " + NEW_ENDING)


# ---- EXAMPLE 2: an In trials card's ending is exactly the new paragraph ----

def test_2_an_in_trials_card_has_exactly_the_new_ending(client):
    card = clue_named(clues_json(client, *FIVE)["being_studied"], "Vardenafil")
    assert card["trial_phase"] == "Phase 3"  # it really is an In trials card
    assert card["ending"] == NEW_ENDING


def test_2_an_in_trials_explanation_ends_with_the_new_ending(client):
    card, answer = explained(client, "being_studied", "Vardenafil",
                             gemini_unreachable, *FIVE)
    assert "Doctors are already testing Vardenafil for this disease." in answer["text"]
    assert answer["text"].endswith(" " + NEW_ENDING)


# ---- EXAMPLE 3: several proteins say "these proteins", same new sentence ----

def test_3_the_several_proteins_ending_in_the_code_is_word_for_word():
    assert explain.ENDING_MANY == NEW_ENDING_MANY
    assert explain.ENDING_MANY == NEW_ENDING.replace("this protein", "these proteins")


def test_3_a_card_with_several_proteins_says_these_proteins(client):
    card = clue_named(clues_json(client, *GUCY1)["new_clues"], "Isosorbide Mononitrate")
    assert len(card["proteins"]) == 3
    assert card["ending"] == NEW_ENDING_MANY
    assert "these proteins" in card["ending"] and "this protein" not in card["ending"]
    assert card["ending"].endswith(NEW_LAST_SENTENCE)


def test_3_an_explanation_with_several_proteins_ends_the_same_way(client):
    _, answer = explained(client, "new_clues", "Isosorbide Mononitrate",
                          gemini_unreachable, *GUCY1)
    assert answer["text"].endswith(" " + NEW_ENDING_MANY)


# ---- EXAMPLE 4: no ending anywhere holds the old words ----

def test_4_no_ending_in_the_code_holds_the_old_words():
    for ending in (explain.ENDING, explain.ENDING_MANY):
        for gone in GONE:
            assert gone.upper() not in ending.upper(), gone
        assert ending.endswith(NEW_LAST_SENTENCE)


def test_4_no_card_from_the_api_holds_the_old_words(client):
    data = every_clue_card(client)
    for card in data["new_clues"] + data["being_studied"]:
        assert card["ending"] in (NEW_ENDING, NEW_ENDING_MANY), card["medicine"]
        for gone in GONE:
            assert gone.upper() not in card["ending"].upper(), gone
    for gone in GONE:
        assert gone.upper() not in json.dumps(data).upper(), gone


def test_4_no_explanation_holds_the_old_words(client):
    data = clues_json(client, *FIVE)
    cards = data["new_clues"] + data["being_studied"]
    assert cards
    with with_targets(*FIVE), \
            patch("moonlight.explain._gemini_request", side_effect=gemini_unreachable):
        for card in cards:
            answer = client.get(
                "/api/explain", params={"disease_id": PAH_ID, "clue_id": card["id"]}
            ).json()
            assert answer["text"].endswith(" " + card["ending"]), card["medicine"]
            for gone in GONE:
                assert gone.upper() not in answer["text"].upper(), gone


def test_4_the_page_holds_the_old_words_nowhere(page):
    words = plain(page)
    for gone in GONE:
        assert gone.upper() not in words.upper(), gone
        assert gone.upper() not in page.upper(), gone


def test_4_the_sample_card_in_the_guide_has_the_new_ending(page):
    guide = guide_of(page)
    card = guide[guide.index('<section id="guide-card"'):]
    ending = card[card.index('<div class="ending">'):card.index('<div class="card-foot">')]
    assert plain(ending) == "H " + NEW_ENDING  # ticket 3.9: the catch is letter H now, was G


def test_4_every_ending_written_on_the_page_is_the_new_one(page):
    # Every place the page itself spells out "But there is a catch".
    written = re.findall(r"But there is a catch\.[^<]*", page)
    assert written, "the guide's sample card should spell the ending out"
    for ending in written:
        assert ending.strip() in (NEW_ENDING, NEW_ENDING_MANY)


# ---- EXAMPLE 5: Approved cards still have no ending at all ----

def test_5_no_approved_card_from_the_api_has_an_ending(client):
    data = every_clue_card(client)
    assert data["approved"]
    for item in data["approved"]:
        assert "ending" not in item and "explanation" not in item
    said = json.dumps(data["approved"]).upper()
    assert "DO NOT TRY IT" not in said
    assert "BUT THERE IS A CATCH" not in said
    assert "NEVER START, STOP" not in said


def test_5_the_page_still_takes_the_ending_off_an_approved_card(page):
    script = page[page.index("function approvedCard("):]
    script = script[:script.index("\n  }\n")]
    assert 'slot(el, "ending").remove()' in script
    # Ticket 3.8, commit B: no card has an explanation slot any more.
    assert 'data-slot="explanation"' not in page
    assert "Do not try it" not in script and "/api/explain" not in script


# ---- EXAMPLE 6: the safety line at the top is unchanged, word for word ----

def test_6_the_safety_line_is_unchanged_word_for_word(page):
    assert SAFETY_LINE == (
        "For learning and research exploration, not medical advice. "
        "Never start, stop or change any medicine without a doctor."
    )
    line = page[page.index('data-slot="safety-line"'):]
    line = line[line.index(">") + 1:line.index("</div></div>")]
    assert plain(line) == SAFETY_LINE
    # The ending's new last sentence is the second half of this line.
    assert SAFETY_LINE.endswith(" " + NEW_LAST_SENTENCE)
    assert plain(page).count(SAFETY_LINE) == 1
