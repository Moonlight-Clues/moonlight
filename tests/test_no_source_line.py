"""Ticket 2.23. The line on a card with no source link.

Kashish's decision:

- A card with no source link STAYS on the page.
- It says, her words exactly:
  "The database gives no source link for this medicine."
- On every tab and in every box.
- A card with a source link never shows that sentence.

THE EIGHT PLACES A CARD CAN BE
  Approved tab:   the main list, the narrower-disease box, the wider-group box
  In trials tab:  the list, the "More medicines in trials" box (ticket 2.21),
                  the "new medicines in trials" box (ticket 2.24)
  New clues tab:  the list, and the opposite-way box under it (ticket 2.28)

The eighth place came with ticket 2.28, after these tests were first
written. The API still sends every new clue in "new_clues", and names the
ones that sit in the opposite-way box in "opposite_way_box" (their ids).
The page puts those in the box and the rest in the list. So here
"new_clues" means the list above the box, and "opposite_way_box" means the
cards inside it. Together they are every new clue.

THE EXAMPLES
1. Asthma (MONDO_0004979), from the saved answers in fixtures/narrower_box/.
   Nothing is changed in it. Five of its 126 new clues have no source link
   in the data: Dyphylline, Amlexanox, Crisaborole, Drotaverine, Flavoxate.
   All five are in the list (100 cards). None is in the box (26 cards).
2. Acute lymphoblastic leukemia (MONDO_0004967), from the same folder. It
   has cards in all eight places, and every one has a source link. No saved
   answer on main has a card with no link outside the New clues list, so for this
   test only, the FIRST card of each place is handed to the page with its
   link taken away. The test says so wherever it does this.

NOT TESTED HERE: the print page reads its words from the card, so it says
the sentence too; tests/test_snapshot_page.py checks that. cli.py keeps its
old words for now.

Tests never touch the network: Open Targets is replaced by saved files, and
the browser is only given the page and the answer.
"""
import copy
import json
import pathlib
import shutil
import subprocess
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from moonlight import api

# Ticket 2.62 (delete the asthma rows there and `moved` is 0).
from test_red_warnings_2_62 import RED_ROWS, page as page_2_62  # noqa: E402

import test_narrower_box
from test_narrower_box import saved_post_json

ROOT = pathlib.Path(__file__).resolve().parent.parent
PAGE_FILE = ROOT / "web" / "index.html"
PAGE = PAGE_FILE.read_text(encoding="utf-8")

# Kashish's words, exactly.
SENTENCE = "The database gives no source link for this medicine."
# The words the card has today. The card must not say both.
OLD_WORDS = "No source link in the data"
LINK_WORDS = "Source record"

ASTHMA = "MONDO_0004979"
LEUKEMIA = "MONDO_0004967"  # acute lymphoblastic leukemia

ASTHMA_NO_LINK = ["Dyphylline", "Amlexanox", "Crisaborole", "Drotaverine", "Flavoxate"]

# The eight places, by the name each has in the answer of /api/clues.
PLACES = ["approved", "narrower", "wider_group",
          "being_studied", "more_in_trials", "new_in_trials", "new_clues",
          "opposite_way_box"]
# How many cards acute lymphoblastic leukemia has in each place.
# Its 21 new clues are 20 in the list and 1 in the opposite-way box.
# Ticket 2.45 put red warnings on two of its 15 saved approved cards. They sit
# in the red-warning box, not the main list.
LEUKEMIA_CARDS = {"approved": 13, "narrower": 13, "wider_group": 12,
                  "being_studied": 16, "more_in_trials": 150, "new_in_trials": 80,
                  "new_clues": 20, "opposite_way_box": 1}


