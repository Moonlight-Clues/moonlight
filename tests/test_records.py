"""Ticket 1.3. Each EXAMPLE from Kashish's paper graph is one test here.

These tests build records by hand. They read no files and use no network.
"""

import pytest

from moonlight.records import (
    STAGE_ORDER,
    Disease,
    Medicine,
    MedicineForm,
    Path,
    Target,
    direction_from_action_types,
    stronger_stage,
)


def form(id, name, best_stage, disease_stage=None, parent_id=None):
    return MedicineForm(
        id=id,
        name=name,
        best_stage=best_stage,
        disease_stage=disease_stage,
        parent_id=parent_id,
    )


# Example 1
def test_sildenafil_and_its_citrate_are_one_medicine():
    sildenafil = form("CHEMBL192", "SILDENAFIL", "APPROVAL", "PHASE_3")
    citrate = form(
        "CHEMBL1737", "SILDENAFIL CITRATE", "APPROVAL", "APPROVAL", "CHEMBL192"
    )

    medicine = Medicine(name="SILDENAFIL", forms=[sildenafil, citrate])

    assert len(medicine.forms) == 2
    assert medicine.best_stage == "APPROVAL"
    assert medicine.disease_stage == "APPROVAL"


# Example 2
def test_vardenafil_family_keeps_the_link_only_one_form_has():
    vardenafil = form("V1", "VARDENAFIL", "APPROVAL", "PHASE_3")
    hydrochloride = form("V2", "VARDENAFIL HYDROCHLORIDE", "APPROVAL", None, "V1")

    medicine = Medicine(name="VARDENAFIL", forms=[vardenafil, hydrochloride])

    assert len(medicine.forms) == 2
    assert medicine.disease_stage == "PHASE_3"


# Example 2 again, with the forms the other way round: order must not matter.
def test_form_order_does_not_change_the_disease_stage():
    vardenafil = form("V1", "VARDENAFIL", "APPROVAL", "PHASE_3")
    hydrochloride = form("V2", "VARDENAFIL HYDROCHLORIDE", "APPROVAL", None, "V1")

    medicine = Medicine(name="VARDENAFIL", forms=[hydrochloride, vardenafil])

    assert medicine.disease_stage == "PHASE_3"


# Example 3
def test_doxapram_family_with_no_link_has_disease_stage_none():
    doxapram = form("D1", "DOXAPRAM", "APPROVAL")
    hydrochloride = form("D2", "DOXAPRAM HYDROCHLORIDE", "APPROVAL", None, "D1")

    medicine = Medicine(name="DOXAPRAM", forms=[doxapram, hydrochloride])

    assert len(medicine.forms) == 2
    assert medicine.best_stage == "APPROVAL"
    assert medicine.disease_stage is None


# Example 4
def test_tadalafil_alone_is_a_medicine_with_one_form():
    tadalafil = form("T1", "TADALAFIL", "APPROVAL")

    medicine = Medicine(name="TADALAFIL", forms=[tadalafil])

    assert len(medicine.forms) == 1
    assert medicine.forms[0] == tadalafil
    assert medicine.best_stage == "APPROVAL"


def test_best_stage_is_the_strongest_of_the_forms():
    medicine = Medicine(
        name="X", forms=[form("X1", "X", "PHASE_2"), form("X2", "X SALT", "PHASE_3")]
    )

    assert medicine.best_stage == "PHASE_3"


def test_a_medicine_needs_at_least_one_form():
    with pytest.raises(ValueError):
        Medicine(name="NOTHING", forms=[])


# Example 5
def test_phase_2_3_sits_between_phase_2_and_phase_3():
    assert stronger_stage("PHASE_2_3", "PHASE_2") == "PHASE_2_3"
    assert stronger_stage("PHASE_2", "PHASE_2_3") == "PHASE_2_3"
    assert stronger_stage("PHASE_2_3", "PHASE_3") == "PHASE_3"
    assert stronger_stage("PHASE_3", "PHASE_2_3") == "PHASE_3"


