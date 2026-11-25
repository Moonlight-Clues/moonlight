"""Ticket 3.14. "multiple sclerosis" leads to the disease page, named as typed.

Open Targets 26.09 keeps multiple sclerosis under one entry, EFO_0803536,
whose own name is "multiple sclerosis symptom measurement". "multiple
sclerosis" is on its exact "also called" list, and the search already puts
it first (ticket 5.9). Its old ids MONDO_0005301 and EFO_0003885 are on its
"obsoleteTerms" list, and asking for them gives nothing.

MAIN 4's decisions, 25 Nov:
A. When the visitor arrived through an exact "also called" match, that name
   is the big heading of the disease page, with "Database name: ..." under
   it: the same words the search list has shown since 5.9. No new words.
B. Open Targets' description is shown as sent.
C. Not now: the not-found message stays as it is, and no bulk files are read.
The search stays as it is. The rule is not about multiple sclerosis: it is
about any disease reached through an exact "also called" name.

Saved files only, no network: fixtures/ms_lookalike/ (Open Targets, live
on 2026-11-25, data 26.09) and fixtures/probe_p2/search/diabetes.* (16 Nov).
Open Targets is replaced at fetch._post_json and Gemini at
translate._gemini_request. The browser test opens web/index.html in
Chromium, with the API answers built here from those files.

The two other diseases with measurement look-alikes, from the fixtures:
- autism spectrum disorder: Open Targets also sends "autism spectrum
  disorder symptom" (group phenotype, so it is not hidden).
- schizophrenia: Open Targets also sends "schizophrenia symptom severity
  measurement" (group measurement only, so it is hidden).
And asthma, an ordinary search, whose four measurement entries stay hidden.
"""

import json
import pathlib
import re
import shutil
import subprocess
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from moonlight import api, fetch, translate

ROOT = pathlib.Path(__file__).resolve().parent.parent
SAVED = ROOT / "fixtures" / "ms_lookalike"
OLDER_SEARCHES = ROOT / "fixtures" / "probe_p2" / "search"
PAGE_FILE = ROOT / "web" / "index.html"

MS = "EFO_0803536"
MS_DATABASE_NAME = "multiple sclerosis symptom measurement"
OLD_MS_IDS = ["MONDO_0005301", "EFO_0003885"]
ASD, SCHIZOPHRENIA, ASTHMA = "MONDO_0005258", "MONDO_0005090", "MONDO_0004979"
DIABETES = "MONDO_0005015"
LOOK_ALIKES = {
    "autism spectrum disorder": "autism spectrum disorder symptom",
    "schizophrenia": "schizophrenia symptom severity measurement",
    "asthma": "asthma symptoms measurement",
}
DATABASE_LINE = "Database name: "  # the 5.9 words, as the search list writes them
NOT_KNOWN = "Open Targets does not know this disease."  # unchanged (decision C)
MISSPELT = "multipel sclerosys"


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def slug(text):
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")


def saved_answer(body):
    """Stands in for fetch._post_json: the saved answer to this question."""
    assert set(body) == {"query", "variables"}
    variables = body["variables"]
    if body["query"] == fetch.SEARCH_QUERY:
        if variables["text"] == MISSPELT:
            return {"data": {"search": {"total": 0, "hits": []}}}
        for folder in (SAVED / "search", OLDER_SEARCHES):
            saved = folder / f"{slug(variables['text'])}.response.json"
            if saved.exists():
                assert load(saved.with_name(saved.name.replace(".response.", ".request.")))[
                    "query"] == body["query"]
                return load(saved)
        raise AssertionError(f"no saved search for {variables['text']!r}")
    if body["query"] == fetch.DISEASE_QUERY:
        saved = SAVED / "disease" / f"{variables['diseaseId']}.response.json"
        assert saved.exists(), f"no saved disease {variables['diseaseId']}"
        assert load(saved.with_name(saved.name.replace(".response.", ".request.")))[
            "query"] == body["query"]
        return load(saved)
    raise AssertionError("this test only asks searches and disease records")


def gemini_says(text):
    """Stands in for translate._gemini_request: Gemini writes this text."""
    answer = {"candidates": [{"content": {"parts": [{"text": text}]}}]}

    def fake(method, path, body=None, timeout=None):
        if method == "GET":
            return 200, {"models": [{
                "name": "models/gemini-3.5-flash",
                "supportedGenerationMethods": ["generateContent"],
            }]}
        return 200, answer
    return fake