def cards_in(answer, place):
    """The cards the page puts in one place, in the page's order.

    The answer names the clues of the opposite-way box by id. Those go in
    the box. The other new clues stay in the list above it.
    """
    boxed = set(answer.get("opposite_way_box") or [])
    if place == "new_clues":
        return [clue for clue in answer["new_clues"] if clue["id"] not in boxed]
    if place == "opposite_way_box":
        return [clue for clue in answer["new_clues"] if clue["id"] in boxed]
    if place == "approved":  # ticket 2.45: the main list, without the red-warning box's cards
        red = set(answer.get("wrong_approvals_box") or [])
        return [card for card in answer.get("approved", []) if card["id"] not in red]
    return answer.get(place, [])


@pytest.fixture(autouse=True)
def offline():
    """Real HTTP is an error."""
    with patch("requests.request", side_effect=AssertionError("network used")), \
            patch("requests.post", side_effect=AssertionError("network used")), \
            patch("requests.get", side_effect=AssertionError("network used")), \
            patch("requests.sessions.Session.request",
                  side_effect=AssertionError("network used")):
        yield


def clues_of(disease_id):
    """The answer of /api/clues, from the saved Open Targets answers."""
    api.forget_visitors()
    with patch("moonlight.fetch._post_json", side_effect=saved_post_json):
        reply = TestClient(api.app).get("/api/clues", params={"disease_id": disease_id})
    assert reply.status_code == 200
    return reply.json()


@pytest.fixture(scope="module")
def answers():
    """Two answers of /api/clues for the page.

    "asthma" is the saved answer, untouched.
    "every_place" is acute lymphoblastic leukemia with the link of the
    first card in each of the eight places taken away, for this test only.
    """
    with patch("requests.request", side_effect=AssertionError("network used")), \
            patch("requests.sessions.Session.request",
                  side_effect=AssertionError("network used")):
        asthma = clues_of(ASTHMA)
        leukemia = clues_of(LEUKEMIA)
    every_place = copy.deepcopy(leukemia)
    for place in PLACES:
        assert cards_in(leukemia, place)[0]["source"], place  # it had a link in the data
        cards_in(every_place, place)[0]["source"] = None
    return {"asthma": asthma, "every_place": every_place}


# ---- the card stays: the answer of /api/clues ----

def test_the_five_asthma_clues_with_no_link_stay_in_the_answer(answers):
    """EXAMPLE 1. Nothing is left out because its link is missing."""
    new_clues = answers["asthma"]["new_clues"]
    assert len(new_clues) == 126
    assert [clue["medicine"] for clue in new_clues if clue["source"] is None] == ASTHMA_NO_LINK


def test_no_other_asthma_card_is_without_a_link(answers):
    asthma = answers["asthma"]
    for place in PLACES:
        if place != "new_clues":
            assert all(card["source"] for card in cards_in(asthma, place)), place


def test_leukemia_has_cards_in_all_eight_places(answers):
    """EXAMPLE 2 is the right size before any link is taken away."""
    every_place = answers["every_place"]
    assert len(every_place["new_clues"]) == 21  # the list and the box together
    assert {place: len(cards_in(every_place, place)) for place in PLACES} == LEUKEMIA_CARDS
    for place in PLACES:
        cards = cards_in(every_place, place)
        without = [card for card in cards if not card["source"]]
        assert without == [cards[0]], place  # only the one this test changed


# ---- the page, read as text ----

def test_the_page_holds_kashishs_sentence_once_in_the_card():
    """One card template makes every card, so the sentence lives there, once."""
    assert PAGE.count(SENTENCE) == 1
    template = PAGE[PAGE.index('<template id="card-template">'):]
    template = template[:template.index("</template>")]
    assert f'data-part="no-source" hidden>{SENTENCE}</span>' in template
    assert OLD_WORDS not in template


def test_the_safety_line_and_the_link_words_are_not_changed():
    assert ("For learning and research exploration, not medical advice. Never start, stop or "
            "change any medicine without a doctor.") in PAGE
    assert f'data-slot="source" hidden>{LINK_WORDS}</a>' in PAGE


# ---- the page, in a real browser ----

