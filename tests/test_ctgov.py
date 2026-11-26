"""Ticket T1. Read one saved ClinicalTrials.gov trial.

moonlight/ctgov.py is handed a study the registry already sent, plus the
name of one medicine. It returns a frozen reading: the status word, the
end line, the phases as sent, and that medicine's role. An observational
study or an expanded-access record is not an interventional trial, so the
answer is None. Nothing here calls the network.

The 15 studies in fixtures/ctgov/ were fetched once on 2026-11-26. See
that folder's README. The words below are the ticket's words, worked out
by hand from those files.
"""

import copy
import dataclasses
import json
import pathlib
from unittest.mock import patch

import pytest

from moonlight.ctgov import Trial, read_trial

ROOT = pathlib.Path(__file__).resolve().parent.parent
FIXTURES = ROOT / "fixtures" / "ctgov"
READER = ROOT / "moonlight" / "ctgov.py"

# The 15 saved studies. Every status word in the ticket's map has one.
SAVED = (
    "NCT06758557",  # recruiting
    "NCT07911579",  # not yet recruiting
    "NCT01841723",  # active, not recruiting
    "NCT05477862",  # invitation only
    "NCT04123561",  # finished; drug in both groups; comparator only
    "NCT01340183",  # paused; placebo
    "NCT00789659",  # withdrawn before starting
    "NCT00645580",  # status unknown
    "NCT02733523",  # no completion date
    "NCT04118153",  # early phase 1
    "NCT02006251",  # stopped early; no phases
    "NCT00188396",  # arms module, but no arm groups
    "NCT03208946",  # sham comparison group
    "NCT03876223",  # observational
    "NCT04921956",  # expanded access
)


def study(nct):
    return json.loads((FIXTURES / f"{nct}.json").read_text(encoding="utf-8"))


@pytest.fixture(autouse=True)
def no_network():
    """The reader is pure. A test that reaches the network fails."""
    with patch("requests.get", side_effect=AssertionError("network used")), \
            patch("requests.post", side_effect=AssertionError("network used")), \
            patch("requests.sessions.Session.request",
                  side_effect=AssertionError("network used")):
        yield


def test_the_saved_studies_are_the_fifteen_registry_answers():
    files = sorted(path.stem for path in FIXTURES.glob("*.json"))
    assert files == sorted(SAVED)
    for nct in SAVED:
        body = study(nct)
        assert set(body) == {"protocolSection"}
        assert body["protocolSection"]["identificationModule"]["nctId"] == nct


# Hand-worked readings. phases are the registry's own tokens, in its order.
# The end line uses the year only. A date that has not happened is the
# registry's type ESTIMATED; the ticket's word for that same date is
# ANTICIPATED. Both mean "Expected to end [year]".
READINGS = [
    ("NCT06758557", "Pemetrexed",
     "Recruiting", "Expected to end 2026", ("PHASE1", "PHASE2"), "Being tested"),
    ("NCT07911579", "SYH2051",
     "Not yet recruiting", "Expected to end 2029", ("PHASE1", "PHASE2"), "Being tested"),
    ("NCT01841723", "Ibrutinib",
     "Running, not recruiting", "Expected to end 2029", ("PHASE2",), "Being tested"),
    ("NCT05477862", "Clinically Designed Improvisatory Music",
     "Invitation only", "Expected to end 2026", ("NA",), "Being tested"),
    ("NCT04123561", "DSP",
     "Finished", "Ended 2022", ("PHASE3",), "Used for comparison"),
    ("NCT04123561", "TLC599",
     "Finished", "Ended 2022", ("PHASE3",), "Role not stated"),
    ("NCT04123561", "Normal Saline",
     "Finished", "Ended 2022", ("PHASE3",), "Used for comparison"),
    ("NCT01340183", "Placebo",
     "Paused", "Expected to end 2011", ("PHASE1",), "Used for comparison"),
    ("NCT01340183", "AZD5099",
     "Paused", "Expected to end 2011", ("PHASE1",), "Being tested"),
    ("NCT00789659", "Negative pressure dressing",
     "Withdrawn before starting", "Ended 2014", ("NA",), "Being tested"),
    ("NCT00645580", "Fluvoxamine",
     "Status unknown", "Expected to end 2009", ("NA",), "Being tested"),
    ("NCT02733523", 'Program "Sentirnos bien" (Feeling well)',
     "Finished", "End date not recorded", ("NA",), "Being tested"),
    ("NCT04118153", "Abatacept",
     "Finished", "Ended 2024", ("EARLY_PHASE1",), "Being tested"),
    ("NCT02006251", "Real-time Instrumentation",
     "Stopped early", "Ended 2014", (), "Being tested"),
    ("NCT02006251", "Standard Total Hip Arthroplasty",
     "Stopped early", "Ended 2014", (), "Role not stated"),
    ("NCT00188396", "Citalopram",
     "Finished", "Ended 2008", ("NA",), "Role not stated"),
    ("NCT03208946", "Low-CML diet",
     "Finished", "Ended 2018", ("NA",), "Used for comparison"),
    ("NCT03208946", "High-CML diet",
     "Finished", "Ended 2018", ("NA",), "Being tested"),
]


