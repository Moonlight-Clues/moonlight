"""Ticket 2.21. A box for more medicines in trials.

Kashish's decisions, 22 Nov:

1. Today's In trials list is unchanged: same cards, same order.
2. Under it, a folded box labelled, in her exact words, "More medicines in
   trials for this disease. They do not act on one of the 25 proteins."
3. A medicine is in the box when all of these are true: the disease's own
   list gives it a trial stage for this disease; it is approved for
   something else, by the same rule In trials uses (filter.group_of); it
   is not already on any tab or box of the page; no existing rule leaves
   it out (withdrawn, corrections, left out by hand).
4. One card per medicine, forms merged as elsewhere.
5. Furthest trial stage first, then A to Z.
6. A box card shows the medicine, its trial stage and its source link. No
   score and no explain button.
7. /api/clues gains one new key, "more_in_trials". Every old key keeps its
   meaning.
8. The box shows ALL its medicines, however many (breast cancer: 365).
9. The number on the In trials tab is the list plus the box.
10. When the list is empty and the box has cards, the sentence "No
    medicine in this data is being studied for this disease." is not
    shown, and the box starts open.
11. No new kind of request to Open Targets.

Kashish's decisions, 23 Nov:

12. Every card in the box ends with her sentence, exactly: "Never start,
    stop or change any medicine without a doctor." Only that sentence, not
    the part about the protein.
13. The line above the In trials list no longer says "Only medicines that
    act on one of the proteins most linked to this disease.", on the page
    and on the print page. The rest stays word for word.
14. The question to Open Targets stays exactly as it is on main. A medicine
    whose "approved for something else" the list cannot tell stays hidden.

Her example: primary biliary cholangitis (MONDO_0005388). 7 cards today,
26 in the box, Phase 3 first.

Saved files only: fixtures/more_in_trials/ (copied from the probe of 21
Nov) and, for breast cancer, fixtures/narrower_box/. No network.
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
from moonlight.engine import sort_into_tabs
from moonlight.fetch import Listed
from moonlight.filter import sort_paths
from moonlight.records import Disease, Medicine, MedicineForm, Path, Target

import test_narrower_box
from source_3_11 import back_to_before as trials_back_to_before  # ticket 3.11: In trials links

ROOT = pathlib.Path(__file__).resolve().parent.parent
SAVED = ROOT / "fixtures" / "more_in_trials"
PAGE_FILE = ROOT / "web" / "index.html"
PAGE = PAGE_FILE.read_text(encoding="utf-8")

PBC = Disease(id="MONDO_0005388", name="primary biliary cholangitis")
BREAST_CANCER = "MONDO_0007254"

# Kashish's words, exactly.
LABEL = ("More medicines in trials for this disease. They do not act on one of "
         "the 25 proteins.")
EMPTY_SENTENCE = "No medicine in this data is being studied for this disease."
# Kashish's words of 23 Nov, exactly. The last words on every box card.
CARD_ENDING = "Never start, stop or change any medicine without a doctor."
# The line above the In trials list, without its old last sentence.
TRIALS_LINE = ("Medicines being tested for this disease. A separate "
               "research category, not a prediction of effectiveness. Not every trial is listed.")
GONE_SENTENCE = "Only medicines that act on one of the proteins most linked to this disease."

# Today's In trials list for the example, in today's order.
PBC_LIST_7 = ["Elafibranor", "Saroglitazar", "Ustekinumab", "Fenofibrate", "Bezafibrate",
              "Pemafibrate", "Seladelpar"]
# The 26 of fixtures/probe_p6/trials_missing.csv (branch probe-key-diseases),
# rule "not on a top-25 protein", in the box's order: furthest stage first,
# then A to Z. (id, name as the card writes it, stage as the card writes it)
PBC_BOX_26 = [
    ("CHEMBL1487", "Atorvastatin", "Phase 3"),
    ("CHEMBL1370", "Budesonide", "Phase 3"),
    ("CHEMBL107", "Colchicine", "Phase 3"),
    ("CHEMBL34259", "Methotrexate", "Phase 3"),
    ("CHEMBL6068331", "Colesevelam", "Phase 2/3"),
    ("CHEMBL141", "Lamivudine", "Phase 2/3"),
    ("CHEMBL635", "Prednisone", "Phase 2/3"),
    ("CHEMBL129", "Zidovudine", "Phase 2/3"),
    ("CHEMBL2105759", "Baricitinib", "Phase 2"),
    ("CHEMBL4297912", "Bifidobacterium SPP.", "Phase 2"),
    ("CHEMBL3989915", "Difelikefalin", "Phase 2"),
    ("CHEMBL885", "Emtricitabine", "Phase 2"),
    ("CHEMBL161381", "EMTRICITABINE, (+/-)-", "Phase 2"),
    ("CHEMBL3358920", "Etrasimod", "Phase 2"),
    ("CHEMBL363392", "Maralixibat", "Phase 2"),
    ("CHEMBL1165", "Moexipril", "Phase 2"),
    ("CHEMBL982", "Nalmefene", "Phase 2"),
    ("CHEMBL6068083", "Netakimab", "Phase 2"),
    ("CHEMBL4297588", "Odevixibat", "Phase 2"),
    ("CHEMBL628", "Pentoxifylline", "Phase 2"),
    ("CHEMBL254316", "Raltegravir", "Phase 2"),
    ("CHEMBL1201576", "Rituximab", "Phase 2"),
    ("CHEMBL1538", "Tenofovir Disoproxil", "Phase 2"),
    ("CHEMBL1201587", "Alemtuzumab", "Phase 1"),
    ("CHEMBL88", "Cyclophosphamide Anhydrous", "Phase 1"),
    ("CHEMBL1568", "Fludarabine", "Phase 1"),
]
# In a trial for the disease, approved for nothing: her rule stands, hidden.
PBC_NOT_APPROVED_ANYWHERE = [
    "CHEMBL2109379", "CHEMBL5314422", "CHEMBL3775741", "CHEMBL4298055", "CHEMBL2387408",
    "CHEMBL4303187", "CHEMBL4297942", "CHEMBL3545019",
]


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def saved_post_json(body):
    """Stands in for fetch._post_json with the files in fixtures/more_in_trials/."""
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


def without_hand_approvals_for_the_example():
    """Ticket 2.34 (24 Nov) put elafibranor and seladelpar under Approved for
    this disease, by hand, from their labels. The example in this file is the
    page as it was saved on 21 Nov: 7 cards in the list. So it is read without
    the hand-written approvals for this one disease. Every other disease gets
    the real file. tests/test_approvals_fourth_batch.py holds the page as it
    is with them: 5 cards in the list, and those two under Approved."""
    kept = [entry for entry in engine._read_approvals() if entry["disease_id"] != PBC.id]
    return patch.object(engine, "_read_approvals", return_value=kept)


@pytest.fixture
def offline():
    with patch("moonlight.fetch._post_json", side_effect=saved_post_json) as mock, \
            without_hand_approvals_for_the_example():
        yield mock


@pytest.fixture
def client():
    api.forget_visitors()
    return TestClient(api.app)


@pytest.fixture
def pbc(offline, client):
    """What /api/clues answers for the example, from saved answers."""
    answer = client.get("/api/clues", params={"disease_id": PBC.id})
    assert answer.status_code == 200
    return answer.json()


# ---- fetch: the disease's own list, as records ----

def test_the_own_list_is_read_as_one_record_per_medicine_family(offline):
    on_list = fetch.fetch_listed_medicines(PBC)
    assert len(on_list) == 50  # 51 rows, one family has two forms on the list
    by_id = {entry.medicine.forms[0].parent_id or entry.medicine.forms[0].id: entry
             for entry in on_list}
    assert len(by_id) == 50

    colchicine = by_id["CHEMBL107"]
    assert colchicine.medicine == Medicine(name="COLCHICINE", forms=(MedicineForm(
        id="CHEMBL107", name="COLCHICINE", best_stage="APPROVAL", disease_stage="PHASE_3",
        parent_id=None, withdrawn=False),))
    # Each report link with the report's own stage.
    assert colchicine.reports == (("https://clinicaltrials.gov/study/NCT00004748", "PHASE_3"),)


def test_a_medicine_and_its_tablet_form_on_the_list_are_one_record(offline):
    by_name = {entry.medicine.name: entry for entry in fetch.fetch_listed_medicines(PBC)}
    tenofovir = by_name["TENOFOVIR DISOPROXIL"].medicine
    # The parent first. The family takes the strongest stage of its forms.
    assert [form.name for form in tenofovir.forms] == [
        "TENOFOVIR DISOPROXIL", "TENOFOVIR DISOPROXIL FUMARATE"]
    assert tenofovir.forms[1].parent_id == "CHEMBL1538"
    assert [form.disease_stage for form in tenofovir.forms] == ["PHASE_2", "UNKNOWN"]
    assert tenofovir.disease_stage == "PHASE_2"
    assert tenofovir.best_stage == "APPROVAL"
    # A form whose parent has no row of its own: named after the parent.
    colesevelam = by_name["COLESEVELAM"].medicine
    assert [(form.id, form.name, form.parent_id) for form in colesevelam.forms] == [
        ("CHEMBL1201473", "COLESEVELAM HYDROCHLORIDE", "CHEMBL6068331")]


def test_reading_the_list_as_records_is_the_question_moonlight_already_asks(offline):
    fetch.fetch_listed_medicines(PBC)
    asked = [call.args[0] for call in offline.call_args_list]
    assert asked == [{"query": fetch.DISEASE_DRUGS_QUERY, "variables": {"diseaseId": PBC.id}}]


def test_a_disease_open_targets_does_not_know_has_no_records():
    answer = {"data": {"disease": None}}
    with patch("moonlight.fetch._post_json", return_value=answer):
        assert fetch.fetch_listed_medicines(Disease(id="MONDO_NOPE", name="nope")) == []


# ---- engine: who is in the box (made-up records, one rule at a time) ----

OURS = Disease(id="MONDO_TEST", name="test disease")
PROTEIN = Target(id="ENSG_TEST", symbol="TEST1", name="test protein", score=0.5)


def on_list(family_id, name, stage, best="APPROVAL", withdrawn=False, reports=None, forms=None):
    """One made-up family on the disease's own list."""
    forms = forms or (MedicineForm(id=family_id, name=name, best_stage=best,
                                   disease_stage=stage, withdrawn=withdrawn),)
    if reports is None:
        reports = ((f"https://example.org/{family_id}", stage),)
    return fetch.OnList(medicine=Medicine(name=name, forms=forms), reports=tuple(reports))


