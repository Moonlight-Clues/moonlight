"""Ticket T5. The name matcher.

A trial names its medicine, sometimes with other names. match() gives the ONE
Open Targets medicine those names mean, or None. Exact matching only: no fuzzy
and no AI matching.

Kashish's rules (26 Nov 2026):
- Names used: each record's name, and its synonyms and trade names whose source
  is "ChEMBL", for the medicine and its salt (child) forms. Names from AACT are
  never used. Trade names "X component of Y" are never used.
- Before comparing, case and spaces are evened out, and amounts with units
  ("500 mg", "1.5 mg/kg", "0.5%") are removed. Form words ("tablets") stay.
- A name in brackets is an extra name. "Erlotinib (Tarceva)" is tried as
  "Erlotinib" and as "Tarceva" (MAIN 5, 26 Nov 2026).
- "(drug)" is dropped. "Fenofibrate (drug)" is tried as "Fenofibrate".
- A medicine and its salt forms are one medicine: Open Targets' parentMolecule,
  else moonlight/salt_parents.json (read through fetch, ticket 3.23).
- A name with a joining mark (/ + , ; & and with plus) is a combination. A
  combination matches nothing, and neither does a trial that has one among its
  names.
- Names that point to two medicines match nothing. A log line names both.
- moonlight/trial_names.json is a hand list:
  {"<trial name>": {"id": "CHEMBL...", "source": "...", "date": "..."}}.
  Its names are compared the same way. Ticket T9 adds its checks.

No HTTP calls here: the drug records are handed in.
"""

import json
import logging
import pathlib
import re
from typing import Dict, Iterable, List, Optional, Set, Union

from moonlight import fetch

_log = logging.getLogger(__name__)

TRIAL_NAMES_FILE = pathlib.Path(__file__).resolve().parent / "trial_names.json"
_TRIAL_NAMES: Optional[Dict[str, dict]] = None

CHEMBL = "ChEMBL"
COMPONENT_OF = " component of "

_UNIT = r"(?:mg|mcg|µg|μg|ug|g|kg|ml|l|iu|units?|mmol|nmol|meq|%)"
_PER = r"(?:kg|m2|m²|ml|l|day|d|dose|h|hr|hours?|weeks?|wk)"
_DOSE = re.compile(rf"(?<![a-z0-9])\d+(?:[.,]\d+)?\s*{_UNIT}(?:\s*/\s*{_PER})?(?![a-z0-9])")
_JOIN = re.compile(r"[/+,;&]|\b(?:and|with|plus)\b")
_SPACES = re.compile(r"\s+")
_DRUG_TAG = re.compile(r"\(\s*drug\s*\)", re.IGNORECASE)
_BRACKETS = re.compile(r"\(([^)]*)\)")


def _read_trial_names(path: pathlib.Path) -> Dict[str, dict]:
    found = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(found, dict):
        raise ValueError("trial_names.json must hold an object.")
    for name, row in found.items():
        if not isinstance(row, dict) or not isinstance(row.get("id"), str) or not row["id"].strip():
            raise ValueError(f"A trial name row needs an id: {name!r}")
    return found


def _trial_names() -> Dict[str, dict]:
    """The one place the hand list is read. Tests replace this."""
    global _TRIAL_NAMES
    if _TRIAL_NAMES is None:
        _TRIAL_NAMES = _read_trial_names(TRIAL_NAMES_FILE)
    return _TRIAL_NAMES


def _clean(name: str) -> str:
    """Small letters, no amounts with units, single spaces."""
    text = _DOSE.sub(" ", name.casefold())
    return _SPACES.sub(" ", text).strip()


def names_to_try(name: str) -> List[str]:
    """One trial string, as the names to look up.

    "(drug)" is dropped. Text in brackets is its own name, and so is the
    text outside the brackets. "Erlotinib (Tarceva)" gives "Erlotinib" and
    "Tarceva". "Fenofibrate (drug)" gives "Fenofibrate".
    """
    without_drug_tag = _DRUG_TAG.sub(" ", name)
    insides = _BRACKETS.findall(without_drug_tag)
    outside = _BRACKETS.sub(" ", without_drug_tag)
    found = []
    for part in [outside, *insides]:
        part = " ".join(part.split())
        if part:
            found.append(part)
    return found


def is_combination(name: str) -> bool:
    return bool(_JOIN.search(_clean(name)))


def _family(drug: dict) -> str:
    parent = fetch._parent_of({"id": drug["id"], "parentMolecule": drug.get("parentMolecule")})
    return parent["id"] if parent else drug["id"]


def _labels(drug: dict) -> List[str]:
    labels = [drug.get("name") or ""]
    for field in ("synonyms", "tradeNames"):
        labels += [row["label"] for row in drug.get(field) or [] if row.get("source") == CHEMBL]
    return labels


def _index(drugs: Iterable[dict]):
    """name -> medicines it names, and record id -> its medicine."""
    names: Dict[str, Set[str]] = {}
    families: Dict[str, str] = {}
    for drug in drugs:
        family = _family(drug)
        records = [drug] + list(drug.get("childMolecules") or [])
        for record in records:
            families[record["id"]] = family
            for label in _labels(record):
                key = _clean(label)
                if not key or is_combination(label) or COMPONENT_OF in f" {key} ":
                    continue
                names.setdefault(key, set()).add(family)
    return names, families


def match(names: Union[str, Iterable[str]], drugs: Iterable[dict]) -> Optional[str]:
    """The one medicine (ChEMBL id of the medicine, not a salt form) that the
    trial's names mean, or None."""
    if isinstance(names, str):
        names = [names]
    raw = [name for name in names if name and str(name).strip()]
    given = []
    for name in raw:
        given.extend(names_to_try(name))
    combos = [name for name in given if is_combination(name)]
    if combos:
        _log.warning("Trial names %r hold a combination %r: no match.", given, combos)
        return None
    index, families = _index(drugs)
    hand = {_clean(name): row["id"] for name, row in _trial_names().items()}
    found: Set[str] = set()
    for name in given:
        key = _clean(name)
        found |= index.get(key, set())
        if key in hand:
            hand_id = hand[key]
            salt = fetch._salt_parents().get(hand_id)
            found.add(families.get(hand_id) or (salt["parent"] if salt else hand_id))
    if len(found) == 1:
        return found.pop()
    if found:
        _log.warning("Trial names %r point to two or more medicines %s: no match.",
                     given, ", ".join(sorted(found)))
    return None
