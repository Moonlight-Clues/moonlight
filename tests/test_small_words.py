"""Ticket 5.6. Small words.

Kashish's decisions, 16 Nov.
1. An Approved tab with nothing in it at all says a new, more careful sentence.
2. The guide has one name everywhere: "How to use Moonlight".
3. On a phone the search's first words do not touch the safety line.
   The safety line itself does not change.

The page is read from GET / and from web/index.html. Saved files only
(fixtures/family/). No network.
"""

import pathlib
import re
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from moonlight import api, explain
from moonlight.engine import sort_into_tabs
from moonlight.filter import sort_paths

from test_family import PRE_B_ALL, family_post_json, made_up_path, searching

ROOT = pathlib.Path(__file__).resolve().parent.parent

NEW_EMPTY = (
    "The database lists no approved medicine under this exact name. That "
    "does not mean there is none. Ask a doctor."
)
OLD_EMPTY = "The database lists no medicine approved for this disease."
SAFETY_LINE = (
    "For learning and research exploration, not medical advice. "
    "Never start, stop or change any medicine without a doctor."
)
# The page's rule: the sentence is hidden when the tab has anything in it.
EMPTY_RULE = 'byId("approved-empty").hidden = !!approvedCards.length || !!widerCards.length || !!narrowerCards.length;'


@pytest.fixture(autouse=True)
def offline():
    """Saved files instead of Open Targets. Real HTTP is an error."""
    explain.forget_everything()
    with patch("moonlight.fetch._post_json", side_effect=family_post_json), \
            patch("requests.request", side_effect=AssertionError("network used")), \
            patch("requests.post", side_effect=AssertionError("network used")), \
            patch("requests.get", side_effect=AssertionError("network used")), \
            patch("requests.sessions.Session.request",
                  side_effect=AssertionError("network used")):
        yield
    explain.forget_everything()


@pytest.fixture
def client():
    return TestClient(api.app)


@pytest.fixture
def page(client):
    return client.get("/").text


def plain(html):
    """The words a reader sees: tags taken out, spaces tidied."""
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html)).strip()


def empty_box_of(page):
    """The box the Approved tab shows when it has nothing in it."""
    return re.search(r'(?s)<div [^>]*id="approved-empty"[^>]*>.*?</div>', page).group(0)


def sentence_is_shown(approved, wider_group):
    """The page's rule, worked by hand: shown only when both are empty."""
    return not approved and not wider_group


# ---- Example 1: the empty Approved tab ----

def test_the_empty_approved_tab_holds_the_new_sentence_exactly(page):
    assert plain(empty_box_of(page)) == NEW_EMPTY


def test_the_old_empty_sentence_is_nowhere_on_the_page(page):
    assert OLD_EMPTY not in page
    assert page.count(NEW_EMPTY) == 1


def test_the_new_sentence_stays_hidden_until_the_tab_is_empty(page):
    tag = re.search(r'<div [^>]*id="approved-empty"[^>]*>', page).group(0)
    assert " hidden" in tag
    assert EMPTY_RULE in page


def test_a_disease_with_nothing_approved_shows_the_new_sentence_and_not_the_old(page):
    tabs = sort_into_tabs(sort_paths([made_up_path("CLUEMIL")]), [])
    assert tabs.approved == [] and tabs.wider_group == []
    assert sentence_is_shown(tabs.approved, tabs.wider_group)
    assert NEW_EMPTY in plain(empty_box_of(page))
    assert OLD_EMPTY not in page


def test_pre_b_all_whose_box_has_15_shows_neither_sentence(client, page):
    with searching(PRE_B_ALL):
        answer = client.get("/api/clues", params={"disease_id": PRE_B_ALL.id})
    assert answer.status_code == 200
    data = answer.json()
    assert [item["id"] for item in data["approved"]] == ["CHEMBL941"] and len(data["wider_group"]) == 15  # ticket 2.64: imatinib was []
    # The new sentence lives only in the box the rule keeps hidden here,
    # the old one is gone, and the API sends neither.
    assert not sentence_is_shown(data["approved"], data["wider_group"])
    assert EMPTY_RULE in page
    assert page.count(NEW_EMPTY) == 1 and NEW_EMPTY in plain(empty_box_of(page))
    assert OLD_EMPTY not in page
    assert NEW_EMPTY not in answer.text and OLD_EMPTY not in answer.text


# ---- Example 2: one name for the guide ----

def test_the_page_says_how_to_use_moonlight_and_never_how_to_read_moonlight(page):
    assert "How to use Moonlight" in page
    assert "How to read Moonlight" not in page


def test_the_line_near_the_search_box_has_the_new_words(page):
    home = page[page.index('<section id="home"'):page.index('<section id="results"')]
    assert "New here? How to use Moonlight." in plain(home)
    assert re.search(
        r'New here\? <a [^>]*href="#guide"[^>]*data-guide[^>]*>How to use Moonlight\.</a>', home)


def test_how_to_read_a_card_stays_as_it_is(page):
    assert re.search(r'<a [^>]*href="#guide-card"[^>]*data-guide[^>]*>How to read a card</a>', page)


# ---- Example 3: the safety line, and the space below it ----

def test_the_safety_lines_words_are_exactly_as_before(page):
    start = page.index('data-slot="safety-line"')
    line = page[page.rindex("<", 0, start):page.index("<main")]
    assert plain(line) == SAFETY_LINE
    assert page.count(SAFETY_LINE) == 1
    assert SAFETY_LINE in re.sub(r"\s+", " ", (ROOT / "CLAUDE.md").read_text(encoding="utf-8"))


def test_the_safety_lines_own_styles_are_as_before(page):
    for rule in (
        ".safety{position:sticky;top:0;z-index:10;background:#203448;color:white;"
        "border-bottom:1px solid #5F9E9B}",
        ".safety-inner{display:flex;align-items:flex-start;gap:10px;padding:11px 0;"
        "font-size:12px;line-height:1.45;color:#F4F0E9}",
        ".safety svg{flex:none;margin-top:1px}",
        ".safety-inner{padding:9px 0;font-size:11px}",
    ):
        assert rule in page, rule


def test_the_search_stops_below_the_pinned_safety_line_when_the_page_jumps_to_it(page):
    """The safety line is pinned to the top. When the page jumps back to the
    search, the search must stop a little below it, not underneath it."""
    rule = re.search(r"\.search-area\{[^}]*\}", page).group(0)
    space = re.search(r"scroll-margin-top:(\d+)px", rule)
    assert space, rule
    # On a narrow phone the safety line is three lines tall, about 67px.
    assert int(space.group(1)) >= 80
