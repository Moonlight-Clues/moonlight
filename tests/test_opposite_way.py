"""Ticket 3.7. The opposite-way line.

Kashish's decision. A clue card or an In trials card gets one extra line
when its medicine turns a protein the opposite way to the approved
medicines for this disease. Her words, exactly:

    Opposite way to the approved medicines for this disease.

The rule, for one disease and one protein:
  1. Take the medicines in the MAIN Approved list only (not the narrower
     box, not the wider box) that turn this protein up or down. Leave out
     any with the red warning. Ignore mixed and unknown.
  2. None left: no card gets the line for this protein.
  3. All up, or all down: the protein is "one-way". Some up and some
     down: "both-ways", and no card gets the line for this protein.
  4. On a one-way protein, a New clues or In trials card turning it the
     other way gets the line. Mixed or unknown never does.
  5. Approved cards never get the line.

One test or more for each of the ticket's eight EXAMPLES, a to h. Every
record is built by hand. Nothing here touches the network: api._find, the
one place the API gets its data from, is swapped for the hand-built
records, and the corrections list is swapped for a hand-built one.
"""

import re
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from moonlight import api
from moonlight.engine import CHILD, PARENT, Neighbour
from moonlight.fetch import Listed
from moonlight.filter import sort_paths
from moonlight.records import Disease, Medicine, MedicineForm, Path, Target

# Word for word from the ticket.
LINE = "Opposite way to the approved medicines for this disease."
NO_DIRECTION = "The data does not say which direction this disease needs."

DISEASE = Disease("TEST_0000001", "test disease")
WIDER = Disease("TEST_0000002", "wider test group")
NARROWER = Disease("TEST_0000003", "narrower test disease")

NR3C1 = Target("ENSG00000113580", "NR3C1", "glucocorticoid receptor", 0.8)
ADRB1 = Target("ENSG00000043591", "ADRB1", "beta-1 adrenergic receptor", 0.6)

UP = ("AGONIST",)
DOWN = ("ANTAGONIST",)
MIXED = ("AGONIST", "ANTAGONIST")
UNKNOWN = ("BINDING AGENT",)

APPROVED_HERE = "APPROVAL"  # approved for this disease: the main Approved list
IN_TRIALS = "PHASE_2"  # in trials for this disease: the In trials tab
NO_LINK = None  # approved for something else only: a new clue


def path(name, medicine_id, target, action_types, link=NO_LINK):
    """One hand-built path: this medicine does this to this protein."""
    form = MedicineForm(medicine_id, name, best_stage="APPROVAL", disease_stage=link,
                        withdrawn=False)
    return Path(Medicine(name, (form,)), target, DISEASE, action_types, target.score,
                (f"https://example.org/{medicine_id}",))


def cards(paths, wrong=(), neighbours=()):
    """What /api/clues sends for these hand-built paths."""
    found = api._Found(DISEASE, sort_paths(paths), [], [], list(neighbours))
    with patch.object(api, "_find", return_value=found), \
         patch.object(api, "looks_wrong", return_value=set(wrong)):
        response = TestClient(api.app).get("/api/clues", params={"disease_id": DISEASE.id})
    assert response.status_code == 200
    return response.json()


def card(answer, tab, medicine):
    for item in answer[tab]:
        if item["medicine"].lower() == medicine.lower():
            return item
    raise AssertionError(f"no {medicine} card in {tab}")


def lines(item):
    """symbol -> the protein's extra line, or None if it has none."""
    return {protein["symbol"]: protein.get("opposite_way") for protein in item["proteins"]}


MIFEPRISTONE = path("MIFEPRISTONE", "CHEMBL1276308", NR3C1, DOWN, APPROVED_HERE)
DEXAMETHASONE = path("DEXAMETHASONE", "CHEMBL384467", NR3C1, UP)
DOBUTAMINE = path("DOBUTAMINE", "CHEMBL926", ADRB1, UP, APPROVED_HERE)
METOPROLOL = path("METOPROLOL", "CHEMBL13", ADRB1, DOWN, APPROVED_HERE)


