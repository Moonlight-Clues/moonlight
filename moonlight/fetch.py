"""Fetch: ask Open Targets about a disease, its proteins, and their medicines.

Five questions, five functions:

    search_diseases(text)          -> list of Disease, the exact name typed first
    search_matches(text)           -> the same list, each with its "also called" names
    fetch_disease(disease_id)      -> one Disease with its description and its
                                      exact "also called" names filled in
    fetch_targets(disease, limit)  -> list of Target, highest score first
    fetch_paths(disease, target)   -> list of Path, one per Medicine family
    fetch_approved(disease)        -> list of Listed: the medicines Open Targets'
                                      own list says are approved for the disease
    fetch_withdrawn(disease)       -> list of Listed: the medicines on that same
                                      list that were withdrawn in any country
    fetch_family(disease)          -> Family: the disease's direct parents and
                                      direct children, one step only
    fetch_listed_medicines(disease) -> list of OnList: every medicine family on
                                      the disease's own list, as records
                                      (ticket 2.21). The same question again.

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
"parents" and "children" on a disease were read from the live API on
2026-11-16 and are saved in fixtures/family/.
"description" and "synonyms" ("relation", "terms") on a disease were read
from the live API on 2026-11-16 and are saved in
fixtures/MONDO_0015924/disease_about.* and fixtures/MONDO_0100338/disease_about.*.
"clinicalStage" on a clinical report was read from the live API on
2026-11-16 and is saved in fixtures/approval_proof/.
"source" on a clinical report, and its values, were read from the answers
saved in fixtures/probe_p3/ on the branch probe-approval-proof (2026-11-17)
and from the live API on 2026-11-18. They are saved in fixtures/no_regulator/.
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
# "category" list (its groups), and a measurement's list holds this word.
# Nothing is guessed from the name or the id.
# Kashish's decisions, 2026-11-16 (ticket 5.9). Open Targets files some real
# diseases, multiple sclerosis for one, under "measurement" as well as under
# disease groups. So a match is hidden only when "measurement" is its ONLY
# group. And a match whose name, or exact "also called" name, is exactly
# what the person typed is never hidden and always comes first.
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
  disease(efoId: $diseaseId) { id name description synonyms { relation terms } }
}
"""

# Ticket 2.12. One sheet up and one sheet down. "parents" and "children" are
# the direct ones only. "ancestors" and "descendants" go further and are not
# asked for.
FAMILY_QUERY = """
query DiseaseFamily($diseaseId: String!) {
  disease(efoId: $diseaseId) {
    id
    name
    parents { id name }
    children { id name }
  }
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
# Ticket 2.13. Each report is one receipt. "clinicalStage" on the report says
# what kind: "APPROVAL" for an approval record, a phase word for a trial.
# Adding it changed the question's words, so an answer saved for the old
# question is filed under another name and is never read for this one.
# Ticket 2.17. "source" on the report says who wrote the receipt: a
# regulator like "DailyMed", or a second-hand list like "TTD". The same
# goes for this change: old saved answers are never read for the new words.
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
        clinicalReports { url clinicalStage source }
      }
    }
  }
}
"""
APPROVAL = "APPROVAL"  # the stage word for "approved", in both stage fields

# Ticket 2.17, Kashish's decisions of 18 Nov. The Open Targets team told us
# which values of "source" are regulators: the offices that approve
# medicines. An approval report from one of these is a regulator record.
# Compared letter for letter. Nothing that only looks like one counts.
REGULATOR_SOURCES = ("DailyMed", "FDA", "EMA Human Drugs", "PMDA")
# Every value met so far: the regulators, the two second-hand lists the
# team named ("TTD", "ATC"), and three more met in the study of 124
# diseases. None of the others is a regulator. A value that is not here is
# new to Moonlight: it does not count as a regulator either, and it is
# written in the log so Kashish can be told.
KNOWN_SOURCES = REGULATOR_SOURCES + ("TTD", "ATC", "ClinicalTrials.gov", "USAN", "INN")

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


def _exact_terms(groups: Optional[List[dict]]) -> Tuple[str, ...]:
    """The names in the group Open Targets calls exact, word for word and
    in its order. () if there is no such group, or no groups at all."""
    names: List[str] = []
    for group in groups or []:
        if group["relation"] == EXACT_SYNONYM:
            names.extend(group["terms"])
    return tuple(names)


def _exact_names(hit: dict) -> Tuple[str, ...]:
    """The names Open Targets says mean exactly this disease. () if none."""
    return _exact_terms((hit.get("object") or {}).get("synonyms"))


def plain_words(text: str) -> str:
    """Words in small letters with single spaces, for comparing."""
    return " ".join(text.split()).casefold()


def _only_a_measurement(hit: dict) -> bool:
    """Is "measurement" the hit's only group? No groups at all means no."""
    return set(hit.get("category") or []) == {MEASUREMENT}


