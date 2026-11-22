"""The small API behind Sidha's page. Medicine first.

    GET /                                   the page (web/index.html)
    GET /api/search?q=                      matching diseases, best first, and "did you mean"
    GET /api/clues?disease_id=              the three tabs: approved, being studied
                                            and new clues. No explanations. Also
                                            "more_in_trials": the folded box under
                                            the In trials list (ticket 2.21). Also
                                            "about_disease": Open Targets' own
                                            description and "also called" names
    GET /api/explain?disease_id=&clue_id=   one clue's explanation

Run it with:  uvicorn moonlight.api:app

Nothing here fetches, filters, ranks or explains by itself. It asks
fetch.py, engine.py, rank.py and explain.py, and turns their answers into
JSON. Three kinds of medicine are named: new clues, medicines being studied,
and medicines already approved for the disease (ticket 5.3). Approved
medicines are in A to Z order, with no rank, no explanation and no ending.
Medicines that are not approved anywhere, or have an unclear link, are sent
as two counts and nothing else.

/api/explain looks the disease up again to find its clue. It gives
explain.py the Open Targets data version, so a finished explanation is
saved, and asking for the same clue again makes no Gemini call.

The cost guard (ticket 8.2, Kashish's decisions of 2026-11-16, and
ticket 6.1, "the hall problem"). Like a ticket counter with one small
notepad per visitor: each visitor may make 60 requests to /api/search in
any MINUTE_SECONDS, and, counted on a separate notepad, 30 NEW
explanations (the numbers are in MAX_A_MINUTE). At an event a whole hall
shares one Wi-Fi, so Moonlight sees the hall as one visitor.

Only an explanation that needs a new Gemini call goes on the notepad. A
request answered from a saved explanation is never written down and is
never refused, even when the visitor is over the limit. The request takes
a place on the notepad first, and gives it back once it is answered
without a new Gemini call (or not answered at all: a 404 or a 502).

One more than the limit gets HTTP 429 and the words in TOO_MANY, and
nothing is asked of Open Targets or Gemini. An explanation request over
the limit is only answered if the explanation was already handed out by
this program (explain.remembered): that lookup asks nobody anything.
A search longer than MAX_SEARCH_LETTERS is refused the same way, before
anything is sent anywhere.

Who is "one visitor"? Their address. On Cloud Run the direct caller is
always Google's front door, never the visitor, and the visitor's address
arrives in the X-Forwarded-For header. That header is a list. The visitor
can write anything they like at the start of it, and the front door adds
the address it really saw at the END. So Moonlight reads only the entry
PROXIES_IN_FRONT from the end (1: the last one) and ignores the rest. If
another service is put in front later, read _visitor before deploying:
that number must change.

The notepads live in this program's memory and nowhere else. An address
is never printed, never written to a file and never sent to anyone, and
it is forgotten once its minute has passed.
"""

import pathlib
import threading
import time
from collections import deque
from concurrent.futures import ThreadPoolExecutor
from typing import Deque, Dict, Iterable, List, Optional, Tuple

import requests
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse

from moonlight import explain, translate
from moonlight.engine import ApprovedMedicine, Neighbour, fetch_neighbours, find_clues
from moonlight.engine import OPPOSITE_LINE, WRONG_WARNING, looks_wrong, sort_into_tabs
from moonlight.engine import one_way_proteins, opposite_way
from moonlight.engine import leave_out, pushes_wrong_way, warning_words, wrong_way_line
from moonlight.engine import TrialMedicine, keep_out
from moonlight.fetch import (
    FetchError,
    data_version,
    fetch_approved,
    fetch_disease,
    fetch_listed_medicines,
    fetch_targets,
    fetch_withdrawn,
    search_diseases,
    search_matches,
)
from moonlight.fetch import Listed, OnList
from moonlight.filter import NOT_APPROVED, UNCLEAR_LINK
from moonlight.rank import RULE_TEXT, Clue
from moonlight.records import Disease, Path

