"""Ticket 3.23 (MAIN 4, 26 Nov). One card per medicine when Open Targets misses
a salt form's parent (error E52).

Open Targets 26.09 gives some salt forms no parentMolecule (thread 2106), so
the salt showed as a second card. moonlight/salt_parents.json is a hand list:
{"<salt id>": {"parent": "<parent id>", "source": "...", "date": "..."}}.
fetch.py treats a drug with no parentMolecule whose id is in the list as having
that parent. Nothing else in grouping changes.

Saved answers only, no network. Lists and protein answers come from the
fixtures/ folders earlier tickets saved.
"""

import json
import pathlib
from unittest.mock import patch

import pytest

from moonlight import api, engine, fetch
from moonlight.fetch import fetch_approved, fetch_listed_medicines, fetch_paths
from moonlight.records import Disease, Target

import test_givosiran_2_61 as givosiran
import test_approvals_batch as second_batch

ROOT = pathlib.Path(__file__).resolve().parent.parent
LIST_FILE = ROOT / "moonlight" / "salt_parents.json"
FIXTURES = ROOT / "fixtures"

AHP = "Orphanet_95157"
AMYLOIDOSIS = "MONDO_0019065"  # where patisiran's two cards are saved
T2D = "MONDO_0005148"
GIVOSIRAN, GIVOSIRAN_SODIUM = "CHEMBL4297760", "CHEMBL4594265"
PATISIRAN, PATISIRAN_SODIUM = "CHEMBL3989987", "CHEMBL4297536"
METFORMIN_GLYCINATE = "CHEMBL2108299"

# The ten pairs (MAIN 4 dropped sefaxersen sodium: no page names both): salt -> parent.
PAIRS = {
    "CHEMBL4594265": "CHEMBL4297760",  # givosiran sodium
    "CHEMBL4297536": "CHEMBL3989987",  # patisiran sodium
    "CHEMBL4594335": "CHEMBL4594334",  # eplontersen sodium
    "CHEMBL5095303": "CHEMBL4594511",  # vutrisiran sodium
    "CHEMBL5315048": "CHEMBL4298207",  # zilucoplan sodium
    "CHEMBL3707226": "CHEMBL2108396",  # defibrotide sodium
    "CHEMBL4298005": "CHEMBL471498",   # mitiglinide calcium dihydrate
    "CHEMBL4297658": "CHEMBL2018096",  # ipragliflozin L-proline
    "CHEMBL3545432": "CHEMBL2141296",  # ixazomib citrate
    "CHEMBL87992": "CHEMBL315985",     # eslicarbazepine acetate
}


def load(file):
    return json.loads(file.read_text(encoding="utf-8"))


def _saved_list(disease_id):
    for file in sorted(FIXTURES.glob(f"**/disease_drugs/{disease_id}.response.json")):
        return load(file)
    raise AssertionError(f"no saved list for {disease_id}")


def saved_post_json(body):
    """Stands in for fetch._post_json: the disease's own saved list."""
    return _saved_list(body["variables"]["diseaseId"])


@pytest.fixture(autouse=True)
def offline():
    api.forget_visitors()
    with patch("requests.request", side_effect=AssertionError("network used")), \
            patch("requests.post", side_effect=AssertionError("network used")), \
            patch("requests.get", side_effect=AssertionError("network used")), \
            patch("requests.sessions.Session.request", side_effect=AssertionError("network used")), \
            patch("moonlight.fetch._post_json", side_effect=saved_post_json):
        yield
    api.forget_visitors()


def listing(disease_id, salt_parents):
    with patch.object(fetch, "_salt_parents", return_value=salt_parents):
        return {listed.id: listed for listed in fetch_approved(Disease(disease_id, "d"))}


def families(disease_id, salt_parents):
    with patch.object(fetch, "_salt_parents", return_value=salt_parents):
        return fetch._list_families(Disease(disease_id, "d"))


def real_list():
    return load(LIST_FILE)


# ---- the hand list ----

def test_the_list_holds_exactly_the_ten_pairs_and_not_sefaxersen():
    assert {salt: row["parent"] for salt, row in real_list().items()} == PAIRS
    assert len(PAIRS) == 10
    assert "CHEMBL6068441" not in real_list()  # sefaxersen sodium


