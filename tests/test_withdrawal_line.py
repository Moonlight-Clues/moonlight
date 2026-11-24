"""Ticket 2.31. Withdrawal line on the card.

Kashish's decision, 23 Nov 2026, 6:02 pm. It changes her 22 Nov decision
("hide, and say how many"):

A medicine on the Approved tab whose list holds a WITHDRAWAL report keeps
its card and carries one quiet grey line. Nothing is hidden by this rule.
Her words for the line, exactly:

    The database records a withdrawal for this medicine in some country or region.

Which cards carry it:
- a card on the main Approved list: when the searched disease's own list
  has a WITHDRAWAL report for that medicine;
- a card in the narrower box or the wider-group box: when the searched
  disease's own list has one, or the list the card came from has one.

Her example, haemophilia A (MONDO_0010602): octocog alfa (CHEMBL4297873)
has three WITHDRAWAL reports on the disease's own list. Its card stays, in
its A to Z place, with the line. Roctavian (valoctocogene roxaparvovec,
CHEMBL4297579) has none: its card stays and has no line. Everything else
on the page is letter for letter what main gives.

Second example: sitaxentan on the pulmonary arterial hypertension list
(fixtures/MONDO_0015924/). Its card stays among the 14 and carries the line.

The older "Withdrawn" warning flag is a different thing. It still hides a
medicine, and this ticket does not touch it.

Saved files only: fixtures/withdrawal_reports/ (see its README) and
fixtures/MONDO_0015924/. No network.
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
from moonlight.engine import HandApproval, Neighbour, sort_into_tabs
from moonlight.fetch import Listed, OnList
from moonlight.filter import sort_paths
from moonlight.records import Disease, Medicine, MedicineForm, Path, Target

import test_api
import test_fetch

ROOT = pathlib.Path(__file__).resolve().parent.parent
SAVED = ROOT / "fixtures" / "withdrawal_reports"
PAGE_FILE = ROOT / "web" / "index.html"
PAGE = PAGE_FILE.read_text(encoding="utf-8")

HEM_A = "MONDO_0010602"
HEM_A_DISEASE = Disease(HEM_A, "hemophilia A")
PAH = "MONDO_0015924"
KEY = "withdrawal_note"

# Kashish's words, exactly.
LINE = "The database records a withdrawal for this medicine in some country or region."
NO_REGULATOR_LINE = "The database lists this as approved, but gives no regulator record for it."
SAFETY_LINE = ("For learning and research exploration, not medical advice. Never start, stop or "
               "change any medicine without a doctor.")

OCTOCOG = "CHEMBL4297873"
ROCTAVIAN = "CHEMBL4297579"
# The main Approved list of haemophilia A, counted from the saved answers
# as main sorts them: 18 cards, A to Z.
HEM_A_APPROVED_18 = [
    "Antihemophilic FACTOR, Pegylated (MW 20000) Human Sequence Recombinant",
    "Concizumab", "Damoctocog Alfa Pegol", "Efanesoctocog Alfa", "Efmoroctocog Alfa",
    "Emicizumab", "Eptacog Alfa (ACTIVATED)", "Eptacog Beta (ACTIVATED)", "Lonoctocog Alfa",
    "Marstacimab", "Moroctocog Alfa", "Octocog Alfa", "Simoctocog Alfa", "Susoctocog Alfa",
    "Tranexamic Acid", "Turoctocog Alfa", "Turoctocog Alfa Pegol", "Valoctocogene Roxaparvovec",
]
OCTOCOG_PLACE = 11  # counting from 0: the twelfth card
HEM_A_WIDER_11 = [
    "Aminocaproic Acid", "Catridecacog", "Coagulation Factor Ix Human",
    "Coagulation Factor Ix Recombinant Human", "Dicumarol", "Ethanolamine Oleate",
    "Pentastarch", "Phytonadione", "Protamine Sulfate", "Thrombin",
    "Von Willebrand Factor Human",
]
# Used by the tests that add a report to a copy of a saved answer.
RITUXIMAB = "CHEMBL1201576"  # only in a trial for haemophilia A: the "more in trials" box
THROMBIN = "CHEMBL2108110"  # approved on the parent "hemorrhagic disease" only
HEMORRHAGIC = "MONDO_0002243"
VWF = "CHEMBL4298126"  # approved on the parent "hemophilia", in a trial for haemophilia A
CARD_LISTS = ("approved", "narrower", "wider_group", "being_studied", "new_clues",
              "more_in_trials", "new_in_trials")
APPROVED_TAB = ("approved", "narrower", "wider_group")


def load(file):
    return json.loads(file.read_text(encoding="utf-8"))


def saved_post_json(body):
    """Stands in for fetch._post_json with the saved files."""
    assert set(body) == {"query", "variables"}
    query, variables = body["query"], body["variables"]
    if "targetId" in variables:
        kind, asked = "target_drugs", variables["targetId"]
    else:
        asked = variables["diseaseId"]
        if "parents" in query:
            kind = "family"
        elif "associatedTargets" in query:
            kind = "associated_targets"
        elif "drugAndClinicalCandidates" in query:
            kind = "disease_drugs"
        else:
            kind = "disease"
    file = SAVED / kind / f"{asked}.response.json"
    assert file.exists(), f"no saved answer for {kind} {asked}"
    return load(file)


def changed_list(disease_id, change):
    """saved_post_json, but the medicine list of one disease is first handed
    to change(rows), which may alter the copy."""
    def post_json(body):
        answer = saved_post_json(body)
        if ("drugAndClinicalCandidates" in body["query"]
                and body["variables"].get("diseaseId") == disease_id):
            answer = copy.deepcopy(answer)
            change(answer["data"]["disease"]["drugAndClinicalCandidates"]["rows"])
        return answer
    return post_json


def add_withdrawal_report(medicine_id):
    """A change for changed_list: one more report, stage WITHDRAWAL, on the
    medicine's own row. It has no link, so the card's report count and
    source stay as they were."""
    def change(rows):
        (row,) = [row for row in rows if row["drug"]["id"] == medicine_id]
        row["clinicalReports"].append(
            {"url": None, "clinicalStage": "WITHDRAWAL",
             "source": "EMA Human Drugs"})
    return change


def no_stages(body):
    """The saved answers as an older question got them: no report says its stage."""
    answer = copy.deepcopy(saved_post_json(body))
    if "drugAndClinicalCandidates" in body["query"] and "diseaseId" in body["variables"]:
        for row in answer["data"]["disease"]["drugAndClinicalCandidates"]["rows"]:
            for report in row["clinicalReports"]:
                del report["clinicalStage"]
    return answer


def no_network():
    return [patch(name, side_effect=AssertionError("network used")) for name in (
        "requests.request", "requests.post", "requests.get",
        "requests.sessions.Session.request")]


@pytest.fixture
def offline():
    guards = no_network() + [patch("moonlight.fetch._post_json", side_effect=saved_post_json)]
    for guard in guards:
        guard.start()
    yield
    for guard in guards:
        guard.stop()


def page_answer(disease_id=HEM_A, post_json=saved_post_json, approvals=None, wrong=None):
    """What /api/clues sends, from saved answers. The hand-written files are
    the real ones unless a test hands in its own."""
    api.forget_visitors()
    guards = no_network() + [patch("moonlight.fetch._post_json", side_effect=post_json)]
    if approvals is not None:
        guards.append(patch.object(engine, "_read_approvals", return_value=approvals))
    if wrong is not None:
        guards.append(patch.object(engine, "_read_corrections", return_value=wrong))
    for guard in guards:
        guard.start()
    try:
        response = TestClient(api.app).get("/api/clues", params={"disease_id": disease_id})
    finally:
        for guard in guards:
            guard.stop()
        api.forget_visitors()
    assert response.status_code == 200
    return response.json()


def left_out_before_2_43():
    """Ticket 2.43 (24 Nov) left out ten blood thinners on this page by hand.
    The comparisons with main's saved page here are about the withdrawal line,
    so they read the left-out list as it was before that ticket.
    tests/test_left_out_r1_r6.py holds the new entries."""
    entries = json.loads((ROOT / "moonlight" / "left_out.json").read_text(encoding="utf-8"))
    return patch.object(engine, "_read_left_out",
                        return_value=[e for e in entries if e["date"] < "2026-11-24"])


@pytest.fixture(scope="module")
def hem_a():
    with left_out_before_2_43():
        return page_answer()


@pytest.fixture(scope="module")
def before():
    """What main answered for haemophilia A before the ticket, from the same
    saved answers."""
    return load(SAVED / f"clues_before_2.31_{HEM_A}.json")


def card(answer, medicine_id, where="approved"):
    (found,) = [item for item in answer.get(where, []) if item["id"] == medicine_id]
    return found


def cards_with_the_key(answer):
    return [(where, item["id"]) for where in CARD_LISTS for item in answer.get(where, [])
            if KEY in item]


def without_the_key(answer):
    plain = copy.deepcopy(answer)
    for where in CARD_LISTS:
        for item in plain.get(where, []):
            item.pop(KEY, None)
    return plain


# ---- the saved answers show the example as the ticket writes it ----

def own_rows():
    answer = load(SAVED / "disease_drugs" / f"{HEM_A}.response.json")
    return answer["data"]["disease"]["drugAndClinicalCandidates"]["rows"]


def stages_of(rows, medicine_id):
    return [report["clinicalStage"] for row in rows
            if medicine_id in (row["drug"]["id"], (row["drug"]["parentMolecule"] or {}).get("id"))
            for report in row["clinicalReports"]]


def test_saved_octocog_alfa_has_three_withdrawal_reports_on_the_diseases_own_list():
    assert stages_of(own_rows(), OCTOCOG).count("WITHDRAWAL") == 3


def test_saved_roctavian_has_reports_and_none_is_a_withdrawal():
    stages = stages_of(own_rows(), ROCTAVIAN)
    assert stages and "WITHDRAWAL" not in stages


def test_saved_no_parent_or_child_list_holds_a_withdrawal_report():
    """So in the saved answers the line can only come from the own list."""
    files = sorted((SAVED / "disease_drugs").glob("*.response.json"))
    assert len(files) == 9  # the disease, its 4 parents and its 4 children
    for file in files:
        if file.name.startswith(HEM_A):
            continue
        rows = load(file)["data"]["disease"]["drugAndClinicalCandidates"]["rows"]
        assert not any(report.get("clinicalStage") == "WITHDRAWAL"
                       for row in rows for report in row["clinicalReports"]), file.name


def test_the_saved_before_answer_has_no_such_key_and_the_same_cards(before):
    assert cards_with_the_key(before) == []
    assert [item["medicine"] for item in before["approved"]] == HEM_A_APPROVED_18


# ---- fetch.py: Listed and OnList say whether the list has such a report ----

def test_fetch_the_word_is_exactly_withdrawal():
    assert fetch.WITHDRAWAL == "WITHDRAWAL"


def test_fetch_the_list_as_records_says_octocog_alfa_has_one(offline):
    found = {entry.medicine.forms[0].parent_id or entry.medicine.forms[0].id: entry
             for entry in fetch.fetch_listed_medicines(HEM_A_DISEASE)}
    assert found[OCTOCOG].withdrawal_report is True
    assert found[ROCTAVIAN].withdrawal_report is False
    assert [family_id for family_id, entry in found.items() if entry.withdrawal_report] == [
        OCTOCOG]


def test_fetch_the_approved_list_says_octocog_alfa_has_one(offline):
    found = {entry.id: entry for entry in fetch.fetch_approved(HEM_A_DISEASE)}
    assert found[OCTOCOG].withdrawal_report is True
    assert found[ROCTAVIAN].withdrawal_report is False
    assert [entry.id for entry in found.values() if entry.withdrawal_report] == [OCTOCOG]


def test_fetch_not_said_is_false_on_both_classes():
    assert Listed(id="X", name="X", forms=(), sources=()).withdrawal_report is False
    medicine = Medicine("X", (MedicineForm("X", "X", best_stage="APPROVAL"),))
    assert OnList(medicine=medicine, reports=()).withdrawal_report is False


def test_fetch_an_answer_with_no_stage_on_its_reports_says_false():
    with patch("moonlight.fetch._post_json", side_effect=no_stages):
        records = fetch.fetch_listed_medicines(HEM_A_DISEASE)
        approved = fetch.fetch_approved(HEM_A_DISEASE)
    assert records and not any(entry.withdrawal_report for entry in records)
    assert not any(entry.withdrawal_report for entry in approved)


@pytest.mark.parametrize("word", ["Withdrawal", "withdrawal", "WITHDRAWN", "WITHDRAWAL ", None])
def test_fetch_only_the_exact_word_counts(word):
    def change(rows):
        for row in rows:
            for report in row["clinicalReports"]:
                if report["clinicalStage"] == "WITHDRAWAL":
                    report["clinicalStage"] = word
    with patch("moonlight.fetch._post_json", side_effect=changed_list(HEM_A, change)):
        records = fetch.fetch_listed_medicines(HEM_A_DISEASE)
    assert not any(entry.withdrawal_report for entry in records)


def test_fetch_a_report_on_a_tablet_form_counts_for_the_whole_family():
    """The saved PAH list: sitaxentan sodium is a form of sitaxentan. A
    WITHDRAWAL report on the form's row marks the one family."""
    sodium = "CHEMBL2105740"

    def post_json(body):
        answer = copy.deepcopy(test_api.fake_with_the_disease_list(body))
        if "drugAndClinicalCandidates" in body["query"] and "diseaseId" in body["variables"]:
            for row in answer["data"]["disease"]["drugAndClinicalCandidates"]["rows"]:
                kept = [report for report in row["clinicalReports"]
                        if report["clinicalStage"] != "WITHDRAWAL"]
                row["clinicalReports"] = kept
            add_withdrawal_report(sodium)(
                answer["data"]["disease"]["drugAndClinicalCandidates"]["rows"])
        return answer

    with patch("moonlight.fetch._post_json", side_effect=post_json):
        records = fetch.fetch_listed_medicines(test_api.PAH)
    marked = [entry.medicine.name for entry in records if entry.withdrawal_report]
    assert marked == ["SITAXENTAN"]


