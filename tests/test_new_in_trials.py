"""Ticket 2.24. A box for new medicines in trials.

Kashish's decisions, 23 Nov:

1. Today's In trials list and the ticket 2.21 box are unchanged: same
   cards, same order.
2. Under them, a second folded box labelled, in her exact words, "New
   medicines being tested for this disease. The database records no
   approval for them for any disease."
3. A medicine is in this box when all of these are true: the disease's own
   list gives it a trial stage for this disease; no form of it that we can
   see is approved for anything; it is not on any other tab or box of the
   page; no existing rule leaves it out (withdrawn, corrections, left out
   by hand).
4. A medicine for which "approved for something" CANNOT BE TOLD stays out
   of both boxes: the answer names a parent or a tablet form of it that
   has no row on the list, so nobody said how far that one got.
5. One card per medicine, forms merged. Furthest trial stage first, then
   A to Z.
6. A card shows the medicine, its trial stage and its source link, and
   ends with "Never start, stop or change any medicine without a doctor."
   No score and no explain button.
7. /api/clues gains one new key, "new_in_trials". Every old key keeps its
   meaning.
8. The tab count is the list plus both boxes. "No medicine in this data is
   being studied for this disease." is not shown when either box has cards.
9. The line above the In trials list now starts "Medicines being tested
   for this disease." The rest stays word for word.
10. No new request, and no change to any question asked of Open Targets.

Her example: limb-girdle muscular dystrophy (MONDO_0016971). The 2.21 box
holds prednisone (Phase 2). The new box holds ribitol (Phase 3), ATYR-1940
(Phase 1/2), bidridistrogene xeboparvovec (Phase 1/2). "In trials (4)".

Saved files only: fixtures/new_in_trials/ (see its README) and
fixtures/more_in_trials/. No network.
"""

import copy
import json
import pathlib
import shutil
import subprocess
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from moonlight import api, engine, fetch
from moonlight.engine import CHILD, PARENT, Neighbour, sort_into_tabs
from moonlight.fetch import Listed
from moonlight.filter import BEING_STUDIED, group_of, sort_paths
from moonlight.records import STAGE_ORDER, Disease, Medicine, MedicineForm, Path, Target

import test_more_in_trials
from test_more_in_trials import PBC, PBC_BOX_26, PBC_LIST_7
from source_3_11 import back_to_before as trials_back_to_before  # ticket 3.11: In trials links

ROOT = pathlib.Path(__file__).resolve().parent.parent
SAVED = ROOT / "fixtures" / "new_in_trials"
PAGE_FILE = ROOT / "web" / "index.html"
PAGE = PAGE_FILE.read_text(encoding="utf-8")

LGMD = Disease(id="MONDO_0016971", name="limb-girdle muscular dystrophy")

# Kashish's words, exactly.
LABEL = ("New medicines being tested for this disease. The database records no "
         "approval for them for any disease.")
OLD_BOX_LABEL = ("More medicines in trials for this disease. They do not act on one of "
                 "the 25 proteins.")
CARD_ENDING = "Never start, stop or change any medicine without a doctor."
EMPTY_SENTENCE = "No medicine in this data is being studied for this disease."
OLD_FIRST_SENTENCE = "Approved for another disease and now being tested for this one."
TRIALS_LINE = ("Medicines being tested for this disease. A separate research category, not a "
               "prediction of effectiveness. Not every trial is listed.")

# Her example, in the box's order. (id, name on the card, stage on the card)
LGMD_NEW_3 = [
    ("CHEMBL3137744", "Ribitol", "Phase 3"),
    ("CHEMBL4297550", "ATYR-1940", "Phase 1/2"),
    ("CHEMBL4650240", "Bidridistrogene Xeboparvovec", "Phase 1/2"),
]
# Primary biliary cholangitis: the ten on its own list that are in a trial,
# approved for nothing, and whose whole family is on the list. Seladelpar is
# not one of them: it is on today's list of 7.
PBC_NEW_10 = [
    ("CHEMBL2387408", "Linerixibat", "Phase 3"),
    ("CHEMBL3775741", "Tiomolibdate Diammonium", "Phase 3"),
    ("CHEMBL4298055", "Aldafermin", "Phase 2"),
    ("CHEMBL5314422", "Berberine Ursodeoxycholate", "Phase 2"),
    ("CHEMBL4297613", "Cilofexor", "Phase 2"),
    ("CHEMBL3545019", "MBX-8025", "Phase 2"),
    ("CHEMBL2109379", "NI-0801", "Phase 2"),
    ("CHEMBL4297942", "Quetmolimab", "Phase 2"),
    ("CHEMBL4303187", "Setanaxib", "Phase 2"),
    ("CHEMBL4298169", "Tropifexor", "Phase 2"),
]


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def saved_post_json(body):
    """Stands in for fetch._post_json with the files in fixtures/new_in_trials/."""
    assert set(body) == {"query", "variables"}
    query, variables = body["query"], body["variables"]
    if "targetId" in variables:
        return load(SAVED / "target_drugs" / f"{variables['targetId']}.response.json")
    disease_id = variables["diseaseId"]
    if "parents" in query:
        kind = "family"
    elif "associatedTargets" in query:
        kind = "associated_targets"
    elif "drugAndClinicalCandidates" in query:
        kind = "disease_drugs"
    else:
        kind = "disease"
    return load(SAVED / kind / f"{disease_id}.response.json")


@pytest.fixture
def offline():
    with patch("moonlight.fetch._post_json", side_effect=saved_post_json) as mock:
        yield mock


@pytest.fixture
def client():
    api.forget_visitors()
    return TestClient(api.app)


