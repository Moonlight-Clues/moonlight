"""Ticket 2.45. Red warnings from the overnight label check: 62 entries.

Only list entries: moonlight/corrections.json. Every entry is backed by
official labels, fetched on 25 Nov 2026 and saved in fixtures/labels_read/2.45/
with one line in its README.md in the shape the ticket asked for:

    card | change | quoted label sentence | link(s) searched | value replaced

The ticket's 97 cards were each read against ALL current labels of the
medicine. 62 got the red warning (PART A below). 23 are on the wrong source
link: another product's label does name the disease, so NO red warning
(WRONG_SOURCE). 12 were left alone and reported (NOT_ADDED): not sure, or no
US label (conivaptan; dicumarol on the haemophilia A page).

Saved files only: fixtures/labels_read/2.45/ (the labels, and the own list of
the five diseases with the most entries, asked live on 2026-11-25 with
fetch.py's DISEASE_DRUGS_QUERY). No network.
"""

import hashlib
import json
import pathlib
import re
from unittest.mock import patch

import pytest

from moonlight import api, engine

# Ticket 2.62: the signed rows of tests/test_red_warnings_2_62.py (delete a row there and these follow).
from test_red_warnings_2_62 import LIMIT_ROWS, RED_ROWS  # noqa: E402

import test_approvals_batch as second_batch
import test_approvals_by_hand as first_batch

ROOT = pathlib.Path(__file__).resolve().parent.parent
CORRECTIONS_FILE = ROOT / "moonlight" / "corrections.json"
APPROVALS_FILE = ROOT / "moonlight" / "approvals.json"
LEFT_OUT_FILE = ROOT / "moonlight" / "left_out.json"
LABELS = ROOT / "fixtures" / "labels_read" / "2.45"
WRONG_DIR = LABELS / "wrong_source"
README = LABELS / "README.md"
OUR_LISTS = LABELS / "disease_drugs"

THE_DAY = "2026-11-25"
NOTE = "This looks like a mistake in the database. The official label is for a different disease."
DAILYMED = "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid="
# The 39 entries that were there before this ticket, exactly as they were.
OLD_39_SHA256 = "b06d45c2ddb1b8e1940d783b458bfe57e30db62b1948aaf4ed8d95c1b104b269"