# ---- a. the opposite way gets the line ----

def test_a_clue_turning_the_protein_the_other_way_has_the_line():
    answer = cards([MIFEPRISTONE, DEXAMETHASONE])
    assert lines(card(answer, "new_clues", "dexamethasone")) == {"NR3C1": LINE}


def test_a_up_against_down_and_down_against_up_both_count():
    approved_up = path("APPROVEDUP", "CHEMBL9001", NR3C1, UP, APPROVED_HERE)
    clue_down = path("CLUEDOWN", "CHEMBL9002", NR3C1, DOWN)
    answer = cards([approved_up, clue_down])
    assert lines(card(answer, "new_clues", "cluedown")) == {"NR3C1": LINE}


def test_a_the_line_is_kashishs_words_exactly():
    answer = cards([MIFEPRISTONE, DEXAMETHASONE])
    protein = card(answer, "new_clues", "dexamethasone")["proteins"][0]
    assert protein["opposite_way"] == "Opposite way to the approved medicines for this disease."


# ---- b. the same way gets no line ----

def test_b_clue_turning_the_protein_the_same_way_has_no_line():
    same_way = path("SAMEWAY", "CHEMBL9003", NR3C1, DOWN)
    answer = cards([MIFEPRISTONE, DEXAMETHASONE, same_way])
    assert lines(card(answer, "new_clues", "sameway")) == {"NR3C1": None}
    # and the other card on the same disease still has it
    assert lines(card(answer, "new_clues", "dexamethasone")) == {"NR3C1": LINE}


# ---- c. both-ways: no card gets the line ----

def test_c_both_ways_protein_gives_no_line_to_a_down_clue():
    clue = path("CLUEDOWN", "CHEMBL9002", ADRB1, DOWN)
    answer = cards([DOBUTAMINE, METOPROLOL, clue])
    assert lines(card(answer, "new_clues", "cluedown")) == {"ADRB1": None}


def test_c_both_ways_protein_gives_no_line_to_an_up_clue_either():
    clue = path("CLUEUP", "CHEMBL9004", ADRB1, UP)
    answer = cards([DOBUTAMINE, METOPROLOL, clue])
    assert lines(card(answer, "new_clues", "clueup")) == {"ADRB1": None}


# ---- d. the red warning takes an approved medicine out of the rule ----

def test_d_only_approved_medicine_has_the_red_warning_so_no_line():
    answer = cards([MIFEPRISTONE, DEXAMETHASONE], wrong={"CHEMBL1276308"})
    assert card(answer, "approved", "mifepristone")["warning"]  # it does have the warning
    assert lines(card(answer, "new_clues", "dexamethasone")) == {"NR3C1": None}


def test_d_a_warned_medicine_does_not_make_a_protein_both_ways():
    # dobutamine (up) has the warning, so only metoprolol (down) counts:
    # ADRB1 is one-way down, and a clue turning it up gets the line.
    clue = path("CLUEUP", "CHEMBL9004", ADRB1, UP)
    answer = cards([DOBUTAMINE, METOPROLOL, clue], wrong={"CHEMBL926"})
    assert lines(card(answer, "new_clues", "clueup")) == {"ADRB1": LINE}


# ---- e. an approved medicine with no clear direction is ignored ----

def test_e_approved_medicine_direction_unknown_gives_no_line():
    approved = path("APPROVEDUNKNOWN", "CHEMBL9005", NR3C1, UNKNOWN, APPROVED_HERE)
    answer = cards([approved, DEXAMETHASONE])
    assert lines(card(answer, "new_clues", "dexamethasone")) == {"NR3C1": None}


def test_e_approved_medicine_direction_mixed_gives_no_line():
    approved = path("APPROVEDMIXED", "CHEMBL9006", NR3C1, MIXED, APPROVED_HERE)
    answer = cards([approved, DEXAMETHASONE])
    assert lines(card(answer, "new_clues", "dexamethasone")) == {"NR3C1": None}


