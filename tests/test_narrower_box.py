"""Ticket 2.14. A box for narrower diseases, and a better source link.

Kashish's decisions, 16 Nov:

1. The main Approved list holds only medicines approved on the disease's
   own entry.
2. A medicine approved only on a child entry is in the folded box
   "Approved for a narrower disease (N)": closed at first, A to Z, above the
   wider-group box. Its label is the same as before.
3. The wider-group box is unchanged.
4. When the main list is empty, every box that has cards starts open and
   the empty-tab sentence is not shown.
5. The number on the Approved tab counts everything in the tab.
6. On a child and on a parent, not on the own entry: the narrower box.
7. In trials and New clues are unchanged.
8. The terminal runner follows the same rule.
9. "Source record" on an Approved card: an exact approval receipt first,
   then Japan's general list, then the link shown before.
10. The guide's line for doctors says each kind has its own folded box.

Saved files only: fixtures/narrower_box/ (copied from the probe of ticket
P2) and fixtures/family/ (ticket 2.12). No network.
"""

import json
import pathlib
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from moonlight import api, engine, explain, fetch
from moonlight.engine import JAPAN_LIST, sort_into_tabs
from moonlight.fetch import Listed
from moonlight.filter import sort_paths
from moonlight.records import Disease

import test_family
import test_fetch
from test_family import AMYLOIDOSIS, ECZEMA, PRE_B_ALL, CHILD_WORDS, PARENT_WORDS
from test_family import child, made_up_path, parent

ROOT = pathlib.Path(__file__).resolve().parent.parent
SAVED = ROOT / "fixtures" / "narrower_box"
PAGE = (ROOT / "web" / "index.html").read_text(encoding="utf-8")

ALL = Disease(id="MONDO_0004967", name="acute lymphoblastic leukemia")
PAH = Disease(id="MONDO_0015924", name="pulmonary arterial hypertension")

NARROWER_TITLE = "Approved for a narrower disease"
CLL_LABEL = "Approved for B-cell chronic lymphocytic leukemia" + CHILD_WORDS

ALL_MAIN_15 = test_family.ALL_15  # the same 15 that Pre-B ALL shows as its wider group
ALL_NARROWER_13 = [
    "ACALABRUTINIB", "ALEMTUZUMAB", "BENDAMUSTINE", "DUVELISIB", "FLUDARABINE PHOSPHATE",
    "IBRUTINIB", "IDELALISIB", "NELARABINE", "OBECABTAGENE AUTOLEUCEL", "OBINUTUZUMAB",
    "OFATUMUMAB", "VENETOCLAX", "ZANUBRUTINIB",
]
THE_FOUR = ["ACALABRUTINIB", "IBRUTINIB", "VENETOCLAX", "ZANUBRUTINIB"]
AMYLOIDOSIS_NARROWER_6 = [
    "ACORAMIDIS", "DIFLUNISAL", "EPLONTERSEN", "EPLONTERSEN SODIUM", "VUTRISIRAN",
    "VUTRISIRAN SODIUM",
]
ECZEMA_NARROWER_4 = ["CICLOPIROX", "COAL TAR", "SALICYLIC ACID", "SELENIUM SULFIDE"]


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def saved_post_json(body):
    """Stands in for fetch._post_json with the files in fixtures/narrower_box/."""
    assert set(body) == {"query", "variables"}
    query, variables = body["query"], body["variables"]
    if "targetId" in variables:
        return load(SAVED / "target_drugs" / f"{variables['targetId']}.response.json")
    disease_id = variables["diseaseId"]
    if "parents" in query:
        return load(SAVED / "family" / f"{disease_id}.response.json")
    if "associatedTargets" in query:
        return load(SAVED / "associated_targets" / f"{disease_id}.response.json")
    if "drugAndClinicalCandidates" in query:
        return load(SAVED / "disease_drugs" / f"{disease_id}.response.json")
    return load(SAVED / "disease" / f"{disease_id}.response.json")


@pytest.fixture(autouse=True)
def offline():
    """Saved files instead of Open Targets. Real HTTP is an error."""
    explain.forget_everything()
    api.forget_visitors()
    with patch("moonlight.fetch._post_json", side_effect=saved_post_json) as fake, \
            patch("requests.request", side_effect=AssertionError("network used")), \
            patch("requests.post", side_effect=AssertionError("network used")), \
            patch("requests.get", side_effect=AssertionError("network used")), \
            patch("requests.sessions.Session.request",
                  side_effect=AssertionError("network used")):
        yield fake
    explain.forget_everything()


