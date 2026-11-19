"""Ticket 5.2. The register shows the opposite-way line.

Kashish's decision. On screen, a New clues card can show under one of its
proteins (ticket 3.7):

    Opposite way to the approved medicines for this disease.

The printed register (ticket 5.1) now prints the same words, word for word,
in its NEW CLUES table, directly under that protein's "Turns it" value in
the same row. A medicine with two proteins shows the words only by the
protein they are true for. The page uses the value the API already sent
("opposite_way" on the protein). It does not work the rule out again.
Approved rows never get the words.

How these tests work. Like tests/test_snapshot_page.py: the page is opened
in a real browser (Chromium) that is never let outside. The answer to
/api/clues starts as a real one, built by moonlight/api.py from the saved
files in fixtures/narrower_box/, so every field name is the API's own. Then
the first few new clues are given hand-made proteins, so each of the
ticket's examples has its own row:

    Clue A  one protein, with the line                    (example a)
    Clue B  two proteins, the line on the FIRST only      (example b)
    Clue C  two proteins, the line on the SECOND only     (example b)
    Clue D  one protein, no line                          (example c)

One Approved medicine is also handed the line by force, which the real API
never does, to show an Approved row still does not print it (example d).
"""

import copy
import json
import shutil
import subprocess

import pytest

from moonlight.engine import OPPOSITE_LINE

from test_snapshot_page import PAGE, PAGE_FILE, ROOT, SAFETY_LINE, real_answer

# Word for word from the ticket.
LINE = "Opposite way to the approved medicines for this disease."

TURNS_IT = 2  # the "Turns it" column, counting from 0


def protein(symbol, direction, points, opposite=False):
    made = {"symbol": symbol, "direction": direction, "points": points}
    if opposite:
        made["opposite_way"] = LINE  # the API's own field name (moonlight/api.py)
    return made


@pytest.fixture(scope="module")
def answer():
    real = real_answer()
    made = copy.deepcopy(real)
    clues = made["new_clues"]
    assert len(clues) >= 5

    def remake(place, name, proteins):
        # keep every other field of the real protein, change only these
        template = clues[place]["proteins"][0]
        clues[place]["medicine"] = name
        clues[place]["proteins"] = [dict(copy.deepcopy(template), **one) for one in proteins]
        for one, wanted in zip(clues[place]["proteins"], proteins):
            if "opposite_way" not in wanted:
                one.pop("opposite_way", None)

    remake(0, "Clue A", [protein("AAA1", "up", 71, opposite=True)])
    remake(1, "Clue B", [protein("BBB1", "down", 62, opposite=True), protein("BBB2", "up", 53)])
    remake(2, "Clue C", [protein("CCC1", "down", 44), protein("CCC2", "up", 35, opposite=True)])
    remake(3, "Clue D", [protein("DDD1", "down", 26)])
    for clue in clues[4:]:  # no other clue has the line
        for one in clue["proteins"]:
            one.pop("opposite_way", None)

    # An Approved medicine handed the line by force. The real API never does this.
    forced = next(medicine for medicine in made["approved"] if medicine["proteins"])
    forced["medicine"] = "Approved Forced"
    forced["proteins"][0]["opposite_way"] = LINE
    return made


BROWSER_SCRIPT = r"""
"use strict";
const fs = require("fs");
const { chromium } = require("playwright");
const PAGE = fs.readFileSync(process.argv[1], "utf-8");
const ANSWER = fs.readFileSync(process.argv[2], "utf-8");
const SITE = "http://moonlight.test";

function readRegister() {
  const shownOnPage = el => el.getClientRects().length > 0;
  const table = id => [...document.querySelectorAll("#" + id + " > tbody > tr")].map(tr => ({
    kind: tr.dataset.row,
    // each cell as its lines, top to bottom, as a reader sees them
    cells: [...tr.children].map(td => td.innerText.trim().split("\n").map(line => line.trim())),
    hiddenLines: [...tr.querySelectorAll("td *")].filter(el => !shownOnPage(el)).length,
  }));
  const register = document.getElementById("register");
  return {
    text: register.innerText,
    safety: register.querySelector('[data-reg="safety"]').innerText.trim(),
    footer: register.querySelector('[data-reg="footer"]').innerText.trim(),
    approved: table("register-approved"),
    clues: table("register-clues"),
  };
}

(async () => {
  const browser = await chromium.launch();
  const context = await browser.newContext({ viewport: { width: 390, height: 844 } });
  const page = await context.newPage();
  const errors = [], outside = [];
  page.on("pageerror", problem => errors.push(String(problem)));
  await page.addInitScript(() => { window.print = () => {}; });
  await context.route("**/*", route => {
    const url = route.request().url();
    if (url === SITE + "/" || url.startsWith(SITE + "/?"))
      return route.fulfill({ contentType: "text/html; charset=utf-8", body: PAGE });
    if (url.startsWith(SITE + "/api/clues?"))
      return route.fulfill({ contentType: "application/json", body: ANSWER });
    outside.push(url);
    return route.abort();
  });
  await page.goto(SITE + "/?disease=MONDO_TEST");
  await page.waitForSelector("#found", { state: "visible" });
  /* the cards on screen, before the register: which proteins carry the line */
  const cards = await page.evaluate(() => [...document.querySelectorAll('#panel-clues [data-slot="opposite-way"]')]
    .map(line => line.closest('[data-slot="protein"]').querySelector(".protein-id").textContent
      + ": " + line.textContent));
  await page.click("#print-page");
  await page.waitForTimeout(300);
  const out = { cards, errors };
  out.screen = await page.evaluate(readRegister);
  await page.emulateMedia({ media: "print" });
  out.paper = await page.evaluate(readRegister);
  await browser.close();
  console.log(JSON.stringify(out));
})().catch(problem => { console.error(problem); process.exit(1); });
"""


