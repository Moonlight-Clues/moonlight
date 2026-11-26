"""Ticket T6. Disease search.

The batch searches ClinicalTrials.gov for one disease's own name and for
Open Targets' synonyms. It keeps interventional trials only, and of those
only drug and biological interventions. Placebo is dropped. Each remaining
intervention is stored as a matched medicine (its Open Targets id, from the
T5 matcher) or as found only on ClinicalTrials.gov (the name as listed).
Each disease also stores how many medicines and how many trials that is.

A search whose total is over 2,000 trials is not fetched and not stored.
A synonym that names another Open Targets disease, or that brings back
trials for a different disease, is not used. Both are recorded as stops.

No test touches the network. Saved shapes only.
"""

import json
import pathlib
from unittest.mock import patch

import pytest

from moonlight import disease_search

ROOT = pathlib.Path(__file__).resolve().parent.parent

PSC = "MONDO_0018646"
FRIEDREICH = "MONDO_0100339"
BREAST = "MONDO_0007254"
CYSTIC = "MONDO_0009061"


def disease(disease_id, name, exact=(), related=(), narrow=(), broad=()):
    return {
        "id": disease_id,
        "name": name,
        "synonyms": [
            {"relation": "hasExactSynonym", "terms": list(exact)},
            {"relation": "hasRelatedSynonym", "terms": list(related)},
            {"relation": "hasNarrowSynonym", "terms": list(narrow)},
            {"relation": "hasBroadSynonym", "terms": list(broad)},
        ],
    }


def study(nct, conditions, interventions, study_type="INTERVENTIONAL"):
    """One ClinicalTrials.gov v2 study, only the fields the batch reads."""
    return {"protocolSection": {
        "identificationModule": {"nctId": nct},
        "designModule": {"studyType": study_type},
        "conditionsModule": {"conditions": list(conditions)},
        "armsInterventionsModule": {"interventions": list(interventions)},
    }}


def drug_iv(name, kind="DRUG", other=()):
    row = {"type": kind, "name": name}
    if other:
        row["otherNames"] = list(other)
    return row


def searches_of(disease_name, name_studies, **synonym_studies):
    """term -> the registry's answer. Keys are the words that were searched."""
    out = {disease_name: {"total": len(name_studies), "studies": name_studies}}
    for key, rows in synonym_studies.items():
        out[key] = {"total": len(rows), "studies": rows}
    return out


def catalog(*rows):
    return list(rows)


METFORMIN = {"id": "CHEMBL1431", "name": "METFORMIN", "parentMolecule": None,
             "synonyms": [{"label": "Metformin", "source": "ChEMBL"}], "tradeNames": []}
URSODIOL = {"id": "CHEMBL1551", "name": "URSODIOL", "parentMolecule": None,
            "synonyms": [{"label": "Ursodiol", "source": "ChEMBL"}], "tradeNames": []}


@pytest.fixture(autouse=True)
def _no_network():
    with patch("urllib.request.urlopen", side_effect=AssertionError("network")):
        yield


# --- what is searched -------------------------------------------------------

def test_search_terms_are_the_disease_name_plus_every_synonym():
    one = disease(FRIEDREICH, "Friedreich ataxia",
                  exact=("FA", "Friedreich ataxia", "Friedreich's ataxia"),
                  related=("hereditary spinal ataxia",))
    assert disease_search.search_terms(one) == [
        "Friedreich ataxia", "FA", "Friedreich's ataxia", "hereditary spinal ataxia"]


def test_a_blank_synonym_and_a_repeat_are_not_searched_twice():
    one = disease(PSC, "sclerosing cholangitis",
                  exact=("  ", "sclerosing cholangitis", "Sclerosing   Cholangitis",
                         "primary sclerosing cholangitis"))
    assert disease_search.search_terms(one) == [
        "sclerosing cholangitis", "primary sclerosing cholangitis"]


# --- stops: the two reasons the ticket names --------------------------------

