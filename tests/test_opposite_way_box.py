"""Ticket 2.28. A folded box for opposite-way clues.

Kashish's ticket, 23 Nov:

On the New clues tab, every clue that carries the line "Opposite way to the
approved medicines for this disease." moves into one folded box at the
bottom of the tab. Nothing is removed. Clues left out by hand stay left out.

- Label, proposed: "These push the opposite way to the approved medicines
  for this disease." with a count, in the same style as the other boxes.
- Cards inside are unchanged and keep their order.
- The list above keeps its order without them. The tab count is unchanged.
- The box is folded, and open only when it is the only thing on the tab.
- The print page takes its first clues from the list above the box.

Her example: ADPKD (MONDO_0004691). Desmopressin, vasopressin, argipressin
tannate and lypressin are in the box. Terlipressin and conivaptan are not.

How it is built. /api/clues gains one new key, "opposite_way_box": the ids
of the clues in the box, in the list's own order. It is only there when the
box holds something. Every old key keeps its meaning: "new_clues" still
holds every new clue, in ranked order. The page moves the named cards into
the box. It does not work the rule out again.

Saved files only: fixtures/opposite_way_box/ (see its README), and
fixtures/narrower_box/ for the one answer that folder already held.
fixtures/new_in_trials/ gives a page with no opposite-way clue. No network.
"""

import copy
import json
import pathlib
import shutil
import subprocess
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from moonlight import api, engine
from moonlight.filter import sort_paths
from moonlight.records import Disease, Medicine, MedicineForm, Path, Target

import test_new_in_trials

ROOT = pathlib.Path(__file__).resolve().parent.parent
SAVED = ROOT / "fixtures" / "opposite_way_box"
REUSED = ROOT / "fixtures" / "narrower_box"  # one protein's answer, the same data
PAGE_FILE = ROOT / "web" / "index.html"
PAGE = PAGE_FILE.read_text(encoding="utf-8")

ADPKD = "MONDO_0004691"
KEY = "opposite_way_box"

# The line a card carries (ticket 3.7), word for word.
LINE = "Opposite way to the approved medicines for this disease."
# The label of the box. Proposed in the ticket: unless Kashish says no.
LABEL = "These push the opposite way to the approved medicines for this disease."
SAFETY_LINE = ("For learning and research exploration, not medical advice. Never start, stop or "
               "change any medicine without a doctor.")
NO_CLUES = "No new clues found for this disease."

# Her example. (id, name on the card, its place on the whole list)
ADPKD_BOX_4 = [
    ("CHEMBL1429", "Desmopressin", 1),
    ("CHEMBL373742", "Vasopressin", 3),
    ("CHEMBL2108986", "Argipressin Tannate", 5),
    ("CHEMBL1200690", "Lypressin", 6),
]
# The first ten of the list above the box, with their places on the whole list.
ADPKD_ABOVE_FIRST_10 = [
    ("Terlipressin", 2), ("Conivaptan", 4), ("Mozavaptan", 7), ("Tacrolimus Anhydrous", 8),
    ("Temsirolimus", 9), ("Pimecrolimus", 10), ("Zotarolimus", 11),
    ("Lutetium Oxodotreotide", 12), ("Paltusotine", 13), ("Benazepril", 14),
]
ADPKD_NEW_CLUES = 42


def load(file):
    return json.loads(file.read_text(encoding="utf-8"))


def saved_post_json(body):
    """Stands in for fetch._post_json with the saved files."""
    assert set(body) == {"query", "variables"}
    query, variables = body["query"], body["variables"]
    if "targetId" in variables:
        kind, asked = "target_drugs", variables["targetId"]
    else:
        asked = variables["diseaseId"]
        if "parents" in query:
            kind = "family"
        elif "associatedTargets" in query:
            kind = "associated_targets"
        elif "drugAndClinicalCandidates" in query:
            kind = "disease_drugs"
        else:
            kind = "disease"
    for folder in (SAVED, REUSED):
        file = folder / kind / f"{asked}.response.json"
        if file.exists():
            return load(file)
    raise AssertionError(f"no saved answer for {kind} {asked}")


