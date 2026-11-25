"""Ticket 2.25. Kashish's second red warning on tafamidis for AL amyloidosis.

Kashish's decision, 23 Nov: tafamidis sits under Approved for AL amyloidosis
(MONDO_0019438). She chose: keep the card in its place, add the second red
warning.

One new entry in moonlight/corrections.json does it. No code
changes. No other card on any page changes.

No network. The real corrections file is read as it is. The page is built
from the Open Targets answers saved live on 23 Nov (data 26.09) in
fixtures/tafamidis_warning/: fetch._post_json is swapped for a reader of
those files. In them the tafamidis Approved card's id is CHEMBL2103837, and
there is one tafamidis card, not two.
"""

import copy
import json
import pathlib
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from moonlight import api, engine
from moonlight.filter import sort_paths
from moonlight.records import Disease, Medicine, MedicineForm, Path, Target
from source_3_11 import back_to_before as trials_back_to_before  # ticket 3.11: In trials links

ROOT = pathlib.Path(__file__).resolve().parent.parent
CORRECTIONS_FILE = ROOT / "moonlight" / "corrections.json"
SAVED = ROOT / "fixtures" / "tafamidis_warning"

TAFAMIDIS = "CHEMBL2103837"
AL_AMYLOIDOSIS = "MONDO_0019438"
DARATUMUMAB = "CHEMBL1743007"  # ticket 2.30 added its approval for this disease by hand
AMYLOIDOSIS = "MONDO_0019065"  # the wider group "amyloidosis": another page, out of scope
THE_DAY = "2026-11-23"
# Kashish's words of 19 Nov, exactly (ticket 2.18).
SECOND_NOTE = ("This looks like a mistake in the database. The official label is "
               "for a different disease.")
THE_ENTRY = {"medicine_id": TAFAMIDIS, "disease_id": AL_AMYLOIDOSIS,
             "date": THE_DAY, "note": SECOND_NOTE}

PROTEIN = Target("ENSG00000000001", "ABC1", "test protein", 0.8)


@pytest.fixture(autouse=True)
def offline():
    """Real HTTP is an error."""
    api.forget_visitors()
    with patch("requests.request", side_effect=AssertionError("network used")), \
            patch("requests.post", side_effect=AssertionError("network used")), \
            patch("requests.get", side_effect=AssertionError("network used")), \
            patch("requests.sessions.Session.request",
                  side_effect=AssertionError("network used")):
        yield
    api.forget_visitors()


def real_corrections():
    return json.loads(CORRECTIONS_FILE.read_text(encoding="utf-8"))


def _saved_answers():
    """Every saved question, with the answer Open Targets gave to it."""
    pairs = []
    for request in sorted(SAVED.glob("*/*.request.json")):
        response = request.with_name(request.name.replace(".request.", ".response."))
        pairs.append((json.loads(request.read_text(encoding="utf-8")),
                      json.loads(response.read_text(encoding="utf-8"))))
    return pairs


def _from_the_saved_files(body):
    # These files were saved before ticket 3.8 added "functionDescriptions"
    # to the proteins question, and before ticket 3.1 added "datatypeScores"
    # and "therapeuticAreas", so those fields are set aside to find them.
    asked = dict(body, query=body["query"].replace(
        "approvedName functionDescriptions }", "approvedName }").replace(
        "        datatypeScores { id score }\n", "").replace(
        "    therapeuticAreas { id }\n", ""))
    for question, answer in _saved_answers():
        if question == asked:
            return answer
    raise AssertionError(f"no saved answer for {body['variables']}")


def real_page():
    """What /api/clues sends for AL amyloidosis, from the saved answers and
    the REAL corrections file."""
    with patch("moonlight.fetch._post_json", side_effect=_from_the_saved_files):
        response = TestClient(api.app).get("/api/clues", params={"disease_id": AL_AMYLOIDOSIS})
    assert response.status_code == 200
    return response.json()


def every_card(page):
    """Every card on the page, from every tab and folded box."""
    cards = []
    for part in page.values():
        if isinstance(part, list):
            cards.extend(item for item in part if isinstance(item, dict))
    return cards


def approved_path(name, medicine_id, disease):
    """One hand-built path: a medicine approved for this disease."""
    form = MedicineForm(medicine_id, name, best_stage="APPROVAL", disease_stage="APPROVAL",
                        withdrawn=False)
    return Path(Medicine(name, (form,)), PROTEIN, disease, ("INHIBITOR",), PROTEIN.score,
                (f"https://example.org/{medicine_id}",))


def hand_built_cards(disease_id):
    """What /api/clues sends for a page holding a hand-built tafamidis card
    and one other card, with the REAL corrections file."""
    disease = Disease(disease_id, "test page")
    paths = [approved_path("TAFAMIDIS", TAFAMIDIS, disease),
             approved_path("OTHERMEDICINE", "CHEMBL8002", disease)]
    found = api._Found(disease, sort_paths(paths), [], [], [])
    with patch.object(api, "_find", return_value=found):
        response = TestClient(api.app).get("/api/clues", params={"disease_id": disease_id})
    assert response.status_code == 200
    return {card["id"]: card for card in response.json()["approved"]}


# ---- the entry in the hand-written file ----

def test_the_note_is_the_engines_second_note_exactly():
    assert engine.SECOND_NOTE == SECOND_NOTE


def test_the_new_entry_is_in_the_real_file_once():
    # Not "it is last": the next warning goes after it (Kashish, 23 Nov).
    assert real_corrections().count(THE_ENTRY) == 1