def test_stage_order_is_the_one_in_the_ticket():
    assert STAGE_ORDER == (
        "APPROVAL",
        "PHASE_4",
        "PHASE_3",
        "PHASE_2_3",
        "PHASE_2",
        "PHASE_1_2",
        "PHASE_1",
        "EARLY_PHASE_1",
        "IND",
        "PRECLINICAL",
        "WITHDRAWAL",
        "UNKNOWN",
    )
    for stronger, weaker in zip(STAGE_ORDER, STAGE_ORDER[1:]):
        assert stronger_stage(stronger, weaker) == stronger
        assert stronger_stage(weaker, stronger) == stronger


def test_any_stage_is_stronger_than_no_stage():
    assert stronger_stage("UNKNOWN", None) == "UNKNOWN"
    assert stronger_stage(None, "PHASE_1") == "PHASE_1"
    assert stronger_stage(None, None) is None


# Changed in ticket 2.10 with Kashish's yes (2026-11-15). It used to say
# that a stage word we do not know IS an error.
def test_a_stage_word_we_do_not_know_is_not_an_error_and_is_not_approved():
    assert stronger_stage("PHASE_9", "APPROVAL") == "APPROVAL"
    z = form("Z1", "Z", "approved-ish")
    assert Medicine(name="Z", forms=[z]).best_stage != "APPROVAL"


# Example 6
def test_direction_examples():
    assert direction_from_action_types(["INHIBITOR"]) == "down"
    assert direction_from_action_types(["OPENER"]) == "up"
    assert direction_from_action_types([]) == "unknown"


@pytest.mark.parametrize("action", ["INHIBITOR", "ANTAGONIST", "BLOCKER"])
def test_down_action_types(action):
    assert direction_from_action_types([action]) == "down"


@pytest.mark.parametrize(
    "action",
    ["AGONIST", "OPENER", "POSITIVE MODULATOR", "POSITIVE ALLOSTERIC MODULATOR"],
)
def test_up_action_types(action):
    assert direction_from_action_types([action]) == "up"


def test_up_and_down_together_is_mixed():
    assert direction_from_action_types(["INHIBITOR", "AGONIST"]) == "mixed"


def test_an_action_type_not_on_either_list_is_unknown():
    assert direction_from_action_types(["MODULATOR"]) == "unknown"


def test_path_holds_the_whole_chain_and_its_direction():
    disease = Disease(id="MONDO_0015924", name="pulmonary arterial hypertension")
    target = Target(
        id="ENSG00000138735",
        symbol="PDE5A",
        name="phosphodiesterase 5A",
        score=0.61,
    )
    medicine = Medicine(name="TADALAFIL", forms=[form("T1", "TADALAFIL", "APPROVAL")])

    path = Path(
        medicine=medicine,
        target=target,
        disease=disease,
        action_types=["INHIBITOR"],
        score=0.61,
        sources=["https://example.org/label"],
    )

    assert path.medicine is medicine
    assert path.target.symbol == "PDE5A"
    assert path.disease.name == "pulmonary arterial hypertension"
    assert path.action_types == ("INHIBITOR",)
    assert path.direction == "down"
    assert path.score == 0.61
    assert path.sources == ("https://example.org/label",)


def test_path_with_no_action_types_says_unknown():
    path = Path(
        medicine=Medicine(name="T", forms=[form("T1", "T", "APPROVAL")]),
        target=Target(id="E1", symbol="S", name="n", score=0.5),
        disease=Disease(id="D1", name="d"),
        action_types=[],
        score=0.5,
        sources=[],
    )

    assert path.direction == "unknown"


# ---- Ticket 2.8. A path knows the other pieces of its machine ----

def _plain_path(**extra):
    return Path(
        medicine=Medicine(name="T", forms=[form("T1", "T", "APPROVAL")]),
        target=Target(id="E1", symbol="S", name="n", score=0.5),
        disease=Disease(id="D1", name="d"),
        action_types=[],
        score=0.5,
        sources=[],
        **extra,
    )


def test_path_has_no_machine_partners_unless_told():
    assert _plain_path().same_machine_ids == ()


def test_path_keeps_the_ids_of_the_other_pieces_of_its_machine():
    path = _plain_path(same_machine_ids=["E2", "E3"])
    assert path.same_machine_ids == ("E2", "E3")


# ---- Ticket 3.5: a disease can carry a description ----

