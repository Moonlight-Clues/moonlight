"""Ticket 2.18. A second red warning, and clues left out by hand.

Kashish's decisions, 19 Nov:

PART 1. A corrections entry's note may be exactly one of two sentences.
A card with the first note keeps today's red words. A card with the second
note shows the second note itself, word for word, in the same red box.
Everything else about corrections stays the same.

PART 2. moonlight/left_out.json lists (medicine, disease, date) entries
written by hand. For that disease the medicine is not shown in New clues,
and one line at the bottom of the list says how many were left out. Only
medicines that would have been shown are counted. Approved and In trials
are not changed. No code may add to the file.

No network. Hand-built records, as in test_opposite_way.py: api._find is
swapped for them, and the two hand-written files are read through
engine._read_corrections and engine._read_left_out, which tests replace.
"""

import inspect
import json
import pathlib
import re
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from moonlight import api, engine
from moonlight.engine import CHILD, PARENT, Neighbour
from moonlight.fetch import Listed
from moonlight.filter import sort_paths
from moonlight.records import Disease, Medicine, MedicineForm, Path, Target

ROOT = pathlib.Path(__file__).resolve().parent.parent
PAGE = (ROOT / "web" / "index.html").read_text(encoding="utf-8")
CORRECTIONS_FILE = ROOT / "moonlight" / "corrections.json"
LEFT_OUT_FILE = ROOT / "moonlight" / "left_out.json"

# Kashish's words, exactly.
FIRST_NOTE = "A doctor confirmed this looks wrong."
FIRST_WARNING = "A doctor has told us this looks like a mistake in the database."
SECOND_NOTE = ("This looks like a mistake in the database. The official label is "
               "for a different disease.")
MANY_LINE = "4 medicines left out because they push the wrong way for this disease."
ONE_LINE = "1 medicine left out because it pushes the wrong way for this disease."

TODAY = "2026-11-19"
MONDAY = "2026-11-16"
TICKET_2_19_DAY = "2026-11-22"  # the one entry ticket 2.19 added

DISEASE = Disease("TEST_0000001", "test disease")
OTHER = Disease("TEST_0000009", "another test disease")
WIDER = Disease("TEST_0000002", "wider test group")
NARROWER = Disease("TEST_0000003", "narrower test disease")

PROTEIN = Target("ENSG00000000001", "ABC1", "test protein", 0.8)
DOWN = ("INHIBITOR",)
APPROVED_HERE = "APPROVAL"
IN_TRIALS = "PHASE_2"
NO_LINK = None


def path(name, medicine_id, link=NO_LINK, disease=DISEASE):
    """One hand-built path: this medicine turns the test protein down."""
    form = MedicineForm(medicine_id, name, best_stage="APPROVAL", disease_stage=link,
                        withdrawn=False)
    return Path(Medicine(name, (form,)), PROTEIN, disease, DOWN, PROTEIN.score,
                (f"https://example.org/{medicine_id}",))


def correction(medicine_id, disease_id, note, date=TODAY):
    return {"medicine_id": medicine_id, "disease_id": disease_id, "date": date, "note": note}


def left_out(medicine_id, disease_id, date=TODAY):
    return {"medicine_id": medicine_id, "disease_id": disease_id, "date": date}


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


def cards(paths, corrections=(), left=(), neighbours=(), disease=DISEASE):
    """What /api/clues sends for these hand-built paths and hand-written lists."""
    found = api._Found(disease, sort_paths(paths), [], [], list(neighbours))
    with patch.object(api, "_find", return_value=found), \
            patch("moonlight.engine._read_corrections", return_value=list(corrections)), \
            patch("moonlight.engine._read_left_out", return_value=list(left)):
        response = TestClient(api.app).get("/api/clues", params={"disease_id": disease.id})
    assert response.status_code == 200
    return response.json()


def card(answer, tab, medicine):
    for item in answer[tab]:
        if item["medicine"].lower() == medicine.lower():
            return item
    raise AssertionError(f"no {medicine} card in {tab}")


