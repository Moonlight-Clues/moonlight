"""Ticket 2.56. Night label audit, batch 1: hand-written list entries only.

Saved answers, no network: fixtures/task12_batch1/before/<disease>.clues.json is
the live /api/clues answer of 2026-11-25 with the old lists, .../after/ the
answer with this ticket's entries, both saved as sent (Open Targets 26.09).

NOT added, held for a question to Kashish (STOP AND ASK): the two withdrawals
(voxelotor on sickle cell disease, ataluren on Duchenne). Both cards already
carry the older "some country or region" line, and that line wins over the
hand-written one (api.py), so the ticket's check cannot pass without changing
the code. fixtures/task12_batch1/stopped/ holds the answers with the entries in.
"""

import json

from hand_ids import without_correction_id
import pathlib

import pytest

from moonlight import engine

# Ticket 2.62: the signed rows of tests/test_red_warnings_2_62.py (delete a row there and these follow).
from test_red_warnings_2_62 import LIMIT_ROWS, RED_ROWS  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
LISTS = ROOT / "moonlight"
SAVED = ROOT / "fixtures" / "task12_batch1"
THE_DAY = "2026-11-25"
SECOND_NOTE = ("This looks like a mistake in the database. The official label is for "
               "a different disease.")
DM = "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid="
JAYEMPI = "https://www.ema.europa.eu/en/medicines/human/EPAR/jayempi"
OLD_WITHDRAWN = "The database records a withdrawal for this medicine in some country or region."
LIMITED = "The label covers only some people with this disease."

SICKLE, UC, SLE = "MONDO_0011382", "MONDO_0005101", "MONDO_0007915"
HF, HTN, DMD, MG = "MONDO_0005252", "MONDO_0005044", "MONDO_0010679", "MONDO_0009688"

NEW = {
    "corrections.json": [
        {"medicine_id": m, "disease_id": d, "date": THE_DAY, "note": SECOND_NOTE}
        for m, d in [("CHEMBL582", UC), ("CHEMBL1755", HF), ("CHEMBL1491", HF),
                     ("CHEMBL844", HTN), ("CHEMBL1051", HTN)]],
    "confirmed.json": [
        {"medicine_id": "CHEMBL1535", "disease_id": SLE, "date": THE_DAY,
         "label": DM + "5ca218af-b3f4-512a-e063-6394a90a3ec6"},
        {"medicine_id": "CHEMBL1542", "disease_id": UC, "date": THE_DAY, "label": JAYEMPI},
        {"medicine_id": "CHEMBL278020", "disease_id": MG, "date": THE_DAY,
         "label": "https://www.medicines.org.uk/emc/product/6268/smpc"},
    ],
    "limits.json": [
        {"medicine_id": "CHEMBL1542", "disease_id": UC, "date": THE_DAY, "label": JAYEMPI},
    ],
}


def load(path):
    return without_correction_id(json.loads(path.read_text(encoding="utf-8")))


def answer(state, disease_id):
    return load(SAVED / state / f"{disease_id}.clues.json")


def cards(page):
    return [(tab, c) for tab, v in page.items() if isinstance(v, list)
            for c in v if isinstance(c, dict) and "id" in c]


def card(page, tab, medicine_id):
    (found,) = [c for t, c in cards(page) if t == tab and c["id"] == medicine_id]
    return found


@pytest.mark.parametrize("name", list(NEW))
def test_each_file_ends_with_the_new_entries(name):
    entries = load(LISTS / name)
    if name == "corrections.json":
        # Ticket 2.58 (25N-16) added six entries after these, dated 2026-11-26.
        entries = entries[:-6 - len(RED_ROWS)]  # ticket 2.62 added RED_ROWS after those
    if name == "limits.json":
        entries = entries[:len(entries) - len(LIMIT_ROWS)]  # ticket 2.62 added LIMIT_ROWS after these
    if name == "confirmed.json":
        from test_list_fixes_2_64 import CONFIRMED_ROWS  # ticket 2.64
        entries = entries[:-len(CONFIRMED_ROWS)]  # ticket 2.64 added two after givosiran: Suiny, Deberza
        # Ticket 2.61 (26 Nov) added one entry after these: givosiran, Orphanet_95157.
        entries = entries[:-1]
    bare = lambda entry: {k: v for k, v in entry.items() if k != "label"}
    assert [bare(entry) for entry in entries[-len(NEW[name]):]] == [bare(entry) for entry in NEW[name]]
    assert len(entries) > len(NEW[name])


