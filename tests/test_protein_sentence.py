"""Ticket 3.8. What the protein does, in one sentence from UniProt.

Kashish's decision (23 Nov 2026, signed paper): a clue card says in one
sentence what its protein does. 200 letters or less. One credit line in the
guide. It must never read as which way the disease needs the protein turned.

The sentence is UniProt's. Moonlight reads it through Open Targets, on a
question it already asks (TARGETS_QUERY gains "functionDescriptions").
UniProt itself is never asked. moonlight/protein.py takes the packaging off
and keeps the first sentence. It changes no word, adds no word and reorders
nothing. A sentence longer than 200 characters is not shown at all. It is
never cut short.

Her example: Graves disease (MONDO_0005364), New clues, the first card:
ipilimumab, protein CTLA4. The whole search is saved in
fixtures/protein_sentence/ (asked live on 2026-11-24, data 26.09).

How these tests work. The first part hands texts to the cleaning function.
The second builds /api/clues from the saved answers, never from the network.
The third opens web/index.html in a real browser (Chromium) that is never
let outside, at phone width (390), the same way tests/test_opposite_way_box.py
does.
"""

import copy
import json
import pathlib
import re
import shutil
import subprocess
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from moonlight import api, fetch
from moonlight.filter import sort_paths
from moonlight.records import Disease, Medicine, MedicineForm, Path, Target

ROOT = pathlib.Path(__file__).resolve().parent.parent
SAVED = ROOT / "fixtures" / "protein_sentence"
PAGE_FILE = ROOT / "web" / "index.html"
PAGE = PAGE_FILE.read_text(encoding="utf-8")

GRAVES = "MONDO_0005364"
KEY = "function"  # the one new key on a protein of a clue card
LIMIT = 200

# What the saved answer gives for CTLA4, read from
# fixtures/protein_sentence/associated_targets/MONDO_0005364.response.json.
# The first text there starts:
#   "Inhibitory receptor acting as a major negative regulator of T-cell
#    responses (PubMed:11279501, PubMed:11279502, PubMed:16551244,
#    PubMed:1714933, PubMed:18641304, PubMed:28484017). Acts as a decoy ..."
CTLA4_SENTENCE = (
    "Inhibitory receptor acting as a major negative regulator of T-cell responses.")

# The other four proteins on the Graves clue cards, read from the same file.
GRAVES_SENTENCES = {
    "CTLA4": CTLA4_SENTENCE,
    "IGF1R": ("Receptor tyrosine kinase which mediates actions of insulin-like growth "
              "factor 1 (IGF1)."),
    "TSHR": "Receptor for the thyroid-stimulating hormone (TSH) or thyrotropin.",
    "IL2RA": "Receptor for interleukin-2.",
    "TGFB2": ("Precursor of the Latency-associated peptide (LAP) and Transforming growth "
              "factor beta-2 (TGF-beta-2) chains, which constitute the regulatory and "
              "active subunit of TGF-beta-2, respectively."),
}

# These stay word for word.
DIRECTION_LINE = "The data does not say which direction this disease needs."
ENDING = (
    "But there is a catch. Nobody knows from our information if the disease needs this "
    "protein turned up or down. So this is a clue to read about. Never start, stop or "
    "change any medicine without a doctor.")
SAFETY_LINE = ("For learning and research exploration, not medical advice. Never start, stop or "
               "change any medicine without a doctor.")
# Kashish's approved words, exactly.
CREDIT = "Protein descriptions. Written by UniProt, read through Open Targets. CC BY 4.0."


def load(file):
    return json.loads(file.read_text(encoding="utf-8"))


def saved_post_json(body):
    """Stands in for fetch._post_json with the saved files."""
    assert set(body) == {"query", "variables"}
    query, variables = body["query"], body["variables"]
    if "targetId" in variables:
        kind, asked = "target_drugs", variables["targetId"]
    else:
        asked = variables["diseaseId"]
        if "parents" in query:
            kind = "family"
        elif "associatedTargets" in query:
            kind = "associated_targets"
        elif "drugAndClinicalCandidates" in query:
            kind = "disease_drugs"
        else:
            kind = "disease"
    file = SAVED / kind / f"{asked}.response.json"
    assert file.exists(), f"no saved answer for {kind} {asked}"
    return load(file)


def no_network():
    return [patch(name, side_effect=AssertionError("network used")) for name in (
        "requests.request", "requests.post", "requests.get",
        "requests.sessions.Session.request")]


def page_answer(disease_id):
    """What /api/clues sends, from saved answers and the real hand-written files."""
    api.forget_visitors()
    guards = no_network()
    for guard in guards:
        guard.start()
    try:
        with patch("moonlight.fetch._post_json", side_effect=saved_post_json):
            response = TestClient(api.app).get("/api/clues", params={"disease_id": disease_id})
    finally:
        for guard in guards:
            guard.stop()
        api.forget_visitors()
    assert response.status_code == 200
    return response.json()


