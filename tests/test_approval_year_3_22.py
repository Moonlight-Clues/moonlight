"""Ticket 3.22. "First approved: [year] ([region])" and a sort switch on the Approved tab.

Facts, not ranking. The year comes from a hand-written list,
moonlight/approval_years.json (Open Targets 26.09 has no usable approval
year, so Moonlight asks nobody; MAIN 4, 26 Nov). The API sends the main list
A to Z, exactly as before, plus first_approved on a card that has an entry.
The ORDER is chosen in the page only.

The words on the page are DRAFT until Kashish signs sheet rows W7 and W7b.
They live in one block (APPROVAL_WORDS in web/index.html); these tests read
that block instead of copying the words.

Saved answers and a three-entry hand-made list only. No network.
"""

import json
import pathlib
import re
import shutil
import subprocess
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from moonlight import api, approval_years, fetch

import test_narrower_box as saved_pages

ROOT = pathlib.Path(__file__).resolve().parent.parent
PAGE_FILE = ROOT / "web" / "index.html"
PAGE = PAGE_FILE.read_text(encoding="utf-8")

# Hand-made. Three entries, in the shape of moonlight/approval_years.json.
THREE = {
    "CHEMBL1": {"year": 2001, "region": "US", "source": "https://example.org/one"},
    "CHEMBL2": {"year": 2015, "region": "EU", "source": "https://example.org/two"},
    "CHEMBL3": {"year": 2001, "region": "JP"},
}


def read_as(entries):
    return patch.object(approval_years, "_read", return_value=entries)


# ---- the list file ----

def test_the_real_list_file_is_valid_json_and_loads():
    assert isinstance(json.loads(approval_years.FILE.read_text(encoding="utf-8")), dict)
    assert isinstance(approval_years.load(), dict)


def test_three_good_entries_load_as_they_are():
    with read_as(THREE):
        assert approval_years.load() == THREE


def test_a_bad_entry_is_skipped_and_the_good_ones_stay():
    bad = {**THREE, "B1": {"year": "2001", "region": "US"}, "B2": {"year": 2001},
           "B3": {"year": 2001, "region": " "}, "B4": {"year": True, "region": "US"},
           "B5": {"year": 1500, "region": "US"}, "B6": "2001",
           "B7": {"year": 2002, "region": "US", "source": "javascript:alert(1)"}}
    with read_as(bad):
        loaded = approval_years.load()
    assert set(loaded) == {"CHEMBL1", "CHEMBL2", "CHEMBL3", "B7"}
    assert "source" not in loaded["B7"]


def test_a_missing_or_wrong_shaped_file_means_no_lines_and_no_crash():
    for odd in ([], "x", None):
        with read_as(odd):
            assert approval_years.load() == {}
    with patch.object(approval_years, "_read", side_effect=OSError("gone")):
        assert approval_years.load() == {}
    with patch.object(approval_years, "_read", side_effect=ValueError("bad json")):
        assert approval_years.load() == {}


def test_no_open_targets_year_question_exists_and_the_old_two_are_untouched():
    import hashlib
    sha = lambda text: hashlib.sha256(text.encode("utf-8")).hexdigest()
    assert not hasattr(fetch, "APPROVAL_YEAR_QUERY")
    assert sha(fetch.TARGET_DRUGS_QUERY) == (
        "3ebc33d2a20cb8487c6241b37ed7103d9145c6b03a9f57dc186c9fd8bb453386")
    assert sha(fetch.DISEASE_DRUGS_QUERY) == (
        "50b87b5caab0b74f2dfa95d1b8d5d6330907eb0bf80185bd506ca7a7b2642008")


# ---- the API: the order is as it was, plus the year ----

def page_with(entries):
    with patch("moonlight.fetch._post_json", side_effect=saved_pages.saved_post_json), \
            patch("requests.post", side_effect=AssertionError("network used")), \
            read_as(entries):
        return saved_pages.clues_json(TestClient(api.app), saved_pages.PAH)


def test_api_with_an_empty_list_the_page_is_exactly_as_before():
    page = page_with({})
    assert all("first_approved" not in card for card in page["approved"])


def test_api_a_card_with_an_entry_carries_it_and_the_others_have_no_key():
    plain = page_with({})
    ids = [card["id"] for card in plain["approved"]]
    entries = {ids[0]: THREE["CHEMBL1"], ids[2]: THREE["CHEMBL3"], "NOT_ON_THE_PAGE": THREE["CHEMBL2"]}
    page = page_with(entries)
    assert page["approved"][0]["first_approved"] == THREE["CHEMBL1"]
    assert page["approved"][2]["first_approved"] == THREE["CHEMBL3"]
    assert [c["id"] for c in page["approved"] if "first_approved" in c] == [ids[0], ids[2]]