@pytest.fixture
def lgmd(offline, client):
    """What /api/clues answers for the example, from saved answers."""
    answer = client.get("/api/clues", params={"disease_id": LGMD.id})
    assert answer.status_code == 200
    return answer.json()


@pytest.fixture
def pbc(client):
    with patch("moonlight.fetch._post_json", side_effect=test_more_in_trials.saved_post_json), \
            test_more_in_trials.without_hand_approvals_for_the_example():  # ticket 2.34
        answer = client.get("/api/clues", params={"disease_id": PBC.id})
    assert answer.status_code == 200
    return answer.json()


# ---- fetch: can the list tell whether the whole family was seen? ----

OURS = Disease(id="MONDO_TEST", name="test disease")
PROTEIN = Target(id="ENSG_TEST", symbol="TEST1", name="test protein", score=0.5)


def row(drug_id, name, best, stage, parent=None, children=(), say_children=True):
    """One made-up row of the disease's own list, in Open Targets' shape."""
    drug = {"id": drug_id, "name": name, "maximumClinicalStage": best, "drugWarnings": [],
            "parentMolecule": ({"id": parent[0], "name": parent[1], "drugWarnings": []}
                               if parent else None)}
    if say_children:
        drug["childMolecules"] = [
            {"id": child_id, "name": child_name, "drugWarnings": []}
            for child_id, child_name in children]
    return {"maxClinicalStage": stage, "drug": drug,
            "clinicalReports": [{"url": f"https://example.org/{drug_id}", "clinicalStage": stage,
                                 "source": "ClinicalTrials.gov"}]}


def listed_from(rows):
    answer = {"data": {"disease": {"id": OURS.id, "drugAndClinicalCandidates": {
        "count": len(rows), "rows": rows}}}}
    with patch("moonlight.fetch._post_json", return_value=answer):
        return fetch.fetch_listed_medicines(OURS)


def test_a_medicine_alone_with_no_parent_and_no_tablet_form_is_wholly_seen():
    (entry,) = listed_from([row("CHEMBL_A", "ALPHA", "PHASE_3", "PHASE_2")])
    assert entry.all_seen is True


def test_a_parent_named_with_no_row_of_its_own_cannot_be_told():
    """Like cediranib maleate: the tablet form is on the list, the medicine
    it is a form of is only named."""
    (entry,) = listed_from([row("CHEMBL_SALT", "ALPHA MALEATE", "PHASE_3", "PHASE_2",
                                parent=("CHEMBL_A", "ALPHA"))])
    assert entry.all_seen is False


def test_a_tablet_form_named_with_no_row_of_its_own_cannot_be_told():
    """Like cenicriviroc: the medicine is on the list, one tablet form of
    it is only named."""
    (entry,) = listed_from([row("CHEMBL_A", "ALPHA", "PHASE_3", "PHASE_2",
                                children=[("CHEMBL_SALT", "ALPHA MALEATE")])])
    assert entry.all_seen is False


def test_a_medicine_and_all_its_tablet_forms_on_the_list_are_wholly_seen():
    (entry,) = listed_from([
        row("CHEMBL_A", "ALPHA", "PHASE_3", "PHASE_2", children=[("CHEMBL_SALT", "ALPHA MALEATE")]),
        row("CHEMBL_SALT", "ALPHA MALEATE", "PHASE_2", "PHASE_1", parent=("CHEMBL_A", "ALPHA")),
    ])
    assert entry.all_seen is True
    assert [form.name for form in entry.medicine.forms] == ["ALPHA", "ALPHA MALEATE"]


def test_one_of_two_tablet_forms_missing_cannot_be_told():
    (entry,) = listed_from([
        row("CHEMBL_A", "ALPHA", "PHASE_3", "PHASE_2",
            children=[("CHEMBL_SALT", "ALPHA MALEATE"), ("CHEMBL_SALT2", "ALPHA SODIUM")]),
        row("CHEMBL_SALT", "ALPHA MALEATE", "PHASE_2", "PHASE_1", parent=("CHEMBL_A", "ALPHA")),
    ])
    assert entry.all_seen is False


def test_an_answer_that_does_not_say_the_tablet_forms_cannot_be_told():
    """Answers saved before the tablet forms were asked for. Not said is
    not the same as none."""
    (entry,) = listed_from([row("CHEMBL_A", "ALPHA", "PHASE_3", "PHASE_2", say_children=False)])
    assert entry.all_seen is False


def test_a_record_made_without_saying_is_not_taken_as_wholly_seen():
    form = MedicineForm(id="CHEMBL_A", name="ALPHA", best_stage="PHASE_3", disease_stage="PHASE_2")
    assert fetch.OnList(medicine=Medicine(name="ALPHA", forms=(form,)), reports=()).all_seen is False


def test_the_question_is_word_for_word_the_one_on_main():
    """Kashish, 23 Nov: no change to any question asked of Open Targets."""
    question = fetch.DISEASE_DRUGS_QUERY
    assert "parentMolecule { id name drugWarnings { warningType } }" in question
    assert "childMolecules { id name drugWarnings { warningType } }" in question
    assert question.count("maximumClinicalStage") == 1


def test_the_example_list_is_read_from_the_saved_answer(offline):
    by_name = {entry.medicine.name: entry for entry in fetch.fetch_listed_medicines(LGMD)}
    assert sorted(by_name) == ["ATYR-1940", "BIDRIDISTROGENE XEBOPARVOVEC", "PREDNISONE", "RIBITOL"]
    assert all(entry.all_seen for entry in by_name.values())
    ribitol = by_name["RIBITOL"].medicine
    assert (ribitol.best_stage, ribitol.disease_stage, ribitol.withdrawn) == (
        "PHASE_3", "PHASE_3", False)
    assert by_name["BIDRIDISTROGENE XEBOPARVOVEC"].medicine.best_stage == "PHASE_3"
    assert by_name["BIDRIDISTROGENE XEBOPARVOVEC"].medicine.disease_stage == "PHASE_1_2"