def path_for(family_id, name, best="APPROVAL", stage=None, withdrawn=False):
    """A made-up path: the medicine acts on one of the proteins looked at."""
    form = MedicineForm(id=family_id, name=name, best_stage=best, disease_stage=stage,
                        withdrawn=withdrawn)
    return Path(medicine=Medicine(name=name, forms=(form,)), target=PROTEIN, disease=OURS,
                action_types=("INHIBITOR",), score=0.5, sources=("https://example.org/p",))


def box_of(entries, paths=(), listed=(), withdrawn_listed=(), neighbours=()):
    tabs = sort_into_tabs(sort_paths(list(paths)), list(listed), list(withdrawn_listed),
                          list(neighbours), on_list=entries)
    return tabs.more_in_trials


def test_the_label_is_kashishs_words_exactly():
    assert engine.MORE_IN_TRIALS_LABEL == LABEL


def test_in_a_trial_and_approved_for_something_else_is_in_the_box():
    box = box_of([on_list("CHEMBL_A", "ALPHA", "PHASE_2")])
    assert box == [engine.TrialMedicine(
        id="CHEMBL_A", name="ALPHA", forms=("ALPHA",), stage="PHASE_2",
        sources=("https://example.org/CHEMBL_A",))]


def test_with_no_list_handed_in_there_is_no_box():
    tabs = sort_into_tabs(sort_paths([path_for("CHEMBL_P", "PAPA", stage="PHASE_2")]), [])
    assert tabs.more_in_trials == []