ALPHA = path("ALPHA", "CHEMBL8001", APPROVED_HERE)
BRAVO = path("BRAVO", "CHEMBL8002", APPROVED_HERE)
CHARLIE = path("CHARLIE", "CHEMBL8003", APPROVED_HERE)


# =====================================================================
# PART 1. The second red warning
# =====================================================================

def test_the_two_notes_and_the_old_red_words_are_kashishs_words_exactly():
    assert engine.CORRECTION_NOTE == FIRST_NOTE
    assert engine.WRONG_WARNING == FIRST_WARNING
    assert engine.SECOND_NOTE == SECOND_NOTE
    assert engine.CORRECTION_NOTES == (FIRST_NOTE, SECOND_NOTE)
    assert "doctor" not in SECOND_NOTE.lower()  # no doctor is named, or even mentioned


# ---- a. an entry with the new note: the card shows the new words in red ----

def test_a_card_with_the_new_note_shows_the_new_words():
    answer = cards([ALPHA, BRAVO], [correction("CHEMBL8002", DISEASE.id, SECOND_NOTE)])
    assert card(answer, "approved", "bravo")["warning"] == SECOND_NOTE
    assert "warning" not in card(answer, "approved", "alpha")


def test_a_the_page_puts_a_cards_warning_words_in_the_red_box():
    # The words the API sends go, unchanged, into the bright red box.
    assert "part(slot(el, \"warning\"), \"warning-words\").textContent = medicine.warning;" in PAGE
    assert '<p class="wrong-warning" data-slot="warning" hidden>' in PAGE
    red = re.search(r"\.wrong-warning\{[^}]*\}", PAGE).group(0)
    assert "color:#D40000" in red and "border:2px solid #D40000" in red
    # Neither sentence is typed into the page: a card shows what its entry carries.
    assert SECOND_NOTE not in PAGE and FIRST_WARNING not in PAGE


def test_a_the_card_keeps_its_a_to_z_place_and_nothing_else_changes():
    plain = cards([CHARLIE, ALPHA, BRAVO])
    answer = cards([CHARLIE, ALPHA, BRAVO], [correction("CHEMBL8002", DISEASE.id, SECOND_NOTE)])
    assert [item["medicine"] for item in answer["approved"]] == ["Alpha", "Bravo", "Charlie"]
    for before, after in zip(plain["approved"], answer["approved"]):
        assert {key: value for key, value in after.items() if key != "warning"} == before


# ---- b. an entry with the old note still shows the old words ----

def test_b_card_with_the_old_note_still_shows_the_old_red_words():
    answer = cards([ALPHA, BRAVO], [correction("CHEMBL8001", DISEASE.id, FIRST_NOTE, MONDAY)])
    assert card(answer, "approved", "alpha")["warning"] == FIRST_WARNING
    assert "warning" not in card(answer, "approved", "bravo")


def test_b_two_cards_on_one_page_each_show_their_own_entrys_words():
    answer = cards([ALPHA, BRAVO, CHARLIE], [
        correction("CHEMBL8001", DISEASE.id, FIRST_NOTE, MONDAY),
        correction("CHEMBL8002", DISEASE.id, SECOND_NOTE),
    ])
    assert card(answer, "approved", "alpha")["warning"] == FIRST_WARNING
    assert card(answer, "approved", "bravo")["warning"] == SECOND_NOTE
    assert "warning" not in card(answer, "approved", "charlie")


def test_b_the_engine_says_which_words_each_medicine_gets():
    entries = [correction("CHEMBL8001", DISEASE.id, FIRST_NOTE, MONDAY),
               correction("CHEMBL8002", DISEASE.id, SECOND_NOTE)]
    with patch("moonlight.engine._read_corrections", return_value=entries):
        assert engine.warning_words(DISEASE.id) == {
            "CHEMBL8001": FIRST_WARNING, "CHEMBL8002": SECOND_NOTE}
        # The old question still has its old answer: the ids, for both notes.
        assert engine.looks_wrong(DISEASE.id) == {"CHEMBL8001", "CHEMBL8002"}
        assert engine.corrections() == {("CHEMBL8001", DISEASE.id), ("CHEMBL8002", DISEASE.id)}


