"""Ticket 2.34. Approvals by hand, fourth batch.

The ticket named seven medicines. Claude in the main window opened each
official label on 24 Nov 2026 and read the indication. Five are added, at
the end of moonlight/approvals.json, dated 2026-11-24, in the ticket's order:

  - eculizumab for myasthenia gravis (MONDO_0009688), limited
  - secukinumab for hidradenitis suppurativa (MONDO_0006559)
  - bimekizumab for hidradenitis suppurativa (MONDO_0006559)
  - elafibranor for primary biliary cholangitis (MONDO_0005388), limited
  - seladelpar for primary biliary cholangitis (MONDO_0005388), limited

Ticket 2.34b added a sixth, after those five (the main window's answer of
24 Nov to the ticket's STOP AND ASK: of the two pages, this one):

  - avatrombopag for autoimmune thrombocytopenic purpura (MONDO_0008558),
    limited. No page is named "immune thrombocytopenia". This is the one
    the search for those words finds. The wider page, "autoimmune
    thrombocytopenia" (MONDO_0019098), gets no entry.

One is left out for good (the main window, 24 Nov):

  - givosiran for acute hepatic porphyria. The database already records
    the approval on the list of its page "Acute hepatic porphyria"
    (Orphanet_95157), so the hand-added line would be untrue there.

The EXAMPLE is the primary biliary cholangitis page: elafibranor and
seladelpar are each under Approved, A to Z, each with two grey lines, and
no longer in a trials box or list.

Saved files only. Myasthenia gravis, hidradenitis suppurativa, autoimmune
thrombocytopenic purpura and acute hepatic porphyria: each disease's own list, asked live on
2026-11-24 (Open Targets data 26.09) with fetch.py's own question, in
fixtures/approvals_by_hand/disease_drugs/. Primary biliary cholangitis:
the whole search ticket 2.21 saved in fixtures/more_in_trials/. Its own
list is letter for letter the live answer of 2026-11-24, so it was not
saved again. No network.
"""

import copy
import json
import pathlib
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from moonlight import api, engine

import test_approvals_batch as second_batch
import test_approvals_by_hand as first_batch
import test_label_limit_line as limited_batch
import test_more_in_trials as pbc_page

ROOT = pathlib.Path(__file__).resolve().parent.parent
APPROVALS_FILE = ROOT / "moonlight" / "approvals.json"
CORRECTIONS_FILE = ROOT / "moonlight" / "corrections.json"
LEFT_OUT_FILE = ROOT / "moonlight" / "left_out.json"
NEW_LISTS = ROOT / "fixtures" / "approvals_by_hand" / "disease_drugs"
PBC_LISTS = ROOT / "fixtures" / "more_in_trials" / "disease_drugs"  # ticket 2.21's

# Kashish's words, exactly. This ticket changes neither line.
ADDED_LINE = "This approval is missing from the database. We added it from the official label."
LIMITED_LINE = "The label covers only some people with this disease."
THE_DAY = "2026-11-24"

MYASTHENIA = "MONDO_0009688"  # myasthenia gravis
HIDRADENITIS = "MONDO_0006559"  # hidradenitis suppurativa
PBC = "MONDO_0005388"  # primary biliary cholangitis
ITP = "MONDO_0008558"  # autoimmune thrombocytopenic purpura
SAVED_LISTS = {MYASTHENIA: NEW_LISTS, HIDRADENITIS: NEW_LISTS, PBC: PBC_LISTS,
               ITP: NEW_LISTS}

ECULIZUMAB = "CHEMBL1201828"
SECUKINUMAB = "CHEMBL1743068"
BIMEKIZUMAB = "CHEMBL4297700"
ELAFIBRANOR = "CHEMBL3707395"
SELADELPAR = "CHEMBL230158"
SELADELPAR_TABLET = "CHEMBL3989960"  # seladelpar lysine
AVATROMBOPAG = "CHEMBL2103883"
AVATROMBOPAG_TABLET = "CHEMBL2105758"  # avatrombopag maleate

