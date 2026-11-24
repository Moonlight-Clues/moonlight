"""Ticket 2.17. A quiet line on approvals with no regulator record.

Kashish's decisions, 18 Nov:

- An Approved card whose medicine has no approval report from a regulator
  STAYS. Nothing is hidden and nothing is red.
- It gets one quiet grey line, in the same style and place as the Japan
  line: "The database lists this as approved, but gives no regulator
  record for it."

THE RULE
1. fetch asks for "source" on each report of the disease medicine list.
2. The line is for an Approved card whose medicine (all forms together)
   has NO report with the stage APPROVAL from DailyMed, FDA, EMA Human
   Drugs or PMDA. No APPROVAL report at all counts too.
3. The source is matched exactly. A missing or unknown value is not a
   regulator. Not said is not the same as no. Made clearer by Kashish on
   18 Nov: "not said" is only for a medicine that HAS reports and none of
   them carries a source value (the old saved files): no line. A medicine
   with NO reports at all has no regulator approval report: the line.
4. Approved main list and both folded boxes. Never In trials or New clues.
5. The Japan line and the red warning work as before. Japan line and new
   line on one card: only the Japan line.
6. No card moves, appears or disappears. No count changes. The Source
   record link is chosen as before.

Saved files only: fixtures/no_regulator/ (see its README) and, for the old
answers without "source", fixtures/approval_proof/. No network.
"""

import json
import logging
import pathlib
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from moonlight import api, engine, explain, fetch
from moonlight.engine import JAPAN_LINE, JAPAN_LIST, WRONG_WARNING, sort_into_tabs
from moonlight.fetch import Listed
from moonlight.filter import sort_paths
from moonlight.records import Disease

import test_approval_proof
import test_family
from test_family import made_up_path

ROOT = pathlib.Path(__file__).resolve().parent.parent
SAVED = ROOT / "fixtures" / "no_regulator"
OLD = ROOT / "fixtures" / "approval_proof"
PAGE = (ROOT / "web" / "index.html").read_text(encoding="utf-8")

# Kashish's words, exactly.
LINE = "The database lists this as approved, but gives no regulator record for it."

SARCOIDOSIS = Disease(id="MONDO_0019338", name="sarcoidosis")
HUNTINGTON = Disease(id="MONDO_0007739", name="Huntington disease")
DUCHENNE = Disease(id="MONDO_0010679", name="Duchenne muscular dystrophy")
NARCOLEPSY = Disease(id="MONDO_0021107", name="narcolepsy")
HYPERTHYROIDISM = Disease(id="MONDO_0004425", name="hyperthyroidism")
THE_FIVE = (SARCOIDOSIS, HUNTINGTON, DUCHENNE, NARCOLEPSY, HYPERTHYROIDISM)
# Its own list only, with no whole search: 25 medicines and no reports at all.
FRIEDREICH = Disease(id="MONDO_0100339", name="Friedreich ataxia")

REGULATORS = {"DailyMed", "FDA", "EMA Human Drugs", "PMDA"}
# Every value met in the study of 124 diseases (its REPORT.md, part 2).
MET = REGULATORS | {"TTD", "ATC", "ClinicalTrials.gov", "USAN", "INN"}

COLLAGENASE_ID = "CHEMBL2108709"
METHYLPHENIDATE_ID = "CHEMBL796"
ATALUREN_ID = "CHEMBL256997"


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def saved_post_json(body):
    """Stands in for fetch._post_json with the files in fixtures/no_regulator/."""
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


def whole_search(disease):
    """The whole search for one disease, the way the API does it."""
    tray = engine.find_clues(disease, fetch.fetch_targets(disease, 25))
    return sort_into_tabs(tray, fetch.fetch_approved(disease), fetch.fetch_withdrawn(disease),
                          engine.fetch_neighbours(disease))


@pytest.fixture(scope="module")
def saved_tabs():
    """Each disease's tabs, worked out once."""
    made = {}

    def get(disease):
        if disease.id not in made:
            with patch("moonlight.fetch._post_json", side_effect=saved_post_json):
                made[disease.id] = whole_search(disease)
        return made[disease.id]

    return get


@pytest.fixture(scope="module")
def saved_json():
    """Each disease's /api/clues answer, with the real corrections file."""
    made = {}

    def get(disease):
        if disease.id not in made:
            api.forget_visitors()
            with patch("moonlight.fetch._post_json", side_effect=saved_post_json):
                answer = TestClient(api.app).get("/api/clues", params={"disease_id": disease.id})
            assert answer.status_code == 200
            made[disease.id] = answer.json()
        return made[disease.id]

    return get


