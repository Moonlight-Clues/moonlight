"""Ticket 2.42. A folded box for approvals with no regulator record.

Kashish's decisions, 24 Nov 2026, 8:25 pm IST (spoken, to be signed):

1. Cards carrying NO_REGULATOR_LINE move off the main Approved list into
   their own folded box at the bottom of the Approved tab. They are not
   counted in the tab's number. The box title (option A):
   "The database lists these as approved, but gives no regulator record
   for them."
2. Cards carrying JAPAN_LINE go in the same box.

The rule, on the searched disease's MAIN Approved list only:
- the red box wins: a card with a red warning is in the red box only;
- a hand-added card (ADDED_LINE) never goes in;
- the card itself does not change, it only moves;
- the narrower and wider-group boxes are not touched;
- the tab's number counts the main list only.

The addition of 24 Nov, asked for when the rule would have emptied
Friedreich ataxia's main list: moonlight/confirmed.json, a hand-written
list (medicine_id, disease_id, date, label). A main-list card on it stays
on the main list, never goes in the box, loses its grey line, and shows
the label as its source. Each label is saved in fixtures/labels_confirmed/
and names the disease as an indication. The three entries: omaveloxolone
for Friedreich ataxia, ursodiol for primary biliary cholangitis,
dextroamphetamine for narcolepsy.

How it is built, as ticket 2.27 (pull request 64): engine.no_regulator_box
names the cards, /api/clues sends their ids as "no_regulator_box" (only
when there is one), and the page moves the named cards into a folded box
directly above the red box. "approved" is unchanged.

Saved files only. No network.
"""

import copy
import json
import pathlib
import shutil
import subprocess
from unittest.mock import patch

import pytest

from moonlight import api, engine, fetch
from moonlight.engine import ApprovedMedicine, sort_into_tabs

import test_approvals_batch as batch_files
import test_approvals_by_hand as graves_files
import test_approvals_fourth_batch as pbc_files
import test_approvals_third_batch as huntington_files
import test_narrower_box as pah_files
import test_no_regulator_line as friedreich_files
import test_withdrawal_line as hem_a_files

ROOT = pathlib.Path(__file__).resolve().parent.parent
PAGE_FILE = ROOT / "web" / "index.html"
PAGE = PAGE_FILE.read_text(encoding="utf-8")
DECISIONS = (ROOT / "DECISIONS.md").read_text(encoding="utf-8")
LABELS = ROOT / "fixtures" / "labels_confirmed"

KEY = "no_regulator_box"
RED_KEY = "wrong_approvals_box"
# Kashish's choice, option A, word for word.
TITLE = "The database lists these as approved, but gives no regulator record for them."
# The two grey lines, word for word. This ticket changes neither.
NO_REGULATOR_LINE = "The database lists this as approved, but gives no regulator record for it."
JAPAN_LINE = ("Approved in Japan, according to the database. Moonlight could not find the "
              "exact record for this disease.")
ADDED_LINE = "This approval is missing from the database. We added it from the official label."
RED_TITLE = "The database lists these as approved for this disease. They look like mistakes."
SAFETY_LINE = ("For learning and research exploration, not medical advice. Never start, stop or "
               "change any medicine without a doctor.")

GRAVES = "MONDO_0005364"
PBC = "MONDO_0005388"
PAH = "MONDO_0015924"
NARCOLEPSY = "MONDO_0021107"
HUNTINGTON = "MONDO_0007739"
HYPERTHYROIDISM = "MONDO_0004425"
FRIEDREICH = friedreich_files.FRIEDREICH

IPODATE = ("CHEMBL1201243", "Ipodate")
TEPROTUMUMAB = ("CHEMBL1743079", "Teprotumumab")
METHIMAZOLE = ("CHEMBL1515", "Methimazole")
PROPYLTHIOURACIL = ("CHEMBL1518", "Propylthiouracil")
BERAPROST = ("CHEMBL1207745", "Beraprost")
TAURURSODIOL = ("CHEMBL272427", "Taurursodiol")
URSODIOL = ("CHEMBL1551", "Ursodiol")
DEXTROAMPHETAMINE = ("CHEMBL612", "Dextroamphetamine")
OMAVELOXOLONE = ("CHEMBL4303525", "OMAVELOXOLONE")
IDEBENONE = ("CHEMBL252556", "IDEBENONE")
POTASSIUM_IODIDE = "Potassium Iodide"  # in hyperthyroidism's narrower box, with the grey line