ECULIZUMAB_LABEL = ("https://www.accessdata.fda.gov/drugsatfda_docs/label/2026/"
                    "125166s454lbl.pdf")
SECUKINUMAB_LABEL = ("https://www.accessdata.fda.gov/drugsatfda_docs/label/2026/"
                     "761349s011lbl.pdf")
BIMEKIZUMAB_LABEL = ("https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm"
                     "?setid=26b88358-871f-4c80-9d80-b2fb16477f81")
ELAFIBRANOR_LABEL = ("https://www.accessdata.fda.gov/drugsatfda_docs/nda/2024/"
                     "218860Orig1s000Lbl.pdf")
SELADELPAR_LABEL = ("https://www.accessdata.fda.gov/drugsatfda_docs/label/2026/"
                    "217899s002lbl.pdf")
AVATROMBOPAG_LABEL = ("https://www.accessdata.fda.gov/drugsatfda_docs/label/2026/"
                      "210238Orig1s010lbl.pdf")

FIRST_TEN = limited_batch.FIRST_EIGHT + limited_batch.NEW_TWO
FOURTH_BATCH = [
    {"medicine_id": ECULIZUMAB, "name": "Eculizumab", "disease_id": MYASTHENIA,
     "date": THE_DAY, "label": ECULIZUMAB_LABEL, "limited": True},
    {"medicine_id": SECUKINUMAB, "name": "Secukinumab", "disease_id": HIDRADENITIS,
     "date": THE_DAY, "label": SECUKINUMAB_LABEL},
    {"medicine_id": BIMEKIZUMAB, "name": "Bimekizumab", "disease_id": HIDRADENITIS,
     "date": THE_DAY, "label": BIMEKIZUMAB_LABEL},
    {"medicine_id": ELAFIBRANOR, "name": "Elafibranor", "disease_id": PBC,
     "date": THE_DAY, "label": ELAFIBRANOR_LABEL, "limited": True},
    {"medicine_id": SELADELPAR, "name": "Seladelpar", "disease_id": PBC,
     "date": THE_DAY, "label": SELADELPAR_LABEL, "limited": True},
]
ECULIZUMAB_ENTRY, SECUKINUMAB_ENTRY, BIMEKIZUMAB_ENTRY, ELAFIBRANOR_ENTRY, SELADELPAR_ENTRY = \
    FOURTH_BATCH
# Ticket 2.34b: the sixteenth entry.
AVATROMBOPAG_ENTRY = {"medicine_id": AVATROMBOPAG, "name": "Avatrombopag", "disease_id": ITP,
                      "date": THE_DAY, "label": AVATROMBOPAG_LABEL, "limited": True}
ALL_NEW = FOURTH_BATCH + [AVATROMBOPAG_ENTRY]
FIRST_FIFTEEN = FIRST_TEN + FOURTH_BATCH
TABLETS = {SELADELPAR: [(SELADELPAR_TABLET, "SELADELPAR LYSINE")],
           AVATROMBOPAG: [(AVATROMBOPAG_TABLET, "AVATROMBOPAG MALEATE")]}
# No whole search is saved for these three diseases.
ON_OWN_LIST_ONLY = FOURTH_BATCH[:3] + [AVATROMBOPAG_ENTRY]


def names(value):
    """A test's short name: the medicine's, for an entry."""
    return value["name"] if isinstance(value, dict) else None


# The one left out. Its ids, as the saved list writes them.
GIVOSIRAN = "CHEMBL4297760"
GIVOSIRAN_SODIUM = "CHEMBL4594265"
ACUTE_HEPATIC_PORPHYRIA = "Orphanet_95157"
NOT_ADDED_LISTS = {ACUTE_HEPATIC_PORPHYRIA: NEW_LISTS}

