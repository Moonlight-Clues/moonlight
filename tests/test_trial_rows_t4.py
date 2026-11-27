"""Tickets T4 and T4b. The page: trial rows on trial cards.

THE TICKETS (MAIN 5; the words are in T4_spec.md, which replaces "the build file")
  T4   Main-list trial cards (the In trials tab's top list) show "Trials for
       this disease, newest first" under the name and forms, above the pathway:
       one row per trial, the whole row one link to ClinicalTrials.gov, NCT
       number and phase on top, then "status · end · role" exactly as the API
       sends them. "All [N] trials on ClinicalTrials.gov" when the total is
       over 3. A finished note once at the top of the tab. A footer line
       "Trial details checked [date]." when trials_checked is sent.
  T4b  Cards in "More medicines in trials" and "New medicines being tested"
       show the same list in the same place.

NOT IN THIS FILE: the footer words "Data from Open Targets and
ClinicalTrials.gov". Four old tests pin today's footer text
(tests/test_api.py FOOTER_NOTE, which test_design_pass.py and
test_guide_and_front_page.py reuse, and tests/test_version_3_21.py). MAIN 5
decides; see the PR.

Saved files only, plus a real browser at 390 px (skipped if node/playwright is
missing). No network. The answers are the saved ADPKD page with trial fields
added by hand in the shape T3 sends.
"""

import copy
import json
import pathlib
import re
import shutil
import subprocess
from unittest.mock import patch
from urllib.parse import quote

import pytest
from fastapi.testclient import TestClient

from moonlight import api
from moonlight import trials as trials_module

import test_opposite_way_box as adpkd_page

ROOT = pathlib.Path(__file__).resolve().parent.parent
PAGE_FILE = ROOT / "web" / "index.html"
PAGE = PAGE_FILE.read_text(encoding="utf-8")

SUBHEAD = "Trials for this disease, newest first"
FINISHED_NOTE = "'Finished' means the trial ended. It does not mean the medicine worked."
LINK = "https://clinicaltrials.gov/study/"
ALL_URL = "https://clinicaltrials.gov/search?cond=x&intr="  # as the API would send it; the page must use it as sent

CSS_LINES = [
    # The spec's rule, scoped to the slot: .card-subhead already styles the "Research pathway" line.
    '[data-slot="studies"] .card-subhead{font-size:12px;font-weight:700;color:var(--muted);margin:10px 0 2px;text-transform:none;letter-spacing:normal}',
    ".studies{list-style:none;margin:0 0 4px;padding:0}",
    ".studies li{border-top:1px solid var(--line)}",
    ".studies li:first-child{border-top:0}",
    ".study-row{display:block;min-height:44px;padding:8px 0;text-decoration:none;color:inherit}",
    ".study-row .sr1{display:flex;justify-content:space-between;gap:8px;font-size:13px}",
    ".study-row .nct{color:var(--teal);font-weight:700;text-decoration:underline;text-underline-offset:3px}",
    ".study-row .phase-t{font-size:12px;font-weight:700;color:var(--neutral);white-space:nowrap}",
    ".study-row .sr2{display:block;font-size:12px;color:var(--muted);line-height:1.5;margin-top:2px}",
    ".all-studies{display:inline-flex;align-items:center;min-height:44px;font-size:13px;font-weight:650}",
    ".finished-note{font-size:13px;color:var(--muted);margin:0 0 12px}",
    "@media print{.study-row .nct{color:#000}}",
]


def trial(nct, status="Recruiting", end="Expected to end 2031", phases=("PHASE3",), role="Being tested"):
    return {"nct_id": nct, "status": status, "end": end, "phases": list(phases), "role": role,
            "url": LINK + nct}


def six(first="NCT0000000"):
    return [trial(f"{first}{n}") for n in range(1, 4)]


# ------------------------------------------------------------- the answers

@pytest.fixture(scope="module")
def base():
    """The saved ADPKD page as it is today: no trial fields at all."""
    api.forget_answers()
    with patch.object(trials_module, "TRIALS_PATH", pathlib.Path("/nonexistent/trials.sqlite")):
        with TestClient(api.app):
            with patch("moonlight.fetch._post_json", side_effect=adpkd_page.saved_post_json):
                answer = TestClient(api.app).get(
                    "/api/clues", params={"disease_id": adpkd_page.ADPKD}).json()
    api.forget_answers()
    for key in ("being_studied", "more_in_trials", "new_in_trials"):
        assert answer[key], key
        assert all("studies" not in card for card in answer[key])
    return answer


