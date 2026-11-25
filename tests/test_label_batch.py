"""Ticket 2.41. Label batch: red warnings and missing approvals, from labels.

Only list entries. Every entry is backed by an official label, fetched on
24 Nov 2026 and saved in fixtures/labels_read/, with one line in its
README.md in the shape a tester asked for:

    card | change | quoted label sentence | link | value replaced

Part A: fourteen red warnings in moonlight/corrections.json, each with the
note already on twelve cards, word for word. Each card's OWN source link is
the label that was read: it does not name the disease as a use.

Part B: six missing approvals in moonlight/approvals.json, each read from
the current label. Left out, and reported (the ticket's STOP AND ASK):
hydrocortisone for Addison disease, because two pages fit.

The entries are proposals until MAIN 3 has read the saved label text.

Saved files only: fixtures/labels_read/ (the labels and each disease's own
list, asked live on 2026-11-24, Open Targets data 26.09) and the myasthenia
gravis list in fixtures/approvals_by_hand/. No network.
"""

import json
import pathlib
import re
from unittest.mock import patch

import pytest

from moonlight import api, engine

import test_approvals_batch as second_batch
import test_approvals_by_hand as first_batch
import test_approvals_fourth_batch as fourth_batch
import test_approvals_third_batch as third_batch  # ticket 2.39

ROOT = pathlib.Path(__file__).resolve().parent.parent
APPROVALS_FILE = ROOT / "moonlight" / "approvals.json"
CORRECTIONS_FILE = ROOT / "moonlight" / "corrections.json"
LEFT_OUT_FILE = ROOT / "moonlight" / "left_out.json"
LABELS = ROOT / "fixtures" / "labels_read"
README = LABELS / "README.md"
OUR_LISTS = LABELS / "disease_drugs"
MYASTHENIA_LIST = ROOT / "fixtures" / "approvals_by_hand" / "disease_drugs"  # ticket 2.34's

THE_DAY = "2026-11-24"
NOTE = "This looks like a mistake in the database. The official label is for a different disease."
ADDED_LINE = "This approval is missing from the database. We added it from the official label."
LIMITED_LINE = "The label covers only some people with this disease."
DAILYMED = "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid="

HYPOTHYROIDISM = "MONDO_0005420"
MELANOMA = "MONDO_0005105"
MIGRAINE = "MONDO_0005277"
MYASTHENIA = "MONDO_0009688"
RHEUMATOID = "MONDO_0008383"
TYPE_2_DIABETES = "MONDO_0005148"
AHUS = "MONDO_0016244"  # atypical hemolytic-uremic syndrome
EOE = "MONDO_0005361"  # eosinophilic esophagitis
DUCHENNE = "MONDO_0010679"  # Duchenne muscular dystrophy
DERMATOMYOSITIS = "MONDO_0016367"
ADDISON_PAGES = ("MONDO_0015129", "MONDO_0015128")  # the two that fit, not added