# The cards, exactly as /api/clues must send them.
ECULIZUMAB_CARD = {
    "id": ECULIZUMAB,
    "medicine": "Eculizumab",
    "forms": ["Eculizumab"],
    "proteins": [],  # no protein search is saved for this disease
    "reports": 4,  # its report links on the disease's own saved list
    "source": ECULIZUMAB_LABEL,
    "proof_note": ADDED_LINE,
    "limit_note": LIMITED_LINE,
}
SECUKINUMAB_CARD = {
    "id": SECUKINUMAB,
    "medicine": "Secukinumab",
    "forms": ["Secukinumab"],
    "proteins": [],
    "reports": 9,
    "source": SECUKINUMAB_LABEL,
    "proof_note": ADDED_LINE,
}
BIMEKIZUMAB_CARD = {
    "id": BIMEKIZUMAB,
    "medicine": "Bimekizumab",
    "forms": ["Bimekizumab"],
    "proteins": [],
    "reports": 5,
    "source": BIMEKIZUMAB_LABEL,
    "proof_note": ADDED_LINE,
}
AVATROMBOPAG_CARD = {
    "id": AVATROMBOPAG,
    "medicine": "Avatrombopag",
    "forms": ["Avatrombopag"],  # its tablet form has no row on this list
    "proteins": [],
    "reports": 13,
    "source": AVATROMBOPAG_LABEL,
    "proof_note": ADDED_LINE,
    "limit_note": LIMITED_LINE,
}
OWN_LIST_CARDS = {ECULIZUMAB: ECULIZUMAB_CARD, SECUKINUMAB: SECUKINUMAB_CARD,
                  BIMEKIZUMAB: BIMEKIZUMAB_CARD, AVATROMBOPAG: AVATROMBOPAG_CARD}
# On the whole saved page. Everything but the last three lines is what the
# In trials card already said about the medicine.
ELAFIBRANOR_CARD = {
    "id": ELAFIBRANOR,
    "medicine": "Elafibranor",
    "forms": ["Elafibranor"],
    "proteins": [
        {"symbol": "PPARA", "points": 44, "direction": "up", "machine": 1,
         "piece_of_machine": False},
        {"symbol": "PPARD", "points": 42, "direction": "up", "machine": 2,
         "piece_of_machine": False}],
    "reports": 38,
    "source": ELAFIBRANOR_LABEL,
    "proof_note": ADDED_LINE,
    "limit_note": LIMITED_LINE,
}
SELADELPAR_CARD = {
    "id": SELADELPAR,
    "medicine": "Seladelpar",
    "forms": ["Seladelpar", "Seladelpar Lysine"],
    "proteins": [
        {"symbol": "PPARD", "points": 42, "direction": "up", "machine": 1,
         "piece_of_machine": False}],
    "reports": 14,
    "source": SELADELPAR_LABEL,
    "proof_note": ADDED_LINE,
    "limit_note": LIMITED_LINE,
}


def load(file):
    return json.loads(file.read_text(encoding="utf-8"))


def saved_rows(disease_id, folders=SAVED_LISTS):
    answer = load(folders[disease_id] / f"{disease_id}.response.json")
    assert answer["data"]["disease"]["id"] == disease_id
    return answer["data"]["disease"]["drugAndClinicalCandidates"]["rows"]


def saved_post_json(body):
    """Stands in for fetch._post_json: ticket 2.21's whole saved search for
    primary biliary cholangitis, and the lists in fixtures/approvals_by_hand/."""
    try:
        return pbc_page.saved_post_json(body)
    except FileNotFoundError:
        return first_batch.saved_post_json(body)