# ---- c. an entry with any other note is refused ----

@pytest.mark.parametrize("note", [
    "Some other words.",
    "This looks like a mistake in the database.",  # only the first half
    "The official label is for a different disease.",  # only the second half
    SECOND_NOTE + " Dr A Name said so.",
    SECOND_NOTE.lower(),
    SECOND_NOTE.replace("  ", " ").replace(". The", ".  The"),  # two spaces
    FIRST_NOTE + " " + SECOND_NOTE,  # both at once
    FIRST_WARNING,  # the red words are not a note
    "",
    None,
    [SECOND_NOTE],
])
def test_c_an_entry_with_any_other_note_is_refused_out_loud(note):
    entry = correction("CHEMBL8001", DISEASE.id, note)
    with patch("moonlight.engine._read_corrections", return_value=[entry]):
        for ask in (engine.corrections, lambda: engine.looks_wrong(DISEASE.id),
                    lambda: engine.warning_words(DISEASE.id)):
            with pytest.raises(ValueError):
                ask()


@pytest.mark.parametrize("entry", [
    {"medicine_id": "C1", "disease_id": "D1", "date": TODAY},  # no note
    {"medicine_id": "C1", "disease_id": "D1", "date": TODAY, "note": SECOND_NOTE,
     "doctor": "A Name"},  # no doctor is ever named
    {"medicine_id": "", "disease_id": "D1", "date": TODAY, "note": SECOND_NOTE},
    {"medicine_id": "C1", "disease_id": "D1", "date": "19 Nov", "note": SECOND_NOTE},
])
def test_c_the_new_note_does_not_loosen_any_other_check(entry):
    with patch("moonlight.engine._read_corrections", return_value=[entry]):
        with pytest.raises(ValueError):
            engine.corrections()


def test_c_one_card_cannot_carry_both_notes():
    entries = [correction("CHEMBL8001", DISEASE.id, FIRST_NOTE, MONDAY),
               correction("CHEMBL8001", DISEASE.id, SECOND_NOTE)]
    with patch("moonlight.engine._read_corrections", return_value=entries):
        with pytest.raises(ValueError):
            engine.corrections()


# ---- everything else about corrections stays the same ----

def test_an_entry_with_the_new_note_works_only_for_its_own_disease():
    entries = [correction("CHEMBL8002", OTHER.id, SECOND_NOTE)]
    answer = cards([ALPHA, BRAVO], entries)
    assert all("warning" not in item for item in answer["approved"])
    with patch("moonlight.engine._read_corrections", return_value=entries):
        assert engine.warning_words(DISEASE.id) == {}
        assert engine.warning_words(OTHER.id) == {"CHEMBL8002": SECOND_NOTE}


@pytest.mark.parametrize("role, box", [(CHILD, "narrower"), (PARENT, "wider_group")])
def test_a_card_inside_a_folded_box_shows_the_new_words_too(role, box):
    entry_disease = NARROWER if role == CHILD else WIDER
    listed = Listed("CHEMBL8010", "BOXED", (("CHEMBL8010", "BOXED"),), ())
    neighbour = Neighbour(role, entry_disease, (listed,), ())
    plain = cards([ALPHA, path("BOXED", "CHEMBL8010")], neighbours=[neighbour])
    answer = cards([ALPHA, path("BOXED", "CHEMBL8010")],
                   [correction("CHEMBL8010", DISEASE.id, SECOND_NOTE)], neighbours=[neighbour])
    (boxed,) = answer[box]
    assert boxed["warning"] == SECOND_NOTE
    assert boxed["label"]  # still says where the database lists it
    assert {key: value for key, value in boxed.items() if key != "warning"} == plain[box][0]
    assert "warning" not in card(answer, "approved", "alpha")