@pytest.fixture(scope="module")
def graves():
    return page_answer(GRAVES)


def saved_rows():
    answer = load(SAVED / "associated_targets" / f"{GRAVES}.response.json")
    return answer["data"]["disease"]["associatedTargets"]["rows"]


def saved_texts():
    """symbol -> the texts as Open Targets sent them, for Graves' 25 proteins."""
    return {row["target"]["approvedSymbol"]: row["target"]["functionDescriptions"]
            for row in saved_rows()}


# ---- 1. the cleaning function ----

from moonlight import protein  # noqa: E402  (new in this ticket)


def test_no_texts_gives_none_not_an_empty_string():
    assert protein.sentence([]) is None
    assert protein.sentence(()) is None
    assert protein.sentence(None) is None
    assert protein.sentence([""]) is None
    assert protein.sentence(["  .  "]) is None


def test_step_1_curly_evidence_tags_go_with_their_full_stop():
    assert protein.sentence(
        ["May play a role in mast cells. {ECO:0000269|PubMed:11418668}."]
    ) == "May play a role in mast cells."


def test_step_2_the_trailing_space_and_stop_go():
    assert protein.sentence(["May play an important role in lymphopoiesis. ."]) == (
        "May play an important role in lymphopoiesis.")


def test_step_3_a_label_in_square_brackets_at_the_front_goes():
    assert protein.sentence(
        ["[Isoform 1]: Mediates the potassium ion permeability of excitable membranes."]
    ) == "Mediates the potassium ion permeability of excitable membranes."


def test_step_4_line_wrap_marks_go_and_a_real_hanging_hyphen_stays():
    assert protein.sentence(
        ["Induces the release of T-cell- attracting chemokines for IL1RL1/ ST2."]
    ) == "Induces the release of T-cell-attracting chemokines for IL1RL1/ST2."
    hanging = "Tubulin filaments consist of alpha- and beta-tubulin heterodimers."
    assert protein.sentence([hanging]) == hanging


def test_step_5_only_the_first_sentence_is_kept():
    assert protein.sentence(
        ["Receptor for interleukin-2. The receptor is involved in immune tolerance."]
    ) == "Receptor for interleukin-2."


def test_step_5_an_abbreviation_does_not_end_the_sentence():
    whole = "Connects chaperones, e.g. HSPA1A or HSPA8, and small heat shock proteins."
    assert protein.sentence([whole + " Acts as a scaffold."]) == whole


def test_only_the_first_text_is_used():
    assert protein.sentence(["First text here.", "Second text here."]) == "First text here."


def test_new_step_pubmed_brackets_go_with_the_space_before_them():
    # the ticket's own shape
    assert protein.sentence(
        ["Regulates T cells (PubMed:123, PubMed:456). Acts as a decoy."]
    ) == "Regulates T cells."
    # one in the middle of a sentence
    assert protein.sentence(
        ["Receptor for TNFSF5/CD40LG (PubMed:31331973) on B cells."]
    ) == "Receptor for TNFSF5/CD40LG on B cells."
    # two in one sentence
    assert protein.sentence(
        ["Binds iron (PubMed:1) and copper (PubMed:2, PubMed:3)."]
    ) == "Binds iron and copper."


def test_other_round_brackets_are_not_touched():
    for whole in ("Receptor for the thyroid-stimulating hormone (TSH) or thyrotropin.",
                  "Transcriptional regulator that acts as a repressor (By similarity)."):
        assert protein.sentence([whole]) == whole


def test_new_step_exactly_200_characters_is_shown_whole():
    whole = "A" + "b" * 198 + "."
    assert len(whole) == LIMIT
    assert protein.sentence([whole]) == whole


def test_new_step_201_characters_gives_nothing():
    whole = "A" + "b" * 199 + "."
    assert len(whole) == LIMIT + 1
    assert protein.sentence([whole]) is None
    assert protein.sentence([whole + " A short second sentence."]) is None


def test_the_length_is_measured_after_the_pubmed_brackets_are_gone():
    whole = "A" + "b" * 198 + "."
    with_citations = whole[:-1] + " (PubMed:11279501, PubMed:11279502)."
    assert len(with_citations) > LIMIT
    assert protein.sentence([with_citations]) == whole


def test_a_sentence_is_never_cut_and_never_gets_dots():
    """Every length from 150 to 260: the whole sentence or nothing."""
    for length in range(150, 261):
        whole = "A" + "b" * (length - 2) + "."
        got = protein.sentence([whole + " Another sentence follows it."])
        if length <= LIMIT:
            assert got == whole
        else:
            assert got is None
        assert got is None or ("..." not in got and "…" not in got)


