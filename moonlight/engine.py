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
corrections list in moonlight/corrections.json: the medicines confirmed
to look wrong for that disease. Their cards get a red warning.

Ticket 2.14, a box for narrower diseases. The main Approved list holds
only medicines approved on the disease's own entry. One approved only on a
child entry goes in Tabs.narrower, the folded box "Approved for a narrower
disease". ApprovedMedicine.source_record picks the link a card shows as
"Source record": an approval receipt first.

Ticket 2.17, a quiet line on approvals with no regulator record. An
Approved card whose medicine has no approval report from a regulator
(fetch.REGULATOR_SOURCES) gets the line NO_REGULATOR_LINE, in the same
place as the Japan line (ApprovedMedicine.proof_note). The card stays
where it is. A medicine with no reports at all gets the line too. If it
has reports and none says where it comes from (answers saved before this
ticket), the card gets no line: not said is not the same as no.

Ticket 3.7, the opposite-way line. one_way_proteins(approved, wrong) reads
the main Approved list and says which proteins its medicines all turn the
same way. opposite_way(clue, one_way) then says on which of a clue's
proteins the card carries OPPOSITE_LINE. Nothing is moved or hidden.

Ticket 2.18, a second red warning, and clues left out by hand. A
corrections entry's note is one of two sentences (CORRECTION_NOTES).
warning_words(disease_id) says which red words each listed card shows: its
own entry's. pushes_wrong_way(disease_id) reads moonlight/left_out.json, a
list written by hand: for that disease those medicines are not shown in
New clues (leave_out), and wrong_way_line says how many. No code ever
writes to that file: only a hand check may remove a card.

Ticket 2.21, a box for more medicines in trials. sort_into_tabs is also
handed the disease's own list as records (fetch.fetch_listed_medicines).
A medicine on it that is in a trial for the disease and approved for
something else, by the same rule as In trials (filter.group_of), and is
nowhere else on the page, goes in Tabs.more_in_trials: the folded box
under the In trials list. keep_out(more, ids) takes out the medicines a
hand-written list names for this disease. Today's In trials list is not
touched.

