"""Ticket 3.27. The address and the Back button.

A search writes ?disease=<id>&tab=approved as a new step. Switching tabs
updates &tab= without a new step. Back and Forward restore the disease and
the tab. A link that carries &tab= scrolls so the tab bar sits at the top;
a normal search does not jump. The A-to-Z parameter (order=az) stays.
A trial row still opens in this same tab, and Back brings the disease back
from the address.

Saved answers only. The browser never reaches the network: every request is
answered here. The phone width is 390.
"""

import json
import pathlib
import shutil
import subprocess

import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent
PAGE_FILE = ROOT / "web" / "index.html"

PAH = "MONDO_0015924"
PSC = "MONDO_0018646"
TRIAL_URL = "https://clinicaltrials.gov/study/NCT01234567"
LONG = "This line is only here so the page is tall enough to scroll. " * 16


def protein():
    return {"symbol": "GENE1", "direction": "down", "points": 40}


def approved(name):
    return {
        "id": "CHEMBL_" + name,
        "medicine": name,
        "forms": [name],
        "proteins": [protein()],
        "reports": 3,
        "source": "https://example.test/approved",
        "first_approved": {"year": 2001, "region": "US"},
    }


def studied(name, with_row):
    card = {
        "id": "CHEMBL_T_" + name,
        "medicine": name,
        "forms": [name],
        "proteins": [protein()],
        "reports": 2,
        "source": "https://example.test/trial",
        "trial_phase": "Phase 2",
        "ending": LONG,
    }
    if with_row:
        card["studies"] = [{
            "nct_id": "NCT01234567",
            "phases": ["PHASE2"],
            "status": "Recruiting",
            "end": "",
            "role": "Tested",
            "url": TRIAL_URL,
        }]
    return card


def page(disease_id, name, approved_name, trial_name):
    return {
        "disease": {"id": disease_id, "name": name},
        "about_disease": {"also_called": [], "description": ""},
        "rule_text": "Connections worth reading about, never treatments.",
        "approved": [approved(approved_name)],
        "narrower": [],
        "wider_group": [],
        "wrong_approvals_box": [],
        "no_regulator_box": [],
        "new_clues": [],
        "being_studied": [
            studied(trial_name, True),
            studied(trial_name + " two", False),
            studied(trial_name + " three", False),
        ],
        "more_in_trials": [],
        "new_in_trials": [],
        "opposite_way_box": [],
        "wrong_way_line": "",
        "left_out": {"not_approved": 0, "unclear_link": 0},
    }


ANSWERS = {
    PAH: page(PAH, "pulmonary arterial hypertension", "Ambrisentan", "Udenafil"),
    PSC: page(PSC, "primary sclerosing cholangitis", "Ursodiol", "Vancomycin"),
}


