"""Ticket T11. "How to read a card" shows one sample trial row.

The row is a picture of a trial row on a card. It is not a link and it has
no address. MAIN 5 named the words: "NCT number" in the row's teal, "Phase 3"
on the right, and "Finished 2016 · Was tested" underneath. Then the three
approved sentences, word for word. The gold letters A to J, the Doxapram
card and its lines stay as they are.
"""

import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from moonlight import api

from test_api import guide_of, plain
from test_guide_card_3_9 import LEGEND

ROOT = Path(__file__).resolve().parent.parent
PAGE_FILE = ROOT / "web" / "index.html"

TOP = "NCT number"
PHASE = "Phase 3"
BOTTOM = "Finished 2016 \u00b7 Was tested"
LINES = (
    "Each row is one trial on ClinicalTrials.gov. Tap it to open the trial.",
    "Status says where the trial is now. 'Finished' means it ended, not that the medicine worked.",
    "Role says whether this medicine was the one tested or was used for comparison.",
)


@pytest.fixture(scope="module")
def page():
    return TestClient(api.app).get("/").text


@pytest.fixture(scope="module")
def guide(page):
    return guide_of(page)


def card_section(guide):
    """The "How to read a card" part, from its heading to the end of that section."""
    part = guide[guide.index('id="guide-card"'):]
    return part[:part.index("</section>")]


def between_card_and_key(guide):
    """What sits under the Doxapram card and above the gold-letter key."""
    part = card_section(guide)
    return part[part.index("</article>"):part.index('<ul class="key">')]


def doxapram_card(guide):
    part = card_section(guide)
    return part[part.index('<article class="card"'):part.index("</article>")]


# ---- the sample row and the three sentences ----

def test_one_sample_row_is_a_picture_with_the_approved_words(guide):
    gap = between_card_and_key(guide)
    assert gap.count('class="study-row"') == 1
    assert re.search(r"<a\b", gap, re.I) is None
    assert re.search(r"\bhref\b", gap, re.I) is None
    assert "http" not in gap.lower()
    assert re.search(r"NCT\d", gap) is None  # a placeholder, never a made-up trial number
    assert re.search(r'<span class="study-row">', gap)
    assert gap.index('class="sr1"') < gap.index('class="nct"') < gap.index("NCT number")
    assert gap.index("NCT number") < gap.index('class="phase-t"') < gap.index("Phase 3")
    assert gap.index("Phase 3") < gap.index('class="sr2"') < gap.index(BOTTOM)
    assert '<span class="nct">NCT number</span>' in gap
    assert '<span class="phase-t">Phase 3</span>' in gap
    assert '<span class="sr2">%s</span>' % BOTTOM in gap
    words = plain(gap)
    assert words.index(TOP) < words.index(PHASE) < words.index(BOTTOM) < words.index(LINES[0])


def test_the_three_lines_are_the_approved_sentences_once_each(guide):
    gap = between_card_and_key(guide)
    words = plain(gap)
    for earlier, later in zip(LINES, LINES[1:]):
        assert words.index(earlier) < words.index(later)
    whole = plain(guide)
    for line in LINES:
        assert whole.count(line) == 1
        assert doxapram_card(guide).count(line) == 0


def test_the_doxapram_card_and_its_letters_stay_a_to_j(guide):
    card = doxapram_card(guide)
    assert re.findall(r'<span class="k" aria-label="([A-Z])">\1</span>', card) == list("ABCDEFGHIJ")
    assert "NCT number" not in card and BOTTOM not in card
    found = re.findall(
        r'<li><span class="k" aria-hidden="true">([A-Z])</span><span>([^<]+)</span></li>',
        card_section(guide))
    assert found == LEGEND


# ---- the row's look at 390 px ----