Ticket 2.24, a box for new medicines in trials. A medicine on the disease's
own list that is in a trial for the disease and that no form we can see
says is approved for anything goes in Tabs.new_in_trials: a second folded
box, under the one from ticket 2.21. If the list cannot tell whether it is
approved for something (fetch.OnList.all_seen is False), it stays out of
both boxes. keep_out works for this box too.

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
from moonlight.fetch import Listed, OnList
from moonlight.filter import (
    ALREADY_APPROVED,
    BEING_STUDIED,
    GROUPS,
    NEW_CLUE,
    NOT_APPROVED,
    SHOWN_GROUPS,
    UNCLEAR_LINK,
    group_of,
    sort_paths,
)
from moonlight.rank import Clue, rank_clues
from moonlight.records import STAGE_ORDER, Disease, Medicine, Path, Target

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
# Ticket 2.17, Kashish's decision of 18 Nov. Her words, exactly. Changing
# them needs her approval.
NO_REGULATOR_LINE = (
    "The database lists this as approved, but gives no regulator record for it."
)
# Ticket 3.7, Kashish's words, exactly. Changing them needs her approval.
OPPOSITE_LINE = "Opposite way to the approved medicines for this disease."
WRONG_WARNING = "A doctor has told us this looks like a mistake in the database."
CORRECTION_NOTE = "A doctor confirmed this looks wrong."  # the first note
# Ticket 2.18, Kashish's words of 19 Nov, exactly. The second note an entry
# may carry. A card with this note shows these same words in red.
SECOND_NOTE = (
    "This looks like a mistake in the database. The official label is for "
    "a different disease."
)
# An entry's note is exactly one of these. Note -> the red words on the card.
RED_WORDS = {CORRECTION_NOTE: WRONG_WARNING, SECOND_NOTE: SECOND_NOTE}
CORRECTION_NOTES = tuple(RED_WORDS)
# Ticket 2.21, Kashish's words of 22 Nov, exactly. The label of the folded
# box under the In trials list. Changing them needs her approval.
MORE_IN_TRIALS_LABEL = (
    "More medicines in trials for this disease. They do not act on one of "
    "the 25 proteins."
)
# Kashish's words of 23 Nov, exactly. The last words on every card of that
# box. Only this sentence: a box card has no protein, so it says nothing
# about one. Changing them needs her approval.
MORE_IN_TRIALS_ENDING = "Never start, stop or change any medicine without a doctor."
# Ticket 2.24, Kashish's words of 23 Nov, exactly. The label of the second
# folded box under the In trials list. Changing them needs her approval.
# Its cards end with MORE_IN_TRIALS_ENDING, the same sentence.
NEW_IN_TRIALS_LABEL = (
    "New medicines being tested for this disease. The database records no "
    "approval for them for any disease."
)
CORRECTIONS_FILE = pathlib.Path(__file__).resolve().parent / "corrections.json"
CORRECTION_KEYS = {"medicine_id", "disease_id", "date", "note"}
# Ticket 2.18. The clues left out by hand. Nothing in Moonlight writes here.
LEFT_OUT_FILE = pathlib.Path(__file__).resolve().parent / "left_out.json"
LEFT_OUT_KEYS = {"medicine_id", "disease_id", "date"}


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
    # Ticket 2.17. Do the lists naming it hold an approval report from a
    # regulator, for any of its forms? True: yes. False: none of those
    # lists holds such a report. None: not said. It is on no list, or on
    # one of them its reports carry no source value.
    regulator_record: Optional[bool] = None

    @property
    def proof_note(self) -> Optional[str]:
        """The one quiet grey line the card carries, or None.

        Like a receipt check with two questions, asked in this order:
          1. Is Japan's general list its only approval receipt? Then
             JAPAN_LINE (ticket 2.13), and nothing else.
          2. Is it known to have no approval report from a regulator
             (regulator_record is False)? Then NO_REGULATOR_LINE
             (ticket 2.17). That includes no approval report at all.
        None if it has a regulator's approval report, or if nobody said
        where its reports come from. The line never moves or hides a card.
        """
        if self.approval_sources and all(link == JAPAN_LIST for link in self.approval_sources):
            return JAPAN_LINE
        if self.regulator_record is False:
            return NO_REGULATOR_LINE
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
class TrialMedicine:
    """One card of a folded box under the In trials list.

    Ticket 2.21, "More medicines in trials": in a trial for the disease,
    approved for something else, and it acts on none of the proteins
    looked at. Ticket 2.24, "New medicines being tested": in a trial for
    the disease and approved for nothing. Either way the card has no path,
    no score and no rank, and it is never explained.
    """

    id: str  # the id shared by the medicine and its tablet forms
    name: str
    forms: Tuple[str, ...]  # the names of its forms on the list, the parent first
    stage: str  # how far it got for this disease: the strongest of its forms
    # Its report links from the disease's own list: the reports for the
    # stage on the card first, then the others.
    sources: Tuple[str, ...] = ()

    @property
    def source_record(self) -> Optional[str]:
        """The one link the card shows: the first https link. None if none."""
        for link in self.sources:
            if link.startswith("https://"):
                return link
        return None


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
    # Ticket 2.21. In a trial for the disease, approved for something else,
    # on none of the proteins looked at: the folded box under the In trials
    # list. Furthest trial stage first, then A to Z. No rank.
    more_in_trials: List[TrialMedicine] = field(default_factory=list)
    # Ticket 2.24. In a trial for the disease, and no form we can see is
    # approved for anything: the second folded box, under that one.
    # Furthest trial stage first, then A to Z. No rank.
    new_in_trials: List[TrialMedicine] = field(default_factory=list)


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


# Ticket 2.16, Kashish's words, 18 Nov. Both box labels start with this, so
# nobody takes a boxed card as approved for their own disease.
NOT_THIS_EXACT_DISEASE = "Not listed as approved for this exact disease."


def child_label(names: List[str]) -> str:
    """Kashish's words, 16 and 18 Nov. They say only what the database does."""
    return (
        f"{NOT_THIS_EXACT_DISEASE} Approved for {_joined(names)}, "
        "which the database lists under this disease."
    )