LABEL_LINK = "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid="
SKYCLARYS = LABEL_LINK + "2709e870-df3d-f30f-e063-6394a90aeda1"
URSO = LABEL_LINK + "e8fc4fc2-fe5c-4cba-b6e0-5ceaf2157a61"
DEXTROAMPHETAMINE_LABEL = LABEL_LINK + "ec2d13f3-d14f-47e4-abe9-7763f95a8e94"
# The three entries, with the saved label file and the sentence that names
# the disease as an indication.
CONFIRMED = [
    (OMAVELOXOLONE[0], FRIEDREICH.id, SKYCLARYS, "skyclarys-omaveloxolone.txt",
     "SKYCLARYS is indicated for the treatment of Friedreich's ataxia in adults and "
     "adolescents aged 16 years and older."),
    (URSODIOL[0], PBC, URSO, "urso-ursodiol.txt",
     "URSO 250 and URSO Forte (ursodiol) tablets are indicated for the treatment of "
     "patients with primary biliary cholangitis (PBC)."),
    (DEXTROAMPHETAMINE[0], NARCOLEPSY, DEXTROAMPHETAMINE_LABEL,
     "dextroamphetamine-sulfate-tablets.txt", "Narcolepsy."),
]


def page_answer(disease_id, post_json):
    """What /api/clues sends, from saved answers and the real hand-written files."""
    return hem_a_files.page_answer(disease_id, post_json)


@pytest.fixture(scope="module")
def graves():
    return page_answer(GRAVES, graves_files.saved_post_json)


@pytest.fixture(scope="module")
def pbc():
    return page_answer(PBC, pbc_files.saved_post_json)


@pytest.fixture(scope="module")
def pah():
    return page_answer(PAH, pah_files.saved_post_json)


@pytest.fixture(scope="module")
def narcolepsy():
    return page_answer(NARCOLEPSY, batch_files.saved_post_json)


@pytest.fixture(scope="module")
def huntington():
    return page_answer(HUNTINGTON, huntington_files.saved_post_json)


@pytest.fixture(scope="module")
def hyperthyroidism():
    return page_answer(HYPERTHYROIDISM, batch_files.saved_post_json)


def pairs(cards):
    return [(card["id"], card["medicine"]) for card in cards]


def main_list(answer):
    """The main Approved list: "approved" without either box's cards."""
    boxed = set(answer.get(KEY, [])) | set(answer.get(RED_KEY, []))
    return [card for card in answer["approved"] if card["id"] not in boxed]


def box(answer):
    by_id = {card["id"]: card for card in answer["approved"]}
    return [by_id[card_id] for card_id in answer.get(KEY, [])]


def tab_number(answer):
    """The number on the Approved tab: the main list and the two older boxes."""
    return (len(main_list(answer)) + len(answer.get("narrower", []))
            + len(answer.get("wider_group", [])))


def friedreich_main_list():
    """Friedreich ataxia's main Approved list, from its saved list (ticket 2.17)."""
    with patch("moonlight.fetch._post_json", side_effect=friedreich_files.saved_post_json):
        listed = fetch.fetch_approved(FRIEDREICH)
        tabs = sort_into_tabs({}, listed, fetch.fetch_withdrawn(FRIEDREICH))
    return engine.confirm_by_label(tabs.approved, FRIEDREICH.id)


# ---- hand-built cards ----

def card(medicine_id, name, *, regulator=None, sources=(), added=None, label=None):
    return ApprovedMedicine(id=medicine_id, name=name, forms=(name,), clue=None,
                            listed_sources=(), approval_sources=tuple(sources),
                            regulator_record=regulator, added_from_label=added, label=label)