# Part A, in the ticket's order: (medicine, its id, disease id, disease, saved file).
PART_A = [
    ('Ofloxacin', 'CHEMBL4', 'MONDO_0011438', 'acne', 'ofloxacin-acne'),
    ('Chlorambucil', 'CHEMBL515', 'MONDO_0004967', 'acute lymphoblastic leukemia', 'chlorambucil-acute-lymphoblastic-leukemia'),
    ('Plerixafor', 'CHEMBL18442', 'MONDO_0004967', 'acute lymphoblastic leukemia', 'plerixafor-acute-lymphoblastic-leukemia'),
    ('Tagraxofusp', 'CHEMBL4297573', 'MONDO_0018874', 'acute myeloid leukemia', 'tagraxofusp-acute-myeloid-leukemia'),
    ('Cladribine', 'CHEMBL1619', 'MONDO_0002280', 'anemia', 'cladribine-anemia'),
    ('Felbamate', 'CHEMBL1094', 'MONDO_0002280', 'anemia', 'felbamate-anemia'),
    ('Imiglucerase', 'CHEMBL1201632', 'MONDO_0002280', 'anemia', 'imiglucerase-anemia'),
    ('Levoleucovorin', 'CHEMBL1908841', 'MONDO_0002280', 'anemia', 'levoleucovorin-anemia'),
    ('Pentostatin', 'CHEMBL1580', 'MONDO_0002280', 'anemia', 'pentostatin-anemia'),
    ('Candesartan Cilexetil', 'CHEMBL1014', 'EFO_0003913', 'angina pectoris', 'candesartan-cilexetil-angina-pectoris'),
    ('Chlorthalidone', 'CHEMBL1055', 'EFO_0003913', 'angina pectoris', 'chlorthalidone-angina-pectoris'),
    ('Hydrochlorothiazide', 'CHEMBL435', 'EFO_0003913', 'angina pectoris', 'hydrochlorothiazide-angina-pectoris'),
    ('Dexamethasone', 'CHEMBL384467', 'MONDO_0015909', 'aplastic anemia', 'dexamethasone-aplastic-anemia'),
    ('Dexamethasone Phosphoric Acid', 'CHEMBL1201302', 'MONDO_0015909', 'aplastic anemia', 'dexamethasone-phosphoric-acid-aplastic-anemia'),
    ('Prednisolone', 'CHEMBL131', 'MONDO_0015909', 'aplastic anemia', 'prednisolone-aplastic-anemia'),
    ('Prednisone', 'CHEMBL635', 'MONDO_0015909', 'aplastic anemia', 'prednisone-aplastic-anemia'),
    ('Flunisolide', 'CHEMBL1512', 'MONDO_0004979', 'asthma', 'flunisolide-asthma'),
    ('Ipratropium', 'CHEMBL1621597', 'MONDO_0004979', 'asthma', 'ipratropium-asthma'),
    ('Mannitol', 'CHEMBL689', 'MONDO_0004979', 'asthma', 'mannitol-asthma'),
    ('Bempedoic Acid', 'CHEMBL3545313', 'MONDO_0005311', 'atherosclerosis', 'bempedoic-acid-atherosclerosis'),
    ('Promethazine', 'CHEMBL643', 'MONDO_0004980', 'atopic eczema', 'promethazine-atopic-eczema'),
    ('Griseofulvin', 'CHEMBL562', 'MONDO_0002026', 'candidiasis', 'griseofulvin-candidiasis'),
    ('Ceftaroline Fosamil', 'CHEMBL501122', 'MONDO_0005300', 'chronic kidney disease', 'ceftaroline-fosamil-chronic-kidney-disease'),
    ('Oseltamivir', 'CHEMBL1229', 'MONDO_0005300', 'chronic kidney disease', 'oseltamivir-chronic-kidney-disease'),
    ('Resmetirom', 'CHEMBL3261331', 'MONDO_0005155', 'cirrhosis of liver', 'resmetirom-cirrhosis-of-liver'),
    ('Ribavirin', 'CHEMBL1643', 'MONDO_0005155', 'cirrhosis of liver', 'ribavirin-cirrhosis-of-liver'),
    ('Semaglutide', 'CHEMBL2108724', 'MONDO_0005155', 'cirrhosis of liver', 'semaglutide-cirrhosis-of-liver'),
    ('Azithromycin', 'CHEMBL529', 'MONDO_0009061', 'cystic fibrosis', 'azithromycin-cystic-fibrosis'),
    ('Buspirone', 'CHEMBL49', 'MONDO_0002050', 'depressive disorder', 'buspirone-depressive-disorder'),
    ('Lisdexamfetamine', 'CHEMBL1201222', 'MONDO_0005041', 'glaucoma', 'lisdexamfetamine-glaucoma'),
    ('Doxorubicin', 'CHEMBL53463', 'MONDO_0005252', 'heart failure', 'doxorubicin-heart-failure'),
    ('Olmesartan Medoxomil', 'CHEMBL1200692', 'MONDO_0005252', 'heart failure', 'olmesartan-medoxomil-heart-failure'),
    ('Sodium Chloride', 'CHEMBL1200574', 'MONDO_0005252', 'heart failure', 'sodium-chloride-heart-failure'),
    ('Tolvaptan', 'CHEMBL344159', 'MONDO_0005252', 'heart failure', 'tolvaptan-heart-failure'),
    ('Mirtazapine', 'CHEMBL654', 'MONDO_0013600', 'insomnia', 'mirtazapine-insomnia'),
    ('Bivalirudin', 'CHEMBL5314348', 'MONDO_0006805', 'intermediate coronary syndrome', 'bivalirudin-intermediate-coronary-syndrome'),
    ('Clindamycin Phosphate', 'CHEMBL3184512', 'MONDO_0005052', 'irritable bowel syndrome', 'clindamycin-phosphate-irritable-bowel-syndrome'),
    ('Ibrutinib', 'CHEMBL1873475', 'MONDO_0018876', 'mantle cell lymphoma', 'ibrutinib-mantle-cell-lymphoma'),
    ('Candesartan Cilexetil', 'CHEMBL1014', 'MONDO_0005068', 'myocardial infarction', 'candesartan-cilexetil-myocardial-infarction'),
    ('Doxazosin', 'CHEMBL707', 'MONDO_0005068', 'myocardial infarction', 'doxazosin-myocardial-infarction'),
    ('Hydrochlorothiazide', 'CHEMBL435', 'MONDO_0005068', 'myocardial infarction', 'hydrochlorothiazide-myocardial-infarction'),
    ('Nadolol', 'CHEMBL521606', 'MONDO_0005068', 'myocardial infarction', 'nadolol-myocardial-infarction'),
    ('Olmesartan Medoxomil', 'CHEMBL1200692', 'MONDO_0005068', 'myocardial infarction', 'olmesartan-medoxomil-myocardial-infarction'),
    ('Spironolactone', 'CHEMBL1393', 'MONDO_0005068', 'myocardial infarction', 'spironolactone-myocardial-infarction'),
    ('Torsemide', 'CHEMBL1148', 'MONDO_0005068', 'myocardial infarction', 'torsemide-myocardial-infarction'),
    ('Amifampridine', 'CHEMBL354077', 'MONDO_0021248', 'nervous system neoplasm', 'amifampridine-nervous-system-neoplasm'),
    ('Posaconazole', 'CHEMBL1397', 'MONDO_0001475', 'neutropenia', 'posaconazole-neutropenia'),
    ('Prasterone', 'CHEMBL90593', 'MONDO_0005178', 'osteoarthritis', 'prasterone-osteoarthritis'),
    ('Celecoxib', 'CHEMBL118', 'MONDO_0004247', 'peptic ulcer disease', 'celecoxib-peptic-ulcer-disease'),
    ('Dexamethasone', 'CHEMBL384467', 'MONDO_0004247', 'peptic ulcer disease', 'dexamethasone-peptic-ulcer-disease'),
    ('Dexamethasone Phosphoric Acid', 'CHEMBL1201302', 'MONDO_0004247', 'peptic ulcer disease', 'dexamethasone-phosphoric-acid-peptic-ulcer-disease'),
    ('Prednisolone', 'CHEMBL131', 'MONDO_0004247', 'peptic ulcer disease', 'prednisolone-peptic-ulcer-disease'),
    ('Prednisone', 'CHEMBL635', 'MONDO_0004247', 'peptic ulcer disease', 'prednisone-peptic-ulcer-disease'),
    ('Chlorothiazide', 'CHEMBL842', 'MONDO_0005081', 'preeclampsia', 'chlorothiazide-preeclampsia'),
    ('Chlorthalidone', 'CHEMBL1055', 'MONDO_0005081', 'preeclampsia', 'chlorthalidone-preeclampsia'),
    ('Hydrochlorothiazide', 'CHEMBL435', 'MONDO_0005081', 'preeclampsia', 'hydrochlorothiazide-preeclampsia'),
    ('Indapamide', 'CHEMBL406', 'MONDO_0005081', 'preeclampsia', 'indapamide-preeclampsia'),
    ('Metolazone', 'CHEMBL878', 'MONDO_0005081', 'preeclampsia', 'metolazone-preeclampsia'),
    ('Spironolactone', 'CHEMBL1393', 'MONDO_0005081', 'preeclampsia', 'spironolactone-preeclampsia'),
    ('Triamterene', 'CHEMBL585', 'MONDO_0005081', 'preeclampsia', 'triamterene-preeclampsia'),
    ('Penicillamine', 'CHEMBL1430', 'MONDO_0003937', 'spondylitis', 'penicillamine-spondylitis'),
    ('Ziprasidone', 'CHEMBL708', 'MONDO_0005477', 'ventricular tachycardia', 'ziprasidone-ventricular-tachycardia'),
]
NEW_CORRECTIONS = [
    {"medicine_id": medicine_id, "disease_id": disease_id, "date": THE_DAY, "note": NOTE}
    for _, medicine_id, disease_id, _, _ in PART_A
]

