"""Ticket 2.58: list changes from the 25 Nov decisions 25N-13 and 25N-16.

25N-13: ipratropium (CHEMBL1621597) on asthma (MONDO_0004979) loses its red
note. The UK Atrovent 250 UDVs label (eMC, updated 27 Oct 2026), section 4.1,
names asthma.
25N-16: six cards on type 2 diabetes (MONDO_0005148) get the red note. They
stayed in the wider-group box. Ticket 3.16 (Kashish's decision Q7, 25 Nov)
moves them to the red box: their cards stay in "wider_group" in the API
answer, and "wrong_approvals_box" names them.

Saved answers only (fixtures/old_withdrawn_flag/). No network.
"""

import json
import pathlib

import pytest

from moonlight import engine

import old_flag_saved as saved

ROOT = pathlib.Path(__file__).resolve().parent.parent
CORRECTIONS_FILE = ROOT / "moonlight" / "corrections.json"

NOTE = ("This looks like a mistake in the database. The official label is for "
        "a different disease.")
ASTHMA, IPRATROPIUM = "MONDO_0004979", "CHEMBL1621597"
T2D = "MONDO_0005148"
SIX = {  # medicine id -> name
    "CHEMBL1014": "candesartan cilexetil", "CHEMBL1200692": "olmesartan medoxomil",
    "CHEMBL24": "atenolol", "CHEMBL1055": "chlorthalidone",
    "CHEMBL435": "hydrochlorothiazide", "CHEMBL1237": "lisinopril",
}
NOT_ADDED = {"irbesartan": "CHEMBL1513", "losartan": "CHEMBL191"}  # diabetic kidney disease


def real():
    return json.loads(CORRECTIONS_FILE.read_text(encoding="utf-8"))


def entry(medicine_id, disease_id, day):
    return {"medicine_id": medicine_id, "disease_id": disease_id, "date": day, "note": NOTE}


def as_before():
    """The file as it was before this ticket."""
    entries = [e for e in real() if not (e["disease_id"] == T2D and e["medicine_id"] in SIX)]
    entries.append(entry(IPRATROPIUM, ASTHMA, "2026-11-25"))
    return entries


def ids_in(page, part):
    return [c["id"] if isinstance(c, dict) else c for c in page.get(part, [])]


def strip_card(page, medicine_id):
    """The page without one card, wherever it sits (a card, or a bare id)."""
    out = {}
    for key, value in page.items():
        if isinstance(value, list):
            value = [c for c in value
                     if (c.get("id") if isinstance(c, dict) else c) != medicine_id]
        out[key] = value
    return out


@pytest.fixture(scope="module")
def asthma():
    return saved.page_answer(ASTHMA, wrong=as_before()), saved.page_answer(ASTHMA)


@pytest.fixture(scope="module")
def diabetes():
    return saved.page_answer(T2D, wrong=as_before()), saved.page_answer(T2D)


# ---- the file ----

def test_ipratropium_on_asthma_is_gone_from_the_file_and_nothing_else_is_lost():
    entries = real()
    assert not [e for e in entries if e["medicine_id"] == IPRATROPIUM]
    assert len(entries) == 122  # 118 - mannitol (3.10) - ipratropium + six
    assert len({(e["medicine_id"], e["disease_id"]) for e in entries}) == 122


def test_the_six_entries_are_in_the_existing_shape_with_the_existing_note():
    new = [e for e in real() if e["date"] == "2026-11-26"]
    assert new == [entry(m, T2D, "2026-11-26") for m in SIX]
    assert all(list(e) == ["medicine_id", "disease_id", "date", "note"] for e in new)


def test_irbesartan_and_losartan_are_not_red_on_type_2_diabetes():
    assert not set(NOT_ADDED.values()) & engine.looks_wrong(T2D)


def test_the_engine_gives_the_six_the_red_words_on_type_2_diabetes_only():
    for medicine_id in SIX:
        assert engine.warning_words(T2D)[medicine_id] == NOTE
    # a correction works only for the disease written on it (decision 2026-11-17)
    assert engine.warning_words("MONDO_0004979").keys().isdisjoint(SIX)


# ---- asthma ----

def test_before_ipratropium_was_red_on_asthma(asthma):
    before, _ = asthma
    assert IPRATROPIUM in ids_in(before, "wrong_approvals_box")


def test_ipratropium_on_asthma_is_no_longer_red(asthma):
    _, after = asthma
    assert IPRATROPIUM not in engine.looks_wrong(ASTHMA)
    assert IPRATROPIUM not in ids_in(after, "wrong_approvals_box")
    cards = [c for part in after.values() if isinstance(part, list)
             for c in part if isinstance(c, dict) and c.get("id") == IPRATROPIUM]
    assert cards, "ipratropium is still on the page"
    assert all("warning" not in c for c in cards)


def test_nothing_else_on_the_asthma_page_changes(asthma):
    before, after = asthma
    assert strip_card(after, IPRATROPIUM) == strip_card(before, IPRATROPIUM)


# ---- type 2 diabetes ----

@pytest.mark.parametrize("medicine_id", sorted(SIX), ids=lambda m: SIX[m])
def test_each_of_the_six_cards_shows_the_red_sentence(diabetes, medicine_id):
    before, after = diabetes
    (old,) = [c for c in before["wider_group"] if c["id"] == medicine_id]
    (card,) = [c for c in after["wider_group"] if c["id"] == medicine_id]
    assert "warning" not in old
    assert card["warning"] == NOTE


def test_the_six_cards_stay_in_wider_group_and_the_red_box_names_them(diabetes):
    before, after = diabetes
    assert ids_in(after, "wider_group") == ids_in(before, "wider_group")
    # Ticket 3.16 (Q7), changed on purpose: the red box names the six. Before: none of them.
    assert set(SIX) <= set(ids_in(after, "wrong_approvals_box"))


def test_nothing_else_on_the_type_2_diabetes_page_changes(diabetes):
    before, after = diabetes
    for card in after["wider_group"]:
        if card["id"] in SIX:
            card.pop("warning")
    # Ticket 3.16 (Q7): the red box names the six too. Nothing else changes.
    after["wrong_approvals_box"] = [m for m in after["wrong_approvals_box"] if m not in SIX]
    assert after == before
