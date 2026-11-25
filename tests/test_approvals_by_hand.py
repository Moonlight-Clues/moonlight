"""Ticket 2.26. A hand-written list of missing approvals.

Kashish's decisions, 23 Nov:

1. A medicine whose official label names a disease, but which the database
   does not record as approved for it, is shown under Approved for that
   disease. The list is moonlight/approvals.json, written by hand. Each
   entry holds: medicine_id, name, disease_id, date, label (the
   regulator's own page).
2. The medicine is on the Approved tab's main list, in the order that list
   already uses (A to Z), and counted in the tab.
3. Its card carries, in her exact words: "This approval is missing from
   the database. We added it from the official label."
4. Its source link is the label in the file.
5. If the medicine is already on that page in another tab or box, it is
   shown only under Approved.
6. An entry works only for the disease written on it.
7. No new request to Open Targets. The name comes from the file. A protein
   path is shown only if the page already fetched one for that medicine.
8. Existing rules still win: a withdrawn medicine, or one on the
   corrections list, is not added.

Her first entries, dated 2026-11-23:
  - propranolol for essential tremor (MONDO_0003233). Before: on no tab.
  - methimazole for Graves disease (MONDO_0005364). Before: in the folded
    box "More medicines in trials".

Saved files only: fixtures/approvals_by_hand/ (see its README), and
fixtures/no_regulator/ for the answers that folder already held. No network.
"""

import copy
import json
import pathlib
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from moonlight import api, engine
from moonlight.engine import CHILD, PARENT, Neighbour, sort_into_tabs
from moonlight.fetch import Listed, OnList
from moonlight.filter import sort_paths
from moonlight.records import Disease, Medicine, MedicineForm, Path, Target
from source_2_53 import back_to_before  # ticket 2.53: Source record links
from source_3_11 import back_to_before as trials_back_to_before  # ticket 3.11: In trials links
from diagnostic_3_10 import back_to_before as tag_back_to_before  # ticket 3.10: the DIAGNOSTIC tag

ROOT = pathlib.Path(__file__).resolve().parent.parent
APPROVALS_FILE = ROOT / "moonlight" / "approvals.json"
CORRECTIONS_FILE = ROOT / "moonlight" / "corrections.json"
SAVED = ROOT / "fixtures" / "approvals_by_hand"
REUSED = ROOT / "fixtures" / "no_regulator"  # answers saved for ticket 2.17, the same data

# Kashish's words, exactly.
LINE = "This approval is missing from the database. We added it from the official label."

ESSENTIAL_TREMOR = "MONDO_0003233"
GRAVES = "MONDO_0005364"
PROPRANOLOL = "CHEMBL27"
METHIMAZOLE = "CHEMBL1515"
PROPYLTHIOURACIL = "CHEMBL1518"  # ticket 2.33 added it to the Graves disease page
PRIMIDONE = "CHEMBL856"  # ticket 2.54 (signed answer Q13) added it to essential tremor
PROPRANOLOL_LABEL = ("https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm"
                     "?setid=013a485a-4227-46ae-b19f-c550302fcb96")
METHIMAZOLE_LABEL = ("https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm"
                     "?setid=06bb4bcc-5e47-48b6-a76c-648f846704e8")
THE_DAY = "2026-11-23"
FIRST_ENTRIES = [
    {"medicine_id": PROPRANOLOL, "name": "Propranolol", "disease_id": ESSENTIAL_TREMOR,
     "date": THE_DAY, "label": PROPRANOLOL_LABEL},
    {"medicine_id": METHIMAZOLE, "name": "Methimazole", "disease_id": GRAVES,
     "date": THE_DAY, "label": METHIMAZOLE_LABEL},
]

# The two cards, exactly as /api/clues must send them.
PROPRANOLOL_CARD = {
    "id": PROPRANOLOL,
    "medicine": "Propranolol",
    "forms": ["Propranolol"],
    "proteins": [],  # the page fetched no protein path for it
    "reports": 1,  # its one report link on the disease's own list, as before
    "source": PROPRANOLOL_LABEL,
    "proof_note": LINE,
}
METHIMAZOLE_CARD = {
    "id": METHIMAZOLE,
    "medicine": "Methimazole",
    "forms": ["Methimazole"],
    "proteins": [],
    "reports": 13,  # its report links on the disease's own list
    "source": METHIMAZOLE_LABEL,
    "proof_note": LINE,
}