def test_every_row_has_a_source_and_the_build_date():
    for salt, row in real_list().items():
        assert set(row) == {"parent", "source", "date"}, salt
        assert row["source"].strip(), salt
        assert row["date"] == "2026-11-27", salt
        assert row["source"].startswith("https://"), salt  # Product's 26 Nov evidence URL


def test_metformin_glycinate_is_not_in_the_list():
    assert METFORMIN_GLYCINATE not in real_list()
    assert METFORMIN_GLYCINATE not in {row["parent"] for row in real_list().values()}


def test_the_engine_reads_the_real_file():
    assert fetch._salt_parents() == real_list()


# ---- Orphanet_95157: givosiran ----

def test_before_givosiran_was_two_families():
    assert set(listing(AHP, {})) == {GIVOSIRAN, GIVOSIRAN_SODIUM}


def test_after_givosiran_is_one_family_with_both_forms_parent_first():
    found = listing(AHP, real_list())
    assert list(found) == [GIVOSIRAN]
    assert [form_id for form_id, _ in found[GIVOSIRAN].forms] == [GIVOSIRAN, GIVOSIRAN_SODIUM]


def test_the_merged_family_keeps_every_record_and_source_of_both():
    before, after = listing(AHP, {}), listing(AHP, real_list())
    merged = after[GIVOSIRAN]
    for old in before.values():
        for link in old.sources:
            assert link in merged.sources
        for link in old.approval_sources:
            assert link in merged.approval_sources
        for link in old.regulator_sources:
            assert link in merged.regulator_sources
    assert merged.regulator_record is True  # the salt's FDA receipt counts


def test_the_merged_on_list_family_holds_both_records_with_the_parent_first():
    with patch.object(fetch, "_salt_parents", return_value=real_list()):
        found = fetch_listed_medicines(Disease(AHP, "d"))
    assert len(found) == 1
    forms = found[0].medicine.forms
    assert [form.id for form in forms] == [GIVOSIRAN, GIVOSIRAN_SODIUM]
    assert forms[1].parent_id == GIVOSIRAN and forms[0].parent_id is None


def test_the_acute_hepatic_porphyria_page_has_one_givosiran_card():
    page = givosiran.page(AHP)
    assert list(page["cards"]) == [GIVOSIRAN]
    assert page["main"] == [GIVOSIRAN] and page["box"] == []
    card = page["cards"][GIVOSIRAN]
    assert card["forms"] == ["Givosiran", "Givosiran Sodium"]
    assert card["source"] == givosiran.LABEL  # DailyMed Givlaari
    assert "proof_note" not in card


# ---- patisiran: the ONPATTRO label sits on the salt's record ----

def test_patisiran_is_one_card_and_its_source_record_is_the_onpattro_dailymed_label():
    disease = Disease(AMYLOIDOSIS, "amyloidosis")
    with patch.object(fetch, "_salt_parents", return_value=real_list()):
        tabs = second_batch.tabs_for(AMYLOIDOSIS, [])
    ids = [medicine.id for medicine in tabs.approved]
    assert ids.count(PATISIRAN) == 1 and PATISIRAN_SODIUM not in ids
    medicine = next(m for m in tabs.approved if m.id == PATISIRAN)
    assert list(medicine.forms) == ["PATISIRAN", "PATISIRAN SODIUM"]  # the parent first
    card = api._approved_json(medicine)
    assert card["source"].startswith("https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=e87ec36f")
    assert disease.id == AMYLOIDOSIS


# ---- the rest of the rule ----

def test_metformin_glycinate_is_untouched():
    old, new = families(T2D, {}), families(T2D, real_list())
    assert METFORMIN_GLYCINATE in old
    assert new[METFORMIN_GLYCINATE] == old[METFORMIN_GLYCINATE]
    assert [form[0] for form in new[METFORMIN_GLYCINATE]["forms"]] == [METFORMIN_GLYCINATE]


