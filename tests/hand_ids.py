"""Set a permanent correction id aside when an older test reads a hand list.

The seven hand lists carry "id" (C-001, C-002, ...). Tests written before
that pin the other fields. without_correction_id removes only an id whose
value is a correction number, so a card's own medicine id stays.
"""

import re

_CORRECTION_ID = re.compile(r"^C-\d{3,}$")
_REPORT = re.compile(r"^E\d+$")


def without_correction_id(value):
    """A hand-list value with correction ids and report numbers removed.

    Other JSON is unchanged. A card's own medicine id stays.
    """
    if isinstance(value, list):
        return [without_correction_id(item) for item in value]
    if isinstance(value, dict):
        cid = value.get("id")
        if isinstance(cid, str) and _CORRECTION_ID.fullmatch(cid):
            value = {key: item for key, item in value.items() if key != "id"}
        report = value.get("report")
        if isinstance(report, str) and _REPORT.fullmatch(report):
            value = {key: item for key, item in value.items() if key != "report"}
    return value