@pytest.fixture(autouse=True)
def offline():
    """Real HTTP is an error. Every question is answered from saved files."""
    api.forget_visitors()
    with patch("requests.request", side_effect=AssertionError("network used")), \
            patch("requests.post", side_effect=AssertionError("network used")), \
            patch("requests.get", side_effect=AssertionError("network used")), \
            patch("requests.sessions.Session.request",
                  side_effect=AssertionError("network used")), \
            patch("moonlight.fetch._post_json", side_effect=saved_post_json):
        yield
    api.forget_visitors()


def page(entries=None):
    """What /api/clues sends for primary biliary cholangitis: with the REAL
    file, or with these entries."""
    api.forget_visitors()
    if entries is None:
        response = TestClient(api.app).get("/api/clues", params={"disease_id": PBC})
    else:
        with patch.object(engine, "_read_approvals", return_value=entries):
            response = TestClient(api.app).get("/api/clues", params={"disease_id": PBC})
    assert response.status_code == 200
    return response.json()


def tabs_from_own_list(disease_id, entries=None):
    """The tabs from the disease's own saved list alone: with the REAL file,
    or with these entries."""
    if entries is None:
        hand = engine.added_by_hand(disease_id)
    else:
        with patch.object(engine, "_read_approvals", return_value=entries):
            hand = engine.added_by_hand(disease_id)
    return second_batch.tabs_for(disease_id, hand)


# ---- the hand-written file, entry for entry ----

def test_the_real_file_holds_the_first_ten_entries_then_the_five_then_avatrombopag():
    # Ticket 2.41's six sit between the five and avatrombopag (entries 15 to 20).
    # tests/test_label_batch.py holds them.
    assert load(APPROVALS_FILE)[:15] == FIRST_TEN + FOURTH_BATCH
    assert load(APPROVALS_FILE)[21:] == [AVATROMBOPAG_ENTRY]
    assert len(load(APPROVALS_FILE)) == 22


def test_the_first_ten_entries_are_written_as_they_were():
    assert load(APPROVALS_FILE)[:10] == FIRST_TEN
    assert [entry["date"] for entry in FIRST_TEN] == ["2026-11-23"] * 10


def test_the_new_entries_are_dated_the_day_the_labels_were_read():
    # Ticket 2.41's six (entries 15 to 20) are left out of this batch's slice.
    assert [entry["date"] for entry in load(APPROVALS_FILE)[10:15] + load(APPROVALS_FILE)[21:]] \
        == [THE_DAY] * 6


def test_four_new_entries_are_limited_and_two_are_not():
    new = load(APPROVALS_FILE)[10:15] + load(APPROVALS_FILE)[21:]  # not ticket 2.41's six
    assert [entry["name"] for entry in new if entry.get("limited") is True] == [
        "Eculizumab", "Elafibranor", "Seladelpar", "Avatrombopag"]
    assert [entry["name"] for entry in new if "limited" not in entry] == [
        "Secukinumab", "Bimekizumab"]


def test_the_engine_reads_the_six_new_entries():
    # Not ticket 2.41's six (entries 15 to 20).
    assert engine.approvals_by_hand()[10:15] + engine.approvals_by_hand()[21:] == [
        engine.HandApproval(ECULIZUMAB, "Eculizumab", MYASTHENIA, ECULIZUMAB_LABEL,
                            limited=True),
        engine.HandApproval(SECUKINUMAB, "Secukinumab", HIDRADENITIS, SECUKINUMAB_LABEL),
        engine.HandApproval(BIMEKIZUMAB, "Bimekizumab", HIDRADENITIS, BIMEKIZUMAB_LABEL),
        engine.HandApproval(ELAFIBRANOR, "Elafibranor", PBC, ELAFIBRANOR_LABEL, limited=True),
        engine.HandApproval(SELADELPAR, "Seladelpar", PBC, SELADELPAR_LABEL, limited=True),
        engine.HandApproval(AVATROMBOPAG, "Avatrombopag", ITP, AVATROMBOPAG_LABEL,
                            limited=True)]


