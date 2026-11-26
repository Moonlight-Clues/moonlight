"""Ticket 2.67. "No study found" line and long names (sheet W6, 26 Nov).

1. An In trials card with no study or record link says, Kashish's words exactly,
   "No study of this disease was found for this medicine." in place of the link.
2. Card titles: a long word breaks only with a hyphen (lang="en", hyphens: auto),
   never as "Dexbrompheniramin / e".

The three In trials places: the list (being_studied), "More medicines in trials"
(more_in_trials) and "New medicines being tested" (new_in_trials). A card on
Approved or New clues keeps the ticket-2.23 sentence.

Saved answers only (pulmonary arterial hypertension, fixtures/). The first card of
each place is handed to the page with its link taken away, for this test only.
No network.
"""
import copy
import json
import pathlib
import re
import shutil
import subprocess
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from moonlight import api

import test_narrower_box as saved_pages

ROOT = pathlib.Path(__file__).resolve().parent.parent
PAGE_FILE = ROOT / "web" / "index.html"
PAGE = PAGE_FILE.read_text(encoding="utf-8")

NO_STUDY = "No study of this disease was found for this medicine."
NO_SOURCE = "The database gives no source link for this medicine."  # ticket 2.23, other tabs
LINK_WORDS = "Source record"
LONG_NAME = "Dexbrompheniramine"

TRIAL_PLACES = [("being_studied", "tab-trials", "studied-cards", None),
                ("more_in_trials", "tab-trials", "more-trials-cards", "more-trials-box"),
                ("new_in_trials", "tab-trials", "new-trials-cards", "new-trials-box")]
OTHER_PLACES = [("new_clues", "tab-clues", "new-cards", None),
                ("approved", "tab-approved", "approved-cards", None)]


# ---- the page, read as text ----

def template():
    text = PAGE[PAGE.index('<template id="card-template">'):]
    return text[:text.index("</template>")]


def test_the_page_holds_the_no_study_sentence_once_in_the_card_template():
    assert PAGE.count(NO_STUDY) == 1
    assert f'data-part="no-study" hidden>{NO_STUDY}</span>' in template()


def test_the_2_23_sentence_and_the_link_words_are_not_changed():
    assert PAGE.count(NO_SOURCE) == 1
    assert f'data-part="no-source" hidden>{NO_SOURCE}</span>' in template()
    assert f'data-slot="source" hidden>{LINK_WORDS}</a>' in template()


def test_the_page_is_english_and_card_titles_hyphenate_without_breaking_anywhere():
    assert re.search(r"<html[^>]*\blang=\"en\"", PAGE)
    rule = re.search(r"\.card h3\{([^}]*)\}", PAGE).group(1)
    assert "hyphens:auto" in rule
    assert "anywhere" not in rule and "break-all" not in rule


# ---- the page, in a real browser ----

@pytest.fixture(scope="module")
def answers():
    api.forget_visitors()
    with patch("moonlight.fetch._post_json", side_effect=saved_pages.saved_post_json):
        base = saved_pages.clues_json(TestClient(api.app), saved_pages.PAH)
    nolink = copy.deepcopy(base)
    for place, *_ in TRIAL_PLACES:
        assert nolink[place][0]["source"], place  # it has a link today
        nolink[place][0]["source"] = None
    nolink["new_clues"][0]["source"] = None
    nolink["approved"][0]["source"] = None
    long_name = copy.deepcopy(base)
    for place, *_ in TRIAL_PLACES:
        long_name[place][0]["medicine"] = LONG_NAME
        long_name[place][0]["forms"] = [LONG_NAME]
    return {"base": base, "nolink": nolink, "long": long_name}