# ---- hand-built pieces for the rules ----

DISEASE = Disease("TEST_0000001", "test disease")
PROTEIN = Target("ENSG00000000001", "ABC1", "test protein", 0.8)
HAND_LABEL = "https://example.org/official-label"


def by_hand(medicine_id="CHEMBL9001", name="Handmedicine", disease_id=DISEASE.id,
            label=HAND_LABEL):
    return engine.HandApproval(medicine_id=medicine_id, name=name, disease_id=disease_id,
                               label=label)


def path(name, medicine_id, best="APPROVAL", link=None, withdrawn=False):
    form = MedicineForm(medicine_id, name, best_stage=best, disease_stage=link,
                        withdrawn=withdrawn)
    return Path(Medicine(name, (form,)), PROTEIN, DISEASE, ("INHIBITOR",), PROTEIN.score,
                (f"https://example.org/path/{medicine_id}",))


def listed(name, medicine_id, approved=True):
    return Listed(id=medicine_id, name=name, forms=((medicine_id, name),),
                  sources=(f"https://example.org/list/{medicine_id}",), approved=approved,
                  approval_sources=(f"https://example.org/list/{medicine_id}",),
                  regulator_record=True)


def on_list(name, medicine_id, best="APPROVAL", link="PHASE_3", withdrawn=False):
    form = MedicineForm(medicine_id, name, best_stage=best, disease_stage=link,
                        withdrawn=withdrawn)
    return OnList(medicine=Medicine(name, (form,)),
                  reports=((f"https://example.org/trial/{medicine_id}", link),), all_seen=True)


def everywhere(tabs):
    """Tab or box name -> the ids of its cards."""
    def clue_id(clue):
        first = clue.medicine.forms[0]
        return first.parent_id or first.id
    return {
        "approved": [medicine.id for medicine in tabs.approved],
        "narrower": [medicine.id for medicine in tabs.narrower],
        "wider_group": [medicine.id for medicine in tabs.wider_group],
        "being_studied": [clue_id(clue) for clue in tabs.being_studied],
        "new_clues": [clue_id(clue) for clue in tabs.new_clues],
        "more_in_trials": [medicine.id for medicine in tabs.more_in_trials],
        "new_in_trials": [medicine.id for medicine in tabs.new_in_trials],
    }


def only_under_approved(tabs, medicine_id):
    places = [place for place, ids in everywhere(tabs).items() if medicine_id in ids]
    return places == ["approved"] and everywhere(tabs)["approved"].count(medicine_id) == 1


# ---- the saved pages ----

def load(file):
    return json.loads(file.read_text(encoding="utf-8"))


def saved_post_json(body):
    """Stands in for fetch._post_json with the saved files."""
    assert set(body) == {"query", "variables"}
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


@pytest.fixture(autouse=True)
def offline():
    """Real HTTP is an error. Every question is answered from saved files."""
    api.forget_visitors()
    with patch("requests.request", side_effect=AssertionError("network used")), \
            patch("requests.post", side_effect=AssertionError("network used")), \
            patch("requests.get", side_effect=AssertionError("network used")), \
            patch("requests.sessions.Session.request",
                  side_effect=AssertionError("network used")), \
            patch("moonlight.fetch._post_json", side_effect=saved_post_json) as asked:
        yield asked
    api.forget_visitors()


def page(disease_id):
    """What /api/clues sends, from the saved answers and the REAL hand-written files."""
    response = TestClient(api.app).get("/api/clues", params={"disease_id": disease_id})
    assert response.status_code == 200
    return response.json()


def without_primidone():
    """Ticket 2.54, signed answer Q13. The real approvals file, less primidone
    for essential tremor, so the page is as the tests below knew it."""
    return patch.object(engine, "_read_approvals", return_value=[
        entry for entry in load(APPROVALS_FILE) if entry["medicine_id"] != PRIMIDONE])


def before(disease_id):
    """What main answered for this page before the ticket, from the same saved answers."""
    return load(SAVED / f"clues_before_2.26_{disease_id}.json")


def cards_naming(a_page, word):
    """(tab or box, card) for every card anywhere on the page that names the word."""
    return [(key, card) for key, part in a_page.items() if isinstance(part, list)
            for card in part if isinstance(card, dict) and word in json.dumps(card).lower()]