def whole_search(disease, with_family=True):
    """The whole search for one disease, the way the API does it."""
    tray = engine.find_clues(disease, fetch.fetch_targets(disease, 25))
    neighbours = engine.fetch_neighbours(disease) if with_family else ()
    return sort_into_tabs(
        tray, fetch.fetch_approved(disease), fetch.fetch_withdrawn(disease), neighbours)


@pytest.fixture(scope="module")
def saved_tabs():
    """Each disease's tabs, worked out once: (with no family, with the family)."""
    made = {}

    def get(disease):
        if disease.id not in made:
            if (SAVED / "disease" / f"{disease.id}.response.json").exists():
                with patch("moonlight.fetch._post_json", side_effect=saved_post_json):
                    made[disease.id] = (whole_search(disease, False), whole_search(disease))
            else:  # saved by ticket 2.12
                with patch("moonlight.fetch._post_json", side_effect=test_family.family_post_json):
                    made[disease.id] = (
                        test_family.tabs_for(disease, False), test_family.tabs_for(disease, True))
        return made[disease.id]
    return get


def names(medicines):
    return [medicine.name for medicine in medicines]


def clue_ids(clues):
    return [engine._family_id(clue.medicine) for clue in clues]


def in_tab(tabs):
    """How many cards the Approved tab holds: main list and both boxes."""
    return len(tabs.approved) + len(tabs.narrower) + len(tabs.wider_group)


# ---- the saved files ----

def test_the_saved_files_were_made_with_the_questions_fetch_asks():
    questions = {
        "disease": fetch.DISEASE_QUERY, "associated_targets": fetch.TARGETS_QUERY,
        "family": fetch.FAMILY_QUERY, "disease_drugs": test_fetch.list_question_before_2_17(),
        "target_drugs": fetch.TARGET_DRUGS_QUERY,
    }
    counted = {}
    for kind, question in questions.items():
        files = list((SAVED / kind).glob("*.request.json"))
        counted[kind] = len(files)
        for file in files:
            assert load(file)["query"] == question
    # Four diseases; their own lists and those of their 11 parents and 32
    # children. Three of the 100 proteins are in the top 25 of two diseases.
    assert counted == {"disease": 4, "associated_targets": 4, "family": 4,
                       "disease_drugs": 47, "target_drugs": 97}


def test_the_database_lists_chronic_lymphocytic_leukemia_under_all():
    children = fetch.fetch_family(ALL).children
    assert ("MONDO_0004948", "B-cell chronic lymphocytic leukemia") in [
        (entry.id, entry.name) for entry in children]


# ---- EXAMPLE: acute lymphoblastic leukemia ----

def test_all_main_list_15_narrower_box_13_wider_box_12(saved_tabs):
    _, tabs = saved_tabs(ALL)
    assert names(tabs.approved) == ALL_MAIN_15
    assert names(tabs.narrower) == ALL_NARROWER_13  # A to Z
    assert len(tabs.wider_group) == 12
    # The tab says 40. That is also the true total: no medicine is in two places.
    assert in_tab(tabs) == 40
    ids = [m.id for m in tabs.approved + tabs.narrower + tabs.wider_group]
    assert len(set(ids)) == 40


def test_all_the_four_are_in_the_narrower_box_and_not_in_the_main_list(saved_tabs):
    _, tabs = saved_tabs(ALL)
    for name in THE_FOUR:
        assert name in names(tabs.narrower)
        assert name not in names(tabs.approved)
        assert test_family.named(tabs.narrower, name).label == CLL_LABEL


def test_all_the_main_list_is_exactly_the_own_entrys_list_with_no_label(saved_tabs):
    alone, tabs = saved_tabs(ALL)
    assert tabs.approved == alone.approved  # as with no family at all
    assert all(medicine.label is None for medicine in tabs.approved)


def test_all_every_narrower_card_keeps_its_child_label(saved_tabs):
    _, tabs = saved_tabs(ALL)
    for medicine in tabs.narrower:
        assert medicine.label.startswith("Approved for ")
        assert medicine.label.endswith(CHILD_WORDS)
    assert test_family.named(tabs.narrower, "NELARABINE").label == (
        "Approved for T-cell acute lymphoblastic leukemia and precursor T-cell acute "
        "lymphoblastic leukemia" + CHILD_WORDS)