@pytest.fixture(autouse=True)
def offline(tmp_path, monkeypatch):
    """Saved files instead of Open Targets. Real HTTP is an error."""
    monkeypatch.setenv("MOONLIGHT_CACHE_DIR", str(tmp_path))
    translate.forget_everything()
    api.forget_visitors()
    with patch("moonlight.fetch._post_json", side_effect=saved_answer), \
            patch("requests.request", side_effect=AssertionError("network used")), \
            patch("requests.post", side_effect=AssertionError("network used")), \
            patch("requests.get", side_effect=AssertionError("network used")), \
            patch("requests.sessions.Session.request",
                  side_effect=AssertionError("network used")):
        yield
    translate.forget_everything()


@pytest.fixture
def client():
    return TestClient(api.app)


def search_json(client, words, gemini="[]"):
    with patch("moonlight.translate._gemini_request", side_effect=gemini_says(gemini)):
        response = client.get("/api/search", params={"q": words})
    assert response.status_code == 200
    return response.json()


def clues_answer(disease_id):
    """A /api/clues answer for the disease: its record and description built
    by api.py from the saved Open Targets record, with empty tabs. The
    heading only reads "disease" and "about_disease"."""
    disease = fetch.fetch_disease(disease_id)
    return {
        "disease": {"id": disease.id, "name": disease.name},
        "about_disease": api._about_json(disease),
        "rule_text": api.RULE_TEXT,
        "approved": [], "being_studied": [], "new_clues": [],
        "left_out": {group: 0 for group in api.LEFT_OUT_GROUPS},
    }


# ---- the saved answers hold what the report says ----

def test_the_saved_answers_hold_the_cause():
    first = load(SAVED / "search" / "multiple_sclerosis.response.json")["data"]["search"]["hits"][0]
    assert first["id"] == MS and first["name"] == MS_DATABASE_NAME
    assert "measurement" in first["category"]
    old = load(SAVED / "old_ids" / f"{MS}.response.json")["data"]["disease"]
    assert old["obsoleteTerms"] == OLD_MS_IDS
    for old_id in OLD_MS_IDS:
        assert load(SAVED / "disease" / f"{old_id}.response.json") == {"data": {"disease": None}}
    assert load(SAVED / "data_version.response.json")["data"]["meta"]["dataVersion"] == {
        "year": "26", "month": "09", "iteration": None}


@pytest.mark.parametrize("words", list(LOOK_ALIKES))
def test_the_saved_searches_hold_a_look_alike(words):
    hits = load(SAVED / "search" / f"{slug(words)}.response.json")["data"]["search"]["hits"]
    assert LOOK_ALIKES[words] in [hit["name"] for hit in hits]


# ---- the search stays as it is ----

def test_api_multiple_sclerosis_search_is_as_before(client):
    data = search_json(client, "multiple sclerosis")
    assert data["matches"][0] == {"id": MS, "name": MS_DATABASE_NAME}
    assert data["also_called"] == {MS: "multiple sclerosis"}


@pytest.mark.parametrize("words, disease_id", [
    ("autism spectrum disorder", ASD), ("schizophrenia", SCHIZOPHRENIA), ("asthma", ASTHMA)])
def test_api_look_alike_searches_put_the_disease_first_with_no_swap(client, words, disease_id):
    data = search_json(client, words)
    assert data["matches"][0] == {"id": disease_id, "name": words}
    assert data["also_called"] == {}
    assert data["matches"][0]["name"] != LOOK_ALIKES[words]


def test_api_asthma_matches_are_the_same_as_on_16_november(client):
    data = search_json(client, "asthma")
    before = load(OLDER_SEARCHES / "asthma.response.json")["data"]["search"]["hits"]
    assert data["matches"] == [
        {"id": hit["id"], "name": hit["name"]} for hit in before
        if hit["category"] != ["measurement"]]


# ---- decision C: old ids and the not-found message are not touched ----

@pytest.mark.parametrize("old_id", OLD_MS_IDS)
def test_old_ids_still_get_the_same_not_found_message(client, old_id):
    response = client.get("/api/clues", params={"disease_id": old_id})
    assert response.status_code == 404
    assert response.json() == {"detail": NOT_KNOWN}


# ---- decision B: the description goes as sent ----

def test_the_description_is_open_targets_own_words():
    sent = load(SAVED / "disease" / f"{MS}.response.json")["data"]["disease"]["description"]
    assert clues_answer(MS)["about_disease"]["description"] == sent.strip()
    assert sent.startswith("Quantification of some aspect of multiple sclerosis symptoms")


# ---- the page, in a real browser ----

