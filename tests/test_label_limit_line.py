"""Ticket 2.33. "Only some people": one more grey line on a hand-added approval.

Kashish's decisions, 23 Nov 2026, 6:37 pm. Two medicines whose official
label covers only some people with the disease go under Approved from that
label, and each card says so in one fixed sentence, the same on both. Her
words, exactly:

    The label covers only some people with this disease.

The two entries, at the end of moonlight/approvals.json, both with
"limited": true:

  - imatinib for systemic mastocytosis (MONDO_0016586, as avapritinib's entry)
  - propylthiouracil for Graves disease (MONDO_0005364, as methimazole's entry)

The EXAMPLE is the Graves disease page: propylthiouracil is under Approved,
A to Z, and nowhere else. Its card shows two grey lines, the hand-added line
and then the new one. Methimazole, on the same page, shows the first only.

Moonlight never writes which people a label covers.

Saved files only. Graves disease: the whole search ticket 2.26 saved in
fixtures/approvals_by_hand/. Systemic mastocytosis: its own list, saved for
ticket 2.32 in the same folder. Nothing new was asked. No network.
"""

import copy
import json
import pathlib
import shutil
import subprocess
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from moonlight import api, engine

import test_approvals_batch as second_batch
import test_approvals_by_hand as first_batch
import test_approvals_third_batch as third_batch

ROOT = pathlib.Path(__file__).resolve().parent.parent
APPROVALS_FILE = ROOT / "moonlight" / "approvals.json"
CORRECTIONS_FILE = ROOT / "moonlight" / "corrections.json"
LEFT_OUT_FILE = ROOT / "moonlight" / "left_out.json"
LISTS = ROOT / "fixtures" / "approvals_by_hand" / "disease_drugs"
PAGE = (ROOT / "web" / "index.html").read_text(encoding="utf-8")

# Kashish's words, exactly.
LINE = "The label covers only some people with this disease."
ADDED_LINE = "This approval is missing from the database. We added it from the official label."
KEY = "limit_note"
THE_DAY = "2026-11-23"

GRAVES = "MONDO_0005364"
MASTOCYTOSIS = "MONDO_0016586"
PROPYLTHIOURACIL = "CHEMBL1518"
IMATINIB = "CHEMBL941"
IMATINIB_TABLET = "CHEMBL1642"  # imatinib mesylate
METHIMAZOLE = first_batch.METHIMAZOLE
AVAPRITINIB = third_batch.AVAPRITINIB
IMATINIB_LABEL = ("https://www.accessdata.fda.gov/drugsatfda_docs/label/2026/"
                  "021588s067lbl.pdf")
PROPYLTHIOURACIL_LABEL = ("https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm"
                          "?setid=804fa92a-a5ba-4be0-aa44-a40a2e89fde6")

FIRST_EIGHT = first_batch.FIRST_ENTRIES + second_batch.SECOND_BATCH + third_batch.THIRD_BATCH
NEW_TWO = [
    {"medicine_id": IMATINIB, "name": "Imatinib", "disease_id": MASTOCYTOSIS,
     "date": THE_DAY, "label": IMATINIB_LABEL, "limited": True},
    {"medicine_id": PROPYLTHIOURACIL, "name": "Propylthiouracil", "disease_id": GRAVES,
     "date": THE_DAY, "label": PROPYLTHIOURACIL_LABEL, "limited": True},
]

# The card, exactly as /api/clues must send it.
PROPYLTHIOURACIL_CARD = {
    "id": PROPYLTHIOURACIL,
    "medicine": "Propylthiouracil",
    "forms": ["Propylthiouracil"],
    "proteins": [],  # the page fetched no protein path for it
    "reports": 4,  # its four report links on the disease's own saved list
    "source": PROPYLTHIOURACIL_LABEL,
    "proof_note": ADDED_LINE,
    "limit_note": LINE,
}

