"""Ticket 2.36. The printed page shows what the screen shows.

The register (the plain page behind "Print this page") must hold the same
Approved cards in the same groups, with the same lines, as the screen:

- every grey line and the red warning a card shows, in the card's order;
- under APPROVED the main list only, as the screen's main list;
- then each Approved box the screen shows, in the screen's order (narrower,
  wider, no-regulator, red), each under its own title as the screen writes it;
- a box with no cards is not printed;
- there is no "boxes" line: every box is printed in full (Kashish's decision).

How these tests work. The page is opened in a real browser (Chromium), as
tests/test_snapshot_page.py does. The browser never reaches the network: the
page and the answer to /api/clues are handed to it, and every other request
is stopped. The answers are built by moonlight/api.py from saved files only
(fixtures/), for type 2 diabetes, haemophilia A, Huntington disease and
Graves disease. The test reads the SCREEN's cards first, then presses the
print button and reads the REGISTER, and compares the two.
"""

import json
import pathlib
import shutil
import subprocess

import pytest

import old_flag_saved
import test_approvals_third_batch as huntington_files
import test_label_limit_line as graves_files
import test_withdrawal_line as hem_a_files

ROOT = pathlib.Path(__file__).resolve().parent.parent
PAGE_FILE = ROOT / "web" / "index.html"

T2D = "MONDO_0005148"
HEM_A = "MONDO_0010602"
HUNTINGTON = "MONDO_0007739"
GRAVES = "MONDO_0005364"
DISEASES = {"t2d": T2D, "hem_a": HEM_A, "huntington": HUNTINGTON, "graves": GRAVES}

LINE = "The database records a withdrawal for this medicine in some country or region."


def answers_from_saved_files():
    return {
        "t2d": old_flag_saved.page_answer(T2D),
        "hem_a": hem_a_files.page_answer(HEM_A, hem_a_files.saved_post_json),
        "huntington": hem_a_files.page_answer(HUNTINGTON, huntington_files.saved_post_json),
        "graves": hem_a_files.page_answer(GRAVES, graves_files.saved_post_json),
    }


