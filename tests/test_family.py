"""Ticket 2.12. Approved medicines from one sheet up and one sheet down.

Kashish's decisions, 16 Nov. The Approved tab also looks at the disease's
direct parents and direct children. A medicine found only there gets a
label saying where the database lists it. Found on a child: main list.
Found only on a parent: the folded box "Approved for a wider group".
It is never a new clue. If it is in trials for this exact disease it stays
in In trials too.

Saved files only (fixtures/family/, asked live on 2026-11-16). No network.
"""

import json
import pathlib
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from moonlight import api, engine, explain, fetch
from moonlight.engine import Neighbour, sort_into_tabs
from moonlight.fetch import Listed
from moonlight.filter import sort_paths
from moonlight.records import Disease, Medicine, MedicineForm, Path, Target

from test_fetch import PAH, noted_post_json

REAL_POST_JSON = fetch._post_json  # kept before any test swaps it

ROOT = pathlib.Path(__file__).resolve().parent.parent
FAMILY = ROOT / "fixtures" / "family"
PAGE = (ROOT / "web" / "index.html").read_text(encoding="utf-8")

AMYLOIDOSIS = Disease(id="MONDO_0019065", name="amyloidosis")
PRE_B_ALL = Disease(id="MONDO_0020511", name="precursor B-cell acute lymphoblastic leukemia")
ECZEMA = Disease(id="MONDO_0004980", name="atopic eczema")
FIVE = ("BMPR2", "KCNK3", "ACVRL1", "EDNRA", "PDE5A")

CHILD_WORDS = ", which the database lists under this disease."
PARENT_WORDS = ", a wider group the database puts this disease in."
ALL_LABEL = "Approved for acute lymphoblastic leukemia" + PARENT_WORDS
BOX_TITLE = "Approved for a wider group"
APPROVED_EMPTY = "The database lists no medicine approved for this disease."

ALL_15 = [
    "ASPARAGINASE ERWINIA CHRYSANTHEMI", "BLINATUMOMAB", "CALASPARGASE PEGOL",
    "CHLORAMBUCIL", "CLOFARABINE", "CYTARABINE", "DASATINIB ANHYDROUS",
    "INOTUZUMAB OZOGAMICIN", "MERCAPTOPURINE ANHYDROUS", "METHOTREXATE",
    "PEGASPARGASE", "PLERIXAFOR", "PONATINIB", "RITUXIMAB", "THIOGUANINE",
]
# Withdrawn in some country and approved on a parent or child of atopic eczema.
ECZEMA_WITHDRAWN = (
    "ASTEMIZOLE", "BUFEXAMAC", "CARBINOXAMINE", "KETOCONAZOLE", "METHAPYRILENE",
    "PHENOL", "TERFENADINE", "THENALIDINE",
)


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def one_file(folder, pattern):
    (file,) = folder.glob(pattern)
    return file


def family_post_json(body, searched=None):
    """Stands in for fetch._post_json with the files saved for ticket 2.12.

    A list question is answered from the folder of whichever of the five
    diseases has that entry as itself, a parent or a child. A protein
    question is answered from the folder of the disease being searched.
    """
    assert set(body) == {"query", "variables"}
    query, variables = body["query"], body["variables"]
    if "targetId" in variables:
        assert searched, "say which disease is being searched"
        return load(one_file(
            FAMILY / searched / "target_drugs", f"*_{variables['targetId']}.response.json"))
    disease_id = variables["diseaseId"]
    if "parents" in query:
        return load(FAMILY / disease_id / "family.response.json")
    if "associatedTargets" in query:
        return load(FAMILY / disease_id / "associated_targets.response.json")
    if "drugAndClinicalCandidates" in query:
        files = sorted(FAMILY.glob(f"*/disease_drugs/*_{disease_id}.response.json"))
        assert files, f"no saved list for {disease_id}"
        return load(files[0])
    return load(FAMILY / disease_id / "disease.response.json")


def pah_post_json(body):
    """PAH: the answer-key files (the ones with the withdrawn note), plus the
    family and the parent's and children's lists saved for this ticket."""
    variables = body["variables"]
    if "parents" in body["query"]:
        return family_post_json(body)
    if "drugAndClinicalCandidates" in body["query"] and variables.get("diseaseId") not in (
            None, PAH.id):
        return family_post_json(body)
    return noted_post_json(body)


@pytest.fixture(autouse=True)
def offline():
    """Saved files instead of Open Targets. Real HTTP is an error."""
    explain.forget_everything()
    with patch("moonlight.fetch._post_json", side_effect=family_post_json) as fake, \
            patch("requests.request", side_effect=AssertionError("network used")), \
            patch("requests.post", side_effect=AssertionError("network used")), \
            patch("requests.get", side_effect=AssertionError("network used")), \
            patch("requests.sessions.Session.request",
                  side_effect=AssertionError("network used")):
        yield fake
    explain.forget_everything()