def test_each_new_entry_is_handed_only_to_its_own_disease():
    # Ticket 2.41 added ravulizumab after eculizumab for myasthenia gravis.
    assert [entry.medicine_id for entry in engine.added_by_hand(MYASTHENIA)][:1] == [ECULIZUMAB]
    assert [entry.medicine_id for entry in engine.added_by_hand(HIDRADENITIS)] == [
        SECUKINUMAB, BIMEKIZUMAB]
    assert [entry.medicine_id for entry in engine.added_by_hand(PBC)] == [
        ELAFIBRANOR, SELADELPAR]
    assert [entry.medicine_id for entry in engine.added_by_hand(ITP)] == [AVATROMBOPAG]
    new = {entry["medicine_id"] for entry in ALL_NEW}
    # Not to a narrower disease, a wider group, or an earlier batch's disease.
    others = ["MONDO_0018324", "MONDO_0018325", "MONDO_0006866", "MONDO_0000590",
              "MONDO_0024516", "MONDO_0002260", "MONDO_0007329", "MONDO_0004868",
              # the three wider pages of autoimmune thrombocytopenic purpura
              "MONDO_0019098", "MONDO_0043768", "MONDO_0004680"]
    others += sorted({entry["disease_id"] for entry in FIRST_TEN})
    for other in others:
        assert not new & {entry.medicine_id for entry in engine.added_by_hand(other)}


# ---- "Find each medicine's id ... Parent medicine id, not a salt form's." ----

@pytest.mark.parametrize("entry", ALL_NEW, ids=names)
def test_the_id_is_the_one_open_targets_uses_in_the_saved_list(entry):
    tablets = TABLETS.get(entry["medicine_id"], [])
    drugs = {row["drug"]["id"]: row["drug"] for row in saved_rows(entry["disease_id"])}
    drug = drugs[entry["medicine_id"]]
    assert drug["name"] == entry["name"].upper()
    assert drug["parentMolecule"] is None  # the medicine itself, not a tablet form
    assert [(form["id"], form["name"]) for form in drug["childMolecules"]] == tablets
    for tablet_id, _ in tablets:
        assert tablet_id not in drugs  # the tablet form has no row of its own


def test_the_saved_lists_are_the_diseases_own():
    assert len(saved_rows(MYASTHENIA)) == 77
    assert len(saved_rows(HIDRADENITIS)) == 77
    assert len(saved_rows(PBC)) == 51
    assert len(saved_rows(ITP)) == 105


@pytest.mark.parametrize("entry", ALL_NEW, ids=names)
def test_the_database_records_no_approval_on_the_list_so_the_line_is_true(entry):
    family = [entry["medicine_id"]] + [
        tablet_id for tablet_id, _ in TABLETS.get(entry["medicine_id"], [])]
    rows = [row for row in saved_rows(entry["disease_id"])
            if row["drug"]["id"] in family
            or (row["drug"]["parentMolecule"] or {}).get("id") in family]
    assert [row["drug"]["id"] for row in rows] == [entry["medicine_id"]]
    assert rows[0]["maxClinicalStage"] == "PHASE_3"  # in trials, all six
    assert "APPROVAL" not in [report["clinicalStage"] for report in rows[0]["clinicalReports"]]


@pytest.mark.parametrize("entry, warnings", [
    (ECULIZUMAB_ENTRY, ["Black Box Warning", "Black Box Warning"]), (SECUKINUMAB_ENTRY, []),
    (BIMEKIZUMAB_ENTRY, []), (ELAFIBRANOR_ENTRY, []), (SELADELPAR_ENTRY, []),
    (AVATROMBOPAG_ENTRY, [])], ids=names)
def test_none_is_hidden_by_the_older_withdrawn_flag(entry, warnings):
    drug = [row["drug"] for row in saved_rows(entry["disease_id"])
            if row["drug"]["id"] == entry["medicine_id"]][0]
    found = [warning["warningType"] for one in [drug] + drug["childMolecules"]
             for warning in one["drugWarnings"]]
    assert found == warnings
    assert "withdrawn" not in [warning.lower() for warning in found]


