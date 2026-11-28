"""Ticket R4. Polish for the "Recruiting now" panel.

1. Chosen country first on each row's country line, then the others A to Z,
   then "and N more": three names in all. All countries: today's line.
2. The country picker takes the page font and the 3 px teal focus ring.
3. After "Show all", focus moves to the first newly shown item (Recruiting
   now list, "More medicines in trials", "New medicines being tested").
4. #recruiting-fact is aria-live="polite".
5. "How to read a card" is hidden while the Recruiting now panel is visible.

Saved answers only. The browser never reaches the network: every request is
answered here. Two widths: 390 (phone) and 1280 (desktop).

The PAH page is the saved answer of ticket 2.52 (48 cards in "More medicines
in trials", 27 in "New medicines being tested") with the real recruiting key
saved for ticket R3 (fixtures/recruiting_r3/pah.json, checked 2026-11-26).
Every expected line below is worked out here from that data.
"""

import copy
import json
import pathlib
import shutil
import subprocess

import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent
PAGE_FILE = ROOT / "web" / "index.html"
PAH_PAGE_FILE = ROOT / "fixtures" / "labels_read" / "2.52" / "page_answers" / "MONDO_0015924.clues.json"
PAH_RECRUITING_FILE = ROOT / "fixtures" / "recruiting_r3" / "pah.json"
FIRST = 20


def build_answers():
    pah = json.loads(PAH_PAGE_FILE.read_text(encoding="utf-8"))
    pah["disease"] = {"id": "MONDO_0015924", "name": pah["disease"]["name"]}
    pah["recruiting"] = json.loads(PAH_RECRUITING_FILE.read_text(encoding="utf-8"))
    # The same PAH page with no recruiting key at all: the page as on main.
    main = copy.deepcopy(pah)
    del main["recruiting"]
    main["disease"] = {"id": "MONDO_0000009", "name": pah["disease"]["name"]}
    # Disease free survival: the trials file holds no recruiting trial for it (total 0).
    dfs = copy.deepcopy(main)
    dfs["disease"] = {"id": "EFO_0000409", "name": "disease free survival"}
    dfs["recruiting"] = {"checked": "2026-11-26", "total": 0, "countries": [], "trials": []}
    return {"pah": pah, "main": main, "dfs": dfs}


