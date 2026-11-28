"""Ticket R3. The "Recruiting now" panel on the In trials tab (layout A).

Saved answers only. The browser never reaches the network: every request is
answered here. Two widths: 390 (phone) and 1280 (desktop).

The PAH answer is the real one, saved in fixtures/recruiting_r3/pah.json from
moonlight/trials.sqlite (checked 2026-11-26). Every expected number and line
below is worked out here from that data, not read from the page.
"""

import copy
import json
import pathlib
import shutil
import subprocess

import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent
PAGE_FILE = ROOT / "web" / "index.html"
PAH_FILE = ROOT / "fixtures" / "recruiting_r3" / "pah.json"

PAH_ID = "MONDO_0015924"
CAUTION = "Not every trial is listed. This is not advice to join one."
GUIDE_LINE = ("Recruiting now. Trials the registry lists as recruiting. "
              "Not every trial is listed, and this is not advice to join one.")
THE = {"United States", "United Kingdom", "Netherlands", "Philippines"}


def trial(n, countries, title=None, phases=("PHASE2",)):
    nct = "NCT%08d" % n
    return {"nct_id": nct, "title": title or "Trial number %d" % n, "phases": list(phases),
            "countries": sorted(countries),
            "url": "https://clinicaltrials.gov/study/%s#contacts-and-locations" % nct}


def recruiting(trials, checked="2026-11-26"):
    counts = {}
    for item in trials:
        for name in set(item["countries"]):
            counts[name] = counts.get(name, 0) + 1
    return {"checked": checked, "total": len(trials),
            "countries": [{"name": n, "count": counts[n]} for n in sorted(counts)],
            "trials": trials}


def page(disease_id, name, rec):
    return {
        "disease": {"id": disease_id, "name": name},
        "about_disease": {"also_called": [], "description": ""},
        "rule_text": "Connections worth reading about, never treatments.",
        "approved": [{"id": "CHEMBL_A", "medicine": "Ambrisentan", "forms": ["Ambrisentan"],
                      "proteins": [{"symbol": "GENE1", "direction": "down", "points": 40}],
                      "reports": 3, "source": "https://example.test/a",
                      "first_approved": {"year": 2001, "region": "US"}}],
        "narrower": [], "wider_group": [], "wrong_approvals_box": [], "no_regulator_box": [],
        "new_clues": [],
        "being_studied": [{"id": "CHEMBL_T", "medicine": "Udenafil", "forms": ["Udenafil"],
                           "proteins": [{"symbol": "GENE1", "direction": "down", "points": 40}],
                           "reports": 2, "source": "https://example.test/t", "trial_phase": "Phase 2"}],
        "more_in_trials": [], "new_in_trials": [], "opposite_way_box": [], "wrong_way_line": "",
        "left_out": {"not_approved": 0, "unclear_link": 0},
        "recruiting": rec,
    }


def build_answers():
    pah = json.loads(PAH_FILE.read_text())
    many = [trial(i, ["United States", "Canada"] if i % 2 else ["France"]) for i in range(1, 413)]
    huge = [trial(i, ["United States", "Japan"] if i % 3 else ["Brazil"]) for i in range(1, 1241)]
    scenes = {
        "pah": ("MONDO_0015924", pah),
        "nous": ("MONDO_0000001", recruiting([trial(1, ["Canada", "Peru"]), trial(2, ["Germany"]),
                                                trial(3, ["Peru"])])),
        "one": ("MONDO_0000002", recruiting([trial(1, ["United States"])])),
        "onecountry": ("MONDO_0000003", recruiting([trial(1, ["Peru"]), trial(2, ["Peru"])])),
        "c412": ("MONDO_0000004", recruiting(many)),
        "c1240": ("MONDO_0000005", recruiting(huge)),
        "uk": ("MONDO_0000006", recruiting([trial(1, ["United Kingdom"]), trial(2, ["Netherlands"]),
                                             trial(3, ["Philippines", "Peru"])])),
        "null": ("MONDO_0000007", None),
        "zero": ("MONDO_0000008", recruiting([])),
    }
    answers = {}
    for key, (disease_id, rec) in scenes.items():
        answers[key] = page(disease_id, "pah", rec)
    # The same PAH page with no recruiting at all: the baseline "as on main".
    base = copy.deepcopy(answers["pah"])
    del base["recruiting"]
    base["disease"] = {"id": "MONDO_0000009", "name": "pah"}
    answers["main"] = base
    return answers