BROWSER_SCRIPT = r"""
"use strict";
const fs = require("fs");
const { chromium } = require("playwright");
const PAGE = fs.readFileSync(process.argv[1], "utf-8");
const ANSWERS = JSON.parse(fs.readFileSync(process.argv[2], "utf-8"));
const SITE = "http://moonlight.test";
const PAH = "MONDO_0015924";
const PSC = "MONDO_0018646";

function read() {
  const names = sel => [...document.querySelectorAll(sel)].map(el => el.textContent);
  const tabButton = document.querySelector('[role="tab"][aria-selected="true"]');
  const tabs = document.querySelector('[data-slot="tabs"]');
  const search = document.getElementById("disease-search");
  const az = document.querySelector('#order-switch button[data-order="az"]');
  const row = document.querySelector("#studied-cards .study-row");
  return {
    title: document.getElementById("disease-title").textContent,
    tab: tabButton ? tabButton.dataset.tab : null,
    approved: names("#approved-cards > .card [data-slot='medicine-name']"),
    trials: names("#studied-cards > .card [data-slot='medicine-name']"),
    address: location.search,
    y: window.scrollY,
    searchTop: search.getBoundingClientRect().top,
    tabTop: tabs.getBoundingClientRect().top,
    safety: document.querySelector(".safety").getBoundingClientRect().height,
    resultsHidden: document.getElementById("results").hidden,
    homeHidden: document.getElementById("home").hidden,
    history: history.length,
    azPressed: az ? az.getAttribute("aria-pressed") : null,
    switchShown: document.getElementById("order-switch").getClientRects().length > 0,
    rowTarget: row ? row.getAttribute("target") : "missing",
  };
}

async function open(browser) {
  const context = await browser.newContext({ viewport: { width: 390, height: 844 } });
  const page = await context.newPage();
  page.setDefaultTimeout(15000);
  const errors = [];
  page.on("pageerror", problem => errors.push(String(problem)));
  await context.route("**/*", route => {
    const url = route.request().url();
    if (url === SITE + "/" || url.startsWith(SITE + "/?"))
      return route.fulfill({ contentType: "text/html; charset=utf-8", body: PAGE });
    if (url.startsWith(SITE + "/api/search?")) {
      const q = new URL(url).searchParams.get("q").toLowerCase();
      const matches = Object.values(ANSWERS)
        .map(answer => answer.disease)
        .filter(disease => disease.name.toLowerCase().includes(q));
      return route.fulfill({
        contentType: "application/json",
        body: JSON.stringify({matches, did_you_mean: [], also_called: {}}),
      });
    }
    if (url.startsWith(SITE + "/api/clues?")) {
      const id = new URL(url).searchParams.get("disease_id");
      return route.fulfill({ contentType: "application/json", body: JSON.stringify(ANSWERS[id]) });
    }
    if (url.startsWith(SITE + "/api/version"))
      return route.fulfill({ contentType: "application/json", body: JSON.stringify({fingerprint: "0123456789ab"}) });
    if (url.startsWith("https://clinicaltrials.gov/"))
      return route.fulfill({ contentType: "text/html; charset=utf-8", body: "<!doctype html><title>Trial</title><p>Trial page</p>" });
    return route.abort();
  });
  return { context, page, errors };
}

async function searchFor(page, text) {
  await page.fill("#disease-search", text);
  await page.click('#search-form button[type="submit"]');
  await page.waitForSelector("#disease-matches button");
  const before = await page.evaluate(read);
  await page.click("#disease-matches button");
  await page.waitForSelector("#found", { state: "visible" });
  await page.waitForTimeout(400);
  const after = await page.evaluate(read);
  return { before, after };
}

async function shown(page, words) {
  await page.waitForFunction(wanted => {
    const title = document.getElementById("disease-title");
    return title && title.textContent.indexOf(wanted) !== -1;
  }, words);
  return page.evaluate(read);
}

(async () => {
  const browser = await chromium.launch();
  const out = { errors: [] };
  try {
    const { context, page, errors } = await open(browser);
    out.errors.push(...errors);
    await page.goto(SITE + "/");
    const first = await searchFor(page, "pulmonary");
    out.search = first.after;
    out.search.beforeY = first.before.y;
    out.search.beforeSearchTop = first.before.searchTop;
    out.search.historyBefore = first.before.history;

    const freshPage = await context.newPage();
    const freshErrors = [];
    freshPage.on("pageerror", problem => freshErrors.push(String(problem)));
    freshPage.setDefaultTimeout(15000);
    await freshPage.goto(page.url());
    await freshPage.waitForSelector("#found", { state: "visible" });
    await freshPage.waitForTimeout(400);
    out.fresh = await freshPage.evaluate(read);
    out.errors.push(...freshErrors);
    await freshPage.close();

    await page.click("#tab-trials");
    await page.waitForTimeout(100);
    out.tab = await page.evaluate(read);

    const second = await searchFor(page, "sclerosing");
    out.second = second.after;
    await page.click("#tab-clues");
    await page.waitForTimeout(100);
    out.secondTab = await page.evaluate(read);

    await page.goBack();
    out.back = await shown(page, "Pulmonary");
    await page.goForward();
    out.forward = await shown(page, "Primary");

    await page.goBack();
    await shown(page, "Pulmonary");
    await page.waitForSelector("#studied-cards .study-row", { state: "visible" });
    out.trial = { target: await page.evaluate(() => {
      const row = document.querySelector("#studied-cards .study-row");
      return row ? row.getAttribute("target") : "missing";
    }), pagesBefore: page.context().pages().length };
    await Promise.all([
      page.waitForURL(/clinicaltrials\.gov/),
      page.click("#studied-cards .study-row"),
    ]);
    out.trial.left = page.url();
    out.trial.pages = page.context().pages().length;
    await page.goBack();
    out.trial.back = await shown(page, "Pulmonary");

    const linkPage = await context.newPage();
    const linkErrors = [];
    linkPage.on("pageerror", problem => linkErrors.push(String(problem)));
    linkPage.setDefaultTimeout(15000);
    await linkPage.goto(SITE + "/?disease=" + PAH + "&tab=trials");
    await linkPage.waitForSelector("#found", { state: "visible" });
    let last = null;
    for (let tries = 0; tries < 40; tries++) {
      await linkPage.waitForTimeout(50);
      const now = await linkPage.evaluate(() => document.querySelector('[data-slot="tabs"]').getBoundingClientRect().top);
      if (last !== null && Math.abs(now - last) < 0.5) break;
      last = now;
    }
    out.link = await linkPage.evaluate(read);
    out.errors.push(...linkErrors);

    await context.close();

    const order = await open(browser);
    out.errors.push(...order.errors);
    await order.page.goto(SITE + "/?disease=" + PAH + "&order=az");
    await order.page.waitForSelector("#found", { state: "visible" });
    await order.page.waitForTimeout(300);
    const opened = await order.page.evaluate(read);
    await order.page.click("#tab-trials");
    const switched = await order.page.evaluate(read);
    // The switch lives on the Approved tab, so come back before tapping it.
    await order.page.click("#tab-approved");
    await order.page.click('#order-switch button[data-order="newest"]');
    const newest = await order.page.evaluate(read);
    await order.page.click('#order-switch button[data-order="az"]');
    const again = await order.page.evaluate(read);
    const searched = await searchFor(order.page, "sclerosing");
    out.order = { opened, switched, newest, again, searched: searched.after };
    await order.context.close();
  } catch (problem) {
    out.scriptError = String(problem && problem.stack || problem);
  }
  await browser.close();
  console.log(JSON.stringify(out));
})().catch(problem => { console.error(problem); process.exit(1); });
"""