@pytest.mark.parametrize("best", ["PHASE_3", "PHASE_4", "UNKNOWN", "WITHDRAWAL", "SOMETHING_NEW"])
def test_not_approved_for_anything_stays_hidden(best):
    assert box_of([on_list("CHEMBL_A", "ALPHA", "PHASE_3", best=best)]) == []


@pytest.mark.parametrize("stage", ["PHASE_4", "PHASE_3", "PHASE_2_3", "PHASE_2", "PHASE_1_2",
                                   "PHASE_1", "EARLY_PHASE_1"])
def test_every_trial_stage_counts(stage):
    assert [m.stage for m in box_of([on_list("CHEMBL_A", "ALPHA", stage)])] == [stage]


@pytest.mark.parametrize("stage", ["APPROVAL", "UNKNOWN", "WITHDRAWAL", "IND", "PRECLINICAL",
                                   "SOMETHING_NEW", None])
def test_a_stage_that_is_not_a_trial_in_people_is_not_in_the_box(stage):
    assert box_of([on_list("CHEMBL_A", "ALPHA", stage)]) == []


def test_withdrawn_on_the_own_list_is_left_out():
    assert box_of([on_list("CHEMBL_A", "ALPHA", "PHASE_2", withdrawn=True)]) == []


def test_one_withdrawn_form_is_enough_for_the_whole_family():
    forms = (
        MedicineForm(id="CHEMBL_A", name="ALPHA", best_stage="APPROVAL", disease_stage="PHASE_2",
                     withdrawn=False),
        MedicineForm(id="CHEMBL_A2", name="ALPHA SODIUM", best_stage="APPROVAL",
                     disease_stage=None, parent_id="CHEMBL_A", withdrawn=True),
    )
    assert box_of([on_list("CHEMBL_A", "ALPHA", "PHASE_2", forms=forms)]) == []


def test_withdrawal_not_said_is_not_guessed():
    box = box_of([on_list("CHEMBL_A", "ALPHA", "PHASE_2", withdrawn=None)])
    assert [medicine.name for medicine in box] == ["ALPHA"]


def test_withdrawn_on_a_parents_or_childs_list_is_left_out():
    wider = Disease(id="MONDO_WIDE", name="wide group")
    marked = Listed(id="CHEMBL_A", name="ALPHA", forms=(("CHEMBL_A", "ALPHA"),), sources=(),
                    approved=False)
    neighbour = engine.Neighbour(engine.PARENT, wider, approved=(), withdrawn=(marked,))
    assert box_of([on_list("CHEMBL_A", "ALPHA", "PHASE_2")], neighbours=[neighbour]) == []


def test_withdrawn_on_the_withdrawn_list_handed_in_is_left_out():
    marked = Listed(id="CHEMBL_A", name="ALPHA", forms=(("CHEMBL_A", "ALPHA"),), sources=(),
                    approved=False)
    assert box_of([on_list("CHEMBL_A", "ALPHA", "PHASE_2")], withdrawn_listed=[marked]) == []


@pytest.mark.parametrize("best, stage", [
    ("APPROVAL", "PHASE_2"),  # today's In trials card
    ("APPROVAL", None),  # a new clue
    ("APPROVAL", "APPROVAL"),  # approved for the disease
    ("APPROVAL", "UNKNOWN"),  # unclear link, counted only
    ("PHASE_2", "PHASE_2"),  # not approved anywhere, counted only
])
def test_a_medicine_that_acts_on_one_of_the_proteins_is_never_in_the_box(best, stage):
    """The label says "They do not act on one of the 25 proteins"."""
    paths = [path_for("CHEMBL_A", "ALPHA", best=best, stage=stage)]
    assert box_of([on_list("CHEMBL_A", "ALPHA", "PHASE_2")], paths=paths) == []