BROWSER_SCRIPT = r"""
"use strict";
const fs = require("fs");
const { chromium } = require("playwright");
const PAGE = fs.readFileSync(process.argv[1], "utf-8");
const ANSWERS = JSON.parse(fs.readFileSync(process.argv[2], "utf-8"));
const WIDTH = Number(process.argv[3]);
const SITE = "http://moonlight.test";
const BY_ID = {};
for (const [key, answer] of Object.entries(ANSWERS)) BY_ID[answer.disease.id] = answer;

function read() {
  const panel = document.getElementById("recruiting-panel");
  const shown = panel && panel.getClientRects().length > 0;
  const text = sel => { const el = document.querySelector(sel); return el ? el.textContent : null; };
  const tabs = document.querySelector('[data-slot="tabs"]').getBoundingClientRect();
  const h2 = document.querySelector("#panel-trials h2").getBoundingClientRect();
  const pick = document.getElementById("recruiting-country");
  const number = document.getElementById("recruiting-number");
  const heading = document.getElementById("recruiting-heading");
  const button = document.getElementById("recruiting-toggle");
  const rows = [...document.querySelectorAll("#recruiting-rows > li")].filter(li => li.getClientRects().length);
  const lineH = el => parseFloat(getComputedStyle(el).lineHeight) || parseFloat(getComputedStyle(el).fontSize) * 1.2;
  return {
    shown: Boolean(shown),
    inDom: Boolean(panel),
    top: shown ? panel.getBoundingClientRect().top : null,
    bottom: shown ? panel.getBoundingClientRect().bottom : null,
    tabsBottom: tabs.bottom,
    studiedTop: h2.top,
    dotShown: shown && Boolean(panel.querySelector(".r-dot")),
    heading: heading ? heading.textContent : null,
    headingLines: shown ? Math.round(heading.getBoundingClientRect().height / lineH(heading)) : null,
    number: number ? number.textContent : null,
    numberAria: number ? number.getAttribute("aria-hidden") : null,
    numberSize: shown ? getComputedStyle(number).fontSize : null,
    numberLines: shown ? Math.round(number.getBoundingClientRect().height / lineH(number)) : null,
    numberColor: shown ? getComputedStyle(number).color : null,
    label: shown ? document.querySelector('label[for="recruiting-country"]').textContent : null,
    pickerTag: pick ? pick.tagName : null,
    picked: pick && pick.options.length ? pick.options[pick.selectedIndex].value : null,
    options: pick ? [...pick.options].map(o => o.textContent) : [],
    fact: text("#recruiting-fact"),
    button: button ? button.textContent : null,
    buttonTag: button ? button.tagName : null,
    expanded: button ? button.getAttribute("aria-expanded") : null,
    caution: text("#recruiting-caution"),
    cautionShown: shown && document.getElementById("recruiting-caution").getClientRects().length > 0,
    rowsShown: rows.length,
    rows: rows.map(li => {
      const link = li.querySelector("a"), words = li.querySelector(".r-link");
      return {
        nct: li.querySelector(".r-nct").textContent,
        phase: li.querySelector(".r-phase") ? li.querySelector(".r-phase").textContent : "",
        title: li.querySelector(".r-title") ? li.querySelector(".r-title").textContent : "",
        countries: li.querySelector(".r-countries") ? li.querySelector(".r-countries").textContent : "",
        link: words ? words.textContent : null, linkWhole: link ? link.contains(words) : false, href: link ? link.getAttribute("href") : null,
        target: link ? link.getAttribute("target") : null, rel: link ? link.getAttribute("rel") : null,
        tag: link ? link.tagName : null,
      };
    }),
    showAll: document.getElementById("recruiting-show-all") && document.getElementById("recruiting-show-all").getClientRects().length > 0
      ? document.getElementById("recruiting-show-all").textContent : null,
    scrollWidth: document.documentElement.scrollWidth,
    clientWidth: document.documentElement.clientWidth,
    panelRight: shown ? panel.getBoundingClientRect().right : null,
    address: location.search + location.hash,
    storage: JSON.stringify([Object.keys(localStorage), Object.keys(sessionStorage)]),
    activeTab: document.querySelector('[role="tab"][aria-selected="true"]').dataset.tab,
    styles: shown ? (() => {
      const c = (id, p) => getComputedStyle(typeof id === "string" ? document.querySelector(id) : id)[p];
      const sel = document.getElementById("recruiting-country"), btn = button;
      const head = document.querySelector(".r-head"), list = document.getElementById("recruiting-list");
      const a = document.querySelector("#recruiting-rows .r-row");
      const o = {
        panelBg: c(panel, "backgroundColor"), panelBorder: c(panel, "borderTopWidth") + " " + c(panel, "borderTopColor"),
        radius: c(panel, "borderTopLeftRadius"), overflow: c(panel, "overflow"), color: c(panel, "color"),
        headPad: c(head, "padding"), headDir: c(head, "flexDirection"), headGap: c(head, "rowGap"),
        h2: [c(heading, "fontSize"), c(heading, "lineHeight"), c(heading, "letterSpacing"), c(heading, "margin")].join("|"),
        dot: (d => d.width + "x" + d.height)(panel.querySelector(".r-dot").getBoundingClientRect()) + " " + c(".r-dot", "backgroundColor") + " " + c(".r-dot", "borderRadius"),
        dotAria: panel.querySelector(".r-dot").getAttribute("aria-hidden"),
        dotGap: Math.round(heading.getBoundingClientRect().left - panel.querySelector(".r-dot").getBoundingClientRect().right),
        barGap: c(".r-bar", "columnGap"),
        count: [c(number, "fontWeight"), c(number, "lineHeight"), c(number, "letterSpacing"), c(number, "fontSize")].join("|"),
        fact: [c("#recruiting-fact", "fontSize"), c("#recruiting-fact", "lineHeight"), c("#recruiting-fact", "color"), c("#recruiting-fact", "marginTop")].join("|"),
        label: [c(".r-label", "fontSize"), c(".r-label", "color"), c(".r-label", "marginBottom")].join("|"),
        select: [c(sel, "minHeight"), c(sel, "backgroundColor"), c(sel, "borderTopWidth") + c(sel, "borderTopColor"), c(sel, "borderTopLeftRadius"), c(sel, "color"), c(sel, "fontSize"), c(sel, "padding")].join("|"),
        button: [c(btn, "minHeight"), c(btn, "borderTopWidth"), c(btn, "borderTopLeftRadius"), c(btn, "backgroundColor"), c(btn, "color"), c(btn, "fontSize"), c(btn, "fontWeight"), c(btn, "padding")].join("|"),
        controls: [c(".r-controls", "flexWrap"), c(".r-controls", "columnGap"), c(sel.parentElement, "flex"), c(btn, "flex")].join("|"),
        bottomsAligned: Math.abs(sel.getBoundingClientRect().bottom - btn.getBoundingClientRect().bottom) < 1,
        sideBySide: Math.abs(sel.getBoundingClientRect().top - btn.getBoundingClientRect().top) < 30 ? "side" : "stacked",
        caution: [c("#recruiting-caution", "fontSize"), c("#recruiting-caution", "lineHeight"), c("#recruiting-caution", "color"), c("#recruiting-caution", "marginTop")].join("|"),
        cautionLast: head.lastElementChild.id,
        tabsToPanel: Math.round(panel.getBoundingClientRect().top - tabs.bottom),
        headOverflow: head.scrollWidth - head.clientWidth,
      };
      if (!list.hidden && a) {
        const r1 = document.querySelector("#recruiting-rows li:nth-child(2)");
        o.list = [c(list, "backgroundColor"), c(list, "color"), c(list, "padding")].join("|");
        o.row = [a.tagName, c(a, "display"), c(a, "minHeight"), c(a, "paddingTop"), c(a, "textDecorationLine")].join("|");
        o.rowLine = r1 ? c(r1, "borderTopWidth") + " " + c(r1, "borderTopColor") : "";
        o.firstLine = c("#recruiting-rows li:first-child", "borderTopWidth");
        o.l1 = [c(".r-nct", "fontSize"), c(".r-nct", "fontWeight"), c(".r-nct", "color")].join("|");
        o.l1p = (e => e ? [c(e, "fontSize"), c(e, "fontWeight"), c(e, "color"), c(e, "whiteSpace")].join("|") : "")(document.querySelector(".r-phase"));
        o.l2 = [c(".r-title", "fontSize"), c(".r-title", "lineHeight"), c(".r-title", "color"), c(".r-title", "marginTop")].join("|");
        o.l3 = (e => e ? [c(e, "fontSize"), c(e, "color"), c(e, "marginTop")].join("|") : "")(document.querySelector(".r-countries"));
        o.l4 = [c(".r-link", "fontSize"), c(".r-link", "fontWeight"), c(".r-link", "color"), c(".r-link", "textDecorationLine"), c(".r-link", "textUnderlineOffset"), c(".r-link", "marginTop")].join("|");
        const sa = document.getElementById("recruiting-show-all");
        o.showAll = sa ? [c(sa, "width") === list.querySelector(".r-rows").getBoundingClientRect().width + "px", c(sa, "minHeight"), c(sa, "backgroundColor"), c(sa, "borderTopWidth") + c(sa, "borderTopColor"), c(sa, "borderTopLeftRadius"), c(sa, "color"), c(sa, "fontSize"), c(sa, "fontWeight"), c(sa, "marginTop")].join("|") : "";
      }
      return o;
    })() : null,
    approvedHtml: document.getElementById("panel-approved").outerHTML,
    cluesHtml: document.getElementById("panel-clues").outerHTML,
    studiedHtml: document.getElementById("panel-trials").outerHTML,
    tabsHtml: document.querySelector('[data-slot="tabs"]').outerHTML,
  };
}

async function open(browser, umami) {
  const context = await browser.newContext({ viewport: { width: WIDTH, height: 900 } });
  const page = await context.newPage();
  page.setDefaultTimeout(15000);
  const errors = [];
  page.on("pageerror", problem => errors.push(String(problem)));
  await context.route("**/*", route => {
    const url = route.request().url();
    if (url.includes("umami")) { umami.push(route.request().method() + " " + url); return route.abort(); }
    if (url === SITE + "/" || url.startsWith(SITE + "/?"))
      return route.fulfill({ contentType: "text/html; charset=utf-8", body: PAGE });
    if (url.startsWith(SITE + "/api/clues?")) {
      const id = new URL(url).searchParams.get("disease_id");
      return route.fulfill({ contentType: "application/json", body: JSON.stringify(BY_ID[id]) });
    }
    if (url.startsWith(SITE + "/api/version"))
      return route.fulfill({ contentType: "application/json", body: JSON.stringify({fingerprint: "0123456789ab"}) });
    if (url.startsWith("https://clinicaltrials.gov/"))
      return route.fulfill({ contentType: "text/html; charset=utf-8", body: "<!doctype html><title>Trial</title>" });
    return route.abort();
  });
  return { context, page, errors };
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
    const umami = [];
    const { context, page, errors } = await open(browser, umami);
    for (const key of Object.keys(ANSWERS)) {
      await gotoTab(page, ANSWERS[key].disease.id, "trials");
      out[key] = await page.evaluate(read);
    }
    // The other two tabs of PAH: the panel is not there.
    await gotoTab(page, ANSWERS.pah.disease.id, "approved");
    out.pahApprovedTab = await page.evaluate(read);
    await gotoTab(page, ANSWERS.pah.disease.id, "clues");
    out.pahCluesTab = await page.evaluate(read);

    // PAH again: change the country, open the list, watch Umami and the address.
    await gotoTab(page, ANSWERS.pah.disease.id, "trials");
    const requestsBefore = umami.length;
    const addressBefore = await page.evaluate(() => location.href);
    const historyBefore = await page.evaluate(() => history.length);
    out.pahChanges = [];
    for (const choice of ["Germany", "All countries", "United States"]) {
      await page.selectOption("#recruiting-country", { label: await page.evaluate(c => {
        const o = [...document.getElementById("recruiting-country").options].find(x => x.value === c || x.textContent.startsWith(c));
        return o.textContent; }, choice) });
      out.pahChanges.push(await page.evaluate(read));
    }
    await page.click("#recruiting-toggle");
    out.pahOpenUS = await page.evaluate(read);
    await page.selectOption("#recruiting-country", { value: "Germany" });
    out.pahOpenGermany = await page.evaluate(read);
    await page.selectOption("#recruiting-country", { value: "" });
    out.pahOpenAll = await page.evaluate(read);
    await page.click("#recruiting-show-all");
    out.pahOpenAllShown = await page.evaluate(read);
    out.umamiAfterChange = umami.length - requestsBefore;
    out.addressSame = addressBefore === await page.evaluate(() => location.href);
    out.historySame = historyBefore === await page.evaluate(() => history.length);

    // One trial: open it, the button says "Hide the trial".
    await gotoTab(page, ANSWERS.one.disease.id, "trials");
    await page.click("#recruiting-toggle");
    out.oneOpen = await page.evaluate(read);
    // The big fixtures on All countries.
    for (const key of ["c412", "c1240"]) {
      await gotoTab(page, ANSWERS[key].disease.id, "trials");
      await page.selectOption("#recruiting-country", { value: "" });
      out[key + "All"] = await page.evaluate(read);
    }
    // The "in the" countries.
    await gotoTab(page, ANSWERS.uk.disease.id, "trials");
    out.ukChoices = [];
    for (const c of ["United Kingdom", "Netherlands", "Philippines", "Peru"]) {
      await page.selectOption("#recruiting-country", { value: c });
      out.ukChoices.push(await page.evaluate(() => document.getElementById("recruiting-fact").textContent));
    }

    // Keyboard: Tab from the country picker to the button, Enter opens it.
    await gotoTab(page, ANSWERS.pah.disease.id, "trials");
    await page.focus("#recruiting-country");
    await page.keyboard.press("Tab");
    out.focusAfterTab = await page.evaluate(() => document.activeElement.id + ":" + document.activeElement.tagName);
    await page.keyboard.press("Enter");
    out.afterEnter = await page.evaluate(read);
    // The first row link is reachable with Tab and is an <a> with a href.
    await page.keyboard.press("Tab");
    out.focusRow = await page.evaluate(() => document.activeElement.tagName + ":" + (document.activeElement.getAttribute("href") || ""));
    // The link opens the registry in a new tab.
    const [popup] = await Promise.all([context.waitForEvent("page"),
      page.click("#recruiting-rows > li:first-child a")]);
    out.popupUrl = popup.url();
    await popup.close();

    // A new disease starts closed and back on United States (the choice lives only on the page).
    await gotoTab(page, ANSWERS.pah.disease.id, "trials");
    out.pahReopened = await page.evaluate(read);
    out.errors.push(...errors);
  } finally {
    await browser.close();
  }
  process.stdout.write(JSON.stringify(out));
})().catch(problem => { process.stderr.write(String(problem && problem.stack || problem)); process.exit(1); });
"""


