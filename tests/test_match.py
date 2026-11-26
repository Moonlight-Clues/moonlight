"""Ticket T5. The name matcher: moonlight/match.py.

A trial gives a medicine name and maybe other names. match.match(names, drugs)
gives the ONE Open Targets medicine they mean, or None.

Kashish's answers, 26 Nov 2026:
- Q1: only names from ChEMBL (the record's name, and synonyms and trade names
  whose source is "ChEMBL"). Names from AACT are never used.
- Q2: a name that points to two medicines matches nothing, and a log line names
  both. A medicine and its salt forms count as one medicine.
- Q3: a company code matches only when ChEMBL lists it for exactly one
  medicine. A code on no record matches nothing.
- Q4: a name with a joining mark (/ + , ; and with plus) is a combination, and a
  combination matches nothing.
- Dose words are amounts and units only ("500 mg", "5 mg/kg"). Form words
  ("tablets", "injection") stay, so they stop a match.
- moonlight/trial_names.json is a hand list, empty for now:
  {"<trial name>": {"id": "CHEMBL...", "source": "...", "date": "..."}}.

Drug records are live Open Targets answers saved in fixtures/match_t5/
(26 Nov 2026). No test touches the network.
"""

import json
import logging
import pathlib
from unittest.mock import patch

import pytest

from moonlight import match

ROOT = pathlib.Path(__file__).resolve().parent.parent
SAVED = ROOT / "fixtures" / "match_t5"

PHENYLPROPANOLAMINE = "CHEMBL61006"
METFORMIN = "CHEMBL1431"
IMATINIB = "CHEMBL941"
SACUBITRIL = "CHEMBL3137301"
VALSARTAN = "CHEMBL1069"
ESLICARBAZEPINE_ACETATE = "CHEMBL87992"  # a salt with no parentMolecule (E52)
ESLICARBAZEPINE = "CHEMBL315985"


def _drug(chembl_id):
    answer = json.loads((SAVED / f"{chembl_id}.response.json").read_text(encoding="utf-8"))
    return answer["data"]["drug"]


ALL = [PHENYLPROPANOLAMINE, METFORMIN, IMATINIB, SACUBITRIL, VALSARTAN,
       ESLICARBAZEPINE_ACETATE, ESLICARBAZEPINE]


@pytest.fixture
def drugs():
    return [_drug(chembl_id) for chembl_id in ALL]


@pytest.fixture(autouse=True)
def _no_network_and_empty_hand_list():
    with patch("requests.post", side_effect=AssertionError("network")), \
            patch("requests.get", side_effect=AssertionError("network")), \
            patch.object(match, "_trial_names", return_value={}):
        yield


# --- names that match -------------------------------------------------------

def test_the_record_name_matches(drugs):
    assert match.match(["Metformin"], drugs) == METFORMIN
    assert match.match(["IMATINIB"], drugs) == IMATINIB


def test_case_and_spaces_do_not_matter(drugs):
    assert match.match(["  vAlSaRtAn  "], drugs) == VALSARTAN
    assert match.match(["metformin    hydrochloride"], drugs) == METFORMIN


def test_a_salt_form_name_gives_its_parent_medicine(drugs):
    # PHENYLPROPANOLAMINE HYDROCHLORIDE is a child record of CHEMBL61006.
    assert match.match(["Phenylpropanolamine Hydrochloride"], drugs) == PHENYLPROPANOLAMINE
    assert match.match(["imatinib mesylate"], drugs) == IMATINIB


def test_chembl_synonyms_and_trade_names_match(drugs):
    assert match.match(["Norephedrine"], drugs) == PHENYLPROPANOLAMINE  # synonym
    assert match.match(["Diovan"], drugs) == VALSARTAN                  # trade name
    assert match.match(["Glucophage"], drugs) == METFORMIN              # salt's trade name
    assert match.match(["Gleevec"], drugs) == IMATINIB


def test_amounts_and_units_are_removed(drugs):
    assert match.match(["Metformin 500 mg"], drugs) == METFORMIN
    assert match.match(["imatinib 400mg"], drugs) == IMATINIB
    assert match.match(["Valsartan 1.5 mg/kg"], drugs) == VALSARTAN
    assert match.match(["Glucophage XR 750 mg"], drugs) == METFORMIN
    assert match.match(["valsartan 0.5%"], drugs) == VALSARTAN


def test_a_code_chembl_lists_for_one_medicine_matches(drugs):
    # Q3: early trials often give only the code.
    assert match.match(["STI571"], drugs) == IMATINIB
    assert match.match(["AHU-377"], drugs) == SACUBITRIL
    assert match.match(["CGP 48933"], drugs) == VALSARTAN


def test_one_good_name_among_other_names_is_enough(drugs):
    assert match.match(["Study drug", "imatinib"], drugs) == IMATINIB
    assert match.match(["Gleevec", "STI571", "Imatinib mesylate"], drugs) == IMATINIB


def test_a_bare_string_is_one_name(drugs):
    assert match.match("valsartan", drugs) == VALSARTAN


# --- near misses that must not match -----------------------------------------

def test_one_letter_off_does_not_match(drugs):
    for name in ["Metformim", "imatinab", "valsatran", "sacubitri"]:
        assert match.match([name], drugs) is None, name


def test_form_words_stay_and_stop_a_match(drugs):
    # ticket T5b: drop the form word only when what is left exactly matches
    # one known medicine. "Metformin tablets" is Metformin. A form word on a
    # name that is not a medicine still matches nothing.
    assert match.match(["metformin tablets"], drugs) == METFORMIN
    assert match.match(["valsartan injection"], drugs) == VALSARTAN
    assert match.match(["notarealdrug tablets"], drugs) is None