def test_a_card_with_the_new_note_is_also_ignored_by_the_opposite_way_line():
    # Ticket 3.7 leaves red-warning cards out when it reads the Approved
    # list. A card with the second warning is a red-warning card too.
    clue = Path(Medicine("CLUEUP", (MedicineForm("CHEMBL8020", "CLUEUP", best_stage="APPROVAL",
                                                 withdrawn=False),)),
                PROTEIN, DISEASE, ("AGONIST",), PROTEIN.score, ())
    plain = cards([ALPHA, clue])
    assert "opposite_way" in card(plain, "new_clues", "clueup")["proteins"][0]
    answer = cards([ALPHA, clue], [correction("CHEMBL8001", DISEASE.id, SECOND_NOTE)])
    assert "opposite_way" not in card(answer, "new_clues", "clueup")["proteins"][0]


# ---- the real file: Monday's twelve, and today's ten ----

# Read live from Open Targets on 2026-11-19 and shown to Kashish in a table
# before anything was written. She said yes to every id.
PACRITINIB, MOMELOTINIB = "CHEMBL2035187", "CHEMBL1078178"
POLYCYTHEMIA_VERA = "MONDO_0009891"  # acquired polycythemia vera
ERYTHROID_NEOPLASM = "MONDO_0020703"
FAMILIAL_POLYCYTHEMIA = "MONDO_0001115"
CONNECTIVE_TISSUE = "MONDO_0023603"  # hereditary disorder of connective tissue
ESSENTIAL_THROMBOCYTHEMIA = "MONDO_0005029"
THROMBOCYTOSIS = "MONDO_0002249"  # thrombocytosis disease
THE_FOUR_PAGES = [POLYCYTHEMIA_VERA, ERYTHROID_NEOPLASM, FAMILIAL_POLYCYTHEMIA, CONNECTIVE_TISSUE]
TODAYS_TEN = (
    {(PACRITINIB, page) for page in THE_FOUR_PAGES}
    | {(MOMELOTINIB, page) for page in THE_FOUR_PAGES}
    | {(MOMELOTINIB, ESSENTIAL_THROMBOCYTHEMIA), (MOMELOTINIB, THROMBOCYTOSIS)}
)


def real_corrections():
    return json.loads(CORRECTIONS_FILE.read_text(encoding="utf-8"))


def test_the_real_file_holds_todays_ten_with_the_new_note_and_no_other():
    assert len(TODAYS_TEN) == 10
    today = [entry for entry in real_corrections() if entry["date"] == TODAY]
    assert len(today) == 10  # no pair twice
    assert {(entry["medicine_id"], entry["disease_id"]) for entry in today} == TODAYS_TEN
    for entry in today:
        assert set(entry) == {"medicine_id", "disease_id", "date", "note"}
        assert entry["note"] == SECOND_NOTE
    # Kashish: no entry for momelotinib under myeloproliferative disorder.
    assert all(entry["disease_id"] != "EFO_0004251" for entry in real_corrections())


def test_the_real_file_holds_mondays_twelve_and_todays_ten_and_nothing_else():
    entries = real_corrections()
    # Ticket 2.19 added one: deferoxamine, hemochromatosis. Ticket 2.25 added
    # one: tafamidis, AL amyloidosis (Kashish's yes, 23 Nov).
    assert len(entries) == 24
    assert len(engine.corrections()) == 24
    monday = [entry for entry in entries if entry["date"] == MONDAY]
    assert len(monday) == 12
    assert all(entry["note"] == FIRST_NOTE for entry in monday)
    assert {entry["date"] for entry in entries} == {
        MONDAY, TODAY, TICKET_2_19_DAY, "2026-11-23"}
    # Read as plain text: nothing is left once the keys, the ids, the two
    # days and the two notes are taken away. No room for anybody's name.
    text = CORRECTIONS_FILE.read_text(encoding="utf-8")
    ids = {entry[key] for entry in entries for key in ("medicine_id", "disease_id")}
    for known in ["medicine_id", "disease_id", "date", "note", FIRST_NOTE, SECOND_NOTE,
                  MONDAY, TODAY, TICKET_2_19_DAY, "2026-11-23",
                  *sorted(ids, key=len, reverse=True)]:
        text = text.replace(f'"{known}"', "")
    assert re.sub(r"[\s\[\]{}:,]", "", text) == ""


