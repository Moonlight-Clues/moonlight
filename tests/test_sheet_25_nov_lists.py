"""Ticket 2.54. Hand-written list entries from Kashish's signed sheet of 25 Nov.

List entries only (moonlight/*.json). Saved answers, no network:
fixtures/sheet_25_nov/before/<disease>.clues.json is the live /api/clues
answer of 2026-11-25 with the old lists, and .../after/ the answer with the
new entries, both saved as sent (Open Targets data 26.09).

Not added, on purpose (the ticket's STOP AND ASK / DO NOT ADD):
  * dicumarol on haemophilia A: the signed note is not one of the two notes
    the engine accepts (engine.CORRECTION_NOTES), and engine.py is out of scope.
  * the four testosterone medicines of prostate cancer that sit in "Already
    being studied": a left-out entry never touches that box.
  * the two "other" Graves medicines: MAIN 4 names them next sheet.
"""

import json
import pathlib

import pytest

from moonlight import engine

ROOT = pathlib.Path(__file__).resolve().parent.parent
LISTS = ROOT / "moonlight"
SAVED = ROOT / "fixtures" / "sheet_25_nov"
THE_DAY = "2026-11-25"
SECOND_NOTE = ("This looks like a mistake in the database. The official label is for "
               "a different disease.")
DM = "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid="

ADDISON, AML, PARKINSON, GRAVES = "MONDO_0015129", "MONDO_0018874", "MONDO_0005180", "MONDO_0005364"
PROSTATE, HEM_A, TREMOR, ALS = "MONDO_0008315", "MONDO_0010602", "MONDO_0003233", "MONDO_0004976"
ADPKD, T2D, DUODENAL, HUNTINGTON = "MONDO_0004691", "MONDO_0005148", "MONDO_0005412", "MONDO_0007739"

NEW = {
    "approvals.json": [
        {"medicine_id": "CHEMBL389621", "name": "Hydrocortisone", "disease_id": ADDISON,
         "date": THE_DAY, "label": DM + "9ce19944-dd88-4a7b-84ca-b07f4ec23bad"},
        {"medicine_id": "CHEMBL856", "name": "Primidone", "disease_id": TREMOR,
         "date": THE_DAY, "label": "https://www.medicines.org.uk/emc/product/2940/smpc"},
    ],
    "limits.json": [
        {"medicine_id": "CHEMBL1201506", "disease_id": AML, "date": THE_DAY,
         "label": DM + "32fd2bb2-1cfa-4250-feb8-d7956c794e05"},
        {"medicine_id": "CHEMBL1324", "disease_id": PARKINSON, "date": THE_DAY,
         "label": "https://www.ema.europa.eu/en/documents/product-information/"
                  "tasmar-epar-product-information_en.pdf"},
    ],
    "withdrawals.json": [
        {"medicine_id": "CHEMBL1469", "disease_id": ALS, "date": THE_DAY,
         "source": "https://www.amylyx.com/news/amylyx-pharmaceuticals-announces-formal-"
                   "intention-to-remove-relyvrior/albriozatm-from-the-market-provides-"
                   "updates-on-access-to-therapy-pipeline-corporate-restructuring-and-strategy"},
    ],
    "left_out.json": [
        {"medicine_id": "CHEMBL1201532", "disease_id": GRAVES, "date": THE_DAY},  # thyrotropin
        {"medicine_id": "CHEMBL1201533", "disease_id": GRAVES, "date": THE_DAY},  # thyrotropin alfa
        {"medicine_id": "CHEMBL1789844", "disease_id": GRAVES, "date": THE_DAY},  # ipilimumab
        {"medicine_id": "CHEMBL1170", "disease_id": PROSTATE, "date": THE_DAY},   # testosterone propionate
        {"medicine_id": "CHEMBL1395", "disease_id": PROSTATE, "date": THE_DAY},   # methyltestosterone
        {"medicine_id": "CHEMBL2135460", "disease_id": ADPKD, "date": THE_DAY},   # terlipressin
    ],
    "corrections.json": [
        {"medicine_id": "CHEMBL1064", "disease_id": T2D, "date": THE_DAY, "note": SECOND_NOTE},
        {"medicine_id": "CHEMBL606", "disease_id": DUODENAL, "date": THE_DAY, "note": SECOND_NOTE},
    ],
    "confirmed.json": [
        {"medicine_id": "CHEMBL1770248", "disease_id": T2D, "date": THE_DAY,
         "label": DM + "e6f3e718-bb99-48f1-ab94-b9f0af05fed6"},
        {"medicine_id": "CHEMBL117785", "disease_id": HUNTINGTON, "date": THE_DAY,
         "label": DM + "ac768bab-8afa-4446-bc7f-caeeffec0cda"},
    ],
}
PAGES = [ADDISON, AML, PARKINSON, GRAVES, PROSTATE, HEM_A, TREMOR, ALS, ADPKD, T2D,
         HUNTINGTON, DUODENAL]


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def answer(state, disease_id):
    return load(SAVED / state / f"{disease_id}.clues.json")