# ---- engine: who is in the new box (made-up records, one rule at a time) ----

def on_list(family_id, name, stage, best="PHASE_3", withdrawn=False, reports=None, forms=None,
            all_seen=True):
    """One made-up family on the disease's own list. Approved for nothing,
    and wholly seen, unless said otherwise."""
    forms = forms or (MedicineForm(id=family_id, name=name, best_stage=best,
                                   disease_stage=stage, withdrawn=withdrawn),)
    if reports is None:
        reports = ((f"https://example.org/{family_id}", stage),)
    return fetch.OnList(medicine=Medicine(name=name, forms=forms), reports=tuple(reports),
                        all_seen=all_seen)


def path_for(family_id, name, best="APPROVAL", stage=None, withdrawn=False):
    """A made-up path: the medicine acts on one of the proteins looked at."""
    form = MedicineForm(id=family_id, name=name, best_stage=best, disease_stage=stage,
                        withdrawn=withdrawn)
    return Path(medicine=Medicine(name=name, forms=(form,)), target=PROTEIN, disease=OURS,
                action_types=("INHIBITOR",), score=0.5, sources=("https://example.org/p",))


def tabs_of(entries, paths=(), listed=(), withdrawn_listed=(), neighbours=()):
    return sort_into_tabs(sort_paths(list(paths)), list(listed), list(withdrawn_listed),
                          list(neighbours), on_list=entries)


def new_box(entries, **more):
    return tabs_of(entries, **more).new_in_trials


def test_in_a_trial_and_approved_for_nothing_is_in_the_new_box():
    tabs = tabs_of([on_list("CHEMBL_A", "ALPHA", "PHASE_2")])
    assert tabs.new_in_trials == [engine.TrialMedicine(
        id="CHEMBL_A", name="ALPHA", forms=("ALPHA",), stage="PHASE_2",
        sources=("https://example.org/CHEMBL_A",))]
    assert tabs.more_in_trials == []  # never in both boxes


def test_with_no_list_handed_in_there_is_no_new_box():
    tabs = sort_into_tabs(sort_paths([path_for("CHEMBL_P", "PAPA", stage="PHASE_2")]), [])
    assert tabs.new_in_trials == []


def test_approved_for_something_goes_in_the_2_21_box_not_the_new_one():
    tabs = tabs_of([on_list("CHEMBL_A", "ALPHA", "PHASE_2", best="APPROVAL")])
    assert tabs.new_in_trials == []
    assert [medicine.id for medicine in tabs.more_in_trials] == ["CHEMBL_A"]


@pytest.mark.parametrize("best", [word for word in STAGE_ORDER if word != "APPROVAL"]
                         + ["SOMETHING_NEW"])
def test_any_furthest_stage_that_is_not_approval_is_no_approval(best):
    assert [m.id for m in new_box([on_list("CHEMBL_A", "ALPHA", "PHASE_1", best=best)])] == [
        "CHEMBL_A"]


@pytest.mark.parametrize("stage", ["PHASE_4", "PHASE_3", "PHASE_2_3", "PHASE_2", "PHASE_1_2",
                                   "PHASE_1", "EARLY_PHASE_1"])
def test_every_trial_stage_counts(stage):
    assert [m.stage for m in new_box([on_list("CHEMBL_A", "ALPHA", stage)])] == [stage]


@pytest.mark.parametrize("stage", ["APPROVAL", "UNKNOWN", "WITHDRAWAL", "IND", "PRECLINICAL",
                                   "SOMETHING_NEW", None])
def test_a_stage_that_is_not_a_trial_in_people_is_not_in_the_new_box(stage):
    assert new_box([on_list("CHEMBL_A", "ALPHA", stage)]) == []


@pytest.mark.parametrize("stage", list(STAGE_ORDER) + ["SOMETHING_NEW", None])
def test_a_trial_stage_is_the_same_thing_as_for_the_in_trials_list(stage):
    """The new box and filter.group_of agree on which words are a trial."""
    approved = Medicine(name="A", forms=(MedicineForm(
        id="CHEMBL_A", name="A", best_stage="APPROVAL", disease_stage=stage),))
    in_new_box = bool(new_box([on_list("CHEMBL_A", "ALPHA", stage)]))
    assert in_new_box == (group_of(approved) == BEING_STUDIED)


def test_cannot_be_told_stays_out_of_both_boxes():
    """The eight of the ticket 2.21 report, and any other in their position."""
    tabs = tabs_of([on_list("CHEMBL_A", "ALPHA", "PHASE_2", all_seen=False)])
    assert tabs.new_in_trials == [] and tabs.more_in_trials == []


def test_cannot_be_told_from_a_real_answer_stays_out_of_both_boxes():
    """The probe's answers also hold the parent's stage. It is never read:
    Moonlight's own question does not ask for it."""
    salt = row("CHEMBL_SALT", "ALPHA MALEATE", "PHASE_2_3", "PHASE_2", parent=("CHEMBL_A", "ALPHA"))
    salt["drug"]["parentMolecule"]["maximumClinicalStage"] = "PHASE_3"  # even if it were sent
    tabs = tabs_of(listed_from([salt]))
    assert tabs.new_in_trials == [] and tabs.more_in_trials == []


