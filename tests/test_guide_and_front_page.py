"""Ticket 5.7. The front-page heading, the contact line, and the guide.

Kashish's decisions, 16 Nov. Words and layout only.
A. The front page's big heading and the line under it have new words.
   "Old medicines. New questions." stays, smaller and lower down.
B. The footer's guide link is replaced by a contact line.
C. The guide's section "What Moonlight cannot tell you" is renamed, and
   gets two boxes at its top. Its six points stay as they were.

The page is read from GET /. No network.
"""

import re

import pytest
from fastapi.testclient import TestClient

from moonlight import api

from test_api import FOOTER_LINE, FOOTER_NOTE, NEW_ORDER, SAFETY_LINE, guide_of, plain

HEADING = "Disease → protein → medicine. One search."
LINE_UNDER = (
    "Moonlight follows Open Targets research data from a disease to its "
    "proteins, then to medicines that act on them. Research clues, not "
    "treatment recommendations."
)
MOTTO = "Old medicines. New questions."
CONTACT = "Found something wrong or have any feedback? Contact hello@moonlightclues.com"
ADDRESS = "hello@moonlightclues.com"

EVERYONE = "For everyone: what Moonlight can and cannot tell you"
CAN = [
    "show which medicines are already approved for a disease",
    "show which medicines are being tested for it",
    "show new connections that scientists might find worth reading about",
    "help you write down questions to take to your doctor",
]
CANNOT = [
    "tell you whether a medicine will help or harm you",
    "tell you which medicine is best",
    "tell you what is approved in your country",
    "replace your doctor",
]
# The six points that were in the section before this ticket, word for word.
SIX_POINTS = [
    "Whether a clue would help or harm. That takes trials in people.",
    "Which direction the disease needs. A medicine that turns a protein the "
    "wrong way could make things worse.",
    "Anything beyond the 25 most-linked proteins. Moonlight stops there for each disease.",
    "Treatments that do not act on a protein. A moisturiser, a diet or surgery "
    "will never appear.",
    "What is approved where you live. The database records approval in at "
    "least one country.",
    "That the record is complete or current. Public databases have gaps and "
    "mistakes, and they change.",
]


@pytest.fixture
def page():
    return TestClient(api.app).get("/").text


def home_of(page):
    return page[page.index('<section id="home"'):page.index('<section id="results"')]


def footer_of(page):
    return page[page.index("<footer"):page.index("</footer>")]


def everyone_of(page):
    """The "For everyone" section of the guide, from its heading to its end."""
    guide = guide_of(page)
    section = guide[guide.index('id="guide-limits-title"'):]
    return section[:section.index("</section>")]


def box_items(section, title):
    """The lines of the box with this title."""
    box = section[section.index("<h3>%s</h3>" % title):]
    box = box[:box.index("</ul>")]
    return [plain(item) for item in re.findall(r"(?s)<li>(.*?)</li>", box)]


# ---- Example 1: the front page ----

def test_the_big_heading_has_the_new_words(page):
    home = home_of(page)
    assert re.findall(r"(?s)<h1[^>]*>(.*?)</h1>", home) == [HEADING]


def test_the_line_under_the_heading_has_the_new_words(page):
    home = home_of(page)
    assert re.search(r"</h1>\s*<p>%s</p>" % re.escape(LINE_UNDER), home)
    assert "not treatment recommendations" in page


def test_old_medicines_new_questions_stays_smaller_and_lower_down(page):
    home = home_of(page)
    assert page.count(MOTTO) == 1 and MOTTO in home
    # No longer a heading, and under the search box and the quick-start chip.
    assert not re.search(r"(?s)<h\d[^>]*>[^<]*%s" % re.escape(MOTTO), home)
    assert home.index('class="search-box"') < home.index('data-slot="chips"') < home.index(MOTTO)


def test_the_search_box_the_chip_and_the_new_here_line_do_not_change(page):
    home = home_of(page)
    assert 'placeholder="Type a disease name"' in home
    assert "Search by disease name<" in home
    assert re.findall(r'<button class="chip"[^>]*>(.*?)</button>', home) == [
        "Pulmonary arterial hypertension"]
    assert re.search(
        r'New here\? <a [^>]*href="#guide"[^>]*data-guide[^>]*>How to use Moonlight\.</a>', home)


# ---- Example 2: the footer ----

def test_the_footer_holds_the_contact_line(page):
    assert CONTACT in plain(footer_of(page))


def test_the_address_is_text_and_also_a_mail_link(page):
    footer = footer_of(page)
    assert '<a href="mailto:%s">%s</a>' % (ADDRESS, ADDRESS) in footer


def test_the_footer_has_no_link_to_the_guide(page):
    footer = footer_of(page)
    assert "data-guide" not in footer
    assert 'href="#guide' not in footer
    assert "How to use Moonlight" not in footer


def test_the_footers_two_other_lines_stay(page):
    footer = footer_of(page)
    assert re.search(r'class="made"[^>]*>\s*%s\s*<svg' % FOOTER_LINE, footer)
    assert FOOTER_NOTE in footer
    assert footer.index(CONTACT.split("?")[0]) < footer.index(FOOTER_LINE) \
        < footer.index(FOOTER_NOTE)


# ---- Example 3: the guide's list for everyone ----

def test_the_section_has_its_new_name_and_the_old_name_is_gone(page):
    guide = guide_of(page)
    assert '<h2 id="guide-limits-title">%s</h2>' % EVERYONE in guide
    assert "What Moonlight cannot tell you" not in page


def test_the_two_boxes_hold_kashishs_lines_word_for_word(page):
    section = everyone_of(page)
    assert box_items(section, "Moonlight can") == CAN
    assert box_items(section, "Moonlight cannot") == CANNOT


def test_the_two_boxes_look_like_use_it_to_and_do_not_use_it_to(page):
    section = everyone_of(page)
    assert re.search(
        r'(?s)<div class="pair">\s*<div class="box do"><h3>Moonlight can</h3>.*?'
        r'<div class="box dont"><h3>Moonlight cannot</h3>', section)


def test_the_six_old_points_stay_underneath_unchanged(page):
    section = everyone_of(page)
    points = section[section.index('<ul class="limits">'):]
    points = points[:points.index("</ul>")]
    assert [plain(item) for item in re.findall(r"(?s)<li>(.*?)</li>", points)] == SIX_POINTS
    assert section.index("Moonlight cannot</h3>") < section.index('<ul class="limits">')
    assert "Knowing these makes the rest more useful." in section  # nothing is removed


# ---- Example 4: the safety line ----

def test_the_safety_line_is_word_for_word_as_before(page):
    assert page.count(SAFETY_LINE) == 1
    assert SAFETY_LINE == (
        "For learning and research exploration, not medical advice. "
        "Never start, stop or change any medicine without a doctor."
    )


# ---- Example 5: medicines named before a search ----

def test_outside_the_guide_no_medicine_is_named_and_inside_only_doxapram(page):
    guide = guide_of(page)
    outside = page.replace(guide, "").upper()
    for name in NEW_ORDER + ["Udenafil", "Vardenafil", "Sildenafil", "Tadalafil"]:
        assert name.upper() not in outside, name
        if name != "Doxapram":
            assert name.upper() not in guide.upper(), name
    assert "Doxapram" in guide


# ---- Careful: the mail link is the only one ----

def test_the_page_has_one_mail_link_and_it_is_in_the_footer(page):
    assert page.count("mailto:") == 1
    assert "mailto:" + ADDRESS in footer_of(page)
