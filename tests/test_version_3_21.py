"""Ticket 3.21. Which build is live: a fingerprint of what the image serves.

The fingerprint is a SHA-256 over every moonlight/*.json, moonlight/*.py and
web/index.html, in sorted path order, each fed as "<relative path>\\n<bytes>\\n".
FINGERPRINT is its first 12 hex characters. The tests build small copies of
the served files in a temporary folder, so no real file is touched.

The footer line is checked in a real browser (Chromium) at 390 px, as
tests/test_print_page.py does; the browser never reaches the network.
"""

import hashlib
import json
import pathlib
import re
import shutil
import subprocess
import sys

import pytest
from fastapi.testclient import TestClient

from moonlight import api, version

ROOT = pathlib.Path(__file__).resolve().parent.parent
PAGE_FILE = ROOT / "web" / "index.html"
SCRIPT = ROOT / "scripts" / "fingerprint.py"


@pytest.fixture
def tree(tmp_path):
    """A small pretend checkout holding served files and unserved ones."""
    for name, body in {
        "moonlight/a.py": b"A = 1\n",
        "moonlight/b.json": b'{"b": 1}\n',
        "moonlight/__init__.py": b"",
        "web/index.html": b"<html>page</html>\n",
        "tests/t.py": b"t\n",
        "docs/d.md": b"d\n",
        "fixtures/f.json": b"{}\n",
    }.items():
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(body)
    return tmp_path


def test_the_fingerprint_is_the_agreed_hash(tree):
    feed = hashlib.sha256()
    for rel in ["moonlight/__init__.py", "moonlight/a.py", "moonlight/b.json", "web/index.html"]:
        feed.update(rel.encode() + b"\n" + (tree / rel).read_bytes() + b"\n")
    assert version.fingerprint(tree) == feed.hexdigest()[:12]
    assert re.fullmatch(r"[0-9a-f]{12}", version.fingerprint(tree))


@pytest.mark.parametrize("rel", ["moonlight/a.py", "moonlight/b.json", "web/index.html"])
def test_one_changed_served_byte_changes_it(tree, rel):
    before = version.fingerprint(tree)
    with open(tree / rel, "ab") as handle:
        handle.write(b" ")
    assert version.fingerprint(tree) != before


@pytest.mark.parametrize("rel", ["tests/t.py", "docs/d.md", "fixtures/f.json", "tests/new.py"])
def test_unserved_files_do_not_change_it(tree, rel):
    before = version.fingerprint(tree)
    with open(tree / rel, "ab") as handle:
        handle.write(b"changed")
    assert version.fingerprint(tree) == before


def test_a_file_name_is_part_of_it(tree):
    before = version.fingerprint(tree)
    (tree / "moonlight" / "b.json").rename(tree / "moonlight" / "c.json")
    assert version.fingerprint(tree) != before


def test_import_time_value_is_the_real_checkout():
    assert version.FINGERPRINT == version.fingerprint(ROOT)


def test_the_script_prints_exactly_the_fingerprint():
    run = subprocess.run([sys.executable, str(SCRIPT)], capture_output=True, text=True,
                         cwd=str(ROOT))
    assert run.returncode == 0, run.stderr
    assert run.stdout == version.FINGERPRINT + "\n"


def test_the_script_does_not_copy_the_code():
    assert "sha256" not in SCRIPT.read_text(encoding="utf-8")


def test_api_version_has_two_keys_and_local_without_k_revision(monkeypatch):
    monkeypatch.delenv("K_REVISION", raising=False)
    assert version.read_revision() == "local"
    response = TestClient(api.app).get("/api/version")
    assert response.status_code == 200
    assert set(response.json()) == {"fingerprint", "revision"}
    assert response.json()["fingerprint"] == version.FINGERPRINT


def test_revision_is_read_from_k_revision(monkeypatch):
    monkeypatch.setenv("K_REVISION", "moonlight-00042-abc")
    assert version.read_revision() == "moonlight-00042-abc"


def test_the_route_answers_with_the_values_set_at_import(monkeypatch):
    monkeypatch.setattr(api.version, "FINGERPRINT", "0123456789ab")
    monkeypatch.setattr(api.version, "REVISION", "rev-1")
    assert TestClient(api.app).get("/api/version").json() == {
        "fingerprint": "0123456789ab", "revision": "rev-1"}


def test_the_dockerfile_copies_what_the_fingerprint_reads():
    docker = (ROOT / "Dockerfile").read_text(encoding="utf-8")
    assert "COPY moonlight/ moonlight/" in docker and "COPY web/ web/" in docker


# ---- the footer line, seen in a real browser ----