def given(answer, where, studies, total=None, checked="2026-11-26"):
    """A copy of the answer with trial fields on the cards named in `where`
    ([(list name, position)]); studies is the same for each."""
    out = copy.deepcopy(answer)
    for key, place in where:
        card = out[key][place]
        card["studies"] = copy.deepcopy(studies)
        card["study_total"] = len(studies) if total is None else total
        card["studies_url"] = ALL_URL + quote(card["medicine"], safe="")
        card["trials_checked"] = checked
    return out


MAIN, MORE, NEW = ("being_studied", 0), ("more_in_trials", 0), ("new_in_trials", 0)


@pytest.fixture(scope="module")
def answers(base):
    three = [trial("NCT00000011", phases=("PHASE1", "PHASE2")),
             trial("NCT00000012", status="Finished", end="Ended 2019", phases=("PHASE2",), role="Being tested"),
             trial("NCT00000013", status="Recruiting", end="Expected to end 2031", phases=[], role="Role not stated")]
    every = [MAIN, MORE, NEW]
    out = {
        "today": base,
        "six": given(base, [MAIN], three, total=6),
        "three": given(base, [MAIN], three),
        "four": given(base, [MAIN], three, total=4),
        "none": given(base, [MAIN], [], total=0),
        "boxes": given(base, every, three, total=5),
        "plain": given(base, [MAIN], [trial("NCT00000021", status="Recruiting")]),
        "noChecked": given(base, [MAIN], three, total=6),
        "noUrl": given(base, [MAIN], three, total=6),
    }
    for item in out["noUrl"]["being_studied"][0]["studies"]:
        item.pop("url")
    out["noUrl"]["being_studied"][0].pop("studies_url")
    for card in out["noChecked"]["being_studied"]:
        card.pop("trials_checked", None)
    return out


# ------------------------------------------------------- the page text itself

def test_the_slot_is_in_the_template_right_after_the_top_before_the_pathway():
    template = PAGE[PAGE.index('<template id="card-template">'):PAGE.index("</template>", PAGE.index('<template id="card-template">'))]
    assert re.search(r'<span class="reports" data-slot="reports"></span>\s*</div>\s*(<!--.*?-->\s*)?'
                     r'<div data-slot="studies" hidden></div>\s*<p class="where-label"', template, re.S)
    assert template.index('data-slot="studies"') < template.index('data-part="path-head"')
    assert template.count('data-slot="studies"') == 1


@pytest.mark.parametrize("line", CSS_LINES)
def test_each_spec_css_line_is_in_the_page_once(line):
    assert PAGE.count(line) == 1


def test_the_research_pathway_heading_keeps_its_own_style():
    assert ".card-subhead{font-size:11px;letter-spacing:.07em;text-transform:uppercase;color:var(--muted);font-weight:750;margin:18px 0 8px}" in PAGE
    assert "\n.card-subhead{font-size:12px" not in PAGE


def test_no_dashed_edge_and_no_new_colour_in_the_new_css():
    new = "\n".join(CSS_LINES)
    assert "dashed" not in new
    assert not re.search(r"#[0-9a-fA-F]{3,6}", new.replace("color:#000", ""))
    for token in ("--muted", "--teal", "--neutral", "--line"):
        assert re.search(re.escape(token) + r":", PAGE), token


def test_the_page_holds_no_clinicaltrials_address_of_its_own():
    script = "".join(re.findall(r"(?s)<script>(.*?)</script>", PAGE))
    assert "clinicaltrials.gov/" not in script.lower()  # the words "on ClinicalTrials.gov" are not an address
    assert "http" not in script.lower()


def test_the_words_are_in_the_page_exactly():
    assert SUBHEAD in PAGE
    assert FINISHED_NOTE in PAGE
    assert "Trial details checked " in PAGE
    assert ("Not clinical findings · Data from Open Targets and ClinicalTrials.gov"
            ' · <a href="/corrections">Corrections</a></div>') in PAGE  # ticket 2.66


def test_the_new_code_writes_with_textcontent_only():
    start = PAGE.index("/* Ticket T4.")
    end = PAGE.index("*/", start)
    code = PAGE[start:PAGE.index("  /* A card of a folded box on the In trials tab")]
    assert "innerHTML" not in code and "insertAdjacentHTML" not in code
    assert "textContent" in code


# ------------------------------------------------------------ a real browser

