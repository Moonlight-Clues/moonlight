"""Ticket 3.18 (Q9, Kashish's decision of 25 Nov). No wider-group box for
groups that are too broad.

moonlight/broad_groups.json is a list written by hand: one entry per group,
with its disease_id, name, date and reason. A card that reaches the folded
box "Approved for a wider group" only through a group on that list is not
shown. A card that also reaches the box through a group that is not on the
list stays, with its label as it was. Cards in other boxes and tabs are
untouched. A box left empty is not shown, as before.

Saved files only: fixtures/broad_groups/answers (asked once on 25 Nov 2026)
and fixtures/old_withdrawn_flag/answers. No network.
"""

import json
import pathlib
from unittest.mock import patch

import pytest

from moonlight import engine
from moonlight.engine import parent_label, sort_into_tabs
from moonlight.filter import sort_paths

import old_flag_saved
from test_family import WIDE, WIDER, child, listed, made_up_path, parent

ROOT = pathlib.Path(__file__).resolve().parent.parent
BROAD_ANSWERS = ROOT / "fixtures" / "broad_groups" / "answers"

# The six groups of the ticket, as the saved answers name them.
SIX = {
    "MONDO_0005240": "kidney disorder",
    "MONDO_0005046": "immune system disorder",
    "MONDO_0005275": "lung disorder",
    "MONDO_0005560": "brain disorder",
    "MONDO_0005267": "heart disorder",
    "MONDO_0005087": "respiratory system disorder",
}
# Each group is a direct parent of the disease the ticket reports it on.
REPORTED_ON = {
    "MONDO_0005240": ["MONDO_0007915"],  # lupus
    "MONDO_0005046": ["MONDO_0005083"],  # psoriasis
    "MONDO_0005275": ["MONDO_0005002"],  # COPD
    "MONDO_0005560": ["EFO_0803536", "MONDO_0005027", "MONDO_0005277"],  # MS, epilepsy, migraine
    "MONDO_0005267": ["MONDO_0005252"],  # heart failure
    "MONDO_0005087": ["MONDO_0009061"],  # cystic fibrosis
}
LUPUS, PSORIASIS, COPD = "MONDO_0007915", "MONDO_0005083", "MONDO_0005002"
TYPE_2_DIABETES, EPILEPSY = "MONDO_0005148", "MONDO_0005027"


def _index(folder):
    return {old_flag_saved._key(entry["kind"], entry["variables"]): folder / entry["file"]
            for entry in json.loads((folder / "index.json").read_text(encoding="utf-8"))}


BROAD_INDEX = _index(BROAD_ANSWERS)


def broad_post_json(body):
    """Stands in for fetch._post_json with the answers saved for this ticket."""
    assert set(body) == {"query", "variables"}
    kind = old_flag_saved.KINDS.get(body["query"])
    assert kind is not None, "a question the saved answers never heard"
    key = old_flag_saved._key(kind, body["variables"])
    assert key in BROAD_INDEX, f"no saved answer for {key}"
    return json.loads(BROAD_INDEX[key].read_text(encoding="utf-8"))


def family_of(disease_id):
    for index in (BROAD_INDEX, {k: v for k, v in _index(old_flag_saved.ANSWERS).items()}):
        key = old_flag_saved._key("family", {"diseaseId": disease_id})
        if key in index:
            return json.loads(index[key].read_text(encoding="utf-8"))["data"]["disease"]
    raise AssertionError(f"no saved family for {disease_id}")


def page(disease_id, broad=None):
    """The page from the saved answers. broad=[] is the page without the list."""
    post_json = broad_post_json if old_flag_saved._key(
        "disease", {"diseaseId": disease_id}) in BROAD_INDEX else old_flag_saved.saved_post_json
    if broad is None:
        return old_flag_saved.page_answer(disease_id, post_json=post_json)
    with patch.object(engine, "_read_broad_groups", return_value=broad):
        return old_flag_saved.page_answer(disease_id, post_json=post_json)


def only_through_a_listed_group(card):
    """Its label names one wider group, and that group is on the list."""
    return any(card.get("label") == parent_label([name]) for name in SIX.values())


# ---- the hand-written list ----

def test_the_list_holds_the_six_groups_with_name_date_and_reason():
    entries = json.loads((ROOT / "moonlight" / "broad_groups.json").read_text(encoding="utf-8"))
    assert {entry["disease_id"]: entry["name"] for entry in entries} == SIX
    for entry in entries:
        assert set(entry) == {"disease_id", "name", "date", "reason"}
        assert entry["date"] == "2026-11-25" and entry["reason"]
    assert engine.broad_group_ids() == set(SIX)


@pytest.mark.parametrize("group_id", sorted(SIX))
def test_each_group_is_confirmed_by_the_saved_answers(group_id):
    for disease_id in REPORTED_ON[group_id]:
        parents = {p["id"]: p["name"] for p in family_of(disease_id)["parents"]}
        assert parents.get(group_id) == SIX[group_id]


@pytest.mark.parametrize("entries", [
    [{"disease_id": "MONDO_1", "name": "x", "date": "2026-11-25"}],  # no reason
    [{"disease_id": "MONDO_1", "name": "x", "date": "25 Nov", "reason": "r"}],  # not a date
    [{"disease_id": "", "name": "x", "date": "2026-11-25", "reason": "r"}],
    [{"disease_id": "MONDO_1", "name": "x", "date": "2026-11-25", "reason": "r"}] * 2,
    {"disease_id": "MONDO_1"},  # not a list
])
def test_an_entry_not_written_the_right_way_is_refused(entries):
    with patch.object(engine, "_read_broad_groups", return_value=entries), \
            pytest.raises(ValueError):
        engine.broad_group_ids()


