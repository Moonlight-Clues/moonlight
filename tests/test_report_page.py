"""Ticket 3.3. The "Report" link on every card, seen in a real browser.

The page is opened in Chromium at phone size (390 x 844), as
tests/test_print_page.py does. The browser never reaches the network:
the page and the answer to /api/clues are handed to it, POST /api/report
is answered by the test (200, or 503 to see the failure words), and every
other request is stopped.

The answer is type 2 diabetes from saved files (fixtures/), which has a
card of every kind but one: the main Approved list, the wider-group box,
the no-regulator box, the red box, In trials and its two boxes, new clues
and the opposite-way box. No saved disease has a narrower box, so its two
cards are copies of the first two wider-group cards with new ids.

Set MOONLIGHT_SHOTS to a folder to also save the two phone pictures.
"""

import json
import os
import pathlib
import shutil
import subprocess

import pytest

import old_flag_saved

ROOT = pathlib.Path(__file__).resolve().parent.parent
PAGE_FILE = ROOT / "web" / "index.html"
T2D = "MONDO_0005148"

PRIVACY = "No names or health details, please. We store nothing about you."
THANKS = "Thank you. We read every report."
FAILED = "Couldn't send. Please try again later."
CHOICES = ["Wrong disease", "Not approved", "Wrong link", "Something else"]

# Each pile of cards on the page: its holder, its tab and box, and where its cards come from.
PILES = [
    ("approved-cards", "approved", None),
    ("narrower-cards", "approved", "narrower"),
    ("wider-cards", "approved", "wider"),
    ("no-regulator-cards", "approved", "no_regulator"),
    ("wrong-cards", "approved", "wrong"),
    ("studied-cards", "trials", None),
    ("more-trials-cards", "trials", "more_in_trials"),
    ("new-trials-cards", "trials", "new_in_trials"),
    ("new-cards", "clues", None),
    ("opposite-cards", "clues", "opposite_way"),
]


def the_answer():
    answer = old_flag_saved.page_answer(T2D)
    narrower = []
    for place, medicine in enumerate(answer["wider_group"][:2]):
        copy = dict(medicine, id="NARROWER_%d" % place)
        narrower.append(copy)
    answer["narrower"] = narrower
    return answer


