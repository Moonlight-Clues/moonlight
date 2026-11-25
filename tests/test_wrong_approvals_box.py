"""Ticket 2.27. A folded box for approvals that look wrong.

Kashish's decision, 23 Nov 2026 (DECISIONS.md): "A medicine with a red
warning sits in its own folded box on the Approved tab, not on the main
list."

Why: doctors reported that the four attention medicines still count in
"Approved" for Huntington disease and sit above tetrabenazine. A red
warning on the card was not enough.

- Every card on the MAIN Approved list that carries a red warning for the
  searched disease goes in one folded box at the bottom of the Approved
  tab, under the narrower-disease box and the wider-group box. A to Z.
- Each card is drawn exactly as before, red words included.
- The box is folded when the page opens, always. It never opens by itself,
  even when the main list is empty.
- The number on the tab, "Approved (N)", leaves these cards out.
- Label, proposed: "The database lists these as approved for this disease.
  They look like mistakes." with the count and "Tap to open".

Her example: Huntington disease (MONDO_0007739). Atomoxetine, guanfacine,
lisdexamfetamine and methylphenidate are in the box. The main list holds
tetrabenazine and valbenazine. The tab says Approved (6): 2 on the main
list, 0 in the narrower box, 4 in the wider-group box. Before it said (10).
Second example: AL amyloidosis (MONDO_0019438). Tafamidis is in the box.
Daratumumab is alone on the main list.

How it is built. /api/clues gains one key, "wrong_approvals_box": the ids
of the cards in the box, in the order they have on the main list. It is
only there when the box holds something. "approved" is unchanged: the same
cards, the same order, each still with its "warning". The page moves the
named cards into the box. It does not work the rule out again. This is the
shape ticket 2.28 used for "opposite_way_box" (pull request 58).

Two answers Kashish's side gave on 24 Nov, before the code:
- The label is one constant in engine.py and is typed once in the page,
  like every other box. A test here checks the two are the same.
- When the main list is empty and this box is not, the tab's "nothing
  approved" words stay hidden: they would be untrue. Only the folded box
  is shown. No new words.

Saved files only: the saved answers the older tickets left on main
(fixtures/no_regulator/, fixtures/approvals_by_hand/,
fixtures/tafamidis_warning/, fixtures/opposite_way_box/,
fixtures/withdrawal_reports/). No new file is
saved. What main sent before the ticket is kept here as fingerprints. No
network.
"""

import copy
import hashlib
import json
import pathlib
import shutil
import subprocess
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from moonlight import api, engine
from moonlight.filter import sort_paths
from moonlight.records import Disease, Medicine, MedicineForm, Path, Target

import test_approvals_third_batch as huntington_files
import test_opposite_way_box as adpkd_files
import test_tafamidis_warning as amyloidosis_files
import test_withdrawal_line as hem_a_files

ROOT = pathlib.Path(__file__).resolve().parent.parent
PAGE_FILE = ROOT / "web" / "index.html"
PAGE = PAGE_FILE.read_text(encoding="utf-8")
DECISIONS = (ROOT / "DECISIONS.md").read_text(encoding="utf-8")

KEY = "wrong_approvals_box"
# The label of the box. Proposed in the ticket: unless Kashish says no.
LABEL = "The database lists these as approved for this disease. They look like mistakes."
# The two red warnings, word for word. This ticket changes neither.
DOCTOR_WARNING = "A doctor has told us this looks like a mistake in the database."
LABEL_WARNING = ("This looks like a mistake in the database. The official label is "
                 "for a different disease.")
EMPTY_WORDS = ("The database lists no approved medicine under this exact name. That does "
               "not mean there is none. Ask a doctor.")
SAFETY_LINE = ("For learning and research exploration, not medical advice. Never start, stop or "
               "change any medicine without a doctor.")
DOCTOR_LINE = "Talk to your doctor before changing any medicine."

HUNTINGTON = "MONDO_0007739"
AL_AMYLOIDOSIS = "MONDO_0019438"
ADPKD = "MONDO_0004691"
SARCOIDOSIS = "MONDO_0019338"
COLLAGENASE = "CHEMBL2108709"  # its card carries the "no regulator record" grey line

# Her example. The four attention medicines, A to Z: (id, name on the card).
HUNTINGTON_BOX_4 = [
    ("CHEMBL641", "Atomoxetine"),
    ("CHEMBL862", "Guanfacine"),
    ("CHEMBL1201222", "Lisdexamfetamine"),
    ("CHEMBL796", "Methylphenidate"),
]
HUNTINGTON_MAIN_2 = [("CHEMBL117785", "Tetrabenazine"), ("CHEMBL2364639", "Valbenazine")]
HUNTINGTON_WIDER_4 = ["Ioflupane", "Penicillamine", "Trientine", "Zinc Acetate Anhydrous"]
# The tab's number, worked out from the saved answers:
# 2 on the main list + 0 in the narrower box + 4 in the wider-group box.
HUNTINGTON_TAB = "Approved (6)"
HUNTINGTON_TAB_BEFORE = "Approved (10)"  # the same, with the four counted
VALBENAZINE_LINE = "This approval is missing from the database. We added it from the official label."

TAFAMIDIS = ("CHEMBL2103837", "Tafamidis")
DARATUMUMAB = ("CHEMBL1743007", "Daratumumab")
AL_TAB = "Approved (7)"  # 1 on the main list + 0 narrower + 6 in the wider-group box

