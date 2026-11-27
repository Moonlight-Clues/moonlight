"""Ticket 3.24 (MAIN 5, 27 Nov). Salt-form loose ends after 3.23.

A merged salt card keeps the best source among its forms and carries the
medicine's name.

1. Name. Each salt_parents.json row now holds "parent_name": the medicine's
   name as its label writes it. When no Open Targets row names the parent,
   the card is named parent_name, never the salt's name.
2. Forms. The forms belong to the medicine, not the page (MAIN 5): an
   Approved-tab card holding a listed salt lists the parent too, named
   parent_name, even when the list it came from has no row for the parent.
3. Source record, Approved-tab cards only (MAIN 5). A regulator label from
   any form (decided by the report's "source" field) beats a secondary
   source. If the parent and a salt both have one, the parent's own is kept.
   Hand lists (confirmed.json, source_overrides.json) still win over both.
   A clue card's link is a research link, not proof of approval: Eplontersen
   and Eslicarbazepine clue cards stay as they are.
4. The entries' date is the day they were made and merged: 2026-11-26.

Out of scope (MAIN 5): new salt pairs, which box a card sits in, the
In-trials Ixazomib card that left the AL amyloidosis page in 3.23 (its own
ticket), and Tofogliflozin Anhydrous (Open Targets' own, accurate name).

Saved answers only, no network.
"""

import copy
import json
import pathlib
from dataclasses import replace
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from moonlight import api, engine, fetch
from moonlight.fetch import fetch_approved, fetch_listed_medicines, fetch_withdrawn
from moonlight.filter import sort_paths
from moonlight.records import Disease

import old_flag_saved
import test_approvals_by_hand as by_hand
import test_approvals_third_batch as huntington_files
import test_givosiran_2_61 as givosiran
import test_tafamidis_warning as amyloidosis_files

ROOT = pathlib.Path(__file__).resolve().parent.parent
pytestmark = pytest.mark.salt_parents  # the real list

LIST_FILE = ROOT / "moonlight" / "salt_parents.json"
BEFORE = ROOT / "fixtures" / "salt_3_24" / "before"

AL_AMYLOIDOSIS = "MONDO_0019438"
AMYLOIDOSIS = "MONDO_0019065"
AHP = "Orphanet_95157"
HUNTINGTON = "MONDO_0007739"
ESSENTIAL_TREMOR = "MONDO_0003233"
T2D = "MONDO_0005148"
MYASTHENIA_GRAVIS = "MONDO_0009688"

IXAZOMIB, IXAZOMIB_CITRATE = "CHEMBL2141296", "CHEMBL3545432"
GIVOSIRAN, GIVOSIRAN_SODIUM = "CHEMBL4297760", "CHEMBL4594265"
EPLONTERSEN = "CHEMBL4594334"
ESLICARBAZEPINE = "CHEMBL315985"
TOFOGLIFLOZIN_ANHYDROUS = "CHEMBL2110731"
ZILUCOPLAN = "CHEMBL4298207"
ZILBRYSQ_EMA = "https://www.ema.europa.eu/en/medicines/human/EPAR/zilbrysq"  # the parent's own
ZILBRYSQ_FDA = "https://www.accessdata.fda.gov/drugsatfda_docs/label/2023/216834s000lbl.pdf"  # the salt's

# Each parent's name, as its label (the row's own source) writes it.
PARENT_NAMES = {
    "CHEMBL4594265": "Givosiran",
    "CHEMBL4297536": "Patisiran",
    "CHEMBL4594335": "Eplontersen",
    "CHEMBL5095303": "Vutrisiran",
    "CHEMBL5315048": "Zilucoplan",
    "CHEMBL3707226": "Defibrotide",
    "CHEMBL4298005": "Mitiglinide",
    "CHEMBL4297658": "Ipragliflozin",
    "CHEMBL3545432": "Ixazomib",
    "CHEMBL87992": "Eslicarbazepine",
}

CARD_PARTS = ("approved", "narrower", "wider_group", "being_studied", "new_clues",
              "more_in_trials", "new_in_trials")


