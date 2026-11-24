"""Ticket 2.37. Tidy the "Tap to open" line on the folded boxes.

On a phone, a folded box's label often wraps, and "· Tap to open" landed
on its own line with a stray dot in front. Now, on all six folded boxes,
the same way on each:

- "Tap to open" / "Tap to close" always sits on its own line under the
  label, with no dot in front, in the same muted style as before.
- The count in brackets stays at the end of the label.
- The words "Tap to open" and "Tap to close" do not change.
- Nothing else about a box changes: order, cards, folding, which box
  opens by itself.

Page only: web/index.html, markup and CSS. No engine, API or wording change.

The ticket's example: Huntington disease at 390 wide, Approved tab. The
wider-group box and the red-warning box each show the label, then "Tap to
open" on the next line with no dot. At 1200 wide they look the same way.

One answer given on 24 Nov, before the code. The dot was part of the name
a screen reader gets for a box ("Approved for a wider group (4) · Tap to
open"). The ticket said to stop if that text would change. The answer:
remove the dot everywhere. The name loses the dot and nothing else.

Saved answers only (the Huntington page of ticket 2.27's tests). Two of
the six boxes are not on that page, so one more answer is cut from it by
hand to show all six. No network.
"""

import copy
import json
import pathlib
import shutil
import subprocess

import pytest

import test_wrong_approvals_box as huntington_page

ROOT = pathlib.Path(__file__).resolve().parent.parent
PAGE_FILE = ROOT / "web" / "index.html"
PAGE = PAGE_FILE.read_text(encoding="utf-8")
STYLES = PAGE[PAGE.index("<style>"):PAGE.index("</style>")]

DOT = "·"
TAP_OPEN, TAP_CLOSE = "Tap to open", "Tap to close"
MUTED = "rgb(86, 104, 119)"  # the page's --muted, #566877: the colour the words had before
NAVY_WEIGHT, TAP_WEIGHT = "700", "500"  # the label is bold, the tap words are not: as before

# The six folded boxes: id, the tab it is on, and its label, word for word.
BOXES = [
    ("narrower-box", "approved", "Approved for a narrower disease"),
    ("wider-box", "approved", "Approved for a wider group"),
    ("wrong-box", "approved",
     "The database lists these as approved for this disease. They look like mistakes."),
    ("more-trials-box", "trials",
     "More medicines in trials for this disease. They do not act on one of the 25 proteins."),
    ("new-trials-box", "trials",
     "New medicines being tested for this disease. The database records no approval for "
     "them for any disease."),
    ("opposite-box", "clues",
     "These push the opposite way to the approved medicines for this disease."),
]
BOX_IDS = [box_id for box_id, _, _ in BOXES]
COUNT_IDS = {"narrower-box": "narrower-count", "wider-box": "wider-count",
             "wrong-box": "wrong-count", "more-trials-box": "more-trials-count",
             "new-trials-box": "new-trials-count", "opposite-box": "opposite-count"}
# How many cards each box holds: on the Huntington page, and on the page cut to show all six.
HUNTINGTON_COUNTS = {"wider-box": 4, "wrong-box": 4, "more-trials-box": 23, "new-trials-box": 18}
ALL_SIX_COUNTS = dict(HUNTINGTON_COUNTS, **{"narrower-box": 2, "opposite-box": 3})
WIDTHS = (390, 1200)


# ---- the page, read as text ----

def test_no_dot_is_drawn_in_front_of_the_tap_words():
    assert '[data-part="tap"]::before' not in STYLES
    assert f'content:"{DOT}"' not in STYLES
    assert f"{DOT} Tap to" not in PAGE


def test_the_cut_that_hid_the_dot_is_gone_with_the_dot():
    # It was only there to cut the dot off a dropped line (ticket 4.1).
    assert "clip-path" not in STYLES
    assert "#narrower-box summary" not in STYLES and "#wider-box summary" not in STYLES


def test_one_rule_puts_the_tap_words_on_their_own_line_for_every_box():
    assert ('.wider-box summary [data-part="tap"]{display:block;font-weight:500;'
            'color:var(--muted);white-space:nowrap}') in STYLES
    assert STYLES.count('[data-part="tap"]') == 1  # one rule, the same for all six
    for box_id in BOX_IDS:
        assert f'<details class="wider-box" id="{box_id}" hidden>' in PAGE


def test_the_markup_of_each_box_title_is_unchanged():
    for box_id, _, label in BOXES:
        start = PAGE.index(f'<details class="wider-box" id="{box_id}"')
        summary = PAGE[PAGE.index("<summary>", start):PAGE.index("</summary>", start)]
        assert summary == (f'<summary>{label} (<span id="{COUNT_IDS[box_id]}"></span>) '
                           f'<span data-part="tap">{TAP_OPEN}</span>')