def cards(page):
    """(tab, card) for every card of the page; box tabs holding bare ids are skipped."""
    return [(tab, card) for tab, value in page.items() if isinstance(value, list)
            for card in value if isinstance(card, dict) and "id" in card]


def places(page, medicine_id):
    return [tab for tab, card in cards(page) if card["id"] == medicine_id]


def card(page, tab, medicine_id):
    (found,) = [c for t, c in cards(page) if t == tab and c["id"] == medicine_id]
    return found


def gone_and_new(disease_id):
    before = {(t, c["id"]) for t, c in cards(answer("before", disease_id))}
    after = {(t, c["id"]) for t, c in cards(answer("after", disease_id))}
    return before - after, after - before


# ---- the files ----

@pytest.mark.parametrize("name", list(NEW))
def test_each_file_ends_with_the_new_entries_all_dated_25_nov(name):
    entries = load(LISTS / name)
    new = NEW[name]
    assert entries[-len(new):] == new
    assert all(entry["date"] == THE_DAY for entry in new)
    assert len(entries) > len(new)  # the older entries stay in front, untouched


@pytest.mark.parametrize("name", list(NEW))
def test_no_pair_is_written_twice(name):
    pairs = [(e["medicine_id"], e["disease_id"]) for e in load(LISTS / name)]
    assert len(pairs) == len(set(pairs))


def test_the_engine_reads_every_file():
    engine.approvals_by_hand()
    assert {(e.medicine_id, e.disease_id) for e in engine.limits_by_hand()} >= {
        ("CHEMBL1201506", AML), ("CHEMBL1324", PARKINSON)}
    assert any(e.medicine_id == "CHEMBL1469" and e.disease_id == ALS
               for e in engine.withdrawals_by_hand())
    engine.left_out_by_hand()
    assert engine.confirmed_by_label()[("CHEMBL117785", HUNTINGTON)] == NEW["confirmed.json"][1]["label"]
    assert engine.confirmed_by_label()[("CHEMBL1770248", T2D)] == NEW["confirmed.json"][0]["label"]


def test_corrections_use_only_the_existing_wording():
    for entry in load(LISTS / "corrections.json"):
        assert entry["note"] in engine.CORRECTION_NOTES
    assert engine.looks_wrong(T2D) >= {"CHEMBL1064", "CHEMBL925"}
    assert "CHEMBL606" in engine.looks_wrong(DUODENAL)


# ---- Q2 / item 1: hydrocortisone for Addison disease ----

def test_hydrocortisone_before_was_only_in_trials_and_in_the_narrower_box():
    assert sorted(places(answer("before", ADDISON), "CHEMBL389621")) == ["being_studied", "narrower"]


def test_hydrocortisone_after_is_on_the_main_approved_list_with_the_label_line():
    page = answer("after", ADDISON)
    assert places(page, "CHEMBL389621") == ["approved"]
    c = card(page, "approved", "CHEMBL389621")
    assert c["proof_note"] == ("This approval is missing from the database. "
                               "We added it from the official label.")
    assert c["source"] == NEW["approvals.json"][0]["label"]


# ---- Q4 / items 2, 3: limits ----

@pytest.mark.parametrize("disease_id, medicine_id", [(AML, "CHEMBL1201506"),
                                                     (PARKINSON, "CHEMBL1324")])