# The eight earlier cards, as main gave them from each disease's own saved
# list before this ticket (printed on main, 23 Nov, and pasted here).
EARLIER_CARDS = [
    ("MONDO_0003233", "CHEMBL27", "Propranolol", 1, first_batch.PROPRANOLOL_LABEL),
    (GRAVES, METHIMAZOLE, "Methimazole", 13, first_batch.METHIMAZOLE_LABEL),
    ("MONDO_0019438", "CHEMBL1743007", "Daratumumab", 13, second_batch.DARATUMUMAB_LABEL),
    ("MONDO_0005342", "CHEMBL9194", "Atrasentan", 5, second_batch.ATRASENTAN_LABEL),
    ("MONDO_0005342", "CHEMBL4594614", "Sibeprenlimab", 5, second_batch.SIBEPRENLIMAB_LABEL),
    ("MONDO_0019100", "CHEMBL3989986", "Ravulizumab", 4, third_batch.RAVULIZUMAB_LABEL),
    (MASTOCYTOSIS, AVAPRITINIB, "Avapritinib", 5, third_batch.AVAPRITINIB_LABEL),
    ("MONDO_0007739", "CHEMBL2364639", "Valbenazine", 0, third_batch.VALBENAZINE_LABEL),
]


def load(file):
    return json.loads(file.read_text(encoding="utf-8"))


def saved_rows(disease_id):
    answer = load(LISTS / f"{disease_id}.response.json")
    assert answer["data"]["disease"]["id"] == disease_id
    return answer["data"]["disease"]["drugAndClinicalCandidates"]["rows"]


def saved_post_json(body):
    """Stands in for fetch._post_json: the saved answers of the three earlier tickets."""
    for saved in (first_batch.saved_post_json, second_batch.saved_post_json,
                  third_batch.saved_post_json):
        try:
            return saved(body)
        except (AssertionError, FileNotFoundError):
            pass
    raise AssertionError(f"no saved answer for {body['variables']}")


@pytest.fixture(autouse=True)
def offline():
    """Real HTTP is an error. Every question is answered from saved files."""
    api.forget_visitors()
    with patch("requests.request", side_effect=AssertionError("network used")), \
            patch("requests.post", side_effect=AssertionError("network used")), \
            patch("requests.get", side_effect=AssertionError("network used")), \
            patch("requests.sessions.Session.request",
                  side_effect=AssertionError("network used")), \
            patch("moonlight.fetch._post_json", side_effect=saved_post_json):
        yield
    api.forget_visitors()


def page(disease_id, entries=None):
    """What /api/clues sends: with the REAL file, or with these entries."""
    api.forget_visitors()
    if entries is None:
        response = TestClient(api.app).get("/api/clues", params={"disease_id": disease_id})
    else:
        with patch.object(engine, "_read_approvals", return_value=entries):
            response = TestClient(api.app).get("/api/clues", params={"disease_id": disease_id})
    assert response.status_code == 200
    return response.json()


def read(entries):
    with patch.object(engine, "_read_approvals", return_value=entries):
        return engine.approvals_by_hand()


def own_list_card(disease_id, medicine_id, entries=None):
    """The card /api/clues would send for a medicine, from the disease's own saved list."""
    if entries is None:
        hand = engine.added_by_hand(disease_id)
    else:
        with patch.object(engine, "_read_approvals", return_value=entries):
            hand = engine.added_by_hand(disease_id)
    tabs = second_batch.tabs_for(disease_id, hand)
    assert first_batch.only_under_approved(tabs, medicine_id)
    return api._approved_json(
        [medicine for medicine in tabs.approved if medicine.id == medicine_id][0])


def cards_with_the_key(a_page):
    return [(place, card["id"]) for place, part in a_page.items() if isinstance(part, list)
            for card in part if isinstance(card, dict) and KEY in card]


# ---- the words ----

def test_the_line_is_kashishs_words_exactly():
    assert engine.LIMITED_LINE == LINE
    assert engine.ADDED_LINE == ADDED_LINE  # the older line is as it was


# ---- the hand-written file ----

def test_the_real_file_holds_the_eight_earlier_entries_then_the_two_new_ones():
    # Ticket 2.34 added to the file. tests/test_approvals_fourth_batch.py holds the whole file.
    # Ticket 2.39 marked valbenazine "limited".
    assert load(APPROVALS_FILE)[:10] == third_batch.as_written_now(FIRST_EIGHT) + NEW_TWO


