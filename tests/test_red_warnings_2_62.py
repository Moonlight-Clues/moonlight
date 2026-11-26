"""Ticket 2.62. Red warnings from Kashish's sheet of 26 Nov (Part 1), and
three "only some people" lines (Part 3 rows 6-7 (row 8 waits: see the PR)).

Draft: built for every row; MAIN 4 removes the rows Kashish answers No to.

TO REMOVE A ROW: delete its one line in RED_ROWS (or LIMIT_ROWS) below and its
one line in moonlight/corrections.json (or limits.json). Nothing else in this
file names a row: every test is parametrised over these two tables, and the
counts are worked out from them.

Saved answers only (fixtures/red_warnings_2_62/): Open Targets answers
recorded live on 2026-11-26 (see its README). No network. "Before" is the
same saved answers read with the ticket's entries taken out of the lists, so
a card can only differ because of an entry.
"""

import copy
import json
import pathlib
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from moonlight import api, engine, fetch

ROOT = pathlib.Path(__file__).resolve().parent.parent
SAVED = ROOT / "fixtures" / "red_warnings_2_62"
CORRECTIONS_FILE = ROOT / "moonlight" / "corrections.json"
LIMITS_FILE = ROOT / "moonlight" / "limits.json"

THE_DAY = "2026-11-26"
NOTE = ("This looks like a mistake in the database. The official label is for "
        "a different disease.")
LIMIT_LINE = "The label covers only some people with this disease."
# Entries in the files on main (507dae6) before this ticket.
CORRECTIONS_ON_MAIN = 122
LIMITS_ON_MAIN = 5

# (sheet row, medicine id, disease id, name on the card, list it sits in today)
RED_ROWS = [
    (1, "CHEMBL1447", "EFO_0803536", "Lincomycin", "approved"),
    (2, "CHEMBL1095777", "MONDO_0004979", "Indacaterol", "approved"),
    (3, "CHEMBL1187833", "MONDO_0004979", "Umeclidinium", "approved"),
    (4, "CHEMBL1201335", "MONDO_0004979", "Glycopyrronium", "approved"),
    (5, "CHEMBL1200500", "MONDO_0005002", "Beclomethasone Dipropionate", "approved"),
    (5, "CHEMBL1586", "MONDO_0005002", "Beclomethasone", "approved"),
    (6, "CHEMBL1676", "MONDO_0005002", "Fluticasone Furoate", "approved"),
    (7, "CHEMBL689", "MONDO_0005002", "Mannitol", "narrower"),
    (8, "CHEMBL485", "MONDO_0005277", "Codeine", "approved"),
    (10, "CHEMBL1590", "MONDO_0005277", "Pseudoephedrine", "approved"),
    (11, "CHEMBL582", "MONDO_0005083", "Isopropyl Alcohol", "approved"),
    (12, "CHEMBL3988900", "MONDO_0005083", "Zinc Oxide", "approved"),
    (13, "CHEMBL256087", "MONDO_0005083", "Menthol", "approved"),
    (14, "CHEMBL582", "MONDO_0008383", "Isopropyl Alcohol", "approved"),
    (15, "CHEMBL1201320", "MONDO_0008383", "Esomeprazole", "approved"),
    (16, "CHEMBL1503", "MONDO_0008383", "Omeprazole", "approved"),
    (17, "CHEMBL902", "MONDO_0008383", "Famotidine", "approved"),
    (18, "CHEMBL606", "MONDO_0008383", "Misoprostol", "approved"),
    (19, "CHEMBL1201287", "MONDO_0008383", "Dexbrompheniramine", "wider_group"),
    (20, "CHEMBL1200929", "MONDO_0010200", "Zinc Sulfate", "approved"),
]
EMA = "https://www.ema.europa.eu/en/medicines/human/EPAR/"
DM = "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid="
# (part 3 row, medicine id, disease id, name, label)
LIMIT_ROWS = [
    (6, "CHEMBL2108334", "MONDO_0010602", "Eptacog Alfa (ACTIVATED)", EMA + "novoseven"),
    (7, "CHEMBL5315078", "MONDO_0010602", "Eptacog Beta (ACTIVATED)", EMA + "cevenfacta"),
    # Row 8, daratumumab CHEMBL1743007 / MONDO_0019438, is NOT here: see the PR. The
    # pair is already in approvals.json, and the engine refuses a pair in both files.
]
# The eight checked NOT-red cards: (disease, medicine id, name, list)
NOT_RED = [
    ("MONDO_0005002", "CHEMBL1473", "Fluticasone Propionate", "approved"),
    ("MONDO_0005002", "CHEMBL1370", "Budesonide", "approved"),
    ("MONDO_0005277", "CHEMBL112", "Acetaminophen", "approved"),  # paracetamol
    ("MONDO_0005277", "CHEMBL25", "Aspirin", "approved"),
    ("MONDO_0008383", "CHEMBL112", "Acetaminophen", "wider_group"),
    ("MONDO_0008383", "CHEMBL15768", "Camphor", "wider_group"),
    ("MONDO_0008383", "CHEMBL25", "Aspirin", "wider_group"),
    ("MONDO_0008383", "CHEMBL294199", "Capsaicin", "wider_group"),
]
NOT_RED_PAGES = ("MONDO_0005002", "MONDO_0005277", "MONDO_0008383")
LISTS = ("approved", "narrower", "wider_group")


