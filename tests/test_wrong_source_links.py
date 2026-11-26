"""Ticket 2.48. The 23 wrong source links from ticket 2.45.

Each of these Approved cards showed, as its "Source record", a label for a
different product, while another current label of the same medicine names
the disease. Only list entries: 23 lines added to moonlight/confirmed.json
(ticket 2.42), date 2026-11-25. confirmed.json makes the card show exactly
that label as its Source record.

The labels were read in ticket 2.45 and are saved in
fixtures/labels_read/2.45/wrong_source/ (not fetched again). Each disease's
own list was asked live on 2026-11-25 (Open Targets data 26.09) and saved in
fixtures/labels_read/2.48/disease_drugs/, with the diseases' names and exact
synonyms in fixtures/labels_read/2.48/diseases.response.json. No network.

Every card was on its disease's main Approved list, with no grey line, before
this ticket. None was skipped.
"""

import json
import pathlib
import re
from unittest.mock import patch

import pytest

from moonlight import api, engine

import test_approvals_batch as second_batch
import test_approvals_by_hand as first_batch

ROOT = pathlib.Path(__file__).resolve().parent.parent
CONFIRMED_FILE = ROOT / "moonlight" / "confirmed.json"
LABELS = ROOT / "fixtures" / "labels_read" / "2.45" / "wrong_source"
OLD_README = ROOT / "fixtures" / "labels_read" / "2.45" / "README.md"
FOLDER = ROOT / "fixtures" / "labels_read" / "2.48"
README = FOLDER / "README.md"
OUR_LISTS = FOLDER / "disease_drugs"
DISEASES = FOLDER / "diseases.response.json"

THE_DAY = "2026-11-25"
DAILYMED = "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid="
EXCEDRIN = DAILYMED + "7ed841fb-a61c-4868-b4e5-4f2311a5e79c"

