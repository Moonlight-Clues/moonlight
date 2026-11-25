"""Ticket 3.5. The Report link, its form and the gene line: design polish.

No new words. The page is opened in Chromium at phone size (390 x 844),
as tests/test_report_page.py does. The browser never reaches the network:
the page and the answer to /api/clues are handed to it, POST /api/report
is answered by the test, and every other request is stopped.

The answer is type 2 diabetes from saved files (fixtures/).

Set MOONLIGHT_SHOTS to a folder to also save the three phone pictures:
a closed card, an open form and a clue card with gene lines.
"""

import json
import os
import pathlib
import re
import shutil
import subprocess

import pytest

from test_gene_evidence import page_answer

ROOT = pathlib.Path(__file__).resolve().parent.parent
PAGE_FILE = ROOT / "web" / "index.html"
PAGE = PAGE_FILE.read_text(encoding="utf-8")
T2D = "MONDO_0005148"

HEADING = "What looks wrong?"
START = "Linked to this disease by:"
TEAL = "rgb(66, 157, 154)"   # --teal, the colour of "Source record"
NAVY = "rgb(16, 31, 49)"     # --navy, the card's dark text
MUTED = "rgb(86, 104, 119)"  # --muted, the grey
NAMES = {
    "genetic_association": "inherited gene changes",
    "somatic_mutation": "gene changes found in tumours",
    "animal_model": "studies in animals",
    "affected_pathway": "the body process the gene is part of",
    "rna_expression": "how active the gene is in the disease",
    "literature": "mentioned together in research papers",
}

