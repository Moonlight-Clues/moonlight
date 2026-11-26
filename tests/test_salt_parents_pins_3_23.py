"""Ticket 3.23 (MAIN 4). Each of the 33 older pinned pages: switching the salt
list on is one merge per listed pair found, and nothing more.

The 33 older tests below pin a page, a card count or an order as it was before
the list existed. They are NOT changed. conftest.py keeps the list empty for
them, so they pass as written. This file proves, for each one, what the list
does to the pages it builds, by running exactly those 33 tests twice in a child
pytest (tests/salt_pin_recorder.py writes down every page the engine builds):

  OFF  the list empty (as in the suite). All 33 must pass, as written.
  ON   MOONLIGHT_SALT_PARENTS=on, the real moonlight/salt_parents.json.

For every pinned test, over the pages it builds (its own, and those of the
module-scoped fixtures its file builds), comparing page by page, OFF vs ON:

  * A listed pair is FOUND on a page when both the salt's id and the parent's
    id are cards on it (any list). The number of distinct medicines on the page
    falls by exactly the number of pairs found.
  * Every medicine that is in no listed pair keeps its list, and each list's
    cards that are in no pair stay in the same order.
  * A salt whose parent is not on the page is the same card under the parent's
    id (the card's id is the family's id). Nothing else is added or lost.
  * Each of the 33 finds at least one pair somewhere: that is why it changed.

Saved answers only. No network (the child runs the same saved-answer tests).
"""

import json
import os
import pathlib
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

import pytest

pytestmark = pytest.mark.salt_parents  # the real list, for the comparison itself

ROOT = pathlib.Path(__file__).resolve().parent.parent
LIST_FILE = ROOT / "moonlight" / "salt_parents.json"
LISTS = ("approved", "narrower", "wider_group", "being_studied", "new_clues",
         "more_in_trials", "new_in_trials")

PINS = [
    "tests/test_approvals_batch.py::test_the_whole_page_is_as_it_was_before_the_entry",
    "tests/test_approvals_by_hand.py::test_nothing_else_on_the_essential_tremor_page_changes",
    "tests/test_approvals_by_hand.py::test_a_medicine_on_the_corrections_list_for_this_disease_is_not_added",
    "tests/test_approvals_fourth_batch.py::test_the_approved_list_is_a_to_z_and_every_other_card_stays_where_it_was[myasthenia gravis]",
    "tests/test_box_labels.py::test_example_5_no_card_moved[MONDO_0015924]",
    "tests/test_box_labels.py::test_example_5_no_card_moved[MONDO_0019065]",
    "tests/test_family.py::test_amyloidosis_main_list_is_5_the_narrower_box_is_6_and_the_box_is_empty",
    "tests/test_family.py::test_amyloidosis_one_medicine_leaves_new_clues",
    "tests/test_family.py::test_the_runner_does_not_print_a_labelled_medicine_as_a_new_clue",
    "tests/test_family.py::test_api_amyloidosis_labels_only_on_the_six_from_children",
    "tests/test_huntington_limit_line.py::test_example_every_other_part_is_what_main_sent",
    "tests/test_narrower_box.py::test_amyloidosis_main_list_5_narrower_box_6_no_wider_box",
    "tests/test_narrower_box.py::test_in_trials_and_new_clues_are_as_they_were_for_every_example",
    "tests/test_narrower_box.py::test_api_amyloidosis_and_eczema_through_the_api",
    "tests/test_narrower_box.py::test_add_on_the_line_for_each_example",
    "tests/test_narrower_box.py::test_add_on_2_nobody_goes_missing",
    "tests/test_no_regulator_line.py::test_example_6_the_same_cards_in_the_same_order_as_before[Huntington disease]",
    "tests/test_no_source_line.py::test_leukemia_has_cards_in_all_eight_places",
    "tests/test_no_source_line.py::test_browser_a_card_with_a_link_never_says_the_sentence[more_in_trials]",
    "tests/test_old_withdrawn_flag.py::test_exactly_the_eight_come_back_and_nothing_else",
    "tests/test_old_withdrawn_flag.py::test_every_card_shown_today_is_where_it_was_letter_for_letter[MONDO_0005148]",
    "tests/test_old_withdrawn_flag.py::test_every_card_shown_today_is_where_it_was_letter_for_letter[MONDO_0005027]",
    "tests/test_old_withdrawn_flag.py::test_every_card_shown_today_is_where_it_was_letter_for_letter[MONDO_0002050]",
    "tests/test_old_withdrawn_flag.py::test_the_tab_number_counts_the_cards_that_came_back[MONDO_0005148]",
    "tests/test_old_withdrawn_flag.py::test_the_tab_number_counts_the_cards_that_came_back[MONDO_0005027]",
    "tests/test_tafamidis_warning.py::test_the_card_keeps_its_place_and_nothing_else_on_the_page_changes",
    "tests/test_withdrawal_line.py::test_example_everything_else_is_letter_for_letter_what_main_gives",
    "tests/test_withdrawal_line.py::test_guard_a_wider_group_card_gets_the_line_from_the_list_it_came_from",
    "tests/test_wrong_approvals_box.py::test_example_in_trials_and_new_clues_are_letter_for_letter_what_main_gives",
    "tests/test_wrong_approvals_box.py::test_example_every_old_key_answers_what_main_answered_and_one_key_is_new[MONDO_0007739]",
    "tests/test_wrong_approvals_box.py::test_example_every_old_key_answers_what_main_answered_and_one_key_is_new[MONDO_0019438]",
    "tests/test_wrong_approvals_box.py::test_browser_example_in_trials_and_new_clues_are_letter_for_letter_as_before",
    "tests/test_wrong_approvals_box.py::test_browser_second_example_tafamidis_is_in_the_box_and_daratumumab_is_alone",
]