# Part A, in the ticket's order: (medicine, its id, disease, the card's own
# label, the saved file).
PART_A = [
    ("Cholestyramine", "CHEMBL1201625", HYPOTHYROIDISM,
     "362ddd91-a63f-4ec6-841a-75785dd208c8", "questran-cholestyramine"),
    ("Fenofibrate", "CHEMBL672", HYPOTHYROIDISM,
     "66d2c555-2880-4ac6-80f8-69a00f1fbc4c", "fenofibrate-capsules-mylan"),
    ("Mecasermin", "CHEMBL1201716", HYPOTHYROIDISM,
     "a8b27a1b-a611-4f91-ad22-76d4b390c3ae", "increlex-mecasermin"),
    ("OMEGA-3-ACID Ethyl Esters", "CHEMBL1200711", HYPOTHYROIDISM,
     "0d842966-26bc-4521-b401-635a83618012", "omega-3-acid-ethyl-esters"),
    ("Hydroxyurea", "CHEMBL467", MELANOMA,
     "0a5c7030-5fac-4708-b309-f9d07103285a", "hydroxyurea-capsules"),
    ("Butalbital", "CHEMBL454", MIGRAINE,
     "04bddbc4-86c7-4bac-9327-010568020568", "butalbital-aspirin-caffeine-codeine"),
    ("Fentanyl", "CHEMBL596", MIGRAINE,
     "4906457e-30ad-4da7-b3ac-bb9e6651a670", "abstral-fentanyl"),
    ("Amifampridine", "CHEMBL354077", MYASTHENIA,
     "2731310a-c060-4d3e-ba41-763d791f63a9", "ruzurgi-amifampridine"),
    ("Guanidine", "CHEMBL821", MYASTHENIA,
     "903fbd33-e5d9-41fb-9414-7bd6f42a8593", "guanidine-hydrochloride"),
    ("Pralidoxime", "CHEMBL1420", MYASTHENIA,
     "2741d8fd-51c2-46be-880b-99f2b20a6137", "protopam-pralidoxime"),
    ("Trientine", "CHEMBL609", RHEUMATOID,
     "c34f77a7-996b-4470-b5df-d946a7fe5dbe", "syprine-trientine"),
    ("Fenofibrate", "CHEMBL672", TYPE_2_DIABETES,
     "0f958942-1504-40a1-8ad8-43df2c3f717e", "fenofibrate-tablets"),
    ("Fenofibric Acid", "CHEMBL981", TYPE_2_DIABETES,
     "31c80f84-0169-4659-b9cf-8f897ed319eb", "fibricor-fenofibric-acid"),
    ("Ticagrelor", "CHEMBL398435", TYPE_2_DIABETES,
     "4f9bd52a-99a7-4606-92b4-456a917aabef", "brilinta-ticagrelor"),
]
NEW_CORRECTIONS = [
    {"medicine_id": medicine_id, "disease_id": disease_id, "date": THE_DAY, "note": NOTE}
    for _, medicine_id, disease_id, _, _ in PART_A
]

ULTOMIRIS = DAILYMED + "a9a590d9-0217-43c7-908d-e62a71279791"
DUPIXENT = DAILYMED + "595f437d-2729-40bb-9c62-c8ece1f82780"
EOHILIA = DAILYMED + "56f2023a-69b2-4470-b4ad-af7ec1be527a"
ELEVIDYS = DAILYMED + "3525abcd-fbd2-46c5-9706-cffdf2e8a361"
ACTHAR = DAILYMED + "7b48ddec-e815-45f4-9ca0-5c0daaf56f30"

RAVULIZUMAB = "CHEMBL3989986"
DUPILUMAB = "CHEMBL2108675"
BUDESONIDE = "CHEMBL1370"
DELANDISTROGENE = "CHEMBL4650241"
CORTICOTROPIN = "CHEMBL1201610"
HYDROCORTISONE = "CHEMBL389621"

PART_B = [
    {"medicine_id": RAVULIZUMAB, "name": "Ravulizumab", "disease_id": MYASTHENIA,
     "date": THE_DAY, "label": ULTOMIRIS, "limited": True},
    {"medicine_id": RAVULIZUMAB, "name": "Ravulizumab", "disease_id": AHUS,
     "date": THE_DAY, "label": ULTOMIRIS},
    {"medicine_id": DUPILUMAB, "name": "Dupilumab", "disease_id": EOE,
     "date": THE_DAY, "label": DUPIXENT},
    {"medicine_id": BUDESONIDE, "name": "Budesonide", "disease_id": EOE,
     "date": THE_DAY, "label": EOHILIA},
    {"medicine_id": DELANDISTROGENE, "name": "Delandistrogene Moxeparvovec",
     "disease_id": DUCHENNE, "date": THE_DAY, "label": ELEVIDYS, "limited": True},
    {"medicine_id": CORTICOTROPIN, "name": "Corticotropin", "disease_id": DERMATOMYOSITIS,
     "date": THE_DAY, "label": ACTHAR},
]
PART_B_FILES = {ULTOMIRIS: "ultomiris-ravulizumab", DUPIXENT: "dupixent-dupilumab",
                EOHILIA: "eohilia-budesonide",
                ELEVIDYS: "elevidys-delandistrogene-moxeparvovec",
                ACTHAR: "acthar-repository-corticotropin"}
