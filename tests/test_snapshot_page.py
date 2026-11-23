"""Ticket 5.1. The snapshot page (Design 1, the register).

Kashish's decision. After a search the page shows a button with the words
"Print this page". Pressing it shows a plain register of the same results
and opens the browser's print box. It uses only what the page already has:
no new request to the API, Open Targets or Gemini.

The register, top to bottom: the disease, today's date and the safety line.
APPROVED: the tab's top line, then every medicine of the main list, A to Z.
IN TRIALS: one line. NEW CLUES: the first 10, in the page's own order.
A footer on every printed page.

How these tests work. The first few read web/index.html as text. The rest
open the page in a real browser (Chromium), the same way tests/test_umami.py
does. The browser is never let outside: the page itself and the answer to
/api/clues are handed to it by the test, and every other request is stopped
and counted. The answer starts as a real one, built by moonlight/api.py from
the saved files in fixtures/narrower_box/, so every field name is the API's
own. The medicines in it are then repeated under made-up names to get
Kashish's numbers (103 approved, 55 new clues, 4 new clues).
"""

import copy
import json
import pathlib
import shutil
import subprocess
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from moonlight import api, explain
from moonlight.engine import JAPAN_LINE, NO_REGULATOR_LINE, WRONG_WARNING

from test_narrower_box import ALL, saved_post_json

ROOT = pathlib.Path(__file__).resolve().parent.parent
PAGE_FILE = ROOT / "web" / "index.html"
PAGE = PAGE_FILE.read_text(encoding="utf-8")

# Kashish's words, exactly.
BUTTON_WORDS = "Print this page"
SAFETY_LINE = (
    "For learning and research exploration, not medical advice. Never start, "
    "stop or change any medicine without a doctor."
)
APPROVED_TOP_LINE = (
    "Already approved for this disease in at least one country, according to "
    "the database. Nothing here says how well any of them works. Listed A to Z."
)
TRIALS_TOP_LINE = (
    "Approved for another disease and now being tested for this one. A "
    "separate research category, not a prediction of effectiveness. Not every "
    "trial is listed."
)
DIRECTION_LINE = "The data does not say which direction this disease needs."
NEVER_TREATMENTS = "These are connections worth reading about, never treatments."
SEE_THE_SITE = "See the site for these."
SITE = "moonlightclues.com"
COLUMNS = ["Medicine", "Protein", "Turns it", "Points / 100", "Source"]
DASH = "—"
NO_SOURCE = "No source link in the data"  # the card's own words

# Where the made-up warning and grey lines sit in the 103.
WARNED, JAPAN, NO_REGULATOR, NO_LINK = 5, 6, 7, 8


# ---- the answers the browser is handed ----

def real_answer():
    """What the API sends the page for acute lymphoblastic leukemia,
    from saved files only."""
    explain.forget_everything()
    api.forget_visitors()
    with patch("moonlight.fetch._post_json", side_effect=saved_post_json), \
            patch("requests.request", side_effect=AssertionError("network used")), \
            patch("requests.post", side_effect=AssertionError("network used")), \
            patch("requests.get", side_effect=AssertionError("network used")), \
            patch("requests.sessions.Session.request",
                  side_effect=AssertionError("network used")):
        answer = TestClient(api.app).get("/api/clues", params={"disease_id": ALL.id})
    explain.forget_everything()
    assert answer.status_code == 200
    return answer.json()


def repeated(items, count, word):
    """count medicines, copied from the real ones in turn, each with its own
    made-up name and id. The names are already in A to Z order."""
    made = []
    for number in range(count):
        item = copy.deepcopy(items[number % len(items)])
        item["id"] = "TEST%s%03d" % (word.upper(), number)
        item["medicine"] = "%s %03d" % (word, number)
        made.append(item)
    return made


def with_counts(real, approved, clues):
    answer = copy.deepcopy(real)
    answer["approved"] = repeated(real["approved"], approved, "Approvedmed")
    answer["new_clues"] = repeated(real["new_clues"], clues, "Cluemed")
    return answer