BROWSER_SCRIPT = r"""
"use strict";
const fs = require("fs");
const { chromium } = require("playwright");
const PAGE = fs.readFileSync(process.argv[1], "utf-8");
const ANSWERS = JSON.parse(fs.readFileSync(process.argv[2], "utf-8"));
const WIDTH = Number(process.argv[3]);
const SITE = "http://moonlight.test";
const BY_ID = {};
for (const answer of Object.values(ANSWERS)) BY_ID[answer.disease.id] = answer;

function read() {
  const visible = el => Boolean(el) && el.getClientRects().length > 0;
  const help = document.querySelector(".card-help");
  const panel = document.getElementById("recruiting-panel");
  const tabs = document.querySelector('[data-slot="tabs"]').getBoundingClientRect();
  const rows = [...document.querySelectorAll("#recruiting-rows > li")].filter(visible);
  return {
    panelShown: visible(panel),
    helpShown: visible(help) && visible(help.querySelector("a")),
    helpHtml: help.outerHTML.replace(/ hidden(="")?/, ""),
    tabsToPanel: visible(panel) ? Math.round(panel.getBoundingClientRect().top - tabs.bottom) : null,
    activeTab: document.querySelector('[role="tab"][aria-selected="true"]').dataset.tab,
    picked: document.getElementById("recruiting-country").value,
    rows: rows.map(li => ({
      nct: li.querySelector(".r-nct").textContent,
      countries: li.querySelector(".r-countries") ? li.querySelector(".r-countries").textContent : "",
    })),
    fact: document.getElementById("recruiting-fact").textContent,
    factLive: document.getElementById("recruiting-fact").getAttribute("aria-live"),
    scrollWidth: document.documentElement.scrollWidth,
    clientWidth: document.documentElement.clientWidth,
    approvedHtml: document.getElementById("panel-approved").outerHTML,
    cluesHtml: document.getElementById("panel-clues").outerHTML,
    tabsHtml: document.querySelector('[data-slot="tabs"]').outerHTML,
  };
}

function ring(id) {
  const s = getComputedStyle(document.getElementById(id));
  return [s.outlineStyle, s.outlineWidth, s.outlineColor, s.outlineOffset].join("|");
}

/* What has focus: the tag, and where it sits among the items it belongs to. */
function focused() {
  const el = document.activeElement;
  const out = { tag: el.tagName, id: el.id };
  const li = el.closest("#recruiting-rows > li");
  if (li) { out.where = "recruiting"; out.index = [...li.parentElement.children].indexOf(li); out.nct = li.querySelector(".r-nct").textContent; out.isRowLink = el.classList.contains("r-row"); }
  for (const box of ["more-trials-cards", "new-trials-cards"]) {
    const list = document.getElementById(box);
    if (el.parentElement === list) { out.where = box; out.index = [...list.children].indexOf(el); out.name = el.querySelector('[data-slot="medicine-name"]').textContent; out.shown = el.checkVisibility(); }
  }
  return out;
}

async function open(browser) {
  const context = await browser.newContext({ viewport: { width: WIDTH, height: 900 } });
  const page = await context.newPage();
  page.setDefaultTimeout(15000);
  const errors = [], requests = [];
  page.on("pageerror", problem => errors.push(String(problem)));
  await context.route("**/*", route => {
    const url = route.request().url();
    requests.push(route.request().method() + " " + url);
    if (url.includes("umami")) return route.abort();
    if (url === SITE + "/" || url.startsWith(SITE + "/?"))
      return route.fulfill({ contentType: "text/html; charset=utf-8", body: PAGE });
    if (url.startsWith(SITE + "/api/clues?")) {
      const id = new URL(url).searchParams.get("disease_id");
      return route.fulfill({ contentType: "application/json", body: JSON.stringify(BY_ID[id]) });
    }
    if (url.startsWith(SITE + "/api/version"))
      return route.fulfill({ contentType: "application/json", body: JSON.stringify({fingerprint: "0123456789ab"}) });
    return route.abort();
  });
  return { context, page, errors, requests };
}

async function gotoTab(page, id, tab) {
  await page.goto(SITE + "/?disease=" + id + "&tab=" + tab);
  await page.waitForSelector("#found", { state: "visible" });
  await page.waitForTimeout(250);
}

(async () => {
  const browser = await chromium.launch();
  const out = { errors: [] };
  try {
    const { page, errors, requests } = await open(browser);
    const PAH = ANSWERS.pah.disease.id;
    for (const key of Object.keys(ANSWERS))
      for (const tab of ["trials", "approved", "clues"]) {
        await gotoTab(page, ANSWERS[key].disease.id, tab);
        out[key + ":" + tab] = await page.evaluate(read);
      }
    // Switching tabs on the page: the line comes and goes with the panel.
    await gotoTab(page, PAH, "approved");
    out.switched = [];
    for (const tab of ["trials", "approved", "trials", "clues"]) {
      await page.click("#tab-" + tab);
      await page.waitForTimeout(100);
      out.switched.push([tab, await page.evaluate(read)]);
    }

    // 1. Country lines. Open the list, show every row, then change the country.
    await gotoTab(page, PAH, "trials");
    const before = requests.length;
    await page.click("#recruiting-toggle");
    out.countries = {};
    for (const value of ["United States", "Portugal", "", "Germany"]) {
      await page.selectOption("#recruiting-country", { value });
      const all = await page.$("#recruiting-show-all");
      if (all) await all.click();
      out.countries[value] = await page.evaluate(read);
    }
    out.newRequests = requests.slice(before);

    // 2. The picker and the button: font, and the ring on keyboard focus.
    await gotoTab(page, PAH, "trials");
    out.fonts = await page.evaluate(() => [getComputedStyle(document.getElementById("recruiting-country")).fontFamily,
                                           getComputedStyle(document.getElementById("recruiting-toggle")).fontFamily]);
    out.bodyFont = await page.evaluate(() => getComputedStyle(document.body).fontFamily);
    out.panelTeal = await page.evaluate(() => {
      const probe = document.createElement("span");
      probe.style.color = "var(--teal)";
      document.getElementById("recruiting-panel").append(probe);
      const color = getComputedStyle(probe).color;
      probe.remove();
      return color;
    });
    await page.focus("#tab-trials");
    await page.keyboard.press("Tab");
    out.pickFocus = await page.evaluate(() => document.activeElement.id);
    out.pickRing = await page.evaluate(ring, "recruiting-country");
    await page.keyboard.press("Tab");
    out.buttonFocus = await page.evaluate(() => document.activeElement.id);
    out.buttonRing = await page.evaluate(ring, "recruiting-toggle");

    // 3. Enter on each "Show all": focus lands on the first newly shown item.
    await gotoTab(page, PAH, "trials");
    const before3 = requests.length;
    await page.click("#recruiting-toggle");
    out.recruitingShowAllText = await page.textContent("#recruiting-show-all");
    await page.focus("#recruiting-show-all");
    await page.keyboard.press("Enter");
    out.focusRecruiting = await page.evaluate(focused);
    out.recruitingAfter = await page.evaluate(read);
    for (const box of ["more-trials", "new-trials"]) {
      out[box + "Text"] = await page.textContent("#" + box + "-show-all");
      await page.focus("#" + box + "-show-all");
      await page.keyboard.press("Enter");
      out["focus:" + box] = await page.evaluate(focused);
      out[box + "Shown"] = await page.evaluate(b => [...document.querySelectorAll("#" + b + "-cards > .card")].filter(c => c.checkVisibility()).length, box);
    }
    out.newRequests3 = requests.slice(before3);
    out.after3 = await page.evaluate(read);
    out.errors.push(...errors);
  } finally {
    await browser.close();
  }
  process.stdout.write(JSON.stringify(out));
})().catch(problem => { process.stderr.write(String(problem && problem.stack || problem)); process.exit(1); });
"""


