"""Ticket 3.11. A trial card links to a trial for THIS disease when one exists.

Kashish, Q18, answer A (25 Nov): "Link each card to the trial for this
disease when one exists, as we did for labels today."

THE RULE (a card on the main In trials list, api._one_source):
  1. the first https link among the card's own records (its proteins'
     report links, strongest protein first, the order the card already
     uses) that is a trial report for this disease;
  2. otherwise the first https link among them, as before.
"A trial report for this disease" (engine.studies_for_this_disease): a
report on the disease's own medicine list, filed under the medicine's own
family, whose own stage is a trial phase. Open Targets files that list
under the disease's id, so the record's disease is the page's disease.
A report whose stage is not said is not a trial report: nothing is guessed.
The card's records are matched by their link, letter for letter.
Nothing else on the card changes: not its place, box, count, stage or words.

Saved answers only, no network:
  fixtures/withdrawal_reports/target_drugs/ENSG00000122194 (PLG's medicines)
  fixtures/labels_read/2.49/disease_drugs/MONDO_0019623 (HAE's own list)
  fixtures/opposite_way_box/ (the whole ADPKD page)
"""

import json
import pathlib
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from moonlight import api, engine, fetch
from moonlight.engine import studies_for_this_disease
from moonlight.records import Disease, Medicine, MedicineForm, Path, Target
from moonlight.rank import Clue

import test_opposite_way_box as adpkd_page

ROOT = pathlib.Path(__file__).resolve().parent.parent
PLG_FILE = ROOT / "fixtures" / "withdrawal_reports" / "target_drugs" / "ENSG00000122194.response.json"
HAE_LIST = ROOT / "fixtures" / "labels_read" / "2.49" / "disease_drugs" / "MONDO_0019623.response.json"
HAE = Disease(id="MONDO_0019623", name="hereditary angioedema")
PLG = Target(id="ENSG00000122194", symbol="PLG", name="plasminogen", score=0.74)

STUDY = "https://clinicaltrials.gov/study/"
PROSTATE = STUDY + "NCT00670345"  # Tranexamic Acid in Urologic Surgery
HAE_STUDY = STUDY + "NCT00500656"  # icatibant versus oral tranexamic acid, HAE

# Every In trials card of the saved ADPKD page whose link moves, in the
# page's order: (id, name, old link, new link). Found by building the page
# with the new rule and the old rule side by side. Each new link is a trial
# report ADPKD's own list holds for that medicine. The first five opened a
# study of another disease (2.49 README, card 1b); the last four opened an
# approval page for another use.
ADPKD_MOVED = (
    ("CHEMBL3349607", "Pasireotide", STUDY + "NCT02527993", STUDY + "NCT01670110"),
    ("CHEMBL1908360", "Everolimus", STUDY + "NCT00154297", STUDY + "NCT02134899"),
    ("CHEMBL413", "Sirolimus", STUDY + "NCT00044720", STUDY + "NCT00346918"),
    ("CHEMBL1823872", "Somatostatin", STUDY + "NCT00863837", STUDY + "NCT00309283"),
    ("CHEMBL1237", "Lisinopril Anhydrous", STUDY + "NCT00000542", STUDY + "NCT00283686"),
    ("CHEMBL1201185", "Lanreotide",
     "https://www.pmda.go.jp/english/review-services/reviews/approved-information/drugs/0001.html",
     STUDY + "NCT01616927"),
    ("CHEMBL1680", "Octreotide",
     "https://www.ema.europa.eu/en/medicines/human/EPAR/mycapssa", STUDY + "NCT01377246"),
    ("CHEMBL1017", "Telmisartan",
     "https://www.ema.europa.eu/en/medicines/human/EPAR/telmisartan-teva", STUDY + "NCT00283686"),
    ("CHEMBL1431", "Metformin",
     "https://www.ema.europa.eu/en/medicines/human/EPAR/avandamet", STUDY + "NCT03764605"),
)


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


# ---- the ticket's example: tranexamic acid on hereditary angioedema ----

@pytest.fixture
def hae_tranexamic():
    """The tranexamic acid card's records and HAE's own list, from saved answers."""
    def saved(body):
        if "targetId" in body["variables"]:
            return load(PLG_FILE)
        return load(HAE_LIST)

    with patch("moonlight.fetch._post_json", side_effect=saved):
        paths = fetch.fetch_paths(HAE, PLG)
        on_list = fetch.fetch_listed_medicines(HAE)
    (path,) = [one for one in paths if one.medicine.name == "TRANEXAMIC ACID"]
    return Clue(paths=(path,)), studies_for_this_disease(on_list)


def test_tranexamic_acid_today_opens_the_prostate_surgery_study(hae_tranexamic):
    clue, _ = hae_tranexamic
    assert len(clue.paths[0].sources) == 506  # the card says 506 reports
    assert api._one_source(clue) == PROSTATE  # the old rule, as on the live page


def test_tranexamic_acid_now_opens_the_hae_study_from_its_own_records(hae_tranexamic):
    clue, studies = hae_tranexamic
    assert studies["CHEMBL877"] == {HAE_STUDY}  # HAE's own list: one trial report
    assert HAE_STUDY in clue.paths[0].sources  # and it is one of the card's records
    assert api._one_source(clue, studies["CHEMBL877"]) == HAE_STUDY
    assert clue.reports == 506  # the count is as it was