def no_network():
    return [patch(name, side_effect=AssertionError("network used")) for name in (
        "requests.request", "requests.post", "requests.get",
        "requests.sessions.Session.request")]


def page_answer(disease_id, post_json=saved_post_json):
    """What /api/clues sends, from saved answers and the real hand-written files."""
    api.forget_visitors()
    guards = no_network()
    for guard in guards:
        guard.start()
    try:
        with patch("moonlight.fetch._post_json", side_effect=post_json):
            response = TestClient(api.app).get("/api/clues", params={"disease_id": disease_id})
    finally:
        for guard in guards:
            guard.stop()
        api.forget_visitors()
    assert response.status_code == 200
    return response.json()


@pytest.fixture(scope="module")
def adpkd():
    return page_answer(ADPKD)


@pytest.fixture(scope="module")
def before():
    """What main answered for ADPKD before the ticket, from the same saved answers."""
    return load(SAVED / f"clues_before_2.28_{ADPKD}.json")


def carries_the_line(clue):
    return any(protein.get("opposite_way") for protein in clue["proteins"])


# ---- hand-built pieces for the rule ----

DISEASE = Disease("TEST_0000001", "test disease")
NR3C1 = Target("ENSG00000113580", "NR3C1", "glucocorticoid receptor", 0.8)
ADRB1 = Target("ENSG00000043591", "ADRB1", "beta-1 adrenergic receptor", 0.6)
UP, DOWN, MIXED, UNKNOWN = ("AGONIST",), ("ANTAGONIST",), ("AGONIST", "ANTAGONIST"), ("BINDING AGENT",)
APPROVED_HERE, IN_TRIALS, NO_LINK = "APPROVAL", "PHASE_2", None


def path(name, medicine_id, target, action_types, link=NO_LINK):
    form = MedicineForm(medicine_id, name, best_stage="APPROVAL", disease_stage=link,
                        withdrawn=False)
    return Path(Medicine(name, (form,)), target, DISEASE, action_types, target.score,
                (f"https://example.org/{medicine_id}",))


def cards(paths, left_out=()):
    """What /api/clues sends for these hand-built paths."""
    found = api._Found(DISEASE, sort_paths(paths), [], [], [])
    with patch.object(api, "_find", return_value=found), \
            patch.object(api, "looks_wrong", return_value=set()), \
            patch.object(api, "pushes_wrong_way", return_value=set(left_out)):
        response = TestClient(api.app).get("/api/clues", params={"disease_id": DISEASE.id})
    assert response.status_code == 200
    return response.json()


APPROVED_DOWN = path("APPROVEDDOWN", "CHEMBL9000", NR3C1, DOWN, APPROVED_HERE)


# ---- the rule, on hand-built clues ----

def test_the_label_is_the_proposed_words():
    assert engine.OPPOSITE_BOX_LABEL == LABEL


def test_a_clue_with_the_line_is_in_the_box_and_one_without_is_not():
    answer = cards([APPROVED_DOWN, path("CLUEUP", "CHEMBL9001", NR3C1, UP),
                    path("CLUEDOWN", "CHEMBL9002", NR3C1, DOWN)])
    assert answer[KEY] == ["CHEMBL9001"]
    assert [clue["id"] for clue in answer["new_clues"]] == ["CHEMBL9001", "CHEMBL9002"]


def test_unknown_and_mixed_directions_are_not_in_the_box():
    answer = cards([APPROVED_DOWN, path("CLUEUP", "CHEMBL9001", NR3C1, UP),
                    path("CLUEUNKNOWN", "CHEMBL9003", NR3C1, UNKNOWN),
                    path("CLUEMIXED", "CHEMBL9004", NR3C1, MIXED)])
    assert answer[KEY] == ["CHEMBL9001"]


def test_a_clue_with_the_line_on_one_of_its_two_proteins_is_in_the_box():
    answer = cards([APPROVED_DOWN, path("TWOWAYS", "CHEMBL9005", NR3C1, UP),
                    path("TWOWAYS", "CHEMBL9005", ADRB1, DOWN)])
    (clue,) = answer["new_clues"]
    assert [protein.get("opposite_way") for protein in clue["proteins"]] == [LINE, None]
    assert answer[KEY] == ["CHEMBL9005"]