def test_the_real_file_gives_each_of_todays_pages_the_new_words():
    assert engine.warning_words(POLYCYTHEMIA_VERA) == {
        PACRITINIB: SECOND_NOTE, MOMELOTINIB: SECOND_NOTE}
    assert engine.warning_words(ESSENTIAL_THROMBOCYTHEMIA) == {MOMELOTINIB: SECOND_NOTE}
    assert engine.warning_words(THROMBOCYTOSIS) == {MOMELOTINIB: SECOND_NOTE}
    # Monday's pages still get the old words.
    assert set(engine.warning_words("MONDO_0004975").values()) == {FIRST_WARNING}


# =====================================================================
# PART 2. Clues left out by hand
# =====================================================================

def sixty_clues():
    """Sixty new clues, CLUE01 the first and CLUE60 the last (A to Z, as
    they all have the same points and reports)."""
    return [path(f"CLUE{number:02d}", f"CHEMBL70{number:02d}") for number in range(1, 61)]


LISTED_FOUR = ["CHEMBL7003", "CHEMBL7010", "CHEMBL7011", "CHEMBL7060"]


def names(answer, tab="new_clues"):
    return [item["medicine"] for item in answer[tab]]


# ---- d. four listed clues among 60: 56 cards and the line ----

def test_d_four_listed_clues_among_sixty_leave_56_cards_and_the_line():
    plain = cards(sixty_clues())
    assert len(plain["new_clues"]) == 60 and "wrong_way_line" not in plain
    answer = cards(sixty_clues(), left=[left_out(medicine_id, DISEASE.id)
                                         for medicine_id in LISTED_FOUR])
    assert len(answer["new_clues"]) == 56
    assert answer["wrong_way_line"] == MANY_LINE
    gone = {"CLUE03", "CLUE10", "CLUE11", "CLUE60"}
    assert gone <= {name.upper() for name in names(plain)}
    assert not gone & {name.upper() for name in names(answer)}
    # The other 56 are the same cards, in the same order.
    assert answer["new_clues"] == [item for item in plain["new_clues"]
                                   if item["medicine"].upper() not in gone]


def test_d_with_one_medicine_the_line_is_for_one():
    answer = cards(sixty_clues(), left=[left_out("CHEMBL7003", DISEASE.id)])
    assert len(answer["new_clues"]) == 59
    assert answer["wrong_way_line"] == ONE_LINE


def test_d_with_none_there_is_no_line():
    answer = cards(sixty_clues(), left=[])
    assert len(answer["new_clues"]) == 60
    assert "wrong_way_line" not in answer


def test_d_the_lines_are_kashishs_words_exactly():
    assert engine.wrong_way_line(0) is None
    assert engine.wrong_way_line(1) == ONE_LINE
    assert engine.wrong_way_line(4) == MANY_LINE
    assert engine.wrong_way_line(12) == (
        "12 medicines left out because they push the wrong way for this disease.")


def test_d_a_tablet_form_is_left_out_with_its_medicine():
    # The entry holds the family id, the one on the card. The path is for
    # a tablet form of it.
    form = MedicineForm("CHEMBL7999", "SALTY CITRATE", best_stage="APPROVAL",
                        parent_id="CHEMBL7998", withdrawn=False)
    salty = Path(Medicine("SALTY", (form,)), PROTEIN, DISEASE, DOWN, PROTEIN.score, ())
    answer = cards([salty, path("PLAIN", "CHEMBL7997")],
                   left=[left_out("CHEMBL7998", DISEASE.id)])
    assert names(answer) == ["Plain"]
    assert answer["wrong_way_line"] == ONE_LINE


