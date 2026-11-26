"""Ticket T13. Cards on the In trials tab do not show the record count.

EXAMPLE. Pulmonary arterial hypertension, from the saved files:
  Udenafil, on In trials, does not show "0 records".
  Sotatercept, on Approved, still shows "17 records".

The count on the other tabs stays. Saved files only. No network.
"""

import json
import pathlib
import re
import shutil
import subprocess
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from moonlight import api, explain

import test_api

ROOT = pathlib.Path(__file__).resolve().parent.parent
PAGE_FILE = ROOT / "web" / "index.html"
PAGE = PAGE_FILE.read_text(encoding="utf-8")

PAH = "MONDO_0015924"


def card_named(cards, name):
    found = [card for card in cards if card["name"] == name]
    assert len(found) == 1, name
    return found[0]


@pytest.fixture(scope="module")
def pah():
    """The pulmonary arterial hypertension page, from the saved answers."""
    explain.forget_everything()
    api.forget_answers()
    with patch("moonlight.fetch._post_json", side_effect=test_api.fake_post_json), \
            patch("requests.request", side_effect=AssertionError("network used")), \
            patch("requests.post", side_effect=AssertionError("network used")), \
            patch("requests.get", side_effect=AssertionError("network used")), \
            patch("requests.sessions.Session.request",
                  side_effect=AssertionError("network used")), \
            test_api.with_saved_targets():
        reply = TestClient(api.app).get("/api/clues", params={"disease_id": PAH})
    assert reply.status_code == 200
    return reply.json()


def test_the_example_numbers_are_zero_and_seventeen(pah):
    """Udenafil really has no records. Sotatercept really has 17."""
    (udenafil,) = [card for card in pah["being_studied"] if card["medicine"] == "Udenafil"]
    (sotatercept,) = [card for card in pah["approved"] if card["medicine"] == "Sotatercept"]
    assert udenafil["reports"] == 0
    assert sotatercept["reports"] == 17
    assert [card["medicine"] for card in pah["being_studied"]][:2] == ["Udenafil", "Vardenafil"]


def test_only_the_in_trials_list_is_told_to_hide_the_count():
    """The reports slot is hidden when the In trials list is drawn, and nowhere else."""
    draw = PAGE[PAGE.index("const studiedCards"):PAGE.index("const moreTrialsCards")]
    assert 'slot(el, "reports").hidden = true' in draw
    approved = PAGE[PAGE.index("function approvedCard("):PAGE.index("function trialBoxCard(")]
    clues = PAGE[PAGE.index("const newCards"):PAGE.index("const studiedCards")]
    assert 'slot(el, "reports").hidden' not in approved
    assert 'slot(el, "reports").hidden' not in clues
    # The other tabs still write the count, one record or many.
    assert '(clue.reports === 1 ? " record" : " records")' in PAGE


# ---- the page, in a real browser, at 390 px ----

BROWSER = r"""
"use strict";
const fs = require("fs");
const { chromium } = require("playwright");
const PAGE = fs.readFileSync(process.argv[1], "utf-8");
const ANSWER = fs.readFileSync(process.argv[2], "utf-8");
const SITE = "http://moonlight.test";

function readCards(rootId) {
  const root = document.getElementById(rootId);
  return [...root.querySelectorAll(":scope > .card")].map(card => {
    const reports = card.querySelector('[data-slot="reports"]');
    const shown = el => !!el && !el.hidden && el.getClientRects().length > 0;
    return {
      name: card.querySelector('[data-slot="medicine-name"]').textContent,
      reportsText: reports ? reports.textContent : null,
      reportsShown: shown(reports),
      words: card.innerText.replace(/\s+/g, " ").trim(),
    };
  });
}

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
    if (url.startsWith(SITE + "/api/clues?"))
      return route.fulfill({ contentType: "application/json", body: ANSWER });
    return route.abort();
  });
  await page.goto(SITE + "/?disease=MONDO_0015924");
  await page.waitForSelector("#found", { state: "visible" });
  const out = { errors };
  out.approved = await page.evaluate(readCards, "approved-cards");
  await page.click("#tab-clues");
  await page.waitForSelector("#panel-clues", { state: "visible" });
  out.clues = await page.evaluate(readCards, "new-cards");
  await page.click("#tab-trials");
  await page.waitForSelector("#panel-trials", { state: "visible" });
  out.trials = await page.evaluate(readCards, "studied-cards");
  out.wide = await page.evaluate(() => document.documentElement.scrollWidth);
  await browser.close();
  console.log(JSON.stringify(out));
})().catch(problem => { console.error(problem); process.exit(1); });
"""


@pytest.fixture(scope="module")
def seen(pah, tmp_path_factory):
    node = shutil.which("node")
    if not node or subprocess.run(
            [node, "-e", "require('playwright')"], capture_output=True).returncode:
        pytest.skip("needs node with playwright to open a real browser")
    answer = tmp_path_factory.mktemp("t13") / "pah.json"
    answer.write_text(json.dumps(pah), encoding="utf-8")
    run = subprocess.run(
        [node, "-e", BROWSER, str(PAGE_FILE), str(answer)],
        capture_output=True, text=True, timeout=120, cwd=str(ROOT))
    assert run.returncode == 0, run.stderr[-3000:]
    out = json.loads(run.stdout)
    assert out["errors"] == []
    return out


def test_example_udenafil_on_in_trials_does_not_show_0_records(seen):
    udenafil = card_named(seen["trials"], "Udenafil")
    assert udenafil["reportsShown"] is False
    assert "0 records" not in udenafil["words"]
    # Every card on the In trials list, not only Udenafil.
    assert seen["trials"]
    for card in seen["trials"]:
        assert card["reportsShown"] is False, card["name"]
        assert not re.search(r"\d+ records?", card["words"]), card["name"]
    assert seen["wide"] <= 390


def test_example_sotatercept_on_approved_still_shows_17_records(seen):
    sotatercept = card_named(seen["approved"], "Sotatercept")
    assert sotatercept["reportsShown"] is True
    assert sotatercept["reportsText"] == "17 records"
    assert "17 records" in sotatercept["words"]


def test_a_new_clue_still_shows_its_record_count(seen, pah):
    """The count on the other tabs stays. One new clue on the main list is enough."""
    boxed = set(pah.get("opposite_way_box") or [])
    sent = next(card for card in pah["new_clues"] if card["id"] not in boxed)
    card = card_named(seen["clues"], sent["medicine"])
    words = "1 record" if sent["reports"] == 1 else f"{sent['reports']} records"
    assert card["reportsShown"] is True
    assert card["reportsText"] == words
    assert words in card["words"]
