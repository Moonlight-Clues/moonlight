"""Ticket 2.64. Three list fixes (sheet D1, Part 3 rows 9-10).

Lists only: one entry in moonlight/approvals.json, two in moonlight/confirmed.json.

  * Imatinib (CHEMBL941) on the pre-B acute lymphoblastic leukaemia page
    (MONDO_0020511, the page tests/test_family.py calls PRE_B_ALL) leaves
    "Already being studied" for the Approved main list, marked "limited", from
    the DailyMed Gleevec label (it names Philadelphia chromosome positive ALL).
    The card says, in Kashish's signed words:
        The label covers only some people with this disease.
  * Anagliptin (Suiny) and tofogliflozin (Deberza) on type 2 diabetes
    (MONDO_0005148) keep their place on Approved; their Source record opens
    the Japanese package insert (PMDA). Product opened both links: each is the
    Japanese label and names type 2 diabetes (2型糖尿病).

Saved answers, no network: fixtures/list_fixes_2_64/before/<disease>.clues.json
is the live /api/clues answer of 2026-11-26 on main 401018f, and .../after/ the
answer with the three entries, both saved as sent (Open Targets data 26.09).
"""

import json
import pathlib

import pytest

from moonlight import engine

ROOT = pathlib.Path(__file__).resolve().parent.parent
LISTS = ROOT / "moonlight"
SAVED = ROOT / "fixtures" / "list_fixes_2_64"
THE_DAY = "2026-11-26"

PRE_B_ALL = "MONDO_0020511"
T2D = "MONDO_0005148"
IMATINIB = "CHEMBL941"
ANAGLIPTIN = "CHEMBL1929396"
TOFOGLIFLOZIN = "CHEMBL2110731"

# Kashish's words, exactly (26 Nov sheet).
LIMIT_LINE = "The label covers only some people with this disease."
ADDED_LINE = "This approval is missing from the database. We added it from the official label."

GLEEVEC = ("https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm"
           "?setid=211ef2da-2868-4a77-8055-1cb2cd78e24b")
SUINY = "https://www.pmda.go.jp/PmdaSearch/iyakuDetail/ResultDataSetPDF/300297_3969016F1023_1_12"
DEBERZA = "https://www.pmda.go.jp/PmdaSearch/iyakuDetail/ResultDataSetPDF/270072_3969021F1032_1_12"

IMATINIB_ENTRY = {"medicine_id": IMATINIB, "name": "Imatinib", "disease_id": PRE_B_ALL,
                  "date": THE_DAY, "label": GLEEVEC, "limited": True}
CONFIRMED_ENTRIES = [
    {"medicine_id": ANAGLIPTIN, "disease_id": T2D, "date": THE_DAY, "label": SUINY},
    {"medicine_id": TOFOGLIFLOZIN, "disease_id": T2D, "date": THE_DAY, "label": DEBERZA},
]


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


# ---- the files ----

def test_approvals_json_ends_with_the_imatinib_entry_and_keeps_the_older_imatinib_entry():
    entries = load(LISTS / "approvals.json")
    # Ticket 2.64 appends one entry at the very end.
    assert entries[-1] == IMATINIB_ENTRY
    older = [e for e in entries[:-1] if e["medicine_id"] == IMATINIB]
    assert [(e["disease_id"], e.get("limited")) for e in older] == [("MONDO_0016586", True)]
    pairs = [(e["medicine_id"], e["disease_id"]) for e in entries]
    assert len(pairs) == len(set(pairs))


def test_confirmed_json_ends_with_the_two_japanese_labels():
    entries = load(LISTS / "confirmed.json")
    assert entries[-2:] == CONFIRMED_ENTRIES
    pairs = [(e["medicine_id"], e["disease_id"]) for e in entries]
    assert len(pairs) == len(set(pairs))


def test_the_engine_reads_the_new_entries():
    hand = [e for e in engine.approvals_by_hand()
            if (e.medicine_id, e.disease_id) == (IMATINIB, PRE_B_ALL)]
    assert len(hand) == 1 and hand[0].limited is True
    labels = engine.confirmed_by_label()
    assert labels[(ANAGLIPTIN, T2D)] == SUINY
    assert labels[(TOFOGLIFLOZIN, T2D)] == DEBERZA