# Where each card sat before, from its disease's own list alone. On the
# live page of 24 Nov, dupilumab and budesonide were ALSO in the wider-group
# folded box (approved for esophagitis). That box needs the parent's list,
# which is not saved, so it is not shown here.
PART_B_BEFORE = {
    (RAVULIZUMAB, MYASTHENIA): ["more_in_trials"],
    (RAVULIZUMAB, AHUS): ["more_in_trials"],
    (DUPILUMAB, EOE): ["more_in_trials"],
    (BUDESONIDE, EOE): ["more_in_trials"],
    (DELANDISTROGENE, DUCHENNE): ["more_in_trials"],
    (CORTICOTROPIN, DERMATOMYOSITIS): ["more_in_trials"],
}
FIRST_FIFTEEN = fourth_batch.FIRST_TEN + fourth_batch.FOURTH_BATCH


def names(value):
    if isinstance(value, dict):
        return f'{value["name"]} {value["disease_id"]}'
    if isinstance(value, tuple) and len(value) == 5:
        return f"{value[0]} {value[2]}"
    return None


def load(file):
    return json.loads(file.read_text(encoding="utf-8"))


def list_file(disease_id):
    folder = MYASTHENIA_LIST if disease_id == MYASTHENIA else OUR_LISTS
    return folder / f"{disease_id}.response.json"


def saved_rows(disease_id):
    answer = load(list_file(disease_id))
    assert answer["data"]["disease"]["id"] == disease_id
    return answer["data"]["disease"]["drugAndClinicalCandidates"]["rows"]


def family_rows(disease_id, medicine_id):
    return [row for row in saved_rows(disease_id)
            if medicine_id in (row["drug"]["id"],
                               (row["drug"]["parentMolecule"] or {}).get("id"))]


def saved_post_json(body):
    """Stands in for fetch._post_json: each disease's own saved list."""
    assert set(body) == {"query", "variables"}
    assert "drugAndClinicalCandidates" in body["query"] and "parents" not in body["query"]
    file = list_file(body["variables"]["diseaseId"])
    if not file.exists():
        raise AssertionError(f"no saved list for {body['variables']}")
    return load(file)


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


def tabs(disease_id, entries=None):
    """The tabs from the disease's own saved list alone: with the REAL
    approvals file, or with these entries."""
    if entries is None:
        hand = engine.added_by_hand(disease_id)
    else:
        with patch.object(engine, "_read_approvals", return_value=entries):
            hand = engine.added_by_hand(disease_id)
    return second_batch.tabs_for(disease_id, hand)


# ---- the README: one line per entry, in the tester's shape ----

def readme_lines():
    """The README's table rows, each split into its five cells."""
    rows = []
    for line in README.read_text(encoding="utf-8").splitlines():
        cells = line.split(" | ")
        if len(cells) == 5 and cells[0] != "card":
            rows.append(cells)
    return rows


def readme_line(medicine_id, disease_id):
    found = [cells for cells in readme_lines()
             if re.findall(r"\b(?:CHEMBL\d+|[A-Za-z]+_\d+)\b", cells[0])
             == [medicine_id, disease_id]]
    assert len(found) == 1, (medicine_id, disease_id)
    return found[0]


def saved_label(link):
    """The saved label whose first line is this link."""
    found = [file for file in sorted(LABELS.glob("*.txt"))
             if file.read_text(encoding="utf-8").splitlines()[0] == link]
    assert len(found) == 1, link
    return found[0]


def test_the_readme_header_is_the_testers_shape():
    assert "card | change | quoted label sentence | link | value replaced" in \
        README.read_text(encoding="utf-8").splitlines()