def _run(folder, mode, nodeid, number):
    """One pinned test alone in a child pytest, so every page recorded belongs
    to it (and to the module-scoped fixtures it uses), never to a neighbour."""
    record = folder / f"{mode}_{number}.json"
    env = dict(os.environ)
    env["SALT_PIN_RECORD"] = str(record)
    env["PYTHONPATH"] = os.pathsep.join([str(ROOT), str(ROOT / "tests")])
    env["MOONLIGHT_SALT_PARENTS"] = mode
    env["MOONLIGHT_FIRESTORE_CACHE"] = "0"
    subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "-p", "salt_pin_recorder",
         "--tb=no", nodeid],
        cwd=ROOT, env=env, check=False, capture_output=True, text=True, timeout=900)
    return json.loads(record.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def records(tmp_path_factory):
    folder = tmp_path_factory.mktemp("pins")
    jobs = [(mode, node, number) for number, node in enumerate(PINS) for mode in ("off", "on")]
    with ThreadPoolExecutor(max_workers=4) as pool:
        done = list(pool.map(lambda job: _run(folder, job[0], job[1], job[2]), jobs))
    return {(mode, node): record for (mode, node, _), record in zip(jobs, done)}


def _pages(record):
    """{key: [pages]}: the test's own pages, and each module fixture's."""
    return {key: pages for key, pages in sorted(record["pages"].items()) if pages}


def _pairs():
    return {salt: row["parent"] for salt, row in json.loads(LIST_FILE.read_text("utf-8")).items()}


def _flat(page):
    return [card for name in LISTS for card in page[name]]


def test_the_33_pins_pass_as_written_with_the_list_empty(records):
    assert len(PINS) == len(set(PINS)) == 33
    outcomes = {node: records[("off", node)]["outcomes"].get(node) for node in PINS}
    assert outcomes == {node: "passed" for node in PINS}


def test_with_the_list_on_each_of_the_33_pins_fails_so_it_really_was_changed(records):
    outcomes = {node: records[("on", node)]["outcomes"].get(node) for node in PINS}
    assert outcomes == {node: "failed" for node in PINS}


# OPEN FINDING (for MAIN 4, not fixed here: "nothing else in grouping changes").
# On the amyloidosis page built with no neighbouring diseases, VUTRISIRAN SODIUM
# is a new clue. Its parent VUTRISIRAN is on the disease's own list with the
# stage UNKNOWN for amyloidosis. Joined to its parent, the family has an unclear
# link, and the existing rule leaves such a family out ("unclear_link"). So that
# card leaves the page: one card fewer than the number of pairs found, and not
# "the best seat of the two" as the ticket says. With the neighbours (the real
# page) vutrisiran sits in the narrower-disease box and the proof passes.
# strict=True: when the engine or the ticket changes, these flip to failures.
FINDING = (
    "VUTRISIRAN SODIUM leaves the page: its parent's own-list stage is UNKNOWN, "
    "so the joined family is left out as an unclear link (see the comment above)")
OPEN_FINDING = {
    "tests/test_family.py::test_amyloidosis_main_list_is_5_the_narrower_box_is_6_and_the_box_is_empty",
    "tests/test_family.py::test_amyloidosis_one_medicine_leaves_new_clues",
    "tests/test_family.py::test_the_runner_does_not_print_a_labelled_medicine_as_a_new_clue",
    "tests/test_narrower_box.py::test_amyloidosis_main_list_5_narrower_box_6_no_wider_box",
    "tests/test_narrower_box.py::test_in_trials_and_new_clues_are_as_they_were_for_every_example",
    "tests/test_narrower_box.py::test_add_on_the_line_for_each_example",
    "tests/test_narrower_box.py::test_add_on_2_nobody_goes_missing",
}
assert OPEN_FINDING <= set(PINS)


@pytest.mark.parametrize("nodeid", [
    pytest.param(node, marks=pytest.mark.xfail(strict=True, reason=FINDING)) if node in OPEN_FINDING
    else node for node in PINS])
def test_the_list_on_is_one_merge_per_pair_found_and_nothing_more(nodeid, records):
    pairs = _pairs()
    touched = set(pairs) | set(pairs.values())
    before, after = _pages(records[("off", nodeid)]), _pages(records[("on", nodeid)])
    assert before, f"no page recorded with the list off for {nodeid}"
    found_in_all = 0
    compared = 0
    for key, old_pages in before.items():
        # with the list on a test stops at its first failed pin, so a key may
        # hold fewer pages there: those it did build are compared
        for index, new in enumerate(after.get(key, [])[:len(old_pages)]):
            old = old_pages[index]
            compared += 1
            old_cards, new_cards = set(_flat(old)), set(_flat(new))
            found = sum(1 for salt, parent in pairs.items()
                        if salt in old_cards and parent in old_cards)
            found_in_all += found
            where = (key, index, found)
            # the count of distinct medicines on the page
            assert len(old_cards) - len(new_cards) == found, where
            # nothing added or lost: every salt is its parent's card, the rest are as they were
            assert new_cards == {pairs.get(card, card) for card in old_cards}, where
            assert not set(pairs) & new_cards, where
            for name in LISTS:
                # every card that is in no pair: same list, same order
                assert [c for c in new[name] if c not in touched] == \
                    [c for c in old[name] if c not in touched], (where, name)
                # a merged card is one card, never two
                assert len(new[name]) == len(set(new[name])), (where, name)
    assert compared, f"no page recorded with the list on for {nodeid}"
    # each of the 33 changed because of at least one merge on a page it builds
    assert found_in_all >= 1, f"{nodeid}: no listed pair found on any page it builds"
