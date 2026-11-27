"""Ticket 3.29. The browser title and the link preview.

A shared link is read by WhatsApp before any script runs, so the server
writes the title and the description into the HTML it sends back.
The home page, and a disease Open Targets does not know, both use the
home title. A known disease uses Open Targets' own name.

The description is the same on every page, word for word:

    What open research records about the medicine for any disease,
    with the official label beside each one.

Saved files only. No network: fetch._post_json is swapped for a fake.
The browser test opens the page in Chromium, searches, and reads the
title the tab shows after the results are drawn.
"""

import html
import json
import os
import pathlib
import re
import shutil
import subprocess
from unittest.mock import patch

import pytest
import requests
from fastapi.testclient import TestClient

import test_api as saved
from moonlight import api, explain, fetch, translate

ROOT = pathlib.Path(__file__).resolve().parent.parent
PAGE_FILE = ROOT / "web" / "index.html"
PAH_ID = saved.PAH_ID
UNKNOWN_ID = "MONDO_0000000"
# A name that would break the page if it were pasted in raw.
ODD_ID = "MONDO_ODD_NAME"
ODD_NAME = 'A & B <tag> "quote"'
# The ticket's words, exactly. "beside", and "the medicine" singular.
DESCRIPTION = (
    "What open research records about the medicine for any disease, "
    "with the official label beside each one."
)
HOME_TITLE = "Moonlight"


def open_targets_name():
    """The disease's name as the saved Open Targets answer spells it."""
    path = ROOT / "fixtures" / "MONDO_0015924" / "disease_description.response.json"
    return json.loads(path.read_text(encoding="utf-8"))["data"]["disease"]["name"]


def disease_title(name):
    return name + " · " + HOME_TITLE


def fake_post_json(body):
    """The saved PAH answers, plus one made-up name and one unknown id."""
    variables = body["variables"]
    disease_id = variables.get("diseaseId")
    if disease_id == ODD_ID:
        return {"data": {"disease": {
            "id": ODD_ID, "name": ODD_NAME, "description": None, "synonyms": None,
        }}}
    if disease_id == UNKNOWN_ID:
        return {"data": {"disease": None}}
    return saved.fake_post_json(body)


@pytest.fixture
def client():
    """Saved files instead of Open Targets. A real HTTP call is an error."""
    explain.forget_everything()
    translate.forget_everything()
    with patch("moonlight.fetch._post_json", side_effect=fake_post_json), \
            patch("moonlight.explain._gemini_request", side_effect=saved.gemini_unreachable), \
            patch("moonlight.translate._gemini_request", side_effect=saved.gemini_unreachable), \
            patch("requests.sessions.Session.request",
                  side_effect=AssertionError("network used")):
        yield TestClient(api.app)
    explain.forget_everything()
    translate.forget_everything()


def assert_preview(page, title):
    """The four tags a link preview reads, already filled in, before any script."""
    safe_title = html.escape(title, quote=True)
    safe_description = html.escape(DESCRIPTION, quote=True)
    assert page.count("<title>") == 1
    assert len(re.findall(r'<meta name="description"', page)) == 1
    assert len(re.findall(r'<meta property="og:title"', page)) == 1
    assert len(re.findall(r'<meta property="og:description"', page)) == 1
    assert f"<title>{safe_title}</title>" in page
    assert f'<meta name="description" content="{safe_description}">' in page
    assert f'<meta property="og:title" content="{safe_title}">' in page
    assert f'<meta property="og:description" content="{safe_description}">' in page
    head = page[:page.index("<script")]
    for bit in ("<title>", 'name="description"', 'property="og:title"',
                'property="og:description"'):
        assert bit in head, bit


def assert_home(page):
    assert_preview(page, HOME_TITLE)


# ---- the served HTML: home, a known id, an unknown id ----