def _is_what_was_typed(text: str, match: Match) -> bool:
    """Is the entry's name, or one of its exact "also called" names, exactly
    the words typed? Capitals and spaces at the ends do not count."""
    wanted = plain_words(text)
    names = (match.disease.name, *match.also_called)
    return bool(wanted) and wanted in [plain_words(name) for name in names]


def search_matches(text: str) -> List[Match]:
    """Diseases matching the words, each with its exact "also called" names.

    Like a librarian's pile of books. A book is left off the pile only if
    its ONLY shelf is "measurement". The book whose title, or exact "also
    called" title, is exactly what the person asked for is never left off,
    and goes on top. Every other book stays in the order Open Targets
    ranked it.

    An answer saved before 2026-11-13 has no "category" and no "object".
    Then nothing is hidden and there are no "also called" names.
    """
    data = _ask(SEARCH_QUERY, {"text": text, "size": SEARCH_SIZE})
    typed: List[Match] = []
    others: List[Match] = []
    for hit in data["search"]["hits"]:
        if hit["entity"] != "disease":
            continue
        match = Match(
            disease=Disease(id=hit["id"], name=hit["name"]), also_called=_exact_names(hit)
        )
        if _is_what_was_typed(text, match):
            typed.append(match)
        elif not _only_a_measurement(hit):
            others.append(match)
    return typed + others


def search_diseases(text: str) -> List[Disease]:
    """Diseases matching the words: the exact name typed first, then the
    order Open Targets ranks them. Entries that are only measurements are
    left out."""
    return [match.disease for match in search_matches(text)]


def fetch_disease(disease_id: str) -> Optional[Disease]:
    """The disease with its description and its exact "also called" names
    filled in. None if the id is not known.

    Both are Open Targets' own words, kept word for word (ticket 5.5).
    Open Targets may send no description at all. Then it stays "", and
    nothing is made up to fill the gap. An answer saved before 2026-11-16
    has no "synonyms". Then there are no "also called" names.
    """
    data = _ask(DISEASE_QUERY, {"diseaseId": disease_id})
    record = data["disease"]
    if record is None:
        return None
    return Disease(
        id=record["id"],
        name=record["name"],
        description=(record["description"] or "").strip(),
        also_called=_exact_terms(record.get("synonyms")),
    )


@dataclass(frozen=True)
class Family:
    """A disease's direct parents and direct children, in Open Targets' order."""

    parents: Tuple[Disease, ...]
    children: Tuple[Disease, ...]