def test_fetch_asks_the_same_questions_as_main():
    """No new question and no new field in a question: the questions are
    letter for letter the ones main had. One later change, by ticket 3.8
    (Kashish, 23 Nov 2026): the proteins question also asks for
    "functionDescriptions"."""
    main = load(SAVED / "questions_on_main.json")
    now = {name: getattr(fetch, name) for name in main}
    now["TARGETS_QUERY"] = test_fetch.targets_question_before_3_8()
    assert now == main
    assert sorted(main) == sorted(
        name for name in dir(fetch) if name.endswith("_QUERY"))


# ---- engine.py: the words, and which cards carry them ----

DISEASE = Disease("MONDO_TEST", "test disease")
PROTEIN = Target("ENSG_TEST", "TEST1", "test protein", 0.9)
CHILD = Disease("MONDO_CHILD", "small test disease")
PARENT = Disease("MONDO_PARENT", "test disease group")


def test_engine_the_line_is_kashishs_words_exactly():
    assert engine.WITHDRAWAL_LINE == LINE


def a_path(name, medicine_id, best="APPROVAL", link=None):
    form = MedicineForm(medicine_id, name, best_stage=best, disease_stage=link, withdrawn=False)
    return Path(Medicine(name, (form,)), PROTEIN, DISEASE, ("INHIBITOR",), PROTEIN.score,
                (f"https://example.org/path/{medicine_id}",))