def page_with(paths=(), own=(), hand=(), wrong_file=(), disease=DISEASE, **more):
    """What /api/clues sends for a hand-built page."""
    found = api._Found(disease, sort_paths(paths), list(own), by_hand=list(hand), **more)
    with patch.object(api, "_find", return_value=found), \
            patch.object(engine, "_read_corrections", return_value=list(wrong_file)):
        response = TestClient(api.app).get("/api/clues", params={"disease_id": disease.id})
    assert response.status_code == 200
    return response.json()


# ---- the hand-written file ----

def test_the_line_is_kashishs_words_exactly():
    assert engine.ADDED_LINE == LINE


def test_the_real_file_holds_the_first_two_entries_first():
    # Ticket 2.30 added three entries after these. tests/test_approvals_batch.py
    # holds the whole file, entry for entry.
    assert load(APPROVALS_FILE)[:2] == FIRST_ENTRIES


def test_the_engine_reads_the_real_file():
    assert engine.approvals_by_hand()[:2] == [  # ticket 2.30 added three after these
        engine.HandApproval(PROPRANOLOL, "Propranolol", ESSENTIAL_TREMOR, PROPRANOLOL_LABEL),
        engine.HandApproval(METHIMAZOLE, "Methimazole", GRAVES, METHIMAZOLE_LABEL),
    ]


def test_the_ids_are_the_ones_open_targets_uses_in_the_saved_answers():
    for disease_id, name in ((ESSENTIAL_TREMOR, "essential tremor"), (GRAVES, "Graves disease")):
        record = load(SAVED / "disease" / f"{disease_id}.response.json")["data"]["disease"]
        assert (record["id"], record["name"]) == (disease_id, name)
    for disease_id, medicine_id, name in ((ESSENTIAL_TREMOR, PROPRANOLOL, "PROPRANOLOL"),
                                          (GRAVES, METHIMAZOLE, "METHIMAZOLE")):
        rows = load(SAVED / "disease_drugs" / f"{disease_id}.response.json")[
            "data"]["disease"]["drugAndClinicalCandidates"]["rows"]
        drugs = [row["drug"] for row in rows if row["drug"]["id"] == medicine_id]
        assert [drug["name"] for drug in drugs] == [name]
        assert drugs[0]["parentMolecule"] is None  # it is the medicine, not a tablet form


def test_the_first_entries_clash_with_no_existing_rule():
    wrong = {(entry["medicine_id"], entry["disease_id"]) for entry in load(CORRECTIONS_FILE)}
    for entry in FIRST_ENTRIES:
        assert (entry["medicine_id"], entry["disease_id"]) not in wrong
        # Not withdrawn in the saved answers: a black box warning is not a withdrawal.
        rows = load(SAVED / "disease_drugs" / f"{entry['disease_id']}.response.json")[
            "data"]["disease"]["drugAndClinicalCandidates"]["rows"]
        warnings = [warning["warningType"].lower() for row in rows
                    if row["drug"]["id"] == entry["medicine_id"]
                    for warning in row["drug"]["drugWarnings"]]
        assert "withdrawn" not in warnings


@pytest.mark.parametrize("change", [
    {"medicine_id": ""},
    {"name": ""},
    {"name": 7},
    {"disease_id": ""},
    {"date": "23 Nov"},
    {"label": ""},
    {"label": "http://example.org/not-https"},
    {"label": "dailymed.nlm.nih.gov"},
    {"doctor": "a name"},  # one thing too many
])
def test_an_entry_that_is_not_written_properly_is_refused(change):
    entry = dict(FIRST_ENTRIES[0], **change)
    with patch.object(engine, "_read_approvals", return_value=[entry]):
        with pytest.raises(ValueError):
            engine.approvals_by_hand()


@pytest.mark.parametrize("missing", ["medicine_id", "name", "disease_id", "date", "label"])
def test_an_entry_with_a_piece_missing_is_refused(missing):
    entry = {key: value for key, value in FIRST_ENTRIES[0].items() if key != missing}
    with patch.object(engine, "_read_approvals", return_value=[entry]):
        with pytest.raises(ValueError):
            engine.approvals_by_hand()


def test_a_file_that_is_not_a_list_is_refused():
    with patch.object(engine, "_read_approvals", return_value={"entries": []}):
        with pytest.raises(ValueError):
            engine.approvals_by_hand()