def parent_label(names: List[str]) -> str:
    """Kashish's words, 16 and 18 Nov. With two or more names the grammar is for many."""
    group = "a wider group" if len(names) == 1 else "wider groups"
    return (
        f"{NOT_THIS_EXACT_DISEASE} Approved for {_joined(names)}, "
        f"{group} the database puts this disease in."
    )


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
    on_list: Iterable[OnList] = (),
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

    on_list (ticket 2.21, Kashish's decisions of 22 Nov) is the disease's
    own list as records (fetch.fetch_listed_medicines). It only fills
    more_in_trials, the folded box under the In trials list. Like a second
    guest list checked at the door, after everyone else is seated:
      - the same rule as In trials decides (filter.group_of): approved for
        at least one disease, not withdrawn, and a trial stage for this one;
      - withdrawn in any source is left out, as everywhere;
      - a medicine that acts on one of the proteins looked at is never in
        the box, whatever group the tray put it in: the box's label says
        "They do not act on one of the 25 proteins";
      - a medicine on the Approved tab or in one of its boxes is already
        on the page, so it is not in this box.
    Nothing else in the answer changes: the box is worked out last.

    on_list also fills new_in_trials (ticket 2.24, Kashish's decisions of
    23 Nov), the second folded box. The same guest list, read once more
    for the guests the first reading turned away:
      - the list gives it a trial stage for this disease, the same stage
        words as In trials;
      - no form of it that we can see is approved for anything: not on
        the list, and not on a path through one of the proteins;
      - the list must be able to tell (OnList.all_seen). If it names a
        parent or a tablet form it has no row for, the medicine stays out
        of both boxes;
      - withdrawn in any source is left out, as everywhere;
      - a medicine on any tab or in any other box is not in this one.
    A medicine in this box that acts on one of the proteins looked at is
    still counted in left_out as before: the counts keep their meaning.
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

    acts_on_a_protein = {
        _family_id(path.medicine) for paths in tray.values() for path in paths
    }
    more_in_trials = [
        _trial_medicine(entry)
        for entry in on_list
        if group_of(entry.medicine) == BEING_STUDIED  # the same rule as In trials
        and _family_id(entry.medicine) not in withdrawn_ids
        and _family_id(entry.medicine) not in acts_on_a_protein
        and _family_id(entry.medicine) not in own_ids
        and _family_id(entry.medicine) not in nearby
    ]
    # Furthest trial stage first, then A to Z, ignoring capitals. The last
    # two only make the order the same every time.
    more_in_trials.sort(key=lambda medicine: (
        STAGE_ORDER.index(medicine.stage), medicine.name.casefold(), medicine.name, medicine.id))

    # Ticket 2.24. Approved for something, as far as a path can see.
    approved_on_a_path = {
        _family_id(path.medicine)
        for paths in tray.values()
        for path in paths
        if path.medicine.best_stage == fetch.APPROVAL
    }
    new_in_trials = [
        _trial_medicine(entry)
        for entry in on_list
        if entry.all_seen  # the list can tell: nobody in the family is missing
        and entry.medicine.best_stage != fetch.APPROVAL  # approved for nothing
        and _is_a_trial(entry.medicine.disease_stage)
        and entry.medicine.withdrawn is not True
        and _family_id(entry.medicine) not in withdrawn_ids
        and _family_id(entry.medicine) not in approved_on_a_path
        and _family_id(entry.medicine) not in own_ids
        and _family_id(entry.medicine) not in nearby
    ]
    new_in_trials.sort(key=lambda medicine: (
        STAGE_ORDER.index(medicine.stage), medicine.name.casefold(), medicine.name, medicine.id))

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
        more_in_trials=more_in_trials,
        new_in_trials=new_in_trials,
    )


def _is_a_trial(stage: Optional[str]) -> bool:
    """Is this stage word a trial in people? The same words filter.group_of
    takes as "being studied": a phase, early or not. Nothing else."""
    return stage is not None and (stage.startswith("PHASE_") or stage.startswith("EARLY_PHASE_"))


def _trial_medicine(entry: OnList) -> TrialMedicine:
    """One card of either box, from the family's records on the disease's list."""
    medicine = entry.medicine
    stage = medicine.disease_stage  # the strongest of its forms
    # The receipt for the stage on the card first, then the other links.
    links = [link for link, said in entry.reports if said == stage]
    links += [link for link, _ in entry.reports if link not in links]
    return TrialMedicine(
        id=_family_id(medicine),
        name=medicine.name,
        forms=tuple(form.name for form in medicine.forms),
        stage=stage,
        sources=tuple(links),
    )


