"""Ticket 3.13 (made smaller by MAIN 4). A trial card opens a study of this
disease from another Open Targets record when its own records have none.

THE RULE (a card on the main In trials list, api._one_source), in order:
  1. the first https link among the card's own records that is a study of
     this disease (unchanged from 3.11);
  2. otherwise the first https study of this disease that the disease's own
     list holds for this medicine (engine.studies_for_this_disease), in
     A to Z order so the page is the same every time;
  3. otherwise the link the card had before, exactly as in 3.11.
No new words, no "no link" case. New-clue cards are not touched.

Saved answers only, no network:
  fixtures/approval_proof/MONDO_0004980/ (the atopic eczema page)
  fixtures/approval_proof/MONDO_0004980/disease_drug_reports/own_MONDO_0004980.response.json
    (the same list with each report's "source"; the page's saved list
    was asked before 3.11 added "source" to the question)
"""

import json
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from moonlight import api, explain

import test_approval_proof as proof
from test_trial_link_this_disease import STUDY, clue_of

ECZEMA = proof.ECZEMA.id
APREMILAST = "CHEMBL514800"
PNEUMONIA = STUDY + "NCT02735707"  # the study apremilast's card opened before
ECZEMA_STUDIES = {STUDY + number for number in (
    "NCT00931242", "NCT01393158", "NCT02087943", "NCT03160248", "NCT04306965")}
REPORTS = proof.PROOF / ECZEMA / "disease_drug_reports" / f"own_{ECZEMA}.response.json"


def _sources():
    """(medicine id, link) -> the report's "source", from the saved reports."""
    rows = proof.load(REPORTS)["data"]["disease"]["drugAndClinicalCandidates"]["rows"]
    return {(row["drug"]["id"], report["url"]): report["source"]
            for row in rows for report in row["clinicalReports"]}


def saved_post_json(body):
    """The saved eczema page. The disease's own list gets each report's
    "source" from the saved reports file, matched by medicine and link."""
    proof._searched["id"] = ECZEMA
    answer = proof.proof_post_json(body)
    variables = body["variables"]
    if ("targetId" not in variables and variables.get("diseaseId") == ECZEMA
            and "drugAndClinicalCandidates" in body["query"]):
        answer = json.loads(json.dumps(answer))  # a copy: the file stays as saved
        sources = _sources()
        for row in answer["data"]["disease"]["drugAndClinicalCandidates"]["rows"]:
            for report in row["clinicalReports"]:
                report["source"] = sources.get((row["drug"]["id"], report["url"]))
    return answer


def eczema_page(studies=None):
    explain.forget_everything()
    api.forget_visitors()
    api.forget_answers()
    with patch("moonlight.fetch._post_json", side_effect=saved_post_json):
        if studies is None:
            answer = TestClient(api.app).get("/api/clues", params={"disease_id": ECZEMA})
        else:
            with patch.object(api, "studies_for_this_disease", return_value=studies):
                answer = TestClient(api.app).get("/api/clues", params={"disease_id": ECZEMA})
    assert answer.status_code == 200
    return answer.json()


@pytest.fixture(scope="module")
def page():
    return eczema_page()


def test_apremilast_on_atopic_eczema_opens_an_atopic_eczema_study(page):
    (card,) = [card for card in page["being_studied"] if card["id"] == APREMILAST]
    assert card["medicine"] == "Apremilast"
    assert card["source"] in ECZEMA_STUDIES
    assert card["source"] == STUDY + "NCT00931242"  # the first of the five, A to Z
    assert card["source"] != PNEUMONIA


def test_apremilast_s_own_records_hold_no_eczema_study_so_3_11_kept_pneumonia():
    old = eczema_page(studies={})  # the page with no studies of this disease known
    (card,) = [card for card in old["being_studied"] if card["id"] == APREMILAST]
    assert card["source"] == PNEUMONIA


def test_a_card_with_no_study_of_its_disease_keeps_its_3_11_link():
    clue = clue_of((STUDY + "A", "https://example.org/label"))
    assert api._one_source(clue, set()) == STUDY + "A"
    assert api._one_source(clue) == STUDY + "A"
    # A study of this disease that is not https is never opened (as in 3.11).
    assert api._one_source(clue, {"http://clinicaltrials.gov/study/X"}) == STUDY + "A"


def test_the_card_s_own_study_still_wins_over_the_list_s():
    clue = clue_of((STUDY + "A", STUDY + "C"))
    assert api._one_source(clue, {STUDY + "B", STUDY + "C"}) == STUDY + "C"


def test_new_clue_cards_keep_their_links(page):
    old = eczema_page(studies={})
    assert [card["source"] for card in page["new_clues"]] == \
        [card["source"] for card in old["new_clues"]]


# ---- a card with no link of its own gains a study of this disease ----

PAH_GAINS = {  # (medicine id) -> (name, the study PAH's own list holds for it)
    "CHEMBL1520": ("Vardenafil", STUDY + "NCT00718952"),
    "CHEMBL2103849": ("Udenafil", STUDY + "NCT01553721"),
}


def pah_page(studies=None):
    """The saved pulmonary arterial hypertension page (fixtures/MONDO_0015924/)."""
    import test_api as pah
    explain.forget_everything()
    api.forget_visitors()
    api.forget_answers()
    with patch("moonlight.fetch._post_json", side_effect=pah.fake_with_the_disease_list):
        with pah.with_saved_targets():
            if studies is None:
                answer = TestClient(api.app).get("/api/clues", params={"disease_id": pah.PAH_ID})
            else:
                with patch.object(api, "studies_for_this_disease", return_value=studies):
                    answer = TestClient(api.app).get("/api/clues",
                                                     params={"disease_id": pah.PAH_ID})
    assert answer.status_code == 200
    return answer.json()


def test_vardenafil_and_udenafil_had_no_link_and_now_open_a_pah_study():
    old = {card["id"]: card for card in pah_page(studies={})["being_studied"]}
    new = {card["id"]: card for card in pah_page()["being_studied"]}
    for medicine_id, (name, study) in PAH_GAINS.items():
        assert new[medicine_id]["medicine"] == name
        assert old[medicine_id]["source"] is None, name  # the card has no link of its own
        assert new[medicine_id]["source"] == study, name
        # Nothing else on the card changes, and no words are added.
        assert dict(new[medicine_id], source=None) == old[medicine_id], name