def red_ids():
    return {(medicine, disease) for _, medicine, disease, _, _ in RED_ROWS}


def limit_ids():
    return {(medicine, disease) for _, medicine, disease, _, _ in LIMIT_ROWS}


def pages():
    return sorted({disease for _, _, disease, _, _ in RED_ROWS}
                  | {disease for _, _, disease, _, _ in LIMIT_ROWS}
                  | set(NOT_RED_PAGES))


def row_id(row):
    return f"row{row[0]:02d}-{row[1]}-{row[2]}"


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


# ---- the saved answers ----

_INDEX = {entry["kind"] + " " + json.dumps(entry["variables"], sort_keys=True): entry["file"]
          for entry in read(SAVED / "answers" / "index.json")}
_KINDS = {
    fetch.DISEASE_QUERY: "disease", fetch.FAMILY_QUERY: "family",
    fetch.TARGETS_QUERY: "targets", fetch.TARGET_DRUGS_QUERY: "target_drugs",
    fetch.DISEASE_DRUGS_QUERY: "disease_drugs",
}


def saved_post_json(body):
    """Stands in for fetch._post_json. A question with no saved answer is an error."""
    assert set(body) == {"query", "variables"}
    key = _KINDS[body["query"]] + " " + json.dumps(body["variables"], sort_keys=True)
    assert key in _INDEX, f"no saved answer for {key}"
    return read(SAVED / "answers" / _INDEX[key])


def page(disease_id, signed=True):
    """/api/clues from the saved answers. signed=False reads the lists with
    this ticket's entries taken out: the page as it was before."""
    corrections = read(CORRECTIONS_FILE)
    limits = read(LIMITS_FILE)
    if not signed:
        corrections = [e for e in corrections
                       if not (e["date"] == THE_DAY and (e["medicine_id"], e["disease_id"]) in red_ids())]
        limits = [e for e in limits
                  if not (e["date"] == THE_DAY and (e["medicine_id"], e["disease_id"]) in limit_ids())]
    guards = [patch(name, side_effect=AssertionError("network used")) for name in (
        "requests.request", "requests.post", "requests.get", "requests.sessions.Session.request")]
    guards += [patch("moonlight.fetch._post_json", side_effect=saved_post_json),
               patch.object(engine, "_read_corrections", return_value=corrections),
               patch.object(engine, "_read_limits", return_value=limits)]
    api.forget_visitors()
    for guard in guards:
        guard.start()
    try:
        response = TestClient(api.app).get("/api/clues", params={"disease_id": disease_id})
    finally:
        for guard in guards:
            guard.stop()
        api.forget_visitors()
    assert response.status_code == 200, response.text
    return response.json()


@pytest.fixture(scope="module")
def after():
    return {d: page(d) for d in pages()}


@pytest.fixture(scope="module")
def before():
    return {d: page(d, signed=False) for d in pages()}


def card(answer, part, medicine_id):
    (found,) = [c for c in answer.get(part, []) if c["id"] == medicine_id]
    return found


def everywhere(answer, medicine_id):
    return [part for part in LISTS if medicine_id in [c["id"] for c in answer.get(part, [])]]


# ---- the files ----

@pytest.mark.parametrize("row", RED_ROWS, ids=row_id)
def test_each_red_row_is_in_corrections_json_once_with_the_note(row):
    _, medicine, disease, _, _ = row
    found = [e for e in read(CORRECTIONS_FILE)
             if (e["medicine_id"], e["disease_id"]) == (medicine, disease)]
    assert found == [{"medicine_id": medicine, "disease_id": disease,
                      "date": THE_DAY, "note": NOTE}]