def searching(disease):
    """The pretend Open Targets, while this disease is the one searched."""
    return patch("moonlight.fetch._post_json",
                 side_effect=lambda body: family_post_json(body, disease.id))


def tabs_for(disease, with_family=True, targets=None):
    if targets is None:
        with searching(disease):
            return tabs_for(disease, with_family, fetch.fetch_targets(disease, 25))
    tray = engine.find_clues(disease, targets)
    neighbours = engine.fetch_neighbours(disease) if with_family else ()
    return sort_into_tabs(
        tray, fetch.fetch_approved(disease), fetch.fetch_withdrawn(disease), neighbours)


@pytest.fixture(scope="module")
def saved_tabs():
    """Each disease's tabs, worked out once: (today, with the family)."""
    made = {}

    def get(disease):
        if disease.id not in made:
            made[disease.id] = (tabs_for(disease, False), tabs_for(disease, True))
        return made[disease.id]
    return get


def names(medicines):
    return [medicine.name for medicine in medicines]


def clue_ids(clues):
    return [engine._family_id(clue.medicine) for clue in clues]


def named(medicines, name):
    (found,) = [medicine for medicine in medicines if medicine.name == name]
    return found


def everyone_shown(tabs):
    """Every medicine and form name in any tab or in the box, in capitals."""
    found = set()
    for medicine in tabs.approved + tabs.wider_group:
        found.add(medicine.name.upper())
        found.update(name.upper() for name in medicine.forms)
    for clue in tabs.being_studied + tabs.new_clues:
        found.add(clue.medicine.name.upper())
        found.update(form.name.upper() for form in clue.medicine.forms)
    return found


# ---- fetch: the question and its answer ----

def test_the_saved_files_were_made_with_the_questions_fetch_asks():
    families = list(FAMILY.glob("*/family.request.json"))
    lists = list(FAMILY.glob("*/disease_drugs/*.request.json"))
    assert len(families) == 5 and len(lists) == 48
    for file in families:
        assert load(file)["query"] == fetch.FAMILY_QUERY
    for file in lists:
        assert load(file)["query"] == fetch.DISEASE_DRUGS_QUERY


def test_the_family_question_asks_for_parents_and_children_by_those_names():
    saved = load(FAMILY / "disease_type.response.json")
    fields = {field["name"] for field in saved["data"]["__type"]["fields"]}
    assert {"parents", "children"} <= fields
    assert "parents { id name }" in fetch.FAMILY_QUERY
    assert "children { id name }" in fetch.FAMILY_QUERY
    # One step only. Not grandparents.
    assert "ancestors" not in fetch.FAMILY_QUERY.lower()
    assert "descendants" not in fetch.FAMILY_QUERY.lower()


def test_pre_b_all_has_two_parents_and_two_children(offline):
    family = fetch.fetch_family(PRE_B_ALL)
    assert [(d.id, d.name) for d in family.parents] == [
        ("MONDO_0017595", "aggressive B-cell non-Hodgkin lymphoma"),
        ("MONDO_0004967", "acute lymphoblastic leukemia"),
    ]
    assert [d.id for d in family.children] == ["MONDO_0000814", "MONDO_0000872"]
    (body,) = [call.args[0] for call in offline.call_args_list]
    assert body == {"query": fetch.FAMILY_QUERY, "variables": {"diseaseId": PRE_B_ALL.id}}


def test_a_disease_open_targets_does_not_know_has_no_family(offline):
    offline.side_effect = lambda body: {"data": {"disease": None}}
    family = fetch.fetch_family(Disease(id="NOT_AN_ID", name="?"))
    assert family.parents == () and family.children == ()


def test_an_answer_with_no_family_fields_means_no_family_and_nothing_is_guessed(offline):
    offline.side_effect = lambda body: {"data": {"disease": {"id": "X", "name": "x"}}}
    family = fetch.fetch_family(Disease(id="X", name="x"))
    assert family.parents == () and family.children == ()


# ---- engine: the extra entries, side by side, by lane number ----

def test_neighbours_come_back_parents_first_in_open_targets_order():
    neighbours = engine.fetch_neighbours(AMYLOIDOSIS)
    assert [n.role for n in neighbours] == ["parent"] + ["child"] * 11
    saved = load(FAMILY / AMYLOIDOSIS.id / "family.response.json")["data"]["disease"]
    assert [n.disease.id for n in neighbours] == [
        entry["id"] for entry in saved["parents"] + saved["children"]]