@pytest.fixture(scope="module")
def seen(tmp_path_factory):
    node = shutil.which("node")
    if not node or subprocess.run(
            [node, "-e", "require('playwright')"], capture_output=True).returncode:
        pytest.skip("needs node with playwright to open a real browser")
    folder = tmp_path_factory.mktemp("address_back_3_27")
    answers = folder / "answers.json"
    answers.write_text(json.dumps(ANSWERS), encoding="utf-8")
    run = subprocess.run(
        [node, "-e", BROWSER_SCRIPT, str(PAGE_FILE), str(answers)],
        capture_output=True, text=True, timeout=180, cwd=str(ROOT))
    assert run.returncode == 0, run.stderr[-4000:]
    out = json.loads(run.stdout)
    assert "scriptError" not in out, out["scriptError"]
    assert out["errors"] == []
    return out


def test_browser_a_search_writes_the_disease_and_the_approved_tab_as_a_new_step(seen):
    search = seen["search"]
    assert search["address"] == "?disease=%s&tab=approved" % PAH
    assert search["tab"] == "approved"
    assert "Pulmonary" in search["title"]
    assert search["history"] == search["historyBefore"] + 1


def test_browser_opening_the_copied_address_fresh_shows_the_same_page(seen):
    fresh, search = seen["fresh"], seen["search"]
    assert fresh["address"] == search["address"]
    assert fresh["title"] == search["title"]
    assert fresh["tab"] == search["tab"]
    assert fresh["approved"] == search["approved"]
    assert fresh["trials"] == search["trials"]


def test_browser_a_normal_search_does_not_jump(seen):
    search = seen["search"]
    assert search["beforeY"] == 0
    assert search["y"] == 0
    assert 0 < search["searchTop"] < 600
    assert search["tabTop"] > 80


def test_browser_switching_tabs_updates_the_tab_without_a_new_step(seen):
    tab, search = seen["tab"], seen["search"]
    assert tab["history"] == search["history"]
    assert tab["tab"] == "trials"
    assert tab["address"] == "?disease=%s&tab=trials" % PAH


def test_browser_back_and_forward_restore_the_disease_and_the_tab(seen):
    assert "Pulmonary" in seen["back"]["title"]
    assert seen["back"]["tab"] == "trials"
    assert ("disease=%s" % PAH) in seen["back"]["address"]
    assert "tab=trials" in seen["back"]["address"]
    assert "Primary" in seen["forward"]["title"]
    assert seen["forward"]["tab"] == "clues"
    assert ("disease=%s" % PSC) in seen["forward"]["address"]
    assert "tab=clues" in seen["forward"]["address"]


def test_browser_a_second_search_writes_its_own_approved_step(seen):
    assert seen["second"]["address"] == "?disease=%s&tab=approved" % PSC
    assert seen["second"]["tab"] == "approved"
    assert "Primary" in seen["second"]["title"]
    assert seen["second"]["history"] == seen["tab"]["history"] + 1


def test_browser_a_trial_row_opens_in_the_same_tab_and_back_restores_the_disease(seen):
    trial = seen["trial"]
    assert trial["target"] is None
    assert trial["pages"] == trial["pagesBefore"] == 1
    assert trial["left"].startswith(TRIAL_URL)
    assert "Pulmonary" in trial["back"]["title"]
    assert trial["back"]["tab"] == "trials"
    assert ("disease=%s" % PAH) in trial["back"]["address"]


def test_browser_a_trials_link_puts_the_tab_bar_within_80px_of_the_top(seen):
    link = seen["link"]
    assert link["tab"] == "trials"
    assert "Pulmonary" in link["title"]
    assert ("tab=trials" in link["address"])
    assert 0 <= link["tabTop"] <= 80


def test_browser_the_a_to_z_parameter_is_kept(seen):
    order = seen["order"]
    assert order["opened"]["address"] == "?disease=%s&order=az" % PAH
    assert order["opened"]["switchShown"] is True
    assert order["opened"]["azPressed"] == "true"
    assert order["switched"]["address"] == "?disease=%s&order=az&tab=trials" % PAH
    assert order["newest"]["address"] == "?disease=%s&tab=approved" % PAH
    assert order["again"]["address"] == "?disease=%s&tab=approved&order=az" % PAH
    assert order["searched"]["address"] == "?disease=%s&tab=approved&order=az" % PSC
    assert order["searched"]["azPressed"] == "true"
    assert "Primary" in order["searched"]["title"]
