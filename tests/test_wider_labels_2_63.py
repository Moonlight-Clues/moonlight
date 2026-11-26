"""Ticket 2.63. The wider-label line (W1) and the points line (W2).

Words signed by Kashish on 26 Nov (sheet W1, W2).

W1. moonlight/wider_labels.json is a hand list, one entry per card:
{"medicine_id", "disease_id", "group", "date", "label"}. /api/clues gives
such a card the key "wider_label_note" with exactly
"The label names {group}, which includes this disease." The page shows it
as a grey line under the card's other lines. A pair that is also on
corrections.json stops the app before it serves a page.

W2. Every card that shows protein points gets, once, under its protein rows:
"Points: how strongly research data links this protein to the disease, out
of 100. Not how well the medicine works." A card with no points never does.

Givosiran on acute intermittent porphyria is also added to approvals.json
(sheet D2), so it sits on the main list. Its test is marked salt_parents
(ticket 3.23): givosiran and givosiran sodium are one card.

Saved answers only (fixtures/wider_labels_2_63/). No network.
"""

import json
import pathlib
import shutil
import subprocess
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from moonlight import api, approval_years, engine, fetch

import wider_labels_saved as saved
from wider_labels_saved import AIP, HAEMOPHILIA_A, T2D

# Every test here reads the real wider-labels list (see conftest.py, ticket 2.63).
pytestmark = pytest.mark.wider_labels

ROOT = pathlib.Path(__file__).resolve().parent.parent
WIDER_FILE = ROOT / "moonlight" / "wider_labels.json"
APPROVALS_FILE = ROOT / "moonlight" / "approvals.json"
PAGE_FILE = ROOT / "web" / "index.html"

LINE = "The label names {group}, which includes this disease."
POINTS_LINE = ("Points: how strongly research data links this protein to the disease, "
               "out of 100. Not how well the medicine works.")

GIVLAARI = "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=167e663c-11e1-497b-a3fc-951d65d58eaa"
GIVOSIRAN, GIVOSIRAN_SODIUM = "CHEMBL4297760", "CHEMBL4594265"

# The six cards: (medicine id, disease id) -> (group, label). Labels read by hand, 26 Nov.
SIX = {
    ("CHEMBL2107869", T2D): ("diabetes mellitus",  # insulin degludec, Tresiba
                             "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=456c5e87-3dfd-46fa-8ac0-c6128d4c97c6"),
    ("CHEMBL1201497", T2D): ("diabetes mellitus",  # insulin glargine, Lantus
                             "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=3a97c40f-0c83-42d7-a8ee-484b208db4e3"),
    ("CHEMBL1201631", T2D): ("diabetes mellitus",  # insulin human, Humulin R U-500
                             "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=b60e8dd0-1d48-4dc9-87fd-e14675255e8c"),
    ("CHEMBL4594581", T2D): ("diabetes mellitus",  # insulin icodec, Awiqli
                             "https://www.ema.europa.eu/en/medicines/human/EPAR/awiqli"),
    ("CHEMBL877", HAEMOPHILIA_A): ("hemophilia",  # tranexamic acid
                                   "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=19f3483e-da9f-4a11-b2eb-b3c6d5d92fc8"),
    (GIVOSIRAN, AIP): ("acute hepatic porphyria", GIVLAARI),  # givosiran, Givlaari
}
INSULIN_GLARGINE = "CHEMBL1201497"

# Sheet D2: the rows this ticket adds at the end of approvals.json. Older tests
# that count or list that file read this, the way ticket 2.62's RED_ROWS is read.
APPROVAL_ROWS = [
    {"medicine_id": GIVOSIRAN, "name": "Givosiran", "disease_id": AIP,
     "date": "2026-11-26", "label": GIVLAARI},
]

LISTS = ("approved", "narrower", "wider_group", "being_studied", "new_clues",
         "more_in_trials", "new_in_trials")


def no_years():
    return patch.object(approval_years, "load", return_value={})


def cards(page):
    """Every card on the page: (list name, card)."""
    return [(name, card) for name in LISTS for card in page.get(name, [])]


def without_note(card):
    return {key: value for key, value in card.items() if key != "wider_label_note"}


@pytest.fixture(scope="module")
def pages():
    """T2D and haemophilia A as every unmarked test sees them (salt list off)."""
    return {disease: saved.page_answer(disease, [no_years()]) for disease in (T2D, HAEMOPHILIA_A)}


# ---- the hand list ----

def test_the_file_holds_the_six_entries_exactly():
    entries = json.loads(WIDER_FILE.read_text(encoding="utf-8"))
    assert len(entries) == 6
    for entry in entries:
        assert set(entry) == {"medicine_id", "disease_id", "group", "date", "label"}
        assert entry["date"] == "2026-11-26"
        assert entry["label"].startswith("https://")
    assert {(e["medicine_id"], e["disease_id"]): (e["group"], e["label"]) for e in entries} == SIX


