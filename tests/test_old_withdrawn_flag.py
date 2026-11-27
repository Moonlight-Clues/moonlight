"""Ticket 2.40. The older "Withdrawn" flag: eight cards come back, with the line.

Since ticket 2.11 a medicine carrying the older "Withdrawn" warning flag is
in no tab. Study P11 (branch probe-old-withdrawn-flag) found 88 such cards
across 50 diseases. Kashish's signed answer, 24 Nov 2026:

    Show the ones with a regulator approval, with the grey withdrawal line.
    Keep the rest hidden.

and answer B to the follow-up of the same day: all eight with a regulator's
approval report come back, rosiglitazone too, although its list also holds
a WITHDRAWAL report.

The rule: a medicine the older flag would hide is on the Approved tab's main
list when it is on the searched disease's OWN list, approved there, and that
list holds an APPROVAL report for it from a regulator (fetch.REGULATOR_SOURCES).
Its card carries engine.WITHDRAWAL_LINE. Everything else the flag hides stays
hidden: approval reports only from TTD or ATC, no approval report, and every
card that would sit in the narrower or wider boxes.

Before the code, the labels behind the eight cards' regulator reports were
saved in fixtures/labels_read/ticket_2.40/. Prasterone's label (lupus) does not name
rheumatoid arthritis, so its card also carries the red label warning (rule 6),
and so sits in the red-warning box of the Approved tab (ticket 2.27).

Saved answers only: fixtures/old_withdrawn_flag/ (see old_flag_saved.py).
"""

import json
import pathlib
from unittest.mock import patch

import pytest

from moonlight import engine
from moonlight.fetch import Listed
from moonlight.filter import sort_paths
from moonlight.records import Disease, Medicine, MedicineForm, Path, Target

import old_flag_saved as saved
from source_2_53 import back_to_before  # ticket 2.53: Source record links
from test_red_warnings_2_62 import RED_ROWS, opposite_ids, without_opposite_lines  # ticket 2.62
from source_3_11 import back_to_before as trials_back_to_before  # ticket 3.11: In trials links
from diagnostic_3_10 import back_to_before as tag_back_to_before  # ticket 3.10: the DIAGNOSTIC tag
from source_3_17 import back_to_before as labels_back_to_before  # ticket 3.17: own-label links
from broad_3_18 import back_to_before as broad_back_to_before  # ticket 3.18: broad wider groups
from source_3_13 import back_to_before as trials_back_to_3_11  # ticket 3.13: In trials links

ROOT = pathlib.Path(__file__).resolve().parent.parent
CORRECTIONS_FILE = ROOT / "moonlight" / "corrections.json"

# Kashish's words of 23 Nov, exactly.
LINE = "The database records a withdrawal for this medicine in some country or region."
LABEL_WARNING = ("This looks like a mistake in the database. The official label is for a "
                 "different disease.")

ASTHMA = "MONDO_0004979"
T2D = "MONDO_0005148"
EPILEPSY = "MONDO_0005027"
RA = "MONDO_0008383"
PARKINSON = "MONDO_0005180"
AML = "MONDO_0018874"
CUSHING = "MONDO_0018912"
DEPRESSION = "MONDO_0002050"
CML = "MONDO_0011996"
DISEASES = [ASTHMA, T2D, EPILEPSY, RA, PARKINSON, AML, CUSHING, DEPRESSION, CML]