def test_the_eight_earlier_entries_are_written_as_they_were_with_no_new_key():
    for entry in load(APPROVALS_FILE)[:8]:
        if entry["medicine_id"] == third_batch.VALBENAZINE:  # ticket 2.39 marked it
            assert set(entry) == {"medicine_id", "name", "disease_id", "date", "label",
                                  "limited"}
            continue
        assert set(entry) == {"medicine_id", "name", "disease_id", "date", "label"}


def test_the_five_required_keys_are_as_they_were():
    assert engine.APPROVAL_KEYS == {"medicine_id", "name", "disease_id", "date", "label"}


def test_the_engine_reads_the_two_new_entries_as_limited():
    assert engine.approvals_by_hand()[8:10] == [  # ticket 2.34 added five after these
        engine.HandApproval(IMATINIB, "Imatinib", MASTOCYTOSIS, IMATINIB_LABEL, limited=True),
        engine.HandApproval(PROPYLTHIOURACIL, "Propylthiouracil", GRAVES,
                            PROPYLTHIOURACIL_LABEL, limited=True)]


def test_the_eight_earlier_entries_are_not_limited():
    earlier = engine.approvals_by_hand()[:8]
    assert [entry.medicine_id for entry in earlier] == [e["medicine_id"] for e in FIRST_EIGHT]
    assert [entry.limited for entry in earlier] == [False] * 7 + [True]  # ticket 2.39
    # Written the old way, with four things, an entry is as it was.
    assert engine.HandApproval("CHEMBL1", "Name", "MONDO_1", "https://example.org/label") \
        == engine.HandApproval("CHEMBL1", "Name", "MONDO_1", "https://example.org/label",
                               limited=False)


def test_each_new_entry_is_handed_only_to_its_own_disease():
    assert [entry.medicine_id for entry in engine.added_by_hand(GRAVES)] == [
        METHIMAZOLE, PROPYLTHIOURACIL]
    assert [entry.medicine_id for entry in engine.added_by_hand(MASTOCYTOSIS)] == [
        AVAPRITINIB, IMATINIB]
    for other in ("MONDO_0003233", "MONDO_0007739", "MONDO_0019100", "MONDO_0005342",
                  "MONDO_0019438", "MONDO_0020334", "MONDO_0007950"):
        assert not {IMATINIB, PROPYLTHIOURACIL} & {
            entry.medicine_id for entry in engine.added_by_hand(other)}


# ---- guards: how "limited" may be written ----

@pytest.mark.parametrize("value", [False, "yes", "true", 1, 0, None, [], {}],
                         ids=repr)
def test_guard_any_value_other_than_true_is_refused(value):
    with pytest.raises(ValueError):
        read([dict(FIRST_EIGHT[0], limited=value)])


@pytest.mark.parametrize("more", [
    {"doctor": "a name"},
    {"people": "adults"},  # Moonlight never writes which people
    {"limit": True},
    {"Limited": True},
    {"limited": True, "people": "adults"},
], ids=lambda more: "+".join(more))
def test_guard_any_unknown_key_is_refused(more):
    with pytest.raises(ValueError):
        read([dict(FIRST_EIGHT[0], **more)])


@pytest.mark.parametrize("missing", ["medicine_id", "name", "disease_id", "date", "label"])
def test_guard_a_limited_entry_still_needs_all_five_things(missing):
    entry = {key: value for key, value in NEW_TWO[0].items() if key != missing}
    with pytest.raises(ValueError):
        read([entry])


def test_guard_the_same_entry_written_once_limited_and_once_not_is_refused():
    plain = {key: value for key, value in NEW_TWO[0].items() if key != "limited"}
    with pytest.raises(ValueError):
        read([NEW_TWO[0], plain])


def test_guard_an_entry_without_the_key_never_gets_the_line():
    plain = [{key: value for key, value in entry.items() if key != "limited"}
             for entry in NEW_TWO]
    assert [entry.limited for entry in read(plain)] == [False, False]
    card = own_list_card(GRAVES, PROPYLTHIOURACIL, FIRST_EIGHT + plain)
    assert KEY not in card
    assert card == {key: value for key, value in PROPYLTHIOURACIL_CARD.items() if key != KEY}


# ---- the ids, from saved answers: the parent medicine's id, not a salt form's ----

