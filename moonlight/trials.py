"""Look up saved trials for a card. Ticket T3.

Like a drawer of race cards that someone else filled (scripts/build_trials.py
fills it, and it is the file moonlight/trials.sqlite). This file never goes to
the network and never changes the drawer.

    Trials.open()                    -> Trials, or None if the file is missing
                                        or is not a trials file (logged)
    trials.for_card(links, names)    -> ([up to 3 trials, newest first], total)
    trials.for_cards(cards, disease_name=...)  -> the new fields for each card
    trials.checked                   -> the date the file was built, "2026-11-26"

links are the card's own trial links for the page's disease (they hold the
NCT numbers). The file holds the studies but not which disease a medicine
was tested for, so it is only used to look those numbers up. total counts the
numbers that are in the file (it holds interventional studies only).

Newest first means the study's start date, newest first. A start date that is
missing, is not a real date, is before 1950 or is more than 10 years after
today counts as unknown and goes after every known date (Kashish's co-founder,
MAIN 5, 26 Nov). Ties go to the higher NCT number, so the order never changes
between two asks.

Each trial is what moonlight/ctgov.py reads (ticket T1): nct_id, status, end,
phases, role; and (ticket T4) "url", its page on ClinicalTrials.gov. A card
also gets "studies_url", the register's search for the card's medicine and
the page's disease, for the page's "All [N] trials" link. The page holds no
address of its own: it uses these. The role is read for the card's medicine, trying its name and
then each of its tablet forms; the first form that says more than "Role not
stated" wins.

How the file is read (standard library only; see scripts/build_trials.py): a
study is JSON compressed with zlib and one preset dictionary kept in the
"meta" row. start_date is kept plain in its own column, so sorting does not
open any study; only the three shown are opened.
"""

import dataclasses
import datetime
import json
import logging
import pathlib
import re
import sqlite3
import threading
import urllib.parse
import zlib
from typing import Iterable, List, Optional, Sequence, Tuple

from moonlight import ctgov

_log = logging.getLogger(__name__)

TRIALS_PATH = pathlib.Path(__file__).with_name("trials.sqlite")

MAX_SHOWN = 3
EARLIEST_START = datetime.date(1950, 1, 1)
YEARS_AHEAD = 10
ASK_AT_A_TIME = 500  # SQLite's own limit on "?" marks is far higher; this is plenty

_NCT = re.compile(r"NCT\d{8}", re.IGNORECASE)
_DATE = re.compile(r"^(\d{4})(?:-(\d{2}))?(?:-(\d{2}))?$")


def nct_numbers(links: Iterable[str]) -> List[str]:
    """The NCT numbers named in links, upper case, each once, sorted.
    A link with none (a drug page, a label) names no trial."""
    found = set()
    for link in links:
        match = _NCT.search(link or "")
        if match:
            found.add(match.group(0).upper())
    return sorted(found)


def start_key(text: Optional[str], today: datetime.date) -> Optional[datetime.date]:
    """A start date as a day (a missing month or day is the first), or None
    when it counts as unknown: not there, not a real date, before 1950, or
    more than ten years after today."""
    match = _DATE.match(text or "")
    if not match:
        return None
    year, month, day = (int(part) if part else 1 for part in match.groups())
    try:
        start = datetime.date(year, month, day)
    except ValueError:
        return None
    try:
        latest = today.replace(year=today.year + YEARS_AHEAD)
    except ValueError:  # 29 February, ten years on is not a leap year
        latest = today.replace(year=today.year + YEARS_AHEAD, day=28)
    if start < EARLIEST_START or start > latest:
        return None
    return start