def test_the_box_keeps_the_lists_own_order():
    names = ["ZETA", "ALPHA", "MIDDLE"]
    paths = [APPROVED_DOWN] + [
        path(name, f"CHEMBL91{place}", NR3C1, UP) for place, name in enumerate(names)]
    answer = cards(paths)
    ranked = [clue["id"] for clue in answer["new_clues"]]
    assert sorted(answer[KEY]) == sorted(ranked) and answer[KEY] == ranked


def test_no_key_when_no_clue_carries_the_line():
    answer = cards([APPROVED_DOWN, path("CLUEDOWN", "CHEMBL9002", NR3C1, DOWN)])
    assert KEY not in answer
    assert KEY not in cards([path("CLUEUP", "CHEMBL9001", NR3C1, UP)])  # nothing approved


def test_an_in_trials_card_with_the_line_stays_where_it_is():
    answer = cards([APPROVED_DOWN, path("TRIALUP", "CHEMBL9006", NR3C1, UP, IN_TRIALS)])
    (studied,) = answer["being_studied"]
    assert studied["proteins"][0]["opposite_way"] == LINE  # it has the line, as before
    assert KEY not in answer  # the box is for the New clues tab only


def test_a_clue_left_out_by_hand_is_not_in_the_box_or_anywhere():
    paths = [APPROVED_DOWN, path("CLUEUP", "CHEMBL9001", NR3C1, UP),
             path("OTHERUP", "CHEMBL9007", NR3C1, UP)]
    answer = cards(paths, left_out={"CHEMBL9001"})
    assert [clue["id"] for clue in answer["new_clues"]] == ["CHEMBL9007"]
    assert answer[KEY] == ["CHEMBL9007"]
    assert answer["wrong_way_line"] == (
        "1 medicine left out because it pushes the wrong way for this disease.")
    assert "CHEMBL9001" not in json.dumps(answer)


def test_the_engine_names_the_clues_of_the_box_in_order():
    tabs = sort_paths([APPROVED_DOWN, path("CLUEUP", "CHEMBL9001", NR3C1, UP),
                       path("CLUEDOWN", "CHEMBL9002", NR3C1, DOWN),
                       path("SECONDUP", "CHEMBL9008", NR3C1, UP)])
    found = api._Found(DISEASE, tabs, [], [], [])
    one_way = engine.one_way_proteins(found.approved)
    boxed = engine.opposite_box(found.new_clues, one_way)
    assert [clue.medicine.name for clue in boxed] == [
        clue.medicine.name for clue in found.new_clues
        if clue.medicine.name in ("CLUEUP", "SECONDUP")]
    assert len(boxed) == 2
    assert engine.opposite_box(found.new_clues, {}) == []


# ---- the API: her example, from saved answers ----

def test_example_the_box_holds_the_four_in_this_order(adpkd):
    by_id = {clue["id"]: clue["medicine"] for clue in adpkd["new_clues"]}
    assert [(clue_id, by_id[clue_id]) for clue_id in adpkd[KEY]] == [
        (clue_id, name) for clue_id, name, _ in ADPKD_BOX_4]


def test_example_terlipressin_and_conivaptan_are_not_in_the_box(adpkd):
    by_name = {clue["medicine"]: clue for clue in adpkd["new_clues"]}
    for name in ("Terlipressin", "Conivaptan"):
        assert by_name[name]["id"] not in adpkd[KEY]
        assert not carries_the_line(by_name[name])


def test_example_the_box_is_exactly_the_clues_that_carry_the_line(adpkd):
    assert adpkd[KEY] == [clue["id"] for clue in adpkd["new_clues"] if carries_the_line(clue)]


