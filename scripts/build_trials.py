"""Ticket T2 (fuller trials). Build moonlight/trials.sqlite.

One row for every ClinicalTrials.gov study that Open Targets 26.09 links to a
disease, interventional studies only (studyType INTERVENTIONAL; expanded-access
and observational records are left out). Each row holds a small copy of the
study's ClinicalTrials.gov API v2 JSON, with only the fields ticket T1 needs.

Where the NCT numbers come from
    Open Targets Platform 26.09, dataset "clinical_report"
    (https://ftp.ebi.ac.uk/pub/databases/opentargets/platform/26.09/output/clinical_report/00000000.parquet).
    A row counts when its "source" is "ClinicalTrials.gov" and at least one of
    its "diseases" has a "diseaseId". Its "id" ("nct00785291") is upper-cased
    to the NCT number. This is the same report the API hands Moonlight as
    clinicalReports { url } on a disease's medicine list. Reading the parquet
    needs pyarrow, at build time only. The ids read are saved in the cache as
    ot_nct_ids.json, so a second run needs neither pyarrow nor the parquet.

Where the study details come from
    ClinicalTrials.gov API v2, GET /api/v2/studies with filter.ids (500 NCT
    numbers a call: 1,000 makes the address too long, HTTP 414), pageSize
    1000 and a fields= projection (FIELDS below). No key. One call at most
    every MIN_SECONDS_BETWEEN_CALLS seconds (30 a minute, under the about 50
    a minute ClinicalTrials.gov allows). A 429 or 5xx answer waits and tries
    again (BACKOFF_SECONDS); after that the run stops and says so. A 403
    stops it at once. Every answer is saved, gzip'd, under the cache folder,
    so a run with --offline rebuilds the same file without the network.

What is stored, per study (one JSON object, keys in sorted order):
    {"protocolSection": {
       "identificationModule": {"nctId", "briefTitle"},
       "statusModule": {"overallStatus", "startDateStruct",
                        "completionDateStruct", "lastUpdatePostDateStruct"},
       "designModule": {"studyType", "phases"},
       "armsInterventionsModule": {
           "armGroups": [{"label", "type", "interventionNames"}],
           "interventions": [{"name", "type", "otherNames", "armGroupLabels"}]}}}
    A key ClinicalTrials.gov leaves out is left out here too (so a study with
    no arms module has none), so T1's functions see the same shapes they see
    in a full saved study.

How the file is compressed (read with the standard library only)
    Table "studies" (nct_id TEXT PRIMARY KEY, start_date, last_update, study
    BLOB) WITHOUT ROWID. "study" is the JSON above, UTF-8, compressed with
    zlib (level 9) using a preset dictionary. The dictionary is stored once,
    in the meta row ("zdict"). To read one study:

        import json, sqlite3, zlib
        con = sqlite3.connect("file:moonlight/trials.sqlite?mode=ro", uri=True)
        zdict = con.execute("SELECT zdict FROM meta").fetchone()[0]
        blob = con.execute("SELECT study FROM studies WHERE nct_id = ?",
                           ("NCT00785291",)).fetchone()[0]
        d = zlib.decompressobj(zdict=zdict)
        study = json.loads(d.decompress(blob) + d.flush())

    (read_study below does exactly this.) A preset dictionary makes each row
    about a quarter of its plain zlib size, and the file is opened in place:
    nothing has to be unpacked at app start. "start_date" and "last_update"
    are copies of startDateStruct.date and lastUpdatePostDateStruct.date, kept
    plain so trials can be sorted newest first without opening every row.

    nct_id is the NCT number as Open Targets gives it. When ClinicalTrials.gov
    answers with a study under a newer number (the old one is in its
    nctIdAliases), the row is kept under Open Targets' number, and the JSON
    holds ClinicalTrials.gov's own nctId.

The meta table has one row: run_date, ot_release, ctgov_api_version,
ctgov_data_timestamp, compression, counts (JSON, sorted keys) and zdict.

Same input, same file: rows are written in NCT order, JSON keys are sorted,
the dictionary is built from the rows themselves, and the only date written is
the run date, which --run-date sets (default: today). Two runs from the same
cache give byte-identical files.

    python scripts/build_trials.py --ot-parquet clinical_report.parquet \
        --cache /path/to/cache [--offline] [--run-date 2026-11-26] \
        [--out moonlight/trials.sqlite]
"""

import argparse
import datetime
import gzip
import json
import os
import pathlib
import sqlite3
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import zlib
from typing import Callable, Dict, Iterable, List, Optional, Tuple

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "moonlight" / "trials.sqlite"