def test_the_engine_reads_the_six_entries():
    assert {(e.medicine_id, e.disease_id): (e.group, e.label)
            for e in engine.wider_labels_by_hand()} == SIX


def test_givosiran_on_aip_is_on_approvals_json_with_the_givlaari_label():
    entries = json.loads(APPROVALS_FILE.read_text(encoding="utf-8"))
    rows = [e for e in entries if (e["medicine_id"], e["disease_id"]) == (GIVOSIRAN, AIP)]
    assert rows == APPROVAL_ROWS
    assert entries[-len(APPROVAL_ROWS):] == APPROVAL_ROWS  # at the end of the file


GOOD = {"medicine_id": "CHEMBL1", "disease_id": "MONDO_1", "group": "a group",
        "date": "2026-11-26", "label": "https://example.org/label"}


@pytest.mark.parametrize("bad", [
    {k: v for k, v in GOOD.items() if k != "group"},
    {**GOOD, "note": "anything"},
    {**GOOD, "group": ""},
    {**GOOD, "group": "   "},
    {**GOOD, "group": 3},
    {**GOOD, "label": "http://example.org/label"},
    {**GOOD, "date": "26 Nov"},
    "CHEMBL1",
])
def test_an_entry_not_written_the_right_way_is_refused(bad):
    with patch.object(engine, "_read_wider_labels", return_value=[GOOD, bad]):
        with pytest.raises(ValueError):
            engine.wider_labels_by_hand()


def test_the_same_card_written_twice_is_refused():
    with patch.object(engine, "_read_wider_labels", return_value=[GOOD, dict(GOOD)]):
        with pytest.raises(ValueError):
            engine.wider_labels_by_hand()


def test_a_list_that_is_not_a_list_is_refused():
    with patch.object(engine, "_read_wider_labels", return_value={"a": GOOD}):
        with pytest.raises(ValueError):
            engine.wider_labels_by_hand()


# ---- the app refuses to start on a clash with corrections.json ----

def test_the_app_refuses_to_start_if_a_pair_is_in_both_lists():
    clash = {"medicine_id": "CHEMBL672", "disease_id": T2D, "group": "diabetes mellitus",
             "date": "2026-11-26", "label": "https://example.org/label"}
    assert ("CHEMBL672", T2D) in engine.corrections()  # metformin's red row on type 2 diabetes
    with patch.object(engine, "_read_wider_labels", return_value=[clash]):
        with pytest.raises(ValueError, match="corrections.json"):
            with TestClient(api.app):
                pass


def test_the_app_starts_with_the_real_lists():
    with TestClient(api.app) as client:
        assert client.get("/api/version").status_code == 200


def test_no_real_entry_is_on_corrections_json():
    assert not {pair for pair in SIX} & engine.corrections()


# ---- /api/clues, salt list off ----

def test_example_insulin_glargine_on_type_2_diabetes(pages):
    page = pages[T2D]
    card = next(c for c in page["approved"] if c["id"] == INSULIN_GLARGINE)
    assert card["wider_label_note"] == "The label names diabetes mellitus, which includes this disease."
    # On the main list: in neither folded box of the Approved tab.
    assert INSULIN_GLARGINE not in page.get("wrong_approvals_box", [])
    assert INSULIN_GLARGINE not in page.get("no_regulator_box", [])
    assert list(card)[-1] == "wider_label_note"  # after its existing lines


@pytest.mark.parametrize("pair", [p for p in SIX if p[1] != AIP])
def test_each_card_carries_the_exact_line(pages, pair):
    medicine_id, disease_id = pair
    found = [(name, c) for name, c in cards(pages[disease_id]) if c["id"] == medicine_id]
    with_note = [(name, c) for name, c in found if "wider_label_note" in c]
    assert [name for name, _ in with_note] == ["approved"]
    assert with_note[0][1]["wider_label_note"] == LINE.format(group=SIX[pair][0])


@pytest.mark.parametrize("disease_id", [T2D, HAEMOPHILIA_A])
def test_no_other_card_on_the_page_changes(pages, disease_id):
    after, before = pages[disease_id], saved.before(disease_id)
    assert set(after) == set(before)
    for key in before:
        if key in LISTS:
            assert [without_note(c) for c in after[key]] == before[key], key
        else:
            assert after[key] == before[key], key


@pytest.mark.parametrize("disease_id", [T2D, HAEMOPHILIA_A])
def test_a_card_not_in_the_list_has_no_such_key(pages, disease_id):
    named = {m for m, d in SIX if d == disease_id}
    for name, card in cards(pages[disease_id]):
        if not (name == "approved" and card["id"] in named):
            assert "wider_label_note" not in card, (name, card["id"])