# 23 cards: another product of the same medicine IS approved for the disease.
WRONG_SOURCE = [
    ('Pasireotide', 'CHEMBL3349607', 'MONDO_0019933', 'acromegaly', 'pasireotide-acromegaly'),
    ('Fluticasone Propionate', 'CHEMBL1473', 'MONDO_0011786', 'allergic rhinitis', 'fluticasone-propionate-allergic-rhinitis'),
    ('Tiotropium', 'CHEMBL1900528', 'MONDO_0004979', 'asthma', 'tiotropium-asthma'),
    ('Imiquimod', 'CHEMBL1282', 'MONDO_0020804', 'basal cell carcinoma', 'imiquimod-basal-cell-carcinoma'),
    ('Efgartigimod Alfa', 'CHEMBL4297551', 'MONDO_0006702', 'chronic inflammatory demyelinating polyradiculoneuropathy', 'efgartigimod-alfa-chronic-inflammatory-demyelinating-polyradiculoneuropathy'),
    ('Eplerenone', 'CHEMBL1095097', 'MONDO_0005252', 'heart failure', 'eplerenone-heart-failure'),
    ('Lisinopril Anhydrous', 'CHEMBL1237', 'MONDO_0005252', 'heart failure', 'lisinopril-anhydrous-heart-failure'),
    ('Etodolac', 'CHEMBL622', 'MONDO_0011429', 'juvenile idiopathic arthritis', 'etodolac-juvenile-idiopathic-arthritis'),
    ('Doxycycline Anhydrous', 'CHEMBL1433', 'MONDO_0005136', 'malaria', 'doxycycline-anhydrous-malaria'),
    ('Quinidine', 'CHEMBL1294', 'MONDO_0005136', 'malaria', 'quinidine-malaria'),
    ('Acetaminophen', 'CHEMBL112', 'MONDO_0005277', 'migraine disorder', 'acetaminophen-migraine-disorder'),
    ('Aspirin', 'CHEMBL25', 'MONDO_0005277', 'migraine disorder', 'aspirin-migraine-disorder'),
    ('Caffeine', 'CHEMBL113', 'MONDO_0005277', 'migraine disorder', 'caffeine-migraine-disorder'),
    ('Ibuprofen', 'CHEMBL521', 'MONDO_0005277', 'migraine disorder', 'ibuprofen-migraine-disorder'),
    ('Telmisartan', 'CHEMBL1017', 'MONDO_0005068', 'myocardial infarction', 'telmisartan-myocardial-infarction'),
    ('Valsartan', 'CHEMBL1069', 'MONDO_0005068', 'myocardial infarction', 'valsartan-myocardial-infarction'),
    ('Paroxetine', 'CHEMBL490', 'MONDO_0008114', 'obsessive-compulsive disorder', 'paroxetine-obsessive-compulsive-disorder'),
    ('Paroxetine', 'CHEMBL490', 'MONDO_0005383', 'panic disorder', 'paroxetine-panic-disorder'),
    ('Venlafaxine', 'CHEMBL637', 'MONDO_0005383', 'panic disorder', 'venlafaxine-panic-disorder'),
    ('Paroxetine', 'CHEMBL490', 'MONDO_0005146', 'post-traumatic stress disorder', 'paroxetine-post-traumatic-stress-disorder'),
    ('Dabigatran Etexilate', 'CHEMBL539697', 'MONDO_0005279', 'pulmonary embolism', 'dabigatran-etexilate-pulmonary-embolism'),
    ('Ciprofloxacin', 'CHEMBL8', 'MONDO_0005619', 'typhoid fever', 'ciprofloxacin-typhoid-fever'),
    ('Risankizumab', 'CHEMBL3990029', 'MONDO_0005101', 'ulcerative colitis', 'risankizumab-ulcerative-colitis'),
]
# Left alone: (medicine, id, disease id). Not sure, or no US label.
NOT_ADDED = [
    ('Ezetimibe', 'CHEMBL1138', 'MONDO_0005311'),
    ('Progesterone', 'CHEMBL103', 'MONDO_0006096'),
    ('Faricimab', 'CHEMBL4297750', 'MONDO_0007935'),
    ('Hydrochlorothiazide', 'CHEMBL435', 'MONDO_0005252'),
    ('Icosapent Ethyl', 'CHEMBL2095209', 'MONDO_0002525'),
    ('Amlodipine', 'CHEMBL1491', 'MONDO_0005068'),
    ('Eplerenone', 'CHEMBL1095097', 'MONDO_0005068'),
    ('Benzocaine', 'CHEMBL278172', 'MONDO_0002258'),
    ('Chlorhexidine', 'CHEMBL790', 'MONDO_0002258'),
    ('Salicylic Acid', 'CHEMBL424', 'MONDO_0002898'),
]
# Ticket 2.55, Kashish's signed Q10: dicumarol on haemophilia A, left alone
# here (study P12: no US label at all), now has its own entry with the third
# note. tests/test_red_note_2_55.py holds it.
DICUMAROL = ("Dicumarol", "CHEMBL1466", "MONDO_0010602")
# Ticket 2.56, rule Q22 (a label that names the disease only to rule it out is
# not an approval): amlodipine and conivaptan on heart failure, left alone here,
# now have entries. tests/test_task12_batch1.py holds them.
MOVED_2_56 = [
    ('Amlodipine', 'CHEMBL1491', 'MONDO_0005252'),
    ('Conivaptan', 'CHEMBL1755', 'MONDO_0005252'),
]
# How each wrong-source disease is named in the label that was saved as proof.
NAMED = {
    "MONDO_0019933": r"acromegaly", "MONDO_0011786": r"seasonal allergic rhinitis",
    "MONDO_0004979": r"treatment of asthma", "MONDO_0020804": r"basal cell carcinoma",
    "MONDO_0006702": r"demyelinating polyneuropathy", "MONDO_0005252": r"heart failure",
    "MONDO_0011429": r"juvenile arthritis", "MONDO_0005136": r"malaria",
    "MONDO_0005277": r"treats migraine", "MONDO_0005068": r"myocardial infarction",
    "MONDO_0008114": r"obsessive compulsive disorder", "MONDO_0005383": r"panic disorder",
    "MONDO_0005146": r"posttraumatic stress disorder", "MONDO_0005279": r"pulmonary embolism",
    "MONDO_0005619": r"typhoid fever", "MONDO_0005101": r"ulcerative colitis",
}

