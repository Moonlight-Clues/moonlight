"""Ticket T7. Matched medicines, the count line, the sources line.

A medicine the disease-search file matched, and that Open Targets has no
trial for on this disease, goes through today's tab rules. Its card carries
the grey line "Its trials for this disease were found on ClinicalTrials.gov,
not in Open Targets." The In trials tab shows the agreed count sentence
and "Trials come from Open Targets and ClinicalTrials.gov."

A medicine Open Targets already has a trial for is left as it is.
An approved medicine is not added to In trials.
The same medicine is never added twice.
A medicine on the corrections list or left_out.json for this disease is
not added.

Saved files and hand-built records only. No network. The browser part
needs node and playwright, and is skipped when they are missing.
"""

import json
import pathlib
import shutil
import subprocess
from dataclasses import replace
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from moonlight import api, disease_search, fetch
from moonlight.engine import (
    ApprovedMedicine,
    Tabs,
    place_matched,
    trials_count_line,
    CTGOV_TRIAL_LINE,
    TRIALS_SOURCES_LINE,
)
from moonlight.fetch import DrugFact, OnList
from moonlight.filter import GROUPS
from moonlight.rank import Clue
from moonlight.records import Disease, Medicine, MedicineForm, Path, Target

ROOT = pathlib.Path(__file__).resolve().parent.parent
PAGE = (ROOT / "web" / "index.html").read_text(encoding="utf-8")
DISEASE = Disease(id="MONDO_TEST", name="Example disease")
LINE = CTGOV_TRIAL_LINE
SOURCES = TRIALS_SOURCES_LINE


def form(drug_id, name, best="APPROVAL", stage=None, withdrawn=False, parent=None):
    return MedicineForm(id=drug_id, name=name, best_stage=best, disease_stage=stage,
                        parent_id=parent, withdrawn=withdrawn)


def medicine(drug_id, name, best="APPROVAL", stage=None, withdrawn=False, parent=None):
    return Medicine(name=name, forms=(form(drug_id, name, best, stage, withdrawn, parent),))


def one_path(med, symbol="GENE"):
    return Path(
        medicine=med,
        target=Target(id="ENSG" + symbol, symbol=symbol, name=symbol, score=0.5),
        disease=DISEASE,
        action_types=("INHIBITOR",),
        score=0.5,
        sources=("https://example.test/source",),
    )


def empty_tabs(**kwargs):
    made = Tabs(approved=[], being_studied=[], new_clues=[],
                left_out={"not_approved": 0, "unclear_link": 0})
    return replace(made, **kwargs) if kwargs else made


def matched(drug_id, *ncts):
    return SimpleNamespace(medicine_id=drug_id, nct_ids=tuple(ncts))


def ids(cards):
    found = []
    for card in cards:
        if hasattr(card, "id"):
            found.append(card.id)
        else:
            form = card.medicine.forms[0]
            found.append(form.parent_id or form.id)
    return found


def place(tabs, matched_rows, on_list=(), tray=None, facts=None, blocked=()):
    if tray is None:
        tray = {group: [] for group in GROUPS}
    return place_matched(tabs, on_list, tray, matched_rows, facts or {}, blocked)


# ---------------------------------------------------------------- placement


def test_a_new_clue_with_only_a_ctgov_trial_moves_to_in_trials():
    """Approved for something else, no Open Targets link, but ClinicalTrials.gov
    has a trial. It leaves New clues and is one In trials card, with the line."""
    med = medicine("CHEMBL1", "EXAMPLE")
    clue = Clue(paths=(one_path(med),))
    tray = {group: [] for group in GROUPS}
    tray["new_clue"] = [one_path(med)]
    placed = place(empty_tabs(new_clues=[clue]), [matched("CHEMBL1", "NCT00000001")], tray=tray)
    assert ids(placed.new_clues) == []
    assert ids(placed.being_studied) == ["CHEMBL1"]
    assert ids(placed.more_in_trials) == []
    assert ids(placed.new_in_trials) == []
    assert placed.grey == {"CHEMBL1"}
    assert placed.extra_ncts["CHEMBL1"] == {"NCT00000001"}


