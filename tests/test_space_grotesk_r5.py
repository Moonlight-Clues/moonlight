"""Ticket R5. Moonlight ships its own heading font, Space Grotesk.

Each line of the ticket is a test here. No test touches the network.

The browser tests open the page and the corrections page in a real browser
(Chromium, through Playwright) at phone width. The machine running them does
not have Space Grotesk installed (the test checks that first), so the only way
a heading can be drawn in it is that the site sent the file itself.

The one outside address the page is allowed to ask for is Umami's counter
(ticket 8.3, DECISIONS.md: "the only thing my page loads from outside"). The
browser stops that request too, so nothing is sent. Any other outside address
fails the test.
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
from moonlight import api, cache, corrections_page, explain, fetch, translate

ROOT = pathlib.Path(__file__).resolve().parent.parent
FONT_FILE = ROOT / "web" / "fonts" / "space-grotesk-latin-wght-normal.woff2"
LICENCE_FILE = ROOT / "web" / "fonts" / "OFL.txt"
FONT_ADDRESS = "/fonts/space-grotesk-latin-wght-normal.woff2"
INDEX = ROOT / "web" / "index.html"
ALLOWED_OUTSIDE = {"cloud.umami.is"}


def test_the_font_file_and_its_licence_are_in_web_fonts():
    assert FONT_FILE.is_file()
    assert FONT_FILE.read_bytes()[:4] == b"wOF2"
    licence = LICENCE_FILE.read_text(encoding="utf-8")
    assert "SIL OPEN FONT LICENSE Version 1.1" in licence
    assert "Space Grotesk Project Authors" in licence


def test_the_font_address_answers_with_the_file_and_a_long_cache_time():
    answer = TestClient(api.app).get(FONT_ADDRESS)
    assert answer.status_code == 200
    assert answer.content == FONT_FILE.read_bytes()
    assert answer.headers["content-type"] in ("font/woff2", "application/font-woff2")
    cache_line = answer.headers["cache-control"]
    assert "public" in cache_line and "immutable" in cache_line
    assert int(re.search(r"max-age=(\d+)", cache_line).group(1)) >= 31536000


def test_an_address_that_is_not_in_the_folder_is_not_found():
    client = TestClient(api.app)
    assert client.get("/fonts/nothing.woff2").status_code == 404
    assert client.get("/fonts/../moonlight/api.py").status_code in (404, 400)
    assert client.get("/fonts/%2e%2e/moonlight/api.py").status_code == 404


FACE = re.compile(r"@font-face\s*\{[^}]*font-family:\s*[\"']Space Grotesk[\"'][^}]*\}")


@pytest.mark.parametrize("name", ["index", "corrections"])
def test_both_pages_have_the_font_face_rule(name):
    html = INDEX.read_text(encoding="utf-8") if name == "index" else \
        TestClient(api.app).get("/corrections").text
    rule = FACE.search(html)
    assert rule, "no @font-face rule for Space Grotesk"
    assert "url(%s)" % FONT_ADDRESS in rule.group(0).replace('"', "").replace("'", "")
    assert "woff2" in rule.group(0)
    assert "font-display:swap" in rule.group(0).replace(" ", "")
    assert re.search(r"font-weight:\s*300\s+700", rule.group(0))


def test_the_home_page_preloads_the_font():
    html = INDEX.read_text(encoding="utf-8")
    link = re.search(r"<link[^>]*rel=\"preload\"[^>]*>", html)
    assert link, "no preload link"
    tag = link.group(0)
    assert 'href="%s"' % FONT_ADDRESS in tag
    assert 'as="font"' in tag and 'type="font/woff2"' in tag
    assert "crossorigin" in tag  # fonts are always fetched in cors mode
    assert html.index(tag) < html.index("<style>")  # found before the styles


def test_the_safety_line_and_other_texts_are_untouched():
    html = INDEX.read_text(encoding="utf-8")
    assert saved.SAFETY_LINE in html


BROWSER_SCRIPT = r"""
"use strict";
const { chromium } = require("playwright");
const LOCAL = process.argv[1];
const ALLOWED = JSON.parse(process.argv[2]);

async function fontsOf(page, client, selector) {
  const { root } = await client.send("DOM.getDocument", { depth: 0 });
  const { nodeId } = await client.send("DOM.querySelector", { nodeId: root.nodeId, selector });
  if (!nodeId) return { selector, missing: true };
  const { fonts } = await client.send("CSS.getPlatformFontsForNode", { nodeId });
  const box = await page.evaluate(s => {
    const el = document.querySelector(s);
    return { shown: el.getClientRects().length > 0, text: el.textContent.trim().slice(0, 40) };
  }, selector);
  return { selector, ...box, fonts };
}