PAGE = pathlib.Path(__file__).resolve().parent.parent / "web" / "index.html"
TOP_TARGETS = 25  # the same number of proteins the terminal runner looks at

# Who wrote the disease's description. The page shows "Source: " and this.
DESCRIPTION_SOURCE = "Open Targets"

# The left-out groups, in the order they are sent. Counts only.
LEFT_OUT_GROUPS = (NOT_APPROVED, UNCLEAR_LINK)

# "Did you mean" is given up on after this long, counted from the start of
# the search: Gemini's 3 seconds, and 2 more to look its names up in Open
# Targets. The normal matches never wait longer than this for it.
DID_YOU_MEAN_SECONDS = translate.GEMINI_SECONDS + 2
# Where "did you mean" runs while the normal search runs.
_side_lane = ThreadPoolExecutor(max_workers=8, thread_name_prefix="did-you-mean")

# ---- the cost guard (ticket 8.2, ticket 6.1) ----
# Requests one visitor may make in a minute. Each lane has its own notepad.
# "explain" counts only explanations that need a new Gemini call.
MAX_A_MINUTE = {"search": 60, "explain": 30}
MINUTE_SECONDS = 60
MAX_SEARCH_LETTERS = 100  # the search box on the page stops here too
# Word for word from the ticket. The page shows exactly this.
TOO_MANY = "Too many requests. Please wait a minute."
# Kashish's exact words, 2026-11-16. The page cannot send a search this
# long (its box stops at 100), so this is only seen by someone who goes
# around the page.
TOO_LONG = "That search is too long. Please use 100 letters or fewer."
# How many services Google runs between the visitor and this program.
# On Cloud Run with nothing else in front it is 1: Google's front door.
# It writes the address it saw as the last entry of X-Forwarded-For.
PROXIES_IN_FRONT = 1
FORWARDING_HEADER = "x-forwarded-for"

# One notepad per lane ("search", "explain") and visitor: the times of the
# requests that were answered in the last minute, oldest first.
_visits: Dict[Tuple[str, str], Deque[float]] = {}
_visits_lock = threading.Lock()
_swept_at = 0.0  # when the old notepads were last thrown away


def _now() -> float:
    """The cost guard's clock, in seconds. Tests replace this."""
    return time.monotonic()


def forget_visitors() -> None:
    """Throw every notepad away."""
    global _swept_at
    with _visits_lock:
        _visits.clear()
        _swept_at = 0.0


def visitors_remembered() -> int:
    """How many notepads there are just now. A number, never an address."""
    with _visits_lock:
        return len(_visits)


def _visitor(request: Request) -> str:
    """The address that tells one visitor from another.

    With a forwarding header: the entry PROXIES_IN_FRONT from the end,
    the one Google's front door wrote. Earlier entries are whatever the
    visitor sent and are never trusted. With no header (a laptop, a
    test): the direct caller. This value is only ever a key in _visits.
    """
    entries = [
        entry.strip()
        for value in request.headers.getlist(FORWARDING_HEADER)
        for entry in value.split(",")
        if entry.strip()
    ]
    if len(entries) >= PROXIES_IN_FRONT:
        return entries[-PROXIES_IN_FRONT]
    return request.client.host if request.client else "unknown"


# One place on a notepad: whose notepad, and the time written on it.
_Place = Tuple[Tuple[str, str], float]


def _take_place(lane: str, request: Request) -> Optional[_Place]:
    """Write this request on the visitor's notepad and say where, or say
    None if the notepad is full.

    A request that is not written down does not make the wait any longer.
    """
    global _swept_at
    now = _now()
    oldest_kept = now - MINUTE_SECONDS
    key = (lane, _visitor(request))
    with _visits_lock:
        if now - _swept_at >= MINUTE_SECONDS:
            # Once a minute, notepads with nothing recent on them go in the bin.
            for old in [k for k, times in _visits.items() if times[-1] <= oldest_kept]:
                del _visits[old]
            _swept_at = now
        times = _visits.setdefault(key, deque())
        while times and times[0] <= oldest_kept:
            times.popleft()
        allowed = len(times) < MAX_A_MINUTE[lane]
        if allowed:
            times.append(now)
        elif not times:  # never left empty: the sweep reads the last entry
            del _visits[key]
    return (key, now) if allowed else None