def test_the_new_entries_clash_with_no_existing_rule():
    ids = {entry["medicine_id"] for entry in ALL_NEW} | {SELADELPAR_TABLET, AVATROMBOPAG_TABLET}
    for file in (CORRECTIONS_FILE, LEFT_OUT_FILE):
        assert not [one for one in load(file) if one["medicine_id"] in ids]
    assert engine.approvals_left_out() == []


def test_no_entry_in_the_whole_file_clashes_or_is_written_twice():
    entries = load(APPROVALS_FILE)
    pairs = [(entry["medicine_id"], entry["disease_id"]) for entry in entries]
    assert len(set(pairs)) == len(pairs)
    for file in (CORRECTIONS_FILE, LEFT_OUT_FILE):
        assert not set(pairs) & {(one["medicine_id"], one["disease_id"]) for one in load(file)}


def test_each_label_link_is_the_tickets_and_a_regulators():
    assert [entry["label"] for entry in
            load(APPROVALS_FILE)[10:15] + load(APPROVALS_FILE)[21:]] == [  # not 2.41's six
        ECULIZUMAB_LABEL, SECUKINUMAB_LABEL, BIMEKIZUMAB_LABEL, ELAFIBRANOR_LABEL,
        SELADELPAR_LABEL, AVATROMBOPAG_LABEL]
    for entry in ALL_NEW:
        assert entry["label"].startswith(("https://www.accessdata.fda.gov/drugsatfda_docs/",
                                          "https://dailymed.nlm.nih.gov/dailymed/"))


# ---- eculizumab, secukinumab, bimekizumab and avatrombopag, on their diseases' own
# ---- saved lists ----

@pytest.mark.parametrize("entry", ON_OWN_LIST_ONLY, ids=names)
def test_before_each_was_in_the_more_in_trials_box_and_not_under_approved(entry):
    earlier = FIRST_TEN if entry in FOURTH_BATCH else FIRST_FIFTEEN
    places = first_batch.everywhere(tabs_from_own_list(entry["disease_id"], earlier))
    assert [place for place, ids in places.items() if entry["medicine_id"] in ids] == [
        "more_in_trials"]


@pytest.mark.parametrize("entry", ON_OWN_LIST_ONLY, ids=names)
def test_each_is_now_only_under_approved_with_the_line_and_its_label(entry):
    tabs = tabs_from_own_list(entry["disease_id"])
    assert first_batch.only_under_approved(tabs, entry["medicine_id"])
    card = [medicine for medicine in tabs.approved if medicine.id == entry["medicine_id"]][0]
    assert card.name == entry["name"]
    assert card.proof_note == ADDED_LINE
    assert card.source_record == entry["label"]
    assert card.label is None  # the main list, not a folded box
    assert api._approved_json(card) == OWN_LIST_CARDS[entry["medicine_id"]]


@pytest.mark.parametrize("disease_id, added, a_to_z", [
    (MYASTHENIA, [ECULIZUMAB], [
        "AMBENONIUM", "AMIFAMPRIDINE", "Eculizumab", "EDROPHONIUM", "EFGARTIGIMOD ALFA",
        "GUANIDINE", "NEOSTIGMINE", "NIPOCALIMAB", "PRALIDOXIME", "PYRIDOSTIGMINE",
        "ROZANOLIXIZUMAB", "ZILUCOPLAN", "ZILUCOPLAN SODIUM"]),
    (HIDRADENITIS, [BIMEKIZUMAB, SECUKINUMAB], ["ADALIMUMAB", "Bimekizumab", "Secukinumab"]),
    (ITP, [AVATROMBOPAG], [
        "Avatrombopag", "CORTISONE ACETATE", "DEXAMETHASONE", "DEXAMETHASONE PHOSPHORIC ACID",
        "ELTROMBOPAG", "ESOMEPRAZOLE", "FOSTAMATINIB", "GMA-161", "HUMAN IMMUNOGLOBULIN G",
        "PREDNISONE", "RILZABRUTINIB", "ROMIPLOSTIM", "VALZIFLOCEPT", "VONOPRAZAN"]),
], ids=["myasthenia gravis", "hidradenitis suppurativa",
        "autoimmune thrombocytopenic purpura"])
