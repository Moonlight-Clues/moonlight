"""Ticket 3.17 (Q8). The Source record opens the medicine's own current label.

Decision of 25 Nov: when a medicine has its own current label, the Source
record opens it. It does not open a combination product's page, a premixed
form, a different medicine with a similar name, or an archived, replaced
DailyMed label. A combination page is used only when no single-medicine
label exists. The 2.53 regulator-first order stays for every other card.

THE RULE: moonlight/source_overrides.json is a list written by hand. Each
entry holds medicine_id, disease_id (or "*" for every page), url, date,
note and evidence_file (MAIN 4, 25 Nov: note is the CSV's quote word for
word, date is its label_date, evidence_file is kept). On an Approved card
(main list and both folded boxes) that the list names for this page, the
Source record is that url, before any other choice. Nothing else on the
card changes. A card the list does not name is unchanged.

The first batch is MAIN 4's source_overrides_batch1.csv, saved unchanged in
fixtures/source_overrides/. Saved answers only. No network.
"""

import csv
import json
import pathlib
from dataclasses import replace
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from moonlight import api, engine, fetch
from moonlight.engine import ADDED_LINE, ApprovedMedicine
from moonlight.records import Disease

ROOT = pathlib.Path(__file__).resolve().parent.parent
BATCH = ROOT / "fixtures" / "source_overrides" / "source_overrides_batch1.csv"
OVERRIDES_FILE = ROOT / "moonlight" / "source_overrides.json"
KEYS = {"medicine_id", "disease_id", "url", "date", "note", "evidence_file"}

PAH = Disease(id="MONDO_0015924", name="pulmonary arterial hypertension")
TREMOR = Disease(id="MONDO_0003233", name="essential tremor")
MOVEMENT_DISORDER = "MONDO_0005395"  # a parent of essential tremor
T2D = Disease(id="MONDO_0005148", name="type 2 diabetes mellitus")

MACITENTAN, TETRABENAZINE, ALOGLIPTIN = "CHEMBL2103873", "CHEMBL117785", "CHEMBL376359"
OPSUMIT = "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=1e484a50-55db-4b85-8c57-6cd1b0353abd"
XENAZINE = "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=ac768bab-8afa-4446-bc7f-caeeffec0cda"
NESINA = "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=a3768c7e-aa4c-44d3-bc53-43bb7346c0b0"

LABEL = "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=made-up-label"
OTHER = "https://www.ema.europa.eu/en/medicines/human/EPAR/made-up-other"


def load(file):
    return json.loads(file.read_text(encoding="utf-8"))


def entry(medicine_id="CHEMBL1", disease_id="MONDO_X", url=LABEL, **more):
    base = dict(medicine_id=medicine_id, disease_id=disease_id, url=url,
                date="2026-11-25", note="A made-up indication sentence.",
                evidence_file="made-up.csv")
    base.update(more)
    return base


def card(**fields):
    """An Approved card with no paths, only what the test names."""
    base = dict(id="CHEMBL1", name="Made-up", forms=("Made-up",), clue=None,
                listed_sources=(OTHER,), approval_sources=(OTHER,),
                regulator_sources=(OTHER,), regulator_record=True)
    base.update(fields)
    return ApprovedMedicine(**base)


def with_list(entries):
    return patch.object(engine, "_read_source_overrides", return_value=list(entries))


def from_saved_list(file, disease, medicine_id):
    """One Approved card, built the engine's way from a saved medicine list."""
    with patch("moonlight.fetch._post_json", return_value=load(file)):
        by_id = {one.id: one for one in fetch.fetch_approved(disease)}
    return engine._approved_medicine(medicine_id, None, [by_id[medicine_id]])


# ---- the hand-written file is MAIN 4's batch, exactly ----

def batch_rows():
    with BATCH.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def test_the_file_holds_the_54_rows_of_the_batch_exactly_in_order():
    # Ticket 2.60 (MAIN 4, 26 Nov) added two rows after the batch (rosiglitazone on
    # type 2 diabetes, Roctavian on haemophilia A): 56 rows. tests/test_source_links_2_60.py
    # holds them. The first 54 are still the batch, unchanged.
    rows = batch_rows()
    assert len(rows) == 54
    written = load(OVERRIDES_FILE)
    assert len(written) == 57  # 2.61 added givosiran, Orphanet_95157
    assert written[:54] == [
        {"medicine_id": row["medicine_id"], "disease_id": row["disease_id"],
         "url": row["url"], "date": row["label_date"], "note": row["quote"],
         "evidence_file": row["evidence_file"]}
        for row in rows]