def test_an_approved_medicine_is_not_added_to_in_trials():
    """Approved for this disease. The grey line goes on that card. No second card."""
    approved = ApprovedMedicine("CHEMBL1", "EXAMPLE", ("EXAMPLE",), None, ())
    placed = place(empty_tabs(approved=[approved]), [matched("CHEMBL1", "NCT00000001", "NCT00000002")])
    assert ids(placed.being_studied) == []
    assert ids(placed.more_in_trials) == []
    assert ids(placed.new_in_trials) == []
    assert placed.grey == {"CHEMBL1"}
    assert "CHEMBL1" not in placed.extra_ncts


def test_a_medicine_open_targets_already_has_a_trial_for_is_left_alone():
    """One card, no grey line, no second copy."""
    med = medicine("CHEMBL1", "EXAMPLE", stage="PHASE_2")
    clue = Clue(paths=(one_path(med),))
    link = "https://clinicaltrials.gov/study/NCT00000009"
    entry = OnList(medicine=med, reports=((link, "PHASE_2"),), all_seen=True, study_links=(link,))
    placed = place(empty_tabs(being_studied=[clue]),
                   [matched("CHEMBL1", "NCT00000009", "NCT00000010")], on_list=[entry])
    assert ids(placed.being_studied) == ["CHEMBL1"]
    assert placed.grey == set()
    assert placed.extra_ncts == {}
    assert placed.held == []


def test_an_approved_medicine_on_no_protein_goes_in_the_more_box_once():
    """Not on the disease list and not on a protein. Approved elsewhere."""
    fact = DrugFact(id="CHEMBL9", name="FARAWAY", best_stage="APPROVAL", withdrawn=False,
                    parent_id=None, parent_name=None)
    placed = place(empty_tabs(), [matched("CHEMBL9", "NCT00000003")],
                   facts={"CHEMBL9": fact})
    assert ids(placed.more_in_trials) == ["CHEMBL9"]
    assert ids(placed.being_studied) == []
    assert ids(placed.new_in_trials) == []
    assert placed.more_in_trials[0].name == "FARAWAY"
    assert placed.grey == {"CHEMBL9"}
    assert placed.extra_ncts["CHEMBL9"] == {"NCT00000003"}


def test_a_medicine_approved_nowhere_goes_in_the_new_box():
    fact = DrugFact(id="CHEMBL8", name="NEWCOMER", best_stage="PHASE_2", withdrawn=False,
                    parent_id=None, parent_name=None)
    placed = place(empty_tabs(), [matched("CHEMBL8", "NCT00000004")], facts={"CHEMBL8": fact})
    assert ids(placed.new_in_trials) == ["CHEMBL8"]
    assert ids(placed.more_in_trials) == []
    assert placed.grey == {"CHEMBL8"}


def test_a_withdrawn_medicine_is_not_shown():
    fact = DrugFact(id="CHEMBL7", name="PULLED", best_stage="APPROVAL", withdrawn=True,
                    parent_id=None, parent_name=None)
    placed = place(empty_tabs(), [matched("CHEMBL7", "NCT00000005")], facts={"CHEMBL7": fact})
    assert ids(placed.being_studied) == []
    assert ids(placed.more_in_trials) == []
    assert ids(placed.new_in_trials) == []
    assert placed.grey == set()


def test_a_salt_and_its_parent_are_one_medicine():
    """Two matched ids, one family. Both trials are kept. One card."""
    fact = DrugFact(id="CHEMBL_SALT", name="EXAMPLE MALEATE", best_stage="APPROVAL",
                    withdrawn=False, parent_id="CHEMBL1", parent_name="EXAMPLE")
    placed = place(empty_tabs(),
                   [matched("CHEMBL_SALT", "NCT00000001"), matched("CHEMBL1", "NCT00000002")],
                   facts={"CHEMBL_SALT": fact})
    assert ids(placed.more_in_trials) == ["CHEMBL1"]
    assert placed.extra_ncts["CHEMBL1"] == {"NCT00000001", "NCT00000002"}