# The five diseases with the most new entries have their own saved list.
PAGES = ["MONDO_0005068", "MONDO_0005081", "MONDO_0002280", "MONDO_0005252", "MONDO_0004247"]


def names(card):
    return f"{card[0]} {card[2]}"


def load(file):
    return json.loads(file.read_text(encoding="utf-8"))


def saved_post_json(body):
    """Stands in for fetch._post_json: each page's own saved list."""
    assert set(body) == {"query", "variables"}
    assert "drugAndClinicalCandidates" in body["query"] and "parents" not in body["query"]
    file = OUR_LISTS / f"{body['variables']['diseaseId']}.response.json"
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


# ---- the README: one line per entry, in the ticket's shape ----

def readme_rows():
    rows = []
    for line in README.read_text(encoding="utf-8").splitlines():
        cells = line.split(" | ")
        if len(cells) == 5 and cells[0] != "card":
            rows.append(cells)
    return rows


def readme_row(medicine_id, disease_id):
    found = [cells for cells in readme_rows()
             if re.findall(r"\b(?:CHEMBL\d+|[A-Za-z]+_\d+)\b", cells[0]) == [medicine_id, disease_id]]
    assert len(found) == 1, (medicine_id, disease_id)
    return found[0]


def test_the_readme_header_is_the_tickets_shape():
    assert "card | change | quoted label sentence | link(s) searched | value replaced" in \
        README.read_text(encoding="utf-8").splitlines()