@pytest.mark.parametrize("row", LIMIT_ROWS, ids=row_id)
def test_each_limit_row_is_in_limits_json_once_with_its_label(row):
    _, medicine, disease, _, label = row
    found = [e for e in read(LIMITS_FILE)
             if (e["medicine_id"], e["disease_id"]) == (medicine, disease)]
    assert found == [{"medicine_id": medicine, "disease_id": disease,
                      "date": THE_DAY, "label": label}]


def test_corrections_json_grew_by_exactly_the_signed_rows():
    assert len(read(CORRECTIONS_FILE)) == CORRECTIONS_ON_MAIN + len(RED_ROWS)


def test_limits_json_grew_by_exactly_the_signed_rows():
    assert len(read(LIMITS_FILE)) == LIMITS_ON_MAIN + len(LIMIT_ROWS)


@pytest.mark.parametrize("path", [CORRECTIONS_FILE, LIMITS_FILE], ids=lambda p: p.name)
def test_no_pair_is_written_twice(path):
    pairs = [(e["medicine_id"], e["disease_id"]) for e in read(path)]
    assert len(pairs) == len(set(pairs))


def test_the_engine_still_reads_both_files():
    engine.corrections()
    engine.limits_by_hand()


# ---- the pages: red rows ----

@pytest.mark.parametrize("row", RED_ROWS, ids=row_id)
def test_the_card_was_not_red_before(row, before):
    _, medicine, disease, _, box = row
    assert medicine not in before[disease].get("wrong_approvals_box", [])
    assert "warning" not in card(before[disease], box, medicine)


@pytest.mark.parametrize("row", RED_ROWS, ids=row_id)
def test_the_card_is_in_the_red_box_with_the_note(row, after):
    _, medicine, disease, name, box = row
    answer = after[disease]
    assert medicine in answer["wrong_approvals_box"]
    found = card(answer, box, medicine)
    assert found["medicine"] == name
    assert found["warning"] == NOTE
    assert everywhere(answer, medicine) == [box]  # one card, in its own list


def without_opposite_lines(cards):
    """New clues as the page draws them, minus the per-protein opposite-way line."""
    return [{**c, "proteins": [{k: v for k, v in p.items() if k != "opposite_way"}
                               for p in c["proteins"]]} for c in cards]


def opposite_ids(cards):
    return {c["id"] for c in cards if any("opposite_way" in p for p in c["proteins"])}


@pytest.mark.parametrize("disease", sorted({r[2] for r in RED_ROWS}))
def test_no_other_card_moves(disease, before, after):
    signed = {m for _, m, d, _, _ in RED_ROWS if d == disease}
    old, new = before[disease], after[disease]
    assert set(old) <= set(new)
    for part, value in old.items():
        if part in ("wrong_approvals_box", "opposite_way_box"):
            continue  # checked below
        if part == "new_clues":
            assert without_opposite_lines(new[part]) == without_opposite_lines(value)
        elif part in LISTS:
            assert [c["id"] for c in new[part]] == [c["id"] for c in value]
            for was, now in zip(value, new[part]):
                if was["id"] in signed:
                    assert {k: v for k, v in now.items() if k != "warning"} == was
                else:
                    assert now == was
        else:
            assert new[part] == value
    # the red box: what it held, plus exactly the signed cards
    assert set(old.get("wrong_approvals_box", [])) <= set(new["wrong_approvals_box"])
    assert set(new["wrong_approvals_box"]) - set(old.get("wrong_approvals_box", [])) == signed


@pytest.mark.parametrize("disease", sorted({r[2] for r in RED_ROWS}))
def test_the_only_side_effect_is_an_opposite_way_line_that_goes_away(disease, before, after):
    """Engine rule (ticket 3.7): a card with a red note is not one of "the approved
    medicines" that fix which way a protein is pushed. Once a signed medicine is red,
    a new clue whose line depended on it can lose the line; no card ever gains one,
    and the opposite-way box is the new clues that still carry it, in the same order."""
    old, new = before[disease], after[disease]
    lost = opposite_ids(old["new_clues"]) - opposite_ids(new["new_clues"])
    assert opposite_ids(new["new_clues"]) <= opposite_ids(old["new_clues"])
    assert new.get("opposite_way_box", []) == [
        i for i in old.get("opposite_way_box", []) if i not in lost]


