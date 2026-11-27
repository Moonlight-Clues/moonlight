"""Ticket 5.8, part 2. The guide, condensed.

Papa and Kashish approved this design on 16 Nov: the same pictures with far
fewer words. The detail for doctors and the sources are folded and open
with one tap. Every text in quotes in the ticket is word for word here.

The three lines "AI.", "Words." and "Left out." are Kashish's second
wording, after the first was checked against the code and found not true
in every case.

The page is read from GET /. No network.
"""

import re

import pytest
from fastapi.testclient import TestClient

from moonlight import api

from test_api import ENDING, NEW_ORDER, SAFETY_LINE, guide_of, plain

ADDRESS = "hello@moonlightclues.com"
MAIL_LINK = '<a href="mailto:%s">%s</a>' % (ADDRESS, ADDRESS)

HEADINGS = [
    "How to read what Moonlight finds.",
    "A medicine for one disease may act on a protein linked to another.",
    "Three steps",
    "The three tabs",
    "How to read a card",
    "What Moonlight can and cannot tell you",
    "Doctor, pharmacist or researcher?",
]
CAPTIONS = [
    ("Medicine", "already approved"),
    ("Protein", "a tiny machine in the body"),
    ("Disease", "linked to that protein"),
]
STEPS = [
    ("Type a disease", "Not sure? Moonlight asks “Did you mean?”"),
    ("Pick the one you mean", "Moonlight never picks for you."),
    ("Open a tab", "Three lists of medicines."),
]
TILES = [
    ("Approved", "Approved for this disease. Listed A to Z."),
    ("In trials", "Being tested for it. Not a prediction."),
    ("New clues", "No recorded link yet. Worth reading about."),
]
CARD_EXPLANATION = "Doxapram grabs a protein called KCNK3 and turns it down, like a volume knob."
KEY = [
    ("A", "Medicine and its forms"),
    ("B", "Trial and approval records in the database"),  # ticket 3.9
    ("C", "The path, in three steps"),
    ("D", "Up, down or unknown"),
    ("E", "How strong the link is"),
    # Ticket 3.9: Kashish's signed words of 25 Nov. B is new words; F, G and J are new
    # parts of the card; the catch and the source move to H and I.
    ("F", "What the protein does"),
    ("G", "Why the gene is linked"),
    ("H", "The catch, on every clue"),
    ("I", "Where the fact comes from"),
    ("J", "Tell us if something is wrong"),
]
CAN = [
    "medicines approved for a disease",
    "medicines being tested for it",
    "new connections worth reading about",
    "questions to take to your doctor",
]
CANNOT = [
    "if a medicine will help or harm",
    "which medicine is best",
    "what is approved in your country",
    "anything in place of your doctor",
]
DOCTORS_TITLE = "For doctors: how far to trust each part"
DOCTORS = [
    # Ticket 3.32: ClinicalTrials.gov is named as the source of trial details.
    ("Source.", "Open Targets Platform. Trial details from ClinicalTrials.gov."),
    ("“Approved”.", "In at least one country, per the database. Not a measure of efficacy."),
    ("Left out.", "Withdrawn anywhere, or approved nowhere: counted, never named. "
                  "Unclear link to the disease: counted separately."),
    ("Wider and narrower diseases.", "Shown with a label, each in its own folded box."),
    # Ticket 3.32: new line.
    ("Trials.", "Rows are the trials the database links to the medicine. Medicines found only on ClinicalTrials.gov are matched by exact name. A finished trial is a record, not a result."),
    ("Known gaps.", "A missing medicine may be withdrawn somewhere, filed further away, "
                    "or not recorded yet."),
    ("Weak proof.", "Japan-list-only approvals say so. Approvals with no regulator "
                    "record say so. Confirmed mistakes carry a red warning."),
    ("Ranking.", "Link strength across the top 25 proteins. One protein machine counts once."),
    # Ticket 3.8, commit B: the sentence about explanations is no longer true and is gone.
    ("AI.", "Gemini suggests which disease you mean, and Open Targets confirms it."),
]
NOT_REFERENCE = "Moonlight is not a prescribing reference."
FACTS_TITLE = "Where the facts come from"
FACTS = [
    ("Facts.", "Open Targets Platform, an open research database."),  # ticket T0
    # Ticket 3.32: new line, straight after Facts.
    ("Trials.", "ClinicalTrials.gov, the US public register of clinical studies."),
    # Ticket 3.8, commit B: the sentence about explanations is no longer true and is gone.
    ("Words.", "What you type is sent to Gemini, so type no names or private details."),
    ("Visits.", "Counted with Umami. No cookies. Never the disease or anything you type."),
    # Ticket 3.8: Kashish's credit line, 23 Nov 2026.
    ("Protein descriptions.", "Written by UniProt, read through Open Targets. CC BY 4.0."),
    # Ticket 3.32: the report note moved here from under the A to J key. Last line.
    ("Reports.", "We read every report. Nothing about you is kept."),
]
STRIP = "Test a condition you know well. Tell us what is missing or wrong."