def test_api_the_order_and_every_other_part_are_unchanged_by_the_list():
    plain = page_with({})
    ids = [card["id"] for card in plain["approved"]]
    page = page_with({ids[-1]: THREE["CHEMBL2"], ids[1]: THREE["CHEMBL1"]})
    assert [c["id"] for c in page["approved"]] == ids  # still the API's order
    stripped = [{k: v for k, v in c.items() if k != "first_approved"} for c in page["approved"]]
    assert stripped == plain["approved"]
    assert {k: v for k, v in page.items() if k != "approved"} == \
        {k: v for k, v in plain.items() if k != "approved"}


def test_api_only_the_main_list_carries_the_year():
    plain = page_with({})
    everything = {c["id"]: THREE["CHEMBL1"] for part in ("approved", "narrower", "wider_group")
                  for c in plain.get(part, [])}
    page = page_with(everything)
    for part in ("narrower", "wider_group"):
        assert all("first_approved" not in c for c in page.get(part, []))
    assert all("first_approved" in c for c in page["approved"])


# ---- the page: the words block ----

def test_all_four_texts_are_in_one_block_with_the_exact_words():
    block = re.search(r"const APPROVAL_WORDS = \{(.*?)\n  \};", PAGE, re.S).group(1)
    lines = [line for line in block.split("\n") if line.strip()]
    assert [line.split(":")[0].strip() for line in lines] == ["card", "newest", "az", "note"]
    assert "DRAFT" not in block  # decided 26 Nov (revised ticket): the words are exact
    assert [line.split('"')[1] for line in lines] == [
        "First approved: {year} ({region})", "Newest approval first", "A to Z",
        "Newest approvals are listed first. Newer does not mean better."]


def test_the_heading_line_text_is_not_changed_by_this_ticket():
    assert "Nothing here says how well any of them works. Listed A to Z.</p>" in PAGE


# ---- the page, in a real browser ----

def draft_words():
    block = re.search(r"const APPROVAL_WORDS = \{(.*?)\n  \};", PAGE, re.S).group(1)
    return dict(re.findall(r'(\w+): "((?:[^"\\]|\\.)*)"', block))


BROWSER_SCRIPT = r"""
"use strict";
const fs = require("fs");
const { chromium } = require("playwright");
const PAGE = fs.readFileSync(process.argv[1], "utf-8");
const CASES = JSON.parse(fs.readFileSync(process.argv[2], "utf-8"));
const SITE = "http://moonlight.test";

function read() {
  const words = el => el.innerText.replace(/\s+/g, " ").trim();
  const names = sel => [...document.querySelectorAll(sel)].map(
    card => card.querySelector('[data-slot="medicine-name"]').textContent);
  const shown = id => document.getElementById(id).getClientRects().length > 0;
  const yearLine = card => { const el = card.querySelector('[data-slot="first-year"]');
    return el && el.getClientRects().length ? el.textContent : null; };
  const yearHref = card => { const a = card.querySelector('[data-slot="first-year"] a');
    return a && a.getClientRects().length ? a.href : null; };
  const lines = (document.querySelector("#panel-approved") || document.body).innerText;
  return {
    list: names("#approved-cards > .card"),
    years: [...document.querySelectorAll("#approved-cards > .card")].map(yearLine),
    hrefs: [...document.querySelectorAll("#approved-cards > .card")].map(yearHref),
    boxYears: [...document.querySelectorAll("#panel-approved details .card")].map(yearLine),
    narrower: names("#narrower-cards > .card"),
    wider: names("#wider-cards > .card"),
    red: names("#wrong-cards > .card"),
    noReg: names("#no-regulator-cards > .card"),
    heading: words(document.querySelector("#approved-list .tab-words")),
    noteShown: shown("order-note"),
    noteText: words(document.getElementById("order-note")),
    noteCount: (document.body.innerText.match(/Newer does not mean better/g) || []).length,
    switchShown: shown("order-switch"),
    buttons: [...document.querySelectorAll("#order-switch button")].map(
      b => [b.textContent, b.getAttribute("aria-pressed")]),
    switchesInBoxes: document.querySelectorAll("#panel-approved details #order-switch").length,
    tab: words(document.getElementById("tab-approved")),
    address: location.search,
    sideways: document.documentElement.scrollWidth > document.documentElement.clientWidth,
    fontPx: (() => { const el = [...document.querySelectorAll("#approved-cards [data-slot='first-year']")]
      .find(e => e.getClientRects().length); return el ? getComputedStyle(el).fontSize : null; })(),
  };
}

async function oneCase(browser, spec) {
  const context = await browser.newContext({ viewport: { width: 390, height: 844 } });
  const page = await context.newPage();
  const errors = [];
  page.on("pageerror", problem => errors.push(String(problem)));
  await context.route("**/*", route => {
    const url = route.request().url();
    if (url === SITE + "/" || url.startsWith(SITE + "/?"))
      return route.fulfill({ contentType: "text/html; charset=utf-8", body: PAGE });
    if (url.startsWith(SITE + "/api/clues?"))
      return route.fulfill({ contentType: "application/json", body: JSON.stringify(spec.answer) });
    return route.abort();
  });
  await page.goto(SITE + "/?disease=MONDO_TEST" + (spec.query || ""));
  await page.waitForSelector("#found", { state: "visible" });
  await page.waitForTimeout(300);
  const out = { errors, opened: await page.evaluate(read) };
  if (spec.clickAz) {
    await page.click('#order-switch button[data-order="az"]');
    out.az = await page.evaluate(read);
    await page.click('#order-switch button[data-order="newest"]');
    out.back = await page.evaluate(read);
  }
  await context.close();
  return out;
}

(async () => {
  const browser = await chromium.launch();
  const out = {};
  for (const name of Object.keys(CASES)) out[name] = await oneCase(browser, CASES[name]);
  await browser.close();
  console.log(JSON.stringify(out));
})().catch(problem => { console.error(problem); process.exit(1); });
"""

