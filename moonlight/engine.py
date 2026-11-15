"""The engine: join fetch and filter into one step.

Give it a disease and a list of targets. It fetches the paths for the
targets, up to AT_ONCE of them at the same time, and hands them all to the
sorting tray in filter.py. The paths are put back in the order the targets
were given, so the answer is the same as fetching one after another.
find_clues does not rank. find_ranked_clues then puts the shown groups in
Kashish's order using rank.py, and only counts the groups that are left out.

sort_into_tabs makes the three tabs of the page (ticket 5.3): Approved,
In trials and New clues. It joins the medicines the tray found to be
already approved with Open Targets' own list for the disease.

preload(disease_ids) fills the saved results for a list of diseases ahead
of time. From a terminal:

    python -m moonlight.engine MONDO_0015924 EFO_0000685
"""

import sys
import threading
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Tuple

from moonlight import fetch
from moonlight.fetch import fetch_disease, fetch_paths, fetch_targets
from moonlight.fetch import Listed
from moonlight.filter import (
    ALREADY_APPROVED,
    BEING_STUDIED,
    GROUPS,
    NEW_CLUE,
    NOT_APPROVED,
    SHOWN_GROUPS,
    UNCLEAR_LINK,
    sort_paths,
)
from moonlight.rank import Clue, rank_clues
from moonlight.records import Disease, Medicine, Path, Target

AT_ONCE = 5  # the most proteins fetched at the same time
PRELOAD_TARGETS = 25  # the same number of proteins cli.py looks at


@dataclass(frozen=True)
class RankedClues:
    """What may be shown, in ranked order, and how many were left out."""

    new_clues: List[Clue]  # one per medicine, ranked
    being_studied: List[Clue]  # one per medicine, ranked
    left_out: Dict[str, int]  # group -> number of medicines. Counts only.


@dataclass(frozen=True)
class ApprovedMedicine:
    """One medicine already approved for the disease. It is not a clue.

    It has no rank and is never explained. clue is only used as a holder
    for its paths through the proteins that were looked at.
    """

    id: str  # the id shared by the medicine and its tablet forms
    name: str
    forms: Tuple[str, ...]  # the names of its forms, the parent first
    clue: Optional[Clue]  # None if it acts on none of the proteins looked at
    listed_sources: Tuple[str, ...]  # report links from the disease's own list

    @property
    def sources(self) -> Tuple[str, ...]:
        """Its report links: the ones on its paths first, then the list's."""
        found: List[str] = []
        for path in self.clue.paths if self.clue else ():
            found.extend(source for source in path.sources if source not in found)
        found.extend(source for source in self.listed_sources if source not in found)
        return tuple(found)

    @property
    def reports(self) -> int:
        """Counted the way a clue's reports are, if it has paths. If it has
        none, the number of report links on the disease's own list."""
        return self.clue.reports if self.clue else len(self.listed_sources)


@dataclass(frozen=True)
class Tabs:
    """The three tabs of the page, and how many medicines were left out."""

    approved: List[ApprovedMedicine]  # A to Z by name. No rank.
    being_studied: List[Clue]  # one per medicine, ranked
    new_clues: List[Clue]  # one per medicine, ranked
    left_out: Dict[str, int]  # not_approved and unclear_link. Counts only.


def find_clues(disease: Disease, targets: Iterable[Target]) -> Dict[str, List[Path]]:
    """Paths for every target, sorted into Kashish's groups.

    Every group is in the answer, even when empty. Only the groups in
    filter.SHOWN_GROUPS may be shown.
    """
    paths: List[Path] = []
    for found in _fetch_all(disease, list(targets)):
        paths.extend(found)
    return sort_paths(paths)


def _fetch_all(disease: Disease, targets: List[Target]) -> List[List[Path]]:
    """fetch_paths for every target, AT_ONCE at a time, answers in target order.

    Like swimmers in five lanes. Each swimmer dives in only after the one
    before has dived in, so they always start in the order given. They swim
    at the same time, and the results are written down by lane number, not
    by who touched the wall first.
    """
    if not targets:
        return []
    # go[n] is set when target n may start. The first may start at once.
    go = [threading.Event() for _ in range(len(targets) + 1)]
    go[0].set()

    def one(number: int) -> List[Path]:
        go[number].wait()
        fetch.started(go[number + 1].set)  # the next starts when this one has begun
        try:
            return fetch_paths(disease, targets[number])
        finally:
            fetch.started(None)
            go[number + 1].set()  # also if it never asked, or went wrong

    with ThreadPoolExecutor(max_workers=AT_ONCE) as pool:
        waiting = [pool.submit(one, number) for number in range(len(targets))]
        try:
            return [answer.result() for answer in waiting]
        except BaseException:
            for answer in waiting:
                answer.cancel()  # do not start the ones still in the queue
            raise


def find_ranked_clues(disease: Disease, targets: Iterable[Target]) -> RankedClues:
    """The shown groups as ranked Clues, and the left-out groups as counts.

    A medicine that acts on two proteins is one Clue, and one in a count.
    No medicine from a left-out group is named in the answer.
    """
    tray = find_clues(disease, targets)
    left_out = {
        # A medicine that acts on two proteins is still one medicine.
        group: len({path.medicine.name for path in tray[group]})
        for group in GROUPS
        if group not in SHOWN_GROUPS
    }
    return RankedClues(
        new_clues=rank_clues(tray[NEW_CLUE]),
        being_studied=rank_clues(tray[BEING_STUDIED]),
        left_out=left_out,
    )