def test_the_limited_cards_were_on_approved_and_now_carry_the_line(disease_id, medicine_id):
    assert "approved" in places(answer("before", disease_id), medicine_id)
    assert "limit_note" not in card(answer("before", disease_id), "approved", medicine_id)
    after = card(answer("after", disease_id), "approved", medicine_id)
    assert after["limit_note"] == engine.LIMITED_LINE
    gone, new = gone_and_new(disease_id)
    assert not gone and not new


# ---- Q5 / items 4, 5, 9: left out ----

@pytest.mark.parametrize("disease_id, ids", [
    (GRAVES, {"CHEMBL1201532", "CHEMBL1201533", "CHEMBL1789844"}),
    (PROSTATE, {"CHEMBL1170", "CHEMBL1395"}),
    (ADPKD, {"CHEMBL2135460"}),
])
def test_left_out_cards_were_new_clues_and_now_are_in_no_list_of_the_page(disease_id, ids):
    for medicine_id in ids:
        assert "new_clues" in places(answer("before", disease_id), medicine_id)
        assert places(answer("after", disease_id), medicine_id) == []
    gone, new = gone_and_new(disease_id)
    assert {m for _, m in gone} == ids
    assert not new


def test_the_same_medicines_stay_on_other_pages():
    for disease_id, ids in ((GRAVES, {"CHEMBL1789844"}), (ADPKD, {"CHEMBL2135460"})):
        for other in (HEM_A, ADDISON, T2D):
            assert not ids & engine.pushes_wrong_way(other)
    assert engine.pushes_wrong_way(ADPKD) == {"CHEMBL2135460"}


def test_graves_never_leaves_out_an_antithyroid_medicine():
    never = {"CHEMBL1201225",  # iodine
             "CHEMBL1141",     # potassium iodide
             "CHEMBL1233550",  # iodide
             "CHEMBL42115",    # thyroxine
             "CHEMBL508102"}   # carbimazole
    assert not never & engine.pushes_wrong_way(GRAVES)
    for medicine_id in never:
        assert places(answer("after", GRAVES), medicine_id) == places(
            answer("before", GRAVES), medicine_id) != []


def test_the_other_graves_candidates_are_not_added():
    # Tremelimumab, aldesleukin, denileukin diftitox: MAIN 4 reads the labels
    # and Kashish decides by name on the next sheet.
    waiting = {"CHEMBL2108658", "CHEMBL1201438", "CHEMBL1201550"}
    assert not waiting & engine.pushes_wrong_way(GRAVES)
    for medicine_id in waiting:
        assert places(answer("after", GRAVES), medicine_id) == ["new_clues"]


def test_prostate_testosterones_in_being_studied_are_untouched():
    # A left-out entry cannot touch "Already being studied": no entry written.
    studied = {"CHEMBL386630", "CHEMBL2107067", "CHEMBL1201101", "CHEMBL1200335"}
    assert not studied & engine.pushes_wrong_way(PROSTATE)
    for medicine_id in studied:
        assert places(answer("before", PROSTATE), medicine_id) == ["being_studied"]
        assert places(answer("after", PROSTATE), medicine_id) == ["being_studied"]


# ---- Q10 / item 6: dicumarol waits ----

def test_dicumarol_has_no_correction_yet():
    assert "CHEMBL1466" not in engine.looks_wrong(HEM_A)
    assert places(answer("before", HEM_A), "CHEMBL1466") == ["wider_group"]
    assert places(answer("after", HEM_A), "CHEMBL1466") == ["wider_group"]
    assert answer("before", HEM_A) == answer("after", HEM_A)


# ---- Q13 / item 7: primidone ----

def test_primidone_before_none_after_on_approved_with_the_emc_page():
    assert places(answer("before", TREMOR), "CHEMBL856") == []
    page = answer("after", TREMOR)
    assert places(page, "CHEMBL856") == ["approved"]
    c = card(page, "approved", "CHEMBL856")
    assert c["proof_note"] == ("This approval is missing from the database. "
                               "We added it from the official label.")
    assert c["source"] == "https://www.medicines.org.uk/emc/product/2940/smpc"


# ---- Q14 / item 8: Relyvrio ----

