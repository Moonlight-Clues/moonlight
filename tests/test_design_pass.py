"""Ticket 5.8. Sidha's design pass.

Decisions, 16 Nov (Sidha is the designer; Kashish approved). Layout and words only.
1. "Old medicines. New questions." is removed, with the thin line above it.
2. "Made with care by a family in Kochi" and its heart are removed, and the
   handwriting font (Caveat) with them. The contact line and the last footer
   line stay.
3. The page has equal space on both sides: on a wide screen the content
   column sits in the middle. Text is aligned as before. (The first build
   centred every line of text. Kashish corrected that on 16 Nov.)

The page is read from GET /. No network.
"""

import re

import pytest
from fastapi.testclient import TestClient

from moonlight import api

from test_api import FOOTER_NOTE, NEW_ORDER, SAFETY_LINE, guide_of, plain

MOTTO = "Old medicines. New questions."
MADE = "Made with care by a family in Kochi"
HEADING = "Research a disease: approved medicines, trials and new clues."
LINE_UNDER = (
    "Type a disease name to begin. Research clues, not "
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
    # Ticket R5 (asked for by Kashish): the one @font-face allowed is Space
    # Grotesk, from the site's own folder. Nothing else.
    own = re.sub(r'@font-face\{font-family:"Space Grotesk";[^}]*\}', "", page)
    own = own.replace("/fonts/space-grotesk-latin-wght-normal.woff2", "")
    assert page.count("@font-face") == 1
    assert "@font-face" not in own
    assert "caveat" not in page.lower()
    assert "woff" not in own.lower().replace('type="font/woff2"', "")
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
    # Ticket 2.66 (MAIN 5's named OK, 27 Nov): the last line ends with
    # " · Corrections", a link to the corrections page.
    assert plain(footer) == CONTACT + " " + FOOTER_NOTE + " · Corrections"
    assert ("Found something wrong or have any feedback? Contact "
            '<a href="mailto:hello@moonlightclues.com">hello@moonlightclues.com</a>') in footer
    assert re.search(r'<div class="footer-note">[^<]* · <a href="/corrections">Corrections</a></div>',
                     footer)  # ticket 2.66


# ---- Example 3: no medicine is named before a search ----

def test_outside_the_guide_the_page_still_names_no_medicine(page):
    outside = page.replace(guide_of(page), "").upper()
    for name in NEW_ORDER + ["Udenafil", "Vardenafil", "Sildenafil", "Tadalafil"]:
        assert name.upper() not in outside, name


# ---- Decision 3, corrected by Kashish on 16 Nov: equal space on both sides ----
# The first build centred every line of text. That was a misunderstanding.
# Text is aligned as on main. Only the content column moves to the middle.

def test_the_columns_sit_in_the_middle_of_the_screen(page):
    """The search, the results and the guide are narrower than a wide screen.
    Each one must sit in the middle, with the same space on its left and right."""
    styles = styles_of(page)
    for name in (".search-area", ".results", ".guide"):
        rule = re.search(r"(?m)^%s\{[^}]*\}" % re.escape(name), styles).group(0)
        assert "max-width:760px" in rule, rule
        assert "margin-inline:auto" in rule, rule


def test_on_a_phone_the_space_is_16px_on_each_side_as_before(page):
    assert ".wrap{width:min(100% - 32px,1060px);margin-inline:auto}" in styles_of(page)


def test_text_is_not_centred_it_is_aligned_as_on_main(page):
    styles = styles_of(page)
    body = re.search(r"(?m)^body\{[^}]*\}", styles).group(0)
    assert "text-align" not in body
    # The rules the first build changed, word for word as on main.
    for rule in (
        ".brandline{display:flex;align-items:center;gap:10px}",
        ".tagline{margin:8px 0 0;color:#C4D2D9;font-size:13px;max-width:640px}",
        ".match-list button{width:100%;text-align:left;",
        ".chips{display:flex;flex-wrap:wrap;gap:7px}",
        ".card-top{display:flex;justify-content:space-between;align-items:start;gap:12px}",
        ".card-title{display:flex;align-items:flex-start;gap:11px;min-width:0}",
        ".reports{font-size:11px;color:var(--muted);white-space:nowrap;text-align:right;flex:none}",
        ".protein-row{display:flex;align-items:center;justify-content:space-between;gap:10px;",
        ".card-foot{display:flex;justify-content:space-between;align-items:center;",
        ".card-help{font-size:12px;text-align:right;margin:8px 2px 0}",
    ):
        assert rule in styles, rule
    assert ".safety-inner{justify-content:center}" not in styles
