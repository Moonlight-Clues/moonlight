"""Ticket 3.25. Long names never widen the page.

At 390 px no card may make the page wider than the screen. Long single-word
names wrap with a hyphen (the 2.67 rule), so the card title's text box has to
be allowed to shrink (min-width:0 on .card-title > div).

The example is melanoma (MONDO_0005105): the page is 390 px wide, there is no
sideways scroll, and the long names in "New medicines being tested" wrap.
The same check runs on sclerosing cholangitis (the database's page for
primary sclerosing cholangitis, MONDO_0018646), type 2 diabetes
(MONDO_0005148) and rheumatoid arthritis (MONDO_0008383).

Saved files only: fixtures/narrow_cards_3_25/ (see its README). No network.
The page is opened in a real browser with every tab visited and every folded
box opened, so every card on the page is measured.
"""

import json
import pathlib
import shutil
import subprocess
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from moonlight import api

ROOT = pathlib.Path(__file__).resolve().parent.parent
SAVED = ROOT / "fixtures" / "narrow_cards_3_25"
PAGE_FILE = ROOT / "web" / "index.html"
PAGE = PAGE_FILE.read_text(encoding="utf-8")
WIDTH = 390

MELANOMA, PSC, DIABETES, RHEUMATOID = "MONDO_0005105", "MONDO_0018646", "MONDO_0005148", "MONDO_0008383"
DISEASES = {"melanoma": MELANOMA, "primary sclerosing cholangitis": PSC,
            "type 2 diabetes": DIABETES, "rheumatoid arthritis": RHEUMATOID}


def saved_post_json(body):
    """Stands in for fetch._post_json with the files in fixtures/narrow_cards_3_25/."""
    assert set(body) == {"query", "variables"}
    query, variables = body["query"], body["variables"]
    # ticket T7. A medicine question has no diseaseId. The answer is the same
    # drug object these saved files already hold, or nothing when they do not.
    if "chemblId" in query:
        by_id = {}
        wanted = set(variables.values())
        for folder in ("disease_drugs", "target_drugs"):
            for path in (SAVED / folder).glob("*.response.json"):
                payload = json.loads(path.read_text(encoding="utf-8"))
                root = payload.get("data") or {}
                asked = root.get("disease") or root.get("target") or {}
                rows = (asked.get("drugAndClinicalCandidates") or {}).get("rows") or []
                for row in rows:
                    drug = row.get("drug") or {}
                    if drug.get("id") in wanted:
                        by_id.setdefault(drug["id"], drug)
        return {"data": {key: by_id.get(drug_id) for key, drug_id in variables.items()}}
    if "targetId" in variables:
        path = SAVED / "target_drugs" / f"{variables['targetId']}.response.json"
    else:
        if "parents" in query:
            kind = "family"
        elif "associatedTargets" in query:
            kind = "associated_targets"
        elif "drugAndClinicalCandidates" in query:
            kind = "disease_drugs"
        else:
            kind = "disease"
        path = SAVED / kind / f"{variables['diseaseId']}.response.json"
    return json.loads(path.read_text(encoding="utf-8"))


BROWSER_SCRIPT = r"""
"use strict";
const fs = require("fs");
const { chromium } = require("playwright");
const PAGE = fs.readFileSync(process.argv[1], "utf-8");
const ANSWERS = JSON.parse(fs.readFileSync(process.argv[2], "utf-8"));
const WIDTH = Number(process.argv[3]);
const SITE = "http://moonlight.test";

// Everything that sticks out past the right edge of the screen, with where it is.
function measure(width) {
  const out = [];
  for (const el of document.querySelectorAll("body *")) {
    if (!el.getClientRects().length) continue;               // not on the page
    if (el.closest("details:not([open]) > :not(summary)")) continue;  // folded away
    const right = el.getBoundingClientRect().right;
    if (right > width + 0.5) {
      const where = el.closest(".card");
      out.push({
        tag: el.tagName.toLowerCase() + (el.className ? "." + String(el.className).split(" ")[0] : ""),
        right: Math.round(right),
        card: where ? (where.querySelector('[data-slot="medicine-name"]') || {}).textContent || "?" : null,
      });
    }
  }
  return out;
}

async function oneSearch(browser, id, answer) {
  const context = await browser.newContext({ viewport: { width: WIDTH, height: 844 } });
  const page = await context.newPage();
  const errors = [];
  page.on("pageerror", problem => errors.push(String(problem)));
  await page.addInitScript(() => { window.print = () => {}; });
  await page.addInitScript(`window.measure = ${measure.toString()};`);  // the function runs in the page
  await context.route("**/*", route => {
    const url = route.request().url();
    if (url === SITE + "/" || url.startsWith(SITE + "/?"))
      return route.fulfill({ contentType: "text/html; charset=utf-8", body: PAGE });
    if (url.startsWith(SITE + "/api/clues?"))
      return route.fulfill({ contentType: "application/json", body: JSON.stringify(answer) });
    return route.abort();
  });
  await page.goto(SITE + "/?disease=" + id);
  await page.waitForSelector("#found", { state: "visible" });
  const out = { errors, tabs: {} };
  for (const tab of ["approved", "trials", "clues"]) {
    await page.click("#tab-" + tab);
    // open every folded box on this tab
    await page.evaluate(() => document.querySelectorAll("#found details").forEach(d => { d.open = true; }));
    await page.waitForTimeout(300);
    out.tabs[tab] = await page.evaluate(({ width, tab }) => ({
      pageWidth: document.documentElement.scrollWidth,
      windowWidth: window.innerWidth,
      sideways: window.scrollX !== 0 || document.documentElement.scrollWidth > window.innerWidth,
      cards: [...document.querySelectorAll("#panel-" + tab + " .card")].filter(c => c.checkVisibility()).length,
      outside: measure(width),
    }), { width: WIDTH, tab });
  }
  // The long names in "New medicines being tested": the title's text box must be inside
  // its card, and a name too long for one line must have wrapped (taller than one line).
  await page.click("#tab-trials");
  out.newBox = await page.evaluate(() => [...document.querySelectorAll("#new-trials-cards > .card")].map(card => {
    const h3 = card.querySelector(".card-title h3");
    const line = parseFloat(getComputedStyle(h3).lineHeight) || parseFloat(getComputedStyle(h3).fontSize) * 1.2;
    return {
      name: h3.textContent.trim().replace(/\s+/g, " "),
      lines: Math.round(h3.getBoundingClientRect().height / line),
      insideCard: h3.getBoundingClientRect().right <= card.getBoundingClientRect().right + 0.5,
    };
  }));
  await context.close();
  return out;
}

(async () => {
  const browser = await chromium.launch();
  const out = {};
  for (const name of Object.keys(ANSWERS)) out[name] = await oneSearch(browser, ANSWERS[name].id, ANSWERS[name].answer);
  await browser.close();
  console.log(JSON.stringify(out));
})().catch(problem => { console.error(problem); process.exit(1); });
"""