def test_the_real_file_is_in_date_order():
    dates = [entry["date"] for entry in real_corrections()]
    assert dates == sorted(dates)


def test_the_file_holds_24_entries():
    # Ticket 2.41 added fourteen after these, dated 2026-11-24. Ticket 2.40
    # added one more the same day. Ticket 2.45 added 62, dated 2026-11-25.
    # Ticket 2.52 added seven more, dated 2026-11-25.
    # Ticket 2.54, signed answers Q22 and 10b: two more, dated 2026-11-25.
    # Ticket 2.55, signed answers Q10 and Q22: two more, dated 2026-11-25.
    # Ticket 2.56, signed rule Q22: five more, dated 2026-11-25.
    # Ticket 3.10 (MAIN 4, Q14): mannitol's red entry on asthma deleted.
    assert len(real_corrections()) == 117
    assert len(engine.corrections()) == 117
    assert len(real_corrections()[:24]) == 24


def test_it_is_the_only_entry_of_that_day_and_the_only_one_for_tafamidis():
    entries = real_corrections()
    assert [entry for entry in entries if entry["date"] == THE_DAY] == [THE_ENTRY]
    assert [entry for entry in entries if entry["medicine_id"] == TAFAMIDIS] == [THE_ENTRY]
    assert [entry for entry in entries if entry["disease_id"] == AL_AMYLOIDOSIS] == [THE_ENTRY]


def test_the_engine_gives_the_al_amyloidosis_page_the_second_words_for_tafamidis_only():
    assert engine.looks_wrong(AL_AMYLOIDOSIS) == {TAFAMIDIS}
    assert engine.warning_words(AL_AMYLOIDOSIS) == {TAFAMIDIS: SECOND_NOTE}


# ---- the id is the one the real card uses ----

def test_the_saved_page_has_one_tafamidis_card_under_approved_with_this_id():
    page = real_page()
    assert page["disease"] == {"id": AL_AMYLOIDOSIS, "name": "AL amyloidosis"}
    tafamidis = [card for card in every_card(page)
                 if "tafamidis" in json.dumps(card).lower()]
    assert len(tafamidis) == 1
    # Under Approved, and nowhere else. Ticket 2.30 added daratumumab to this
    # list by hand, so the list is no longer tafamidis alone.
    assert tafamidis == [card for card in page["approved"] if card["id"] == TAFAMIDIS]
    assert tafamidis[0]["id"] == TAFAMIDIS
    assert tafamidis[0]["medicine"] == "Tafamidis"
    assert tafamidis[0]["forms"] == ["Tafamidis", "Tafamidis Meglumine"]


# ---- the EXAMPLE: the red warning, word for word ----

def test_the_tafamidis_card_on_the_real_page_shows_the_red_words_word_for_word():
    # Ticket 2.30: daratumumab, added by hand, now comes before it A to Z.
    cards = [card for card in real_page()["approved"] if card["id"] == TAFAMIDIS]
    assert [card["warning"] for card in cards] == [SECOND_NOTE]


def test_no_other_card_on_the_page_has_a_warning():
    warned = [card["id"] for card in every_card(real_page()) if "warning" in card]
    assert warned == [TAFAMIDIS]


def test_the_card_keeps_its_place_and_nothing_else_on_the_page_changes():
    # clues_before_2.25.json is what main answered for this page before the
    # entry. Today's answer is the same, plus the warning on one card.
    before = json.loads((SAVED / "clues_before_2.25.json").read_text(encoding="utf-8"))
    expected = copy.deepcopy(before)
    expected["approved"][0]["warning"] = SECOND_NOTE
    # Ticket 2.24 added the box of new medicines in trials after that copy
    # was saved. It is set aside here, and it is the only extra key.
    page = trials_back_to_before(real_page())  # ticket 3.11
    # Ticket 2.27 added one key: the ids of the cards in the red-warning box.
    # It names tafamidis. The card itself is still in "approved", as below.
    assert set(page) - set(before) == {"new_in_trials", "wrong_approvals_box"}
    assert page.pop("wrong_approvals_box") == [TAFAMIDIS]
    del page["new_in_trials"]
    # Ticket 2.30 added daratumumab's approval by hand after that copy was
    # saved. Its card moved from the "more in trials" box to Approved, where
    # it comes before tafamidis A to Z. It is set aside here too.
    assert [card["id"] for card in page["approved"]] == [DARATUMUMAB, TAFAMIDIS]
    page["approved"] = page["approved"][1:]
    assert DARATUMUMAB in [card["id"] for card in expected["more_in_trials"]]
    expected["more_in_trials"] = [card for card in expected["more_in_trials"]
                                  if card["id"] != DARATUMUMAB]
    assert page == expected


def test_beside_another_card_tafamidis_alone_is_warned_and_stays_a_to_z():
    cards = hand_built_cards(AL_AMYLOIDOSIS)
    assert cards[TAFAMIDIS]["warning"] == SECOND_NOTE
    assert "warning" not in cards["CHEMBL8002"]
    assert [card["medicine"] for card in cards.values()] == ["Othermedicine", "Tafamidis"]


# ---- "A correction works only for the disease written on it." ----

def test_on_any_other_disease_page_tafamidis_has_no_warning():
    for other in (AMYLOIDOSIS, "TEST_0000009"):
        assert engine.warning_words(other) == {}
        assert "warning" not in hand_built_cards(other)[TAFAMIDIS]