def test_the_readme_has_one_row_per_entry_and_no_other():
    pairs = sorted((re.findall(r"CHEMBL\d+", cells[0])[0],
                    re.findall(r"\b(?:MONDO|EFO|Orphanet)_\d+", cells[0])[0])
                   for cells in readme_rows())
    assert pairs == sorted((e["medicine_id"], e["disease_id"]) for e in NEW_CORRECTIONS)
    assert len(pairs) == 62


def test_the_saved_files_are_exactly_the_62_and_the_23_proofs():
    assert sorted(file.stem for file in LABELS.glob("*.txt")) == sorted(card[4] for card in PART_A)
    assert sorted(file.stem for file in WRONG_DIR.glob("*.txt")) == sorted(
        card[4] for card in WRONG_SOURCE)


@pytest.mark.parametrize("card", PART_A, ids=names)
def test_part_a_label_is_saved_with_link_date_name_line_and_whole_section(card):
    medicine, medicine_id, disease_id, disease, short = card
    lines = (LABELS / f"{short}.txt").read_text(encoding="utf-8").splitlines()
    assert lines[0].startswith(DAILYMED) and re.fullmatch(r"[0-9a-f-]{36}", lines[0][len(DAILYMED):])
    assert lines[1] == THE_DAY
    assert "INDICATIONS" in lines[3].upper()  # then the section, from its heading
    # The product name line (line 3) names the medicine, or the page does.
    word = medicine.split()[0].lower()
    assert word in "\n".join(lines[2:4]).lower() or word in "\n".join(lines).lower()
    assert len(lines) > 4