def test_d_a_left_out_clue_cannot_be_explained():
    found = api._Found(DISEASE, sort_paths(sixty_clues()), [], [], [])
    with patch.object(api, "_find", return_value=found), \
            patch("moonlight.engine._read_left_out",
                  return_value=[left_out("CHEMBL7003", DISEASE.id)]), \
            patch.object(api.explain, "explain", side_effect=AssertionError("explained")):
        response = TestClient(api.app).get(
            "/api/explain", params={"disease_id": DISEASE.id, "clue_id": "CHEMBL7003"})
    assert response.status_code == 404


# ---- e. the same four on another disease's page are still shown ----

def test_e_the_same_four_medicines_on_another_diseases_page_are_still_shown():
    entries = [left_out(medicine_id, DISEASE.id) for medicine_id in LISTED_FOUR]
    paths = [path(f"CLUE{number:02d}", f"CHEMBL70{number:02d}", disease=OTHER)
             for number in range(1, 61)]
    answer = cards(paths, left=entries, disease=OTHER)
    assert len(answer["new_clues"]) == 60
    assert {"CLUE03", "CLUE10", "CLUE11", "CLUE60"} <= {name.upper() for name in names(answer)}
    assert "wrong_way_line" not in answer
    with patch("moonlight.engine._read_left_out", return_value=entries):
        assert engine.pushes_wrong_way(DISEASE.id) == set(LISTED_FOUR)
        assert engine.pushes_wrong_way(OTHER.id) == set()


# ---- f. a listed medicine that is not among the clues is not counted ----

def test_f_a_listed_medicine_that_is_not_among_the_clues_is_not_counted():
    entries = [left_out(medicine_id, DISEASE.id)
               for medicine_id in LISTED_FOUR + ["CHEMBL9999"]]  # five listed, four are clues
    answer = cards(sixty_clues(), left=entries)
    assert len(answer["new_clues"]) == 56
    assert answer["wrong_way_line"] == MANY_LINE


def test_f_if_no_listed_medicine_is_among_the_clues_there_is_no_line():
    answer = cards(sixty_clues(), left=[left_out("CHEMBL9999", DISEASE.id)])
    assert len(answer["new_clues"]) == 60
    assert "wrong_way_line" not in answer


# ---- g. a listed medicine in the In trials tab stays there ----

def test_g_a_listed_medicine_in_the_in_trials_tab_stays_there():
    paths = sixty_clues() + [path("STUDIED", "CHEMBL7100", IN_TRIALS)]
    plain = cards(paths)
    answer = cards(paths, left=[left_out("CHEMBL7100", DISEASE.id)])
    assert names(answer, "being_studied") == ["Studied"]
    assert answer["being_studied"] == plain["being_studied"]
    assert len(answer["new_clues"]) == 60
    assert "wrong_way_line" not in answer  # it would not have been a new clue


def test_g_the_approved_tab_and_both_boxes_are_not_changed_by_the_list():
    child = Neighbour(CHILD, NARROWER, (Listed("CHEMBL7201", "NARROW", (("CHEMBL7201", "NARROW"),), ()),), ())
    parent = Neighbour(PARENT, WIDER, (Listed("CHEMBL7202", "WIDE", (("CHEMBL7202", "WIDE"),), ()),), ())
    paths = sixty_clues()[:5] + [path("OWN", "CHEMBL7200", APPROVED_HERE),
                                 path("NARROW", "CHEMBL7201"), path("WIDE", "CHEMBL7202")]
    entries = [left_out(medicine_id, DISEASE.id)
               for medicine_id in ("CHEMBL7200", "CHEMBL7201", "CHEMBL7202", "CHEMBL7001")]
    plain = cards(paths, neighbours=[child, parent])
    answer = cards(paths, left=entries, neighbours=[child, parent])
    for tab in ("approved", "narrower", "wider_group", "being_studied", "left_out"):
        assert answer[tab] == plain[tab]
    assert names(answer, "approved") == ["Own"]
    assert names(answer, "narrower") == ["Narrow"] and names(answer, "wider_group") == ["Wide"]
    assert len(answer["new_clues"]) == 4  # only CLUE01 was a new clue
    assert answer["wrong_way_line"] == ONE_LINE