# What main (60aad4f) sent before the ticket, part by part, as fingerprints:
# sha256 of the part written as JSON with sorted keys. A part that changes
# by one letter has another fingerprint.
MAIN_SENT = {
    HUNTINGTON: {
        "disease": "e33e4a0f7e05e4fb63641d026d892dc4982c8cd95b08e9606a127c40258f083b",
        "about_disease": "7dbdd6130bb966494bb00e715537c8e60d4ca1e02721e66aaafdf730326c4e0c",
        "rule_text": "f574f0af0f825c8869c66f5fe5cafc601155943303f7842e325cb3a2f6c10298",
        "approved": "247d62234ae441cf8ff034c1f61c2076548c6cdb83794de6a0985a84833e80e0",
        "being_studied": "a0348076d118a931be992c8e95a8c7136d5e87ee60ec4795ed457fb51023a86a",
        "new_clues": "4383d21923ad4cc26fac25be49fbef5a8f55cdd1530fbc5a098069cbad14ee3a",
        "left_out": "94bbb8397f8c9f72f6a46d17c2475d4f36f7f2d115b554f0989a9ac099fbcb73",
        "wider_group": "e5a66a6e57cad7117ca2c01a6fab5502a32e13feef7639806b17ca3455cdf639",
        "more_in_trials": "1b7229f9fb810bcfc4956c4d62503cda8b97ddbb12d03eec68aaa2c9dac73354",
        "new_in_trials": "f874538b1126a74ad757393a84c44da477449bc6e9689acde5453887a0264b0a",
    },
    AL_AMYLOIDOSIS: {
        "disease": "0c6b3b326eb574a1aacae57768e2208d44fbb1de91581a6afb0c03bec60cedba",
        "about_disease": "5a540f8dbd480d4e1e554f02fa8268623b68479aefe7bf42788843a4a1f4943b",
        "rule_text": "f574f0af0f825c8869c66f5fe5cafc601155943303f7842e325cb3a2f6c10298",
        "approved": "61c693e1c45da33ec078863bb6daad1b6718783f048c6211c4727f7b5896aefb",
        "being_studied": "151bd52a7e1197037f62d951ef63e27eb0e4724f4fcb59ab432194c2fa8f4672",
        "new_clues": "54f3036c660df335655d8768ceb795df1acf446083b37bf06b3471867cd45503",
        "left_out": "53d3faf89c2977fd0f3fe685d7cf3490ecb0095a1125304450dd098d10b2cad3",
        "wider_group": "f2eef447be084f51cc0bdec2e802dbb3ffb7d47cf9d97aa4edcb31b2af6c19b6",
        "more_in_trials": "418d3c581de569c861f21bb9206c045bd42a5cff5e62d97c51491c52ec38edf9",
        "new_in_trials": "4f9dce0d915a837bd782f2afd97b841ce46571a8609ad5b23f1afba04c46496f",
    },
}