def test_the_ids_are_the_ones_open_targets_uses_in_the_saved_lists():
    drugs = {row["drug"]["id"]: row["drug"] for row in saved_rows(GRAVES)}
    assert drugs[PROPYLTHIOURACIL]["name"] == "PROPYLTHIOURACIL"
    assert drugs[PROPYLTHIOURACIL]["parentMolecule"] is None  # the medicine itself
    assert drugs[PROPYLTHIOURACIL]["childMolecules"] == []  # and it has no tablet form
    drugs = {row["drug"]["id"]: row["drug"] for row in saved_rows(MASTOCYTOSIS)}
    assert drugs[IMATINIB]["name"] == "IMATINIB"
    assert drugs[IMATINIB]["parentMolecule"] is None  # the medicine, not a tablet form
    assert [(form["id"], form["name"]) for form in drugs[IMATINIB]["childMolecules"]] == [
        (IMATINIB_TABLET, "IMATINIB MESYLATE")]
    assert IMATINIB_TABLET not in drugs  # the tablet form has no row of its own


@pytest.mark.parametrize("entry, stage, tablets", [
    (NEW_TWO[0], "PHASE_2", [IMATINIB_TABLET]), (NEW_TWO[1], "PHASE_3", [])],
    ids=["Imatinib", "Propylthiouracil"])
def test_the_database_lists_them_only_as_in_trials_so_the_first_line_is_true(
        entry, stage, tablets):
    family = [entry["medicine_id"]] + tablets
    rows = [row for row in saved_rows(entry["disease_id"])
            if row["drug"]["id"] in family
            or (row["drug"]["parentMolecule"] or {}).get("id") in family]
    assert [row["drug"]["id"] for row in rows] == [entry["medicine_id"]]
    assert rows[0]["maxClinicalStage"] == stage
    assert "APPROVAL" not in [report["clinicalStage"] for report in rows[0]["clinicalReports"]]


@pytest.mark.parametrize("entry, warnings", [
    (NEW_TWO[0], []), (NEW_TWO[1], ["Black Box Warning"])],
    ids=["Imatinib", "Propylthiouracil"])
def test_neither_is_hidden_by_the_older_withdrawn_flag(entry, warnings):
    drug = [row["drug"] for row in saved_rows(entry["disease_id"])
            if row["drug"]["id"] == entry["medicine_id"]][0]
    found = [warning["warningType"] for one in [drug] + drug["childMolecules"]
             for warning in one["drugWarnings"]]
    assert found == warnings
    assert "withdrawn" not in [warning.lower() for warning in found]


def test_the_new_entries_clash_with_no_existing_rule():
    ids = {IMATINIB, IMATINIB_TABLET, PROPYLTHIOURACIL}
    for file in (CORRECTIONS_FILE, LEFT_OUT_FILE):
        assert not [one for one in load(file) if one["medicine_id"] in ids]
    assert engine.approvals_left_out() == []


# ---- the engine's card ----

@pytest.mark.parametrize("entry", NEW_TWO, ids=lambda entry: entry["name"])
def test_before_each_was_in_the_more_in_trials_box_and_not_under_approved(entry):
    places = first_batch.everywhere(second_batch.tabs_for(entry["disease_id"], []))
    assert [place for place, ids in places.items() if entry["medicine_id"] in ids] == [
        "more_in_trials"]


@pytest.mark.parametrize("entry, older", [(NEW_TWO[0], AVAPRITINIB),
                                          (NEW_TWO[1], METHIMAZOLE)],
                         ids=["Imatinib", "Propylthiouracil"])
