"""Ticket T6. Search ClinicalTrials.gov for each disease and store the result.

The disease's own name is searched, then each Open Targets synonym. Only
interventional drug and biological trials are asked for. Placebo is dropped.
Each intervention is stored as a matched medicine id, or as the name
ClinicalTrials.gov listed when it does not match one medicine.

A disease whose own-name search is more than 2,000 trials is skipped: the
count is recorded and the studies are not downloaded. A synonym that names a
different disease, or that returns trials of a different disease, is not
used. Both are written into the stops table. MAIN 5 confirmed this on
26 Nov 2026, including keeping out "cholangitis, sclerosing", "FA", "CF"
and "Fibrocystic disease", and MONDO_0018646 as the PSC record.

Names are matched against every Open Targets medicine in --drug-file
(output/drug_molecule), not only the medicines on that disease's list.
The name matcher is moonlight/match.py (T5, with the bracket and "(drug)"
follow-up). This batch does not read moonlight/trials.sqlite.

Open Targets facts come from the 26.09 files, not from a live question:
    --disease-file   output/disease (id, name, synonyms)
    --drug-file      output/drug_molecule, every medicine (id, name, parentId,
                     synonyms, tradeNames), not one disease's list
    --report-file    output/clinical_report (id, source, drugs, diseases)
A .json file is read as written. A .parquet file needs pyarrow, at build time
only. Tests pass the JSON.

ClinicalTrials.gov is the only network. One call at a time, with a gap, and
every answer is saved under --cache. A second run with --offline reads the
cache and writes the same file. Same --run-date, same bytes.

The check diseases (ticket T6):
    MONDO_0018646  sclerosing cholangitis
                   (primary sclerosing cholangitis is an exact synonym: PSC)
    MONDO_0100339  Friedreich ataxia                          (a rare disease)
    MONDO_0007254  breast cancer                              (a common cancer)
    MONDO_0009061  cystic fibrosis        (many combination products, under 2,000)

    python scripts/build_disease_search.py \
        --diseases MONDO_0018646 MONDO_0100339 MONDO_0007254 MONDO_0009061 \
        --disease-file disease.parquet --drug-file drug_molecule.parquet \
        --report-file clinical_report.parquet \
        --cache /path/to/cache --run-date 2026-11-26 \
        --out moonlight/disease_search.sqlite
"""

import argparse
import datetime
import gzip
import hashlib
import json
import os
import pathlib
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Callable, Dict, List, Optional, Sequence, Tuple

ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from moonlight import disease_search  # noqa: E402

OUT = ROOT / "moonlight" / "disease_search.sqlite"
API = "https://clinicaltrials.gov/api/v2/studies"
FILTER = ("AREA[StudyType]INTERVENTIONAL AND "
          "(AREA[InterventionType]DRUG OR AREA[InterventionType]BIOLOGICAL)")
FIELDS = ",".join((
    "protocolSection.identificationModule.nctId",
    "protocolSection.designModule.studyType",
    "protocolSection.conditionsModule.conditions",
    "protocolSection.armsInterventionsModule.interventions.name",
    "protocolSection.armsInterventionsModule.interventions.type",
    "protocolSection.armsInterventionsModule.interventions.otherNames",
))
MIN_SECONDS_BETWEEN_CALLS = 2.0
BACKOFF_SECONDS = (30, 60, 120, 240, 480)
TIMEOUT_SECONDS = 120
USER_AGENT = "moonlight-disease-search/1 (+https://github.com/Moonlight-Clues/moonlight)"
CACHE_PREFIX = "v1|" + FILTER + "|"


class StopAndAsk(RuntimeError):
    """ClinicalTrials.gov refused the batch. Stop and report it."""


def canonical(value) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def studies_url(term: str, page_size: int, page_token: Optional[str] = None) -> str:
    quoted = '"' + " ".join(term.replace('"', " ").split()) + '"'
    query = [("query.cond", quoted), ("filter.advanced", FILTER), ("fields", FIELDS),
             ("pageSize", str(page_size)), ("countTotal", "true"), ("format", "json")]
    if page_token:
        query.append(("pageToken", page_token))
    return API + "?" + urllib.parse.urlencode(query)


def http_get(url: str) -> Tuple[int, bytes]:
    """One real GET. The one place this batch uses the network."""
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT,
                                                   "Accept": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as answer:
            return answer.status, answer.read()
    except urllib.error.HTTPError as error:
        return error.code, error.read()