def test_relyvrio_is_the_sodium_phenylbutyrate_card_in_the_no_regulator_box():
    before = answer("before", ALS)
    assert before["no_regulator_box"] == ["CHEMBL2359370", "CHEMBL1469"]
    assert card(before, "approved", "CHEMBL1469")["forms"] == ["Sodium Phenylbutyrate"]
    assert "withdrawal_note" not in card(before, "approved", "CHEMBL1469")
    after = answer("after", ALS)
    assert card(after, "approved", "CHEMBL1469")["withdrawal_note"] == engine.HAND_WITHDRAWAL_LINE
    gone, new = gone_and_new(ALS)
    assert not gone and not new
    assert after["no_regulator_box"] == before["no_regulator_box"]


# ---- Q22 / item 10 and 10b: red warnings ----

@pytest.mark.parametrize("disease_id, medicine_id", [(T2D, "CHEMBL1064"),
                                                     (DUODENAL, "CHEMBL606")])
def test_the_card_was_plain_on_approved_and_is_now_red_in_the_red_box(disease_id, medicine_id):
    before, after = answer("before", disease_id), answer("after", disease_id)
    assert "warning" not in card(before, "approved", medicine_id)
    assert medicine_id not in before.get("wrong_approvals_box", [])
    assert card(after, "approved", medicine_id)["warning"] == SECOND_NOTE
    assert medicine_id in after["wrong_approvals_box"]


def test_tyrosine_stays_red_on_type_2_diabetes():
    for state in ("before", "after"):
        assert card(answer(state, T2D), "approved", "CHEMBL925")["warning"] == SECOND_NOTE
    assert ("CHEMBL925", T2D) in engine.corrections()


# ---- item 12: Source record fixes ----

def test_ertugliflozin_opens_steglatro_not_steglujan():
    assert card(answer("before", T2D), "approved", "CHEMBL1770248")["source"] == \
        "https://www.ema.europa.eu/en/medicines/human/EPAR/steglujan"
    assert card(answer("after", T2D), "approved", "CHEMBL1770248")["source"] == \
        DM + "e6f3e718-bb99-48f1-ab94-b9f0af05fed6"


def test_tetrabenazine_opens_xenazine_and_keeps_its_limit_line():
    before = card(answer("before", HUNTINGTON), "approved", "CHEMBL117785")
    after = card(answer("after", HUNTINGTON), "approved", "CHEMBL117785")
    assert after["source"] == DM + "ac768bab-8afa-4446-bc7f-caeeffec0cda"
    assert after["source"] != before["source"]
    assert after["limit_note"] == before["limit_note"] == engine.LIMITED_LINE


# ---- nothing else on a page changes ----

# What each page is allowed to lose or gain, besides the entries above: adding
# an approved card (hydrocortisone, primidone) makes the engine's existing
# opposite-way rule move some look-alike clues into the folded box.
ALLOWED = {
    ADDISON: ({("being_studied", "CHEMBL389621"), ("narrower", "CHEMBL389621")},
              {("approved", "CHEMBL389621")}),
    TREMOR: (set(), {("approved", "CHEMBL856")}),
}


@pytest.mark.parametrize("disease_id", PAGES)
def test_a_page_changes_only_where_an_entry_says(disease_id):
    gone, new = gone_and_new(disease_id)
    new = {(tab, m) for tab, m in new if tab != "opposite_way_box"}
    gone = {(tab, m) for tab, m in gone if tab != "opposite_way_box"}
    expected_gone, expected_new = ALLOWED.get(disease_id, (None, None))
    if expected_gone is not None:
        assert gone == expected_gone and new == expected_new
    elif disease_id in (GRAVES, PROSTATE, ADPKD):
        assert not new
        assert all(tab == "new_clues" for tab, _ in gone)
    elif disease_id == DUODENAL:
        assert not gone and not new
    else:
        assert not gone and not new


@pytest.mark.parametrize("disease_id", [AML, PARKINSON, HEM_A])
def test_the_pages_with_one_small_change_keep_every_other_card_word_for_word(disease_id):
    before, after = answer("before", disease_id), answer("after", disease_id)
    old = {(t, c["id"]): c for t, c in cards(before)}
    for (tab, medicine_id), c in ((k, v) for k, v in
                                  {(t, c["id"]): c for t, c in cards(after)}.items()):
        if medicine_id in ("CHEMBL1201506", "CHEMBL1324"):
            continue
        assert old[(tab, medicine_id)] == c
