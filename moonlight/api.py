"""The small API behind Sidha's page. Medicine first.

    GET /                                   the page (web/index.html)
    GET /api/search?q=                      matching diseases, best first, and "did you mean"
    GET /api/clues?disease_id=              the three tabs: approved, being studied
                                            and new clues. No explanations
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
"""

import pathlib
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List, Optional, Tuple

import requests
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse

from moonlight import explain, translate
from moonlight.engine import ApprovedMedicine, find_clues, sort_into_tabs
from moonlight.fetch import (
    FetchError,
    data_version,
    fetch_approved,
    fetch_disease,
    fetch_targets,
    search_diseases,
    search_matches,
)
from moonlight.fetch import Listed
from moonlight.filter import NOT_APPROVED, UNCLEAR_LINK
from moonlight.rank import RULE_TEXT, Clue
from moonlight.records import Disease, Path

PAGE = pathlib.Path(__file__).resolve().parent.parent / "web" / "index.html"
TOP_TARGETS = 25  # the same number of proteins the terminal runner looks at

# The left-out groups, in the order they are sent. Counts only.
LEFT_OUT_GROUPS = (NOT_APPROVED, UNCLEAR_LINK)

# "Did you mean" is given up on after this long, counted from the start of
# the search: Gemini's 3 seconds, and 2 more to look its names up in Open
# Targets. The normal matches never wait longer than this for it.
DID_YOU_MEAN_SECONDS = translate.GEMINI_SECONDS + 2
# Where "did you mean" runs while the normal search runs.
_side_lane = ThreadPoolExecutor(max_workers=8, thread_name_prefix="did-you-mean")

app = FastAPI(title="Moonlight", docs_url=None, redoc_url=None, openapi_url=None)


class _Found:
    """Everything worked out for one disease in one request."""

    def __init__(self, disease: Disease, tray: Dict[str, List[Path]], listed: List[Listed]):
        self.disease = disease
        tabs = sort_into_tabs(tray, listed)
        self.approved = tabs.approved  # A to Z. Not clues: no rank, never explained.
        self.new_clues = tabs.new_clues
        self.being_studied = tabs.being_studied
        self.left_out = tabs.left_out
        # Every medicine name Moonlight met, shown or not. Only the
        # explainer's check sees these. They are never sent to anyone.
        names = set()
        for paths in tray.values():
            for path in paths:
                names.add(path.medicine.name)
                names.update(form.name for form in path.medicine.forms)
        for medicine in tabs.approved:  # also the ones only on the disease's own list
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
        return _Found(disease, find_clues(disease, targets), fetch_approved(disease))
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


def _proteins_json(clue: Clue) -> List[dict]:
    """The proteins of one medicine, strongest first, with points and direction."""
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
    return proteins


def _clue_json(clue: Clue, disease: Disease) -> dict:
    """One clue's facts. No explanation, so this is quick."""
    # The names, the points and the ending come from explain.py, so a card
    # and its explanation always say the same thing.
    facts = explain.facts_for(clue, disease)
    return {
        "id": _clue_id(clue),
        "medicine": facts["medicine"]["name"],
        "forms": facts["medicine"]["forms"],
        "proteins": _proteins_json(clue),
        "reports": clue.reports,
        "source": _one_source(clue),
        "trial_phase": facts.get("trial_phase"),  # only for being studied
        "ending": explain.ending_for(facts),
    }


def _approved_json(medicine: ApprovedMedicine) -> dict:
    """One medicine already approved for the disease. It is not a clue, so
    it has no rank, no explanation and no ending.

    proteins is empty when the medicine acts on none of the top proteins.
    """
    # explain.py's own way of writing a name, so "SILDENAFIL" is written
    # "Sildenafil" here exactly as a clue's name is.
    display = explain._display
    return {
        "id": medicine.id,
        "medicine": display(medicine.name),
        "forms": [display(name) for name in medicine.forms],
        "proteins": _proteins_json(medicine.clue) if medicine.clue else [],
        "reports": medicine.reports,
        "source": _first_link(medicine.sources),
    }


@app.get("/", response_class=HTMLResponse)
def page() -> str:
    return PAGE.read_text(encoding="utf-8")


@app.get("/api/search")
def search(q: str = "") -> dict:
    """The matches, as before, plus "did_you_mean" and "also_called".

    Two swimmers, two lanes. Gemini's guesses set off in the side lane
    while the normal Open Targets search swims here. If the side lane is
    slow or goes wrong, the matches still come back, with no suggestions
    and no error. Moonlight never picks a disease: it only offers them.
    """
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
    return {
        "disease": {"id": disease.id, "name": disease.name},
        "rule_text": RULE_TEXT,
        # The three tabs, in the order the page shows them.
        "approved": [_approved_json(medicine) for medicine in found.approved],
        "being_studied": [_clue_json(clue, disease) for clue in found.being_studied],
        "new_clues": [_clue_json(clue, disease) for clue in found.new_clues],
        "left_out": {group: found.left_out[group] for group in LEFT_OUT_GROUPS},
    }


@app.get("/api/explain")
def explain_clue(disease_id: str, clue_id: str) -> dict:
    found = _find(disease_id)
    # Only a new clue or a medicine being studied can be explained. A
    # medicine already approved for the disease is not a clue: it is
    # "not found" here, like anything else.
    for clue in found.new_clues + found.being_studied:
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
    answer = explain.explain(clue, found.disease, found.known_names, data_version=version)
    return {
        "clue_id": clue_id,
        "text": answer.text,
        "source": answer.source,  # "gemini" or "template"
        "model": answer.model,  # None for the template
    }