def test_a_synonym_that_is_another_diseases_name_is_a_stop_and_is_not_used():
    """'Fibrocystic disease' is an exact synonym of cystic fibrosis and the
    name of breast fibrocystic disease. It must not be searched in."""
    cystic = disease(CYSTIC, "cystic fibrosis", exact=("Fibrocystic disease", "CF"))
    breast_fibro = disease("MONDO_0005219", "breast fibrocystic disease",
                           exact=("Fibrocystic disease",))
    index = disease_search.exact_index([cystic, breast_fibro])
    name_trials = [study("NCT1", ["cystic fibrosis"], [drug_iv("Ivacaftor")])]
    # The bad synonym's own trials are about the other disease.
    fibro_trials = [study("NCT9", ["Fibrocystic disease of breast"],
                          [drug_iv("Evening primrose oil")])]
    result = disease_search.assemble(
        cystic, searches_of("cystic fibrosis", name_trials,
                            **{"Fibrocystic disease": fibro_trials, "CF": name_trials}),
        catalog(), index, reports=[], parents={})
    assert result["stored"] is True
    assert result["terms_used"] == ["cystic fibrosis", "CF"]
    reasons = {(stop["term"], stop["reason"]) for stop in result["stops"]}
    assert ("Fibrocystic disease", "other_disease") in reasons
    detail = next(s for s in result["stops"] if s["term"] == "Fibrocystic disease"
                  and s["reason"] == "other_disease")
    assert detail["detail"]["other_diseases"] == [
        {"id": "MONDO_0005219", "name": "breast fibrocystic disease"}]
    assert "NCT9" not in result["trial_ids"]


def test_a_synonym_that_brings_trials_of_a_different_disease_is_a_stop():
    """'FA' is an exact synonym of Friedreich ataxia. On the registry it also
    returns Fanconi anemia and colorectal cancer. Those trials do not mention
    Friedreich ataxia, so the synonym is not used."""
    one = disease(FRIEDREICH, "Friedreich ataxia", exact=("FA", "FRDA"))
    index = disease_search.exact_index([one])  # no other disease is named FA
    friedreich = [study("NCT1", ["Friedreich ataxia"], [drug_iv("Omaveloxolone")])]
    fa = friedreich + [
        study("NCT2", ["Fanconi Anemia"], [drug_iv("Androgen")]),
        study("NCT3", ["Colorectal Cancer"], [drug_iv("Fluorouracil")]),
    ]
    frda = friedreich
    result = disease_search.assemble(
        one, searches_of("Friedreich ataxia", friedreich, FA=fa, FRDA=frda),
        catalog(), index, [], {})
    assert ("FA", "extra_trials") in {(s["term"], s["reason"]) for s in result["stops"]}
    assert "FA" not in result["terms_used"]
    assert "FRDA" in result["terms_used"]
    assert result["trial_ids"] == ["NCT1"]
    extra = next(s for s in result["stops"] if s["term"] == "FA")
    assert extra["detail"]["extra_total"] == 2
    assert [row["nct_id"] for row in extra["detail"]["examples"]] == ["NCT2", "NCT3"]
    assert extra["detail"]["examples"][0]["conditions"] == ["Fanconi Anemia"]


def test_a_word_inside_another_word_does_not_count_as_the_disease():
    assert disease_search.mentions("Fanconi Anemia", ["Friedreich ataxia", "FA"]) is False
    assert disease_search.mentions("Friedreich's ataxia", ["Friedreich ataxia", "FA"]) is False
    assert disease_search.mentions("primary sclerosing cholangitis",
                                   ["sclerosing cholangitis"]) is True


