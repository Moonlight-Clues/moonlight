"""Ticket 3.33. The guide on a 390 px phone, and its Approved line.

Static checks read the page file. The browser checks open the real page in
Chromium (through node and playwright, like the other guide tests) with every
request except the page itself refused, so nothing touches the network.
"""

import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
PAGE_FILE = ROOT / "web" / "index.html"
PAGE = PAGE_FILE.read_text(encoding="utf-8")
GUIDE = PAGE[PAGE.index('<section id="guide"'):PAGE.index("<!-- end of the guide -->")]

APPROVED_LINE = "Approved for this disease. Newest approval first. Newer does not mean better."


# ---- the words: one change, and nothing else ----

def test_the_approved_line_in_the_guide_says_newest_first():
    assert "<h3>Approved</h3><p>%s</p>" % APPROVED_LINE in GUIDE
    assert "Listed A to Z" not in GUIDE


def test_the_approved_tabs_own_heading_on_the_disease_page_is_left_alone():
    outside = PAGE.replace(GUIDE, "")
    assert "Listed A to Z." in outside


# ---- the shape of the guide ----

def test_the_pretend_tab_bar_is_gone_from_the_guide():
    assert 'class="tabs"' not in GUIDE
    assert 'class="tab on"' not in GUIDE


def test_there_are_two_back_to_search_buttons_and_the_second_is_last():
    assert len(re.findall(r'<a class="ghost-btn"[^>]*data-guide-close[^>]*>Back to search</a>', GUIDE)) == 2
    assert re.search(r'(?s)<a [^>]*data-guide-close[^>]*>Back to search</a>\s*</section>\s*$', GUIDE)


def test_the_legend_sits_right_after_the_card_and_the_trial_picture_after_the_legend():
    card_part = GUIDE[GUIDE.index('id="guide-card"'):]
    places = [card_part.index(mark) for mark in (
        '<article class="card">', '<ul class="key">', '<div class="guide-trial">')]
    assert places == sorted(places)
    between = card_part[card_part.index("</article>"):card_part.index('<ul class="key">')]
    assert "guide-trial" not in between


# ---- in a real browser ----