# ---- the file, read in one small function and checked strictly ----

def test_the_left_out_file_is_the_one_the_engine_reads():
    assert engine.LEFT_OUT_FILE == LEFT_OUT_FILE
    assert engine._read_left_out() == json.loads(LEFT_OUT_FILE.read_text(encoding="utf-8"))


@pytest.mark.parametrize("entries", [
    [{"medicine_id": "C1", "disease_id": "D1"}],  # no date
    [{"medicine_id": "C1", "date": TODAY}],  # no disease
    [{"medicine_id": "C1", "disease_id": "D1", "date": TODAY, "note": "Why."}],  # a fourth thing
    [{"medicine_id": "C1", "disease_id": "D1", "date": TODAY, "doctor": "A Name"}],
    [{"medicine_id": "", "disease_id": "D1", "date": TODAY}],
    [{"medicine_id": "C1", "disease_id": "", "date": TODAY}],
    [{"medicine_id": "C1", "disease_id": "D1", "date": "19 Nov"}],
    [{"medicine_id": "C1", "disease_id": "D1", "date": "2026-13-45"}],
    [{"medicine_id": 7, "disease_id": "D1", "date": TODAY}],
    ["C1"],
    [["C1", "D1", TODAY]],
    {"medicine_id": "C1", "disease_id": "D1", "date": TODAY},  # not a list
])
def test_a_left_out_entry_that_is_not_written_the_agreed_way_is_refused_out_loud(entries):
    with patch("moonlight.engine._read_left_out", return_value=entries):
        for ask in (engine.left_out_by_hand, lambda: engine.pushes_wrong_way("D1")):
            with pytest.raises(ValueError):
                ask()


def test_a_well_written_left_out_list_is_read_as_pairs():
    entries = [left_out("C1", "D1"), left_out("C2", "D1"), left_out("C1", "D2", MONDAY)]
    with patch("moonlight.engine._read_left_out", return_value=entries):
        assert engine.left_out_by_hand() == {("C1", "D1"), ("C2", "D1"), ("C1", "D2")}
        assert engine.pushes_wrong_way("D1") == {"C1", "C2"}
        assert engine.pushes_wrong_way("D2") == {"C1"}
        assert engine.pushes_wrong_way("D3") == set()


# Read live from Open Targets on 2026-11-19. Kashish said yes to every id.
ADDISON = "MONDO_0015129"  # chronic primary adrenal insufficiency, also called "Addison disease"
ADDISON_FOUR = {
    "CHEMBL295698",   # levoketoconazole
    "CHEMBL1670",     # mitotane
    "CHEMBL3099695",  # osilodrostat
    "CHEMBL934",      # metyrapone
}


def test_the_real_left_out_file_holds_the_four_for_addisons_and_nothing_else():
    # Ticket 2.20 (22 Nov): the file now also holds entries for another
    # disease (anaphylaxis, tests/test_anaphylaxis_left_out.py). "Nothing
    # else" now means: nothing else for Addison's. Every entry in the file
    # still has only the three keys, and the file is still ids and days only.
    every_entry = json.loads(LEFT_OUT_FILE.read_text(encoding="utf-8"))
    for entry in every_entry:
        assert set(entry) == {"medicine_id", "disease_id", "date"}
    entries = [entry for entry in every_entry if entry["disease_id"] == ADDISON]
    # Ticket 2.43 (R1, 24 Nov) added mifepristone for Addison's.
    # tests/test_left_out_r1_r6.py holds it. Here: the four of 19 Nov.
    assert [entry for entry in entries if entry["date"] > TODAY] == [
        {"medicine_id": "CHEMBL1276308", "disease_id": ADDISON, "date": "2026-11-24"}]
    entries = [entry for entry in entries if entry["date"] == TODAY]
    assert len(entries) == 4
    for entry in entries:
        assert entry["date"] == TODAY
    assert {entry["medicine_id"] for entry in entries} == ADDISON_FOUR
    assert {pair for pair in engine.left_out_by_hand() if pair[1] == ADDISON} == {
        (medicine_id, ADDISON) for medicine_id in ADDISON_FOUR | {"CHEMBL1276308"}}
    assert engine.pushes_wrong_way(ADDISON) == ADDISON_FOUR | {"CHEMBL1276308"}
    # Read as plain text: only the keys, the ids and the day. No names, no reasons.
    text = LEFT_OUT_FILE.read_text(encoding="utf-8")
    other_diseases = [entry for entry in every_entry if entry["disease_id"] != ADDISON]
    for entry in other_diseases:  # ticket 2.20: their ids and days, checked in their own test
        assert re.fullmatch(r"CHEMBL\d+", entry["medicine_id"])
        assert re.fullmatch(r"[A-Za-z]+_\d+", entry["disease_id"])
        assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", entry["date"])
    others = {value for entry in other_diseases for value in entry.values()}
    for known in ["medicine_id", "disease_id", "date", ADDISON, TODAY, "2026-11-24",
                  *sorted(ADDISON_FOUR | others | {"CHEMBL1276308"}, key=len, reverse=True)]:
        text = text.replace(f'"{known}"', "")
    assert re.sub(r"[\s\[\]{}:,]", "", text) == ""