def card(medicines, medicine_id):
    (found,) = [medicine for medicine in medicines if medicine.id == medicine_id]
    return found


def item(items, medicine_id):
    (found,) = [entry for entry in items if entry["id"] == medicine_id]
    return found


def rows_of(disease_id, folder=SAVED / "disease_drugs"):
    answer = load(folder / f"{disease_id}.response.json")
    return answer["data"]["disease"]["drugAndClinicalCandidates"]["rows"]


def approval_report_sources(disease_id, family_id):
    """Read straight from the saved list, not through fetch: the source of
    every APPROVAL report on the rows of one medicine and its forms."""
    found = []
    for row in rows_of(disease_id):
        drug = row["drug"]
        parent_molecule = drug["parentMolecule"]
        if (parent_molecule["id"] if parent_molecule else drug["id"]) == family_id:
            found += [report["source"] for report in row["clinicalReports"]
                      if report["clinicalStage"] == "APPROVAL"]
    return found


def with_new_line(medicines):
    return [medicine.name for medicine in medicines if medicine.proof_note == LINE]


def all_cards(tabs):
    return tabs.approved + tabs.narrower + tabs.wider_group


# ---- rule 1: the one extra thing asked about each report ----

def test_the_list_question_asks_for_each_reports_source_by_its_saved_name():
    assert "clinicalReports { url clinicalStage source }" in fetch.DISEASE_DRUGS_QUERY
    assert fetch.DISEASE_DRUGS_QUERY.count("source") == 1
    # The name was read from the saved answers: every saved report has it.
    reports = [report for file in (SAVED / "disease_drugs").glob("*.response.json")
               for row in load(file)["data"]["disease"]["drugAndClinicalCandidates"]["rows"]
               for report in row["clinicalReports"]]
    assert len(reports) == 692
    assert all(set(report) == {"url", "clinicalStage", "source"} for report in reports)
    assert all(report["source"] for report in reports)


def test_the_saved_lists_were_made_with_the_question_fetch_asks_now():
    requests_saved = list((SAVED / "disease_drugs").glob("*.request.json"))
    # 5 own entries with 6 parents and 22 children, and Friedreich ataxia's own.
    assert len(requests_saved) == 34
    for file in requests_saved:
        body = load(file)
        assert body["query"] == fetch.DISEASE_DRUGS_QUERY
        assert body["variables"] == {"diseaseId": file.name.split(".")[0]}


def test_the_question_about_one_protein_is_not_changed():
    assert "clinicalReports { url }" in fetch.TARGET_DRUGS_QUERY
    assert "source" not in fetch.TARGET_DRUGS_QUERY


def test_the_regulators_are_the_four_the_open_targets_team_named():
    assert set(fetch.REGULATOR_SOURCES) == REGULATORS
    assert set(fetch.KNOWN_SOURCES) == MET


def test_every_source_value_in_the_saved_lists_is_one_moonlight_has_met():
    met = {report["source"] for file in (SAVED / "disease_drugs").glob("*.response.json")
           for row in load(file)["data"]["disease"]["drugAndClinicalCandidates"]["rows"]
           for report in row["clinicalReports"]}
    assert met == MET - {"ATC"}  # ATC was met in the study, not in these 34 lists


# ---- rule 2 in fetch: does the family have a regulator's approval report? ----

def test_fetch_says_whether_a_family_has_a_regulators_approval_report():
    listed = {entry.name: entry for entry in fetch.fetch_approved(SARCOIDOSIS)}
    assert listed["COLLAGENASE CLOSTRIDIUM HISTOLYTICUM"].regulator_record is False
    assert listed["PREDNISONE"].regulator_record is True
    listed = {entry.name: entry for entry in fetch.fetch_approved(HUNTINGTON)}
    assert listed["METHYLPHENIDATE"].regulator_record is True  # PMDA is a regulator
    listed = {entry.name: entry for entry in fetch.fetch_approved(DUCHENNE)}
    assert listed["ATALUREN"].regulator_record is False  # no APPROVAL report at all