@pytest.fixture(scope="module")
def answers():
    real = real_answer()
    # The real answer holds what these tests lean on.
    assert len(real["approved"]) == 15 and len(real["new_clues"]) == 21
    assert len(real["narrower"]) == 13 and len(real["wider_group"]) == 12
    assert len(real["being_studied"]) == 16
    assert any(not medicine["proteins"] for medicine in real["approved"])
    assert any(len(medicine["proteins"]) > 1 for medicine in real["approved"])

    big = with_counts(real, 103, 55)  # examples a and b
    big["approved"][WARNED]["warning"] = WRONG_WARNING  # example d
    big["approved"][JAPAN]["proof_note"] = JAPAN_LINE
    big["approved"][NO_REGULATOR]["proof_note"] = NO_REGULATOR_LINE
    big["approved"][NO_LINK]["source"] = None

    small = with_counts(real, 3, 4)  # example c
    del small["narrower"], small["wider_group"]
    small["being_studied"] = small["being_studied"][:1]

    empty = with_counts(real, 0, 0)
    return {"big": big, "small": small, "empty": empty}


# ---- the browser ----

BROWSER_SCRIPT = r"""
"use strict";
const fs = require("fs");
const { chromium } = require("playwright");
const PAGE = fs.readFileSync(process.argv[1], "utf-8");
const ANSWERS = JSON.parse(fs.readFileSync(process.argv[2], "utf-8"));
const SITE = "http://moonlight.test";

/* One fresh window. The page and /api/clues are answered here. Everything
   else is stopped. Every request is written down. */
async function open(browser, answer, address) {
  const context = await browser.newContext({
    viewport: { width: 390, height: 844 }, timezoneId: "Asia/Kolkata", locale: "en-IN" });
  const page = await context.newPage();
  const requests = [], errors = [];
  page.on("pageerror", problem => errors.push(String(problem)));
  await page.clock.setFixedTime(new Date("2026-11-19T10:00:00+05:30"));
  await page.addInitScript(() => { window.printBoxes = 0; window.print = () => { window.printBoxes += 1; }; });
  await context.route("**/*", route => {
    const url = route.request().url();
    requests.push(url);
    if (url === SITE + "/" || url.startsWith(SITE + "/?"))
      return route.fulfill({ contentType: "text/html; charset=utf-8", body: PAGE });
    if (url.startsWith(SITE + "/api/clues?"))
      return route.fulfill({ contentType: "application/json", body: JSON.stringify(answer) });
    return route.abort();
  });
  await page.goto(SITE + address);
  return { context, page, requests, errors };
}

const BUTTON = "#print-page";

function readRegister() {
  const words = part => {
    const el = document.querySelector('#register [data-reg="' + part + '"]');
    return el ? el.innerText.trim() : null;
  };
  const table = id => {
    const el = document.getElementById(id);
    if (!el) return null;
    return {
      shown: el.getClientRects().length > 0,
      columns: [...el.querySelectorAll("thead th")].map(th => th.innerText.trim()),
      // one entry for every row, top to bottom, of either kind
      rows: [...el.querySelectorAll(":scope > tbody > tr")].map(tr => ({
        kind: tr.dataset.row,
        cells: [...tr.children].map(td => td.innerText.trim()),
      })),
    };
  };
  const register = document.getElementById("register");
  const box = el => { const r = el.getBoundingClientRect(); return r.width > 0 && r.height > 0; };
  return {
    shown: !!register && box(register),
    restOfPageShown: box(document.getElementById("found")),
    text: register ? register.innerText : "",
    disease: words("disease"), date: words("date"), safety: words("safety"),
    approvedHead: words("approved-head"), approvedTop: words("approved-top"),
    approvedEmpty: words("approved-empty"), boxes: words("boxes"),
    trialsHead: words("trials-head"), trials: words("trials"),
    cluesHead: words("clues-head"), cluesCount: words("clues-count"),
    cluesEmpty: words("clues-empty"),
    direction: words("direction"), never: words("never-treatments"),
    footer: words("footer"),
    approved: table("register-approved"), clues: table("register-clues"),
    colours: [...register.querySelectorAll("*")].filter(box).map(el => {
      const style = getComputedStyle(el);
      return style.color + " on " + style.backgroundColor;
    }).filter((value, place, all) => all.indexOf(value) === place),
  };
}

async function oneSearch(browser, answer) {
  const { context, page, requests, errors } = await open(browser, answer, "/?disease=MONDO_TEST");
  await page.waitForSelector("#found", { state: "visible" });
  const seen = { buttonAfterSearch: await page.isVisible(BUTTON),
                 buttonWords: (await page.innerText(BUTTON)).trim() };
  const before = requests.length;
  await page.click(BUTTON);
  await page.waitForTimeout(300);
  seen.printBoxes = await page.evaluate(() => window.printBoxes);
  seen.register = await page.evaluate(readRegister);
  await page.emulateMedia({ media: "print" });
  seen.inPrint = await page.evaluate(readRegister);
  await page.emulateMedia({ media: "screen" });
  seen.requestsAfterPress = requests.slice(before);
  seen.cluesRequests = requests.filter(url => url.includes("/api/clues")).length;
  /* back to the results, and the cards are as they were */
  seen.cardsBefore = await page.locator("#approved-cards .card").count();
  await page.click("#register-back");
  seen.afterBack = { registerShown: await page.isVisible("#register"),
                     resultsShown: await page.isVisible("#found"),
                     cards: await page.locator("#approved-cards .card").count() };
  seen.errors = errors;
  await context.close();
  return seen;
}

(async () => {
  const browser = await chromium.launch();
  const out = {};
  for (const name of Object.keys(ANSWERS)) out[name] = await oneSearch(browser, ANSWERS[name]);

  /* Before any search, and while a new search is starting. */
  const { context, page } = await open(browser, ANSWERS.small, "/");
  out.start = { buttonShown: await page.isVisible(BUTTON), registerShown: await page.isVisible("#register"),
                buttons: await page.locator(BUTTON).count() };
  await page.click("[data-disease-id]");
  await page.waitForSelector("#found", { state: "visible" });
  out.start.buttonAfterSearch = await page.isVisible(BUTTON);
  await context.route("**/api/search?*", () => {});  /* this search never answers */
  await page.fill("#disease-search", "anything");
  await page.click("#search-form button[type=submit]");
  await page.waitForTimeout(200);
  out.start.buttonWhileSearchingAgain = await page.isVisible(BUTTON);
  await context.close();

  await browser.close();
  console.log(JSON.stringify(out));
})().catch(problem => { console.error(problem); process.exit(1); });
"""


