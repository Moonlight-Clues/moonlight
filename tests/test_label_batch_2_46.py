"""Ticket 2.46. Approvals reported missing, added from their labels.

List entries only, in moonlight/approvals.json, the way ticket 2.41 did. Each
entry is backed by an official label, fetched on 25 Nov 2026 and saved in
fixtures/labels_read/2.46/, with one line in that folder's README.md in the
shape a tester asked for:

    card | change | quoted label sentence | link | value replaced

Seven are added (the ticket's order, dated 2026-11-25):

  - apitegromab for spinal muscular atrophy (MONDO_0001516)
  - hemin for acute intermittent porphyria (MONDO_0008294), limited
  - fitusiran for haemophilia A (MONDO_0010602)
  - anti-inhibitor coagulant complex (FEIBA) for haemophilia A, limited
  - human coagulation factor VIII (Hemofil M, Koate) for haemophilia A
  - desmopressin (DDAVP injection) for haemophilia A, limited
  - ciprofloxacin (Otiprio) for otitis media with effusion. No "limited" key:
    the ticket leaves that to MAIN 3.

Not added, and reported: Alphanate, Humate-P and Wilate (Open Targets has no
medicine for the complex itself). Itvisma is not in this ticket. Roctavian and
Obizur are only reported.

Saved files only: fixtures/labels_read/2.46/ (the labels and each disease's
own list, asked live on 2026-11-25). No network.
"""

import json
import pathlib
import re
from unittest.mock import patch

import pytest

from moonlight import api, engine

import test_approvals_batch as second_batch
from test_wider_labels_2_63 import APPROVAL_ROWS  # noqa: E402  ticket 2.63 (D2): the rows it added to approvals.json
import test_approvals_by_hand as first_batch

ROOT = pathlib.Path(__file__).resolve().parent.parent
APPROVALS_FILE = ROOT / "moonlight" / "approvals.json"
CORRECTIONS_FILE = ROOT / "moonlight" / "corrections.json"
LEFT_OUT_FILE = ROOT / "moonlight" / "left_out.json"
FOLDER = ROOT / "fixtures" / "labels_read" / "2.46"
README = FOLDER / "README.md"
OUR_LISTS = FOLDER / "disease_drugs"

THE_DAY = "2026-11-25"
ADDED_LINE = "This approval is missing from the database. We added it from the official label."
LIMITED_LINE = "The label covers only some people with this disease."
DAILYMED = "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid="
OTIPRIO_PDF = "https://www.accessdata.fda.gov/drugsatfda_docs/label/2018/207986s002lbl.pdf"

SMA = "MONDO_0001516"  # spinal muscular atrophy
PROXIMAL_SMA = "MONDO_0019079"  # the second page that fits apitegromab: no entry
PORPHYRIA = "MONDO_0008294"  # acute intermittent porphyria
HAEMOPHILIA_A = "MONDO_0010602"
OME = "MONDO_0005892"  # otitis media with effusion

APITEGROMAB = "CHEMBL4594326"
HEMIN = "CHEMBL1200662"
FITUSIRAN = "CHEMBL4297754"
FEIBA = "CHEMBL4297953"
FACTOR_VIII = "CHEMBL2108175"
VON_WILLEBRAND_FACTOR = "CHEMBL4298126"
DESMOPRESSIN = "CHEMBL1429"
CIPROFLOXACIN = "CHEMBL8"
ROCTAVIAN = "CHEMBL4297579"
OBIZUR = "CHEMBL5315075"  # susoctocog alfa

ISEMBYLD = DAILYMED + "b1cd8ab8-8a10-48ed-9806-75a44f22b963"
PANHEMATIN = DAILYMED + "9984267a-4d57-4444-9bb5-16bca7dea691"
QFITLIA = DAILYMED + "6dd2f8ac-6f90-4cbf-b197-97d74964135c"
FEIBA_LABEL = DAILYMED + "752604e5-4ea2-44f4-83ed-1569373f6412"
HEMOFIL = DAILYMED + "b8953ff7-3bba-4a0b-a486-f26fb81f05d9"
DDAVP = DAILYMED + "651f6fee-a2c7-431b-8d5d-58b156c72244"