def test_fetch_agrees_with_the_saved_reports_for_every_approved_family():
    checked = 0
    for file in sorted((SAVED / "disease_drugs").glob("*.response.json")):
        disease = Disease(id=file.name.split(".")[0], name="saved")
        for entry in fetch.fetch_approved(disease):
            sources = approval_report_sources(disease.id, entry.id)
            assert entry.regulator_record is bool(REGULATORS & set(sources)), entry.name
            checked += 1
    assert checked > 40


def made_up_list(reports, more_rows=()):
    """One approved medicine, NEWINE, with these reports on its row."""
    def row(drug_id, name, row_reports, parent_molecule=None):
        return {
            "maxClinicalStage": "APPROVAL",
            "drug": {"id": drug_id, "name": name, "maximumClinicalStage": "APPROVAL",
                     "drugWarnings": [], "parentMolecule": parent_molecule,
                     "childMolecules": []},
            "clinicalReports": row_reports,
        }
    rows = [row("C1", "NEWINE", reports)] + [row(*more) for more in more_rows]
    return {"data": {"disease": {"id": "D1", "drugAndClinicalCandidates": {
        "count": len(rows), "rows": rows}}}}


def report(source, stage="APPROVAL", url="https://example.org/record/1"):
    return {"url": url, "clinicalStage": stage, "source": source}


SOMEONE_SAID = ("C9", "OTHERINE", [report("ClinicalTrials.gov", "PHASE_2")])


def newine(offline, answer):
    offline.side_effect = lambda body: answer
    (entry,) = [entry for entry in fetch.fetch_approved(Disease(id="D1", name="made up"))
                if entry.name == "NEWINE"]
    return entry


@pytest.mark.parametrize("source", sorted(REGULATORS))
def test_an_approval_report_from_each_of_the_four_regulators_counts(offline, source):
    assert newine(offline, made_up_list([report(source)])).regulator_record is True


@pytest.mark.parametrize("source", ["TTD", "ATC", "ClinicalTrials.gov", "USAN", "INN"])
def test_an_approval_report_from_any_other_source_met_does_not_count(offline, source):
    assert newine(offline, made_up_list([report(source)])).regulator_record is False


@pytest.mark.parametrize("source", [
    "dailymed", "DAILYMED", "DailyMed ", " FDA", "fda", "EMA", "EMA Human Drugs.",
    "Pmda", "FDA/EMA", "Health Canada", "",
])
def test_the_source_is_matched_exactly_and_a_new_value_is_never_guessed(offline, source):
    answer = made_up_list([report(source), report("ClinicalTrials.gov", "PHASE_2")])
    assert newine(offline, answer).regulator_record is False


def test_a_report_with_no_source_value_does_not_count_as_a_regulator(offline):
    # Another of its reports has a source, so its sources were said.
    answer = made_up_list([report(None), report("TTD", "PHASE_2")])
    assert newine(offline, answer).regulator_record is False
    answer = made_up_list([{"url": "https://example.org/1", "clinicalStage": "APPROVAL"},
                           report("ClinicalTrials.gov", "PHASE_3")])
    assert newine(offline, answer).regulator_record is False


def test_a_regulators_report_that_is_not_an_approval_does_not_count(offline):
    answer = made_up_list([report("EMA Human Drugs", "WITHDRAWAL"), report("FDA", "PHASE_3"),
                           report("DailyMed", None), report("TTD")])
    assert newine(offline, answer).regulator_record is False


def test_a_medicine_with_no_reports_at_all_has_no_regulator_record(offline):
    assert newine(offline, made_up_list([], [SOMEONE_SAID])).regulator_record is False
    # Also when no other medicine on the list has a report either.
    assert newine(offline, made_up_list([])).regulator_record is False
    silent = ("C9", "OTHERINE", [{"url": "https://example.org/1", "clinicalStage": "PHASE_2"}])
    assert newine(offline, made_up_list([], [silent])).regulator_record is False


def test_all_forms_together_no_form_has_a_report(offline):
    salt = ("C2", "NEWINE HYDROCHLORIDE", [], {"id": "C1", "name": "NEWINE", "drugWarnings": []})
    assert newine(offline, made_up_list([], [salt])).regulator_record is False