def test_disease_description_is_empty_by_default():
    assert Disease(id="D1", name="d").description == ""


def test_disease_can_hold_a_description():
    disease = Disease(id="D1", name="d", description="A made-up disease for this test.")
    assert disease.description == "A made-up disease for this test."


# ---- Ticket 3.5 add-on: ACTIVATOR is "up", BINDING AGENT stays "unknown" ----

def test_activator_gives_up():
    assert direction_from_action_types(["ACTIVATOR"]) == "up"


def test_binding_agent_alone_gives_unknown():
    assert direction_from_action_types(["BINDING AGENT"]) == "unknown"


def test_binding_agent_does_not_change_a_known_direction():
    assert direction_from_action_types(["BINDING AGENT", "ACTIVATOR"]) == "up"
    assert direction_from_action_types(["BINDING AGENT", "INHIBITOR"]) == "down"


def test_activator_with_a_down_word_is_mixed():
    assert direction_from_action_types(["ACTIVATOR", "INHIBITOR"]) == "mixed"


# ---- Ticket 2.10: stage words PRECLINICAL and IND, and words we do not know ----
#
# The two saved files in fixtures/stage_words/ are live Open Targets answers
# from 2026-11-15 (data version 26.09). No test here touches the network:
# fetch._post_json is swapped for a function that hands back a saved file.

import copy
import json
import pathlib
from unittest.mock import patch

from moonlight import fetch
from moonlight.filter import NOT_APPROVED, group_of

STAGE_WORDS = pathlib.Path(__file__).resolve().parent.parent / "fixtures" / "stage_words"
ASTHMA = Disease(id="MONDO_0004979", name="asthma")
MIGRAINE = Disease(id="MONDO_0005277", name="migraine disorder")
ADORA2B = Target(id="ENSG00000170425", symbol="ADORA2B", name="adenosine A2b receptor", score=0.5)
SCN1A = Target(
    id="ENSG00000144285",
    symbol="SCN1A",
    name="sodium voltage-gated channel alpha subunit 1",
    score=0.5,
)


def _saved(name):
    file = STAGE_WORDS / f"{name}.response.json"
    return json.loads(file.read_text(encoding="utf-8"))


def _medicine_from(answer, disease, target, name):
    """Read a saved answer the way Moonlight does and pick one medicine out."""
    with patch.object(fetch, "_post_json", return_value=answer):
        paths = fetch.fetch_paths(disease, target)
    found = [path.medicine for path in paths if path.medicine.name == name]
    assert len(found) == 1, f"{name} is not in the saved answer"
    return found[0]


# Example 1
def test_a_medicine_whose_best_stage_is_preclinical_is_not_approved():
    answer = _saved("asthma_ADORA2B_ENSG00000170425")

    medicine = _medicine_from(answer, ASTHMA, ADORA2B, "LAS101057")

    assert medicine.best_stage == "PRECLINICAL"
    assert group_of(medicine) == NOT_APPROVED


# Example 2
def test_a_medicine_whose_best_stage_is_ind_is_not_approved():
    answer = _saved("migraine_SCN1A_ENSG00000144285")

    medicine = _medicine_from(answer, MIGRAINE, SCN1A, "NKTR-171")

    assert medicine.best_stage == "IND"
    assert group_of(medicine) == NOT_APPROVED


# Example 3. The saved asthma answer, with one medicine's stage words
# swapped for a made-up one. The file itself is not changed.
def test_a_medicine_whose_best_stage_is_a_made_up_word_is_not_approved():
    answer = copy.deepcopy(_saved("asthma_ADORA2B_ENSG00000170425"))
    swapped = 0
    for row in answer["data"]["target"]["drugAndClinicalCandidates"]["rows"]:
        drug = row["drug"]
        if drug["name"] == "LAS101057":
            drug["maximumClinicalStage"] = "MOON_STAGE"
            for indication in drug["indications"]["rows"]:
                indication["maxClinicalStage"] = "MOON_STAGE"
            swapped += 1
    assert swapped == 1

    medicine = _medicine_from(answer, ASTHMA, ADORA2B, "LAS101057")  # nothing raises

    assert medicine.best_stage == "MOON_STAGE"
    assert medicine.disease_stage == "MOON_STAGE"
    assert group_of(medicine) == NOT_APPROVED