def fact_place(name):
    return ("the " + name) if name in THE else name


def date_words(iso):
    months = ["January", "February", "March", "April", "May", "June", "July", "August",
              "September", "October", "November", "December"]
    y, m, d = iso.split("-")
    return "%d %s %s" % (int(d), months[int(m) - 1], y)


def commas(n):
    return "{:,}".format(n)


def expected_fact(rec, country):
    """The fact line worked out from the API data. country None = all countries."""
    day = date_words(rec["checked"])
    if country is None:
        n, m = rec["total"], len(rec["countries"])
        trial_words = "1 trial is" if n == 1 else commas(n) + " trials are"
        country_words = "1 country" if m == 1 else commas(m) + " countries"
        line = "%s recruiting in %s. Checked on %s." % (trial_words, country_words, day)
        if not any(c["name"] == "United States" for c in rec["countries"]):
            line = "No trial is recruiting in the United States. " + line
        return line
    n = next(c["count"] for c in rec["countries"] if c["name"] == country)
    trial_words = "1 trial is" if n == 1 else commas(n) + " trials are"
    return "%s recruiting in %s. Checked on %s." % (trial_words, fact_place(country), day)


def rows_for(rec, country):
    return [t for t in rec["trials"] if country is None or country in t["countries"]]


def countries_words(countries):
    names = sorted(countries)
    if len(names) > 3:
        more = len(names) - 3
        return "%s, %s, %s and %d more" % (names[0], names[1], names[2], more)
    if len(names) > 1:
        return ", ".join(names[:-1]) + " and " + names[-1]
    return "".join(names)