def countries_words(countries, chosen=None):
    """Chosen country first, then the others A to Z; three names, then "and N more"."""
    others = sorted(c for c in countries if c != chosen)
    names = ([chosen] if chosen in countries else []) + others
    if len(names) > 3:
        return "%s, %s, %s and %d more" % (names[0], names[1], names[2], len(names) - 3)
    if len(names) > 1:
        return ", ".join(names[:-1]) + " and " + names[-1]
    return "".join(names)


@pytest.fixture(scope="module", params=[390, 1280], ids=["390px", "1280px"])
def seen(request, tmp_path_factory):
    node = shutil.which("node")
    if not node or subprocess.run([node, "-e", "require('playwright')"], capture_output=True).returncode:
        pytest.skip("needs node with playwright to open a real browser")
    answers = build_answers()
    path = tmp_path_factory.mktemp("r4") / "answers.json"
    path.write_text(json.dumps(answers))
    run = subprocess.run([node, "-e", BROWSER_SCRIPT, str(PAGE_FILE), str(path), str(request.param)],
                         capture_output=True, text=True, timeout=240)
    assert run.returncode == 0, run.stderr
    out = json.loads(run.stdout)
    out["_answers"] = answers
    out["_width"] = request.param
    return out


def pah_trials(seen, country):
    rec = seen["_answers"]["pah"]["recruiting"]
    return [t for t in rec["trials"] if not country or country in t["countries"]]


def test_no_page_errors(seen):
    assert seen["errors"] == []


# ---- 1. Chosen country first ----

@pytest.mark.parametrize("country", ["United States", "Portugal", "Germany"])
def test_every_row_starts_with_the_chosen_country(seen, country):
    p = seen["countries"][country]
    want = pah_trials(seen, country)
    assert p["picked"] == country
    assert [r["nct"] for r in p["rows"]] == [t["nct_id"] for t in want]
    for row, item in zip(p["rows"], want):
        assert row["countries"].startswith(country), row
        assert row["countries"] == countries_words(item["countries"], country)


def test_the_tickets_examples(seen):
    us = {r["nct"]: r["countries"] for r in seen["countries"]["United States"]["rows"]}
    pt = {r["nct"]: r["countries"] for r in seen["countries"]["Portugal"]["rows"]}
    assert us["NCT07175038"] == "United States, Australia, Canada and 6 more"
    assert us["NCT07143448"] == "United States, Spain and United Kingdom"
    assert us["NCT06872112"] == "United States"  # only the chosen country: just that country
    # The ticket's Portugal example says "and 12 more"; no PAH trial has 15 countries.
    # The 14-country trial gives this, by the same rule.
    assert pt["NCT07365332"] == "Portugal, Argentina, Australia and 11 more"
    assert pt["NCT06317805"] == "Portugal, Argentina, Austria and 9 more"


def test_all_countries_lines_are_todays(seen):
    p = seen["countries"][""]
    want = pah_trials(seen, "")
    assert p["picked"] == "" and len(p["rows"]) == len(want) == 34
    for row, item in zip(p["rows"], want):
        assert row["countries"] == countries_words(item["countries"])  # plain A to Z, as R3


# ---- 2. The picker looks like the other controls ----

def test_the_picker_takes_the_page_font(seen):
    pick, button = seen["fonts"]
    assert pick == button and pick == seen["bodyFont"]