# (medicine, id, disease id, disease, saved label, old link, new link), in
# the order of the 2.45 README.
CARDS = [
    ('Pasireotide', 'CHEMBL3349607', 'MONDO_0019933', 'acromegaly', 'pasireotide-acromegaly',
     'https://www.ema.europa.eu/en/medicines/human/EPAR/signifor',
     'https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=a0aad470-3f38-af97-e053-2995a90a383a'),
    ('Fluticasone Propionate', 'CHEMBL1473', 'MONDO_0011786', 'allergic rhinitis', 'fluticasone-propionate-allergic-rhinitis',
     'https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=0d9a521b-8314-437c-8c9f-f6188f1134fe',
     'https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=4c557ec4-c4cf-11df-851a-0800200c9a66'),
    ('Tiotropium', 'CHEMBL1900528', 'MONDO_0004979', 'asthma', 'tiotropium-asthma',
     'https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=1cf82d42-5ad0-4b86-838e-9230c61cf3d4',
     'https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=7b656b14-fcaa-2741-f6f0-e0be48971c02'),
    ('Imiquimod', 'CHEMBL1282', 'MONDO_0020804', 'basal cell carcinoma', 'imiquimod-basal-cell-carcinoma',
     'https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=51913a5a-1cab-4b9e-b2c2-e0174062df73',
     'https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=a18a3f7e-7254-56c0-e053-2a95a90a7036'),
    ('Efgartigimod Alfa', 'CHEMBL4297551', 'MONDO_0006702', 'chronic inflammatory demyelinating polyradiculoneuropathy', 'efgartigimod-alfa-chronic-inflammatory-demyelinating-polyradiculoneuropathy',
     'https://www.ema.europa.eu/en/medicines/human/EPAR/vyvgart',
     'https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=7104d9e5-9910-47f5-9a93-741ac50f43b6'),
    ('Eplerenone', 'CHEMBL1095097', 'MONDO_0005252', 'heart failure', 'eplerenone-heart-failure',
     'https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=3a3047f2-0155-4a07-955f-839a312cf879',
     'https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=1a52bedc-8e2c-4116-a296-a87770676b4a'),
    ('Lisinopril Anhydrous', 'CHEMBL1237', 'MONDO_0005252', 'heart failure', 'lisinopril-anhydrous-heart-failure',
     'https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=0d3a966f-f937-05a8-a90f-5aa52ebbd613',
     'https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=838c2d78-d2d8-4981-9ec9-e50ef9e1a5d8'),
    ('Etodolac', 'CHEMBL622', 'MONDO_0011429', 'juvenile idiopathic arthritis', 'etodolac-juvenile-idiopathic-arthritis',
     'https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=3b3610c8-b937-41a4-e054-00144ff88e88',
     'https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=107ea9d7-80a9-41a4-b61e-168370127319'),
    ('Doxycycline Anhydrous', 'CHEMBL1433', 'MONDO_0005136', 'malaria', 'doxycycline-anhydrous-malaria',
     'https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=50490db4-9728-6d7e-e054-00144ff88e88',
     'https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=f9277bb8-982d-444d-9325-35d5c53a2d35'),
    ('Quinidine', 'CHEMBL1294', 'MONDO_0005136', 'malaria', 'quinidine-malaria',
     'https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=3af30c3b-944e-4293-baa5-38965b1d1137',
     'https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=b0d6341b-d880-4f0b-8844-bc788c03004a'),
    ('Acetaminophen', 'CHEMBL112', 'MONDO_0005277', 'migraine disorder', 'acetaminophen-migraine-disorder',
     'https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=07b47cba-fadc-437e-9a9a-845ee1cce591',
     'https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=7ed841fb-a61c-4868-b4e5-4f2311a5e79c'),
    ('Aspirin', 'CHEMBL25', 'MONDO_0005277', 'migraine disorder', 'aspirin-migraine-disorder',
     'https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=04bddbc4-86c7-4bac-9327-010568020568',
     'https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=7ed841fb-a61c-4868-b4e5-4f2311a5e79c'),
    ('Caffeine', 'CHEMBL113', 'MONDO_0005277', 'migraine disorder', 'caffeine-migraine-disorder',
     'https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=04bddbc4-86c7-4bac-9327-010568020568',
     'https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=7ed841fb-a61c-4868-b4e5-4f2311a5e79c'),
    ('Ibuprofen', 'CHEMBL521', 'MONDO_0005277', 'migraine disorder', 'ibuprofen-migraine-disorder',
     'https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=1223c4f1-090a-4328-9a5d-85f0b4a6a482',
     'https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=34818110-5291-4bda-9571-bd77d90bba7c'),
    ('Telmisartan', 'CHEMBL1017', 'MONDO_0005068', 'myocardial infarction', 'telmisartan-myocardial-infarction',
     'https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=4be6575f-ea8d-4cd8-a49d-3d1c93f2621a',
     'https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=20a60231-64f0-4751-aa81-6c0e64334179'),
    ('Valsartan', 'CHEMBL1069', 'MONDO_0005068', 'myocardial infarction', 'valsartan-myocardial-infarction',
     'https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=00743170-275e-43b2-8728-bef3c788aa0f',
     'https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=5ddba454-f3e6-43c2-a7a6-58365d297213'),
    ('Paroxetine', 'CHEMBL490', 'MONDO_0008114', 'obsessive-compulsive disorder', 'paroxetine-obsessive-compulsive-disorder',
     'https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=50361fc8-8fba-1c45-e054-00144ff88e88',
     'https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=ef3b5cbe-f9e1-c1ac-79da-cfe14e3a7e7e'),
    ('Paroxetine', 'CHEMBL490', 'MONDO_0005383', 'panic disorder', 'paroxetine-panic-disorder',
     'https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=50361fc8-8fba-1c45-e054-00144ff88e88',
     'https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=ef3b5cbe-f9e1-c1ac-79da-cfe14e3a7e7e'),
    ('Venlafaxine', 'CHEMBL637', 'MONDO_0005383', 'panic disorder', 'venlafaxine-panic-disorder',
     'https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=516e7566-35c2-4a25-88d8-54d9dbc8f6be',
     'https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=c848a5d8-ba94-4c84-80e3-0bf35fb8e32e'),
    ('Paroxetine', 'CHEMBL490', 'MONDO_0005146', 'post-traumatic stress disorder', 'paroxetine-post-traumatic-stress-disorder',
     'https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=50361fc8-8fba-1c45-e054-00144ff88e88',
     'https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=ef3b5cbe-f9e1-c1ac-79da-cfe14e3a7e7e'),
    ('Dabigatran Etexilate', 'CHEMBL539697', 'MONDO_0005279', 'pulmonary embolism', 'dabigatran-etexilate-pulmonary-embolism',
     'https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=5db7f199-8752-4d24-85f7-e34ca8f4d02e',
     'https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=ba74e3cd-b06f-4145-b284-5fd6b84ff3c9'),
    ('Ciprofloxacin', 'CHEMBL8', 'MONDO_0005619', 'typhoid fever', 'ciprofloxacin-typhoid-fever',
     'https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=19df63de-9f44-40ce-9a4f-0c96345b8a23',
     'https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=a7e5174a-dd01-6050-e053-2a95a90add3f'),
    ('Risankizumab', 'CHEMBL3990029', 'MONDO_0005101', 'ulcerative colitis', 'risankizumab-ulcerative-colitis',
     'https://www.ema.europa.eu/en/medicines/human/EPAR/skyrizi',
     'https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=7148c8eb-b39e-e20a-6494-a6df82392858'),
]