@pytest.mark.parametrize("card", PART_A, ids=names)
def test_part_a_readme_row_quotes_the_saved_label_word_for_word(card):
    medicine, medicine_id, disease_id, disease, short = card
    cells = readme_row(medicine_id, disease_id)
    text = (LABELS / f"{short}.txt").read_text(encoding="utf-8")
    assert cells[0] == f"{medicine} ({medicine_id}), {disease} ({disease_id})"
    assert cells[1] == "red warning"
    assert cells[2] in text
    links = cells[3].split()
    assert text.splitlines()[0] in links  # the label that was read first
    assert cells[4].startswith("no warning")


@pytest.mark.parametrize("card", WRONG_SOURCE, ids=names)
def test_wrong_source_proof_names_the_disease_and_gets_no_red_warning(card):
    medicine, medicine_id, disease_id, disease, short = card
    lines = (WRONG_DIR / f"{short}.txt").read_text(encoding="utf-8").splitlines()
    assert lines[0].startswith(DAILYMED) and lines[1] == THE_DAY
    assert "INDICATIONS" in lines[3].upper()
    assert re.search(NAMED[disease_id], "\n".join(lines[3:]), re.I)
    assert (medicine.split()[0].lower() in "\n".join(lines).lower()
            or medicine_id in ("CHEMBL25", "CHEMBL113", "CHEMBL112"))  # Excedrin Migraine
    pairs = {(e["medicine_id"], e["disease_id"]) for e in load(CORRECTIONS_FILE)}
    # Ticket 2.62 (signed sheet row 9) made caffeine on migraine red on purpose.
    pairs -= {(m, d) for _, m, d, _, _ in RED_ROWS}
    assert (medicine_id, disease_id) not in pairs


@pytest.mark.parametrize("card", NOT_ADDED, ids=names)
def test_a_card_left_alone_has_no_entry(card):
    _, medicine_id, disease_id = card
    assert (medicine_id, disease_id) not in {
        (e["medicine_id"], e["disease_id"]) for e in load(CORRECTIONS_FILE)}


def test_the_ticket_cards_are_all_accounted_for():
    assert len(PART_A) + len(WRONG_SOURCE) + len(NOT_ADDED) + len(MOVED_2_56) == 97  # dicumarol, the extra one, moved out in 2.55; two more in 2.56
    assert DICUMAROL not in NOT_ADDED
    pairs = [(card[1], card[2]) for card in PART_A + WRONG_SOURCE]
    assert len(set(pairs)) == len(pairs)


# ---- the corrections file ----