def test_neighbours_keep_their_lane_even_when_a_later_one_answers_first(offline):
    import threading
    import time
    slow = "MONDO_0017595"  # the first parent

    def slow_first(body):
        if "drugAndClinicalCandidates" in body["query"] and body["variables"]["diseaseId"] == slow:
            time.sleep(0.05)
        return family_post_json(body)

    offline.side_effect = slow_first
    neighbours = engine.fetch_neighbours(PRE_B_ALL)
    assert [n.disease.id for n in neighbours] == [
        "MONDO_0017595", "MONDO_0004967", "MONDO_0000814", "MONDO_0000872"]
    assert threading.active_count() < 50


def test_each_extra_entry_is_asked_with_the_list_question_through_post_json(offline):
    engine.fetch_neighbours(PRE_B_ALL)
    asked = [call.args[0] for call in offline.call_args_list]
    assert asked[0]["query"] == fetch.FAMILY_QUERY
    assert all(body["query"] == fetch.DISEASE_DRUGS_QUERY for body in asked[1:])
    assert {body["variables"]["diseaseId"] for body in asked[1:]} == {
        "MONDO_0017595", "MONDO_0004967", "MONDO_0000814", "MONDO_0000872"}


def test_the_list_question_for_an_extra_entry_is_saved_with_a_use_by_date(tmp_path, monkeypatch):
    """Through the real _post_json: asked twice, saved, then not asked again."""
    monkeypatch.setenv("MOONLIGHT_CACHE_DIR", str(tmp_path))
    sent = []

    def send(body):
        sent.append(body)
        return family_post_json(body)

    with patch("moonlight.fetch._post_json", REAL_POST_JSON), \
            patch("moonlight.fetch._send", side_effect=send), \
            patch("moonlight.fetch.data_version", return_value="test"):
        from moonlight import cache
        cache.forget_memory()
        parent = Disease(id="MONDO_0004967", name="acute lymphoblastic leukemia")
        first = fetch.fetch_approved(parent)
        assert len(sent) == fetch.ASKS_AT_FIRST  # the ask-twice rule
        assert fetch.fetch_approved(parent) == first
        assert len(sent) == fetch.ASKS_AT_FIRST  # from the saved results
        with patch("moonlight.cache._now",
                   return_value=cache._now() + fetch.USE_BY_SECONDS + 1):
            fetch.fetch_approved(parent)
        assert len(sent) == 2 * fetch.ASKS_AT_FIRST  # past its use-by date
        cache.forget_memory()


# ---- EXAMPLE: Pre-B ALL ----

def test_pre_b_all_main_list_is_empty_and_the_box_holds_the_15_from_all(saved_tabs):
    today, tabs = saved_tabs(PRE_B_ALL)
    assert today.approved == [] and today.wider_group == []
    assert tabs.approved == []
    assert names(tabs.wider_group) == ALL_15  # A to Z
    assert all(medicine.label == ALL_LABEL for medicine in tabs.wider_group)


def test_pre_b_all_in_trials_and_new_clues_are_unchanged(saved_tabs):
    today, tabs = saved_tabs(PRE_B_ALL)
    assert len(today.being_studied) == 23
    assert tabs.being_studied == today.being_studied
    assert tabs.new_clues == today.new_clues
    assert tabs.left_out == today.left_out


def test_pre_b_all_six_medicines_are_in_trials_and_also_in_the_box(saved_tabs):
    _, tabs = saved_tabs(PRE_B_ALL)
    both = set(clue_ids(tabs.being_studied)) & {m.id for m in tabs.wider_group}
    in_both = sorted(m.name for m in tabs.wider_group if m.id in both)
    assert in_both == ["BLINATUMOMAB", "CLOFARABINE", "CYTARABINE", "DASATINIB ANHYDROUS",
                       "PONATINIB", "RITUXIMAB"]


# ---- EXAMPLE: atopic eczema ----

def test_atopic_eczema_main_list_is_45_and_the_box_is_68(saved_tabs):
    today, tabs = saved_tabs(ECZEMA)
    assert len(today.approved) == 41
    assert len(tabs.approved) == 45 and len(tabs.wider_group) == 68
    for group in (tabs.approved, tabs.wider_group):
        assert names(group) == sorted(names(group), key=str.casefold)
    # The 41 from the disease's own entry are as today, with no label.
    assert [m for m in tabs.approved if m.label is None] == today.approved


def test_atopic_eczema_four_carry_the_child_label(saved_tabs):
    _, tabs = saved_tabs(ECZEMA)
    labelled = {m.name: m.label for m in tabs.approved if m.label}
    assert labelled == {
        name: "Approved for seborrheic dermatitis" + CHILD_WORDS
        for name in ("CICLOPIROX", "COAL TAR", "SALICYLIC ACID", "SELENIUM SULFIDE")
    }


