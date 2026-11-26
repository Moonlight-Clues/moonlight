"""Ticket 3.10. Card words from the 25 Nov sheet.

PART A (Q1, decided by MAIN 4 on 25 Nov). Scan medicines keep their place on
the Approved tab, with a tag: the word DIAGNOSTIC in a solid navy pill on the
card's first line, right after the medicine's name. moonlight/diagnostic.json
is a hand-written list {"medicine_id", "disease_id", "date", "label"}; the
disease is "*" for every page. A card carries the tag wherever it is on the
Approved tab: the main list and every folded box. Nothing moves, nothing is
re-counted, no other word changes.
MAIN 4 also decided: mannitol is tagged on asthma only (it is a treatment on
other pages), ipodate is not tagged, and mannitol's red entry on asthma is
deleted from corrections.json (Q14).

PART B (Q14). A card in the "no regulator record" box whose medicine has a
withdrawals.json entry for this disease shows the same withdrawal line as on
the main list. Relyvrio (sodium phenylbutyrate) on ALS.

PART C (Q15). The count at the top of a card says "records", not "reports".
The Report link and the reports database keep their names.

PART D (Q17). Two gene-line phrases, Kashish's words (answer A).

Saved files only. No network.
"""

import json
import pathlib
import re
import shutil
import subprocess
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from moonlight import api, engine, explain

import test_approval_proof as alzheimer_files

ROOT = pathlib.Path(__file__).resolve().parent.parent
FILE = ROOT / "moonlight" / "diagnostic.json"
CORRECTIONS = ROOT / "moonlight" / "corrections.json"
PAGE_FILE = ROOT / "web" / "index.html"
PAGE = PAGE_FILE.read_text(encoding="utf-8")
SHEET = ROOT / "fixtures" / "sheet_25_nov" / "after"
PAGE_ANSWERS = ROOT / "fixtures" / "labels_read"
ASTHMA_SAVED = ROOT / "fixtures" / "old_withdrawn_flag" / "clues_before_2.40_MONDO_0004979.json"
THE_DAY = "2026-11-25"
TAG = "DIAGNOSTIC"
EVERY_PAGE = "*"

ALZHEIMER, ASTHMA, PROSTATE, TREMOR = "MONDO_0004975", "MONDO_0004979", "MONDO_0008315", "MONDO_0003233"
PARKINSON, HUNTINGTON, ALS, GRAVES = "MONDO_0005180", "MONDO_0007739", "MONDO_0004976", "MONDO_0005364"

# MAIN 4's list, in its order. Each id was checked against a saved Open Targets
# answer in fixtures/ (the name the database gives it is on the right).
ON_EVERY_PAGE = {
    "CHEMBL1945778": "Ioflupane",
    "CHEMBL1908906": "Florbetaben",
    "CHEMBL1908919": "Florbetapir",
    "CHEMBL3546271": "Flortaucipir",
    "CHEMBL579205": "Flutemetamol",
    "CHEMBL978": "Methacholine",
    "CHEMBL920": "Choline",            # its form here is Choline C-11
    "CHEMBL1908917": "Fluciclovine",   # Fluciclovine F18
    "CHEMBL4299851": "Piflufolastat",  # Piflufolastat F18
    "CHEMBL951": "Iophendylate",
    "CHEMBL2108285": "Capromab",
    # the ticket's five, kept as they are
    "CHEMBL4650356": "Fapi GA-68",
    "CHEMBL3578202": "Gozetotide",
    "CHEMBL539": "Acetic Acid",        # its only form on the prostate page is Acetic Acid C-11
    "CHEMBL4297855": "Technetium TC-99M Trofolastat Chloride",
    "CHEMBL4650432": "Zirconium ZR-89-DESFERRIOXAMINE-IAB22M2C",
}
# Left out (MAIN 4, 25 Nov): no regulator page calls any of these four diagnostic
# (iophendylate, Fapi Ga-68, acetic acid, Zr-89 IAB22M2C). Acetic acid also has an
# approved treatment use, as ear drops.
LEFT_OUT = {"CHEMBL951", "CHEMBL4650356", "CHEMBL539", "CHEMBL4650432"}
WRITTEN = [medicine_id for medicine_id in ON_EVERY_PAGE if medicine_id not in LEFT_OUT]
MANNITOL = "CHEMBL689"
IPODATE = "CHEMBL1201243"
ALZHEIMER_TRACERS = ["CHEMBL1908906", "CHEMBL1908919", "CHEMBL3546271", "CHEMBL579205"]
IOFLUPANE, FLORBETAPIR, CHOLINE = "CHEMBL1945778", "CHEMBL1908919", "CHEMBL920"
RELYVRIO = "CHEMBL1469"

