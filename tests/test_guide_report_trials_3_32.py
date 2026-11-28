"""Ticket 3.32. Two fixes to the "how to read" guide, from Shreshth's phone pass.

1. The floating report note under the A to J key is gone. Its words are now the
   last line of "Where the facts come from".
2. ClinicalTrials.gov is named as a source, in both folded parts.

Every new line is checked word for word. The page is read from the file; the
browser check opens it at 390 px with every network call refused. No network.
"""

import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest

from test_api import guide_of, plain
from test_condensed_guide import DOCTORS_TITLE, FACTS_TITLE, fold, lines_of

ROOT = Path(__file__).resolve().parent.parent
PAGE_FILE = ROOT / "web" / "index.html"
PAGE = PAGE_FILE.read_text(encoding="utf-8")
GUIDE = guide_of(PAGE)

DOCTORS_NEW = [
    ("Source.", "Open Targets Platform. Trial details from ClinicalTrials.gov."),
    ("Trials.", "Rows are the trials the database links to the medicine. Medicines found only on ClinicalTrials.gov are matched by exact name. A finished trial is a record, not a result."),
]
FACTS_NEW = [
    ("Trials.", "ClinicalTrials.gov, the US public register of clinical studies."),
    ("Reports.", "We read every report. Nothing about you is kept."),
]


def test_the_doctors_fold_has_the_new_source_line_and_the_new_trials_line_in_place():
    lines = lines_of(fold(GUIDE, DOCTORS_TITLE)[1])
    labels = [label for label, _ in lines]
    assert lines[labels.index("Source.")] == DOCTORS_NEW[0]
    assert lines[labels.index("Trials.")] == DOCTORS_NEW[1]
    assert labels.index("Trials.") == labels.index("Wider and narrower diseases.") + 1
    assert labels.count("Trials.") == 1 and len(lines) == 9


def test_the_facts_fold_has_the_trials_line_after_facts_and_the_report_line_last():
    lines = lines_of(fold(GUIDE, FACTS_TITLE)[1])
    labels = [label for label, _ in lines]
    assert lines[labels.index("Facts.") + 1] == FACTS_NEW[0]
    assert lines[-1] == FACTS_NEW[1]
    assert labels.count("Reports.") == 1 and len(lines) == 7  # ticket R3: one more line, Recruiting now


def test_the_new_lines_are_written_once_each_in_the_lists_own_style():
    for label, words in DOCTORS_NEW[1:] + FACTS_NEW:
        assert "<li><div><b>%s</b> <span>%s</span></div></li>" % (label, words) in PAGE
    assert PAGE.count("We read every report. Nothing about you is kept.") == 1


def test_no_key_note_is_left_in_the_page_or_its_styles():
    assert "key-note" not in PAGE
    assert "We read every report.<br>" not in PAGE


def test_the_key_is_the_last_thing_in_the_card_part():
    card_part = GUIDE[GUIDE.index('id="guide-card"'):]
    card_part = card_part[:card_part.index("</section>")]
    assert re.search(r"</ul>\s*$", card_part)
    key = card_part[card_part.index('<ul class="key">'):]
    assert re.findall(r'aria-hidden="true">([A-Z])</span>', key)[-1] == "J"


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
  await page.waitForSelector("#guide", { state: "visible" });
  const shut = await page.evaluate(() => document.documentElement.scrollWidth > document.documentElement.clientWidth);
  await page.evaluate(() => document.querySelectorAll("#guide details").forEach(d => { d.open = true; }));
  await page.waitForTimeout(200);
  const out = await page.evaluate(() => {
    const key = document.querySelector("#guide-card .key");
    const lines = id => [...document.getElementById(id).closest("details").querySelectorAll("li")]
      .map(li => li.innerText.replace(/\s+/g, " ").trim());
    return {
      keyLast: key.lastElementChild.innerText.replace(/\s+/g, " ").trim(),
      keyNext: key.nextElementSibling && key.nextElementSibling.tagName,
      keyNoteCount: document.querySelectorAll(".key-note").length,
      sectionEndsWithKey: document.querySelector("#guide-card").lastElementChild === key,
      doctors: lines("guide-doctors-title"),
      facts: lines("guide-facts-title"),
      sideways: document.documentElement.scrollWidth > document.documentElement.clientWidth,
      wide: [...document.querySelectorAll("#guide *")].filter(el => el.getBoundingClientRect().right > innerWidth + 0.5).length,
    };
  });
  out.sidewaysShut = shut;
  out.errors = errors;
  await browser.close();
  console.log(JSON.stringify(out));
})().catch(problem => { console.error(problem); process.exit(1); });
"""


@pytest.fixture(scope="module")
def seen():
    node = shutil.which("node")
    if not node or subprocess.run(
            [node, "-e", "require('playwright')"], capture_output=True).returncode:
        pytest.skip("needs node with playwright to open a real browser")
    run = subprocess.run([node, "-e", BROWSER_SCRIPT, str(PAGE_FILE)],
                         capture_output=True, text=True, timeout=240, cwd=str(ROOT))
    assert run.returncode == 0, run.stderr[-3000:]
    return json.loads(run.stdout)


def test_browser_390_the_key_ends_at_j_with_nothing_under_it(seen):
    assert seen["errors"] == []
    assert seen["keyLast"] == "J Tell us if something is wrong"
    assert seen["keyNext"] is None and seen["sectionEndsWithKey"]
    assert seen["keyNoteCount"] == 0


def test_browser_390_both_folds_show_the_new_lines_word_for_word(seen):
    for label, words in DOCTORS_NEW:
        assert "%s %s" % (label, words) in seen["doctors"]
    for label, words in FACTS_NEW:
        assert "%s %s" % (label, words) in seen["facts"]
    assert seen["facts"][-1] == "Reports. We read every report. Nothing about you is kept."


def test_browser_390_no_sideways_scroll_folds_shut_or_open(seen):
    assert not seen["sidewaysShut"]
    assert not seen["sideways"]
    assert seen["wide"] == 0