OT_RELEASE = "26.09"
OT_SOURCE = ("https://ftp.ebi.ac.uk/pub/databases/opentargets/platform/26.09/"
             "output/clinical_report/00000000.parquet")
CTGOV_SOURCE = "ClinicalTrials.gov"

API = "https://clinicaltrials.gov/api/v2/studies"
VERSION_API = "https://clinicaltrials.gov/api/v2/version"
BATCH = 500
PAGE_SIZE = 1000
MIN_SECONDS_BETWEEN_CALLS = 2.0
BACKOFF_SECONDS = (30, 60, 120, 240, 480)
TIMEOUT_SECONDS = 120
USER_AGENT = "moonlight-build-trials/1 (+https://github.com/Moonlight-Clues/moonlight)"

FIELDS = (
    "protocolSection.identificationModule.nctId",
    "protocolSection.identificationModule.nctIdAliases",
    "protocolSection.identificationModule.briefTitle",
    "protocolSection.statusModule.overallStatus",
    "protocolSection.statusModule.startDateStruct",
    "protocolSection.statusModule.completionDateStruct",
    "protocolSection.statusModule.lastUpdatePostDateStruct",
    "protocolSection.designModule.studyType",
    "protocolSection.designModule.phases",
    "protocolSection.armsInterventionsModule.armGroups.label",
    "protocolSection.armsInterventionsModule.armGroups.type",
    "protocolSection.armsInterventionsModule.armGroups.interventionNames",
    "protocolSection.armsInterventionsModule.interventions.name",
    "protocolSection.armsInterventionsModule.interventions.type",
    "protocolSection.armsInterventionsModule.interventions.otherNames",
    "protocolSection.armsInterventionsModule.interventions.armGroupLabels",
)

# What is kept of each module (anything else ClinicalTrials.gov sends is dropped).
KEEP = {
    "identificationModule": ("nctId", "briefTitle"),
    "statusModule": ("overallStatus", "startDateStruct", "completionDateStruct",
                     "lastUpdatePostDateStruct"),
    "designModule": ("studyType", "phases"),
}
ARM_KEYS = ("label", "type", "interventionNames")
INTERVENTION_KEYS = ("name", "type", "otherNames", "armGroupLabels")
DATE_KEYS = ("date", "type")

INTERVENTIONAL = "INTERVENTIONAL"
EXPANDED_ACCESS = "EXPANDED_ACCESS"
OBSERVATIONAL = "OBSERVATIONAL"

COMPRESSION = "zlib-level9-preset-dictionary-v1"
ZDICT_BYTES = 32768
ZDICT_SAMPLES = 400
PAGE_BYTES = 4096


class StopAndAsk(RuntimeError):
    """ClinicalTrials.gov refused the batch, or the file is too big. Stop, report."""


# ---------------------------------------------------------------- Open Targets

def nct_ids_from_reports(rows: Iterable[dict]) -> Tuple[List[str], Dict[str, int]]:
    """Open Targets clinical_report rows -> (sorted NCT numbers linked to a
    disease, counts). Pure: no file, no network."""
    seen_ctgov = set()
    linked = set()
    for row in rows:
        if row.get("source") != CTGOV_SOURCE:
            continue
        nct = (row.get("id") or "").strip().upper()
        if not nct.startswith("NCT"):
            continue
        seen_ctgov.add(nct)
        if any((d or {}).get("diseaseId") for d in (row.get("diseases") or [])):
            linked.add(nct)
    counts = {"ot_ctgov_reports": len(seen_ctgov),
              "ot_nct_linked_to_disease": len(linked),
              "ot_nct_without_disease": len(seen_ctgov - linked)}
    return sorted(linked), counts


def read_ot_parquet(path: pathlib.Path) -> List[dict]:
    """The clinical_report parquet, as plain rows. Needs pyarrow (build time only)."""
    import pyarrow.parquet as pq  # noqa: WPS433 - optional, build-time only
    return pq.read_table(str(path), columns=["id", "source", "diseases"]).to_pylist()


def ot_ids(cache: pathlib.Path, parquet: Optional[pathlib.Path]) -> Tuple[List[str], Dict[str, int]]:
    """NCT numbers from the parquet, saved to the cache; or from the cache."""
    saved = cache / "ot_nct_ids.json"
    if parquet is not None:
        ids, counts = nct_ids_from_reports(read_ot_parquet(parquet))
        write_json_file(saved, {"counts": counts, "ids": ids, "release": OT_RELEASE,
                                "source": OT_SOURCE})
        return ids, counts
    found = json.loads(saved.read_text(encoding="utf-8"))
    if found.get("release") != OT_RELEASE:
        raise ValueError(f"{saved} is for Open Targets {found.get('release')}, not {OT_RELEASE}")
    return list(found["ids"]), dict(found["counts"])