def test_the_readme_has_one_line_per_entry_and_no_other():
    pairs = sorted((re.findall(r"CHEMBL\d+", cells[0])[0],
                    re.findall(r"\b(?:MONDO|EFO|Orphanet)_\d+", cells[0])[0])
                   for cells in readme_lines())
    expected = sorted([(entry["medicine_id"], entry["disease_id"]) for entry in NEW_CORRECTIONS]
                      + [(entry["medicine_id"], entry["disease_id"]) for entry in PART_B])
    assert pairs == expected
    assert len(pairs) == 20


def test_every_saved_label_backs_an_entry():
    links = {DAILYMED + setid for *_, setid, _ in PART_A} | set(PART_B_FILES)
    assert sorted(file.stem for file in LABELS.glob("*.txt")) == sorted(
        [short for *_, short in PART_A] + list(PART_B_FILES.values()))
    assert {file.read_text(encoding="utf-8").splitlines()[0]
            for file in LABELS.glob("*.txt")} == links


@pytest.mark.parametrize("card", PART_A, ids=names)
def test_part_a_label_is_saved_with_its_link_and_date_and_names_the_medicine(card):
    medicine, medicine_id, disease_id, setid, short = card
    file = LABELS / f"{short}.txt"
    assert saved_label(DAILYMED + setid) == file
    lines = file.read_text(encoding="utf-8").splitlines()
    assert lines[0] == DAILYMED + setid
    assert lines[1] == THE_DAY
    assert "INDICATIONS" in lines[3].upper()  # then the section, from its heading
    # The saved file names the medicine (or one of its forms).
    forms = {row["drug"]["name"].lower() for row in family_rows(disease_id, medicine_id)}
    assert any(name in "\n".join(lines).lower() for name in forms | {medicine.lower()})


@pytest.mark.parametrize("card", PART_A, ids=names)
def test_part_a_readme_line_quotes_the_saved_label_word_for_word(card):
    medicine, medicine_id, disease_id, setid, short = card
    cells = readme_line(medicine_id, disease_id)
    assert cells[0].startswith(f"{medicine} ({medicine_id})")
    assert cells[1] == "red warning"
    assert cells[2] in (LABELS / f"{short}.txt").read_text(encoding="utf-8")
    assert cells[3] == DAILYMED + setid
    assert cells[4] == "no warning"


@pytest.mark.parametrize("entry", PART_B, ids=names)
def test_part_b_label_is_saved_and_the_readme_line_quotes_it(entry):
    file = LABELS / f"{PART_B_FILES[entry['label']]}.txt"
    assert saved_label(entry["label"]) == file
    text = file.read_text(encoding="utf-8")
    lines = text.splitlines()
    assert lines[0] == entry["label"] and lines[1] == THE_DAY
    assert "INDICATIONS" in lines[3].upper()
    forms = {row["drug"]["name"].lower()
             for row in family_rows(entry["disease_id"], entry["medicine_id"])}
    assert any(name in text.lower() for name in forms | {entry["name"].lower()})
    cells = readme_line(entry["medicine_id"], entry["disease_id"])
    assert cells[0].startswith(f'{entry["name"]} ({entry["medicine_id"]})')
    assert cells[1].startswith("added under Approved")
    assert ("limited" in cells[1]) == entry.get("limited", False)
    assert cells[2] in text
    assert cells[3] == entry["label"]


# ---- Part A: the fourteen red warnings ----

def test_the_corrections_file_holds_the_old_24_then_the_fourteen_new_ones():
    entries = load(CORRECTIONS_FILE)
    assert len(entries) == 122  # Ticket 2.58: ipratropium on asthma deleted (25N-13), six type 2 diabetes entries added, dated 2026-11-26 (25N-16); Ticket 3.10 (MAIN 4, 25 Nov, Q14): mannitol's red entry on asthma deleted; ticket 2.56, signed rule Q22 (and Q3, Q13 for the other lists): five more, dated 2026-11-25; Ticket 2.55, signed answers Q10 and Q22: dicumarol, sodium phenylbutyrate; ticket 2.54, signed answers Q22 and 10b: simvastatin, misoprostol; ticket 2.52 added seven; ticket 2.47 added Obizur; ticket 2.40 added one after these: prasterone; ticket 2.45, 62 more
    assert entries[24:38] == NEW_CORRECTIONS
    assert [entry["date"] for entry in entries[:24]] == sorted(
        entry["date"] for entry in entries[:24])
    assert all(entry["date"] < THE_DAY for entry in entries[:24])