BROWSER_SCRIPT = r"""
"use strict";
const fs = require("fs");
const { chromium } = require("playwright");
const PAGE = fs.readFileSync(process.argv[1], "utf-8");
const ANSWER = JSON.parse(fs.readFileSync(process.argv[2], "utf-8"));
const SHOTS = process.argv[3] || "";
const SITE = "http://moonlight.test";

const look = el => {
  const style = getComputedStyle(el), box = el.getBoundingClientRect();
  return { color: style.color, weight: style.fontWeight, size: style.fontSize,
           underline: style.textDecorationLine, width: box.width, height: box.height,
           marginTop: style.marginTop };
};

(async () => {
  const browser = await chromium.launch();
  const context = await browser.newContext({ viewport: { width: 390, height: 844 },
                                             deviceScaleFactor: SHOTS ? 2 : 1,
                                             isMobile: true, hasTouch: true });
  const page = await context.newPage();
  const errors = [], sent = [];
  page.on("pageerror", problem => errors.push(String(problem)));
  await context.route("**/*", route => {
    const request = route.request(), url = request.url();
    if (url === SITE + "/" || url.startsWith(SITE + "/?"))
      return route.fulfill({ contentType: "text/html; charset=utf-8", body: PAGE });
    if (url.startsWith(SITE + "/api/clues?"))
      return route.fulfill({ contentType: "application/json", body: JSON.stringify(ANSWER) });
    if (url.startsWith(SITE + "/api/explain?"))
      return route.fulfill({ status: 404, contentType: "application/json", body: "{}" });
    if (url === SITE + "/api/report" && request.method() === "POST") {
      sent.push(JSON.parse(request.postData()));
      return route.fulfill({ status: 200, contentType: "application/json", body: "{}" });
    }
    return route.abort();
  });
  await page.goto(SITE + "/?disease=" + ANSWER.disease.id);
  await page.waitForSelector("#found", { state: "visible" });
  await page.click("#tab-approved");
  const out = { errors, sent, ways: {} };

  const card = n => page.locator("#approved-cards > .card").nth(n);
  const state = async c => c.evaluate(el => {
    const panel = el.querySelector('[data-part="report-panel"]');
    const link = el.querySelector('[data-part="report-open"]');
    return {
      open: !!panel && !panel.hidden && panel.getClientRects().length > 0,
      expanded: link.getAttribute("aria-expanded"),
      linkShown: !link.hidden && link.getClientRects().length > 0,
      picked: panel ? [...panel.querySelectorAll('input[type="radio"]')].filter(r => r.checked).length : 0,
      note: panel ? panel.querySelector("textarea").value : "",
      sendDisabled: panel ? panel.querySelector('[data-part="report-send"]').disabled : true,
      focusOnLink: document.activeElement === link,
    };
  });

  // The link, closed, beside "Source record".
  const first = card(0);
  await first.scrollIntoViewIfNeeded();
  out.link = await first.locator('[data-part="report-open"]').evaluate(look);
  out.source = await first.locator('[data-slot="source"]').evaluate(look);
  out.closed = await state(first);
  if (SHOTS) await first.screenshot({ path: SHOTS + "/3.5-closed-card.png" });

  // Each way out: open, pick, write, then close that way, then open again to see it is clear.
  const ways = {
    toggle: async c => c.locator('[data-part="report-open"]').click(),
    close: async c => c.locator('[data-part="report-close"]').click(),
    escape: async () => page.keyboard.press("Escape"),
    cancel: async c => c.locator('[data-part="report-cancel"]').click(),
  };
  let n = 1;
  for (const [way, shut] of Object.entries(ways)) {
    const c = card(n++);
    await c.locator('[data-part="report-open"]').scrollIntoViewIfNeeded();
    await c.locator('[data-part="report-open"]').click();
    await c.locator("label.report-choice").nth(1).click();
    await c.locator("textarea").fill("A note.");
    if (way === "escape") await c.locator("textarea").focus();
    const whileOpen = await state(c);
    await shut(c);
    const after = await state(c);
    await c.locator('[data-part="report-open"]').click();
    const reopened = await state(c);
    await ways.toggle(c);
    out.ways[way] = { whileOpen, after, reopened };
  }

  // The open panel: the x, the heading, the note box.
  const open = card(n++);
  await open.locator('[data-part="report-open"]').scrollIntoViewIfNeeded();
  await open.locator('[data-part="report-open"]').click();
  await page.waitForTimeout(700);
  out.panel = await open.evaluate(el => {
    const panel = el.querySelector('[data-part="report-panel"]');
    const close = panel.querySelector('[data-part="report-close"]');
    const heading = panel.querySelector("legend");
    const first = panel.querySelector("label.report-choice");
    const note = panel.querySelector("textarea"), noteStyle = getComputedStyle(note);
    const p = panel.getBoundingClientRect(), x = close.getBoundingClientRect();
    const h = heading.getBoundingClientRect();
    return {
      close: { label: close.getAttribute("aria-label"), width: x.width, height: x.height,
               rightGap: p.right - x.right, topGap: x.top - p.top, leftHalf: x.left < p.left + p.width / 2,
               type: close.type },
      heading: { text: heading.textContent, visible: h.width > 0 && h.height > 0
                 && getComputedStyle(heading).visibility !== "hidden" && heading.checkVisibility(),
                 above: h.bottom <= first.getBoundingClientRect().top + 1,
                 size: getComputedStyle(heading).fontSize, clip: getComputedStyle(heading).clip },
      note: { inner: note.clientHeight - parseFloat(noteStyle.paddingTop) - parseFloat(noteStyle.paddingBottom),
              line: parseFloat(noteStyle.lineHeight), rows: note.rows },
      buttons: [...panel.querySelectorAll(".report-buttons button")].map(b => b.textContent.trim()),
    };
  });
  if (SHOTS) await open.screenshot({ path: SHOTS + "/3.5-open-form.png" });
  await ways.toggle(open);

  // Scrolling: a link at the very bottom of the screen opens a panel that is scrolled into view.
  const low = card(n++);
  await low.locator('[data-part="report-open"]').evaluate(el => {
    const box = el.getBoundingClientRect();
    window.scrollBy({ top: box.bottom - window.innerHeight + 2, behavior: "instant" });
  });
  await page.waitForTimeout(100);
  await low.locator('[data-part="report-open"]').click();
  await page.waitForTimeout(1200);
  out.lowPanel = await low.locator('[data-part="report-panel"]').evaluate(el => {
    const box = el.getBoundingClientRect();
    return { top: box.top, bottom: box.bottom, height: window.innerHeight };
  });
  await ways.toggle(low);

  // A panel that fits where it opens does not move the page.
  const mid = card(n++);
  await mid.locator('[data-part="report-open"]').evaluate(el => {
    const box = el.getBoundingClientRect();
    window.scrollBy({ top: box.top - 80, behavior: "instant" });
  });
  await page.waitForTimeout(100);
  const before = await page.evaluate(() => window.scrollY);
  await mid.locator('[data-part="report-open"]').click();
  await page.waitForTimeout(800);
  out.midMoved = (await page.evaluate(() => window.scrollY)) - before;
  await ways.toggle(mid);

  // Sending still sends the same fields, and thanks.
  const send = card(n++);
  await send.locator('[data-part="report-open"]').scrollIntoViewIfNeeded();
  await send.locator('[data-part="report-open"]').click();
  await send.locator("label.report-choice").first().click();
  await send.locator('[data-part="report-send"]').click();
  await send.locator('[data-part="report-thanks"]').waitFor({ state: "visible" });
  out.afterSend = await state(send);

  // The gene lines on the New clues cards.
  await page.click("#tab-clues");
  await page.waitForTimeout(300);
  out.genes = await page.evaluate(() =>
    [...document.querySelectorAll("#panel-clues .card")].map(card => ({
      name: card.querySelector('[data-slot="medicine-name"]').textContent,
      lines: [...card.querySelectorAll('[data-slot="protein-evidence"]')].map(line => {
        const parts = [...line.children];
        const style = el => ({ color: getComputedStyle(el).color, weight: getComputedStyle(el).fontWeight,
                               size: getComputedStyle(el).fontSize });
        return { text: line.textContent, marginTop: getComputedStyle(line).marginTop,
                 size: getComputedStyle(line).fontSize,
                 parts: parts.map(el => Object.assign({ text: el.textContent }, style(el))) };
      }),
    })));
  if (SHOTS) {
    const shown = page.locator("#panel-clues .card", { has: page.locator('[data-slot="protein-evidence"]') }).first();
    await shown.scrollIntoViewIfNeeded();
    await shown.screenshot({ path: SHOTS + "/3.5-clue-card-gene-lines.png" });
  }
  await browser.close();
  console.log(JSON.stringify(out));
})().catch(problem => { console.error(problem); process.exit(1); });
"""