def test_example_the_places_on_the_whole_list(adpkd):
    place = {clue["id"]: number for number, clue in enumerate(adpkd["new_clues"], start=1)}
    assert [place[clue_id] for clue_id in adpkd[KEY]] == [number for _, _, number in ADPKD_BOX_4]
    above = [(clue["medicine"], place[clue["id"]]) for clue in adpkd["new_clues"]
             if clue["id"] not in adpkd[KEY]]
    assert above[:10] == ADPKD_ABOVE_FIRST_10
    assert len(above) == ADPKD_NEW_CLUES - 4


def test_example_nothing_is_removed_and_every_old_key_answers_what_it_answered_before(
        adpkd, before):
    assert len(adpkd["new_clues"]) == ADPKD_NEW_CLUES
    assert KEY not in before
    assert {key: value for key, value in adpkd.items() if key != KEY} == before
    assert [key for key in adpkd if key != KEY] == list(before)  # in the same order


def test_example_the_answer_has_these_parts_in_this_order(adpkd):
    assert list(adpkd) == [
        "disease", "about_disease", "rule_text", "approved", "being_studied", "new_clues",
        "left_out", "more_in_trials", "new_in_trials", "opposite_way_box",
    ]


def test_example_a_clue_left_out_by_hand_stays_left_out():
    desmopressin = ADPKD_BOX_4[0][0]
    hand_list = [{"medicine_id": desmopressin, "disease_id": ADPKD, "date": "2026-11-23"}]
    with patch("moonlight.engine._read_left_out", return_value=hand_list):
        answer = page_answer(ADPKD)
    assert answer[KEY] == [clue_id for clue_id, _, _ in ADPKD_BOX_4[1:]]
    assert desmopressin not in [clue["id"] for clue in answer["new_clues"]]
    assert len(answer["new_clues"]) == ADPKD_NEW_CLUES - 1
    assert answer["wrong_way_line"] == (
        "1 medicine left out because it pushes the wrong way for this disease.")


def test_example_needs_no_more_requests_than_before():
    asked = []

    def counting(body):
        asked.append(body)
        return saved_post_json(body)

    page_answer(ADPKD, counting)
    # Recorded on main before the ticket: 47 questions for this page.
    assert len(asked) == 47


def test_a_page_with_no_opposite_way_clue_has_no_key():
    answer = page_answer(test_new_in_trials.LGMD.id, test_new_in_trials.saved_post_json)
    assert len(answer["new_clues"]) == 1 and KEY not in answer


# ---- the page, read as text ----

PANEL = PAGE[PAGE.index('id="panel-clues"'):PAGE.index('data-slot="left-out"')]


def test_the_page_holds_the_box_at_the_bottom_of_the_tab_with_the_exact_label():
    assert PANEL.index('id="new-cards"') < PANEL.index('id="empty"') < PANEL.index(
        'id="opposite-box"')
    assert PAGE.count(LABEL) == 1 and LABEL in PANEL
    assert (f"<summary>{LABEL} (<span id=\"opposite-count\"></span>) "
            "<span data-part=\"tap\">Tap to open</span></summary>") in PANEL
    assert '<details class="wider-box" id="opposite-box" hidden>' in PANEL  # folded, like the others
    assert 'id="opposite-cards"' in PANEL


def test_the_page_still_does_not_type_the_cards_line_itself():
    assert "Opposite way" not in PAGE  # the card's line comes from the API


def test_the_other_words_of_the_new_clues_tab_are_not_changed():
    assert ('<p class="tab-words">Approved for another disease, with no recorded link to this '
            'one. Connections worth reading about, never treatments.</p>') in PANEL
    assert f"<h3>{NO_CLUES}</h3>" in PANEL
    assert SAFETY_LINE in PAGE
    assert '" new clues. Being first on the list does not mean best."' in PAGE


# ---- the page, in a real browser ----

