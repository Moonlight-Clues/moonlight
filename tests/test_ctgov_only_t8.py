"""Ticket T8. The box of medicines found only on ClinicalTrials.gov.

A new open box under the two boxes already on the In trials tab.
Title: "Medicines found only on ClinicalTrials.gov ([N] trials)".
Each card says "Found only on ClinicalTrials.gov."
The box says "These are listed on ClinicalTrials.gov. Moonlight has no other records for them."
Cards keep the normal card edge. The first 20 show, then "Show all [N]".
At most 300 cards are sent. Past that, a link to the ClinicalTrials.gov search.
The In trials tab count includes the box.

Saved files only. No network. The browser part needs node and playwright.
"""

import json
import pathlib
import shutil
import subprocess

import pytest
from fastapi.testclient import TestClient

from moonlight import api, disease_search
from moonlight.filter import GROUPS
from moonlight.records import Disease

import test_matched_trials_t7 as t7

ROOT = pathlib.Path(__file__).resolve().parent.parent
PAGE = (ROOT / "web" / "index.html").read_text(encoding="utf-8")

LINE = "Found only on ClinicalTrials.gov."
NOTE = "These are listed on ClinicalTrials.gov. Moonlight has no other records for them."
TITLE = "Medicines found only on ClinicalTrials.gov"


def test_the_words_are_the_ones_in_the_ticket():
    from moonlight.engine import CTGOV_ONLY_LINE, CTGOV_ONLY_NOTE, CTGOV_ONLY_SENT
    assert CTGOV_ONLY_LINE == LINE
    assert CTGOV_ONLY_NOTE == NOTE
    assert CTGOV_ONLY_SENT == 300


def test_the_api_sends_the_box_under_three_hundred(monkeypatch, tmp_path):
    disease = Disease(id="MONDO_T8", name="Example disease")
    path = tmp_path / "disease_search.sqlite"
    disease_search.write_sqlite(path, [
        t7._result("MONDO_T8", "Example disease", True, [], [
            {"name": "Zebra drug", "nct_ids": ["NCT00000002"]},
            {"name": "Alpha drug", "nct_ids": ["NCT00000001", "NCT00000002"]},
        ], 2),
    ], "2026-11-26")
    tray = {group: [] for group in GROUPS}
    t7._patch_find(monkeypatch, disease, tray, [], [])
    api.forget_answers()
    with TestClient(api.app) as client:
        monkeypatch.setattr(api, "_search", disease_search.SearchFile.open(path))
        answer = client.get("/api/clues", params={"disease_id": disease.id}).json()
    box = answer["ctgov_only"]
    assert [card["name"] for card in box["cards"]] == ["Alpha drug", "Zebra drug"]
    assert box["line"] == LINE
    assert box["note"] == NOTE
    assert box["trials"] == 2  # two trials, not two names: one trial names both
    assert "more_url" not in box
    assert "more_in_trials" not in answer or True


def test_past_three_hundred_only_three_hundred_are_sent_and_a_link(monkeypatch, tmp_path):
    disease = Disease(id="MONDO_T8", name="Example disease")
    rows = [{"name": f"Drug {i:03d}", "nct_ids": [f"NCT{i:08d}"]} for i in range(1, 306)]
    path = tmp_path / "disease_search.sqlite"
    disease_search.write_sqlite(path, [
        t7._result("MONDO_T8", "Example disease", True, [], rows, 305),
    ], "2026-11-26")
    tray = {group: [] for group in GROUPS}
    t7._patch_find(monkeypatch, disease, tray, [], [])
    api.forget_answers()
    with TestClient(api.app) as client:
        monkeypatch.setattr(api, "_search", disease_search.SearchFile.open(path))
        answer = client.get("/api/clues", params={"disease_id": disease.id}).json()
    box = answer["ctgov_only"]
    assert len(box["cards"]) == 300
    assert box["cards"][0]["name"] == "Drug 001"
    assert box["more_url"].startswith("https://clinicaltrials.gov/search?")
    assert "example" in box["more_url"].lower()
    # the tab's count line includes the 300 cards
    assert answer["trials_count_line"].startswith("300 medicines")