@pytest.fixture(scope="module")
def answers():
    out = {}
    with patch("moonlight.fetch._post_json", side_effect=saved_post_json):
        for name, disease_id in DISEASES.items():
            api.forget_visitors()
            api.forget_answers()
            answer = TestClient(api.app).get("/api/clues", params={"disease_id": disease_id})
            assert answer.status_code == 200, name
            out[name] = {"id": disease_id, "answer": answer.json()}
    return out


@pytest.fixture(scope="module")
def seen(answers, tmp_path_factory):
    node = shutil.which("node")
    if not node or subprocess.run(
            [node, "-e", "require('playwright')"], capture_output=True).returncode:
        pytest.skip("needs node with playwright to open a real browser")
    answers_file = tmp_path_factory.mktemp("long_names") / "answers.json"
    answers_file.write_text(json.dumps(answers), encoding="utf-8")
    run = subprocess.run(
        [node, "-e", BROWSER_SCRIPT, str(PAGE_FILE), str(answers_file), str(WIDTH)],
        capture_output=True, text=True, timeout=300, cwd=str(ROOT))
    assert run.returncode == 0, run.stderr[-3000:]
    out = json.loads(run.stdout)
    for name in answers:
        assert out[name]["errors"] == [], name
    return out


@pytest.mark.parametrize("name", list(DISEASES))
@pytest.mark.parametrize("tab", ["approved", "trials", "clues"])
def test_no_card_makes_the_page_wider_than_the_390_px_screen(seen, name, tab):
    result = seen[name]["tabs"][tab]
    assert result["windowWidth"] == WIDTH
    assert result["outside"] == [], result["outside"][:6]
    assert result["pageWidth"] <= WIDTH, result["pageWidth"]
    assert result["sideways"] is False


@pytest.mark.parametrize("name", list(DISEASES))
def test_the_check_really_measured_cards(seen, name):
    """Guards the test itself: some tab of each page showed cards."""
    assert sum(seen[name]["tabs"][tab]["cards"] for tab in seen[name]["tabs"]) > 0


def test_melanoma_page_is_390_wide_with_no_sideways_scroll(seen):
    for tab, result in seen["melanoma"]["tabs"].items():
        assert result["pageWidth"] == WIDTH, (tab, result["pageWidth"])
        assert result["sideways"] is False, tab


def test_melanoma_new_medicines_names_stay_inside_their_cards_and_the_long_ones_wrap(seen):
    cards = seen["melanoma"]["newBox"]
    assert cards, "the melanoma example has cards in 'New medicines being tested'"
    assert all(card["insideCard"] for card in cards), [c for c in cards if not c["insideCard"]]
    long_ones = [card for card in cards if max(len(word) for word in card["name"].split()) > 22]
    assert len(long_ones) >= 2, "the example has two long names"
    assert all(card["lines"] >= 2 for card in long_ones), long_ones


def test_the_fix_is_the_one_line_from_the_ticket_and_the_old_line_is_untouched():
    assert ".card-title>div{min-width:0}" in PAGE
    assert ".card-title{display:flex;align-items:flex-start;gap:11px;min-width:0}" in PAGE