def test_a_medicine_on_the_corrections_list_is_not_added():
    """left_out.json and corrections.json for this disease. Not placed, and named."""
    fact = DrugFact(id="CHEMBL5", name="HELD", best_stage="APPROVAL", withdrawn=False,
                    parent_id=None, parent_name=None)
    placed = place(empty_tabs(), [matched("CHEMBL5", "NCT00000006")],
                   facts={"CHEMBL5": fact}, blocked={"CHEMBL5"})
    assert ids(placed.more_in_trials) == []
    assert placed.grey == set()
    assert placed.held == ["CHEMBL5"]


def test_the_same_medicine_already_in_a_box_is_not_copied():
    """Open Targets recorded a phase, but not a ClinicalTrials.gov trial.
    The card stays the one card and gains the line."""
    med = medicine("CHEMBL4", name := "BOXED", best="APPROVAL", stage="PHASE_3")
    card = api_trial(med)
    placed = place(empty_tabs(more_in_trials=[card]), [matched("CHEMBL4", "NCT00000007")])
    assert ids(placed.more_in_trials) == ["CHEMBL4"]
    assert ids(placed.being_studied) == []
    assert placed.grey == {"CHEMBL4"}


def api_trial(med):
    from moonlight.engine import TrialMedicine
    return TrialMedicine(id=med.forms[0].id, name=med.name, forms=(med.name,),
                         stage=med.disease_stage, sources=())


# ---------------------------------------------------------------- the lines


def test_the_count_line_says_one_when_there_is_one():
    """MAIN 5, 27 Nov. The agreed sentence, not a bare pair of counts."""
    assert trials_count_line(1, 1) == "This medicine is in 1 drug trial on ClinicalTrials.gov."
    assert trials_count_line(1, 2) == "This medicine is in 2 drug trials on ClinicalTrials.gov."
    assert trials_count_line(2, 1) == "These 2 medicines are in 1 drug trial on ClinicalTrials.gov."
    assert trials_count_line(12, 40) == "These 12 medicines are in 40 drug trials on ClinicalTrials.gov."
    assert trials_count_line(50, 67) == "These 50 medicines are in 67 drug trials on ClinicalTrials.gov."
    assert "1 drug trial" in trials_count_line(4, 1)
    assert "1 drug trials" not in trials_count_line(1, 1)


def test_the_sources_line_is_the_ticket_sentence():
    assert SOURCES == "Trials come from Open Targets and ClinicalTrials.gov."
    assert LINE == ("Its trials for this disease were found on "
                    "ClinicalTrials.gov, not in Open Targets.")


# ---------------------------------------------------------------- the file


def _result(disease_id, name, stored, matched_rows, only_rows, total):
    return {
        "disease_id": disease_id, "name": name, "stored": stored,
        "terms_used": [name] if stored else [],
        "name_trial_total": total, "trial_total": total if stored else None,
        "medicine_total": (len(matched_rows) + len(only_rows)) if stored else None,
        "matched_total": len(matched_rows) if stored else None,
        "ctgov_only_total": len(only_rows) if stored else None,
        "before_trials": 0, "before_medicines": 0,
        "matched": matched_rows, "ctgov_only": only_rows, "stops": [],
    }


