"""Ticket 2.52. Nitric oxide on pulmonary arterial hypertension, and six odd
cards and two wrong links on type 2 diabetes.

From Grok's final live check of 25 Nov (4 pm), which read every Source record
on the main Approved list of the ten audited diseases. Lists only:

  - corrections.json: seven red warnings (the card stays on the page, in the
    red box, with the second-warning words from ticket 2.19):
      1. nitric oxide, pulmonary arterial hypertension (MONDO_0015924)
      2-6. biotin, cyanocobalamin, folic acid, omega-3-acid ethyl esters,
           pyridoxine, type 2 diabetes (MONDO_0005148)
      7. tyrosine, type 2 diabetes
  - confirmed.json: two links (the card shows exactly that label as its
    Source record, as in ticket 2.48):
      8. liraglutide -> Victoza (it showed Xultophy, a combination)
      9. canagliflozin -> Invokana (it showed Invokamet, a combination)
  - 10. simvastatin: nothing changed. It is reported only.

Every label was read on 25 Nov 2026 and is saved in fixtures/labels_read/2.52/
(`labels/` whole indications text, `sweeps/` one line per current label of each
medicine). Each disease's own list was asked live on 2026-11-25 (Open Targets
data 26.09) and is saved in fixtures/labels_read/2.52/disease_drugs/. No network.
"""

import json
import pathlib
import re
from unittest.mock import patch

import pytest

from moonlight import api, engine

import test_approvals_batch as second_batch

ROOT = pathlib.Path(__file__).resolve().parent.parent
CORRECTIONS_FILE = ROOT / "moonlight" / "corrections.json"
CONFIRMED_FILE = ROOT / "moonlight" / "confirmed.json"
FOLDER = ROOT / "fixtures" / "labels_read" / "2.52"
README = FOLDER / "README.md"
OUR_LISTS = FOLDER / "disease_drugs"

PAH = "MONDO_0015924"
T2D = "MONDO_0005148"
THE_DAY = "2026-11-25"
DAILYMED = "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid="
SECOND_NOTE = ("This looks like a mistake in the database. The official label is "
               "for a different disease.")

DIVISTA = DAILYMED + "06c485cd-ee30-44f2-be63-bb98f8d1a907"
APPFORMIN = DAILYMED + "0569d5d5-70df-46d7-954a-fe00542a7191"
XULTOPHY = DAILYMED + "21335fe4-d395-4501-ac2a-2f20d7520da9"
VICTOZA = DAILYMED + "5a9ef4ea-c76a-4d34-a604-27c5b505f5a4"
INVOKAMET = DAILYMED + "6868666b-c25e-40d1-9d1f-306bbe9390c1"
INVOKANA = DAILYMED + "b9057d3b-b104-4f09-8a61-c61ef9d4a3f3"
JUVISYNC = DAILYMED + "2062b3d3-580f-46f8-94b6-4bdecb7b53b1"
NOXIVENT = DAILYMED + "27586e4f-66f1-4583-981c-e0bccb8b02e0"

NITRIC_OXIDE = "CHEMBL1200689"
BIOTIN = "CHEMBL857"
CYANOCOBALAMIN = "CHEMBL2110563"
FOLIC_ACID = "CHEMBL1622"
OMEGA_3 = "CHEMBL1200711"
PYRIDOXINE = "CHEMBL1364"
TYROSINE = "CHEMBL925"
LIRAGLUTIDE = "CHEMBL4084119"
CANAGLIFLOZIN = "CHEMBL2048484"  # the card's id; CHEMBL4594217 is its tablet form
SIMVASTATIN = "CHEMBL1064"

RED = [(NITRIC_OXIDE, PAH), (BIOTIN, T2D), (CYANOCOBALAMIN, T2D), (FOLIC_ACID, T2D),
       (OMEGA_3, T2D), (PYRIDOXINE, T2D), (TYROSINE, T2D)]
