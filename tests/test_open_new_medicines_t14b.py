"""Ticket T14b. Open "New medicines being tested".

The box starts open. The first 20 cards are on screen, in the order the
answer already has. The rest stay in the page, hidden, until a button that
reads "Show all [N]". One click shows every card and the button goes away.
A box of 20 or fewer has no button. The number in the summary stays the
full count.

Pulmonary arterial hypertension, from the saved answer of ticket 2.52:
27 medicines in the box, so the button reads "Show all 27".

"More medicines in trials" is not changed. No network.
"""

import copy
import json
import pathlib
import shutil
import subprocess

import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent
PAGE_FILE = ROOT / "web" / "index.html"
PAH_FILE = ROOT / "fixtures" / "labels_read" / "2.52" / "page_answers" / "MONDO_0015924.clues.json"
PAH = json.loads(PAH_FILE.read_text(encoding="utf-8"))
PAH_NAMES = [card["medicine"] for card in PAH["new_in_trials"]]
FIRST = 20
LABEL = ("New medicines being tested for this disease. The database records no "
         "approval for them for any disease.")

BROWSER_SCRIPT = r"""
"use strict";
const fs = require("fs");
const { chromium } = require("playwright");
const PAGE = fs.readFileSync(process.argv[1], "utf-8");
const ANSWERS = JSON.parse(fs.readFileSync(process.argv[2], "utf-8"));
const SITE = "http://moonlight.test";

function readBox() {
  const box = document.getElementById("new-trials-box");
  const cards = [...document.querySelectorAll("#new-trials-cards > .card")];
  const button = document.getElementById("new-trials-show-all");
  const older = document.getElementById("more-trials-box");
  const count = document.getElementById("new-trials-count").textContent;
  return {
    open: box.open,
    shown: box.getClientRects().length > 0,
    count,
    summary: box.querySelector("summary").innerText.replace(/\s+/g, " ").trim(),
    summaryHasFullCount: box.querySelector("summary").innerText.includes("(" + count + ")"),
    names: cards.map(card => card.querySelector('[data-slot="medicine-name"]').textContent),
    onScreen: cards.map(card => card.checkVisibility()),
    showAll: button ? button.textContent : null,
    showAllTag: button ? button.tagName : null,
    showAllHeight: button ? Math.round(button.getBoundingClientRect().height) : null,
    buttonAfterCards: button
      ? !!(document.getElementById("new-trials-cards").compareDocumentPosition(button)
        & Node.DOCUMENT_POSITION_FOLLOWING) : null,
    moreOpen: older.open,
    moreShown: older.getClientRects().length > 0,
    moreShowAll: (document.getElementById("more-trials-show-all") || {}).textContent || null,
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
  await page.goto(SITE + "/?disease=" + answer.disease.id);
  await page.waitForSelector("#found", { state: "visible" });
  await page.click("#tab-trials");
  const out = { errors };
  out.open = await page.evaluate(readBox);
  if (out.open.showAll) {
    await page.click("#new-trials-box summary");
    await page.waitForTimeout(300);
    out.folded = await page.evaluate(readBox);
    await page.click("#new-trials-box summary");
    await page.waitForTimeout(300);
    out.reopened = await page.evaluate(readBox);
    await page.click("#new-trials-show-all");
    out.shown = await page.evaluate(readBox);
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


def answers():
    """The saved PAH page, and the same page cut to 20 cards and to 5."""
    twenty = copy.deepcopy(PAH)
    twenty["new_in_trials"] = twenty["new_in_trials"][:FIRST]
    five = copy.deepcopy(PAH)
    five["new_in_trials"] = five["new_in_trials"][:5]
    return {"pah": PAH, "twenty": twenty, "five": five}


@pytest.fixture(scope="module")
def seen(tmp_path_factory):
    """Opens each answer and returns what a reader sees in the box."""
    node = shutil.which("node")
    if not node or subprocess.run(
            [node, "-e", "require('playwright')"], capture_output=True).returncode:
        pytest.skip("needs node with playwright to open a real browser")
    answers_file = tmp_path_factory.mktemp("open_new") / "answers.json"
    answers_file.write_text(json.dumps(answers()), encoding="utf-8")
    run = subprocess.run(
        [node, "-e", BROWSER_SCRIPT, str(PAGE_FILE), str(answers_file)],
        capture_output=True, text=True, timeout=180, cwd=str(ROOT))
    assert run.returncode == 0, run.stderr[-3000:]
    out = json.loads(run.stdout)
    for name in ("pah", "twenty", "five"):
        assert out[name]["errors"] == [], name
    return out


def test_the_saved_pah_answer_holds_27():
    assert len(PAH_NAMES) == 27
    assert len(PAH["being_studied"]) > 0 and len(PAH["more_in_trials"]) > 0


def test_pah_starts_open_with_the_first_20_and_show_all_27(seen):
    opened = seen["pah"]["open"]
    assert opened["shown"] and opened["open"]
    assert opened["count"] == "27"
    assert opened["summaryHasFullCount"] is True
    assert opened["summary"].endswith("(27) Tap to close")
    assert opened["names"] == PAH_NAMES  # every card stays in the page, in the same order
    assert opened["onScreen"] == [True] * FIRST + [False] * (27 - FIRST)
    assert opened["showAll"] == "Show all 27"
    assert opened["showAllTag"] == "BUTTON"
    assert opened["showAllHeight"] >= 44
    assert opened["buttonAfterCards"] is True
    # The other box on this tab is unchanged: still open, with its own Show all.
    assert opened["moreShown"] and opened["moreOpen"] is True
    assert opened["moreShowAll"] == "Show all 48"


def test_pah_the_summary_still_folds_the_box_and_reopening_keeps_the_first_20(seen):
    assert seen["pah"]["folded"]["open"] is False
    assert seen["pah"]["folded"]["onScreen"] == [False] * 27
    assert seen["pah"]["folded"]["count"] == "27"  # the summary keeps the full count
    again = seen["pah"]["reopened"]
    assert again["open"] is True
    assert again["onScreen"] == [True] * FIRST + [False] * (27 - FIRST)
    assert again["showAll"] == "Show all 27"
    assert again["count"] == "27"


def test_pah_show_all_27_shows_every_card_and_the_button_goes_away(seen):
    shown = seen["pah"]["shown"]
    assert shown["open"] is True
    assert shown["names"] == PAH_NAMES
    assert shown["onScreen"] == [True] * 27
    assert shown["showAll"] is None
    assert shown["count"] == "27"


def test_a_box_of_20_shows_every_card_and_has_no_button(seen):
    opened = seen["twenty"]["open"]
    assert "shown" not in seen["twenty"]
    assert opened["open"] is True and opened["count"] == "20"
    assert opened["summaryHasFullCount"] is True
    assert opened["summary"].endswith("(20) Tap to close")
    assert opened["names"] == PAH_NAMES[:FIRST]
    assert opened["onScreen"] == [True] * FIRST
    assert opened["showAll"] is None


def test_a_box_of_fewer_than_20_shows_every_card_and_has_no_button(seen):
    opened = seen["five"]["open"]
    assert "shown" not in seen["five"]
    assert opened["open"] is True and opened["count"] == "5"
    assert opened["summaryHasFullCount"] is True
    assert opened["summary"].endswith("(5) Tap to close")
    assert opened["names"] == PAH_NAMES[:5]
    assert opened["onScreen"] == [True] * 5
    assert opened["showAll"] is None
