"""Ticket T6. Decide what a disease search keeps.

The batch asks ClinicalTrials.gov for a disease's own name and for each of
Open Targets' synonyms. This file does not ask. It only sorts the answers
it is handed.

What is kept
    Interventional trials only. Expanded-access records and observational
    records are left out. Inside a trial, only drug and biological
    interventions are kept. Placebo is dropped. A trial that is only a
    placebo still counts as a trial, and it adds no medicine.

How a medicine is stored
    The T5 matcher (moonlight/match.py) gets the intervention's name and its
    other names. One Open Targets medicine: store that medicine's id.
    Anything else, including a combination and a name the matcher does not
    know: store the name as ClinicalTrials.gov listed it.

When to stop
    A disease whose own-name search is more than 2,000 trials is skipped.
    Nothing is fetched past the count, and the count is recorded. Its In
    trials tab stays as it is today (MAIN 5, 26 Nov 2026).
    A synonym that is the name, or an exact synonym, of a different Open
    Targets disease is not used.
    A synonym that brings back a trial for a different disease (a trial the
    disease's own name did not return, and whose conditions do not mention
    this disease) is not used.
    The disease's own name is still used, unless that search itself is over
    2,000 trials. Then the whole disease is not stored.
"""

import json
import os
import pathlib
import re
import sqlite3
from typing import Dict, Iterable, List, Optional, Sequence

from moonlight import match

TRIAL_LIMIT = 2000
OT_RELEASE = "26.09"
# The four diseases the ticket's check names, as Open Targets 26.09 ids.
# PSC has no record of its own: Open Targets files it under sclerosing
# cholangitis, with "primary sclerosing cholangitis" as an exact synonym.
# MAIN 5 confirmed MONDO_0018646 is the right PSC record (26 Nov 2026).
CHECK_DISEASES = (
    ("MONDO_0018646", "sclerosing cholangitis"),
    ("MONDO_0100339", "Friedreich ataxia"),
    ("MONDO_0007254", "breast cancer"),
    ("MONDO_0009061", "cystic fibrosis"),
)

INTERVENTIONAL = "INTERVENTIONAL"
KEPT_TYPES = frozenset({"DRUG", "BIOLOGICAL"})
EXACT = "hasExactSynonym"
CTGOV_SOURCE = "ClinicalTrials.gov"
EXAMPLE_LIMIT = 20

_WORD = re.compile(r"(?<![a-z0-9])placebo(?![a-z0-9])")
_PHRASE_EDGE = r"(?<![a-z0-9]){body}(?![a-z0-9])"


def plain(text: str) -> str:
    """Small letters, single spaces, ends trimmed."""
    return " ".join((text or "").split()).casefold()


def mentions(text: str, phrases: Sequence[str]) -> bool:
    """Does the text hold one of these phrases as whole words?

    'FA' does not count as being inside 'Fanconi'. 'sclerosing cholangitis'
    does count inside 'primary sclerosing cholangitis'.
    """
    hay = plain(text)
    for phrase in phrases:
        needle = plain(phrase)
        if not needle:
            continue
        if re.search(_PHRASE_EDGE.format(body=re.escape(needle)), hay):
            return True
    return False


def is_placebo(name: str) -> bool:
    return bool(_WORD.search(plain(name)))


def search_terms(disease: dict) -> List[str]:
    """The disease's name, then every synonym, each wording once.

    Blank terms are left out. A repeat that differs only by capitals or
    the number of spaces is left out. The first wording is the one kept.
    """
    seen = set()
    terms: List[str] = []
    raw = [disease.get("name") or ""]
    for group in disease.get("synonyms") or []:
        raw.extend(group.get("terms") or [])
    for term in raw:
        key = plain(term)
        if not key or key in seen:
            continue
        seen.add(key)
        terms.append(" ".join(term.split()))
    return terms


def exact_index(diseases: Iterable[dict]) -> Dict[str, List[dict]]:
    """plain name or exact synonym -> the diseases that go by that name.

    Only exact synonyms. A related, narrow or broad synonym is a different
    wording, and it is checked later, against the trials it actually returns.
    """
    index: Dict[str, List[dict]] = {}
    for disease in diseases:
        names = [disease.get("name") or ""]
        for group in disease.get("synonyms") or []:
            if group.get("relation") == EXACT:
                names.extend(group.get("terms") or [])
        seen = set()
        for name in names:
            key = plain(name)
            if not key or key in seen:
                continue
            seen.add(key)
            bucket = index.setdefault(key, [])
            if not any(row["id"] == disease["id"] for row in bucket):
                bucket.append({"id": disease["id"], "name": disease["name"]})
    return index


