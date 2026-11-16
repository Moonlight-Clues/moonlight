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

fetch_neighbours(disease) asks for the medicine lists of the disease's
direct parents and direct children (ticket 2.12), side by side.
sort_into_tabs gives a medicine found only there a label saying where the
database lists it.

preload(disease_ids) fills the saved results for a list of diseases ahead
of time. From a terminal:

    python -m moonlight.engine MONDO_0015924 EFO_0000685
"""

import sys
import threading
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from typing import Callable, Dict, Iterable, List, Optional, Tuple, TypeVar

from moonlight import fetch
from moonlight.fetch import fetch_approved, fetch_disease, fetch_family, fetch_paths
from moonlight.fetch import fetch_targets, fetch_withdrawn
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

AT_ONCE = 5  # the most proteins, or extra disease entries, fetched at the same time
PRELOAD_TARGETS = 25  # the same number of proteins cli.py looks at


@dataclass(frozen=True)
class RankedClues:
    """What may be shown, in ranked order, and how many were left out."""

    new_clues: List[Clue]  # one per medicine, ranked
    being_studied: List[Clue]  # one per medicine, ranked
    left_out: Dict[str, int]  # group -> number of medicines. Counts only.
    # Ticket 2.12. How many medicines are not new clues because they are
    # approved on a parent or child entry. Only counted if neighbours are given.
    moved_to_approved: int = 0


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
    # Ticket 2.12. None if it is approved on the disease's own entry. If it
    # was found only on a child or parent entry, the sentence saying which.
    label: Optional[str] = None

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
    # Ticket 2.12. Approved only on a parent entry: the folded box
    # "Approved for a wider group". A to Z. No rank. Not counted on the tab.
    wider_group: List[ApprovedMedicine] = field(default_factory=list)


PARENT = "parent"  # one sheet up: a wider group the database puts the disease in
CHILD = "child"  # one sheet down: a disease the database lists under this one


@dataclass(frozen=True)
class Neighbour:
    """One direct parent or direct child of the disease, with its own list."""

    role: str  # PARENT or CHILD
    disease: Disease
    approved: Tuple[Listed, ...]  # approved on that entry, withdrawn ones left out
    withdrawn: Tuple[Listed, ...]  # on that entry's list and withdrawn in any country


def _joined(names: List[str]) -> str:
    """["a"] -> "a", ["a", "b"] -> "a and b", three -> "a, b and c"."""
    if len(names) == 1:
        return names[0]
    return ", ".join(names[:-1]) + " and " + names[-1]


def child_label(names: List[str]) -> str:
    """Kashish's words, 16 Nov. They say only what the database does."""
    return f"Approved for {_joined(names)}, which the database lists under this disease."


def parent_label(names: List[str]) -> str:
    """Kashish's words, 16 Nov. With two or more names the grammar is for many."""
    group = "a wider group" if len(names) == 1 else "wider groups"
    return f"Approved for {_joined(names)}, {group} the database puts this disease in."


def find_clues(disease: Disease, targets: Iterable[Target]) -> Dict[str, List[Path]]:
    """Paths for every target, sorted into Kashish's groups.

    Every group is in the answer, even when empty. Only the groups in
    filter.SHOWN_GROUPS may be shown.
    """
    paths: List[Path] = []
    for found in _fetch_all(disease, list(targets)):
        paths.extend(found)
    return sort_paths(paths)


Answer = TypeVar("Answer")


def _in_lanes(count: int, work: Callable[[int], Answer]) -> List[Answer]:
    """work(0) ... work(count - 1), AT_ONCE at a time, answers by lane number.

    Like swimmers in five lanes. Each swimmer dives in only after the one
    before has dived in, so they always start in the order given. They swim
    at the same time, and the results are written down by lane number, not
    by who touched the wall first.
    """
    if not count:
        return []
    # go[n] is set when number n may start. The first may start at once.
    go = [threading.Event() for _ in range(count + 1)]
    go[0].set()

    def one(number: int) -> Answer:
        go[number].wait()
        fetch.started(go[number + 1].set)  # the next starts when this one has begun
        try:
            return work(number)
        finally:
            fetch.started(None)
            go[number + 1].set()  # also if it never asked, or went wrong

    with ThreadPoolExecutor(max_workers=AT_ONCE) as pool:
        waiting = [pool.submit(one, number) for number in range(count)]
        try:
            return [answer.result() for answer in waiting]
        except BaseException:
            for answer in waiting:
                answer.cancel()  # do not start the ones still in the queue
            raise


def _fetch_all(disease: Disease, targets: List[Target]) -> List[List[Path]]:
    """fetch_paths for every target, side by side, answers in target order."""
    return _in_lanes(len(targets), lambda number: fetch_paths(disease, targets[number]))