PRASTERONE = "CHEMBL90593"
US_2_59 = {"CHEMBL817", "CHEMBL782"}  # tolazamide, tolbutamide (ticket 2.59)
US_LINE_2_59 = "Its approval was withdrawn in the US. It may still be sold elsewhere."
# The eight of P11's CSV (hidden_by_old_flag.csv): main list, a regulator's
# approval report on the disease's own list. (disease, id, name on the card)
EIGHT = [
    (ASTHMA, "CHEMBL211456", "Ephedrine"),
    (ASTHMA, "CHEMBL776", "Metaproterenol"),
    (T2D, "CHEMBL121", "Rosiglitazone"),
    (EPILEPSY, "CHEMBL87493", "Fenfluramine"),
    (RA, PRASTERONE, "Prasterone"),
    (PARKINSON, "CHEMBL1324", "Tolcapone"),
    (AML, "CHEMBL1201506", "Gemtuzumab Ozogamicin"),
    (CUSHING, "CHEMBL157101", "Ketoconazole"),
]
# Ticket 2.45 put the red warning on these cards of the same three pages (the
# card keeps its place; it moves into the red-warning box, so it leaves the tab number).
RED_2_45 = {
    # Ticket 3.10 (MAIN 4, 25 Nov, Q14): mannitol's red entry on asthma was deleted, so it is
    # a plain card again (with the DIAGNOSTIC tag). It was CHEMBL689 here.
    # Ticket 2.58 (25N-13): ipratropium (CHEMBL1621597) lost its red note too.
    ASTHMA: {"CHEMBL1512"},  # flunisolide
    AML: {"CHEMBL4297573"},  # tagraxofusp
    "MONDO_0002050": {"CHEMBL49"},  # buspirone, depressive disorder
    # Ticket 2.52 put the red warning on six cards of type 2 diabetes (biotin,
    # cyanocobalamin, folic acid, omega-3-acid ethyl esters, pyridoxine, tyrosine).
    # Ticket 2.54, signed answer Q22, put it on simvastatin (CHEMBL1064) too.
    T2D: {"CHEMBL857", "CHEMBL2110563", "CHEMBL1622", "CHEMBL1200711", "CHEMBL1364",
          "CHEMBL925", "CHEMBL1064"},
}
# Ticket 2.58 (25N-16): six cards of type 2 diabetes got the red note while they
# stay in the wider-group box: candesartan, olmesartan, atenolol, chlorthalidone,
# hydrochlorothiazide, lisinopril. Ticket 3.16 (Q7): their cards stay in
# "wider_group", and the red box names them, so the page shows them there.
WIDER_RED_2_58 = {
    T2D: {"CHEMBL1014", "CHEMBL1200692", "CHEMBL24", "CHEMBL1055", "CHEMBL435", "CHEMBL1237"},
}
# Ticket 2.48 set the Source record of this card (moonlight/confirmed.json):
# card id -> (the link the saved page shows, the label it shows now).
SOURCE_2_48 = {
    ASTHMA: {"CHEMBL1900528": (  # tiotropium
        "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=1cf82d42-5ad0-4b86-838e-9230c61cf3d4",
        "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=7b656b14-fcaa-2741-f6f0-e0be48971c02")},
    # Ticket 2.52 set the Source record of two cards of type 2 diabetes
    # (moonlight/confirmed.json): liraglutide (Xultophy -> Victoza) and
    # canagliflozin (Invokamet -> Invokana).
    T2D: {
        "CHEMBL4084119": (
            "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=21335fe4-d395-4501-ac2a-2f20d7520da9",
            "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=5a9ef4ea-c76a-4d34-a604-27c5b505f5a4"),
        "CHEMBL2048484": (
            "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=6868666b-c25e-40d1-9d1f-306bbe9390c1",
            "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=b9057d3b-b104-4f09-8a61-c61ef9d4a3f3"),
        # Ticket 2.54, item 12: ertugliflozin (Steglujan -> Steglatro).
        "CHEMBL1770248": (
            "https://ttd.idrblab.cn/data/drug/details/D0Q3VE",
            "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=e6f3e718-bb99-48f1-ab94-b9f0af05fed6"),
    },
}
BACK = {}
for _disease, _id, _ in EIGHT:
    BACK.setdefault(_disease, []).append(_id)

# Hidden today and hidden after, from the same CSV. (disease, id, why)
STAY_HIDDEN = [
    (ASTHMA, "CHEMBL32800", "fenoterol: main list, approval report from TTD only"),
    (EPILEPSY, "CHEMBL40", "phenobarbital: main list, approval reports from ATC and TTD"),
    (RA, "CHEMBL94081", "alclofenac: main list, approval report from TTD only"),
    (RA, "CHEMBL865", "valdecoxib: main list, no approval report, a WITHDRAWAL report"),
    (DEPRESSION, "CHEMBL37744", "zimeldine: main list, no approval report at all"),
    (DEPRESSION, "CHEMBL273575", "nomifensine: narrower box"),
    (T2D, "CHEMBL408", "troglitazone: wider-group box"),
    (RA, "CHEMBL122", "rofecoxib: wider-group box"),
    (CML, "CHEMBL1201506", "gemtuzumab ozogamicin: wider-group box, DailyMed on that list"),
]

CARD_PARTS = ("approved", "narrower", "wider_group", "being_studied", "new_clues",
              "more_in_trials", "new_in_trials")


@pytest.fixture(scope="module")
def pages():
    return {disease_id: saved.page_answer(disease_id) for disease_id in DISEASES}