def test_the_words_tap_to_open_and_tap_to_close_do_not_change():
    assert PAGE.count(f'<span data-part="tap">{TAP_OPEN}</span>') == 7  # 7 since ticket 2.42
    assert 'part(box, "tap").textContent = box.open ? "Tap to close" : "Tap to open";' in PAGE


# ---- the page, in a real browser, at phone width and at 1200 wide ----

BROWSER_SCRIPT = r"""
"use strict";
const fs = require("fs");
const { chromium } = require("playwright");
const PAGE = fs.readFileSync(process.argv[1], "utf-8");
const ANSWERS = JSON.parse(fs.readFileSync(process.argv[2], "utf-8"));
const BOXES = JSON.parse(process.argv[3]);  // [[box id, tab], ...]
const WIDTHS = JSON.parse(process.argv[4]);
const SITE = "http://moonlight.test";

function readBox(boxId) {
  const box = document.getElementById(boxId);
  const summary = box.querySelector("summary");
  const tap = summary.querySelector('[data-part="tap"]');
  const count = summary.querySelector("span[id$='-count']");
  const shown = box.getClientRects().length > 0;
  const style = getComputedStyle(tap), before = getComputedStyle(tap, "::before");
  const range = document.createRange();
  range.selectNodeContents(tap);
  const tapLines = [...range.getClientRects()], countRect = count.getBoundingClientRect();
  // The label's words: every text piece of the summary that is not the tap words.
  const labelRange = document.createRange();
  labelRange.setStartBefore(summary.firstChild);
  labelRange.setEndBefore(tap);
  const labelLines = [...labelRange.getClientRects()].filter(rect => rect.width > 0);
  const labelBottom = Math.max(...labelLines.map(rect => rect.bottom));
  const labelLeft = Math.min(...labelLines.map(rect => rect.left));
  const inside = summary.getBoundingClientRect();
  return {
    shown,
    open: box.open,
    cards: box.querySelectorAll(".card").length,
    text: summary.innerText,                     // with its line breaks
    tapWords: tap.textContent,
    tapLines: tapLines.length,
    tapTop: tapLines.length ? tapLines[0].top : null,
    tapLeft: tapLines.length ? tapLines[0].left : null,
    tapRight: tapLines.length ? tapLines[0].right : null,
    labelBottom, labelLeft,
    labelLineCount: new Set(labelLines.map(rect => Math.round(rect.top))).size,
    countBottom: countRect.bottom,
    countIsOnTheLabelsLastLine: Math.abs(countRect.bottom - labelBottom) < 4,
    summaryLeft: inside.left, summaryRight: inside.right,
    display: style.display, color: style.color, weight: style.fontWeight,
    size: style.fontSize, labelWeight: getComputedStyle(summary).fontWeight,
    labelSize: getComputedStyle(summary).fontSize,
    before: before.content,                      // "none" when nothing is drawn in front
    clip: getComputedStyle(summary).clipPath,
    marginLeft: getComputedStyle(summary).marginLeft,
    sideways: document.documentElement.scrollWidth > document.documentElement.clientWidth,
  };
}

// The name the browser hands a screen reader for the box's title (its summary).
async function spokenName(context, page, boxId) {
  const client = await context.newCDPSession(page);
  const { root } = await client.send("DOM.getDocument");
  const { nodeId } = await client.send(
    "DOM.querySelector", { nodeId: root.nodeId, selector: "#" + boxId + " summary" });
  const { nodes } = await client.send(
    "Accessibility.getPartialAXTree", { nodeId, fetchRelatives: false });
  await client.detach();
  return nodes[0].name.value;
}

async function oneSearch(browser, answer, width) {
  const context = await browser.newContext({ viewport: { width, height: 900 } });
  const page = await context.newPage();
  const errors = [];
  page.on("pageerror", problem => errors.push(String(problem)));
  await context.route("**/*", route => {
    const url = route.request().url();
    if (url === SITE + "/" || url.startsWith(SITE + "/?"))
      return route.fulfill({ contentType: "text/html; charset=utf-8", body: PAGE });
    if (url.startsWith(SITE + "/api/clues?"))
      return route.fulfill({ contentType: "application/json", body: JSON.stringify(answer) });
    if (url.startsWith(SITE + "/api/explain?"))
      return route.fulfill({ status: 404, contentType: "application/json", body: "{}" });
    return route.abort();
  });
  await page.goto(SITE + "/?disease=MONDO_TEST");
  await page.waitForSelector("#found", { state: "visible" });
  await page.waitForTimeout(300);
  const out = { errors, closed: {}, spoken: {}, tapped: {}, spokenTapped: {}, tappedAgain: {} };
  for (const [boxId, tab] of BOXES) {
    await page.click("#tab-" + tab);
    await page.waitForTimeout(100);
    out.closed[boxId] = await page.evaluate(readBox, boxId);
    if (!out.closed[boxId].shown) continue;
    // What a screen reader is told for the box's title.
    out.spoken[boxId] = await spokenName(context, page, boxId);
    await page.click("#" + boxId + " summary");
    await page.waitForTimeout(300);  // the box tells the page it was opened a moment later
    out.tapped[boxId] = await page.evaluate(readBox, boxId);
    out.spokenTapped[boxId] = await spokenName(context, page, boxId);
    await page.click("#" + boxId + " summary");
    await page.waitForTimeout(300);
    out.tappedAgain[boxId] = await page.evaluate(readBox, boxId);
  }
  await context.close();
  return out;
}

(async () => {
  const browser = await chromium.launch();
  const out = {};
  for (const name of Object.keys(ANSWERS)) {
    out[name] = {};
    for (const width of WIDTHS) out[name][width] = await oneSearch(browser, ANSWERS[name], width);
  }
  await browser.close();
  console.log(JSON.stringify(out));
})().catch(problem => { console.error(problem); process.exit(1); });
"""


