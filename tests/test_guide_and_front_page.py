"""Ticket 5.7. The front-page heading, the contact line, and the guide.

Kashish's decisions, 16 Nov. Words and layout only.
A. The front page's big heading and the line under it have new words.
   "Old medicines. New questions." stays, smaller and lower down.
B. The footer's guide link is replaced by a contact line.
C. The guide gets an invitation for doctors straight after its opening.
   Its section "What Moonlight cannot tell you" is renamed, and gets two
   boxes at its top. Its six points stay as they were. Straight after it
   is a new section for doctors.

The page is read from GET /. No network.
"""

import re

import pytest
from fastapi.testclient import TestClient

from moonlight import api

from test_api import FOOTER_LINE, FOOTER_NOTE, NEW_ORDER, SAFETY_LINE, guide_of, plain

HEADING = "Research a disease: approved medicines, trials and new clues."
LINE_UNDER = (
    "Moonlight follows Open Targets research data from a disease to its "
    "proteins, then to medicines that act on them. Research clues, not "
    "treatment recommendations."
)
MOTTO = "Old medicines. New questions."
CONTACT = "Found something wrong or have any feedback? Contact hello@moonlightclues.com"
ADDRESS = "hello@moonlightclues.com"

# Ticket 5.8: the guide is condensed. The words below are the new design's.
EVERYONE = "What Moonlight can and cannot tell you"
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
# The six points that were in the section before ticket 5.8, word for word.
# They are removed now.
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

INVITE_HEADING = "Doctor, pharmacist or researcher?"
INVITE_TEXT = "Test a condition you know well. Tell us what is missing or wrong."
MAIL_LINK = '<a href="mailto:%s">%s</a>' % (ADDRESS, ADDRESS)

DOCTORS = "For doctors: how far to trust each part"
# Kashish's words, 16 Nov. Each was checked against the code on main.
DOCTOR_POINTS = [
    "Source. Open Targets Platform.",
    "“Approved”. In at least one country, per the database. Not a measure of efficacy.",
    "Left out. Withdrawn anywhere, or approved nowhere: counted, never named. "
    "Unclear link to the disease: counted separately.",
    "Wider and narrower diseases. Shown with a label, each in its own folded box.",
    "Known gaps. A missing medicine may be withdrawn somewhere, filed further away, "
    "or not recorded yet.",
    "Weak proof. Japan-list-only approvals say so. Approvals with no regulator "
    "record say so. Confirmed mistakes carry a red warning.",
    "Ranking. Link strength across the top 25 proteins. One protein machine counts once.",
    # Ticket 3.8, commit B: the sentence about explanations is no longer true and is gone.
    "AI. Gemini suggests which disease you mean, and Open Targets confirms it.",
]
LAST_SENTENCE = "Moonlight is not a prescribing reference."


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


# Sidha's design decision, 2026-11-16 (ticket 5.8): the line is removed. This
# test used to be test_old_medicines_new_questions_stays_smaller_and_lower_down.
def test_old_medicines_new_questions_is_removed(page):
    home = home_of(page)
    assert MOTTO not in page
    # The search box and the quick-start chip are still in their order.
    assert home.index('class="search-box"') < home.index('data-slot="chips"')


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


# Ticket 5.8: "Made with care by a family in Kochi" is removed. This test used
# to be test_the_footers_two_other_lines_stay.
def test_the_footers_last_line_stays_and_the_handwritten_line_is_removed(page):
    footer = footer_of(page)
    assert FOOTER_LINE not in footer
    assert FOOTER_NOTE in footer
    assert footer.index(CONTACT.split("?")[0]) < footer.index(FOOTER_NOTE)


# ---- Example 3: the guide's list for everyone ----

def test_the_section_has_its_new_name_and_the_old_name_is_gone(page):
    guide = guide_of(page)
    assert '<h2 id="guide-limits-title">%s</h2>' % EVERYONE in guide
    assert "What Moonlight cannot tell you" not in page


