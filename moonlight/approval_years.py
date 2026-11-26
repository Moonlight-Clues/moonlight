"""Ticket 3.22. The year a medicine was first approved, from a hand-written list.

moonlight/approval_years.json, shape:
    {"CHEMBL...": {"year": 2001, "region": "US", "source": "<https link>"}}

The key is the medicine family id, the same id an Approved card carries. Open
Targets 26.09 has no usable approval year (checked 2026-11-26: no US years), so
Moonlight asks nobody. It reads this file, and nothing else, for the card line.

A bad entry is skipped and named in the log, never guessed and never allowed
to take the page down. No entry for a card: no line.
"""

import json
import logging
import pathlib
from typing import Dict

FILE = pathlib.Path(__file__).with_name("approval_years.json")
_log = logging.getLogger(__name__)


def _read() -> object:
    """The one place the file is read. Tests replace this."""
    return json.loads(FILE.read_text(encoding="utf-8"))


def load() -> Dict[str, dict]:
    """medicine id -> {"year": int, "region": str, "source": str}. {} if the
    file cannot be read. "source" is only there if it is an https link."""
    try:
        entries = _read()
    except (OSError, ValueError):
        _log.warning("approval_years.json could not be read: no year lines are shown.")
        return {}
    if not isinstance(entries, dict):
        _log.warning("approval_years.json must hold an object: no year lines are shown.")
        return {}
    good: Dict[str, dict] = {}
    for medicine_id, entry in entries.items():
        year = entry.get("year") if isinstance(entry, dict) else None
        region = entry.get("region") if isinstance(entry, dict) else None
        if (not isinstance(year, int) or isinstance(year, bool) or not 1800 <= year <= 2100
                or not isinstance(region, str) or not region.strip()):
            _log.warning("approval_years.json: entry %r skipped (needs a year and a region).",
                         medicine_id)
            continue
        item = {"year": year, "region": region.strip()}
        source = entry.get("source")
        if isinstance(source, str) and source.startswith("https://"):
            item["source"] = source
        good[medicine_id] = item
    return good