# The words for the disease in each quoted sentence. Each is the database's
# own name for the disease or one of its exact synonyms (checked below).
NAMED_AS = {
    'MONDO_0019933': 'acromegaly',
    'MONDO_0011786': 'allergic rhinitis',
    'MONDO_0004979': 'asthma',
    'MONDO_0020804': 'basal cell carcinoma',
    'MONDO_0006702': 'chronic inflammatory demyelinating polyneuropathy',
    'MONDO_0005252': 'heart failure',
    'MONDO_0011429': 'juvenile arthritis',
    'MONDO_0005136': 'malaria',
    'MONDO_0005277': 'migraine',
    'MONDO_0005068': 'myocardial infarction',
    'MONDO_0008114': 'obsessive compulsive disorder',
    'MONDO_0005383': 'panic disorder',
    'MONDO_0005146': 'posttraumatic stress disorder',
    'MONDO_0005279': 'pulmonary embolism',
    'MONDO_0005619': 'typhoid fever',
    'MONDO_0005101': 'ulcerative colitis',
}

MIGRAINE_COMBINATION = {'CHEMBL112', 'CHEMBL25', 'CHEMBL113'}


def names(card):
    return f"{card[1]}-{card[2]}"


def load(file):
    return json.loads(file.read_text(encoding="utf-8"))


def saved_post_json(body):
    """Stands in for fetch._post_json: each disease's own saved live list."""
    assert "drugAndClinicalCandidates" in body["query"]
    file = OUR_LISTS / f'{body["variables"]["diseaseId"]}.response.json'
    if not file.exists():
        raise AssertionError(f"no saved list for {body['variables']}")
    return load(file)


@pytest.fixture(autouse=True)
def offline():
    api.forget_visitors()
    with patch("requests.request", side_effect=AssertionError("network used")), \
            patch("requests.post", side_effect=AssertionError("network used")), \
            patch("requests.get", side_effect=AssertionError("network used")), \
            patch("requests.sessions.Session.request",
                  side_effect=AssertionError("network used")), \
            patch("moonlight.fetch._post_json", side_effect=saved_post_json):
        yield
    api.forget_visitors()


def without_this_ticket():
    """confirmed.json as it was before 2.48: every entry not dated today."""
    return [entry for entry in load(CONFIRMED_FILE) if entry["date"] != THE_DAY]


def approved_tab(disease_id, before=False):
    """The Approved tab the way api._Found builds it, then its three parts:
    (every card, the main list, the no-regulator box, the red box)."""
    tabs = second_batch.tabs_for(disease_id, engine.added_by_hand(disease_id))
    if before:
        with patch.object(engine, "_read_confirmed", return_value=without_this_ticket()):
            approved = engine.confirm_by_label(tabs.approved, disease_id)
    else:
        approved = engine.confirm_by_label(tabs.approved, disease_id)
    red = [m.id for m in engine.wrong_approvals_box(approved, disease_id)]
    grey = [m.id for m in engine.no_regulator_box(approved, disease_id)]
    main = [m for m in approved if m.id not in red and m.id not in grey]
    return tabs, approved, main, grey, red


def the_card(cards, medicine_id):
    found = [medicine for medicine in cards if medicine.id == medicine_id]
    assert len(found) == 1, medicine_id
    return found[0]


def readme_rows():
    rows = []
    for line in README.read_text(encoding="utf-8").splitlines():
        cells = line.split(" | ")
        if len(cells) == 5 and cells[0] != "card":
            rows.append(cells)
    return rows


# ---- one test per card: its Source record is now the right label ----

@pytest.mark.parametrize("card", CARDS, ids=names)
def test_the_card_source_record_is_now_the_label_that_names_its_disease(card):
    medicine, medicine_id, disease_id, disease, short, old, new = card
    _, _, main, _, _ = approved_tab(disease_id)
    found = the_card(main, medicine_id)
    assert found.source_record == new
    assert found.source_record != old


