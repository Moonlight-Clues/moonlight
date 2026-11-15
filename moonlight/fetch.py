"""Fetch: ask Open Targets about a disease, its proteins, and their medicines.

Five questions, five functions:

    search_diseases(text)          -> list of Disease, best match first
    search_matches(text)           -> the same list, each with its "also called" names
    fetch_disease(disease_id)      -> one Disease with its description filled in
    fetch_targets(disease, limit)  -> list of Target, highest score first
    fetch_paths(disease, target)   -> list of Path, one per Medicine family
    fetch_approved(disease)        -> list of Listed: the medicines Open Targets'
                                      own list says are approved for the disease

and one about the data itself:

    data_version()                 -> the Open Targets data release, like "26.09"

Nothing here sorts medicines into groups or ranks them.

Every question goes through _post_json. It looks in the saved results
(moonlight/cache.py) first and only asks Open Targets when the answer is
not there, or is past its use-by date of one day. Tests that swap
_post_json swap the saved results out with it.
Every real HTTP call goes through _send, on one shared connection.

Field names were read from the saved responses in fixtures/ and from
docs/schema-notes.md, not from memory. "meta", "dataVersion", "year",
"month" and "iteration" were read from the live API on 2026-11-12.
"category", "object", "synonyms", "relation" and "terms" in the search were
read from the live API on 2026-11-13 and are saved in fixtures/search/.
"drugWarnings", "warningType" and "childMolecules" were read from the live
API on 2026-11-15 and are saved in fixtures/withdrawn_probe/ and
fixtures/withdrawn/.
The fields of the disease's own medicine list ("drugAndClinicalCandidates"
on a disease, "maxClinicalStage" on its rows) were read from
fixtures/MONDO_0015924/disease_drugs.* and the live API on 2026-11-15.
"""

import logging
import threading
import time
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import requests

from moonlight import cache
from moonlight.records import (
    Disease,
    Medicine,
    MedicineForm,
    Path,
    Target,
    stronger_stage,
)

URL = "https://api.platform.opentargets.org/api/v4/graphql"
TIMEOUT_SECONDS = 30
SEARCH_SIZE = 10
VERSION_CHECK_SECONDS = 3600  # a long-running program reads the version again after this
# Kashish's decision, 2026-11-12. Open Targets sometimes gives a short
# answer to "which medicines act on this protein?", with reports missing.
# So that question is asked twice, and a third time only if the first two
# answers differ. "Which medicines are on this disease's own list?" is the
# same kind of question, so it is asked the same way (ticket 5.3). The answer with the most clinical reports is kept, and
# only then is it saved. The medicines must be the same in every answer.
# If they are not, Moonlight stops and saves nothing.
ASKS_AT_FIRST = 2
ASKS_AT_MOST = 3
# Kashish's decision, 2026-11-13. A saved Open Targets answer has a use-by
# date of one day, like milk. An older one is not used and is asked for
# fresh. So a short answer saved by mistake can only stay for a day.
USE_BY_SECONDS = 24 * 60 * 60

VERSION_QUERY = """
query DataVersion {
  meta { dataVersion { year month iteration } }
}
"""

SEARCH_QUERY = """
query DiseaseSearch($text: String!, $size: Int!) {
  search(queryString: $text, entityNames: ["disease"], page: {index: 0, size: $size}) {
    total
    hits {
      id
      entity
      name
      category
      object { ... on Disease { synonyms { relation terms } } }
    }
  }
}
"""

# Kashish's decision, 2026-11-13. Measurements are hidden from the list of
# matches. Open Targets says which entries they are: each search hit has a
# "category" list, and a measurement's list holds this word. Nothing is
# guessed from the name or the id.
MEASUREMENT = "measurement"
# The group of "also called" names that mean exactly the same disease.
EXACT_SYNONYM = "hasExactSynonym"

# Kashish's decision, 2026-11-15. If any country took a medicine off the
# shelves, Moonlight leaves it out. Open Targets keeps this in a list called
# "drugWarnings". Each warning has a "warningType". Only this type counts.
# The other type seen, "Black Box Warning", is not a withdrawal.
WITHDRAWN = "withdrawn"  # compared in small letters

_log = logging.getLogger(__name__)

DISEASE_QUERY = """
query DiseaseRecord($diseaseId: String!) {
  disease(efoId: $diseaseId) { id name description }
}
"""