def test_approved_and_cannot_be_told_is_in_the_2_21_box_as_before():
    """One approved form is enough to know. Ticket 2.21 is not changed."""
    tabs = tabs_of([on_list("CHEMBL_A", "ALPHA", "PHASE_2", best="APPROVAL", all_seen=False)])
    assert [medicine.id for medicine in tabs.more_in_trials] == ["CHEMBL_A"]
    assert tabs.new_in_trials == []


def test_a_withdrawn_medicine_is_left_out():
    assert new_box([on_list("CHEMBL_A", "ALPHA", "PHASE_2", withdrawn=True)]) == []


def test_withdrawn_not_said_is_not_guessed():
    assert len(new_box([on_list("CHEMBL_A", "ALPHA", "PHASE_2", withdrawn=None)])) == 1


def test_withdrawn_on_the_disease_s_own_list_is_left_out():
    gone = Listed(id="CHEMBL_A", name="ALPHA", forms=(("CHEMBL_A", "ALPHA"),), sources=(),
                  approved=False)
    assert new_box([on_list("CHEMBL_A", "ALPHA", "PHASE_2")], withdrawn_listed=[gone]) == []


def test_withdrawn_on_a_neighbour_s_list_is_left_out():
    gone = Listed(id="CHEMBL_A", name="ALPHA", forms=(("CHEMBL_A", "ALPHA"),), sources=(),
                  approved=False)
    wider = Neighbour(PARENT, Disease(id="MONDO_UP", name="wider"), approved=(), withdrawn=(gone,))
    assert new_box([on_list("CHEMBL_A", "ALPHA", "PHASE_2")], neighbours=[wider]) == []


def test_a_path_that_says_withdrawn_leaves_it_out():
    paths = [path_for("CHEMBL_A", "ALPHA", best="PHASE_3", withdrawn=True)]
    assert new_box([on_list("CHEMBL_A", "ALPHA", "PHASE_2")], paths=paths) == []


@pytest.mark.parametrize("role", [CHILD, PARENT])
def test_one_shown_in_an_approved_box_is_not_in_the_new_box(role):
    there = Listed(id="CHEMBL_A", name="ALPHA", forms=(("CHEMBL_A", "ALPHA"),), sources=())
    near = Neighbour(role, Disease(id="MONDO_NEAR", name="near"), approved=(there,), withdrawn=())
    tabs = tabs_of([on_list("CHEMBL_A", "ALPHA", "PHASE_2")], neighbours=[near])
    assert tabs.new_in_trials == []
    assert [m.id for m in tabs.narrower + tabs.wider_group] == ["CHEMBL_A"]


@pytest.mark.parametrize("stage", [None, "PHASE_2", "APPROVAL", "UNKNOWN"])
def test_a_form_seen_through_a_protein_that_is_approved_keeps_it_out(stage):
    """No form of it THAT WE CAN SEE is approved for anything. A path
    shows a form too."""
    paths = [path_for("CHEMBL_A", "ALPHA", best="APPROVAL", stage=stage)]
    assert new_box([on_list("CHEMBL_A", "ALPHA", "PHASE_2")], paths=paths) == []


def test_acting_on_a_protein_does_not_keep_it_out_and_the_count_stays():
    """The new box's label says nothing about proteins. The medicine is
    still counted as before in "not approved"."""
    paths = [path_for("CHEMBL_A", "ALPHA", best="PHASE_3", stage="PHASE_2")]
    tabs = tabs_of([on_list("CHEMBL_A", "ALPHA", "PHASE_2")], paths=paths)
    assert [medicine.id for medicine in tabs.new_in_trials] == ["CHEMBL_A"]
    assert tabs.left_out == {"not_approved": 1, "unclear_link": 0}
    assert tabs.being_studied == [] and tabs.new_clues == [] and tabs.approved == []


def test_forms_are_merged_into_one_card_with_the_strongest_stage():
    forms = (
        MedicineForm(id="CHEMBL_A", name="ALPHA", best_stage="PHASE_3", disease_stage="PHASE_1",
                     withdrawn=False),
        MedicineForm(id="CHEMBL_SALT", name="ALPHA MALEATE", best_stage="PHASE_2",
                     disease_stage="PHASE_2", parent_id="CHEMBL_A", withdrawn=False),
    )
    reports = (("https://example.org/one", "PHASE_1"), ("https://example.org/two", "PHASE_2"))
    (card,) = new_box([on_list("CHEMBL_A", "ALPHA", None, forms=forms, reports=reports)])
    assert card == engine.TrialMedicine(
        id="CHEMBL_A", name="ALPHA", forms=("ALPHA", "ALPHA MALEATE"), stage="PHASE_2",
        sources=("https://example.org/two", "https://example.org/one"))
    assert card.source_record == "https://example.org/two"  # the receipt for the card's stage


def test_one_approved_form_makes_the_whole_medicine_approved():
    forms = (
        MedicineForm(id="CHEMBL_A", name="ALPHA", best_stage="PHASE_3", disease_stage="PHASE_2",
                     withdrawn=False),
        MedicineForm(id="CHEMBL_SALT", name="ALPHA MALEATE", best_stage="APPROVAL",
                     disease_stage="PHASE_1", parent_id="CHEMBL_A", withdrawn=False),
    )
    tabs = tabs_of([on_list("CHEMBL_A", "ALPHA", None, forms=forms)])
    assert tabs.new_in_trials == []
    assert [medicine.id for medicine in tabs.more_in_trials] == ["CHEMBL_A"]


def test_the_order_is_furthest_stage_first_then_a_to_z():
    entries = [
        on_list("CHEMBL_1", "zeta", "PHASE_2"),
        on_list("CHEMBL_2", "BETA", "PHASE_1_2"),
        on_list("CHEMBL_3", "Alpha", "PHASE_2"),
        on_list("CHEMBL_4", "ATYR-1", "PHASE_1_2"),
        on_list("CHEMBL_5", "OMEGA", "PHASE_4"),
        on_list("CHEMBL_6", "DELTA", "EARLY_PHASE_1"),
    ]
    assert [medicine.name for medicine in new_box(entries)] == [
        "OMEGA", "Alpha", "zeta", "ATYR-1", "BETA", "DELTA"]