def phase_words(tokens):
    """As the trial rows elsewhere on the page say it: Phase 2, Phase 1/2, Early Phase 1."""
    found = [(t.startswith("EARLY_"), t[-1]) for t in tokens if "PHASE" in t]
    if found and not any(early for early, _ in found):
        return "Phase " + "/".join(n for _, n in found)
    return " / ".join(("Early " if early else "") + "Phase " + n for early, n in found)


@pytest.fixture(scope="module", params=[390, 1280], ids=["390px", "1280px"])
def seen(request, tmp_path_factory):
    node = shutil.which("node")
    if not node or subprocess.run([node, "-e", "require('playwright')"], capture_output=True).returncode:
        pytest.skip("needs node with playwright to open a real browser")
    answers = build_answers()
    path = tmp_path_factory.mktemp("r3") / "answers.json"
    path.write_text(json.dumps(answers))
    run = subprocess.run([node, "-e", BROWSER_SCRIPT, str(PAGE_FILE), str(path), str(request.param)],
                         capture_output=True, text=True, timeout=240)
    assert run.returncode == 0, run.stderr
    out = json.loads(run.stdout)
    out["_answers"] = answers
    out["_width"] = request.param
    return out


def rec_of(seen, key):
    return seen["_answers"][key]["recruiting"]