NO_RECORD = card("CHEMBL9001", "ALPHAMIL", regulator=False)
JAPAN_ONLY = card("CHEMBL9002", "BRAVOMIL", regulator=True, sources=(engine.JAPAN_LIST,))
WITH_RECORD = card("CHEMBL9003", "CHARLIEMIL", regulator=True,
                   sources=("https://www.accessdata.fda.gov/charliemil.pdf",))
NOT_SAID = card("CHEMBL9004", "DELTAMIL", regulator=None)
BY_HAND = card("CHEMBL9005", "ECHOMIL", regulator=False,
               added="https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=echo")
TEST_DISEASE = "TEST_0000001"


def boxed(approved, wrong=(), confirmed=(), disease_id=TEST_DISEASE):
    with patch.object(engine, "_read_corrections", return_value=list(wrong)), \
            patch.object(engine, "_read_confirmed", return_value=list(confirmed)):
        approved = engine.confirm_by_label(approved, disease_id)
        return [medicine.name for medicine in engine.no_regulator_box(approved, disease_id)]


def red(medicine_id, disease_id=TEST_DISEASE):
    return {"medicine_id": medicine_id, "disease_id": disease_id, "date": "2026-11-24",
            "note": "A doctor confirmed this looks wrong."}


def confirmed_entry(medicine_id, disease_id=TEST_DISEASE, label=SKYCLARYS):
    return {"medicine_id": medicine_id, "disease_id": disease_id, "date": "2026-11-24",
            "label": label}


# ---- the engine ----

def test_the_box_title_is_kashishs_option_a():
    assert engine.NO_REGULATOR_BOX_LABEL == TITLE


def test_the_two_grey_lines_and_the_red_box_title_are_not_changed():
    assert engine.NO_REGULATOR_LINE == NO_REGULATOR_LINE
    assert engine.JAPAN_LINE == JAPAN_LINE
    assert engine.WRONG_APPROVALS_BOX_LABEL == RED_TITLE


def test_engine_a_no_regulator_card_and_a_japan_card_go_in_and_others_do_not():
    approved = [NO_RECORD, JAPAN_ONLY, WITH_RECORD, NOT_SAID, BY_HAND]
    assert boxed(approved) == ["ALPHAMIL", "BRAVOMIL"]


def test_engine_the_box_keeps_the_order_handed_in():
    assert boxed([JAPAN_ONLY, WITH_RECORD, NO_RECORD]) == ["BRAVOMIL", "ALPHAMIL"]


def test_engine_a_hand_added_card_never_goes_in():
    assert BY_HAND.proof_note == ADDED_LINE
    assert boxed([BY_HAND]) == []


def test_engine_the_red_box_wins_for_either_line():
    wrong = [red(NO_RECORD.id), red(JAPAN_ONLY.id)]
    assert boxed([NO_RECORD, JAPAN_ONLY, WITH_RECORD], wrong=wrong) == []
    with patch.object(engine, "_read_corrections", return_value=wrong):
        assert [m.name for m in engine.wrong_approvals_box(
            [NO_RECORD, JAPAN_ONLY, WITH_RECORD], TEST_DISEASE)] == ["ALPHAMIL", "BRAVOMIL"]


def test_engine_a_red_warning_for_another_disease_does_not_keep_a_card_out():
    assert boxed([NO_RECORD], wrong=[red(NO_RECORD.id, "TEST_0000002")]) == ["ALPHAMIL"]


def test_engine_the_card_is_not_changed_and_nothing_is_taken_off_the_list():
    approved = [NO_RECORD, WITH_RECORD]
    before = copy.deepcopy(approved)
    with patch.object(engine, "_read_corrections", return_value=[]):
        (inside,) = engine.no_regulator_box(approved, TEST_DISEASE)
    assert inside is NO_RECORD and inside.proof_note == NO_REGULATOR_LINE
    assert approved == before


# ---- confirmed.json ----