def other_diseases(term: str, disease_id: str, index: Dict[str, List[dict]]) -> List[dict]:
    """Other diseases whose name or exact synonym is this term."""
    found = [row for row in index.get(plain(term), []) if row["id"] != disease_id]
    return sorted(found, key=lambda row: row["id"])


def _nct(study: dict) -> str:
    ident = (study.get("protocolSection") or {}).get("identificationModule") or {}
    return (ident.get("nctId") or "").strip()


def _conditions(study: dict) -> List[str]:
    module = (study.get("protocolSection") or {}).get("conditionsModule") or {}
    return list(module.get("conditions") or [])


def _interventions(study: dict) -> List[dict]:
    module = (study.get("protocolSection") or {}).get("armsInterventionsModule") or {}
    return list(module.get("interventions") or [])


def kept_study(study: dict) -> bool:
    """An interventional trial with at least one drug or biological intervention.

    Placebo still counts here: it is a drug intervention, and the trial stays
    even when every such intervention is later dropped as placebo.
    """
    design = (study.get("protocolSection") or {}).get("designModule") or {}
    if design.get("studyType") != INTERVENTIONAL:
        return False
    for item in _interventions(study):
        if (item.get("type") or "").upper() in KEPT_TYPES:
            return True
    return False


def _label_index(drugs: Sequence[dict]) -> Dict[str, List[dict]]:
    """The matcher's own labels, so a lookup does not rebuild them per name."""
    index: Dict[str, List[dict]] = {}
    for drug in drugs:
        records = [drug] + list(drug.get("childMolecules") or [])
        for record in records:
            for label in match._labels(record):
                key = match._clean(label)
                if not key or match.is_combination(label) or match.COMPONENT_OF in f" {key} ":
                    continue
                index.setdefault(key, []).append(drug)
    return index


def _match_names(names: Sequence[str], by_label: Dict[str, List[dict]]) -> Optional[str]:
    """One medicine id, or None. The decision is match.match, not this file.

    by_label is every Open Targets medicine, not the disease's own list.
    The first name is the medicine's own name. Later names are aliases.
    search_keys picks every catalogue row those pieces might name.
    """
    given = [name for name in names if name and str(name).strip()]
    if not given:
        return None
    seen = set()
    candidates = []
    for key in match.search_keys(given):
        for drug in by_label.get(key, ()):
            if drug["id"] not in seen:
                seen.add(drug["id"])
                candidates.append(drug)
    return match.match(given, candidates)


def _stop(term: str, reason: str, detail: dict) -> dict:
    return {"term": term, "reason": reason, "detail": detail}


def _empty_result(disease: dict, before: dict, name_total: Optional[int], stops: List[dict],
                  stored: bool = False) -> dict:
    return {
        "disease_id": disease["id"],
        "name": disease["name"],
        "stored": stored,
        "terms_used": [],
        "name_trial_total": name_total,
        "trial_ids": [],
        "matched": [],
        "ctgov_only": [],
        "trial_total": None,
        "medicine_total": None,
        "matched_total": None,
        "ctgov_only_total": None,
        "before_trials": before["trials"],
        "before_medicines": before["medicines"],
        "stops": stops,
    }