# ---- the rule, with made-up medicines ----

def _tabs(neighbours, paths=(), broad=("WIDE",)):
    rows = [{"disease_id": group, "name": group, "date": "2026-11-25", "reason": "r"}
            for group in broad]
    with patch.object(engine, "_read_broad_groups", return_value=rows):
        return sort_into_tabs(sort_paths(list(paths)), [], neighbours=neighbours)


def test_a_card_only_through_a_listed_group_is_not_shown():
    tabs = _tabs([parent(WIDE, [listed("ALPHA")])])
    assert tabs.wider_group == []


def test_a_card_also_through_a_group_not_on_the_list_stays_with_its_label():
    tabs = _tabs([parent(WIDE, [listed("ALPHA")]), parent(WIDER, [listed("ALPHA")])])
    assert [(card.name, card.label) for card in tabs.wider_group] == [
        ("ALPHA", parent_label([WIDE.name, WIDER.name]))]


def test_a_card_through_a_group_not_on_the_list_stays():
    tabs = _tabs([parent(WIDE, [listed("ALPHA")]), parent(WIDER, [listed("BETA")])])
    assert [card.name for card in tabs.wider_group] == ["BETA"]


def test_cards_in_other_boxes_and_tabs_are_untouched():
    paths = [made_up_path("ALPHA"), made_up_path("GAMMA", disease_stage="PHASE_2")]
    neighbours = [parent(WIDE, [listed("ALPHA"), listed("GAMMA"), listed("DELTA")]),
                  child(approved=[listed("DELTA")])]
    before, after = _tabs(neighbours, paths, broad=()), _tabs(neighbours, paths)
    assert sorted(card.name for card in before.wider_group) == ["ALPHA", "GAMMA"]
    assert after.wider_group == []
    # The card taken out is shown nowhere else: not a new clue again.
    assert after.new_clues == before.new_clues == []
    assert after.being_studied == before.being_studied  # GAMMA stays in In trials
    assert after.narrower == before.narrower and [c.name for c in after.narrower] == ["DELTA"]
    assert after.approved == before.approved and after.left_out == before.left_out
    assert after.more_in_trials == before.more_in_trials
    assert after.new_in_trials == before.new_in_trials


# ---- the saved pages ----

@pytest.mark.parametrize("disease_id, lost", [(LUPUS, 6), (PSORIASIS, 45), (COPD, 10)])
def test_lupus_psoriasis_and_copd_lose_the_listed_cards(disease_id, lost):
    before, after = page(disease_id, broad=[]), page(disease_id)
    gone = [card for card in before["wider_group"] if only_through_a_listed_group(card)]
    assert len(gone) == lost
    kept = [card for card in before["wider_group"] if not only_through_a_listed_group(card)]
    assert after.get("wider_group", []) == kept
    assert not any(only_through_a_listed_group(card) for card in after.get("wider_group", []))
    # Nothing else on the page changes.
    assert {k: v for k, v in after.items() if k != "wider_group"} == \
        {k: v for k, v in before.items() if k != "wider_group"}


def test_lupus_keeps_the_cards_of_its_other_wider_groups():
    after = page(LUPUS)
    assert len(after["wider_group"]) == 2
    assert all(parent_label([SIX["MONDO_0005240"]]) != card["label"]
               for card in after["wider_group"])


def test_copd_box_left_empty_is_not_shown():
    assert "wider_group" in page(COPD, broad=[])
    assert "wider_group" not in page(COPD)


def test_type_2_diabetes_whose_wider_group_is_not_listed_is_unchanged():
    after = page(TYPE_2_DIABETES)
    assert after == page(TYPE_2_DIABETES, broad=[])
    assert after["wider_group"]
    assert {card["label"] for card in after["wider_group"]} == {parent_label(["diabetes mellitus"])}


def test_epilepsy_loses_its_brain_disorder_box():
    before, after = page(EPILEPSY, broad=[]), page(EPILEPSY)
    assert before["wider_group"]
    assert all(only_through_a_listed_group(card) for card in before["wider_group"])
    assert "wider_group" not in after


# ---- the count on the 16 saved pages ----

SAVED_PAGES = sorted(
    [entry["variables"]["diseaseId"] for entry in json.loads(
        (BROAD_ANSWERS / "index.json").read_text(encoding="utf-8")) if entry["kind"] == "family"]
    + [entry["variables"]["diseaseId"] for entry in json.loads(
        (old_flag_saved.ANSWERS / "index.json").read_text(encoding="utf-8"))
       if entry["kind"] == "family"])
LOST = {LUPUS: 6, PSORIASIS: 45, COPD: 10, "EFO_0803536": 4, "MONDO_0005277": 4,
        "MONDO_0005252": 3, "MONDO_0009061": 15, EPILEPSY: 4}


def test_sixteen_saved_pages():
    assert len(SAVED_PAGES) == 16


@pytest.mark.parametrize("disease_id", SAVED_PAGES)
def test_the_put_back_helper_gives_the_page_without_the_list(disease_id):
    from broad_3_18 import REMOVED, back_to_before
    after = page(disease_id)
    assert back_to_before(after, disease_id) == page(disease_id, broad=[])
    assert len(REMOVED.get(disease_id, [])) == LOST.get(disease_id, 0)


def test_ninety_one_cards_leave_the_box_on_the_saved_pages():
    assert sum(LOST.values()) == 91