@pytest.fixture(scope="module")
def seen(answers, tmp_path_factory):
    """Runs the browser once and returns everything it saw."""
    node = shutil.which("node")
    if not node or subprocess.run(
            [node, "-e", "require('playwright')"], capture_output=True).returncode:
        pytest.skip("needs node with playwright to open a real browser")
    answers_file = tmp_path_factory.mktemp("snapshot") / "answers.json"
    answers_file.write_text(json.dumps(answers), encoding="utf-8")
    run = subprocess.run(
        [node, "-e", BROWSER_SCRIPT, str(PAGE_FILE), str(answers_file)],
        capture_output=True, text=True, timeout=240, cwd=str(ROOT))
    assert run.returncode == 0, run.stderr[-3000:]
    return json.loads(run.stdout)


def medicine_rows(table):
    return [row for row in table["rows"] if row["kind"] == "medicine"]


def notes_under(table):
    """For each medicine row, the note rows straight under it."""
    under, name = {}, None
    for row in table["rows"]:
        if row["kind"] == "medicine":
            name = row["cells"][0]
            under[name] = []
        else:
            assert row["kind"] == "note", row
            under[name].append(row["cells"][0])
    return under


def expected_cells(medicine):
    """What one medicine's row must say, from the answer the page was given."""
    proteins = medicine["proteins"]
    if not proteins:
        facts = [DASH, DASH, DASH]
    else:
        facts = ["\n".join(protein["symbol"] for protein in proteins),
                 "\n".join(protein["direction"] for protein in proteins),
                 "\n".join(str(protein["points"]) for protein in proteins)]
    return [medicine["medicine"]] + facts + [medicine["source"] or NO_SOURCE]