@pytest.fixture
def page():
    return TestClient(api.app).get("/").text


@pytest.fixture
def guide(page):
    return guide_of(page)


def part(guide, start, end):
    """The piece of the guide from one mark to the next."""
    piece = guide[guide.index(start):]
    return piece[:piece.index(end)]


def fold(guide, title):
    """The folded part with this title: (its opening tag, everything inside)."""
    at = guide.index(">%s</summary>" % title)
    opening = guide[guide.rindex("<details", 0, at):guide.rindex("<summary", 0, at)]
    return opening, guide[at:guide.index("</details>", at)]


def lines_of(inside):
    """(bold label, words) for each line of a folded list."""
    return [(plain(label), plain(words)) for label, words in re.findall(
        r"(?s)<li><div><b>(.*?)</b>\s*<span>(.*?)</span></div></li>", inside)]


# ---- the order of the whole guide ----

def test_the_guide_has_these_seven_headings_in_this_order(guide):
    headings = [plain(h) for h in re.findall(r"(?s)<h[12][^>]*>(.*?)</h[12]>", guide)]
    assert headings == HEADINGS


def test_the_two_folds_come_after_the_boxes_and_before_the_last_strip(guide):
    places = [guide.index(mark) for mark in (
        ">What Moonlight can and cannot tell you</h2>",
        ">%s</summary>" % DOCTORS_TITLE,
        ">%s</summary>" % FACTS_TITLE,
        ">Doctor, pharmacist or researcher?</h2>",
    )]
    assert places == sorted(places)
    assert guide.count("<details") == 2


# ---- a. the opening ----

def test_the_opening_is_an_eyebrow_a_heading_one_line_and_the_button(guide):
    opening = guide[:guide.index("</section>")]
    assert re.search(
        r'<div class="eyebrow">How to use Moonlight</div>\s*'
        r"<h1>How to read what Moonlight finds\.</h1>\s*"
        r"<p>Type a disease\. See the medicines that act on its proteins\.</p>\s*"
        r'<a class="ghost-btn" href="#home" data-guide-close>Back to search</a>', opening)
    assert opening.count("<p>") == 1


# ---- b. the navy picture ----

def test_the_picture_has_the_three_shapes_with_short_captions_and_no_paragraph(guide):
    picture = part(guide, 'aria-labelledby="guide-idea-title"', "</section>")
    assert 'class="idea"' in guide[guide.rindex("<section", 0, guide.index("guide-idea-title")):]
    found = re.findall(r'<strong class="display">([^<]+)</strong><span>([^<]+)</span>', picture)
    assert found == CAPTIONS
    for shape in ("circle", "diamond", "square"):
        assert 'class="shape %s"' % shape in picture
    assert "<p" not in picture


# ---- c. three steps ----

def test_the_three_steps_have_these_words_and_no_sub_line(guide):
    steps = part(guide, 'id="guide-steps-title"', "</section>")
    found = re.findall(
        r'<li><span class="rank" aria-hidden="true">(\d)</span><div><h3>([^<]+)</h3>'
        r"<p>([^<]+)</p></div></li>", steps)
    assert found == [(str(n + 1), title, words) for n, (title, words) in enumerate(STEPS)]
    assert "guide-sub" not in steps


# ---- d. the three tabs ----