CONFIRMED = {(LIRAGLUTIDE, T2D): (XULTOPHY, VICTOZA),
             (CANAGLIFLOZIN, T2D): (INVOKAMET, INVOKANA)}
CARD_IDS = [NITRIC_OXIDE, BIOTIN, CYANOCOBALAMIN, FOLIC_ACID, OMEGA_3, PYRIDOXINE,
            TYROSINE, LIRAGLUTIDE, CANAGLIFLOZIN, SIMVASTATIN]

DIVISTA_SENTENCE = ("DivistaTM is specially designed as a once a day nutritional adjuvant to "
                    "the current standard of care for patients with, or at risk of developing "
                    "type 2 diabetes mellitus (T2DM).")


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


def corrections_without_this_ticket():
    return [e for e in load(CORRECTIONS_FILE) if (e["medicine_id"], e["disease_id"]) not in RED]


def confirmed_without_this_ticket():
    return [e for e in load(CONFIRMED_FILE)
            if (e["medicine_id"], e["disease_id"]) not in CONFIRMED]


def approved_tab(disease_id, before=False):
    """The Approved tab the way api._Found builds it, then its three parts:
    (every card, the main list, the no-regulator box, the red box)."""
    tabs = second_batch.tabs_for(disease_id, engine.added_by_hand(disease_id))
    if before:
        with patch.object(engine, "_read_confirmed", return_value=confirmed_without_this_ticket()), \
                patch.object(engine, "_read_corrections",
                             return_value=corrections_without_this_ticket()):
            approved = engine.confirm_by_label(tabs.approved, disease_id)
            red = [m.id for m in engine.wrong_approvals_box(approved, disease_id)]
    else:
        approved = engine.confirm_by_label(tabs.approved, disease_id)
        red = [m.id for m in engine.wrong_approvals_box(approved, disease_id)]
    grey = [m.id for m in engine.no_regulator_box(approved, disease_id)]
    main = [m for m in approved if m.id not in red and m.id not in grey]
    return approved, main, grey, red


def the_card(cards, medicine_id):
    found = [medicine for medicine in cards if medicine.id == medicine_id]
    assert len(found) == 1, medicine_id
    return found[0]


def text(*parts):
    return FOLDER.joinpath(*parts).read_text(encoding="utf-8")


def sweep(name):
    lines = text("sweeps", f"{name}.tsv").splitlines()
    return lines[0], [line.split("\t") for line in lines[2:]]


def readme_rows():
    rows = []
    for line in README.read_text(encoding="utf-8").splitlines():
        cells = line.split(" | ")
        if len(cells) == 5 and cells[0] != "card":
            rows.append(cells)
    return rows


# ---- the README ----

def test_the_readme_has_the_testers_header_and_one_line_per_card_in_ticket_order():
    assert "card | change | quoted label sentence | link | value replaced" in \
        README.read_text(encoding="utf-8").splitlines()
    ids = [re.findall(r"CHEMBL\d+", cells[0])[0] for cells in readme_rows()]
    assert ids == CARD_IDS


def test_each_readme_link_and_quote_come_from_a_saved_label():
    saved = {
        NITRIC_OXIDE: ("labels/nitric_oxide/noxivent-27586e4f-the-card-link.txt", NOXIVENT),
        TYROSINE: ("labels/tyrosine/appformin-metformin-tyrosine-kit.txt", APPFORMIN),
        LIRAGLUTIDE: ("labels/liraglutide/victoza-liraglutide.txt", VICTOZA),
        CANAGLIFLOZIN: ("labels/canagliflozin/invokana-canagliflozin.txt", INVOKANA),
        SIMVASTATIN: ("labels/not_current/juvisync-sitagliptin-simvastatin.txt", JUVISYNC),
    }
    for medicine_id in (BIOTIN, CYANOCOBALAMIN, FOLIC_ACID, OMEGA_3, PYRIDOXINE):
        saved[medicine_id] = ("labels/not_current/divista-chromium-picolinate-capsule.txt",
                              DIVISTA)
    for cells in readme_rows():
        medicine_id = re.findall(r"CHEMBL\d+", cells[0])[0]
        short, link = saved[medicine_id]
        label = text(*short.split("/"))
        assert label.splitlines()[0] == link == cells[3]
        assert label.splitlines()[1] == THE_DAY
        assert cells[2] in label, medicine_id