def test_the_same_medicine_and_disease_written_twice_differently_is_refused():
    twice = [FIRST_ENTRIES[0], dict(FIRST_ENTRIES[0], label="https://example.org/other")]
    with patch.object(engine, "_read_approvals", return_value=twice):
        with pytest.raises(ValueError):
            engine.approvals_by_hand()


def test_an_empty_file_adds_nothing():
    with patch.object(engine, "_read_approvals", return_value=[]):
        assert engine.approvals_by_hand() == []
        assert engine.added_by_hand(ESSENTIAL_TREMOR) == []


# ---- "An entry works only for the disease written on it." ----

def test_an_entry_is_handed_only_to_its_own_disease():
    # Ticket 2.54, signed answer Q13: primidone is the second entry for essential tremor.
    assert [entry.medicine_id for entry in engine.added_by_hand(ESSENTIAL_TREMOR)] == [
        PROPRANOLOL, PRIMIDONE]
    assert [entry.medicine_id for entry in engine.added_by_hand(GRAVES)] == [
        METHIMAZOLE, PROPYLTHIOURACIL]  # ticket 2.33 added the second
    assert engine.added_by_hand("MONDO_0005395") == []  # movement disorder, the wider group
    assert engine.added_by_hand(DISEASE.id) == []


def test_on_the_other_saved_page_neither_medicine_is_added():
    assert not [card for card in page(GRAVES)["approved"] if card["id"] == PROPRANOLOL]
    assert not cards_naming(page(ESSENTIAL_TREMOR), "methimazole")
    # Ticket 2.33 added propylthiouracil to the Graves disease page.
    for a_page, own in ((page(GRAVES), [METHIMAZOLE, PROPYLTHIOURACIL]),
                        # Ticket 2.54, signed answer Q13: primidone, A to Z before propranolol.
                        (page(ESSENTIAL_TREMOR), [PRIMIDONE, PROPRANOLOL])):
        with_line = [card["id"] for _, card in cards_naming(a_page, LINE.lower())]
        assert with_line == own


# ---- the EXAMPLE, page 1: propranolol for essential tremor ----

def test_before_essential_tremor_had_no_approved_medicine_and_no_propranolol_card():
    old = before(ESSENTIAL_TREMOR)
    assert old["disease"] == {"id": ESSENTIAL_TREMOR, "name": "essential tremor"}
    assert old["approved"] == []
    assert cards_naming(old, "propranolol") == []


def test_propranolol_is_the_approved_list_of_essential_tremor():
    # Ticket 2.54, signed answer Q13: primidone's card is on this list too.
    approved = page(ESSENTIAL_TREMOR)["approved"]
    assert [card["id"] for card in approved] == [PRIMIDONE, PROPRANOLOL]
    assert approved[1] == PROPRANOLOL_CARD


def test_nothing_else_on_the_essential_tremor_page_changes():
    expected = copy.deepcopy(before(ESSENTIAL_TREMOR))
    expected["approved"] = [PROPRANOLOL_CARD]
    with without_primidone():  # Ticket 2.54, signed answer Q13
        assert back_to_before(trials_back_to_before(tag_back_to_before(page(ESSENTIAL_TREMOR)))) == expected


# ---- the EXAMPLE, page 2: methimazole for Graves disease ----

def test_before_methimazole_was_only_in_the_more_in_trials_box():
    old = before(GRAVES)
    assert old["disease"] == {"id": GRAVES, "name": "Graves disease"}
    assert [card["medicine"] for card in old["approved"]] == ["Ipodate", "Teprotumumab"]
    assert [key for key, _ in cards_naming(old, "methimazole")] == ["more_in_trials"]
    assert len(old["more_in_trials"]) == 18


def test_methimazole_is_on_the_approved_list_of_graves_disease_a_to_z():
    approved = page(GRAVES)["approved"]
    # Ticket 2.33 added propylthiouracil to this list.
    assert [card["medicine"] for card in approved] == [
        "Ipodate", "Methimazole", "Propylthiouracil", "Teprotumumab"]
    assert approved[1] == METHIMAZOLE_CARD


def test_methimazole_is_shown_only_under_approved():
    new = page(GRAVES)
    assert [key for key, _ in cards_naming(new, "methimazole")] == ["approved"]
    assert len(new["more_in_trials"]) == 16  # ticket 2.33 moved propylthiouracil out too