def test_a_salt_id_that_already_has_a_parentMolecule_ignores_the_list():
    answer = _saved_list(AHP)
    for row in answer["data"]["disease"]["drugAndClinicalCandidates"]["rows"]:
        if row["drug"]["id"] == GIVOSIRAN_SODIUM:
            row["drug"]["parentMolecule"] = {"id": "CHEMBL_OTHER", "name": "OTHER",
                                             "drugWarnings": []}
    with patch("moonlight.fetch._post_json", return_value=answer):
        found = families(AHP, real_list())
    assert set(found) == {GIVOSIRAN, "CHEMBL_OTHER"}  # not merged into givosiran
    assert [form[0] for form in found["CHEMBL_OTHER"]["forms"]] == [GIVOSIRAN_SODIUM]


def test_a_salt_whose_parent_has_no_row_is_named_after_the_salt_until_the_parent_appears():
    answer = _saved_list(AHP)
    rows = answer["data"]["disease"]["drugAndClinicalCandidates"]["rows"]
    answer["data"]["disease"]["drugAndClinicalCandidates"]["rows"] = [
        row for row in rows if row["drug"]["id"] != GIVOSIRAN]
    with patch("moonlight.fetch._post_json", return_value=answer):
        found = families(AHP, real_list())
    assert list(found) == [GIVOSIRAN]
    assert found[GIVOSIRAN]["name"]  # never None
    assert [form[0] for form in found[GIVOSIRAN]["forms"]] == [GIVOSIRAN_SODIUM]


def _every_saved_disease():
    seen = {}
    for file in sorted(FIXTURES.glob("**/disease_drugs/*.response.json")):
        if file.name.count(".") == 2:  # <id>.response.json, not <id>.<word>.drug.response.json
            seen.setdefault(file.name.split(".")[0], file)
    return sorted(seen)


@pytest.mark.parametrize("disease_id", _every_saved_disease())
def test_every_other_family_on_every_saved_list_is_unchanged(disease_id):
    """Only a family holding a listed salt (or its listed parent) may differ."""
    try:
        old, new = families(disease_id, {}), families(disease_id, real_list())
    except (KeyError, TypeError):
        pytest.skip("not a list answer of the current shape")
    touched = set(PAIRS) | set(PAIRS.values())
    untouched = {key for key, family in old.items()
                 if not touched & {form[0] for form in family["forms"]}}
    assert {key: new[key] for key in untouched} == {key: old[key] for key in untouched}
    for key, family in new.items():
        if key not in untouched:
            assert touched & {form[0] for form in family["forms"]}
    # a merge only ever lowers the count, and by the number of pairs found together
    assert len(new) <= len(old)
    for key in old:
        assert key in new or key in PAIRS  # only a salt's own family can disappear


def test_protein_paths_merge_too_and_keep_both_forms():
    """TTR in the saved answer: patisiran and its sodium form were two paths."""
    target = Target("ENSG00000118271", "TTR", "transthyretin", 1.0)
    saved = load(FIXTURES / "tafamidis_warning" / "target_drugs" / "ENSG00000118271.response.json")
    with patch("moonlight.fetch._post_json", return_value=saved):
        with patch.object(fetch, "_salt_parents", return_value={}):
            old = fetch_paths(Disease(AMYLOIDOSIS, "amyloidosis"), target)
        with patch.object(fetch, "_salt_parents", return_value=real_list()):
            new = fetch_paths(Disease(AMYLOIDOSIS, "amyloidosis"), target)
    old_ids = [p.medicine.forms[0].parent_id or p.medicine.forms[0].id for p in old]
    new_ids = [p.medicine.forms[0].parent_id or p.medicine.forms[0].id for p in new]
    assert PATISIRAN in old_ids and PATISIRAN_SODIUM in old_ids
    assert PATISIRAN in new_ids and PATISIRAN_SODIUM not in new_ids
    assert len(new) < len(old)
    patisiran = next(p for p in new if p.medicine.forms[0].id == PATISIRAN
                     or p.medicine.forms[0].parent_id == PATISIRAN)
    assert {f.id for f in patisiran.medicine.forms} >= {PATISIRAN, PATISIRAN_SODIUM}
    touched = set(PAIRS) | set(PAIRS.values())
    # every other path keeps its place; a merged one stands where Open Targets first named it
    assert [i for i in old_ids if i not in touched] == [i for i in new_ids if i not in touched]
