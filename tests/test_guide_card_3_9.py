"""Ticket 3.9. The guide's example card matches today's cards; a tidier guide.

The example card in #guide-card is a picture of the live New clues card for
pulmonary arterial hypertension -> Doxapram. It now has the protein sentence
(ticket 3.8), the gene line (3.1, styled by 3.5) and the Report link, closed
(3.3, styled by 3.5). Its gold letters run A to J with no gap, in reading order
down the card, and the legend under it holds Kashish's signed words (25 Nov).

The live card is drawn from the saved answers in fixtures/gene_evidence/, the
same answer the other gene-line tests use. No network.
"""

import copy
import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from moonlight import api, engine

from test_api import ENDING, guide_of, plain
from test_gene_evidence import PAH, clue, page_answer

ROOT = Path(__file__).resolve().parent.parent
PAGE_FILE = ROOT / "web" / "index.html"
PAGE = PAGE_FILE.read_text(encoding="utf-8")

# Kashish's signed words, 25 Nov. Word for word.
LEGEND = [
    ("A", "Medicine and its forms"),
    ("B", "Trial and approval records in the database"),
    ("C", "The path, in three steps"),
    ("D", "Up, down or unknown"),
    ("E", "How strong the link is"),
    ("F", "What the protein does"),
    ("G", "Why the gene is linked"),
    ("H", "The catch, on every clue"),
    ("I", "Where the fact comes from"),
    ("J", "Tell us if something is wrong"),
]
REPORT_NOTE = "We read every report. Nothing about you is kept."
LETTERS = [letter for letter, _ in LEGEND]


@pytest.fixture(scope="module")
def pah():
    return page_answer(PAH)


@pytest.fixture(scope="module")
def doxapram(pah):
    return clue(pah, "Doxapram")


@pytest.fixture(scope="module")
def guide():
    return guide_of(TestClient(api.app).get("/").text)


@pytest.fixture(scope="module")
def card(guide):
    return guide[guide.index('<article class="card"'):guide.index("</article>")]


def key_of(guide):
    key = guide[guide.index('<ul class="key">'):]
    return key[:key.index("</ul>")]


# ---- letters and legend ----

def test_the_card_letters_run_a_to_j_with_no_gap(card):
    assert re.findall(r'<span class="k" aria-label="([A-Z])">\1</span>', card) == LETTERS
    assert card.count('class="k"') == len(LETTERS)


def test_the_legend_holds_kashishs_signed_words_one_line_per_letter(guide):
    found = re.findall(
        r'<li><span class="k" aria-hidden="true">([A-Z])</span><span>([^<]+)</span></li>',
        key_of(guide))
    assert found == LEGEND
    assert key_of(guide).count("<li>") == len(LEGEND)


def test_the_report_note_is_under_the_legend_word_for_word(guide):
    card_part = guide[guide.index('id="guide-card"'):]
    card_part = card_part[:card_part.index("</section>")]
    note = re.search(r'(?s)</ul>\s*<p class="key-note">(.*?)</p>\s*$', card_part)
    assert note, "the note comes straight after the legend, last in the card part"
    assert plain(note.group(1)) == REPORT_NOTE
    assert note.group(1).count("<br>") == 1  # two lines, one sentence each


def test_the_old_legend_words_are_gone(guide):
    assert "Reports written about it" not in guide


# ---- the card's words, against the saved answer ----

def test_the_saved_answer_still_has_the_card_the_guide_shows(pah, doxapram):
    assert [item["medicine"] for item in pah["new_clues"]].index("Doxapram") == 5  # number 6
    assert doxapram["forms"] == ["Doxapram", "Doxapram Hydrochloride"]
    assert doxapram["reports"] == 8
    assert doxapram["ending"] == ENDING
    [kcnk3] = doxapram["proteins"]
    assert (kcnk3["symbol"], kcnk3["points"], kcnk3["direction"]) == ("KCNK3", 79, "down")
    assert kcnk3["evidence"] == ["genetic_association", "literature"]
    assert kcnk3["function"]


def test_the_protein_sentence_is_the_saved_one_word_for_word(card, doxapram):
    sentence = re.search(r'(?s)<p class="protein-function">(.*?)<span class="k"', card).group(1)
    assert sentence.strip() == doxapram["proteins"][0]["function"]


def test_the_gene_line_is_written_by_the_pages_own_code_from_the_saved_ids(card, doxapram):
    # The words are typed once on the page, in EVIDENCE_START and EVIDENCE_NAMES.
    # The guide card holds only the ids; the script writes the words.
    line = re.search(r'<p class="protein-evidence" data-guide-evidence="([^"]*)">', card)
    assert line, "the guide card's gene line carries the evidence ids"
    assert line.group(1).split() == doxapram["proteins"][0]["evidence"]
    assert engine.EVIDENCE_START + ", ".join(
        engine.EVIDENCE_NAMES[kind] for kind in line.group(1).split()) + "." == (
        "Linked to this disease by: inherited gene changes, mentioned together in research papers.")