def test_engine_a_confirmed_card_stays_out_of_the_box_with_no_line_and_the_label_as_source():
    entry = confirmed_entry(NO_RECORD.id)
    assert boxed([NO_RECORD, JAPAN_ONLY], confirmed=[entry]) == ["BRAVOMIL"]
    with patch.object(engine, "_read_confirmed", return_value=[entry]):
        (confirmed, japan) = engine.confirm_by_label([NO_RECORD, JAPAN_ONLY], TEST_DISEASE)
    assert confirmed.proof_note is None
    assert confirmed.source_record == SKYCLARYS
    assert (confirmed.id, confirmed.name) == (NO_RECORD.id, NO_RECORD.name)
    assert japan is JAPAN_ONLY  # a card not on the list is handed back as it was


def test_engine_a_confirmed_japan_card_stays_out_too():
    entry = confirmed_entry(JAPAN_ONLY.id)
    assert boxed([JAPAN_ONLY], confirmed=[entry]) == []


def test_engine_a_confirmed_entry_works_only_for_its_own_disease():
    entry = confirmed_entry(NO_RECORD.id, disease_id="TEST_0000002")
    assert boxed([NO_RECORD], confirmed=[entry]) == ["ALPHAMIL"]


def test_engine_a_confirmed_entry_does_not_change_a_hand_added_card():
    entry = confirmed_entry(BY_HAND.id)
    with patch.object(engine, "_read_confirmed", return_value=[entry]):
        (same,) = engine.confirm_by_label([BY_HAND], TEST_DISEASE)
    assert same is BY_HAND and same.proof_note == ADDED_LINE


@pytest.mark.parametrize("change", [
    {"date": "24 Nov"},  # not a real date
    {"label": "http://dailymed.nlm.nih.gov/x"},  # not https
    {"label": ""},
    {"medicine_id": ""},
    {"note": "a reason"},  # nothing more than the four keys
    {"name": "Omaveloxolone"},
])
def test_an_entry_not_written_properly_is_refused(change):
    entry = dict(confirmed_entry(NO_RECORD.id), **change)
    with patch.object(engine, "_read_confirmed", return_value=[entry]):
        with pytest.raises(ValueError):
            engine.confirmed_by_label()


@pytest.mark.parametrize("missing", ["medicine_id", "disease_id", "date", "label"])
def test_an_entry_with_a_piece_missing_is_refused(missing):
    entry = confirmed_entry(NO_RECORD.id)
    del entry[missing]
    with patch.object(engine, "_read_confirmed", return_value=[entry]):
        with pytest.raises(ValueError):
            engine.confirmed_by_label()


def test_a_file_that_is_not_a_list_is_refused():
    with patch.object(engine, "_read_confirmed", return_value={"entries": []}):
        with pytest.raises(ValueError):
            engine.confirmed_by_label()


def test_the_same_pair_written_twice_with_two_labels_is_refused():
    twice = [confirmed_entry(NO_RECORD.id), confirmed_entry(NO_RECORD.id, label=URSO)]
    with patch.object(engine, "_read_confirmed", return_value=twice):
        with pytest.raises(ValueError):
            engine.confirmed_by_label()


def test_the_file_holds_the_three_entries():
    entries = json.loads((ROOT / "moonlight" / "confirmed.json").read_text(encoding="utf-8"))
    assert [(e["medicine_id"], e["disease_id"], e["label"]) for e in entries] == [
        (medicine_id, disease_id, label) for medicine_id, disease_id, label, _, _ in CONFIRMED]
    assert all(e["date"] == "2026-11-24" for e in entries)
    assert engine.confirmed_by_label() == {
        (medicine_id, disease_id): label for medicine_id, disease_id, label, _, _ in CONFIRMED}


@pytest.mark.parametrize("medicine_id, disease_id, label, saved, sentence", CONFIRMED)
def test_each_entry_is_backed_by_a_saved_label_naming_the_disease(
        medicine_id, disease_id, label, saved, sentence):
    lines = (LABELS / saved).read_text(encoding="utf-8").split("\n")
    assert lines[0] == label
    assert lines[1] == "2026-11-24"
    assert "INDICATIONS AND USAGE" in lines[3]
    assert sentence in lines[4:]
    readme = (LABELS / "README.md").read_text(encoding="utf-8")
    assert f"({medicine_id})" in readme and f"({disease_id})" in readme and label in readme