def test_no_page_errors(seen):
    assert seen["errors"] == []


def test_pah_panel_is_under_the_tabs_above_already_being_studied(seen):
    p = seen["pah"]
    assert p["shown"] and p["activeTab"] == "trials"
    assert p["tabsBottom"] <= p["top"] <= p["tabsBottom"] + 40  # directly under the tab bar
    assert p["bottom"] <= p["studiedTop"]


def test_pah_opens_on_united_states_and_agrees_with_the_api(seen):
    rec, p = rec_of(seen, "pah"), seen["pah"]
    assert p["label"] == "Country" and p["pickerTag"] == "SELECT"
    assert p["picked"] == "United States"
    us = next(c["count"] for c in rec["countries"] if c["name"] == "United States")
    assert p["number"] == str(us)
    assert p["fact"] == expected_fact(rec, "United States")
    assert p["options"] == ["%s (%s)" % (c["name"], commas(c["count"])) for c in rec["countries"]] + \
        ["All countries (%s)" % commas(rec["total"])]
    assert p["heading"] == "Recruiting now" and p["dotShown"]
    assert p["numberAria"] == "true"
    assert p["caution"] == CAUTION and p["cautionShown"]
    assert p["button"] == "See the trials" and p["expanded"] == "false" and p["buttonTag"] == "BUTTON"
    assert p["rowsShown"] == 0  # closed: no rows showing