NEW_ENTRIES = [
    {"medicine_id": APITEGROMAB, "name": "Apitegromab", "disease_id": SMA,
     "date": THE_DAY, "label": ISEMBYLD},
    {"medicine_id": HEMIN, "name": "Hemin", "disease_id": PORPHYRIA,
     "date": THE_DAY, "label": PANHEMATIN, "limited": True},
    {"medicine_id": FITUSIRAN, "name": "Fitusiran", "disease_id": HAEMOPHILIA_A,
     "date": THE_DAY, "label": QFITLIA},
    {"medicine_id": FEIBA, "name": "Anti-Inhibitor Coagulant Complex",
     "disease_id": HAEMOPHILIA_A, "date": THE_DAY, "label": FEIBA_LABEL, "limited": True},
    {"medicine_id": FACTOR_VIII, "name": "Human Coagulation Factor VIII",
     "disease_id": HAEMOPHILIA_A, "date": THE_DAY, "label": HEMOFIL},
    {"medicine_id": DESMOPRESSIN, "name": "Desmopressin", "disease_id": HAEMOPHILIA_A,
     "date": THE_DAY, "label": DDAVP, "limited": True},
    {"medicine_id": CIPROFLOXACIN, "name": "Ciprofloxacin", "disease_id": OME,
     "date": THE_DAY, "label": OTIPRIO_PDF},
]

# Each entry's saved file, its product name as the label says it (the saved
# file must name the medicine), and the sentence the README quotes.
SAVED = {
    ISEMBYLD: ("isembyld-apitegromab", "ISEMBYLD",
               "ISEMBYLD is indicated for the treatment of spinal muscular atrophy (SMA) in "
               "adults and pediatric patients 2 years of age and older who are currently "
               "receiving a survival motor neuron 2 (SMN2)-targeted treatment."),
    PANHEMATIN: ("panhematin-hemin", "PANHEMATIN",
                 "PANHEMATIN is a hemin for injection indicated for the amelioration of "
                 "recurrent attacks of acute intermittent porphyria temporally related to the "
                 "menstrual cycle in susceptible women, after initial carbohydrate therapy is "
                 "known or suspected to be inadequate."),
    QFITLIA: ("qfitlia-fitusiran", "QFITLIA",
              "QFITLIA is indicated for routine prophylaxis to prevent or reduce the "
              "frequency of bleeding episodes in adult and pediatric patients aged 12 years "
              "and older with hemophilia A or B with or without factor VIII or IX inhibitors."),
    FEIBA_LABEL: ("feiba-anti-inhibitor-coagulant-complex", "FEIBA",
                  "FEIBA is an Anti-Inhibitor Coagulant Complex indicated for use in "
                  "hemophilia A and B patients with inhibitors for:"),
    HEMOFIL: ("hemofil-m-antihemophilic-factor", "HEMOFIL M",
              "HEMOFIL M is indicated in hemophilia A (classical hemophilia) for the "
              "prevention and control of hemorrhagic episodes."),
    DDAVP: ("ddavp-injection-desmopressin", "DDAVP",
            "DDAVP Injection is indicated for patients with hemophilia A with factor VIII "
            "coagulant activity levels greater than 5% without factor VIII antibodies to:"),
    OTIPRIO_PDF: ("otiprio-ciprofloxacin", "OTIPRIO",
                  "The treatment of pediatric patients (6 months of age and older) with "
                  "bilateral otitis media with effusion undergoing tympanostomy tube "
                  "placement."),
}

# Where each card sat before, from its disease's own list alone. On the live
# page of 25 Nov, fitusiran and factor VIII were in the box "Already being
# studied for this disease" (a protein path also finds them: that needs the
# protein searches, which are not saved). Either way: not under Approved.
BEFORE = {
    (APITEGROMAB, SMA): ["new_in_trials"],
    (HEMIN, PORPHYRIA): [],
    (FITUSIRAN, HAEMOPHILIA_A): ["more_in_trials"],
    (FEIBA, HAEMOPHILIA_A): ["more_in_trials"],
    (FACTOR_VIII, HAEMOPHILIA_A): ["more_in_trials"],
    (DESMOPRESSIN, HAEMOPHILIA_A): [],
    (CIPROFLOXACIN, OME): [],
}
# The ones the disease's own list holds. Hemin and ciprofloxacin are not on
# their pages' lists at all.
ON_THE_LIST = {pair: places for pair, places in BEFORE.items() if pair[0] not in (HEMIN, CIPROFLOXACIN)}


def pair(entry):
    return (entry["medicine_id"], entry["disease_id"])


def names(entry):
    return f'{entry["name"]} {entry["disease_id"]}'


def load(file):
    return json.loads(file.read_text(encoding="utf-8"))