BROWSER_SCRIPT = r"""
"use strict";
const fs = require("fs");
const { chromium } = require("playwright");
const PAGE = fs.readFileSync(process.argv[1], "utf-8");
const SITE = "http://moonlight.test";

(async () => {
  const browser = await chromium.launch();
  const context = await browser.newContext({ viewport: { width: 390, height: 844 } });
  const page = await context.newPage();
  const errors = [];
  page.on("pageerror", problem => errors.push(String(problem)));
  await context.route("**/*", route => {
    const url = route.request().url();
    if (url === SITE + "/" || url.startsWith(SITE + "/?"))
      return route.fulfill({ contentType: "text/html; charset=utf-8", body: PAGE });
    return route.abort();
  });
  await page.goto(SITE + "/?guide=1");
  await page.waitForSelector("#guide:not([hidden])");
  const seen = await page.evaluate(() => {
    const section = document.getElementById("guide-card");
    const article = section.querySelector("article.card");
    const row = section.querySelector(".study-row");
    const box = el => {
      const r = el.getBoundingClientRect();
      return { top: r.top, right: r.right, bottom: r.bottom, left: r.left, height: r.height };
    };
    if (!row) return { missing: true };
    const nct = row.querySelector(".nct");
    const phase = row.querySelector(".phase-t");
    const line = row.querySelector(".sr2");
    const paint = el => getComputedStyle(el);
    return {
      missing: false,
      tag: row.tagName,
      href: row.getAttribute("href"),
      insideCard: article.contains(row),
      nct: nct.textContent,
      phase: phase.textContent,
      line: line.textContent,
      nctColor: paint(nct).color,
      nctLine: paint(nct).textDecorationLine,
      phaseColor: paint(phase).color,
      phaseWeight: paint(phase).fontWeight,
      lineColor: paint(line).color,
      nctBox: box(nct),
      phaseBox: box(phase),
      lineBox: box(line),
      rowHeight: row.getBoundingClientRect().height,
      sideways: document.documentElement.scrollWidth > document.documentElement.clientWidth,
      letters: [...article.querySelectorAll(".k")].map(k => k.textContent).join(""),
    };
  });
  seen.errors = errors;
  console.log(JSON.stringify(seen));
  await browser.close();
})().catch(problem => { console.error(problem); process.exit(1); });
"""


@pytest.fixture(scope="module")
def seen_at_390():
    node = shutil.which("node")
    if not node or subprocess.run(
            [node, "-e", "require('playwright')"], capture_output=True).returncode:
        pytest.skip("needs node with playwright to open a real browser")
    run = subprocess.run(
        [node, "-e", BROWSER_SCRIPT, str(PAGE_FILE)],
        capture_output=True, text=True, timeout=120, cwd=str(ROOT))
    assert run.returncode == 0, run.stderr[-3000:]
    seen = json.loads(run.stdout)
    assert seen["errors"] == []
    return seen


def test_browser_the_sample_row_looks_like_a_trial_row_at_390(seen_at_390):
    seen = seen_at_390
    assert seen["missing"] is False
    assert seen["tag"] == "SPAN" and seen["href"] is None
    assert seen["insideCard"] is False
    assert (seen["nct"], seen["phase"], seen["line"]) == (TOP, PHASE, BOTTOM)
    assert seen["nctColor"] == "rgb(66, 157, 154)"  # the row's teal
    assert "underline" in seen["nctLine"]
    assert seen["phaseColor"] == "rgb(83, 96, 108)"  # the row's phase grey
    assert seen["phaseWeight"] in ("700", "bold")
    assert seen["lineColor"] == "rgb(86, 104, 119)"
    nct, phase, line = seen["nctBox"], seen["phaseBox"], seen["lineBox"]
    assert phase["left"] > nct["right"]
    assert phase["top"] < nct["bottom"] and nct["top"] < phase["bottom"]
    assert line["top"] >= nct["bottom"] - 1
    assert seen["rowHeight"] >= 44
    assert seen["sideways"] is False
    assert seen["letters"] == "ABCDEFGHIJ"