def test_each_new_entry_has_exactly_the_four_keys_and_the_note_already_used():
    old_notes = [entry["note"] for entry in load(CORRECTIONS_FILE)[:24]]
    assert old_notes.count(NOTE) == 12  # "It is already on twelve cards."
    entries = load(CORRECTIONS_FILE)
    # Ticket 2.55: dicumarol (Kashish's signed Q10) carries the third note.
    third = [e for e in entries[24:] if e["note"] == engine.THIRD_NOTE]
    assert [(e["medicine_id"], e["disease_id"]) for e in third] == [("CHEMBL1466", "MONDO_0010602")]
    for entry in entries[24:]:
        assert list(entry) == ["medicine_id", "disease_id", "date", "note"]
        if entry not in third:
            assert entry["note"] == NOTE


def test_no_pair_is_written_twice():
    pairs = [(entry["medicine_id"], entry["disease_id"]) for entry in load(CORRECTIONS_FILE)]
    assert len(set(pairs)) == len(pairs)


@pytest.mark.parametrize("disease_id, ids", [
    (HYPOTHYROIDISM, {"CHEMBL1201625", "CHEMBL672", "CHEMBL1201716", "CHEMBL1200711"}),
    (MELANOMA, {"CHEMBL467"}),
    (MIGRAINE, {"CHEMBL454", "CHEMBL596"}),
    (MYASTHENIA, {"CHEMBL354077", "CHEMBL821", "CHEMBL1420"}),
    (RHEUMATOID, {"CHEMBL609", "CHEMBL90593"}),  # ticket 2.40 added prasterone
    (TYPE_2_DIABETES, {"CHEMBL672", "CHEMBL981", "CHEMBL398435",
                       # ticket 2.52: biotin, cyanocobalamin, folic acid, omega-3-acid
                       # ethyl esters, pyridoxine, tyrosine
                       "CHEMBL857", "CHEMBL2110563", "CHEMBL1622", "CHEMBL1200711",
                       "CHEMBL1364", "CHEMBL925",
                       # Ticket 2.54, signed answer Q22: simvastatin
                       "CHEMBL1064",
                       # Ticket 2.58, 25N-16: candesartan, olmesartan, atenolol,
                       # chlorthalidone, hydrochlorothiazide, lisinopril
                       "CHEMBL1014", "CHEMBL1200692", "CHEMBL24", "CHEMBL1055",
                       "CHEMBL435", "CHEMBL1237"}),
])
def test_the_engine_gives_each_page_the_red_words_for_its_cards_only(disease_id, ids):
    assert engine.looks_wrong(disease_id) == ids
    assert engine.warning_words(disease_id) == {medicine_id: NOTE for medicine_id in ids}


@pytest.mark.parametrize("card", PART_A, ids=names)
def test_the_cards_own_source_is_the_label_that_was_read(card):
    """The ticket: the card must be on that disease's Approved tab, with that
    link as its source. On the disease's own list, the medicine is approved
    for the disease, and its approval report is that label."""
    _, medicine_id, disease_id, setid, _ = card
    rows = family_rows(disease_id, medicine_id)
    assert "APPROVAL" in [row["maxClinicalStage"] for row in rows]
    reports = [(report["clinicalStage"], report["source"])
               for row in rows for report in row["clinicalReports"]
               if report["url"] == DAILYMED + setid]
    assert reports == [("APPROVAL", "DailyMed")]
    found = tabs(disease_id)
    assert first_batch.only_under_approved(found, medicine_id)
    approved = [medicine for medicine in found.approved if medicine.id == medicine_id][0]
    assert approved.source_record == DAILYMED + setid