def listed(name, medicine_id, withdrawal=False):
    return Listed(id=medicine_id, name=name, forms=((medicine_id, name),),
                  sources=(f"https://example.org/list/{medicine_id}",), approved=True,
                  approval_sources=(f"https://example.org/list/{medicine_id}",),
                  regulator_record=True, withdrawal_report=withdrawal)


def on_list(name, medicine_id, link="APPROVAL", withdrawal=False):
    form = MedicineForm(medicine_id, name, best_stage="APPROVAL", disease_stage=link,
                        withdrawn=False)
    return OnList(medicine=Medicine(name, (form,)),
                  reports=((f"https://example.org/report/{medicine_id}", link),),
                  all_seen=True, withdrawal_report=withdrawal)


def neighbour(role, *approved):
    disease = CHILD if role == engine.CHILD else PARENT
    return Neighbour(role, disease, tuple(approved), ())


def notes_for(paths=(), own=(), neighbours=(), records=(), hand=()):
    """(the tabs, the engine's answer: card id -> the line)."""
    tabs = sort_into_tabs(sort_paths(list(paths)), list(own), (), list(neighbours),
                          list(records), list(hand))
    return tabs, engine.withdrawal_notes(tabs, list(records), list(neighbours))


def test_engine_a_main_card_with_a_report_on_the_own_list_carries_the_line():
    tabs, notes = notes_for(
        own=[listed("Alpha", "A", withdrawal=True), listed("Beta", "B")],
        records=[on_list("Alpha", "A", withdrawal=True), on_list("Beta", "B")])
    assert [medicine.id for medicine in tabs.approved] == ["A", "B"]
    assert notes == {"A": LINE}