def test_todays_list_is_the_same_with_or_without_the_box():
    paths = [path_for("CHEMBL_P", "PAPA", stage="PHASE_2"), path_for("CHEMBL_N", "NOVEMBER")]
    entries = [on_list("CHEMBL_P", "PAPA", "PHASE_2"), on_list("CHEMBL_A", "ALPHA", "PHASE_3")]
    before = sort_into_tabs(sort_paths(paths), [])
    after = sort_into_tabs(sort_paths(paths), [], on_list=entries)
    assert after.being_studied == before.being_studied
    assert after.new_clues == before.new_clues
    assert after.approved == before.approved
    assert after.left_out == before.left_out
    assert [medicine.name for medicine in after.more_in_trials] == ["ALPHA"]


def test_a_medicine_on_the_approved_tab_is_not_in_the_box():
    approved_here = Listed(id="CHEMBL_A", name="ALPHA", forms=(("CHEMBL_A", "ALPHA"),),
                           sources=())
    assert box_of([on_list("CHEMBL_A", "ALPHA", "PHASE_3")], listed=[approved_here]) == []


@pytest.mark.parametrize("role", [engine.PARENT, engine.CHILD])
def test_a_medicine_in_an_approved_box_is_not_in_this_box(role):
    near = Disease(id="MONDO_NEAR", name="near disease")
    entry = Listed(id="CHEMBL_A", name="ALPHA", forms=(("CHEMBL_A", "ALPHA"),), sources=())
    neighbour = engine.Neighbour(role, near, approved=(entry,), withdrawn=())
    tabs = sort_into_tabs(sort_paths([]), [], [], [neighbour],
                          on_list=[on_list("CHEMBL_A", "ALPHA", "PHASE_3")])
    assert len(tabs.narrower) + len(tabs.wider_group) == 1  # already on the page
    assert tabs.more_in_trials == []


def test_furthest_stage_first_then_a_to_z():
    entries = [
        on_list("CHEMBL_1", "zulu", "PHASE_2"),
        on_list("CHEMBL_2", "BRAVO", "PHASE_1"),
        on_list("CHEMBL_3", "Yankee", "PHASE_3"),
        on_list("CHEMBL_4", "alpha", "PHASE_2"),
        on_list("CHEMBL_5", "DELTA", "PHASE_2_3"),
        on_list("CHEMBL_6", "CHARLIE", "PHASE_3"),
        on_list("CHEMBL_7", "ECHO", "EARLY_PHASE_1"),
        on_list("CHEMBL_8", "FOXTROT", "PHASE_4"),
        on_list("CHEMBL_9", "GOLF", "PHASE_1_2"),
    ]
    assert [(m.name, m.stage) for m in box_of(entries)] == [
        ("FOXTROT", "PHASE_4"), ("CHARLIE", "PHASE_3"), ("Yankee", "PHASE_3"),
        ("DELTA", "PHASE_2_3"), ("alpha", "PHASE_2"), ("zulu", "PHASE_2"),
        ("GOLF", "PHASE_1_2"), ("BRAVO", "PHASE_1"), ("ECHO", "EARLY_PHASE_1"),
    ]
    # The order handed in does not matter.
    assert box_of(list(reversed(entries))) == box_of(entries)


def test_forms_are_merged_into_one_card_with_the_strongest_stage():
    forms = (
        MedicineForm(id="CHEMBL_A", name="ALPHA", best_stage="PHASE_3", disease_stage="PHASE_1",
                     withdrawn=False),
        MedicineForm(id="CHEMBL_A2", name="ALPHA SODIUM", best_stage="APPROVAL",
                     disease_stage="PHASE_3", parent_id="CHEMBL_A", withdrawn=False),
    )
    reports = (("https://example.org/one", "PHASE_1"), ("https://example.org/three", "PHASE_3"))
    box = box_of([on_list("CHEMBL_A", "ALPHA", None, forms=forms, reports=reports)])
    assert box == [engine.TrialMedicine(
        id="CHEMBL_A", name="ALPHA", forms=("ALPHA", "ALPHA SODIUM"), stage="PHASE_3",
        # The receipt for the stage on the card first, then the others.
        sources=("https://example.org/three", "https://example.org/one"))]


def test_the_source_link_is_the_report_for_the_stage_shown():
    reports = (("https://example.org/early", "PHASE_1"), ("http://example.org/plain", "PHASE_3"),
               ("https://example.org/far", "PHASE_3"), ("https://example.org/far2", "PHASE_3"))
    box = box_of([on_list("CHEMBL_A", "ALPHA", "PHASE_3", reports=reports)])
    assert box[0].source_record == "https://example.org/far"  # only an https link


def test_no_report_for_that_stage_gives_the_first_link_and_no_link_gives_none():
    reports = (("https://example.org/early", "PHASE_1"), ("https://example.org/none", None))
    box = box_of([on_list("CHEMBL_A", "ALPHA", "PHASE_3", reports=reports)])
    assert box[0].source_record == "https://example.org/early"
    assert box_of([on_list("CHEMBL_B", "BRAVO", "PHASE_3", reports=())])[0].source_record is None


def test_keep_out_takes_listed_medicines_out_and_keeps_the_order():
    box = box_of([on_list("CHEMBL_1", "ALPHA", "PHASE_3"), on_list("CHEMBL_2", "BRAVO", "PHASE_3"),
                  on_list("CHEMBL_3", "CHARLIE", "PHASE_2")])
    kept = engine.keep_out(box, {"CHEMBL_2", "CHEMBL_OTHER"})
    assert [medicine.name for medicine in kept] == ["ALPHA", "CHARLIE"]
    assert engine.keep_out(box, set()) == box


# ---- engine: the example, from saved answers ----

@pytest.fixture
def pbc_found(offline):
    return api._find(PBC.id)


