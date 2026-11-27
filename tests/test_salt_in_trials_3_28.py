"""Ticket 3.28. Merging salt forms never removes a medicine from In trials.

Since 3.23 the In-trials Ixazomib card (NCT03236792) had left the AL
amyloidosis page: once Ixazomib Citrate joined Ixazomib, the medicine's id
was the same as its wider-group card's, and the folded In-trials box left
out every medicine already in a narrower or wider-group box.

A medicine in trials for this disease stays on In trials, even when its
merged card also sits in an Approved box. No card leaves an Approved box.

The check is run for every pair on salt_parents.json, on every 3.23 page
(the pages of tests/test_salt_loose_ends_3_24.py): each In-trials card the
page shows with the list switched OFF is still on In trials, under the
medicine's id, with the list ON.

Saved answers only, no network.
"""

import json
import pathlib
from unittest.mock import patch

import pytest

from moonlight import engine, fetch

import test_salt_loose_ends_3_24 as pages_3_24

ROOT = pathlib.Path(__file__).resolve().parent.parent
pytestmark = pytest.mark.salt_parents  # the real list

LIST_FILE = ROOT / "moonlight" / "salt_parents.json"
BEFORE = ROOT / "fixtures" / "salt_3_24" / "before"

AL_AMYLOIDOSIS = pages_3_24.AL_AMYLOIDOSIS
IXAZOMIB, IXAZOMIB_CITRATE = "CHEMBL2141296", "CHEMBL3545432"
NCT03236792 = "https://clinicaltrials.gov/study/NCT03236792"

IN_TRIALS = ("being_studied", "more_in_trials", "new_in_trials")
APPROVED_PARTS = ("approved", "narrower", "wider_group")

# The pages built from the disease's own list alone: only the folded
# In-trials boxes can be read there (no proteins are looked at).
LIST_ONLY = {
    pages_3_24.MYASTHENIA_GRAVIS: pages_3_24.by_hand.saved_post_json,
    pages_3_24.AHP: pages_3_24.givosiran.saved_post_json,
    pages_3_24.AMYLOIDOSIS: pages_3_24.amyloidosis_files._from_the_saved_files,
}


def load(file):
    return json.loads(file.read_text(encoding="utf-8"))


SALTS = load(LIST_FILE)
PARENT = {salt: row["parent"] for salt, row in SALTS.items()}


def _page(disease_id):
    """{part: [card ids]} for the In-trials and Approved parts of a 3.23 page."""
    if disease_id in LIST_ONLY:
        tabs = pages_3_24._tabs(disease_id, LIST_ONLY[disease_id])
        found = {part: [medicine.id for medicine in getattr(tabs, part)]
                 for part in APPROVED_PARTS + ("more_in_trials", "new_in_trials")}
        found["being_studied"] = [engine._family_id(clue.medicine) for clue in tabs.being_studied]
        return found
    page = pages_3_24.PAGES[disease_id]()
    return {part: [card["id"] for card in page.get(part) or []]
            for part in APPROVED_PARTS + IN_TRIALS}


def _built(list_on):
    if list_on:
        guard = patch.object(fetch, "_SALT_PARENTS", None)  # read the real file afresh
    else:
        guard = patch.object(fetch, "_salt_parents", return_value={})
    with guard:
        return {disease_id: _page(disease_id) for disease_id in pages_3_24.PAGES}


@pytest.fixture(scope="module")
def off():
    return _built(False)


@pytest.fixture(scope="module")
def on():
    return _built(True)


@pytest.fixture(scope="module")
def al_page():
    with patch.object(fetch, "_SALT_PARENTS", None):
        return pages_3_24.PAGES[AL_AMYLOIDOSIS]()


# ---- Example: Ixazomib on AL amyloidosis ----

def test_ixazomib_is_on_in_trials_with_nct03236792(al_page):
    found = [card for part in IN_TRIALS for card in al_page.get(part) or []
             if card["id"] == IXAZOMIB]
    assert len(found) == 1, found
    card = found[0]
    assert card["medicine"] == "Ixazomib"
    assert card["source"] == NCT03236792
    assert card["trial_phase"] == "Phase 1/2"