def test_example_friedreich_ataxia_two_cards_with_no_reports_at_all_carry_the_line():
    rows = rows_of(FRIEDREICH.id)
    assert len(rows) == 25 and all(row["clinicalReports"] == [] for row in rows)
    listed = fetch.fetch_approved(FRIEDREICH)
    assert [entry.name for entry in listed] == ["IDEBENONE", "OMAVELOXOLONE"]
    assert all(entry.sources == () and entry.approval_sources == () for entry in listed)
    assert [entry.regulator_record for entry in listed] == [False, False]
    tabs = sort_into_tabs({}, listed, fetch.fetch_withdrawn(FRIEDREICH))
    assert [(medicine.name, medicine.proof_note) for medicine in tabs.approved] == [
        ("IDEBENONE", LINE), ("OMAVELOXOLONE", LINE)]
    assert [api._approved_json(medicine)["proof_note"] for medicine in tabs.approved] == [LINE] * 2
    assert tabs.narrower == [] and tabs.wider_group == []


def test_all_forms_together_one_forms_regulator_report_is_enough(offline):
    salt = ("C2", "NEWINE HYDROCHLORIDE", [report("TTD"), report("FDA")],
            {"id": "C1", "name": "NEWINE", "drugWarnings": []})
    assert newine(offline, made_up_list([report("TTD")], [salt])).regulator_record is True


def test_a_regulators_approval_report_counts_even_with_no_link(offline):
    assert newine(offline, made_up_list([report("FDA", url=None)])).regulator_record is True


def test_a_value_moonlight_has_never_met_is_written_in_the_log(offline, caplog):
    answer = made_up_list([report("Health Canada"), report("TTD")])
    with caplog.at_level(logging.WARNING, logger="moonlight.fetch"):
        newine(offline, answer)
    assert "Health Canada" in caplog.text
    assert "TTD" not in caplog.text and "NEWINE" not in caplog.text


def test_values_moonlight_has_met_write_nothing_in_the_log(caplog):
    with caplog.at_level(logging.WARNING, logger="moonlight.fetch"):
        for disease in THE_FIVE:
            fetch.fetch_approved(disease)
    assert "source" not in caplog.text


# ---- rule 3 and EXAMPLE 7: not said is not the same as no ----

def test_example_7_an_answer_with_no_source_anywhere_is_not_said(offline):
    old = load(SAVED / "disease_drugs" / f"{SARCOIDOSIS.id}.response.json")
    for row in old["data"]["disease"]["drugAndClinicalCandidates"]["rows"]:
        for one in row["clinicalReports"]:
            del one["source"]
    offline.side_effect = lambda body: old
    listed = fetch.fetch_approved(SARCOIDOSIS)
    assert len(listed) == 5
    assert all(entry.regulator_record is None for entry in listed)
    tabs = sort_into_tabs({}, listed)
    assert len(tabs.approved) == 5
    assert [medicine.proof_note for medicine in tabs.approved] == [None] * 5


def test_a_medicine_whose_reports_all_have_an_empty_source_is_not_said_either(offline):
    answer = made_up_list([report(None)], [("C9", "OTHERINE", [report(None, "PHASE_2")])])
    assert newine(offline, answer).regulator_record is None
    assert newine(offline, made_up_list([report(None), report("")])).regulator_record is None


def test_not_said_is_about_the_medicines_own_reports_not_the_rest_of_the_list(offline):
    """Kashish, 18 Nov: "not said" is for a medicine that HAS reports and
    none of them carries a source value."""
    bare = {"url": "https://example.org/1", "clinicalStage": "APPROVAL"}
    # Another medicine's reports name their source. NEWINE's own do not.
    assert newine(offline, made_up_list([bare], [SOMEONE_SAID])).regulator_record is None
    assert newine(offline, made_up_list([report(None)], [SOMEONE_SAID])).regulator_record is None
    # One of its own reports names a source: then it was said.
    answer = made_up_list([bare, report("ClinicalTrials.gov", "PHASE_2")])
    assert newine(offline, answer).regulator_record is False
    salt = ("C2", "NEWINE HYDROCHLORIDE", [report("TTD")],
            {"id": "C1", "name": "NEWINE", "drugWarnings": []})
    assert newine(offline, made_up_list([bare], [salt])).regulator_record is False


@pytest.mark.parametrize("disease", [
    test_approval_proof.ALZHEIMER, test_approval_proof.HUNTINGTON, test_approval_proof.ECZEMA,
], ids=lambda disease: disease.name)
def test_example_7_the_old_saved_files_give_no_new_line_on_any_card(disease):
    # The lists saved for ticket 2.13: each report has a link and a stage, no source.
    for file in (OLD / disease.id / "disease_drugs").glob("*.response.json"):
        for row in load(file)["data"]["disease"]["drugAndClinicalCandidates"]["rows"]:
            assert all("source" not in one for one in row["clinicalReports"])
    with patch("moonlight.fetch._post_json", side_effect=test_approval_proof.proof_post_json):
        tabs = test_approval_proof.tabs_for(disease)
    cards = all_cards(tabs)
    assert len(cards) > 5
    assert with_new_line(cards) == []
    assert all(medicine.proof_note in (None, JAPAN_LINE) for medicine in cards)