# Ticket 2.62 put the red note on the signed rows of tests/test_red_warnings_2_62.py.
# A main-list card is treated like the 2.45 ones (red box, out of the tab number); a
# wider-group card like the 2.58 ones. Delete a row there and these follow.
for _, _medicine, _disease, _, _box in RED_ROWS:
    if _box == "approved":
        RED_2_45.setdefault(_disease, set()).add(_medicine)
    elif _box == "wider_group":
        WIDER_RED_2_58.setdefault(_disease, set()).add(_medicine)


def card_ids(answer, part):
    ids = []
    for card in answer.get(part, []):
        ids.append(card["id"] if "id" in card else card.get("medicine_id"))
    return ids


def every_id_on(answer):
    """Every medicine id on any tab or in any box of the page."""
    found = set()
    for part in CARD_PARTS:
        for card in answer.get(part, []):
            found.add(card.get("id"))
            found.update(protein.get("medicine_id") for protein in card.get("proteins", [])
                         if isinstance(protein, dict))
    return found - {None}


def main_list(answer):
    boxed = set(answer.get("wrong_approvals_box", []))
    return [card for card in answer["approved"] if card["id"] not in boxed]


def tab_number(answer):
    """The Approved tab's number, as the page counts it (ticket 2.27)."""
    return len(main_list(answer)) + len(answer.get("narrower", [])) + len(
        answer.get("wider_group", []))


# ---- the saved lists say what P11 said ----

def test_the_saved_answers_hide_all_eight_today():
    for disease_id, medicine_id, name in EIGHT:
        before = saved.before(disease_id)
        assert medicine_id not in [card["id"] for part in ("approved", "narrower", "wider_group")
                                   for card in before.get(part, [])], name


# ---- the eight come back ----

@pytest.mark.parametrize("disease_id, medicine_id, name", EIGHT, ids=[e[2] for e in EIGHT])
def test_each_of_the_eight_is_on_its_approved_list_with_the_line(pages, disease_id,
                                                                 medicine_id, name):
    answer = pages[disease_id]
    cards = {card["id"]: card for card in answer["approved"]}
    assert medicine_id in cards, name
    card = cards[medicine_id]
    assert card["medicine"] == name
    assert card["withdrawal_note"] == LINE
    # Only the Approved tab: no box of it, no other tab.
    for part in CARD_PARTS[1:]:
        assert medicine_id not in [one.get("id") for one in answer.get(part, [])], part


@pytest.mark.parametrize("disease_id, medicine_id, name", EIGHT, ids=[e[2] for e in EIGHT])
def test_each_card_shows_a_regulators_receipt_or_the_japan_line(pages, disease_id,
                                                                medicine_id, name):
    card = {card["id"]: card for card in pages[disease_id]["approved"]}[medicine_id]
    assert card["source"].startswith("https://")
    # A regulator's report is there, so never the "no regulator record" line.
    assert card.get("proof_note") != engine.NO_REGULATOR_LINE


def test_seven_are_on_the_main_list_and_prasterone_is_in_the_red_warning_box(pages):
    for disease_id, medicine_id, name in EIGHT:
        answer = pages[disease_id]
        on_main = medicine_id in [card["id"] for card in main_list(answer)]
        assert on_main == (medicine_id != PRASTERONE), name
    ra = pages[RA]
    # The box keeps the main list's own order, A to Z (ticket 2.27).
    expected = (set(saved.before(RA)["wrong_approvals_box"]) | {PRASTERONE}
                | RED_2_45.get(RA, set()) | WIDER_RED_2_58.get(RA, set()))  # ticket 2.62
    # (ticket 2.62: a wider-group card is in the box too; A to Z across the lists, ticket 3.16)
    across = sorted(ra["approved"] + ra.get("narrower", []) + ra["wider_group"],
                    key=lambda card: (card["medicine"].casefold(), card["medicine"]))
    assert ra["wrong_approvals_box"] == [card["id"] for card in across if card["id"] in expected]
    card = {card["id"]: card for card in ra["approved"]}[PRASTERONE]
    assert card["warning"] == LABEL_WARNING
    assert card["withdrawal_note"] == LINE


def test_rosiglitazone_comes_back_although_its_list_holds_a_withdrawal_report(pages):
    # Kashish's answer B of 24 Nov.
    card = {card["id"]: card for card in pages[T2D]["approved"]}["CHEMBL121"]
    assert card["withdrawal_note"] == LINE
    assert "warning" not in card