def test_the_reader_returns_matched_medicines_and_a_skipped_disease(tmp_path):
    path = tmp_path / "disease_search.sqlite"
    disease_search.write_sqlite(path, [
        _result("MONDO_A", "Alpha", True,
                [{"medicine_id": "CHEMBL1", "nct_ids": ["NCT00000002", "NCT00000001"]}],
                [{"name": "Mystery", "nct_ids": ["NCT00000003"]}], 2),
        _result("MONDO_B", "Beta", False, [], [], 7765),
    ], "2026-11-26")
    opened = disease_search.SearchFile.open(path)
    alpha = opened.get("MONDO_A")
    assert alpha.stored is True
    assert [(row.medicine_id, row.nct_ids) for row in alpha.matched] == [
        ("CHEMBL1", ("NCT00000001", "NCT00000002"))]
    beta = opened.get("MONDO_B")
    assert beta.stored is False
    assert beta.name_trial_total == 7765
    assert beta.matched == ()
    assert opened.get("MONDO_NO") is None


def test_breast_cancer_is_skipped_in_the_shipped_file():
    """Over 2,000 trials: stored as skipped, with the search total."""
    opened = disease_search.SearchFile.open(ROOT / "moonlight" / "disease_search.sqlite")
    row = opened.get("MONDO_0007254")
    assert row is not None and row.stored is False
    assert row.name_trial_total == 7765
    assert row.matched == ()


def test_drug_facts_read_the_fields_open_targets_sends(monkeypatch):
    """The query is the one checked against a live answer. No network here."""
    sent = {}

    def fake(body):
        sent["body"] = body
        return {"data": {"id0": {
            "id": "CHEMBL1", "name": "EXAMPLE", "maximumClinicalStage": "APPROVAL",
            "drugWarnings": [], "parentMolecule": None, "childMolecules": [],
        }}}

    monkeypatch.setattr(fetch, "_post_json", fake)
    monkeypatch.setattr(fetch, "data_version", lambda: "26.09")
    facts = fetch.fetch_drug_facts(["CHEMBL1"])
    assert facts["CHEMBL1"].name == "EXAMPLE"
    assert facts["CHEMBL1"].best_stage == "APPROVAL"
    assert facts["CHEMBL1"].withdrawn is False
    assert "maximumClinicalStage" in sent["body"]["query"]
    assert "drugWarnings" in sent["body"]["query"]
    assert sent["body"]["variables"]["id0"] == "CHEMBL1"


# ---------------------------------------------------------------- the API


def _patch_find(monkeypatch, disease, tray, listed, on_list):
    monkeypatch.setattr(api, "fetch_disease", lambda disease_id: disease)
    monkeypatch.setattr(api, "fetch_targets", lambda disease, limit: [])
    monkeypatch.setattr(api, "find_clues", lambda disease, targets: tray)
    monkeypatch.setattr(api, "fetch_approved", lambda disease: listed)
    monkeypatch.setattr(api, "fetch_withdrawn", lambda disease: [])
    monkeypatch.setattr(api, "fetch_neighbours", lambda disease: [])
    monkeypatch.setattr(api, "fetch_listed_medicines", lambda disease: on_list)
    monkeypatch.setattr(api, "added_by_hand", lambda disease_id: [])


def test_the_api_sends_the_line_the_count_and_the_sources(monkeypatch, tmp_path):
    """One matched medicine Open Targets has never listed. It is the only
    In trials card. The tab's numbers match that one card and its one trial."""
    disease = Disease(id="MONDO_T7", name="Example disease")
    fact = DrugFact(id="CHEMBL9", name="FARAWAY", best_stage="APPROVAL", withdrawn=False,
                    parent_id=None, parent_name=None)
    monkeypatch.setattr(api, "fetch_drug_facts", lambda ids: {"CHEMBL9": fact} if "CHEMBL9" in ids else {})
    path = tmp_path / "disease_search.sqlite"
    disease_search.write_sqlite(path, [
        _result("MONDO_T7", "Example disease", True,
                [{"medicine_id": "CHEMBL9", "nct_ids": ["NCT00000003"]}], [], 1),
    ], "2026-11-26")
    tray = {group: [] for group in GROUPS}
    _patch_find(monkeypatch, disease, tray, [], [])
    api.forget_answers()
    with TestClient(api.app) as client:
        monkeypatch.setattr(api, "_search", disease_search.SearchFile.open(path))
        answer = client.get("/api/clues", params={"disease_id": disease.id}).json()
    cards = (answer["being_studied"] + answer.get("more_in_trials", [])
             + answer.get("new_in_trials", []))
    assert [card["id"] for card in cards] == ["CHEMBL9"]
    assert cards[0]["ctgov_note"] == LINE
    assert answer["approved"] == []
    assert answer["trials_count_line"] == "This medicine is in 1 drug trial on ClinicalTrials.gov."
    assert answer["trials_sources_line"] == SOURCES
    assert len({card["id"] for card in cards}) == len(cards)