def test_the_readme_says_what_each_card_got():
    changes = {cells[0].split(" (")[0]: cells[1] for cells in readme_rows()}
    for name in ("Nitric oxide", "Biotin", "Cyanocobalamin", "Folic acid",
                 "OMEGA-3-ACID Ethyl Esters", "Pyridoxine", "Tyrosine"):
        assert changes[name].startswith("red warning added to corrections.json"), name
    for name in ("Liraglutide", "Canagliflozin"):
        assert changes[name].startswith("confirmed link added to confirmed.json"), name
    assert changes["Simvastatin"].startswith("none")


def test_the_replaced_links_in_the_readme_are_what_the_cards_showed_on_main():
    saved = {d: load(FOLDER / "page_answers" / f"{d}.clues.json") for d in (PAH, T2D)}
    shown = {c["id"]: c["source"] for page in saved.values() for c in page["approved"]}
    rows = {re.findall(r"CHEMBL\d+", cells[0])[0]: cells for cells in readme_rows()}
    assert shown[NITRIC_OXIDE] == NOXIVENT
    for medicine_id in (BIOTIN, CYANOCOBALAMIN, FOLIC_ACID, OMEGA_3, PYRIDOXINE):
        assert shown[medicine_id] == DIVISTA
    assert shown[TYROSINE] == APPFORMIN
    assert shown[LIRAGLUTIDE] == XULTOPHY and rows[LIRAGLUTIDE][4] == XULTOPHY + " (Xultophy)"
    assert shown[CANAGLIFLOZIN] == INVOKAMET and rows[CANAGLIFLOZIN][4] == INVOKAMET + " (Invokamet)"
    assert shown[SIMVASTATIN] == JUVISYNC


# ---- the red warnings (cards 1 to 7): one test each ----

@pytest.mark.parametrize("medicine_id, disease_id", RED)
def test_the_card_is_now_in_the_red_box_and_the_card_is_kept(medicine_id, disease_id):
    approved, main, grey, red = approved_tab(disease_id)
    assert medicine_id in red
    assert medicine_id in [m.id for m in approved]  # kept on the Approved tab
    assert medicine_id not in [m.id for m in main]
    assert engine.warning_words(disease_id)[medicine_id] == SECOND_NOTE
    found = [e for e in load(CORRECTIONS_FILE)
             if (e["medicine_id"], e["disease_id"]) == (medicine_id, disease_id)]
    assert [{k: v for k, v in e.items() if k != "label"} for e in found] == [
        {"medicine_id": medicine_id, "disease_id": disease_id, "date": THE_DAY,
         "note": SECOND_NOTE}]


@pytest.mark.parametrize("medicine_id, disease_id", RED)
def test_before_this_ticket_the_card_was_on_the_main_list_with_no_warning(medicine_id, disease_id):
    approved, main, grey, red = approved_tab(disease_id, before=True)
    assert medicine_id in [m.id for m in main]
    assert medicine_id not in red and medicine_id not in grey
    assert the_card(main, medicine_id).proof_note is None


def test_the_other_cards_on_the_two_pages_are_not_moved_by_the_seven_warnings():
    for disease_id in (PAH, T2D):
        _, _, _, red_before = approved_tab(disease_id, before=True)
        _, _, _, red_after = approved_tab(disease_id)
        added = {m for m, d in RED if d == disease_id}
        assert set(red_after) - set(red_before) == added
        assert set(red_before) <= set(red_after)