def test_the_three_tabs_are_a_picture_and_three_tiles(guide):
    tabs = part(guide, 'id="guide-tabs-title"', "</section>")
    assert ('<div class="tabs" aria-hidden="true"><span class="tab on">Approved</span>'
            '<span class="tab">In trials</span><span class="tab">New clues</span></div>') in tabs
    found = re.findall(r'<div class="tab-note"><h3>([^<]+)</h3><p>([^<]+)</p></div>', tabs)
    assert found == TILES
    assert tabs.count("<p") == 3


# ---- e. how to read a card ----

def test_the_card_part_has_its_sub_line(guide):
    card = part(guide, 'id="guide-card-title"', "</section>")
    assert '<p class="guide-sub">A real clue. Match the gold letters.</p>' in card


# Ticket 3.8, commit B: no letter F, because the card has no explanation.
# Ticket 3.9: Kashish signed the new legend (25 Nov): letters A to J, no gap. This test used to be
# test_the_example_card_is_doxapram_with_its_gold_letters_a_to_h, checking list("ABCDEGH").
def test_the_example_card_is_doxapram_with_its_gold_letters_a_to_j(guide):
    card = part(guide, '<article class="card">', "</article>")
    assert re.findall(r'<span class="k" aria-label="([A-J])">\1</span>', card) == list("ABCDEFGHIJ")
    words = plain(card)
    assert "Forms: Doxapram, Doxapram Hydrochloride" in words
    assert "8 records" in words  # ticket 3.10, Q15: the count says records
    assert "Doxapram → KCNK3 → Pulmonary arterial hypertension" in words
    assert "79 / 100 points" in words and "Down" in words
    assert "The data does not say which direction this disease needs." in words


# Ticket 3.8, commit B. This test used to be
# test_the_example_cards_explanation_is_one_sentence.
def test_the_example_card_has_no_explanation(guide):
    card = part(guide, '<article class="card">', "</article>")
    assert '<div class="explanation">' not in card
    assert "Plain-language explanation" not in guide
    assert CARD_EXPLANATION not in guide


def test_the_example_cards_fixed_ending_is_word_for_word(guide):
    card = part(guide, '<article class="card">', "</article>")
    ending = card[card.index('<div class="ending">'):card.index('<div class="card-foot">')]
    assert plain(ending) == "H " + ENDING  # ticket 3.9: the catch is letter H now, was G


# Ticket 3.8, commit B: seven chips now. This test used to be
# test_under_the_card_are_eight_chips_each_a_gold_letter_and_a_few_words.
# Ticket 3.9: Kashish signed the new legend (25 Nov): letters A to J, no gap. Ten chips now. This test used to be
# test_under_the_card_are_seven_chips_each_a_gold_letter_and_a_few_words.
def test_under_the_card_are_ten_chips_each_a_gold_letter_and_a_few_words(guide):
    card_part = guide[guide.index('id="guide-card"'):]
    assert card_part.index("</article>") < card_part.index('<ul class="key">')
    key = part(guide, '<ul class="key">', "</ul>")
    found = re.findall(
        r'<li><span class="k" aria-hidden="true">([A-J])</span><span>([^<]+)</span></li>', key)
    assert found == KEY
    assert "<dl" not in guide and "<dt" not in guide and "<dd" not in guide


# ---- f. can and cannot ----

def test_the_two_boxes_hold_these_lines(guide):
    boxes = part(guide, 'id="guide-limits-title"', "</section>")
    can = part(boxes, "<h3>It can show</h3>", "</ul>")
    cannot = part(boxes, "<h3>It cannot tell you</h3>", "</ul>")
    assert [plain(item) for item in re.findall(r"(?s)<li>(.*?)</li>", can)] == CAN
    assert [plain(item) for item in re.findall(r"(?s)<li>(.*?)</li>", cannot)] == CANNOT
    assert boxes.index('class="box do"') < boxes.index('class="box dont"')
    assert boxes.count("<li>") == 8


def test_good_ways_to_use_it_and_the_six_long_points_are_removed(guide):
    for gone in (
        "Good ways to use it", "Use it to", "Do not use it to",
        "Whether a clue would help or harm.", "Which direction the disease needs.",
        "Anything beyond the 25 most-linked proteins.",
        "Treatments that do not act on a protein.", "What is approved where you live.",
        "That the record is complete or current.",
    ):
        assert gone not in guide, gone