# Each saved page, and the Approved-tab cards on it that carry the tag.
SAVED_PAGES = {
    PROSTATE: {"CHEMBL2108285", "CHEMBL920", "CHEMBL1908917", "CHEMBL4299851"},
    TREMOR: {IOFLUPANE},      # in the wider-group box
    PARKINSON: {IOFLUPANE},
    HUNTINGTON: {IOFLUPANE},  # in the wider-group box
    ALS: set(), GRAVES: set(), "MONDO_0004691": set(), "MONDO_0005148": set(),
    "MONDO_0005412": set(), "MONDO_0010602": set(), "MONDO_0015129": set(),
    "MONDO_0018874": set(),
}
APPROVED_PARTS = ("approved", "narrower", "wider_group")
CARD_PARTS = APPROVED_PARTS + ("being_studied", "new_clues", "more_in_trials", "new_in_trials")

HAND_LINE = "The maker or a regulator has withdrawn this medicine from the market."


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def saved(disease_id):
    return load(ASTHMA_SAVED) if disease_id == ASTHMA else load(SHEET / f"{disease_id}.clues.json")


def tagged_on(answer):
    return {card["id"] for part in CARD_PARTS for card in answer.get(part, [])
            if card.get("diagnostic_tag")}


# ---- the file ----

def test_the_file_holds_main_4s_list_and_nothing_else():
    entries = load(FILE)
    assert all(set(entry) == {"medicine_id", "disease_id", "date", "label"} for entry in entries)
    assert all(entry["date"] == THE_DAY for entry in entries)
    assert all(entry["label"].startswith("https://") for entry in entries)
    pairs = [(entry["medicine_id"], entry["disease_id"]) for entry in entries]
    assert pairs == [(medicine_id, EVERY_PAGE) for medicine_id in WRITTEN] + [(MANNITOL, ASTHMA)]


def test_ipodate_is_not_on_the_list():
    assert IPODATE not in {entry["medicine_id"] for entry in load(FILE)}


@pytest.mark.parametrize("medicine_id, name", list(ON_EVERY_PAGE.items()) + [(MANNITOL, "Mannitol")])
def test_each_id_is_in_a_saved_open_targets_answer_under_its_name(medicine_id, name):
    words = name.upper()
    for file in ROOT.joinpath("fixtures").rglob("*.json"):
        text = file.read_text(encoding="utf-8")
        if f'"{medicine_id}"' in text and words in text.upper():
            return
    pytest.fail(f"{medicine_id} {name} is in no saved file")


def test_the_engine_reads_the_list_page_by_page():
    every = set(WRITTEN)
    assert engine.diagnostic_ids(ASTHMA) == every | {MANNITOL}
    for disease_id in (ALZHEIMER, PROSTATE, TREMOR, "MONDO_0005148"):
        assert engine.diagnostic_ids(disease_id) == every


@pytest.mark.parametrize("bad", [
    {"medicine_id": "CHEMBL1", "disease_id": "*", "date": THE_DAY},  # no label
    {"medicine_id": "CHEMBL1", "disease_id": "*", "date": THE_DAY, "label": "http://x.org"},
    {"medicine_id": "CHEMBL1", "disease_id": "*", "date": "25 Nov", "label": "https://x.org"},
    {"medicine_id": "CHEMBL1", "disease_id": "*", "date": THE_DAY, "label": "https://x.org",
     "why": "a scan"},
])
def test_an_entry_not_written_the_right_way_is_refused(bad):
    with patch.object(engine, "_read_diagnostic", return_value=[bad]):
        with pytest.raises(ValueError):
            engine.diagnostic_ids(ALZHEIMER)


def test_the_same_pair_written_twice_is_refused():
    entry = {"medicine_id": "CHEMBL1", "disease_id": "*", "date": THE_DAY, "label": "https://x.org"}
    with patch.object(engine, "_read_diagnostic", return_value=[entry, dict(entry)]):
        with pytest.raises(ValueError):
            engine.diagnostic_ids(ALZHEIMER)