# ---- givosiran on acute intermittent porphyria, salt list on ----

@pytest.mark.salt_parents
def test_givosiran_on_aip_is_one_card_on_the_main_list_with_the_line():
    page = saved.page_answer(AIP, [no_years()])
    givosiran = [(name, c) for name, c in cards(page) if "givosiran" in c["medicine"].lower()]
    assert len(givosiran) == 1  # one card, not two: givosiran sodium is a form of it
    name, card = givosiran[0]
    assert name == "approved" and card["id"] == GIVOSIRAN
    assert GIVOSIRAN not in page.get("no_regulator_box", [])
    assert GIVOSIRAN not in page.get("wrong_approvals_box", [])
    assert GIVOSIRAN_SODIUM not in {c["id"] for _, c in cards(page)}
    assert card["source"] == GIVLAARI
    assert card["wider_label_note"] == ("The label names acute hepatic porphyria, "
                                        "which includes this disease.")
    assert "warning" not in card


@pytest.mark.salt_parents
def test_aip_every_other_card_is_as_before():
    after, before = saved.page_answer(AIP, [no_years()]), saved.before(AIP, salt=True)
    assert [c["id"] for c in before["being_studied"]] == [GIVOSIRAN]
    assert after["being_studied"] == []  # it moved to Approved, nowhere else
    assert [c for c in after["approved"] if c["id"] != GIVOSIRAN] == before["approved"]
    for key in before:
        if key not in ("approved", "being_studied"):
            assert after[key] == before[key], key
    assert set(after) == set(before)
    others = [c for _, c in cards(after) if c["id"] != GIVOSIRAN]
    assert not any("wider_label_note" in c for c in others)


# ---- the page, in a real browser (390 px) ----

BROWSER_SCRIPT = r"""
"use strict";
const fs = require("fs");
const { chromium } = require("playwright");
const PAGE = fs.readFileSync(process.argv[1], "utf-8");
const CASES = JSON.parse(fs.readFileSync(process.argv[2], "utf-8"));
const SHOTS = process.argv[3] || "";
const SITE = "http://moonlight.test";

function read() {
  const visible = el => !!el && el.getClientRects().length > 0;
  // Only the cards drawn on the open tab (a card on a closed tab has no box to measure).
  const all = [...document.querySelectorAll("#found .card")].filter(visible);
  return all.map(card => {
    const name = card.querySelector('[data-slot="medicine-name"]').textContent;
    const proteins = [...card.querySelectorAll('[data-part="proteins"] .protein-row')];
    const points = [...card.querySelectorAll('[data-slot="points-line"]')];
    const list = card.querySelector('[data-part="proteins"]');
    // Every grey or red line above the path, in the order shown.
    const lines = [...card.querySelectorAll(
      '[data-slot="label"],[data-slot="proof-note"],[data-slot="limit-note"],' +
      '[data-slot="withdrawal-note"],[data-slot="wider-label-note"],[data-slot="warning"]')]
      .filter(visible).map(el => [el.dataset.slot, el.textContent.trim()]);
    const wider = card.querySelector('[data-slot="wider-label-note"]');
    return {
      name,
      where: card.closest("details") ? "box" : (card.parentElement && card.parentElement.id),
      scores: proteins.filter(row => visible(row.querySelector('[data-slot="score"]'))).length,
      points: points.map(el => ({ text: el.textContent, shown: visible(el),
        afterList: !!(list && (list.compareDocumentPosition(el) & Node.DOCUMENT_POSITION_FOLLOWING)
          && !list.contains(el)) })),
      lines,
      widerGrey: wider && visible(wider) ? wider.className : null,
    };
  });
}

async function oneCase(browser, name, spec) {
  const context = await browser.newContext({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2 });
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
  await page.goto(SITE + "/?disease=" + spec.disease);
  await page.waitForSelector("#found", { state: "visible" });
  await page.waitForTimeout(300);
  const out = { errors, cards: [] };
  // Open every tab and folded box so every card is drawn and can be read.
  for (const tab of await page.$$('[role="tab"]')) {
    await tab.click();
    await page.evaluate(() => document.querySelectorAll("#found details").forEach(d => d.open = true));
    out.cards.push(...await page.evaluate(read));
  }
  out.sideways = await page.evaluate(() =>
    document.documentElement.scrollWidth > document.documentElement.clientWidth);
  if (SHOTS) {
    for (const [file, medicine, tabId] of spec.shots || []) {
      await page.click("#" + tabId);
      const card = page.locator("#found .card", { has: page.locator('[data-slot="medicine-name"]', { hasText: medicine }) }).first();
      await card.scrollIntoViewIfNeeded();
      await card.screenshot({ path: SHOTS + "/" + file });
    }
  }
  await context.close();
  return out;
}

(async () => {
  const browser = await chromium.launch();
  const out = {};
  for (const name of Object.keys(CASES)) out[name] = await oneCase(browser, name, CASES[name]);
  await browser.close();
  console.log(JSON.stringify(out));
})().catch(problem => { console.error(problem); process.exit(1); });
"""