def squash(text):
    return "".join(text.split())


def unpacked(text):
    """The first text with only packaging gone: curly tags, PubMed brackets
    and all spaces. No word is touched."""
    text = re.sub(r"\{[^{}]*\}\.?", "", text)
    text = re.sub(r"\(PubMed:[^()]*\)", "", text)
    return squash(text)


def test_example_ctla4_from_the_saved_answer():
    assert protein.sentence(saved_texts()["CTLA4"]) == CTLA4_SENTENCE
    assert len(CTLA4_SENTENCE) <= LIMIT


def test_example_the_other_graves_proteins_on_cards():
    texts = saved_texts()
    for symbol, sentence in GRAVES_SENTENCES.items():
        assert protein.sentence(texts[symbol]) == sentence, symbol


def test_example_what_the_25_saved_proteins_give():
    """Counted from the saved answer: 21 get a sentence, 3 are too long
    (CLNK, NFKB1, PTPN22) and 1 (C1QTNF6) has no text."""
    texts = saved_texts()
    assert len(texts) == 25
    got = {symbol: protein.sentence(found) for symbol, found in texts.items()}
    assert texts["C1QTNF6"] == [] and got["C1QTNF6"] is None
    with_one = sorted(symbol for symbol, sentence in got.items() if sentence)
    without = sorted(symbol for symbol, sentence in got.items() if sentence is None)
    assert len(with_one) + len(without) == 25
    assert without == ["C1QTNF6", "CLNK", "NFKB1", "PTPN22"]
    assert len(with_one) == 21
    # the three that are too long have a text; they are not cut to fit
    for symbol in ("CLNK", "NFKB1", "PTPN22"):
        assert texts[symbol] and texts[symbol][0]


def test_no_saved_sentence_contains_words_moonlight_added():
    """Each sentence, letter for letter, is one unbroken piece of the first
    text once the packaging is off. Nothing added, changed or reordered."""
    seen = 0
    for symbol, texts in saved_texts().items():
        sentence = protein.sentence(texts)
        if sentence is None:
            continue
        seen += 1
        assert squash(sentence) in unpacked(texts[0]), symbol
        assert len(sentence) <= LIMIT
        assert sentence == sentence.strip() and "  " not in sentence
        for packaging in ("{", "}", "ECO:", "PubMed", "...", "…"):
            assert packaging not in sentence, (symbol, packaging)
    assert seen == 21


# ---- 2. fetch.py and api.py, from the saved answers ----

def test_the_question_asks_for_the_one_new_field_on_the_target():
    assert "target { id approvedSymbol approvedName functionDescriptions }" in fetch.TARGETS_QUERY
    # on no other question
    for query in (fetch.DISEASE_QUERY, fetch.FAMILY_QUERY, fetch.TARGET_DRUGS_QUERY,
                  fetch.DISEASE_DRUGS_QUERY):
        assert "functionDescriptions" not in query


def test_uniprot_is_never_asked():
    for module in ("fetch.py", "protein.py", "api.py"):
        code = (ROOT / "moonlight" / module).read_text(encoding="utf-8")
        assert "uniprot.org" not in code.lower(), module
    assert "requests" not in (ROOT / "moonlight" / "protein.py").read_text(encoding="utf-8")


def test_a_target_carries_the_texts_as_open_targets_sent_them():
    with patch("moonlight.fetch._post_json", side_effect=saved_post_json):
        targets = fetch.fetch_targets(Disease(GRAVES, "Graves disease"), 25)
    assert len(targets) == 25
    sent = saved_texts()
    for target in targets:
        assert target.function_texts == tuple(sent[target.symbol]), target.symbol
    by_symbol = {target.symbol: target for target in targets}
    assert by_symbol["CTLA4"].function_texts[0].startswith(
        "Inhibitory receptor acting as a major negative regulator of T-cell responses "
        "(PubMed:11279501,")
    assert by_symbol["C1QTNF6"].function_texts == ()


def test_an_old_saved_answer_without_the_field_still_loads():
    old = load(ROOT / "fixtures" / "opposite_way_box" / "associated_targets"
               / "MONDO_0004691.response.json")
    assert "functionDescriptions" not in json.dumps(old)
    with patch("moonlight.fetch._post_json", return_value=old):
        targets = fetch.fetch_targets(Disease("MONDO_0004691", "ADPKD"), 25)
    assert len(targets) == 25
    assert all(target.function_texts == () for target in targets)


def test_a_target_made_the_old_way_has_no_texts():
    assert Target("ENSG_TEST", "TEST1", "test protein", 0.5).function_texts == ()