def _family_id(medicine: Medicine) -> str:
    """The id shared by a medicine and its tablet forms (as in rank.py)."""
    first = medicine.forms[0]
    return first.parent_id or first.id


def sort_into_tabs(tray: Dict[str, List[Path]], listed: Iterable[Listed]) -> Tabs:
    """The tray from find_clues and the disease's own list -> the three tabs.

    Approved has two sources, joined with no medicine twice:
      1. the tray's already_approved group, found through the proteins;
      2. listed: Open Targets' own list of medicines approved for the disease.
    A medicine found only in the list has no paths.

    A medicine and its forms are one item, and the item takes the strongest
    stage of its forms. So if the list says a medicine is approved for the
    disease, every path of that medicine belongs to Approved, whichever
    group the tray put it in. It is then not a clue, and not counted as
    left out.

    Withdrawn comes first (ticket 2.11). If any path says the medicine or
    one of its forms was withdrawn, the medicine is withdrawn in every
    source: it is in no tab, whatever the list says, and it is counted in
    not_approved. A list with no withdrawn note never wins over a path
    that says "withdrawn". A missing note alone is still not guessed.
    """
    withdrawn_ids = {
        _family_id(path.medicine)
        for paths in tray.values()
        for path in paths
        if path.medicine.withdrawn is True
    }
    listed_by_id = {entry.id: entry for entry in listed if entry.id not in withdrawn_ids}

    approved_paths: List[Path] = []
    others: Dict[str, List[Path]] = {group: [] for group in GROUPS if group != ALREADY_APPROVED}
    for group, paths in tray.items():
        for path in paths:
            if _family_id(path.medicine) in withdrawn_ids:
                others[NOT_APPROVED].append(path)  # counted, never named
            elif group == ALREADY_APPROVED or _family_id(path.medicine) in listed_by_id:
                approved_paths.append(path)
            else:
                others[group].append(path)

    approved: List[ApprovedMedicine] = []
    seen = set()
    for clue in rank_clues(approved_paths):  # only to join each medicine's paths
        family_id = _family_id(clue.medicine)
        seen.add(family_id)
        entry = listed_by_id.get(family_id)
        forms: Dict[str, str] = {}  # form id -> name, each form once
        for path in clue.paths:
            for form in path.medicine.forms:
                forms.setdefault(form.id, form.name)
        for form_id, name in entry.forms if entry else ():
            forms.setdefault(form_id, name)
        approved.append(
            ApprovedMedicine(
                id=family_id,
                name=clue.medicine.name,
                forms=_parent_first(family_id, forms),
                clue=clue,
                listed_sources=entry.sources if entry else (),
            )
        )
    for entry in listed_by_id.values():
        if entry.id not in seen:
            approved.append(
                ApprovedMedicine(
                    id=entry.id,
                    name=entry.name,
                    forms=_parent_first(entry.id, dict(entry.forms)),
                    clue=None,
                    listed_sources=entry.sources,
                )
            )
    # A to Z, ignoring capitals. The last two only make the order the same
    # every time.
    approved.sort(key=lambda medicine: (medicine.name.casefold(), medicine.name, medicine.id))

    return Tabs(
        approved=approved,
        being_studied=rank_clues(others[BEING_STUDIED]),
        new_clues=rank_clues(others[NEW_CLUE]),
        left_out={
            # A medicine that acts on two proteins is still one medicine.
            group: len({path.medicine.name for path in others[group]})
            for group in (NOT_APPROVED, UNCLEAR_LINK)
        },
    )


def _parent_first(family_id: str, forms: Dict[str, str]) -> Tuple[str, ...]:
    """The form names in the order they were met, but the parent first."""
    ids = sorted(forms, key=lambda form_id: form_id != family_id)  # sorted keeps the rest in order
    return tuple(forms[form_id] for form_id in ids)


def preload(disease_ids: Iterable[str], top_targets: int = PRELOAD_TARGETS) -> List[str]:
    """Fill the saved results for these disease ids. -> the ids that were loaded.

    For each disease it asks for the disease record, its top proteins and
    the medicines for each protein: the questions a search for that disease
    asks. An id Open Targets does not know is skipped. Explanations are not
    made here.
    """
    loaded = []
    for disease_id in disease_ids:
        disease = fetch_disease(disease_id)
        if disease is None:
            continue
        find_clues(disease, fetch_targets(disease, top_targets))
        loaded.append(disease.id)
    return loaded


def main(argv: Optional[List[str]] = None) -> int:
    wanted = sys.argv[1:] if argv is None else argv
    if not wanted:
        print("Give one or more disease ids, like: python -m moonlight.engine MONDO_0015924")
        return 2
    loaded = preload(wanted)
    for disease_id in wanted:
        print(f"{disease_id}: {'saved' if disease_id in loaded else 'not known to Open Targets'}")
    return 0 if len(loaded) == len(wanted) else 1


if __name__ == "__main__":
    sys.exit(main())