def test_exactly_the_eight_come_back_and_nothing_else(pages):
    came_back = []
    for disease_id in DISEASES:
        before = {card["id"] for card in saved.before(disease_id)["approved"]}
        after = [card["id"] for card in pages[disease_id]["approved"]]
        came_back += [(disease_id, medicine_id) for medicine_id in after if medicine_id not in before]
    assert sorted(came_back) == sorted((disease_id, medicine_id)
                                       for disease_id, medicine_id, _ in EIGHT)


# ---- the rest stay hidden ----

@pytest.mark.parametrize("disease_id, medicine_id, why", STAY_HIDDEN,
                         ids=[e[2].split(":")[0] for e in STAY_HIDDEN])
def test_the_others_the_flag_hides_stay_in_no_tab(pages, disease_id, medicine_id, why):
    answer = pages[disease_id]
    for part in CARD_PARTS:
        assert medicine_id not in [card.get("id") for card in answer.get(part, [])], (why, part)
    assert f'"{medicine_id}"' not in json.dumps(answer), why  # the exact id, quoted


# ---- nothing shown today moves ----

@pytest.mark.parametrize("disease_id", DISEASES)
def test_every_card_shown_today_is_where_it_was_letter_for_letter(pages, disease_id):
    before = saved.before(disease_id)
    after = back_to_before(trials_back_to_before(trials_back_to_3_11(tag_back_to_before(labels_back_to_before(
        broad_back_to_before(pages[disease_id], disease_id))))))  # ticket 3.18 first
    back = set(BACK.get(disease_id, []))
    red = RED_2_45.get(disease_id, set())
    plain = [({key: value for key, value in card.items() if key != "warning"}
              if card["id"] in red else card) for card in after["approved"]]
    assert all("warning" in card for card in after["approved"] if card["id"] in red)
    sources = SOURCE_2_48.get(disease_id, {})
    assert all(card["source"] == sources[card["id"]][1]
               for card in plain if card["id"] in sources)
    plain = [dict(card, source=sources[card["id"]][0]) if card["id"] in sources else card
             for card in plain]
    # Ticket 2.59 (MAIN 4 approved): tolazamide and tolbutamide on type 2 diabetes
    # carry the US region sentence. Only that line is added; the rest is as saved.
    if disease_id == T2D:
        assert all(card.get("withdrawal_note") == US_LINE_2_59
                   for card in plain if card["id"] in US_2_59)
        plain = [{k: v for k, v in card.items() if k != "withdrawal_note"}
                 if card["id"] in US_2_59 else card for card in plain]
    if disease_id == T2D:  # ticket 2.64: anagliptin, tofogliflozin open their Japanese labels
        from test_list_fixes_2_64 import ANAGLIPTIN, DEBERZA, SUINY, TOFOGLIFLOZIN  # ticket 2.64
        japanese = {ANAGLIPTIN: SUINY, TOFOGLIFLOZIN: DEBERZA}  # ticket 2.64
        assert all(card["source"] == japanese[card["id"]] for card in plain if card["id"] in japanese)  # ticket 2.64
        was = {card["id"]: card["source"] for card in before["approved"]}  # ticket 2.64
        plain = [dict(card, source=was[card["id"]]) if card["id"] in japanese else card for card in plain]  # ticket 2.64
    assert [card for card in plain if card["id"] not in back] == before["approved"]
    wider_red = WIDER_RED_2_58.get(disease_id, set())
    assert all("warning" in card for card in after.get("wider_group", []) if card["id"] in wider_red)
    after = dict(after, **({"wider_group": [
        ({key: value for key, value in card.items() if key != "warning"}
         if card["id"] in wider_red else card) for card in after["wider_group"]]}
        if wider_red else {}))
    for key in before:
        if key in ("approved", "left_out", "wrong_approvals_box"):
            continue
        if key == "new_clues":
            # Ticket 2.62: a card that is red is not one of "the approved medicines" that fix
            # the direction, so a new clue can lose its opposite-way line. Only that differs.
            assert without_opposite_lines(after[key]) == without_opposite_lines(before[key]), key
            assert opposite_ids(after[key]) <= opposite_ids(before[key])
            continue
        if key == "opposite_way_box":
            gone = set(before[key]) - set(after[key])
            assert after[key] == [i for i in before[key] if i not in gone], key
            assert not gone or disease_id in {d for _, _, d, _, _ in RED_ROWS}
            continue
        assert after[key] == before[key], key
    # Ticket 2.42 (merged after these pages were saved) adds the key
    # no_regulator_box and moves cards into that box. They stay in
    # "approved", so the check above already holds each card letter for letter.
    assert set(after) - set(before) <= {"wrong_approvals_box", "no_regulator_box"}
    approved_ids = [card["id"] for card in after["approved"]]
    assert all(medicine_id in approved_ids for medicine_id in after.get("no_regulator_box", []))
    boxed = [medicine_id for medicine_id in after.get("wrong_approvals_box", [])
             if medicine_id not in back and medicine_id not in red
             and medicine_id not in wider_red]  # ticket 3.16 (Q7): the six moved to the red box
    assert boxed == before.get("wrong_approvals_box", [])


