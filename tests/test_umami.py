"""Ticket 8.3. Moonlight counts visits with Umami, privately.

Each EXAMPLE in the ticket is a test here. No test touches the network
and nothing is ever sent to Umami.

The first tests read the page from GET /. The browser tests open the page
in a real browser (Chromium, driven by tests/umami/browser_check.js) and
catch every outside request inside the browser, where it is stopped. The
tracker those tests run is a saved copy of https://cloud.umami.is/script.js
(tests/umami/script.saved.js, saved 2026-11-16). The page is served by a
local copy of the API that reads the saved Open Targets files.

Attribute names were checked on 2026-11-16 against Umami's tracker
configuration page and against the saved script.
"""

import json
import pathlib
import re
import shutil
import socket
import subprocess
import threading
import time
from unittest.mock import patch

import pytest
import uvicorn
from fastapi.testclient import TestClient

import test_api as saved  # the fakes that read saved files
from moonlight import api, cache, explain, fetch, translate

ROOT = pathlib.Path(__file__).resolve().parent.parent
HERE = pathlib.Path(__file__).resolve().parent / "umami"
SAVED_SCRIPT = HERE / "script.saved.js"

SCRIPT_ADDRESS = "https://cloud.umami.is/script.js"
WEBSITE_ID = "dad3a425-ea8e-4028-9768-88a183fc9140"
DOMAINS = "moonlightclues.com,www.moonlightclues.com,moonlight-1038733794937.asia-south1.run.app"
GUIDE_LINE = (
    "Moonlight counts visits with Umami. It uses no cookies, and it never "
    "receives the disease or anything you type."
)
GEMINI_LINE = "The words you type are sent to Gemini. Do not type names or private details."
DECISION = (
    "- 2026-11-16: I changed my mind about counting visitors. Moonlight uses "
    "Umami to count visits and which country they come from. It never gets "
    "the disease or any words someone types, and it uses no cookies. It is "
    "the only thing my page loads from outside."
)
# Nothing typed and no disease id may appear in anything caught.
NEVER_SENT = ("disease", "mondo", "tab", "guide", "pulmonary", "arterial",
              "hypertension", "secretword", "example.org/", "?", "#")


@pytest.fixture(scope="module")
def page():
    return TestClient(api.app).get("/").text


def outside_script_tags(page):
    return re.findall(r"(?is)<script\b[^>]*\bsrc\s*=[^>]*>", page)


def attributes(tag):
    found = dict(re.findall(r'([a-z-]+)="([^"]*)"', tag))
    found.update({name: "" for name in re.findall(r"\s([a-z-]+)(?=[\s>])", tag) if name not in found})
    return found


# ---- Example: exactly one script from outside, with every attribute ----

def test_one_outside_script_from_umami_with_the_website_id(page):
    tags = outside_script_tags(page)
    assert len(tags) == 1, tags
    tag = attributes(tags[0])
    assert tag["src"] == SCRIPT_ADDRESS
    assert tag["data-website-id"] == WEBSITE_ID


def test_the_script_has_every_privacy_attribute(page):
    tag = attributes(outside_script_tags(page)[0])
    assert tag["data-exclude-search"] == "true"   # rule 1
    assert tag["data-exclude-hash"] == "true"     # rule 2
    assert tag["data-do-not-track"] == "true"     # rule 5
    assert tag["data-domains"] == DOMAINS         # rule 7
    assert tag["data-before-send"]                # rules 1, 3, 4
    assert "defer" in tag


def test_the_script_asks_for_nothing_more(page):
    # Rule 6. No user id, tag, performance or error tracking, no other host.
    tag = attributes(outside_script_tags(page)[0])
    allowed = {"src", "defer", "crossorigin", "data-website-id", "data-domains",
               "data-exclude-search", "data-exclude-hash", "data-do-not-track",
               "data-before-send"}
    assert set(tag) <= allowed, set(tag) - allowed
    lowered = page.lower()
    for word in ("data-distinct-id", "data-tag", "data-performance", "data-errors",
                 "data-host-url", "data-fetch-credentials", "data-umami-event",
                 "umamiconfig", "umami.track", "umami.identify", "captureexception",
                 "recorder"):
        assert word not in lowered, word
    assert not re.search(r"umami\s*\.\s*(track|identify)", page)


def test_every_attribute_name_is_one_the_saved_tracker_reads(page):
    # Rule 8. The saved tracker reads its settings with k("name").
    tracker = SAVED_SCRIPT.read_text(encoding="utf-8")
    read_by_tracker = set(re.findall(r'\bk\("([a-z-]+)"\)', tracker))
    tag = attributes(outside_script_tags(page)[0])
    for name in tag:
        if name.startswith("data-"):
            assert name[len("data-"):] in read_by_tracker, name