def test_each_is_now_only_under_approved_with_both_lines_and_its_label(entry, older):
    disease_id = entry["disease_id"]
    with patch.object(engine, "_read_approvals", return_value=FIRST_EIGHT):
        before = second_batch.tabs_for(disease_id, engine.added_by_hand(disease_id))
    tabs = second_batch.tabs_for(disease_id, engine.added_by_hand(disease_id))
    assert first_batch.only_under_approved(tabs, entry["medicine_id"])
    card = [medicine for medicine in tabs.approved if medicine.id == entry["medicine_id"]][0]
    assert card.name == entry["name"]
    assert card.proof_note == ADDED_LINE
    assert card.limit_note == LINE
    assert card.source_record == entry["label"]
    assert card.label is None  # the main list, not a folded box
    assert len(tabs.approved) == len(before.approved) + 1
    names = [medicine.name.lower() for medicine in tabs.approved]
    assert names == sorted(names)  # A to Z
    # The older hand-added card of the same disease has the first line only.
    other = [medicine for medicine in tabs.approved if medicine.id == older][0]
    assert other.proof_note == ADDED_LINE
    assert other.limit_note is None
    # Every other card stays where it was, and no other card has the line.
    assert [medicine.id for medicine in tabs.approved if medicine.limit_note] == [
        entry["medicine_id"]]
    for place, ids in first_batch.everywhere(before).items():
        if place != "approved":
            assert first_batch.everywhere(tabs)[place] == [
                i for i in ids if i != entry["medicine_id"]]


def test_imatinibs_card_from_the_saved_list_of_systemic_mastocytosis():
    assert own_list_card(MASTOCYTOSIS, IMATINIB) == {
        "id": IMATINIB,
        "medicine": "Imatinib",
        "forms": ["Imatinib"],  # its tablet form has no row on this list
        "proteins": [],
        "reports": 2,
        "source": IMATINIB_LABEL,
        "proof_note": ADDED_LINE,
        "limit_note": LINE,
    }


def test_guard_a_card_the_database_records_never_has_the_line():
    """Only a hand-added card can have it: limit_note needs the label link."""
    plain = engine.ApprovedMedicine(id="CHEMBL1", name="Name", forms=("Name",), clue=None,
                                    listed_sources=())
    assert plain.limit_note is None
    assert KEY not in api._approved_json(plain)


@pytest.mark.parametrize("disease_id, medicine_id, name, reports, label", EARLIER_CARDS,
                         ids=[card[2] for card in EARLIER_CARDS])
def test_guard_the_eight_earlier_entries_give_the_cards_they_gave_on_main(
        disease_id, medicine_id, name, reports, label):
    card = {"id": medicine_id, "medicine": name, "forms": [name], "proteins": [],
            "reports": reports, "source": label, "proof_note": ADDED_LINE}
    if medicine_id == third_batch.VALBENAZINE:  # ticket 2.39: one more line
        card[KEY] = LINE
    assert own_list_card(disease_id, medicine_id) == card


# ---- the EXAMPLE, on the whole saved page: Graves disease ----

def test_before_propylthiouracil_was_only_in_the_more_in_trials_box():
    old = page(GRAVES, FIRST_EIGHT)
    assert old["disease"] == {"id": GRAVES, "name": "Graves disease"}
    assert [card["medicine"] for card in old["approved"]] == [
        "Ipodate", "Methimazole", "Teprotumumab"]
    assert [key for key, _ in first_batch.cards_naming(old, "propylthiouracil")] == [
        "more_in_trials"]
    assert len(old["more_in_trials"]) == 17
    assert cards_with_the_key(old) == []


def test_propylthiouracil_is_under_approved_a_to_z():
    approved = page(GRAVES)["approved"]
    assert [card["medicine"] for card in approved] == [
        "Ipodate", "Methimazole", "Propylthiouracil", "Teprotumumab"]
    assert approved[2] == PROPYLTHIOURACIL_CARD


def test_its_card_has_the_two_grey_lines_in_order_and_the_label_as_source():
    card = page(GRAVES)["approved"][2]
    assert card["proof_note"] == ADDED_LINE  # unchanged
    assert card[KEY] == LINE
    keys = list(card)
    assert keys.index("proof_note") < keys.index(KEY)
    assert card["source"] == PROPYLTHIOURACIL_LABEL
    assert "warning" not in card and "label" not in card and "withdrawal_note" not in card


def test_methimazole_on_the_same_page_shows_the_first_line_only():
    card = page(GRAVES)["approved"][1]
    assert card == first_batch.METHIMAZOLE_CARD
    assert KEY not in card