@pytest.fixture(scope="module")
def answers():
    """Huntington disease as /api/clues sends it from the saved answers, and
    the same page cut by hand so that all six boxes hold something."""
    huntington = huntington_page.page_answer(
        huntington_page.HUNTINGTON, huntington_page.huntington_files.saved_post_json)
    assert "narrower" not in huntington and "opposite_way_box" not in huntington
    all_six = copy.deepcopy(huntington)
    all_six["narrower"] = copy.deepcopy(huntington["wider_group"][:2])  # two cards to fill the box
    all_six["opposite_way_box"] = [clue["id"] for clue in huntington["new_clues"][:3]]
    return {"huntington": huntington, "all_six": all_six}


@pytest.fixture(scope="module")
def seen(answers, tmp_path_factory):
    """Opens each answer at each width and returns what a reader sees."""
    node = shutil.which("node")
    if not node or subprocess.run(
            [node, "-e", "require('playwright')"], capture_output=True).returncode:
        pytest.skip("needs node with playwright to open a real browser")
    answers_file = tmp_path_factory.mktemp("tap_line_tidy") / "answers.json"
    answers_file.write_text(json.dumps(answers), encoding="utf-8")
    run = subprocess.run(
        [node, "-e", BROWSER_SCRIPT, str(PAGE_FILE), str(answers_file),
         json.dumps([[box_id, tab] for box_id, tab, _ in BOXES]), json.dumps(list(WIDTHS))],
        capture_output=True, text=True, timeout=300, cwd=str(ROOT))
    assert run.returncode == 0, run.stderr[-3000:]
    out = json.loads(run.stdout)
    for name in answers:
        for width in WIDTHS:
            assert out[name][str(width)]["errors"] == [], (name, width)
    return out


def label_of(box_id):
    return {known: label for known, _, label in BOXES}[box_id]


def every_shown_box(seen, state="closed"):
    """(page, width, box id, what was read) for every box a reader can see."""
    for name, counts in (("huntington", HUNTINGTON_COUNTS), ("all_six", ALL_SIX_COUNTS)):
        for width in WIDTHS:
            read = seen[name][str(width)][state]
            assert sorted(box_id for box_id in BOX_IDS if read.get(box_id, {}).get("shown")) \
                == sorted(counts), (name, width)
            for box_id in counts:
                yield name, width, box_id, read[box_id]


@pytest.mark.parametrize("width", WIDTHS)
def test_example_huntington_the_two_approved_boxes_read_label_then_tap_to_open(seen, width):
    closed = seen["huntington"][str(width)]["closed"]
    assert closed["wider-box"]["text"] == "Approved for a wider group (4)\nTap to open"
    assert closed["wrong-box"]["text"] == (
        "The database lists these as approved for this disease. They look like mistakes. (4)"
        "\nTap to open")
    for box_id in ("wider-box", "wrong-box"):
        assert DOT not in closed[box_id]["text"]
        assert closed[box_id]["before"] == "none"
        assert closed[box_id]["open"] is False


def test_all_six_boxes_are_shown_on_the_page_cut_to_show_them(seen):
    for width in WIDTHS:
        closed = seen["all_six"][str(width)]["closed"]
        assert [box_id for box_id in BOX_IDS if closed[box_id]["shown"]] == BOX_IDS


def test_every_box_ends_with_its_count_then_tap_to_open_on_the_next_line(seen):
    counts = {"huntington": HUNTINGTON_COUNTS, "all_six": ALL_SIX_COUNTS}
    for name, width, box_id, read in every_shown_box(seen):
        number = counts[name][box_id]
        assert read["cards"] == number
        assert read["text"] == f"{label_of(box_id)} ({number})\n{TAP_OPEN}", (name, width, box_id)