def test_the_before_send_function_is_on_the_page_before_the_tracker(page):
    tag = outside_script_tags(page)[0]
    name = attributes(tag)["data-before-send"]
    assert re.fullmatch(r"[A-Za-z]+", name)
    assert f"window.{name} = function" in page[: page.index(tag)]


def test_the_browser_sends_only_the_site_as_the_referer(page):
    # The browser's own Referer header, for the script and for each send.
    assert '<meta name="referrer" content="strict-origin-when-cross-origin">' in page


def test_the_script_is_loaded_without_cookies(page):
    assert attributes(outside_script_tags(page)[0])["crossorigin"] == "anonymous"


def test_the_saved_tracker_never_touches_cookies_or_writes_storage():
    tracker = SAVED_SCRIPT.read_text(encoding="utf-8")
    assert ".cookie" not in tracker
    assert "setItem" not in tracker and "sessionStorage" not in tracker
    assert "indexedDB" not in tracker


# ---- Example: no other outside script, stylesheet, font or image ----

def test_nothing_else_comes_from_outside(page):
    without = page.replace(SCRIPT_ADDRESS, "")
    assert page.count(SCRIPT_ADDRESS) == 1
    assert "http" not in without.lower()
    assert not re.search(r"""(?:src|href|action|poster|srcset)\s*=\s*["']?\s*//""", without, flags=re.I)
    assert "<link" not in without.lower()
    assert "@import" not in without
    assert not re.search(r"<(img|iframe|video|audio|source|embed|object)\b", without, flags=re.I)
    addresses = re.findall(r"url\(\s*[\"']?([^\"')]{0,12})", without)
    assert all(address.startswith("data:") for address in addresses), addresses


# ---- Add-on: the guide tells people they are counted ----

def test_the_guide_says_visits_are_counted_after_the_gemini_line(page):
    guide = page[page.index('<section id="guide"'): page.index("<!-- end of the guide -->")]
    assert guide.count(GUIDE_LINE) == 1
    assert page.count(GUIDE_LINE) == 1
    facts = guide[guide.index("Where the facts come from"):]
    assert GEMINI_LINE in facts
    after_gemini = facts[facts.index(GEMINI_LINE) + len(GEMINI_LINE):]
    assert after_gemini.lstrip().startswith("</p>")
    assert after_gemini.lstrip()[len("</p>"):].lstrip().startswith("<p>" + GUIDE_LINE + "</p>")


def test_the_safety_line_is_unchanged(page):
    assert saved.SAFETY_LINE in page


def test_the_decision_is_written_down_word_for_word():
    assert DECISION in (ROOT / "DECISIONS.md").read_text(encoding="utf-8").splitlines()


# ---- Examples in a real browser ----

def _free_port():
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


@pytest.fixture(scope="module")
def caught(tmp_path_factory):
    """Runs the browser once and returns everything it caught."""
    node = shutil.which("node")
    if not node or subprocess.run(
            [node, "-e", "require('playwright')"], capture_output=True).returncode:
        pytest.skip("needs node with playwright to open a real browser")

    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setenv("MOONLIGHT_CACHE_DIR", str(tmp_path_factory.mktemp("saved")))
    for forget in (explain.forget_everything, translate.forget_everything,
                   cache.forget_memory, fetch.forget_version):
        forget()
    port = _free_port()
    server = uvicorn.Server(uvicorn.Config(api.app, host="127.0.0.1", port=port, log_level="error"))
    with patch("moonlight.fetch._post_json", side_effect=saved.fake_post_json), \
            patch("moonlight.fetch._send", side_effect=saved.fake_send), \
            patch("moonlight.explain._gemini_request", side_effect=saved.gemini_unreachable), \
            patch("moonlight.translate._gemini_request", side_effect=saved.gemini_unreachable), \
            patch("requests.sessions.Session.request", side_effect=AssertionError("network used")), \
            saved.with_saved_targets():
        thread = threading.Thread(target=server.run, daemon=True)
        thread.start()
        while not server.started:
            time.sleep(0.05)
        try:
            run = subprocess.run(
                [node, str(HERE / "browser_check.js"), f"http://127.0.0.1:{port}", str(SAVED_SCRIPT)],
                capture_output=True, text=True, timeout=240)
        finally:
            server.should_exit = True
            thread.join(timeout=10)
    monkeypatch.undo()
    for forget in (explain.forget_everything, translate.forget_everything,
                   cache.forget_memory, fetch.forget_version):
        forget()
    assert run.returncode == 0, run.stderr
    result = json.loads(run.stdout)
    print("\nCAUGHT IN THE BROWSER (nothing was sent to Umami):")
    print(json.dumps(result, indent=1))
    return result