@pytest.fixture(scope="module")
def seen(answer, tmp_path_factory):
    """Runs the browser once and returns everything it saw."""
    node = shutil.which("node")
    if not node or subprocess.run(
            [node, "-e", "require('playwright')"], capture_output=True).returncode:
        pytest.skip("needs node with playwright to open a real browser")
    answer_file = tmp_path_factory.mktemp("opposite") / "answer.json"
    answer_file.write_text(json.dumps(answer), encoding="utf-8")
    run = subprocess.run(
        [node, "-e", BROWSER_SCRIPT, str(PAGE_FILE), str(answer_file)],
        capture_output=True, text=True, timeout=240, cwd=str(ROOT))
    assert run.returncode == 0, run.stderr[-3000:]
    out = json.loads(run.stdout)
    assert out["errors"] == []
    return out


VIEWS = ["screen", "paper"]


def row_of(table, name):
    rows = [row for row in table if row["kind"] == "medicine" and row["cells"][0] == [name]]
    assert len(rows) == 1, name
    return rows[0]


def words_in_row(row):
    return sum(line.count(LINE) for cell in row["cells"] for line in cell)


# ---- the words themselves ----

def test_the_words_are_the_engines_words():
    assert LINE == OPPOSITE_LINE


def test_the_page_does_not_type_the_words_itself():
    # They come from the API's answer. The page holds no copy to drift apart.
    assert "Opposite way" not in PAGE


# ---- example a ----

@pytest.mark.parametrize("view", VIEWS)
def test_example_a_a_clue_with_the_line_has_the_words_once_under_turns_it(seen, view):
    row = row_of(seen[view]["clues"], "Clue A")
    assert words_in_row(row) == 1
    assert row["cells"][TURNS_IT] == ["up", LINE]
    assert row["cells"][1] == ["AAA1"]
    assert row["cells"][3] == ["71"]
    assert row["hiddenLines"] == 0


# ---- example b ----

@pytest.mark.parametrize("view", VIEWS)
def test_example_b_the_line_on_the_first_protein_only(seen, view):
    row = row_of(seen[view]["clues"], "Clue B")
    assert words_in_row(row) == 1
    # straight under "down" (BBB1), and above "up" (BBB2)
    assert row["cells"][TURNS_IT] == ["down", LINE, "up"]
    assert row["cells"][1] == ["BBB1", "BBB2"]
    assert row["cells"][3] == ["62", "53"]


@pytest.mark.parametrize("view", VIEWS)
def test_example_b_the_line_on_the_second_protein_only(seen, view):
    row = row_of(seen[view]["clues"], "Clue C")
    assert words_in_row(row) == 1
    # straight under "up" (CCC2), not under "down" (CCC1)
    assert row["cells"][TURNS_IT] == ["down", "up", LINE]
    assert row["cells"][1] == ["CCC1", "CCC2"]
    assert row["cells"][3] == ["44", "35"]


# ---- example c ----

@pytest.mark.parametrize("view", VIEWS)
def test_example_c_a_clue_without_the_line_does_not_have_the_words(seen, view):
    row = row_of(seen[view]["clues"], "Clue D")
    assert words_in_row(row) == 0
    assert row["cells"][TURNS_IT] == ["down"]


@pytest.mark.parametrize("view", VIEWS)
def test_the_words_are_in_the_register_three_times_and_nowhere_else(seen, view):
    # Clue A, Clue B and Clue C: once each. No other row, no other place.
    assert seen[view]["text"].count(LINE) == 3
    assert sum(words_in_row(row) for row in seen[view]["clues"]) == 3


def test_the_register_and_the_cards_agree(seen):
    # The same proteins carry the line on the cards and in the register.
    assert sorted(seen["cards"]) == [
        "AAA1: " + LINE, "BBB1: " + LINE, "CCC2: " + LINE]


# ---- example d ----

@pytest.mark.parametrize("view", VIEWS)
def test_example_d_an_approved_row_never_has_the_words(seen, view):
    approved = seen[view]["approved"]
    assert len(approved) > 0
    row_of(approved, "Approved Forced")  # the row handed the line is there
    assert sum(words_in_row(row) for row in approved) == 0


# ---- the rows are as they were ----

@pytest.mark.parametrize("view", VIEWS)
def test_the_number_and_order_of_rows_did_not_change(seen, answer, view):
    clue_rows = seen[view]["clues"]
    assert [row["kind"] for row in clue_rows] == ["medicine"] * 10
    assert [row["cells"][0][0] for row in clue_rows] == [
        clue["medicine"] for clue in answer["new_clues"][:10]]
    approved = [row for row in seen[view]["approved"] if row["kind"] == "medicine"]
    assert [row["cells"][0][0] for row in approved] == [
        medicine["medicine"] for medicine in answer["approved"]]


# ---- example e ----

@pytest.mark.parametrize("view", VIEWS)
def test_example_e_the_safety_line_is_still_in_the_register_word_for_word(seen, view):
    assert seen[view]["safety"] == SAFETY_LINE
    assert SAFETY_LINE in seen[view]["footer"]
    assert seen[view]["text"].count(SAFETY_LINE) == 2  # the top, and the footer