def test_the_2_21_box_is_the_same_with_and_without_new_medicines_on_the_list():
    approved = [on_list("CHEMBL_B", "BETA", "PHASE_2", best="APPROVAL"),
                on_list("CHEMBL_C", "GAMMA", "PHASE_3", best="APPROVAL")]
    new = [on_list("CHEMBL_A", "ALPHA", "PHASE_3")]
    assert tabs_of(approved + new).more_in_trials == tabs_of(approved).more_in_trials


def test_the_label_and_the_card_ending_are_kashishs_words():
    assert engine.NEW_IN_TRIALS_LABEL == LABEL
    assert engine.MORE_IN_TRIALS_ENDING == CARD_ENDING  # the same sentence as the 2.21 box
    assert engine.MORE_IN_TRIALS_LABEL == OLD_BOX_LABEL  # not changed


# ---- the API: her example, from saved answers ----

def test_example_the_list_is_empty_and_the_2_21_box_holds_prednisone(lgmd):
    assert lgmd["being_studied"] == []
    assert [(card["id"], card["medicine"], card["trial_phase"])
            for card in lgmd["more_in_trials"]] == [("CHEMBL635", "Prednisone", "Phase 2")]


def test_example_the_new_box_holds_the_three_in_this_order(lgmd):
    assert [(card["id"], card["medicine"], card["trial_phase"])
            for card in lgmd["new_in_trials"]] == LGMD_NEW_3


def test_example_the_tab_would_say_four(lgmd):
    total = len(lgmd["being_studied"]) + len(lgmd["more_in_trials"]) + len(lgmd["new_in_trials"])
    assert total == 4


def test_example_one_new_box_card_in_full(lgmd):
    assert lgmd["new_in_trials"][1] == {
        "id": "CHEMBL4297550",
        "medicine": "ATYR-1940",
        "forms": ["ATYR-1940"],
        "trial_phase": "Phase 1/2",
        "source": "https://clinicaltrials.gov/study/NCT02579239",
        "ending": CARD_ENDING,
    }
    # The receipt for the stage on the card, not the report of unknown stage.
    assert lgmd["new_in_trials"][0]["source"] == "https://ttd.idrblab.cn/data/drug/details/D5LZO9"


def test_example_a_new_box_card_has_no_score_and_nothing_to_explain(lgmd):
    for card in lgmd["new_in_trials"]:
        assert set(card) == {"id", "medicine", "forms", "trial_phase", "source", "ending"}
        assert card["ending"] == CARD_ENDING


def test_example_the_answer_has_these_parts_in_this_order(lgmd):
    assert [key for key in lgmd if key != "recruiting"] == [  # ticket R2: recruiting is set aside
        "disease", "about_disease", "rule_text", "approved", "being_studied", "new_clues",
        "left_out", "more_in_trials", "new_in_trials",
    ]


def test_example_the_other_tabs_are_as_the_study_found_them(lgmd):
    """Study P10, 23 Nov: Approved 0, New clues 1 (ocriplasmin)."""
    assert lgmd["approved"] == [] and "narrower" not in lgmd and "wider_group" not in lgmd
    assert [clue["medicine"] for clue in lgmd["new_clues"]] == ["Ocriplasmin"]
    assert lgmd["left_out"] == {"not_approved": 0, "unclear_link": 0}


def test_example_needs_no_more_requests_than_before(offline, client):
    assert client.get("/api/clues", params={"disease_id": LGMD.id}).status_code == 200
    asked = [call.args[0] for call in offline.call_args_list]
    questions = {(body["query"], json.dumps(body["variables"], sort_keys=True)) for body in asked}
    # The disease, its 25 proteins, the family, 25 protein lists, and the
    # own list with the one parent's and the two children's. Nothing new.
    assert len(questions) == 1 + 1 + 1 + 25 + 4
    known = {fetch.DISEASE_QUERY, fetch.TARGETS_QUERY, fetch.FAMILY_QUERY,
             fetch.TARGET_DRUGS_QUERY, fetch.DISEASE_DRUGS_QUERY}
    assert {body["query"] for body in asked} <= known


def test_a_new_box_card_cannot_be_explained(offline, client):
    with patch("moonlight.explain.explain") as explained, \
            patch("moonlight.api.data_version", return_value="26.09"):
        answer = client.get("/api/explain",
                            params={"disease_id": LGMD.id, "clue_id": "CHEMBL3137744"})
    assert answer.status_code == 404
    explained.assert_not_called()


def test_the_explainer_is_handed_the_same_names_as_before(offline):
    """The grounding check is not changed by this ticket."""
    found = api._find(LGMD.id)
    with patch("moonlight.api.fetch_listed_medicines", return_value=[]):
        without = api._find(LGMD.id)
    assert found.known_names == without.known_names
    assert "RIBITOL" not in found.known_names


def test_no_key_when_the_new_box_is_empty(offline, client):
    with patch("moonlight.api.fetch_listed_medicines", return_value=[]):
        answer = client.get("/api/clues", params={"disease_id": LGMD.id}).json()
    assert "new_in_trials" not in answer and "more_in_trials" not in answer