def test_pah_open_rows_match_the_api_for_united_states(seen):
    rec, p = rec_of(seen, "pah"), seen["pahOpenUS"]
    want = rows_for(rec, "United States")
    assert p["button"] == "Hide the trials" and p["expanded"] == "true"
    assert p["rowsShown"] == min(20, len(want))
    for row, item in zip(p["rows"], want):
        assert row["nct"] == item["nct_id"]
        assert row["phase"] == phase_words(item["phases"])
        assert row["title"] == item["title"]
        assert row["countries"] == countries_words(item["countries"])
        assert row["link"] == "Sites and contacts on ClinicalTrials.gov"
        assert row["href"] == item["url"]
        assert row["target"] == "_blank" and "noopener" in row["rel"] and row["tag"] == "A"
    assert p["showAll"] == ("Show all %d" % len(want) if len(want) > 20 else None)


def test_pah_open_all_countries_shows_first_20_then_show_all(seen):
    rec, p = rec_of(seen, "pah"), seen["pahOpenAll"]
    assert p["picked"] == "" and p["number"] == str(rec["total"])
    assert p["fact"] == expected_fact(rec, None)
    assert p["rowsShown"] == 20 and p["showAll"] == "Show all %d" % rec["total"]
    assert seen["pahOpenAllShown"]["rowsShown"] == rec["total"]
    assert seen["pahOpenAllShown"]["showAll"] is None


def test_changing_the_country_changes_number_fact_and_rows_and_sends_nothing(seen):
    rec = rec_of(seen, "pah")
    germany, all_, us = seen["pahChanges"]
    de = next(c["count"] for c in rec["countries"] if c["name"] == "Germany")
    assert germany["number"] == str(de) and germany["fact"] == expected_fact(rec, "Germany")
    assert all_["number"] == str(rec["total"]) and all_["fact"] == expected_fact(rec, None)
    assert us["fact"] == expected_fact(rec, "United States")
    g = seen["pahOpenGermany"]
    assert g["rowsShown"] == de
    assert [r["nct"] for r in g["rows"]] == [t["nct_id"] for t in rows_for(rec, "Germany")]
    assert seen["umamiAfterChange"] == 0
    assert seen["addressSame"] and seen["historySame"]
    assert seen["pahOpenAll"]["storage"] == "[[],[]]"