def test_the_two_withdrawals_are_not_in_the_list_yet():
    ids = {(e["medicine_id"], e["disease_id"]) for e in load(LISTS / "withdrawals.json")}
    assert ("CHEMBL4101807", SICKLE) not in ids and ("CHEMBL256997", DMD) not in ids


def test_the_entries_read_cleanly():
    engine.corrections()
    engine.confirmed_by_label()
    engine.limits_by_hand()


@pytest.mark.parametrize("medicine_id,disease_id", [
    ("CHEMBL582", UC), ("CHEMBL1755", HF), ("CHEMBL1491", HF),
    ("CHEMBL844", HTN), ("CHEMBL1051", HTN)])
def test_red_card_stays_in_approved_with_kashishs_words_and_joins_the_red_box(
        medicine_id, disease_id):
    before, after = answer("before", disease_id), answer("after", disease_id)
    assert "warning" not in card(before, "approved", medicine_id)
    assert card(after, "approved", medicine_id)["warning"] == SECOND_NOTE
    assert medicine_id in after["wrong_approvals_box"]
    assert medicine_id not in before.get("wrong_approvals_box", [])


def test_hydroxychloroquine_leaves_the_no_regulator_box_for_the_main_list():
    before, after = answer("before", SLE), answer("after", SLE)
    assert "CHEMBL1535" in before["no_regulator_box"]
    assert "CHEMBL1535" not in after.get("no_regulator_box", [])
    old, new = card(before, "approved", "CHEMBL1535"), card(after, "approved", "CHEMBL1535")
    assert "proof_note" in old and "proof_note" not in new
    assert new["source"] == DM + "5ca218af-b3f4-512a-e063-6394a90a3ec6"
    assert "limit_note" not in new and "warning" not in new


def test_azathioprine_is_approved_with_the_only_some_people_line():
    before, after = answer("before", UC), answer("after", UC)
    assert "CHEMBL1542" in before["no_regulator_box"]
    assert "CHEMBL1542" not in after["no_regulator_box"]
    new = card(after, "approved", "CHEMBL1542")
    assert "proof_note" not in new and new["limit_note"] == LIMITED
    assert new["source"] == JAYEMPI


def test_neostigmine_stays_put_and_its_source_opens_the_emc_page():
    before, after = answer("before", MG), answer("after", MG)
    old, new = card(before, "approved", "CHEMBL278020"), card(after, "approved", "CHEMBL278020")
    assert old["source"].startswith(DM)
    assert new["source"] == "https://www.medicines.org.uk/emc/product/6268/smpc"
    assert {k: v for k, v in new.items() if k != "source"} == \
           {k: v for k, v in old.items() if k != "source"}
    assert before["wrong_approvals_box"] == after["wrong_approvals_box"]
    assert before["no_regulator_box"] == after["no_regulator_box"]


def test_the_two_withdrawal_pages_are_unchanged_for_now():
    for disease_id in (SICKLE, DMD):
        assert answer("before", disease_id) == answer("after", disease_id)
    assert card(answer("after", SICKLE), "approved", "CHEMBL4101807")[
        "withdrawal_note"] == OLD_WITHDRAWN


def test_no_other_card_changes():
    """Per disease: the cards that differ are exactly the entries' cards."""
    expected = {
        UC: {"CHEMBL582", "CHEMBL1542"}, SLE: {"CHEMBL1535"}, HF: {"CHEMBL1755", "CHEMBL1491"},
        HTN: {"CHEMBL844", "CHEMBL1051"}, MG: {"CHEMBL278020"}, SICKLE: set(), DMD: set()}
    for disease_id, ids in expected.items():
        b, a = answer("before", disease_id), answer("after", disease_id)
        old = {(t, c["id"]): c for t, c in cards(b)}
        new = {(t, c["id"]): c for t, c in cards(a)}
        assert old.keys() == new.keys()
        assert {i for (t, i), c in old.items() if c != new[(t, i)]} == ids