class Fetcher:
    """A gap between calls. A 429 or a 5xx waits and tries again. A 403 stops."""

    def __init__(self, get: Callable[[str], Tuple[int, bytes]] = http_get,
                 sleep: Callable[[float], None] = time.sleep,
                 clock: Callable[[], float] = time.monotonic,
                 gap: float = MIN_SECONDS_BETWEEN_CALLS,
                 backoff: Tuple[float, ...] = BACKOFF_SECONDS,
                 log: Callable[[str], None] = lambda text: None):
        self.get, self.sleep, self.clock = get, sleep, clock
        self.gap, self.backoff, self.log = gap, backoff, log
        self.calls = 0
        self._last = None

    def _wait_gap(self) -> None:
        if self._last is not None and self.gap > 0:
            left = self.gap - (self.clock() - self._last)
            if left > 0:
                self.sleep(left)
        self._last = self.clock()

    def json(self, url: str) -> dict:
        for attempt in range(len(self.backoff) + 1):
            self._wait_gap()
            self.calls += 1
            try:
                status, body = self.get(url)
            except (urllib.error.URLError, OSError) as error:
                status, body = 0, str(error).encode()
            if status == 200:
                return json.loads(body.decode("utf-8"))
            if status == 403:
                raise StopAndAsk(f"ClinicalTrials.gov answered 403 (blocked): {body[:200]!r}")
            if status == 429 or status >= 500 or status == 0:
                if attempt < len(self.backoff):
                    self.log(f"answer {status}; waiting {self.backoff[attempt]} s")
                    self.sleep(self.backoff[attempt])
                    continue
                raise StopAndAsk(f"ClinicalTrials.gov kept refusing ({status}) after "
                                 f"{attempt + 1} tries: {body[:200]!r}")
            raise StopAndAsk(f"ClinicalTrials.gov answered {status}: {body[:200]!r}")
        raise AssertionError("not reached")


def cache_path(cache: pathlib.Path, term: str) -> pathlib.Path:
    digest = hashlib.sha256((CACHE_PREFIX + term).encode("utf-8")).hexdigest()
    return cache / "ctgov" / f"{digest}.json.gz"


def write_gzip_json(path: pathlib.Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "wb") as raw, gzip.GzipFile(fileobj=raw, mode="wb", mtime=0,
                                                filename="") as out:
        out.write(canonical(value).encode("utf-8"))
    os.replace(tmp, path)


def read_gzip_json(path: pathlib.Path):
    with gzip.open(path, "rb") as file:
        return json.loads(file.read().decode("utf-8"))


def fetch_term(term: str, fetcher: Fetcher, cache: pathlib.Path, offline: bool) -> dict:
    """{"total", "studies"}. studies is None when the total is over the limit:
    the studies are not downloaded."""
    path = cache_path(cache, term)
    if path.exists():
        return read_gzip_json(path)
    if offline:
        raise FileNotFoundError(f"offline, and {term!r} is not saved in {path}")
    probe = fetcher.json(studies_url(term, 1))
    total = int(probe["totalCount"])
    if total > disease_search.TRIAL_LIMIT:
        saved = {"total": total, "studies": None}
        write_gzip_json(path, saved)
        return saved
    if total == 0:
        saved = {"total": 0, "studies": []}
        write_gzip_json(path, saved)
        return saved
    studies: List[dict] = []
    token = None
    while True:
        page = fetcher.json(studies_url(term, 1000, token))
        total = int(page.get("totalCount", total))
        studies.extend(page.get("studies") or [])
        token = page.get("nextPageToken")
        if not token or len(studies) >= total or len(studies) > disease_search.TRIAL_LIMIT:
            break
    if total > disease_search.TRIAL_LIMIT:
        saved = {"total": total, "studies": None}
    else:
        saved = {"total": total, "studies": studies}
    write_gzip_json(path, saved)
    return saved


def _rows(path: pathlib.Path, columns: Optional[Sequence[str]] = None) -> list:
    if path.suffix == ".json":
        return json.loads(path.read_text(encoding="utf-8"))
    import pyarrow.parquet as pq  # build time only; tests pass JSON
    table = pq.read_table(str(path), columns=list(columns) if columns else None)
    return table.to_pylist()


def load_diseases(path: pathlib.Path) -> List[dict]:
    rows = _rows(path, ["id", "name", "synonyms"])
    diseases = []
    for row in rows:
        synonyms = row.get("synonyms")
        if isinstance(synonyms, list):
            diseases.append({"id": row["id"], "name": row["name"], "synonyms": synonyms})
            continue
        synonyms = synonyms or {}
        diseases.append({
            "id": row["id"],
            "name": row["name"],
            "synonyms": [
                {"relation": "hasExactSynonym", "terms": list(synonyms.get("hasExactSynonym") or [])},
                {"relation": "hasRelatedSynonym",
                 "terms": list(synonyms.get("hasRelatedSynonym") or [])},
                {"relation": "hasNarrowSynonym", "terms": list(synonyms.get("hasNarrowSynonym") or [])},
                {"relation": "hasBroadSynonym", "terms": list(synonyms.get("hasBroadSynonym") or [])},
            ],
        })
    return diseases