def test_all_in_trials_is_unchanged_and_no_labelled_medicine_is_a_new_clue(saved_tabs):
    alone, tabs = saved_tabs(ALL)
    assert tabs.being_studied == alone.being_studied and len(tabs.being_studied) == 16
    assert len(tabs.new_clues) == 21
    labelled = {m.id for m in tabs.narrower + tabs.wider_group}
    assert labelled & set(clue_ids(tabs.new_clues)) == set()
    # Three narrower-box medicines are in trials for this exact disease: they stay there too.
    both = sorted(m.name for m in tabs.narrower if m.id in set(clue_ids(tabs.being_studied)))
    assert both == ["FLUDARABINE PHOSPHATE", "IBRUTINIB", "VENETOCLAX"]


# ---- EXAMPLES: amyloidosis, atopic eczema, Pre-B ALL ----

def test_amyloidosis_main_list_5_narrower_box_6_no_wider_box(saved_tabs):
    alone, tabs = saved_tabs(AMYLOIDOSIS)
    assert tabs.approved == alone.approved and len(tabs.approved) == 5
    assert names(tabs.narrower) == AMYLOIDOSIS_NARROWER_6
    assert tabs.wider_group == []
    assert in_tab(tabs) == 11


def test_atopic_eczema_main_list_41_narrower_box_4_wider_box_68(saved_tabs):
    alone, tabs = saved_tabs(ECZEMA)
    assert tabs.approved == alone.approved and len(tabs.approved) == 41
    assert names(tabs.narrower) == ECZEMA_NARROWER_4
    assert len(tabs.wider_group) == 68
    assert in_tab(tabs) == 113


def test_pre_b_all_main_list_empty_no_narrower_box_wider_box_15(saved_tabs):
    _, tabs = saved_tabs(PRE_B_ALL)
    assert tabs.approved == [] and tabs.narrower == []
    assert names(tabs.wider_group) == test_family.ALL_15


def test_in_trials_and_new_clues_are_as_they_were_for_every_example(saved_tabs):
    # Worked out again the old way: every labelled medicine leaves New clues,
    # nothing leaves In trials.
    for disease, new_clues, in_trials in (
            (AMYLOIDOSIS, 11, 2), (ECZEMA, 100, 26), (PRE_B_ALL, None, 23)):
        alone, tabs = saved_tabs(disease)
        assert tabs.being_studied == alone.being_studied and len(tabs.being_studied) == in_trials
        labelled = {m.id for m in tabs.narrower + tabs.wider_group}
        assert clue_ids(tabs.new_clues) == [
            i for i in clue_ids(alone.new_clues) if i not in labelled]
        if new_clues is not None:
            assert len(tabs.new_clues) == new_clues


# ---- the rules, one at a time, with made-up medicines ----

def listed(name, sources=None, approval_sources=()):
    if sources is None:
        sources = (f"https://example.org/{name}",)
    return Listed(id="ID_" + name, name=name, forms=(("ID_" + name, name),),
                  sources=tuple(sources), approval_sources=tuple(approval_sources))


def test_only_on_a_child_is_in_the_narrower_box_and_not_in_the_main_list():
    tabs = sort_into_tabs(sort_paths([]), [listed("OWNMIL")], (),
                          [child(approved=[listed("ZEDMIL"), listed("alphamil")])])
    assert names(tabs.approved) == ["OWNMIL"] and tabs.approved[0].label is None
    assert names(tabs.narrower) == ["alphamil", "ZEDMIL"]  # A to Z, capitals ignored
    assert tabs.narrower[0].label == "Approved for narrow disease" + CHILD_WORDS
    assert tabs.wider_group == []


def test_on_a_child_and_on_a_parent_goes_in_the_narrower_box():
    tabs = sort_into_tabs(sort_paths([]), [], (), [
        parent(approved=[listed("BOTHMIL"), listed("WIDEMIL")]),
        child(approved=[listed("BOTHMIL")])])
    assert tabs.approved == []
    assert names(tabs.narrower) == ["BOTHMIL"] and names(tabs.wider_group) == ["WIDEMIL"]
    assert tabs.narrower[0].label == "Approved for narrow disease" + CHILD_WORDS
    assert tabs.wider_group[0].label == "Approved for wide disease" + PARENT_WORDS


def test_on_the_own_entry_and_on_a_child_stays_in_the_main_list_with_no_label():
    tabs = sort_into_tabs(sort_paths([]), [listed("OWNMIL")], (),
                          [child(approved=[listed("OWNMIL")])])
    assert names(tabs.approved) == ["OWNMIL"] and tabs.approved[0].label is None
    assert tabs.narrower == []