TARGETS_QUERY = """
query AssociatedTargets($diseaseId: String!, $size: Int!) {
  disease(efoId: $diseaseId) {
    id
    associatedTargets(page: {index: 0, size: $size}) {
      count
      rows {
        score
        target { id approvedSymbol approvedName }
      }
    }
  }
}
"""

TARGET_DRUGS_QUERY = """
query TargetDrugs($targetId: String!) {
  target(ensemblId: $targetId) {
    id
    drugAndClinicalCandidates {
      count
      rows {
        drug {
          id
          name
          maximumClinicalStage
          drugWarnings { warningType }
          parentMolecule { id name drugWarnings { warningType } }
          childMolecules { id name drugWarnings { warningType } }
          mechanismsOfAction {
            rows {
              actionType
              targets { id }
            }
          }
          indications {
            rows { maxClinicalStage disease { id } }
          }
        }
        clinicalReports { url }
      }
    }
  }
}
"""

# Ticket 5.3. Open Targets' own list of medicines for a disease. Each row is
# one medicine form, and "maxClinicalStage" on the row is how far that form
# got for THIS disease. "maximumClinicalStage" on the drug is how far it got
# for any disease.
DISEASE_DRUGS_QUERY = """
query DiseaseDrugs($diseaseId: String!) {
  disease(efoId: $diseaseId) {
    id
    drugAndClinicalCandidates {
      count
      rows {
        maxClinicalStage
        drug {
          id
          name
          maximumClinicalStage
          drugWarnings { warningType }
          parentMolecule { id name drugWarnings { warningType } }
          childMolecules { id name drugWarnings { warningType } }
        }
        clinicalReports { url }
      }
    }
  }
}
"""
APPROVAL = "APPROVAL"  # the stage word for "approved", in both stage fields

# The two "which medicines?" questions. Both are asked twice, see below.
MEDICINE_QUERIES = (TARGET_DRUGS_QUERY, DISEASE_DRUGS_QUERY)


class FetchError(RuntimeError):
    """Open Targets answered, but with an error instead of data."""


class AnswersDisagree(FetchError):
    """Asked the same question again, Open Targets named different medicines."""


# One connection to Open Targets, opened once and used for every call.
_session = requests.Session()

_version: Optional[str] = None
_version_read_at = 0.0
_version_lock = threading.Lock()
_turn = threading.local()  # see started()


def _send(body: dict) -> dict:
    """The one place Moonlight talks to Open Targets. Tests replace this."""
    response = _session.post(URL, json=body, timeout=TIMEOUT_SECONDS)
    response.raise_for_status()
    return response.json()


def data_version() -> str:
    """The Open Targets data release, read from the API. Like "26.09".

    It is read once and remembered, because every saved result is filed
    under it. A program that runs for a long time reads it again every hour.
    """
    global _version, _version_read_at
    with _version_lock:
        now = time.monotonic()
        if _version is None or now - _version_read_at > VERSION_CHECK_SECONDS:
            answer = _send({"query": VERSION_QUERY, "variables": {}})
            if answer.get("errors") or not answer.get("data"):
                raise FetchError(f"Open Targets did not give its data version: {answer}")
            version = answer["data"]["meta"]["dataVersion"]
            parts = [version["year"], version["month"], version["iteration"]]
            _version = ".".join(str(part) for part in parts if part)
            _version_read_at = now
        return _version


def forget_version() -> None:
    """Forget the data version, so the next question reads it again."""
    global _version
    with _version_lock:
        _version = None


def _is_good(answer: dict) -> bool:
    return not answer.get("errors") and answer.get("data") is not None


def _rows(answer: dict) -> List[dict]:
    """The medicine rows of an answer, about a protein or about a disease."""
    asked_about = answer["data"].get("target") or answer["data"].get("disease") or {}
    return (asked_about.get("drugAndClinicalCandidates") or {}).get("rows") or []


def _report_count(answer: dict) -> int:
    """How many clinical reports a "which medicines?" answer holds."""
    return sum(len(row.get("clinicalReports") or []) for row in _rows(answer))


def _medicine_ids(answer: dict) -> List[str]:
    """The id of every medicine form in the answer, sorted."""
    return sorted((row.get("drug") or {}).get("id") or "" for row in _rows(answer))