def test_engine_a_main_card_with_no_report_has_none():
    _, notes = notes_for(own=[listed("Beta", "B")], records=[on_list("Beta", "B")])
    assert notes == {}


def test_engine_a_main_card_found_through_a_protein_carries_the_line_too():
    """Approved for the disease on a path. The own list has the report."""
    tabs, notes = notes_for(
        paths=[a_path("Alpha", "A", link="APPROVAL")],
        records=[on_list("Alpha", "A", link="PHASE_3", withdrawal=True)])
    assert [medicine.id for medicine in tabs.approved] == ["A"]
    assert notes == {"A": LINE}


def test_engine_a_main_card_gets_no_line_from_a_parents_or_childs_list():
    """Only the searched disease's own list counts for the main list."""
    tabs, notes = notes_for(
        own=[listed("Alpha", "A")], records=[on_list("Alpha", "A")],
        neighbours=[neighbour(engine.CHILD, listed("Alpha", "A", withdrawal=True)),
                    neighbour(engine.PARENT, listed("Alpha", "A", withdrawal=True))])
    assert [medicine.id for medicine in tabs.approved] == ["A"]
    assert notes == {}


@pytest.mark.parametrize("role, box", [(engine.CHILD, "narrower"), (engine.PARENT, "wider_group")])
def test_engine_a_box_card_carries_the_line_when_its_own_list_has_a_report(role, box):
    tabs, notes = notes_for(
        neighbours=[neighbour(role, listed("Alpha", "A", withdrawal=True), listed("Beta", "B"))])
    assert [medicine.id for medicine in getattr(tabs, box)] == ["A", "B"]
    assert notes == {"A": LINE}


@pytest.mark.parametrize("role, box", [(engine.CHILD, "narrower"), (engine.PARENT, "wider_group")])
def test_engine_a_box_card_carries_the_line_when_the_searched_list_has_a_report(role, box):
    """In a trial for the searched disease, with a WITHDRAWAL report there."""
    tabs, notes = notes_for(
        neighbours=[neighbour(role, listed("Alpha", "A"))],
        records=[on_list("Alpha", "A", link="PHASE_3", withdrawal=True)])
    assert [medicine.id for medicine in getattr(tabs, box)] == ["A"]
    assert notes == {"A": LINE}


def test_engine_a_box_card_with_no_report_anywhere_has_none():
    _, notes = notes_for(
        neighbours=[neighbour(engine.CHILD, listed("Alpha", "A")),
                    neighbour(engine.PARENT, listed("Beta", "B"))],
        records=[on_list("Alpha", "A", link="PHASE_3")])
    assert notes == {}


def test_engine_a_hand_added_approval_whose_list_has_a_report_carries_the_line():
    hand = HandApproval("A", "Alpha", DISEASE.id, "https://example.org/label")
    tabs, notes = notes_for(
        records=[on_list("Alpha", "A", link="PHASE_3", withdrawal=True)], hand=[hand])
    (added,) = tabs.approved
    assert added.added_from_label and added.proof_note == engine.ADDED_LINE
    assert notes == {"A": LINE}


def test_engine_only_approved_tab_cards_are_ever_named():
    """A medicine in In trials only, or a new clue, is not in the answer,
    whatever its list says."""
    tabs, notes = notes_for(
        paths=[a_path("Trial", "T", link="PHASE_3"), a_path("Clue", "C")],
        records=[on_list("Trial", "T", link="PHASE_3", withdrawal=True),
                 on_list("Boxed", "X", link="PHASE_2", withdrawal=True)])
    assert [clue.medicine.name for clue in tabs.being_studied] == ["Trial"]
    assert [medicine.id for medicine in tabs.more_in_trials] == ["X"]
    assert notes == {}