async function look(browser, path, selectors) {
  const context = await browser.newContext({ viewport: { width: 390, height: 844 } });
  const hosts = [], outside = [], errors = [];
  await context.route("**/*", route => {
    const url = new URL(route.request().url());
    if (url.origin === LOCAL) return route.continue();
    outside.push(url.host);
    return route.abort();
  });
  const page = await context.newPage();
  page.on("pageerror", e => errors.push(String(e)));
  const fontRequests = [];
  page.on("request", r => { if (r.url().includes("/fonts/")) fontRequests.push(r.url()); });
  await page.goto(LOCAL + path, { waitUntil: "load" });
  await page.evaluate(() => document.fonts.ready);
  const client = await context.newCDPSession(page);
  await client.send("DOM.enable");
  await client.send("CSS.enable");
  const found = [];
  for (const selector of selectors) found.push(await fontsOf(page, client, selector));
  const sideways = await page.evaluate(() => ({
    scrollWidth: document.documentElement.scrollWidth, innerWidth: window.innerWidth,
    bodyScrollWidth: document.body.scrollWidth }));
  const loaded = await page.evaluate(() =>
    [...document.fonts].filter(f => f.family.replace(/["']/g, "") === "Space Grotesk")
      .map(f => f.status));
  await context.close();
  return { path, found, outside, errors, sideways, loaded, fontRequests };
}

(async () => {
  const browser = await chromium.launch();
  const out = {};
  out.index = await look(browser, "/", [".wordmark", "#home h1"]);
  out.corrections = await look(browser, "/corrections", [".wordmark", "h1"]);
  await browser.close();
  console.log(JSON.stringify(out));
})().catch(problem => { console.error(problem); process.exit(1); });
"""


def _free_port():
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


@pytest.fixture(scope="module")
def seen(tmp_path_factory):
    node = shutil.which("node")
    if not node or subprocess.run(
            [node, "-e", "require('playwright')"], capture_output=True).returncode:
        pytest.skip("needs node with playwright to open a real browser")
    fc_list = shutil.which("fc-list")
    if fc_list:
        installed = subprocess.run([fc_list], capture_output=True, text=True).stdout
        assert "space grotesk" not in installed.lower(), \
            "this machine has Space Grotesk installed, so the test proves nothing"

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
                [node, "-e", BROWSER_SCRIPT, f"http://127.0.0.1:{port}",
                 json.dumps(sorted(ALLOWED_OUTSIDE))],
                capture_output=True, text=True, timeout=240, cwd=str(ROOT))
        finally:
            server.should_exit = True
            thread.join(timeout=10)
    monkeypatch.undo()
    for forget in (explain.forget_everything, translate.forget_everything,
                   cache.forget_memory, fetch.forget_version):
        forget()
    assert run.returncode == 0, run.stderr[-4000:]
    return json.loads(run.stdout)


@pytest.mark.parametrize("name", ["index", "corrections"])
def test_browser_the_wordmark_and_a_heading_are_drawn_in_space_grotesk(seen, name):
    page = seen[name]
    assert page["errors"] == []
    assert page["loaded"] == ["loaded"]
    assert page["fontRequests"] and set(page["fontRequests"]) == {
        page["fontRequests"][0]}
    for item in page["found"]:
        assert not item.get("missing"), item
        assert item["shown"], item
        assert item["fonts"], item
        # The file is one variable font; Chromium names it after the file's
        # default step ("Space Grotesk Light") whatever weight is drawn.
        assert all(f["familyName"].startswith("Space Grotesk") for f in item["fonts"]), item
        assert all(f["postScriptName"].startswith("SpaceGrotesk") for f in item["fonts"]), item
        assert all(f["isCustomFont"] for f in item["fonts"]), item


@pytest.mark.parametrize("name", ["index", "corrections"])
def test_browser_the_page_asks_no_other_host(seen, name):
    outside = set(seen[name]["outside"])
    assert outside <= ALLOWED_OUTSIDE, outside
    assert not [host for host in outside if "google" in host or "gstatic" in host]


@pytest.mark.parametrize("name", ["index", "corrections"])
def test_browser_no_sideways_scroll_at_390_pixels(seen, name):
    sideways = seen[name]["sideways"]
    assert sideways["innerWidth"] == 390
    assert sideways["scrollWidth"] <= 390, sideways
    assert sideways["bodyScrollWidth"] <= 390, sideways