def test_a_synonym_that_only_adds_the_same_disease_is_used():
    one = disease(CYSTIC, "cystic fibrosis", exact=("mucoviscidosis",))
    index = disease_search.exact_index([one])
    by_name = [study("NCT1", ["cystic fibrosis"], [drug_iv("Ivacaftor")])]
    by_synonym = by_name + [study("NCT2", ["mucoviscidosis"], [drug_iv("Ivacaftor")])]
    result = disease_search.assemble(
        one, searches_of("cystic fibrosis", by_name, mucoviscidosis=by_synonym),
        catalog(URSODIOL), index, [], {})
    assert result["stops"] == []
    assert result["terms_used"] == ["cystic fibrosis", "mucoviscidosis"]
    assert result["trial_ids"] == ["NCT1", "NCT2"]


def test_a_search_over_2000_trials_stores_nothing_for_that_disease():
    one = disease(BREAST, "breast cancer", exact=("BC", "cancer of breast"))
    index = disease_search.exact_index([one])
    searches = {
        "breast cancer": {"total": 7765, "studies": None},
        "BC": {"total": 108, "studies": [study("NCT9", ["breast cancer"], [drug_iv("X")])]},
        "cancer of breast": {"total": 7765, "studies": None},
    }
    result = disease_search.assemble(one, searches, catalog(), index, [], {})
    assert result["stored"] is False
    assert result["trial_ids"] == []
    assert result["matched"] == []
    assert result["ctgov_only"] == []
    assert result["stops"] == [{
        "term": "breast cancer",
        "reason": "skipped",
        "detail": {"trial_total": 7765},
    }]
    assert disease_search.TRIAL_LIMIT == 2000


def test_a_synonym_over_2000_is_its_own_stop_and_the_name_search_is_kept():
    one = disease(PSC, "sclerosing cholangitis", exact=("wide group",))
    index = disease_search.exact_index([one])
    name_rows = [study("NCT1", ["sclerosing cholangitis"], [drug_iv("Ursodiol")])]
    searches = {
        "sclerosing cholangitis": {"total": 1, "studies": name_rows},
        "wide group": {"total": 2001, "studies": None},
    }
    result = disease_search.assemble(
        one, searches, catalog(URSODIOL), index, [], {})
    assert result["stored"] is True
    assert result["trial_ids"] == ["NCT1"]
    assert result["stops"][0]["term"] == "wide group"
    assert result["stops"][0]["reason"] == "over_2000"
    assert result["stops"][0]["detail"]["trial_total"] == 2001


# --- what is kept from a trial ----------------------------------------------

def test_only_interventional_drug_and_biological_interventions_are_kept():
    one = disease(PSC, "sclerosing cholangitis")
    rows = [
        study("NCT1", ["sclerosing cholangitis"], [
            drug_iv("Ursodiol", "DRUG"),
            drug_iv("A cell", "BIOLOGICAL"),
            drug_iv("A pump", "DEVICE"),
            drug_iv("A diet", "DIETARY_SUPPLEMENT"),
            drug_iv("A combo box", "COMBINATION_PRODUCT"),
        ]),
        study("NCT2", ["sclerosing cholangitis"], [drug_iv("Ursodiol")],
              study_type="OBSERVATIONAL"),
        study("NCT3", ["sclerosing cholangitis"], [drug_iv("Ursodiol")],
              study_type="EXPANDED_ACCESS"),
        study("NCT4", ["sclerosing cholangitis"], [drug_iv("A scan", "DEVICE")]),
    ]
    result = disease_search.assemble(
        one, searches_of("sclerosing cholangitis", rows), catalog(URSODIOL),
        disease_search.exact_index([one]), [], {})
    assert result["trial_ids"] == ["NCT1"]
    # Ursodiol matches. The biological does not, so it is stored as listed.
    assert result["matched"] == [{"medicine_id": "CHEMBL1551", "nct_ids": ["NCT1"]}]
    assert result["ctgov_only"] == [{"name": "A cell", "nct_ids": ["NCT1"]}]