def main_places(page):
    """Places in page["approved"] of the cards the page draws in the main list (not in a box)."""
    boxed = set(page.get("wrong_approvals_box", [])) | set(page.get("no_regulator_box", []))
    return [place for place, card in enumerate(page["approved"]) if card["id"] not in boxed]


def with_entries(page, entries):
    """The PAH page with first_approved put on the n-th card of the MAIN list."""
    page = json.loads(json.dumps(page))
    places = main_places(page)
    for nth, entry in entries.items():
        page["approved"][places[nth]]["first_approved"] = entry
    return page


@pytest.fixture(scope="module")
def base_page():
    with patch("moonlight.fetch._post_json", side_effect=saved_pages.saved_post_json), \
            read_as({}):
        return saved_pages.clues_json(TestClient(api.app), saved_pages.PAH)


@pytest.fixture(scope="module")
def seen(base_page, tmp_path_factory):
    node = shutil.which("node")
    if not node or subprocess.run(
            [node, "-e", "require('playwright')"], capture_output=True).returncode:
        pytest.skip("needs node with playwright to open a real browser")
    assert len(main_places(base_page)) >= 6
    # Main-list places 0 (2001 US), 1 (2015 EU), 2 (2001 JP, ties with place 0), 3 (1999 US); the rest none.
    entries = {0: THREE["CHEMBL1"], 1: THREE["CHEMBL2"], 2: THREE["CHEMBL3"],
               3: {"year": 1999, "region": "US"}}
    cases = {
        "years": {"answer": with_entries(base_page, entries), "clickAz": True},
        "az": {"answer": with_entries(base_page, entries), "query": "&order=az"},
        "none": {"answer": base_page},
    }
    path = tmp_path_factory.mktemp("approval_year") / "cases.json"
    path.write_text(json.dumps(cases), encoding="utf-8")
    run = subprocess.run([node, "-e", BROWSER_SCRIPT, str(PAGE_FILE), str(path)],
                         capture_output=True, text=True, timeout=240, cwd=str(ROOT))
    assert run.returncode == 0, run.stderr[-3000:]
    out = json.loads(run.stdout)
    for name in cases:
        assert out[name]["errors"] == [], name
    return out


def test_browser_newest_first_is_the_default_ties_a_to_z_no_year_last_a_to_z(seen):
    # the main list is the API's list minus the cards in the boxes, so find the four by name
    opened = seen["years"]["opened"]["list"]
    api_order = seen["az"]["opened"]["list"]
    assert sorted(opened) == sorted(api_order)
    with_years = [name for name, year in zip(opened, seen["years"]["opened"]["years"]) if year]
    assert len(with_years) == 4
    assert opened[:4] == with_years                      # the four with years come first
    assert opened[4:] == [n for n in api_order if n not in with_years]  # then the rest, A to Z as sent
    order_years = [int(re.search(r"\d{4}", y).group()) for y in seen["years"]["opened"]["years"][:4]]
    assert order_years == [2015, 2001, 2001, 1999]
    tied = opened[1:3]
    assert tied == [n for n in api_order if n in tied]   # the tie keeps the API's A to Z