def test_the_seven_entries_are_dated_today_and_use_the_standard_words():
    entries = [e for e in load(CORRECTIONS_FILE) if (e["medicine_id"], e["disease_id"]) in RED]
    assert [(e["medicine_id"], e["disease_id"]) for e in entries] == RED
    assert {e["date"] for e in entries} == {THE_DAY}
    assert {e["note"] for e in entries} == {SECOND_NOTE}


# ---- evidence for the red warnings: the saved labels ----

def test_no_nitric_oxide_label_names_pulmonary_arterial_hypertension():
    files = sorted((FOLDER / "labels" / "nitric_oxide").glob("*.txt"))
    assert len(files) == 12  # every label DailyMed returns for nitric oxide
    assert len(sweep("nitric-oxide")[1]) == 12
    for file in files:
        assert not re.search(r"pulmonary arterial hypertension|\bPAH\b", file.read_text(
            encoding="utf-8"), re.I), file.name


def test_the_seven_nitric_oxide_medicine_labels_are_for_newborns_with_respiratory_failure():
    files = sorted((FOLDER / "labels" / "nitric_oxide").glob("*.txt"))
    newborn = [f for f in files if "neonates with hypoxic respiratory failure"
               in f.read_text(encoding="utf-8")]
    assert len(newborn) == 7  # Noxivent x2, INOmax, Genosyl x3, Ulspira
    assert "noxivent-27586e4f-the-card-link.txt" in [f.name for f in newborn]


def test_divista_is_not_current_and_not_approved_and_has_six_ingredients():
    label = text("labels", "not_current", "divista-chromium-picolinate-capsule.txt")
    assert DIVISTA_SENTENCE in label
    assert "Marketing end date: 09/30/2011" in label
    assert "unapproved drug other" in label
    assert "has not been found by FDA to be safe and effective" in label
    for ingredient in ("CHROMIUM PICOLINATE", "BIOTIN", "PYRIDOXINE", "CYANOCOBALAMIN",
                       "FOLIC ACID", "OMEGA-3-ACID ETHYL ESTERS"):
        assert ingredient in label
    # DailyMed's own current list does not hold it, so no sweep line has its setid
    for name in ("biotin", "cyanocobalamin", "folic-acid", "pyridoxine",
                 "omega-3-acid-ethyl-esters"):
        assert "06c485cd-ee30-44f2-be63-bb98f8d1a907" not in text("sweeps", f"{name}.tsv")


@pytest.mark.parametrize("name, count", [
    ("biotin", 302), ("cyanocobalamin", 465), ("folic-acid", 551),
    ("pyridoxine", 534), ("omega-3-acid-ethyl-esters", 43), ("tyrosine", 41)])
def test_every_current_label_of_the_medicine_was_read_and_none_has_it_for_type_2_diabetes(
        name, count):
    header, rows = sweep(name)
    assert len(rows) == count and f"{count} labels" in header
    for row in rows:
        sentences = row[4]
        if name == "tyrosine":
            continue  # the two Appformin kits, tested below
        # a sentence naming diabetes is a warning, a precaution or a cause to
        # control first, never a sentence that says what the medicine is for
        assert "indicated" not in sentences.lower() or "such as diabetes" in sentences, row[0]
        assert not re.search(r"indicated.{0,200}type 2 diabetes", sentences, re.I), row[0]


def test_every_current_omega_3_label_names_diabetes_only_as_a_cause_to_control_first():
    _, rows = sweep("omega-3-acid-ethyl-esters")
    named = [row for row in rows if row[4]]
    # 43 labels held omega-3-acid ethyl esters; all but two (kits that carry no
    # indications section) say the standard sentence
    assert len(named) >= 41
    for row in named:
        assert re.search(r"control of any medical problems,? such as diabetes", row[4]), row[0]
    label = text("labels", "omega_3", "lovaza-omega-3-acid-ethyl-esters.txt")
    assert "control of any medical problems such as diabetes mellitus and hypothyroidism" in label