def test_engine_the_rule_moves_nothing():
    """The tabs are the same whether or not a list has such a report."""
    def tabs(withdrawal):
        return sort_into_tabs(
            sort_paths([a_path("Clue", "C"), a_path("Trial", "T", link="PHASE_3")]),
            [listed("Alpha", "A", withdrawal), listed("Beta", "B")], (),
            [neighbour(engine.PARENT, listed("Gamma", "G", withdrawal))],
            [on_list("Alpha", "A", withdrawal=withdrawal), on_list("Beta", "B")])

    def shape(found):
        return ([m.id for m in found.approved], [m.id for m in found.narrower],
                [m.id for m in found.wider_group],
                [c.medicine.name for c in found.being_studied],
                [c.medicine.name for c in found.new_clues], found.left_out,
                [m.id for m in found.more_in_trials], [m.id for m in found.new_in_trials])

    assert shape(tabs(True)) == shape(tabs(False))
    assert shape(tabs(True))[0] == ["A", "B"]


# ---- /api/clues: Kashish's example ----

def test_example_octocog_alfa_stays_in_its_a_to_z_place_with_the_line(hem_a):
    names = [item["medicine"] for item in hem_a["approved"]]
    assert names == sorted(names, key=str.casefold)
    assert hem_a["approved"][OCTOCOG_PLACE]["id"] == OCTOCOG
    assert hem_a["approved"][OCTOCOG_PLACE]["medicine"] == "Octocog Alfa"
    assert card(hem_a, OCTOCOG)[KEY] == LINE


def test_example_roctavian_stays_and_has_no_line(hem_a):
    roctavian = card(hem_a, ROCTAVIAN)
    assert roctavian["medicine"] == "Valoctocogene Roxaparvovec"
    assert KEY not in roctavian


def test_example_the_approved_tab_has_exactly_the_cards_of_main_in_order(hem_a, before):
    assert [item["medicine"] for item in hem_a["approved"]] == HEM_A_APPROVED_18
    assert len(hem_a["approved"]) == 18
    assert "narrower" not in hem_a and "narrower" not in before  # no such box on this page
    assert [item["medicine"] for item in hem_a["wider_group"]] == HEM_A_WIDER_11
    for where in APPROVED_TAB:
        assert [item["id"] for item in hem_a.get(where, [])] == [
            item["id"] for item in before.get(where, [])]


def test_example_only_octocog_alfas_card_has_the_key(hem_a):
    assert cards_with_the_key(hem_a) == [("approved", OCTOCOG)]


def test_example_octocog_alfas_card_is_otherwise_what_main_gives(hem_a, before):
    now = dict(card(hem_a, OCTOCOG))
    assert now.pop(KEY) == LINE
    assert now == card(before, OCTOCOG)


def test_example_everything_else_is_letter_for_letter_what_main_gives(hem_a, before):
    for where in ("being_studied", "new_clues", "left_out", "more_in_trials", "new_in_trials"):
        assert hem_a[where] == before[where], where
    assert hem_a["left_out"] == {"not_approved": 23, "unclear_link": 0}
    assert len(hem_a["being_studied"]) == 10 and len(hem_a["new_clues"]) == 38
    assert without_the_key(hem_a) == before
    assert list(hem_a) == list(before)  # the same keys in the same order


def test_example_there_is_no_not_shown_line(hem_a):
    assert "not_shown_line" not in hem_a
    assert "not shown" not in json.dumps(hem_a).lower()


def test_example_the_words_come_from_the_engine():
    with patch.object(engine, "WITHDRAWAL_LINE", "words from the engine"):
        answer = page_answer()
    assert card(answer, OCTOCOG)[KEY] == "words from the engine"


def test_example_the_page_asks_open_targets_the_same_questions_as_main(before):
    """Counted with the withdrawal reports cut out of the answers: the page
    then asks exactly the same questions, so the line costs no question."""
    def questions(post_json):
        asked = []

        def noting(body):
            asked.append(json.dumps(body, sort_keys=True))
            return post_json(body)
        page_answer(post_json=noting)
        return asked

    def cut_out(rows):
        for row in rows:
            row["clinicalReports"] = [report for report in row["clinicalReports"]
                                      if report["clinicalStage"] != "WITHDRAWAL"]
    # Sorted: side by side, the lanes may write their questions down in any order.
    with_reports = sorted(questions(saved_post_json))
    assert with_reports == sorted(questions(changed_list(HEM_A, cut_out)))


# ---- /api/clues: the second example, sitaxentan ----

@pytest.fixture
def pah():
    api.forget_visitors()
    guards = no_network() + [
        patch("moonlight.fetch._post_json", side_effect=test_api.fake_with_the_disease_list)]
    for guard in guards:
        guard.start()
    try:
        yield test_api.clues_json(TestClient(api.app), *test_api.FIVE)
    finally:
        for guard in guards:
            guard.stop()
        api.forget_visitors()


def test_sitaxentan_stays_among_the_14_and_carries_the_line(pah):
    names = [item["medicine"] for item in pah["approved"]]
    assert names == test_api.APPROVED_14 and len(names) == 14
    (sitaxentan,) = [item for item in pah["approved"] if item["medicine"] == "Sitaxentan"]
    assert sitaxentan["id"] == "CHEMBL282724"
    assert sitaxentan[KEY] == LINE


def test_sitaxentan_is_the_only_pah_card_with_the_key(pah):
    assert cards_with_the_key(pah) == [("approved", "CHEMBL282724")]


# ---- /api/clues: guards ----

def test_guard_a_card_with_no_withdrawal_report_never_has_the_key(hem_a):
    for where in CARD_LISTS:
        for item in hem_a.get(where, []):
            if item["id"] != OCTOCOG:
                assert KEY not in item, (where, item["medicine"])