BROWSER_SCRIPT = r"""
"use strict";
const fs = require("fs");
const { chromium } = require("playwright");
const PAGE = fs.readFileSync(process.argv[1], "utf-8");
const ANSWER = JSON.parse(fs.readFileSync(process.argv[2], "utf-8"));
const PILES = JSON.parse(process.argv[3]);
const SHOTS = process.argv[4] || "";
const SITE = "http://moonlight.test";

(async () => {
  const browser = await chromium.launch();
  const context = await browser.newContext({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2,
                                             isMobile: true, hasTouch: true });
  const page = await context.newPage();
  const errors = [], dialogs = [], sent = [];
  let reply = 200;
  page.on("pageerror", problem => errors.push(String(problem)));
  page.on("dialog", dialog => { dialogs.push(dialog.type()); dialog.dismiss(); });
  await page.addInitScript(() => { window.print = () => {}; });
  await context.route("**/*", route => {
    const request = route.request(), url = request.url();
    if (url === SITE + "/" || url.startsWith(SITE + "/?"))
      return route.fulfill({ contentType: "text/html; charset=utf-8", body: PAGE });
    if (url.startsWith(SITE + "/api/clues?"))
      return route.fulfill({ contentType: "application/json", body: JSON.stringify(ANSWER) });
    if (url === SITE + "/api/report" && request.method() === "POST") {
      sent.push({ body: JSON.parse(request.postData()), type: request.headers()["content-type"] });
      return route.fulfill({ status: reply, contentType: "application/json", body: "{}" });
    }
    return route.abort();
  });
  await page.goto(SITE + "/?disease=" + ANSWER.disease.id);
  await page.waitForSelector("#found", { state: "visible" });

  // Every card of every pile: how many Report links it has.
  const piles = await page.evaluate(PILES => PILES.map(([holder]) => {
    const cards = [...document.getElementById(holder).querySelectorAll(":scope > .card")];
    return { holder, cards: cards.length,
             links: cards.map(card => [...card.querySelectorAll("button, a")]
                                     .filter(el => el.textContent.trim() === "Report").length) };
  }), PILES);

  const out = { piles, errors, dialogs, sent, cases: {} };

  // Open each pile's box (if it is in one), go to its tab, tap its first card's Report, send.
  for (const [holder, tab, box] of PILES) {
    await page.evaluate(([holder, tab]) => {
      document.querySelector('.tab[data-tab="' + tab + '"]').click();
      const details = document.getElementById(holder).closest("details");
      if (details) details.open = true;
    }, [holder, tab]);
    const card = page.locator("#" + holder + " > .card").first();
    const link = card.locator('[data-part="report-open"]');
    const before = sent.length;
    await link.scrollIntoViewIfNeeded();
    await link.click();
    const panel = card.locator('[data-part="report-panel"]');
    const seen = await panel.evaluate(el => ({
      visible: !el.hidden && el.getClientRects().length > 0,
      choices: [...el.querySelectorAll("label.report-choice")].map(l => l.textContent.trim()),
      sendDisabledBeforeChoice: el.querySelector('[data-part="report-send"]').disabled,
      privacy: el.querySelector('[data-part="report-privacy"]').textContent.trim(),
      placeholder: el.querySelector("textarea").placeholder,
      maxLength: el.querySelector("textarea").maxLength,
      buttons: [...el.querySelectorAll("button")].map(b => b.textContent.trim()),
      inCard: !!el.closest(".card"),
    }));
    await card.locator("label.report-choice").nth(2).click();
    await card.locator("textarea").fill("Link goes to the wrong trial.");
    out.cases[holder] = { seen, medicineName: await card.locator("h3").first().textContent() };
    if (holder === "wrong-cards" && SHOTS) {
      await card.scrollIntoViewIfNeeded();
      await card.screenshot({ path: SHOTS + "/report-panel-open.png" });
    }
    await card.locator('[data-part="report-send"]').click();
    await card.locator('[data-part="report-thanks"]').waitFor({ state: "visible" });
    out.cases[holder].thanks = (await card.locator('[data-part="report-thanks"]').textContent()).trim();
    out.cases[holder].panelGone = await panel.evaluate(el => el.hidden || el.getClientRects().length === 0);
    out.cases[holder].linkGone = await link.evaluate(el => el.hidden || el.getClientRects().length === 0);
    out.cases[holder].body = sent.length > before ? sent[sent.length - 1] : null;
    if (holder === "wrong-cards" && SHOTS) await card.screenshot({ path: SHOTS + "/report-thank-you.png" });
  }

  // Tap sizes and Cancel, on a fresh card of the main Approved list.
  await page.evaluate(() => document.querySelector('.tab[data-tab="approved"]').click());
  const second = page.locator("#approved-cards > .card").nth(1);
  await second.locator('[data-part="report-open"]').click();
  out.heights = await second.evaluate(card => {
    const tall = el => Math.round(el.getBoundingClientRect().height);
    return {
      link: tall(card.querySelector('[data-part="report-open"]')),
      choices: [...card.querySelectorAll("label.report-choice")].map(tall),
      buttons: [...card.querySelector('[data-part="report-panel"]').querySelectorAll("button")].map(tall),
    };
  });
  // The link's height while closed is measured on a third card.
  out.closedLink = await page.locator("#approved-cards > .card").nth(2).locator('[data-part="report-open"]')
    .evaluate(el => Math.round(el.getBoundingClientRect().height));
  await second.locator('[data-part="report-cancel"]').click();
  out.afterCancel = await second.evaluate(card => ({
    panelHidden: card.querySelector('[data-part="report-panel"]').hidden,
    linkShown: !card.querySelector('[data-part="report-open"]').hidden,
  }));

  // A failure: the API says 503.
  reply = 503;
  const third = page.locator("#approved-cards > .card").nth(3);
  await third.locator('[data-part="report-open"]').click();
  await third.locator("label.report-choice").first().click();
  await third.locator('[data-part="report-send"]').click();
  await third.locator('[data-part="report-problem"]').waitFor({ state: "visible" });
  out.failure = {
    words: (await third.locator('[data-part="report-problem"]').textContent()).trim(),
    thanksShown: await third.locator('[data-part="report-thanks"]').evaluate(el => !el.hidden),
    body: sent[sent.length - 1].body,
  };

  // The print page: the register holds no Report, and on paper the cards show none.
  await page.click("#print-page");
  await page.waitForTimeout(200);
  out.registerReports = await page.evaluate(() =>
    [...document.querySelectorAll("#register *")].filter(el => el.children.length === 0
      && el.textContent.trim() === "Report").length);
  await page.click("#register-back");
  await page.emulateMedia({ media: "print" });
  out.printedReports = await page.evaluate(() =>
    [...document.querySelectorAll(".card .report-row")].filter(el => getComputedStyle(el).display !== "none").length);
  out.dialogs = dialogs;
  await browser.close();
  console.log(JSON.stringify(out));
})().catch(problem => { console.error(problem); process.exit(1); });
"""


@pytest.fixture(scope="module")
def answer():
    return the_answer()