def test_the_picker_has_the_buttons_focus_ring(seen):
    assert seen["pickFocus"] == "recruiting-country" and seen["buttonFocus"] == "recruiting-toggle"
    assert seen["pickRing"] == seen["buttonRing"]
    style, width, color, offset = seen["pickRing"].split("|")
    assert (style, width, offset) == ("solid", "3px", "3px")
    assert color == seen["panelTeal"]  # the site's teal, as the panel sets it


def test_the_two_css_rules_name_select():
    text = PAGE_FILE.read_text(encoding="utf-8")
    assert "button,input,select{font:inherit}" in text
    assert ("a:focus-visible,button:focus-visible,input:focus-visible,select:focus-visible,"
            "summary:focus-visible{outline:3px solid var(--teal);outline-offset:3px}") in text


# ---- 3. Focus after "Show all" ----

def test_focus_after_show_all_in_recruiting_now(seen):
    want = pah_trials(seen, "United States")
    assert seen["recruitingShowAllText"] == "Show all %d" % len(want) == "Show all 21"
    f = seen["focusRecruiting"]
    assert f["tag"] != "BODY"
    assert f["where"] == "recruiting" and f["index"] == FIRST and f["isRowLink"] and f["tag"] == "A"
    assert f["nct"] == want[FIRST]["nct_id"]
    assert len(seen["recruitingAfter"]["rows"]) == 21


@pytest.mark.parametrize("box,list_key,total", [
    ("more-trials", "more_in_trials", 48), ("new-trials", "new_in_trials", 27)])
def test_focus_after_show_all_in_the_trial_boxes(seen, box, list_key, total):
    cards = seen["_answers"]["pah"][list_key]
    assert len(cards) == total and seen[box + "Text"] == "Show all %d" % total
    f = seen["focus:" + box]
    assert f["tag"] != "BODY"
    assert f["where"] == box + "-cards" and f["index"] == FIRST and f["shown"]
    assert f["name"] == cards[FIRST]["medicine"]
    assert seen[box + "Shown"] == total


# ---- 4. Screen readers ----

def test_the_fact_line_is_polite_live(seen):
    assert seen["pah:trials"]["factLive"] == "polite"
    assert 'id="recruiting-fact" aria-live="polite"' in PAGE_FILE.read_text(encoding="utf-8")


# ---- 5. "How to read a card" ----

def test_the_link_is_hidden_under_the_panel(seen):
    p = seen["pah:trials"]
    assert p["panelShown"] and not p["helpShown"]
    assert p["tabsToPanel"] == 22


@pytest.mark.parametrize("key", ["pah:approved", "pah:clues", "dfs:trials", "dfs:approved", "dfs:clues",
                                 "main:trials", "main:approved", "main:clues"])
def test_the_link_shows_where_there_is_no_panel(seen, key):
    p = seen[key]
    assert not p["panelShown"] and p["helpShown"]
    assert p["helpHtml"] == seen["main:trials"]["helpHtml"]  # not moved, not reworded


def test_the_link_follows_the_panel_when_switching_tabs(seen):
    got = [(tab, p["panelShown"], p["helpShown"]) for tab, p in seen["switched"]]
    assert got == [("trials", True, False), ("approved", False, True),
                   ("trials", True, False), ("clues", False, True)]


def test_the_link_text_and_place_are_unchanged():
    text = PAGE_FILE.read_text(encoding="utf-8")
    assert text.count('<p class="card-help"><a href="#guide-card" data-guide>How to read a card</a></p>') == 1
    assert text.index('id="recruiting-panel"') < text.index('class="card-help"') < text.index('id="panel-approved"')


# ---- Everywhere ----

def test_no_new_request_when_changing_country_opening_or_showing_all(seen):
    assert seen["newRequests"] == []
    assert seen["newRequests3"] == []


@pytest.mark.parametrize("key", ["pah:trials", "pah:approved", "pah:clues", "dfs:trials", "after3"])
def test_no_sideways_scroll(seen, key):
    p = seen[key]
    assert p["scrollWidth"] <= seen["_width"] and p["scrollWidth"] == p["clientWidth"]


@pytest.mark.parametrize("country", ["United States", "Portugal", "", "Germany"])
def test_no_sideways_scroll_with_every_row_open(seen, country):
    p = seen["countries"][country]
    assert p["scrollWidth"] <= seen["_width"] and p["scrollWidth"] == p["clientWidth"]


def test_approved_and_new_clues_tabs_are_unchanged(seen):
    for tab in ("approved", "clues"):
        for part in ("approvedHtml", "cluesHtml", "tabsHtml"):
            assert seen["pah:" + tab][part] == seen["main:" + tab][part], (tab, part)