@pytest.mark.parametrize("disease_id", DISEASES)
def test_the_tab_number_counts_the_cards_that_came_back(pages, disease_id):
    back_on_main = [medicine_id for medicine_id in BACK.get(disease_id, [])
                    if medicine_id != PRASTERONE]  # in the red-warning box, as every such card
    red = len(RED_2_45.get(disease_id, set()))  # ticket 2.45: in the red-warning box now
    page = broad_back_to_before(pages[disease_id], disease_id)  # ticket 3.18
    assert tab_number(page) == tab_number(saved.before(disease_id)) + len(back_on_main) - red


@pytest.mark.parametrize("disease_id", DISEASES)
def test_not_approved_goes_down_by_exactly_the_cards_that_came_back(pages, disease_id):
    before, after = saved.before(disease_id)["left_out"], pages[disease_id]["left_out"]
    assert before["not_approved"] - after["not_approved"] == len(BACK.get(disease_id, []))
    assert after["unclear_link"] == before["unclear_link"]


def test_the_total_count_goes_down_by_eight(pages):
    total = sum(saved.before(d)["left_out"]["not_approved"] - pages[d]["left_out"]["not_approved"]
                for d in DISEASES)
    assert total == 8


def test_no_new_question_to_open_targets():
    asked = []

    def counting(body):
        asked.append(json.dumps(body, sort_keys=True))
        return saved.saved_post_json(body)

    for disease_id in (ASTHMA, T2D):
        saved.page_answer(disease_id, counting)
    after = sorted(asked)
    del asked[:]
    with patch.object(engine, "_comes_back", return_value=False):
        for disease_id in (ASTHMA, T2D):
            saved.page_answer(disease_id, counting)
    assert after == sorted(asked)


def test_the_line_on_the_page_is_the_engines():
    other = "Other words, to show whose they are."
    with patch.object(engine, "WITHDRAWAL_LINE", other):
        answer = saved.page_answer(CUSHING)
    card = {card["id"]: card for card in answer["approved"]}["CHEMBL157101"]
    assert card["withdrawal_note"] == other


# ---- the hand-written files ----

def test_prasterone_has_the_label_warning_for_rheumatoid_arthritis_only():
    entries = json.loads(CORRECTIONS_FILE.read_text(encoding="utf-8"))
    # Ticket 2.45 added prasterone for osteoarthritis after this one: only the RA entry is read here.
    mine = [entry for entry in entries
            if entry["medicine_id"] == PRASTERONE and entry["disease_id"] == RA]
    assert [{k: v for k, v in entry.items() if k != "label"} for entry in mine] == [
        {"medicine_id": PRASTERONE, "disease_id": RA, "date": "2026-11-24",
         "note": LABEL_WARNING}]
    assert entries[38] == mine[0]  # added at the end of the 39 that were there then


def test_each_label_read_is_saved():
    folder = ROOT / "fixtures" / "labels_read" / "ticket_2.40"
    for name in ("prastera-prasterone.txt", "primatene-ephedrine.txt",
                 "metaproterenol-tablets.txt", "avandia-rosiglitazone-ef14122b.txt",
                 "pmda-general-list-fenfluramine.txt", "tasmar-tolcapone.txt",
                 "mylotarg-gemtuzumab-ozogamicin-ema.txt", "ketoconazole-esteve-ema.txt"):
        lines = (folder / name).read_text(encoding="utf-8").splitlines()
        assert lines[0].startswith("https://") and lines[1] == "2026-11-24", name
    prastera = (folder / "prastera-prasterone.txt").read_text(encoding="utf-8")
    assert "rheumatoid" not in prastera.lower()


# ---- the engine, with hand-built lists ----

DISEASE = Disease("TEST_0000001", "test disease")
PROTEIN = Target("ENSG00000000001", "ABC1", "test protein", 0.8)


