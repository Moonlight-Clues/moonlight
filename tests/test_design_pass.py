"""Ticket 5.8. Sidha's design pass.

Decisions, 16 Nov (Sidha is the designer; Kashish approved). Layout and words only.
1. "Old medicines. New questions." is removed, with the thin line above it.
2. "Made with care by a family in Kochi" and its heart are removed, and the
   handwriting font (Caveat) with them. The contact line and the last footer
   line stay.
3. Everything on the page is centred.

The page is read from GET /. No network.
"""

import re

import pytest
from fastapi.testclient import TestClient

from moonlight import api

from test_api import FOOTER_NOTE, NEW_ORDER, SAFETY_LINE, guide_of, plain

MOTTO = "Old medicines. New questions."
MADE = "Made with care by a family in Kochi"
HEADING = "Disease → protein → medicine. One search."
LINE_UNDER = (
    "Moonlight follows Open Targets research data from a disease to its "
    "proteins, then to medicines that act on them. Research clues, not "
    "treatment recommendations."
)
CONTACT = "Found something wrong or have any feedback? Contact hello@moonlightclues.com"


@pytest.fixture
def page():
    return TestClient(api.app).get("/").text


def styles_of(page):
    return "".join(re.findall(r"(?s)<style>(.*?)</style>", page))


def home_of(page):
    return page[page.index('<section id="home"'):page.index('<section id="results"')]


def footer_of(page):
    return page[page.index("<footer"):page.index("</footer>")]


# ---- Example 1: what is removed ----

def test_old_medicines_new_questions_is_gone(page):
    assert MOTTO not in page
    assert "Old medicines" not in page


def test_the_thin_line_above_it_is_gone_too(page):
    assert 'class="motto' not in page
    assert ".motto" not in styles_of(page)


def test_made_with_care_and_its_heart_are_gone(page):
    assert MADE not in page
    assert "Kochi" not in page
    footer = footer_of(page)
    assert "<svg" not in footer            # the heart
    assert 'class="made"' not in page
    assert ".made" not in styles_of(page)


def test_the_handwriting_font_is_gone(page):
    assert "@font-face" not in page
    assert "caveat" not in page.lower()
    assert "woff" not in page.lower()
    assert "cursive" not in styles_of(page)


# ---- Example 2: what stays, word for word ----

def test_the_safety_line_is_word_for_word_as_before(page):
    assert page.count(SAFETY_LINE) == 1
    start = page.index('data-slot="safety-line"')
    line = page[page.rindex("<", 0, start):page.index("<main")]
    assert plain(line) == SAFETY_LINE


def test_the_heading_and_the_line_under_it_are_as_before(page):
    home = home_of(page)
    assert re.findall(r"(?s)<h1[^>]*>(.*?)</h1>", home) == [HEADING]
    assert re.search(r"</h1>\s*<p>%s</p>" % re.escape(LINE_UNDER), home)


def test_the_search_box_is_as_before(page):
    home = home_of(page)
    assert "Search by disease name<" in home
    assert 'placeholder="Type a disease name"' in home
    assert re.search(r'<button class="btn" type="submit">Explore</button>', home)
    assert re.findall(r'<button class="chip"[^>]*>(.*?)</button>', home) == [
        "Pulmonary arterial hypertension"]


def test_the_three_tabs_are_as_before(page):
    tabs = page[page.index('data-slot="tabs"'):]
    tabs = tabs[:tabs.index("</div>")]
    assert [plain(tab) for tab in re.findall(r"(?s)<button[^>]*>(.*?)</button>", tabs)] == [
        "Approved", "In trials", "New clues"]


def test_the_footer_keeps_the_contact_line_and_the_last_line_in_that_order(page):
    footer = footer_of(page)
    assert plain(footer) == CONTACT + " " + FOOTER_NOTE
    assert ("Found something wrong or have any feedback? Contact "
            '<a href="mailto:hello@moonlightclues.com">hello@moonlightclues.com</a>') in footer


# ---- Example 3: no medicine is named before a search ----

def test_outside_the_guide_the_page_still_names_no_medicine(page):
    outside = page.replace(guide_of(page), "").upper()
    for name in NEW_ORDER + ["Udenafil", "Vardenafil", "Sildenafil", "Tadalafil"]:
        assert name.upper() not in outside, name


# ---- Decision 3: everything is centred ----

def test_the_whole_page_is_centred_and_nothing_is_pushed_left_or_right(page):
    styles = styles_of(page)
    assert re.search(r"body\{[^}]*text-align:center", styles)
    assert "text-align:left" not in styles
    assert "text-align:right" not in styles
    # The script and the templates set no side of their own either.
    assert not re.search(r"text-align\s*:\s*(left|right)", page)
    assert not re.search(r"textAlign", page)


def test_the_columns_sit_in_the_middle_of_the_screen(page):
    """The search, the results and the guide are narrower than a wide screen.
    Each one must sit in the middle, not against the left edge."""
    styles = styles_of(page)
    for name in (".search-area", ".results", ".guide"):
        rule = re.search(r"(?m)^%s\{[^}]*\}" % re.escape(name), styles).group(0)
        assert "margin-inline:auto" in rule, rule