def test_the_approved_list_is_a_to_z_and_every_other_card_stays_where_it_was(
        disease_id, added, a_to_z):
    before = tabs_from_own_list(disease_id, FIRST_TEN)
    # Ticket 2.41 added ravulizumab for myasthenia gravis: this batch's entries are used.
    tabs = tabs_from_own_list(disease_id, FIRST_TEN + ALL_NEW)
    assert [medicine.name for medicine in tabs.approved] == a_to_z
    assert [name.lower() for name in a_to_z] == sorted(name.lower() for name in a_to_z)
    assert len(tabs.approved) == len(before.approved) + len(added)
    assert sorted(medicine.id for medicine in tabs.approved if medicine.proof_note == ADDED_LINE) \
        == sorted(added)
    for place, ids in first_batch.everywhere(before).items():
        if place != "approved":
            assert first_batch.everywhere(tabs)[place] == [i for i in ids if i not in added]


def test_eculizumab_carries_the_only_some_people_line():
    # Ticket 2.41 added ravulizumab, also limited: this batch's file is used.
    tabs = tabs_from_own_list(MYASTHENIA, FIRST_TEN + FOURTH_BATCH)
    assert [medicine.id for medicine in tabs.approved if medicine.limit_note] == [ECULIZUMAB]
    card = [medicine for medicine in tabs.approved if medicine.id == ECULIZUMAB][0]
    assert card.limit_note == LIMITED_LINE
    sent = api._approved_json(card)
    assert list(sent).index("proof_note") < list(sent).index("limit_note")


def test_avatrombopag_carries_the_only_some_people_line():
    tabs = tabs_from_own_list(ITP)
    assert [medicine.id for medicine in tabs.approved if medicine.limit_note] == [AVATROMBOPAG]
    card = [medicine for medicine in tabs.approved if medicine.id == AVATROMBOPAG][0]
    assert card.limit_note == LIMITED_LINE
    sent = api._approved_json(card)
    assert list(sent).index("proof_note") < list(sent).index("limit_note")


def test_the_wider_page_autoimmune_thrombocytopenia_gets_no_entry():
    assert engine.added_by_hand("MONDO_0019098") == []
    assert [entry["disease_id"] for entry in load(APPROVALS_FILE)
            if entry["medicine_id"] == AVATROMBOPAG] == [ITP]


def test_secukinumab_and_bimekizumab_do_not_carry_it():
    tabs = tabs_from_own_list(HIDRADENITIS)
    assert [medicine.id for medicine in tabs.approved if medicine.limit_note] == []
    for medicine_id in (SECUKINUMAB, BIMEKIZUMAB):
        card = [medicine for medicine in tabs.approved if medicine.id == medicine_id][0]
        assert card.limit_note is None
        assert "limit_note" not in api._approved_json(card)
        assert LIMITED_LINE not in json.dumps(api._approved_json(card))


# ---- the EXAMPLE, on the whole saved page: primary biliary cholangitis ----

def test_before_elafibranor_and_seladelpar_were_only_on_the_in_trials_list():
    old = page(FIRST_TEN)
    assert old["disease"] == {"id": PBC, "name": "primary biliary cholangitis"}
    assert [card["medicine"] for card in old["approved"]] == ["Taurursodiol", "Ursodiol"]
    assert [card["medicine"] for card in old["being_studied"]] == pbc_page.PBC_LIST_7
    for word in ("elafibranor", "seladelpar"):
        assert [key for key, _ in first_batch.cards_naming(old, word)] == ["being_studied"]
    assert limited_batch.cards_with_the_key(old) == []


