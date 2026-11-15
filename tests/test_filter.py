"""Ticket 2.4. Each EXAMPLE from Kashish's paper graph is one test here.

These tests build Medicine records by hand. They read no files and use no
network.
"""

import pytest

from moonlight.filter import GROUPS, SHOWN_GROUPS, group_of, sort_paths
from moonlight.records import Disease, Medicine, MedicineForm, Path, Target


def form(name, best_stage, disease_stage=None, parent_id=None):
    return MedicineForm(
        id="ID_" + name.upper().replace(" ", "_"),
        name=name,
        best_stage=best_stage,
        disease_stage=disease_stage,
        parent_id=parent_id,
    )


def single(name, best_stage, disease_stage=None):
    """A medicine with only one form."""
    return Medicine(name=name, forms=(form(name, best_stage, disease_stage),))


def family(name, *forms):
    return Medicine(name=name, forms=forms)


# Example 1
def test_avanafil_approved_with_no_link_is_a_new_clue():
    assert group_of(single("Avanafil", "APPROVAL")) == "new_clue"


# Example 2
def test_tadalafil_approved_for_the_disease_is_already_approved():
    assert group_of(single("Tadalafil", "APPROVAL", "APPROVAL")) == "already_approved"


# Example 3
def test_udenafil_in_trials_for_the_disease_is_being_studied():
    assert group_of(single("Udenafil", "APPROVAL", "PHASE_2_3")) == "being_studied"


# Example 4
def test_gisadenafil_not_approved_anywhere_is_not_approved():
    assert group_of(single("Gisadenafil", "PHASE_2")) == "not_approved"


# Example 5
def test_bq123_question_1_wins_even_though_it_has_a_link():
    assert group_of(single("BQ-123", "PHASE_2", "PHASE_2")) == "not_approved"


# Example 6
def test_sparsentan_best_stage_is_not_the_link():
    assert group_of(single("Sparsentan", "APPROVAL")) == "new_clue"


# Example 7
def test_sildenafil_family_is_already_approved():
    sildenafil = family(
        "Sildenafil",
        form("Sildenafil", "APPROVAL", "PHASE_3"),
        form("Sildenafil Citrate", "APPROVAL", "APPROVAL", parent_id="ID_SILDENAFIL"),
    )
    assert group_of(sildenafil) == "already_approved"


# Example 8
def test_vardenafil_family_is_being_studied_and_tablet_form_is_not_a_new_clue():
    vardenafil = family(
        "Vardenafil",
        form("Vardenafil", "APPROVAL", "PHASE_3"),
        form("Vardenafil Hydrochloride", "APPROVAL", None, parent_id="ID_VARDENAFIL"),
    )
    assert group_of(vardenafil) == "being_studied"

    # The whole family travels as ONE path, so the tablet form cannot turn
    # up in the new-clue list on its own.
    sorted_paths = sort_paths([path_for(vardenafil)])
    assert sorted_paths["new_clue"] == []
    assert [p.medicine.name for p in sorted_paths["being_studied"]] == ["Vardenafil"]


# Example 9
def test_sitaxentan_family_is_already_approved():
    sitaxentan = family(
        "Sitaxentan",
        form("Sitaxentan", "APPROVAL", "APPROVAL"),
        form("Sitaxentan Sodium", "APPROVAL", "PHASE_3", parent_id="ID_SITAXENTAN"),
    )
    assert group_of(sitaxentan) == "already_approved"


# Example 10
def test_doxapram_family_with_no_link_is_a_new_clue():
    doxapram = family(
        "Doxapram",
        form("Doxapram", "APPROVAL"),
        form("Doxapram Hydrochloride", "APPROVAL", parent_id="ID_DOXAPRAM"),
    )
    assert group_of(doxapram) == "new_clue"


# The rest of the CONTRACT


@pytest.mark.parametrize(
    "stage",
    ["PHASE_4", "PHASE_3", "PHASE_2_3", "PHASE_2", "PHASE_1_2", "PHASE_1", "EARLY_PHASE_1"],
)
def test_every_phase_stage_for_the_disease_is_being_studied(stage):
    assert group_of(single("Testamil", "APPROVAL", stage)) == "being_studied"


@pytest.mark.parametrize("stage", ["WITHDRAWAL", "UNKNOWN"])
def test_withdrawal_or_unknown_link_is_unclear_link(stage):
    assert group_of(single("Testamil", "APPROVAL", stage)) == "unclear_link"