def _give_back(place: _Place) -> None:
    """Rub one place off a notepad (ticket 6.1): the request did not need a
    new Gemini call after all."""
    key, written = place
    with _visits_lock:
        times = _visits.get(key)
        if times is None:
            return
        try:
            times.remove(written)
        except ValueError:
            return  # already gone with its minute
        if not times:  # never left empty: the sweep reads the last entry
            del _visits[key]


def _count_visit(lane: str, request: Request) -> None:
    """Write this request on the visitor's notepad, or refuse it with 429."""
    if _take_place(lane, request) is None:
        raise HTTPException(status_code=429, detail=TOO_MANY)


app = FastAPI(title="Moonlight", docs_url=None, redoc_url=None, openapi_url=None)


class _Found:
    """Everything worked out for one disease in one request."""

    def __init__(self, disease: Disease, tray: Dict[str, List[Path]], listed: List[Listed],
                 withdrawn_listed: List[Listed] = (), neighbours: List[Neighbour] = (),
                 on_list: List[OnList] = ()):
        self.disease = disease
        tabs = sort_into_tabs(tray, listed, withdrawn_listed, neighbours, on_list)
        self.approved = tabs.approved  # A to Z. Not clues: no rank, never explained.
        # Approved only for a wider group (ticket 2.12): the folded box.
        self.wider_group = tabs.wider_group
        # Approved only for a narrower disease (ticket 2.14): its own folded box.
        self.narrower = tabs.narrower
        self.new_clues = tabs.new_clues
        self.being_studied = tabs.being_studied
        self.left_out = tabs.left_out
        # In a trial for the disease, on none of the proteins (ticket 2.21):
        # the folded box under the In trials list. Their names are not added
        # to known_names below: the explainer's check is as it was.
        self.more_in_trials = tabs.more_in_trials
        # Every medicine name Moonlight met, shown or not. Only the
        # explainer's check sees these. They are never sent to anyone.
        names = set()
        for paths in tray.values():
            for path in paths:
                names.add(path.medicine.name)
                names.update(form.name for form in path.medicine.forms)
        # Also the ones only on the disease's own list, or on a parent's or child's.
        for medicine in tabs.approved + tabs.narrower + tabs.wider_group:
            names.add(medicine.name)
            names.update(medicine.forms)
        self.known_names = names


def _find(disease_id: str) -> _Found:
    """Disease -> its top proteins and its own medicine list -> the three tabs."""
    try:
        disease = fetch_disease(disease_id)
        if disease is None:
            raise HTTPException(status_code=404, detail="Open Targets does not know this disease.")
        targets = fetch_targets(disease, TOP_TARGETS)
        return _Found(disease, find_clues(disease, targets), fetch_approved(disease),
                      fetch_withdrawn(disease),  # the same saved answer, not a new question
                      fetch_neighbours(disease),  # one step up and one step down
                      fetch_listed_medicines(disease))  # the same saved answer again
    except (FetchError, requests.RequestException):
        raise HTTPException(
            status_code=502, detail="Could not get the data from Open Targets."
        ) from None


def _clue_id(clue: Clue) -> str:
    """The id shared by a medicine and its tablet forms (as in rank.py)."""
    first = clue.medicine.forms[0]
    return first.parent_id or first.id


def _first_link(sources) -> Optional[str]:
    for source in sources:
        if source.startswith("https://"):
            return source
    return None


def _one_source(clue: Clue) -> Optional[str]:
    """One link, from the strongest protein that has one. None if there is none."""
    return _first_link(source for path in clue.paths for source in path.sources)