def test_elafibranor_and_seladelpar_are_each_under_approved_a_to_z():
    new = page()
    assert [card["medicine"] for card in new["approved"]] == [
        "Elafibranor", "Seladelpar", "Taurursodiol", "Ursodiol"]
    assert new["approved"][0] == ELAFIBRANOR_CARD
    assert new["approved"][1] == SELADELPAR_CARD


def test_each_has_the_two_grey_lines_in_order_and_its_label_as_source():
    approved = page()["approved"]
    for card, label in ((approved[0], ELAFIBRANOR_LABEL), (approved[1], SELADELPAR_LABEL)):
        assert card["proof_note"] == ADDED_LINE
        assert card["limit_note"] == LIMITED_LINE
        keys = list(card)
        assert keys.index("proof_note") < keys.index("limit_note")
        assert card["source"] == label
        assert "trial_phase" not in card and "ending" not in card  # not a trials card
        assert "warning" not in card and "label" not in card and "withdrawal_note" not in card
    assert limited_batch.cards_with_the_key(page()) == [
        ("approved", ELAFIBRANOR), ("approved", SELADELPAR)]


def test_they_are_no_longer_in_a_trials_box_or_list_and_nothing_else_changes():
    old = page(FIRST_TEN)
    new = page()
    for word in ("elafibranor", "seladelpar"):
        assert [key for key, _ in first_batch.cards_naming(new, word)] == ["approved"]
    assert [card["medicine"] for card in new["being_studied"]] == [
        "Saroglitazar", "Ustekinumab", "Fenofibrate", "Bezafibrate", "Pemafibrate"]
    expected = copy.deepcopy(old)
    expected["approved"] = [ELAFIBRANOR_CARD, SELADELPAR_CARD] + old["approved"]
    expected["being_studied"] = [card for card in old["being_studied"]
                                 if card["id"] not in (ELAFIBRANOR, SELADELPAR)]
    assert len(expected["being_studied"]) == 5
    assert new == expected
    assert len(new["more_in_trials"]) == 26 and len(new["new_in_trials"]) == 10  # as before


# ---- STOP AND ASK: the entry left out ----

def test_givosiran_has_no_entry_in_the_hand_written_file():
    for entry in load(APPROVALS_FILE):
        assert entry["medicine_id"] not in (GIVOSIRAN, GIVOSIRAN_SODIUM)
        assert entry["name"] != "Givosiran"


def test_the_database_already_records_givosirans_approval_for_acute_hepatic_porphyria():
    """ "If the database already records an approval for a medicine on that
    disease's list ... Leave that entry out and say so." """
    rows = {row["drug"]["id"]: row
            for row in saved_rows(ACUTE_HEPATIC_PORPHYRIA, NOT_ADDED_LISTS)}
    assert sorted(rows) == sorted([GIVOSIRAN, GIVOSIRAN_SODIUM])  # the whole list
    assert rows[GIVOSIRAN]["drug"]["name"] == "GIVOSIRAN"
    assert rows[GIVOSIRAN]["maxClinicalStage"] == "APPROVAL"
    assert rows[GIVOSIRAN_SODIUM]["maxClinicalStage"] == "APPROVAL"
    assert ("APPROVAL", "FDA") in {(report["clinicalStage"], report["source"])
                                   for report in rows[GIVOSIRAN_SODIUM]["clinicalReports"]}


def test_givosiran_is_under_approved_there_already_without_a_hand_added_line():
    tabs = tabs_from_own_list(ACUTE_HEPATIC_PORPHYRIA)
    assert first_batch.only_under_approved(tabs, GIVOSIRAN)
    assert [medicine.proof_note for medicine in tabs.approved
            if medicine.proof_note == ADDED_LINE] == []
