"""Ticket 3.26. Trial-card tidy.

THE TICKET (Kashish's words, decided; MAIN 5's order)
  1. The subhead "Trials for this disease, newest first" looks exactly like
     "RESEARCH PATHWAY" (size, capitals, spacing).
  2. The phase in a trial row uses the pill's format ("Phase 2/3"). The phase
     pill at the card foot is hidden when the card shows exactly one trial row.
  3. "Source record" is hidden when its address equals one of the card's
     trial-row links.
  4. A trial that is over (Finished, Stopped early, Withdrawn before starting):
     no "Ended" after "Finished" -> "Finished 2016"; the role in the past
     tense: "Was tested" / "Was used for comparison" ("Role not stated" stays).
  5. An In trials card with no trial rows shows a grey line where the rows
     would be: "No trial details were found on ClinicalTrials.gov." A card that
     already shows "No study of this disease was found for this medicine."
     keeps that line instead; never both.

Saved files only. The page runs in a real browser at 390 px (skipped if
node/playwright is missing). No network.
"""

import copy
import json
import pathlib
import shutil
import subprocess

import pytest

from moonlight import ctgov
from moonlight.ctgov import read_trial

from test_trial_rows_t4 import (  # noqa: F401  (base is a fixture: pytest finds it here)
    BROWSER_SCRIPT, MAIN, MORE, NEW, ROOT, PAGE_FILE, PAGE, base, given, trial, LINK)

import test_ctgov

NO_DETAILS = "No trial details were found on ClinicalTrials.gov."
NO_STUDY = "No study of this disease was found for this medicine."
OTHER = "https://example.org/label"


# ------------------------------------------------------------ item 4: the words

def reading_line(nct, medicine):
    found = read_trial(test_ctgov.study(nct), medicine)
    return " · ".join(part for part in (found.status, found.end, found.role) if part)


def test_the_new_words_are_constants_in_ctgov():
    assert ctgov.WAS_TESTED == "Was tested"
    assert ctgov.WAS_USED_FOR_COMPARISON == "Was used for comparison"
    assert ctgov.ROLE_NOT_STATED == "Role not stated"


def test_example_finished_trial_says_finished_year_and_was_tested():
    # NCT04118153: finished, ended 2024, Abatacept in an experimental group.
    assert reading_line("NCT04118153", "Abatacept") == "Finished 2024 · Was tested"


def test_example_finished_trial_used_for_comparison():
    assert reading_line("NCT04123561", "Normal Saline") == "Finished 2022 · Was used for comparison"


def test_example_stopped_early_keeps_its_ended_year():
    assert reading_line("NCT02006251", "Real-time Instrumentation") == "Stopped early · Ended 2014 · Was tested"
    raw = test_ctgov.study("NCT02006251")
    arms = raw["protocolSection"]["armsInterventionsModule"]
    for group in arms["armGroups"]:
        group["type"] = "ACTIVE_COMPARATOR"
    assert read_trial(raw, "Real-time Instrumentation").role == "Was used for comparison"


def test_withdrawn_before_starting_is_over_too():
    assert reading_line("NCT00789659", "Negative pressure dressing") == \
        "Withdrawn before starting · Ended 2014 · Was tested"


def test_role_not_stated_is_unchanged_on_a_finished_trial():
    assert reading_line("NCT00188396", "Citalopram") == "Finished 2008 · Role not stated"


def test_a_finished_trial_with_no_end_date_keeps_its_words():
    assert reading_line("NCT02733523", 'Program "Sentirnos bien" (Feeling well)') == \
        "Finished · End date not recorded · Was tested"


def test_a_trial_that_is_not_over_keeps_the_present_tense():
    assert reading_line("NCT06758557", "Pemetrexed") == "Recruiting · Expected to end 2026 · Being tested"
    assert reading_line("NCT01340183", "Placebo") == "Paused · Expected to end 2011 · Used for comparison"


# ------------------------------------------------------------ the page, in a browser