def test_placebo_is_dropped_and_the_trial_stays():
    one = disease(PSC, "sclerosing cholangitis")
    rows = [study("NCT1", ["sclerosing cholangitis"], [
        drug_iv("Ursodiol"),
        drug_iv("Placebo"),
        drug_iv("placebo for ursodiol"),
        drug_iv("Placebo (matched to ELX/TEZ/IVA)"),
        drug_iv("Matching placebo"),
        drug_iv("Placental growth factor", "BIOLOGICAL"),
    ])]
    result = disease_search.assemble(
        one, searches_of("sclerosing cholangitis", rows), catalog(URSODIOL),
        disease_search.exact_index([one]), [], {})
    assert result["trial_ids"] == ["NCT1"]
    listed = [row["name"] for row in result["ctgov_only"]]
    assert listed == ["Placental growth factor"]
    assert result["matched"] == [{"medicine_id": "CHEMBL1551", "nct_ids": ["NCT1"]}]
    assert result["medicine_total"] == 2
    assert result["trial_total"] == 1


def test_a_placebo_only_trial_counts_as_a_trial_and_adds_no_medicine():
    one = disease(PSC, "sclerosing cholangitis")
    rows = [study("NCT1", ["sclerosing cholangitis"], [drug_iv("Placebo oral capsule")])]
    result = disease_search.assemble(
        one, searches_of("sclerosing cholangitis", rows), catalog(),
        disease_search.exact_index([one]), [], {})
    assert result["trial_total"] == 1
    assert result["medicine_total"] == 0
    assert result["matched"] == []
    assert result["ctgov_only"] == []


# --- matched id, or the name as listed --------------------------------------

def test_a_matched_medicine_is_stored_by_its_id_not_by_the_trial_spelling():
    one = disease(PSC, "sclerosing cholangitis")
    rows = [
        study("NCT1", ["sclerosing cholangitis"], [drug_iv("Metformin")]),
        study("NCT2", ["sclerosing cholangitis"], [drug_iv("METFORMIN")]),
    ]
    result = disease_search.assemble(
        one, searches_of("sclerosing cholangitis", rows), catalog(METFORMIN),
        disease_search.exact_index([one]), [], {})
    assert result["matched"] == [{"medicine_id": "CHEMBL1431", "nct_ids": ["NCT1", "NCT2"]}]
    assert result["ctgov_only"] == []
    assert result["medicine_total"] == 1
    assert result["trial_total"] == 2
    assert result["matched_total"] == 1
    assert result["ctgov_only_total"] == 0


def test_an_unmatched_name_is_stored_as_listed_with_its_trials():
    one = disease(FRIEDREICH, "Friedreich ataxia")
    rows = [
        study("NCT1", ["Friedreich ataxia"], [drug_iv("Omaveloxolone")]),
        study("NCT2", ["Friedreich ataxia"], [drug_iv("Omaveloxolone")]),
        study("NCT3", ["Friedreich ataxia"], [drug_iv("omaveloxolone")]),
    ]
    result = disease_search.assemble(
        one, searches_of("Friedreich ataxia", rows), catalog(METFORMIN),
        disease_search.exact_index([one]), [], {})
    assert result["matched"] == []
    assert result["ctgov_only"] == [
        {"name": "Omaveloxolone", "nct_ids": ["NCT1", "NCT2"]},
        {"name": "omaveloxolone", "nct_ids": ["NCT3"]},
    ]
    assert result["medicine_total"] == 2
    assert result["trial_total"] == 3


def test_other_names_are_used_for_matching_and_the_listed_name_is_what_is_stored():
    one = disease(PSC, "sclerosing cholangitis")
    rows = [study("NCT1", ["sclerosing cholangitis"],
                  [drug_iv("Company code 9", other=("ursodiol",))])]
    result = disease_search.assemble(
        one, searches_of("sclerosing cholangitis", rows), catalog(URSODIOL),
        disease_search.exact_index([one]), [], {})
    assert result["matched"] == [{"medicine_id": "CHEMBL1551", "nct_ids": ["NCT1"]}]
    assert result["ctgov_only"] == []