# ---------------------------------------------------------- ClinicalTrials.gov

def batches(ids: List[str], size: int = BATCH) -> List[List[str]]:
    return [ids[i:i + size] for i in range(0, len(ids), size)]


def batch_url(ids: List[str], page_token: Optional[str] = None) -> str:
    query = [("filter.ids", ",".join(ids)), ("fields", ",".join(FIELDS)),
             ("pageSize", str(PAGE_SIZE)), ("format", "json")]
    if page_token:
        query.append(("pageToken", page_token))
    return API + "?" + urllib.parse.urlencode(query, safe=",")


def http_get(url: str) -> Tuple[int, bytes]:
    """One real GET. Returns (status, body). The one place the network is used."""
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT,
                                                   "Accept": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as answer:
            return answer.status, answer.read()
    except urllib.error.HTTPError as error:
        return error.code, error.read()


class Fetcher:
    """Asks ClinicalTrials.gov politely: a gap between calls, waits on 429/5xx,
    stops (StopAndAsk) on 403 or when the waits run out."""

    def __init__(self, get: Callable[[str], Tuple[int, bytes]] = http_get,
                 sleep: Callable[[float], None] = time.sleep,
                 clock: Callable[[], float] = time.monotonic,
                 gap: float = MIN_SECONDS_BETWEEN_CALLS,
                 backoff: Tuple[float, ...] = BACKOFF_SECONDS,
                 log: Callable[[str], None] = lambda text: None):
        self.get, self.sleep, self.clock, self.gap, self.backoff = get, sleep, clock, gap, backoff
        self.log = log
        self.calls = 0
        self.refusals = 0
        self._last = None

    def _wait_gap(self):
        if self._last is not None:
            left = self.gap - (self.clock() - self._last)
            if left > 0:
                self.sleep(left)

    def json(self, url: str) -> dict:
        for attempt in range(len(self.backoff) + 1):
            self._wait_gap()
            self._last = self.clock()
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
                self.refusals += 1
                if attempt < len(self.backoff):
                    self.log(f"answer {status}; waiting {self.backoff[attempt]} s")
                    self.sleep(self.backoff[attempt])
                    continue
                raise StopAndAsk(f"ClinicalTrials.gov kept refusing ({status}) after "
                                 f"{attempt + 1} tries: {body[:200]!r}")
            raise StopAndAsk(f"ClinicalTrials.gov answered {status}: {body[:200]!r}")
        raise AssertionError("not reached")

    def batch(self, ids: List[str]) -> dict:
        """Every study for these ids, following nextPageToken if there is one."""
        studies, token = [], None
        while True:
            page = self.json(batch_url(ids, token))
            studies.extend(page.get("studies") or [])
            token = page.get("nextPageToken")
            if not token:
                return {"studies": studies}