def test_the_tag_word_is_the_signed_word():
    assert engine.DIAGNOSTIC_TAG == TAG


# ---- Q14: mannitol's red entry on asthma is gone ----

def test_mannitols_red_entry_on_asthma_is_deleted():
    assert (MANNITOL, ASTHMA) not in engine.corrections()
    assert MANNITOL not in engine.looks_wrong(ASTHMA)
    # Ticket 2.62 (sheet row 7) adds mannitol on COPD: only asthma is checked here.
    assert not [e for e in load(CORRECTIONS)
                if e["medicine_id"] == MANNITOL and e["disease_id"] == ASTHMA]


# ---- the API: a real page, built offline ----

@pytest.fixture(scope="module")
def alzheimer_found():
    alzheimer_files._searched["id"] = ALZHEIMER
    explain.forget_everything()
    with patch("moonlight.fetch._post_json", side_effect=alzheimer_files.proof_post_json), \
            patch("requests.post", side_effect=AssertionError("network used")), \
            patch("requests.sessions.Session.request", side_effect=AssertionError("network used")):
        yield api._find(ALZHEIMER)
    explain.forget_everything()


def clues_for(found):
    api.forget_answers()
    with patch.object(api, "_find", return_value=found), \
            patch("requests.post", side_effect=AssertionError("network used")), \
            patch("requests.sessions.Session.request", side_effect=AssertionError("network used")):
        response = TestClient(api.app).get("/api/clues", params={"disease_id": found.disease.id})
    api.forget_answers()
    assert response.status_code == 200
    return response.json()


@pytest.fixture(scope="module")
def alzheimer(alzheimer_found):
    return clues_for(alzheimer_found)


def test_alzheimers_four_pet_tracers_and_ioflupane_carry_the_tag(alzheimer):
    assert tagged_on(alzheimer) == set(ALZHEIMER_TRACERS) | {IOFLUPANE}
    for card in alzheimer["approved"]:
        if card["id"] in tagged_on(alzheimer):
            assert card["diagnostic_tag"] == TAG
        else:
            assert "diagnostic_tag" not in card


def test_the_tagged_cards_stay_on_the_approved_tab_in_a_to_z_order(alzheimer):
    names = [card["medicine"] for card in alzheimer["approved"]]
    assert names == sorted(names, key=str.lower)
    assert len(alzheimer["approved"]) == 21  # as test_approval_proof counts it
    for medicine_id in ALZHEIMER_TRACERS + [IOFLUPANE]:
        assert medicine_id not in alzheimer.get("wrong_approvals_box", [])
        assert medicine_id not in alzheimer.get("no_regulator_box", [])


def test_the_tag_changes_nothing_else_on_a_card(alzheimer_found, alzheimer):
    with patch.object(engine, "_read_diagnostic", return_value=[]):
        without = clues_for(alzheimer_found)
    assert tagged_on(without) == set()
    for card in alzheimer["approved"]:
        card = dict(card)
        card.pop("diagnostic_tag", None)
        assert card in without["approved"]
    assert {k: v for k, v in alzheimer.items() if k != "approved"} == \
        {k: v for k, v in without.items() if k != "approved"}


def test_the_tag_shows_in_the_folded_boxes_too(alzheimer_found):
    """A tagged card in the narrower box or the wider-group box carries it too."""
    by_id = {medicine.id: medicine for medicine in alzheimer_found.approved}
    old = (alzheimer_found.narrower, alzheimer_found.wider_group)
    try:
        alzheimer_found.narrower = [by_id[FLORBETAPIR]]
        alzheimer_found.wider_group = [by_id[IOFLUPANE], by_id["CHEMBL502"]]  # donepezil: no tag
        answer = clues_for(alzheimer_found)
    finally:
        alzheimer_found.narrower, alzheimer_found.wider_group = old
    assert [c.get("diagnostic_tag") for c in answer["narrower"]] == [TAG]
    assert [c.get("diagnostic_tag") for c in answer["wider_group"]] == [TAG, None]