def load(file):
    return json.loads(file.read_text(encoding="utf-8"))


def real_list():
    return load(LIST_FILE)


# ---- how the 3.23 pages are built (the same builders made fixtures/salt_3_24/before) ----

def _no_network():
    return [patch("requests.request", side_effect=AssertionError("network used")),
            patch("requests.post", side_effect=AssertionError("network used")),
            patch("requests.get", side_effect=AssertionError("network used")),
            patch("requests.sessions.Session.request", side_effect=AssertionError("network used"))]


def _api_page(disease_id, post_json):
    """What /api/clues sends, from saved answers and the REAL hand-written files."""
    api.forget_visitors()
    api.forget_answers()
    guards = _no_network() + [patch("moonlight.fetch._post_json", side_effect=post_json)]
    for guard in guards:
        guard.start()
    try:
        response = TestClient(api.app).get("/api/clues", params={"disease_id": disease_id})
    finally:
        for guard in guards:
            guard.stop()
        api.forget_visitors()
        api.forget_answers()
    assert response.status_code == 200
    return response.json()


def _tabs(disease_id, post_json):
    disease = Disease(disease_id, "the disease")
    guards = _no_network() + [patch("moonlight.fetch._post_json", side_effect=post_json)]
    for guard in guards:
        guard.start()
    try:
        return engine.sort_into_tabs(
            sort_paths([]), fetch_approved(disease), withdrawn_listed=fetch_withdrawn(disease),
            on_list=fetch_listed_medicines(disease), by_hand=engine.added_by_hand(disease_id))
    finally:
        for guard in guards:
            guard.stop()


def _list_page(disease_id, post_json):
    """The Approved-tab cards built from the disease's own list alone (no proteins)."""
    tabs = _tabs(disease_id, post_json)
    return {name: [api._approved_json(m) for m in getattr(tabs, name)]
            for name in ("approved", "narrower", "wider_group")}


PAGES = {
    AL_AMYLOIDOSIS: lambda: _api_page(AL_AMYLOIDOSIS, amyloidosis_files._from_the_saved_files),
    HUNTINGTON: lambda: _api_page(HUNTINGTON, huntington_files.saved_post_json),
    ESSENTIAL_TREMOR: lambda: _api_page(ESSENTIAL_TREMOR, by_hand.saved_post_json),
    T2D: lambda: _api_page(T2D, old_flag_saved.saved_post_json),
    MYASTHENIA_GRAVIS: lambda: _list_page(MYASTHENIA_GRAVIS, by_hand.saved_post_json),
    AHP: lambda: _list_page(AHP, givosiran.saved_post_json),
    AMYLOIDOSIS: lambda: _list_page(AMYLOIDOSIS, amyloidosis_files._from_the_saved_files),
}


@pytest.fixture(scope="module")
def pages():
    return {disease_id: build() for disease_id, build in PAGES.items()}


def cards(page):
    """{(part, id): card} for every card on the page."""
    found = {}
    for part in CARD_PARTS:
        for card in page.get(part) or []:
            found[(part, card.get("id"))] = card
    return found


# ---- the hand list ----

def test_every_row_has_parent_name_as_the_label_writes_it():
    found = real_list()
    assert {salt: row["parent_name"] for salt, row in found.items()} == PARENT_NAMES
    for salt, row in found.items():
        assert set(row) - {"id"} == {"parent", "parent_name", "source", "date"}, salt  # id is the permanent correction number


def test_every_row_is_dated_the_day_it_was_made_and_merged():
    assert {row["date"] for row in real_list().values()} == {"2026-11-26"}


def test_the_engine_refuses_a_row_without_parent_name(tmp_path, monkeypatch):
    # This file is marked salt_parents, so fetch._salt_parents is the real reader.
    bad = tmp_path / "salt_parents.json"
    bad.write_text(json.dumps({"CHEMBL1": {"parent": "CHEMBL2", "source": "https://x",
                                           "date": "2026-11-26"}}), encoding="utf-8")
    monkeypatch.setattr(fetch, "SALT_PARENTS_FILE", bad)
    monkeypatch.setattr(fetch, "_SALT_PARENTS", None)
    with pytest.raises(ValueError):
        fetch._salt_parents()