def test_a_new_visit_starts_closed_on_united_states_again(seen):
    p = seen["pahReopened"]
    assert p["picked"] == "United States" and p["expanded"] == "false" and p["rowsShown"] == 0


def test_no_us_trials_opens_on_all_countries_with_the_extra_sentence(seen):
    rec, p = rec_of(seen, "nous"), seen["nous"]
    assert p["picked"] == "" and p["number"] == "3"
    assert p["fact"] == expected_fact(rec, None)
    assert p["fact"].startswith("No trial is recruiting in the United States. 3 trials are recruiting in 3 countries.")
    assert p["fact"] == ("No trial is recruiting in the United States. "
                         "3 trials are recruiting in 3 countries. Checked on 26 November 2026.")


def test_one_trial_words(seen):
    p = seen["one"]
    assert p["number"] == "1" and p["numberSize"] == "54px"
    assert p["fact"] == "1 trial is recruiting in the United States. Checked on 26 November 2026."
    assert p["button"] == "See the trial"


def test_one_trial_open_button_says_hide_the_trial(seen):
    # A fixture with one trial, opened by the same keyboard path as PAH's.
    assert seen["oneOpen"]["button"] == "Hide the trial"


def test_all_countries_with_one_country_says_1_country(seen):
    p = seen["onecountry"]
    assert p["picked"] == ""  # no US trials: opens on All countries
    assert p["fact"] == ("No trial is recruiting in the United States. "
                         "2 trials are recruiting in 1 country. Checked on 26 November 2026.")


def test_the_in_the_countries(seen):
    p = seen["uk"]
    assert p["picked"] == ""
    assert "United Kingdom (1)" in p["options"] and "Philippines (1)" in p["options"]
    assert seen["ukChoices"] == [
        "1 trial is recruiting in the United Kingdom. Checked on 26 November 2026.",
        "1 trial is recruiting in the Netherlands. Checked on 26 November 2026.",
        "1 trial is recruiting in the Philippines. Checked on 26 November 2026.",
        "1 trial is recruiting in Peru. Checked on 26 November 2026."]


@pytest.mark.parametrize("key,size,number,fact", [
    ("c412", "44px", "206", "206 trials are recruiting in the United States. Checked on 26 November 2026."),
    ("c1240", "44px", "827", "827 trials are recruiting in the United States. Checked on 26 November 2026."),
    ("pah", "54px", "21", "21 trials are recruiting in the United States. Checked on 26 November 2026."),
])
def test_number_size_by_digits(seen, key, size, number, fact):
    p = seen[key]
    assert p["numberSize"] == size and p["number"] == number and p["fact"] == fact


def test_the_whole_count_sizes(seen):
    # Whole counts, via All countries, on the three big fixtures: 412 -> 44px, 1,240 -> 34px.
    assert seen["c412All"]["number"] == "412" and seen["c412All"]["numberSize"] == "44px"
    assert seen["c1240All"]["number"] == "1,240" and seen["c1240All"]["numberSize"] == "34px"
    assert seen["c1240All"]["fact"] == ("1,240 trials are recruiting in 3 countries. "
                                        "Checked on 26 November 2026.")
    assert seen["c412All"]["numberSize"] != seen["c1240All"]["numberSize"]


@pytest.mark.parametrize("key", ["pah", "one", "c412", "c1240", "c412All", "c1240All", "nous", "pahOpenAll"])
def test_head_does_not_wrap_and_page_does_not_scroll_sideways(seen, key):
    p = seen[key]
    assert p["headingLines"] == 1 and p["numberLines"] == 1
    assert p["scrollWidth"] <= seen["_width"] and p["scrollWidth"] == p["clientWidth"]
    assert p["panelRight"] <= p["clientWidth"]


@pytest.mark.parametrize("key", ["null", "zero", "main"])
def test_no_panel_when_recruiting_is_null_or_total_zero(seen, key):
    p = seen[key]
    assert p["shown"] is False


def test_tab_is_exactly_as_on_main_with_no_panel(seen):
    # With recruiting null or total 0 the page is main's page; with a panel the three tabs
    # and the tab bar are still byte for byte the same (the panel sits outside them).
    base = seen["main"]
    assert base["shown"] is False
    for part in ("approvedHtml", "cluesHtml", "studiedHtml", "tabsHtml"):
        assert seen["pah"][part] == base[part], part