def test_guard_an_answer_with_no_stage_on_its_reports_gives_no_line():
    answer = page_answer(post_json=no_stages)
    assert OCTOCOG in [item["id"] for item in answer["approved"]]
    assert cards_with_the_key(answer) == []


def test_guard_with_the_reports_cut_out_the_page_is_what_main_gives_without_them(before):
    """Without the three reports the card has no key. Nothing else on the
    Approved tab moves."""
    def cut_out(rows):
        for row in rows:
            row["clinicalReports"] = [report for report in row["clinicalReports"]
                                      if report["clinicalStage"] != "WITHDRAWAL"]
    answer = page_answer(post_json=changed_list(HEM_A, cut_out))
    assert cards_with_the_key(answer) == []
    assert [item["medicine"] for item in answer["approved"]] == HEM_A_APPROVED_18


def test_guard_a_hand_added_approval_whose_list_has_a_report_gets_the_line(before):
    """Rituximab is only in a trial for haemophilia A in the saved answers.
    Here it is added by hand, and its row is given a WITHDRAWAL report."""
    entry = {"medicine_id": RITUXIMAB, "name": "Rituximab", "disease_id": HEM_A,
             "date": "2026-11-23", "label": "https://example.org/label"}
    assert RITUXIMAB in [item["id"] for item in before["more_in_trials"]]
    answer = page_answer(post_json=changed_list(HEM_A, add_withdrawal_report(RITUXIMAB)),
                         approvals=[entry])
    added = card(answer, RITUXIMAB)
    assert added["proof_note"] == engine.ADDED_LINE  # its own grey line stays
    assert added[KEY] == LINE
    assert added["source"] == "https://example.org/label"
    assert sorted(cards_with_the_key(answer)) == [("approved", RITUXIMAB), ("approved", OCTOCOG)]


def test_guard_a_hand_added_approval_with_no_report_has_no_line():
    entry = {"medicine_id": RITUXIMAB, "name": "Rituximab", "disease_id": HEM_A,
             "date": "2026-11-23", "label": "https://example.org/label"}
    answer = page_answer(approvals=[entry])
    assert KEY not in card(answer, RITUXIMAB)


def test_guard_a_wider_group_card_gets_the_line_from_the_list_it_came_from(before):
    """Thrombin is approved on the parent "hemorrhagic disease" only. Here
    that list is given a WITHDRAWAL report for it."""
    with left_out_before_2_43():  # ticket 2.43, see above
        answer = page_answer(
            post_json=changed_list(HEMORRHAGIC, add_withdrawal_report(THROMBIN)))
    assert card(answer, THROMBIN, "wider_group")[KEY] == LINE
    assert [item["medicine"] for item in answer["wider_group"]] == HEM_A_WIDER_11
    assert without_the_key(answer) == before  # nothing moved


def test_guard_a_wider_group_card_gets_the_line_from_the_searched_diseases_list(before):
    """Von Willebrand factor is approved on the parent "hemophilia" and in a
    trial for haemophilia A. Here haemophilia A's own list is given a
    WITHDRAWAL report for it. Its wider-group card carries the line. Its In
    trials card is not touched: that tab is out of this ticket."""
    answer = page_answer(post_json=changed_list(HEM_A, add_withdrawal_report(VWF)))
    assert card(answer, VWF, "wider_group")[KEY] == LINE
    (in_trials,) = [item for item in answer["being_studied"]
                    if item["medicine"] == "Von Willebrand Factor Human"]
    assert KEY not in in_trials
    assert sorted(cards_with_the_key(answer)) == [("approved", OCTOCOG), ("wider_group", VWF)]


def test_guard_a_card_with_a_red_warning_and_a_report_shows_both():
    wrong = [{"medicine_id": OCTOCOG, "disease_id": HEM_A, "date": "2026-11-23",
              "note": engine.CORRECTION_NOTE}]
    octocog = card(page_answer(wrong=wrong), OCTOCOG)
    assert octocog["warning"] == engine.WRONG_WARNING
    assert octocog[KEY] == LINE


def test_guard_a_card_can_carry_the_no_regulator_line_and_this_line():
    """Two different grey lines, in two different keys."""
    def change(rows):
        for row in rows:
            if row["drug"]["id"] == OCTOCOG:
                for report in row["clinicalReports"]:
                    report["source"] = "TTD"  # not a regulator
    octocog = card(page_answer(post_json=changed_list(HEM_A, change)), OCTOCOG)
    assert octocog["proof_note"] == NO_REGULATOR_LINE
    assert octocog[KEY] == LINE


def test_guard_the_older_withdrawn_flag_still_hides_a_medicine():
    """Out of this ticket, so it must be as it was: a "Withdrawn" warning on
    octocog alfa takes its card off the page and counts it as left out."""
    def change(rows):
        for row in rows:
            if row["drug"]["id"] == OCTOCOG:
                row["drug"]["drugWarnings"] = [{"warningType": "Withdrawn"}]
    answer = page_answer(post_json=changed_list(HEM_A, change))
    assert OCTOCOG not in [item["id"] for item in answer["approved"]]
    assert len(answer["approved"]) == 17
    assert answer["left_out"]["not_approved"] == 24
    assert cards_with_the_key(answer) == []


# ---- web/index.html, read as text ----

TEMPLATE = PAGE[PAGE.index('<template id="card-template">'):]
TEMPLATE = TEMPLATE[:TEMPLATE.index("</template>")]