# ---- Example: Ixazomib on AL amyloidosis ----

def test_ixazomib_on_al_amyloidosis_is_titled_ixazomib_with_both_forms(pages):
    card = cards(pages[AL_AMYLOIDOSIS])[("wider_group", IXAZOMIB)]
    assert card["medicine"] == "Ixazomib"
    assert card["forms"] == ["Ixazomib", "Ixazomib Citrate"]


def test_ixazomib_keeps_its_box_and_source(pages):
    before = cards(load(BEFORE / f"{AL_AMYLOIDOSIS}.json"))[("wider_group", IXAZOMIB)]
    after = cards(pages[AL_AMYLOIDOSIS])[("wider_group", IXAZOMIB)]
    assert {k: v for k, v in after.items() if k not in ("medicine", "forms")} == \
        {k: v for k, v in before.items() if k not in ("medicine", "forms")}


def test_the_ixazomib_family_on_the_amyloidosis_list_is_named_after_the_parent():
    with patch("moonlight.fetch._post_json", side_effect=amyloidosis_files._from_the_saved_files):
        found = {listed.id: listed for listed in fetch_approved(Disease(AMYLOIDOSIS, "d"))}
    assert found[IXAZOMIB].name == "Ixazomib"
    assert found[IXAZOMIB].forms == ((IXAZOMIB, "Ixazomib"), (IXAZOMIB_CITRATE, "IXAZOMIB CITRATE"))


# ---- Name: a salt whose parent has no row is named parent_name ----

def test_givosiran_sodium_alone_is_named_givosiran_never_the_salt():
    answer = copy.deepcopy(givosiran.saved_post_json(
        {"query": "", "variables": {"diseaseId": AHP}}))
    rows = answer["data"]["disease"]["drugAndClinicalCandidates"]["rows"]
    answer["data"]["disease"]["drugAndClinicalCandidates"]["rows"] = [
        row for row in rows if row["drug"]["id"] != GIVOSIRAN]
    with patch("moonlight.fetch._post_json", return_value=answer):
        found = {listed.id: listed for listed in fetch_approved(Disease(AHP, "d"))}
    assert found[GIVOSIRAN].name == "Givosiran"
    assert found[GIVOSIRAN].forms == ((GIVOSIRAN, "Givosiran"), (GIVOSIRAN_SODIUM, "GIVOSIRAN SODIUM"))


def test_when_the_parent_has_a_row_its_own_name_and_form_are_used():
    with patch("moonlight.fetch._post_json", side_effect=givosiran.saved_post_json):
        found = {listed.id: listed for listed in fetch_approved(Disease(AHP, "d"))}
    assert found[GIVOSIRAN].name == "GIVOSIRAN"
    assert [name for _, name in found[GIVOSIRAN].forms] == ["GIVOSIRAN", "GIVOSIRAN SODIUM"]


def test_tofogliflozin_anhydrous_is_left_as_open_targets_names_it(pages):
    titles = [card["medicine"] for (part, medicine_id), card in cards(pages[T2D]).items()
              if medicine_id == TOFOGLIFLOZIN_ANHYDROUS]
    assert titles and set(titles) == {"Tofogliflozin Anhydrous"}


# ---- Source record: Approved-tab cards only ----

def _listed_answer(rows):
    return {"data": {"disease": {"drugAndClinicalCandidates": {"rows": rows}}}}


def _row(drug_id, name, reports, parent=None):
    return {
        "maxClinicalStage": "APPROVAL",
        "clinicalReports": [{"url": url, "source": source, "clinicalStage": "APPROVAL"}
                            for url, source in reports],
        "drug": {"id": drug_id, "name": name, "maximumClinicalStage": "APPROVAL",
                 "drugWarnings": [], "parentMolecule": parent, "childMolecules": []},
    }