def fingerprint(part):
    written = json.dumps(part, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(written.encode("utf-8")).hexdigest()


def page_answer(disease_id, post_json, approvals=None, wrong=None):
    """What /api/clues sends, from saved answers. The hand-written files
    are the real ones unless a test hands in its own. Real HTTP is an error."""
    return hem_a_files.page_answer(disease_id, post_json, approvals, wrong)


@pytest.fixture(scope="module")
def huntington():
    return page_answer(HUNTINGTON, huntington_files.saved_post_json)


@pytest.fixture(scope="module")
def amyloidosis():
    return page_answer(AL_AMYLOIDOSIS, amyloidosis_files._from_the_saved_files)


@pytest.fixture(scope="module")
def adpkd():
    """A saved page with no red warning on it."""
    return page_answer(ADPKD, adpkd_files.saved_post_json)


@pytest.fixture(scope="module")
def hem_a():
    """A saved page with grey lines (no regulator record, withdrawal) and no red warning."""
    return page_answer(hem_a_files.HEM_A, hem_a_files.saved_post_json)


@pytest.fixture(scope="module")
def sarcoidosis():
    """A saved page with the "no regulator record" grey line and no red warning."""
    return page_answer(SARCOIDOSIS, huntington_files.saved_post_json)


def before_2_39(answer):
    """Ticket 2.39 gave two Huntington cards, tetrabenazine and valbenazine,
    the key limit_note, and nothing else. The answer without it, to compare
    with what main sent before."""
    marked = [card["id"] for card in answer["approved"] if "limit_note" in card]
    assert marked == [] or marked == ["CHEMBL117785", "CHEMBL2364639"]
    return dict(answer, approved=[{key: value for key, value in card.items()
                                   if key != "limit_note"} for card in answer["approved"]])


def names(cards):
    return [card["medicine"] for card in cards]


def ids(cards):
    return [card["id"] for card in cards]


def main_list(answer):
    """The cards the main Approved list shows: "approved" without the box's."""
    boxed = set(answer.get(KEY, []))
    return [card for card in answer["approved"] if card["id"] not in boxed]


def box(answer):
    """The cards of the box, in the order the API names them."""
    by_id = {card["id"]: card for card in answer["approved"]}
    return [by_id[card_id] for card_id in answer.get(KEY, [])]


# ---- the engine, with hand-built cards ----

DISEASE = Disease("TEST_0000001", "test disease")
OTHER_DISEASE = Disease("TEST_0000002", "another test disease")
PROTEIN = Target("ENSG00000000001", "ABC1", "test protein", 0.8)


def approved_path(name, medicine_id, disease=DISEASE):
    """One hand-built path: a medicine approved for this disease."""
    form = MedicineForm(medicine_id, name, best_stage="APPROVAL", disease_stage="APPROVAL",
                        withdrawn=False)
    return Path(Medicine(name, (form,)), PROTEIN, disease, ("INHIBITOR",), PROTEIN.score,
                (f"https://example.org/{medicine_id}",))


def correction(medicine_id, disease=DISEASE, note="A doctor confirmed this looks wrong."):
    return {"medicine_id": medicine_id, "disease_id": disease.id, "date": "2026-11-24",
            "note": note}


def approved_list(*pairs):
    """The main Approved list of a hand-built page, A to Z, as the engine sorts it."""
    return engine.sort_into_tabs(
        sort_paths([approved_path(name, medicine_id) for name, medicine_id in pairs]), []).approved


def in_the_box(approved, wrong, disease=DISEASE):
    with patch.object(engine, "_read_corrections", return_value=wrong):
        return [medicine.name for medicine in engine.wrong_approvals_box(approved, disease.id)]


FOUR = (("DELTAMIL", "CHEMBL9004"), ("ALPHAMIL", "CHEMBL9001"),
        ("CHARLIEMIL", "CHEMBL9003"), ("BRAVOMIL", "CHEMBL9002"))


def test_the_label_is_the_proposed_words():
    assert engine.WRONG_APPROVALS_BOX_LABEL == LABEL


def test_engine_a_card_with_a_red_warning_is_in_the_box_and_one_without_is_not():
    approved = approved_list(*FOUR)
    assert [medicine.name for medicine in approved] == [
        "ALPHAMIL", "BRAVOMIL", "CHARLIEMIL", "DELTAMIL"]
    assert in_the_box(approved, [correction("CHEMBL9003")]) == ["CHARLIEMIL"]


def test_engine_either_red_warning_puts_a_card_in_the_box():
    approved = approved_list(*FOUR)
    wrong = [correction("CHEMBL9004"),  # the first note: "A doctor has told us ..."
             correction("CHEMBL9002", note=LABEL_WARNING)]  # the second: the label's
    assert in_the_box(approved, wrong) == ["BRAVOMIL", "DELTAMIL"]


def test_engine_the_box_keeps_the_main_lists_own_order():
    approved = approved_list(*FOUR)
    wrong = [correction(medicine_id) for _, medicine_id in FOUR]  # written in another order
    assert in_the_box(approved, wrong) == ["ALPHAMIL", "BRAVOMIL", "CHARLIEMIL", "DELTAMIL"]


def test_engine_a_warning_for_another_disease_does_not_count():
    approved = approved_list(*FOUR)
    assert in_the_box(approved, [correction("CHEMBL9001", OTHER_DISEASE)]) == []


def test_engine_no_red_warning_means_an_empty_box():
    assert in_the_box(approved_list(*FOUR), []) == []
    assert in_the_box([], [correction("CHEMBL9001")]) == []


def test_engine_the_box_is_exactly_the_cards_warning_words_names():
    approved = approved_list(*FOUR)
    wrong = [correction("CHEMBL9001"), correction("CHEMBL9004", note=LABEL_WARNING)]
    with patch.object(engine, "_read_corrections", return_value=wrong):
        words = engine.warning_words(DISEASE.id)
        boxed = engine.wrong_approvals_box(approved, DISEASE.id)
    assert [medicine.id for medicine in boxed] == [
        medicine.id for medicine in approved if medicine.id in words]


def test_engine_nothing_is_taken_off_the_list_it_is_handed():
    approved = approved_list(*FOUR)
    kept = list(approved)
    in_the_box(approved, [correction("CHEMBL9001")])
    assert approved == kept


# ---- the API, with hand-built pages ----

def hand_built_page(found, wrong):
    api.forget_visitors()
    with patch.object(api, "_find", return_value=found), \
            patch.object(engine, "_read_corrections", return_value=wrong):
        response = TestClient(api.app).get("/api/clues", params={"disease_id": DISEASE.id})
    api.forget_visitors()
    assert response.status_code == 200
    return response.json()


def found_with(*pairs):
    paths = [approved_path(name, medicine_id) for name, medicine_id in pairs]
    return api._Found(DISEASE, sort_paths(paths), [], [], [])


def test_api_the_key_holds_the_ids_in_the_main_lists_order():
    answer = hand_built_page(found_with(*FOUR),
                             [correction("CHEMBL9004"), correction("CHEMBL9002")])
    assert answer[KEY] == ["CHEMBL9002", "CHEMBL9004"]
    assert names(answer["approved"]) == ["Alphamil", "Bravomil", "Charliemil", "Deltamil"]
    assert [card["medicine"] for card in answer["approved"] if "warning" in card] == [
        "Bravomil", "Deltamil"]


def test_api_no_key_when_no_card_has_a_red_warning():
    answer = hand_built_page(found_with(*FOUR), [])
    assert KEY not in answer


def test_api_the_key_is_exactly_the_main_cards_that_carry_a_warning():
    answer = hand_built_page(found_with(*FOUR), [correction("CHEMBL9001", note=LABEL_WARNING)])
    assert answer[KEY] == [card["id"] for card in answer["approved"] if "warning" in card]
    assert box(answer)[0]["warning"] == LABEL_WARNING  # its own red words, as before


def test_api_a_red_warning_card_in_an_older_box_stays_where_it_is():
    # Out of scope for this ticket: a red-warning card inside the narrower
    # box or the wider-group box is left there, and is not named by the key.
    found = found_with(*FOUR)
    found.wider_group, found.approved = found.approved[:1], found.approved[1:]
    found.narrower, found.approved = found.approved[:1], found.approved[1:]
    wrong = [correction(medicine_id) for _, medicine_id in FOUR]
    answer = hand_built_page(found, wrong)
    assert names(answer["wider_group"]) == ["Alphamil"] and "warning" in answer["wider_group"][0]
    assert names(answer["narrower"]) == ["Bravomil"] and "warning" in answer["narrower"][0]
    assert answer[KEY] == ["CHEMBL9003", "CHEMBL9004"]  # the main list's two only


# ---- her example: Huntington disease, from the saved answers ----

def test_example_all_four_are_in_the_box_a_to_z_with_their_red_words(huntington):
    assert huntington[KEY] == [card_id for card_id, _ in HUNTINGTON_BOX_4]
    assert names(box(huntington)) == [name for _, name in HUNTINGTON_BOX_4]
    assert names(box(huntington)) == sorted(names(box(huntington)))
    assert [card["warning"] for card in box(huntington)] == [DOCTOR_WARNING] * 4


def test_example_none_of_the_four_is_on_the_main_list(huntington):
    assert not set(ids(main_list(huntington))) & {card_id for card_id, _ in HUNTINGTON_BOX_4}


def test_example_the_main_list_holds_tetrabenazine_then_valbenazine(huntington):
    assert [(card["id"], card["medicine"]) for card in main_list(huntington)] == HUNTINGTON_MAIN_2
    assert not any("warning" in card for card in main_list(huntington))


def test_example_approved_is_unchanged_the_same_six_in_the_same_order(huntington):
    assert names(huntington["approved"]) == [
        "Atomoxetine", "Guanfacine", "Lisdexamfetamine", "Methylphenidate",
        "Tetrabenazine", "Valbenazine"]
    assert fingerprint(before_2_39(huntington)["approved"]) == MAIN_SENT[HUNTINGTON]["approved"]


def test_example_the_number_on_the_tab_is_six(huntington):
    # The main list and the two older boxes, and not the four.
    assert "narrower" not in huntington
    assert names(huntington["wider_group"]) == HUNTINGTON_WIDER_4
    counted = len(main_list(huntington)) + len(huntington.get("narrower", [])) + len(
        huntington["wider_group"])
    assert f"Approved ({counted})" == HUNTINGTON_TAB
    assert f"Approved ({counted + len(huntington[KEY])})" == HUNTINGTON_TAB_BEFORE


def test_example_in_trials_and_new_clues_are_letter_for_letter_what_main_gives(huntington):
    for part in ("being_studied", "more_in_trials", "new_in_trials", "new_clues"):
        assert fingerprint(huntington[part]) == MAIN_SENT[HUNTINGTON][part], part
    assert (len(huntington["being_studied"]), len(huntington["more_in_trials"]),
            len(huntington["new_in_trials"]), len(huntington["new_clues"])) == (6, 23, 18, 175)


@pytest.mark.parametrize("disease_id", [HUNTINGTON, AL_AMYLOIDOSIS])
def test_example_every_old_key_answers_what_main_answered_and_one_key_is_new(
        disease_id, huntington, amyloidosis):
    answer = {HUNTINGTON: before_2_39(huntington), AL_AMYLOIDOSIS: amyloidosis}[disease_id]
    old = MAIN_SENT[disease_id]
    assert [key for key in answer if key != KEY] == list(old)  # in the same order
    assert {key: fingerprint(answer[key]) for key in old} == old
    assert KEY in answer


def test_example_no_red_warning_card_sits_in_an_older_box(huntington, amyloidosis):
    # The ticket: "If the saved answers hold one, leave it where it is and
    # report it." They hold none.
    for answer in (huntington, amyloidosis):
        for where in ("narrower", "wider_group"):
            assert not [card for card in answer.get(where, []) if "warning" in card]


def test_example_needs_no_more_requests_than_before():
    asked = []

    def counting(body):
        asked.append(body)
        return huntington_files.saved_post_json(body)

    with patch.object(engine, "wrong_approvals_box", return_value=[]), \
            patch.object(api, "wrong_approvals_box", return_value=[], create=True):
        page_answer(HUNTINGTON, counting)
    without = len(asked)
    del asked[:]
    page_answer(HUNTINGTON, counting)
    assert len(asked) == without  # no new question to Open Targets


# ---- second example: AL amyloidosis ----

def test_second_example_tafamidis_is_in_the_box_with_its_label_warning(amyloidosis):
    assert amyloidosis[KEY] == [TAFAMIDIS[0]]
    assert [(card["medicine"], card["warning"]) for card in box(amyloidosis)] == [
        (TAFAMIDIS[1], LABEL_WARNING)]


def test_second_example_daratumumab_is_alone_on_the_main_list(amyloidosis):
    assert [(card["id"], card["medicine"]) for card in main_list(amyloidosis)] == [DARATUMUMAB]
    assert names(amyloidosis["approved"]) == ["Daratumumab", "Tafamidis"]  # unchanged


# ---- guards ----

def test_guard_a_page_with_no_red_warning_has_no_key(adpkd, hem_a, sarcoidosis):
    # Haemophilia A is not here since ticket 2.47: Obizur has a red warning there.
    for answer in (adpkd, sarcoidosis):
        assert answer["approved"]
        assert not any("warning" in card for card in answer["approved"])
        assert KEY not in answer


def test_guard_a_card_with_only_a_grey_line_never_goes_in_the_box(huntington, hem_a, sarcoidosis):
    # Hand-added (ticket 2.26): valbenazine's grey line. It is on the main list.
    valbenazine = [card for card in huntington["approved"] if card["medicine"] == "Valbenazine"]
    assert [card.get("proof_note") for card in valbenazine] == [VALBENAZINE_LINE]
    assert valbenazine[0]["id"] not in huntington[KEY]
    # The withdrawal line (ticket 2.31): octocog alfa, on haemophilia A's page.
    assert [card["id"] for card in hem_a["approved"]
            if card.get("withdrawal_note") == hem_a_files.LINE] == [hem_a_files.OCTOCOG]
    assert hem_a[KEY] == ["CHEMBL5315075"]  # only Obizur's red warning (ticket 2.47)
    # No regulator record (ticket 2.17): collagenase, on sarcoidosis's page.
    assert [card["id"] for card in sarcoidosis["approved"]
            if card.get("proof_note") == hem_a_files.NO_REGULATOR_LINE] == [COLLAGENASE]
    assert KEY not in sarcoidosis


def test_guard_a_grey_line_beside_a_red_warning_changes_nothing(huntington):
    # The four carry Japan's grey line too. It is the red words that count.
    assert all("proof_note" in card and "warning" in card for card in box(huntington))


def test_guard_the_withdrawal_line_alone_does_not_box_a_card_and_with_a_warning_it_does():
    octocog = hem_a_files.OCTOCOG
    answer = page_answer(hem_a_files.HEM_A, hem_a_files.saved_post_json,
                         wrong=[correction(octocog, Disease(hem_a_files.HEM_A, "hemophilia A"))])
    assert answer[KEY] == [octocog]
    (card,) = box(answer)
    assert card["withdrawal_note"] == hem_a_files.LINE and card["warning"] == DOCTOR_WARNING


def test_guard_a_hand_added_approval_with_a_corrections_entry_is_not_added_at_all():
    valbenazine = HUNTINGTON_MAIN_2[1][0]
    real = json.loads((ROOT / "moonlight" / "corrections.json").read_text(encoding="utf-8"))
    wrong = real + [correction(valbenazine, Disease(HUNTINGTON, "Huntington disease"))]
    answer = page_answer(HUNTINGTON, huntington_files.saved_post_json, wrong=wrong)
    assert valbenazine not in ids(answer["approved"])  # as today: not added
    assert answer[KEY] == [card_id for card_id, _ in HUNTINGTON_BOX_4]  # so not in the box
    assert names(main_list(answer)) == ["Tetrabenazine"]


def test_guard_sort_into_tabs_still_puts_the_four_on_the_approved_list(huntington):
    # The ticket does not change sort_into_tabs: the tab's list is as it was.
    assert ids(huntington["approved"])[:4] == [card_id for card_id, _ in HUNTINGTON_BOX_4]


# ---- DECISIONS.md ----

def test_the_decision_line_says_the_ticket_is_built():
    line = ("- 2026-11-23: A medicine with a red warning sits in its own folded box on the "
            "Approved tab, not on the main list. (Ticket 2.27.)")
    assert line in DECISIONS.splitlines()
    assert "(Ticket 2.27, not built.)" not in DECISIONS


# ---- the page, read as text ----

PANEL = PAGE[PAGE.index('id="panel-approved"'):PAGE.index('id="panel-trials"')]


def test_the_page_holds_the_box_at_the_bottom_of_the_tab_with_the_exact_label():
    assert PANEL.index('id="approved-cards"') < PANEL.index('id="narrower-box"') < PANEL.index(
        'id="wider-box"') < PANEL.index('id="wrong-box"')
    assert PAGE.count(LABEL) == 1 and LABEL in PANEL
    assert (f"<summary>{LABEL} (<span id=\"wrong-count\"></span>) "
            "<span data-part=\"tap\">Tap to open</span></summary>") in PANEL
    assert '<details class="wider-box" id="wrong-box" hidden>' in PANEL  # folded, like the others
    assert 'id="wrong-cards"' in PANEL


def test_the_page_never_opens_the_box_by_itself():
    assert 'byId("wrong-box").open = false;' in PAGE
    assert PAGE.count('byId("wrong-box").open') == 1


def test_the_page_still_does_not_type_a_red_warning_itself():
    assert DOCTOR_WARNING not in PAGE and LABEL_WARNING not in PAGE  # they come from the API


def test_the_other_words_of_the_approved_tab_are_not_changed():
    assert ('<p class="tab-words">Already approved for this disease in at least one country, '
            'according to the database. Nothing here says how well any of them works. '
            'Listed A to Z.</p>') in PANEL
    assert f"<h3>{EMPTY_WORDS}</h3>" in PANEL
    assert "Approved for a narrower disease (" in PANEL and "Approved for a wider group (" in PANEL
    assert PANEL.count(DOCTOR_LINE) == 3  # the tab and its two older boxes, as before
    assert SAFETY_LINE in PAGE


# ---- the page, in a real browser, at phone width ----

BROWSER_SCRIPT = r"""
"use strict";
const fs = require("fs");
const { chromium } = require("playwright");
const PAGE = fs.readFileSync(process.argv[1], "utf-8");
const ANSWERS = JSON.parse(fs.readFileSync(process.argv[2], "utf-8"));
const SITE = "http://moonlight.test";

function readApproved() {
  const shownOnPage = el => !!el && el.getClientRects().length > 0;
  const words = el => el.innerText.replace(/\s+/g, " ").trim();
  const readCard = card => {
    const warning = card.querySelector('[data-slot="warning"]');
    return {
      name: card.querySelector('[data-slot="medicine-name"]').textContent,
      onScreen: card.checkVisibility(),  // false inside a folded box
      warning: warning && !warning.hidden ? warning.textContent.replace(/\s+/g, " ").trim() : null,
      // Everything a reader can read on the card, shown or folded.
      words: card.textContent.replace(/\s+/g, " ").trim(),
      html: card.outerHTML,
    };
  };
  const readBox = (boxId, cardsId) => {
    const box = document.getElementById(boxId);
    return box && {
      shown: shownOnPage(box),
      open: box.open,
      summary: words(box.querySelector("summary")),
      cards: [...box.querySelectorAll("#" + cardsId + " > .card")].map(readCard),
      caution: [...box.querySelectorAll(".doctor-line")].map(el => el.textContent),
    };
  };
  const follows = (first, second) =>
    !!(first.compareDocumentPosition(second) & Node.DOCUMENT_POSITION_FOLLOWING);
  const panel = document.getElementById("panel-approved");
  const wrong = document.getElementById("wrong-box");
  const moreLine = document.getElementById("more-line");
  return {
    tab: words(document.getElementById("tab-approved")),
    tabs: ["tab-approved", "tab-trials", "tab-clues"].map(id => words(document.getElementById(id))),
    listShown: shownOnPage(document.getElementById("approved-list")),
    list: [...document.querySelectorAll("#approved-cards > .card")].map(readCard),
    emptyShown: shownOnPage(document.getElementById("approved-empty")),
    emptyWords: document.querySelector("#approved-empty h3").textContent,
    moreLine: shownOnPage(moreLine) ? moreLine.textContent : null,
    narrower: readBox("narrower-box", "narrower-cards"),
    wider: readBox("wider-box", "wider-cards"),
    wrong: readBox("wrong-box", "wrong-cards"),
    wrongIsLast: !!wrong && follows(document.getElementById("approved-cards"), wrong)
      && follows(document.getElementById("narrower-box"), wrong)
      && follows(document.getElementById("wider-box"), wrong)
      && panel.lastElementChild === wrong,
    cardsOnTheTab: panel.querySelectorAll(".card").length,
    seenText: words(panel),  // what a reader can see on the tab right now
    sideways: document.documentElement.scrollWidth > document.documentElement.clientWidth,
    trialsText: document.getElementById("panel-trials").textContent,
    cluesText: document.getElementById("panel-clues").textContent,
  };
}

async function oneSearch(browser, answer) {
  const context = await browser.newContext({ viewport: { width: 390, height: 844 } });
  const page = await context.newPage();
  const errors = [];
  page.on("pageerror", problem => errors.push(String(problem)));
  await context.route("**/*", route => {
    const url = route.request().url();
    if (url === SITE + "/" || url.startsWith(SITE + "/?"))
      return route.fulfill({ contentType: "text/html; charset=utf-8", body: PAGE });
    if (url.startsWith(SITE + "/api/clues?"))
      return route.fulfill({ contentType: "application/json", body: JSON.stringify(answer) });
    if (url.startsWith(SITE + "/api/explain?"))
      return route.fulfill({ status: 404, contentType: "application/json", body: "{}" });
    return route.abort();
  });
  await page.goto(SITE + "/?disease=MONDO_TEST");
  await page.waitForSelector("#found", { state: "visible" });
  await page.waitForTimeout(300);
  const out = { errors };
  out.firstTab = await page.evaluate(
    () => document.querySelector('.tab[aria-selected="true"]').dataset.tab);
  out.opened = await page.evaluate(readApproved);  // the tab as the page opens

  const box = page.locator("#wrong-box");
  if (await box.count() && await box.isVisible()) {
    await page.click("#wrong-box summary");
    await page.waitForTimeout(300);  // the box tells the page it was opened a moment later
    out.tapped = await page.evaluate(readApproved);
    await page.click("#wrong-box summary");
    await page.waitForTimeout(300);
    out.tappedAgain = await page.evaluate(readApproved);
  }
  await context.close();
  return out;
}

(async () => {
  const browser = await chromium.launch();
  const out = {};
  for (const name of Object.keys(ANSWERS)) out[name] = await oneSearch(browser, ANSWERS[name]);
  await browser.close();
  console.log(JSON.stringify(out));
})().catch(problem => { console.error(problem); process.exit(1); });
"""


def without_the_key(answer):
    plain = copy.deepcopy(answer)
    plain.pop(KEY, None)
    return plain


@pytest.fixture(scope="module")
def answers(huntington, amyloidosis, adpkd):
    """Answers of /api/clues: her two examples, each also as main answered
    it before the ticket (no key), a page with no red warning, and three
    cut-down ones."""
    boxed = set(huntington[KEY])
    only_box = copy.deepcopy(huntington)  # every approved card has a red warning, no older box
    only_box["approved"] = [card for card in huntington["approved"] if card["id"] in boxed]
    del only_box["wider_group"]
    with_wider = copy.deepcopy(huntington)  # the same, with the wider-group box
    with_wider["approved"] = only_box["approved"]
    nothing = without_the_key(only_box)  # no approved card at all
    nothing["approved"] = []
    return {"example": huntington, "before": without_the_key(huntington),
            "second": amyloidosis, "second_before": without_the_key(amyloidosis),
            "no_warning": adpkd, "only_box": only_box, "with_wider": with_wider,
            "nothing": nothing}


@pytest.fixture(scope="module")
def seen(answers, tmp_path_factory):
    """Opens the page once per answer, 390 wide, and returns what a reader sees."""
    node = shutil.which("node")
    if not node or subprocess.run(
            [node, "-e", "require('playwright')"], capture_output=True).returncode:
        pytest.skip("needs node with playwright to open a real browser")
    answers_file = tmp_path_factory.mktemp("wrong_approvals_box") / "answers.json"
    answers_file.write_text(json.dumps(answers), encoding="utf-8")
    run = subprocess.run(
        [node, "-e", BROWSER_SCRIPT, str(PAGE_FILE), str(answers_file)],
        capture_output=True, text=True, timeout=240, cwd=str(ROOT))
    assert run.returncode == 0, run.stderr[-3000:]
    out = json.loads(run.stdout)
    for name in answers:
        assert out[name]["errors"] == [], name
    return out


def read_names(cards_read):
    return [card["name"] for card in cards_read]


def test_browser_example_the_page_opens_on_the_approved_tab(seen):
    assert seen["example"]["firstTab"] == "approved"


def test_browser_example_the_tab_says_six_and_before_it_said_ten(seen):
    assert seen["example"]["opened"]["tab"] == HUNTINGTON_TAB
    assert seen["before"]["opened"]["tab"] == HUNTINGTON_TAB_BEFORE


def test_browser_example_the_main_list_holds_tetrabenazine_then_valbenazine(seen):
    opened = seen["example"]["opened"]
    assert read_names(opened["list"]) == ["Tetrabenazine", "Valbenazine"]
    assert all(card["onScreen"] for card in opened["list"])
    assert [card["warning"] for card in opened["list"]] == [None, None]


def test_browser_example_before_the_four_sat_above_tetrabenazine(seen):
    assert read_names(seen["before"]["opened"]["list"]) == [
        "Atomoxetine", "Guanfacine", "Lisdexamfetamine", "Methylphenidate",
        "Tetrabenazine", "Valbenazine"]
    assert seen["before"]["opened"]["wrong"]["shown"] is False


def test_browser_example_the_box_holds_the_four_a_to_z_with_their_red_words(seen):
    wrong = seen["example"]["opened"]["wrong"]
    assert read_names(wrong["cards"]) == [name for _, name in HUNTINGTON_BOX_4]
    assert [card["warning"] for card in wrong["cards"]] == [DOCTOR_WARNING] * 4


def test_browser_example_the_box_is_folded_at_the_bottom_of_the_tab(seen):
    opened = seen["example"]["opened"]
    wrong = opened["wrong"]
    assert wrong["shown"] is True and wrong["open"] is False
    assert wrong["summary"] in (f"{LABEL} (4) Tap to open", f"{LABEL} (4) · Tap to open")
    assert not any(card["onScreen"] for card in wrong["cards"])
    assert opened["wrongIsLast"] is True  # under the narrower box and the wider-group box


def test_browser_example_no_red_words_can_be_seen_until_the_box_is_opened(seen):
    assert DOCTOR_WARNING not in seen["example"]["opened"]["seenText"]
    assert DOCTOR_WARNING in seen["before"]["opened"]["seenText"]
    assert DOCTOR_WARNING in seen["example"]["tapped"]["seenText"]


def test_browser_example_a_tap_opens_the_box_and_a_second_tap_folds_it(seen):
    tapped, again = seen["example"]["tapped"]["wrong"], seen["example"]["tappedAgain"]["wrong"]
    assert tapped["open"] is True
    assert tapped["summary"] in (f"{LABEL} (4) Tap to close", f"{LABEL} (4) · Tap to close")
    assert all(card["onScreen"] for card in tapped["cards"])
    assert again["open"] is False and "Tap to open" in again["summary"]
    # Opening it changes neither the number on the tab nor the main list.
    assert seen["example"]["tapped"]["tab"] == HUNTINGTON_TAB
    assert read_names(seen["example"]["tapped"]["list"]) == ["Tetrabenazine", "Valbenazine"]


def test_browser_example_the_open_box_adds_no_words_of_its_own(seen):
    # Inside the box there are the four cards and nothing else: no new sentence.
    tapped = seen["example"]["tapped"]
    assert tapped["wrong"]["caution"] == []
    assert tapped["wider"]["caution"] == [DOCTOR_LINE]  # the older box, as before
    # The tab's own doctor line is still above the main list, shown.
    assert DOCTOR_LINE in tapped["seenText"]


@pytest.mark.parametrize("name, old", [("example", "before"), ("second", "second_before")])
def test_browser_every_card_is_drawn_exactly_as_before(seen, name, old):
    def drawn(view):
        cards = view["list"] + view["wrong"]["cards"]
        return {card["name"]: card["html"] for card in cards}

    now, then = drawn(seen[name]["opened"]), drawn(seen[old]["opened"])
    assert now == then  # each card, tag for tag and word for word
    assert len(now) == seen[old]["opened"]["cardsOnTheTab"] - len(
        seen[old]["opened"]["wider"]["cards"])


def test_browser_example_nothing_is_removed_and_no_card_is_there_twice(seen):
    opened, before = seen["example"]["opened"], seen["before"]["opened"]
    assert opened["cardsOnTheTab"] == before["cardsOnTheTab"] == 10
    everything = read_names(opened["list"] + opened["wider"]["cards"] + opened["wrong"]["cards"])
    assert len(everything) == len(set(everything)) == 10


def test_browser_example_the_older_boxes_are_as_before(seen):
    opened, before = seen["example"]["opened"], seen["before"]["opened"]
    assert opened["wider"] == before["wider"]
    assert opened["narrower"] == before["narrower"]
    assert read_names(opened["wider"]["cards"]) == HUNTINGTON_WIDER_4
    assert opened["wider"]["open"] is False
    # The line that points at the older boxes counts their cards only, as before.
    assert opened["moreLine"] == before["moreLine"] == (
        "4 more approved medicines are in the folded boxes below.")


def test_browser_example_in_trials_and_new_clues_are_letter_for_letter_as_before(seen):
    opened, before = seen["example"]["opened"], seen["before"]["opened"]
    assert opened["trialsText"] == before["trialsText"]
    assert opened["cluesText"] == before["cluesText"]
    assert opened["tabs"][1:] == before["tabs"][1:] == ["In trials (47)", "New clues (175)"]


def test_browser_example_the_page_does_not_scroll_sideways_at_phone_width(seen):
    assert seen["example"]["opened"]["sideways"] is False
    assert seen["example"]["tapped"]["sideways"] is False


def test_browser_second_example_tafamidis_is_in_the_box_and_daratumumab_is_alone(seen):
    opened = seen["second"]["opened"]
    assert read_names(opened["list"]) == ["Daratumumab"]
    assert read_names(opened["wrong"]["cards"]) == ["Tafamidis"]
    assert [card["warning"] for card in opened["wrong"]["cards"]] == [LABEL_WARNING]
    assert opened["wrong"]["open"] is False
    assert opened["wrong"]["summary"] in (f"{LABEL} (1) Tap to open",
                                          f"{LABEL} (1) · Tap to open")
    assert opened["tab"] == AL_TAB
    assert seen["second_before"]["opened"]["tab"] == "Approved (8)"


def test_browser_no_key_means_no_box_and_the_tab_as_before(seen):
    opened = seen["no_warning"]["opened"]
    assert opened["wrong"]["shown"] is False and opened["wrong"]["cards"] == []
    assert read_names(opened["list"]) == ["Tolvaptan"]
    assert opened["tab"] == "Approved (1)"
    assert "tapped" not in seen["no_warning"]  # there was no box to tap


def test_browser_only_the_box_it_stays_folded_and_no_untrue_words_are_shown(seen):
    opened = seen["only_box"]["opened"]
    assert opened["list"] == [] and opened["listShown"] is False
    assert opened["wrong"]["shown"] is True
    assert opened["wrong"]["open"] is False  # it never opens by itself
    assert read_names(opened["wrong"]["cards"]) == [name for _, name in HUNTINGTON_BOX_4]
    # "The database lists no approved medicine ..." would be untrue here.
    assert opened["emptyShown"] is False
    assert EMPTY_WORDS not in opened["seenText"]
    assert opened["tab"] == "Approved (0)"
    assert opened["seenText"] in (f"{LABEL} (4) Tap to open", f"{LABEL} (4) · Tap to open")


def test_browser_only_the_box_a_tap_still_opens_it(seen):
    tapped = seen["only_box"]["tapped"]
    assert tapped["wrong"]["open"] is True
    assert all(card["onScreen"] for card in tapped["wrong"]["cards"])
    assert tapped["emptyShown"] is False


def test_browser_empty_main_list_the_wider_box_opens_as_before_and_this_box_does_not(seen):
    opened = seen["with_wider"]["opened"]
    assert opened["list"] == []
    assert opened["wider"]["shown"] is True and opened["wider"]["open"] is True  # as today
    assert opened["wrong"]["shown"] is True and opened["wrong"]["open"] is False
    assert opened["emptyShown"] is False
    assert opened["tab"] == "Approved (4)"  # the wider-group box's four
    assert opened["wrongIsLast"] is True


def test_browser_nothing_approved_at_all_still_says_todays_words(seen):
    opened = seen["nothing"]["opened"]
    assert opened["emptyShown"] is True and opened["emptyWords"] == EMPTY_WORDS
    assert opened["wrong"]["shown"] is False
    assert opened["tab"] == "Approved (0)"