BROWSER_SCRIPT = r"""
"use strict";
const fs = require("fs");
const { chromium } = require("playwright");
const PAGE = fs.readFileSync(process.argv[1], "utf-8");
const ANSWERS = JSON.parse(fs.readFileSync(process.argv[2], "utf-8"));
const SITE = "http://moonlight.test";

function read() {
  const text = el => el.textContent.replace(/\s+/g, " ").trim();
  const shownEl = el => el.getClientRects().length > 0;
  const lists = {main: "#studied-cards", more: "#more-trials-cards", new: "#new-trials-cards"};
  const out = {cards: {}};
  for (const [name, sel] of Object.entries(lists)) {
    out.cards[name] = [...document.querySelectorAll(sel + " > .card")].map(card => {
      const slot = card.querySelector('[data-slot="studies"]');
      const top = card.querySelector(".card-top");
      const rows = [...card.querySelectorAll(".study-row")].map(row => ({
        href: row.getAttribute("href"), target: row.getAttribute("target"), rel: row.getAttribute("rel"),
        tag: row.tagName, nct: text(row.querySelector(".nct")),
        phase: row.querySelector(".phase-t") ? text(row.querySelector(".phase-t")) : null,
        line: text(row.querySelector(".sr2")), height: row.getBoundingClientRect().height,
        color: getComputedStyle(row.querySelector(".sr2")).color,
        insideLink: row.closest("li") !== null,
      }));
      const all = card.querySelector(".all-studies");
      return {
        name: text(card.querySelector('[data-slot="medicine-name"]')),
        hasSlot: !!slot, slotAfterTop: !!slot && slot.previousElementSibling === top,
        slotBeforePath: !!slot && !!card.querySelector(".path")
          && !!(slot.compareDocumentPosition(card.querySelector(".path")) & Node.DOCUMENT_POSITION_FOLLOWING),
        slotShown: !!slot && shownEl(slot), slotHidden: !!slot && slot.hidden,
        subhead: card.querySelector('[data-slot="studies"] .card-subhead') ? text(card.querySelector('[data-slot="studies"] .card-subhead')) : null,
        rows, all: all ? {text: text(all), href: all.getAttribute("href"), height: all.getBoundingClientRect().height, target: all.getAttribute("target")} : null,
        outer: card.outerHTML, height: card.getBoundingClientRect().height, width: card.getBoundingClientRect().width,
        studiesHeight: slot ? slot.getBoundingClientRect().height : 0,
      };
    });
  }
  const notes = [...document.querySelectorAll(".finished-note")];
  const panel = document.getElementById("panel-trials");
  const desc = panel.querySelector(".section-desc");
  out.notes = notes.map(n => ({text: text(n), shown: shownEl(n), inPanel: panel.contains(n),
    afterDesc: desc.nextElementSibling === n, beforeCards: !!(n.compareDocumentPosition(document.getElementById("studied-cards")) & Node.DOCUMENT_POSITION_FOLLOWING)}));
  const line = document.getElementById("trials-checked-line");
  const build = document.getElementById("build-line");
  out.checked = line ? {text: text(line), shown: shownEl(line), afterBuild: build.nextElementSibling === line,
    color: getComputedStyle(line).color, buildColor: getComputedStyle(build).color} : null;
  out.sideways = document.documentElement.scrollWidth > document.documentElement.clientWidth;
  out.tab = text(document.getElementById("tab-trials"));
  return out;
}

async function oneSearch(browser, answer) {
  const context = await browser.newContext({ viewport: { width: 390, height: 844 } });
  const page = await context.newPage();
  const errors = [];
  page.on("pageerror", problem => errors.push(String(problem)));
  await context.route("**/*", route => {
    const url = route.request().url();
    if (url === SITE + "/" || url.startsWith(SITE + "/?"))
      return route.fulfill({ contentType: "text/html; charset=utf-8", body: PAGE });
    if (url.startsWith(SITE + "/api/clues?"))
      return route.fulfill({ contentType: "application/json", body: JSON.stringify(answer) });
    if (url.startsWith(SITE + "/api/version"))
      return route.fulfill({ contentType: "application/json", body: JSON.stringify({fingerprint: "0123456789ab"}) });
    return route.abort();
  });
  await page.goto(SITE + "/?disease=MONDO_TEST&tab=trials");
  await page.waitForSelector("#found", { state: "visible" });
  await page.click("#tab-trials");
  await page.evaluate(() => document.querySelectorAll("#panel-trials details").forEach(d => { d.open = true; }));
  await page.waitForTimeout(300);
  const first = await page.evaluate(read);
  await page.waitForTimeout(700);
  const later = await page.evaluate(read);
  const shifted = JSON.stringify(Object.values(first.cards).flat().map(c => [c.height, c.width]))
    !== JSON.stringify(Object.values(later.cards).flat().map(c => [c.height, c.width]));
  await context.close();
  return { errors, ...first, shifted };
}

(async () => {
  const browser = await chromium.launch();
  const out = {};
  for (const name of Object.keys(ANSWERS)) out[name] = await oneSearch(browser, ANSWERS[name]);
  await browser.close();
  console.log(JSON.stringify(out));
})().catch(problem => { console.error(problem); process.exit(1); });
"""