def test_e_mixed_and_unknown_are_ignored_next_to_a_clear_one():
    # mifepristone (down) still makes NR3C1 one-way.
    mixed = path("APPROVEDMIXED", "CHEMBL9006", NR3C1, MIXED, APPROVED_HERE)
    unknown = path("APPROVEDUNKNOWN", "CHEMBL9005", NR3C1, UNKNOWN, APPROVED_HERE)
    answer = cards([MIFEPRISTONE, mixed, unknown, DEXAMETHASONE])
    assert lines(card(answer, "new_clues", "dexamethasone")) == {"NR3C1": LINE}


# ---- f. a clue with no clear direction never gets the line ----

@pytest.mark.parametrize("action_types", [UNKNOWN, MIXED, ()])
def test_f_clue_with_unknown_or_mixed_direction_has_no_line(action_types):
    clue = path("CLUEUNCLEAR", "CHEMBL9007", NR3C1, action_types)
    answer = cards([MIFEPRISTONE, clue])
    assert lines(card(answer, "new_clues", "clueunclear")) == {"NR3C1": None}


# ---- g. only the main Approved list counts, not the boxes ----

def boxed(role, entry_disease):
    """BOXED turns NR3C1 up and is approved only on a parent or child entry."""
    listed = Listed("CHEMBL9008", "BOXED", (("CHEMBL9008", "BOXED"),), ())
    return path("BOXED", "CHEMBL9008", NR3C1, UP), Neighbour(role, entry_disease, (listed,), ())


def test_g_wider_box_medicine_does_not_count():
    boxed_path, neighbour = boxed(PARENT, WIDER)
    clue = path("CLUEDOWN", "CHEMBL9002", NR3C1, DOWN)
    answer = cards([boxed_path, clue], neighbours=[neighbour])
    assert [item["medicine"] for item in answer["wider_group"]] == ["Boxed"]  # it is in the box
    assert answer["approved"] == []  # nothing in the main list touches NR3C1
    assert lines(card(answer, "new_clues", "cluedown")) == {"NR3C1": None}


def test_g_narrower_box_medicine_does_not_count():
    boxed_path, neighbour = boxed(CHILD, NARROWER)
    clue = path("CLUEDOWN", "CHEMBL9002", NR3C1, DOWN)
    answer = cards([boxed_path, clue], neighbours=[neighbour])
    assert [item["medicine"] for item in answer["narrower"]] == ["Boxed"]
    assert lines(card(answer, "new_clues", "cluedown")) == {"NR3C1": None}


def test_g_a_boxed_medicine_does_not_make_a_protein_both_ways():
    # mifepristone (down, main list) and BOXED (up, wider box): still one-way down.
    boxed_path, neighbour = boxed(PARENT, WIDER)
    answer = cards([MIFEPRISTONE, boxed_path, DEXAMETHASONE], neighbours=[neighbour])
    assert lines(card(answer, "new_clues", "dexamethasone")) == {"NR3C1": LINE}


# ---- h. In trials cards get the line too ----

def test_h_in_trials_card_the_opposite_way_has_the_line():
    studied = path("STUDIEDUP", "CHEMBL9009", NR3C1, UP, IN_TRIALS)
    answer = cards([MIFEPRISTONE, studied])
    assert lines(card(answer, "being_studied", "studiedup")) == {"NR3C1": LINE}


def test_h_in_trials_card_the_same_way_has_no_line():
    studied = path("STUDIEDDOWN", "CHEMBL9010", NR3C1, DOWN, IN_TRIALS)
    answer = cards([MIFEPRISTONE, studied])
    assert lines(card(answer, "being_studied", "studieddown")) == {"NR3C1": None}


# ---- rule 5. Approved cards never get the line ----

def test_approved_cards_never_have_the_line():
    boxed_path, neighbour = boxed(PARENT, WIDER)
    # On ADRB1, dobutamine and metoprolol turn opposite ways to each other.
    answer = cards([MIFEPRISTONE, DOBUTAMINE, METOPROLOL, boxed_path, DEXAMETHASONE],
                   neighbours=[neighbour])
    for tab in ("approved", "wider_group"):
        for item in answer[tab]:
            for protein in item["proteins"]:
                assert "opposite_way" not in protein, (tab, item["medicine"])