def test_the_real_four_are_left_out_on_addisons_page_and_nowhere_else():
    def real_page(disease):
        paths = [path(f"REAL{number}", medicine_id, disease=disease)
                 for number, medicine_id in enumerate(sorted(ADDISON_FOUR), start=1)]
        paths.append(path("OTHER", "CHEMBL7300", disease=disease))
        found = api._Found(disease, sort_paths(paths), [], [], [])
        with patch.object(api, "_find", return_value=found):  # the real two files
            return TestClient(api.app).get("/api/clues", params={"disease_id": disease.id}).json()

    addison = real_page(Disease(ADDISON, "chronic primary adrenal insufficiency"))
    assert names(addison) == ["Other"] and addison["wrong_way_line"] == MANY_LINE
    # One step up, where the same four are top clues too: not on the list.
    parent = real_page(Disease("MONDO_0015128", "primary adrenal insufficiency"))
    assert len(parent["new_clues"]) == 5 and "wrong_way_line" not in parent


# ---- only a hand check may remove a card: no code adds to the file ----

def test_no_code_writes_to_the_left_out_file():
    source = inspect.getsource(engine)
    # The file's name is given once and read once, in the one small function.
    assert source.count("LEFT_OUT_FILE") == 2
    assert "LEFT_OUT_FILE.read_text(" in inspect.getsource(engine._read_left_out)
    for module in (ROOT / "moonlight").glob("*.py"):
        text = module.read_text(encoding="utf-8")
        if module.name != "engine.py":
            assert "left_out.json" not in text and "LEFT_OUT_FILE" not in text
    assert "left_out.json" not in (ROOT / "cli.py").read_text(encoding="utf-8")


# ---- the page: one line at the bottom of the New clues list ----

def test_the_page_has_one_place_for_the_line_at_the_bottom_of_the_new_clues_list():
    panel = PAGE[PAGE.index('id="panel-clues"'):PAGE.index('data-slot="left-out"')]
    assert PAGE.count('id="wrong-way-line"') == 1
    assert panel.count('id="wrong-way-line"') == 1
    # Below the cards, and hidden until there is something to say.
    assert panel.index('id="new-cards"') < panel.index('id="wrong-way-line"')
    assert re.search(r'<p [^>]*id="wrong-way-line"[^>]* hidden></p>', panel)


def test_the_page_shows_the_apis_words_and_types_none_of_its_own():
    assert 'byId("wrong-way-line").textContent = data.wrong_way_line || "";' in PAGE
    assert 'byId("wrong-way-line").hidden = !data.wrong_way_line;' in PAGE
    assert "push the wrong way" not in PAGE and "pushes the wrong way" not in PAGE


def test_the_safety_line_is_still_on_the_page():
    assert ("For learning and research exploration, not medical advice. Never start, "
            "stop or change any medicine without a doctor.") in PAGE