@pytest.mark.parametrize("case", NOT_RED, ids=lambda c: f"{c[0]}-{c[1]}")
def test_the_eight_checked_not_red_cards_are_unchanged(case, before, after):
    disease, medicine, name, box = case
    now = card(after[disease], box, medicine)
    assert now["medicine"] == name
    assert now == card(before[disease], box, medicine)
    assert "warning" not in now
    assert medicine not in after[disease].get("wrong_approvals_box", [])


# ---- the pages: "only some people" ----

@pytest.mark.parametrize("row", LIMIT_ROWS, ids=row_id)
def test_the_card_carries_the_only_some_people_line(row, before, after):
    _, medicine, disease, name, _ = row
    assert "limit_note" not in card(before[disease], "approved", medicine)
    found = card(after[disease], "approved", medicine)
    assert found["medicine"] == name
    assert found["limit_note"] == LIMIT_LINE
    assert "warning" not in found  # a limit is grey, not red
    assert medicine not in after[disease].get("wrong_approvals_box", [])
    assert everywhere(after[disease], medicine) == ["approved"]


@pytest.mark.parametrize("row", LIMIT_ROWS, ids=row_id)
def test_only_that_card_changes_on_a_limit_page(row, before, after):
    _, medicine, disease, _, _ = row
    signed = {m for _, m, d, _, _ in LIMIT_ROWS if d == disease}
    for part, value in before[disease].items():
        if part in LISTS:
            for was, now in zip(value, after[disease][part]):
                if was["id"] in signed and part == "approved":
                    assert {k: v for k, v in now.items() if k != "limit_note"} == was
                else:
                    assert now == was
        else:
            assert after[disease][part] == value


# ---- the replay is honest ----

@pytest.mark.parametrize("disease", pages())
def test_the_offline_before_is_the_live_answer_saved_at_recording(disease, before):
    assert before[disease] == read(SAVED / "before" / f"{disease}.clues.json")


# ---- part 3 row 8: daratumumab, marked in approvals.json (MAIN 4, 26 Nov) ----
# Its pair is already in approvals.json (added by hand, 23 Nov), and the engine
# refuses a pair in both files, so the row is made with "limited": true on that
# entry. TO REMOVE THIS ROW: empty ROW8_PAIRS and delete the `, "limited": true`
# on the CHEMBL1743007 line of moonlight/approvals.json. The old tests that know
# about it read ROW8_PAIRS too.

ROW8_PAIRS = [("CHEMBL1743007", "MONDO_0019438")]
ADDED_LINE = "This approval is missing from the database. We added it from the official label."


def mark_row8(entries):
    """approvals.json entries as the file holds them with row 8 in."""
    return [dict(e, limited=True) if (e["medicine_id"], e["disease_id"]) in ROW8_PAIRS else e
            for e in entries]


def unmark_row8(entries):
    """The same entries as they were on main."""
    return [{k: v for k, v in e.items() if k != "limited"}
            if (e["medicine_id"], e["disease_id"]) in ROW8_PAIRS else e for e in entries]


def without_row8_line(answer):
    """A page answer with row 8's limit line taken off its card."""
    return {**answer, "approved": [
        {k: v for k, v in c.items() if k != "limit_note"}
        if (c["id"], answer["disease"]["id"]) in ROW8_PAIRS else c for c in answer["approved"]]}


@pytest.mark.parametrize("pair", ROW8_PAIRS)
def test_part3_row8_the_approvals_entry_is_marked_limited_and_nothing_else_changed(pair):
    (entry,) = [e for e in read(ROOT / "moonlight" / "approvals.json")
                if (e["medicine_id"], e["disease_id"]) == pair]
    assert entry == {"medicine_id": "CHEMBL1743007", "name": "Daratumumab",
                     "disease_id": "MONDO_0019438", "date": "2026-11-23",
                     "label": DM + "4bb241af-4299-4373-8762-2d6709515db0", "limited": True}
    assert pair not in {(e["medicine_id"], e["disease_id"]) for e in read(LIMITS_FILE)}


@pytest.mark.parametrize("pair", ROW8_PAIRS)
def test_part3_row8_the_card_shows_the_only_some_people_line_and_keeps_its_added_line(pair):
    medicine, disease = pair
    answer = page(disease)
    found = card(answer, "approved", medicine)
    assert found["limit_note"] == LIMIT_LINE
    assert found["proof_note"] == ADDED_LINE  # the grey line it had before stays
    assert "warning" not in found
    assert everywhere(answer, medicine) == ["approved"]
    was = card(read(SAVED / "before" / f"{disease}.clues.json"), "approved", medicine)
    assert {k: v for k, v in found.items() if k != "limit_note"} == was
