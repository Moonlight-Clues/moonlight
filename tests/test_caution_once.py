"""Ticket 2.29. The caution sentence once per trial box.

Kashish's decision, 23 Nov:

1. In both folded boxes on the In trials tab, "Never start, stop or change
   any medicine without a doctor." is shown once, at the top of the box,
   under its label.
2. It is taken off the cards inside the boxes.
3. The words do not change.
4. Cards in the main In trials list keep their own ending.
5. The safety line at the top of the page is untouched.

Like a swimming pool: one sign on the wall at the start of the lanes,
not the same sign taped to every swimmer.

Her example here: primary biliary cholangitis (MONDO_0005388). 7 cards in
the list, 26 in the first box, 10 in the second.

Saved files only: fixtures/more_in_trials/, through the helpers of
tests/test_more_in_trials.py. No new saved file. No network.
"""

import copy
import json
import pathlib
import shutil
import subprocess
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from moonlight import api, engine

import test_more_in_trials
from test_more_in_trials import PBC

ROOT = pathlib.Path(__file__).resolve().parent.parent
PAGE_FILE = ROOT / "web" / "index.html"
PAGE = PAGE_FILE.read_text(encoding="utf-8")

# Kashish's words, exactly. Not changed by this ticket.
CAUTION = "Never start, stop or change any medicine without a doctor."
SAFETY_LINE = ("For learning and research exploration, not medical advice. "
               "Never start, stop or change any medicine without a doctor.")
OLD_BOX_LABEL = ("More medicines in trials for this disease. They do not act on one of "
                 "the 25 proteins.")
NEW_BOX_LABEL = ("New medicines being tested for this disease. The database records no "
                 "approval for them for any disease.")
BOXES = [("more-trials-box", "more-trials-cards", OLD_BOX_LABEL),
         ("new-trials-box", "new-trials-cards", NEW_BOX_LABEL)]


# ---- the page, read as text ----

def box_text(box_id):
    start = PAGE.index(f'<details class="wider-box" id="{box_id}" hidden>')
    return PAGE[start:PAGE.index("</details>", start)]


def test_the_words_are_the_engines_words_and_did_not_change():
    assert engine.MORE_IN_TRIALS_ENDING == CAUTION


@pytest.mark.parametrize("box_id, cards_id, label", BOXES)
def test_each_box_holds_the_sentence_once_under_its_label_above_its_cards(box_id, cards_id, label):
    box = box_text(box_id)
    assert box.count(CAUTION) == 1
    assert f'<p class="doctor-line" data-part="caution">{CAUTION}</p>' in box
    assert box.index(label) < box.index("</summary>") < box.index(CAUTION) < box.index(
        f'id="{cards_id}"')


def test_the_safety_line_at_the_top_of_the_page_is_untouched():
    assert PAGE.count(SAFETY_LINE) == 1
    assert PAGE.index(SAFETY_LINE) < PAGE.index('id="panel-trials"')
    assert 'data-slot="safety-line" role="note"' in PAGE


# ---- the page, in a real browser ----