def flagged_path(name, medicine_id):
    form = MedicineForm(medicine_id, name, best_stage="APPROVAL", disease_stage="APPROVAL",
                        withdrawn=True)
    return Path(Medicine(name, (form,)), PROTEIN, DISEASE, ("INHIBITOR",), PROTEIN.score,
                (f"https://example.org/{medicine_id}",))


def flagged(medicine_id, regulator_record=True, approved=True, withdrawal_report=False):
    return Listed(medicine_id, "FLAGMIL", ((medicine_id, "FLAGMIL"),),
                  ("https://example.org/label",), approved=approved,
                  approval_sources=("https://example.org/label",),
                  regulator_record=regulator_record, withdrawal_report=withdrawal_report)


def tabs_with(entry, neighbours=(), paths=()):
    return engine.sort_into_tabs(sort_paths(list(paths)), [], [entry] if entry else [],
                                 neighbours)


def test_engine_a_regulator_approval_on_the_own_list_brings_it_back_with_the_line():
    tabs = tabs_with(flagged("CHEMBL9001"), paths=[flagged_path("FLAGMIL", "CHEMBL9001")])
    assert [medicine.id for medicine in tabs.approved] == ["CHEMBL9001"]
    assert tabs.approved[0].clue is not None  # its path goes with it
    assert tabs.left_out["not_approved"] == 0
    assert engine.withdrawal_notes(tabs, []) == {"CHEMBL9001": LINE}


def test_engine_with_a_withdrawal_report_too_it_still_comes_back():
    tabs = tabs_with(flagged("CHEMBL9001", withdrawal_report=True))
    assert [medicine.id for medicine in tabs.approved] == ["CHEMBL9001"]


@pytest.mark.parametrize("entry", [
    flagged("CHEMBL9001", regulator_record=False),  # TTD or ATC only, or no approval report
    flagged("CHEMBL9001", regulator_record=None),  # not said
    flagged("CHEMBL9001", approved=False),  # on the list, not approved for this disease
], ids=["no-regulator", "not-said", "not-approved-here"])
def test_engine_without_all_three_it_stays_hidden(entry):
    tabs = tabs_with(entry, paths=[flagged_path("FLAGMIL", "CHEMBL9001")])
    assert tabs.approved == [] and tabs.new_clues == [] and tabs.being_studied == []
    assert engine.withdrawal_notes(tabs, []) == {}


def test_engine_a_flag_only_on_a_neighbours_list_stays_hidden():
    child = engine.Neighbour(engine.CHILD, Disease("TEST_0000002", "child disease"),
                             (), (flagged("CHEMBL9001"),))
    tabs = tabs_with(None, neighbours=[child])
    assert tabs.approved == [] and tabs.narrower == [] and tabs.wider_group == []


def test_engine_a_neighbours_flag_does_not_hide_one_that_comes_back():
    parent = engine.Neighbour(engine.PARENT, Disease("TEST_0000003", "parent disease"),
                              (), (flagged("CHEMBL9001"),))
    tabs = tabs_with(flagged("CHEMBL9001"), neighbours=[parent])
    assert [medicine.id for medicine in tabs.approved] == ["CHEMBL9001"]
    assert tabs.wider_group == [] and tabs.left_out["not_approved"] == 0


def test_engine_a_hand_added_approval_is_never_added_for_a_flagged_medicine():
    hand = engine.HandApproval("CHEMBL9001", "Flagmil", DISEASE.id, "https://example.org/l")
    entry = flagged("CHEMBL9001", regulator_record=False)
    tabs = engine.sort_into_tabs({}, [], [entry], by_hand=[hand])
    assert tabs.approved == []


# ---- the written rules ----

def test_decisions_md_has_her_answer():
    lines = (ROOT / "DECISIONS.md").read_text(encoding="utf-8").rstrip("\n").split("\n")
    # Ticket 2.54 added dated lines after hers (13), so find hers by its words.
    (hers,) = [line for line in lines if line.startswith("- 2026-11-24: ")
               and "regulator" in line and LINE in line]
    assert hers


def test_claude_md_rule_says_the_exception():
    rules = " ".join((ROOT / "CLAUDE.md").read_text(encoding="utf-8").split())
    assert ("A medicine withdrawn in any country does not count as approved, unless the "
            "disease's own list holds a regulator's approval of it for that disease: then it is "
            "on the Approved tab with the withdrawal line below.") in rules