@pytest.fixture(scope="module")
def seen(answer, tmp_path_factory):
    node = shutil.which("node")
    if not node or subprocess.run(
            [node, "-e", "require('playwright')"], capture_output=True).returncode:
        pytest.skip("needs node with playwright to open a real browser")
    answer_file = tmp_path_factory.mktemp("report") / "answer.json"
    answer_file.write_text(json.dumps(answer), encoding="utf-8")
    run = subprocess.run(
        [node, "-e", BROWSER_SCRIPT, str(PAGE_FILE), str(answer_file), json.dumps(PILES),
         os.environ.get("MOONLIGHT_SHOTS", "")],
        capture_output=True, text=True, timeout=240, cwd=str(ROOT))
    assert run.returncode == 0, run.stderr[-3000:]
    return json.loads(run.stdout)


def test_the_page_draws_without_an_error_or_a_dialog(seen):
    assert seen["errors"] == []
    assert seen["dialogs"] == []


@pytest.mark.parametrize("holder", [pile[0] for pile in PILES])
def test_every_card_of_every_kind_has_one_report_link(seen, holder):
    pile = next(p for p in seen["piles"] if p["holder"] == holder)
    assert pile["cards"] > 0
    assert pile["links"] == [1] * pile["cards"]


def test_the_number_of_cards_is_the_answers(seen, answer):
    count = {p["holder"]: p["cards"] for p in seen["piles"]}
    approved = sum(count[h] for h in ("approved-cards", "no-regulator-cards", "wrong-cards"))
    assert approved == len(answer["approved"])
    assert count["narrower-cards"] == len(answer["narrower"])
    assert count["wider-cards"] == len(answer["wider_group"])
    assert count["studied-cards"] == len(answer["being_studied"])
    assert count["more-trials-cards"] == len(answer["more_in_trials"])
    assert count["new-trials-cards"] == len(answer["new_in_trials"])
    assert count["new-cards"] + count["opposite-cards"] == len(answer["new_clues"])


@pytest.mark.parametrize("holder", [pile[0] for pile in PILES])
def test_the_panel_opens_inside_the_card_with_the_tickets_words(seen, holder):
    panel = seen["cases"][holder]["seen"]
    assert panel["visible"] and panel["inCard"]
    assert panel["choices"] == CHOICES
    assert panel["sendDisabledBeforeChoice"] is True  # one reason must be picked
    assert panel["privacy"] == PRIVACY
    assert panel["placeholder"] == "Anything else? (optional)"
    assert panel["maxLength"] == 200
    assert panel["buttons"] == ["Send", "Cancel"]


@pytest.mark.parametrize("holder,tab,box", PILES)
def test_send_posts_the_card_and_shows_thank_you(seen, answer, holder, tab, box):
    case = seen["cases"][holder]
    assert case["thanks"] == THANKS
    assert case["panelGone"] and case["linkGone"]
    sent = case["body"]
    assert sent["type"].startswith("application/json")
    body = sent["body"]
    assert set(body) == {"disease_id", "medicine_id", "medicine_name", "tab", "box", "reason", "note", "website"}
    assert body["disease_id"] == answer["disease"]["id"]
    assert body["tab"] == tab and body["box"] == box
    assert body["reason"] == "wrong_link"  # the third choice
    assert body["note"] == "Link goes to the wrong trial."
    assert body["website"] == ""
    assert body["medicine_name"] == case["medicineName"].strip()
    every_id = {m["id"] for key in ("approved", "narrower", "wider_group", "being_studied", "more_in_trials",
                                    "new_in_trials", "new_clues") for m in answer.get(key, [])}
    assert body["medicine_id"] in every_id


def test_tap_targets_are_at_least_44_px_on_a_phone(seen):
    heights = seen["heights"]
    assert seen["closedLink"] >= 44
    assert heights["link"] >= 44 or heights["link"] == 0  # hidden while the panel is open
    assert heights["choices"] and min(heights["choices"]) >= 44
    assert min(heights["buttons"]) >= 44


def test_cancel_closes_the_panel_and_brings_back_the_link(seen):
    assert seen["afterCancel"] == {"panelHidden": True, "linkShown": True}


def test_a_failure_says_so_and_does_not_thank(seen):
    assert seen["failure"]["words"] == FAILED
    assert seen["failure"]["thanksShown"] is False
    assert seen["failure"]["body"]["reason"] == "wrong_disease"
    assert seen["failure"]["body"]["note"] == ""


def test_the_print_page_has_no_report(seen):
    assert seen["registerReports"] == 0
    assert seen["printedReports"] == 0


def test_the_privacy_line_is_written_once_in_the_page():
    page = PAGE_FILE.read_text(encoding="utf-8")
    assert page.count(PRIVACY) == 1