def test_in_trials_medicine_also_in_a_box_gets_the_line_only_on_its_in_trials_card():
    listed = Listed("CHEMBL9009", "STUDIEDUP", (("CHEMBL9009", "STUDIEDUP"),), ())
    studied = path("STUDIEDUP", "CHEMBL9009", NR3C1, UP, IN_TRIALS)
    answer = cards([MIFEPRISTONE, studied],
                   neighbours=[Neighbour(PARENT, WIDER, (listed,), ())])
    assert lines(card(answer, "being_studied", "studiedup")) == {"NR3C1": LINE}
    assert "opposite_way" not in card(answer, "wider_group", "studiedup")["proteins"][0]


# ---- where it shows: only by the protein it is true for ----

def test_card_with_two_proteins_has_the_line_only_by_the_one_it_is_true_for():
    # One medicine, two proteins. Opposite on NR3C1, the same way on ADRB1.
    form = MedicineForm("CHEMBL9011", "TWOPROTEINS", best_stage="APPROVAL", withdrawn=False)
    medicine = Medicine("TWOPROTEINS", (form,))
    two = [Path(medicine, NR3C1, DISEASE, UP, NR3C1.score, ()),
           Path(medicine, ADRB1, DISEASE, DOWN, ADRB1.score, ())]
    answer = cards([MIFEPRISTONE, METOPROLOL] + two)
    assert lines(card(answer, "new_clues", "twoproteins")) == {"NR3C1": LINE, "ADRB1": None}


# ---- do not change ----

def test_order_of_the_cards_is_the_same_and_no_card_is_hidden():
    same_way = path("SAMEWAY", "CHEMBL9003", NR3C1, DOWN)
    unclear = path("CLUEUNCLEAR", "CHEMBL9007", NR3C1, UNKNOWN)
    studied = path("STUDIEDUP", "CHEMBL9009", NR3C1, UP, IN_TRIALS)
    clues = [DEXAMETHASONE, same_way, unclear, studied]
    with_approved = cards([MIFEPRISTONE] + clues)
    without = cards(clues)  # no approved medicine, so no line anywhere
    for tab in ("new_clues", "being_studied"):
        assert [item["medicine"] for item in with_approved[tab]] == \
               [item["medicine"] for item in without[tab]]
        for item in without[tab]:
            assert lines(item) == {"NR3C1": None}
    assert len(with_approved["new_clues"]) == 3
    assert len(with_approved["being_studied"]) == 1


def test_the_line_changes_nothing_else_on_the_card():
    with_approved = card(cards([MIFEPRISTONE, DEXAMETHASONE]), "new_clues", "dexamethasone")
    without = card(cards([DEXAMETHASONE]), "new_clues", "dexamethasone")
    assert with_approved["proteins"][0].pop("opposite_way") == LINE
    assert with_approved == without  # the ending, the direction, the points: all the same


# ---- the page ----

@pytest.fixture
def page():
    return TestClient(api.app).get("/").text


def card_template(page):
    return re.search(r'<template id="card-template">.*?</template>', page, re.S).group(0)


def test_page_shows_the_line_from_the_protein_it_belongs_to(page):
    assert "protein.opposite_way" in page
    # The page never writes the words itself: they come from the engine.
    assert LINE not in page


def test_page_line_is_plain_text_with_no_red_and_no_icon(page):
    rule = re.search(r"\.opposite-way\{[^}]*\}", page).group(0)
    assert "#D40000" not in rule and "red" not in rule
    assert "var(--muted)" in rule  # the same quiet grey as the direction note
    template = re.search(r'<template id="opposite-way-template">.*?</template>', page, re.S).group(0)
    assert "<svg" not in template and "<img" not in template


def test_page_still_has_the_direction_words_on_every_card(page):
    assert f'<p class="direction-note">{NO_DIRECTION}</p>' in card_template(page)