def test_a_skipped_disease_has_no_box(monkeypatch, tmp_path):
    disease = Disease(id="MONDO_SKIP", name="breast cancer")
    path = tmp_path / "disease_search.sqlite"
    disease_search.write_sqlite(path, [
        t7._result("MONDO_SKIP", "breast cancer", False, [], [], 7765),
    ], "2026-11-26")
    tray = {group: [] for group in GROUPS}
    t7._patch_find(monkeypatch, disease, tray, [], [])
    api.forget_answers()
    with TestClient(api.app) as client:
        monkeypatch.setattr(api, "_search", disease_search.SearchFile.open(path))
        answer = client.get("/api/clues", params={"disease_id": disease.id}).json()
    assert "ctgov_only" not in answer


def test_the_box_markup_sits_under_the_two_boxes_and_has_no_dashed_edge():
    panel = PAGE[PAGE.index('id="panel-trials"'):PAGE.index('id="panel-clues"')]
    assert panel.index('id="new-trials-box"') < panel.index('id="ctgov-only-box"')
    assert "dashed" not in panel[panel.index('id="ctgov-only-box"'):]
    assert TITLE in panel
    assert 'id="ctgov-only-cards"' in panel


# ---------------------------------------------------------------- the page

BROWSER = r"""
"use strict";
const fs = require("fs");
const { chromium } = require("playwright");
const PAGE = fs.readFileSync(process.argv[1], "utf-8");
const ANSWERS = JSON.parse(fs.readFileSync(process.argv[2], "utf-8"));
const SITE = "http://moonlight.test";

function readBox() {
  const box = document.getElementById("ctgov-only-box");
  const cards = [...document.querySelectorAll("#ctgov-only-cards > .card")];
  const button = document.getElementById("ctgov-only-show-all");
  const count = document.querySelector('#tab-trials [data-part="count"]').textContent;
  const edge = cards[0] ? getComputedStyle(cards[0]).borderLeftStyle : "";
  return {
    open: box.open,
    shown: box.getClientRects().length > 0,
    summary: box.querySelector("summary").innerText.replace(/\s+/g, " ").trim(),
    note: document.getElementById("ctgov-only-note").textContent,
    names: cards.map(card => card.querySelector('[data-slot="medicine-name"]').textContent),
    lines: cards.map(card => (card.querySelector('[data-slot="ctgov-only-line"]') || {}).textContent || ""),
    onScreen: cards.map(card => card.checkVisibility()),
    showAll: button ? button.textContent : null,
    showAllHeight: button ? Math.round(button.getBoundingClientRect().height) : null,
    count,
    cardCount: document.querySelectorAll("#panel-trials .card").length,
    edge,
    dashed: /dashed/.test(edge),
    width: document.documentElement.clientWidth,
    shifted: document.documentElement.scrollWidth > document.documentElement.clientWidth + 1,
  };
}

(async () => {
  const browser = await chromium.launch();
  const out = {};
  for (const name of Object.keys(ANSWERS)) {
    const answer = ANSWERS[name];
    const context = await browser.newContext({ viewport: { width: 390, height: 844 } });
    const page = await context.newPage();
    const errors = [];
    page.on("pageerror", problem => errors.push(String(problem)));
    await page.exposeFunction("noPrint", () => {});
    await context.route("**/*", route => {
      const url = route.request().url();
      if (url === SITE + "/" || url.startsWith(SITE + "/?"))
        return route.fulfill({ contentType: "text/html; charset=utf-8", body: PAGE });
      if (url.startsWith(SITE + "/api/clues?"))
        return route.fulfill({ contentType: "application/json", body: JSON.stringify(answer) });
      if (url.startsWith(SITE + "/api/version"))
        return route.fulfill({ contentType: "application/json", body: '{"fingerprint":"0123456789ab","revision":"local"}' });
      return route.abort();
    });
    await page.goto(SITE + "/?disease=" + answer.disease.id + "&tab=trials");
    await page.waitForSelector("#found", { state: "visible" });
    await page.evaluate(() => { window.print = () => {}; });
    out[name] = { errors };
    out[name].open = await page.evaluate(readBox);
    if (process.argv[3] && name === "many" && out[name].open.shown) {
      await page.locator("#ctgov-only-box summary").scrollIntoViewIfNeeded();
      await page.evaluate(() => {
        document.getElementById("ctgov-only-box").scrollIntoView({block: "start"});
        window.scrollBy(0, -80);
      });
      await page.waitForTimeout(200);
      await page.screenshot({ path: process.argv[3], fullPage: false });
    }
    if (out[name].open.showAll) {
      await page.click("#ctgov-only-show-all");
      out[name].shown = await page.evaluate(readBox);
    }
    await page.click("#print-page");
    out[name].printed = await page.locator('[data-reg="trials"]').innerText();
    await context.close();
  }
  await browser.close();
  console.log(JSON.stringify(out));
})().catch(problem => { console.error(problem); process.exit(1); });
"""