def test_the_home_page_has_the_home_title_and_the_description(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    assert_home(response.text)


def test_the_home_page_does_not_ask_open_targets():
    """No disease in the address: nothing to look up."""
    called = []

    def spy(body):
        called.append(body)
        return fake_post_json(body)

    with patch("moonlight.fetch._post_json", side_effect=spy):
        page = TestClient(api.app).get("/").text
    assert called == []
    assert_home(page)


def test_a_known_disease_uses_open_targets_name(client):
    name = open_targets_name()
    assert name == "pulmonary arterial hypertension"  # as the saved answer spells it
    response = client.get("/", params={"disease": PAH_ID})
    assert response.status_code == 200
    assert_preview(response.text, disease_title(name))
    # The preview sentence is not Open Targets' description of the disease.
    sent = json.loads(
        (ROOT / "fixtures" / "MONDO_0015924" / "disease_description.response.json")
        .read_text(encoding="utf-8"))["data"]["disease"]["description"]
    assert sent not in response.text
    assert DESCRIPTION in response.text


def test_a_link_with_a_tab_still_uses_the_disease_name(client):
    page = client.get("/", params={"disease": PAH_ID, "tab": "clues"}).text
    assert_preview(page, disease_title(open_targets_name()))


def test_an_unknown_id_uses_the_home_page_text(client):
    page = client.get("/", params={"disease": UNKNOWN_ID}).text
    assert_home(page)
    assert UNKNOWN_ID not in page


def test_an_unknown_id_is_not_written_into_the_page(client):
    nasty = '"><script>alert(1)</script>'
    page = client.get("/", params={"disease": nasty}).text
    assert_home(page)
    assert nasty not in page
    assert "<script>alert" not in page


def test_a_name_with_html_is_escaped(client):
    page = client.get("/", params={"disease": ODD_ID}).text
    assert_preview(page, disease_title(ODD_NAME))
    assert ODD_NAME not in page
    assert "<tag>" not in page


@pytest.mark.parametrize("problem", [
    fetch.FetchError("down"),
    requests.ConnectionError("down"),
])
def test_when_open_targets_does_not_answer_the_page_still_opens(problem):
    """A shared link still opens. With no name, it uses the home title."""
    def broken(body):
        raise problem

    with patch("moonlight.fetch._post_json", side_effect=broken), \
            patch("requests.sessions.Session.request",
                  side_effect=AssertionError("network used")):
        response = TestClient(api.app).get("/", params={"disease": PAH_ID})
    assert response.status_code == 200
    assert_home(response.text)


# ---- one browser test: the title after a search ----

BROWSER_SCRIPT = r"""
"use strict";
const fs = require("fs");
const { chromium } = require("playwright");
const PAGE = fs.readFileSync(process.argv[1], "utf-8");
const PLAN = JSON.parse(fs.readFileSync(process.argv[2], "utf-8"));
const SHOT = process.argv[3] || "";
const SITE = "http://moonlight.test";
const TYPED = "pulmonary arterial hypertension";

(async () => {
  const browser = await chromium.launch();
  const context = await browser.newContext({ viewport: { width: 390, height: 844 } });
  const page = await context.newPage();
  const errors = [];
  page.on("pageerror", problem => errors.push(String(problem)));
  await context.route("**/*", route => {
    const url = new URL(route.request().url());
    if (url.origin !== SITE) return route.abort();
    if (url.pathname === "/")
      return route.fulfill({ contentType: "text/html; charset=utf-8", body: PAGE });
    if (url.pathname === "/api/search") {
      const body = PLAN.search[url.searchParams.get("q")];
      if (!body) return route.fulfill({ status: 404, contentType: "application/json", body: "{}" });
      return route.fulfill({ contentType: "application/json", body: JSON.stringify(body) });
    }
    if (url.pathname === "/api/clues") {
      const body = PLAN.clues[url.searchParams.get("disease_id")];
      if (!body) return route.fulfill({ status: 404, contentType: "application/json", body: "{}" });
      return route.fulfill({ contentType: "application/json", body: JSON.stringify(body) });
    }
    if (url.pathname === "/api/version")
      return route.fulfill({ status: 404, contentType: "application/json", body: "{}" });
    return route.abort();
  });
  await page.goto(SITE + "/");
  const titleBefore = await page.title();
  await page.fill("#disease-search", TYPED);
  await page.click("#search-form button[type=submit]");
  await page.locator("#disease-matches button", { hasText: PLAN.id }).click();
  await page.waitForSelector("#found:not([hidden])");
  await page.waitForFunction(() => document.getElementById("disease-title").textContent !== "");
  const out = {
    errors,
    titleBefore,
    title: await page.title(),
    heading: await page.textContent("#disease-title"),
    width: page.viewportSize().width,
  };
  if (SHOT) {
    await page.locator("#disease-title").scrollIntoViewIfNeeded();
    await page.screenshot({ path: SHOT });
    out.shot = SHOT;
  }
  await browser.close();
  console.log(JSON.stringify(out));
})().catch(problem => { console.error(String(problem && problem.stack || problem)); process.exit(1); });
"""


@pytest.fixture(scope="module")
def searched(tmp_path_factory):
    """Searches once in Chromium and returns the title the tab shows."""
    node = shutil.which("node")
    if not node or subprocess.run(
            [node, "-e", "require('playwright')"], capture_output=True).returncode:
        pytest.skip("needs node with playwright to open a real browser")
    explain.forget_everything()
    translate.forget_everything()
    api.forget_answers()
    api.forget_visitors()
    with patch("moonlight.fetch._post_json", side_effect=fake_post_json), \
            patch("moonlight.translate._gemini_request", side_effect=saved.gemini_unreachable), \
            patch("moonlight.explain._gemini_request", side_effect=saved.gemini_unreachable), \
            patch("requests.sessions.Session.request",
                  side_effect=AssertionError("network used")):
        with saved.with_targets("BMPR2"):
            client = TestClient(api.app)
            search = client.get(
                "/api/search", params={"q": "pulmonary arterial hypertension"}).json()
            clues = client.get("/api/clues", params={"disease_id": PAH_ID}).json()
    assert search["matches"][0]["id"] == PAH_ID
    assert clues["disease"]["name"] == open_targets_name()
    plan = tmp_path_factory.mktemp("title_3_29") / "plan.json"
    plan.write_text(json.dumps({
        "id": PAH_ID,
        "search": {"pulmonary arterial hypertension": search},
        "clues": {PAH_ID: clues},
    }), encoding="utf-8")
    shot = os.environ.get("MOONLIGHT_329_SHOT", "")
    run = subprocess.run(
        [node, "-e", BROWSER_SCRIPT, str(PAGE_FILE), str(plan), shot],
        capture_output=True, text=True, timeout=240, cwd=str(ROOT))
    assert run.returncode == 0, run.stderr[-4000:]
    found = json.loads(run.stdout)
    assert found["errors"] == [], found["errors"]
    return found


def test_browser_the_title_after_a_search(searched):
    assert searched["width"] == 390
    assert searched["titleBefore"] == HOME_TITLE
    assert searched["title"] == disease_title(open_targets_name())
    assert searched["heading"]  # the page drew the disease