CARD_SCRIPT = r"""
"use strict";
const fs = require("fs");
const { chromium } = require("playwright");
const PAGE = fs.readFileSync(process.argv[1], "utf-8");
const ANSWERS = JSON.parse(fs.readFileSync(process.argv[2], "utf-8"));
const SITE = "http://moonlight.test";
function read() {
  const text = el => el.textContent.replace(/\s+/g, " ").trim();
  const shown = el => !!el && el.getClientRects().length > 0;
  const style = el => { if (!el) return null; const c = getComputedStyle(el);
    return [c.fontSize, c.textTransform, c.letterSpacing, c.fontWeight, c.color, c.marginTop, c.marginBottom, c.lineHeight].join("|"); };
  const lists = {main: "#studied-cards", more: "#more-trials-cards", new: "#new-trials-cards"};
  const out = {};
  for (const [name, sel] of Object.entries(lists)) {
    out[name] = [...document.querySelectorAll(sel + " > .card")].map(card => {
      const slot = card.querySelector('[data-slot="studies"]');
      const noDetails = card.querySelector(".no-details");
      const foot = card.querySelector(".card-foot");
      const pill = card.querySelector('[data-slot="phase"]');
      const source = card.querySelector('[data-slot="source"]');
      const noStudy = card.querySelector('[data-part="no-study"]');
      return {
        subhead: slot && slot.querySelector(".card-subhead") ? text(slot.querySelector(".card-subhead")) : null,
        subheadStyle: slot ? style(slot.querySelector(".card-subhead")) : null,
        pathStyle: style(card.querySelector('[data-part="path-head"]')),
        pathText: card.querySelector('[data-part="path-head"]') ? card.querySelector('[data-part="path-head"]').textContent : null,
        rows: [...card.querySelectorAll(".study-row")].map(row => ({
          href: row.getAttribute("href"), phase: row.querySelector(".phase-t") ? text(row.querySelector(".phase-t")) : null,
          line: text(row.querySelector(".sr2"))})),
        pill: shown(pill) ? text(pill) : null,
        pillInDom: !!pill,
        source: shown(source) ? source.getAttribute("href") : null,
        noStudy: shown(noStudy),
        noDetails: noDetails ? {text: text(noDetails), shown: shown(noDetails), color: getComputedStyle(noDetails).color,
          muted: getComputedStyle(card.querySelector('[data-part="no-study"]')).color,
          inSlot: !!slot && slot.contains(noDetails), slotBeforeFoot: !!slot && !!(slot.compareDocumentPosition(foot) & Node.DOCUMENT_POSITION_FOLLOWING),
          nextIsPath: !!slot && !!(slot.compareDocumentPosition(card.querySelector(".card-foot")) & Node.DOCUMENT_POSITION_FOLLOWING)} : null,
        height: card.getBoundingClientRect().height,
        text: text(card),
      };
    });
  }
  out.sideways = document.documentElement.scrollWidth > document.documentElement.clientWidth;
  return out;
}
(async () => {
  const browser = await chromium.launch();
  const result = {};
  for (const name of Object.keys(ANSWERS)) {
    const context = await browser.newContext({ viewport: { width: 390, height: 844 } });
    const page = await context.newPage();
    const errors = [];
    page.on("pageerror", problem => errors.push(String(problem)));
    await context.route("**/*", route => {
      const url = route.request().url();
      if (url === SITE + "/" || url.startsWith(SITE + "/?")) return route.fulfill({ contentType: "text/html; charset=utf-8", body: PAGE });
      if (url.startsWith(SITE + "/api/clues?")) return route.fulfill({ contentType: "application/json", body: JSON.stringify(ANSWERS[name]) });
      if (url.startsWith(SITE + "/api/version")) return route.fulfill({ contentType: "application/json", body: JSON.stringify({fingerprint: "0123456789ab"}) });
      return route.abort();
    });
    await page.goto(SITE + "/?disease=MONDO_TEST&tab=trials");
    await page.waitForSelector("#found", { state: "visible" });
    await page.click("#tab-trials");
    await page.evaluate(() => document.querySelectorAll("#panel-trials details").forEach(d => { d.open = true; }));
    await page.waitForTimeout(300);
    result[name] = { errors, ...(await page.evaluate(read)) };
    await context.close();
  }
  await browser.close();
  console.log(JSON.stringify(result));
})().catch(problem => { console.error(problem); process.exit(1); });
"""