@pytest.fixture(scope="module")
def answer():
    return page_answer(T2D)


@pytest.fixture(scope="module")
def seen(answer, tmp_path_factory):
    node = shutil.which("node")
    if not node or subprocess.run(
            [node, "-e", "require('playwright')"], capture_output=True).returncode:
        pytest.skip("needs node with playwright to open a real browser")
    answer_file = tmp_path_factory.mktemp("report_polish") / "answer.json"
    answer_file.write_text(json.dumps(answer), encoding="utf-8")
    run = subprocess.run(
        [node, "-e", BROWSER_SCRIPT, str(PAGE_FILE), str(answer_file),
         os.environ.get("MOONLIGHT_SHOTS", "")],
        capture_output=True, text=True, timeout=240, cwd=str(ROOT))
    assert run.returncode == 0, run.stderr[-3000:]
    out = json.loads(run.stdout)
    assert out["errors"] == []
    return out


# ---- Report link ----

def test_the_link_is_teal_like_source_record_regular_13px_underlined(seen):
    link, source = seen["link"], seen["source"]
    assert link["color"] == source["color"] == TEAL
    assert link["weight"] == "400"
    assert int(source["weight"]) > int(link["weight"])  # "Source record" stays the stronger link
    assert link["size"] == "13px"
    assert "underline" in link["underline"]


def test_the_link_is_at_least_44_by_44(seen):
    assert seen["link"]["width"] >= 44
    assert seen["link"]["height"] >= 44


def test_aria_expanded_follows_the_panel(seen):
    assert seen["closed"]["expanded"] == "false"
    for way, case in seen["ways"].items():
        assert case["whileOpen"]["open"] and case["whileOpen"]["expanded"] == "true", way
        assert not case["after"]["open"] and case["after"]["expanded"] == "false", way


def test_the_link_stays_visible_while_the_form_is_open(seen):
    for way, case in seen["ways"].items():
        assert case["whileOpen"]["linkShown"], way
        assert case["after"]["linkShown"], way