def test_a_skipped_disease_keeps_todays_cards_and_gains_the_link(monkeypatch, tmp_path):
    """Breast cancer's shape: nothing stored, a total, no new card."""
    disease = Disease(id="MONDO_SKIP", name="breast cancer")
    path = tmp_path / "disease_search.sqlite"
    disease_search.write_sqlite(path, [
        _result("MONDO_SKIP", "breast cancer", False, [], [], 7765),
    ], "2026-11-26")
    monkeypatch.setattr(api, "fetch_drug_facts", lambda ids: (_ for _ in ()).throw(AssertionError("no drug fetch")))
    tray = {group: [] for group in GROUPS}
    _patch_find(monkeypatch, disease, tray, [], [])
    api.forget_answers()
    with TestClient(api.app) as client:
        monkeypatch.setattr(api, "_search", disease_search.SearchFile.open(path))
        answer = client.get("/api/clues", params={"disease_id": disease.id}).json()
    assert answer["being_studied"] == []
    assert "more_in_trials" not in answer
    assert "trials_count_line" not in answer
    assert answer["all_trials"]["total"] == 7765
    assert answer["all_trials"]["url"].startswith("https://clinicaltrials.gov/search?")
    assert "breast" in answer["all_trials"]["url"].lower()


# ---------------------------------------------------------------- the page


BROWSER = r"""
"use strict";
const fs = require("fs");
const { chromium } = require("playwright");
const PAGE = fs.readFileSync(process.argv[1], "utf-8");
const ANSWERS = JSON.parse(fs.readFileSync(process.argv[2], "utf-8"));
const SITE = "http://moonlight.test";

function readTrials() {
  const count = document.querySelector('#tab-trials [data-part="count"]').textContent;
  const cards = [...document.querySelectorAll("#panel-trials .card")];
  const names = cards.map(card => card.querySelector('[data-slot="medicine-name"]').textContent);
  const notes = cards.map(card => {
    const note = card.querySelector('[data-slot="ctgov-note"]');
    return note ? note.textContent : "";
  });
  const countLine = document.getElementById("trials-count-line");
  const sources = document.getElementById("trials-sources-line");
  const link = document.getElementById("all-trials-link");
  const linkLine = document.getElementById("all-trials-line");
  const approved = [...document.querySelectorAll("#panel-approved [data-slot='medicine-name']")]
    .map(el => el.textContent);
  return {
    count, names, notes,
    cardCount: cards.length,
    countLine: countLine.hidden ? "" : countLine.textContent,
    sources: sources.hidden ? "" : sources.textContent,
    link: linkLine.hidden ? "" : link.textContent,
    linkHref: linkLine.hidden ? "" : link.href,
    approved,
    width: document.documentElement.clientWidth,
    shifted: document.documentElement.scrollWidth > document.documentElement.clientWidth + 1,
  };
}

(async () => {
  const browser = await chromium.launch();
  const out = {};
  for (const name of Object.keys(ANSWERS)) {
    const answer = ANSWERS[name];
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
        return route.fulfill({ contentType: "application/json", body: '{"fingerprint":"0123456789ab","revision":"local"}' });
      return route.abort();
    });
    await page.goto(SITE + "/?disease=" + answer.disease.id + "&tab=trials");
    await page.waitForSelector("#found", { state: "visible" });
    const focus = name === "skipped" ? "#all-trials-line" : "#trials-count-line";
    await page.locator(focus).scrollIntoViewIfNeeded();
    out[name] = await page.evaluate(readTrials);
    out[name].errors = errors;
    const shots = {one: process.argv[3], skipped: process.argv[4]};
    if (shots[name]) await page.screenshot({ path: shots[name], fullPage: false });
    await context.close();
  }
  await browser.close();
  console.log(JSON.stringify(out));
})().catch(problem => { console.error(problem); process.exit(1); });
"""


