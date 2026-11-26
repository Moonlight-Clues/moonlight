"""Read one ClinicalTrials.gov trial that was already saved.

Like reading a race card someone else went and fetched. This file never
goes to the network. It only looks at the card it is handed.

    read_trial(study, medicine) -> Trial or None

None means the card is not an interventional trial. An observational
record and an expanded-access record are left out.

A Trial is frozen. It holds the registry's NCT number, a status word,
an end line, the phase tokens as the registry sent them, and the role
of the one named medicine.
"""

from dataclasses import dataclass
from typing import Optional, Tuple

# overallStatus -> the words on the card. A value that is not here is
# "Status unknown". A missing status is "Status not recorded".
STATUS_WORDS = {
    "RECRUITING": "Recruiting",
    "NOT_YET_RECRUITING": "Not yet recruiting",
    "ACTIVE_NOT_RECRUITING": "Running, not recruiting",
    "ENROLLING_BY_INVITATION": "Invitation only",
    "COMPLETED": "Finished",
    "TERMINATED": "Stopped early",
    "SUSPENDED": "Paused",
    "WITHDRAWN": "Withdrawn before starting",
    "UNKNOWN": "Status unknown",
}

# Arm-group types, from the registry's own enum. A comparison group is
# one whose type says COMPARATOR. NO_INTERVENTION and OTHER are neither
# experimental nor comparison, so they fall under "anything else".
EXPERIMENTAL = frozenset({"EXPERIMENTAL"})
COMPARISON = frozenset({
    "ACTIVE_COMPARATOR",
    "PLACEBO_COMPARATOR",
    "SHAM_COMPARATOR",
})

# The v2 DateType enum is ACTUAL and ESTIMATED (the enums list, 26 Nov
# 2026). The ticket's word for a date that has not happened is
# ANTICIPATED. A search for that word returns studies whose JSON type
# is ESTIMATED, so both words take the same end line.
EXPECTED_DATE = frozenset({"ESTIMATED", "ANTICIPATED"})

BEING_TESTED = "Being tested"
USED_FOR_COMPARISON = "Used for comparison"
ROLE_NOT_STATED = "Role not stated"
END_MISSING = "End date not recorded"
STATUS_MISSING = "Status not recorded"
STATUS_UNKNOWN = "Status unknown"


@dataclass(frozen=True)
class Trial:
    """One interventional trial, read for one medicine."""

    nct_id: str
    status: str
    end: str
    phases: Tuple[str, ...]
    role: str

    def __post_init__(self):
        object.__setattr__(self, "phases", tuple(self.phases))


def read_trial(study, medicine) -> Optional[Trial]:
    """The reading of one saved study for one medicine name.

    The name matches an intervention's own name, with case and surrounding
    spaces ignored. It does not match part of a name, and it does not match
    a medicine's other names. The role comes from the arm groups linked to
    that intervention.
    """
    protocol = _dict(study).get("protocolSection")
    protocol = _dict(protocol)
    design = _dict(protocol.get("designModule"))
    if design.get("studyType") != "INTERVENTIONAL":
        return None
    status = _dict(protocol.get("statusModule"))
    return Trial(
        nct_id=_nct_id(protocol),
        status=_status(status),
        end=_end(status),
        phases=_phases(design),
        role=_role(protocol, medicine),
    )


def _dict(value) -> dict:
    return value if isinstance(value, dict) else {}


def _list(value) -> list:
    return value if isinstance(value, list) else []


def _nct_id(protocol: dict) -> str:
    nct_id = _dict(protocol.get("identificationModule")).get("nctId")
    return nct_id if isinstance(nct_id, str) else ""


def _status(status: dict) -> str:
    if "overallStatus" not in status or status.get("overallStatus") is None:
        return STATUS_MISSING
    value = status.get("overallStatus")
    if not isinstance(value, str):
        return STATUS_UNKNOWN
    return STATUS_WORDS.get(value, STATUS_UNKNOWN)


def _end(status: dict) -> str:
    struct = status.get("completionDateStruct")
    if not isinstance(struct, dict):
        return END_MISSING
    year = _year(struct.get("date"))
    kind = struct.get("type")
    if year is None or not isinstance(kind, str):
        return END_MISSING
    if kind == "ACTUAL":
        return f"Ended {year}"
    if kind in EXPECTED_DATE:
        return f"Expected to end {year}"
    return END_MISSING


def _year(date) -> Optional[str]:
    """The first four digits of a partial date: "2011-12" and "2022-02-03"."""
    if isinstance(date, str) and len(date) >= 4 and date[:4].isdigit():
        return date[:4]
    return None


def _phases(design: dict) -> Tuple[str, ...]:
    """Phase tokens as sent, in the registry's order. Nothing is renamed."""
    return tuple(phase for phase in _list(design.get("phases")) if isinstance(phase, str))


def _role(protocol: dict, medicine) -> str:
    """Experimental groups only, comparison groups only, or not stated.

    No arm groups, a medicine that is not on the trial, or a medicine in
    both kinds of group: "Role not stated".
    """
    module = _dict(protocol.get("armsInterventionsModule"))
    label_type = {}
    for group in _list(module.get("armGroups")):
        if not isinstance(group, dict) or not isinstance(group.get("label"), str):
            continue
        label_type[group["label"]] = group.get("type")
    kinds = set()
    wanted = _name(medicine)
    if not wanted:
        return ROLE_NOT_STATED
    for item in _list(module.get("interventions")):
        if not isinstance(item, dict) or _name(item.get("name")) != wanted:
            continue
        for label in _list(item.get("armGroupLabels")):
            kind = label_type.get(label)
            if isinstance(kind, str):
                kinds.add(kind)
    if kinds and kinds <= EXPERIMENTAL:
        return BEING_TESTED
    if kinds and kinds <= COMPARISON:
        return USED_FOR_COMPARISON
    return ROLE_NOT_STATED


def _name(value) -> str:
    if not isinstance(value, str):
        return ""
    return value.strip().casefold()
