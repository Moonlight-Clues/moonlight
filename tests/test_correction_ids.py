"""Permanent correction numbers on the seven hand lists.

Every entry of corrections, approvals, limits, confirmed, withdrawals,
pmda_summaries and salt_parents carries an id like C-001. The numbers are
one sequence, assigned once in date order. On one day, ties keep list
order (the seven names above), then each entry's place in its file.
A number is never reused and never renumbered.

fixtures/correction_ids.json pins id to a stable identity, so a renumber
fails this test. A new entry takes the next number from
moonlight.correction_ids.next_id (or `python -m moonlight.correction_ids`).
"""

import json
import pathlib
import re

import pytest

from moonlight import correction_ids, engine, fetch

ROOT = pathlib.Path(__file__).resolve().parent.parent
FIXTURE = ROOT / "fixtures" / "correction_ids.json"
LISTS = ROOT / "moonlight"
ID_RE = re.compile(r"^C-\d{3,}$")
REPORT_RE = re.compile(r"^E\d+$")
# The eight entries a person checked. No other entry carries "report".
REPORTS = {
    "C-219": "E17",
    "C-059": "E4",
    "C-060": "E6",
    "C-055": "E8",
    "C-056": "E11",
    "C-057": "E14",
    "C-058": "E14",
    "C-278": "E52",
}

# The seven lists, in the order a same-day tie is broken.
HAND_LISTS = (
    "corrections",
    "approvals",
    "limits",
    "confirmed",
    "withdrawals",
    "pmda_summaries",
    "salt_parents",
)


def _load(name):
    return json.loads((LISTS / f"{name}.json").read_text(encoding="utf-8"))


def identities():
    """Stable identity -> id, read straight from the files.

    A list entry is "list|medicine_id|disease_id". A salt row is
    "salt_parents|<salt id>", the key of salt_parents.json. The id is
    not part of the identity, so renumbering changes the value, not the key.
    """
    found = {}
    for name in HAND_LISTS:
        held = _load(name)
        if name == "salt_parents":
            pairs = ((salt, row) for salt, row in held.items())
        else:
            pairs = ((None, row) for row in held)
        for salt, row in pairs:
            if name == "salt_parents":
                key = f"salt_parents|{salt}"
            else:
                key = f"{name}|{row['medicine_id']}|{row['disease_id']}"
            assert key not in found, key
            found[key] = row.get("id")
    return found


def test_the_seven_lists_are_the_documented_sequence():
    assert correction_ids.HAND_LISTS == HAND_LISTS


def test_every_entry_has_a_unique_permanent_id():
    found = identities()
    assert found, "the hand lists are empty"
    ids = list(found.values())
    assert all(isinstance(one, str) and ID_RE.fullmatch(one) for one in ids)
    assert len(ids) == len(set(ids))


def test_ids_never_change_for_an_existing_entry():
    """The fixture is the pin. Renumbering, or dropping an entry, fails."""
    pinned = json.loads(FIXTURE.read_text(encoding="utf-8"))
    assert identities() == pinned


def test_a_report_when_present_matches_a_report_number_and_only_the_eight_have_one():
    """report, when present, matches ^E\\d+$. The other candidates stay blank."""
    found = {}
    for name in HAND_LISTS:
        held = _load(name)
        rows = held.values() if name == "salt_parents" else held
        for row in rows:
            if "report" not in row:
                continue
            assert isinstance(row["report"], str) and REPORT_RE.fullmatch(row["report"])
            assert row["id"] not in found
            found[row["id"]] = row["report"]
    assert found == REPORTS


def test_a_bad_report_is_refused_and_a_good_one_is_kept():
    good = {"id": "C-001", "report": "E17", "medicine_id": "CHEMBL1",
            "disease_id": "MONDO_1", "date": "2026-11-16", "note": engine.CORRECTION_NOTE}
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(engine, "_read_corrections", lambda: [good])
        assert engine.corrections() == {("CHEMBL1", "MONDO_1")}
        patch.setattr(engine, "_read_corrections", lambda: [dict(good, report="e17")])
        with pytest.raises(ValueError, match="E17"):
            engine.corrections()
        patch.setattr(engine, "_read_corrections", lambda: [dict(good, report="E")])
        with pytest.raises(ValueError, match="E17"):
            engine.corrections()


def test_the_helper_offers_the_next_id_and_never_a_used_one():
    pinned = json.loads(FIXTURE.read_text(encoding="utf-8"))
    numbers = [int(value.split("-", 1)[1]) for value in pinned.values()]
    assert correction_ids.next_id() == f"C-{max(numbers) + 1:03d}"
    assert correction_ids.next_id() not in set(pinned.values())


def test_a_correction_may_carry_a_good_id_and_a_bad_id_is_refused():
    good = {"id": "C-001", "medicine_id": "CHEMBL1", "disease_id": "MONDO_1",
            "date": "2026-11-16", "note": engine.CORRECTION_NOTE}
    # Older tests build entries with no id. That still reads.
    plain = {key: value for key, value in good.items() if key != "id"}
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(engine, "_read_corrections", lambda: [plain])
        assert engine.corrections() == {("CHEMBL1", "MONDO_1")}
        patch.setattr(engine, "_read_corrections", lambda: [good])
        assert engine.corrections() == {("CHEMBL1", "MONDO_1")}
        patch.setattr(engine, "_read_corrections", lambda: [dict(good, id="E36")])
        with pytest.raises(ValueError, match="C-001"):
            engine.corrections()
        patch.setattr(engine, "_read_corrections", lambda: [dict(good, id="C-1")])
        with pytest.raises(ValueError, match="C-001"):
            engine.corrections()


@pytest.mark.salt_parents  # the real reader, not the empty stand-in
def test_a_salt_row_may_carry_a_good_id_and_a_bad_id_is_refused(tmp_path, monkeypatch):
    def write(row):
        path = tmp_path / "salt_parents.json"
        path.write_text(json.dumps({"CHEMBL1": row}), encoding="utf-8")
        monkeypatch.setattr(fetch, "SALT_PARENTS_FILE", path)
        monkeypatch.setattr(fetch, "_SALT_PARENTS", None)

    row = {"parent": "CHEMBL2", "parent_name": "Example", "source": "https://example.org/a",
           "date": "2026-11-26"}
    write(row)
    assert fetch._salt_parents()["CHEMBL1"]["parent"] == "CHEMBL2"
    write(dict(row, id="C-010"))
    assert fetch._salt_parents()["CHEMBL1"]["id"] == "C-010"
    write(dict(row, id="nope"))
    with pytest.raises(ValueError, match="C-001"):
        fetch._salt_parents()