def test_mannitol_is_tagged_on_asthma_only():
    medicine = engine.ApprovedMedicine(MANNITOL, "MANNITOL", ("MANNITOL",), None, ())
    assert api._approved_json(medicine, diagnostic=engine.diagnostic_ids(ASTHMA))["diagnostic_tag"] == TAG
    for disease_id in (ALZHEIMER, "MONDO_0009061"):  # cystic fibrosis: a treatment there
        assert "diagnostic_tag" not in api._approved_json(
            medicine, diagnostic=engine.diagnostic_ids(disease_id))


# ---- the saved pages: which cards the list tags ----

@pytest.mark.parametrize("disease_id", list(SAVED_PAGES) + [ASTHMA])
def test_on_each_saved_page_only_the_listed_approved_cards_are_tagged(disease_id):
    page = saved(disease_id)
    tagged = engine.diagnostic_ids(disease_id)
    approved = {card["id"] for part in APPROVED_PARTS for card in page.get(part, [])}
    expected = {MANNITOL, "CHEMBL978"} if disease_id == ASTHMA else SAVED_PAGES[disease_id]
    assert approved & tagged == expected


def test_the_five_of_the_ticket_are_on_no_saved_approved_tab():
    """They are in the prostate page's trials boxes, which left_out.json empties."""
    five = list(ON_EVERY_PAGE)[-5:]
    for disease_id in list(SAVED_PAGES) + [ASTHMA]:
        page = saved(disease_id)
        assert not set(five) & {c["id"] for part in APPROVED_PARTS for c in page.get(part, [])}


def test_no_trials_or_clue_card_carries_the_tag(alzheimer):
    for part in ("being_studied", "new_clues", "more_in_trials", "new_in_trials"):
        assert not [c for c in alzheimer.get(part, []) if "diagnostic_tag" in c]


# ---- PART D: the gene-line phrases ----

NEW_PHRASES = {"affected_pathway": "a body process the gene is part of",
               "literature": "found together in research papers"}
OLD_PHRASES = ["the body process the gene is part of", "mentioned together in research papers"]


def test_the_engine_has_kashishs_two_new_phrases():
    for kind, words in NEW_PHRASES.items():
        assert engine.EVIDENCE_NAMES[kind] == words


def test_the_page_has_kashishs_two_new_phrases():
    for kind, words in NEW_PHRASES.items():
        assert f'{kind}: "{words}",' in PAGE


@pytest.mark.parametrize("old", OLD_PHRASES)
def test_the_old_phrases_are_gone(old):
    assert old not in PAGE
    assert old not in (ROOT / "moonlight" / "engine.py").read_text(encoding="utf-8")


# ---- PART C: records ----

def test_the_count_says_records():
    assert '(clue.reports === 1 ? " record" : " records")' in PAGE
    assert '" report" : " reports"' not in PAGE


def test_the_how_to_card_says_8_records():
    guide = PAGE[PAGE.index('id="guide-card"'):]
    guide = guide[:guide.index("</article>")]
    assert '<span class="reports">8 records <span class="k" aria-label="B">B</span></span>' in guide
    assert "8 reports" not in guide


def test_the_report_link_keeps_its_name():
    assert '>Report</button>' in PAGE
    assert 'const REPORT_THANKS = "Thank you. We read every report.";' in PAGE
    assert "We read every report.<br>Nothing about you is kept." in PAGE


# ---- the tag's look, in the page's own styles ----

def style_rule(selector):
    match = re.search(re.escape(selector) + r"\{([^}]*)\}", PAGE)
    assert match, selector
    return match.group(1)


def test_the_pill_is_navy_and_white_not_red_teal_or_gold():
    rule = style_rule("[data-diagnostic]::after")
    assert "content:attr(data-diagnostic)" in rule
    assert "background:var(--navy)" in rule and "color:#fff" in rule
    assert "font-weight:700" in rule and "border-radius:999px" in rule
    assert "vertical-align:middle" in rule
    for colour in ("--teal", "--gold", "--red", "#C", "#B4"):
        assert colour not in rule


def contrast(one, two):
    def light(hex_colour):
        channels = [int(hex_colour[i:i + 2], 16) / 255 for i in (1, 3, 5)]
        lin = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in channels]
        return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]
    high, low = sorted((light(one), light(two)), reverse=True)
    return (high + 0.05) / (low + 0.05)