# ---- the rule on made-up records ----

def form(family_id, name="Made-up"):
    return MedicineForm(id=family_id, name=name, best_stage="APPROVAL", disease_stage="PHASE_2")


def clue_of(*sources_per_protein):
    medicine = Medicine(name="Made-up", forms=(form("CHEMBL1"),))
    paths = tuple(
        Path(medicine=medicine, target=Target(id=f"ENSG{n}", symbol=f"P{n}", name="p", score=0.9 - n / 10),
             disease=HAE, action_types=("INHIBITOR",), score=0.9 - n / 10, sources=sources)
        for n, sources in enumerate(sources_per_protein)
    )
    return Clue(paths=paths)


def test_a_card_with_no_study_for_this_disease_keeps_its_link():
    clue = clue_of((STUDY + "A", STUDY + "B"))
    assert api._one_source(clue, {STUDY + "Z"}) == STUDY + "A"
    assert api._one_source(clue, set()) == STUDY + "A"
    assert api._one_source(clue) == STUDY + "A"


def test_among_studies_for_this_disease_the_current_order_is_kept():
    clue = clue_of((STUDY + "A", STUDY + "C"), (STUDY + "B",))
    assert api._one_source(clue, {STUDY + "B", STUDY + "C"}) == STUDY + "C"


def test_only_https_links_are_chosen():
    clue = clue_of(("https://example.org/a", "http://clinicaltrials.gov/study/X"))
    assert api._one_source(clue, {"http://clinicaltrials.gov/study/X"}) == "https://example.org/a"


def list_answer(*reports, drug_id="CHEMBL1", parent=None):
    return {"data": {"disease": {"id": HAE.id, "drugAndClinicalCandidates": {"rows": [{
        "maxClinicalStage": "PHASE_2",
        "drug": {"id": drug_id, "name": "MADE-UP", "maximumClinicalStage": "APPROVAL",
                 "drugWarnings": [], "parentMolecule": parent, "childMolecules": []},
        "clinicalReports": list(reports),
    }]}}}}


def studies_from(answer):
    with patch("moonlight.fetch._post_json", return_value=answer):
        return studies_for_this_disease(fetch.fetch_listed_medicines(HAE))


def test_only_trial_reports_on_the_list_count():
    studies = studies_from(list_answer(
        {"url": STUDY + "T", "clinicalStage": "PHASE_2", "source": "ClinicalTrials.gov"},
        {"url": STUDY + "E", "clinicalStage": "EARLY_PHASE_1", "source": "ClinicalTrials.gov"},
        {"url": "https://example.org/label", "clinicalStage": "APPROVAL", "source": "DailyMed"},
        {"url": STUDY + "W", "clinicalStage": "WITHDRAWAL", "source": "ClinicalTrials.gov"},
    ))
    assert studies == {"CHEMBL1": {STUDY + "T", STUDY + "E"}}


def test_a_report_whose_stage_is_not_said_is_not_for_this_disease():
    studies = studies_from(list_answer({"url": STUDY + "T"}, {"url": STUDY + "U", "clinicalStage": None}))
    assert studies == {}


def test_a_tablet_form_s_study_is_filed_under_its_family():
    studies = studies_from(list_answer(
        {"url": STUDY + "T", "clinicalStage": "PHASE_3"},
        drug_id="CHEMBL2", parent={"id": "CHEMBL1", "name": "MADE-UP", "drugWarnings": []}))
    assert studies == {"CHEMBL1": {STUDY + "T"}}


def test_another_medicine_s_study_does_not_count():
    # A study filed under medicine CHEMBL2 is not this card's (CHEMBL1).
    studies = studies_from(list_answer({"url": STUDY + "B", "clinicalStage": "PHASE_3"},
                                       drug_id="CHEMBL2"))
    clue = clue_of((STUDY + "A", STUDY + "B"))
    assert api._one_source(clue, studies.get("CHEMBL1", set())) == STUDY + "A"


# ---- the whole ADPKD page from saved answers: only the links move ----

@pytest.fixture
def adpkd():
    api.forget_visitors()
    with patch("moonlight.fetch._post_json", side_effect=adpkd_page.saved_post_json):
        answer = TestClient(api.app).get("/api/clues", params={"disease_id": adpkd_page.ADPKD})
    assert answer.status_code == 200
    return answer.json()


def test_the_nine_adpkd_cards_open_an_adpkd_study(adpkd):
    by_id = {card["id"]: card for card in adpkd["being_studied"]}
    for medicine_id, name, _old, new in ADPKD_MOVED:
        assert by_id[medicine_id]["medicine"] == name
        assert by_id[medicine_id]["source"] == new, name


def test_nothing_else_on_the_adpkd_page_changes(adpkd):
    """Against the same page with the old rule: only those nine links differ."""
    with patch.object(api, "studies_for_this_disease", return_value={}), \
            patch("moonlight.fetch._post_json", side_effect=adpkd_page.saved_post_json):
        api.forget_answers()
        old = TestClient(api.app).get("/api/clues", params={"disease_id": adpkd_page.ADPKD}).json()
    moved = {medicine_id: (old_link, new) for medicine_id, _, old_link, new in ADPKD_MOVED}
    for card in old["being_studied"]:
        if card["id"] in moved:
            assert card["source"] == moved[card["id"]][0]
            card["source"] = moved[card["id"]][1]
    assert old == adpkd