def _page_answer():
    """A one-card In trials tab, plus an approved medicine that must stay put."""
    return {
        "one": {
            "disease": {"id": "MONDO_T7", "name": "Example disease"},
            "about_disease": {"description": "", "source": None, "also_called": []},
            "rule_text": "Ordered.",
            "approved": [{
                "id": "CHEMBL1", "medicine": "Already Approved", "forms": ["Already Approved"],
                "proteins": [], "reports": 1, "source": None,
            }],
            "being_studied": [{
                "id": "CHEMBL9", "medicine": "Faraway", "forms": ["Faraway"],
                "proteins": [], "reports": 0, "source": None, "ending": "A clue to read about.",
                "ctgov_note": LINE,
            }],
            "new_clues": [],
            "left_out": {"not_approved": 0, "unclear_link": 0},
            "trials_count_line": "This medicine is in 1 drug trial on ClinicalTrials.gov.",
            "trials_sources_line": SOURCES,
        },
        "skipped": {
            "disease": {"id": "MONDO_0007254", "name": "breast cancer"},
            "about_disease": {"description": "", "source": None, "also_called": []},
            "rule_text": "Ordered.",
            "approved": [],
            "being_studied": [],
            "new_clues": [],
            "left_out": {"not_approved": 0, "unclear_link": 0},
            "all_trials": {"total": 7765, "url": "https://clinicaltrials.gov/search?cond=breast%20cancer"},
        },
    }


@pytest.fixture(scope="module")
def seen(tmp_path_factory):
    node = shutil.which("node")
    if not node or subprocess.run([node, "-e", "require('playwright')"], capture_output=True).returncode:
        pytest.skip("needs node with playwright to open a real browser")
    folder = tmp_path_factory.mktemp("t7")
    answers = folder / "answers.json"
    answers.write_text(json.dumps(_page_answer()), encoding="utf-8")
    shot = ROOT / "docs" / "ticket_t7_matched_trials_390.png"
    skipped_shot = ROOT / "docs" / "ticket_t7_breast_cancer_link_390.png"
    run = subprocess.run(
        [node, "-e", BROWSER, str(ROOT / "web" / "index.html"), str(answers), str(shot), str(skipped_shot)],
        capture_output=True, text=True, timeout=120, cwd=str(ROOT))
    assert run.returncode == 0, run.stderr[-3000:]
    return json.loads(run.stdout)


def test_the_tab_count_matches_the_cards_and_the_lines_show(seen):
    one = seen["one"]
    assert one["errors"] == []
    assert one["names"] == ["Faraway"]
    assert one["names"].count("Faraway") == 1
    assert "Already Approved" not in one["names"]
    assert one["notes"] == [LINE]
    assert one["countLine"] == "This medicine is in 1 drug trial on ClinicalTrials.gov."
    assert one["sources"] == SOURCES
    assert one["count"] == "(" + str(one["cardCount"]) + ")"
    assert one["cardCount"] == 1
    assert one["width"] == 390
    assert one["shifted"] is False


def test_a_skipped_disease_shows_the_all_trials_link(seen):
    skipped = seen["skipped"]
    assert skipped["errors"] == []
    assert skipped["names"] == []
    assert skipped["countLine"] == ""
    assert skipped["link"] == "All 7765 trials on ClinicalTrials.gov"
    assert skipped["linkHref"].startswith("https://clinicaltrials.gov/search?")
    assert skipped["width"] == 390
    assert skipped["shifted"] is False