def test_nothing_else_on_the_graves_page_changes():
    old = before(GRAVES)
    expected = copy.deepcopy(old)
    # Ticket 2.33 added propylthiouracil's card. tests/test_label_limit_line.py pins it.
    new = page(GRAVES)
    assert new["approved"][2]["id"] == PROPYLTHIOURACIL
    expected["approved"] = [old["approved"][0], METHIMAZOLE_CARD, new["approved"][2],
                            old["approved"][1]]
    expected["more_in_trials"] = [card for card in old["more_in_trials"]
                                  if card["id"] not in (METHIMAZOLE, PROPYLTHIOURACIL)]
    # Ticket 2.28 added one key: the new clue that carries the opposite-way
    # line is named for the folded box. It is still in "new_clues", as before.
    expected["opposite_way_box"] = ["CHEMBL1201716"]
    # Ticket 2.42 added one key: ipodate and teprotumumab, with the "no
    # regulator record" line, are named for the new folded box. They are
    # still in "approved", as before.
    expected["no_regulator_box"] = ["CHEMBL1201243", "CHEMBL1743079"]
    # Ticket 2.54, signed answer Q5: thyrotropin, thyrotropin alfa and ipilimumab
    # are left out of New clues, and the wrong-way line counts them.
    expected["new_clues"] = [card for card in expected["new_clues"]
                             if card["id"] not in ("CHEMBL1201532", "CHEMBL1201533",
                                                   "CHEMBL1789844")]
    expected["wrong_way_line"] = engine.wrong_way_line(3)
    assert new == expected


# ---- "No new request to Open Targets." ----

@pytest.mark.parametrize("disease_id", [ESSENTIAL_TREMOR, GRAVES])
def test_the_page_asks_open_targets_the_same_questions_as_without_the_file(offline, disease_id):
    def questions():
        return sorted(json.dumps(call.args[0], sort_keys=True) for call in offline.call_args_list)

    page(disease_id)
    with_the_file = questions()
    offline.reset_mock()
    with patch.object(engine, "_read_approvals", return_value=[]):
        page(disease_id)
    assert with_the_file == questions()
    assert with_the_file  # the page did ask something


# ---- the card ----

def test_the_card_has_the_line_the_label_as_source_and_the_name_from_the_file():
    cards = page_with(hand=[by_hand()])["approved"]
    assert cards == [{
        "id": "CHEMBL9001",
        "medicine": "Handmedicine",
        "forms": ["Handmedicine"],
        "proteins": [],
        "reports": 0,
        "source": HAND_LABEL,
        "proof_note": LINE,
    }]


def test_the_card_has_no_box_label_and_no_red_warning():
    card = page_with(hand=[by_hand()])["approved"][0]
    assert "label" not in card
    assert "warning" not in card


def test_the_line_and_the_label_come_from_the_engine():
    medicine = sort_into_tabs(sort_paths([]), [], by_hand=[by_hand()]).approved[0]
    assert medicine.proof_note == LINE
    assert medicine.source_record == HAND_LABEL
    assert medicine.name == "Handmedicine"
    assert medicine.label is None  # it is in the main list, not in a box


def test_the_card_sits_a_to_z_among_the_others_and_is_counted():
    cards = page_with(own=[listed("ALPHAMEDICINE", "CHEMBL8001"),
                           listed("ZETAMEDICINE", "CHEMBL8002")],
                      hand=[by_hand()])["approved"]
    assert [card["medicine"] for card in cards] == [
        "Alphamedicine", "Handmedicine", "Zetamedicine"]
    assert len(cards) == 3  # the tab counts the cards of this list
    assert ["proof_note" in card and card["proof_note"] == LINE for card in cards] == [
        False, True, False]


# ---- "Show a protein path only if the page already fetched one." ----

def test_a_medicine_with_no_path_gets_none():
    assert page_with(hand=[by_hand()])["approved"][0]["proteins"] == []


def test_a_medicine_the_page_fetched_a_path_for_shows_it():
    card = page_with(paths=[path("HANDMEDICINE", "CHEMBL9001")], hand=[by_hand()])["approved"][0]
    assert [protein["symbol"] for protein in card["proteins"]] == ["ABC1"]
    assert card["proteins"][0]["direction"] == "down"
    assert card["medicine"] == "Handmedicine"  # still the name in the file
    assert card["source"] == HAND_LABEL
    assert card["proof_note"] == LINE


# ---- "already on that page in another tab or box: shown only under Approved" ----