# ---- g. the two folded parts ----

@pytest.mark.parametrize("title", [DOCTORS_TITLE, FACTS_TITLE])
def test_each_fold_is_closed_at_first_and_uses_the_wider_group_pattern(page, guide, title):
    opening, _ = fold(guide, title)
    # The same pattern as the wider-group box: <details> with a <summary>.
    # The browser opens it with one tap, or with Enter or Space on the keyboard.
    assert re.fullmatch(r'<details class="wider-box">\s*', opening)
    assert " open" not in opening
    assert '<details class="wider-box" id="wider-box" hidden>' in page
    # Nothing takes the title out of the keyboard's reach.
    assert "tabindex" not in guide


def test_the_fold_for_doctors_holds_these_nine_lines_then_the_sentence_set_apart(guide):
    _, inside = fold(guide, DOCTORS_TITLE)
    assert lines_of(inside) == DOCTORS
    assert inside.index("</ul>") < inside.index('<p class="not-reference">%s</p>' % NOT_REFERENCE)
    assert guide.count(NOT_REFERENCE) == 1


def test_the_fold_of_sources_holds_these_six_lines(guide):
    _, inside = fold(guide, FACTS_TITLE)
    assert lines_of(inside) == FACTS


# ---- h. the last strip ----

def test_the_guide_ends_with_a_short_navy_strip_for_doctors(guide):
    strip = guide[guide.rindex("<section"):]
    assert re.search(
        r'<section class="idea strip" aria-labelledby="guide-invite-title">\s*'
        r'<h2 id="guide-invite-title">Doctor, pharmacist or researcher\?</h2>\s*'
        r"<p>%s</p>\s*"
        r'<p class="contact">%s</p>\s*</section>' % (re.escape(STRIP), re.escape(MAIL_LINK)),
        strip)
    assert guide.rstrip().endswith("</section>")


def test_the_longer_invitation_near_the_top_is_removed(guide):
    assert "Are you a doctor, pharmacist or researcher?" not in guide
    assert "Moonlight gets better when people who know the medicines test it." not in guide
    assert guide.count("guide-invite-title") == 2  # the strip's heading and its label


def test_the_address_can_be_selected_and_is_a_mail_link(page, guide):
    assert guide.count(MAIL_LINK) == 1
    assert ".contact a{user-select:text;-webkit-user-select:text}" in page


# ---- must stay true ----

def test_the_safety_line_is_word_for_word_and_placed_as_on_main(page):
    assert page.count(SAFETY_LINE) == 1
    assert page.index('class="site-header"') < page.index('data-slot="safety-line"') \
        < page.index("<main")
    assert SAFETY_LINE not in guide_of(page)


def test_outside_the_guide_no_medicine_is_named_and_inside_only_doxapram(page):
    guide = guide_of(page)
    outside = page.replace(guide, "").upper()
    for name in NEW_ORDER + ["Udenafil", "Vardenafil", "Sildenafil", "Tadalafil"]:
        assert name.upper() not in outside, name
        if name != "Doxapram":
            assert name.upper() not in guide.upper(), name
    assert "Doxapram" in guide


def test_the_two_links_still_open_the_guide_at_the_right_place(page):
    assert re.findall(r'<a [^>]*href="#(guide[a-z-]*)"[^>]*data-guide[^>]*>([^<]+)</a>', page) == [
        ("guide", "How to use Moonlight."),
        ("guide-card", "How to read a card"),
    ]
    assert page.count('<section id="guide"') == 1
    assert page.count('<section id="guide-card"') == 1
    assert 'linked.get("guide") === "1"' in page


# ---- the footer lines up with the middle column ----

def test_the_footer_lines_up_with_the_middle_column(page):
    styles = "".join(re.findall(r"(?s)<style>(.*?)</style>", page))
    assert ".site-footer .wrap{max-width:760px}" in styles
    # The header and the safety line are not changed: the page's one .wrap rule is as on main.
    assert ".wrap{width:min(100% - 32px,1060px);margin-inline:auto}" in styles