def test_example_the_first_new_clue_is_ipilimumab_with_ctla4s_sentence(graves):
    first = graves["new_clues"][0]
    assert first["medicine"] == "Ipilimumab"
    assert [found["symbol"] for found in first["proteins"]] == ["CTLA4"]
    assert first["proteins"][0][KEY] == CTLA4_SENTENCE


def test_example_every_protein_on_a_graves_clue_card(graves):
    assert len(graves["new_clues"]) == 10
    for clue in graves["new_clues"] + graves["being_studied"]:
        for found in clue["proteins"]:
            assert found[KEY] == GRAVES_SENTENCES[found["symbol"]], clue["medicine"]


def test_example_a_protein_gains_one_key_and_loses_none(graves):
    for clue in graves["new_clues"]:
        for found in clue["proteins"]:
            assert set(found) - {"opposite_way"} == {
                "symbol", "points", "direction", "machine", "piece_of_machine", KEY}


def test_example_nothing_but_a_clue_cards_protein_has_the_key(graves):
    """Approved cards and cards with no path are out of scope: no key there."""
    without = copy.deepcopy(graves)
    for clue in without["new_clues"] + without["being_studied"]:
        for found in clue["proteins"]:
            del found[KEY]
    assert '"%s"' % KEY not in json.dumps(without)
    assert len(graves["approved"]) == 4 and len(graves["more_in_trials"]) == 16


def test_example_the_ending_and_direction_words_are_unchanged(graves):
    for clue in graves["new_clues"]:
        assert clue["ending"] == ENDING


# hand-built clues, for the guards

DISEASE = Disease("TEST_0000001", "test disease")
RAW_WITH_PACKAGING = (
    "Receptor for a test hormone (PubMed:11847099, PubMed:12045258). Also acts on "
    "another one (PubMed:12045258). {ECO:0000269|PubMed:11847099}.")
WITH_TEXT = Target("ENSG00000000001", "ABC1", "test protein one", 0.8,
                   function_texts=(RAW_WITH_PACKAGING,))
NO_TEXT = Target("ENSG00000000002", "ABC2", "test protein two", 0.7)
EXACTLY_200 = Target("ENSG00000000003", "ABC3", "test protein three", 0.6,
                     function_texts=("A" + "b" * 198 + ". A second sentence.",))
ONE_OVER = Target("ENSG00000000004", "ABC4", "test protein four", 0.5,
                  function_texts=("A" + "b" * 199 + ". A second sentence.",))
DOWN = ("ANTAGONIST",)


def path(name, medicine_id, target, link=None):
    form = MedicineForm(medicine_id, name, best_stage="APPROVAL", disease_stage=link,
                        withdrawn=False)
    return Path(Medicine(name, (form,)), target, DISEASE, DOWN, target.score,
                (f"https://example.org/{medicine_id}",))


def cards(paths):
    """What /api/clues sends for these hand-built paths."""
    found = api._Found(DISEASE, sort_paths(paths), [], [], [])
    with patch.object(api, "_find", return_value=found), \
            patch.object(api, "looks_wrong", return_value=set()), \
            patch.object(api, "pushes_wrong_way", return_value=set()):
        response = TestClient(api.app).get("/api/clues", params={"disease_id": DISEASE.id})
    assert response.status_code == 200
    return response.json()


def proteins_of(answer, part="new_clues"):
    return {found["symbol"]: found for clue in answer[part] for found in clue["proteins"]}


@pytest.fixture(scope="module")
def made():
    return cards([
        path("WITHTEXT", "CHEMBL9001", WITH_TEXT),
        path("NOTEXT", "CHEMBL9002", NO_TEXT),
        path("TWOHUNDRED", "CHEMBL9003", EXACTLY_200),
        path("ONEOVER", "CHEMBL9004", ONE_OVER),
        path("STUDIED", "CHEMBL9005", WITH_TEXT, "PHASE_2"),
        path("APPROVEDHERE", "CHEMBL9006", WITH_TEXT, "APPROVAL"),
    ])


def test_guard_a_protein_with_no_text_has_no_key(made):
    assert KEY not in proteins_of(made)["ABC2"]


def test_guard_curly_tags_and_pubmed_brackets_never_reach_the_answer(made):
    assert proteins_of(made)["ABC1"][KEY] == "Receptor for a test hormone."
    sent = json.dumps(made)
    assert "PubMed" not in sent and "ECO:" not in sent and "{ECO" not in sent


def test_guard_200_characters_is_sent_whole_and_201_is_not_sent(made):
    assert proteins_of(made)["ABC3"][KEY] == "A" + "b" * 198 + "."
    assert KEY not in proteins_of(made)["ABC4"]


def test_guard_a_being_studied_card_has_the_sentence_and_an_approved_card_does_not(made):
    assert proteins_of(made, "being_studied")["ABC1"][KEY] == "Receptor for a test hormone."
    assert [medicine["medicine"] for medicine in made["approved"]] == ["Approvedhere"]
    assert KEY not in proteins_of(made, "approved")["ABC1"]