# ---- the page file itself, no browser ----

def test_the_page_has_one_button_with_kashishs_words_hidden_at_first():
    assert PAGE.count(BUTTON_WORDS) == 1
    start = PAGE.index('id="print-page"')
    tag = PAGE[PAGE.rindex("<", 0, start): PAGE.index("</button>", start)]
    assert tag.startswith("<button ")
    assert tag.endswith(">" + BUTTON_WORDS)
    assert " hidden" in tag


def test_the_register_is_in_the_page_hidden_at_first():
    start = PAGE.index('id="register"')
    tag = PAGE[PAGE.rindex("<", 0, start): PAGE.index(">", start)]
    assert " hidden" in tag


def test_the_old_words_of_the_page_are_still_there():
    assert PAGE.count(APPROVED_TOP_LINE) == 1
    assert PAGE.count(TRIALS_TOP_LINE) == 1
    assert SAFETY_LINE in PAGE
    assert ">New search</button>" in PAGE


def test_the_page_still_loads_nothing_new_from_outside():
    # The one outside address in a src or href is still the visit counter.
    assert PAGE.count('src="http') == 1
    assert 'href="http' not in PAGE


# ---- the button ----

def test_the_button_is_hidden_until_results_are_shown(seen):
    assert seen["start"]["buttons"] == 1
    assert seen["start"]["buttonShown"] is False
    assert seen["start"]["registerShown"] is False
    assert seen["start"]["buttonAfterSearch"] is True
    assert seen["big"]["buttonAfterSearch"] is True
    assert seen["big"]["buttonWords"] == BUTTON_WORDS


def test_the_button_hides_again_when_a_new_search_starts(seen):
    assert seen["start"]["buttonWhileSearchingAgain"] is False


def test_pressing_it_shows_the_register_and_opens_the_print_box_once(seen):
    for name in ("big", "small", "empty"):
        assert seen[name]["register"]["shown"] is True, name
        assert seen[name]["register"]["restOfPageShown"] is False, name
        assert seen[name]["printBoxes"] == 1, name
        assert seen[name]["errors"] == [], name


def test_pressing_it_makes_no_new_request_of_any_kind(seen):
    for name in ("big", "small", "empty"):
        assert seen[name]["requestsAfterPress"] == [], name
        assert seen[name]["cluesRequests"] == 1, name


def test_back_to_results_puts_the_page_back_as_it_was(seen):
    back = seen["big"]["afterBack"]
    assert back == {"registerShown": False, "resultsShown": True, "cards": 103}
    assert seen["big"]["cardsBefore"] == 103


# ---- 1. the top of the register ----

def test_the_top_has_the_disease_the_date_and_the_safety_line(seen):
    register = seen["big"]["register"]
    assert register["disease"] == "Acute lymphoblastic leukemia"  # as the page's title writes it
    assert register["date"] == "19 November 2026"  # the browser's clock was set to this day
    assert register["safety"] == SAFETY_LINE


def test_example_e_the_safety_line_is_in_the_register_word_for_word(seen):
    for name in ("big", "small", "empty"):
        assert SAFETY_LINE in " ".join(seen[name]["register"]["text"].split()), name
        assert seen[name]["register"]["safety"] == SAFETY_LINE, name


# ---- 2. APPROVED ----

def test_approved_starts_with_the_tabs_top_line_word_for_word(seen):
    register = seen["big"]["register"]
    assert register["approvedHead"] == "APPROVED"
    assert register["approvedTop"] == APPROVED_TOP_LINE