def assemble(disease: dict, searches: Dict[str, dict], drugs: Sequence[dict],
             index: Dict[str, List[dict]], reports: Sequence[dict],
             parents: Dict[str, str]) -> dict:
    """One disease: the searches it was given, every Open Targets medicine,
    and Open Targets' existing trial rows. searches[term] is {"total", "studies"}.
    studies is None when the search was over the limit and was not fetched.
    The medicine list is the whole catalogue, not the disease's own list.
    """
    terms = search_terms(disease)
    name = terms[0]
    before = before_counts(reports, disease["id"], parents)
    name_search = searches[name]
    if name_search["total"] > TRIAL_LIMIT:
        return _empty_result(disease, before, name_search["total"], [
            _stop(name, "skipped", {"trial_total": name_search["total"]})])

    name_studies = list(name_search.get("studies") or [])
    name_ids = {_nct(study) for study in name_studies if _nct(study)}
    accepted: List[dict] = list(name_studies)
    used = [name]
    stops: List[dict] = []
    for term in terms[1:]:
        found = searches[term]
        if found["total"] > TRIAL_LIMIT:
            stops.append(_stop(term, "over_2000", {"trial_total": found["total"]}))
            continue
        others = other_diseases(term, disease["id"], index)
        studies = list(found.get("studies") or [])
        extras = []
        for study in studies:
            nct = _nct(study)
            if not nct or nct in name_ids:
                continue
            if mentions(" | ".join(_conditions(study)), terms):
                continue
            extras.append(study)
        if others:
            stops.append(_stop(term, "other_disease", {"other_diseases": others}))
        if extras:
            examples = [{"nct_id": _nct(study), "conditions": _conditions(study)}
                        for study in sorted(extras, key=_nct)[:EXAMPLE_LIMIT]]
            stops.append(_stop(term, "extra_trials", {
                "extra_total": len(extras), "examples": examples}))
        if others or extras:
            continue
        used.append(term)
        accepted.extend(studies)

    by_nct: Dict[str, dict] = {}
    for study in accepted:
        nct = _nct(study)
        if nct and nct not in by_nct:
            by_nct[nct] = study

    by_label = _label_index(drugs)
    matched: Dict[str, set] = {}
    listed: Dict[str, set] = {}
    trial_ids = []
    for nct in sorted(by_nct):
        study = by_nct[nct]
        if not kept_study(study):
            continue
        trial_ids.append(nct)
        for item in _interventions(study):
            if (item.get("type") or "").upper() not in KEPT_TYPES:
                continue
            listed_name = item.get("name")
            if not listed_name or not str(listed_name).strip():
                continue
            if is_placebo(listed_name):
                continue
            names = [listed_name] + [other for other in (item.get("otherNames") or []) if other]
            medicine_id = _match_names(names, by_label)
            if medicine_id:
                matched.setdefault(medicine_id, set()).add(nct)
            else:
                listed.setdefault(listed_name, set()).add(nct)

    matched_rows = [{"medicine_id": medicine_id, "nct_ids": sorted(ncts)}
                    for medicine_id, ncts in sorted(matched.items())]
    listed_rows = [{"name": listed_name, "nct_ids": sorted(ncts)}
                   for listed_name, ncts in sorted(listed.items())]
    stops.sort(key=lambda stop: (stop["term"], stop["reason"]))
    return {
        "disease_id": disease["id"],
        "name": disease["name"],
        "stored": True,
        "terms_used": used,
        "name_trial_total": name_search["total"],
        "trial_ids": trial_ids,
        "matched": matched_rows,
        "ctgov_only": listed_rows,
        "trial_total": len(trial_ids),
        "medicine_total": len(matched_rows) + len(listed_rows),
        "matched_total": len(matched_rows),
        "ctgov_only_total": len(listed_rows),
        "before_trials": before["trials"],
        "before_medicines": before["medicines"],
        "stops": stops,
    }


def parent_of(drug_id: str, parents: Dict[str, str]) -> str:
    """Follow parent links to the medicine. A loop stops at the id we started from."""
    seen = set()
    current = drug_id
    while current and current not in seen:
        seen.add(current)
        nxt = parents.get(current)
        if not nxt or nxt == current:
            return current
        current = nxt
    return drug_id


def before_counts(reports: Sequence[dict], disease_id: str, parents: Dict[str, str]) -> dict:
    """Medicines and trials Open Targets already links to this disease.

    A trial counts when its source is ClinicalTrials.gov and the disease is
    on the row. Salt forms of one medicine count as one medicine.
    """
    trials = set()
    medicines = set()
    for row in reports:
        if row.get("source") != CTGOV_SOURCE:
            continue
        disease_ids = {(item or {}).get("diseaseId") for item in (row.get("diseases") or [])}
        if disease_id not in disease_ids:
            continue
        nct = (row.get("id") or "").strip().upper()
        if nct.startswith("NCT"):
            trials.add(nct)
        for drug in row.get("drugs") or []:
            drug_id = (drug or {}).get("drugId")
            if drug_id:
                medicines.add(parent_of(drug_id, parents))
    return {"medicines": len(medicines), "trials": len(trials)}