def write_json_file(path: pathlib.Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(canonical(value), encoding="utf-8")
    os.replace(tmp, path)


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


def fetch_all(ids: List[str], cache: pathlib.Path, offline: bool,
              fetcher: Optional[Fetcher] = None,
              log: Callable[[str], None] = lambda text: None) -> Tuple[List[dict], dict]:
    """All studies for these ids, from the cache or ClinicalTrials.gov.
    Returns (studies, version) where version is the saved /api/v2/version."""
    fetcher = fetcher or Fetcher(log=log)
    folder = cache / "ctgov"
    version_file = cache / "ctgov_version.json"
    if version_file.exists():
        version = json.loads(version_file.read_text(encoding="utf-8"))
    elif offline:
        raise FileNotFoundError(f"offline, and {version_file} is not saved")
    else:
        version = fetcher.json(VERSION_API)
        write_json_file(version_file, version)
    studies: List[dict] = []
    groups = batches(ids)
    for number, group in enumerate(groups):
        file = folder / f"batch_{number:05d}.json.gz"
        saved = read_gzip_json(file) if file.exists() else None
        if saved is None or saved.get("ids") != group:
            if offline:
                raise FileNotFoundError(f"offline, and batch {number} is not saved in {file}")
            saved = {"ids": group, "response": fetcher.batch(group)}
            write_gzip_json(file, saved)
            log(f"batch {number + 1}/{len(groups)}: {len(saved['response']['studies'])} studies, "
                f"{fetcher.calls} calls so far")
        studies.extend(saved["response"]["studies"])
    return studies, version


# ------------------------------------------------------------------ the rows

def _date(value) -> Optional[dict]:
    if not isinstance(value, dict):
        return None
    kept = {key: value[key] for key in DATE_KEYS if key in value}
    return kept or None


def project(study: dict) -> dict:
    """The small copy of one v2 study: only the fields T1 needs, nothing added."""
    section = study.get("protocolSection") or {}
    out: Dict[str, dict] = {}
    for module, keys in KEEP.items():
        found = section.get(module)
        if not isinstance(found, dict):
            continue
        kept = {}
        for key in keys:
            if key not in found:
                continue
            value = found[key]
            if key.endswith("Struct"):
                value = _date(value)
                if value is None:
                    continue
            kept[key] = value
        out[module] = kept
    arms = section.get("armsInterventionsModule")
    if isinstance(arms, dict):
        module = {}
        if "armGroups" in arms:
            module["armGroups"] = [{key: arm[key] for key in ARM_KEYS if key in arm}
                                   for arm in arms.get("armGroups") or []]
        if "interventions" in arms:
            module["interventions"] = [{key: item[key] for key in INTERVENTION_KEYS if key in item}
                                       for item in arms.get("interventions") or []]
        out["armsInterventionsModule"] = module
    return {"protocolSection": out}


def canonical(value) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sort_rows(ids: List[str], studies: List[dict]) -> Tuple[List[Tuple[str, dict]], Dict[str, int]]:
    """Match each returned study to the NCT numbers asked for (its own number
    or one of its nctIdAliases) and keep interventional ones.
    Returns ([(ot_nct_id, projected study)] in NCT order, counts)."""
    asked = set(ids)
    by_id: Dict[str, dict] = {}
    aliased = 0
    for study in studies:
        ident = (study.get("protocolSection") or {}).get("identificationModule") or {}
        own = (ident.get("nctId") or "").upper()
        names = [own] + [str(a).upper() for a in ident.get("nctIdAliases") or []]
        for name in names:
            if name in asked and name not in by_id:
                by_id[name] = study
                if name != own:
                    aliased += 1
    rows = []
    counts = {"requested": len(ids), "found": len(by_id), "not_found": len(asked - set(by_id)),
              "found_under_newer_nct": aliased, "kept_interventional": 0,
              "dropped_observational": 0, "dropped_expanded_access": 0,
              "dropped_other_or_missing_study_type": 0}
    for nct in sorted(by_id):
        study = by_id[nct]
        kind = ((study.get("protocolSection") or {}).get("designModule") or {}).get("studyType")
        if kind == INTERVENTIONAL:
            rows.append((nct, project(study)))
            counts["kept_interventional"] += 1
        elif kind == OBSERVATIONAL:
            counts["dropped_observational"] += 1
        elif kind == EXPANDED_ACCESS:
            counts["dropped_expanded_access"] += 1
        else:
            counts["dropped_other_or_missing_study_type"] += 1
    return rows, counts


def make_zdict(blobs: List[bytes]) -> bytes:
    """A preset dictionary built only from the rows: evenly spaced rows, joined,
    the last ZDICT_BYTES kept (zlib reaches the end of a dictionary first)."""
    if not blobs:
        return b""
    step = max(1, len(blobs) // ZDICT_SAMPLES)
    sample = b"".join(blobs[i] for i in range(0, len(blobs), step))
    return sample[-ZDICT_BYTES:]


def compress(data: bytes, zdict: bytes) -> bytes:
    packer = zlib.compressobj(9, zlib.DEFLATED, 15, 9, zlib.Z_DEFAULT_STRATEGY, zdict) \
        if zdict else zlib.compressobj(9)
    return packer.compress(data) + packer.flush()


def decompress(blob: bytes, zdict: bytes) -> bytes:
    unpacker = zlib.decompressobj(zdict=zdict) if zdict else zlib.decompressobj()
    return unpacker.decompress(blob) + unpacker.flush()


def _struct_date(study: dict, key: str) -> Optional[str]:
    return ((study["protocolSection"].get("statusModule") or {}).get(key) or {}).get("date")


def write_sqlite(out: pathlib.Path, rows: List[Tuple[str, dict]], meta: dict) -> None:
    """Write the file in one go, rows in NCT order, then VACUUM: the same rows
    give the same bytes."""
    blobs = [canonical(study).encode("utf-8") for _, study in rows]
    zdict = make_zdict(blobs)
    out.parent.mkdir(parents=True, exist_ok=True)
    tmp = out.with_name(out.name + ".building")
    if tmp.exists():
        tmp.unlink()
    con = sqlite3.connect(str(tmp), isolation_level=None)
    try:
        con.execute(f"PRAGMA page_size = {PAGE_BYTES}")
        con.execute("PRAGMA journal_mode = OFF")
        con.execute("PRAGMA synchronous = OFF")
        con.execute("BEGIN")
        con.execute("CREATE TABLE meta (run_date TEXT NOT NULL, ot_release TEXT NOT NULL, "
                    "ot_source TEXT NOT NULL, ctgov_api_version TEXT, ctgov_data_timestamp TEXT, "
                    "compression TEXT NOT NULL, counts TEXT NOT NULL, zdict BLOB NOT NULL)")
        con.execute("CREATE TABLE studies (nct_id TEXT PRIMARY KEY, start_date TEXT, "
                    "last_update TEXT, study BLOB NOT NULL) WITHOUT ROWID")
        con.execute("INSERT INTO meta VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (meta["run_date"], OT_RELEASE, OT_SOURCE, meta.get("ctgov_api_version"),
                     meta.get("ctgov_data_timestamp"), COMPRESSION, canonical(meta["counts"]),
                     zdict))
        con.executemany("INSERT INTO studies VALUES (?, ?, ?, ?)",
                        [(nct, _struct_date(study, "startDateStruct"),
                          _struct_date(study, "lastUpdatePostDateStruct"), compress(blob, zdict))
                         for (nct, study), blob in zip(rows, blobs)])
        con.execute("COMMIT")
        con.execute("VACUUM")
    finally:
        con.close()
    os.replace(tmp, out)


def read_study(path: pathlib.Path, nct_id: str) -> Optional[dict]:
    """One saved study as v2 JSON, or None. Standard library only."""
    con = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    try:
        zdict = con.execute("SELECT zdict FROM meta").fetchone()[0]
        found = con.execute("SELECT study FROM studies WHERE nct_id = ?",
                            (nct_id.upper(),)).fetchone()
    finally:
        con.close()
    if found is None:
        return None
    return json.loads(decompress(found[0], zdict).decode("utf-8"))


def build(ids: List[str], ot_counts: Dict[str, int], studies: List[dict], version: dict,
          out: pathlib.Path, run_date: str) -> dict:
    datetime.date.fromisoformat(run_date)  # a real date, or this raises
    rows, counts = sort_rows(ids, studies)
    counts = dict(sorted({**ot_counts, **counts}.items()))
    meta = {"run_date": run_date, "counts": counts,
            "ctgov_api_version": version.get("apiVersion"),
            "ctgov_data_timestamp": version.get("dataTimestamp")}
    write_sqlite(out, rows, meta)
    return meta


MAX_BYTES = 50 * 1024 * 1024


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--ot-parquet", type=pathlib.Path,
                        help="Open Targets 26.09 clinical_report parquet. Without it, "
                             "the ids saved in the cache are used.")
    parser.add_argument("--cache", type=pathlib.Path, required=True)
    parser.add_argument("--out", type=pathlib.Path, default=OUT)
    parser.add_argument("--run-date", default=datetime.date.today().isoformat())
    parser.add_argument("--offline", action="store_true",
                        help="use only saved answers; fail if one is missing")
    args = parser.parse_args(argv)

    def log(text: str) -> None:
        print(f"{datetime.datetime.now().isoformat(timespec='seconds')} {text}", flush=True)

    started = time.monotonic()
    ids, ot_counts = ot_ids(args.cache, args.ot_parquet)
    log(f"Open Targets {OT_RELEASE}: {len(ids)} NCT numbers linked to a disease {ot_counts}")
    fetcher = Fetcher(log=log)
    try:
        studies, version = fetch_all(ids, args.cache, args.offline, fetcher, log)
    except StopAndAsk as error:
        log(f"STOP AND ASK: {error} (calls made: {fetcher.calls})")
        return 3
    meta = build(ids, ot_counts, studies, version, args.out, args.run_date)
    size = args.out.stat().st_size
    log(f"wrote {args.out} ({size} bytes); calls this run: {fetcher.calls}, "
        f"refusals: {fetcher.refusals}; {time.monotonic() - started:.0f} s")
    log("counts " + canonical(meta["counts"]))
    if size > MAX_BYTES:
        log(f"STOP AND ASK: the file is {size} bytes, over 50 MB")
        return 4
    return 0


if __name__ == "__main__":
    sys.exit(main())