def test_not_approved_wins_over_an_unclear_link():
    assert group_of(single("Testamil", "PHASE_3", "WITHDRAWAL")) == "not_approved"


def test_only_new_clue_and_being_studied_are_shown():
    assert GROUPS == (
        "not_approved",
        "new_clue",
        "being_studied",
        "already_approved",
        "unclear_link",
    )
    assert SHOWN_GROUPS == ("new_clue", "being_studied")


PAH = Disease(id="MONDO_0015924", name="pulmonary arterial hypertension")
PDE5A = Target(id="ENSG00000138735", symbol="PDE5A", name="phosphodiesterase 5A", score=0.6)


def path_for(medicine):
    return Path(
        medicine=medicine,
        target=PDE5A,
        disease=PAH,
        action_types=("INHIBITOR",),
        score=0.6,
        sources=("Open Targets",),
    )


def test_sort_paths_puts_each_path_in_its_medicines_group():
    avanafil = path_for(single("Avanafil", "APPROVAL"))
    tadalafil = path_for(single("Tadalafil", "APPROVAL", "APPROVAL"))
    udenafil = path_for(single("Udenafil", "APPROVAL", "PHASE_2_3"))
    gisadenafil = path_for(single("Gisadenafil", "PHASE_2"))
    sparsentan = path_for(single("Sparsentan", "APPROVAL"))
    withdrawn = path_for(single("Testamil", "APPROVAL", "WITHDRAWAL"))

    result = sort_paths([avanafil, tadalafil, udenafil, gisadenafil, sparsentan, withdrawn])

    assert result == {
        "not_approved": [gisadenafil],
        "new_clue": [avanafil, sparsentan],  # same order they came in
        "being_studied": [udenafil],
        "already_approved": [tadalafil],
        "unclear_link": [withdrawn],
    }


def test_sort_paths_with_nothing_gives_every_group_empty():
    assert sort_paths([]) == {group: [] for group in GROUPS}


# ---- Ticket 2.10: a link word that is not a phase and not APPROVAL ----
# Kashish's decision, 2026-11-15: such a link is "unclear link". It never raises.

# Real example, read from Open Targets on 2026-11-15: gabapentin is approved,
# and its link to anxiety disorder is IND.
def test_gabapentin_with_an_ind_link_is_unclear_link():
    assert group_of(single("Gabapentin", "APPROVAL", "IND")) == "unclear_link"


def test_a_preclinical_link_is_unclear_link():
    assert group_of(single("Testamil", "APPROVAL", "PRECLINICAL")) == "unclear_link"


def test_a_preapproval_link_is_unclear_link():
    assert group_of(single("Testamil", "APPROVAL", "PREAPPROVAL")) == "unclear_link"


def test_a_made_up_link_word_is_unclear_link_and_nothing_raises():
    moon = path_for(single("Moonamil", "APPROVAL", "MOON_LINK"))

    assert group_of(moon.medicine) == "unclear_link"
    assert sort_paths([moon])["unclear_link"] == [moon]


def test_a_family_with_an_ind_link_and_a_phase_link_is_still_being_studied():
    medicine = family(
        "Testamil",
        form("Testamil", "APPROVAL", "IND"),
        form("Testamil Sodium", "APPROVAL", "PHASE_2", parent_id="ID_TESTAMIL"),
    )
    assert group_of(medicine) == "being_studied"


def test_phases_approval_and_no_link_sort_exactly_as_before():
    assert group_of(single("Testamil", "APPROVAL")) == "new_clue"
    assert group_of(single("Testamil", "APPROVAL", "APPROVAL")) == "already_approved"
    for stage in ("PHASE_4", "PHASE_3", "PHASE_2_3", "PHASE_2", "PHASE_1_2", "PHASE_1", "EARLY_PHASE_1"):
        assert group_of(single("Testamil", "APPROVAL", stage)) == "being_studied"
    for stage in ("WITHDRAWAL", "UNKNOWN"):
        assert group_of(single("Testamil", "APPROVAL", stage)) == "unclear_link"
    for best in ("PHASE_3", "IND", "PRECLINICAL", "MOON_STAGE"):
        assert group_of(single("Testamil", best, "IND")) == "not_approved"