def test_a_new_clue_moves_to_approved():
    paths = [path("HANDMEDICINE", "CHEMBL9001"), path("OTHERMEDICINE", "CHEMBL8003")]
    assert everywhere(sort_into_tabs(sort_paths(paths), []))["new_clues"] == [
        "CHEMBL9001", "CHEMBL8003"]
    tabs = sort_into_tabs(sort_paths(paths), [], by_hand=[by_hand()])
    assert only_under_approved(tabs, "CHEMBL9001")
    assert everywhere(tabs)["new_clues"] == ["CHEMBL8003"]


def test_a_medicine_in_trials_moves_to_approved():
    paths = [path("HANDMEDICINE", "CHEMBL9001", link="PHASE_3")]
    assert everywhere(sort_into_tabs(sort_paths(paths), []))["being_studied"] == ["CHEMBL9001"]
    tabs = sort_into_tabs(sort_paths(paths), [], by_hand=[by_hand()])
    assert only_under_approved(tabs, "CHEMBL9001")


def test_a_medicine_in_the_more_in_trials_box_moves_to_approved():
    trials = [on_list("HANDMEDICINE", "CHEMBL9001"), on_list("OTHERMEDICINE", "CHEMBL8003")]
    assert everywhere(sort_into_tabs(sort_paths([]), [], on_list=trials))["more_in_trials"] == [
        "CHEMBL9001", "CHEMBL8003"]
    tabs = sort_into_tabs(sort_paths([]), [], on_list=trials, by_hand=[by_hand()])
    assert only_under_approved(tabs, "CHEMBL9001")
    assert everywhere(tabs)["more_in_trials"] == ["CHEMBL8003"]


def test_a_medicine_in_the_new_in_trials_box_moves_to_approved():
    trials = [on_list("HANDMEDICINE", "CHEMBL9001", best="PHASE_3")]
    assert everywhere(sort_into_tabs(sort_paths([]), [], on_list=trials))["new_in_trials"] == [
        "CHEMBL9001"]
    tabs = sort_into_tabs(sort_paths([]), [], on_list=trials, by_hand=[by_hand()])
    assert only_under_approved(tabs, "CHEMBL9001")


@pytest.mark.parametrize("role, box", [(CHILD, "narrower"), (PARENT, "wider_group")])
def test_a_medicine_in_a_folded_approved_box_moves_to_the_main_list(role, box):
    near = [Neighbour(role, Disease("TEST_0000003", "a nearby disease"),
                      (listed("HANDMEDICINE", "CHEMBL9001"),), ())]
    assert everywhere(sort_into_tabs(sort_paths([]), [], neighbours=near))[box] == ["CHEMBL9001"]
    tabs = sort_into_tabs(sort_paths([]), [], neighbours=near, by_hand=[by_hand()])
    assert only_under_approved(tabs, "CHEMBL9001")
    assert tabs.approved[0].label is None
    assert tabs.approved[0].proof_note == LINE


@pytest.mark.parametrize("best, link, group", [
    ("APPROVAL", "UNKNOWN", "unclear_link"),
    ("PHASE_2", None, "not_approved"),
])
def test_a_medicine_that_was_only_counted_as_left_out_is_no_longer_counted(best, link, group):
    paths = [path("HANDMEDICINE", "CHEMBL9001", best=best, link=link)]
    assert sort_into_tabs(sort_paths(paths), []).left_out[group] == 1
    tabs = sort_into_tabs(sort_paths(paths), [], by_hand=[by_hand()])
    assert only_under_approved(tabs, "CHEMBL9001")
    assert tabs.left_out == {"not_approved": 0, "unclear_link": 0}


# ---- "Existing rules still win." ----

def same_page(tabs, plain):
    return everywhere(tabs) == everywhere(plain) and tabs.left_out == plain.left_out


def test_a_medicine_a_path_says_was_withdrawn_is_not_added():
    paths = [path("HANDMEDICINE", "CHEMBL9001", withdrawn=True)]
    plain = sort_into_tabs(sort_paths(paths), [])
    tabs = sort_into_tabs(sort_paths(paths), [], by_hand=[by_hand()])
    assert tabs.approved == []
    assert same_page(tabs, plain)
    assert tabs.left_out["not_approved"] == 1


def test_a_medicine_the_diseases_own_list_says_was_withdrawn_is_not_added():
    gone = [listed("HANDMEDICINE", "CHEMBL9001", approved=False)]
    tabs = sort_into_tabs(sort_paths([]), [], withdrawn_listed=gone, by_hand=[by_hand()])
    assert tabs.approved == []
    assert same_page(tabs, sort_into_tabs(sort_paths([]), [], withdrawn_listed=gone))