@pytest.mark.parametrize("nct,medicine,status,end,phases,role", READINGS)
def test_a_saved_trial_reads_as_worked_out(nct, medicine, status, end, phases, role):
    reading = read_trial(study(nct), medicine)
    assert reading == Trial(
        nct_id=nct, status=status, end=end, phases=phases, role=role)


def test_the_reading_has_only_those_fields_and_is_frozen():
    reading = read_trial(study("NCT01340183"), "AZD5099")
    assert [field.name for field in dataclasses.fields(reading)] == [
        "nct_id", "status", "end", "phases", "role"]
    with pytest.raises(dataclasses.FrozenInstanceError):
        reading.status = "Recruiting"


def test_reading_twice_matches_and_the_study_is_left_unchanged():
    raw = study("NCT04123561")
    snapshot = copy.deepcopy(raw)
    first = read_trial(raw, "TLC599")
    second = read_trial(raw, "TLC599")
    assert first == second
    assert raw == snapshot


def test_an_observational_study_is_left_out():
    assert read_trial(study("NCT03876223"), "anything") is None


def test_an_expanded_access_record_is_left_out():
    # The medicine is named on the record. It is still left out.
    assert read_trial(study("NCT04921956"), "Concizumab") is None


def test_a_missing_study_type_is_left_out():
    raw = study("NCT01841723")
    del raw["protocolSection"]["designModule"]["studyType"]
    assert read_trial(raw, "Ibrutinib") is None


def test_a_missing_status_is_not_the_same_as_an_unknown_status():
    missing = study("NCT01841723")
    del missing["protocolSection"]["statusModule"]["overallStatus"]
    reading = read_trial(missing, "Ibrutinib")
    assert reading.status == "Status not recorded"
    assert reading.end == "Expected to end 2029"
    assert reading.role == "Being tested"

    other = study("NCT01841723")
    other["protocolSection"]["statusModule"]["overallStatus"] = "WITHHELD"
    assert read_trial(other, "Ibrutinib").status == "Status unknown"


def test_the_tickets_word_anticipated_is_an_expected_end():
    # The saved studies say ESTIMATED. The ticket's word is ANTICIPATED.
    # Both are a date that has not happened.
    raw = study("NCT01340183")
    raw["protocolSection"]["statusModule"]["completionDateStruct"]["type"] = "ANTICIPATED"
    assert read_trial(raw, "AZD5099").end == "Expected to end 2011"


def test_a_date_with_no_type_is_not_recorded():
    raw = study("NCT04118153")
    del raw["protocolSection"]["statusModule"]["completionDateStruct"]["type"]
    reading = read_trial(raw, "Abatacept")
    assert reading.end == "End date not recorded"
    assert reading.status == "Finished"


def test_the_name_must_match_the_whole_intervention_name():
    knee = study("NCT04123561")
    assert read_trial(knee, "Saline").role == "Role not stated"
    assert read_trial(knee, "Normal Saline").role == "Used for comparison"
    paused = read_trial(study("NCT01340183"), "Aspirin")
    assert paused.role == "Role not stated"
    assert paused.status == "Paused"
    assert read_trial(study("NCT01340183"), "placebo").role == "Used for comparison"
    assert read_trial(study("NCT01340183"), "PLACEBO").role == "Used for comparison"
    assert read_trial(study("NCT00188396"), "citalopram").role == "Role not stated"
    assert read_trial(study("NCT01340183"), "").role == "Role not stated"
    assert read_trial(study("NCT01340183"), "   ").role == "Role not stated"


def test_another_name_on_the_same_intervention_is_not_used():
    # Matching other names is ticket T5. This reader uses the intervention's
    # own name only.
    raw = study("NCT01340183")
    raw["protocolSection"]["armsInterventionsModule"]["interventions"][0]["otherNames"] = [
        "AZD-5099"]
    assert read_trial(raw, "AZD-5099").role == "Role not stated"
    assert read_trial(raw, "AZD5099").role == "Being tested"


def test_what_is_not_a_study_is_left_out():
    assert read_trial(None, "Ibrutinib") is None
    assert read_trial([], "Ibrutinib") is None
    assert read_trial({}, "Ibrutinib") is None


def test_the_reader_has_no_network_code():
    source = READER.read_text(encoding="utf-8")
    for line in source.splitlines():
        code = line.split("#", 1)[0]
        assert "import requests" not in code
        assert "import urllib" not in code
        assert "import http" not in code
        assert "import socket" not in code