def test_a_combination_is_not_matched_and_is_stored_as_listed():
    one = disease(CYSTIC, "cystic fibrosis")
    rows = [study("NCT1", ["cystic fibrosis"], [
        drug_iv("ELX/TEZ/IVA"),
        drug_iv("Tezacaftor/Ivacaftor"),
        drug_iv("metformin and ursodiol"),
    ])]
    result = disease_search.assemble(
        one, searches_of("cystic fibrosis", rows), catalog(METFORMIN, URSODIOL),
        disease_search.exact_index([one]), [], {})
    assert result["matched"] == []
    assert [row["name"] for row in result["ctgov_only"]] == [
        "ELX/TEZ/IVA", "Tezacaftor/Ivacaftor", "metformin and ursodiol"]


def test_two_medicines_in_one_intervention_match_nothing_and_the_listed_name_is_kept():
    one = disease(PSC, "sclerosing cholangitis")
    alpha = {"id": "CHEMBL1", "name": "ALPHA", "parentMolecule": None,
             "synonyms": [], "tradeNames": []}
    beta = {"id": "CHEMBL2", "name": "BETA", "parentMolecule": None,
            "synonyms": [], "tradeNames": []}
    rows = [study("NCT1", ["sclerosing cholangitis"],
                  [drug_iv("ALPHA", other=("BETA",))])]
    result = disease_search.assemble(
        one, searches_of("sclerosing cholangitis", rows), catalog(alpha, beta),
        disease_search.exact_index([one]), [], {})
    assert result["matched"] == []
    assert result["ctgov_only"] == [{"name": "ALPHA", "nct_ids": ["NCT1"]}]


# --- before counts, from Open Targets, and a file that re-runs the same -----

def test_before_counts_are_the_medicines_and_trials_open_targets_already_links():
    reports = [
        {"id": "nct00000001", "source": "ClinicalTrials.gov",
         "drugs": [{"drugId": "CHEMBL10"}], "diseases": [{"diseaseId": PSC}]},
        {"id": "nct00000001", "source": "ClinicalTrials.gov",
         "drugs": [{"drugId": "CHEMBL11"}], "diseases": [{"diseaseId": PSC}]},
        {"id": "nct00000002", "source": "ClinicalTrials.gov",
         "drugs": [{"drugId": "CHEMBL10"}], "diseases": [{"diseaseId": PSC}]},
        {"id": "nct00000003", "source": "ClinicalTrials.gov",
         "drugs": [{"drugId": "CHEMBL12"}], "diseases": [{"diseaseId": "MONDO_OTHER"}]},
        {"id": "nct00000004", "source": "TTD",
         "drugs": [{"drugId": "CHEMBL13"}], "diseases": [{"diseaseId": PSC}]},
    ]
    # CHEMBL10 and CHEMBL11 are salt forms of one medicine. CHEMBL12 is another.
    parents = {"CHEMBL10": "CHEMBL1", "CHEMBL11": "CHEMBL1"}
    assert disease_search.before_counts(reports, PSC, parents) == {"medicines": 1, "trials": 2}