MADE_UP_LIST = {"CHEMBL_SALT": {"parent": "CHEMBL_PARENT", "parent_name": "Madeupine",
                                "source": "https://example.org/label", "date": "2026-11-26"}}
TTD = "https://ttd.idrblab.cn/data/drug/details/D_MADE_UP"
ATC = "https://www.whocc.no/atc_ddd_index/?code=X00XX00"
SALT_FDA = "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=salt-made-up"
PARENT_EMA = "https://www.ema.europa.eu/en/medicines/human/EPAR/made-up"


def _made_up_card(rows):
    with patch.object(fetch, "_salt_parents", return_value=MADE_UP_LIST), \
            patch("moonlight.fetch._post_json", return_value=_listed_answer(rows)):
        listed = fetch_approved(Disease("MADE_UP", "d"))
    assert [entry.id for entry in listed] == ["CHEMBL_PARENT"]
    return engine._approved_medicine("CHEMBL_PARENT", None, listed)


def test_a_salts_regulator_label_beats_the_parents_secondary_source():
    medicine = _made_up_card([
        _row("CHEMBL_PARENT", "MADEUPINE", [(TTD, "TTD"), (ATC, "ATC")]),
        _row("CHEMBL_SALT", "MADEUPINE SODIUM", [(SALT_FDA, "DailyMed")]),
    ])
    assert medicine.source_record == SALT_FDA


def test_when_the_parent_and_the_salt_both_have_a_regulator_label_the_parents_is_kept():
    medicine = _made_up_card([
        _row("CHEMBL_SALT", "MADEUPINE SODIUM", [(SALT_FDA, "DailyMed")]),  # the salt comes first
        _row("CHEMBL_PARENT", "MADEUPINE", [(TTD, "TTD"), (PARENT_EMA, "EMA Human Drugs")]),
    ])
    assert medicine.source_record == PARENT_EMA


def test_a_salt_alone_with_a_regulator_label_uses_it_under_the_parents_name():
    medicine = _made_up_card([_row("CHEMBL_SALT", "MADEUPINE SODIUM", [(TTD, "TTD"), (SALT_FDA, "FDA")])])
    assert medicine.source_record == SALT_FDA
    assert medicine.name == "Madeupine"
    assert medicine.forms == ("Madeupine", "MADEUPINE SODIUM")


def test_a_link_is_never_called_a_regulator_by_its_address():
    medicine = _made_up_card([
        _row("CHEMBL_PARENT", "MADEUPINE", [(TTD, "TTD")]),
        _row("CHEMBL_SALT", "MADEUPINE SODIUM", [(SALT_FDA, "TTD")]),  # a DailyMed address, said TTD
    ])
    assert medicine.source_record == TTD


def test_the_hand_lists_still_win_over_a_regulator_label():
    medicine = _made_up_card([
        _row("CHEMBL_PARENT", "MADEUPINE", [(TTD, "TTD")]),
        _row("CHEMBL_SALT", "MADEUPINE SODIUM", [(SALT_FDA, "DailyMed")]),
    ])
    confirmed = "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=confirmed-made-up"
    override = "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=override-made-up"
    assert replace(medicine, confirmed_from_label=confirmed).source_record == confirmed
    assert replace(medicine, source_override=override).source_record == override


def test_the_parents_own_is_kept_only_on_a_card_the_hand_list_merged():
    """An Open Targets family (parentMolecule given) keeps the order it had."""
    native = {"id": "CHEMBL_PARENT", "name": "MADEUPINE", "drugWarnings": []}
    medicine = _made_up_card([
        _row("CHEMBL_OTHER_SALT", "MADEUPINE CALCIUM", [(SALT_FDA, "DailyMed")], parent=native),
        _row("CHEMBL_PARENT", "MADEUPINE", [(PARENT_EMA, "EMA Human Drugs")]),
    ])
    assert medicine.source_record == SALT_FDA


# ---- The one real card the parent's-own rule reaches today ----