def sends(part):
    return part["caught"]["umami"]


def assert_private(part):
    assert part["caught"]["headersClean"]
    for send in sends(part):
        assert send["method"] == "POST"
        text = json.dumps(send).lower().replace("https://", "")
        for word in NEVER_SENT:
            assert word not in text, (word, send)


def test_browser_a_disease_link_sends_only_the_path(caught):
    link = caught["link"]
    assert link["caught"]["scriptLoads"] == 1
    assert len(sends(link)) == 1
    body = sends(link)[0]["body"]
    assert body["type"] == "event"
    payload = body["payload"]
    assert payload["url"] == "/"
    assert payload["title"] == "Moonlight"
    assert payload["referrer"] == "https://example.org"   # the site only, rule 4
    assert payload["website"] == WEBSITE_ID
    assert payload["hostname"] == "moonlightclues.com"
    assert set(payload) == {"website", "hostname", "screen", "language", "title", "url", "referrer"}
    assert_private(link)


def test_browser_the_title_never_changes(caught):
    assert caught["link"]["title"] == "Moonlight"
    assert caught["use"]["seen"]["titleAfterSearch"] == "Moonlight"


def test_browser_search_tabs_and_guide_send_nothing_typed(caught):
    use = caught["use"]
    assert use["seen"]["diseaseTitle"].lower() == "pulmonary arterial hypertension"
    assert use["seen"]["clueCards"] > 0 and use["seen"]["guideOpen"]
    assert len(sends(use)) == 2   # one for "/", one for "/?guide=1". None for a search or a tab.
    for send in sends(use):
        payload = send["body"]["payload"]
        assert send["body"]["type"] == "event"
        assert payload["url"] == "/" and payload["title"] == "Moonlight"
        assert payload["referrer"] in ("", "https://moonlightclues.com")
        assert "name" not in payload and "data" not in payload and "id" not in payload
    assert_private(use)


def test_browser_only_umami_is_asked_for_anything_outside(caught):
    for part in caught.values():
        assert part["caught"]["otherOutside"] == []
        for send in sends(part):
            assert send["to"] == "https://gateway.umami.is/api/send"


def test_browser_no_cookie_and_nothing_stored(caught):
    # The trap even tries to set a cookie on both answers. The browser refuses.
    for part in (caught["link"], caught["use"]):
        assert part["storage"] == {"cookies": [], "documentCookie": "",
                                   "localStorageKeys": [], "sessionStorageKeys": []}


def test_browser_page_works_the_same_when_umami_is_blocked(caught):
    blocked, use = caught["blocked"], caught["use"]
    assert blocked["caught"]["scriptLoads"] == 1   # it was asked for, and blocked
    assert blocked["umamiExists"] == "undefined"
    assert sends(blocked) == []
    assert blocked["caught"]["pageErrors"] == []
    assert blocked["seen"] == use["seen"]
    assert blocked["seen"]["safetyLine"] == saved.SAFETY_LINE


def test_browser_no_page_error_with_umami_running(caught):
    for part in caught.values():
        assert part["caught"]["pageErrors"] == []


def test_browser_do_not_track_is_respected(caught):
    assert caught["doNotTrack"]["caught"]["scriptLoads"] == 1
    assert sends(caught["doNotTrack"]) == []


def test_browser_a_laptop_is_not_counted(caught):
    assert caught["laptop"]["caught"]["scriptLoads"] == 1
    assert sends(caught["laptop"]) == []


def test_browser_the_rule_holds_with_only_one_of_the_two_guards(caught):
    # Rule 1 asks for two guards. Here the before-send function is taken
    # away, and data-exclude-search and data-exclude-hash work alone.
    one = caught["oneGuardOnly"]
    assert one["guardMissing"] == "undefined"
    assert len(sends(one)) == 1
    payload = sends(one)[0]["body"]["payload"]
    assert payload["url"] == "https://moonlightclues.com/"
    assert payload["title"] == "Moonlight"
    text = json.dumps(sends(one)).lower()
    for word in ("disease", "mondo", "tab", "secretword", "?", "#"):
        assert word not in text, word
    assert one["caught"]["headersClean"]