def test_tyrosine_only_the_two_appformin_kits_name_type_2_diabetes_and_for_metformin():
    _, rows = sweep("tyrosine")
    named = [row for row in rows if row[4]]
    assert [row[0] for row in named] == ["0569d5d5-70df-46d7-954a-fe00542a7191",
                                         "63f7ac0f-51d7-4e9e-bc54-aee51183bbaa"]
    for row in named:
        assert "Metformin hydrochloride tablets" in row[4]
    label = text("labels", "tyrosine", "appformin-metformin-tyrosine-kit.txt")
    assert "APPFORMIN (METFORMIN HYDROCHLORIDE, TYROSINE) KIT" in label
    assert "AppTrim is intended for the clinical nutritional management" in label
    assert "obesity" in label


# ---- the confirmed links (cards 8 and 9) ----

@pytest.mark.parametrize("key", list(CONFIRMED))
def test_the_card_shows_the_new_label_as_its_source_record_with_no_grey_line(key):
    medicine_id, disease_id = key
    old, new = CONFIRMED[key]
    _, main, grey, red = approved_tab(disease_id)
    found = the_card(main, medicine_id)
    assert found.source_record == new
    assert found.source_record != old
    assert found.proof_note is None
    assert medicine_id not in grey and medicine_id not in red


@pytest.mark.parametrize("key", list(CONFIRMED))
def test_before_this_ticket_the_card_showed_the_combination_label(key):
    medicine_id, disease_id = key
    old, _ = CONFIRMED[key]
    _, main, _, _ = approved_tab(disease_id, before=True)
    assert the_card(main, medicine_id).source_record == old


def test_the_two_confirmed_entries_are_exactly_these():
    entries = [e for e in load(CONFIRMED_FILE) if (e["medicine_id"], e["disease_id"]) in CONFIRMED]
    assert entries == [
        {"medicine_id": LIRAGLUTIDE, "disease_id": T2D, "date": THE_DAY, "label": VICTOZA},
        {"medicine_id": CANAGLIFLOZIN, "disease_id": T2D, "date": THE_DAY, "label": INVOKANA}]


def test_the_canagliflozin_entry_uses_the_cards_id_not_its_tablet_forms_id():
    page = load(FOLDER / "page_answers" / f"{T2D}.clues.json")
    (card,) = [c for c in page["approved"] if c["medicine"].startswith("Canagliflozin")]
    assert card["id"] == CANAGLIFLOZIN
    assert card["forms"] == ["Canagliflozin Anhydrous", "Canagliflozin"]
    assert all(e["medicine_id"] != "CHEMBL4594217" for e in load(CONFIRMED_FILE))


def test_victoza_and_invokana_name_type_2_diabetes_for_the_medicine_alone():
    victoza = text("labels", "liraglutide", "victoza-liraglutide.txt")
    assert victoza.splitlines()[0] == VICTOZA
    assert "VICTOZA is indicated:" in victoza
    assert ("as an adjunct to diet and exercise to improve glycemic control in adults and "
            "pediatric patients aged 10 years and older with type 2 diabetes mellitus,") in victoza
    assert "insulin degludec" not in victoza.lower()
    invokana = text("labels", "canagliflozin", "invokana-canagliflozin.txt")
    assert invokana.splitlines()[0] == INVOKANA
    assert "INVOKANA (canagliflozin) is indicated:" in invokana
    assert ("as an adjunct to diet and exercise to improve glycemic control in adults and "
            "pediatric patients aged 10 years and older with type 2 diabetes mellitus.") in invokana
    assert "metformin" not in invokana.lower()