def test_the_example_box_holds_the_26_of_the_probe_in_order(pbc_found):
    box = pbc_found.more_in_trials
    assert [medicine.id for medicine in box] == [row[0] for row in PBC_BOX_26]
    assert len(box) == 26


def test_the_example_keeps_its_7_cards_in_order(pbc_found):
    names = [api.explain._display(clue.medicine.name) for clue in pbc_found.being_studied]
    assert names == PBC_LIST_7


def test_the_example_hides_what_is_approved_for_nothing(pbc_found):
    in_box = {medicine.id for medicine in pbc_found.more_in_trials}
    assert not in_box & set(PBC_NOT_APPROVED_ANYWHERE)


def test_nobody_in_the_example_box_is_anywhere_else_on_the_page(pbc_found):
    in_box = {medicine.id for medicine in pbc_found.more_in_trials}
    elsewhere = {m.id for m in pbc_found.approved + pbc_found.narrower + pbc_found.wider_group}
    elsewhere |= {api._clue_id(clue) for clue in pbc_found.being_studied + pbc_found.new_clues}
    assert not in_box & elsewhere


# ---- /api/clues ----

def with_ursodiol_confirmed(before):
    """Ticket 2.42. Ursodiol for primary biliary cholangitis is on the
    hand-written list of confirmed approvals: its card shows the label as
    source and has no grey line. Nothing else on its card changes, and it
    stays on the main list. tests/test_no_regulator_box.py holds it."""
    before = copy.deepcopy(before)
    labels = engine.confirmed_by_label()
    for card in before["approved"]:
        if (card["id"], PBC.id) in labels:
            card["source"] = labels[(card["id"], PBC.id)]
            card.pop("proof_note", None)
    return before


def test_every_old_key_answers_what_it_answered_before(pbc):
    before = load(SAVED / "clues_before_2.21.json")  # made on main, commit 7734f6f
    before = with_ursodiol_confirmed(before)  # ticket 2.42
    assert {key: trials_back_to_before(pbc)[key] for key in before} == before
    # This ticket's key, ticket 2.24's, and ticket 2.42's (taurursodiol is in the new box).
    assert set(pbc) - set(before) == {"more_in_trials", "new_in_trials", "no_regulator_box"}
    assert [card["medicine"] for card in pbc["being_studied"]] == PBC_LIST_7


def test_the_new_key_holds_the_box_in_order(pbc):
    box = pbc["more_in_trials"]
    assert [(card["id"], card["medicine"], card["trial_phase"]) for card in box] == PBC_BOX_26
    assert [card["medicine"] for card in box[:5]] == [
        "Atorvastatin", "Budesonide", "Colchicine", "Methotrexate", "Colesevelam"]


def test_one_box_card_in_full(pbc):
    colchicine = next(card for card in pbc["more_in_trials"] if card["id"] == "CHEMBL107")
    assert colchicine == {
        "id": "CHEMBL107",
        "medicine": "Colchicine",
        "forms": ["Colchicine"],
        "trial_phase": "Phase 3",
        "source": "https://clinicaltrials.gov/study/NCT00004748",
        "ending": "Never start, stop or change any medicine without a doctor.",
    }


def test_the_card_ending_is_kashishs_sentence_exactly():
    assert engine.MORE_IN_TRIALS_ENDING == CARD_ENDING


def test_every_box_card_ends_with_that_sentence_and_only_that_sentence(pbc):
    assert len(pbc["more_in_trials"]) == 26
    for card in pbc["more_in_trials"]:
        assert card["ending"] == CARD_ENDING
        assert "protein" not in card["ending"] and "catch" not in card["ending"]
    # Today's cards keep their own, longer ending.
    for card in pbc["being_studied"]:
        assert card["ending"] != CARD_ENDING and card["ending"].endswith(CARD_ENDING)


def test_a_box_card_has_no_score_and_no_proteins(pbc):
    for card in pbc["more_in_trials"]:
        assert set(card) == {"id", "medicine", "forms", "trial_phase", "source", "ending"}
        assert card["source"].startswith("https://")


def test_forms_are_shown_inside_the_one_card(pbc):
    by_id = {card["id"]: card for card in pbc["more_in_trials"]}
    assert by_id["CHEMBL1538"]["forms"] == ["Tenofovir Disoproxil", "Tenofovir Disoproxil Fumarate"]
    assert by_id["CHEMBL6068331"]["medicine"] == "Colesevelam"
    assert by_id["CHEMBL6068331"]["forms"] == ["Colesevelam Hydrochloride"]


def test_the_box_needs_no_more_requests_than_before(offline, client):
    assert client.get("/api/clues", params={"disease_id": PBC.id}).status_code == 200
    asked = [call.args[0] for call in offline.call_args_list]
    questions = {(body["query"], json.dumps(body["variables"], sort_keys=True)) for body in asked}
    # The disease, its 25 proteins, the family, 25 protein lists, and the
    # own list with the two parents' lists. Nothing new.
    assert len(questions) == 1 + 1 + 1 + 25 + 3
    known = {fetch.DISEASE_QUERY, fetch.TARGETS_QUERY, fetch.FAMILY_QUERY,
             fetch.TARGET_DRUGS_QUERY, fetch.DISEASE_DRUGS_QUERY}
    assert {body["query"] for body in asked} <= known