def test_a_medicine_left_out_by_hand_for_this_disease_is_not_in_the_new_box(offline, client):
    by_hand = [{"medicine_id": "CHEMBL3137744", "disease_id": LGMD.id, "date": "2026-11-23"},
               {"medicine_id": "CHEMBL4297550", "disease_id": "MONDO_OTHER", "date": "2026-11-23"}]
    with patch("moonlight.engine._read_left_out", return_value=by_hand):
        answer = client.get("/api/clues", params={"disease_id": LGMD.id}).json()
    assert [card["id"] for card in answer["new_in_trials"]] == ["CHEMBL4297550", "CHEMBL4650240"]
    assert "wrong_way_line" not in answer  # that line counts New clues only


def test_a_medicine_on_the_corrections_list_for_this_disease_is_not_in_the_new_box(
        offline, client):
    listed = [{"medicine_id": "CHEMBL4650240", "disease_id": LGMD.id, "date": "2026-11-23",
               "note": engine.CORRECTION_NOTE}]
    with patch("moonlight.engine._read_corrections", return_value=listed):
        answer = client.get("/api/clues", params={"disease_id": LGMD.id}).json()
    assert [card["id"] for card in answer["new_in_trials"]] == ["CHEMBL3137744", "CHEMBL4297550"]


# ---- the API: primary biliary cholangitis, from saved answers ----

def test_pbc_the_7_cards_and_the_26_box_cards_are_unchanged(pbc):
    assert [card["medicine"] for card in pbc["being_studied"]] == PBC_LIST_7
    assert [(card["id"], card["medicine"], card["trial_phase"])
            for card in pbc["more_in_trials"]] == PBC_BOX_26


def test_pbc_every_old_key_answers_what_it_answered_before(pbc):
    before = load(ROOT / "fixtures" / "more_in_trials" / "clues_before_2.21.json")
    before = test_more_in_trials.with_ursodiol_confirmed(before)  # ticket 2.42
    for key in before:
        assert trials_back_to_before(pbc)[key] == before[key], key
    # Ticket 2.42 added "no_regulator_box": taurursodiol is in the new box.
    assert set(pbc) - set(before) - {"recruiting"} == {"more_in_trials", "new_in_trials", "no_regulator_box"}  # ticket R2: recruiting is set aside


def test_pbc_the_new_box_holds_these_ten(pbc):
    assert [(card["id"], card["medicine"], card["trial_phase"])
            for card in pbc["new_in_trials"]] == PBC_NEW_10


def test_pbc_no_medicine_is_on_the_tab_twice(pbc):
    ids = ([card["id"] for card in pbc["being_studied"]]
           + [card["id"] for card in pbc["more_in_trials"]]
           + [card["id"] for card in pbc["new_in_trials"]])
    assert len(ids) == len(set(ids)) == 7 + 26 + 10
    names = [card["medicine"] for card in pbc["new_in_trials"]]
    assert "Seladelpar" not in names  # on today's list: approved through one of its forms


# ---- the page, read as text ----

def test_the_page_holds_the_new_box_under_the_2_21_box_with_the_exact_label():
    panel = PAGE[PAGE.index('id="panel-trials"'):PAGE.index('id="panel-clues"')]
    assert (panel.index('id="studied-cards"') < panel.index('id="more-trials-box"')
            < panel.index('id="new-trials-box"'))
    assert PAGE.count(LABEL) == 1 and LABEL in panel
    assert (f"<summary>{LABEL} (<span id=\"new-trials-count\"></span>) "
            "<span data-part=\"tap\">Tap to open</span></summary>") in panel
    assert '<details class="wider-box" id="new-trials-box" hidden>' in panel  # folded, like the others
    assert 'id="new-trials-cards"' in panel


def test_the_2_21_box_is_still_on_the_page_word_for_word():
    assert PAGE.count(OLD_BOX_LABEL) == 1
    assert (f"<summary>{OLD_BOX_LABEL} (<span id=\"more-trials-count\"></span>) "
            "<span data-part=\"tap\">Tap to open</span></summary>") in PAGE


def test_the_line_above_the_list_has_the_new_first_sentence_only():
    assert PAGE.count(f'<p class="section-desc">{TRIALS_LINE}</p>') == 1
    assert OLD_FIRST_SENTENCE not in PAGE
    before = (OLD_FIRST_SENTENCE + " A separate research category, not a prediction of "
              "effectiveness. Not every trial is listed.")
    assert TRIALS_LINE == before.replace(OLD_FIRST_SENTENCE, "Medicines being tested for this disease.")


def test_the_print_page_takes_its_line_from_the_page():
    assert '+ pageWords("#panel-trials .section-desc");' in PAGE


def test_the_other_words_of_the_in_trials_tab_are_not_changed():
    assert "<h2>Already being studied for this disease</h2>" in PAGE
    assert EMPTY_SENTENCE in PAGE
    assert ("For learning and research exploration, not medical advice. Never start, stop or "
            "change any medicine without a doctor.") in PAGE


# ---- the page, in a real browser ----