# ---- Ways out ----

@pytest.mark.parametrize("way", ["toggle", "close", "escape", "cancel"])
def test_each_way_out_closes_the_panel_and_clears_it(seen, way):
    case = seen["ways"][way]
    assert case["whileOpen"]["picked"] == 1 and case["whileOpen"]["note"] == "A note."
    assert case["after"]["open"] is False
    assert case["reopened"]["open"] is True
    assert case["reopened"]["picked"] == 0
    assert case["reopened"]["note"] == ""
    assert case["reopened"]["sendDisabled"] is True


@pytest.mark.parametrize("way", ["escape", "cancel", "close"])
def test_closing_puts_focus_back_on_the_link(seen, way):
    assert seen["ways"][way]["after"]["focusOnLink"] is True


def test_the_close_mark_is_top_right_44_by_44_and_named_close(seen):
    close = seen["panel"]["close"]
    assert close["label"] == "Close"
    assert close["type"] == "button"  # never sends the form
    assert close["width"] >= 44 and close["height"] >= 44
    assert not close["leftHalf"]
    assert 0 <= close["rightGap"] <= 12 and 0 <= close["topGap"] <= 12


def test_the_close_mark_has_no_words_of_its_own():
    template = PAGE[PAGE.index('<template id="report-template">'):]
    template = template[:template.index("</template>")]
    button = re.search(r'<button[^>]*data-part="report-close"[^>]*>(.*?)</button>', template, re.S)
    assert button, "no close mark in the panel"
    inner = re.sub(r"<[^>]+>", "", button.group(1)).strip()
    assert inner in ("", "×")  # only the x mark, which is hidden from screen readers or is the mark itself


# ---- Layout ----

def test_the_heading_is_visible_with_exactly_its_words_above_the_choices(seen):
    heading = seen["panel"]["heading"]
    assert heading["text"] == HEADING
    assert heading["visible"] and heading["above"]
    assert heading["size"] in ("12px", "13px")


def test_the_heading_is_written_once_in_the_page():
    assert PAGE.count(HEADING) == 1


def test_the_note_box_is_two_lines_tall(seen):
    note = seen["panel"]["note"]
    assert note["rows"] == 2
    assert abs(note["inner"] - 2 * note["line"]) <= 2


def test_the_buttons_are_still_send_and_cancel(seen):
    assert seen["panel"]["buttons"] == ["Send", "Cancel"]


def test_a_panel_opened_near_the_bottom_is_scrolled_into_view(seen):
    low = seen["lowPanel"]
    assert low["top"] >= 0 and low["bottom"] <= low["height"] + 1


def test_a_panel_already_in_view_does_not_move_the_page(seen):
    assert seen["midMoved"] == 0


def test_sending_still_sends_the_same_fields_and_thanks(seen):
    (body,) = seen["sent"]
    assert set(body) == {"disease_id", "medicine_id", "medicine_name", "tab", "box", "reason", "note", "website"}
    assert body["reason"] == "wrong_disease" and body["note"] == ""
    assert seen["afterSend"]["open"] is False


# ---- Gene line ----

def test_gene_lines_are_word_for_word_as_before(seen, answer):
    sent = {item["medicine"]: item for item in answer["new_clues"]}
    checked = 0
    for card in seen["genes"]:
        if card["name"] not in sent:
            continue
        want = ["Linked to this disease by: " + ", ".join(NAMES[k] for k in p["evidence"]) + "."
                for p in sent[card["name"]]["proteins"] if "evidence" in p]
        assert [line["text"] for line in card["lines"]] == want, card["name"]
        checked += len(want)
    assert checked > 0


def test_the_start_is_dark_600_and_the_names_muted(seen):
    lines = [line for card in seen["genes"] for line in card["lines"]]
    assert lines
    for line in lines:
        start, names = line["parts"]
        assert start["text"] == START
        assert line["text"] == start["text"] + names["text"]
        assert start["color"] == NAVY and start["weight"] == "600"
        assert names["color"] == MUTED and names["weight"] == "400"
        assert line["size"] == start["size"] == names["size"] == "13px"
        assert line["marginTop"] == "4px"