def _proteins_json(clue: Clue, one_way: Optional[Dict[str, str]] = None) -> List[dict]:
    """The proteins of one medicine, strongest first, with points and direction.

    Ticket 3.7. one_way is only given for a new clue or a medicine being
    studied: the proteins the main Approved list turns one way
    (engine.one_way_proteins). A protein the clue turns the other way
    carries "opposite_way": the engine's line, word for word. Any other
    protein has no such key. An Approved card is never given one_way.
    """
    opposite = opposite_way(clue, one_way) if one_way else set()
    machine_of: Dict[str, Tuple[int, bool]] = {}
    for number, machine in enumerate(clue.machines, start=1):
        for path in machine:
            machine_of[path.target.id] = (number, len(machine) > 1)

    proteins = []
    for path in clue.paths:  # a Clue keeps its paths strongest first
        number, shared = machine_of[path.target.id]
        proteins.append(
            {
                "symbol": path.target.symbol,
                # Whole points out of 100, rounded the way explain.py does.
                "points": round(float(f"{path.score:.2f}") * 100),
                "direction": path.direction,
                "machine": number,  # proteins with the same number are one machine
                "piece_of_machine": shared,
            }
        )
        if path.target.id in opposite:
            proteins[-1]["opposite_way"] = OPPOSITE_LINE  # the engine's words
    return proteins


def _clue_json(clue: Clue, disease: Disease, one_way: Optional[Dict[str, str]] = None) -> dict:
    """One clue's facts. No explanation, so this is quick.

    one_way (ticket 3.7) is handed on to _proteins_json.
    """
    # The names, the points and the ending come from explain.py, so a card
    # and its explanation always say the same thing.
    facts = explain.facts_for(clue, disease)
    return {
        "id": _clue_id(clue),
        "medicine": facts["medicine"]["name"],
        "forms": facts["medicine"]["forms"],
        "proteins": _proteins_json(clue, one_way),
        "reports": clue.reports,
        "source": _one_source(clue),
        "trial_phase": facts.get("trial_phase"),  # only for being studied
        "ending": explain.ending_for(facts),
    }


def _approved_json(medicine: ApprovedMedicine, wrong: Iterable[str] = (),
                   words: Optional[Dict[str, str]] = None) -> dict:
    """One medicine already approved for the disease. It is not a clue, so
    it has no rank, no explanation and no ending.

    proteins is empty when the medicine acts on none of the top proteins.
    label is only there for a medicine found on a parent or child entry.

    Ticket 2.13. proof_note is only there when Japan's general list is the
    card's only approval receipt. warning is only there when the medicine's
    id is in wrong: the corrections list for this disease. Neither moves
    the card or takes anything off it.

    Ticket 2.18. words says which red words each listed card shows
    (engine.warning_words): its own entry's. A card in wrong that words
    does not name shows WRONG_WARNING, as before.

    Ticket 2.17. proof_note also carries the engine's other grey line: the
    card's medicine has no approval report from a regulator. One card has
    at most one grey line, and the Japan line comes first.

    Ticket 2.14. source is the engine's choice (source_record): an exact
    approval receipt, else Japan's general list, else the link shown before.
    """
    # explain.py's own way of writing a name, so "SILDENAFIL" is written
    # "Sildenafil" here exactly as a clue's name is.
    display = explain._display
    item = {
        "id": medicine.id,
        "medicine": display(medicine.name),
        "forms": [display(name) for name in medicine.forms],
        "proteins": _proteins_json(medicine.clue) if medicine.clue else [],
        "reports": medicine.reports,
        "source": medicine.source_record,
    }
    if medicine.label:
        item["label"] = medicine.label  # the engine's words, never changed here
    if medicine.proof_note:
        item["proof_note"] = medicine.proof_note  # the engine's words too
    if medicine.id in wrong:
        item["warning"] = (words or {}).get(medicine.id, WRONG_WARNING)
    return item