def _send_keeping_the_fullest(body: dict) -> dict:
    """Ask twice. Ask a third time only if the first two answers differ.
    Keep the answer with the most clinical reports in total.

    If two answers are equally full, the earlier one is kept. An answer
    that is an error is handed straight back. If the answers do not hold
    the same medicines, AnswersDisagree is raised and nothing is saved.
    """
    answers: List[dict] = []
    while len(answers) < ASKS_AT_MOST:
        answer = _send(body)
        if not _is_good(answer):
            return answer
        answers.append(answer)
        if _medicine_ids(answer) != _medicine_ids(answers[0]):
            raise AnswersDisagree(
                "Open Targets gave different medicines for the same question "
                f"({body['variables']}). Nothing was saved. Please tell Kashish."
            )
        if len(answers) == ASKS_AT_FIRST and answers[0] == answers[1]:
            break
    return max(answers, key=_report_count)  # max keeps the earliest of equals


def _post_json(body: dict) -> dict:
    """One question for Open Targets: from the saved results if it is there
    and not past its use-by date, from the network if not. Only good answers
    are saved. Tests replace this.
    """
    version = data_version()
    saved = cache.load("open-targets", version, body, max_age_seconds=USE_BY_SECONDS)
    if saved is not None:
        return saved
    if body["query"] in MEDICINE_QUERIES:
        answer = _send_keeping_the_fullest(body)
    else:
        answer = _send(body)
    if _is_good(answer):
        cache.save("open-targets", version, body, answer)
    return answer


def started(tell) -> None:
    """Ask to be told when this thread next begins a question.

    tell is called once, with nothing, at that moment. The engine uses it to
    start several proteins in order: the next one sets off as soon as this
    one has begun.
    """
    _turn.tell = tell


def _ask(query: str, variables: dict) -> dict:
    """Send one question and hand back the "data" part of the answer."""
    tell = getattr(_turn, "tell", None)
    if tell is not None:
        _turn.tell = None
        tell()
    answer = _post_json({"query": query, "variables": variables})
    if answer.get("errors"):
        raise FetchError(f"Open Targets returned errors: {answer['errors']}")
    data = answer.get("data")
    if data is None:
        raise FetchError("Open Targets returned no data.")
    return data


@dataclass(frozen=True)
class Match:
    """One search match and Open Targets' exact "also called" names for it."""

    disease: Disease
    also_called: Tuple[str, ...]


def _exact_names(hit: dict) -> Tuple[str, ...]:
    """The names Open Targets says mean exactly this disease. () if none."""
    names: List[str] = []
    for group in (hit.get("object") or {}).get("synonyms") or []:
        if group["relation"] == EXACT_SYNONYM:
            names.extend(group["terms"])
    return tuple(names)


def search_matches(text: str) -> List[Match]:
    """Diseases matching the words, in the order Open Targets ranks them,
    each with its exact "also called" names. Measurements are left out.

    An answer saved before 2026-11-13 has no "category" and no "object".
    Then nothing is hidden and there are no "also called" names.
    """
    data = _ask(SEARCH_QUERY, {"text": text, "size": SEARCH_SIZE})
    return [
        Match(disease=Disease(id=hit["id"], name=hit["name"]), also_called=_exact_names(hit))
        for hit in data["search"]["hits"]
        if hit["entity"] == "disease" and MEASUREMENT not in (hit.get("category") or [])
    ]


def search_diseases(text: str) -> List[Disease]:
    """Diseases matching the words, in the order Open Targets ranks them.
    Measurements are left out."""
    return [match.disease for match in search_matches(text)]


def fetch_disease(disease_id: str) -> Optional[Disease]:
    """The disease with its description filled in. None if the id is not known.

    Open Targets may send no description at all. Then it stays "", and
    nothing is made up to fill the gap.
    """
    data = _ask(DISEASE_QUERY, {"diseaseId": disease_id})
    record = data["disease"]
    if record is None:
        return None
    return Disease(
        id=record["id"],
        name=record["name"],
        description=(record["description"] or "").strip(),
    )