def test_atopic_eczema_child_wins_over_parent(saved_tabs):
    # Salicylic acid and selenium sulfide are approved on the child
    # seborrheic dermatitis AND on the parent dermatitis.
    _, tabs = saved_tabs(ECZEMA)
    boxed = names(tabs.wider_group)
    assert "SALICYLIC ACID" not in boxed and "SELENIUM SULFIDE" not in boxed
    assert "dermatitis, a wider group" not in named(tabs.approved, "SALICYLIC ACID").label


def test_atopic_eczema_box_labels_name_the_parent(saved_tabs):
    _, tabs = saved_tabs(ECZEMA)
    labels = {m.label for m in tabs.wider_group}
    assert labels == {"Approved for allergic disease" + PARENT_WORDS,
                      "Approved for dermatitis" + PARENT_WORDS}
    assert named(tabs.wider_group, "CETIRIZINE").label == (
        "Approved for allergic disease" + PARENT_WORDS)
    assert named(tabs.wider_group, "ZINC OXIDE").label == "Approved for dermatitis" + PARENT_WORDS


def test_atopic_eczema_33_medicines_leave_new_clues_and_in_trials_is_unchanged(saved_tabs):
    today, tabs = saved_tabs(ECZEMA)
    assert len(today.new_clues) == 133 and len(tabs.new_clues) == 100
    assert tabs.being_studied == today.being_studied and len(tabs.being_studied) == 26
    # The 100 that stay keep the order they had.
    left = set(clue_ids(tabs.new_clues))
    assert clue_ids(tabs.new_clues) == [i for i in clue_ids(today.new_clues) if i in left]


def test_a_labelled_medicine_is_never_a_new_clue(saved_tabs):
    for disease in (ECZEMA, AMYLOIDOSIS, PRE_B_ALL):
        _, tabs = saved_tabs(disease)
        labelled = {m.id for m in tabs.approved + tabs.wider_group if m.label}
        assert labelled
        assert labelled & set(clue_ids(tabs.new_clues)) == set()


def test_atopic_eczema_withdrawn_on_a_parent_or_child_is_left_out_and_counted(saved_tabs):
    today, tabs = saved_tabs(ECZEMA)
    shown = everyone_shown(tabs)
    for name in ECZEMA_WITHDRAWN:
        assert name not in shown, name
    assert tabs.left_out["unclear_link"] == today.left_out["unclear_link"] == 2
    assert today.left_out["not_approved"] == 94
    # Five of the eight act on the proteins looked at, so they were already
    # counted. Bufexamac, ketoconazole and phenol are new to the count.
    assert tabs.left_out["not_approved"] == 97


# ---- EXAMPLE: amyloidosis ----

def test_amyloidosis_main_list_is_11_and_the_box_is_empty(saved_tabs):
    today, tabs = saved_tabs(AMYLOIDOSIS)
    assert len(today.approved) == 5
    assert len(tabs.approved) == 11 and tabs.wider_group == []
    assert sorted(m.name for m in tabs.approved if m.label) == [
        "ACORAMIDIS", "DIFLUNISAL", "EPLONTERSEN", "EPLONTERSEN SODIUM", "VUTRISIRAN",
        "VUTRISIRAN SODIUM"]


def test_acoramidis_names_both_children(saved_tabs):
    _, tabs = saved_tabs(AMYLOIDOSIS)
    assert named(tabs.approved, "ACORAMIDIS").label == (
        "Approved for hereditary ATTR amyloidosis and cardiac amyloidosis" + CHILD_WORDS)
    assert named(tabs.approved, "DIFLUNISAL").label == (
        "Approved for hereditary ATTR amyloidosis" + CHILD_WORDS)


def test_daratumumab_is_not_approved_for_amyloidosis(saved_tabs):
    # Open Targets says phase 2 for amyloidosis and phase 3 for AL
    # amyloidosis. Moonlight never creates an approval.
    saved = load(FAMILY / "drug_daratumumab_CHEMBL1743007.response.json")
    stages = {row["disease"]["id"]: row["maxClinicalStage"]
              for row in saved["data"]["drug"]["indications"]["rows"]}
    assert stages["MONDO_0019065"] == "PHASE_2" and stages["MONDO_0019438"] == "PHASE_3"
    _, tabs = saved_tabs(AMYLOIDOSIS)
    for medicine in tabs.approved + tabs.wider_group:
        assert "DARATUMUMAB" not in medicine.name.upper()
        assert not any("DARATUMUMAB" in form.upper() for form in medicine.forms)