def test_every_entry_holds_exactly_the_six_fields():
    assert all(set(one) == KEYS for one in load(OVERRIDES_FILE))


def test_the_engine_reads_the_real_file():
    found = engine.source_overrides()
    assert found[(MACITENTAN, PAH.id)] == OPSUMIT
    assert found[(TETRABENAZINE, TREMOR.id)] == XENAZINE
    assert found[(ALOGLIPTIN, T2D.id)] == NESINA
    assert len(found) == 57  # 54 of the batch + 2 from ticket 2.60 + 1 from 2.61


# ---- the file is checked like the other hand-written lists ----

@pytest.mark.parametrize("change", [
    {"url": "http://dailymed.nlm.nih.gov/made-up"},
    {"url": ""},
    {"date": "25 Nov 2026"},
    {"medicine_id": ""},
    {"disease_id": ""},
    {"note": ""},
    {"evidence_file": ""},
    {"note": 7},
    {"reason": "extra"},
])
def test_an_entry_not_written_properly_is_refused(change):
    with with_list([entry(**change)]), pytest.raises(ValueError):
        engine.source_overrides()


@pytest.mark.parametrize("missing", sorted(KEYS))
def test_an_entry_with_a_piece_missing_is_refused(missing):
    one = entry()
    del one[missing]
    with with_list([one]), pytest.raises(ValueError):
        engine.source_overrides()


def test_a_file_that_is_not_a_list_is_refused():
    with patch.object(engine, "_read_source_overrides", return_value={}), \
            pytest.raises(ValueError):
        engine.source_overrides()


def test_the_same_pair_written_twice_with_two_links_is_refused():
    with with_list([entry(), entry(url=OTHER)]), pytest.raises(ValueError):
        engine.source_overrides()


def test_the_app_will_not_start_with_a_broken_file():
    with with_list([entry(url="http://made-up")]), pytest.raises(ValueError):
        with TestClient(api.app):
            pass


# ---- source_record: the list comes before any other choice ----

def test_a_listed_card_opens_the_label():
    with with_list([entry()]):
        (one,) = engine.override_sources([card()], "MONDO_X")
    assert one.source_record == LABEL


@pytest.mark.parametrize("field", ["added_from_label", "confirmed_from_label"])
def test_the_list_comes_before_the_other_hand_written_labels(field):
    with with_list([entry()]):
        (one,) = engine.override_sources([card(**{field: OTHER})], "MONDO_X")
    assert one.source_record == LABEL


def test_only_the_source_record_changes():
    plain = card(regulator_record=False, approval_sources=(OTHER,), regulator_sources=())
    with with_list([entry()]):
        (one,) = engine.override_sources([plain], "MONDO_X")
    assert replace(one, source_override=None) == plain
    assert one.proof_note == plain.proof_note == engine.NO_REGULATOR_LINE


def test_an_added_card_keeps_its_line():
    with with_list([entry()]):
        (one,) = engine.override_sources([card(added_from_label=OTHER)], "MONDO_X")
    assert (one.source_record, one.proof_note) == (LABEL, ADDED_LINE)


def test_an_entry_is_used_only_on_its_own_disease():
    with with_list([entry(disease_id="MONDO_Y")]):
        (one,) = engine.override_sources([card()], "MONDO_X")
    assert one == card()
    assert one.source_record == OTHER


def test_a_star_entry_is_used_on_every_page():
    with with_list([entry(disease_id="*")]):
        for disease_id in ("MONDO_X", "MONDO_Y"):
            (one,) = engine.override_sources([card()], disease_id)
            assert one.source_record == LABEL


def test_the_disease_own_entry_wins_over_a_star_entry():
    with with_list([entry(disease_id="*", url=OTHER), entry()]):
        (here,) = engine.override_sources([card()], "MONDO_X")
        (elsewhere,) = engine.override_sources([card()], "MONDO_Y")
    assert (here.source_record, elsewhere.source_record) == (LABEL, OTHER)


def test_a_card_not_listed_is_unchanged_and_nothing_moves():
    cards = [card(id="CHEMBL1"), card(id="CHEMBL2", name="Other")]
    with with_list([entry(medicine_id="CHEMBL2")]):
        out = engine.override_sources(cards, "MONDO_X")
    assert out[0] is cards[0]
    assert [one.id for one in out] == ["CHEMBL1", "CHEMBL2"]
    assert out[1].source_record == LABEL