def _more_in_trials_json(medicine: TrialMedicine) -> dict:
    """One card of the box under the In trials list (ticket 2.21).

    The medicine, its trial stage and its source link. It acts on none of
    the proteins looked at, so it has no proteins, no points, no reports
    count and no ending, and it is never explained. The stage is written
    the way an In trials card writes it.
    """
    display = explain._display
    return {
        "id": medicine.id,
        "medicine": display(medicine.name),
        "forms": [display(name) for name in medicine.forms],
        "trial_phase": explain._phase_words(medicine.stage),
        "source": medicine.source_record,
    }


def _about_json(disease: Disease) -> dict:
    """The disease in Open Targets' own words (ticket 5.5).

    The description is sent word for word. Nothing here, and nothing
    anywhere else in Moonlight, writes one: if Open Targets has none, the
    description is "" and there is no source, so the page shows neither.
    The "also called" names are Open Targets' exact ones, as it spells them
    and in its order. The disease's own name is not repeated among them.
    """
    own_name = " ".join(disease.name.lower().split())
    return {
        "description": disease.description,
        "source": DESCRIPTION_SOURCE if disease.description else None,
        "also_called": [
            name for name in disease.also_called
            if " ".join(name.lower().split()) != own_name
        ],
    }


def _shown_new_clues(found: _Found) -> Tuple[List[Clue], int]:
    """The New clues tab without the medicines left out by hand for this
    disease, and how many of them there were (ticket 2.18). The engine
    reads the hand-written list. Only New clues is handed to it."""
    return leave_out(found.new_clues, pushes_wrong_way(found.disease.id))


@app.get("/", response_class=HTMLResponse)
def page() -> str:
    return PAGE.read_text(encoding="utf-8")


@app.get("/api/search")
def search(request: Request, q: str = "") -> dict:
    """The matches, as before, plus "did_you_mean" and "also_called".

    Two swimmers, two lanes. Gemini's guesses set off in the side lane
    while the normal Open Targets search swims here. If the side lane is
    slow or goes wrong, the matches still come back, with no suggestions
    and no error. Moonlight never picks a disease: it only offers them.

    Before any of that, the cost guard: the visitor's count, then the
    length of what they typed.
    """
    _count_visit("search", request)
    if len(q) > MAX_SEARCH_LETTERS:
        raise HTTPException(status_code=400, detail=TOO_LONG)
    text = q.strip()
    if not text:
        return {"matches": []}
    give_up_at = time.monotonic() + DID_YOU_MEAN_SECONDS
    guessing = _side_lane.submit(translate.did_you_mean, text)
    try:
        matches = search_diseases(text)
        # The same question once more, answered from the saved results:
        # is what the person typed one of an entry's "also called" names?
        also_called = {
            match.disease.id: translate.small_print(text, match)
            for match in search_matches(text)
        }
    except (FetchError, requests.RequestException):
        raise HTTPException(
            status_code=502, detail="Could not get the data from Open Targets."
        ) from None
    try:
        guesses = guessing.result(timeout=max(0.0, give_up_at - time.monotonic()))
    except Exception:  # slow, busy, unreachable or broken: no suggestions, no error
        guesses = []

    did_you_mean = []
    for guess in guesses:
        if matches and guess.disease.id == matches[0].id:
            continue  # already the first match: not repeated
        did_you_mean.append({"id": guess.disease.id, "name": guess.disease.name})
        also_called.setdefault(guess.disease.id, guess.also_called)
    return {
        "matches": [{"id": disease.id, "name": disease.name} for disease in matches],
        "did_you_mean": did_you_mean,
        # id -> Open Targets' own "also called" word, only where there is one.
        "also_called": {key: word for key, word in also_called.items() if word},
    }