def test_amyloidosis_one_medicine_leaves_new_clues(saved_tabs):
    today, tabs = saved_tabs(AMYLOIDOSIS)
    gone = set(clue_ids(today.new_clues)) - set(clue_ids(tabs.new_clues))
    assert [m.name for m in tabs.approved if m.id in gone] == ["VUTRISIRAN SODIUM"]
    assert tabs.being_studied == today.being_studied


# ---- EXAMPLE: pulmonary arterial hypertension, the answer key ----

def pah_tabs(with_family):
    by_symbol = {t.symbol: t for t in fetch.fetch_targets(PAH)}
    return tabs_for(PAH, with_family, [by_symbol[symbol] for symbol in FIVE])


def test_pah_tolazoline_is_in_the_box(offline):
    offline.side_effect = pah_post_json
    tabs = pah_tabs(True)
    assert names(tabs.wider_group) == ["TOLAZOLINE"]
    assert tabs.wider_group[0].label == "Approved for pulmonary hypertension" + PARENT_WORDS
    assert tabs.wider_group[0].clue is None
    assert len(tabs.approved) == 13 and all(m.label is None for m in tabs.approved)


def test_pah_the_answer_key_16_2_5_13_does_not_change(offline):
    offline.side_effect = pah_post_json
    today, tabs = pah_tabs(False), pah_tabs(True)
    assert len(tabs.new_clues) == 16 and len(tabs.being_studied) == 2
    assert tabs.left_out == {"not_approved": 13, "unclear_link": 0}
    assert tabs.new_clues == today.new_clues and tabs.being_studied == today.being_studied
    assert tabs.approved == today.approved and tabs.left_out == today.left_out
    assert "SITAXENTAN" not in everyone_shown(tabs)  # withdrawn on the parent too


def test_pah_new_clues_keep_kashishs_order_through_the_api(client):
    """The golden files test_api.py uses, with the family added on top."""
    import test_api

    def golden_with_family(body):
        if "parents" in body["query"]:
            return family_post_json(body)
        if "drugAndClinicalCandidates" in body["query"] and body["variables"].get(
                "diseaseId") not in (None, PAH.id):
            return family_post_json(body)
        return test_api.fake_with_the_disease_list(body)

    with patch("moonlight.fetch._post_json", side_effect=golden_with_family), \
            test_api.with_targets(*FIVE):
        data = client.get("/api/clues", params={"disease_id": PAH.id}).json()
    assert [item["medicine"] for item in data["new_clues"]] == test_api.NEW_ORDER
    assert [item["medicine"] for item in data["being_studied"]] == ["Udenafil", "Vardenafil"]
    assert [item["medicine"] for item in data["wider_group"]] == ["Tolazoline"]
    assert all("label" not in item for item in data["approved"])


# ---- the rules, one at a time, with made-up medicines ----

WIDE = Disease(id="WIDE", name="wide disease")
WIDER = Disease(id="WIDER", name="another wide disease")
NARROW = Disease(id="NARROW", name="narrow disease")
SLIM = Disease(id="SLIM", name="slim disease")
THIN = Disease(id="THIN", name="thin disease")


def listed(name, approved=True):
    return Listed(id="ID_" + name, name=name, forms=(("ID_" + name, name),),
                  sources=(f"https://example.org/{name}",), approved=approved)


def parent(disease=WIDE, approved=(), withdrawn=()):
    return Neighbour("parent", disease, tuple(approved), tuple(withdrawn))


def child(disease=NARROW, approved=(), withdrawn=()):
    return Neighbour("child", disease, tuple(approved), tuple(withdrawn))


def made_up_path(name, disease_stage=None, symbol="AAA", withdrawn=False):
    form = MedicineForm(id="ID_" + name, name=name, best_stage="APPROVAL",
                        disease_stage=disease_stage, withdrawn=withdrawn)
    return Path(
        medicine=Medicine(name=name, forms=(form,)),
        target=Target(id="ENSG_" + symbol, symbol=symbol, name=symbol, score=0.5),
        disease=PAH, action_types=("INHIBITOR",), score=0.5,
        sources=(f"https://example.org/{name}/{symbol}",),
    )


def test_approved_on_the_own_entry_and_on_a_parent_has_no_label():
    tabs = sort_into_tabs(sort_paths([]), [listed("OWNMIL")], (),
                          [parent(approved=[listed("OWNMIL")])])
    assert names(tabs.approved) == ["OWNMIL"] and tabs.approved[0].label is None
    assert tabs.wider_group == []


def test_approved_for_the_disease_through_a_protein_and_on_a_child_has_no_label():
    tray = sort_paths([made_up_path("OWNMIL", disease_stage="APPROVAL")])
    tabs = sort_into_tabs(tray, [], (), [child(approved=[listed("OWNMIL")])])
    assert names(tabs.approved) == ["OWNMIL"] and tabs.approved[0].label is None