def fetch_targets(disease: Disease, limit: int = 25) -> List[Target]:
    """The proteins most strongly linked to the disease, highest score first."""
    data = _ask(TARGETS_QUERY, {"diseaseId": disease.id, "size": limit})
    if data["disease"] is None:
        return []
    targets = [
        Target(
            id=row["target"]["id"],
            symbol=row["target"]["approvedSymbol"],
            name=row["target"]["approvedName"],
            score=row["score"],
        )
        for row in data["disease"]["associatedTargets"]["rows"]
    ]
    # Rows arrive highest first already. Sorting keeps the promise even if
    # that ever changes; equal scores keep the order they arrived in.
    targets.sort(key=lambda target: target.score, reverse=True)
    return targets


def _disease_stage(drug: dict, disease_id: str) -> Optional[str]:
    """How far this one form got for our disease. None if it has no link."""
    stage = None
    for indication in drug["indications"]["rows"]:
        linked = indication["disease"]
        if linked and linked["id"] == disease_id:
            stage = stronger_stage(stage, indication["maxClinicalStage"])
    return stage


def _action_types_on(drug: dict, target_id: str) -> List[str]:
    """What this form does to OUR target, ignoring its other targets."""
    found = []
    for mechanism in drug["mechanismsOfAction"]["rows"]:
        if any(hit["id"] == target_id for hit in mechanism["targets"]):
            action = mechanism["actionType"]
            if action and action not in found:
                found.append(action)
    return found


def _same_machine_ids(drug: dict, target_id: str) -> List[str]:
    """The other proteins that are pieces of the same machine as OUR target.

    One mechanism row is one machine. If a row lists our target, every other
    target in that row is a piece of the same machine.
    """
    found = []
    for mechanism in drug["mechanismsOfAction"]["rows"]:
        ids = [hit["id"] for hit in mechanism["targets"]]
        if target_id in ids:
            for other in ids:
                if other != target_id and other not in found:
                    found.append(other)
    return found


def _was_withdrawn(drug: dict) -> Optional[bool]:
    """Was this form, the medicine it is a form of, or one of its own
    tablet forms withdrawn in any country?

    True if any of them has a warning of the type "Withdrawn". False if
    Open Targets sent the warnings for all of them and none is a withdrawal.
    None if a warnings list is missing and no withdrawal was found: then
    it is not known, and nothing is guessed.
    """
    told_everything = True
    if drug.get("childMolecules") is None:
        told_everything = False  # no word about its tablet forms
    molecules = [drug, drug.get("parentMolecule")] + list(drug.get("childMolecules") or [])
    for molecule in molecules:
        if molecule is None:
            continue  # it is not a form of another medicine
        warnings = molecule.get("drugWarnings")
        if warnings is None:
            told_everything = False
            continue
        for warning in warnings:
            if (warning.get("warningType") or "").strip().lower() == WITHDRAWN:
                return True
    return False if told_everything else None


def fetch_paths(disease: Disease, target: Target) -> List[Path]:
    """One Path per medicine family acting on the target.

    A form with a parent joins its parent's family, and the family is named
    after the parent. Families come out in the order Open Targets first
    mentions them. Each form remembers whether it was withdrawn in any
    country. If Open Targets did not say, that is written in the log.
    """
    data = _ask(TARGET_DRUGS_QUERY, {"targetId": target.id})
    if data["target"] is None:
        return []

    families: Dict[str, dict] = {}  # family id -> what we have gathered so far
    for row in data["target"]["drugAndClinicalCandidates"]["rows"]:
        drug = row["drug"]
        if drug is None:
            continue
        parent = drug["parentMolecule"]
        family_id = parent["id"] if parent else drug["id"]
        family = families.setdefault(
            family_id, {"name": None, "forms": [], "actions": [], "sources": [], "machine": []}
        )
        if parent:
            # Named after the parent, even if the parent has no row of its own.
            family["name"] = family["name"] or parent["name"]
        else:
            family["name"] = drug["name"]

        form = MedicineForm(
            id=drug["id"],
            name=drug["name"],
            best_stage=drug["maximumClinicalStage"],
            disease_stage=_disease_stage(drug, disease.id),
            parent_id=parent["id"] if parent else None,
            withdrawn=_was_withdrawn(drug),
        )
        if parent:
            family["forms"].append(form)
        else:
            family["forms"].insert(0, form)  # the parent itself goes first

        for action in _action_types_on(drug, target.id):
            if action not in family["actions"]:
                family["actions"].append(action)
        for other in _same_machine_ids(drug, target.id):
            if other not in family["machine"]:
                family["machine"].append(other)
        for report in row["clinicalReports"]:
            url = report["url"]
            if url and url not in family["sources"]:
                family["sources"].append(url)

    paths = [
        Path(
            medicine=Medicine(name=family["name"], forms=family["forms"]),
            target=target,
            disease=disease,
            action_types=family["actions"],
            score=target.score,
            sources=family["sources"],
            same_machine_ids=sorted(family["machine"]),
        )
        for family in families.values()
    ]
    not_known = sum(1 for path in paths if path.medicine.withdrawn is None)
    if not_known:
        # Said out loud, never guessed. The medicines are counted, not named.
        _log.warning(
            "Open Targets did not say whether %d of the %d medicines acting on %s "
            "were withdrawn. Moonlight could not check them for withdrawal.",
            not_known, len(paths), target.symbol,
        )
    return paths