# ---- the engine: Kashish's EXAMPLES, from the saved files ----

def test_the_line_is_kashishs_words_exactly():
    assert engine.NO_REGULATOR_LINE == LINE
    assert engine.JAPAN_LINE == ("Approved in Japan, according to the database. Moonlight "
                                 "could not find the exact record for this disease.")


def test_example_1_collagenase_has_only_a_ttd_approval_report_and_carries_the_line(saved_tabs):
    assert approval_report_sources(SARCOIDOSIS.id, COLLAGENASE_ID) == ["TTD"]
    tabs = saved_tabs(SARCOIDOSIS)
    collagenase = card(tabs.approved, COLLAGENASE_ID)
    assert collagenase.name == "COLLAGENASE CLOSTRIDIUM HISTOLYTICUM"
    assert collagenase.proof_note == LINE
    assert with_new_line(all_cards(tabs)) == ["COLLAGENASE CLOSTRIDIUM HISTOLYTICUM"]


def test_example_2_prednisone_has_a_dailymed_approval_report_and_no_line(saved_tabs):
    sources = approval_report_sources(SARCOIDOSIS.id, "CHEMBL635")
    assert len(sources) == 41 and set(sources) == {"DailyMed"}
    prednisone = card(saved_tabs(SARCOIDOSIS).approved, "CHEMBL635")
    assert prednisone.name == "PREDNISONE"
    assert prednisone.proof_note is None


def test_example_3_methylphenidate_keeps_the_japan_line_and_gets_no_new_line(saved_tabs):
    assert approval_report_sources(HUNTINGTON.id, METHYLPHENIDATE_ID) == ["PMDA"]
    tabs = saved_tabs(HUNTINGTON)
    methylphenidate = card(tabs.approved, METHYLPHENIDATE_ID)
    assert methylphenidate.approval_sources == (JAPAN_LIST,)
    assert methylphenidate.proof_note == JAPAN_LINE
    assert with_new_line(all_cards(tabs)) == []
    # The red warning: it is on the real corrections list for this disease.
    assert METHYLPHENIDATE_ID in engine.looks_wrong(HUNTINGTON.id)


def test_example_4_ataluren_has_no_approval_report_at_all_and_carries_the_line(saved_tabs):
    assert approval_report_sources(DUCHENNE.id, ATALUREN_ID) == []
    stages = [one["clinicalStage"] for row in rows_of(DUCHENNE.id)
              if row["drug"]["id"] == ATALUREN_ID for one in row["clinicalReports"]]
    assert len(stages) == 14 and "APPROVAL" not in stages
    tabs = saved_tabs(DUCHENNE)
    ataluren = card(tabs.approved, ATALUREN_ID)
    assert ataluren.approval_sources == ()
    assert ataluren.proof_note == LINE
    assert with_new_line(all_cards(tabs)) == ["ATALUREN"]


def test_example_5_a_card_in_the_wider_group_box_carries_the_line_and_its_label(saved_tabs):
    # Aceprometazine: approved only on the parent entry, sleep-wake disorder.
    assert approval_report_sources("MONDO_0003406", "CHEMBL2104054") == ["TTD"]
    tabs = saved_tabs(NARCOLEPSY)
    aceprometazine = card(tabs.wider_group, "CHEMBL2104054")
    assert aceprometazine.proof_note == LINE
    assert aceprometazine.label and "sleep-wake disorder" in aceprometazine.label
    assert with_new_line(tabs.wider_group) == ["ACEPROMETAZINE"]
    assert with_new_line(tabs.narrower) == []
    assert all(medicine.label for medicine in tabs.wider_group + tabs.narrower)


def test_example_5_a_card_in_the_narrower_box_carries_the_line_and_its_label(saved_tabs):
    # Potassium iodide: approved only on the child entry, thyrotoxicosis.
    assert approval_report_sources("MONDO_0010138", "CHEMBL1141") == ["TTD"]
    tabs = saved_tabs(HYPERTHYROIDISM)
    potassium_iodide = card(tabs.narrower, "CHEMBL1141")
    assert potassium_iodide.proof_note == LINE
    assert potassium_iodide.label and "thyrotoxicosis" in potassium_iodide.label
    assert with_new_line(tabs.narrower) == ["POTASSIUM IODIDE"]
    assert with_new_line(tabs.approved) == ["CARBIMAZOLE", "POTASSIUM PERCHLORATE"]