def test_no_key_when_the_box_is_empty(offline, client):
    with patch("moonlight.api.fetch_listed_medicines", return_value=[]):
        answer = client.get("/api/clues", params={"disease_id": PBC.id}).json()
    assert "more_in_trials" not in answer
    assert [card["medicine"] for card in answer["being_studied"]] == PBC_LIST_7


def test_a_medicine_left_out_by_hand_for_this_disease_is_not_in_the_box(offline, client):
    by_hand = [{"medicine_id": "CHEMBL107", "disease_id": PBC.id, "date": "2026-11-22"},
               {"medicine_id": "CHEMBL1370", "disease_id": "MONDO_OTHER", "date": "2026-11-22"}]
    with patch("moonlight.engine._read_left_out", return_value=by_hand):
        answer = client.get("/api/clues", params={"disease_id": PBC.id}).json()
    ids = [card["id"] for card in answer["more_in_trials"]]
    assert "CHEMBL107" not in ids and "CHEMBL1370" in ids  # only for this disease
    assert len(ids) == 25
    assert "wrong_way_line" not in answer  # that line counts New clues only


def test_a_medicine_on_the_corrections_list_for_this_disease_is_not_in_the_box(offline, client):
    listed = [{"medicine_id": "CHEMBL107", "disease_id": PBC.id, "date": "2026-11-22",
               "note": engine.CORRECTION_NOTE}]
    with patch("moonlight.engine._read_corrections", return_value=listed):
        answer = client.get("/api/clues", params={"disease_id": PBC.id}).json()
    ids = [card["id"] for card in answer["more_in_trials"]]
    assert "CHEMBL107" not in ids and len(ids) == 25


def test_a_box_card_cannot_be_explained(offline, client):
    with patch("moonlight.explain.explain") as explained, \
            patch("moonlight.api.data_version", return_value="26.09"):
        answer = client.get("/api/explain", params={"disease_id": PBC.id, "clue_id": "CHEMBL107"})
    assert answer.status_code == 404
    explained.assert_not_called()


def test_the_question_to_open_targets_is_not_given_the_extra_field():
    """Kashish, 23 Nov: the question stays exactly as it is on main."""
    question = fetch.DISEASE_DRUGS_QUERY
    assert "parentMolecule { id name drugWarnings { warningType } }" in question
    assert "childMolecules { id name drugWarnings { warningType } }" in question
    assert question.count("maximumClinicalStage") == 1  # the listed form's own, as before


def test_a_form_the_list_does_not_name_cannot_make_a_medicine_approved():
    """The eight stay hidden. The listed form is in a trial and not approved
    anywhere; the answer names a parent, but says nothing of its stage."""
    answer = {"data": {"disease": {"id": OURS.id, "drugAndClinicalCandidates": {"count": 1, "rows": [{
        "maxClinicalStage": "PHASE_2",
        "drug": {"id": "CHEMBL_SALT", "name": "ALPHA MALEATE", "maximumClinicalStage": "PHASE_2_3",
                 "drugWarnings": [],
                 "parentMolecule": {"id": "CHEMBL_A", "name": "ALPHA", "drugWarnings": [],
                                    "maximumClinicalStage": "APPROVAL"},  # even if it were sent
                 "childMolecules": []},
        "clinicalReports": [{"url": "https://example.org/t", "clinicalStage": "PHASE_2",
                             "source": "ClinicalTrials.gov"}],
    }]}}}}
    with patch("moonlight.fetch._post_json", return_value=answer):
        entries = fetch.fetch_listed_medicines(OURS)
    assert [entry.medicine.best_stage for entry in entries] == ["PHASE_2_3"]
    assert box_of(entries) == []


def test_the_explainer_is_handed_the_same_names_as_before(offline):
    """The grounding check is not changed by this ticket."""
    found = api._find(PBC.id)
    with patch("moonlight.api.fetch_listed_medicines", return_value=[]):
        without = api._find(PBC.id)
    assert found.known_names == without.known_names
    assert "COLCHICINE" not in found.known_names


def test_breast_cancer_shows_all_365(client):
    """Kashish, 22 Nov: the box shows ALL its medicines. No cap of 300."""
    with patch("moonlight.fetch._post_json", side_effect=test_narrower_box.saved_post_json):
        answer = client.get("/api/clues", params={"disease_id": BREAST_CANCER}).json()
    assert len(answer["being_studied"]) == 29
    box = answer["more_in_trials"]
    assert len(box) == 365
    assert len({card["id"] for card in box}) == 365
    ladder = ["Phase 4", "Phase 3", "Phase 2/3", "Phase 2", "Phase 1/2", "Phase 1", "Early Phase 1"]
    order = [(ladder.index(card["trial_phase"]), card["medicine"].casefold()) for card in box]
    assert order == sorted(order)


# ---- the page, read as text ----

def test_the_page_holds_the_box_under_the_list_with_the_exact_label():
    panel = PAGE[PAGE.index('id="panel-trials"'):PAGE.index('id="panel-clues"')]
    assert panel.index('id="studied-cards"') < panel.index('id="more-trials-box"')
    assert PAGE.count(LABEL) == 1 and LABEL in panel
    assert (f"<summary>{LABEL} (<span id=\"more-trials-count\"></span>) "
            "<span data-part=\"tap\">Tap to open</span></summary>") in panel
    assert '<details class="wider-box" id="more-trials-box" hidden>' in panel  # folded, like the others
    assert 'id="more-trials-cards"' in panel


