"""Permanent ids for the seven hand lists.

Every entry carries an "id" like C-001. The numbers are one sequence across
corrections, approvals, limits, confirmed, withdrawals, pmda_summaries and
salt_parents, assigned once in date order. Entries from the same day keep
that list order, then their place in the file. A number is never reused
and never renumbered. A new entry takes the next number:

    python -m moonlight.correction_ids

That prints the next id, for example C-288. Write it on the new entry.
Do not fill a gap, and do not change an id that is already in the file.
"""

import json
import pathlib
import re

HERE = pathlib.Path(__file__).resolve().parent

# Same-day ties break in this order, then by place in the file.
HAND_LISTS = (
    "corrections",
    "approvals",
    "limits",
    "confirmed",
    "withdrawals",
    "pmda_summaries",
    "salt_parents",
)

# At least three digits: C-001, and C-1000 when the sequence passes 999.
ID_RE = re.compile(r"^C-\d{3,}$")
# A report number such as E17 or E4. Only some entries carry one.
REPORT_RE = re.compile(r"^E\d+$")


def check_id(value):
    """ValueError unless value is a permanent correction number."""
    if not isinstance(value, str) or not ID_RE.fullmatch(value):
        raise ValueError(
            f"A hand-list id must be a permanent correction number like C-001: {value!r}")


def check_report(value):
    """ValueError unless value is a report number like E17."""
    if not isinstance(value, str) or not REPORT_RE.fullmatch(value):
        raise ValueError(
            f"A hand-list report must be a report number like E17: {value!r}")


def without_id(entry):
    """The entry without its id and report, after checking them.

    An entry with no id is returned as it is, so a made-up test entry still
    reads. The real files all carry an id; tests/test_correction_ids.py
    refuses a file that drops one. "report" is optional. When it is present
    it must match ^E\\d+$, and it is set aside so the rest of the entry is
    read as before.
    """
    if isinstance(entry, dict) and ("id" in entry or "report" in entry):
        kept = dict(entry)
        if "id" in kept:
            check_id(kept.pop("id"))
        if "report" in kept:
            check_report(kept.pop("report"))
        return kept
    return entry


def _read(name):
    return json.loads((HERE / f"{name}.json").read_text(encoding="utf-8"))


def identities():
    """Stable identity -> id, for every entry that has an id.

    A list entry's identity is "list|medicine_id|disease_id". A salt row's
    identity is "salt_parents|<salt id>", the key in salt_parents.json.
    An entry with no id is omitted here; the test reads the files itself
    and requires every entry to have one.
    """
    found = {}
    for name in HAND_LISTS:
        held = _read(name)
        rows = held.items() if name == "salt_parents" else ((None, row) for row in held)
        for salt, row in rows:
            if "id" not in row:
                continue
            if name == "salt_parents":
                key = f"salt_parents|{salt}"
            else:
                key = f"{name}|{row['medicine_id']}|{row['disease_id']}"
            found[key] = row["id"]
    return found


def used_numbers():
    """Every correction number already written on an entry."""
    numbers = []
    for cid in identities().values():
        check_id(cid)
        numbers.append(int(cid.split("-", 1)[1]))
    return numbers


def format_id(number):
    """287 -> 'C-287'. Past 999 the width grows: 1000 -> 'C-1000'."""
    return f"C-{number:03d}"


def next_id():
    """The next permanent id. One past the highest number already used.

    A gap is left empty. Deleting an entry does not hand its number out again.
    """
    numbers = used_numbers()
    return format_id((max(numbers) if numbers else 0) + 1)


def main():
    print(next_id())


if __name__ == "__main__":
    main()