def test_page_types_none_of_the_words_itself():
    assert LINE not in PAGE
    assert "records a withdrawal" not in PAGE
    assert "withdrawal for this medicine" not in PAGE.lower()


def test_page_the_card_has_its_own_slot_in_the_same_grey_style():
    assert '<p class="proof-note" data-slot="withdrawal-note" hidden></p>' in TEMPLATE
    assert TEMPLATE.count('data-slot="withdrawal-note"') == 1
    assert TEMPLATE.count('data-slot="proof-note"') == 1  # the older slot is still there


def test_page_the_slot_is_under_the_other_grey_line_and_above_the_red_warning():
    older = TEMPLATE.index('data-slot="proof-note"')
    new = TEMPLATE.index('data-slot="withdrawal-note"')
    red = TEMPLATE.index('data-slot="warning"')
    assert older < new < red


def test_page_prints_what_the_api_sends():
    assert 'slot(el, "withdrawal-note").textContent = medicine.withdrawal_note;' in PAGE


def test_page_the_safety_line_is_still_there():
    assert SAFETY_LINE in PAGE


# ---- the rule book and the decision list ----

def test_claude_md_keeps_the_withdrawn_rule_and_adds_the_new_words():
    text = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
    old = ("- A medicine withdrawn in any country does not count as approved. It\n"
           "  is not shown anywhere on the page: no tab, no folded box, and it is\n"
           "  never added from the hand-written list of missing approvals.\n")
    assert old in text
    after = " ".join(text[text.index(old) + len(old):].split("- New clue:")[0].split())
    assert after == (
        "A WITHDRAWAL report on a disease's list is a different thing. It does not hide "
        "a card. On the Approved tab the card stays and says: " + LINE
        + " (Kashish, 23 Nov 2026.)")


# Ticket 3.8 added later decisions under it, so the line is no longer the
# last one. This test used to be test_decisions_md_ends_with_the_new_line.
def test_decisions_md_still_holds_the_new_line():
    lines = (ROOT / "DECISIONS.md").read_text(encoding="utf-8").rstrip("\n").split("\n")
    assert lines.count(
        "- 2026-11-23: A medicine with a WITHDRAWAL report keeps its card on the Approved "
        'tab, with the line "' + LINE + '" This replaces the 22 Nov decision to hide it. '
        "The older Withdrawn warning flag still hides.") == 1


# ---- the page, in a real browser, at phone width ----