def test_ixazomib_stays_in_its_wider_group_box_as_3_24_left_it(al_page):
    before = {card["id"]: card for card in load(BEFORE / f"{AL_AMYLOIDOSIS}.json")["wider_group"]}
    after = {card["id"]: card for card in al_page["wider_group"]}
    assert after[IXAZOMIB] == dict(before[IXAZOMIB], medicine="Ixazomib",
                                   forms=["Ixazomib", "Ixazomib Citrate"])


def test_the_in_trials_card_is_the_one_main_showed_before_3_23(al_page):
    """With the list off (as main built the page before 3.23), the same card,
    now holding both forms: a medicine and its salt are one item."""
    with patch.object(fetch, "_salt_parents", return_value={}):
        old = pages_3_24.PAGES[AL_AMYLOIDOSIS]()
    was = [card for card in old["more_in_trials"] if card["id"] == IXAZOMIB]
    now = [card for card in al_page["more_in_trials"] if card["id"] == IXAZOMIB]
    assert len(was) == 1 and was[0]["forms"] == ["Ixazomib"]
    assert now == [dict(was[0], forms=["Ixazomib", "Ixazomib Citrate"])]


# ---- The same check for every pair, on every 3.23 page ----

# The decided exception (MAIN 5, 27 Nov). "Approved box" means the narrower
# and wider-group boxes. Mitiglinide, merged, is approved for type 2 diabetes
# itself and sits on the main Approved list. A medicine on the main Approved
# list never also appears in In trials (the same rule as T7), so its old
# In-trials card (NCT00461617, Phase 3) stays off.
T2D, MITIGLINIDE, MITIGLINIDE_CALCIUM = pages_3_24.T2D, "CHEMBL471498", "CHEMBL4298005"
ON_THE_MAIN_APPROVED_LIST = {(T2D, MITIGLINIDE)}


@pytest.mark.parametrize("salt", sorted(SALTS))
def test_merging_the_pair_removes_no_medicine_from_in_trials(off, on, salt):
    pair = {salt, PARENT[salt]}
    for disease_id in pages_3_24.PAGES:
        was = {PARENT.get(card_id, card_id) for part in IN_TRIALS
               for card_id in off[disease_id][part] if card_id in pair}
        was -= {medicine for page, medicine in ON_THE_MAIN_APPROVED_LIST if page == disease_id}
        now = {card_id for part in IN_TRIALS for card_id in on[disease_id][part]}
        assert was <= now, (disease_id, salt, sorted(was - now))


def test_the_exception_mitiglinide_is_on_the_main_approved_list_and_not_in_in_trials(off, on):
    assert MITIGLINIDE in off[T2D]["being_studied"]  # before the merge, a separate card
    assert MITIGLINIDE in on[T2D]["approved"]
    assert all(MITIGLINIDE not in on[T2D][part] and MITIGLINIDE_CALCIUM not in on[T2D][part]
               for part in IN_TRIALS)
    # The exception is used: it is the only medicine of any pair it covers.
    assert ON_THE_MAIN_APPROVED_LIST == {(T2D, PARENT[MITIGLINIDE_CALCIUM])}


@pytest.mark.parametrize("disease_id", sorted(pages_3_24.PAGES))
def test_no_medicine_on_the_main_approved_list_is_also_in_in_trials(on, disease_id):
    page = on[disease_id]
    assert not set(page["approved"]) & {card_id for part in IN_TRIALS for card_id in page[part]}


@pytest.mark.parametrize("disease_id", sorted(pages_3_24.PAGES))
def test_no_card_leaves_an_approved_box(on, disease_id):
    """The Approved tab and its boxes are exactly what 3.24 left on main."""
    before = load(BEFORE / f"{disease_id}.json")
    for part in APPROVED_PARTS:
        was = [PARENT.get(card["id"], card["id"]) for card in before.get(part) or []]
        was = list(dict.fromkeys(was))  # a salt and its parent are one card since 3.23
        assert on[disease_id][part] == was, (disease_id, part)