BROWSER_SCRIPT = r"""
"use strict";
const fs = require("fs");
const { chromium } = require("playwright");
const PAGE = fs.readFileSync(process.argv[1], "utf-8");
const ANSWER = JSON.parse(fs.readFileSync(process.argv[2], "utf-8"));
const SITE = "http://moonlight.test";
const box = el => { const r = el.getBoundingClientRect(); return { top: r.top, bottom: r.bottom, h: r.height, w: r.width }; };

async function run(browser, versionReply) {
  const context = await browser.newContext({ viewport: { width: 390, height: 844 } });
  const page = await context.newPage();
  const errors = [];
  page.on("pageerror", problem => errors.push(String(problem)));
  await page.addInitScript(() => { window.print = () => {}; });
  await context.route("**/*", route => {
    const url = route.request().url();
    if (url === SITE + "/" || url.startsWith(SITE + "/?"))
      return route.fulfill({ contentType: "text/html; charset=utf-8", body: PAGE });
    if (url === SITE + "/api/version")
      return versionReply === "fail" ? route.fulfill({ status: 500, body: "boom" })
        : route.fulfill({ contentType: "application/json", body: JSON.stringify(versionReply) });
    if (url.startsWith(SITE + "/api/clues?"))
      return route.fulfill({ contentType: "application/json", body: JSON.stringify(ANSWER) });
    return route.abort();
  });
  await page.goto(SITE + "/");
  await page.waitForTimeout(600);
  const out = await page.evaluate(() => {
    const el = document.getElementById("build-line");
    const note = document.querySelector(".footer-note");
    const r = x => { const b = x.getBoundingClientRect(); return { top: b.top, bottom: b.bottom, h: b.height }; };
    const cs = el ? getComputedStyle(el) : null;
    const ns = getComputedStyle(note);
    return { text: el ? el.textContent : null, size: cs && cs.fontSize, color: cs && cs.color,
             noteColor: ns.color, noteSize: ns.fontSize, noteMargin: ns.marginTop,
             noteBox: r(note), lineBox: el ? r(el) : null,
             lineAfterNote: el ? el.previousElementSibling === note : false,
             noteText: note.textContent,
             overflowX: document.documentElement.scrollWidth > window.innerWidth };
  });
  out.errors = errors;
  await context.close();
  return out;
}

(async () => {
  const browser = await chromium.launch();
  const result = { ok: await run(browser, { fingerprint: "abc123def456", revision: "local" }),
                   failed: await run(browser, "fail") };
  // the printed page: open a disease, press print, read what shows
  const context = await browser.newContext({ viewport: { width: 390, height: 844 } });
  const page = await context.newPage();
  await page.addInitScript(() => { window.print = () => {}; });
  await context.route("**/*", route => {
    const url = route.request().url();
    if (url === SITE + "/" || url.startsWith(SITE + "/?"))
      return route.fulfill({ contentType: "text/html; charset=utf-8", body: PAGE });
    if (url === SITE + "/api/version")
      return route.fulfill({ contentType: "application/json", body: JSON.stringify({ fingerprint: "abc123def456", revision: "local" }) });
    if (url.startsWith(SITE + "/api/clues?"))
      return route.fulfill({ contentType: "application/json", body: JSON.stringify(ANSWER) });
    return route.abort();
  });
  await page.goto(SITE + "/?disease=" + ANSWER.disease.id);
  await page.waitForSelector("#found", { state: "visible" });
  await page.click("#print-page");
  await page.waitForTimeout(300);
  result.printed = await page.evaluate(() => {
    const el = document.getElementById("build-line");
    return { registering: document.body.classList.contains("registering"),
             lineShown: !!el && el.getClientRects().length > 0,
             inRegister: !!el && !!el.closest("#register") };
  });
  await page.emulateMedia({ media: "print" });
  result.printed.printMediaShown = await page.evaluate(() => {
    const el = document.getElementById("build-line");
    return !!el && el.getClientRects().length > 0;
  });
  await browser.close();
  console.log(JSON.stringify(result));
})().catch(problem => { console.error(problem); process.exit(1); });
"""


@pytest.fixture(scope="module")
def seen(tmp_path_factory):
    node = shutil.which("node")
    if not node or subprocess.run(
            [node, "-e", "require('playwright')"], capture_output=True).returncode:
        pytest.skip("needs node with playwright to open a real browser")
    import old_flag_saved
    answer = old_flag_saved.page_answer("MONDO_0005148")
    answer_file = tmp_path_factory.mktemp("build") / "answer.json"
    answer_file.write_text(json.dumps(answer), encoding="utf-8")
    run = subprocess.run([node, "-e", BROWSER_SCRIPT, str(PAGE_FILE), str(answer_file)],
                         capture_output=True, text=True, timeout=240, cwd=str(ROOT))
    assert run.returncode == 0, run.stderr[-3000:]
    return json.loads(run.stdout)


def test_the_footer_line_shows_the_build(seen):
    ok = seen["ok"]
    assert ok["text"] == "Build abc123def456"
    assert ok["lineAfterNote"]
    assert ok["size"] == "11px"
    assert ok["color"] == ok["noteColor"]  # the same muted style as the footer note
    assert not ok["errors"]


def test_the_footer_note_is_unchanged_and_does_not_wrap_at_390(seen):
    ok = seen["ok"]
    # ticket T4 (MAIN 5's named OK): "and ClinicalTrials.gov" added
    assert ok["noteText"] == ("Moonlight · Research exploration only · Not clinical findings"
                              " · Data from Open Targets and ClinicalTrials.gov"
                              " · Corrections")  # ticket 2.66
    assert ok["noteBox"]["h"] == seen["failed"]["noteBox"]["h"]  # the new line does not change it
    assert ok["lineBox"]["top"] >= ok["noteBox"]["bottom"]
    assert ok["lineBox"]["h"] < 20  # one line
    assert not ok["overflowX"]


def test_if_the_call_fails_the_line_stays_empty_without_error_text(seen):
    failed = seen["failed"]
    assert failed["text"] == ""
    assert not failed["errors"]


def test_the_printed_page_does_not_show_it(seen):
    printed = seen["printed"]
    assert printed["registering"]
    assert not printed["lineShown"] and not printed["inRegister"]
    assert not printed["printMediaShown"]