def test_seven_of_the_forty_saved_approved_cards_carry_the_line(saved_tabs):
    counted = {disease.name: (len(with_new_line(all_cards(saved_tabs(disease)))),
                              len(all_cards(saved_tabs(disease)))) for disease in THE_FIVE}
    assert counted == {
        "sarcoidosis": (1, 5), "Huntington disease": (0, 10),
        "Duchenne muscular dystrophy": (1, 8), "narcolepsy": (2, 10),
        "hyperthyroidism": (3, 7),
    }


@pytest.mark.parametrize("disease", THE_FIVE, ids=lambda disease: disease.name)
def test_every_saved_card_follows_the_rule_read_straight_from_the_saved_reports(
        disease, saved_tabs):
    """The line is on a card exactly when the lists naming it as approved
    hold no regulator's approval report for it, and it has no Japan line."""
    tabs = saved_tabs(disease)
    with patch("moonlight.fetch._post_json", side_effect=saved_post_json):
        own = {entry.id for entry in fetch.fetch_approved(disease)}
        neighbours = engine.fetch_neighbours(disease)
    for medicine in all_cards(tabs):
        if medicine.id in own:
            lists = [disease.id]
        else:
            lists = [neighbour.disease.id for neighbour in neighbours
                     if medicine.id in {entry.id for entry in neighbour.approved}]
        assert lists, medicine.name  # every saved card is on a list
        sources = [source for list_id in lists
                   for source in approval_report_sources(list_id, medicine.id)]
        has_regulator = bool(REGULATORS & set(sources))
        if medicine.proof_note == JAPAN_LINE:
            assert has_regulator  # in the saved data the Japan line never hides the new one
        else:
            assert (medicine.proof_note == LINE) is (not has_regulator), medicine.name


# ---- rule 5: the Japan line wins, and the two never meet in the saved data ----

def listed(name, approval_links=(), regulator_record=None, **more):
    links = tuple(approval_links)
    return Listed(id="ID_" + name, name=name, forms=(("ID_" + name, name),),
                  sources=links, approval_sources=links, regulator_record=regulator_record,
                  **more)


def parent(name, approved):
    return engine.Neighbour("parent", Disease(id="P_" + name, name=name), tuple(approved), ())


def child(name, approved):
    return engine.Neighbour("child", Disease(id="C_" + name, name=name), tuple(approved), ())


def only(tabs):
    (medicine,) = all_cards(tabs)
    return medicine


def test_if_both_lines_could_apply_only_the_japan_line_shows():
    tabs = sort_into_tabs({}, [listed("ODDINE", [JAPAN_LIST], regulator_record=False)])
    assert only(tabs).proof_note == JAPAN_LINE


def test_a_regulator_record_and_an_exact_link_no_line():
    tabs = sort_into_tabs({}, [listed("FINEINE", ["https://example.org/1"], True)])
    assert only(tabs).proof_note is None


def test_no_regulator_record_with_an_exact_link_the_new_line():
    tabs = sort_into_tabs({}, [listed("TTDINE", ["https://ttd.example.org/1"], False)])
    assert only(tabs).proof_note == LINE


def test_a_list_entry_that_does_not_say_gives_no_line():
    tabs = sort_into_tabs({}, [listed("OLDINE", ["https://example.org/1"])])
    assert only(tabs).proof_note is None
    tabs = sort_into_tabs({}, [listed("BAREINE")])
    assert only(tabs).proof_note is None


def test_a_boxed_card_on_two_parents_one_regulator_record_is_enough():
    first = parent("first group", [listed("BOXINE", ["https://a.example.org"], False)])
    second = parent("second group", [listed("BOXINE", ["https://b.example.org"], True)])
    assert only(sort_into_tabs({}, [], neighbours=[first, second])).proof_note is None
    assert only(sort_into_tabs({}, [], neighbours=[first])).proof_note == LINE


def test_a_boxed_card_where_one_of_its_lists_does_not_say_gets_no_line():
    first = parent("first group", [listed("BOXINE", ["https://a.example.org"], False)])
    silent = parent("second group", [listed("BOXINE", ["https://b.example.org"], None)])
    assert only(sort_into_tabs({}, [], neighbours=[first, silent])).proof_note is None