def test_combination_products_do_not_match(drugs):
    for name in ["sacubitril/valsartan", "Sacubitril + Valsartan", "valsartan and sacubitril",
                 "imatinib; metformin", "valsartan with sacubitril",
                 "metformin plus imatinib", "Glyburide/metformin 5 mg/500 mg"]:
        assert match.match([name], drugs) is None, name
    # ticket T5b: a comma in the main name is still a combination.
    assert match.match(["metformin, imatinib"], drugs) is None


def test_a_combination_matches_nothing_even_when_one_part_is_known(drugs):
    only_valsartan = [_drug(VALSARTAN)]
    assert match.match(["sacubitril/valsartan"], only_valsartan) is None
    assert match.match(["valsartan + amlodipine"], only_valsartan) is None


def test_a_trial_with_a_combination_among_its_names_matches_nothing(drugs, caplog):
    with caplog.at_level(logging.WARNING, logger="moonlight.match"):
        assert match.match(["Entresto", "sacubitril/valsartan", "valsartan"], drugs) is None
    assert "combination" in caplog.text
    # ticket T5b: a comma in an other-name is an alias list. "drug A, drug B"
    # points at two medicines, so it matches nothing, and the log names both.
    caplog.clear()
    with caplog.at_level(logging.WARNING, logger="moonlight.match"):
        assert match.match(["valsartan", "metformin, imatinib"], drugs) is None
    assert METFORMIN in caplog.text and IMATINIB in caplog.text


def test_placebo_does_not_match(drugs):
    for name in ["placebo for metformin", "Metformin placebo", "matching placebo", "Placebo"]:
        assert match.match([name], drugs) is None, name


def test_investigational_drug_does_not_match(drugs):
    assert match.match(["investigational drug"], drugs) is None
    assert match.match(["Investigational Drug", "study drug"], drugs) is None


def test_a_bare_code_on_no_record_does_not_match(drugs):
    # LCZ696 is listed only by AACT, never by ChEMBL (Q1, Q3).
    assert match.match(["LCZ696"], drugs) is None
    assert match.match(["XYZ-1234"], drugs) is None


def test_names_from_aact_are_never_used(drugs):
    for name in ["eucreas", "biguanides", "met", "arb", "tki", "im", "esl", "csti571"]:
        assert match.match([name], drugs) is None, name


def test_component_of_trade_names_are_not_used(drugs):
    assert match.match(["Valsartan component of entresto"], drugs) is None


def test_no_names_or_no_drugs_match_nothing(drugs):
    assert match.match([], drugs) is None
    assert match.match(["", "   "], drugs) is None
    assert match.match(["metformin"], []) is None


# --- one name, two medicines (Q2) ---------------------------------------------

def test_a_name_on_two_medicines_matches_nothing_and_is_logged(drugs, caplog):
    # Without the salt list, eslicarbazepine acetate has no parent, so the
    # trade name Stedesa sits on two medicines.
    with caplog.at_level(logging.WARNING, logger="moonlight.match"):
        assert match.match(["Stedesa"], drugs) is None
    assert ESLICARBAZEPINE in caplog.text and ESLICARBAZEPINE_ACETATE in caplog.text


@pytest.mark.salt_parents
def test_a_medicine_and_its_salt_form_count_as_one(drugs):
    # salt_parents.json: CHEMBL87992 -> CHEMBL315985 (ticket 3.23).
    assert match.match(["Stedesa"], drugs) == ESLICARBAZEPINE
    assert match.match(["Zebinix"], drugs) == ESLICARBAZEPINE
    assert match.match(["Eslicarbazepine acetate"], drugs) == ESLICARBAZEPINE


def test_names_that_point_to_two_medicines_match_nothing(drugs, caplog):
    with caplog.at_level(logging.WARNING, logger="moonlight.match"):
        assert match.match(["imatinib", "metformin"], drugs) is None
    assert IMATINIB in caplog.text and METFORMIN in caplog.text


# --- the hand list trial_names.json -------------------------------------------

def test_the_hand_list_names_a_medicine(drugs):
    row = {"id": IMATINIB, "source": "https://example.org/label", "date": "2026-11-26"}
    with patch.object(match, "_trial_names", return_value={"Gleevec Capsules": row}):
        assert match.match(["gleevec   capsules"], drugs) == IMATINIB


def test_the_hand_list_and_chembl_disagreeing_match_nothing(drugs, caplog):
    row = {"id": METFORMIN, "source": "https://example.org/label", "date": "2026-11-26"}
    with patch.object(match, "_trial_names", return_value={"Gleevec": row}), \
            caplog.at_level(logging.WARNING, logger="moonlight.match"):
        assert match.match(["Gleevec"], drugs) is None
    assert IMATINIB in caplog.text and METFORMIN in caplog.text


def test_the_real_hand_list_is_an_empty_object():
    found = json.loads((ROOT / "moonlight" / "trial_names.json").read_text(encoding="utf-8"))
    assert found == {}


def test_the_hand_list_reader(tmp_path):
    assert match._read_trial_names(ROOT / "moonlight" / "trial_names.json") == {}
    good = tmp_path / "good.json"
    good.write_text(json.dumps({"Gleevec Capsules": {"id": IMATINIB, "source": "s", "date": "d"}}))
    assert match._read_trial_names(good)["Gleevec Capsules"]["id"] == IMATINIB
    for bad in ([], {"x": "CHEMBL941"}, {"x": {"source": "s"}}):
        path = tmp_path / "bad.json"
        path.write_text(json.dumps(bad))
        with pytest.raises(ValueError):
            match._read_trial_names(path)