BROWSER_SCRIPT = r"""
"use strict";
const fs = require("fs");
const { chromium } = require("playwright");
const PAGE = fs.readFileSync(process.argv[1], "utf-8");
const PLAN = JSON.parse(fs.readFileSync(process.argv[2], "utf-8"));
const SITE = "http://moonlight.test";

function readHeading() {
  const line = document.getElementById("disease-database-name");
  const title = document.getElementById("disease-title");
  return {
    title: title.textContent,
    line: line ? line.textContent : null,
    lineShown: line ? line.checkVisibility() : null,
    lineRightUnderTitle: line ? title.nextElementSibling === line : null,
    description: document.getElementById("disease-description").textContent,
  };
}

async function open(page, step) {
  const answered = page.waitForResponse(r => new URL(r.url()).pathname === "/api/clues"
    && new URL(r.url()).searchParams.get("disease_id") === step.expectId);
  if (step.link) {
    await page.goto(SITE + "/?disease=" + step.link);
  } else {
    await page.fill("#disease-search", step.words);
    await page.press("#disease-search", "Enter");
    const where = step.chip ? "#suggestions button" : "#disease-matches button";
    await page.waitForSelector(where, { state: "visible" });
    const button = page.locator(where).first();
    step.picked = await button.locator("strong").textContent();
    step.small = await button.locator(".secondary").textContent();
    await button.click();
  }
  await answered;
  await page.waitForFunction(() => !document.getElementById("found").hidden
    && document.getElementById("disease-title").textContent !== "");
  const out = await page.evaluate(readHeading);
  out.picked = step.picked || null;
  out.small = step.small || null;
  await page.click("#print-page");
  out.printed = await page.evaluate(
    () => document.querySelector('#register [data-reg="disease"]').textContent);
  await page.click("#register-back");
  return out;
}

(async () => {
  const browser = await chromium.launch();
  const out = {};
  for (const [name, steps] of Object.entries(PLAN.scenarios)) {
    const context = await browser.newContext({ viewport: { width: 390, height: 844 } });
    const page = await context.newPage();
    const errors = [];
    page.on("pageerror", problem => errors.push(String(problem)));
    await page.addInitScript(() => { window.print = () => {}; });
    await context.route("**/*", route => {
      const url = new URL(route.request().url());
      if (url.origin !== SITE) return route.abort();
      if (url.pathname === "/")
        return route.fulfill({ contentType: "text/html; charset=utf-8", body: PAGE });
      if (url.pathname === "/api/search")
        return route.fulfill({ contentType: "application/json",
                               body: JSON.stringify(PLAN.search[url.searchParams.get("q")]) });
      if (url.pathname === "/api/clues")
        return route.fulfill({ contentType: "application/json",
                               body: JSON.stringify(PLAN.clues[url.searchParams.get("disease_id")]) });
      return route.fulfill({ status: 404, contentType: "application/json", body: "{}" });
    });
    await page.goto(SITE + "/");
    const seen = [];
    for (const step of steps) seen.push(await open(page, step));
    out[name] = { errors, seen };
    await context.close();
  }
  await browser.close();
  console.log(JSON.stringify(out));
})().catch(problem => { console.error(problem); process.exit(1); });
"""

SCENARIOS = {
    "ms": [{"words": "multiple sclerosis", "expectId": MS}],
    "ms_capitals": [{"words": "  MULTIPLE Sclerosis ", "expectId": MS}],
    "ms_did_you_mean": [{"words": MISSPELT, "chip": True, "expectId": MS}],
    "ms_link": [{"link": MS, "expectId": MS}],
    "asd": [{"words": "autism spectrum disorder", "expectId": ASD}],
    "schizophrenia": [{"words": "schizophrenia", "expectId": SCHIZOPHRENIA}],
    "asthma": [{"words": "asthma", "expectId": ASTHMA}],
    "diabetes": [{"words": "diabetes", "expectId": DIABETES}],
    "ms_then_asthma": [{"words": "multiple sclerosis", "expectId": MS},
                       {"words": "asthma", "expectId": ASTHMA}],
}