def test_guard_the_key_is_never_empty_or_none(made, graves):
    for answer in (made, graves):
        for part in ("new_clues", "being_studied"):
            for found in proteins_of(answer, part).values():
                assert KEY not in found or (isinstance(found[KEY], str) and found[KEY])


# ---- 3. the page, as text ----

GUIDE = PAGE[PAGE.index('id="guide"'):PAGE.index("<!-- end of the guide -->")]


def test_the_page_types_no_part_of_any_sentence():
    for sentence in GRAVES_SENTENCES.values():
        assert sentence not in PAGE
        assert sentence[:25] not in PAGE


def test_the_line_has_no_label_in_front_and_no_bold():
    template = PAGE[PAGE.index('<template id="protein-function-template">'):]
    template = template[:template.index("</template>") + len("</template>")]
    assert template == ('<template id="protein-function-template">'
                        '<p class="protein-function" data-slot="protein-function"></p></template>')


def test_the_direction_line_is_still_in_the_card_template_word_for_word():
    card = PAGE[PAGE.index('<template id="card-template">'):]
    card = card[:card.index("</template>")]
    assert '<p class="direction-note">' + DIRECTION_LINE + "</p>" in card
    # the proteins come first, the direction line after them
    assert card.index('data-part="proteins"') < card.index('class="direction-note"')


def test_the_credit_line_is_in_the_guides_list_once_in_the_lists_own_style():
    facts = GUIDE[GUIDE.index("Where the facts come from"):]
    facts = facts[:facts.index("</details>")]
    assert ("<li><div><b>Protein descriptions.</b> <span>Written by UniProt, read through "
            "Open Targets. CC BY 4.0.</span></div></li>") in facts
    words = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", PAGE))
    assert words.count(CREDIT) == 1


def test_the_safety_line_is_still_on_the_page():
    assert SAFETY_LINE in re.sub(r"\s+", " ", PAGE)


# ---- the written rules ----

def test_claude_md_has_the_new_line_in_the_sources_rule():
    rules = " ".join((ROOT / "CLAUDE.md").read_text(encoding="utf-8").split())
    assert ("Open Targets also sends UniProt's sentence on what a protein does. Moonlight "
            "shows it as sent, cleaned, never rewritten.") in rules
    assert rules.index("two machine sources and no more") < rules.index(
        "Open Targets also sends UniProt's sentence") < rules.index("## How to work")


def test_decisions_md_ends_with_the_two_new_lines():
    lines = (ROOT / "DECISIONS.md").read_text(encoding="utf-8").rstrip("\n").split("\n")
    lines = lines[:-2]  # ticket 2.43 added two lines (R1 and R6) after these
    assert lines[-2] == (
        "- 2026-11-23: A medicine whose official label covers only some people with the "
        "disease goes under Approved from the label, with one more line: \"The label "
        "covers only some people with this disease.\"")
    assert lines[-1] == (
        "- 2026-11-23: A clue card shows one sentence on what its protein does, 200 "
        "letters or less, written by UniProt and read through Open Targets. It never "
        "says which way the disease needs the protein turned.")


# ---- 4. the page, in a real browser, at phone width ----