BROWSER_SCRIPT = r"""
"use strict";
const fs = require("fs");
const { chromium } = require("playwright");
const PAGE = fs.readFileSync(process.argv[1], "utf-8");
const SITE = "http://moonlight.test";

async function measure(browser, width, height) {
  const context = await browser.newContext({ viewport: { width, height } });
  const page = await context.newPage();
  const errors = [];
  page.on("pageerror", problem => errors.push(String(problem)));
  await context.route("**/*", route => {
    const url = route.request().url();
    if (url === SITE + "/" || url.startsWith(SITE + "/?"))
      return route.fulfill({ contentType: "text/html; charset=utf-8", body: PAGE });
    return route.abort();
  });
  await page.goto(SITE + "/?guide=1");
  await page.waitForSelector("#guide", { state: "visible" });
  await page.waitForTimeout(300);
  const out = await page.evaluate(() => {
    const $ = (s, root = document) => root.querySelector(s);
    const $$ = (s, root = document) => [...root.querySelectorAll(s)];
    const box = el => { const r = el.getBoundingClientRect();
      return { top: r.top + scrollY, bottom: r.bottom + scrollY, left: r.left, right: r.right,
               width: r.width, height: r.height }; };
    const css = (el, p) => getComputedStyle(el)[p];
    const guide = $("#guide");
    const card = $("#guide-card .card"), key = $("#guide-card .key");
    const trial = $("#guide-card .guide-trial");
    const chain = $(".chain");
    const idea = $(".idea");
    const back = $$("[data-guide-close]");
    const mail = $(".idea.strip .contact a");
    const tops = els => els.map(e => Math.round(box(e).top));
    return {
      sideways: document.documentElement.scrollWidth > document.documentElement.clientWidth,
      guideHeight: box(guide).height,
      ideaHeight: box(idea).height,
      chainColumns: css(chain, "gridTemplateColumns").split(" ").length,
      chainGap: css(chain, "columnGap"),
      chainTops: tops($$(".chain>div")),
      shapes: $$(".chain .shape").map(s => [css(s, "width"), css(s, "height")]),
      names: [css($(".chain strong"), "fontSize"), css($(".chain strong"), "fontWeight")],
      caption: css($(".chain span"), "fontSize"),
      arrow: [css($(".chain .arrow"), "fontSize"), css($(".chain .arrow"), "color")],
      ideaPad: css(idea, "padding"), ideaGap: css(idea, "rowGap"),
      backCount: back.length,
      backHeights: back.map(b => box(b).height),
      backLast: guide.lastElementChild === back[back.length - 1],
      backStyle: [css(back[0], "padding"), css(back[0], "borderRadius"), css(back[0], "fontSize"),
                  css(back[0], "fontWeight"), css(back[0], "color"), css(back[0], "backgroundColor")],
      mailHeight: box(mail).height,
      steps: { bg: css($(".steps"), "backgroundColor"), border: css($(".steps"), "borderTopWidth"),
               radius: css($(".steps"), "borderRadius"), pad: css($(".steps"), "padding"),
               tops: tops($$(".steps li")), lefts: $$(".steps li").map(l => Math.round(box(l).left)),
               divider: css($$(".steps li")[1], "borderTopWidth") + "/" + css($$(".steps li")[1], "borderLeftWidth"),
               rank: [css($(".steps .rank"), "width"), css($(".steps .rank"), "height"),
                      css($(".steps .rank"), "backgroundColor")] },
      tabs: { count: $$("#guide .tabs").length, bg: css($(".tab-notes"), "backgroundColor"),
              tops: tops($$(".tab-note")), lefts: $$(".tab-note").map(l => Math.round(box(l).left)) },
      legend: { bg: css(key, "backgroundColor"), columns: css(key, "gridTemplateColumns").split(" ").length,
                rows: $$("li", key).length, firstTop: box($("li", key)).top,
                letter: [css($(".k", key), "width"), css($(".k", key), "fontSize")],
                letterColor: css($(".k", key), "backgroundColor"), rowSize: css($("li", key), "fontSize"),
                left: box(key).left, width: box(key).width },
      card: { bottom: box(card).bottom, top: box(card).top, right: box(card).right, left: box(card).left,
              letter: [css($(".k", card), "width"), css($(".k", card), "fontSize")] },
      trialTop: box(trial).top, keyBottom: box(key).bottom, keyTop: box(key).top,
      type: { h1: css($("#guide .intro h1"), "fontSize"), h1w: css($("#guide .intro h1"), "fontWeight"),
              h2: css($("#guide-steps-title"), "fontSize"), h2w: css($("#guide-steps-title"), "fontWeight"),
              h2c: css($("#guide-steps-title"), "color"), h2m: css($("#guide-steps-title"), "marginBottom"),
              h3: css($(".steps h3"), "fontSize"), gap: css(guide, "rowGap") },
    };
  });
  out.errors = errors;
  await context.close();
  return out;
}

(async () => {
  const browser = await chromium.launch();
  const out = { 390: await measure(browser, 390, 844), 1280: await measure(browser, 1280, 800) };
  await browser.close();
  console.log(JSON.stringify(out));
})().catch(problem => { console.error(problem); process.exit(1); });
"""


@pytest.fixture(scope="module")
def seen():
    node = shutil.which("node")
    if not node or subprocess.run(
            [node, "-e", "require('playwright')"], capture_output=True).returncode:
        pytest.skip("needs node with playwright to open a real browser")
    run = subprocess.run([node, "-e", BROWSER_SCRIPT, str(PAGE_FILE)],
                         capture_output=True, text=True, timeout=240, cwd=str(ROOT))
    assert run.returncode == 0, run.stderr[-3000:]
    out = json.loads(run.stdout)
    for width in out.values():
        assert width["errors"] == []
    return out