def test_a_narrower_medicine_in_trials_for_this_disease_stays_in_trials_too():
    tray = sort_paths([made_up_path("KIDMIL", disease_stage="PHASE_3"), made_up_path("CLUEMIL")])
    alone = sort_into_tabs(tray, [])
    tabs = sort_into_tabs(tray, [], (), [child(approved=[listed("KIDMIL"), listed("CLUEMIL")])])
    assert tabs.being_studied == alone.being_studied and len(tabs.being_studied) == 1
    assert names(tabs.narrower) == ["CLUEMIL", "KIDMIL"]
    assert tabs.new_clues == []  # CLUEMIL has a label: never a new clue
    assert [p.target.symbol for p in tabs.narrower[0].clue.paths] == ["AAA"]  # keeps its paths


def test_with_no_neighbours_there_is_no_narrower_box():
    assert sort_into_tabs(sort_paths([]), [listed("OWNMIL")]).narrower == []


# ---- decision 9: which link "Source record" shows ----

EXACT = "https://example.org/approval-record"
TRIAL = "https://example.org/a-trial"


def test_source_record_is_an_exact_approval_receipt_first():
    entry = listed("AMIL", sources=(TRIAL, JAPAN_LIST, EXACT), approval_sources=(JAPAN_LIST, EXACT))
    tabs = sort_into_tabs(sort_paths([]), [entry])
    assert tabs.approved[0].source_record == EXACT
    assert tabs.approved[0].proof_note is None


def test_source_record_is_japans_general_list_if_there_is_no_exact_receipt():
    entry = listed("AMIL", sources=(TRIAL, JAPAN_LIST), approval_sources=(JAPAN_LIST,))
    tabs = sort_into_tabs(sort_paths([]), [entry])
    assert tabs.approved[0].source_record == JAPAN_LIST
    assert tabs.approved[0].proof_note == engine.JAPAN_LINE  # the line is unchanged


def test_source_record_is_the_link_shown_before_if_there_is_no_receipt_at_all():
    entry = listed("AMIL", sources=("http://example.org/not-https", TRIAL))
    tray = sort_paths([made_up_path("AMIL", disease_stage="APPROVAL")])
    tabs = sort_into_tabs(tray, [entry])
    # Before this ticket: the first https link, the ones on its paths first.
    assert tabs.approved[0].source_record == "https://example.org/AMIL/AAA"
    assert sort_into_tabs(sort_paths([]), [entry]).approved[0].source_record == TRIAL
    nothing = sort_into_tabs(sort_paths([]), [listed("BMIL", sources=())])
    assert nothing.approved[0].source_record is None


def test_source_record_is_never_a_receipt_that_is_not_an_https_link():
    entry = listed("AMIL", sources=(TRIAL,), approval_sources=("ftp://example.org/x",))
    assert sort_into_tabs(sort_paths([]), [entry]).approved[0].source_record == TRIAL


def test_source_record_follows_the_same_order_in_both_boxes():
    kid = listed("KIDMIL", sources=(TRIAL, EXACT), approval_sources=(EXACT,))
    wide = listed("WIDEMIL", sources=(TRIAL, JAPAN_LIST), approval_sources=(JAPAN_LIST,))
    tabs = sort_into_tabs(sort_paths([]), [], (),
                          [child(approved=[kid]), parent(approved=[wide])])
    assert tabs.narrower[0].source_record == EXACT
    assert tabs.wider_group[0].source_record == JAPAN_LIST


def test_pah_12_of_the_13_main_list_cards_show_an_exact_approval_receipt(saved_tabs):
    _, tabs = saved_tabs(PAH)
    assert len(tabs.approved) == 13 and tabs.narrower == []
    assert names(tabs.wider_group) == ["TOLAZOLINE"]
    exact = [m for m in tabs.approved
             if m.source_record in m.approval_sources and m.source_record != JAPAN_LIST]
    assert len(exact) == 12
    (other,) = [m for m in tabs.approved if m not in exact]
    assert other.name == "BERAPROST" and other.source_record == JAPAN_LIST
    assert other.proof_note == engine.JAPAN_LINE
    # Ambrisentan's receipts start with Japan's list. The exact one is still chosen.
    ambrisentan = test_family.named(tabs.approved, "AMBRISENTAN")
    assert ambrisentan.approval_sources[0] == JAPAN_LIST
    assert ambrisentan.source_record == (
        "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm"
        "?setid=a4978a54-1799-43d6-85dd-05fa9de0a5d7")


def test_the_source_link_changes_nothing_else_about_a_card(saved_tabs):
    alone, tabs = saved_tabs(PAH)
    assert tabs.approved == alone.approved
    for medicine in tabs.approved:
        assert medicine.source_record in medicine.sources  # always one of its own links


# ---- the API ----

@pytest.fixture
def client():
    return TestClient(api.app)