UDENAFIL = [trial("NCT00000031", status="Finished 2016", end="", phases=("PHASE2", "PHASE3"), role="Was tested")]
THREE = [trial("NCT00000041", phases=("PHASE1", "PHASE2")), trial("NCT00000042", phases=("PHASE2",)),
         trial("NCT00000043", phases=("PHASE3",))]


def tweak(answer, key, place, **fields):
    card = answer[key][place]
    card.update(fields)
    return answer


@pytest.fixture(scope="module")
def pages(base):
    out = {}
    one = given(base, [MAIN, MORE, NEW], UDENAFIL)
    for key in ("being_studied", "more_in_trials", "new_in_trials"):
        one[key][0].update(source=OTHER, trial_phase="Phase 2/3")
    out["one_row"] = one

    same = given(base, [MAIN, MORE, NEW], UDENAFIL)
    for key in ("being_studied", "more_in_trials", "new_in_trials"):
        same[key][0].update(source=LINK + "NCT00000031", trial_phase="Phase 2/3")
    out["same_link"] = same

    three = given(base, [MAIN, MORE, NEW], THREE)
    for key in ("being_studied", "more_in_trials", "new_in_trials"):
        three[key][0].update(source=LINK + "NCT00000042", trial_phase="Phase 2")
    out["three_rows_source_is_second"] = three

    other3 = given(base, [MAIN, MORE, NEW], THREE)
    for key in ("being_studied", "more_in_trials", "new_in_trials"):
        other3[key][0].update(source=OTHER, trial_phase="Phase 2")
    out["three_rows_other_source"] = other3

    two = given(base, [MAIN, MORE, NEW], THREE[:2])
    for key in ("being_studied", "more_in_trials", "new_in_trials"):
        two[key][0].update(source=OTHER, trial_phase="Phase 2")
    out["two_rows"] = two

    empty = given(base, [MAIN, MORE, NEW], [], total=0)  # Cicletanine: a source, no trials
    for key in ("being_studied", "more_in_trials", "new_in_trials"):
        empty[key][0].update(source=OTHER, trial_phase="Phase 2")
    out["no_rows_with_source"] = empty

    nosrc = given(base, [MAIN, MORE, NEW], [], total=0)
    for key in ("being_studied", "more_in_trials", "new_in_trials"):
        nosrc[key][0].update(source=None, trial_phase="Phase 2")
    out["no_rows_no_source"] = nosrc

    # an answer from a server with no trials file: no "studies" at all
    plain = copy_of(base)
    for key in ("being_studied", "more_in_trials", "new_in_trials"):
        plain[key][0].update(source=OTHER, trial_phase="Phase 2")
    out["no_trial_fields"] = plain
    return out


def copy_of(answer):
    return copy.deepcopy(answer)


@pytest.fixture(scope="module")
def seen(pages, tmp_path_factory):
    node = shutil.which("node")
    if not node or subprocess.run([node, "-e", "require('playwright')"], capture_output=True).returncode:
        pytest.skip("needs node with playwright to open a real browser")
    folder = tmp_path_factory.mktemp("tidy_3_26")
    answers_file = folder / "answers.json"
    answers_file.write_text(json.dumps(pages), encoding="utf-8")
    run = subprocess.run([node, "-e", CARD_SCRIPT, str(PAGE_FILE), str(answers_file)],
                         capture_output=True, text=True, timeout=300, cwd=str(ROOT))
    assert run.returncode == 0, run.stderr[-3000:]
    out = json.loads(run.stdout)
    for name in pages:
        assert out[name]["errors"] == [], name
        assert not out[name]["sideways"], name
    return out