def test_a_made_up_stage_word_never_raises_by_hand():
    made_up = form("M1", "MOON MEDICINE", "MOON_STAGE", "MOON_STAGE")
    medicine = Medicine(name="MOON MEDICINE", forms=[made_up])

    assert medicine.best_stage == "MOON_STAGE"
    assert stronger_stage("MOON_STAGE", None) == "MOON_STAGE"
    assert stronger_stage(None, "MOON_STAGE") == "MOON_STAGE"
    assert group_of(medicine) == NOT_APPROVED


def test_every_saved_medicine_can_be_read_without_an_error():
    for name, disease, target in (
        ("asthma_ADORA2B_ENSG00000170425", ASTHMA, ADORA2B),
        ("migraine_SCN1A_ENSG00000144285", MIGRAINE, SCN1A),
    ):
        with patch.object(fetch, "_post_json", return_value=_saved(name)):
            paths = fetch.fetch_paths(disease, target)
        assert paths
        for path in paths:
            assert path.medicine.best_stage  # worked out, no error


def test_preclinical_and_ind_sit_between_withdrawal_and_the_phases():
    # Lowest to highest: WITHDRAWAL, PRECLINICAL, IND, then the phases.
    assert stronger_stage("PRECLINICAL", "WITHDRAWAL") == "PRECLINICAL"
    assert stronger_stage("WITHDRAWAL", "PRECLINICAL") == "PRECLINICAL"
    assert stronger_stage("IND", "PRECLINICAL") == "IND"
    assert stronger_stage("PRECLINICAL", "IND") == "IND"
    assert stronger_stage("EARLY_PHASE_1", "IND") == "EARLY_PHASE_1"
    assert stronger_stage("IND", "EARLY_PHASE_1") == "EARLY_PHASE_1"
    assert stronger_stage("APPROVAL", "IND") == "APPROVAL"


def test_every_stage_word_on_the_ladder_is_spelled_as_open_targets_spells_it():
    # PHASE_4 and WITHDRAWAL are not in the two new files. They are in the
    # golden disease's saved files from ticket 1.1.
    golden = STAGE_WORDS.parent / "MONDO_0015924"
    text = "".join(
        file.read_text(encoding="utf-8")
        for folder in (STAGE_WORDS, golden, golden / "target_drugs")
        for file in sorted(folder.glob("*.response.json"))
    )
    for word in STAGE_ORDER:
        assert f'ClinicalStage": "{word}"' in text, f"{word} is in no saved answer"


def test_a_known_stage_word_beats_a_made_up_one():
    for known in STAGE_ORDER:
        assert stronger_stage(known, "MOON_STAGE") == known
        assert stronger_stage("MOON_STAGE", known) == known


# Example 4
def test_a_family_takes_the_strongest_stage_of_its_forms_with_the_new_words():
    def family(*stages):
        forms = [form(f"F{n}", f"FORM {n}", stage) for n, stage in enumerate(stages)]
        return Medicine(name="F", forms=forms)

    assert family("PRECLINICAL", "IND").best_stage == "IND"
    assert family("IND", "PRECLINICAL").best_stage == "IND"
    assert family("WITHDRAWAL", "PRECLINICAL").best_stage == "PRECLINICAL"
    assert family("IND", "PHASE_1").best_stage == "PHASE_1"
    assert family("PRECLINICAL", "APPROVAL").best_stage == "APPROVAL"
    assert family("MOON_STAGE", "APPROVAL").best_stage == "APPROVAL"
    assert family("APPROVAL", "MOON_STAGE").best_stage == "APPROVAL"
    assert family("MOON_STAGE", "PRECLINICAL").best_stage == "PRECLINICAL"


def test_a_family_takes_the_strongest_link_of_its_forms_with_the_new_words():
    medicine = Medicine(
        name="G",
        forms=[
            form("G1", "G", "APPROVAL", "IND"),
            form("G2", "G SALT", "APPROVAL", "PHASE_2", "G1"),
            form("G3", "G OTHER SALT", "APPROVAL", None, "G1"),
        ],
    )

    assert medicine.disease_stage == "PHASE_2"
