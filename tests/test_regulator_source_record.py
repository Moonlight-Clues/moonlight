"""Ticket 2.53. Source record: a regulator's page before a second-hand database page.

Grok's live check of 25 Nov: some Approved cards on the main list open
ttd.idrblab.cn (the Therapeutic Target Database, a second-hand list) as
their Source record, though the same medicine also has an approval report
from a regulator. The approvals are real; the card shows the wrong receipt.

THE RULE (ApprovedMedicine.source_record), each step only if the one before
finds nothing:
  1. a hand-written label (added_from_label, confirmed_from_label): unchanged;
  2. the first approval link whose report's source is in
     fetch.REGULATOR_SOURCES and is not Japan's general list;
  3. as before: the first approval link that is not Japan's general list;
  4. as before: Japan's general list, then the first of sources.
Decided by the report's "source" field, never by the look of the link.
Nothing else changes: no card moves, no grey line changes, no count changes.

Saved files only (fixtures/MONDO_0015924). No network.
"""

import json
import pathlib
from dataclasses import replace
from unittest.mock import patch

import pytest

from moonlight import engine, fetch
from moonlight.engine import ADDED_LINE, JAPAN_LINE, JAPAN_LIST, ApprovedMedicine
from moonlight.records import Disease

ROOT = pathlib.Path(__file__).resolve().parent.parent
PAH_FILES = ROOT / "fixtures" / "MONDO_0015924"
PAH = Disease(id="MONDO_0015924", name="pulmonary arterial hypertension")

TTD = "https://ttd.idrblab.cn/data/drug/details/D0U2JP"
DAILYMED = "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=made-up"
EMA = "https://www.ema.europa.eu/en/medicines/human/EPAR/made-up"
LABEL = "https://www.accessdata.fda.gov/drugsatfda_docs/label/made-up.pdf"


def card(**fields):
    """An Approved card with no paths, only what the test names."""
    base = dict(id="CHEMBL1", name="Made-up", forms=("Made-up",), clue=None,
                listed_sources=())
    base.update(fields)
    return ApprovedMedicine(**base)


# ---- the four checks the ticket asks for ----

def test_ttd_first_and_dailymed_second_shows_dailymed():
    one = card(approval_sources=(TTD, DAILYMED), regulator_sources=(DAILYMED,),
               listed_sources=(TTD, DAILYMED), regulator_record=True)
    assert one.source_record == DAILYMED
    assert one.proof_note is None  # the grey line is as it was


def test_only_ttd_shows_ttd_as_today():
    one = card(approval_sources=(TTD,), listed_sources=(TTD,), regulator_record=False)
    assert one.source_record == TTD
    assert one.proof_note == engine.NO_REGULATOR_LINE  # as before


@pytest.mark.parametrize("field", ["added_from_label", "confirmed_from_label"])
def test_hand_written_labels_still_win(field):
    one = card(approval_sources=(TTD, DAILYMED), regulator_sources=(DAILYMED,),
               listed_sources=(TTD, DAILYMED), regulator_record=True, **{field: LABEL})
    assert one.source_record == LABEL


def test_the_added_card_keeps_its_line():
    one = card(regulator_sources=(DAILYMED,), added_from_label=LABEL)
    assert (one.source_record, one.proof_note) == (LABEL, ADDED_LINE)


def test_japan_only_cards_are_unchanged():
    # Japan's general list is a PMDA report, so it IS a regulator's receipt.
    # It is still never chosen ahead of anything else, and on its own it
    # stays the link and keeps the Japan line.
    one = card(approval_sources=(JAPAN_LIST,), regulator_sources=(JAPAN_LIST,),
               listed_sources=(JAPAN_LIST,), regulator_record=True)
    assert (one.source_record, one.proof_note) == (JAPAN_LIST, JAPAN_LINE)


def test_japan_first_then_ttd_still_shows_ttd():
    # No regulator receipt other than Japan's list: step 3, as before.
    one = card(approval_sources=(JAPAN_LIST, TTD), regulator_sources=(JAPAN_LIST,),
               listed_sources=(JAPAN_LIST, TTD), regulator_record=True)
    assert one.source_record == TTD