@pytest.mark.parametrize("card", CARDS, ids=names)
def test_before_this_ticket_the_card_showed_the_old_link(card):
    medicine, medicine_id, disease_id, disease, short, old, new = card
    _, _, main, _, _ = approved_tab(disease_id, before=True)
    assert the_card(main, medicine_id).source_record == old


@pytest.mark.parametrize("card", CARDS, ids=names)
def test_grey_line_box_and_place_are_otherwise_unchanged(card):
    medicine, medicine_id, disease_id, disease, short, old, new = card
    tabs, approved, main, grey, red = approved_tab(disease_id)
    tabs_before, approved_before, main_before, grey_before, red_before = \
        approved_tab(disease_id, before=True)
    # No grey line, before or after (no card had the no-regulator line).
    assert the_card(approved_before, medicine_id).proof_note is None
    assert the_card(approved, medicine_id).proof_note is None
    # Only on the Approved tab, on its main list, in no folded box.
    places = first_batch.everywhere(tabs)
    assert [place for place, ids in places.items() if medicine_id in ids] == ["approved"]
    assert medicine_id not in grey and medicine_id not in red
    # The same place on the main list, the same boxes, the same name.
    # Ticket 2.56 moved two cards on ulcerative colitis, on purpose: azathioprine
    # (signed rule Q3) from the no-regulator box to the main list, and isopropyl
    # alcohol (rule Q22) into the red box. Those two are left out of the comparison.
    moved = {"CHEMBL1542", "CHEMBL582"} if disease_id == "MONDO_0005101" else set()
    keep = lambda ids: [i for i in ids if i not in moved]
    assert keep(m.id for m in main) == keep(m.id for m in main_before)
    assert keep(grey) == keep(grey_before) and keep(red) == keep(red_before)
    assert the_card(main, medicine_id).name == the_card(main_before, medicine_id).name
    assert the_card(main, medicine_id).name.lower() == medicine.lower()


def test_no_other_card_on_these_pages_changed_its_source_or_line():
    ours = {(card[1], card[2]) for card in CARDS}
    # Ticket 2.56 (signed rule Q3): azathioprine's card now says it was
    # confirmed from a label, so it differs from the 2.45 answer on purpose.
    ours.add(("CHEMBL1542", "MONDO_0005101"))
    for disease_id in sorted({card[2] for card in CARDS}):
        _, approved, _, _, _ = approved_tab(disease_id)
        _, approved_before, _, _, _ = approved_tab(disease_id, before=True)
        for after, before in zip(approved, approved_before):
            assert after.id == before.id
            if (after.id, disease_id) not in ours:
                assert after == before, (after.id, disease_id)


# ---- confirmed.json ----

def test_confirmed_json_holds_the_23_new_entries_in_its_own_form():
    entries = load(CONFIRMED_FILE)
    # Ticket 2.52 added two more dated today (liraglutide and canagliflozin,
    # type 2 diabetes); they are not part of this ticket's 23.
    # Ticket 2.54 (signed answers Q3 and item 12) added two more, also dated today:
    # ertugliflozin (type 2 diabetes) and tetrabenazine (Huntington disease).
    later = {("CHEMBL4084119", "MONDO_0005148"), ("CHEMBL2048484", "MONDO_0005148"),
             ("CHEMBL1770248", "MONDO_0005148"), ("CHEMBL117785", "MONDO_0007739"),
             # Ticket 2.56 (signed rules Q3, Q13): hydroxychloroquine, azathioprine, neostigmine
             ("CHEMBL1535", "MONDO_0007915"), ("CHEMBL1542", "MONDO_0005101"),
             ("CHEMBL278020", "MONDO_0009688")}
    new = [entry for entry in entries if entry["date"] == THE_DAY
           and (entry["medicine_id"], entry["disease_id"]) not in later]
    assert new == [{"medicine_id": card[1], "disease_id": card[2], "date": THE_DAY,
                    "label": card[6]} for card in CARDS]
    from test_list_fixes_2_64 import CONFIRMED_ROWS  # ticket 2.64
    assert len(entries) == 3 + 23 + 2 + 2 + 3 + 1 + len(CONFIRMED_ROWS)  # ticket 2.56 added three; 2.61 one (givosiran); ticket 2.64 two (anagliptin, tofogliflozin)
    labels = engine.confirmed_by_label()  # the file still reads
    assert all(labels[(card[1], card[2])] == card[6] for card in CARDS)