def fetch_neighbours(disease: Disease) -> List[Neighbour]:
    """The medicine list of every direct parent and direct child (ticket 2.12).

    One step up and one step down only. Parents first, then children, each
    in Open Targets' order. The lists are asked for side by side, by lane
    number, with the same question as the disease's own list. So they are
    asked twice and saved for a day like every other answer.
    """
    family = fetch_family(disease)
    entries = [(PARENT, entry) for entry in family.parents]
    entries += [(CHILD, entry) for entry in family.children]

    def one(number: int) -> Neighbour:
        role, entry = entries[number]
        # The second question is the same one, answered from the saved results.
        return Neighbour(role, entry, tuple(fetch_approved(entry)), tuple(fetch_withdrawn(entry)))

    return _in_lanes(len(entries), one)


def find_ranked_clues(
    disease: Disease, targets: Iterable[Target], neighbours: Iterable[Neighbour] = ()
) -> RankedClues:
    """The shown groups as ranked Clues, and the left-out groups as counts.

    A medicine that acts on two proteins is one Clue, and one in a count.
    No medicine from a left-out group is named in the answer.

    With neighbours (ticket 2.12) the same rule as the page is followed:
      - a medicine approved on a parent or child entry is never a new clue.
        It is only counted, in moved_to_approved;
      - a medicine in trials for this exact disease stays as it is;
      - a medicine a parent's or child's list marks as withdrawn is shown
        nowhere, and is counted in not_approved.
    """
    tray = find_clues(disease, targets)
    neighbours = list(neighbours)
    withdrawn_ids = {entry.id for neighbour in neighbours for entry in neighbour.withdrawn}
    labelled_ids = {
        entry.id for neighbour in neighbours for entry in neighbour.approved
    } - withdrawn_ids

    kept: Dict[str, List[Path]] = {group: [] for group in GROUPS}
    moved = set()  # names. A medicine that acts on two proteins is still one.
    for group, paths in tray.items():
        for path in paths:
            family_id = _family_id(path.medicine)
            if group in SHOWN_GROUPS and family_id in withdrawn_ids:
                kept[NOT_APPROVED].append(path)  # counted, never named
            elif group == NEW_CLUE and family_id in labelled_ids:
                moved.add(path.medicine.name)
            else:
                kept[group].append(path)
    left_out = {
        # A medicine that acts on two proteins is still one medicine.
        group: len({path.medicine.name for path in kept[group]})
        for group in GROUPS
        if group not in SHOWN_GROUPS
    }
    return RankedClues(
        new_clues=rank_clues(kept[NEW_CLUE]),
        being_studied=rank_clues(kept[BEING_STUDIED]),
        left_out=left_out,
        moved_to_approved=len(moved),
    )


def _family_id(medicine: Medicine) -> str:
    """The id shared by a medicine and its tablet forms (as in rank.py)."""
    first = medicine.forms[0]
    return first.parent_id or first.id