def test_no_box_has_a_dot_anywhere_in_its_title(seen):
    for state in ("closed", "tapped"):
        for name, width, box_id, read in every_shown_box(seen, state):
            assert DOT not in read["text"], (name, width, box_id, state)
            assert read["before"] == "none", (name, width, box_id, state)


def test_the_tap_words_are_always_on_a_line_of_their_own_under_the_label(seen):
    for state in ("closed", "tapped"):
        for name, width, box_id, read in every_shown_box(seen, state):
            where = (name, width, box_id, state)
            assert read["display"] == "block", where
            assert read["tapLines"] == 1, where  # the words themselves never wrap
            assert read["tapTop"] >= read["labelBottom"] - 1, where  # under the label's last line


def test_at_1200_wide_a_short_label_still_has_the_tap_words_underneath(seen):
    # There is room for "Tap to open" beside the label. It goes under it all the same.
    read = seen["huntington"]["1200"]["closed"]["wider-box"]
    assert read["labelLineCount"] == 1
    assert read["tapTop"] >= read["labelBottom"] - 1
    long_one = seen["huntington"]["1200"]["closed"]["wrong-box"]
    assert long_one["labelLineCount"] == 1 and long_one["tapTop"] >= long_one["labelBottom"] - 1


def test_at_390_wide_a_long_label_wraps_and_the_tap_words_are_still_alone(seen):
    read = seen["huntington"]["390"]["closed"]["wrong-box"]
    assert read["labelLineCount"] >= 2
    assert read["tapTop"] >= read["labelBottom"] - 1 and read["tapLines"] == 1


def test_the_count_stays_at_the_end_of_the_label(seen):
    for name, width, box_id, read in every_shown_box(seen):
        assert read["countIsOnTheLabelsLastLine"] is True, (name, width, box_id)


def test_the_tap_words_start_at_the_left_edge_inside_the_box_and_stay_inside_it(seen):
    for name, width, box_id, read in every_shown_box(seen):
        where = (name, width, box_id)
        assert abs(read["tapLeft"] - read["summaryLeft"]) < 1, where
        assert read["tapRight"] <= read["summaryRight"] + 1, where
        assert read["sideways"] is False, where


def test_the_tap_words_keep_the_muted_style_they_had(seen):
    for state in ("closed", "tapped"):
        for name, width, box_id, read in every_shown_box(seen, state):
            where = (name, width, box_id, state)
            assert read["color"] == MUTED, where
            assert read["weight"] == TAP_WEIGHT and read["labelWeight"] == NAVY_WEIGHT, where
            assert read["size"] == read["labelSize"], where  # the same size as the label, as before


def test_every_box_looks_the_same_way_no_box_has_a_cut_or_a_shift_of_its_own(seen):
    for name, width, box_id, read in every_shown_box(seen):
        assert read["clip"] == "none" and read["marginLeft"] == "0px", (name, width, box_id)


def test_a_tap_changes_the_words_to_tap_to_close_and_back(seen):
    counts = {"huntington": HUNTINGTON_COUNTS, "all_six": ALL_SIX_COUNTS}
    for name, width, box_id, read in every_shown_box(seen, "tapped"):
        was_open = seen[name][str(width)]["closed"][box_id]["open"]
        words = TAP_OPEN if was_open else TAP_CLOSE
        assert read["open"] is not was_open
        assert read["text"] == f"{label_of(box_id)} ({counts[name][box_id]})\n{words}"
    for name, width, box_id, read in every_shown_box(seen, "tappedAgain"):
        first = seen[name][str(width)]["closed"][box_id]
        assert (read["open"], read["text"], read["cards"]) == (
            first["open"], first["text"], first["cards"]), (name, width, box_id)


def test_folding_is_unchanged_every_box_opens_folded_on_these_pages(seen):
    # Each tab's main list holds cards here, so no box opens by itself: as before.
    for name, width, box_id, read in every_shown_box(seen):
        assert read["open"] is False and read["tapWords"] == TAP_OPEN, (name, width, box_id)


def test_a_screen_reader_is_told_the_label_the_count_and_the_tap_words_without_the_dot(seen):
    counts = {"huntington": HUNTINGTON_COUNTS, "all_six": ALL_SIX_COUNTS}
    for name in counts:
        for width in WIDTHS:
            spoken = seen[name][str(width)]["spoken"]
            opened = seen[name][str(width)]["spokenTapped"]
            for box_id, number in counts[name].items():
                assert spoken[box_id] == (
                    f"{label_of(box_id)} ({number}) {TAP_OPEN}"), (name, width, box_id)
                assert opened[box_id] == (
                    f"{label_of(box_id)} ({number}) {TAP_CLOSE}"), (name, width, box_id)