@app.get("/api/clues")
def clues(disease_id: str) -> dict:
    found = _find(disease_id)
    disease = found.disease
    wrong = looks_wrong(disease.id)  # the corrections list, for this disease only
    words = warning_words(disease.id)  # each listed card's own red words (ticket 2.18)
    new_clues, wrong_way = _shown_new_clues(found)  # ticket 2.18: left out by hand
    # Ticket 3.7. The main Approved list only, without the red-warning cards.
    one_way = one_way_proteins(found.approved, wrong)
    answer = {
        "disease": {"id": disease.id, "name": disease.name},
        "about_disease": _about_json(disease),
        "rule_text": RULE_TEXT,
        # The three tabs, in the order the page shows them.
        "approved": [_approved_json(medicine, wrong, words) for medicine in found.approved],
        "being_studied": [_clue_json(clue, disease, one_way) for clue in found.being_studied],
        "new_clues": [_clue_json(clue, disease, one_way) for clue in new_clues],
        "left_out": {group: found.left_out[group] for group in LEFT_OUT_GROUPS},
    }
    if found.narrower:
        # The folded box "Approved for a narrower disease". Only there when
        # it holds something. The page shows it above the wider-group box.
        answer["narrower"] = [
            _approved_json(medicine, wrong, words) for medicine in found.narrower]
    if found.wider_group:
        # The folded box in the Approved tab. Only there when it holds something.
        answer["wider_group"] = [
            _approved_json(medicine, wrong, words) for medicine in found.wider_group]
    # Ticket 2.21. The folded box under the In trials list. No existing rule
    # is undone by it: a medicine left out by hand for this disease, or on
    # the corrections list for it, is not shown here either.
    more = keep_out(found.more_in_trials, pushes_wrong_way(disease.id) | wrong)
    if more:
        # Only there when it holds something, like the Approved tab's boxes.
        answer["more_in_trials"] = [_more_in_trials_json(medicine) for medicine in more]
    if wrong_way:
        # One line for the bottom of the New clues list: the engine's
        # words. Only there when a clue was left out by hand.
        answer["wrong_way_line"] = wrong_way_line(wrong_way)
    return answer


def _explanation_json(clue_id: str, answer: explain.Explanation) -> dict:
    return {
        "clue_id": clue_id,
        "text": answer.text,
        "source": answer.source,  # "gemini" or "template"
        "model": answer.model,  # None for the template
    }


@app.get("/api/explain")
def explain_clue(request: Request, disease_id: str, clue_id: str) -> dict:
    place = _take_place("explain", request)
    if place is None:
        # Over the limit. Only an explanation this program has already
        # handed out is given, and finding it asks nobody anything.
        # Anything else is a 429 and nothing else: no template explanation.
        kept = explain.remembered(disease_id, clue_id)
        if kept is None:
            raise HTTPException(status_code=429, detail=TOO_MANY)
        return _explanation_json(clue_id, kept)

    # The place is given back unless a new Gemini call is needed (ticket
    # 6.1): a saved explanation, a 404 and a 502 are not counted.
    keep_place = False
    try:
        found = _find(disease_id)
        # Only a new clue or a medicine being studied can be explained. A
        # medicine already approved for the disease is not a clue: it is
        # "not found" here, like anything else. So is a clue left out by hand
        # (ticket 2.18): its card is not shown, so nothing asks for it.
        for clue in _shown_new_clues(found)[0] + found.being_studied:
            if _clue_id(clue) == clue_id:
                break
        else:
            raise HTTPException(status_code=404, detail="No clue with this id for this disease.")
        # A finished explanation is saved under the data version the clue came
        # from. _find has just read that version, so this asks nothing new.
        try:
            version = data_version()
        except (FetchError, requests.RequestException):
            raise HTTPException(
                status_code=502, detail="Could not get the data from Open Targets."
            ) from None
        answer = explain.saved_explanation(
            clue, found.disease, found.known_names, data_version=version)
        if answer is None:
            keep_place = True  # a new Gemini call: this one is counted
            answer = explain.explain(clue, found.disease, found.known_names,
                                     data_version=version)
    finally:
        if not keep_place:
            _give_back(place)
    explain.remember(disease_id, clue_id, version, answer)
    return _explanation_json(clue_id, answer)