def test_two_writes_of_the_same_result_are_the_same_bytes(tmp_path):
    one = disease(PSC, "sclerosing cholangitis", exact=("primary sclerosing cholangitis",))
    rows = [
        study("NCT2", ["sclerosing cholangitis"], [drug_iv("Omaveloxolone")]),
        study("NCT1", ["sclerosing cholangitis"], [drug_iv("Ursodiol"), drug_iv("Placebo")]),
    ]
    result = disease_search.assemble(
        one, searches_of("sclerosing cholangitis", rows,
                         **{"primary sclerosing cholangitis": rows}),
        catalog(URSODIOL), disease_search.exact_index([one]),
        reports=[{"id": "nct00000001", "source": "ClinicalTrials.gov",
                  "drugs": [{"drugId": "CHEMBL1551"}], "diseases": [{"diseaseId": PSC}]}],
        parents={"CHEMBL1551": "CHEMBL1551"})
    first = tmp_path / "a.sqlite"
    second = tmp_path / "b.sqlite"
    disease_search.write_sqlite(first, [result], "2026-11-26")
    disease_search.write_sqlite(second, [result], "2026-11-26")
    assert first.read_bytes() == second.read_bytes()
    saved = disease_search.read_sqlite(first)
    assert saved["diseases"][0]["disease_id"] == PSC
    assert saved["diseases"][0]["trial_total"] == 2
    assert saved["diseases"][0]["medicine_total"] == 2
    assert saved["diseases"][0]["before_trials"] == 1
    assert saved["diseases"][0]["before_medicines"] == 1
    matched = [row for row in saved["found"] if row["kind"] == "matched"]
    listed = [row for row in saved["found"] if row["kind"] == "ctgov_only"]
    assert matched == [{"disease_id": PSC, "kind": "matched", "medicine_id": "CHEMBL1551",
                        "name": "", "nct_ids": ["NCT1"]}]
    assert listed == [{"disease_id": PSC, "kind": "ctgov_only", "medicine_id": "",
                       "name": "Omaveloxolone", "nct_ids": ["NCT2"]}]
    assert saved["meta"]["run_date"] == "2026-11-26"
    assert saved["meta"]["ot_release"] == "26.09"


def test_a_second_run_reads_the_cache_and_writes_the_same_file(tmp_path):
    import importlib.util

    path = ROOT / "scripts" / "build_disease_search.py"
    spec = importlib.util.spec_from_file_location("build_disease_search_t6", path)
    script = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(script)

    (tmp_path / "diseases.json").write_text(json.dumps([
        disease(PSC, "sclerosing cholangitis")]), encoding="utf-8")
    (tmp_path / "drugs.json").write_text(json.dumps([URSODIOL]), encoding="utf-8")
    (tmp_path / "reports.json").write_text("[]", encoding="utf-8")
    cache = tmp_path / "cache"
    calls = {"n": 0}

    def fake_get(url):
        calls["n"] += 1
        assert "clinicaltrials.gov" in url
        body = {"totalCount": 1, "studies": [
            study("NCT1", ["sclerosing cholangitis"], [drug_iv("Ursodiol")])]}
        return 200, json.dumps(body).encode()

    argv = ["--diseases", PSC,
            "--disease-file", str(tmp_path / "diseases.json"),
            "--drug-file", str(tmp_path / "drugs.json"),
            "--report-file", str(tmp_path / "reports.json"),
            "--cache", str(cache), "--run-date", "2026-11-26"]
    first = tmp_path / "one.sqlite"
    second = tmp_path / "two.sqlite"
    assert script.main(argv + ["--out", str(first)], get=fake_get,
                       sleep=lambda _seconds: None, gap=0) == 0
    assert calls["n"] >= 1
    used = calls["n"]

    def offline_get(_url):
        raise AssertionError("a re-run must read the cache")

    assert script.main(argv + ["--out", str(second), "--offline"], get=offline_get,
                       sleep=lambda _seconds: None, gap=0) == 0
    assert calls["n"] == used
    assert first.read_bytes() == second.read_bytes()
    saved = disease_search.read_sqlite(first)
    assert saved["diseases"][0]["trial_total"] == 1
    assert saved["found"][0]["medicine_id"] == "CHEMBL1551"