@pytest.fixture(scope="module")
def seen(answers, tmp_path_factory):
    node = shutil.which("node")
    if not node or subprocess.run([node, "-e", "require('playwright')"], capture_output=True).returncode:
        pytest.skip("needs node with playwright to open a real browser")
    folder = tmp_path_factory.mktemp("trial_rows_t4")
    answers_file = folder / "answers.json"
    answers_file.write_text(json.dumps(answers), encoding="utf-8")
    run = subprocess.run([node, "-e", BROWSER_SCRIPT, str(PAGE_FILE), str(answers_file)],
                         capture_output=True, text=True, timeout=300, cwd=str(ROOT))
    assert run.returncode == 0, run.stderr[-3000:]
    out = json.loads(run.stdout)
    for name in answers:
        assert out[name]["errors"] == [], name
    return out


def first_main(seen, name):
    return seen[name]["cards"]["main"][0]


# T4 EXAMPLE: 6 trials -> 3 rows and "All 6 trials on ClinicalTrials.gov"

def test_example_six_trials_show_three_rows_and_the_all_link(seen, answers):
    card = first_main(seen, "six")
    assert len(card["rows"]) == 3
    assert card["subhead"] == SUBHEAD
    assert card["all"]["text"] == "All 6 trials on ClinicalTrials.gov"
    assert card["all"]["href"] == ALL_URL + quote(card["name"], safe="")  # the API's address, as sent


def test_three_trials_have_no_all_link_and_four_do(seen):
    assert first_main(seen, "three")["all"] is None
    assert len(first_main(seen, "three")["rows"]) == 3
    assert first_main(seen, "four")["all"]["text"] == "All 4 trials on ClinicalTrials.gov"


# T4 EXAMPLE: 0 trials -> the card as today

def test_example_no_trials_the_card_is_exactly_as_today(seen):
    today = seen["today"]["cards"]["main"]
    for name in ("none", "noChecked"):
        for place, card in enumerate(seen[name]["cards"]["main"]):
            if name == "noChecked" and place == 0:
                continue  # that one has trials; it is the footer test's
            if name == "none" and place == 0:
                assert card["outer"] == today[0]["outer"]
                assert not card["rows"] and card["subhead"] is None and card["all"] is None
            else:
                assert card["outer"] == today[place]["outer"]
    for card in today:
        assert not card["rows"] and card["subhead"] is None and card["all"] is None


def test_cards_with_no_trial_fields_and_new_clues_are_untouched(seen):
    today = seen["today"]["cards"]["main"]
    other = seen["six"]["cards"]["main"]
    for old, new in zip(today[1:], other[1:]):
        assert old["outer"] == new["outer"]


# the row

def test_a_row_is_one_whole_link_to_the_trial_in_the_same_tab(seen):
    rows = first_main(seen, "three")["rows"]
    assert [row["nct"] for row in rows] == ["NCT00000011", "NCT00000012", "NCT00000013"]
    for row in rows:
        assert row["tag"] == "A" and row["insideLink"]
        assert row["href"] == LINK + row["nct"]
        assert row["target"] is None  # opens as the Source record link does today
        assert row["rel"] is None


def test_no_address_sent_means_a_plain_row_and_no_all_link_never_a_made_up_link(seen):
    card = first_main(seen, "noUrl")
    assert len(card["rows"]) == 3 and all(row["tag"] == "SPAN" and row["href"] is None for row in card["rows"])
    assert card["all"] is None


def test_phase_joined_with_a_slash_and_left_out_when_none(seen):
    rows = first_main(seen, "three")["rows"]
    assert [row["phase"] for row in rows] == ["Phase 1 / Phase 2", "Phase 2", None]