def test_white_on_navy_is_at_least_4_5_to_1():
    navy = re.search(r"--navy:(#[0-9A-Fa-f]{6})", PAGE).group(1)
    assert contrast(navy, "#FFFFFF") >= 4.5


def test_the_pill_prints_as_a_black_outlined_pill():
    assert re.search(r"@media print\{\[data-diagnostic\]::after\{[^}]*border:1px solid #000[^}]*\}", PAGE)


# ---- in a real browser, at 390 px ----

BROWSER = r"""
"use strict";
const fs = require("fs");
const { chromium } = require("playwright");
const PAGE = fs.readFileSync(process.argv[1], "utf-8");
const ANSWERS = JSON.parse(fs.readFileSync(process.argv[2], "utf-8"));
const SITE = "http://moonlight.test";
function read() {
  const cards = [...document.querySelectorAll("#panel-approved .card, #panel-trials .card, #panel-clues .card")].map(card => {
    const tag = card.querySelector("[data-diagnostic]");
    const h3 = card.querySelector("h3");
    const box = card.closest("details");
    const out = { name: h3.textContent, box: box ? box.id : null,
                  reports: (card.querySelector('[data-slot="reports"]') || {}).textContent || null,
                  lines: [...card.querySelectorAll('[data-slot="withdrawal-note"]')]
                           .filter(el => !el.hidden).map(el => el.textContent),
                  evidence: [...card.querySelectorAll(".protein-evidence")].map(el => el.textContent),
                  tag: null };
    if (tag) {
      if (box) box.open = true;
      const style = getComputedStyle(tag, "::after");
      out.tag = { text: JSON.parse(style.content), inH3: tag === h3, background: style.backgroundColor,
                  color: style.color, size: parseFloat(style.fontSize), weight: style.fontWeight,
                  inside: card.scrollWidth <= card.clientWidth && h3.scrollWidth <= h3.clientWidth };
    }
    return out;
  });
  return { cards, wide: document.documentElement.scrollWidth };
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
    const seen = await page.evaluate(read);
    seen.headings = await page.getByRole("heading", { level: 3 }).evaluateAll(
      els => els.filter(el => el.closest(".card")).map(el => el.textContent));
    seen.named = {};
    for (const card of seen.cards.filter(c => c.tag))
      seen.named[card.name] = await page.getByRole("heading", { name: card.name + ", diagnostic", exact: true }).count();
    await page.click("#print-page");
    await page.waitForTimeout(200);
    await page.emulateMedia({ media: "print" });
    seen.register = await page.evaluate(() => [...document.querySelectorAll("#register [data-diagnostic]")].map(tag => {
      const style = getComputedStyle(tag, "::after");
      return { text: JSON.parse(style.content), row: tag.textContent,
               border: style.borderTopStyle + " " + style.borderTopColor, color: style.color,
               background: style.backgroundColor };
    }));
    seen.errors = errors;
    out[name] = seen;
    await context.close();
  }
  await browser.close();
  console.log(JSON.stringify(out));
})().catch(problem => { console.error(problem); process.exit(1); });
"""


@pytest.fixture(scope="module")
def seen(alzheimer, tmp_path_factory):
    node = shutil.which("node")
    if not node or subprocess.run([node, "-e", "require('playwright')"], capture_output=True).returncode:
        pytest.skip("needs node with playwright to open a real browser")
    prostate = saved(PROSTATE)
    for part in APPROVED_PARTS:  # the tags as the API now adds them to this saved answer
        for card in prostate.get(part, []):
            if card["id"] in engine.diagnostic_ids(PROSTATE):
                card["diagnostic_tag"] = TAG
    answers = tmp_path_factory.mktemp("pages") / "answers.json"
    answers.write_text(json.dumps({"alzheimer": alzheimer, "prostate": prostate, "als": saved(ALS),
                                   "pah": load(PAGE_ANSWERS / "2.52" / "page_answers" / "MONDO_0015924.clues.json"),
                                   "hem_a": load(PAGE_ANSWERS / "2.50" / "page_answers" / "MONDO_0010602.clues.json")}),
                       encoding="utf-8")
    run = subprocess.run([node, "-e", BROWSER, str(PAGE_FILE), str(answers)],
                         capture_output=True, text=True, timeout=240, cwd=str(ROOT))
    assert run.returncode == 0, run.stderr[-3000:]
    return json.loads(run.stdout)


