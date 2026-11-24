"""Ticket 4.1. Page tidy: leftover words and the front page's heading.

a. The page does not contain "A short explanation of this clue in plain words."
b. The page contains the new heading, word for word, exactly once.
c. The page still contains the safety line, word for word.
d. The "Read explanation" button is still in the clue card.

The heading is also calm and smaller: 20px on a phone, 24px on a wide screen.

The stray dot (Kashish's decision, option A): the dot is no longer part of the
words "Tap to open" and "Tap to close". The style draws it in a small space in
front of the words. When the words drop onto a line of their own, that space
falls outside the title's edge, where it is cut off.

The page is read from GET /. No network.
"""

import re

import pytest
from fastapi.testclient import TestClient

from moonlight import api

LEFTOVER = "A short explanation of this clue in plain words."
HEADING = "Research a disease: approved medicines, trials and new clues."
SAFETY_LINE = (
    "For learning and research exploration, not medical advice. "
    "Never start, stop or change any medicine without a doctor."
)
READ_BUTTON = '<button class="ghost-btn" type="button" data-part="read">Read explanation</button>'
COULD_NOT_FETCH = (
    "Moonlight could not get this explanation. "
    "The facts on this card are still correct."
)


@pytest.fixture(scope="module")
def page():
    return TestClient(api.app).get("/").text


def styles_of(page):
    return "".join(re.findall(r"(?s)<style>(.*?)</style>", page))


def template_of(page, name):
    start = page.index('<template id="%s">' % name)
    return page[start:page.index("</template>", start)]


def explanation_box_of(card):
    """The clue card's explanation box, before the button is pressed."""
    start = card.index('<div class="explanation" data-slot="explanation">')
    return card[start:card.index('<p class="ending"', start)]


# ---- a. the leftover words ----

def test_a_the_leftover_sentence_is_gone(page):
    assert LEFTOVER not in page
    assert "A short explanation" not in page


# Ticket 3.8, commit B (Shreshth, 24 Nov 2026, after speaking with Kashish):
# the explanation box is off the card. These two tests used to be
# test_a_the_box_shows_only_its_label_and_the_button and
# test_a_the_other_two_messages_in_the_box_stay.
def test_a_the_card_has_no_explanation_box(page):
    card = template_of(page, "card-template")
    assert '<div class="explanation" data-slot="explanation">' not in card
    assert "Plain-language explanation" not in page


def test_a_the_other_two_messages_of_the_box_are_gone_with_it(page):
    assert COULD_NOT_FETCH not in page
    assert '<template id="explanation-failed">' not in page
    assert '<template id="explanation-loading">' not in page


# ---- b. the heading ----

def test_b_the_new_heading_is_on_the_page_exactly_once(page):
    assert page.count(HEADING) == 1


def test_b_it_is_the_front_pages_main_heading(page):
    home = page[page.index('<section id="home"'):page.index('<section id="results"')]
    assert re.findall(r"(?s)<h1[^>]*>(.*?)</h1>", home) == [HEADING]


def test_b_the_heading_is_20px_on_a_phone_and_24px_on_a_wide_screen(page):
    styles = styles_of(page)
    assert "#home h1{font-size:20px;" in styles
    assert "@media(min-width:760px){#home h1{font-size:24px}}" in styles


# ---- c. the safety line ----

def test_c_the_safety_line_is_still_there_word_for_word(page):
    assert page.count(SAFETY_LINE) == 1


# ---- d. the button ----

# Ticket 3.8, commit B. This test used to be
# test_d_the_read_explanation_button_is_still_in_the_clue_card.
def test_d_the_read_explanation_button_is_no_longer_in_the_clue_card(page):
    assert READ_BUTTON not in page
    assert "Read explanation" not in page


# ---- the stray dot ----

def test_the_dot_is_not_part_of_the_tap_words(page):
    assert "· Tap to" not in page
    # 5 since ticket 2.28: the opposite-way box on the New clues tab is the fifth.
    # 6 since ticket 2.27: the red-warning box on the Approved tab is the sixth.
    assert page.count('<span data-part="tap">Tap to open</span>') == 6
    assert 'box.open ? "Tap to close" : "Tap to open";' in page


def test_the_style_draws_the_dot_in_front_of_the_words(page):
    styles = styles_of(page)
    assert '.wider-box summary [data-part="tap"]::before{content:"·";' in styles


def test_the_dot_is_cut_off_when_the_words_sit_on_their_own_line(page):
    styles = styles_of(page)
    # The title's box starts a dot's width to the left, and its first line is
    # pushed back by the same width, so only a dropped line starts with the dot.
    assert ("#narrower-box summary,#wider-box summary"
            "{margin-left:-.55em;text-indent:.55em;clip-path:inset(-8px -8px -8px .55em)}") in styles


def test_the_folded_boxes_are_still_details_with_a_summary(page):
    for box in ("narrower-box", "wider-box"):
        start = page.index('<details class="wider-box" id="%s"' % box)
        assert "<summary>" in page[start:page.index("</details>", start)]