BROWSER_SCRIPT = r"""
"use strict";
const fs = require("fs");
const { chromium } = require("playwright");
const PAGE = fs.readFileSync(process.argv[1], "utf-8");
const ANSWERS = JSON.parse(fs.readFileSync(process.argv[2], "utf-8"));
const SITE = "http://moonlight.test";

function readTrials() {
  const shownOnPage = el => !!el && el.getClientRects().length > 0;
  const words = el => el.innerText.replace(/\s+/g, " ").trim();
  const readCard = card => ({
    name: card.querySelector('[data-slot="medicine-name"]').textContent,
    ending: [...card.querySelectorAll('[data-slot="ending"]')].map(el => el.textContent),
    endingShown: shownOnPage(card.querySelector('[data-slot="ending"]')),
    phaseShown: shownOnPage(card.querySelector('[data-slot="phase"]')),
    sourceShown: shownOnPage(card.querySelector('[data-slot="source"]')),
    words: words(card),
  });
  const readBox = (boxId, cardsId) => {
    const box = document.getElementById(boxId);
    const cautions = [...box.querySelectorAll('[data-part="caution"]')];
    const summary = box.querySelector("summary");
    return {
      shown: shownOnPage(box),
      open: box.open,
      children: [...box.children].map(el => el.getAttribute("data-part") || el.id || el.tagName),
      cautions: cautions.map(el => el.textContent),
      cautionShown: cautions.length === 1 && shownOnPage(cautions[0]),
      cautionIsUnderTheLabel: cautions.length === 1 && shownOnPage(cautions[0])
        && cautions[0].getBoundingClientRect().top >= summary.getBoundingClientRect().bottom - 1,
      cautionIsAboveTheCards: cautions.length === 1 && shownOnPage(cautions[0])
        && cautions[0].getBoundingClientRect().bottom
          <= document.getElementById(cardsId).getBoundingClientRect().top + 1,
      cards: [...document.querySelectorAll("#" + cardsId + " > .card")].map(readCard),
      words: words(box),
    };
  };
  return {
    safetyLine: words(document.querySelector('[data-slot="safety-line"]')),
    safetyLineShown: shownOnPage(document.querySelector('[data-slot="safety-line"]')),
    list: [...document.querySelectorAll("#studied-cards > .card")].map(readCard),
    oldBox: readBox("more-trials-box", "more-trials-cards"),
    newBox: readBox("new-trials-box", "new-trials-cards"),
  };
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
    return route.abort();
  });
  await page.goto(SITE + "/?disease=MONDO_TEST");
  await page.waitForSelector("#found", { state: "visible" });
  await page.click("#tab-trials");
  const out = { errors };
  out.closed = await page.evaluate(readTrials);
  for (const id of ["more-trials-box", "new-trials-box"]) {
    const box = page.locator("#" + id);
    if (await box.isVisible() && !(await box.evaluate(el => el.open))) {
      await page.click("#" + id + " summary");
      await page.waitForTimeout(300);  // the box tells the page it was opened a moment later
    }
  }
  out.tapped = await page.evaluate(readTrials);
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
def answers():
    """Answers of /api/clues: the example, the example with only its
    second box, and the example as it was before ticket 2.21 (no boxes)."""
    api.forget_visitors()
    with patch("moonlight.fetch._post_json", side_effect=test_more_in_trials.saved_post_json):
        example = TestClient(api.app).get("/api/clues", params={"disease_id": PBC.id}).json()
    only_new = copy.deepcopy(example)
    only_new["being_studied"] = []
    del only_new["more_in_trials"]
    return {"example": example, "only_new": only_new,
            "before": test_more_in_trials.load(
                ROOT / "fixtures" / "more_in_trials" / "clues_before_2.21.json")}


@pytest.fixture(scope="module")
def seen(answers, tmp_path_factory):
    """Opens the page once per answer and returns what a reader sees."""
    node = shutil.which("node")
    if not node or subprocess.run(
            [node, "-e", "require('playwright')"], capture_output=True).returncode:
        pytest.skip("needs node with playwright to open a real browser")
    answers_file = tmp_path_factory.mktemp("caution_once") / "answers.json"
    answers_file.write_text(json.dumps(answers), encoding="utf-8")
    run = subprocess.run(
        [node, "-e", BROWSER_SCRIPT, str(PAGE_FILE), str(answers_file)],
        capture_output=True, text=True, timeout=240, cwd=str(ROOT))
    assert run.returncode == 0, run.stderr[-3000:]
    out = json.loads(run.stdout)
    for name in answers:
        assert out[name]["errors"] == [], name
    return out


def test_the_example_has_7_in_the_list_26_and_10_in_the_boxes(answers):
    example = answers["example"]
    assert len(example["being_studied"]) == 7
    assert len(example["more_in_trials"]) == 26
    assert len(example["new_in_trials"]) == 10


@pytest.mark.parametrize("box, count", [("oldBox", 26), ("newBox", 10)])
def test_browser_an_open_box_shows_the_sentence_once_at_its_top(seen, box, count):
    opened = seen["example"]["tapped"][box]
    assert opened["open"] and len(opened["cards"]) == count
    assert opened["cautions"] == [CAUTION]  # her words, exactly, one time
    assert opened["cautionShown"]
    assert opened["cautionIsUnderTheLabel"] and opened["cautionIsAboveTheCards"]
    assert opened["children"][:2] == ["SUMMARY", "caution"]  # the label, then the sentence
    # Once in the whole box, however many cards it holds.
    assert opened["words"].count(CAUTION) == 1
    assert opened["words"].count("without a doctor") == 1


@pytest.mark.parametrize("box, label", [("oldBox", OLD_BOX_LABEL), ("newBox", NEW_BOX_LABEL)])
def test_browser_the_sentence_comes_straight_after_the_label(seen, box, label):
    words = seen["example"]["tapped"][box]["words"]
    assert words.startswith(label)
    assert words.index(label) < words.index("Tap to close") < words.index(CAUTION)
    first_card = seen["example"]["tapped"][box]["cards"][0]["name"]
    assert words.index(CAUTION) < words.index(first_card)


@pytest.mark.parametrize("box", ["oldBox", "newBox"])
def test_browser_no_card_inside_a_box_carries_the_sentence(seen, box):
    for card in seen["example"]["tapped"][box]["cards"]:
        assert card["ending"] == [] and not card["endingShown"]
        assert "doctor" not in card["words"] and "Never" not in card["words"]
        assert card["phaseShown"] and card["sourceShown"]  # the stage and the source stay


def test_browser_one_card_of_each_box_in_full(seen):
    colchicine = seen["example"]["tapped"]["oldBox"]["cards"][2]
    assert colchicine["words"] == "Colchicine Forms: Colchicine Source record Phase 3"
    first_new = seen["example"]["tapped"]["newBox"]["cards"][0]
    assert first_new["words"] == (
        f"{first_new['name']} Forms: {first_new['name']} Source record Phase 3")


def test_browser_a_folded_box_keeps_the_sentence_folded_away_with_its_cards(seen):
    closed = seen["example"]["closed"]
    for box in ("oldBox", "newBox"):
        assert closed[box]["shown"] and not closed[box]["open"]
        assert closed[box]["cautions"] == [CAUTION] and not closed[box]["cautionShown"]


def test_browser_a_box_that_starts_open_shows_the_sentence_straight_away(seen):
    closed = seen["only_new"]["closed"]
    assert not closed["oldBox"]["shown"]
    assert closed["newBox"]["open"]  # it is all there is on the tab
    assert closed["newBox"]["cautionShown"] and closed["newBox"]["cautionIsUnderTheLabel"]


def test_browser_cards_in_the_main_list_keep_their_own_ending(seen):
    cards = seen["example"]["tapped"]["list"]
    assert len(cards) == 7
    for card in cards:
        assert len(card["ending"]) == 1 and card["endingShown"]
        assert card["ending"][0].endswith(CAUTION) and card["ending"][0] != CAUTION
        assert card["words"].count(CAUTION) == 1
    # The same cards, word for word, as before the boxes existed.
    assert cards == seen["before"]["tapped"]["list"]


def test_browser_no_box_means_no_sentence_from_a_box(seen):
    before = seen["before"]["tapped"]
    for box in ("oldBox", "newBox"):
        assert not before[box]["shown"] and not before[box]["cautionShown"]


def test_browser_the_safety_line_at_the_top_is_untouched(seen):
    for name in ("example", "only_new", "before"):
        assert seen[name]["closed"]["safetyLineShown"]
        assert seen[name]["closed"]["safetyLine"] == SAFETY_LINE