def test_only_on_a_child_goes_in_the_main_list_with_the_child_label():
    tabs = sort_into_tabs(sort_paths([]), [listed("OWNMIL")], (),
                          [child(approved=[listed("CHILDMIL")])])
    assert names(tabs.approved) == ["CHILDMIL", "OWNMIL"]  # A to Z together
    assert tabs.approved[0].label == "Approved for narrow disease" + CHILD_WORDS
    assert tabs.approved[0].sources == ("https://example.org/CHILDMIL",)
    assert tabs.wider_group == []


def test_only_on_a_parent_goes_in_the_box_with_the_parent_label():
    tabs = sort_into_tabs(sort_paths([]), [], (),
                          [parent(approved=[listed("ZEDMIL"), listed("alphamil")])])
    assert tabs.approved == []
    assert names(tabs.wider_group) == ["alphamil", "ZEDMIL"]  # A to Z, capitals ignored
    assert tabs.wider_group[0].label == "Approved for wide disease" + PARENT_WORDS


def test_on_a_child_and_on_a_parent_the_child_wins():
    tabs = sort_into_tabs(sort_paths([]), [], (), [
        parent(approved=[listed("BOTHMIL")]), child(approved=[listed("BOTHMIL")])])
    assert names(tabs.approved) == ["BOTHMIL"] and tabs.wider_group == []
    assert tabs.approved[0].label == "Approved for narrow disease" + CHILD_WORDS


def test_two_children_are_both_named_joined_with_and():
    tabs = sort_into_tabs(sort_paths([]), [], (), [
        child(NARROW, approved=[listed("TWOMIL")]), child(SLIM, approved=[listed("TWOMIL")])])
    assert tabs.approved[0].label == (
        "Approved for narrow disease and slim disease" + CHILD_WORDS)


def test_two_parents_are_both_named_and_the_grammar_is_for_two():
    tabs = sort_into_tabs(sort_paths([]), [], (), [
        parent(WIDE, approved=[listed("TWOMIL")]), parent(WIDER, approved=[listed("TWOMIL")])])
    assert tabs.wider_group[0].label == (
        "Approved for wide disease and another wide disease, "
        "wider groups the database puts this disease in.")


def test_three_children_are_named_with_a_comma_and_one_and():
    tabs = sort_into_tabs(sort_paths([]), [], (), [
        child(d, approved=[listed("MANYMIL")]) for d in (NARROW, SLIM, THIN)])
    assert tabs.approved[0].label == (
        "Approved for narrow disease, slim disease and thin disease" + CHILD_WORDS)


def test_a_new_clue_with_a_label_leaves_new_clues_and_keeps_its_paths():
    tray = sort_paths([made_up_path("BOXMIL"), made_up_path("CLUEMIL")])
    tabs = sort_into_tabs(tray, [], (), [parent(approved=[listed("BOXMIL")])])
    assert [clue.medicine.name for clue in tabs.new_clues] == ["CLUEMIL"]
    (boxed,) = tabs.wider_group
    assert boxed.name == "BOXMIL" and [p.target.symbol for p in boxed.clue.paths] == ["AAA"]
    assert tabs.left_out == {"not_approved": 0, "unclear_link": 0}


def test_an_unclear_link_to_this_disease_stays_counted_and_is_also_shown_with_its_label():
    # Dimethindene for atopic eczema is the real case: link stage UNKNOWN,
    # approved for the parent, allergic disease.
    tray = sort_paths([made_up_path("FOGMIL", disease_stage="UNKNOWN")])
    tabs = sort_into_tabs(tray, [], (), [parent(approved=[listed("FOGMIL")])])
    assert names(tabs.wider_group) == ["FOGMIL"]
    assert tabs.left_out == {"not_approved": 0, "unclear_link": 1}


def test_in_trials_for_this_disease_stays_in_trials_and_is_also_shown_with_its_label():
    tray = sort_paths([made_up_path("TRIALMIL", disease_stage="PHASE_2"),
                       made_up_path("KIDMIL", disease_stage="PHASE_3")])
    alone = sort_into_tabs(tray, [])
    tabs = sort_into_tabs(tray, [], (), [parent(approved=[listed("TRIALMIL")]),
                                         child(approved=[listed("KIDMIL")])])
    assert tabs.being_studied == alone.being_studied and len(tabs.being_studied) == 2
    assert names(tabs.wider_group) == ["TRIALMIL"] and names(tabs.approved) == ["KIDMIL"]
    assert tabs.wider_group[0].label and tabs.approved[0].label