BROWSER_SCRIPT = r"""
"use strict";
const fs = require("fs");
const { chromium } = require("playwright");
const PAGE = fs.readFileSync(process.argv[1], "utf-8");
const ANSWERS = JSON.parse(fs.readFileSync(process.argv[2], "utf-8"));
const PLACES = JSON.parse(process.argv[3]);
const SHOTS = process.argv[4];
const SITE = "http://moonlight.test";

function readCards([cardsId, noStudy, noSource]) {
  const count = (words, piece) => words.split(piece).length - 1;
  return [...document.querySelectorAll("#" + cardsId + " > .card")].map(card => {
    const words = card.innerText.replace(/\s+/g, " ").trim();
    const links = [...card.querySelectorAll("a")].filter(a => a.checkVisibility());
    const title = card.querySelector('[data-slot="medicine-name"]');
    const range = document.createRange();
    range.selectNodeContents(title);
    const tops = new Set([...range.getClientRects()].map(r => Math.round(r.top)));
    const style = getComputedStyle(title);
    return {
      name: title.textContent,
      noStudy: count(words, noStudy),
      noSource: count(words, noSource),
      linkWords: links.map(a => a.innerText.trim()),
      link: links.length ? links[0].href : null,
      titleLines: tops.size,
      titleOverflows: title.scrollWidth > title.clientWidth,
      hyphens: style.hyphens,
      overflowWrap: style.overflowWrap,
      wordBreak: style.wordBreak,
      lang: document.documentElement.lang,
      sideways: document.documentElement.scrollWidth > document.documentElement.clientWidth,
    };
  });
}

async function oneSearch(browser, name, answer) {
  const context = await browser.newContext({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2 });
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
  const out = { errors, places: {} };
  for (const [place, tab, cardsId, box] of PLACES) {
    await page.click("#" + tab);
    if (box && await page.evaluate(id => { const el = document.getElementById(id); return !el.hidden && !el.open; }, box)) {
      await page.click("#" + box + " summary");
      await page.waitForTimeout(300);
    }
    out.places[place] = await page.evaluate(readCards, [cardsId, process.argv[5], process.argv[6]]);
    if (SHOTS && (name === "nolink" || name === "long") && place !== "approved" && place !== "new_clues")
      await page.locator("#" + cardsId + " > .card").first().screenshot({ path: SHOTS + "/" + name + "_" + place + ".png" });
  }
  await context.close();
  return out;
}

(async () => {
  const browser = await chromium.launch();
  const out = {};
  for (const name of Object.keys(ANSWERS)) out[name] = await oneSearch(browser, name, ANSWERS[name]);
  await browser.close();
  console.log(JSON.stringify(out));
})().catch(problem => { console.error(problem); process.exit(1); });
"""


@pytest.fixture(scope="module")
def seen(answers, tmp_path_factory):
    node = shutil.which("node")
    if not node or subprocess.run(
            [node, "-e", "require('playwright')"], capture_output=True).returncode:
        pytest.skip("needs node with playwright to open a real browser")
    folder = tmp_path_factory.mktemp("no_study")
    answers_file = folder / "answers.json"
    answers_file.write_text(json.dumps(answers), encoding="utf-8")
    shots = ""  # set MOONLIGHT_SHOTS to a folder to keep the 390 px pictures
    import os
    shots = os.environ.get("MOONLIGHT_SHOTS", "")
    run = subprocess.run(
        [node, "-e", BROWSER_SCRIPT, str(PAGE_FILE), str(answers_file),
         json.dumps(TRIAL_PLACES + OTHER_PLACES), shots, NO_STUDY, NO_SOURCE],
        capture_output=True, text=True, timeout=300, cwd=str(ROOT))
    assert run.returncode == 0, run.stderr[-3000:]
    out = json.loads(run.stdout)
    for name in answers:
        assert out[name]["errors"] == [], name
    return out


@pytest.mark.parametrize("place", [p[0] for p in TRIAL_PLACES])
def test_browser_an_in_trials_card_with_no_link_says_no_study_found_in_place_of_the_link(seen, place):
    first = seen["nolink"]["places"][place][0]
    assert first["noStudy"] == 1
    assert first["noSource"] == 0  # instead of the 2.23 sentence, not as well as it
    assert first["linkWords"] == []  # no link to show


@pytest.mark.parametrize("place", [p[0] for p in TRIAL_PLACES])
def test_browser_an_in_trials_card_with_a_link_keeps_its_link_and_never_says_no_study(
        seen, answers, place):
    """STOP AND ASK guard: no trial card that has a link today loses it."""
    for name in ("base", "nolink"):
        handed = answers[name][place]
        cards = seen[name]["places"][place]
        assert len(cards) == len(handed)
        for card, medicine in list(zip(cards, handed))[(1 if name == "nolink" else 0):]:
            assert card["noStudy"] == 0 and card["noSource"] == 0, (name, place, card["name"])
            assert card["linkWords"] == [LINK_WORDS], (name, place, card["name"])
            assert card["link"] == medicine["source"], (name, place, card["name"])


@pytest.mark.parametrize("place", [p[0] for p in OTHER_PLACES])
def test_browser_a_card_on_another_tab_with_no_link_keeps_the_2_23_sentence(seen, place):
    first = seen["nolink"]["places"][place][0]
    assert first["noSource"] == 1 and first["noStudy"] == 0


@pytest.mark.parametrize("place", [p[0] for p in TRIAL_PLACES])
def test_browser_dexbrompheniramine_at_390_px_is_one_line_never_broken_without_a_hyphen(seen, place):
    first = seen["long"]["places"][place][0]
    assert first["name"] == LONG_NAME
    assert first["lang"] == "en" and first["hyphens"] == "auto"
    assert first["overflowWrap"] != "anywhere" and first["wordBreak"] != "break-all"
    assert first["titleLines"] == 1  # one line (a break would need a hyphen, and none is needed)
    assert not first["titleOverflows"] and not first["sideways"]