def clues_json(client, disease):
    answer = client.get("/api/clues", params={"disease_id": disease.id})
    assert answer.status_code == 200
    return answer.json()


def test_api_all_sends_the_three_parts_of_the_approved_tab(client):
    data = clues_json(client, ALL)
    assert [item["medicine"].upper() for item in data["approved"]] == ALL_MAIN_15
    assert [item["medicine"].upper() for item in data["narrower"]] == ALL_NARROWER_13
    assert len(data["wider_group"]) == 12
    assert all("label" not in item for item in data["approved"])
    assert all(item["label"].endswith(CHILD_WORDS) for item in data["narrower"])
    assert len(data["being_studied"]) == 16 and len(data["new_clues"]) == 21


def test_api_a_narrower_item_has_the_facts_of_an_approved_item_and_its_label(client):
    data = clues_json(client, ALL)
    for item in data["narrower"]:
        assert {"id", "medicine", "forms", "proteins", "reports", "source", "label"} <= set(item)
        assert set(item) <= {"id", "medicine", "forms", "proteins", "reports", "source", "label",
                             "proof_note"}
    said = json.dumps(data["narrower"]).upper()
    assert "DO NOT TRY IT" not in said and "ENDING" not in said and "RANK" not in said


def test_api_there_is_no_narrower_part_when_nothing_is_in_it(client):
    assert "narrower" not in clues_json(client, PAH)


def test_api_a_narrower_medicine_that_is_not_in_trials_cannot_be_explained(client):
    data = clues_json(client, ALL)
    in_trials = {item["id"] for item in data["being_studied"]}
    only_boxed = [item for item in data["narrower"] if item["id"] not in in_trials]
    assert len(only_boxed) == 10
    for item in only_boxed:
        answer = client.get("/api/explain", params={"disease_id": ALL.id, "clue_id": item["id"]})
        assert answer.status_code == 404


def test_api_pah_source_record_is_the_exact_receipt_on_12_of_13_cards(client):
    data = clues_json(client, PAH)
    sources = {item["medicine"]: item["source"] for item in data["approved"]}
    assert len(sources) == 13
    assert [name for name, link in sources.items() if link == JAPAN_LIST] == ["Beraprost"]
    assert sources["Sotatercept"] == (
        "https://www.accessdata.fda.gov/drugsatfda_docs/label/2024/761363Orig1s000lbl.pdf")
    # Not a trial link any more.
    assert not any("clinicaltrials.gov" in link for link in sources.values())
    beraprost = [item for item in data["approved"] if item["medicine"] == "Beraprost"][0]
    assert beraprost["proof_note"] == engine.JAPAN_LINE


def test_api_cards_in_trials_and_new_clues_keep_the_source_they_had(client):
    data = clues_json(client, PAH)
    _, tabs = None, whole_search(PAH)
    for sent, clue in zip(data["being_studied"] + data["new_clues"],
                          tabs.being_studied + tabs.new_clues):
        assert sent["source"] == api._one_source(clue)


def test_api_amyloidosis_and_eczema_through_the_api(client):
    for disease, main, narrower, wider in ((AMYLOIDOSIS, 5, 6, 0), (ECZEMA, 41, 4, 68)):
        with test_family.searching(disease):
            data = clues_json(client, disease)
        assert len(data["approved"]) == main
        assert len(data["narrower"]) == narrower
        assert len(data.get("wider_group", [])) == wider
        assert all("label" not in item for item in data["approved"])


# ---- the terminal runner (cli.py) follows the same rule ----

def test_the_runner_never_prints_a_narrower_medicine_as_a_new_clue(saved_tabs):
    import cli
    lines = cli.clue_lines(ALL, fetch.fetch_targets(ALL, 25))
    new = lines[:lines.index(cli.STUDIED_HEADING)]
    assert new[0] == cli.NEW_HEADING
    printed = "\n".join(new).upper()
    _, tabs = saved_tabs(ALL)
    for medicine in tabs.narrower + tabs.wider_group:
        assert f"- {medicine.name} (FORMS:" not in printed, medicine.name
    assert sum(1 for line in new if "| protein" in line) == 21  # the page's New clues


def test_the_runner_counts_a_narrower_medicine_apart_from_this_diseases_own(saved_tabs):
    import cli
    lines = cli.clue_lines(ALL, fetch.fetch_targets(ALL, 25))
    _, tabs = saved_tabs(ALL)
    # "already approved for this disease" counts only the disease's own entry.
    own = {m.name for m in tabs.approved if m.clue}
    assert f"- already approved for this disease: {len(own)}" in lines
    assert lines[-1].startswith(f"- {cli.MOVED_LABEL}: ")
    moved = int(lines[-1].rsplit(": ", 1)[1])
    alone, _ = saved_tabs(ALL)
    assert moved == len(alone.new_clues) - len(tabs.new_clues) > 0