def test_phone_checks_from_the_ticket(seen):
    p = seen["390"]
    assert not p["sideways"]
    assert p["backCount"] == 2 and p["backLast"]
    assert all(h >= 44 for h in p["backHeights"]), p["backHeights"]
    assert p["mailHeight"] >= 44
    assert p["ideaHeight"] < 300, p["ideaHeight"]
    assert p["guideHeight"] <= 3700, p["guideHeight"]


def test_phone_idea_strip_is_one_row_of_three_small_shapes(seen):
    p = seen["390"]
    assert p["chainColumns"] == 5 and p["chainGap"] == "4px"
    assert len(set(p["chainTops"])) == 1, p["chainTops"]
    assert p["shapes"] == [["40px", "40px"]] * 3
    assert p["names"] == ["15px", "700"] and p["caption"] == "12px"
    assert p["arrow"] == ["18px", "rgb(66, 157, 154)"]
    assert p["ideaPad"] == "22px 16px" and p["ideaGap"] == "18px"


def test_phone_steps_and_tabs_are_one_white_card_of_three_rows(seen):
    p = seen["390"]
    s = p["steps"]
    assert s["bg"] == "rgb(255, 255, 255)" and s["border"] == "1px" and s["radius"] == "14px"
    assert s["pad"] == "2px 16px"
    assert len(set(s["lefts"])) == 1 and s["tops"] == sorted(set(s["tops"]))
    assert s["divider"].startswith("1px")
    assert s["rank"] == ["30px", "30px", "rgb(231, 241, 239)"]
    t = p["tabs"]
    assert t["count"] == 0 and t["bg"] == "rgb(255, 255, 255)"
    assert len(set(t["lefts"])) == 1 and t["tops"] == sorted(set(t["tops"]))


def test_phone_the_legend_starts_within_20_px_of_the_bottom_of_the_card(seen):
    p = seen["390"]
    assert 0 <= p["legend"]["firstTop"] - p["card"]["bottom"] <= 20, (
        p["legend"]["firstTop"], p["card"]["bottom"])
    assert p["legend"]["columns"] == 1 and p["legend"]["rows"] == 10
    assert p["legend"]["bg"] == "rgb(255, 255, 255)"
    assert p["legend"]["letter"] == ["22px", "12px"] and p["card"]["letter"] == ["22px", "12px"]
    assert p["legend"]["letterColor"] == "rgb(233, 180, 91)" and p["legend"]["rowSize"] == "14px"
    assert p["trialTop"] > p["keyBottom"]


def test_desktop_steps_tabs_are_three_columns_and_the_legend_sits_beside_the_card(seen):
    d = seen["1280"]
    assert len(set(d["steps"]["tops"])) == 1 and len(set(d["steps"]["lefts"])) == 3
    assert len(set(d["tabs"]["tops"])) == 1 and len(set(d["tabs"]["lefts"])) == 3
    assert abs(d["legend"]["width"] - 280) <= 1
    assert abs(d["legend"]["left"] - d["card"]["right"] - 20) <= 1
    assert abs(d["legend"]["firstTop"] - d["card"]["top"]) < 30
    assert d["trialTop"] > max(d["keyBottom"], d["card"]["bottom"])
    assert not d["sideways"]


def test_type_and_spacing_values(seen):
    p, d = seen["390"]["type"], seen["1280"]["type"]
    assert (p["h1"], d["h1"]) == ("29px", "43px") and p["h1w"] == "650"
    assert p["h2"] == "23px" and p["h2w"] == "700" and p["h2c"] == "rgb(50, 127, 128)"
    assert p["h2m"] == "10px" and p["h3"] == "16px"
    assert p["gap"] == "28px" and d["gap"] == "28px"