def test_the_line_above_the_list_ends_at_not_every_trial_is_listed():
    assert PAGE.count(f'<p class="section-desc">{TRIALS_LINE}</p>') == 1
    assert GONE_SENTENCE not in PAGE
    assert "Only medicines that act on" not in PAGE


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
  const box = document.getElementById("more-trials-box");
  const note = document.getElementById("studied-note");
  const readCard = card => ({
    name: card.querySelector('[data-slot="medicine-name"]').textContent,
    forms: card.querySelector('[data-slot="forms"]').textContent,
    phase: (card.querySelector('[data-slot="phase"]') || {}).textContent || null,
    phaseShown: shownOnPage(card.querySelector('[data-slot="phase"]')),
    source: (card.querySelector('[data-slot="source"]') || {}).href || null,
    sourceShown: shownOnPage(card.querySelector('[data-slot="source"]')),
    noSourceShown: shownOnPage(card.querySelector('[data-part="no-source"]')),
    buttons: card.querySelectorAll("button:not(.report-link)").length,  // 3.3: the Report link is not an explain button
    explanation: card.querySelectorAll('[data-slot="explanation"]').length,
    ending: [...card.querySelectorAll('[data-slot="ending"]')].map(el => el.textContent),
    endingShown: shownOnPage(card.querySelector('[data-slot="ending"]')),
    endingIsLastBeforeTheFoot: !!card.querySelector('[data-slot="ending"] + .card-foot'),
    rank: card.querySelectorAll('[data-slot="rank"]').length,
    proteins: card.querySelectorAll('[data-slot="protein"]').length,
    path: card.querySelectorAll('[data-slot="path"]').length,
    words: card.innerText.replace(/\s+/g, " ").trim(),
  });
  return {
    tab: document.getElementById("tab-trials").innerText.replace(/\s+/g, " ").trim(),
    heading: document.querySelector("#panel-trials h2").innerText.trim(),
    line: document.querySelector("#panel-trials .section-desc").innerText.trim(),
    noteShown: shownOnPage(note) && note.textContent.trim() !== "",
    noteWords: note.textContent.trim(),
    list: [...document.querySelectorAll("#studied-cards > .card")].map(readCard),
    boxShown: shownOnPage(box),
    boxOpen: box.open,
    summary: box.querySelector("summary").innerText.replace(/\s+/g, " ").trim(),
    boxIsAfterTheList: !!(document.getElementById("studied-cards").compareDocumentPosition(box)
      & Node.DOCUMENT_POSITION_FOLLOWING),
    box: [...document.querySelectorAll("#more-trials-cards > .card")].map(readCard),
    boxCardsOnScreen: [...document.querySelectorAll("#more-trials-cards > .card")]
      .filter(card => card.checkVisibility()).length,  // false inside a folded box
    showAll: (document.getElementById("more-trials-show-all") || {}).textContent || null,  // ticket 2.T14
  };
}

async function oneSearch(browser, answer) {
  const context = await browser.newContext({ viewport: { width: 390, height: 844 } });
  const page = await context.newPage();
  const errors = [], outside = [], explainCalls = [];
  page.on("pageerror", problem => errors.push(String(problem)));
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
    outside.push(url);
    return route.abort();
  });
  await page.goto(SITE + "/?disease=MONDO_TEST");
  await page.waitForSelector("#found", { state: "visible" });
  await page.click("#tab-trials");
  const out = { errors };
  out.closed = await page.evaluate(readTrials);
  // ticket 2.T14: this box starts open. Open it only when it started closed,
  // then show the cards past 20 before the reads that expect every card on screen.
  if (out.closed.boxShown && !out.closed.boxOpen) {  // ticket 2.T14
    await page.click("#more-trials-box summary");
    await page.waitForTimeout(300);  // the box tells the page it was opened a moment later
  }
  const showAll = page.locator("#more-trials-show-all");  // ticket 2.T14
  if (out.closed.boxShown && await showAll.count() && await showAll.isVisible()) await showAll.click();  // ticket 2.T14
  if (out.closed.boxShown) {
    out.tapped = await page.evaluate(readTrials);
    if (out.tapped.boxOpen) {  // ticket 2.T14: the summary still folds the box
      await page.click("#more-trials-box summary");
      await page.waitForTimeout(300);
      out.folded = await page.evaluate(readTrials);  // ticket 2.T14
    }
  }
  out.explainAskedFor = explainCalls.map(url => new URL(url).searchParams.get("clue_id"));
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
    """Three answers of /api/clues: the example, the example with an empty
    list above the box, and the example as it was before this ticket."""
    api.forget_visitors()
    with patch("moonlight.fetch._post_json", side_effect=saved_post_json), \
            without_hand_approvals_for_the_example():  # ticket 2.34
        example = TestClient(api.app).get("/api/clues", params={"disease_id": PBC.id}).json()
    example = trials_back_to_before(example)  # ticket 3.11
    empty_list = copy.deepcopy(example)
    empty_list["being_studied"] = []
    no_list_no_box = copy.deepcopy(empty_list)
    del no_list_no_box["more_in_trials"]
    del no_list_no_box["new_in_trials"]
    return {"example": example, "empty_list": empty_list,
            "before": load(SAVED / "clues_before_2.21.json"), "nothing": no_list_no_box}