# ---- the page ----

def panel():
    return PAGE[PAGE.index('id="panel-approved"'):PAGE.index('id="panel-trials"')]


def draw_script():
    script = PAGE[PAGE.index("function draw(data)"):]
    return script[:script.index("\n  }\n")]


def test_the_page_has_the_narrower_box_folded_closed_and_hidden_until_it_holds_something():
    start = PAGE.index('id="narrower-box"')
    tag = PAGE[PAGE.rindex("<", 0, start):PAGE.index(">", start) + 1]
    assert tag.startswith("<details") and " hidden" in tag and " open" not in tag
    summary = PAGE[start:PAGE.index("</summary>", start)]
    assert NARROWER_TITLE + ' (<span id="narrower-count"></span>)' in summary


def test_the_page_puts_the_narrower_box_below_the_main_list_and_above_the_wider_box():
    part = panel()
    assert part.index('id="approved-cards"') < part.index('id="narrower-box"')
    assert part.index('id="narrower-box"') < part.index('id="narrower-cards"')
    assert part.index('id="narrower-cards"') < part.index('id="wider-box"')
    assert part.count('id="narrower-box"') == 1


def test_the_page_says_talk_to_your_doctor_inside_the_narrower_box():
    part = panel()
    box = part[part.index('id="narrower-box"'):part.index('id="wider-box"')]
    assert '<p class="doctor-line">Talk to your doctor before changing any medicine.</p>' in box


def test_the_page_fills_the_narrower_box_and_shows_it_only_when_it_holds_something():
    script = draw_script()
    assert "(data.narrower || []).map(medicine => approvedCard(medicine, diseaseName))" in script
    assert 'byId("narrower-cards").replaceChildren(...narrowerCards)' in script
    assert 'byId("narrower-count").textContent = narrowerCards.length' in script
    assert 'byId("narrower-box").hidden = !narrowerCards.length' in script
    assert ".sort(" not in script  # A to Z is the engine's order, not the page's


def test_the_page_opens_every_box_that_has_cards_when_the_main_list_is_empty():
    script = draw_script()
    assert 'byId("narrower-box").open = !approvedCards.length' in script
    assert 'byId("wider-box").open = !approvedCards.length' in script


def test_the_page_hides_the_empty_sentence_when_any_box_has_cards():
    assert ('byId("approved-empty").hidden = !!approvedCards.length || !!widerCards.length'
            ' || !!narrowerCards.length') in draw_script()


def test_the_number_on_the_approved_tab_counts_the_main_list_and_both_boxes():
    assert ("approved: approvedCards.length + narrowerCards.length + widerCards.length,"
            in draw_script())


def test_the_page_empties_the_narrower_box_when_a_new_search_starts():
    assert 'byId("narrower-cards").replaceChildren();' in PAGE


def test_the_page_writes_no_label_words_itself():
    assert "which the database lists under" not in PAGE


def test_the_guide_line_for_doctors_says_each_kind_has_its_own_folded_box():
    assert ("<li><div><b>Wider and narrower diseases.</b> "
            "<span>Shown with a label, each in its own folded box.</span></div></li>") in PAGE
    assert "The wider group sits in a folded box." not in PAGE


def test_the_safety_line_is_on_the_page_word_for_word():
    assert ("For learning and research exploration, not medical advice. "
            "Never start, stop or change any medicine without a doctor.") in " ".join(PAGE.split())


# ---- the written rules ----

def test_decisions_and_the_rule_line_are_written_down():
    decisions = (ROOT / "DECISIONS.md").read_text(encoding="utf-8")
    assert ("- 2026-11-16: The main Approved list holds only medicines approved for this "
            "exact disease. Medicines approved for a narrower disease go in their own folded "
            "box, because the database sometimes files one disease under another.") in decisions
    assert ("- 2026-11-16: The source link on an Approved card shows an approval record "
            "first, then Japan's general list, then any other link.") in decisions
    rules = " ".join((ROOT / "CLAUDE.md").read_text(encoding="utf-8").split())
    assert ("with a label, in its own folded box: one box for narrower diseases, one for the "
            "wider group. It is not a new clue. If it is in trials for this disease, it stays "
            "in In trials too.") in rules