def test_an_empty_list_changes_nothing():
    cards = [card()]
    with with_list([]):
        assert engine.override_sources(cards, "MONDO_X") == cards


# ---- the three cards the ticket names, from saved answers ----

def test_macitentan_on_pah_opens_opsumit():
    medicine = from_saved_list(ROOT / "fixtures" / "MONDO_0015924" / "disease_drugs.response.json",
                               PAH, MACITENTAN)
    assert medicine.source_record != OPSUMIT  # the saved answer alone does not give it
    (one,) = engine.override_sources([medicine], PAH.id)
    assert one.source_record == OPSUMIT


def test_tetrabenazine_on_essential_tremor_opens_xenazine():
    # It is on essential tremor's page only through its parent, movement
    # disorder: the folded box "Approved for a wider group".
    medicine = from_saved_list(
        ROOT / "fixtures" / "no_regulator" / "disease_drugs" / f"{MOVEMENT_DISORDER}.response.json",
        Disease(id=MOVEMENT_DISORDER, name="movement disorder"), TETRABENAZINE)
    # Before: the EMA page of AUSTEDO, a different medicine with a similar name.
    assert medicine.source_record == "https://www.ema.europa.eu/en/medicines/human/EPAR/austedo"
    (one,) = engine.override_sources([medicine], TREMOR.id)
    assert one.source_record == XENAZINE


def test_alogliptin_on_type_2_diabetes_opens_nesina():
    medicine = from_saved_list(
        ROOT / "fixtures" / "labels_read" / "2.52" / "disease_drugs" / f"{T2D.id}.response.json",
        T2D, ALOGLIPTIN)
    assert medicine.source_record != NESINA
    (one,) = engine.override_sources([medicine], T2D.id)
    assert one.source_record == NESINA


# ---- the whole essential tremor page, from saved answers ----

SAVED = ROOT / "fixtures" / "approvals_by_hand"
REUSED = ROOT / "fixtures" / "no_regulator"


def saved_post_json(body):
    """Stands in for fetch._post_json with the saved files."""
    query, variables = body["query"], body["variables"]
    if "targetId" in variables:
        kind, asked = "target_drugs", variables["targetId"]
    else:
        asked = variables["diseaseId"]
        if "parents" in query:
            kind = "family"
        elif "associatedTargets" in query:
            kind = "associated_targets"
        elif "drugAndClinicalCandidates" in query:
            kind = "disease_drugs"
        else:
            kind = "disease"
    for folder in (SAVED, REUSED):
        file = folder / kind / f"{asked}.response.json"
        if file.exists():
            return load(file)
    raise AssertionError(f"no saved answer for {kind} {asked}")


@pytest.fixture
def offline():
    api.forget_visitors()
    api.forget_answers()
    with patch("requests.request", side_effect=AssertionError("network used")), \
            patch("requests.post", side_effect=AssertionError("network used")), \
            patch("requests.get", side_effect=AssertionError("network used")), \
            patch("requests.sessions.Session.request",
                  side_effect=AssertionError("network used")), \
            patch("moonlight.fetch._post_json", side_effect=saved_post_json):
        yield
    api.forget_visitors()
    api.forget_answers()


def tremor_page():
    response = TestClient(api.app).get("/api/clues", params={"disease_id": TREMOR.id})
    assert response.status_code == 200
    return response.json()


def test_the_essential_tremor_page_opens_xenazine_in_the_wider_box(offline):
    page = tremor_page()
    (tetrabenazine,) = [one for one in page["wider_group"] if one["id"] == TETRABENAZINE]
    assert tetrabenazine["source"] == XENAZINE


def test_on_that_page_only_the_listed_card_changes(offline):
    with with_list([]):
        before = tremor_page()
    api.forget_answers()
    after = tremor_page()
    for part in ("approved", "narrower", "wider_group"):
        for old, new in zip(before.get(part, []), after.get(part, [])):
            if old["id"] == TETRABENAZINE and part == "wider_group":
                assert new == {**old, "source": XENAZINE}
            else:
                assert new == old
    assert {key: value for key, value in after.items() if key != "wider_group"} == \
        {key: value for key, value in before.items() if key != "wider_group"}