@pytest.mark.parametrize("name, tagged", [
    ("alzheimer", {"Florbetaben", "Florbetapir", "Flortaucipir", "Flutemetamol", "Ioflupane"}),
    ("prostate", {"Capromab", "Choline", "Fluciclovine", "Piflufolastat"}),
    ("als", set())])
def test_the_pill_is_on_exactly_the_tagged_cards(seen, name, tagged):
    assert seen[name]["errors"] == []
    assert {card["name"] for card in seen[name]["cards"] if card["tag"]} == tagged


@pytest.mark.parametrize("name", ["alzheimer", "prostate"])
def test_the_pill_is_in_the_first_line_navy_white_and_inside_the_card(seen, name):
    for card in [c for c in seen[name]["cards"] if c["tag"]]:
        tag = card["tag"]
        assert tag["text"] == TAG and tag["inH3"]
        assert tag["background"] == "rgb(16, 31, 49)" and tag["color"] == "rgb(255, 255, 255)"
        assert 11 <= tag["size"] <= 12 and tag["weight"] == "700"
        assert tag["inside"], card["name"]
    assert seen[name]["wide"] <= 390


def test_the_piflufolastat_card_in_the_wider_box_has_the_pill(seen):
    (card,) = [c for c in seen["prostate"]["cards"] if c["name"] == "Piflufolastat"]
    assert card["box"] == "wider-box" and card["tag"]


@pytest.mark.parametrize("name", ["alzheimer", "prostate"])
def test_a_screen_reader_reads_the_tag_as_part_of_the_name(seen, name):
    assert seen[name]["named"] and all(count == 1 for count in seen[name]["named"].values())


@pytest.mark.parametrize("name", ["alzheimer", "prostate"])
def test_the_printed_register_shows_a_black_outlined_pill(seen, name):
    tagged = {card["name"] for card in seen[name]["cards"] if card["tag"]}
    printed = seen[name]["register"]
    assert {row["row"] for row in printed} == tagged
    for row in printed:
        assert row["text"] == TAG
        assert row["border"] == "solid rgb(0, 0, 0)" and row["color"] == "rgb(0, 0, 0)"
        assert row["background"] in ("rgb(255, 255, 255)", "rgba(0, 0, 0, 0)")


def test_the_counts_say_records_on_screen(seen):
    counts = [card["reports"] for card in seen["alzheimer"]["cards"] if card["reports"]]
    assert counts and all(re.fullmatch(r"1 record|\d+ records", words) for words in counts)
    assert not any("report" in words for words in counts)


@pytest.mark.parametrize("name, kind", [("pah", "literature"), ("hem_a", "affected_pathway")])
def test_a_clue_cards_gene_line_uses_the_new_phrase(seen, name, kind):
    lines = [line for card in seen[name]["cards"] for line in card["evidence"]]
    assert any(NEW_PHRASES[kind] in line for line in lines)
    assert not any(old in line for line in lines for old in OLD_PHRASES)


# ---- PART B: the withdrawal line inside the "no regulator record" box ----
# The saved ALS answer (fixtures/sheet_25_nov/after/) is from before ticket 2.55. Since 2.55
# (signed Q22) Relyvrio also has a red entry on ALS, and the red box wins, so on main today the
# card sits in the red box. These tests check the page's rule with the saved answer: a card in
# the "no regulator record" box draws the withdrawal line the API sends, as on the main list.

def test_relyvrio_shows_the_withdrawal_line_inside_the_box(seen):
    (card,) = [c for c in seen["als"]["cards"] if c["name"] == "Phenylbutanoic Acid"]
    assert card["box"] == "no-regulator-box"
    assert card["lines"] == [HAND_LINE]


def test_relyvrios_entry_is_for_als_and_the_api_sends_the_line():
    page = saved(ALS)
    assert RELYVRIO in page["no_regulator_box"]
    (card,) = [c for c in page["approved"] if c["id"] == RELYVRIO]
    assert card["withdrawal_note"] == engine.HAND_WITHDRAWAL_LINE
    assert any(e.medicine_id == RELYVRIO and e.disease_id == ALS for e in engine.withdrawals_by_hand())