BROWSER_SCRIPT = r"""
"use strict";
const fs = require("fs");
const { chromium } = require("playwright");
const PAGE = fs.readFileSync(process.argv[1], "utf-8");
const ANSWERS = JSON.parse(fs.readFileSync(process.argv[2], "utf-8"));
const SITE = "http://moonlight.test";

function readCards() {
  const after = (a, b) => !!(a.compareDocumentPosition(b) & Node.DOCUMENT_POSITION_FOLLOWING);
  const readCard = card => {
    const note = card.querySelector(".direction-note");
    const lines = [...card.querySelectorAll('[data-slot="protein-function"]')];
    return {
      name: card.querySelector('[data-slot="medicine-name"]').textContent,
      onScreen: card.checkVisibility(),
      text: card.innerText,
      html: card.innerHTML,
      directionNotes: [...card.querySelectorAll(".direction-note")].map(el => el.textContent),
      directionNoteShown: !!note && note.getClientRects().length > 0,
      ending: (card.querySelector('[data-slot="ending"]') || {}).textContent || null,
      explanations: card.querySelectorAll('[data-slot="explanation"]').length,
      rows: [...card.querySelectorAll('[data-slot="protein"]')].map(row => {
        const id = row.querySelector(".protein-id");
        const facts = row.querySelector(".protein-facts");
        return {
          symbol: id.textContent,
          lines: [...row.querySelectorAll('[data-slot="protein-function"]')].map(line => {
            const style = getComputedStyle(line);
            const top = line.getBoundingClientRect().top;
            return {
              text: line.textContent,
              seen: line.innerText,
              children: line.children.length,
              weight: style.fontWeight,
              size: parseFloat(style.fontSize),
              colour: style.color,
              mutedColour: getComputedStyle(card.querySelector(".forms")).color,
              bodySize: parseFloat(getComputedStyle(card.querySelector("h3")).fontSize),
              underTheRow: top >= id.getBoundingClientRect().bottom - 1
                && top >= facts.getBoundingClientRect().bottom - 1,
              aboveTheDirectionLine: !!note && after(line, note)
                && line.getBoundingClientRect().bottom <= note.getBoundingClientRect().top + 1,
              insideTheCard: line.getBoundingClientRect().right
                <= card.getBoundingClientRect().right + 1,
            };
          }),
        };
      }),
      linesOutsideARow: lines.filter(line => !line.closest('[data-slot="protein"]')).length,
    };
  };
  const all = id => [...document.querySelectorAll("#" + id + " .card")].map(readCard);
  return {
    clues: [...document.querySelectorAll("#panel-clues .card")].map(readCard),
    linesOnThePage: document.querySelectorAll('[data-slot="protein-function"]').length,
    linesOnTheCluesTab: document.querySelectorAll('#panel-clues [data-slot="protein-function"]').length,
    sideways: document.documentElement.scrollWidth > document.documentElement.clientWidth,
    safety: document.body.innerText.includes(
      "For learning and research exploration, not medical advice."),
  };
}

async function oneSearch(browser, answer) {
  const context = await browser.newContext({ viewport: { width: 390, height: 844 } });
  const page = await context.newPage();
  const errors = [], explainCalls = [], others = [];
  page.on("pageerror", problem => errors.push(String(problem)));
  await context.route("**/*", route => {
    const url = route.request().url();
    if (url === SITE + "/" || url.startsWith(SITE + "/?"))
      return route.fulfill({ contentType: "text/html; charset=utf-8", body: PAGE });
    if (url.startsWith(SITE + "/api/clues?"))
      return route.fulfill({ contentType: "application/json", body: JSON.stringify(answer) });
    if (url.startsWith(SITE + "/api/explain?")) {
      explainCalls.push(url);
      return route.fulfill({ status: 404, contentType: "application/json", body: "{}" });
    }
    others.push(url);
    return route.abort();
  });
  await page.goto(SITE + "/?disease=MONDO_TEST");
  await page.waitForSelector("#found", { state: "visible" });
  const out = { errors };
  await page.click("#tab-clues");
  await page.waitForTimeout(400);
  const box = page.locator("#opposite-box");
  if (await box.count() && await box.isVisible() && !(await box.evaluate(el => el.open))) {
    await page.click("#opposite-box summary");
    await page.waitForTimeout(300);
  }
  out.read = await page.evaluate(readCards);
  await page.click("#tab-trials");
  await page.waitForTimeout(300);
  out.trials = await page.evaluate(() =>
    [...document.querySelectorAll("#panel-trials .card")].map(card => ({
      name: card.querySelector('[data-slot="medicine-name"]').textContent,
      lines: [...card.querySelectorAll('[data-slot="protein-function"]')].map(el => el.textContent),
      directionNotes: [...card.querySelectorAll(".direction-note")].map(el => el.textContent),
      proteins: card.querySelectorAll('[data-slot="protein"]').length,
    })));
  out.explainCalls = explainCalls.length;
  out.uniprotAsked = others.filter(url => url.toLowerCase().includes("uniprot")).length;
  await context.close();
  return out;
}

(async () => {
  const browser = await chromium.launch();
  const out = {};
  for (const name of Object.keys(ANSWERS)) out[name] = await oneSearch(browser, ANSWERS[name]);
  await browser.close();
  console.log(JSON.stringify(out));
})().catch(problem => { console.error(problem); process.exit(1); });
"""

# A sentence that would break a page that did not treat it as plain words.
TRICKY = "Binds <b>bold</b> & {curly} things."


@pytest.fixture(scope="module")
def answers(graves, made):
    """Answers of /api/clues: her example as the API sends it; the same with
    hand-set sentences; and the hand-built clues."""
    edited = copy.deepcopy(graves)
    clues = edited["new_clues"]
    assert [clue["medicine"] for clue in clues[1:4]] == ["Tremelimumab", "Mecasermin", "Masoprocol"]
    del clues[1]["proteins"][0][KEY]  # Tremelimumab: no sentence at all
    clues[2]["proteins"][0][KEY] = TRICKY  # Mecasermin
    # A card with two proteins: the first has a sentence, the second has none.
    second = copy.deepcopy(clues[3]["proteins"][0])
    second.update(symbol="TEST2", points=11, machine=2)
    del second[KEY]
    clues[3]["proteins"].append(second)
    return {"graves": graves, "edited": edited, "made": made}