@pytest.fixture(scope="module")
def seen(tmp_path_factory):
    """Opens the page once per scenario and returns what a reader sees."""
    node = shutil.which("node")
    if not node or subprocess.run(
            [node, "-e", "require('playwright')"], capture_output=True).returncode:
        pytest.skip("needs node with playwright to open a real browser")
    client = TestClient(api.app)
    with patch("moonlight.fetch._post_json", side_effect=saved_answer), \
            patch("requests.sessions.Session.request",
                  side_effect=AssertionError("network used")):
        search = {}
        for steps in SCENARIOS.values():
            for step in steps:
                # The page trims the typed words before it searches.
                words = step.get("words", "").strip()
                if words and words not in search:
                    translate.forget_everything()
                    api.forget_visitors()
                    gemini = '["Multiple Sclerosis"]' if step.get("chip") else "[]"
                    search[words] = search_json(client, words, gemini)
        diabetes_saved = SAVED / "disease" / f"{DIABETES}.response.json"
        clues = {}
        for disease_id in (MS, ASD, SCHIZOPHRENIA, ASTHMA):
            clues[disease_id] = clues_answer(disease_id)
    # Diabetes has no saved record here: its name comes from its saved search.
    assert not diabetes_saved.exists()
    clues[DIABETES] = {
        "disease": {"id": DIABETES, "name": "diabetes mellitus"},
        "about_disease": {"description": "", "source": None, "also_called": []},
        "rule_text": api.RULE_TEXT, "approved": [], "being_studied": [], "new_clues": [],
        "left_out": {group: 0 for group in api.LEFT_OUT_GROUPS},
    }
    translate.forget_everything()
    plan = tmp_path_factory.mktemp("heading_3_14") / "plan.json"
    plan.write_text(json.dumps({"scenarios": SCENARIOS, "search": search, "clues": clues}),
                    encoding="utf-8")
    run = subprocess.run([node, "-e", BROWSER_SCRIPT, str(PAGE_FILE), str(plan)],
                         capture_output=True, text=True, timeout=240, cwd=str(ROOT))
    assert run.returncode == 0, run.stderr[-3000:]
    out = json.loads(run.stdout)
    for name in SCENARIOS:
        assert out[name]["errors"] == [], name
    return out


def the_page(seen, name, place=0):
    return seen[name]["seen"][place]


# EXAMPLE: "multiple sclerosis" leads to the disease page, named as typed.

@pytest.mark.parametrize("name", ["ms", "ms_capitals", "ms_did_you_mean"])
def test_browser_multiple_sclerosis_heading_is_the_typed_name(seen, name):
    page = the_page(seen, name)
    assert page["picked"].rstrip("?") == "Multiple sclerosis"
    assert page["title"] == "Multiple sclerosis"
    assert page["line"] == DATABASE_LINE + MS_DATABASE_NAME
    assert page["lineShown"] is True
    assert page["lineRightUnderTitle"] is True


def test_browser_the_line_is_the_search_lists_own_words(seen):
    page = the_page(seen, "ms")
    # The search list wrote "Database name: <name> · <id>". The heading's line
    # is the same words, without the id.
    assert page["small"] == f"{DATABASE_LINE}{MS_DATABASE_NAME} · {MS}"
    assert page["small"].startswith(page["line"])


def test_browser_multiple_sclerosis_description_is_as_sent(seen):
    sent = load(SAVED / "disease" / f"{MS}.response.json")["data"]["disease"]["description"]
    assert the_page(seen, "ms")["description"] == sent.strip()


def test_browser_the_printed_sheet_carries_the_same_heading(seen):
    assert the_page(seen, "ms")["printed"] == "Multiple sclerosis"


def test_browser_a_link_with_no_search_keeps_the_database_name(seen):
    page = the_page(seen, "ms_link")
    assert page["title"] == "Multiple sclerosis symptom measurement"
    assert page["line"] == "" and page["lineShown"] is False


# EXAMPLE: two diseases with look-alikes, and asthma, are unchanged.

@pytest.mark.parametrize("name, words", [
    ("asd", "Autism spectrum disorder"), ("schizophrenia", "Schizophrenia"), ("asthma", "Asthma")])
def test_browser_look_alike_diseases_head_with_their_own_name(seen, name, words):
    page = the_page(seen, name)
    assert page["picked"] == words
    assert page["title"] == words
    assert page["line"] == "" and page["lineShown"] is False
    assert page["printed"] == words


def test_browser_a_second_search_takes_the_line_away(seen):
    first, second = seen["ms_then_asthma"]["seen"]
    assert first["title"] == "Multiple sclerosis" and first["lineShown"] is True
    assert second["title"] == "Asthma"
    assert second["line"] == "" and second["lineShown"] is False


# The rule is about any exact "also called" match, not one disease.

def test_browser_any_also_called_match_heads_with_the_typed_name(seen):
    page = the_page(seen, "diabetes")
    assert page["title"] == "Diabetes"
    assert page["line"] == DATABASE_LINE + "diabetes mellitus"
    assert page["lineShown"] is True