@pytest.mark.parametrize("card", PART_A, ids=names)
def test_each_card_now_shows_the_red_words_and_sits_in_the_folded_box(card):
    _, medicine_id, disease_id, _, _ = card
    found = tabs(disease_id)
    approved = [medicine for medicine in found.approved if medicine.id == medicine_id][0]
    sent = api._approved_json(approved, engine.looks_wrong(disease_id),
                              engine.warning_words(disease_id))
    assert sent["warning"] == NOTE
    assert medicine_id in [medicine.id for medicine in
                           engine.wrong_approvals_box(found.approved, disease_id)]


# ---- Part B: the six missing approvals ----

def test_the_approvals_file_holds_the_first_fifteen_then_the_six_new_ones():
    # Ticket 2.39 marked valbenazine (entry 8) "limited".
    assert load(APPROVALS_FILE)[:21] == third_batch.as_written_now(FIRST_FIFTEEN) + PART_B
    assert len(load(APPROVALS_FILE)) == 31  # Ticket 2.54, signed answers Q2 and Q13: hydrocortisone, primidone; 2.34b added avatrombopag after these, 2.46 seven more


def test_two_new_entries_are_limited_and_four_are_not():
    new = load(APPROVALS_FILE)[15:21]  # ticket 2.34b added avatrombopag after these
    assert [(entry["name"], entry["disease_id"]) for entry in new
            if entry.get("limited") is True] == [
        ("Ravulizumab", MYASTHENIA), ("Delandistrogene Moxeparvovec", DUCHENNE)]
    assert [entry["name"] for entry in new if "limited" not in entry] == [
        "Ravulizumab", "Dupilumab", "Budesonide", "Corticotropin"]


def test_the_engine_reads_the_six_new_entries():
    assert engine.approvals_by_hand()[15:21] == [  # then ticket 2.34b's avatrombopag
        engine.HandApproval(entry["medicine_id"], entry["name"], entry["disease_id"],
                            entry["label"], limited=entry.get("limited", False))
        for entry in PART_B]


@pytest.mark.parametrize("entry", PART_B, ids=names)
def test_the_id_is_the_parent_medicine_open_targets_uses_in_the_saved_list(entry):
    rows = family_rows(entry["disease_id"], entry["medicine_id"])
    assert [row["drug"]["id"] for row in rows] == [entry["medicine_id"]]
    drug = rows[0]["drug"]
    assert drug["name"] == entry["name"].upper()
    assert drug["parentMolecule"] is None
    assert drug["childMolecules"] == []


@pytest.mark.parametrize("entry", PART_B, ids=names)
def test_the_database_records_no_approval_on_the_list_so_the_line_is_true(entry):
    rows = family_rows(entry["disease_id"], entry["medicine_id"])
    assert rows[0]["maxClinicalStage"] != "APPROVAL"
    assert "APPROVAL" not in [report["clinicalStage"] for report in rows[0]["clinicalReports"]]


@pytest.mark.parametrize("entry", PART_B, ids=names)
def test_none_is_withdrawn(entry):
    drug = family_rows(entry["disease_id"], entry["medicine_id"])[0]["drug"]
    warnings = [warning["warningType"].lower() for warning in drug["drugWarnings"]]
    assert "withdrawn" not in warnings
    assert "WITHDRAWAL" not in [report["clinicalStage"] for report in
                                family_rows(entry["disease_id"],
                                            entry["medicine_id"])[0]["clinicalReports"]]


def test_the_new_entries_clash_with_no_existing_rule():
    pairs = {(entry["medicine_id"], entry["disease_id"]) for entry in PART_B}
    for file in (CORRECTIONS_FILE, LEFT_OUT_FILE):
        assert not pairs & {(one["medicine_id"], one["disease_id"]) for one in load(file)}
    assert engine.approvals_left_out() == []
    all_pairs = [(entry["medicine_id"], entry["disease_id"]) for entry in load(APPROVALS_FILE)]
    assert len(set(all_pairs)) == len(all_pairs)