def test_propylthiouracil_is_nowhere_else_on_the_page_and_nothing_else_changes():
    old = page(GRAVES, FIRST_EIGHT)
    new = page(GRAVES)
    assert [key for key, _ in first_batch.cards_naming(new, "propylthiouracil")] == ["approved"]
    assert cards_with_the_key(new) == [("approved", PROPYLTHIOURACIL)]
    expected = copy.deepcopy(old)
    expected["approved"] = old["approved"][:2] + [PROPYLTHIOURACIL_CARD] + old["approved"][2:]
    expected["more_in_trials"] = [card for card in old["more_in_trials"]
                                  if card["id"] != PROPYLTHIOURACIL]
    assert len(expected["more_in_trials"]) == 16
    assert new == expected


def test_the_line_on_the_page_is_the_engines():
    other = "Other words, to show whose they are."
    with patch.object(engine, "LIMITED_LINE", other):
        assert page(GRAVES)["approved"][2][KEY] == other


# Ticket 2.39 took Huntington disease (MONDO_0007739) out of this list: its
# two cards now carry the line. tests/test_huntington_limit_line.py checks it.
@pytest.mark.parametrize("disease_id", ["MONDO_0003233", "MONDO_0019438"])
def test_guard_the_other_saved_pages_are_as_they_were_and_have_no_such_line(disease_id):
    """Essential tremor and AL amyloidosis: whole saved pages with a
    hand-added card each. Not one letter moves."""
    new = page(disease_id)
    assert new == page(disease_id, FIRST_EIGHT)
    assert cards_with_the_key(new) == []
    assert LINE not in json.dumps(new)


# ---- web/index.html, read as text ----

TEMPLATE = PAGE[PAGE.index('<template id="card-template">'):]
TEMPLATE = TEMPLATE[:TEMPLATE.index("</template>")]


def test_page_types_none_of_the_words_itself():
    assert LINE not in PAGE
    assert "only some people" not in PAGE.lower()
    assert "label covers" not in PAGE.lower()


def test_page_the_card_has_its_own_slot_in_the_same_grey_style():
    assert '<p class="proof-note" data-slot="limit-note" hidden></p>' in TEMPLATE
    assert TEMPLATE.count('data-slot="limit-note"') == 1
    assert TEMPLATE.count('data-slot="proof-note"') == 1  # the older slots are still there
    assert TEMPLATE.count('data-slot="withdrawal-note"') == 1


def test_page_the_slot_is_right_under_the_first_grey_line_and_above_the_withdrawal_line():
    lines = [line.strip() for line in TEMPLATE.splitlines()]
    first = lines.index('<p class="proof-note" data-slot="proof-note" hidden></p>')
    assert lines[first + 1] == '<p class="proof-note" data-slot="limit-note" hidden></p>'
    assert lines[first + 2] == '<p class="proof-note" data-slot="withdrawal-note" hidden></p>'
    assert TEMPLATE.index('data-slot="withdrawal-note"') < TEMPLATE.index('data-slot="warning"')


def test_page_prints_what_the_api_sends():
    assert 'slot(el, "limit-note").textContent = medicine.limit_note;' in PAGE


def test_page_the_safety_line_is_still_there():
    assert ("For learning and research exploration, not medical advice. Never start, stop "
            "or change any medicine without a doctor.") in " ".join(PAGE.split())


# ---- the page, in a real browser, at phone width ----