def saved_rows(disease_id):
    answer = load(OUR_LISTS / f"{disease_id}.response.json")
    assert answer["data"]["disease"]["id"] == disease_id
    return answer["data"]["disease"]["drugAndClinicalCandidates"]["rows"]


def family_rows(disease_id, medicine_id):
    return [row for row in saved_rows(disease_id)
            if medicine_id in (row["drug"]["id"], (row["drug"]["parentMolecule"] or {}).get("id"))]


def saved_post_json(body):
    """Stands in for fetch._post_json: each disease's own saved list."""
    assert set(body) == {"query", "variables"}
    assert "drugAndClinicalCandidates" in body["query"] and "parents" not in body["query"]
    file = OUR_LISTS / f'{body["variables"]["diseaseId"]}.response.json'
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
    rows = []
    for line in README.read_text(encoding="utf-8").splitlines():
        cells = line.split(" | ")
        if len(cells) == 5 and cells[0] != "card":
            rows.append(cells)
    return rows


def readme_line(medicine_id, disease_id):
    found = [cells for cells in readme_lines()
             if re.findall(r"\b(?:CHEMBL\d+|[A-Za-z]+_\d+)\b", cells[0]) == [medicine_id, disease_id]]
    assert len(found) == 1, (medicine_id, disease_id)
    return found[0]


def test_the_readme_header_is_the_testers_shape():
    assert "card | change | quoted label sentence | link | value replaced" in \
        README.read_text(encoding="utf-8").splitlines()


def test_the_readme_has_one_line_per_entry_and_no_other():
    pairs = sorted((re.findall(r"CHEMBL\d+", cells[0])[0],
                    re.findall(r"\b(?:MONDO|EFO|Orphanet)_\d+", cells[0])[0])
                   for cells in readme_lines())
    assert pairs == sorted(pair(entry) for entry in NEW_ENTRIES)
    assert len(pairs) == 7


def test_every_label_in_the_folder_backs_an_entry():
    """The folder's own .txt files are the seven entries' labels, and no
    other. Koate, the skipped three and the two report-only labels sit in
    their own sub-folders."""
    assert sorted(file.stem for file in FOLDER.glob("*.txt")) == sorted(
        short for short, _, _ in SAVED.values())
    assert {file.read_text(encoding="utf-8").splitlines()[0] for file in FOLDER.glob("*.txt")} == set(SAVED)


@pytest.mark.parametrize("entry", NEW_ENTRIES, ids=names)
def test_the_label_is_saved_and_the_readme_line_quotes_it_word_for_word(entry):
    short, product, sentence = SAVED[entry["label"]]
    file = FOLDER / f"{short}.txt"
    text = file.read_text(encoding="utf-8")
    lines = text.splitlines()
    assert lines[0] == entry["label"] and lines[1] == THE_DAY
    assert "INDICATIONS" in lines[3].upper()  # then the section, from its heading
    # The saved file names the medicine, and holds the quoted sentence.
    assert product.lower() in text.lower()
    assert sentence in lines
    cells = readme_line(entry["medicine_id"], entry["disease_id"])
    assert cells[0].startswith(f'{entry["name"]} ({entry["medicine_id"]})')
    assert cells[1].startswith("added under Approved")
    assert cells[2] == sentence and cells[2] in text
    assert cells[3] == entry["label"]


@pytest.mark.parametrize("entry", NEW_ENTRIES, ids=names)
def test_the_readme_says_limited_exactly_where_the_entry_does(entry):
    cells = readme_line(entry["medicine_id"], entry["disease_id"])
    assert cells[1].endswith(", limited") == entry.get("limited", False)


@pytest.mark.parametrize("entry", NEW_ENTRIES, ids=names)
def test_every_label_names_its_disease_as_an_indication(entry):
    """The one condition for an entry: the saved indications name the
    disease (the label's own spelling)."""
    short, _, _ = SAVED[entry["label"]]
    text = (FOLDER / f"{short}.txt").read_text(encoding="utf-8").lower()
    words = {SMA: "spinal muscular atrophy", PORPHYRIA: "acute intermittent porphyria",
             HAEMOPHILIA_A: "hemophilia a", OME: "otitis media with effusion"}
    assert words[entry["disease_id"]] in text


def test_koate_is_read_too_and_names_the_same_disease():
    text = (FOLDER / "also_read" / "koate-antihemophilic-factor.txt").read_text(encoding="utf-8")
    lines = text.splitlines()
    assert lines[0].startswith(DAILYMED) and lines[1] == THE_DAY and "KOATE" in lines[2].upper()
    assert "patients with hemophilia A (hereditary Factor VIII deficiency)" in text