def test_the_replaced_labels_are_the_combinations():
    xultophy = text("labels", "liraglutide", "xultophy-insulin-degludec-liraglutide-REPLACED.txt")
    assert xultophy.splitlines()[0] == XULTOPHY
    assert "XULTOPHY 100/3.6 is a combination of insulin degludec and liraglutide" in xultophy
    invokamet = text("labels", "canagliflozin", "invokamet-canagliflozin-metformin-REPLACED.txt")
    assert invokamet.splitlines()[0] == INVOKAMET
    assert "INVOKAMET is a combination of canagliflozin and metformin" in invokamet


def test_both_labels_are_in_dailymeds_current_list_and_not_in_the_corrections_file():
    _, liraglutide = sweep("liraglutide")
    _, canagliflozin = sweep("canagliflozin")
    assert "5a9ef4ea-c76a-4d34-a604-27c5b505f5a4" in [row[0] for row in liraglutide]
    assert "b9057d3b-b104-4f09-8a61-c61ef9d4a3f3" in [row[0] for row in canagliflozin]
    wrong = {(e["medicine_id"], e["disease_id"]) for e in load(CORRECTIONS_FILE)}
    assert not (set(CONFIRMED) & wrong)  # a confirmed card is never also a red one


# ---- card 10: simvastatin, nothing changed ----

def test_simvastatin_is_in_no_list_and_still_shows_juvisync():
    # Ticket 2.54, signed answer Q22: simvastatin is now on corrections.json (red),
    # because a combination pill's label does not count for one of its parts.
    # Still true: it is in no confirmed list and still shows the Juvisync link.
    assert [e["disease_id"] for e in load(CORRECTIONS_FILE)
            if e["medicine_id"] == SIMVASTATIN] == [T2D]
    assert SIMVASTATIN not in {e["medicine_id"] for e in load(CONFIRMED_FILE)}
    with patch.object(engine, "_read_corrections", return_value=[
            e for e in load(CORRECTIONS_FILE) if e["medicine_id"] != SIMVASTATIN]):
        _, main, grey, red = approved_tab(T2D)
    found = the_card(main, SIMVASTATIN)
    assert found.source_record == JUVISYNC
    assert SIMVASTATIN not in grey and SIMVASTATIN not in red
    assert found.proof_note is None


def test_simvastatin_report_the_juvisync_label_is_not_current():
    label = text("labels", "not_current", "juvisync-sitagliptin-simvastatin.txt")
    assert "Marketing end date: 07/31/2014" in label
    assert "Sitagliptin is a dipeptidyl peptidase-4 (DPP-4) inhibitor indicated as an adjunct" in label
    assert "2062b3d3-580f-46f8-94b6-4bdecb7b53b1" not in text("sweeps", "simvastatin.tsv")


def test_simvastatin_report_no_current_label_has_it_to_treat_type_2_diabetes():
    header, rows = sweep("simvastatin")
    assert len(rows) == 182 and "182 labels" in header
    older = [r for r in rows if "high risk of coronary events because of existing coronary "
             "heart disease, diabetes, peripheral vessel disease" in r[4]]
    newer = [r for r in rows if "and/or diabetes, who are at high risk of coronary heart "
             "disease events" in r[4]]
    assert (len(older), len(newer), len([r for r in rows if not r[4]])) == (72, 103, 7)
    for row in rows:
        assert not re.search(r"glycemic control|type 2 diabetes", row[4], re.I), row[0]


# ---- the two pages, as a whole ----

def test_only_the_expected_cards_changed_place_on_the_two_pages():
    for disease_id in (PAH, T2D):
        before = approved_tab(disease_id, before=True)
        after = approved_tab(disease_id)
        assert [m.id for m in before[0]] == [m.id for m in after[0]]  # nothing removed or added
        moved = {m.id for m in before[1]} - {m.id for m in after[1]}
        assert moved == {m for m, d in RED if d == disease_id}
        changed_source = {m.id for m in after[1] if m.source_record != the_card(before[0], m.id).source_record}
        assert changed_source == {m for m, d in CONFIRMED if d == disease_id}