def test_withdrawn_on_a_parent_entry_is_left_out_and_counted():
    gone = listed("GONEMIL")
    tabs = sort_into_tabs(sort_paths([]), [], (), [parent(approved=[], withdrawn=[gone])])
    assert tabs.approved == [] and tabs.wider_group == []
    assert tabs.left_out == {"not_approved": 1, "unclear_link": 0}


def test_withdrawn_on_a_child_entry_is_left_out_everywhere_and_counted_once():
    # The child's list says withdrawn. The parent's list has no note and
    # the protein answer has no note. Withdrawn still wins, in every tab.
    gone = listed("GONEMIL")
    tray = sort_paths([made_up_path("GONEMIL", withdrawn=None)])
    tabs = sort_into_tabs(tray, [], (), [
        parent(approved=[gone]), child(approved=[], withdrawn=[gone])])
    assert everyone_shown(tabs) == set()
    assert tabs.left_out == {"not_approved": 1, "unclear_link": 0}


def test_withdrawn_but_only_in_trials_on_a_parent_entry_is_not_counted():
    tabs = sort_into_tabs(sort_paths([]), [], (), [
        parent(withdrawn=[listed("TRIALGONE", approved=False)])])
    assert tabs.left_out == {"not_approved": 0, "unclear_link": 0}


def test_with_no_neighbours_everything_is_as_before():
    tray = sort_paths([made_up_path("CLUEMIL")])
    assert sort_into_tabs(tray, [listed("OWNMIL")]) == sort_into_tabs(
        tray, [listed("OWNMIL")], (), [])
    assert sort_into_tabs(tray, [listed("OWNMIL")]).wider_group == []


# ---- the runner (cli.py) follows the same rule as the page ----

def test_the_runner_does_not_print_a_labelled_medicine_as_a_new_clue():
    import cli
    with searching(AMYLOIDOSIS):
        lines = cli.clue_lines(AMYLOIDOSIS, fetch.fetch_targets(AMYLOIDOSIS, 25))
    text = "\n".join(lines).upper()
    assert "NEW CLUES" in text and "TAFAMIDIS" not in text  # approved: never printed
    assert "VUTRISIRAN SODIUM" not in text
    assert lines[-1] == f"- {cli.MOVED_LABEL}: 1"
    assert sum(1 for line in lines if line.startswith("- ") and "| protein" in line) == 11 + 2


def test_the_runner_counts_33_for_atopic_eczema_and_keeps_in_trials(saved_tabs):
    with searching(ECZEMA):
        targets = fetch.fetch_targets(ECZEMA, 25)
        today = engine.find_ranked_clues(ECZEMA, targets)
        ranked = engine.find_ranked_clues(ECZEMA, targets, engine.fetch_neighbours(ECZEMA))
    assert today.moved_to_approved == 0
    assert ranked.moved_to_approved == 33
    assert len(today.new_clues) - len(ranked.new_clues) == 33
    assert ranked.being_studied == today.being_studied
    _, tabs = saved_tabs(ECZEMA)
    labelled = {m.id for m in tabs.approved + tabs.wider_group if m.label}
    assert labelled & set(clue_ids(ranked.new_clues)) == set()


def test_the_runner_prints_no_extra_line_when_nothing_moved(offline):
    import cli
    offline.side_effect = pah_post_json
    by_symbol = {t.symbol: t for t in fetch.fetch_targets(PAH)}
    lines = cli.clue_lines(PAH, [by_symbol[symbol] for symbol in FIVE])
    assert not any(cli.MOVED_LABEL in line for line in lines)
    assert lines[-1].startswith("- unclear link:")


def test_the_runner_leaves_out_a_medicine_withdrawn_on_a_parent_entry():
    gone = listed("GONEMIL")
    paths = [[made_up_path("GONEMIL", withdrawn=None), made_up_path("CLUEMIL")]]
    with patch("moonlight.engine._fetch_all", return_value=paths):
        ranked = engine.find_ranked_clues(PAH, [], [parent(withdrawn=[gone])])
    assert [clue.medicine.name for clue in ranked.new_clues] == ["CLUEMIL"]
    assert ranked.left_out["not_approved"] == 1 and ranked.moved_to_approved == 0


# ---- the API ----

@pytest.fixture
def client():
    return TestClient(api.app)


def clues_json(client, disease):
    with searching(disease):
        answer = client.get("/api/clues", params={"disease_id": disease.id})
    assert answer.status_code == 200
    return answer.json()


def test_api_pre_b_all_main_list_empty_box_of_15_each_with_the_parent_label(client):
    data = clues_json(client, PRE_B_ALL)
    assert data["approved"] == []
    box = data["wider_group"]
    assert [item["medicine"].upper() for item in box] == ALL_15
    assert all(item["label"] == ALL_LABEL for item in box)
    assert len(data["being_studied"]) == 23