# ---- the approvals file ----

def test_the_approvals_file_ends_with_the_seven_new_entries_in_the_tickets_order():
    entries = load(APPROVALS_FILE)
    assert entries[22:29] == NEW_ENTRIES
    assert all(entry["date"] < THE_DAY for entry in entries[:22])


def test_the_same_pair_is_never_written_twice():
    pairs = [pair(entry) for entry in load(APPROVALS_FILE)]
    assert len(set(pairs)) == len(pairs)


def test_three_entries_are_limited_and_the_rest_say_nothing_about_it():
    new = load(APPROVALS_FILE)[22:29]
    assert [entry["name"] for entry in new if entry.get("limited") is True] == [
        "Hemin", "Anti-Inhibitor Coagulant Complex", "Desmopressin"]
    assert [entry["name"] for entry in new if "limited" not in entry] == [
        "Apitegromab", "Fitusiran", "Human Coagulation Factor VIII", "Ciprofloxacin"]
    assert not any(entry.get("limited") is False for entry in new)


def test_each_entry_has_the_five_keys_in_the_files_order():
    for entry in load(APPROVALS_FILE)[22:29]:
        keys = list(entry)
        assert keys[:5] == ["medicine_id", "name", "disease_id", "date", "label"]
        assert keys[5:] in ([], ["limited"])


def test_the_engine_reads_the_seven_new_entries():
    assert engine.approvals_by_hand()[22:29] == [
        engine.HandApproval(entry["medicine_id"], entry["name"], entry["disease_id"],
                            entry["label"], limited=entry.get("limited", False))
        for entry in NEW_ENTRIES]


def test_the_other_lists_hold_none_of_the_seven_pairs():
    """The ticket changes neither corrections.json nor left_out.json: no
    pair of the seven is on either, so no entry is held back."""
    new = {pair(entry) for entry in NEW_ENTRIES}
    for file in (CORRECTIONS_FILE, LEFT_OUT_FILE):
        assert not new & {(e["medicine_id"], e["disease_id"]) for e in load(file)}
    for entry in NEW_ENTRIES:
        assert entry["medicine_id"] in [hand.medicine_id
                                         for hand in engine.added_by_hand(entry["disease_id"])]


# ---- the ids are Open Targets' own ----

@pytest.mark.parametrize("entry", [e for e in NEW_ENTRIES if pair(e) in ON_THE_LIST], ids=names)
def test_the_id_is_the_parent_medicine_open_targets_uses_in_the_saved_list(entry):
    rows = family_rows(entry["disease_id"], entry["medicine_id"])
    assert [row["drug"]["id"] for row in rows] == [entry["medicine_id"]]
    assert rows[0]["drug"]["parentMolecule"] is None
    # The saved name is the entry's name, in capitals, or the same words.
    assert rows[0]["drug"]["name"].lower() == entry["name"].lower()


@pytest.mark.parametrize("entry", [e for e in NEW_ENTRIES if pair(e) in ON_THE_LIST], ids=names)
def test_the_database_records_no_approval_on_the_list_so_the_line_is_true(entry):
    for row in family_rows(entry["disease_id"], entry["medicine_id"]):
        assert row["maxClinicalStage"] != "APPROVAL"
        assert "APPROVAL" not in [report["clinicalStage"] for report in row["clinicalReports"]]
        warnings = [w["warningType"].lower() for w in row["drug"]["drugWarnings"]]
        assert "withdrawn" not in warnings
        assert "WITHDRAWAL" not in [report["clinicalStage"] for report in row["clinicalReports"]]


@pytest.mark.parametrize("entry", [e for e in NEW_ENTRIES if pair(e) not in ON_THE_LIST], ids=names)
def test_hemin_and_ciprofloxacin_are_not_on_their_pages_lists_at_all(entry):
    assert family_rows(entry["disease_id"], entry["medicine_id"]) == []


def test_heme_arginate_is_another_medicine_and_stays_where_it_was():
    """Heme arginate (Normosang) sits on the porphyria page's list as a
    trial. It is not hemin under another name: its own id, no entry."""
    rows = family_rows(PORPHYRIA, "CHEMBL4297285")
    assert [row["drug"]["name"] for row in rows] == ["HEME ARGINATE"]
    assert "CHEMBL4297285" not in {e["medicine_id"] for e in load(APPROVALS_FILE)}


# ---- the pages: before and after ----