BROWSER_SCRIPT = r"""
"use strict";
const fs = require("fs");
const { chromium } = require("playwright");
const PAGE = fs.readFileSync(process.argv[1], "utf-8");
const ANSWERS = JSON.parse(fs.readFileSync(process.argv[2], "utf-8"));
const SENTENCE = process.argv[3], OLD_WORDS = process.argv[4];
const SITE = "http://moonlight.test";

// Each place: its name in the answer, its tab, its cards, the box to open first (if any).
const PLACES = [
  ["approved", "tab-approved", "approved-cards", null],
  ["narrower", "tab-approved", "narrower-cards", "narrower-box"],
  ["wider_group", "tab-approved", "wider-cards", "wider-box"],
  ["being_studied", "tab-trials", "studied-cards", null],
  ["more_in_trials", "tab-trials", "more-trials-cards", "more-trials-box"],
  ["new_in_trials", "tab-trials", "new-trials-cards", "new-trials-box"],
  ["new_clues", "tab-clues", "new-cards", null],
  ["opposite_way_box", "tab-clues", "opposite-cards", "opposite-box"],
];

// What a reader sees on each card of one place. Read while the place is open.
function readCards([cardsId, sentence, oldWords]) {
  const count = (words, piece) => words.split(piece).length - 1;
  return [...document.querySelectorAll("#" + cardsId + " > .card")].map(card => {
    const words = card.innerText.replace(/\s+/g, " ").trim();  // only what is on screen
    const links = [...card.querySelectorAll("a")].filter(a => a.checkVisibility());
    return {
      name: card.querySelector('[data-slot="medicine-name"]').textContent,
      onScreen: card.checkVisibility(),
      sentences: count(words, sentence),
      oldWords: count(words, oldWords),
      linksShown: links.length,
      linkWords: links.map(a => a.innerText.trim()),
      link: links.length ? links[0].href : null,
    };
  });
}

async function oneSearch(browser, answer) {
  const context = await browser.newContext({ viewport: { width: 390, height: 844 } });
  const page = await context.newPage();
  const errors = [];
  page.on("pageerror", problem => errors.push(String(problem)));
  await context.route("**/*", route => {
    const url = route.request().url();
    if (url === SITE + "/" || url.startsWith(SITE + "/?"))
      return route.fulfill({ contentType: "text/html; charset=utf-8", body: PAGE });
    if (url.startsWith(SITE + "/api/clues?"))
      return route.fulfill({ contentType: "application/json", body: JSON.stringify(answer) });
    if (url.startsWith(SITE + "/api/explain?"))
      return route.fulfill({ status: 404, contentType: "application/json", body: "{}" });
    return route.abort();  // anything else never leaves the test
  });
  await page.goto(SITE + "/?disease=MONDO_TEST");
  await page.waitForSelector("#found", { state: "visible" });
  const out = { errors, places: {} };
  for (const [name, tab, cardsId, box] of PLACES) {
    await page.click("#" + tab);
    if (box && await page.evaluate(id => {
      const el = document.getElementById(id);
      return !el.hidden && !el.open;
    }, box)) {
      await page.click("#" + box + " summary");
      await page.waitForTimeout(300);
    }
    out.places[name] = await page.evaluate(readCards, [cardsId, SENTENCE, OLD_WORDS]);
  }
  await context.close();
  return out;
}

(async () => {
  const browser = await chromium.launch();
  const out = {};
  for (const name of Object.keys(ANSWERS)) out[name] = await oneSearch(browser, ANSWERS[name]);
  await browser.close();
  console.log(JSON.stringify(out));
})().catch(problem => { console.error(problem); process.exit(1); });
"""


