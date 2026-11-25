"""Ticket 3.15, Q6. The exception to Q22.

Q22 (Kashish, signed 25 Nov) stays: a combination pill's label does not
count for one of its parts. The exception (25 Nov, Shreshth with Kashish's
counsel): it does count when the medicine is never sold on its own in the
US, EU or UK. moonlight/combination_only.json lists those medicines.

MAIN 4's answer (b): the list is for the people who read labels by hand.
No code reads it and nothing on any page changes. So these tests check only
that the file is written correctly, and that every id is in a saved Open
Targets answer under the same name. No network.
"""

import json
import pathlib
import re

import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent
LIST_FILE = ROOT / "moonlight" / "combination_only.json"
FIXTURES = ROOT / "fixtures"
KEYS = {"medicine_id", "date", "source"}
THE_DAY = "2026-11-25"

# The six medicines of the ticket, and the saved answer that holds each id.
EXPECTED = {
    "CHEMBL3137301": ("SACUBITRIL", "labels_read/2.48/disease_drugs/MONDO_0005252.response.json"),
    "CHEMBL2103870": ("LUMACAFTOR", "combination_only/disease_drugs_MONDO_0009061.response.json"),
    "CHEMBL3544914": ("TEZACAFTOR", "combination_only/disease_drugs_MONDO_0009061.response.json"),
    "CHEMBL4298128": ("ELEXACAFTOR", "combination_only/disease_drugs_MONDO_0009061.response.json"),
    "CHEMBL1198857": ("VILANTEROL", "family/MONDO_0004979/disease_drugs/own_MONDO_0004979.response.json"),
    "CHEMBL4594379": ("FOSLEVODOPA", "old_withdrawn_flag/answers/disease_drugs/db3b2c7efb3e95a9.json"),
}
# Pages of the official US and EU regulators only.
LABEL_PAGE = re.compile(
    r"^https://(dailymed\.nlm\.nih\.gov/dailymed/drugInfo\.cfm\?setid=[0-9a-f-]{36}"
    r"|www\.ema\.europa\.eu/en/medicines/human/EPAR/[a-z0-9-]+)$")


def entries():
    if not LIST_FILE.exists():
        return []
    return json.loads(LIST_FILE.read_text(encoding="utf-8"))


def ids_and_names(answer):
    """Every (id, name) drug record in a saved Open Targets answer."""
    found = set()

    def walk(x):
        if isinstance(x, dict):
            if isinstance(x.get("id"), str) and x["id"].startswith("CHEMBL") and "name" in x:
                found.add((x["id"], x["name"]))
            for value in x.values():
                walk(value)
        elif isinstance(x, list):
            for value in x:
                walk(value)

    walk(answer)
    return found


def test_the_list_is_a_list_of_entries_with_exactly_the_three_keys():
    assert LIST_FILE.exists()
    listed = entries()
    assert isinstance(listed, list)
    for entry in listed:
        assert set(entry) == KEYS
        assert all(isinstance(entry[key], str) and entry[key] for key in KEYS)


def test_the_list_holds_exactly_the_six_medicines_once_each():
    ids = [entry["medicine_id"] for entry in entries()]
    assert len(ids) == len(set(ids))
    assert set(ids) == set(EXPECTED)


@pytest.mark.parametrize("entry", entries(), ids=lambda e: e["medicine_id"])
def test_each_entry_is_dated_and_points_at_a_label_page(entry):
    assert entry["date"] == THE_DAY
    assert LABEL_PAGE.match(entry["source"]), entry["source"]


@pytest.mark.parametrize("entry", entries(), ids=lambda e: e["medicine_id"])
def test_each_id_is_in_a_saved_answer_under_its_name(entry):
    name, saved = EXPECTED[entry["medicine_id"]]
    answer = json.loads((FIXTURES / saved).read_text(encoding="utf-8"))
    assert (entry["medicine_id"], name) in ids_and_names(answer)


@pytest.mark.parametrize("medicine", ["lumacaftor", "tezacaftor", "elexacaftor"])
def test_each_cystic_fibrosis_id_is_also_confirmed_by_its_own_saved_answers(medicine):
    by_name = {name.lower(): chembl for chembl, (name, _) in EXPECTED.items()}
    chembl = by_name[medicine]
    assert chembl in {e["medicine_id"] for e in entries()}
    saved = FIXTURES / "combination_only"
    search = json.loads((saved / f"search_{medicine}.response.json").read_text())
    hits = search["data"]["search"]["hits"]
    assert (chembl, medicine.upper()) in {(h["id"], h["name"]) for h in hits}
    record = json.loads((saved / f"drug_{chembl}.response.json").read_text())["data"]["drug"]
    assert (record["id"], record["name"]) == (chembl, medicine.upper())


def test_no_code_reads_the_list():
    # MAIN 4's answer (b): it is a list for the people who read labels.
    for code in (ROOT / "moonlight").glob("*.py"):
        assert "combination_only" not in code.read_text(encoding="utf-8"), code.name