BROWSER_SCRIPT = r"""
"use strict";
const fs = require("fs");
const { chromium } = require("playwright");
const PAGE = fs.readFileSync(process.argv[1], "utf-8");
const ANSWERS = JSON.parse(fs.readFileSync(process.argv[2], "utf-8"));
const SITE = "http://moonlight.test";

function readApproved() {
  const words = el => el.innerText.replace(/\s+/g, " ").trim();
  const readCard = card => {
    const lines = [...card.querySelectorAll(".proof-note, .wrong-warning")]
      .filter(el => !el.hidden);
    const note = card.querySelector('[data-slot="withdrawal-note"]');
    const older = card.querySelector('[data-slot="proof-note"]');
    // The bottom edge of the nearest thing shown above it on the card.
    const bottomAbove = el => {
      let above = el.previousElementSibling;
      while (above && !above.getClientRects().length) above = above.previousElementSibling;
      return above.getBoundingClientRect().bottom;
    };
    const style = el => {
      const s = getComputedStyle(el);
      return [s.color, s.backgroundColor, s.fontSize, s.fontWeight, s.borderTopColor].join("|");
    };
    return {
      id: card.dataset.clueId || "",
      name: card.querySelector('[data-slot="medicine-name"]').textContent,
      lines: lines.map(el => ({ slot: el.dataset.slot, words: words(el) })),
      noteShown: !!note && !note.hidden && note.getClientRects().length > 0,
      noteClass: note ? note.className : null,
      sameStyle: note && older ? style(note) === style(older) : null,
      gapAbove: note && !note.hidden ? note.getBoundingClientRect().top - bottomAbove(note) : null,
      fits: note ? note.getBoundingClientRect().right <= card.getBoundingClientRect().right
        && note.getBoundingClientRect().left >= card.getBoundingClientRect().left : null,
      words: card.textContent.replace(/\s+/g, " ").trim(),
    };
  };
  const cards = id => [...document.querySelectorAll("#" + id + " > .card")].map(readCard);
  return {
    tab: words(document.getElementById("tab-approved")),
    approved: cards("approved-cards"),
    narrower: cards("narrower-cards"),
    wider: cards("wider-cards"),
    elsewhere: [...document.querySelectorAll("#panel-trials .card, #panel-clues .card")]
      .filter(card => { const n = card.querySelector('[data-slot="withdrawal-note"]');
                        return n && !n.hidden; }).length,
    sideways: document.documentElement.scrollWidth > window.innerWidth,
  };
}

async function oneSearch(browser, answer) {
  const context = await browser.newContext({ viewport: { width: 390, height: 844 } });
  const page = await context.newPage();
  const errors = [];
  page.on("pageerror", problem => errors.push(String(problem)));
  await context.route("**/*", route => {
    const url = route.request().url();
    if (url === SITE + "/" || url.startsWith(SITE + "/?"))
      return route.fulfill({ contentType: "text/html; charset=utf-8", body: PAGE });
    if (url.startsWith(SITE + "/api/clues?"))
      return route.fulfill({ contentType: "application/json", body: JSON.stringify(answer) });
    if (url.startsWith(SITE + "/api/explain?"))
      return route.fulfill({ status: 404, contentType: "application/json", body: "{}" });
    return route.abort();
  });
  await page.goto(SITE + "/?disease=MONDO_TEST");
  await page.waitForSelector("#found", { state: "visible" });
  const out = { errors };
  out.firstTab = await page.evaluate(
    () => document.querySelector('.tab[aria-selected="true"]').dataset.tab);
  for (const id of ["narrower-box", "wider-box"]) {
    const box = page.locator("#" + id);
    if (await box.isVisible() && !(await box.evaluate(el => el.open)))
      await page.click("#" + id + " summary");
  }
  await page.waitForTimeout(300);
  out.read = await page.evaluate(readApproved);
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
def answers(hem_a, before):
    """Answers of /api/clues: her example, the same page as main answered
    it, and one with every kind of line on octocog alfa's card and a line in
    the wider-group box."""
    both = copy.deepcopy(hem_a)
    octocog = card(both, OCTOCOG)
    octocog["proof_note"] = NO_REGULATOR_LINE
    octocog["warning"] = engine.WRONG_WARNING
    card(both, THROMBIN, "wider_group")[KEY] = LINE
    return {"example": hem_a, "before": before, "both": both}


def open_the_pages(answers, folder):
    node = shutil.which("node")
    if not node or subprocess.run(
            [node, "-e", "require('playwright')"], capture_output=True).returncode:
        pytest.skip("needs node with playwright to open a real browser")
    answers_file = folder / "answers.json"
    answers_file.write_text(json.dumps(answers), encoding="utf-8")
    run = subprocess.run(
        [node, "-e", BROWSER_SCRIPT, str(PAGE_FILE), str(answers_file)],
        capture_output=True, text=True, timeout=240, cwd=str(ROOT))
    assert run.returncode == 0, run.stderr[-3000:]
    out = json.loads(run.stdout)
    for name in answers:
        assert out[name]["errors"] == [], name
    return out


@pytest.fixture(scope="module")
def seen(answers, tmp_path_factory):
    """Opens the page once per answer, 390 wide, and returns what a reader sees."""
    return open_the_pages(answers, tmp_path_factory.mktemp("withdrawal_line"))


def seen_card(seen_page, name, where="approved"):
    (found,) = [item for item in seen_page["read"][where] if item["name"] == name]
    return found


def test_browser_example_the_approved_tab_shows_the_same_18_cards_in_order(seen):
    assert seen["example"]["firstTab"] == "approved"
    assert seen["example"]["read"]["tab"] == seen["before"]["read"]["tab"]
    assert [item["name"] for item in seen["example"]["read"]["approved"]] == HEM_A_APPROVED_18
    assert [item["name"] for item in seen["example"]["read"]["wider"]] == HEM_A_WIDER_11


def test_browser_example_octocog_alfas_card_shows_the_line_in_grey(seen):
    octocog = seen_card(seen["example"], "Octocog Alfa")
    assert octocog["lines"] == [{"slot": "withdrawal-note", "words": LINE}]
    assert octocog["noteShown"] is True
    assert octocog["noteClass"] == "proof-note"
    assert octocog["sameStyle"] is True  # as the "no regulator record" line looks


def test_browser_example_the_line_does_not_crowd_the_card(seen):
    octocog = seen_card(seen["example"], "Octocog Alfa")
    assert octocog["gapAbove"] >= 10  # a clear space above it, in pixels
    assert octocog["fits"] is True
    assert seen["example"]["read"]["sideways"] is False  # the page does not scroll sideways


def test_browser_example_no_other_card_shows_the_line(seen):
    read = seen["example"]["read"]
    for item in read["approved"] + read["wider"] + read["narrower"]:
        if item["name"] != "Octocog Alfa":
            assert item["noteShown"] is False, item["name"]
            assert "withdrawal-note" not in [line["slot"] for line in item["lines"]]
            assert LINE not in item["words"], item["name"]
    assert read["elsewhere"] == 0  # no In trials or New clues card shows it


def test_browser_example_every_other_card_reads_as_on_main(seen):
    for where in ("approved", "wider", "narrower"):
        now, was = seen["example"]["read"][where], seen["before"]["read"][where]
        assert len(now) == len(was)
        for card_now, card_was in zip(now, was):
            if card_now["name"] == "Octocog Alfa":
                assert card_now["words"].replace(LINE, "", 1).split() == card_was["words"].split()
            else:
                assert card_now["words"] == card_was["words"]


def test_browser_main_shows_no_line_anywhere(seen):
    read = seen["before"]["read"]
    assert not any(item["noteShown"] for item in read["approved"] + read["wider"])
    assert LINE not in json.dumps(read)


def test_browser_with_both_grey_lines_it_is_under_the_other_and_the_red_one_shows_too(seen):
    octocog = seen_card(seen["both"], "Octocog Alfa")
    assert octocog["lines"] == [
        {"slot": "proof-note", "words": NO_REGULATOR_LINE},
        {"slot": "withdrawal-note", "words": LINE},
        {"slot": "warning", "words": engine.WRONG_WARNING},
    ]


def test_browser_a_card_in_the_wider_group_box_shows_the_line(seen):
    thrombin = seen_card(seen["both"], "Thrombin", "wider")
    assert thrombin["lines"][-1] == {"slot": "withdrawal-note", "words": LINE}
    assert thrombin["noteShown"] is True
