"""Ticket 2.47. Four cards from public feedback: avapritinib, imatinib,
deferoxamine, Obizur.

One list change, decided by Kashish after the report: Obizur goes in corrections.json
(card 4). The labels were read on 25 Nov 2026 (fixtures/labels_read/2.47/):

  1. avapritinib, systemic mastocytosis: already in approvals.json (23 Nov).
  2. imatinib, systemic mastocytosis: already in approvals.json, limited (23 Nov).
  3. deferoxamine, hemochromatosis: already in corrections.json (22 Nov, 2.19).
  4. susoctocog alfa (Obizur), haemophilia A: the label never says "not for
     congenital haemophilia A", but names only acquired haemophilia A. Kashish:
     the rule is "no current label names the disease", so the red box. Added to
     corrections.json with the standard note.

One test per card on what the page answer shows, from the disease's own saved
list (taken live on 2026-11-25) with the REAL approvals and corrections files.
No network.
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
FOLDER = ROOT / "fixtures" / "labels_read" / "2.47"
README = FOLDER / "README.md"
OUR_LISTS = FOLDER / "disease_drugs"
APPROVALS_FILE = ROOT / "moonlight" / "approvals.json"
CORRECTIONS_FILE = ROOT / "moonlight" / "corrections.json"

MASTOCYTOSIS = "MONDO_0016586"
HEMOCHROMATOSIS = "EFO_1000642"
HAEMOPHILIA_A = "MONDO_0010602"

AVAPRITINIB = "CHEMBL4204794"
IMATINIB = "CHEMBL941"
DEFEROXAMINE = "CHEMBL556"
OBIZUR = "CHEMBL5315075"

DAILYMED = "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid="
SECOND_NOTE = ("This looks like a mistake in the database. The official label is "
               "for a different disease.")

# card -> (saved label, the sentence the README quotes)
CARDS = {
    AVAPRITINIB: ("ayvakit-avapritinib.txt",
                  "AYVAKIT is indicated for the treatment of adult patients with indolent "
                  "systemic mastocytosis (ISM)."),
    IMATINIB: ("gleevec-imatinib-mesylate.txt",
               "Adult patients with aggressive systemic mastocytosis without the D816V c-Kit "
               "mutation or with c-Kit mutational status unknown."),
    DEFEROXAMINE: ("desferal-deferoxamine-novartis.txt",
                   "Desferal is not indicated for the treatment of primary hemochromatosis "
                   "(since phlebotomy is the method of choice for removing excess iron in "
                   "this disorder)."),
    OBIZUR: ("obizur-susoctocog-alfa.txt",
             "OBIZUR is not indicated for the treatment of von Willebrand disease."),
}


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


def tabs(disease_id):
    return second_batch.tabs_for(disease_id, engine.added_by_hand(disease_id))


def card(tabs_, medicine_id):
    found = [medicine for medicine in tabs_.approved if medicine.id == medicine_id]
    assert len(found) == 1, medicine_id
    return found[0]


# ---- the README and the saved labels ----

def readme_rows():
    rows = []
    for line in README.read_text(encoding="utf-8").splitlines():
        cells = line.split(" | ")
        if len(cells) == 5 and cells[0] != "card":
            rows.append(cells)
    return rows


def test_the_readme_has_the_testers_header_and_one_line_per_card():
    assert "card | change | quoted label sentence | link | value replaced" in \
        README.read_text(encoding="utf-8").splitlines()
    ids = [re.findall(r"CHEMBL\d+", cells[0])[0] for cells in readme_rows()]
    assert ids == [AVAPRITINIB, IMATINIB, DEFEROXAMINE, OBIZUR]


@pytest.mark.parametrize("medicine_id", list(CARDS))
def test_each_readme_quote_is_a_sentence_of_its_saved_label(medicine_id):
    short, sentence = CARDS[medicine_id]
    lines = (FOLDER / short).read_text(encoding="utf-8").splitlines()
    assert lines[0].startswith(DAILYMED) and lines[1] == "2026-11-25"
    assert sentence in lines
    cells = [c for c in readme_rows() if medicine_id in c[0]][0]
    assert cells[2] == sentence
    assert cells[3] == lines[0]
    assert cells[1].startswith("none") == (medicine_id != OBIZUR)


def test_the_mitem_deferoxamine_label_is_recorded_as_not_read():
    text = (FOLDER / "unread" / "mitem-desferal-not-readable.txt").read_text(encoding="utf-8")
    assert text.splitlines()[0] == DAILYMED + "38eff751-96c5-c48a-e063-6294a90a0e48"
    assert text.splitlines()[3].startswith("NOT READ")


def test_every_readable_deferoxamine_label_says_not_for_primary_hemochromatosis():
    files = [FOLDER / CARDS[DEFEROXAMINE][0]] + sorted((FOLDER / "also_read").glob("*.txt"))
    assert len(files) == 6  # seven labels on DailyMed; Mitem's holds no text
    for file in files:
        assert re.search(r"not indicated for the treatment of primary hemochromatosis",
                         file.read_text(encoding="utf-8"), re.I), file.name


# ---- card 1: avapritinib ----

def test_avapritinib_shows_on_approved_with_the_added_line_and_not_in_new_clues():
    places = first_batch.everywhere(tabs(MASTOCYTOSIS))
    assert [place for place, ids in places.items() if AVAPRITINIB in ids] == ["approved"]
    assert card(tabs(MASTOCYTOSIS), AVAPRITINIB).proof_note == engine.ADDED_LINE
    lines = (FOLDER / CARDS[AVAPRITINIB][0]).read_text(encoding="utf-8")
    assert "advanced systemic mastocytosis (AdvSM)" in lines
    assert CARDS[AVAPRITINIB][1] in lines
    assert [e for e in load(APPROVALS_FILE) if e["medicine_id"] == AVAPRITINIB
            and e["disease_id"] == MASTOCYTOSIS and "limited" not in e]


# ---- card 2: imatinib ----

def test_imatinib_shows_on_approved_limited_and_not_in_new_clues():
    page = tabs(MASTOCYTOSIS)
    places = first_batch.everywhere(page)
    assert [place for place, ids in places.items() if IMATINIB in ids] == ["approved"]
    imatinib = card(page, IMATINIB)
    assert imatinib.proof_note == engine.ADDED_LINE
    assert imatinib.limit_note == engine.LIMITED_LINE
    assert [e for e in load(APPROVALS_FILE) if e["medicine_id"] == IMATINIB
            and e["disease_id"] == MASTOCYTOSIS and e.get("limited") is True]


# ---- card 3: deferoxamine ----

def test_deferoxamine_is_in_the_red_box_for_hemochromatosis_and_the_card_is_kept():
    page = tabs(HEMOCHROMATOSIS)
    assert DEFEROXAMINE in [m.id for m in page.approved]  # the card is kept, not removed
    assert [m.id for m in engine.wrong_approvals_box(page.approved, HEMOCHROMATOSIS)] == [DEFEROXAMINE]
    assert engine.warning_words(HEMOCHROMATOSIS) == {DEFEROXAMINE: SECOND_NOTE}
    found = [e for e in load(CORRECTIONS_FILE) if e["medicine_id"] == DEFEROXAMINE]
    assert [{k: v for k, v in e.items() if k != "label"} for e in found] == [
        {"medicine_id": DEFEROXAMINE, "disease_id": HEMOCHROMATOSIS,
         "date": "2026-11-22", "note": SECOND_NOTE}]


# ---- card 4: Obizur ----

def test_obizur_label_names_only_acquired_haemophilia_a():
    text = (FOLDER / CARDS[OBIZUR][0]).read_text(encoding="utf-8")
    assert "adults with acquired hemophilia A" in text
    assert CARDS[OBIZUR][1] in text
    assert "congenital" not in text.lower()  # it names no other kind of haemophilia A


def test_obizur_is_in_the_red_box_for_haemophilia_a_and_the_card_is_kept():
    page = tabs(HAEMOPHILIA_A)
    assert OBIZUR in [m.id for m in page.approved]  # the card is kept, not removed
    assert OBIZUR in [m.id for m in engine.wrong_approvals_box(page.approved, HAEMOPHILIA_A)]
    assert engine.warning_words(HAEMOPHILIA_A)[OBIZUR] == SECOND_NOTE
    found = [e for e in load(CORRECTIONS_FILE) if e["medicine_id"] == OBIZUR]
    assert [{k: v for k, v in e.items() if k != "label"} for e in found] == [
        {"medicine_id": OBIZUR, "disease_id": HAEMOPHILIA_A,
         "date": "2026-11-25", "note": SECOND_NOTE}]
    assert OBIZUR not in {e["medicine_id"] for e in load(APPROVALS_FILE)}