def test_a_boxed_card_on_a_child_and_a_parent_with_no_regulator_record_on_either():
    below = child("narrower disease", [listed("BOXINE", ["https://a.example.org"], False)])
    above = parent("wider group", [listed("BOXINE", [], False)])
    tabs = sort_into_tabs({}, [], neighbours=[above, below])
    assert [medicine.name for medicine in tabs.narrower] == ["BOXINE"]
    assert tabs.narrower[0].proof_note == LINE and tabs.narrower[0].label


def test_a_card_found_only_through_a_protein_is_on_no_list_and_gets_no_line():
    tabs = sort_into_tabs(sort_paths([made_up_path("PATHINE", "APPROVAL")]), [])
    assert only(tabs).name == "PATHINE"
    assert only(tabs).regulator_record is None and only(tabs).proof_note is None


# ---- EXAMPLE 6: nobody moves ----

@pytest.mark.parametrize("disease", THE_FIVE, ids=lambda disease: disease.name)
def test_example_6_the_same_cards_in_the_same_order_as_before(disease, saved_json):
    before = load(SAVED / "approved_tab_before_2.17.json")[disease.id]
    data = saved_json(disease)
    assert before["name"] == disease.name == data["disease"]["name"]
    # Ticket 2.32. A card added by hand (valbenazine for Huntington disease) moved
    # from the wider-group box to the main list. It is set aside here.
    # tests/test_approvals_third_batch.py holds that move.
    by_hand = {entry.medicine_id for entry in engine.added_by_hand(disease.id)}
    for box in ("approved", "narrower", "wider_group"):
        now = [one for one in data.get(box, []) if one["id"] not in by_hand]
        as_before = [one for one in before[box] if one["id"] not in by_hand]
        assert [(one["id"], one["medicine"]) for one in now] == [
            (one["id"], one["medicine"]) for one in as_before]
        # The Source record link and the number of reports are as before.
        # Ticket 2.42: a card on the hand-written list of confirmed approvals
        # (dextroamphetamine for narcolepsy) shows its label as source and has
        # no grey line. Its source is set aside here. test_no_regulator_box.py holds it.
        confirmed = {medicine_id for medicine_id, disease_id in engine.confirmed_by_label()
                     if disease_id == disease.id}
        assert [(one["source"], one["reports"]) for one in now if one["id"] not in confirmed] == [
            (one["source"], one["reports"]) for one in as_before if one["id"] not in confirmed]
        for one, was in zip(now, as_before):
            if was["proof_note"]:  # a Japan line stays a Japan line
                assert one["proof_note"] == was["proof_note"] == JAPAN_LINE
            else:  # the only new thing a card can gain is the new line
                assert one.get("proof_note") in (None, LINE)
    # Ticket 2.41. Delandistrogene moxeparvovec for Duchenne muscular dystrophy
    # was added by hand: it left In trials for Approved. Set aside here too.
    # tests/test_label_batch.py holds that move.
    assert [one["id"] for one in data["being_studied"] if one["id"] not in by_hand] == [
        one for one in before["being_studied"] if one not in by_hand]
    assert [one["id"] for one in data["new_clues"]] == before["new_clues"]
    assert data["left_out"] == before["left_out"]


def test_example_6_the_approved_tab_is_still_a_to_z(saved_tabs):
    for disease in THE_FIVE:
        tabs = saved_tabs(disease)
        for cards in (tabs.approved, tabs.narrower, tabs.wider_group):
            names = [medicine.name for medicine in cards]
            assert names == sorted(names, key=str.casefold)


# ---- the API ----

def test_api_the_line_is_sent_word_for_word_in_the_japan_lines_place(saved_json):
    data = saved_json(SARCOIDOSIS)
    noted = [one for one in data["approved"] if "proof_note" in one]
    assert [(one["medicine"], one["proof_note"]) for one in noted] == [
        ("Collagenase Clostridium Histolyticum", LINE)]
    prednisone = item(data["approved"], "CHEMBL635")
    assert "proof_note" not in prednisone and "warning" not in prednisone


def test_api_example_3_methylphenidate_japan_line_and_red_warning_together(saved_json):
    methylphenidate = item(saved_json(HUNTINGTON)["approved"], METHYLPHENIDATE_ID)
    assert methylphenidate["proof_note"] == JAPAN_LINE
    assert methylphenidate["warning"] == WRONG_WARNING