@pytest.fixture(scope="module")
def seen(answers, tmp_path_factory):
    """Opens the page once per answer and returns what a reader sees on every card."""
    node = shutil.which("node")
    if not node or subprocess.run(
            [node, "-e", "require('playwright')"], capture_output=True).returncode:
        pytest.skip("needs node with playwright to open a real browser")
    answers_file = tmp_path_factory.mktemp("no_source_line") / "answers.json"
    answers_file.write_text(json.dumps(answers), encoding="utf-8")
    run = subprocess.run(
        [node, "-e", BROWSER_SCRIPT, str(PAGE_FILE), str(answers_file), SENTENCE, OLD_WORDS],
        capture_output=True, text=True, timeout=300, cwd=str(ROOT))
    assert run.returncode == 0, run.stderr[-3000:]
    out = json.loads(run.stdout)
    for name in answers:
        assert out[name]["errors"] == [], name
    return out


def test_browser_every_card_of_the_answer_is_on_the_page(seen, answers):
    """A card with no link STAYS: no place loses a card."""
    for name in ("asthma", "every_place"):
        for place in PLACES:
            cards = seen[name]["places"][place]
            assert [card["name"] for card in cards] == [
                card["medicine"] for card in cards_in(answers[name], place)], (name, place)
            assert all(card["onScreen"] for card in cards), (name, place)


def asthma_clues_that_left_the_box():
    """Ticket 2.62: asthma new clues whose opposite-way line the signed rows removed."""
    from test_red_warnings_2_62 import opposite_ids
    old, new = page_2_62("MONDO_0004979", signed=False), page_2_62("MONDO_0004979")
    return opposite_ids(old["new_clues"]) - opposite_ids(new["new_clues"])


def test_browser_the_five_asthma_clues_say_kashishs_sentence(seen):
    """EXAMPLE 1, untouched data. All five are in the list above the box."""
    places = seen["asthma"]["places"]
    # Ticket 2.62: red medicines no longer set the direction, so some clues leave the box
    # for the list (the total stays 126). `moved` counts them from the saved answers.
    moved = len(asthma_clues_that_left_the_box())
    assert len(places["new_clues"]) == 100 + moved and len(places["opposite_way_box"]) == 26 - moved
    cards = {card["name"]: card
             for place in ("new_clues", "opposite_way_box") for card in places[place]}
    assert len(cards) == 126  # every new clue, list and box together
    for name in ASTHMA_NO_LINK:
        assert cards[name]["sentences"] == 1, name
        assert cards[name]["linksShown"] == 0, name
    assert [name for name, card in cards.items() if card["sentences"]] == ASTHMA_NO_LINK


@pytest.mark.parametrize("place", PLACES)
def test_browser_a_card_with_no_link_says_the_sentence_in_every_place(seen, place):
    """EXAMPLE 2. The first card of the place was handed over with no link."""
    first = seen["every_place"]["places"][place][0]
    assert first["onScreen"]
    assert first["sentences"] == 1  # said once, and on screen
    assert first["linksShown"] == 0  # there is no link to show


@pytest.mark.parametrize("place", PLACES)
def test_browser_a_card_with_a_link_never_says_the_sentence(seen, answers, place):
    """Every other card of the place has a link: it shows the link, never the sentence."""
    cards = seen["every_place"]["places"][place][1:]
    handed = cards_in(answers["every_place"], place)[1:]
    assert len(cards) == LEUKEMIA_CARDS[place] - 1
    for card, medicine in zip(cards, handed):
        assert card["sentences"] == 0, (place, card["name"])
        assert card["linkWords"] == [LINK_WORDS], (place, card["name"])
        assert card["link"] == medicine["source"], (place, card["name"])


def test_browser_no_asthma_card_with_a_link_says_the_sentence(seen):
    for place in PLACES:
        for card in seen["asthma"]["places"][place]:
            if card["name"] not in ASTHMA_NO_LINK:
                assert card["sentences"] == 0 and card["linkWords"] == [LINK_WORDS], (
                    place, card["name"])


def test_browser_no_card_says_the_old_words(seen):
    """A card says Kashish's sentence instead of the old words, not as well as."""
    for name in ("asthma", "every_place"):
        for place in PLACES:
            for card in seen[name]["places"][place]:
                assert card["oldWords"] == 0, (name, place, card["name"])