BROWSER_SCRIPT = r"""
"use strict";
const fs = require("fs");
const { chromium } = require("playwright");
const PAGE = fs.readFileSync(process.argv[1], "utf-8");
const ANSWERS = JSON.parse(fs.readFileSync(process.argv[2], "utf-8"));
const SITE = "http://moonlight.test";

function readTrials() {
  const shownOnPage = el => !!el && el.getClientRects().length > 0;
  const note = document.getElementById("studied-note");
  const readCard = card => ({
    name: card.querySelector('[data-slot="medicine-name"]').textContent,
    forms: card.querySelector('[data-slot="forms"]').textContent,
    phase: (card.querySelector('[data-slot="phase"]') || {}).textContent || null,
    source: (card.querySelector('[data-slot="source"]') || {}).href || null,
    sourceShown: shownOnPage(card.querySelector('[data-slot="source"]')),
    buttons: card.querySelectorAll("button:not(.report-link)").length,  // 3.3: the Report link is not an explain button
    explanation: card.querySelectorAll('[data-slot="explanation"]').length,
    ending: [...card.querySelectorAll('[data-slot="ending"]')].map(el => el.textContent),
    endingIsLastBeforeTheFoot: !!card.querySelector('[data-slot="ending"] + .card-foot'),
    rank: card.querySelectorAll('[data-slot="rank"]').length,
    proteins: card.querySelectorAll('[data-slot="protein"]').length,
    path: card.querySelectorAll('[data-slot="path"]').length,
    words: card.innerText.replace(/\s+/g, " ").trim(),
  });
  const readBox = (boxId, cardsId) => {
    const box = document.getElementById(boxId);
    const cards = [...document.querySelectorAll("#" + cardsId + " > .card")];
    return {
      shown: shownOnPage(box),
      open: box.open,
      summary: box.querySelector("summary").innerText.replace(/\s+/g, " ").trim(),
      cards: cards.map(readCard),
      cardsOnScreen: cards.filter(card => card.checkVisibility()).length,  // false inside a folded box
    };
  };
  const oldBox = document.getElementById("more-trials-box");
  return {
    tab: document.getElementById("tab-trials").innerText.replace(/\s+/g, " ").trim(),
    heading: document.querySelector("#panel-trials h2").innerText.trim(),
    line: document.querySelector("#panel-trials .section-desc").innerText.trim(),
    noteShown: shownOnPage(note) && note.textContent.trim() !== "",
    noteWords: note.textContent.trim(),
    list: [...document.querySelectorAll("#studied-cards > .card")].map(readCard),
    oldBox: readBox("more-trials-box", "more-trials-cards"),
    newBox: readBox("new-trials-box", "new-trials-cards"),
    newBoxIsAfterTheOldBox: !!(oldBox.compareDocumentPosition(document.getElementById("new-trials-box"))
      & Node.DOCUMENT_POSITION_FOLLOWING),
  };
}

async function oneSearch(browser, answer) {
  const context = await browser.newContext({ viewport: { width: 390, height: 844 } });
  const page = await context.newPage();
  const errors = [], explainCalls = [];
  page.on("pageerror", problem => errors.push(String(problem)));
  await page.addInitScript(() => { window.print = () => {}; });  // no print box in the test
  await context.route("**/*", route => {
    const url = route.request().url();
    if (url === SITE + "/" || url.startsWith(SITE + "/?"))
      return route.fulfill({ contentType: "text/html; charset=utf-8", body: PAGE });
    if (url.startsWith(SITE + "/api/clues?"))
      return route.fulfill({ contentType: "application/json", body: JSON.stringify(answer) });
    if (url.startsWith(SITE + "/api/explain?")) {
      explainCalls.push(url);
      return route.fulfill({ status: 404, contentType: "application/json", body: "{}" });
    }
    return route.abort();
  });
  await page.goto(SITE + "/?disease=MONDO_TEST");
  await page.waitForSelector("#found", { state: "visible" });
  await page.click("#tab-trials");
  const out = { errors };
  out.closed = await page.evaluate(readTrials);
  for (const id of ["more-trials-box", "new-trials-box"]) {
    const box = page.locator("#" + id);
    if (await box.isVisible() && !(await box.evaluate(el => el.open))) {
      await page.click("#" + id + " summary");
      await page.waitForTimeout(300);  // the box tells the page it was opened a moment later
    }
  }
  out.tapped = await page.evaluate(readTrials);
  out.explainAskedFor = explainCalls.map(url => new URL(url).searchParams.get("clue_id"));
  await page.click("#print-page");
  await page.waitForTimeout(300);
  out.printTrials = await page.evaluate(
    () => document.querySelector('#register [data-reg="trials"]').innerText.trim());
  await context.close();
  return out;
}

(async () => {
  const browser = await chromium.launch();
  const out = {};
  for (const name of Object.keys(ANSWERS)) out[name] = await oneSearch(browser, ANSWERS[name]);
  await browser.close();
  console.log(JSON.stringify(out));
})().catch(problem => { console.error(problem); process.exit(1); });
"""


@pytest.fixture(scope="module")
def answers():
    """Answers of /api/clues: her example, primary biliary cholangitis,
    that one as it was before ticket 2.21, and three cut-down ones."""
    api.forget_visitors()
    with patch("moonlight.fetch._post_json", side_effect=saved_post_json):
        example = TestClient(api.app).get("/api/clues", params={"disease_id": LGMD.id}).json()
    with patch("moonlight.fetch._post_json", side_effect=test_more_in_trials.saved_post_json), \
            test_more_in_trials.without_hand_approvals_for_the_example():  # ticket 2.34
        liver = TestClient(api.app).get("/api/clues", params={"disease_id": PBC.id}).json()
    liver = trials_back_to_before(liver)  # ticket 3.11
    only_new = copy.deepcopy(example)
    del only_new["more_in_trials"]
    nothing = copy.deepcopy(only_new)
    del nothing["new_in_trials"]
    return {"example": example, "pbc": liver, "only_new": only_new, "nothing": nothing,
            "before": load(ROOT / "fixtures" / "more_in_trials" / "clues_before_2.21.json")}