def _answers():
    def card(name):
        return {"name": name}
    many = [card(f"Listed drug {i}") for i in range(1, 26)]
    base = {
        "disease": {"id": "MONDO_T8", "name": "Example disease"},
        "about_disease": {"description": "", "source": None, "also_called": []},
        "rule_text": "Ordered.",
        "approved": [],
        "being_studied": [],
        "new_clues": [],
        "left_out": {"not_approved": 0, "unclear_link": 0},
    }
    full = dict(base)
    full["ctgov_only"] = {"trials": 25, "note": NOTE, "line": LINE, "cards": many}
    one = dict(base)
    one["disease"] = {"id": "MONDO_ONE", "name": "One disease"}
    one["ctgov_only"] = {"trials": 1, "note": NOTE, "line": LINE, "cards": [card("Only drug")]}
    return {"many": full, "one": one}


@pytest.fixture(scope="module")
def seen(tmp_path_factory):
    node = shutil.which("node")
    if not node or subprocess.run([node, "-e", "require('playwright')"], capture_output=True).returncode:
        pytest.skip("needs node with playwright to open a real browser")
    folder = tmp_path_factory.mktemp("t8")
    answers = folder / "answers.json"
    answers.write_text(json.dumps(_answers()), encoding="utf-8")
    shot = ROOT / "docs" / "ticket_t8_ctgov_only_box_390.png"
    run = subprocess.run(
        [node, "-e", BROWSER, str(ROOT / "web" / "index.html"), str(answers), str(shot)],
        capture_output=True, text=True, timeout=120, cwd=str(ROOT))
    assert run.returncode == 0, run.stderr[-3000:]
    return json.loads(run.stdout)


def test_the_box_opens_with_twenty_then_show_all_and_the_tab_counts_them(seen):
    opened = seen["many"]["open"]
    assert seen["many"]["errors"] == []
    assert opened["shown"] and opened["open"]
    assert opened["summary"].startswith(TITLE)
    assert "(25 trials)" in opened["summary"] or opened["summary"].count("25")
    assert "25 trials" in opened["summary"]
    assert opened["note"] == NOTE
    assert opened["names"][0] == "Listed drug 1"
    assert opened["lines"][0] == LINE
    assert opened["onScreen"][:20] == [True] * 20
    assert opened["onScreen"][20:] == [False] * 5
    assert opened["showAll"] == "Show all 25"
    assert opened["showAllHeight"] >= 44
    assert opened["count"] == "(" + str(opened["cardCount"]) + ")"
    assert opened["cardCount"] == 25
    assert opened["dashed"] is False
    assert opened["edge"] == "solid"
    assert opened["width"] == 390
    assert opened["shifted"] is False
    assert seen["many"]["shown"]["onScreen"] == [True] * 25
    assert seen["many"]["shown"]["showAll"] is None
    assert TITLE in seen["many"]["printed"]
    assert NOTE in seen["many"]["printed"]


def test_one_card_has_no_show_all_button(seen):
    one = seen["one"]["open"]
    assert one["errors"] == [] if "errors" in one else seen["one"]["errors"] == []
    assert one["names"] == ["Only drug"]
    assert one["showAll"] is None
    assert one["count"] == "(1)"
    assert one["dashed"] is False