def test_the_tables_have_kashishs_columns(seen):
    assert seen["big"]["register"]["approved"]["columns"] == COLUMNS
    assert seen["big"]["register"]["clues"]["columns"] == COLUMNS


def test_example_a_103_approved_medicines_give_103_rows(seen, answers):
    rows = medicine_rows(seen["big"]["register"]["approved"])
    assert len(rows) == 103
    # every one of them, in the page's A to Z order, none cut off
    assert [row["cells"][0] for row in rows] == [
        medicine["medicine"] for medicine in answers["big"]["approved"]]


def test_all_103_rows_are_still_there_on_paper(seen):
    printed = seen["big"]["inPrint"]
    assert printed["shown"] is True
    assert printed["restOfPageShown"] is False
    assert len(medicine_rows(printed["approved"])) == 103
    assert printed["approved"]["shown"] is True


def test_every_approved_row_says_what_its_card_says(seen, answers):
    rows = medicine_rows(seen["big"]["register"]["approved"])
    for row, medicine in zip(rows, answers["big"]["approved"]):
        assert row["cells"] == expected_cells(medicine)


def test_turns_it_is_up_down_mixed_or_unknown(seen):
    for name in ("approved", "clues"):
        for row in medicine_rows(seen["big"]["register"][name]):
            for word in row["cells"][2].split("\n"):
                assert word in {"up", "down", "mixed", "unknown", DASH}, row


def test_a_medicine_with_no_path_shows_a_dash_three_times(seen, answers):
    no_path = [medicine for medicine in answers["big"]["approved"] if not medicine["proteins"]]
    assert no_path
    rows = {row["cells"][0]: row["cells"] for row in medicine_rows(seen["big"]["register"]["approved"])}
    for medicine in no_path:
        assert rows[medicine["medicine"]][1:4] == [DASH, DASH, DASH]


def test_a_medicine_with_no_source_says_so_in_the_cards_words(seen, answers):
    rows = medicine_rows(seen["big"]["register"]["approved"])
    assert answers["big"]["approved"][NO_LINK]["source"] is None
    assert rows[NO_LINK]["cells"][4] == NO_SOURCE
    assert PAGE.count(NO_SOURCE) >= 1


def test_example_d_a_red_warning_is_in_the_register_under_its_row(seen, answers):
    register = seen["big"]["register"]
    assert WRONG_WARNING in register["text"]
    under = notes_under(register["approved"])
    warned = answers["big"]["approved"][WARNED]["medicine"]
    assert under[warned] == ["Warning: " + WRONG_WARNING]


def test_the_japan_line_and_the_no_regulator_line_sit_under_their_rows(seen, answers):
    under = notes_under(seen["big"]["register"]["approved"])
    approved = answers["big"]["approved"]
    assert under[approved[JAPAN]["medicine"]] == [JAPAN_LINE]
    assert under[approved[NO_REGULATOR]["medicine"]] == [NO_REGULATOR_LINE]
    # and no other medicine has a line under it
    assert sum(len(lines) for lines in under.values()) == 3


def test_under_the_table_one_line_counts_both_boxes(seen):
    assert seen["big"]["register"]["boxes"] == (
        "13 more medicines are in the narrower box and 12 more are in the "
        "wider box. " + SEE_THE_SITE)


def test_with_both_boxes_empty_the_line_says_zero(seen):
    assert seen["small"]["register"]["boxes"] == (
        "0 more medicines are in the narrower box and 0 more are in the "
        "wider box. " + SEE_THE_SITE)


def test_no_boxed_medicine_is_in_the_register(seen, answers):
    text = seen["big"]["register"]["text"]
    for medicine in answers["big"]["narrower"] + answers["big"]["wider_group"]:
        assert medicine["medicine"] not in text


# ---- 3. IN TRIALS ----