@pytest.fixture(scope="module")
def seen(answers, tmp_path_factory):
    """Opens the page once per answer and returns what a reader sees."""
    node = shutil.which("node")
    if not node or subprocess.run(
            [node, "-e", "require('playwright')"], capture_output=True).returncode:
        pytest.skip("needs node with playwright to open a real browser")
    answers_file = tmp_path_factory.mktemp("more_in_trials") / "answers.json"
    answers_file.write_text(json.dumps(answers), encoding="utf-8")
    run = subprocess.run(
        [node, "-e", BROWSER_SCRIPT, str(PAGE_FILE), str(answers_file)],
        capture_output=True, text=True, timeout=240, cwd=str(ROOT))
    assert run.returncode == 0, run.stderr[-3000:]
    out = json.loads(run.stdout)
    for name in answers:
        assert out[name]["errors"] == [], name
    return out


def test_browser_the_7_cards_are_the_same_as_before_the_ticket(seen):
    assert seen["example"]["closed"]["list"] == seen["before"]["closed"]["list"]
    assert [card["name"] for card in seen["example"]["closed"]["list"]] == PBC_LIST_7
    assert seen["example"]["closed"]["heading"] == "Already being studied for this disease"


def test_browser_the_box_is_folded_under_the_list_with_its_label_and_count(seen):
    closed = seen["example"]["closed"]
    assert closed["boxShown"] and closed["boxOpen"] and closed["boxIsAfterTheList"]  # ticket 2.T14
    assert closed["summary"] == LABEL + " (26) Tap to close"  # ticket 2.T14
    assert closed["boxCardsOnScreen"] == 20  # ticket 2.T14
    assert closed["showAll"] == "Show all 26"  # ticket 2.T14
    tapped = seen["example"]["tapped"]
    assert tapped["boxOpen"] and tapped["boxCardsOnScreen"] == 26
    assert tapped["showAll"] is None  # ticket 2.T14
    assert tapped["summary"].endswith("Tap to close")
    folded = seen["example"]["folded"]  # ticket 2.T14
    assert not folded["boxOpen"] and folded["boxCardsOnScreen"] == 0  # ticket 2.T14


def test_browser_the_tab_counts_the_list_and_the_box(seen):
    assert seen["example"]["closed"]["tab"] == "In trials (43)"  # 7 + 26 + 10
    assert seen["before"]["closed"]["tab"] == "In trials (7)"
    assert seen["empty_list"]["closed"]["tab"] == "In trials (36)"
    assert seen["nothing"]["closed"]["tab"] == "In trials (0)"


def test_browser_the_box_cards_are_in_the_answers_order(seen):
    cards = seen["example"]["tapped"]["box"]
    assert [(card["name"], card["phase"]) for card in cards] == [
        (name, phase) for _, name, phase in PBC_BOX_26]


def test_browser_a_box_card_shows_the_medicine_its_stage_and_its_source(seen):
    colchicine = seen["example"]["tapped"]["box"][2]
    assert colchicine["name"] == "Colchicine"
    assert colchicine["forms"] == "Forms: Colchicine"
    assert colchicine["phase"] == "Phase 3" and colchicine["phaseShown"]
    assert colchicine["source"] == "https://clinicaltrials.gov/study/NCT00004748"
    assert colchicine["sourceShown"] and not colchicine["noSourceShown"]
    # Nothing else is written on the card.
    # Ticket 2.29: the sentence is once at the top of the box, not on the card.
    assert colchicine["words"] == "Colchicine Forms: Colchicine Source record Phase 3 Report"  # 3.3: the Report link


def test_browser_a_box_card_has_no_score_and_no_explain_button(seen):
    for card in seen["example"]["tapped"]["box"]:
        assert card["buttons"] == 0 and card["explanation"] == 0
        assert card["rank"] == 0 and card["proteins"] == 0 and card["path"] == 0
        assert "points" not in card["words"] and "report" not in card["words"]
    assert seen["example"]["explainAskedFor"] == []  # In trials cards are explained on a tap only


def test_browser_no_box_card_carries_kashishs_sentence_since_ticket_2_29(seen):
    """Ticket 2.29, approved 23 Nov: the sentence is shown once at the top of
    the box (tests/test_caution_once.py) and is off the cards inside."""
    cards = seen["example"]["tapped"]["box"]
    assert len(cards) == 26
    for card in cards:
        assert card["ending"] == [] and not card["endingShown"]
        assert not card["endingIsLastBeforeTheFoot"]
        assert CARD_ENDING not in card["words"]
        assert "protein" not in card["words"] and "catch" not in card["words"]


def test_browser_the_line_above_the_list_is_the_shorter_one(seen):
    for name in ("example", "empty_list", "nothing"):
        assert seen[name]["closed"]["line"] == TRIALS_LINE


def test_browser_an_empty_list_with_a_box_opens_the_box_and_drops_the_sentence(seen):
    closed = seen["empty_list"]["closed"]
    assert closed["list"] == []
    assert not closed["noteShown"] and closed["noteWords"] == ""
    assert closed["boxShown"] and closed["boxOpen"] and closed["boxCardsOnScreen"] == 20  # ticket 2.T14
    assert closed["showAll"] == "Show all 26"  # ticket 2.T14
    assert closed["summary"].endswith("Tap to close")


def test_browser_no_box_key_means_no_box_and_the_sentence_as_before(seen):
    before = seen["before"]["closed"]
    assert not before["boxShown"] and before["box"] == []
    nothing = seen["nothing"]["closed"]
    assert not nothing["boxShown"]
    assert nothing["noteShown"] and nothing["noteWords"] == EMPTY_SENTENCE