def fetch_family(disease: Disease) -> Family:
    """The entries one step up and one step down from the disease.

    Like the sheet above and the sheets below in a stack of paper. Only
    one step: not grandparents, not grandchildren. No parents and no
    children if the disease is not known, or if the answer does not hold
    those lists. Nothing is guessed.
    """
    data = _ask(FAMILY_QUERY, {"diseaseId": disease.id})
    record = data["disease"] or {}

    def entries(field: str) -> Tuple[Disease, ...]:
        found: Dict[str, Disease] = {}
        for entry in record.get(field) or []:
            if entry["id"] != disease.id:  # never the disease itself
                found.setdefault(entry["id"], Disease(id=entry["id"], name=entry["name"]))
        return tuple(found.values())

    return Family(parents=entries("parents"), children=entries("children"))


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

    approval_sources (ticket 2.13) holds only the links of the reports whose
    own stage is approval: the approval receipts. A trial's link is in
    sources but not here. It is empty if the answer did not say each
    report's stage, as answers saved before ticket 2.13 did not: nothing
    is guessed.

    regulator_record (ticket 2.17) answers: does the family, all its forms
    together, have a report whose stage is approval and whose source is one
    of REGULATOR_SOURCES? True: yes. False: none of the family's approval
    reports is a regulator's, or it has no approval report, or it has no
    report of any kind. None: not said. The family HAS reports and none of
    them carries a source value, as in answers saved before ticket 2.17.
    Not said is not the same as no (Kashish, 18 Nov).
    """

    id: str  # the id shared by the medicine and its tablet forms
    name: str
    forms: Tuple[Tuple[str, str], ...]
    sources: Tuple[str, ...]
    # Always True from fetch_approved. fetch_withdrawn also hands over
    # families that are only in trials for the disease: then it is False.
    approved: bool = True
    approval_sources: Tuple[str, ...] = ()
    regulator_record: Optional[bool] = None


def _list_families(disease: Disease) -> Dict[str, dict]:
    """Every medicine family on the disease's own list, by family id, with
    what was gathered about it. {} if the disease is not known."""
    data = _ask(DISEASE_DRUGS_QUERY, {"diseaseId": disease.id})
    if data["disease"] is None:
        return {}

    rows = data["disease"]["drugAndClinicalCandidates"]["rows"]
    # Ticket 2.17. Every source value named anywhere in this answer.
    met = {report.get("source") for row in rows for report in row["clinicalReports"]}
    never_met = sorted(source for source in met if source and source not in KNOWN_SOURCES)
    if never_met:
        # Said out loud, never guessed. Only the source's own name is written.
        _log.warning(
            "Open Targets named a report source Moonlight has never met: %s. "
            "It does not count as a regulator. Please tell Kashish.",
            ", ".join(never_met),
        )

    families: Dict[str, dict] = {}  # family id -> what we have gathered so far
    for row in rows:
        drug = row["drug"]
        if drug is None:
            continue
        parent = drug["parentMolecule"]
        family_id = parent["id"] if parent else drug["id"]
        family = families.setdefault(
            family_id,
            {"name": None, "forms": [], "sources": [], "approved": False, "withdrawn": [],
             "approval_sources": [], "reports": 0, "source_said": False,
             "regulator_report": False, "records": [], "stage_reports": []},
        )
        # Ticket 2.21. The same form as a record: how far it got for any
        # disease, and how far for THIS disease (the row's own stage).
        record = MedicineForm(
            id=drug["id"],
            name=drug["name"],
            best_stage=drug["maximumClinicalStage"],
            disease_stage=row["maxClinicalStage"],
            parent_id=parent["id"] if parent else None,
            withdrawn=_was_withdrawn(drug),
        )
        if record.id not in [known.id for known in family["records"]]:
            if parent:
                family["records"].append(record)
            else:
                family["records"].insert(0, record)  # the parent itself goes first
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
            # Ticket 2.21. Each link once, with the stage of its own report.
            if url and url not in [link for link, _ in family["stage_reports"]]:
                family["stage_reports"].append((url, report.get("clinicalStage")))
            # .get: an answer to the old question has no stage on its reports.
            is_approval = report.get("clinicalStage") == APPROVAL
            if url and is_approval and url not in family["approval_sources"]:
                family["approval_sources"].append(url)
            # Ticket 2.17. The source is matched exactly. No source, or one
            # that is not on the list, is not a regulator. A link is not needed.
            family["reports"] += 1
            if report.get("source"):
                family["source_said"] = True
            if is_approval and report.get("source") in REGULATOR_SOURCES:
                family["regulator_report"] = True
    return families


def _regulator_record(family: dict) -> Optional[bool]:
    """Does the family have an approval report from a regulator?

    Like checking a folder of receipts. A regulator's approval receipt in
    it: True. An empty folder: False, there is no such receipt. Receipts
    that all have the "who wrote this" corner torn off: None, not said.
    Anything else: False.
    """
    if family["regulator_report"]:
        return True
    if family["reports"] and not family["source_said"]:
        return None
    return False


def _as_listed(family_id: str, family: dict) -> Listed:
    return Listed(
        id=family_id,
        name=family["name"],
        forms=tuple(family["forms"]),
        sources=tuple(family["sources"]),
        approved=family["approved"],
        approval_sources=tuple(family["approval_sources"]),
        regulator_record=_regulator_record(family),
    )


@dataclass(frozen=True)
class OnList:
    """One medicine family on the disease's own list, as records (ticket 2.21).

    medicine holds the family's forms that are on the list, the parent
    first if it has a row. Each form's best_stage is how far it got for any
    disease, and its disease_stage is how far it got for THIS disease, both
    in Open Targets' words. A form that is not on the list is not here:
    the list says nothing about its stages, so nothing is guessed.

    reports holds (link, stage) for each report link, once: the stage is
    that report's own, or None if the answer did not say.
    """

    medicine: Medicine
    reports: Tuple[Tuple[str, Optional[str]], ...]


def fetch_listed_medicines(disease: Disease) -> List[OnList]:
    """Every medicine family on the disease's own list, approved for it or
    not, in the order Open Targets first mentions them. The same question
    as fetch_approved, so it is answered from the saved results. [] if the
    disease is not known.

    Nothing is sorted into groups here. engine.py does that, with the rule
    in filter.py.
    """
    return [
        OnList(
            medicine=Medicine(name=family["name"], forms=family["records"]),
            reports=tuple(family["stage_reports"]),
        )
        for family in _list_families(disease).values()
    ]


def fetch_withdrawn(disease: Disease) -> List[Listed]:
    """The families on the disease's own list with a form that was withdrawn
    in any country (ticket 2.11), approved for this disease or not. The same
    question as fetch_approved, so it is answered from the saved results.
    [] if the list holds no withdrawn note: nothing is guessed.
    """
    return [
        _as_listed(family_id, family)
        for family_id, family in _list_families(disease).items()
        if True in family["withdrawn"]  # one withdrawn form is enough
    ]


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
    families = _list_families(disease)
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
        _as_listed(family_id, family)
        for family_id, family in approved.items()
        if True not in family["withdrawn"]  # one withdrawn form is enough
    ]