def sort_into_tabs(
    tray: Dict[str, List[Path]],
    listed: Iterable[Listed],
    withdrawn_listed: Iterable[Listed] = (),
    neighbours: Iterable[Neighbour] = (),
) -> Tabs:
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

    withdrawn_listed is the other direction: the families the disease's own
    list marks as withdrawn (fetch.fetch_withdrawn). They are withdrawn in
    every source too, even when a path has no note. One that is approved
    for the disease is counted in not_approved even if it has no path.

    neighbours (ticket 2.12, Kashish's decisions of 16 Nov) are the direct
    parents and direct children with their own lists (fetch_neighbours).
      - Approved on the disease's own entry: as before, no label.
      - Approved only on a child entry, or on a child and a parent: in the
        Approved list with the child label. The child wins.
      - Approved only on a parent entry: in wider_group, the folded box,
        with the parent label.
      - Two children, or two parents: both are named in the one label.
      - A medicine with a label is never a new clue. Its paths go with it.
      - What the data says about this exact disease comes first: a medicine
        in trials for the disease stays in being_studied exactly as before,
        and is also shown in Approved or the box with its label. One with
        an unclear link to the disease stays counted in unclear_link too.
      - Withdrawn on a parent's or child's list is withdrawn in every
        source, and counted in not_approved if it was approved there.
    """
    withdrawn_listed = list(withdrawn_listed)
    neighbours = list(neighbours)
    withdrawn_nearby = [entry for neighbour in neighbours for entry in neighbour.withdrawn]
    withdrawn_ids = {
        _family_id(path.medicine)
        for paths in tray.values()
        for path in paths
        if path.medicine.withdrawn is True
    } | {entry.id for entry in withdrawn_listed} | {entry.id for entry in withdrawn_nearby}
    listed_by_id = {entry.id: entry for entry in listed if entry.id not in withdrawn_ids}

    # Approved for this exact disease, from either source. These get no label.
    own_ids = set(listed_by_id) | {
        _family_id(path.medicine) for path in tray.get(ALREADY_APPROVED, [])
    }
    # family id -> where else it is approved: [child names, parent names, entries]
    nearby: Dict[str, Tuple[List[str], List[str], List[Listed]]] = {}
    for neighbour in neighbours:
        for entry in neighbour.approved:
            if entry.id in withdrawn_ids or entry.id in own_ids:
                continue
            found = nearby.setdefault(entry.id, ([], [], []))
            names = found[0] if neighbour.role == CHILD else found[1]
            if neighbour.disease.name not in names:
                names.append(neighbour.disease.name)
            found[2].append(entry)

    approved_paths: List[Path] = []
    nearby_paths: Dict[str, List[Path]] = {}
    others: Dict[str, List[Path]] = {group: [] for group in GROUPS if group != ALREADY_APPROVED}
    for group, paths in tray.items():
        for path in paths:
            family_id = _family_id(path.medicine)
            if family_id in withdrawn_ids:
                others[NOT_APPROVED].append(path)  # counted, never named
            elif group == ALREADY_APPROVED or family_id in listed_by_id:
                approved_paths.append(path)
            elif family_id in nearby:
                nearby_paths.setdefault(family_id, []).append(path)
                if group in (BEING_STUDIED, UNCLEAR_LINK):
                    # What the data says about this exact disease comes
                    # first: it stays in In trials, or stays counted as an
                    # unclear link, exactly as before.
                    others[group].append(path)
            else:
                others[group].append(path)

    approved: List[ApprovedMedicine] = []
    seen = set()
    for clue in rank_clues(approved_paths):  # only to join each medicine's paths
        family_id = _family_id(clue.medicine)
        seen.add(family_id)
        entry = listed_by_id.get(family_id)
        approved.append(_approved_medicine(family_id, clue, [entry] if entry else []))
    for entry in listed_by_id.values():
        if entry.id not in seen:
            approved.append(_approved_medicine(entry.id, None, [entry]))

    wider_group: List[ApprovedMedicine] = []
    for family_id, (children, parents, entries) in nearby.items():
        paths = nearby_paths.get(family_id)
        clue = rank_clues(paths)[0] if paths else None  # only to join its paths
        if children:  # the child wins over the parent
            approved.append(_approved_medicine(family_id, clue, entries, child_label(children)))
        else:
            wider_group.append(
                _approved_medicine(family_id, clue, entries, parent_label(parents)))

    # A to Z, ignoring capitals. The last two only make the order the same
    # every time.
    def a_to_z(medicine: ApprovedMedicine):
        return (medicine.name.casefold(), medicine.name, medicine.id)

    approved.sort(key=a_to_z)
    wider_group.sort(key=a_to_z)

    return Tabs(
        approved=approved,
        being_studied=rank_clues(others[BEING_STUDIED]),
        new_clues=rank_clues(others[NEW_CLUE]),
        left_out={
            # A medicine that acts on two proteins is still one medicine.
            # So is one that has a path and is also on a withdrawn list.
            NOT_APPROVED: len(
                {path.medicine.name for path in others[NOT_APPROVED]}
                | {entry.name for entry in withdrawn_listed + withdrawn_nearby if entry.approved}
            ),
            UNCLEAR_LINK: len({path.medicine.name for path in others[UNCLEAR_LINK]}),
        },
        wider_group=wider_group,
    )


def _approved_medicine(
    family_id: str, clue: Optional[Clue], entries: List[Listed], label: Optional[str] = None
) -> ApprovedMedicine:
    """One item of the Approved tab, from its paths and the lists naming it.

    Named as its paths name it, or as the first list does if it has none.
    Its forms: the ones on its paths first, then the lists', each once.
    """
    forms: Dict[str, str] = {}  # form id -> name, each form once
    for path in clue.paths if clue else ():
        for form in path.medicine.forms:
            forms.setdefault(form.id, form.name)
    sources: List[str] = []
    for entry in entries:
        for form_id, name in entry.forms:
            forms.setdefault(form_id, name)
        sources.extend(source for source in entry.sources if source not in sources)
    return ApprovedMedicine(
        id=family_id,
        name=clue.medicine.name if clue else entries[0].name,
        forms=_parent_first(family_id, forms),
        clue=clue,
        listed_sources=tuple(sources),
        label=label,
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