def test_a_medicine_a_nearby_list_says_was_withdrawn_is_not_added():
    near = [Neighbour(PARENT, Disease("TEST_0000003", "a wider group"), (),
                      (listed("HANDMEDICINE", "CHEMBL9001", approved=False),))]
    tabs = sort_into_tabs(sort_paths([]), [], neighbours=near, by_hand=[by_hand()])
    assert tabs.approved == []
    assert same_page(tabs, sort_into_tabs(sort_paths([]), [], neighbours=near))


def test_a_medicine_on_the_corrections_list_for_this_disease_is_not_added():
    wrong = [{"medicine_id": PROPRANOLOL, "disease_id": ESSENTIAL_TREMOR, "date": THE_DAY,
              "note": engine.CORRECTION_NOTE}]
    with patch.object(engine, "_read_corrections", return_value=wrong):
        # Ticket 2.54, signed answer Q13: primidone is still added; propranolol is not.
        assert [entry.medicine_id for entry in engine.added_by_hand(ESSENTIAL_TREMOR)] == [
            PRIMIDONE]
        assert [entry.medicine_id for entry in engine.added_by_hand(GRAVES)] == [
            METHIMAZOLE, PROPYLTHIOURACIL]  # ticket 2.33 added the second
        with without_primidone():
            new = back_to_before(trials_back_to_before(tag_back_to_before(page(ESSENTIAL_TREMOR))))
    assert new == before(ESSENTIAL_TREMOR)  # the page is as it was before the ticket


def test_a_correction_for_another_disease_does_not_stop_the_entry():
    wrong = [{"medicine_id": PROPRANOLOL, "disease_id": GRAVES, "date": THE_DAY,
              "note": engine.CORRECTION_NOTE}]
    with patch.object(engine, "_read_corrections", return_value=wrong):
        assert [entry.medicine_id for entry in engine.added_by_hand(ESSENTIAL_TREMOR)] == [
            PROPRANOLOL, PRIMIDONE]  # Ticket 2.54, signed answer Q13


def test_an_approval_the_database_already_records_keeps_its_own_card():
    # Then nothing is missing from the database, so the line would not be true.
    own = [listed("HANDMEDICINE", "CHEMBL9001")]
    plain = page_with(own=own)
    assert page_with(own=own, hand=[by_hand()]) == plain
    assert "proof_note" not in plain["approved"][0]
    assert plain["approved"][0]["source"] == "https://example.org/list/CHEMBL9001"


def test_an_approval_a_path_already_records_keeps_its_own_card():
    paths = [path("HANDMEDICINE", "CHEMBL9001", link="APPROVAL")]
    plain = page_with(paths=paths)
    assert page_with(paths=paths, hand=[by_hand()]) == plain
    assert "proof_note" not in plain["approved"][0]


# ---- what must not change ----

def test_an_added_card_cannot_be_explained():
    found = api._Found(DISEASE, sort_paths([path("HANDMEDICINE", "CHEMBL9001")]), [],
                       by_hand=[by_hand()])
    with patch.object(api, "_find", return_value=found), \
            patch.object(api.explain, "explain", side_effect=AssertionError("Gemini asked")):
        response = TestClient(api.app).get(
            "/api/explain", params={"disease_id": DISEASE.id, "clue_id": "CHEMBL9001"})
    assert response.status_code == 404


def test_the_names_the_explainers_check_sees_are_as_they_were():
    trials = [on_list("HANDMEDICINE", "CHEMBL9001")]
    plain = api._Found(DISEASE, sort_paths([]), [], on_list=trials)
    added = api._Found(DISEASE, sort_paths([]), [], on_list=trials, by_hand=[by_hand()])
    assert [medicine.id for medicine in added.approved] == ["CHEMBL9001"]
    assert added.known_names == plain.known_names


def test_without_the_new_piece_sort_into_tabs_answers_as_before():
    paths = [path("HANDMEDICINE", "CHEMBL9001"), path("OTHERMEDICINE", "CHEMBL8003")]
    own = [listed("ALPHAMEDICINE", "CHEMBL8001")]
    assert sort_into_tabs(sort_paths(paths), own, by_hand=[]) == sort_into_tabs(
        sort_paths(paths), own)