BROWSER_SCRIPT = r"""
"use strict";
const fs = require("fs");
const { chromium } = require("playwright");
const PAGE = fs.readFileSync(process.argv[1], "utf-8");
const ANSWERS = JSON.parse(fs.readFileSync(process.argv[2], "utf-8"));
const SITE = "http://moonlight.test";

function readScreen() {
  function screenCard(card) {
    const shown = el => el && !el.hidden && el.getClientRects().length > 0;
    const lines = [];
    for (const sel of ['[data-slot="label"]', '[data-slot="proof-note"]', '[data-slot="limit-note"]',
                       '[data-slot="withdrawal-note"]', '[data-slot="warning"]']) {
      const el = card.querySelector(sel);
      if (shown(el)) lines.push(el.textContent.trim());
    }
    const noSource = card.querySelector('[data-part="no-source"]');
    return { name: card.querySelector("h3").textContent.trim(), lines,
             noSource: shown(noSource) ? noSource.textContent.trim() : null };
  }
  const boxes = ["narrower-box", "wider-box", "no-regulator-box", "wrong-box"].map(id => {
    const box = document.getElementById(id);
    if (box.hidden) return null;
    const summary = box.querySelector("summary").cloneNode(true);
    summary.querySelector('[data-part="tap"]').remove();
    return { id, title: summary.textContent.replace(/\s+/g, " ").trim(),
             cards: [...box.querySelectorAll(".card")].map(screenCard) };
  }).filter(Boolean);
  return { main: [...document.querySelectorAll("#approved-cards .card")].map(screenCard), boxes };
}

function readRegister() {
  const bodies = table => [...table.querySelectorAll(":scope > tbody")].map(body => {
    const rows = [...body.rows];
    return { name: rows[0].cells[0].innerText.trim(), source: rows[0].cells[4].innerText.trim(),
             notes: rows.slice(1).map(row => row.cells[0].textContent.trim()) };
  });
  const holder = document.querySelector('#register [data-reg="approved-boxes"]');
  const boxes = [];
  for (const title of holder ? holder.querySelectorAll(":scope > h3") : [])
    boxes.push({ title: title.textContent.trim(), cards: bodies(title.nextElementSibling) });
  const words = part => { const el = document.querySelector('#register [data-reg="' + part + '"]');
                          return el && !el.hidden ? el.textContent.trim() : null; };
  return { main: bodies(document.getElementById("register-approved")), boxes,
           boxesLine: words("boxes"), empty: words("approved-empty"),
           headings: [...document.querySelectorAll("#register h2")].map(h => h.textContent.trim()) };
}

(async () => {
  const browser = await chromium.launch();
  const out = {};
  for (const name of Object.keys(ANSWERS)) {
    const context = await browser.newContext({ viewport: { width: 390, height: 844 } });
    const page = await context.newPage();
    const errors = [];
    page.on("pageerror", problem => errors.push(String(problem)));
    await page.addInitScript(() => { window.print = () => {}; });
    await context.route("**/*", route => {
      const url = route.request().url();
      if (url === SITE + "/" || url.startsWith(SITE + "/?"))
        return route.fulfill({ contentType: "text/html; charset=utf-8", body: PAGE });
      if (url.startsWith(SITE + "/api/clues?"))
        return route.fulfill({ contentType: "application/json", body: JSON.stringify(ANSWERS[name]) });
      return route.abort();
    });
    await page.goto(SITE + "/?disease=" + ANSWERS[name].disease.id);
    await page.waitForSelector("#found", { state: "visible" });
    const screen = await page.evaluate(readScreen);
    await page.click("#print-page");
    await page.waitForTimeout(200);
    out[name] = { screen, register: await page.evaluate(readRegister), errors };
    await context.close();
  }
  await browser.close();
  console.log(JSON.stringify(out));
})().catch(problem => { console.error(problem); process.exit(1); });
"""


@pytest.fixture(scope="module")
def answers():
    return answers_from_saved_files()


@pytest.fixture(scope="module")
def seen(answers, tmp_path_factory):
    node = shutil.which("node")
    if not node or subprocess.run(
            [node, "-e", "require('playwright')"], capture_output=True).returncode:
        pytest.skip("needs node with playwright to open a real browser")
    answers_file = tmp_path_factory.mktemp("print") / "answers.json"
    answers_file.write_text(json.dumps(answers), encoding="utf-8")
    run = subprocess.run(
        [node, "-e", BROWSER_SCRIPT, str(PAGE_FILE), str(answers_file)],
        capture_output=True, text=True, timeout=240, cwd=str(ROOT))
    assert run.returncode == 0, run.stderr[-3000:]
    return json.loads(run.stdout)


def screen_notes(screen_card, answer_card):
    """The screen's lines for a card; the red one is the last, and only when the card has one."""
    lines = list(screen_card["lines"])
    if answer_card.get("warning"):
        lines[-1] = "Warning: " + lines[-1]
    return lines


# ---- the saved answers hold what the ticket speaks about ----

def test_the_saved_answers_hold_the_lines_the_ticket_names(answers):
    t2d = answers["t2d"]["approved"]
    assert sum(1 for card in t2d if card.get("withdrawal_note") == LINE) >= 10
    hem = {card["id"]: card for card in answers["hem_a"]["approved"]}
    assert hem["CHEMBL4297873"]["withdrawal_note"] == LINE
    assert answers["huntington"]["wrong_approvals_box"]
    assert answers["graves"]["approved"]


# ---- the printed page and the screen ----

@pytest.mark.parametrize("name", list(DISEASES))
def test_the_page_draws_without_an_error(seen, name):
    assert seen[name]["errors"] == []