@dataclass(frozen=True)
class Listed:
    """One medicine family that Open Targets' own list for a disease says is
    approved for that disease.

    forms holds (id, name) for every form of the family on that list, the
    parent first. sources holds the family's report links, each once.
    """

    id: str  # the id shared by the medicine and its tablet forms
    name: str
    forms: Tuple[Tuple[str, str], ...]
    sources: Tuple[str, ...]


def fetch_approved(disease: Disease) -> List[Listed]:
    """The medicines on the disease's own list whose stage for this disease
    is approval. One Listed per medicine family, in the order Open Targets
    first mentions them. [] if the disease is not known or none is approved.

    A medicine and its tablet forms are one item, named after the parent.
    The item takes the strongest stage of its forms: it is here if at least
    one form is approved for this disease. That form must also say it is
    approved for at least one disease. If it does not, the two stages
    disagree, and the form does not count. Nothing is guessed.

    Only the word "APPROVAL" is looked for. A form with any other stage
    word, even one Moonlight has never met, is only listed as a form.

    Kashish's decision, 2026-11-15. A medicine withdrawn in any country
    does not count as approved. If any form of a family on this list was
    withdrawn, the whole family is left out, even if the withdrawn form is
    not the approved one. If Open Targets did not say, nothing is guessed:
    the family stays, and that is written in the log.
    """
    data = _ask(DISEASE_DRUGS_QUERY, {"diseaseId": disease.id})
    if data["disease"] is None:
        return []

    families: Dict[str, dict] = {}  # family id -> what we have gathered so far
    for row in data["disease"]["drugAndClinicalCandidates"]["rows"]:
        drug = row["drug"]
        if drug is None:
            continue
        parent = drug["parentMolecule"]
        family_id = parent["id"] if parent else drug["id"]
        family = families.setdefault(
            family_id,
            {"name": None, "forms": [], "sources": [], "approved": False, "withdrawn": []},
        )
        family["withdrawn"].append(_was_withdrawn(drug))  # True, False or None
        if parent:
            family["name"] = family["name"] or parent["name"]
        else:
            family["name"] = drug["name"]

        form = (drug["id"], drug["name"])
        if form not in family["forms"]:
            if parent:
                family["forms"].append(form)
            else:
                family["forms"].insert(0, form)  # the parent itself goes first
        if row["maxClinicalStage"] == APPROVAL and drug["maximumClinicalStage"] == APPROVAL:
            family["approved"] = True
        for report in row["clinicalReports"]:
            url = report["url"]
            if url and url not in family["sources"]:
                family["sources"].append(url)

    approved = {
        family_id: family for family_id, family in families.items() if family["approved"]
    }
    not_known = sum(
        1 for family in approved.values()
        if True not in family["withdrawn"] and None in family["withdrawn"]
    )
    if not_known:
        # Said out loud, never guessed. The medicines are counted, not named.
        _log.warning(
            "Open Targets did not say whether %d of the %d medicines approved for %s "
            "were withdrawn. Moonlight could not check them for withdrawal.",
            not_known, len(approved), disease.name,
        )
    return [
        Listed(
            id=family_id,
            name=family["name"],
            forms=tuple(family["forms"]),
            sources=tuple(family["sources"]),
        )
        for family_id, family in approved.items()
        if True not in family["withdrawn"]  # one withdrawn form is enough
    ]