def keep_out(more: Iterable[TrialMedicine], listed: Iterable[str]) -> List[TrialMedicine]:
    """The box without the listed medicines. The rest keep their order.

    Tickets 2.21 and 2.24: no existing rule may be undone by a box under
    the In trials list. more is either box's cards. listed holds
    the family ids a hand-written list names for this disease
    (pushes_wrong_way and looks_wrong). Nothing is counted or said about
    the ones taken out.
    """
    listed = set(listed)
    return [medicine for medicine in more if medicine.id not in listed]


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
    # Ticket 2.17. One list with a regulator's approval report is enough.
    # "No regulator record" needs every list naming it to have said so. If
    # one of them did not say, or it is on no list at all, it is not known.
    said = [entry.regulator_record for entry in entries]
    if True in said:
        regulator_record: Optional[bool] = True
    elif said and all(answer is False for answer in said):
        regulator_record = False
    else:
        regulator_record = None
    return ApprovedMedicine(
        id=family_id,
        name=clue.medicine.name if clue else entries[0].name,
        forms=_parent_first(family_id, forms),
        clue=clue,
        listed_sources=tuple(sources),
        label=label,
        approval_sources=tuple(approval_sources),
        regulator_record=regulator_record,
    )


def _read_corrections() -> list:
    """The one place the corrections file is read. Tests replace this."""
    return json.loads(CORRECTIONS_FILE.read_text(encoding="utf-8"))


def _checked_pair(entry: object, keys: Set[str], kind: str) -> Tuple[str, str]:
    """One hand-written entry -> (medicine id, disease id), or ValueError.

    The entry must hold exactly the things in keys, with a medicine id, a
    disease id and a real date (like "2026-11-16"). Nothing else: no name,
    no reason.
    """
    if not isinstance(entry, dict) or set(entry) != keys:
        raise ValueError(f"{kind} must hold exactly {sorted(keys)}: {entry!r}")
    medicine_id, disease_id, date = entry["medicine_id"], entry["disease_id"], entry["date"]
    if not all(isinstance(value, str) and value for value in (medicine_id, disease_id, date)):
        raise ValueError(f"{kind} needs a medicine id, a disease id and a date: {entry!r}")
    datetime.date.fromisoformat(date)  # ValueError if it is not a real date
    return medicine_id, disease_id


def _corrections_with_notes() -> Dict[Tuple[str, str], str]:
    """The corrections list as (medicine id, disease id) -> the entry's note.

    Each entry holds exactly four things: the medicine's id, the disease's
    id, the date (like "2026-11-16") and a note that is exactly one of
    CORRECTION_NOTES. No doctor is ever named, so an entry holding anything
    else is refused. An entry that is not written this way raises
    ValueError: a warning is never dropped quietly. One card cannot carry
    both notes.
    """
    entries = _read_corrections()
    if not isinstance(entries, list):
        raise ValueError("corrections.json must hold a list.")
    notes: Dict[Tuple[str, str], str] = {}
    for entry in entries:
        pair = _checked_pair(entry, CORRECTION_KEYS, "A correction")
        note = entry["note"]
        if not isinstance(note, str) or note not in CORRECTION_NOTES:
            raise ValueError(
                f"A correction's note must be exactly one of {CORRECTION_NOTES!r}: {entry!r}")
        if notes.setdefault(pair, note) != note:
            raise ValueError(f"A correction is listed with two different notes: {entry!r}")
    return notes


def corrections() -> Set[Tuple[str, str]]:
    """The corrections list as (medicine id, disease id) pairs, whichever
    of the two notes an entry carries. Checked as _corrections_with_notes
    says."""
    return set(_corrections_with_notes())


def looks_wrong(disease_id: str) -> Set[str]:
    """The ids of the medicines on the corrections list for this disease.

    Their Approved cards show a red warning. The same medicine under
    another disease is not in the answer.
    """
    return {medicine_id for medicine_id, listed_for in corrections() if listed_for == disease_id}