@pytest.fixture(scope="module")
def seen(answers, tmp_path_factory):
    """Opens the page once per answer and returns what a reader sees."""
    node = shutil.which("node")
    if not node or subprocess.run(
            [node, "-e", "require('playwright')"], capture_output=True).returncode:
        pytest.skip("needs node with playwright to open a real browser")
    answers_file = tmp_path_factory.mktemp("new_in_trials") / "answers.json"
    answers_file.write_text(json.dumps(answers), encoding="utf-8")
    run = subprocess.run(
        [node, "-e", BROWSER_SCRIPT, str(PAGE_FILE), str(answers_file)],
        capture_output=True, text=True, timeout=240, cwd=str(ROOT))
    assert run.returncode == 0, run.stderr[-3000:]
    out = json.loads(run.stdout)
    for name in answers:
        assert out[name]["errors"] == [], name
    return out


def test_browser_example_the_tab_says_in_trials_4(seen):
    assert seen["example"]["closed"]["tab"] == "In trials (4)"


def test_browser_example_the_2_21_box_holds_prednisone(seen):
    box = seen["example"]["tapped"]["oldBox"]
    assert box["shown"] and box["summary"].startswith(OLD_BOX_LABEL + " (1)")
    assert [(card["name"], card["phase"]) for card in box["cards"]] == [("Prednisone", "Phase 2")]


def test_browser_example_the_new_box_holds_the_three_in_order(seen):
    closed = seen["example"]["closed"]
    assert closed["newBox"]["shown"] and closed["newBoxIsAfterTheOldBox"]
    assert closed["newBox"]["summary"].startswith(LABEL + " (3)")  # ticket T14b: the summary keeps the full count
    assert closed["newBox"]["summary"].endswith("Tap to close")  # ticket T14b
    assert closed["newBox"]["open"] and closed["newBox"]["cardsOnScreen"] == 3  # ticket T14b
    tapped = seen["example"]["tapped"]["newBox"]
    assert tapped["open"] and tapped["cardsOnScreen"] == 3
    assert tapped["summary"].endswith("Tap to close")
    assert [(card["name"], card["phase"]) for card in tapped["cards"]] == [
        (name, phase) for _, name, phase in LGMD_NEW_3]


def test_browser_example_the_empty_sentence_is_not_shown(seen):
    closed = seen["example"]["closed"]
    assert closed["list"] == []
    assert not closed["noteShown"] and closed["noteWords"] == ""


def test_browser_one_new_box_card_in_full(seen):
    card = seen["example"]["tapped"]["newBox"]["cards"][1]
    assert card["name"] == "ATYR-1940" and card["forms"] == "Forms: ATYR-1940"
    assert card["phase"] == "Phase 1/2"
    assert card["source"] == "https://clinicaltrials.gov/study/NCT02579239" and card["sourceShown"]
    # Nothing else is written on the card.
    # Ticket 2.29: the sentence is once at the top of the box, not on the card.
    assert card["words"] == "ATYR-1940 Forms: ATYR-1940 Source record Phase 1/2 Report"  # 3.3: the Report link


def test_browser_a_new_box_card_has_no_score_and_no_explain_button(seen):
    for name in ("example", "pbc"):
        for card in seen[name]["tapped"]["newBox"]["cards"]:
            assert card["buttons"] == 0 and card["explanation"] == 0
            assert card["rank"] == 0 and card["proteins"] == 0 and card["path"] == 0
            assert "points" not in card["words"] and "report" not in card["words"]
            # Ticket 2.29: the sentence is once at the top of the box, not on the card.
            assert card["ending"] == [] and not card["endingIsLastBeforeTheFoot"]
        assert seen[name]["explainAskedFor"] == []


def test_browser_pbc_the_7_and_the_26_are_as_before_and_the_new_box_has_10(seen):
    tapped = seen["pbc"]["tapped"]
    assert [card["name"] for card in tapped["list"]] == PBC_LIST_7
    assert tapped["list"] == seen["before"]["tapped"]["list"]  # the same cards as before 2.21
    assert [(card["name"], card["phase"]) for card in tapped["oldBox"]["cards"]] == [
        (name, phase) for _, name, phase in PBC_BOX_26]
    assert [(card["name"], card["phase"]) for card in tapped["newBox"]["cards"]] == [
        (name, phase) for _, name, phase in PBC_NEW_10]
    closed = seen["pbc"]["closed"]
    assert closed["tab"] == "In trials (43)"  # 7 + 26 + 10
    assert closed["oldBox"]["open"] and closed["newBox"]["open"]  # ticket T14b
    assert closed["newBox"]["summary"].startswith(LABEL + " (10)")


def test_browser_only_the_new_box_drops_the_sentence_too(seen):
    closed = seen["only_new"]["closed"]
    assert closed["tab"] == "In trials (3)"
    assert not closed["oldBox"]["shown"] and closed["newBox"]["shown"]
    assert not closed["noteShown"]
    assert closed["newBox"]["open"]  # it is all there is on the tab


def test_browser_no_box_keys_means_no_boxes_and_the_sentence_as_before(seen):
    for name in ("nothing", "before"):
        closed = seen[name]["closed"]
        assert not closed["oldBox"]["shown"] and not closed["newBox"]["shown"]
        assert closed["newBox"]["cards"] == []
    nothing = seen["nothing"]["closed"]
    assert nothing["tab"] == "In trials (0)"
    assert nothing["noteShown"] and nothing["noteWords"] == EMPTY_SENTENCE
    assert seen["before"]["closed"]["tab"] == "In trials (7)"


def test_browser_the_line_above_the_list_on_the_page_and_the_print_page(seen):
    for name in ("example", "pbc", "nothing"):
        assert seen[name]["closed"]["line"] == TRIALS_LINE
        assert seen[name]["closed"]["heading"] == "Already being studied for this disease"
    # The print page's count is today's list only, as before (out of scope).
    assert seen["example"]["printTrials"] == "0 medicines. " + TRIALS_LINE
    assert seen["pbc"]["printTrials"] == "7 medicines. " + TRIALS_LINE