def canonical(value) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def write_sqlite(path: pathlib.Path, results: Sequence[dict], run_date: str,
                 ot_release: str = OT_RELEASE) -> None:
    """Write the file in one go, in id order, then VACUUM, so the same
    results give the same bytes."""
    ordered = sorted(results, key=lambda result: result["disease_id"])
    counts = {
        "ctgov_only": sum(result["ctgov_only_total"] or 0 for result in ordered),
        "diseases": len(ordered),
        "matched": sum(result["matched_total"] or 0 for result in ordered),
        "medicines": sum(result["medicine_total"] or 0 for result in ordered),
        "stops": sum(len(result["stops"]) for result in ordered),
        "stored": sum(1 for result in ordered if result["stored"]),
        "trials": sum(result["trial_total"] or 0 for result in ordered),
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".building")
    if tmp.exists():
        tmp.unlink()
    con = sqlite3.connect(str(tmp), isolation_level=None)
    try:
        con.execute("PRAGMA page_size = 4096")
        con.execute("PRAGMA journal_mode = OFF")
        con.execute("PRAGMA synchronous = OFF")
        con.execute("BEGIN")
        con.execute("CREATE TABLE meta (run_date TEXT NOT NULL, ot_release TEXT NOT NULL, "
                    "counts TEXT NOT NULL)")
        con.execute("CREATE TABLE diseases ("
                    "disease_id TEXT PRIMARY KEY, name TEXT NOT NULL, stored INTEGER NOT NULL, "
                    "terms_used TEXT NOT NULL, name_trial_total INTEGER, trial_total INTEGER, "
                    "medicine_total INTEGER, matched_total INTEGER, ctgov_only_total INTEGER, "
                    "before_trials INTEGER, before_medicines INTEGER) WITHOUT ROWID")
        con.execute("CREATE TABLE found ("
                    "disease_id TEXT NOT NULL, kind TEXT NOT NULL, medicine_id TEXT NOT NULL, "
                    "name TEXT NOT NULL, nct_ids TEXT NOT NULL, "
                    "PRIMARY KEY (disease_id, kind, medicine_id, name)) WITHOUT ROWID")
        con.execute("CREATE TABLE stops ("
                    "disease_id TEXT NOT NULL, term TEXT NOT NULL, reason TEXT NOT NULL, "
                    "detail TEXT NOT NULL, PRIMARY KEY (disease_id, term, reason)) WITHOUT ROWID")
        con.execute("INSERT INTO meta VALUES (?, ?, ?)", (run_date, ot_release, canonical(counts)))
        con.executemany(
            "INSERT INTO diseases VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            [(result["disease_id"], result["name"], 1 if result["stored"] else 0,
              canonical(result["terms_used"]), result["name_trial_total"], result["trial_total"],
              result["medicine_total"], result["matched_total"], result["ctgov_only_total"],
              result["before_trials"], result["before_medicines"])
             for result in ordered])
        found_rows = []
        for result in ordered:
            if not result["stored"]:
                continue
            for row in result["matched"]:
                found_rows.append((result["disease_id"], "matched", row["medicine_id"], "",
                                   canonical(row["nct_ids"])))
            for row in result["ctgov_only"]:
                found_rows.append((result["disease_id"], "ctgov_only", "", row["name"],
                                   canonical(row["nct_ids"])))
        found_rows.sort()
        con.executemany("INSERT INTO found VALUES (?, ?, ?, ?, ?)", found_rows)
        stop_rows = []
        for result in ordered:
            for stop in result["stops"]:
                stop_rows.append((result["disease_id"], stop["term"], stop["reason"],
                                  canonical(stop["detail"])))
        stop_rows.sort()
        con.executemany("INSERT INTO stops VALUES (?, ?, ?, ?)", stop_rows)
        con.execute("COMMIT")
        con.execute("VACUUM")
    finally:
        con.close()
    os.replace(tmp, path)


def read_sqlite(path: pathlib.Path) -> dict:
    """The file, with JSON columns read back into lists and objects."""
    con = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    try:
        meta = con.execute("SELECT run_date, ot_release, counts FROM meta").fetchone()
        diseases = [dict(row) for row in con.execute(
            "SELECT * FROM diseases ORDER BY disease_id")]
        found = []
        for row in con.execute(
                "SELECT * FROM found ORDER BY disease_id, kind, medicine_id, name"):
            item = dict(row)
            item["nct_ids"] = json.loads(item["nct_ids"])
            found.append(item)
        stops = []
        for row in con.execute("SELECT * FROM stops ORDER BY disease_id, term, reason"):
            item = dict(row)
            item["detail"] = json.loads(item["detail"])
            stops.append(item)
    finally:
        con.close()
    for disease in diseases:
        disease["terms_used"] = json.loads(disease["terms_used"])
    return {
        "meta": {"run_date": meta["run_date"], "ot_release": meta["ot_release"],
                 "counts": json.loads(meta["counts"])},
        "diseases": diseases,
        "found": found,
        "stops": stops,
    }