def test_every_id_is_the_one_on_the_live_list_and_in_the_2_45_readme():
    old_readme = OLD_README.read_text(encoding="utf-8")
    for medicine, medicine_id, disease_id, disease, short, old, new in CARDS:
        assert f"- {medicine} ({medicine_id}), {disease} ({disease_id}): " \
               f"the card's own link {old} is the wrong product." in old_readme
        rows = load(OUR_LISTS / f"{disease_id}.response.json")["data"]["disease"]
        assert rows["id"] == disease_id
        listed = {}
        for row in rows["drugAndClinicalCandidates"]["rows"]:
            drug = row["drug"]
            listed[drug["id"]] = drug["name"]
            if drug["parentMolecule"]:  # a salt form: the card is its parent
                listed[drug["parentMolecule"]["id"]] = drug["parentMolecule"]["name"]
        assert listed[medicine_id].lower() == medicine.lower()


# ---- the saved labels name the disease ----

@pytest.mark.parametrize("card", CARDS, ids=names)
def test_the_saved_label_is_the_new_link_and_names_the_disease(card):
    medicine, medicine_id, disease_id, disease, short, old, new = card
    lines = (LABELS / f"{short}.txt").read_text(encoding="utf-8").splitlines()
    assert lines[0] == new and lines[1] == THE_DAY
    assert "INDICATIONS" in lines[3].upper()
    cells = [c for c in readme_rows() if f"({medicine_id})" in c[0] and f"({disease_id})" in c[0]]
    assert len(cells) == 1
    sentence = cells[0][2]
    assert sentence in "\n".join(lines[4:])  # word for word, from the section
    assert NAMED_AS[disease_id].lower() in sentence.lower()


def test_each_disease_word_is_the_database_name_or_an_exact_synonym():
    diseases = {d["id"]: d for d in load(DISEASES)["data"]["diseases"]}
    for disease_id, words in NAMED_AS.items():
        record = diseases[disease_id]
        exact = [term.lower() for s in record["synonyms"] if s["relation"] == "hasExactSynonym"
                 for term in s["terms"]]
        assert words == record["name"] or words in exact, disease_id
    assert {card[3] for card in CARDS} == {diseases[card[2]]["name"] for card in CARDS}


# ---- the README ----

def test_the_readme_has_one_line_per_card_in_the_tickets_shape():
    text = README.read_text(encoding="utf-8")
    assert "card | change | quoted sentence | link | value replaced" in text.splitlines()
    rows = readme_rows()
    assert [cells[0] for cells in rows] == [
        f"{medicine} ({medicine_id}), {disease} ({disease_id})"
        for medicine, medicine_id, disease_id, disease, *_ in CARDS]
    for cells, card in zip(rows, CARDS):
        assert cells[3] == card[6]
        assert cells[4] == card[5]
        assert cells[1].startswith("Source record set by confirmed.json")
        assert ("Excedrin Migraine" in cells[1]) == (card[1] in MIGRAINE_COMBINATION)


def test_the_three_migraine_cards_point_at_the_combination_product():
    rows = [card for card in CARDS if card[1] in MIGRAINE_COMBINATION]
    assert len(rows) == 3 and all(card[6] == EXCEDRIN for card in rows)
    text = (LABELS / "aspirin-migraine-disorder.txt").read_text(encoding="utf-8")
    assert "acetaminophen, aspirin (nsaid) and caffeine" in text.splitlines()[2]


def test_paroxetine_is_there_three_times_all_to_paxil():
    paroxetine = [card for card in CARDS if card[1] == "CHEMBL490"]
    assert [card[3] for card in paroxetine] == [
        "obsessive-compulsive disorder", "panic disorder", "post-traumatic stress disorder"]
    assert {card[6] for card in paroxetine} == {DAILYMED + "ef3b5cbe-f9e1-c1ac-79da-cfe14e3a7e7e"}
    assert all("PAXIL" in (LABELS / f"{card[4]}.txt").read_text(encoding="utf-8").splitlines()[2]
               for card in paroxetine)


def test_the_three_ema_links_are_replaced_by_dailymed_labels():
    ema = [card for card in CARDS if card[5].startswith("https://www.ema.europa.eu/")]
    assert [card[0] for card in ema] == ["Pasireotide", "Efgartigimod Alfa", "Risankizumab"]
    assert all(card[6].startswith(DAILYMED) for card in ema)