def test_zilucoplan_on_myasthenia_gravis_keeps_the_parents_own_label(pages):
    """Both forms have a regulator's label on the saved list: the salt FDA's,
    the parent EMA's. MAIN 5: keep the parent's own."""
    card = cards(pages[MYASTHENIA_GRAVIS])[("approved", ZILUCOPLAN)]
    assert card["medicine"] == "Zilucoplan"
    assert card["forms"] == ["Zilucoplan", "Zilucoplan Sodium"]
    assert card["source"] == ZILBRYSQ_EMA
    before = cards(load(BEFORE / f"{MYASTHENIA_GRAVIS}.json"))[("approved", ZILUCOPLAN)]
    assert before["source"] == ZILBRYSQ_FDA


# ---- Clue cards keep their research link (MAIN 5) ----

def test_eplontersen_on_al_amyloidosis_is_a_clue_card_and_keeps_its_link(pages):
    card = cards(pages[AL_AMYLOIDOSIS])[("new_clues", EPLONTERSEN)]
    assert card["source"] == "https://ttd.idrblab.cn/data/drug/details/DE2CW9"


@pytest.mark.parametrize("disease_id", [ESSENTIAL_TREMOR, HUNTINGTON])
def test_eslicarbazepine_cards_are_as_they_were(pages, disease_id):
    before = {key: card for key, card in cards(load(BEFORE / f"{disease_id}.json")).items()
              if key[1] == ESLICARBAZEPINE}
    after = {key: card for key, card in cards(pages[disease_id]).items()
             if key[1] == ESLICARBAZEPINE}
    assert before, "eslicarbazepine is on the saved page"
    assert after == before


# ---- Every other card on the 3.23 pages is unchanged ----

# What 3.24 may change: Ixazomib's title and forms on AL amyloidosis and on
# amyloidosis (its card holds only the salt's row), and Zilucoplan's Source
# record on myasthenia gravis (the parent's own label). Nothing else, anywhere.
CHANGED = {
    (MYASTHENIA_GRAVIS, "approved", ZILUCOPLAN): {"source": ZILBRYSQ_EMA},
    (AL_AMYLOIDOSIS, "wider_group", IXAZOMIB): {"medicine": "Ixazomib",
                                                "forms": ["Ixazomib", "Ixazomib Citrate"]},
    (AMYLOIDOSIS, "approved", IXAZOMIB): {"medicine": "Ixazomib",
                                          "forms": ["Ixazomib", "Ixazomib Citrate"]},
}


# Ticket 3.28 (MAIN 5's named OK): the In-trials Ixazomib card that 3.23 took
# off AL amyloidosis is back. It is the one card added; nothing else is.
ADDED = {AL_AMYLOIDOSIS: [("more_in_trials", IXAZOMIB)]}  # ticket 3.28


@pytest.mark.parametrize("disease_id", sorted(PAGES))
def test_every_other_card_on_the_3_23_pages_is_unchanged(pages, disease_id):
    before, after = load(BEFORE / f"{disease_id}.json"), pages[disease_id]
    old, new = cards(before), cards(after)
    added = ADDED.get(disease_id, [])  # ticket 3.28
    assert [key for key in new if key not in old] == added  # ticket 3.28
    new = {key: card for key, card in new.items() if key not in added}  # ticket 3.28
    assert list(new) == list(old)  # the same cards, in the same places and order
    for key, card in old.items():
        expected = dict(card, **CHANGED.get((disease_id,) + key, {}))
        assert new[key] == expected, key
    # every other part of the answer, letter for letter
    assert {k: v for k, v in after.items() if k not in CARD_PARTS} == \
        {k: v for k, v in before.items() if k not in CARD_PARTS}


def test_each_change_listed_is_a_real_change():
    for (disease_id, part, medicine_id), change in CHANGED.items():
        card = cards(load(BEFORE / f"{disease_id}.json"))[(part, medicine_id)]
        assert all(card[key] != value for key, value in change.items()), (disease_id, part)