@pytest.mark.parametrize("tokens, words", [
    (["EARLY_PHASE1"], "Early Phase 1"), (["PHASE1"], "Phase 1"), (["PHASE2", "PHASE3"], "Phase 2 / Phase 3"),
    (["PHASE4"], "Phase 4"), (["NA"], None), ([], None),
])
def test_phase_words_are_the_cards_phase_words(tokens, words, base, tmp_path_factory):
    node = shutil.which("node")
    if not node:
        pytest.skip("needs node")
    function = re.search(r"function studyPhaseWords\(.*?\n  }\n", PAGE, re.S)
    assert function, "studyPhaseWords is missing"
    run = subprocess.run([node, "-e", function.group(0) + f"console.log(JSON.stringify(studyPhaseWords({json.dumps(tokens)})))"],
                         capture_output=True, text=True)
    assert json.loads(run.stdout) == (words or "")


def test_status_end_and_role_are_shown_as_sent_and_never_coloured(seen):
    rows = first_main(seen, "three")["rows"]
    assert [row["line"] for row in rows] == [
        "Recruiting · Expected to end 2031 · Being tested",
        "Finished · Ended 2019 · Being tested",
        "Recruiting · Expected to end 2031 · Role not stated"]
    muted = {row["color"] for row in rows}
    assert len(muted) == 1  # one grey for every status, Finished and Recruiting alike


def test_every_row_and_the_all_link_are_at_least_44_px_tall(seen):
    for name in ("six", "boxes"):
        for cards in seen[name]["cards"].values():
            for card in cards:
                assert all(row["height"] >= 44 for row in card["rows"])
                if card["all"]:
                    assert card["all"]["height"] >= 44


def test_the_slot_is_right_after_the_card_top_and_unhidden_only_when_filled(seen):
    card = first_main(seen, "six")
    assert card["hasSlot"] and card["slotAfterTop"] and card["slotShown"] and card["slotBeforePath"]
    empty = first_main(seen, "none")
    assert not empty["hasSlot"] or (empty["slotHidden"] and not empty["slotShown"])


# the finished note

def test_finished_note_once_at_the_top_of_the_tab_when_a_row_is_finished(seen):
    (note,) = seen["six"]["notes"]
    assert note["text"] == FINISHED_NOTE and note["shown"] and note["inPanel"]
    assert note["afterDesc"] and note["beforeCards"]


def test_finished_note_is_not_shown_without_a_finished_row(seen):
    for name in ("today", "none", "plain"):
        assert all(not note["shown"] for note in seen[name]["notes"]), name


def test_finished_note_counts_rows_in_the_boxes_too_and_still_shows_once(seen):
    assert len([n for n in seen["boxes"]["notes"] if n["shown"]]) == 1


# T4b

def test_t4b_both_boxes_show_the_same_rows_under_the_name(seen):
    for key in ("more", "new"):
        card = seen["boxes"]["cards"][key][0]
        assert card["subhead"] == SUBHEAD and len(card["rows"]) == 3
        assert card["slotAfterTop"] and card["slotShown"]
        assert card["all"]["text"] == "All 5 trials on ClinicalTrials.gov"
        assert [row["line"] for row in card["rows"]] == [row["line"] for row in first_main(seen, "boxes")["rows"]]


def test_t4b_nothing_else_in_the_box_cards_changes(seen):
    for key in ("more", "new"):
        today = seen["today"]["cards"][key]
        now = seen["boxes"]["cards"][key]
        assert [c["name"] for c in now] == [c["name"] for c in today]
        for old, new in zip(today[1:], now[1:]):
            assert old["outer"] == new["outer"]



# the footer's own line

def test_footer_line_gives_the_date_under_the_build_line(seen):
    line = seen["six"]["checked"]
    assert line["text"] == "Trial details checked 26 November 2026."
    assert line["afterBuild"]
    assert line["color"] == line["buildColor"]  # grey, like the Build line


def test_footer_line_is_absent_without_trials_checked(seen):
    for name in ("today", "noChecked"):
        line = seen[name]["checked"]
        assert line is None or (line["text"] == "" and not line["shown"]), name


# the 390 px limits

def test_nothing_widens_no_sideways_scroll_nothing_shifts(seen):
    for name in ("six", "boxes", "three"):
        assert not seen[name]["sideways"], name
        assert seen[name]["shifted"] is False, name
        for key, cards in seen[name]["cards"].items():
            for card, old in zip(cards, seen["today"]["cards"][key]):
                assert card["width"] == old["width"], (name, key)


def test_a_main_card_with_three_rows_grows_at_most_45_percent(seen):
    old = seen["today"]["cards"]["main"][0]["height"]
    for name in ("three", "six"):
        new = seen[name]["cards"]["main"][0]["height"]
        assert new <= old * 1.45, (name, old, new)