def test_the_file_holds_the_old_39_unchanged_then_the_62_new_ones():
    entries = load(CORRECTIONS_FILE)
    assert len(entries) == 122 + len(RED_ROWS)  # Ticket 2.62 adds RED_ROWS at the end. Ticket 2.58: ipratropium on asthma deleted, six added; Ticket 3.10 (MAIN 4, 25 Nov, Q14): mannitol's red entry on asthma deleted; ticket 2.56, signed rule Q22 (and Q3, Q13 for the other lists): five more, dated 2026-11-25; Ticket 2.55, signed answers Q10 and Q22: dicumarol, sodium phenylbutyrate; ticket 2.54, signed answers Q22 and 10b: simvastatin, misoprostol; ticket 2.52 added seven after Obizur
    assert hashlib.sha256(json.dumps(entries[:39], sort_keys=True).encode()).hexdigest() == \
        OLD_39_SHA256
    # Ticket 2.47 added one more at the end (Obizur, Kashish's decision).
    # Ticket 3.10 (MAIN 4, Q14): mannitol on asthma was deleted from the 62; the other 61 stay in order.
    # Ticket 2.58 (25N-13): ipratropium on asthma was deleted from them too, so 60 stay.
    assert entries[39:99] == [entry for entry in NEW_CORRECTIONS
                              if (entry["medicine_id"], entry["disease_id"]) not in
                              (("CHEMBL689", "MONDO_0004979"), ("CHEMBL1621597", "MONDO_0004979"))]


def test_each_new_entry_has_exactly_the_four_keys_and_the_note_word_for_word():
    for entry in load(CORRECTIONS_FILE)[39:101]:
        assert list(entry) == ["medicine_id", "disease_id", "date", "note"]
        assert entry["date"] == THE_DAY and entry["note"] == NOTE


def test_no_pair_is_written_twice_and_none_clashes_with_another_list():
    pairs = [(e["medicine_id"], e["disease_id"]) for e in load(CORRECTIONS_FILE)]
    assert len(set(pairs)) == len(pairs)
    new = {(e["medicine_id"], e["disease_id"]) for e in NEW_CORRECTIONS}
    for file in (APPROVALS_FILE, LEFT_OUT_FILE):
        assert not new & {(one["medicine_id"], one["disease_id"]) for one in load(file)}


def test_the_other_files_the_ticket_names_are_not_part_of_this_change():
    # Ticket 2.46 added entries dated 2026-11-25 to the approvals file after this one.
    before_2_46 = [e for e in load(APPROVALS_FILE) if e["date"] != THE_DAY]
    # Ticket 2.54 (signed answers Q5, Q20) added six left-out entries: 53 + 6.
    assert len(before_2_46) == 22 and len(load(LEFT_OUT_FILE)) == 59


# ---- the pages: the new red cards are in the red box ----

def tabs(disease_id):
    return second_batch.tabs_for(disease_id, engine.added_by_hand(disease_id))


def new_cards(disease_id):
    return [card for card in PART_A if card[2] == disease_id]


@pytest.mark.parametrize("disease_id, count", [
    ("MONDO_0005068", 7), ("MONDO_0005081", 7), ("MONDO_0002280", 5),
    ("MONDO_0005252", 4), ("MONDO_0004247", 5)])
def test_the_engine_gives_each_page_the_red_words_for_its_new_cards(disease_id, count):
    ids = {card[1] for card in new_cards(disease_id)}
    assert len(ids) == count
    assert ids <= engine.looks_wrong(disease_id)
    assert all(engine.warning_words(disease_id)[medicine_id] == NOTE for medicine_id in ids)


@pytest.mark.parametrize("card", [c for c in PART_A if c[2] in PAGES], ids=names)
def test_each_new_card_shows_the_red_words_and_sits_in_the_folded_box(card):
    medicine, medicine_id, disease_id, _, _ = card
    found = tabs(disease_id)
    assert first_batch.only_under_approved(found, medicine_id)
    approved = [m for m in found.approved if m.id == medicine_id][0]
    sent = api._approved_json(approved, engine.looks_wrong(disease_id),
                              engine.warning_words(disease_id))
    assert sent["warning"] == NOTE
    assert medicine_id in [m.id for m in engine.wrong_approvals_box(found.approved, disease_id)]


@pytest.mark.parametrize("disease_id", ["MONDO_0005068", "MONDO_0005252"])  # the pages with some left
def test_the_cards_left_alone_on_those_pages_show_no_new_red_words(disease_id):
    left = {card[1] for card in WRONG_SOURCE + NOT_ADDED if card[2] == disease_id}
    assert left
    assert not left & engine.looks_wrong(disease_id)