ALL = ("main", "more", "new")


def cards(seen, name, which=ALL):
    return [(w, seen[name][w][0]) for w in which]


# item 1
def test_the_subhead_looks_exactly_like_research_pathway(seen):
    card = seen["one_row"]["main"][0]
    assert card["subhead"] == "Trials for this disease, newest first"
    assert card["pathText"].startswith("Research pathway")
    assert card["subheadStyle"] == card["pathStyle"]
    assert card["subheadStyle"].split("|")[:3] == ["11px", "uppercase", "0.77px"]


def test_the_subhead_has_no_rule_of_its_own_in_the_page():
    assert '[data-slot="studies"] .card-subhead' not in PAGE


# item 2
def test_a_row_phase_uses_the_pills_format(seen):
    for where, card in cards(seen, "three_rows_other_source"):
        assert [row["phase"] for row in card["rows"]] == ["Phase 1/2", "Phase 2", "Phase 3"], where
    for where, card in cards(seen, "one_row"):
        assert card["rows"][0]["phase"] == "Phase 2/3", where


def test_one_row_hides_the_phase_pill_on_every_kind_of_trial_card(seen):
    for name in ("one_row", "same_link"):
        for where, card in cards(seen, name):
            assert len(card["rows"]) == 1 and card["pill"] is None, (name, where)


def test_two_or_three_rows_keep_the_phase_pill(seen):
    for name in ("two_rows", "three_rows_other_source", "three_rows_source_is_second"):
        for where, card in cards(seen, name):
            assert card["pill"] == ("Phase 2"), (name, where)


def test_no_rows_keeps_the_phase_pill(seen):
    for name in ("no_rows_with_source", "no_rows_no_source", "no_trial_fields"):
        for where, card in cards(seen, name):
            assert card["pill"] == "Phase 2", (name, where)


# item 3
def test_source_record_is_hidden_when_it_is_a_trial_row_link(seen):
    for name in ("same_link", "three_rows_source_is_second"):
        for where, card in cards(seen, name):
            assert card["source"] is None, (name, where)
            assert not card["noStudy"], (name, where)
            assert LINK + "NCT00000031" in [r["href"] for r in card["rows"]] or name != "same_link"


def test_source_record_stays_when_it_is_another_address(seen):
    for name in ("one_row", "two_rows", "three_rows_other_source", "no_rows_with_source", "no_trial_fields"):
        for where, card in cards(seen, name):
            assert card["source"] == OTHER, (name, where)


# item 5
def test_no_rows_shows_the_grey_line_where_the_rows_would_be(seen):
    for where, card in cards(seen, "no_rows_with_source"):
        line = card["noDetails"]
        assert line and line["text"] == NO_DETAILS and line["shown"], where
        assert line["inSlot"] and line["slotBeforeFoot"], where
        assert line["color"] == line["muted"], where  # the same grey as the other grey lines
        assert not card["noStudy"], where  # (the hidden no-study span is always in the card)
        assert card["subhead"] is None and not card["rows"], where


def test_a_card_that_shows_the_no_study_line_does_not_also_show_the_new_line(seen):
    for where, card in cards(seen, "no_rows_no_source"):
        assert card["noStudy"] and card["noDetails"] is None, where
        assert NO_STUDY in card["text"] and NO_DETAILS not in card["text"], where


def test_the_new_line_is_never_on_a_card_with_rows(seen):
    for name in ("one_row", "two_rows", "same_link", "three_rows_other_source"):
        for where, card in cards(seen, name):
            assert card["noDetails"] is None and NO_DETAILS not in card["text"], (name, where)


def test_a_server_that_sent_no_trial_details_at_all_is_not_told_there_were_none(seen):
    # No "studies" field means the trials file was not read. "None were found" would be untrue.
    for where, card in cards(seen, "no_trial_fields"):
        assert card["noDetails"] is None and NO_DETAILS not in card["text"], where


def test_the_words_are_in_the_page_exactly():
    assert NO_DETAILS in PAGE