# ---- her saved diseases, through the API ----

def test_graves_ipodate_and_teprotumumab_are_in_the_box_and_not_on_the_main_list(graves):
    assert pairs(box(graves)) == [IPODATE, TEPROTUMUMAB]
    assert graves[KEY] == [IPODATE[0], TEPROTUMUMAB[0]]
    assert all(card["proof_note"] == NO_REGULATOR_LINE for card in box(graves))
    assert not set(graves[KEY]) & {card["id"] for card in main_list(graves)}


def test_graves_the_two_hand_added_cards_stay_on_the_main_list(graves):
    assert pairs(main_list(graves)) == [METHIMAZOLE, PROPYLTHIOURACIL]
    assert [card["proof_note"] for card in main_list(graves)] == [ADDED_LINE, ADDED_LINE]


def test_graves_the_tab_number_drops_by_exactly_the_two_that_moved(graves):
    assert len(graves["approved"]) == 4  # "approved" itself is unchanged
    assert tab_number(graves) == 2
    assert tab_number(graves) == len(graves["approved"]) - len(graves[KEY])


def test_graves_a_moved_card_keeps_every_line_and_its_source(graves):
    ipodate = box(graves)[0]
    assert ipodate["proof_note"] == NO_REGULATOR_LINE
    assert ipodate["source"]  # its source link, as before
    assert "warning" not in ipodate


def test_pah_beraprost_with_the_japan_line_is_in_the_box(pah):
    assert pairs(box(pah)) == [BERAPROST]
    assert box(pah)[0]["proof_note"] == JAPAN_LINE
    assert len(main_list(pah)) == 12
    assert tab_number(pah) == len(pah["approved"]) - 1 + len(pah.get("wider_group", []))


def test_pah_a_card_with_a_regulator_approval_stays_on_the_main_list(pah):
    names = [name for _, name in pairs(main_list(pah))]
    assert "Ambrisentan" in names and "Bosentan" in names
    assert all("proof_note" not in card for card in main_list(pah))


def test_huntington_the_red_box_wins_over_the_japan_line(huntington):
    reds = [card for card in huntington["approved"] if card["id"] in huntington[RED_KEY]]
    assert len(reds) == 4 and all(card["proof_note"] == JAPAN_LINE for card in reds)
    assert KEY not in huntington  # none of them is in both boxes


def test_hyperthyroidism_a_grey_line_card_in_the_narrower_box_stays_there(hyperthyroidism):
    narrower = {card["medicine"]: card for card in hyperthyroidism["narrower"]}
    assert narrower[POTASSIUM_IODIDE]["proof_note"] == NO_REGULATOR_LINE
    assert narrower[POTASSIUM_IODIDE]["id"] not in hyperthyroidism[KEY]
    assert set(hyperthyroidism[KEY]) <= {card["id"] for card in hyperthyroidism["approved"]}


def test_pbc_ursodiol_is_confirmed_and_taurursodiol_moves(pbc):
    assert pairs(box(pbc)) == [TAURURSODIOL]
    ursodiol = {card["id"]: card for card in main_list(pbc)}[URSODIOL[0]]
    assert "proof_note" not in ursodiol
    assert ursodiol["source"] == URSO
    assert tab_number(pbc) == 3


def test_narcolepsy_dextroamphetamine_is_confirmed_and_nothing_moves(narcolepsy):
    assert KEY not in narcolepsy
    dextroamphetamine = {card["id"]: card for card in narcolepsy["approved"]}[DEXTROAMPHETAMINE[0]]
    assert "proof_note" not in dextroamphetamine
    assert dextroamphetamine["source"] == DEXTROAMPHETAMINE_LABEL
    assert tab_number(narcolepsy) == len(narcolepsy["approved"]) + len(
        narcolepsy.get("narrower", [])) + len(narcolepsy.get("wider_group", []))