@pytest.fixture(scope="module")
def seen(answers, tmp_path_factory):
    """Opens the page once per answer and returns what a reader sees."""
    node = shutil.which("node")
    if not node or subprocess.run(
            [node, "-e", "require('playwright')"], capture_output=True).returncode:
        pytest.skip("needs node with playwright to open a real browser")
    answers_file = tmp_path_factory.mktemp("protein_sentence") / "answers.json"
    answers_file.write_text(json.dumps(answers), encoding="utf-8")
    run = subprocess.run(
        [node, "-e", BROWSER_SCRIPT, str(PAGE_FILE), str(answers_file)],
        capture_output=True, text=True, timeout=240, cwd=str(ROOT))
    assert run.returncode == 0, run.stderr[-3000:]
    out = json.loads(run.stdout)
    for name in answers:
        assert out[name]["errors"] == [], name
    return out


def card_named(read, name):
    found = [card for card in read["clues"] if card["name"] == name]
    assert len(found) == 1, name
    return found[0]


def test_browser_example_the_first_card_shows_ctla4s_sentence_under_its_row(seen):
    first = seen["graves"]["read"]["clues"][0]
    assert first["name"] == "Ipilimumab" and first["onScreen"]
    assert [row["symbol"] for row in first["rows"]] == ["CTLA4"]
    lines = first["rows"][0]["lines"]
    assert [line["text"] for line in lines] == [CTLA4_SENTENCE]
    assert lines[0]["seen"] == CTLA4_SENTENCE
    assert lines[0]["underTheRow"] and lines[0]["aboveTheDirectionLine"]
    assert lines[0]["insideTheCard"]


def test_browser_example_every_graves_clue_card_shows_what_the_api_sent(seen, graves):
    read = seen["graves"]["read"]["clues"]
    assert len(read) == len(graves["new_clues"]) == 10
    by_name = {clue["medicine"]: clue for clue in graves["new_clues"]}
    for card in read:
        sent = by_name[card["name"]]["proteins"]
        assert [row["symbol"] for row in card["rows"]] == [found["symbol"] for found in sent]
        for row, found in zip(card["rows"], sent):
            assert [line["text"] for line in row["lines"]] == [found[KEY]], card["name"]
        assert card["linesOutsideARow"] == 0
    assert seen["graves"]["read"]["linesOnTheCluesTab"] == 10


def test_browser_the_line_is_small_and_muted_with_no_label_and_no_bold(seen):
    for card in seen["graves"]["read"]["clues"]:
        for row in card["rows"]:
            for line in row["lines"]:
                assert line["children"] == 0  # plain words, nothing inside
                assert line["weight"] in ("400", "normal")
                assert line["size"] <= 12 < line["bodySize"]
                assert line["colour"] == line["mutedColour"]
                assert line["underTheRow"] and line["aboveTheDirectionLine"]
                assert line["insideTheCard"]


def test_browser_the_direction_line_is_on_every_clue_card_as_before(seen):
    for name in ("graves", "edited", "made"):
        cards_read = seen[name]["read"]["clues"]
        assert cards_read
        for card in cards_read:
            assert card["directionNotes"] == [DIRECTION_LINE], (name, card["name"])
            assert card["directionNoteShown"] or not card["onScreen"]
            assert card["ending"] == ENDING


def test_browser_guard_a_protein_with_no_sentence_has_no_line(seen):
    read = seen["edited"]["read"]
    card = card_named(read, "Tremelimumab")
    assert [row["lines"] for row in card["rows"]] == [[]]
    assert card["directionNotes"] == [DIRECTION_LINE]
    assert CTLA4_SENTENCE not in card["text"]
    two = card_named(read, "Masoprocol")
    assert [row["symbol"] for row in two["rows"]] == ["IGF1R", "TEST2"]
    assert len(two["rows"][0]["lines"]) == 1 and two["rows"][-1]["lines"] == []
    made = seen["made"]["read"]
    assert [row["lines"] for row in card_named(made, "Notext")["rows"]] == [[]]
    assert [row["lines"] for row in card_named(made, "Oneover")["rows"]] == [[]]


def test_browser_guard_the_sentence_is_shown_as_sent_as_plain_words(seen):
    card = card_named(seen["edited"]["read"], "Mecasermin")
    line = card["rows"][0]["lines"][0]
    assert line["text"] == TRICKY and line["seen"] == TRICKY
    assert line["children"] == 0  # the <b> stayed words, it did not become bold