# ---- ADD-ON, Kashish's decision, 16 Nov: nobody misses the boxes ----
#
# 1. Under the two sentences and the doctor line at the top of the Approved
#    tab, one line when the main list has cards AND a box has cards:
#    "N more approved medicines are in the folded boxes below."
#    For one: "1 more approved medicine is in the folded box below."
# 2. Each box's title says "· Tap to open" while closed and "· Tap to close"
#    while open.

ASTHMA = Disease(id="MONDO_0004979", name="asthma")
MORE_MANY = " more approved medicines are in the folded boxes below."
MORE_ONE = "1 more approved medicine is in the folded box below."
TAP_OPEN, TAP_CLOSE = "· Tap to open", "· Tap to close"


def more_line(tabs):
    """The page's rule, worked by hand. None when the line is not shown."""
    boxed = len(tabs.narrower) + len(tabs.wider_group)
    if not tabs.approved or not boxed:
        return None
    return MORE_ONE if boxed == 1 else str(boxed) + MORE_MANY


def test_add_on_the_line_for_each_example(saved_tabs):
    assert more_line(saved_tabs(AMYLOIDOSIS)[1]) == (
        "6 more approved medicines are in the folded boxes below.")
    # Acute lymphoblastic leukemia: both boxes together, 13 and 12.
    assert more_line(saved_tabs(ALL)[1]) == (
        "25 more approved medicines are in the folded boxes below.")
    assert more_line(saved_tabs(PRE_B_ALL)[1]) is None  # main list empty: boxes already open
    asthma = saved_tabs(ASTHMA)[1]
    assert len(asthma.approved) == 70 and asthma.narrower == [] and asthma.wider_group == []
    assert more_line(asthma) is None  # no boxes
    # One card in the boxes: the grammar is for one.
    assert more_line(saved_tabs(PAH)[1]) == MORE_ONE


def test_add_on_the_line_sits_under_the_sentences_and_the_doctor_line_hidden_at_first():
    part = panel()
    top = part[part.index('id="approved-list"'):part.index('id="approved-cards"')]
    assert top.index('class="tab-words"') < top.index('class="doctor-line"') < top.index(
        'id="more-line"')
    start = top.index('id="more-line"')
    tag = top[top.rindex("<", 0, start):top.index(">", start) + 1]
    assert tag.startswith("<p") and " hidden" in tag
    assert PAGE.count('id="more-line"') == 1


def test_add_on_the_page_writes_the_line_with_the_right_grammar_and_rule():
    script = draw_script()
    assert "const boxedCards = narrowerCards.length + widerCards.length;" in script
    assert ('byId("more-line").textContent = boxedCards === 1\n'
            '      ? "1 more approved medicine is in the folded box below."\n'
            '      : boxedCards + " more approved medicines are in the folded boxes below.";'
            ) in script
    # Shown only when the main list has cards and a box has cards.
    assert 'byId("more-line").hidden = !approvedCards.length || !boxedCards;' in script


def test_add_on_each_box_title_says_tap_to_open_after_its_count():
    for box, title in (("narrower", NARROWER_TITLE), ("wider", "Approved for a wider group")):
        start = PAGE.index(f'id="{box}-box"')
        summary = PAGE[PAGE.index("<summary>", start):PAGE.index("</summary>", start)]
        assert summary == (f'<summary>{title} (<span id="{box}-count"></span>) '
                           f'<span data-part="tap">{TAP_OPEN}</span>')


def test_add_on_the_words_follow_the_box_open_or_closed():
    script = PAGE[PAGE.index("function tapWords(box)"):]
    script = script[:script.index("\n  }\n")]
    assert ('part(box, "tap").textContent = box.open ? "· Tap to close" : "· Tap to open";'
            in script)
    # When a person opens or closes a box, and when a search sets it open.
    assert ('for (const id of ["narrower-box", "wider-box"]) '
            'byId(id).addEventListener("toggle", event => tapWords(event.currentTarget));') in PAGE
    draw = draw_script()
    for box in ("narrower-box", "wider-box"):
        assert draw.index(f'byId("{box}").open = ') < draw.index(f'tapWords(byId("{box}"));')
    # The guide's own folds do not get the words.
    assert PAGE.count('<span data-part="tap">') == 2


def test_add_on_the_decision_is_written_down():
    assert ('- 2026-11-16: When medicines sit in a folded box, the top of the Approved tab says '
            'how many, and each box says "Tap to open".') in (
                ROOT / "DECISIONS.md").read_text(encoding="utf-8")


# ---- ADD-ON 2, Kashish's decision, 16 Nov ----

BREAST_CANCER = Disease(id="MONDO_0007254", name="breast cancer")
AL_AMYLOIDOSIS = "MONDO_0019438"  # a child of amyloidosis
EVERY_SAVED_DISEASE = (ALL, AMYLOIDOSIS, ECZEMA, PRE_B_ALL, PAH, ASTHMA, BREAST_CANCER)