BROWSER_SCRIPT = r"""
"use strict";
const fs = require("fs");
const { chromium } = require("playwright");
const PAGE = fs.readFileSync(process.argv[1], "utf-8");
const ANSWERS = JSON.parse(fs.readFileSync(process.argv[2], "utf-8"));
const SITE = "http://moonlight.test";

function readClues() {
  const shownOnPage = el => !!el && el.getClientRects().length > 0;
  const words = el => el.innerText.replace(/\s+/g, " ").trim();
  const readCard = card => ({
    name: card.querySelector('[data-slot="medicine-name"]').textContent,
    rank: card.querySelector('[data-slot="rank"]').textContent,
    onScreen: card.checkVisibility(),  // false inside a folded box, or when filtered away
    line: [...card.querySelectorAll('[data-slot="opposite-way"]')].map(el => el.textContent),
    buttons: card.querySelectorAll("button").length,
    // Everything a reader can read on the card, shown or folded.
    words: card.textContent.replace(/\s+/g, " ").trim(),
  });
  const box = document.getElementById("opposite-box");
  const list = document.getElementById("new-cards");
  const empty = document.getElementById("empty");
  const leftOut = document.getElementById("wrong-way-line");
  return {
    tab: words(document.getElementById("tab-clues")),
    tabWords: words(document.querySelector("#panel-clues .tab-words")),
    list: [...list.querySelectorAll(":scope > .card")].map(readCard),
    emptyShown: shownOnPage(empty),
    filterNote: document.getElementById("filter-note").textContent.trim(),
    leftOut: shownOnPage(leftOut) ? leftOut.textContent : null,
    cardsOnTheTab: document.querySelectorAll("#panel-clues .card").length,
    box: box && {
      shown: shownOnPage(box),
      open: box.open,
      summary: words(box.querySelector("summary")),
      cards: [...box.querySelectorAll("#opposite-cards > .card")].map(readCard),
      isAfterTheList: !!(list.compareDocumentPosition(box) & Node.DOCUMENT_POSITION_FOLLOWING),
      isAfterTheEmptyWords: !!(empty.compareDocumentPosition(box) & Node.DOCUMENT_POSITION_FOLLOWING),
      // the last card of the tab is one of the box's own
      isLastWithCards: box.contains([...document.querySelectorAll("#panel-clues .card")].pop()),
    },
  };
}

function readRegister() {
  const register = document.getElementById("register");
  const reg = name => register.querySelector('[data-reg="' + name + '"]');
  const shownOnPage = el => !!el && el.getClientRects().length > 0;
  return {
    count: reg("clues-count").innerText.trim(),
    rows: [...register.querySelectorAll('#register-clues tbody tr[data-row="medicine"]')]
      .map(row => row.cells[0].innerText.trim()),
    tableShown: shownOnPage(document.getElementById("register-clues")),
    emptyShown: shownOnPage(reg("clues-empty")),
    text: register.innerText,
    safety: reg("safety").innerText.trim(),
  };
}

async function oneSearch(browser, answer) {
  const context = await browser.newContext({ viewport: { width: 390, height: 844 } });
  const page = await context.newPage();
  const errors = [], explainCalls = [];
  page.on("pageerror", problem => errors.push(String(problem)));
  await page.addInitScript(() => { window.print = () => {}; });  // no print box in the test
  await context.route("**/*", route => {
    const url = route.request().url();
    if (url === SITE + "/" || url.startsWith(SITE + "/?"))
      return route.fulfill({ contentType: "text/html; charset=utf-8", body: PAGE });
    if (url.startsWith(SITE + "/api/clues?"))
      return route.fulfill({ contentType: "application/json", body: JSON.stringify(answer) });
    if (url.startsWith(SITE + "/api/explain?")) {
      explainCalls.push(url);
      return route.fulfill({ status: 404, contentType: "application/json", body: "{}" });
    }
    return route.abort();
  });
  await page.goto(SITE + "/?disease=MONDO_TEST");
  await page.waitForSelector("#found", { state: "visible" });
  const out = { errors };
  out.firstTab = await page.evaluate(
    () => document.querySelector('.tab[aria-selected="true"]').dataset.tab);
  await page.click("#tab-clues");
  await page.waitForTimeout(300);
  out.closed = await page.evaluate(readClues);
  out.explainAskedFor = explainCalls.map(url => new URL(url).searchParams.get("clue_id"));

  // One protein's button, then the same button again to show all.
  out.filtered = {};
  for (const symbol of answer.testFilters || []) {
    await page.click('#filters button[data-protein="' + symbol + '"]');
    out.filtered[symbol] = await page.evaluate(readClues);
    await page.click('#filters button[data-protein="' + symbol + '"]');
  }
  out.afterFilters = await page.evaluate(readClues);

  const box = page.locator("#opposite-box");
  if (await box.count() && await box.isVisible() && !(await box.evaluate(el => el.open))) {
    await page.click("#opposite-box summary");
    await page.waitForTimeout(300);  // the box tells the page it was opened a moment later
  }
  out.tapped = await page.evaluate(readClues);

  await page.click("#print-page");
  await page.waitForTimeout(300);
  out.print = await page.evaluate(readRegister);
  await context.close();
  return out;
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
def answers(adpkd, before):
    """Answers of /api/clues: her example, the same page as main answered it
    before the ticket, and three cut-down ones."""
    example = copy.deepcopy(adpkd)
    example["testFilters"] = ["AVPR2", "ACE"]  # read by the test's browser script only
    boxed = set(adpkd[KEY])
    only_box = copy.deepcopy(adpkd)  # every new clue is in the box
    only_box["new_clues"] = [clue for clue in adpkd["new_clues"] if clue["id"] in boxed]
    few_above = copy.deepcopy(adpkd)  # the four, and three clues above them
    few_above["new_clues"] = [
        clue for clue in adpkd["new_clues"]
        if clue["id"] in boxed or clue["medicine"] in ("Terlipressin", "Conivaptan", "Mozavaptan")]
    left_out = copy.deepcopy(adpkd)  # with the line for clues left out by hand
    left_out["wrong_way_line"] = (
        "4 medicines left out because they push the wrong way for this disease.")
    return {"example": example, "before": before, "only_box": only_box,
            "few_above": few_above, "left_out": left_out}


@pytest.fixture(scope="module")
def seen(answers, tmp_path_factory):
    """Opens the page once per answer and returns what a reader sees."""
    node = shutil.which("node")
    if not node or subprocess.run(
            [node, "-e", "require('playwright')"], capture_output=True).returncode:
        pytest.skip("needs node with playwright to open a real browser")
    answers_file = tmp_path_factory.mktemp("opposite_way_box") / "answers.json"
    answers_file.write_text(json.dumps(answers), encoding="utf-8")
    run = subprocess.run(
        [node, "-e", BROWSER_SCRIPT, str(PAGE_FILE), str(answers_file)],
        capture_output=True, text=True, timeout=240, cwd=str(ROOT))
    assert run.returncode == 0, run.stderr[-3000:]
    out = json.loads(run.stdout)
    for name in answers:
        assert out[name]["errors"] == [], name
    return out


def names(cards_read):
    return [card["name"] for card in cards_read]


def test_browser_example_the_tab_count_is_unchanged(seen):
    assert seen["example"]["closed"]["tab"] == f"New clues ({ADPKD_NEW_CLUES})"
    assert seen["before"]["closed"]["tab"] == f"New clues ({ADPKD_NEW_CLUES})"
    assert seen["example"]["firstTab"] == "approved"  # the page still opens on Approved


def test_browser_example_the_box_holds_the_four_in_order(seen):
    box = seen["example"]["closed"]["box"]
    assert box["shown"] is True
    assert names(box["cards"]) == [name for _, name, _ in ADPKD_BOX_4]
    assert box["summary"] == f"{LABEL} (4) Tap to open"


def test_browser_example_the_box_is_folded_at_the_bottom_of_the_tab(seen):
    box = seen["example"]["closed"]["box"]
    assert box["open"] is False
    assert [card["onScreen"] for card in box["cards"]] == [False] * 4
    assert box["isAfterTheList"] and box["isAfterTheEmptyWords"] and box["isLastWithCards"]


def test_browser_example_a_tap_opens_the_box(seen):
    box = seen["example"]["tapped"]["box"]
    assert box["open"] is True
    assert [card["onScreen"] for card in box["cards"]] == [True] * 4
    assert box["summary"] == f"{LABEL} (4) Tap to close"


def test_browser_example_terlipressin_and_conivaptan_are_in_the_list_above(seen):
    closed = seen["example"]["closed"]
    assert names(closed["list"])[:2] == ["Terlipressin", "Conivaptan"]
    for name in ("Terlipressin", "Conivaptan"):
        assert name not in names(closed["box"]["cards"])


def test_browser_example_the_list_above_keeps_its_order_without_them(seen):
    before_names = names(seen["before"]["closed"]["list"])
    boxed = [name for _, name, _ in ADPKD_BOX_4]
    assert len(before_names) == ADPKD_NEW_CLUES
    assert names(seen["example"]["closed"]["list"]) == [
        name for name in before_names if name not in boxed]
    assert [card["onScreen"] for card in seen["example"]["closed"]["list"]] == [True] * 38


def test_browser_example_nothing_is_removed_and_no_card_is_there_twice(seen):
    closed = seen["example"]["closed"]
    everything = names(closed["list"]) + names(closed["box"]["cards"])
    assert closed["cardsOnTheTab"] == ADPKD_NEW_CLUES == len(everything) == len(set(everything))
    assert sorted(everything) == sorted(names(seen["before"]["closed"]["list"]))


def test_browser_example_every_card_is_unchanged_word_for_word(seen):
    """In the box or above it, a card reads exactly as it did before the
    ticket: its number, its line, its ending, everything."""
    before_cards = {card["name"]: card for card in seen["before"]["closed"]["list"]}
    closed = seen["example"]["closed"]
    for card in closed["list"] + closed["box"]["cards"]:
        old = before_cards[card["name"]]
        assert {key: card[key] for key in ("rank", "line", "buttons", "words")} == {
            key: old[key] for key in ("rank", "line", "buttons", "words")}, card["name"]


def test_browser_example_the_numbers_are_the_places_on_the_whole_list(seen):
    closed = seen["example"]["closed"]
    assert [(card["name"], int(card["rank"])) for card in closed["box"]["cards"]] == [
        (name, number) for _, name, number in ADPKD_BOX_4]
    assert [(card["name"], int(card["rank"])) for card in closed["list"][:10]] == (
        ADPKD_ABOVE_FIRST_10)


def test_browser_example_every_box_card_carries_the_line_and_no_card_above_does(seen):
    closed = seen["example"]["closed"]
    assert [card["line"] for card in closed["box"]["cards"]] == [[LINE]] * 4
    assert all(card["line"] == [] for card in closed["list"])


def test_browser_example_the_first_explanations_are_for_the_list_above(seen):
    """Five cards read their explanation when the tab opens, as before. They
    are the first five a reader can see: the list above the folded box."""
    assert len(seen["example"]["explainAskedFor"]) == 5 == len(seen["before"]["explainAskedFor"])
    # Terlipressin, Conivaptan, Mozavaptan, Tacrolimus Anhydrous, Temsirolimus
    assert sorted(seen["example"]["explainAskedFor"]) == sorted(
        ["CHEMBL2135460", "CHEMBL1755", "CHEMBL420762", "CHEMBL269732", "CHEMBL1201182"])
    # Before the ticket: the first five of the whole list.
    assert sorted(seen["before"]["explainAskedFor"]) == sorted(
        ["CHEMBL1429", "CHEMBL2135460", "CHEMBL373742", "CHEMBL1755", "CHEMBL2108986"])


def test_browser_example_the_protein_buttons_work_on_the_list_and_the_box(seen):
    avpr2 = seen["example"]["filtered"]["AVPR2"]
    assert [card["name"] for card in avpr2["list"] if card["onScreen"]] == [
        "Terlipressin", "Conivaptan", "Mozavaptan"]
    assert avpr2["box"]["shown"] is True and avpr2["box"]["summary"] == f"{LABEL} (4) Tap to open"
    ace = seen["example"]["filtered"]["ACE"]
    assert len([card for card in ace["list"] if card["onScreen"]]) == 14
    assert ace["box"]["shown"] is False  # none of its cards acts on ACE
    assert ace["filterNote"] == ("Showing only the medicines that act on ACE. The numbers are "
                                 "their places on the whole list.")
    after = seen["example"]["afterFilters"]
    assert after["box"]["shown"] is True and after == seen["example"]["closed"]


def test_browser_the_box_is_open_when_it_is_the_only_thing_on_the_tab(seen):
    closed = seen["only_box"]["closed"]
    assert closed["list"] == []
    assert closed["box"]["shown"] is True and closed["box"]["open"] is True
    assert closed["box"]["summary"] == f"{LABEL} (4) Tap to close"
    assert [card["onScreen"] for card in closed["box"]["cards"]] == [True] * 4
    assert closed["tab"] == "New clues (4)"
    assert closed["emptyShown"] is False  # there ARE new clues: the "no new clues" words stay away


def test_browser_only_the_box_the_first_explanations_are_for_its_cards(seen):
    assert sorted(seen["only_box"]["explainAskedFor"]) == sorted(
        clue_id for clue_id, _, _ in ADPKD_BOX_4)


def test_browser_no_key_means_no_box_and_the_list_as_before(seen):
    closed = seen["before"]["closed"]
    assert closed["box"]["shown"] is False and closed["box"]["cards"] == []
    assert len(closed["list"]) == ADPKD_NEW_CLUES
    assert names(closed["list"])[:6] == [
        "Desmopressin", "Terlipressin", "Vasopressin", "Conivaptan", "Argipressin Tannate",
        "Lypressin"]


def test_browser_the_left_out_line_is_still_shown_word_for_word(seen):
    assert seen["left_out"]["closed"]["leftOut"] == (
        "4 medicines left out because they push the wrong way for this disease.")
    assert seen["example"]["closed"]["leftOut"] is None
    assert seen["left_out"]["closed"]["box"] == seen["example"]["closed"]["box"]


def test_browser_the_words_above_the_list_are_unchanged(seen):
    assert seen["example"]["closed"]["tabWords"] == seen["before"]["closed"]["tabWords"] == (
        "Approved for another disease, with no recorded link to this one. Connections worth "
        "reading about, never treatments.")


# ---- the print page ----

def test_print_example_takes_its_first_ten_from_the_list_above_the_box(seen):
    printed = seen["example"]["print"]
    assert printed["rows"] == [name for name, _ in ADPKD_ABOVE_FIRST_10]
    for _, name, _ in ADPKD_BOX_4:
        assert name not in printed["rows"]
    assert LINE not in printed["text"]


def test_print_example_the_count_is_the_whole_tab_as_before(seen):
    sentence = (f"Showing the first 10 of {ADPKD_NEW_CLUES} new clues. Being first on the list "
                "does not mean best.")
    assert seen["example"]["print"]["count"] == sentence
    assert seen["before"]["print"]["count"] == sentence


def test_print_before_the_ticket_the_first_ten_held_the_four(seen):
    """The same page with no box key prints as it always did."""
    assert seen["before"]["print"]["rows"][:6] == [
        "Desmopressin", "Terlipressin", "Vasopressin", "Conivaptan", "Argipressin Tannate",
        "Lypressin"]
    assert len(seen["before"]["print"]["rows"]) == 10


def test_print_with_fewer_than_ten_above_prints_only_those(seen):
    printed = seen["few_above"]["print"]
    assert printed["rows"] == ["Terlipressin", "Conivaptan", "Mozavaptan"]
    assert printed["count"] == ("Showing the first 3 of 7 new clues. Being first on the list "
                                "does not mean best.")


def test_print_with_only_the_box_never_says_there_are_no_new_clues(seen):
    printed = seen["only_box"]["print"]
    assert printed["rows"] == [] and printed["tableShown"] is False
    assert printed["emptyShown"] is False
    assert NO_CLUES not in printed["text"]


@pytest.mark.parametrize("name", ["example", "before", "only_box", "few_above", "left_out"])
def test_print_the_safety_line_is_still_there_word_for_word(seen, name):
    assert seen[name]["print"]["safety"] == SAFETY_LINE
    assert seen[name]["print"]["text"].count(SAFETY_LINE) == 2  # the top, and the footer
