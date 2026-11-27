"""Ticket T5. The name matcher.

A trial names its medicine, sometimes with other names. match() gives the ONE
Open Targets medicine those names mean, or None. Exact matching only: no fuzzy
and no AI matching.

Kashish's rules (26 Nov 2026):
- Names used: each record's name, and its synonyms and trade names whose source
  is "ChEMBL", for the medicine and its salt (child) forms. Names from AACT are
  never used. Trade names "X component of Y" are never used.
- Before comparing, case and spaces are evened out, and amounts with units
  ("500 mg", "1.5 mg/kg", "0.5%", and a comma that only introduces one,
  ", 2.5 mg") are removed. That happens before the name is checked for a
  joining mark (ticket T5c).
- A form word (tablets, capsules, injection, oral solution) is dropped only
  when what is left exactly matches one known medicine (MAIN 5, ticket T5b).
- A name in brackets is an extra name. "Erlotinib (Tarceva)" is tried as
  "Erlotinib" and as "Tarceva". "(drug)" is dropped.
- The first name is the trial's main medicine name. A joining mark in it
  (/ + , ; & and with plus) means a combination, and the trial matches nothing.
- Later names are aliases. Commas and semicolons split them into pieces.
  A piece that matches nothing is ignored. A piece with "+" is still a
  combination, and the trial matches nothing.
- A "/" piece in an other-name is a list of aliases when every part is the
  same medicine as the main name, or an unknown brand name: letters only, no
  digits. ® and ™ are not digits. An unknown part with a digit, such as
  VX-445, is a different medicine, so the list is a combination (ticket T5d).
- Names that point to two medicines match nothing. A log line names both.
- A medicine and its salt forms are one medicine: Open Targets' parentMolecule,
  else moonlight/salt_parents.json (read through fetch, ticket 3.23).
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
# A comma is part of the dose only when a number and a unit follow it
# (", 2.5 mg"). A comma between two names is left for the joining check.
_DOSE = re.compile(
    rf",?\s*(?<![a-z0-9])\d+(?:[.,]\d+)?\s*{_UNIT}(?:\s*/\s*{_PER})?(?![a-z0-9])")
_JOIN = re.compile(r"[/+,;&]|\b(?:and|with|plus)\b")
_SPACES = re.compile(r"\s+")
_DRUG_TAG = re.compile(r"\(\s*drug\s*\)", re.IGNORECASE)
_BRACKETS = re.compile(r"\(([^)]*)\)")
_ALIAS_SPLIT = re.compile(r"[,;]")
# ticket T5b. Dropped only when the remainder matches exactly one medicine.
_FORM = re.compile(r"\b(?:oral solution|tablets?|capsules?|injection)\b")


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


def _alias_pieces(name: str) -> List[str]:
    """An other-name, split on commas and semicolons into aliases."""
    pieces = []
    for part in names_to_try(name):
        for bit in _ALIAS_SPLIT.split(part):
            bit = " ".join(bit.split())
            if bit:
                pieces.append(bit)
    return pieces


_OTHER_JOIN = re.compile(r"[+,;&]|\b(?:and|with|plus)\b")


_TRADEMARK = str.maketrans("", "", "®™")


def _brand_like(part: str) -> bool:
    """Letters only, no digits. Trademark marks are ignored."""
    text = "".join(part.translate(_TRADEMARK).split())
    return bool(text) and all(ch.isalpha() for ch in text)


def _slash_parts(piece: str) -> Optional[List[str]]:
    """Parts of an other-name that is only a '/' list, or None.

    '10 mg/kg' is a dose, already removed by _clean, so it is not this list.
    A '+' or another joining mark besides '/' means it is not this list.
    """
    cleaned = _clean(piece)
    if "/" not in cleaned or _OTHER_JOIN.search(cleaned):
        return None
    parts = [" ".join(bit.split()) for bit in piece.split("/")]
    parts = [bit for bit in parts if bit]
    if len(parts) < 2:
        return None
    return parts


def _lookup_bits(raw: List[str]) -> Optional[List[str]]:
    """Pieces to look up, or None when a hard combination needs no catalogue.

    A '/' list in an other-name is included as its parts. The main name's
    joining marks are not opened.
    """
    main_parts = names_to_try(raw[0])
    if any(is_combination(part) for part in main_parts):
        return None
    bits = list(main_parts)
    for alias in raw[1:]:
        for piece in _alias_pieces(alias):
            slash = _slash_parts(piece)
            if slash is not None:
                bits.extend(slash)
                continue
            if is_combination(piece):
                return None
            bits.append(piece)
    return bits


def _keys_of(part: str) -> List[str]:
    key = _clean(part)
    keys = [key] if key else []
    stripped = _SPACES.sub(" ", _FORM.sub(" ", key)).strip()
    if stripped and stripped != key:
        keys.append(stripped)
    return keys


def search_keys(names: Union[str, Iterable[str]]) -> List[str]:
    """Cleaned keys a caller can use to pick candidate medicines.

    The same pieces match() will look up, including a form word dropped from
    a name, and the parts of a '/' alias list. Empty when the main name is a
    combination, or an other-name has a joining mark other than that list.
    """
    if isinstance(names, str):
        names = [names]
    raw = [name for name in names if name and str(name).strip()]
    if not raw:
        return []
    bits = _lookup_bits(raw)
    if bits is None:
        return []
    keys = []
    for part in bits:
        keys.extend(_keys_of(part))
    return keys


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


def _ids_for_key(key: str, index: Dict[str, Set[str]], families: Dict[str, str],
                 hand: Dict[str, str]) -> Set[str]:
    found = set(index.get(key, ()))
    if key in hand:
        hand_id = hand[key]
        salt = fetch._salt_parents().get(hand_id)
        found.add(families.get(hand_id) or (salt["parent"] if salt else hand_id))
    return found


def _ids_for_piece(piece: str, index: Dict[str, Set[str]], families: Dict[str, str],
                   hand: Dict[str, str]) -> Set[str]:
    """Medicines this one piece names. A form word is used only when dropping
    it leaves exactly one medicine. An empty set means this piece names nothing."""
    key = _clean(piece)
    if not key:
        return set()
    found = _ids_for_key(key, index, families, hand)
    if found:
        return found
    stripped = _SPACES.sub(" ", _FORM.sub(" ", key)).strip()
    if not stripped or stripped == key:
        return set()
    dropped = _ids_for_key(stripped, index, families, hand)
    if len(dropped) == 1:
        return dropped
    return set()


def match(names: Union[str, Iterable[str]], drugs: Iterable[dict]) -> Optional[str]:
    """The one medicine (ChEMBL id of the medicine, not a salt form) that the
    trial's names mean, or None.

    The first name is the medicine's own name. The rest are its other names.
    """
    if isinstance(names, str):
        names = [names]
    raw = [name for name in names if name and str(name).strip()]
    if not raw:
        return None
    main_parts = names_to_try(raw[0])
    main_combos = [part for part in main_parts if is_combination(part)]
    if main_combos:
        _log.warning("Trial names %r hold a combination %r: no match.", raw, main_combos)
        return None
    index, families = _index(drugs)
    hand = {_clean(name): row["id"] for name, row in _trial_names().items()}
    found: Set[str] = set()
    for part in main_parts:
        found |= _ids_for_piece(part, index, families, hand)
    main_ids = set(found)
    for alias in raw[1:]:
        for piece in _alias_pieces(alias):
            slash = _slash_parts(piece)
            if slash is not None:
                for bit in slash:
                    ids = _ids_for_piece(bit, index, families, hand)
                    if not ids:
                        if _brand_like(bit):
                            continue
                        _log.warning("Trial names %r hold a combination %r: no match.",
                                     raw, [piece])
                        return None
                    if len(main_ids) != 1 or ids != main_ids:
                        _log.warning("Trial names %r hold a combination %r: no match.",
                                     raw, [piece])
                        return None
                continue
            if is_combination(piece):
                _log.warning("Trial names %r hold a combination %r: no match.", raw, [piece])
                return None
            found |= _ids_for_piece(piece, index, families, hand)
    if len(found) == 1:
        return found.pop()
    if found:
        _log.warning("Trial names %r point to two or more medicines %s: no match.",
                     raw, ", ".join(sorted(found)))
    return None