def test_both_new_confirmed_links_are_https_pmda_package_inserts():
    for entry in CONFIRMED_ENTRIES:
        assert entry["label"].startswith("https://www.pmda.go.jp/PmdaSearch/iyakuDetail/")


# ---- EXAMPLE: pre-B ALL, imatinib ----

def test_imatinib_before_was_only_in_trials():
    assert places(answer("before", PRE_B_ALL), IMATINIB) == ["being_studied"]


def test_imatinib_after_is_on_the_main_approved_list_and_nowhere_else():
    page = answer("after", PRE_B_ALL)
    assert places(page, IMATINIB) == ["approved"]


def test_imatinib_card_shows_the_limit_line_the_added_line_and_the_gleevec_label():
    c = card(answer("after", PRE_B_ALL), "approved", IMATINIB)
    assert c["limit_note"] == LIMIT_LINE == engine.LIMITED_LINE
    assert c["proof_note"] == ADDED_LINE
    assert c["source"] == GLEEVEC
    assert c["medicine"] == "Imatinib"


def test_the_pre_b_all_page_changes_only_where_imatinib_moves():
    before, after = answer("before", PRE_B_ALL), answer("after", PRE_B_ALL)
    old = {(t, c["id"]): c for t, c in cards(before)}
    new = {(t, c["id"]): c for t, c in cards(after)}
    gone = set(old) - set(new)
    added = set(new) - set(old)
    gone = {k for k in gone if k[0] != "opposite_way_box"}
    added = {k for k in added if k[0] != "opposite_way_box"}
    assert gone == {("being_studied", IMATINIB)}
    assert added == {("approved", IMATINIB)}
    for key in set(old) & set(new):
        assert old[key] == new[key], key
    for key in before.keys() | after.keys():
        if isinstance(before.get(key), list):
            continue
        assert before.get(key) == after.get(key), key


def test_pre_b_all_approved_list_is_still_a_to_z():
    approved = [c["medicine"] for c in answer("after", PRE_B_ALL)["approved"]]
    assert approved == sorted(approved, key=str.casefold)


# ---- EXAMPLE: type 2 diabetes, anagliptin and tofogliflozin ----

@pytest.mark.parametrize("medicine_id, label", [(ANAGLIPTIN, SUINY), (TOFOGLIFLOZIN, DEBERZA)])
def test_the_japanese_cards_keep_their_place_and_open_the_japanese_label(medicine_id, label):
    before, after = answer("before", T2D), answer("after", T2D)
    assert places(before, medicine_id) == places(after, medicine_id) == ["approved"]
    ids_before = [c["id"] for c in before["approved"]]
    ids_after = [c["id"] for c in after["approved"]]
    assert ids_before.index(medicine_id) == ids_after.index(medicine_id)
    assert ids_before == ids_after
    old, new = card(before, "approved", medicine_id), card(after, "approved", medicine_id)
    assert old["source"].startswith("https://ttd.idrblab.cn/")
    assert new["source"] == label
    assert {k: v for k, v in old.items() if k != "source"} == \
        {k: v for k, v in new.items() if k != "source"}


def test_the_japanese_cards_gain_no_grey_line():
    after = answer("after", T2D)
    for medicine_id in (ANAGLIPTIN, TOFOGLIFLOZIN):
        c = card(after, "approved", medicine_id)
        assert "proof_note" not in c and "limit_note" not in c and "warning" not in c


def test_nothing_else_on_the_type_2_diabetes_page_changes():
    before, after = answer("before", T2D), answer("after", T2D)
    changed = {ANAGLIPTIN, TOFOGLIFLOZIN}
    assert before.keys() == after.keys()
    for key in before:
        if key == "approved":
            old = {c["id"]: c for c in before[key] if c["id"] not in changed}
            new = {c["id"]: c for c in after[key] if c["id"] not in changed}
            assert old == new
        else:
            assert before[key] == after[key], key