def test_the_first_regulator_receipt_wins_when_there_are_two():
    one = card(approval_sources=(TTD, EMA, DAILYMED), regulator_sources=(EMA, DAILYMED))
    assert one.source_record == EMA


def test_only_https_links_are_chosen():
    plain_http = "http://dailymed.nlm.nih.gov/made-up"
    one = card(approval_sources=(TTD, plain_http), regulator_sources=(plain_http,))
    assert one.source_record == TTD


# ---- fetch: the source field decides, not the link's text ----

def reports_answer(*reports):
    """A disease medicine list with one approved medicine and these reports."""
    return {"data": {"disease": {"drugAndClinicalCandidates": {"rows": [{
        "maxClinicalStage": "APPROVAL",
        "drug": {"id": "CHEMBL1", "name": "MADE-UP", "maximumClinicalStage": "APPROVAL",
                 "parentMolecule": None, "childMolecules": [],
                 "mechanismsOfAction": None},
        "clinicalReports": [dict(clinicalStage="APPROVAL", **report) for report in reports],
    }]}}}}


def listed(*reports):
    with patch("moonlight.fetch._post_json", return_value=reports_answer(*reports)):
        (one,) = fetch.fetch_approved(Disease(id="MONDO_X", name="made-up"))
    return one


def test_fetch_carries_the_regulator_links_in_order():
    one = listed({"url": TTD, "source": "TTD"}, {"url": DAILYMED, "source": "DailyMed"},
                 {"url": EMA, "source": "EMA Human Drugs"})
    assert one.approval_sources == (TTD, DAILYMED, EMA)
    assert one.regulator_sources == (DAILYMED, EMA)


def test_the_source_field_decides_not_the_look_of_the_link():
    # A DailyMed-looking link from TTD is not a regulator's; an odd-looking
    # link from FDA is.
    odd = "https://example.org/fda-letter"
    one = listed({"url": DAILYMED, "source": "TTD"}, {"url": odd, "source": "FDA"})
    assert one.regulator_sources == (odd,)


def test_no_source_value_means_no_regulator_link():
    one = listed({"url": DAILYMED}, {"url": EMA, "source": None})
    assert one.regulator_sources == ()


def test_a_trial_report_from_a_regulator_is_not_an_approval_receipt():
    answer = reports_answer({"url": TTD, "source": "TTD"})
    answer["data"]["disease"]["drugAndClinicalCandidates"]["rows"][0]["clinicalReports"].append(
        {"url": DAILYMED, "source": "DailyMed", "clinicalStage": "PHASE_3"})
    with patch("moonlight.fetch._post_json", return_value=answer):
        (one,) = fetch.fetch_approved(Disease(id="MONDO_X", name="made-up"))
    assert one.regulator_sources == ()


# ---- one real card: iloprost for pulmonary arterial hypertension ----

def test_iloprost_for_pah_now_opens_dailymed_from_the_saved_list():
    """Grok named iloprost (PAH). The saved list for PAH has Japan's general
    list, then a TTD approval report, then a DailyMed one."""
    answer = json.loads((PAH_FILES / "disease_drugs.response.json").read_text(encoding="utf-8"))
    with patch("moonlight.fetch._post_json", return_value=answer):
        by_id = {one.id: one for one in fetch.fetch_approved(PAH)}
    iloprost = by_id["CHEMBL494"]
    ttd = "https://ttd.idrblab.cn/data/drug/details/D05ZTH"
    assert iloprost.approval_sources[:2] == (JAPAN_LIST, ttd)
    medicine = engine._approved_medicine("CHEMBL494", None, [iloprost])
    assert replace(medicine, regulator_sources=()).source_record == ttd  # the old rule
    assert medicine.proof_note is None  # it has a regulator record: no grey line
    assert medicine.source_record == ("https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm"
                     "?setid=d3bebc1c-f032-402a-bbc9-aff024276ed1")