def test_friedreich_omaveloxolone_stays_on_the_main_list_and_idebenone_moves():
    approved = friedreich_main_list()
    by_id = {medicine.id: medicine for medicine in approved}
    assert by_id[OMAVELOXOLONE[0]].proof_note is None
    assert by_id[OMAVELOXOLONE[0]].source_record == SKYCLARYS
    assert by_id[IDEBENONE[0]].proof_note == NO_REGULATOR_LINE
    in_box = engine.no_regulator_box(approved, FRIEDREICH.id)
    assert [medicine.id for medicine in in_box] == [IDEBENONE[0]]
    # The main list is not empty: omaveloxolone is on it.
    assert [m.id for m in approved if m not in in_box] == [OMAVELOXOLONE[0]]


def test_the_key_sits_after_every_old_key(graves):
    keys = list(graves)
    for old in ("approved", "more_in_trials", "new_in_trials", "opposite_way_box", RED_KEY):
        if old in keys:
            assert keys.index(old) < keys.index(KEY)
    if "wrong_way_line" in keys:
        assert keys.index(KEY) < keys.index("wrong_way_line")


# ---- the page's words ----

def test_the_page_title_matches_the_engines_copy():
    assert PAGE.count(engine.NO_REGULATOR_BOX_LABEL) == 1
    start = PAGE.index('<details class="wider-box" id="no-regulator-box" hidden>')
    summary = PAGE[PAGE.index("<summary>", start):PAGE.index("</summary>", start)]
    assert summary == (f'<summary>{engine.NO_REGULATOR_BOX_LABEL} '
                       '(<span id="no-regulator-count"></span>) '
                       '<span data-part="tap">Tap to open</span>')


def test_the_box_is_directly_above_the_red_box():
    panel = PAGE[PAGE.index('id="panel-approved"'):PAGE.index('id="panel-trials"')]
    ours = panel.index('<details class="wider-box" id="no-regulator-box"')
    reds = panel.index('<details class="wider-box" id="wrong-box"')
    assert panel.index('id="wider-box"') < ours < reds
    between = panel[panel.index("</details>", ours):reds]
    assert "<details" not in between and "<div" not in between


def test_the_page_never_opens_the_box_by_itself():
    assert 'byId("no-regulator-box").open = false;' in PAGE
    assert 'byId("no-regulator-box").open = !' not in PAGE


def test_the_safety_line_is_still_there():
    assert SAFETY_LINE in PAGE


def test_the_decision_is_written_down():
    (line,) = [line for line in DECISIONS.split("\n") if "(Ticket 2.42" in line]
    assert line.startswith("- 2026-11-24: ")
    assert "Japan line" in line and "no regulator record" in line


# ---- the page, in a real browser, at phone width ----