def approved_on(neighbours, role, name):
    """The names of the parent or child entries whose list approves this medicine."""
    return [n.disease.name for n in neighbours
            if n.role == role and name in [entry.name for entry in n.approved]]


def test_add_on_2_tafamidis_on_the_own_entry_and_on_a_child_stays_in_the_main_list(saved_tabs):
    with patch("moonlight.fetch._post_json", side_effect=test_family.family_post_json):
        own = fetch.fetch_approved(AMYLOIDOSIS)
        neighbours = engine.fetch_neighbours(AMYLOIDOSIS)
    # The real case: approved on amyloidosis' own entry AND on the child AL amyloidosis.
    assert "TAFAMIDIS" in [entry.name for entry in own]
    assert AL_AMYLOIDOSIS in [n.disease.id for n in neighbours if n.role == "child"]
    assert "AL amyloidosis" in approved_on(neighbours, "child", "TAFAMIDIS")
    _, tabs = saved_tabs(AMYLOIDOSIS)
    tafamidis = test_family.named(tabs.approved, "TAFAMIDIS")  # in the main list, once
    assert tafamidis.label is None
    for box in (tabs.narrower, tabs.wider_group):
        assert tafamidis.id not in [m.id for m in box]
        assert not any("TAFAMIDIS" in name.upper() for m in box for name in (m.name,) + m.forms)


def test_add_on_2_on_the_own_entry_and_on_a_parent_stays_in_the_main_list(saved_tabs):
    own = fetch.fetch_approved(ALL)
    neighbours = engine.fetch_neighbours(ALL)
    # The real case: approved on acute lymphoblastic leukemia's own entry AND
    # on the parent non-Hodgkin lymphoma.
    assert "METHOTREXATE" in [entry.name for entry in own]
    assert "non-Hodgkin lymphoma" in approved_on(neighbours, "parent", "METHOTREXATE")
    _, tabs = saved_tabs(ALL)
    methotrexate = test_family.named(tabs.approved, "METHOTREXATE")
    assert methotrexate.label is None
    for box in (tabs.narrower, tabs.wider_group):
        assert methotrexate.id not in [m.id for m in box]
    # Rituximab: own entry, a parent AND the child chronic lymphocytic leukemia.
    assert approved_on(neighbours, "parent", "RITUXIMAB")
    assert "B-cell chronic lymphocytic leukemia" in approved_on(neighbours, "child", "RITUXIMAB")
    rituximab = test_family.named(tabs.approved, "RITUXIMAB")
    assert rituximab.label is None
    assert rituximab.id not in [m.id for m in tabs.narrower + tabs.wider_group]


def test_add_on_2_nobody_goes_missing(saved_tabs):
    """Main list + narrower box + wider box now == main list + wider box before.

    "Before" is approved_tab_before_2.14.json: what the code on main put in
    the Approved tab for the same saved answers, written down once.
    """
    before = load(SAVED / "approved_tab_before_2.14.json")
    assert set(before) == {disease.id for disease in EVERY_SAVED_DISEASE}
    for disease in EVERY_SAVED_DISEASE:
        was = before[disease.id]
        _, tabs = saved_tabs(disease)
        now = [(m.id, m.name) for m in tabs.approved + tabs.narrower + tabs.wider_group]
        then = [tuple(pair) for pair in was["main_list"] + was["wider_group"]]
        assert len(set(then)) == len(then) > 0, disease.name
        assert len({medicine_id for medicine_id, _ in now}) == len(now), disease.name  # none twice
        assert set(now) == set(then), disease.name  # none lost, none added
        # The wider-group box is exactly as it was, in the same order.
        assert [(m.id, m.name) for m in tabs.wider_group] == [
            tuple(pair) for pair in was["wider_group"]], disease.name
        # The main list and the narrower box together are the old main list.
        assert sorted((m.id, m.name) for m in tabs.approved + tabs.narrower) == sorted(
            tuple(pair) for pair in was["main_list"]), disease.name


def test_add_on_2_breast_cancer_and_asthma_boxes(saved_tabs):
    _, breast = saved_tabs(BREAST_CANCER)
    assert (len(breast.approved), names(breast.narrower), len(breast.wider_group)) == (
        73, ["CYCLOPHOSPHAMIDE ANHYDROUS", "EPIRUBICIN"], 5)
    _, asthma = saved_tabs(ASTHMA)
    assert (len(asthma.approved), asthma.narrower, asthma.wider_group) == (70, [], [])