def test_browser_guard_a_sentence_is_never_cut(seen):
    whole = "A" + "b" * 198 + "."
    line = card_named(seen["made"]["read"], "Twohundred")["rows"][0]["lines"][0]
    assert line["text"] == whole and line["seen"] == whole
    assert line["insideTheCard"]
    for name in ("graves", "made"):
        for card in seen[name]["read"]["clues"]:
            assert "..." not in card["text"] and "…" not in card["text"]


def test_browser_guard_curly_tags_and_pubmed_brackets_never_reach_the_page(seen):
    for name in ("graves", "made"):
        for card in seen[name]["read"]["clues"]:
            for packaging in ("PubMed", "ECO:", "{", "}"):
                assert packaging not in card["text"], (name, card["name"], packaging)
    line = card_named(seen["made"]["read"], "Withtext")["rows"][0]["lines"][0]
    assert line["text"] == "Receptor for a test hormone."


def test_browser_cards_with_no_path_have_no_line(seen):
    trials = seen["graves"]["trials"]
    assert len(trials) >= 16
    for card in trials:
        assert card["lines"] == [], card["name"]


def test_browser_the_page_is_not_wider_than_the_phone_and_keeps_the_safety_line(seen):
    for name in ("graves", "edited", "made"):
        assert not seen[name]["read"]["sideways"]
        assert seen[name]["read"]["safety"]
        assert seen[name]["uniprotAsked"] == 0


# ---- commit B: the explanation slot is off the card ----
#
# Shreshth, 24 Nov 2026, after speaking with Kashish: the "Plain-language
# explanation" written by Gemini leaves the card. explain.py and
# /api/explain stay in the repo and keep working (tests/test_explain.py and
# tests/test_api.py test them). Only the page stops using them.

# The caution sentence said once at the top of each trial box (ticket 2.29).
ONCE_PER_BOX = ('<p class="doctor-line" data-part="caution">Never start, stop or change any '
                "medicine without a doctor.</p>")


def test_b_the_page_has_no_explanation_slot_in_any_form():
    for gone in ("Plain-language explanation", "Read explanation", 'data-slot="explanation"',
                 "explanation-loading", "explanation-ready", "explanation-failed",
                 "explanation-too-many", "readExplanation", "Read more",
                 "Moonlight could not get this explanation"):
        assert gone not in PAGE, gone


def test_b_the_page_never_calls_the_explain_address():
    assert "/api/explain" not in PAGE
    assert "FIRST_EXPLAINED" not in PAGE  # the first-five fetch when a tab opens


def test_b_the_fixed_ending_stays_word_for_word():
    card = PAGE[PAGE.index('<template id="card-template">'):]
    card = card[:card.index("</template>")]
    assert '<p class="ending" data-slot="ending"></p>' in card
    assert 'slot(el, "ending").textContent = clue.ending;' in PAGE
    assert ENDING in re.sub(r"\s+", " ", GUIDE)  # the sample card's ending
    assert PAGE.count(ONCE_PER_BOX) == 2  # once in each of the two trial boxes
    assert SAFETY_LINE in re.sub(r"\s+", " ", PAGE)


def test_b_the_guide_says_nothing_untrue_about_explanations():
    words = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", GUIDE))
    for untrue in ("Plain-language explanation", "Explanations are written by Gemini",
                   "Explanations come from", "The clue in plain words",
                   "Doxapram grabs a protein called KCNK3"):
        assert untrue not in words, untrue
    # the true parts stay
    assert "Gemini suggests which disease you mean, and Open Targets confirms it." in words
    assert "What you type is sent to Gemini, so type no names or private details." in words


def test_b_explain_py_and_its_address_are_still_in_the_repo():
    assert (ROOT / "moonlight" / "explain.py").exists()
    assert (ROOT / "tests" / "test_explain.py").exists()
    assert "/api/explain" in [route.path for route in api.app.routes]


def test_browser_b_no_card_has_an_explanation_slot_and_none_is_asked_for(seen):
    for name in ("graves", "edited", "made"):
        assert seen[name]["explainCalls"] == 0, name
        for card in seen[name]["read"]["clues"]:
            assert card["explanations"] == 0, (name, card["name"])
            assert "explanation" not in card["text"].lower(), (name, card["name"])
            assert card["ending"] == ENDING


def test_browser_b_example_the_first_card_reads_like_this_top_to_bottom(seen):
    first = seen["graves"]["read"]["clues"][0]
    lines = [line.strip() for line in first["text"].split("\n") if line.strip()]
    assert lines == [
        "1", "Ipilimumab", "Forms: Ipilimumab", "804 reports", "RESEARCH PATHWAY",
        "Ipilimumab", "→", "CTLA4", "→", "Graves disease",
        "CTLA4", "Down", "59 / 100 points",
        CTLA4_SENTENCE,
        DIRECTION_LINE,
        ENDING,
        "Source record",
    ]