def test_the_report_link_is_closed_after_the_source_record_and_not_clickable(card):
    foot = card.index('<div class="card-foot">')
    row = card.index('<div class="report-row">')
    assert foot < row
    report = card[row:]
    assert '<span class="report-link">Report</span>' in report
    assert "<button" not in card and "<a " not in card and "href" not in card
    assert "report-panel" not in card and "aria-expanded" not in card


# ---- spacing ----

def test_the_guides_section_gaps_are_24_on_a_phone_and_32_on_a_wide_screen():
    assert ".guide{max-width:760px;margin-inline:auto;display:grid;gap:24px}" in PAGE
    wide = PAGE[PAGE.index("@media(min-width:760px){.main"):]
    wide = wide[:wide.index("\n")]
    assert ".guide{gap:32px}" in wide
    assert "gap:56px" not in PAGE and "gap:68px" not in PAGE


def test_the_jump_to_the_guide_stops_at_the_top_of_the_page():
    assert re.search(r"\.guide\{scroll-margin-top:100vh\}", PAGE)
    assert ".guide>section{scroll-margin-top:70px;min-width:0}" in PAGE


# ---- in a real browser ----

BROWSER_SCRIPT = r"""
"use strict";
const fs = require("fs");
const { chromium } = require("playwright");
const PAGE = fs.readFileSync(process.argv[1], "utf-8");
const ANSWER = fs.readFileSync(process.argv[2], "utf-8");
const SITE = "http://moonlight.test";
const PARTS = [".rank", ".card-title h3", ".forms", ".reports", ".card-subhead", ".path",
  ".path-node", ".protein-id", ".direction", ".score", ".protein-function", ".protein-evidence",
  ".evidence-start", ".direction-note", ".ending", ".source-link", ".report-link"];

function readCard(el) {
  const copy = el.cloneNode(true);
  copy.querySelectorAll(".k").forEach(k => k.remove());
  const out = {};
  for (const sel of PARTS) out[sel] = [...copy.querySelectorAll(sel)].map(found => ({
    text: found.textContent.replace(/\s+/g, " ").trim(),
    cls: found.className, tag: found.tagName,
    title: found.getAttribute("title"),
  }));
  return out;
}

function geometry() {
  const card = document.querySelector("#guide-card .card");
  const box = el => { const r = el.getBoundingClientRect();
    return { top: r.top, bottom: r.bottom, left: r.left, right: r.right }; };
  const key = document.querySelector("#guide-card .key");
  return {
    letters: [...card.querySelectorAll(".k")].map(k => ({ letter: k.textContent, ...box(k) })),
    card: box(card),
    down: box(card.querySelector(".direction")),
    score: box(card.querySelector(".score")),
    keyColumns: getComputedStyle(key).gridTemplateColumns.split(" ").length,
    keyItems: key.children.length,
    keyRows: [...new Set([...key.children].map(li => Math.round(li.getBoundingClientRect().top)))]
      .map(top => [...key.children].filter(li => Math.round(li.getBoundingClientRect().top) === top).length),
    gap: getComputedStyle(document.getElementById("guide")).rowGap,
    sideways: document.documentElement.scrollWidth > document.documentElement.clientWidth,
  };
}

async function open(browser, width, height) {
  const context = await browser.newContext({ viewport: { width, height } });
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
  return { context, page, errors };
}

// The page scrolls smoothly: wait until it has stopped, then read where the header is.
const headerTop = async page => {
  let last = null;
  for (let tries = 0; tries < 40; tries++) {
    await page.waitForTimeout(100);
    const now = await page.evaluate(() => window.scrollY);
    if (now === last) break;
    last = now;
  }
  return page.evaluate(() => document.querySelector(".site-header").getBoundingClientRect().top);
};

(async () => {
  const browser = await chromium.launch();
  const out = { widths: {} };
  for (const [width, height] of [[390, 844], [1366, 768]]) {
    const { context, page, errors } = await open(browser, width, height);
    // the live card, drawn from the saved answer
    await page.goto(SITE + "/?disease=MONDO_0015924");
    await page.waitForSelector("#found", { state: "visible" });
    await page.click("#tab-clues");
    await page.waitForTimeout(200);
    const live = await page.evaluate("(() => {const PARTS = " + JSON.stringify(PARTS) + ";" + readCard.toString() + ";return readCard([...document.querySelectorAll('#new-cards .card')]"
      + ".find(el => el.querySelector('[data-slot=\"medicine-name\"]').textContent === 'Doxapram'));})()");
    // the guide, opened from the link beside the tabs
    await page.click('a[href="#guide-card"]');
    await page.waitForTimeout(200);
    const guide = await page.evaluate("(() => {const PARTS = " + JSON.stringify(PARTS) + ";" + readCard.toString() + ";return readCard(document.querySelector('#guide-card .card'));})()");
    const shape = await page.evaluate(geometry);
    // the guide, opened from the front page link and from ?guide=1
    await page.click("[data-guide-close]");
    await page.click("#new-search");
    await page.waitForTimeout(100);
    await page.evaluate(() => window.scrollTo(0, 400));
    await page.click('a[href="#guide"]');
    await page.waitForTimeout(200);
    const fromLink = await headerTop(page);
    await page.goto(SITE + "/?guide=1");
    await page.waitForTimeout(200);
    const fromAddress = await headerTop(page);
    out.widths[width] = { live, guide, shape, fromLink, fromAddress, errors };
    await context.close();
  }
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
    answer_file = tmp_path_factory.mktemp("guide_card") / "answer.json"
    answer_file.write_text(json.dumps(pah), encoding="utf-8")
    run = subprocess.run(
        [node, "-e", BROWSER_SCRIPT, str(PAGE_FILE), str(answer_file)],
        capture_output=True, text=True, timeout=240, cwd=str(ROOT))
    assert run.returncode == 0, run.stderr[-3000:]
    out = json.loads(run.stdout)
    for width in out["widths"].values():
        assert width["errors"] == []
    return out["widths"]


WIDTHS = ["390", "1366"]


@pytest.mark.parametrize("width", WIDTHS)
def test_browser_the_guide_card_reads_word_for_word_like_the_live_doxapram_card(seen, width):
    live, guide = seen[width]["live"], seen[width]["guide"]
    assert live[".protein-function"] and live[".protein-evidence"] and live[".report-link"]
    for part in live:
        if part == ".source-link":  # a link on the live card, a picture of one in the guide
            assert [found["text"] for found in guide[part]] == ["Source record"]
            continue
        if part == ".report-link":  # a button on the live card, a picture of one in the guide
            assert [(found["text"], found["cls"]) for found in guide[part]] == [
                (found["text"], found["cls"]) for found in live[part]]
            continue
        if part == ".ending":  # a <p> on the live card, a <div> with its letter in the guide
            assert [(found["text"], found["cls"]) for found in guide[part]] == [
                (found["text"], found["cls"]) for found in live[part]]
            continue
        assert guide[part] == live[part], part


def test_browser_the_gene_line_starts_dark_and_names_grey_as_on_the_live_card(seen):
    guide = seen["390"]["guide"]
    assert [found["text"] for found in guide[".protein-evidence"]] == [
        "Linked to this disease by: inherited gene changes, mentioned together in research papers."]
    assert [found["text"] for found in guide[".evidence-start"]] == ["Linked to this disease by:"]


@pytest.mark.parametrize("width", WIDTHS)
def test_browser_the_letters_go_down_the_card_in_reading_order(seen, width):
    letters = seen[width]["shape"]["letters"]
    assert [found["letter"] for found in letters] == LETTERS
    for before, after in zip(letters, letters[1:]):
        # On the same line (the two overlap top to bottom): left to right. Otherwise: lower down.
        same_line = after["top"] < before["bottom"] and before["top"] < after["bottom"]
        if same_line:
            assert after["left"] > before["right"], (before["letter"], after["letter"])
        else:
            assert after["top"] >= before["bottom"], (before["letter"], after["letter"])


@pytest.mark.parametrize("width", WIDTHS)
def test_browser_the_legend_grid_has_no_orphan(seen, width):
    shape = seen[width]["shape"]
    assert shape["keyItems"] == len(LEGEND)
    assert shape["keyColumns"] == 2 if width == "390" else shape["keyColumns"] in (2, 4)
    assert shape["keyRows"][-1] > 1, shape["keyRows"]
    assert sum(shape["keyRows"]) == len(LEGEND)


def test_browser_on_a_phone_d_and_e_sit_by_their_own_parts_without_crowding(seen):
    shape = seen["390"]["shape"]
    at = {found["letter"]: found for found in shape["letters"]}
    down, score, d, e = shape["down"], shape["score"], at["D"], at["E"]
    # nothing overlaps
    for one, other in ((down, d), (d, score), (score, e)):
        assert one["right"] <= other["left"] or one["bottom"] <= other["top"], (one, other)
    # D is beside Down, nearer to it than to the points; E is just after the points
    if abs(d["top"] - score["top"]) < 12:
        assert 4 <= d["left"] - down["right"] < score["left"] - d["right"]
    assert 4 <= e["left"] - score["right"] <= 8
    for letter in at.values():
        assert letter["right"] <= shape["card"]["right"]
    assert not shape["sideways"]


@pytest.mark.parametrize("width,gap", [("390", "24px"), ("1366", "32px")])
def test_browser_the_section_gaps(seen, width, gap):
    assert seen[width]["shape"]["gap"] == gap


@pytest.mark.parametrize("width", WIDTHS)
def test_browser_opening_the_guide_keeps_the_brand_header_in_view(seen, width):
    assert seen[width]["fromLink"] == 0
    assert seen[width]["fromAddress"] == 0