def warning_words(disease_id: str) -> Dict[str, str]:
    """Medicine id -> the red words its Approved card shows for this disease.

    Ticket 2.18. A card shows what its own entry carries: WRONG_WARNING
    for the first note, as before, and SECOND_NOTE itself for the second.
    The ids are the same ones looks_wrong gives.
    """
    return {
        medicine_id: RED_WORDS[note]
        for (medicine_id, listed_for), note in _corrections_with_notes().items()
        if listed_for == disease_id
    }


def _read_left_out() -> list:
    """The one place the left-out file is read. Tests replace this."""
    return json.loads(LEFT_OUT_FILE.read_text(encoding="utf-8"))


def left_out_by_hand() -> Set[Tuple[str, str]]:
    """The left-out list as (medicine id, disease id) pairs (ticket 2.18).

    Each entry holds exactly three things: the medicine's id, the disease's
    id and the date. An entry that is not written this way raises
    ValueError, as for corrections: the list is never half read.

    Kashish's rule of 19 Nov: only a hand check may remove a card. This
    list is written by hand. No code adds to it.
    """
    entries = _read_left_out()
    if not isinstance(entries, list):
        raise ValueError("left_out.json must hold a list.")
    return {_checked_pair(entry, LEFT_OUT_KEYS, "A left-out entry") for entry in entries}


def pushes_wrong_way(disease_id: str) -> Set[str]:
    """The ids of the medicines left out by hand for this disease.

    The same medicine under another disease is not in the answer.
    """
    return {medicine_id for medicine_id, listed_for in left_out_by_hand()
            if listed_for == disease_id}


def leave_out(new_clues: Iterable[Clue], listed: Iterable[str]) -> Tuple[List[Clue], int]:
    """New clues without the listed medicines, and how many were taken out.

    Like taking some cards out of a ranked pile: the rest keep their
    order. new_clues is the New clues tab only. Approved and In trials
    are never handed in, so the list cannot change them. The number
    counts only clues that were in the pile: a listed medicine that was
    not a new clue is not counted. listed holds family ids (pushes_wrong_way).
    """
    listed = set(listed)
    new_clues = list(new_clues)
    kept = [clue for clue in new_clues if _family_id(clue.medicine) not in listed]
    return kept, len(new_clues) - len(kept)


def wrong_way_line(count: int) -> Optional[str]:
    """Kashish's words of 19 Nov, exactly, for the bottom of the New clues
    list. None if no medicine was left out: then there is no line."""
    if count < 1:
        return None
    if count == 1:
        return "1 medicine left out because it pushes the wrong way for this disease."
    return f"{count} medicines left out because they push the wrong way for this disease."


def one_way_proteins(
    approved: Iterable[ApprovedMedicine], wrong: Iterable[str] = ()
) -> Dict[str, str]:
    """Protein id -> "up" or "down", for the proteins that are one-way.

    Like a one-way street: every approved medicine on it drives the same
    way. approved is the MAIN Approved list only (Tabs.approved), never
    the narrower box or the wider box. wrong holds the ids of the
    medicines with the red warning for this disease (looks_wrong): they
    are left out. A medicine that turns the protein "mixed" or "unknown"
    is ignored. A protein with some medicines up and some down is
    both-ways, and a protein with none left is not known: neither is in
    the answer.
    """
    wrong = set(wrong)
    seen: Dict[str, Set[str]] = {}  # protein id -> the directions met
    for medicine in approved:
        if medicine.id in wrong or medicine.clue is None:
            continue
        for path in medicine.clue.paths:
            if path.direction in ("up", "down"):
                seen.setdefault(path.target.id, set()).add(path.direction)
    return {
        target_id: next(iter(directions))
        for target_id, directions in seen.items()
        if len(directions) == 1
    }


def opposite_way(clue: Clue, one_way: Dict[str, str]) -> Set[str]:
    """The ids of the clue's proteins that carry OPPOSITE_LINE.

    clue is a New clues or In trials card, never an Approved one. one_way
    comes from one_way_proteins. Only up against down, or down against
    up, counts. A clue that turns the protein "mixed" or "unknown" never
    gets the line.
    """
    against = {"up": "down", "down": "up"}
    return {
        path.target.id
        for path in clue.paths
        if path.direction in against and one_way.get(path.target.id) == against[path.direction]
    }


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