def test_browser_the_card_line_uses_the_words_block_with_year_and_region(seen):
    line = draft_words()["card"]
    years = seen["years"]["opened"]["years"]
    assert years[:4] == [line.replace("{year}", "2015").replace("{region}", "EU"),
                         line.replace("{year}", "2001").replace("{region}", "US"),
                         line.replace("{year}", "2001").replace("{region}", "JP"),
                         line.replace("{year}", "1999").replace("{region}", "US")]
    assert all(y is None for y in years[4:])
    # 2015 and the first 2001 have a source: the year is a link. The JP one and 1999 have none: plain text.
    assert seen["years"]["opened"]["hrefs"][:4] == [
        "https://example.org/two", "https://example.org/one", None, None]
    assert seen["years"]["opened"]["fontPx"] == "12px"


def test_browser_the_switch_has_two_options_newest_is_pressed_by_default(seen):
    words = draft_words()
    opened = seen["years"]["opened"]
    assert opened["switchShown"] is True
    assert opened["buttons"] == [[words["newest"], "true"], [words["az"], "false"]]


def test_browser_a_to_z_in_the_switch_puts_the_api_order_back_and_writes_the_address(seen):
    az = seen["years"]["az"]
    assert az["list"] == seen["az"]["opened"]["list"]
    assert "order=az" in az["address"] and "disease=MONDO_TEST" in az["address"]
    assert [b[1] for b in az["buttons"]] == ["false", "true"]
    back = seen["years"]["back"]
    assert back["list"] == seen["years"]["opened"]["list"]
    assert "order" not in back["address"]


def test_browser_the_address_order_az_opens_in_a_to_z(seen):
    opened = seen["az"]["opened"]
    assert opened["list"] == seen["none"]["opened"]["list"]  # as sent, A to Z
    assert [b[1] for b in opened["buttons"]] == ["false", "true"]


def test_browser_the_one_line_shows_once_above_the_switch_with_the_newest_order_only(seen):
    words = draft_words()
    opened = seen["years"]["opened"]
    assert opened["noteShown"] and opened["noteText"] == words["note"]
    assert opened["noteCount"] == 1
    assert not seen["az"]["opened"]["noteShown"]
    assert PAGE.index('id="order-note"') < PAGE.index('id="order-switch"')


def test_browser_the_note_replaces_listed_a_to_z_in_the_heading_while_newest_shows(seen):
    old = ("Already approved for this disease in at least one country, according to the "
           "database. Nothing here says how well any of them works. Listed A to Z.")
    assert seen["years"]["opened"]["heading"] == old.replace(" Listed A to Z.", "")
    assert seen["years"]["az"]["heading"] == old
    assert seen["az"]["opened"]["heading"] == old
    assert seen["years"]["back"]["heading"] == old.replace(" Listed A to Z.", "")


def test_browser_the_folded_boxes_have_no_switch_and_no_year_line_and_are_unchanged(seen):
    for name in ("years", "az", "none"):
        opened = seen[name]["opened"]
        assert opened["switchesInBoxes"] == 0
        assert all(year is None for year in opened["boxYears"])
    for part in ("narrower", "wider", "red", "noReg"):
        assert seen["years"]["opened"][part] == seen["none"]["opened"][part]
        assert seen["az"]["opened"][part] == seen["none"]["opened"][part]


def test_browser_the_tab_count_is_unchanged_by_the_order(seen):
    assert seen["years"]["opened"]["tab"] == seen["az"]["opened"]["tab"] == seen["none"]["opened"]["tab"]


def test_browser_with_no_entry_on_any_card_the_page_is_exactly_as_it_was(seen):
    none = seen["none"]["opened"]
    assert all(year is None for year in none["years"])
    assert not none["switchShown"] and not none["noteShown"]
    assert none["heading"].endswith("Listed A to Z.")
    assert none["address"] == "?disease=MONDO_TEST"


def test_browser_nothing_runs_sideways_at_phone_width(seen):
    assert not seen["years"]["opened"]["sideways"]


def test_the_printed_page_shows_the_screen_order_and_hides_only_the_switch_buttons():
    assert "@media print{.order-switch{display:none!important}}" in PAGE
    assert "order-note" not in str(re.findall(r"@media print\{[^}]*\}", PAGE))