BROWSER_SCRIPT = r"""
"use strict";
const fs = require("fs");
const { chromium } = require("playwright");
const PAGE = fs.readFileSync(process.argv[1], "utf-8");
const ANSWERS = JSON.parse(fs.readFileSync(process.argv[2], "utf-8"));
const SITE = "http://moonlight.test";

function readApproved() {
  const words = el => el.innerText.replace(/\s+/g, " ").trim();
  const names = sel => [...document.querySelectorAll(sel)].map(
    card => card.querySelector('[data-slot="medicine-name"]').textContent);
  const box = document.getElementById("no-regulator-box");
  const panel = document.getElementById("panel-approved");
  return {
    tab: words(document.getElementById("tab-approved")),
    list: names("#approved-cards > .card"),
    box: names("#no-regulator-cards > .card"),
    wrong: names("#wrong-cards > .card"),
    shown: box.getClientRects().length > 0,
    open: box.open,
    summary: words(box.querySelector("summary")),
    aboveRed: box.nextElementSibling === document.getElementById("wrong-box"),
    boxCardText: [...document.querySelectorAll("#no-regulator-cards > .card")].map(
      card => card.textContent.replace(/\s+/g, " ").trim()),
    listCardText: [...document.querySelectorAll("#approved-cards > .card")].map(
      card => card.textContent.replace(/\s+/g, " ").trim()),
    sideways: document.documentElement.scrollWidth > document.documentElement.clientWidth,
    emptyShown: document.getElementById("approved-empty").getClientRects().length > 0,
  };
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
    return route.abort();
  });
  await page.goto(SITE + "/?disease=MONDO_TEST");
  await page.waitForSelector("#found", { state: "visible" });
  await page.waitForTimeout(300);
  const out = { errors, opened: await page.evaluate(readApproved) };
  if (await page.locator("#no-regulator-box").isVisible()) {
    await page.click("#no-regulator-box summary");
    await page.waitForTimeout(300);
    out.tapped = await page.evaluate(readApproved);
  }
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
def answers(graves):
    before = copy.deepcopy(graves)
    before.pop(KEY, None)
    both = copy.deepcopy(graves)  # Teprotumumab with a red warning too: the red box wins
    both[RED_KEY] = [TEPROTUMUMAB[0]]
    both[KEY] = [IPODATE[0]]
    only = copy.deepcopy(graves)  # every main card in the box
    only["approved"] = box(graves)
    return {"graves": graves, "before": before, "both": both, "only": only}


@pytest.fixture(scope="module")
def seen(answers, tmp_path_factory):
    node = shutil.which("node")
    if not node or subprocess.run(
            [node, "-e", "require('playwright')"], capture_output=True).returncode:
        pytest.skip("needs node with playwright to open a real browser")
    answers_file = tmp_path_factory.mktemp("no_regulator_box") / "answers.json"
    answers_file.write_text(json.dumps(answers), encoding="utf-8")
    run = subprocess.run([node, "-e", BROWSER_SCRIPT, str(PAGE_FILE), str(answers_file)],
                         capture_output=True, text=True, timeout=240, cwd=str(ROOT))
    assert run.returncode == 0, run.stderr[-3000:]
    out = json.loads(run.stdout)
    for name in answers:
        assert out[name]["errors"] == [], name
    return out


def test_browser_graves_the_tab_says_2_and_before_it_said_4(seen):
    assert seen["graves"]["opened"]["tab"] == "Approved (2)"
    assert seen["before"]["opened"]["tab"] == "Approved (4)"


def test_browser_graves_the_main_list_and_the_folded_box(seen):
    opened = seen["graves"]["opened"]
    assert opened["list"] == ["Methimazole", "Propylthiouracil"]
    assert opened["box"] == ["Ipodate", "Teprotumumab"]
    assert opened["shown"] and not opened["open"]
    assert opened["summary"] == TITLE + " (2) Tap to open"
    assert opened["aboveRed"] is True
    assert not opened["sideways"]


def test_browser_a_tap_opens_the_box_and_each_card_reads_as_before(seen):
    tapped = seen["graves"]["tapped"]
    assert tapped["open"] and tapped["summary"] == TITLE + " (2) Tap to close"
    before = dict(zip(seen["before"]["opened"]["list"], seen["before"]["opened"]["listCardText"]))
    for name, text in zip(tapped["box"], tapped["boxCardText"]):
        assert text == before[name]
        assert NO_REGULATOR_LINE in text


def test_browser_the_red_box_wins_and_the_tab_counts_the_main_list_only(seen):
    opened = seen["both"]["opened"]
    assert opened["wrong"] == ["Teprotumumab"]
    assert opened["box"] == ["Ipodate"]
    assert opened["list"] == ["Methimazole", "Propylthiouracil"]
    assert opened["tab"] == "Approved (2)"


def test_browser_only_the_box_it_stays_folded_and_no_untrue_words(seen):
    opened = seen["only"]["opened"]
    assert opened["list"] == [] and opened["box"] == ["Ipodate", "Teprotumumab"]
    assert opened["tab"] == "Approved (0)"
    assert not opened["open"]
    assert not opened["emptyShown"]