def test_a_medicine_off_the_disease_list_matches_from_the_whole_catalogue():
    """Erlotinib and fenofibrate are not on this disease's trial list.
    The catalogue is every Open Targets medicine, so the bracket name and
    "(drug)" still match."""
    one = disease(PSC, "sclerosing cholangitis")
    erlotinib = {"id": "CHEMBL553", "name": "ERLOTINIB", "parentMolecule": None,
                 "synonyms": [{"label": "Erlotinib", "source": "ChEMBL"}],
                 "tradeNames": [{"label": "Tarceva", "source": "ChEMBL"}]}
    fenofibrate = {"id": "CHEMBL672", "name": "FENOFIBRATE", "parentMolecule": None,
                   "synonyms": [{"label": "Fenofibrate", "source": "ChEMBL"}],
                   "tradeNames": []}
    rows = [study("NCT1", ["sclerosing cholangitis"], [
        drug_iv("Erlotinib (Tarceva)"), drug_iv("Fenofibrate (drug)")])]
    result = disease_search.assemble(
        one, searches_of("sclerosing cholangitis", rows),
        catalog(erlotinib, fenofibrate), disease_search.exact_index([one]), [], {})
    assert result["matched"] == [
        {"medicine_id": "CHEMBL553", "nct_ids": ["NCT1"]},
        {"medicine_id": "CHEMBL672", "nct_ids": ["NCT1"]},
    ]
    assert result["ctgov_only"] == []
    assert result["before_medicines"] == 0


def test_the_four_synonyms_main_5_kept_out_stay_out():
    """cholangitis, sclerosing; FA; CF; Fibrocystic disease. MAIN 5, 26 Nov 2026."""
    psc = disease(PSC, "sclerosing cholangitis", exact=("cholangitis, sclerosing",))
    psc_name = [study("NCT1", ["sclerosing cholangitis"], [drug_iv("Ursodiol")])]
    psc_extra = psc_name + [study("NCT00929266", ["Healthy Volunteers"], [drug_iv("X")])]
    psc_result = disease_search.assemble(
        psc, searches_of("sclerosing cholangitis", psc_name,
                         **{"cholangitis, sclerosing": psc_extra}),
        catalog(URSODIOL), disease_search.exact_index([psc]), [], {})
    assert "cholangitis, sclerosing" not in psc_result["terms_used"]
    assert ("cholangitis, sclerosing", "extra_trials") in {
        (stop["term"], stop["reason"]) for stop in psc_result["stops"]}

    friedreich = disease(FRIEDREICH, "Friedreich ataxia", exact=("FA",))
    fr_name = [study("NCT1", ["Friedreich ataxia"], [drug_iv("Omaveloxolone")])]
    fr_extra = fr_name + [study("NCT00243399", ["Fanconi Anemia"], [drug_iv("Androgen")])]
    fr_result = disease_search.assemble(
        friedreich, searches_of("Friedreich ataxia", fr_name, FA=fr_extra),
        catalog(), disease_search.exact_index([friedreich]), [], {})
    assert "FA" not in fr_result["terms_used"]

    cystic = disease(CYSTIC, "cystic fibrosis", exact=("CF", "Fibrocystic disease"))
    breast = disease("MONDO_0005219", "breast fibrocystic disease", exact=("Fibrocystic disease",))
    cf_name = [study("NCT1", ["cystic fibrosis"], [drug_iv("Ivacaftor")])]
    cf_extra = cf_name + [study("NCT00005036", ["Colorectal Cancer"], [drug_iv("Fluorouracil")])]
    fibro = [study("NCT05717894", ["Fibrocystic Breast Disease"], [drug_iv("Evening primrose oil")])]
    cf_result = disease_search.assemble(
        cystic, searches_of("cystic fibrosis", cf_name, CF=cf_extra, **{"Fibrocystic disease": fibro}),
        catalog(), disease_search.exact_index([cystic, breast]), [], {})
    assert "CF" not in cf_result["terms_used"]
    assert "Fibrocystic disease" not in cf_result["terms_used"]
    reasons = {(stop["term"], stop["reason"]) for stop in cf_result["stops"]}
    assert ("CF", "extra_trials") in reasons
    assert ("Fibrocystic disease", "other_disease") in reasons


def test_the_check_diseases_are_the_four_named_in_the_ticket():
    """PSC, one rare disease, one common cancer, one disease with many
    combination products. The ids are Open Targets 26.09."""
    assert disease_search.CHECK_DISEASES == (
        (PSC, "sclerosing cholangitis"),
        (FRIEDREICH, "Friedreich ataxia"),
        (BREAST, "breast cancer"),
        (CYSTIC, "cystic fibrosis"),
    )