def test_api_example_4_ataluren(saved_json):
    assert item(saved_json(DUCHENNE)["approved"], ATALUREN_ID)["proof_note"] == LINE


def test_api_example_5_both_folded_boxes(saved_json):
    aceprometazine = item(saved_json(NARCOLEPSY)["wider_group"], "CHEMBL2104054")
    assert aceprometazine["proof_note"] == LINE and aceprometazine["label"]
    potassium_iodide = item(saved_json(HYPERTHYROIDISM)["narrower"], "CHEMBL1141")
    assert potassium_iodide["proof_note"] == LINE and potassium_iodide["label"]


def test_api_a_card_may_carry_the_red_warning_and_the_new_line_together(saved_json):
    plain = item(saved_json(SARCOIDOSIS)["approved"], COLLAGENASE_ID)
    entry = {"medicine_id": COLLAGENASE_ID, "disease_id": SARCOIDOSIS.id,
             "date": "2026-11-18", "note": "A doctor confirmed this looks wrong."}
    with patch("moonlight.engine._read_corrections", return_value=[entry]):
        answer = TestClient(api.app).get("/api/clues", params={"disease_id": SARCOIDOSIS.id})
    data = answer.json()
    warned = item(data["approved"], COLLAGENASE_ID)
    assert warned == {**plain, "warning": WRONG_WARNING}
    assert warned["proof_note"] == LINE
    assert [one["id"] for one in data["approved"]] == [
        one["id"] for one in saved_json(SARCOIDOSIS)["approved"]]


@pytest.mark.parametrize("disease", THE_FIVE, ids=lambda disease: disease.name)
def test_example_8_no_card_in_in_trials_or_new_clues_carries_the_line(disease, saved_json):
    data = saved_json(disease)
    clues = data["being_studied"] + data["new_clues"]
    assert clues
    for one in clues:
        assert "proof_note" not in one and "warning" not in one
        assert LINE not in json.dumps(one)


def test_example_8_a_medicine_in_a_box_and_in_trials_has_the_line_on_its_box_card_only():
    below = child("narrower disease", [listed("BOTHINE", ["https://a.example.org"], False)])
    tray = sort_paths([made_up_path("BOTHINE", "PHASE_2")])
    assert [path.medicine.name for path in tray["being_studied"]] == ["BOTHINE"]
    tabs = sort_into_tabs(tray, [], neighbours=[below])
    assert [medicine.name for medicine in tabs.narrower] == ["BOTHINE"]
    assert tabs.narrower[0].proof_note == LINE
    (clue,) = tabs.being_studied
    assert clue.medicine.name == "BOTHINE" and not hasattr(clue, "proof_note")
    found = api._Found(test_family.PAH, tray, [], (), [below])
    assert "proof_note" not in api._clue_json(found.being_studied[0], test_family.PAH)
    assert api._approved_json(found.narrower[0])["proof_note"] == LINE


def test_api_no_approved_card_gains_an_ending_or_an_explanation(saved_json):
    for disease in THE_FIVE:
        data = saved_json(disease)
        for one in data["approved"] + data.get("narrower", []) + data.get("wider_group", []):
            assert "ending" not in one and "explanation" not in one
            assert set(one) <= {"id", "medicine", "forms", "proteins", "reports", "source",
                                "label", "proof_note", "warning",
                                "withdrawal_note",  # ticket 2.31: one more key
                                "limit_note"}  # tickets 2.39 and 2.41: limited cards


# ---- the page: the same slot, the same grey, the engine's words ----

def test_the_page_shows_the_new_line_in_the_japan_lines_slot_and_style():
    # One grey slot on an Approved card. Both lines arrive in "proof_note".
    assert PAGE.count('data-slot="proof-note"') == 1
    script = PAGE[PAGE.index("function approvedCard("):]
    script = script[:script.index("\n  }\n")]
    assert 'slot(el, "proof-note").textContent = medicine.proof_note' in script
    # The words are written by the engine, not by the page.
    assert LINE not in PAGE
    # Quiet and grey: no red anywhere in its style.
    style = PAGE[PAGE.index(".proof-note{"):]
    style = style[:style.index("}")]
    assert "var(--slate)" in style and "#D40000" not in style


def test_the_safety_line_is_still_on_the_page():
    assert ("For learning and research exploration, not medical advice. Never start, "
            "stop or change any medicine without a doctor.") in PAGE