class Trials:
    """The opened file. Open it once; every card asks it."""

    def __init__(self, con: sqlite3.Connection, zdict: bytes, checked: str):
        self._con = con
        self._zdict = zdict
        self.checked = checked
        # One connection is shared by the request threads, one at a time.
        self._lock = threading.Lock()

    @classmethod
    def open(cls, path: Optional[pathlib.Path] = None) -> Optional["Trials"]:
        """The file, read only. None, and a line in the log, if it is not there
        or cannot be read as a trials file: the page is then served without
        trial details, as before."""
        path = pathlib.Path(path if path is not None else TRIALS_PATH)
        if not path.is_file():
            _log.warning("trials file %s is missing: serving without trial details", path)
            return None
        con = None
        try:
            con = sqlite3.connect(f"{path.resolve().as_uri()}?mode=ro", uri=True,
                                  check_same_thread=False)
            zdict, checked = con.execute("SELECT zdict, run_date FROM meta").fetchone()
            con.execute("SELECT nct_id, start_date, study FROM studies LIMIT 1").fetchall()
            return cls(con, bytes(zdict), str(checked))
        except (sqlite3.Error, TypeError, ValueError) as error:
            if con is not None:
                con.close()
            _log.warning("trials file %s cannot be read (%s): serving without trial details",
                         path, error)
            return None

    def close(self) -> None:
        with self._lock:
            self._con.close()

    def for_card(self, links: Iterable[str], names: Sequence[str],
                 today: Optional[datetime.date] = None,
                 limit: int = MAX_SHOWN) -> Tuple[List[dict], int]:
        """(the newest trials, how many are in the file) for one card.

        names is the card's medicine name, then its tablet forms. Raises
        sqlite3.Error or zlib.error if the file is damaged: the caller serves
        the card as it was.
        """
        today = today or datetime.date.today()
        wanted = nct_numbers(links)
        with self._lock:
            starts = {}
            for at in range(0, len(wanted), ASK_AT_A_TIME):
                chunk = wanted[at:at + ASK_AT_A_TIME]
                marks = ",".join("?" * len(chunk))
                starts.update(self._con.execute(
                    f"SELECT nct_id, start_date FROM studies WHERE nct_id IN ({marks})", chunk))
            # Higher NCT number first on a tie, then known dates newest first,
            # then the unknown. Two stable sorts, so ties keep that order.
            order = sorted(starts, reverse=True)
            dated = {nct: start_key(starts[nct], today) for nct in order}
            order.sort(key=lambda nct: (dated[nct] is None,
                                        -dated[nct].toordinal() if dated[nct] else 0))
            shown = []
            for nct in order[:max(limit, 0)]:
                trial = self._read(nct, names)
                if trial is not None:
                    shown.append(_plain(trial))
        return shown, len(starts)

    def for_cards(self, cards: Sequence[Tuple[Iterable[str], Sequence[str]]],
                  today: Optional[datetime.date] = None,
                  disease_name: Optional[str] = None) -> Optional[List[dict]]:
        """The three new fields for each card, in the cards' order: (links,
        names) in, {"studies", "study_total", "trials_checked"} out, and
        (ticket T4) "studies_url" too when disease_name is given.

        All or none. If the file cannot be read for any card, the reason goes
        to the log (this file's, never the page's: the page keeps no log) and
        the answer is None, so the page is served as before.
        """
        try:
            found = []
            for links, names in cards:
                shown, total = self.for_card(links, names, today=today)
                one = {"studies": shown, "study_total": total,
                       "trials_checked": self.checked}
                if disease_name is not None:
                    one["studies_url"] = studies_url(disease_name, names[0] if names else "")
                found.append(one)
            return found
        except (sqlite3.Error, zlib.error, ValueError, TypeError) as error:
            _log.warning("trials file could not be read (%s): serving without trial details",
                         error)
            return None

    def _study(self, nct: str) -> dict:
        blob = self._con.execute("SELECT study FROM studies WHERE nct_id = ?", (nct,)).fetchone()[0]
        opened = zlib.decompressobj(zdict=self._zdict)
        return json.loads(opened.decompress(blob) + opened.flush())

    def _read(self, nct: str, names: Sequence[str]) -> Optional[ctgov.Trial]:
        study = self._study(nct)
        first = None
        for name in names or [""]:
            trial = ctgov.read_trial(study, name)
            if trial is None:
                return None
            first = first or trial
            if trial.role != ctgov.ROLE_NOT_STATED:
                return trial
        return first


STUDY_URL = "https://clinicaltrials.gov/study/"
SEARCH_URL = "https://clinicaltrials.gov/search"


def study_url(nct_id: str) -> str:
    """Ticket T4. One trial's page on ClinicalTrials.gov."""
    return STUDY_URL + nct_id


def studies_url(disease_name: str, medicine_name: str) -> str:
    """Ticket T4. The register's search for this medicine in this disease."""
    return (SEARCH_URL + "?cond=" + urllib.parse.quote(disease_name or "", safe="")
            + "&intr=" + urllib.parse.quote(medicine_name or "", safe=""))


# The same cut the disease-search file uses: interventional drug or biological.
DISEASE_FILTER = ("AREA[StudyType]INTERVENTIONAL AND "
                  "(AREA[InterventionType]DRUG OR AREA[InterventionType]BIOLOGICAL)")


def condition_search_url(disease_name: str) -> str:
    """Ticket T7. The register's search for a disease whose own trial list
    was too long to store. The words of the filter are the ones the search
    counted, so the link is that search."""
    return (SEARCH_URL + "?cond=" + urllib.parse.quote(disease_name or "", safe="")
            + "&term=" + urllib.parse.quote(DISEASE_FILTER, safe=""))


def _plain(trial: ctgov.Trial) -> dict:
    """A Trial as plain JSON: the phases as a list, and its page's address."""
    return {**dataclasses.asdict(trial), "phases": list(trial.phases),
            "url": study_url(trial.nct_id)}
