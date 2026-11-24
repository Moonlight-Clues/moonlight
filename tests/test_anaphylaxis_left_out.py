"""Ticket 2.20. 33 opposite-way clues are left out by hand on the
anaphylaxis page (MONDO_0100053).

Kashish's case, decided 22 Nov 2026: epinephrine is the approved medicine
for anaphylaxis. 34 new clues push the opposite way. She checked them by
hand. 33 only push the opposite way and come out. One, isoxsuprine
(CHEMBL1197051), pushes both ways and STAYS on the page.

The file moonlight/left_out.json holds ids and dates only. The names
below are for the reader of this test. They are not in the file.

No test here touches the network. The page is built from hand-built
paths, with api._find replaced, and the real left-out file is read.
"""

import json
import pathlib
import re
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from moonlight import api, engine
from moonlight.filter import sort_paths
from moonlight.records import Disease, Medicine, MedicineForm, Path, Target

ROOT = pathlib.Path(__file__).resolve().parent.parent
LEFT_OUT_FILE = ROOT / "moonlight" / "left_out.json"

ANAPHYLAXIS = "MONDO_0100053"
DRUG_INDUCED = "HP_0410149"  # "Drug-induced anaphylaxis": another page, not touched
ADDISON = "MONDO_0015129"
DECIDED = "2026-11-22"
ISOXSUPRINE = "CHEMBL1197051"  # pushes both ways: it stays

# In the ticket's order. Kashish said yes to every id.
THE_33 = [
    "CHEMBL321582",   # bucindolol
    "CHEMBL27810",    # celiprolol
    "CHEMBL499",      # timolol
    "CHEMBL434394",   # nebivolol
    "CHEMBL471",      # sotalol
    "CHEMBL631",      # propafenone
    "CHEMBL521606",   # nadolol
    "CHEMBL1201237",  # levobunolol
    "CHEMBL546",      # oxprenolol
    "CHEMBL1290",     # penbutolol
    "CHEMBL429",      # labetalol
    "CHEMBL839",      # carteolol
    "CHEMBL24",       # atenolol
    "CHEMBL1742466",  # landiolol
    "CHEMBL423",      # betaxolol
    "CHEMBL642",      # acebutolol
    "CHEMBL1201274",  # levobetaxolol
    "CHEMBL836",      # tamsulosin
    "CHEMBL597",      # phentolamine
    "CHEMBL707",      # doxazosin
    "CHEMBL2",        # prazosin
    "CHEMBL611",      # terazosin
    "CHEMBL753",      # phenoxybenzamine
    "CHEMBL24778",    # silodosin
    "CHEMBL3559672",  # rauwolfia serpentina
    "CHEMBL2364968",  # ergoloid
    "CHEMBL644",      # trimipramine
    "CHEMBL770",      # tolazoline
    "CHEMBL1201454",  # alseroxylon
    "CHEMBL142635",   # naftopidil
    "CHEMBL188185",   # bunazosin
    "CHEMBL1201216",  # dapiprazole
    "CHEMBL654",      # mirtazapine
]

# The engine's words (Kashish's, 19 Nov), with this page's number.
LINE_33 = "33 medicines left out because they push the wrong way for this disease."

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


def path(name, medicine_id, disease):
    """One hand-built path: this medicine turns the test protein down."""
    form = MedicineForm(medicine_id, name, best_stage="APPROVAL", disease_stage=None,
                        withdrawn=False)
    return Path(Medicine(name, (form,)), PROTEIN, disease, ("INHIBITOR",), PROTEIN.score,
                (f"https://example.org/{medicine_id}",))


def page_of_92(disease):
    """A page shaped like the real one: 92 new clues. The 33, isoxsuprine,
    and 58 others. Read with the real left-out file."""
    ids = THE_33 + [ISOXSUPRINE] + [f"CHEMBL99{number:05d}" for number in range(58)]
    paths = [path(f"Medicine {number}", medicine_id, disease)
             for number, medicine_id in enumerate(ids, start=1)]
    found = api._Found(disease, sort_paths(paths), [], [], [])
    with patch.object(api, "_find", return_value=found):  # the real two files
        response = TestClient(api.app).get("/api/clues", params={"disease_id": disease.id})
    assert response.status_code == 200
    return response.json()