def test_api_a_box_item_has_the_facts_of_an_approved_item_and_its_label(client):
    data = clues_json(client, PRE_B_ALL)
    for item in data["wider_group"]:
        assert set(item) == {"id", "medicine", "forms", "proteins", "reports", "source", "label"}
        assert item["source"] is None or item["source"].startswith("https://")
    said = json.dumps(data["wider_group"]).upper()
    assert "DO NOT TRY IT" not in said and "ENDING" not in said and "RANK" not in said


def test_api_amyloidosis_labels_only_on_the_six_from_children(client):
    data = clues_json(client, AMYLOIDOSIS)
    assert len(data["approved"]) == 11 and "wider_group" not in data
    labelled = [item for item in data["approved"] if "label" in item]
    assert len(labelled) == 6
    acoramidis = [item for item in labelled if item["medicine"] == "Acoramidis"][0]
    assert acoramidis["label"] == (
        "Approved for hereditary ATTR amyloidosis and cardiac amyloidosis" + CHILD_WORDS)
    assert "DARATUMUMAB" not in json.dumps(data["approved"]).upper()
    new = [item["medicine"].upper() for item in data["new_clues"]]
    assert "VUTRISIRAN SODIUM" not in new


def test_api_a_box_medicine_that_is_not_in_trials_cannot_be_explained(client):
    data = clues_json(client, PRE_B_ALL)
    in_trials = {item["id"] for item in data["being_studied"]}
    only_boxed = [item for item in data["wider_group"] if item["id"] not in in_trials]
    assert len(only_boxed) == 9
    for item in only_boxed:
        with searching(PRE_B_ALL):
            answer = client.get(
                "/api/explain", params={"disease_id": PRE_B_ALL.id, "clue_id": item["id"]})
        assert answer.status_code == 404


def test_api_asks_for_the_neighbours_and_a_failure_there_is_a_502(client):
    with searching(PRE_B_ALL), patch("moonlight.api.fetch_neighbours",
                                     side_effect=fetch.FetchError("down")) as asked:
        answer = client.get("/api/clues", params={"disease_id": PRE_B_ALL.id})
    assert asked.call_count == 1 and answer.status_code == 502


# ---- the page ----

def test_the_page_has_the_folded_box_closed_and_hidden_until_there_is_something_in_it():
    start = PAGE.index('id="wider-box"')
    tag = PAGE[PAGE.rindex("<", 0, start):PAGE.index(">", start) + 1]
    assert tag.startswith("<details") and " hidden" in tag and " open" not in tag
    summary = PAGE[start:PAGE.index("</summary>", start)]
    assert BOX_TITLE + " (" in summary
    # Inside the Approved tab, below the main list.
    panel = PAGE[PAGE.index('id="panel-approved"'):PAGE.index('id="panel-trials"')]
    assert panel.index('id="approved-cards"') < panel.index('id="wider-box"')
    assert 'id="wider-cards"' in panel[panel.index('id="wider-box"'):]


def test_the_page_opens_the_box_when_the_main_list_is_empty_and_hides_the_empty_sentence():
    script = PAGE[PAGE.index("function draw(data)"):]
    script = script[:script.index("\n  }\n")]
    assert "data.wider_group || []" in script
    assert 'byId("wider-box").hidden = !widerCards.length' in script
    assert 'byId("wider-box").open = !approvedCards.length' in script
    assert 'byId("approved-empty").hidden = !!approvedCards.length || !!widerCards.length' in script
    # The number on the tab counts everything in the tab: main list and box.
    assert "approved: approvedCards.length + widerCards.length," in script
    assert 'byId("wider-count").textContent = widerCards.length' in script


def test_the_page_keeps_the_approved_tabs_sentences_and_adds_no_ending():
    assert APPROVED_EMPTY in PAGE
    assert ("Already approved for this disease in at least one country, according to "
            "the database. Nothing here says how well any of them works.") in PAGE
    panel = PAGE[PAGE.index('id="panel-approved"'):PAGE.index('id="panel-trials"')]
    assert panel.count("Talk to your doctor before changing any medicine.") == 2  # tab and box
    assert "Do not try it" not in panel


def test_the_page_shows_the_label_on_the_card_as_plain_text():
    assert 'data-slot="label" hidden' in PAGE
    script = PAGE[PAGE.index("function approvedCard("):]
    script = script[:script.index("\n  }\n")]
    assert "medicine.label" in script and "textContent = medicine.label" in script
    assert "innerHTML" not in script
    # The label's words are written by the engine, not by the page.
    assert "which the database lists under" not in PAGE
    assert "a wider group the database puts" not in PAGE
