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

Ticket 2.13, honest proof on Approved cards. An Approved card whose only
approval receipt is the link to Japan's general list gets the line
JAPAN_LINE (ApprovedMedicine.proof_note). looks_wrong(disease_id) reads the
corrections list in moonlight/corrections.json: the medicines a doctor
confirmed look wrong for that disease. Their cards get WRONG_WARNING.

Ticket 2.14, a box for narrower diseases. The main Approved list holds
only medicines approved on the disease's own entry. One approved only on a
child entry goes in Tabs.narrower, the folded box "Approved for a narrower
disease". ApprovedMedicine.source_record picks the link a card shows as
"Source record": an approval receipt first.

preload(disease_ids) fills the saved results for a list of diseases ahead
of time. From a terminal:

    python -m moonlight.engine MONDO_0015924 EFO_0000685
"""

import datetime
import json
import pathlib
import sys
import threading
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from typing import Callable, Dict, Iterable, List, Optional, Set, Tuple, TypeVar

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

# Ticket 2.13, Kashish's decisions of 16 Nov.
# Every report from Japan's medicines agency carries this one link, to its
# general list of approved medicines, not to a record about the medicine
# and the disease. Read from the live API on 2026-11-16 and saved in
# fixtures/approval_proof/: all 52 of its reports there have this link and
# no report from anywhere else has it. Compared letter for letter.
JAPAN_LIST = (
    "https://www.pmda.go.jp/english/review-services/reviews/"
    "approved-information/drugs/0001.html"
)
# Kashish's words, exactly. Changing them needs her approval.
JAPAN_LINE = (
    "Approved in Japan, according to the database. Moonlight could not "
    "find the exact record for this disease."
)
WRONG_WARNING = "A doctor has told us this looks like a mistake in the database."
CORRECTION_NOTE = "A doctor confirmed this looks wrong."  # the note in every entry
CORRECTIONS_FILE = pathlib.Path(__file__).resolve().parent / "corrections.json"
CORRECTION_KEYS = {"medicine_id", "disease_id", "date", "note"}


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
    # Ticket 2.13. The approval receipts from the lists naming it: the links
    # of reports whose own stage is approval. Trial links are not here, and
    # neither are its paths' links: those are about the medicine and the
    # protein, for any disease.
    approval_sources: Tuple[str, ...] = ()

    @property
    def proof_note(self) -> Optional[str]:
        """JAPAN_LINE if Japan's general list is its only approval receipt.

        None if it has an approval receipt with its own link. Also None if
        it has no approval receipt at all: that card is not decided, and is
        left as it is.
        """
        if self.approval_sources and all(link == JAPAN_LIST for link in self.approval_sources):
            return JAPAN_LINE
        return None

    @property
    def source_record(self) -> Optional[str]:
        """The one link the card shows as "Source record" (ticket 2.14).

        Like looking for a receipt in three drawers, in this order:
          1. an exact approval receipt: the first of approval_sources that
             is not Japan's general list;
          2. Japan's general list, if that is its only kind of receipt;
          3. the link shown before this ticket: the first of sources.
        Only an https link is ever chosen. None if it has no such link.
        """
        receipts = [link for link in self.approval_sources if link.startswith("https://")]
        for link in receipts:
            if link != JAPAN_LIST:
                return link
        for link in receipts[:1] + list(self.sources):
            if link.startswith("https://"):
                return link
        return None

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

    # Approved on the disease's own entry, and nothing else. A to Z. No rank.
    approved: List[ApprovedMedicine]
    being_studied: List[Clue]  # one per medicine, ranked
    new_clues: List[Clue]  # one per medicine, ranked
    left_out: Dict[str, int]  # not_approved and unclear_link. Counts only.
    # Ticket 2.12. Approved only on a parent entry: the folded box
    # "Approved for a wider group". A to Z. No rank. Not counted on the tab.
    wider_group: List[ApprovedMedicine] = field(default_factory=list)
    # Ticket 2.14. Approved only on a child entry, or on a child and a
    # parent: the folded box "Approved for a narrower disease". A to Z. No rank.
    narrower: List[ApprovedMedicine] = field(default_factory=list)


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
      - Approved only on a child entry, or on a child and a parent: in
        narrower, its own folded box (ticket 2.14), with the child label.
        The child wins. The database sometimes files one disease under
        another, so these are kept out of the main list.
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

    narrower: List[ApprovedMedicine] = []
    wider_group: List[ApprovedMedicine] = []
    for family_id, (children, parents, entries) in nearby.items():
        paths = nearby_paths.get(family_id)
        clue = rank_clues(paths)[0] if paths else None  # only to join its paths
        if children:  # the child wins over the parent
            narrower.append(_approved_medicine(family_id, clue, entries, child_label(children)))
        else:
            wider_group.append(
                _approved_medicine(family_id, clue, entries, parent_label(parents)))

    # A to Z, ignoring capitals. The last two only make the order the same
    # every time.
    def a_to_z(medicine: ApprovedMedicine):
        return (medicine.name.casefold(), medicine.name, medicine.id)

    approved.sort(key=a_to_z)
    narrower.sort(key=a_to_z)
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
        narrower=narrower,
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
    approval_sources: List[str] = []
    for entry in entries:
        for form_id, name in entry.forms:
            forms.setdefault(form_id, name)
        sources.extend(source for source in entry.sources if source not in sources)
        approval_sources.extend(
            source for source in entry.approval_sources if source not in approval_sources)
    return ApprovedMedicine(
        id=family_id,
        name=clue.medicine.name if clue else entries[0].name,
        forms=_parent_first(family_id, forms),
        clue=clue,
        listed_sources=tuple(sources),
        label=label,
        approval_sources=tuple(approval_sources),
    )


def _read_corrections() -> list:
    """The one place the corrections file is read. Tests replace this."""
    return json.loads(CORRECTIONS_FILE.read_text(encoding="utf-8"))


def corrections() -> Set[Tuple[str, str]]:
    """The corrections list as (medicine id, disease id) pairs.

    Each entry holds exactly four things: the medicine's id, the disease's
    id, the date (like "2026-11-16") and the note CORRECTION_NOTE. No doctor
    is ever named, so an entry holding anything else is refused. An entry
    that is not written this way raises ValueError: a warning is never
    dropped quietly.
    """
    entries = _read_corrections()
    if not isinstance(entries, list):
        raise ValueError("corrections.json must hold a list.")
    pairs = set()
    for entry in entries:
        if not isinstance(entry, dict) or set(entry) != CORRECTION_KEYS:
            raise ValueError(f"A correction must hold exactly {sorted(CORRECTION_KEYS)}: {entry!r}")
        medicine_id, disease_id, date = entry["medicine_id"], entry["disease_id"], entry["date"]
        if not all(isinstance(value, str) and value for value in (medicine_id, disease_id, date)):
            raise ValueError(f"A correction needs a medicine id, a disease id and a date: {entry!r}")
        datetime.date.fromisoformat(date)  # ValueError if it is not a real date
        if entry["note"] != CORRECTION_NOTE:
            raise ValueError(f"A correction's note must be exactly {CORRECTION_NOTE!r}: {entry!r}")
        pairs.add((medicine_id, disease_id))
    return pairs


def looks_wrong(disease_id: str) -> Set[str]:
    """The ids of the medicines on the corrections list for this disease.

    Their Approved cards show WRONG_WARNING. The same medicine under
    another disease is not in the answer.
    """
    return {medicine_id for medicine_id, listed_for in corrections() if listed_for == disease_id}


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