def test_in_trials_is_one_line_the_number_then_the_tabs_top_line(seen):
    assert seen["big"]["register"]["trialsHead"] == "IN TRIALS"
    assert seen["big"]["register"]["trials"] == "16 medicines. " + TRIALS_TOP_LINE
    assert seen["small"]["register"]["trials"] == "1 medicine. " + TRIALS_TOP_LINE
    assert seen["empty"]["register"]["trials"] == "16 medicines. " + TRIALS_TOP_LINE


def test_no_in_trials_medicine_is_named_in_the_register(seen, answers):
    text = seen["big"]["register"]["text"]
    for medicine in answers["big"]["being_studied"]:
        assert medicine["medicine"] not in text


# ---- 4. NEW CLUES ----

def test_example_b_55_new_clues_give_10_rows_and_the_words(seen, answers):
    register = seen["big"]["register"]
    assert register["cluesHead"] == "NEW CLUES"
    rows = medicine_rows(register["clues"])
    assert len(rows) == 10
    assert "Showing the first 10 of 55 new clues." in register["text"]
    assert register["cluesCount"] == (
        "Showing the first 10 of 55 new clues. Being first on the list does not mean best.")
    # the first ten, in the page's own order
    for row, clue in zip(rows, answers["big"]["new_clues"][:10]):
        assert row["cells"] == expected_cells(clue)


def test_example_c_4_new_clues_give_4_rows_and_the_first_4_of_4(seen, answers):
    register = seen["small"]["register"]
    rows = medicine_rows(register["clues"])
    assert len(rows) == 4
    assert "the first 4 of 4" in register["text"]
    assert register["cluesCount"] == (
        "Showing the first 4 of 4 new clues. Being first on the list does not mean best.")
    assert [row["cells"][0] for row in rows] == [
        clue["medicine"] for clue in answers["small"]["new_clues"]]


def test_below_the_clues_the_two_lines_word_for_word(seen):
    for name in ("big", "small", "empty"):
        assert seen[name]["register"]["direction"] == DIRECTION_LINE, name
        assert seen[name]["register"]["never"] == NEVER_TREATMENTS, name


def test_the_clue_rows_carry_no_line_that_hints_one_is_better(seen):
    assert notes_under(seen["big"]["register"]["clues"]) == {
        row["cells"][0]: [] for row in medicine_rows(seen["big"]["register"]["clues"])}


# ---- nothing to list ----

def test_with_no_approved_medicine_and_no_clue_the_page_says_so_in_its_own_words(seen):
    register = seen["empty"]["register"]
    assert medicine_rows(register["approved"]) == []
    assert medicine_rows(register["clues"]) == []
    assert register["approved"]["shown"] is False
    assert register["clues"]["shown"] is False
    assert register["cluesCount"] == (
        "Showing the first 0 of 0 new clues. Being first on the list does not mean best.")
    assert register["cluesEmpty"] == "No new clues found for this disease."
    assert register["approvedTop"] == APPROVED_TOP_LINE
    assert register["boxes"].startswith("13 more medicines are in the narrower box")


# ---- 5. the footer, and black on white ----

def test_the_footer_has_the_site_and_the_safety_line(seen):
    for view in ("register", "inPrint"):
        footer = " ".join(seen["big"][view]["footer"].split())
        assert SITE in footer
        assert SAFETY_LINE in footer


def test_the_footer_is_set_to_come_back_on_every_printed_page():
    # A table's foot is printed again at the bottom of each page it runs over.
    start = PAGE.index('data-reg="footer"')
    assert "<tfoot" in PAGE[PAGE.rindex("<table", 0, start): start]
    assert "table-footer-group" in PAGE


def test_the_register_is_black_on_white(seen):
    for view in ("register", "inPrint"):
        for colours in seen["big"][view]["colours"]:
            ink, paper = colours.split(" on ")
            assert ink == "rgb(0, 0, 0)", colours
            assert paper in {"rgb(255, 255, 255)", "rgba(0, 0, 0, 0)"}, colours