BROWSER_SCRIPT = r"""
"use strict";
const fs = require("fs");
const { chromium } = require("playwright");
const PAGE = fs.readFileSync(process.argv[1], "utf-8");
const ANSWER = JSON.parse(fs.readFileSync(process.argv[2], "utf-8"));
const PICTURE = process.argv[3] || "";
const SITE = "http://moonlight.test";

function readApproved() {
  const words = el => el.innerText.replace(/\s+/g, " ").trim();
  const style = el => {
    const s = getComputedStyle(el);
    return [s.color, s.backgroundColor, s.fontSize, s.fontWeight, s.borderTopColor,
            s.paddingTop, s.paddingLeft, s.borderRadius].join("|");
  };
  const readCard = card => {
    const shown = [...card.querySelectorAll(".proof-note, .wrong-warning")]
      .filter(el => !el.hidden && el.getClientRects().length);
    const box = card.getBoundingClientRect();
    return {
      name: card.querySelector('[data-slot="medicine-name"]').textContent,
      lines: shown.map(el => ({ slot: el.dataset.slot, words: words(el), cls: el.className })),
      sameStyle: shown.every(el => style(el) === style(shown[0])),
      gaps: shown.slice(1).map((el, i) =>
        el.getBoundingClientRect().top - shown[i].getBoundingClientRect().bottom),
      fits: shown.every(el => el.getBoundingClientRect().left >= box.left
        && el.getBoundingClientRect().right <= box.right),
    };
  };
  return {
    approved: [...document.querySelectorAll("#approved-cards > .card")].map(readCard),
    elsewhere: [...document.querySelectorAll('[data-slot="limit-note"]')]
      .filter(el => !el.hidden && !el.closest("#approved-cards")).length,
    sideways: document.documentElement.scrollWidth > window.innerWidth,
  };
}

(async () => {
  const browser = await chromium.launch();
  const context = await browser.newContext({
    viewport: { width: 390, height: 844 }, deviceScaleFactor: PICTURE ? 2 : 1 });
  const page = await context.newPage();
  const errors = [];
  page.on("pageerror", problem => errors.push(String(problem)));
  await context.route("**/*", route => {
    const url = route.request().url();
    if (url === SITE + "/" || url.startsWith(SITE + "/?"))
      return route.fulfill({ contentType: "text/html; charset=utf-8", body: PAGE });
    if (url.startsWith(SITE + "/api/clues?"))
      return route.fulfill({ contentType: "application/json", body: JSON.stringify(ANSWER) });
    if (url.startsWith(SITE + "/api/explain?"))
      return route.fulfill({ status: 404, contentType: "application/json", body: "{}" });
    return route.abort();
  });
  await page.goto(SITE + "/?disease=MONDO_TEST");
  await page.waitForSelector("#found", { state: "visible" });
  await page.click("#tab-approved");
  await page.waitForTimeout(300);
  const out = { errors, read: await page.evaluate(readApproved) };
  if (PICTURE) {
    const card = page.locator("#approved-cards > .card").filter({ hasText: "Propylthiouracil" });
    await card.scrollIntoViewIfNeeded();
    await card.screenshot({ path: PICTURE });
  }
  await browser.close();
  console.log(JSON.stringify(out));
})().catch(problem => { console.error(problem); process.exit(1); });
"""


def open_the_page(answer, folder, picture=""):
    """Opens the page in a real browser, 390 wide, and returns what a reader sees."""
    node = shutil.which("node")
    if not node or subprocess.run(
            [node, "-e", "require('playwright')"], capture_output=True).returncode:
        pytest.skip("needs node with playwright to open a real browser")
    answer_file = folder / "answer.json"
    answer_file.write_text(json.dumps(answer), encoding="utf-8")
    run = subprocess.run(
        [node, "-e", BROWSER_SCRIPT, str(ROOT / "web" / "index.html"), str(answer_file),
         picture],
        capture_output=True, text=True, timeout=240, cwd=str(ROOT))
    assert run.returncode == 0, run.stderr[-3000:]
    return json.loads(run.stdout)


def test_browser_at_phone_width_the_card_shows_the_two_grey_lines_stacked(tmp_path):
    seen = open_the_page(page(GRAVES), tmp_path)
    assert seen["errors"] == []
    read = seen["read"]
    assert not read["sideways"]  # nothing sticks out at 390 wide
    assert read["elsewhere"] == 0
    cards = {card["name"]: card for card in read["approved"]}
    assert list(cards) == ["Ipodate", "Methimazole", "Propylthiouracil", "Teprotumumab"]
    card = cards["Propylthiouracil"]
    assert card["lines"] == [
        {"slot": "proof-note", "words": ADDED_LINE, "cls": "proof-note"},
        {"slot": "limit-note", "words": LINE, "cls": "proof-note"}]
    assert card["sameStyle"] and card["fits"]
    assert card["gaps"] == [12]  # the same gap the grey lines already keep
    assert cards["Methimazole"]["lines"] == [
        {"slot": "proof-note", "words": ADDED_LINE, "cls": "proof-note"}]
    for name in ("Ipodate", "Teprotumumab"):
        assert "limit-note" not in [line["slot"] for line in cards[name]["lines"]]