def test_panel_is_only_on_the_in_trials_tab(seen):
    assert seen["pahApprovedTab"]["shown"] is False
    assert seen["pahCluesTab"]["shown"] is False


def test_button_and_rows_are_real_elements_reachable_by_keyboard(seen):
    assert seen["focusAfterTab"] == "recruiting-toggle:BUTTON"
    assert seen["afterEnter"]["expanded"] == "true" and seen["afterEnter"]["rowsShown"] > 0
    assert seen["focusRow"].startswith("A:https://clinicaltrials.gov/study/")
    assert seen["popupUrl"].startswith("https://clinicaltrials.gov/study/")
    assert seen["popupUrl"].endswith("#contacts-and-locations")


def test_the_guide_line_follows_trials():
    text = PAGE_FILE.read_text()
    start = text.index("<summary id=\"guide-facts-title\">")
    block = text[start:text.index("</details>", start)]
    items = [line for line in block.splitlines() if "<li><div><b>" in line]
    assert items[1].startswith("          <li><div><b>Trials.</b>")
    plain = lambda line: line.replace("</b> <span>", " ").replace("<li><div><b>", "").replace("</span></div></li>", "").strip()
    assert plain(items[2]) == GUIDE_LINE
    assert len(items) == 7  # the six old lines and one new line


def test_panel_styles_are_the_spec(seen):
    p = seen["pah"]["styles"]
    assert p["panelBg"] == "rgb(16, 31, 49)" and p["panelBorder"] == "1px rgb(16, 31, 49)"
    assert p["radius"] == "16px" and p["overflow"] == "hidden" and p["color"] == "rgb(245, 240, 232)"
    assert p["headPad"] == "20px 18px 18px" and p["headDir"] == "column" and p["headGap"] == "12px"
    assert p["h2"].startswith("26px|29.9px|-0.78px|0px")
    assert p["dot"] == "11x11 rgb(233, 180, 91) 50%" and p["dotAria"] == "true" and p["dotGap"] == 10
    assert p["barGap"] == "12px"
    assert p["count"] == "700|48.6px|-2.16px|54px"  # bold, line-height .9, letter-spacing -.04em
    assert p["fact"] == "16px|23.2px|rgb(245, 240, 232)|0px"
    assert p["label"] == "12px|rgb(196, 210, 217)|5px"
    assert p["select"] == "48px|rgb(255, 255, 255)|1pxrgb(199, 215, 217)|10px|rgb(16, 31, 49)|16px|8px 10px"
    assert p["button"] == "48px|0px|10px|rgb(245, 240, 232)|rgb(16, 31, 49)|16px|700|10px 16px"
    assert p["controls"] == "wrap|12px|1 1 220px|1 1 220px"
    assert p["bottomsAligned"] or seen["_width"] == 390  # side by side: bottom-aligned
    assert p["sideBySide"] == ("stacked" if seen["_width"] == 390 else "side")
    assert p["caution"] == "12px|18px|rgb(196, 210, 217)|0px" and p["cautionLast"] == "recruiting-caution"
    assert p["tabsToPanel"] == 22
    assert p["headOverflow"] <= 0


def test_open_list_styles_are_the_spec(seen):
    p = seen["pahOpenAll"]["styles"]
    assert p["list"] == "rgb(255, 255, 255)|rgb(16, 31, 49)|0px 14px 14px"
    assert p["row"] == "A|block|44px|10px|none"
    assert p["rowLine"] == "1px rgb(213, 224, 226)" and p["firstLine"] == "0px"
    assert p["l1"] == "13px|700|rgb(40, 125, 124)"
    assert p["l1p"] == "12px|700|rgb(83, 96, 108)|nowrap"
    assert p["l2"] == "13px|18.85px|rgb(16, 31, 49)|3px"
    assert p["l3"] == "12px|rgb(86, 104, 119)|2px"
    assert p["l4"].startswith("13px|650|rgb(40, 125, 124)|underline|3px|6px")
    assert p["showAll"] == "true|44px|rgb(255, 255, 255)|1pxrgb(169, 202, 203)|9px|rgb(40, 125, 124)|14px|700|12px"
    for row in seen["pahOpenAll"]["rows"]:
        assert row["linkWhole"]  # the whole row is the one <a>


def test_head_of_every_size_fits_inside_the_panel(seen):
    for key in ("one", "c412", "c1240", "c1240All", "c412All"):
        assert seen[key]["styles"]["headOverflow"] <= 0, key