@pytest.mark.parametrize("entry", NEW_ENTRIES, ids=names)
def test_before_the_card_was_in_a_trials_box_or_nowhere_and_not_under_approved(entry):
    places = first_batch.everywhere(tabs(entry["disease_id"], []))
    assert entry["medicine_id"] not in places["approved"]
    assert [place for place, ids in places.items()
            if entry["medicine_id"] in ids] == BEFORE[pair(entry)]


@pytest.mark.parametrize("entry", NEW_ENTRIES, ids=names)
def test_now_the_card_is_only_under_approved_with_the_line_and_its_label(entry):
    found = tabs(entry["disease_id"])
    assert first_batch.only_under_approved(found, entry["medicine_id"])
    card = [m for m in found.approved if m.id == entry["medicine_id"]][0]
    assert card.source_record == entry["label"]
    sent = api._approved_json(card, engine.looks_wrong(entry["disease_id"]),
                              engine.warning_words(entry["disease_id"]),
                              {}, engine.limit_notes(found, entry["disease_id"]))
    assert ADDED_LINE in json.dumps(sent)
    assert (LIMITED_LINE in json.dumps(sent)) == entry.get("limited", False)


@pytest.mark.parametrize("disease_id, ids", [
    (SMA, [APITEGROMAB]), (OME, [CIPROFLOXACIN]),
    (PORPHYRIA, [HEMIN] + [row["medicine_id"] for row in APPROVAL_ROWS]),  # ticket 2.63 (D2): givosiran too
    (HAEMOPHILIA_A, [FITUSIRAN, FEIBA, FACTOR_VIII, DESMOPRESSIN])])
def test_an_entry_works_only_for_its_own_page(disease_id, ids):
    assert [hand.medicine_id for hand in engine.added_by_hand(disease_id)] == ids


def test_the_second_spinal_page_gets_no_card_from_this_ticket():
    """Apitegromab is also on "proximal spinal muscular atrophy" (a trial
    there). The entry is for the page the label names, and no other."""
    assert engine.added_by_hand(PROXIMAL_SMA) == []
    assert APITEGROMAB not in first_batch.everywhere(tabs(PROXIMAL_SMA))["approved"]


# ---- left out, with the reasons ----

def test_nothing_was_added_for_the_plasma_complexes_or_for_itvisma():
    entries = load(APPROVALS_FILE)
    ids = {entry["medicine_id"] for entry in entries}
    # Open Targets has no medicine for the Alphanate / Humate-P / Wilate
    # complexes: only their parts. Factor VIII's pair is written once (for
    # Hemofil M), and von Willebrand factor is not written at all.
    assert VON_WILLEBRAND_FACTOR not in ids
    assert [e["label"] for e in entries if e["medicine_id"] == FACTOR_VIII] == [HEMOFIL]
    assert "CHEMBL4297240" not in ids  # onasemnogene: Itvisma is a new brand of it
    for brand in ("alphanate", "humate", "wilate", "itvisma"):
        assert not [e for e in entries if brand in e["label"].lower() or brand in e["name"].lower()]


@pytest.mark.parametrize("short", [
    "alphanate-antihemophilic-factor-vwf-complex", "humate-p-antihemophilic-factor-vwf-complex",
    "wilate-vwf-factor-viii-complex"])
def test_each_skipped_label_is_saved_and_names_haemophilia_a(short):
    lines = (FOLDER / "skipped" / f"{short}.txt").read_text(encoding="utf-8").splitlines()
    assert lines[0].startswith(DAILYMED) and lines[1] == THE_DAY
    assert "INDICATIONS" in lines[3].upper()
    assert "hemophilia a" in "\n".join(lines).lower()


# ---- reported, not changed: Roctavian and Obizur ----

@pytest.mark.parametrize("medicine_id", [ROCTAVIAN, OBIZUR])
def test_roctavian_and_obizur_are_still_on_the_haemophilia_a_approved_tab(medicine_id):
    assert first_batch.only_under_approved(tabs(HAEMOPHILIA_A), medicine_id)
    assert medicine_id not in {e["medicine_id"] for e in load(APPROVALS_FILE)}


def test_the_two_report_only_labels_say_what_they_are_for():
    roctavian = (FOLDER / "report_only" / "roctavian-valoctocogene-roxaparvovec.txt").read_text(
        encoding="utf-8")
    assert "adults with severe hemophilia A" in roctavian
    obizur = (FOLDER / "report_only" / "obizur-susoctocog-alfa.txt").read_text(encoding="utf-8")
    assert "acquired hemophilia A" in obizur
