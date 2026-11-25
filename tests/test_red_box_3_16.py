"""Ticket 3.16 (Q7). Red cards move out of the folded boxes into the red box.

Kashish's decision of 25 Nov: a card with a red note from corrections.json
that sits today in a folded box (wider-group, narrower, no-regulator) moves
to the red box ("wrong_approvals_box"). A red warning must not be hidden in
a closed box. This reverses the 2.55 behaviour on purpose.

- Any card with a red note for the disease goes to the red box, whichever
  box it was in.
- The card keeps its other grey lines.
- It appears only once on the page.

How it is built, the shape ticket 2.27 used. engine.wrong_approvals_box is
also handed the narrower box and the wider-group box, and names their red
cards too, A to Z with the main list's. In /api/clues every card stays in
its own list ("approved", "narrower" or "wider_group") exactly as before,
and "wrong_approvals_box" names it. The page draws it in the red box and
leaves it out of the box it was in. The no-regulator box already gave way
to the red box (ticket 2.42); that is unchanged.

Saved answers only (fixtures/withdrawal_reports/ for haemophilia A,
fixtures/old_withdrawn_flag/ for type 2 diabetes). No network.
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
from moonlight.filter import sort_paths

import old_flag_saved as t2d_files
import test_withdrawal_line as hem_a_files
import test_wrong_approvals_box as red_box_2_27

ROOT = pathlib.Path(__file__).resolve().parent.parent
PAGE_FILE = ROOT / "web" / "index.html"
CORRECTIONS_FILE = ROOT / "moonlight" / "corrections.json"
KEY = "wrong_approvals_box"

THIRD_NOTE = "A blood thinner cannot be a treatment for a bleeding disease."
LABEL_NOTE = ("This looks like a mistake in the database. The official label is for "
              "a different disease.")

HEM_A, DICUMAROL = "MONDO_0010602", "CHEMBL1466"
T2D = "MONDO_0005148"
SIX = {  # ticket 2.58 (25N-16): medicine id -> name on the card
    "CHEMBL24": "Atenolol", "CHEMBL1014": "Candesartan Cilexetil",
    "CHEMBL1055": "Chlorthalidone", "CHEMBL435": "Hydrochlorothiazide",
    "CHEMBL1237": "Lisinopril Anhydrous", "CHEMBL1200692": "Olmesartan Medoxomil",
}
LISTS = ("approved", "narrower", "wider_group")


def real_corrections():
    return json.loads(CORRECTIONS_FILE.read_text(encoding="utf-8"))


def ids(cards):
    return [card["id"] for card in cards]


def everywhere(answer, medicine_id):
    """Every Approved-tab list that holds this card."""
    return [part for part in LISTS if medicine_id in ids(answer.get(part, []))]


def shown_in(answer, part):
    """The cards the page shows in one Approved-tab list: the red ones are not."""
    boxed = set(answer.get(KEY, []))
    return [card for card in answer.get(part, []) if card["id"] not in boxed]


# ---- her example: dicumarol on haemophilia A ----

@pytest.fixture(scope="module")
def hem_a():
    # As in ticket 2.55's test: the left-out list as it was before 2.43.
    with hem_a_files.left_out_before_2_43():
        return hem_a_files.page_answer(wrong=real_corrections())


def test_dicumarol_moves_into_the_red_box(hem_a):
    assert DICUMAROL in hem_a[KEY]


def test_dicumarol_is_no_longer_shown_in_the_wider_group_box(hem_a):
    assert DICUMAROL not in ids(shown_in(hem_a, "wider_group"))


def test_dicumarol_is_on_the_page_once(hem_a):
    assert hem_a[KEY].count(DICUMAROL) == 1
    assert everywhere(hem_a, DICUMAROL) == ["wider_group"]  # its one card, as before


def test_dicumarol_keeps_its_red_sentence_and_its_wider_group_line(hem_a):
    (card,) = [c for c in hem_a["wider_group"] if c["id"] == DICUMAROL]
    assert card["warning"] == THIRD_NOTE
    assert card["label"]  # the grey "approved for a wider group" words stay on the card


def test_the_other_haemophilia_a_wider_group_cards_stay_where_they_are(hem_a):
    # Folded-box cards with no red note do not move.
    others = [c for c in hem_a["wider_group"] if c["id"] != DICUMAROL]
    assert others and not any("warning" in c for c in others)
    assert ids(shown_in(hem_a, "wider_group")) == ids(others)


# ---- the six 2.58 cards on type 2 diabetes ----

@pytest.fixture(scope="module")
def diabetes():
    return t2d_files.page_answer(T2D)


@pytest.mark.parametrize("medicine_id", sorted(SIX), ids=lambda m: SIX[m])
def test_each_of_the_six_moves_into_the_red_box(diabetes, medicine_id):
    assert medicine_id in diabetes[KEY]
    assert medicine_id not in ids(shown_in(diabetes, "wider_group"))
    assert everywhere(diabetes, medicine_id) == ["wider_group"]
    (card,) = [c for c in diabetes["wider_group"] if c["id"] == medicine_id]
    assert card["warning"] == LABEL_NOTE
    assert card["medicine"] == SIX[medicine_id]


def test_the_red_box_on_type_2_diabetes_is_a_to_z_across_the_lists(diabetes):
    by_id = {c["id"]: c for part in LISTS for c in diabetes.get(part, [])}
    names = [by_id[medicine_id]["medicine"] for medicine_id in diabetes[KEY]]
    assert names == sorted(names, key=str.casefold)
    assert len(diabetes[KEY]) == len(set(diabetes[KEY]))  # nobody twice


def test_the_main_lists_red_cards_are_still_in_the_red_box(diabetes):
    red_main = [c["id"] for c in diabetes["approved"] if "warning" in c]
    assert red_main and set(red_main) <= set(diabetes[KEY])
    assert set(diabetes[KEY]) == set(red_main) | set(SIX)


def test_wider_group_cards_with_no_red_note_on_type_2_diabetes_stay(diabetes):
    plain = [c["id"] for c in diabetes["wider_group"] if "warning" not in c]
    assert plain and ids(shown_in(diabetes, "wider_group")) == plain


# ---- the engine and the API, with hand-built cards ----

FOUR = red_box_2_27.FOUR  # ALPHAMIL, BRAVOMIL, CHARLIEMIL, DELTAMIL
correction = red_box_2_27.correction
DISEASE = red_box_2_27.DISEASE


def three_lists():
    """ALPHAMIL in the wider-group box, BRAVOMIL in the narrower box, the
    other two on the main list."""
    cards = red_box_2_27.approved_list(*FOUR)
    return cards[2:], cards[1:2], cards[:1]  # main, narrower, wider


def test_engine_red_cards_from_every_box_go_in_a_to_z():
    main, narrower, wider = three_lists()
    wrong = [correction(medicine_id) for _, medicine_id in FOUR]
    with patch.object(engine, "_read_corrections", return_value=wrong):
        boxed = engine.wrong_approvals_box(main, DISEASE.id, narrower, wider)
    assert [m.name for m in boxed] == ["ALPHAMIL", "BRAVOMIL", "CHARLIEMIL", "DELTAMIL"]


def test_engine_a_folded_box_card_with_no_red_note_is_not_named():
    main, narrower, wider = three_lists()
    with patch.object(engine, "_read_corrections", return_value=[correction("CHEMBL9004")]):
        boxed = engine.wrong_approvals_box(main, DISEASE.id, narrower, wider)
    assert [m.name for m in boxed] == ["DELTAMIL"]


def test_engine_nothing_is_taken_off_the_lists_it_is_handed():
    main, narrower, wider = three_lists()
    kept = (list(main), list(narrower), list(wider))
    with patch.object(engine, "_read_corrections",
                      return_value=[correction(m) for _, m in FOUR]):
        engine.wrong_approvals_box(main, DISEASE.id, narrower, wider)
    assert (main, narrower, wider) == kept


def test_api_names_the_red_narrower_card_too_and_keeps_its_card_in_its_list():
    found = api._Found(DISEASE, sort_paths([red_box_2_27.approved_path(n, m) for n, m in FOUR]),
                       [], [], [])
    found.narrower, found.approved = found.approved[1:2], found.approved[:1] + found.approved[2:]
    answer = red_box_2_27.hand_built_page(found, [correction("CHEMBL9002", note=LABEL_NOTE)])
    assert answer[KEY] == ["CHEMBL9002"]
    assert [c["medicine"] for c in answer["narrower"]] == ["Bravomil"]
    assert answer["narrower"][0]["warning"] == LABEL_NOTE


def test_a_no_regulator_card_with_a_red_note_still_goes_to_the_red_box_only():
    # Ticket 2.42: the red box wins. Unchanged.
    card = engine.ApprovedMedicine(
        id="CHEMBL9001", name="ALPHAMIL", forms=(), clue=None,
        listed_sources=("https://example.org/CHEMBL9001",), regulator_record=False)
    assert card.proof_note == engine.NO_REGULATOR_LINE
    with patch.object(engine, "_read_corrections", return_value=[correction("CHEMBL9001")]):
        assert engine.wrong_approvals_box([card], DISEASE.id) == [card]
        assert engine.no_regulator_box([card], DISEASE.id) == []


# ---- the page, in a real browser ----

@pytest.fixture(scope="module")
def seen(hem_a, diabetes, tmp_path_factory):
    node = shutil.which("node")
    if not node or subprocess.run(
            [node, "-e", "require('playwright')"], capture_output=True).returncode:
        pytest.skip("needs node with playwright to open a real browser")
    answers = {"hem_a": hem_a, "diabetes": diabetes}
    answers_file = tmp_path_factory.mktemp("red_box_3_16") / "answers.json"
    answers_file.write_text(json.dumps(answers), encoding="utf-8")
    run = subprocess.run(
        [node, "-e", red_box_2_27.BROWSER_SCRIPT, str(PAGE_FILE), str(answers_file)],
        capture_output=True, text=True, timeout=240, cwd=str(ROOT))
    assert run.returncode == 0, run.stderr[-3000:]
    out = json.loads(run.stdout)
    for name in answers:
        assert out[name]["errors"] == [], name
    return out


def names_read(box):
    return [card["name"] for card in box["cards"]] if box else []


def test_browser_dicumarol_is_in_the_red_box_and_not_in_the_wider_group_box(seen):
    opened = seen["hem_a"]["opened"]
    assert "Dicumarol" in names_read(opened["wrong"])
    assert "Dicumarol" not in names_read(opened["wider"])
    assert opened["wrong"]["open"] is False  # the red box still never opens by itself


def test_browser_dicumarol_shows_its_red_sentence_in_the_red_box(seen):
    (card,) = [c for c in seen["hem_a"]["opened"]["wrong"]["cards"] if c["name"] == "Dicumarol"]
    assert card["warning"] == THIRD_NOTE


@pytest.mark.parametrize("name", ["hem_a", "diabetes"])
def test_browser_no_card_is_on_the_page_twice(seen, name):
    opened = seen[name]["opened"]
    every = (names_read({"cards": opened["list"]}) + names_read(opened["narrower"])
             + names_read(opened["wider"]) + names_read(opened["wrong"]))
    assert len(every) == len(set(every))


def test_browser_the_six_are_in_the_red_box_a_to_z_and_not_in_the_wider_group_box(seen):
    opened = seen["diabetes"]["opened"]
    red = names_read(opened["wrong"])
    assert set(SIX.values()) <= set(red)
    assert red == sorted(red, key=str.casefold)
    assert not set(SIX.values()) & set(names_read(opened["wider"]))


def test_browser_the_wider_group_box_count_leaves_the_moved_cards_out(seen, diabetes):
    opened = seen["diabetes"]["opened"]
    left = len(diabetes["wider_group"]) - len(SIX)
    assert len(opened["wider"]["cards"]) == left
    assert f"({left})" in opened["wider"]["summary"]