def load_drugs(path: pathlib.Path) -> List[dict]:
    rows = _rows(path, ["id", "name", "parentId", "synonyms", "tradeNames"])
    drugs = []
    for row in rows:
        if "parentMolecule" in row:
            parent = row.get("parentMolecule")
        else:
            parent_id = row.get("parentId")
            parent = {"id": parent_id} if parent_id else None
        drugs.append({
            "id": row["id"],
            "name": row.get("name") or "",
            "parentMolecule": parent,
            "synonyms": row.get("synonyms") or [],
            "tradeNames": row.get("tradeNames") or [],
            "childMolecules": row.get("childMolecules") or [],
        })
    return drugs


def load_reports(path: pathlib.Path) -> List[dict]:
    return _rows(path, ["id", "source", "drugs", "diseases"])


def parent_map(drugs: Sequence[dict]) -> Dict[str, str]:
    found = {}
    for drug in drugs:
        parent = drug.get("parentMolecule") or {}
        if isinstance(parent, dict) and parent.get("id"):
            found[drug["id"]] = parent["id"]
    return found


def main(argv: Optional[Sequence[str]] = None, *,
         get: Callable[[str], Tuple[int, bytes]] = http_get,
         sleep: Callable[[float], None] = time.sleep,
         clock: Callable[[], float] = time.monotonic,
         gap: float = MIN_SECONDS_BETWEEN_CALLS) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--diseases", nargs="+", required=True,
                        help="Open Targets disease ids")
    parser.add_argument("--disease-file", type=pathlib.Path, required=True)
    parser.add_argument("--drug-file", type=pathlib.Path, required=True)
    parser.add_argument("--report-file", type=pathlib.Path, required=True)
    parser.add_argument("--cache", type=pathlib.Path, required=True)
    parser.add_argument("--out", type=pathlib.Path, default=OUT)
    parser.add_argument("--run-date", default=datetime.date.today().isoformat())
    parser.add_argument("--offline", action="store_true")
    args = parser.parse_args(list(argv) if argv is not None else None)
    datetime.date.fromisoformat(args.run_date)

    def log(text: str) -> None:
        print(f"{datetime.datetime.now().isoformat(timespec='seconds')} {text}", flush=True)

    diseases = {row["id"]: row for row in load_diseases(args.disease_file)}
    missing = [disease_id for disease_id in args.diseases if disease_id not in diseases]
    if missing:
        log("STOP AND ASK: unknown disease id(s): " + ", ".join(missing))
        return 4
    drugs = load_drugs(args.drug_file)
    reports = load_reports(args.report_file)
    index = disease_search.exact_index(diseases.values())
    parents = parent_map(drugs)
    fetcher = Fetcher(get=get, sleep=sleep, clock=clock, gap=gap, log=log)

    results = []
    try:
        for disease_id in args.diseases:
            disease = diseases[disease_id]
            terms = disease_search.search_terms(disease)
            log(f"{disease_id} {disease['name']}: {len(terms)} search terms")
            searches = {}
            for term in terms:
                found = fetch_term(term, fetcher, args.cache, args.offline)
                searches[term] = found
                log(f"  {found['total']} trials for {term!r}")
                if term == terms[0] and found["total"] > disease_search.TRIAL_LIMIT:
                    log(f"  skipped: {term!r} is {found['total']} trials, over "
                        f"{disease_search.TRIAL_LIMIT}. No search is stored. "
                        "The In trials tab stays as it is today.")
                    break
            results.append(disease_search.assemble(
                disease, searches, drugs, index, reports, parents))
    except StopAndAsk as error:
        log(f"STOP AND ASK: {error} (calls made: {fetcher.calls})")
        if results:
            disease_search.write_sqlite(args.out, results, args.run_date)
            log(f"wrote the {len(results)} disease(s) finished before the stop to {args.out}")
        return 3
    except FileNotFoundError as error:
        log(f"STOP AND ASK: {error}")
        return 3

    disease_search.write_sqlite(args.out, results, args.run_date)
    size = args.out.stat().st_size
    saved = disease_search.read_sqlite(args.out)
    log(f"wrote {args.out} ({size} bytes); calls this run: {fetcher.calls}")
    log("counts " + canonical(saved["meta"]["counts"]))
    for disease in saved["diseases"]:
        log(f"{disease['disease_id']} {disease['name']}: "
            f"before {disease['before_medicines']} medicines, {disease['before_trials']} trials; "
            f"stored={disease['stored']} trials={disease['trial_total']} "
            f"medicines={disease['medicine_total']} "
            f"(matched {disease['matched_total']}, "
            f"only on ClinicalTrials.gov {disease['ctgov_only_total']})")
    for stop in saved["stops"]:
        log(f"recorded {stop['disease_id']} {stop['reason']} {stop['term']!r} "
            + canonical(stop["detail"])[:500])
    return 0


if __name__ == "__main__":
    sys.exit(main())