@pytest.mark.parametrize("entry", PART_B, ids=names)
def test_before_the_card_was_not_under_approved(entry):
    places = first_batch.everywhere(tabs(entry["disease_id"], FIRST_FIFTEEN))
    assert sorted(place for place, ids in places.items() if entry["medicine_id"] in ids) == \
        sorted(PART_B_BEFORE[(entry["medicine_id"], entry["disease_id"])])


@pytest.mark.parametrize("entry", PART_B, ids=names)
def test_now_the_card_is_only_under_approved_with_the_line_and_its_label(entry):
    found = tabs(entry["disease_id"])
    assert first_batch.only_under_approved(found, entry["medicine_id"])
    card = [medicine for medicine in found.approved if medicine.id == entry["medicine_id"]][0]
    assert card.proof_note == ADDED_LINE
    assert card.source_record == entry["label"]
    assert card.label is None  # the main list, not a folded box
    assert card.limit_note == (LIMITED_LINE if entry.get("limited") else None)
    sent = api._approved_json(card)
    assert sent["source"] == entry["label"] and sent["proof_note"] == ADDED_LINE
    assert ("limit_note" in sent) == entry.get("limited", False)


@pytest.mark.parametrize("disease_id", [MYASTHENIA, AHUS, EOE, DUCHENNE, DERMATOMYOSITIS])
def test_every_other_card_stays_where_it_was(disease_id):
    added = [entry["medicine_id"] for entry in PART_B if entry["disease_id"] == disease_id]
    before = first_batch.everywhere(tabs(disease_id, FIRST_FIFTEEN))
    after = first_batch.everywhere(tabs(disease_id))
    for place, ids in before.items():
        if place == "approved":
            assert sorted(after[place]) == sorted(ids + added)
        else:
            assert after[place] == [i for i in ids if i not in added]


def test_each_new_entry_is_handed_only_to_its_own_disease():
    assert [entry.medicine_id for entry in engine.added_by_hand(MYASTHENIA)] == [
        fourth_batch.ECULIZUMAB, RAVULIZUMAB]
    assert [entry.medicine_id for entry in engine.added_by_hand(AHUS)] == [RAVULIZUMAB]
    assert [entry.medicine_id for entry in engine.added_by_hand(EOE)] == [DUPILUMAB, BUDESONIDE]
    assert [entry.medicine_id for entry in engine.added_by_hand(DUCHENNE)] == [DELANDISTROGENE]
    assert [entry.medicine_id for entry in engine.added_by_hand(DERMATOMYOSITIS)] == [
        CORTICOTROPIN]
    # Not to a narrower page the search also shows.
    for other in ("MONDO_0005407", "MONDO_0008054", "MONDO_0018324", "MONDO_0035290"):
        assert engine.added_by_hand(other) == []


# ---- STOP AND ASK: hydrocortisone for Addison disease waits ----

def test_hydrocortisone_has_no_entry():
    # Ticket 2.54, signed answer Q2: Kashish's A adds hydrocortisone for
    # MONDO_0015129 only. The other page that fits (MONDO_0015128) still has none.
    entries = [e for e in load(APPROVALS_FILE) if e["medicine_id"] == HYDROCORTISONE]
    assert [e["disease_id"] for e in entries] == ["MONDO_0015129"]


@pytest.mark.parametrize("disease_id", ADDISON_PAGES)
def test_both_pages_that_fit_list_hydrocortisone_in_trials_only(disease_id):
    """Two pages fit "Addison disease": chronic primary adrenal insufficiency
    (its "also called" name is Addison disease) and primary adrenal
    insufficiency (the label's words are "primary or secondary adrenocortical
    insufficiency"). The ticket says: add nothing and report both."""
    rows = family_rows(disease_id, HYDROCORTISONE)
    assert [row["drug"]["name"] for row in rows] == ["HYDROCORTISONE"]
    assert rows[0]["maxClinicalStage"] in ("PHASE_2_3", "PHASE_3")
    assert "APPROVAL" not in [report["clinicalStage"] for report in rows[0]["clinicalReports"]]