def test_the_two_boxes_hold_kashishs_lines_word_for_word(page):
    section = everyone_of(page)
    assert box_items(section, "It can show") == CAN
    assert box_items(section, "It cannot tell you") == CANNOT


def test_the_two_boxes_look_like_use_it_to_and_do_not_use_it_to(page):
    section = everyone_of(page)
    assert re.search(
        r'(?s)<div class="pair">\s*<div class="box do"><h3>It can show</h3>.*?'
        r'<div class="box dont"><h3>It cannot tell you</h3>', section)


# Ticket 5.8: the two boxes replace the six long points. This test used to
# be test_the_six_old_points_stay_underneath_unchanged.
def test_the_six_old_points_are_removed(page):
    section = everyone_of(page)
    assert '<ul class="limits">' not in section
    words = plain(guide_of(page))
    for point in SIX_POINTS:
        assert point not in words, point
    assert "Knowing these makes the rest more useful." not in page


# ---- Example 3: the invitation ----

# Ticket 5.8: the invitation is shorter and is the guide's last part. This
# test used to be
# test_the_invitation_is_a_navy_block_straight_after_the_guides_opening.
def test_the_invitation_is_a_navy_strip_at_the_end_of_the_guide(page):
    guide = guide_of(page)
    sections = re.findall(r'(?s)<section[^>]*>.*?</section>', guide[guide.index(">") + 1:])
    assert 'class="intro"' in sections[0]
    invitation = sections[-1]
    assert invitation.startswith('<section class="idea strip"')  # the navy block's own style
    assert re.search(r'<h2[^>]*>%s</h2>' % re.escape(INVITE_HEADING), invitation)
    assert "<p>%s</p>" % INVITE_TEXT in invitation
    assert invitation.index(INVITE_HEADING) < invitation.index(INVITE_TEXT) \
        < invitation.index(MAIL_LINK)
    assert "A medicine for one disease" in sections[1]  # the picture is straight after the opening


# ---- Example 3: the guide's list for doctors ----

def doctors_of(page):
    guide = guide_of(page)
    section = guide[guide.index('id="guide-doctors-title"'):]
    return section[:section.index("</details>")]  # ticket 5.8: a folded part now


# Ticket 5.8: "For doctors" is a folded part, straight after the two boxes.
def test_for_doctors_comes_straight_after_for_everyone(page):
    guide = guide_of(page)
    assert '<summary id="guide-doctors-title">%s</summary>' % DOCTORS in guide
    marks = re.findall(r'<(?:h2|summary) id="([a-z-]+)"', guide)
    assert marks.index("guide-doctors-title") == marks.index("guide-limits-title") + 1


def test_for_doctors_holds_kashishs_points_word_for_word_in_the_same_list_style(page):
    section = doctors_of(page)
    assert section.count('<ul class="limits">') == 1
    items = re.findall(r"(?s)<li>(.*?)</li>", section)
    assert [plain(item) for item in items] == DOCTOR_POINTS
    assert len(items) == 8
    for item, words in zip(items, DOCTOR_POINTS):  # the first sentence is the bold title
        assert plain(re.search(r"<b>(.*?)</b>", item).group(1)) == words.split(". ")[0] + "."


def test_the_last_sentence_is_set_apart_under_the_list(page):
    section = doctors_of(page)
    assert '<p class="not-reference">%s</p>' % LAST_SENTENCE in section
    assert section.index("</ul>") < section.index(LAST_SENTENCE)
    assert page.count(LAST_SENTENCE) == 1


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


# ---- Careful: the mail links are the only new addresses ----

def test_the_page_has_two_mail_links_the_footers_and_the_invitations(page):
    assert page.count("mailto:") == page.count(MAIL_LINK) == 2
    assert MAIL_LINK in footer_of(page) and MAIL_LINK in guide_of(page)