def shown(answer):
    return {clue["id"] for clue in answer["new_clues"]}


# ---- the file ----

def real_entries():
    return json.loads(LEFT_OUT_FILE.read_text(encoding="utf-8"))


def test_the_ticket_lists_33_different_medicines_and_not_isoxsuprine():
    assert len(THE_33) == 33 == len(set(THE_33))
    assert ISOXSUPRINE not in THE_33


def test_the_file_ends_with_the_33_for_anaphylaxis_in_the_tickets_order():
    last = real_entries()[4:37]  # ticket 2.43 added sixteen after these
    assert [entry["medicine_id"] for entry in last] == THE_33
    for entry in last:
        assert entry == {"medicine_id": entry["medicine_id"],
                         "disease_id": ANAPHYLAXIS, "date": DECIDED}


def test_the_33_are_the_only_entries_for_anaphylaxis():
    listed = [entry["medicine_id"] for entry in real_entries()
              if entry["disease_id"] == ANAPHYLAXIS]
    assert sorted(listed) == sorted(THE_33)
    assert engine.pushes_wrong_way(ANAPHYLAXIS) == set(THE_33)


def test_isoxsuprine_is_not_in_the_file_at_all():
    assert ISOXSUPRINE not in {entry["medicine_id"] for entry in real_entries()}
    assert ISOXSUPRINE not in LEFT_OUT_FILE.read_text(encoding="utf-8")


def test_the_file_holds_ids_and_dates_only_no_names():
    text = LEFT_OUT_FILE.read_text(encoding="utf-8")
    for entry in real_entries():
        assert set(entry) == {"medicine_id", "disease_id", "date"}
        assert re.fullmatch(r"CHEMBL\d+", entry["medicine_id"])
        assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", entry["date"])
    for name in ("bucindolol", "timolol", "atenolol", "prazosin", "mirtazapine",
                 "rauwolfia", "isoxsuprine", "anaphylaxis", "epinephrine"):
        assert name not in text.lower()
    # Nothing but the three keys, ids and days is written there.
    assert re.sub(r'"(medicine_id|disease_id|date|CHEMBL\d+|[A-Za-z]+_\d+|\d{4}-\d{2}-\d{2})"',
                  "", text).strip("[]{}:, \n") == ""
    assert re.sub(r'"[^"]*"', "", text).replace("[", "").replace("]", "") \
        .replace("{", "").replace("}", "").replace(":", "").replace(",", "").strip() == ""


def test_nothing_else_is_listed_for_drug_induced_anaphylaxis():
    assert engine.pushes_wrong_way(DRUG_INDUCED) == set()


def test_the_four_for_addisons_are_still_there_first_and_unchanged():
    assert real_entries()[:4] == [
        {"medicine_id": "CHEMBL295698", "disease_id": ADDISON, "date": "2026-11-19"},
        {"medicine_id": "CHEMBL1670", "disease_id": ADDISON, "date": "2026-11-19"},
        {"medicine_id": "CHEMBL3099695", "disease_id": ADDISON, "date": "2026-11-19"},
        {"medicine_id": "CHEMBL934", "disease_id": ADDISON, "date": "2026-11-19"},
    ]
    # Ticket 2.43 added sixteen, dated 2026-11-24, after these.
    assert len([entry for entry in real_entries() if entry["date"] < "2026-11-24"]) == 4 + 33


# ---- the page ----

def test_the_anaphylaxis_page_shows_59_new_clues_not_92_and_the_line_counts_33():
    answer = page_of_92(Disease(ANAPHYLAXIS, "anaphylaxis"))
    assert len(answer["new_clues"]) == 59
    assert answer["wrong_way_line"] == LINE_33
    assert not shown(answer) & set(THE_33)


def test_isoxsuprine_stays_on_the_anaphylaxis_page():
    assert ISOXSUPRINE in shown(page_of_92(Disease(ANAPHYLAXIS, "anaphylaxis")))


def test_the_same_33_stay_on_any_other_disease_page():
    for other in (Disease(DRUG_INDUCED, "Drug-induced anaphylaxis"),
                  Disease(ADDISON, "chronic primary adrenal insufficiency")):
        answer = page_of_92(other)
        assert len(answer["new_clues"]) == 92 and "wrong_way_line" not in answer
        assert set(THE_33) <= shown(answer)