@pytest.mark.parametrize("name", list(DISEASES))
def test_every_line_a_card_shows_is_printed_under_it(seen, answers, name):
    answer = answers[name]
    every = {card["id"]: card for part in ("approved", "narrower", "wider_group")
             for card in answer.get(part, [])}
    by_name = {card["medicine"]: card for card in every.values()}
    screen, register = seen[name]["screen"], seen[name]["register"]
    pairs = list(zip(screen["main"], register["main"]))
    for box_screen, box_register in zip(screen["boxes"], register["boxes"]):
        pairs += list(zip(box_screen["cards"], box_register["cards"]))
    assert pairs
    for on_screen, printed in pairs:
        assert on_screen["name"] == printed["name"]
        assert printed["notes"] == screen_notes(on_screen, by_name[on_screen["name"]]), on_screen["name"]
        if on_screen["noSource"]:
            assert printed["source"] == on_screen["noSource"]


def test_type_2_diabetes_prints_the_withdrawal_line_on_ten_main_list_cards(seen):
    printed = [card for card in seen["t2d"]["register"]["main"] if LINE in card["notes"]]
    assert len(printed) >= 10
    names = {card["name"] for card in printed}
    assert {"Metformin", "Pioglitazone", "Rosiglitazone"} <= names


def test_haemophilia_a_prints_the_withdrawal_line_under_octocog_alfa(seen):
    (octocog,) = [card for card in seen["hem_a"]["register"]["main"] if card["name"] == "Octocog Alfa"]
    assert LINE in octocog["notes"]


@pytest.mark.parametrize("name", list(DISEASES))
def test_the_printed_main_list_equals_the_screens_main_list(seen, name):
    assert [card["name"] for card in seen[name]["register"]["main"]] == \
        [card["name"] for card in seen[name]["screen"]["main"]]


@pytest.mark.parametrize("name", list(DISEASES))
def test_each_boxs_printed_title_and_cards_equal_the_screens(seen, name):
    screen, register = seen[name]["screen"]["boxes"], seen[name]["register"]["boxes"]
    assert [box["title"] for box in register] == [box["title"] for box in screen]
    for box_screen, box_register in zip(screen, register):
        assert [card["name"] for card in box_register["cards"]] == \
            [card["name"] for card in box_screen["cards"]]


@pytest.mark.parametrize("name", list(DISEASES))
def test_the_boxes_come_in_the_screens_order_and_none_is_empty(seen, name):
    screen = seen[name]["screen"]["boxes"]
    order = ["narrower-box", "wider-box", "no-regulator-box", "wrong-box"]
    assert [box["id"] for box in screen] == [i for i in order if i in {b["id"] for b in screen}]
    assert all(box["cards"] for box in seen[name]["register"]["boxes"])


def test_the_red_and_no_regulator_cards_are_not_under_the_main_approved_heading(seen, answers):
    answer = answers["huntington"]
    outside = set(answer["wrong_approvals_box"]) | set(answer.get("no_regulator_box", []))
    assert outside
    names = {card["id"]: card["medicine"] for card in answer["approved"]}
    main = {card["name"] for card in seen["huntington"]["register"]["main"]}
    for card_id in outside:
        assert names[card_id] not in main
    in_boxes = {card["name"] for box in seen["huntington"]["register"]["boxes"] for card in box["cards"]}
    assert {names[card_id] for card_id in outside} <= in_boxes


@pytest.mark.parametrize("name", list(DISEASES))
def test_there_is_no_boxes_line(seen, name):
    # Every box is printed in full under its own title, so a count adds nothing
    # (Kashish's decision for ticket 2.36).
    assert seen[name]["register"]["boxesLine"] is None


def test_nothing_else_in_the_print_page_changes(seen):
    for name in DISEASES:
        assert seen[name]["register"]["headings"] == ["APPROVED", "IN TRIALS", "NEW CLUES"]