@pytest.fixture(scope="module")
def seen(pages, tmp_path_factory):
    node = shutil.which("node")
    if not node or subprocess.run(
            [node, "-e", "require('playwright')"], capture_output=True).returncode:
        pytest.skip("needs node with playwright to open a real browser")
    cases = {
        "t2d": {"disease": T2D, "answer": pages[T2D]},
        "haemophilia": {"disease": HAEMOPHILIA_A, "answer": pages[HAEMOPHILIA_A]},
    }
    path = tmp_path_factory.mktemp("wider_labels") / "cases.json"
    path.write_text(json.dumps(cases), encoding="utf-8")
    run = subprocess.run([node, "-e", BROWSER_SCRIPT, str(PAGE_FILE), str(path)],
                         capture_output=True, text=True, timeout=300, cwd=str(ROOT))
    assert run.returncode == 0, run.stderr[-3000:]
    out = json.loads(run.stdout)
    for name in cases:
        assert out[name]["errors"] == [], name
    return out


def drawn(seen, name):
    """Each drawn card once (a card is read once per tab it is drawn on)."""
    return seen[name]["cards"]


def test_browser_the_example_card_shows_the_line_last_and_grey(seen):
    glargine = [c for c in drawn(seen, "t2d") if c["name"] == "Insulin Glargine"
                and c["where"] == "approved-cards"]
    assert glargine
    for card in glargine:
        assert card["lines"][-1] == ["wider-label-note",
                                     "The label names diabetes mellitus, which includes this disease."]
        assert "proof-note" in card["widerGrey"]  # the same grey as the other quiet lines


def test_browser_only_the_named_cards_show_the_line(seen):
    for name, named in (("t2d", {"Insulin Degludec", "Insulin Glargine", "Insulin Human",
                                 "Insulin Icodec"}),
                        ("haemophilia", {"Tranexamic Acid"})):
        shown = {c["name"] for c in drawn(seen, name)
                 if any(slot == "wider-label-note" for slot, _ in c["lines"])}
        assert shown == named, name


def test_browser_the_points_line_once_on_every_card_with_points(seen):
    checked = 0
    for name in ("t2d", "haemophilia"):
        for card in drawn(seen, name):
            if card["scores"]:
                assert len(card["points"]) == 1, card["name"]
                line = card["points"][0]
                assert line["text"] == POINTS_LINE and line["shown"] and line["afterList"], card["name"]
                checked += 1
            else:
                assert card["points"] == [], card["name"]
    assert checked > 50


def test_browser_a_card_without_points_has_no_points_line(seen):
    without = [c for name in ("t2d", "haemophilia") for c in drawn(seen, name) if not c["scores"]]
    assert without  # trial-box cards and Approved cards on none of the top proteins
    assert all(c["points"] == [] for c in without)


def test_browser_nothing_runs_sideways_at_phone_width(seen):
    assert not seen["t2d"]["sideways"] and not seen["haemophilia"]["sideways"]


@pytest.mark.salt_parents
def test_browser_givosiran_on_aip_shows_the_line_and_one_card(tmp_path):
    node = shutil.which("node")
    if not node or subprocess.run(
            [node, "-e", "require('playwright')"], capture_output=True).returncode:
        pytest.skip("needs node with playwright to open a real browser")
    answer = saved.page_answer(AIP, [no_years()])
    path = tmp_path / "cases.json"
    path.write_text(json.dumps({"aip": {"disease": AIP, "answer": answer}}), encoding="utf-8")
    run = subprocess.run([node, "-e", BROWSER_SCRIPT, str(PAGE_FILE), str(path)],
                         capture_output=True, text=True, timeout=300, cwd=str(ROOT))
    assert run.returncode == 0, run.stderr[-3000:]
    out = json.loads(run.stdout)["aip"]
    assert out["errors"] == []
    givosiran = {(c["name"], c["where"]) for c in out["cards"] if "givosiran" in c["name"].lower()}
    assert givosiran == {("Givosiran", "approved-cards")}
    card = next(c for c in out["cards"] if c["name"] == "Givosiran")
    assert card["lines"][-1] == ["wider-label-note", "The label names acute hepatic porphyria, "
                                                     "which includes this disease."]
