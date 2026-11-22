"""Study P8 (UniProt), step 1: fetch. Read-only study. No Moonlight code runs.

It talks to UniProt only (rest.uniprot.org). It writes only under
fixtures/probe_p8/.

Run from the repo root:

    python3 fixtures/probe_p8/fetch.py

Which diseases: ten of the 50 in fixtures/probe_p5/diseases.json (branch
probe-baseline, read with "git show"): the first 4 of the COMMON set, the
first 3 of CANCER and the first 3 of RARE, in that file's order. No id is
typed in. Their top 25 proteins are read from probe_p5's saved
results/<disease>.json, so they are the same 25 Moonlight used that night.

For each protein (an Ensembl gene id) it asks UniProt one question:
"which reviewed human entries point at this Ensembl gene?" The raw answer
is saved, gzipped, as responses/<gene id>.json.gz. If that finds nothing it
asks a second question by gene name, saved as responses/<gene id>.byname.json.gz.
index.jsonl has one line per request. One request at a time, at least one
second apart. A gene whose answer is already saved is skipped, so it can be
stopped and started again.
"""

import gzip
import json
import pathlib
import subprocess
import time

import requests

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RESPONSES = HERE / "responses"
INDEX = HERE / "index.jsonl"
P5 = "origin/probe-baseline:fixtures/probe_p5/"
SEARCH = "https://rest.uniprot.org/uniprotkb/search"
PICK = {"COMMON": 4, "CANCER": 3, "RARE": 3}
WAIT_SECONDS = 1.0
HEADERS = {"User-Agent": "probe-p8-study (python-requests)"}

_last = [0.0]


def show(path: str) -> str:
    return subprocess.run(["git", "show", P5 + path], cwd=ROOT, check=True,
                          capture_output=True, text=True).stdout


def choose() -> list:
    left = dict(PICK)
    chosen = []
    for d in json.loads(show("diseases.json"))["diseases"]:
        if left.get(d["set"], 0) > 0:
            left[d["set"]] -= 1
            chosen.append(d)
    return chosen


def ask(gene: str, query: str, file: pathlib.Path) -> int:
    """One GET. Saves the raw bytes gzipped. Returns how many entries came back."""
    for attempt in range(5):
        wait = WAIT_SECONDS - (time.monotonic() - _last[0])
        if wait > 0:
            time.sleep(wait)
        try:
            r = requests.get(SEARCH, params={"query": query, "format": "json", "size": 25},
                             headers=HEADERS, timeout=120)
            _last[0] = time.monotonic()
            if r.status_code == 200:
                break
            trouble = f"HTTP {r.status_code}"
        except requests.RequestException as error:
            _last[0] = time.monotonic()
            trouble = type(error).__name__
        print(f"    trouble ({trouble}), waiting", flush=True)
        time.sleep(20 * 2 ** attempt)
    else:
        raise SystemExit(f"UniProt would not answer for {gene}: {trouble}")
    n = len(r.json()["results"])
    with file.open("wb") as raw, gzip.GzipFile(fileobj=raw, mode="wb", mtime=0) as z:
        z.write(r.content)  # exactly as sent
    with INDEX.open("a", encoding="utf-8") as index:
        index.write(json.dumps({
            "gene": gene, "query": query, "file": file.name, "entries": n,
            "bytes": len(r.content), "release": r.headers.get("x-uniprot-release"),
            "release_date": r.headers.get("x-uniprot-release-date"),
            "at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }) + "\n")
    return n


def main() -> None:
    RESPONSES.mkdir(parents=True, exist_ok=True)
    chosen = choose()
    for d in chosen:
        d["targets"] = json.loads(show(f"results/{d['id']}.json"))["targets"]
        # Open Targets' own "also called" names, from probe_p5's saved answer.
        listing = subprocess.run(
            ["git", "ls-tree", "-r", "--name-only", P5.split(":")[0], P5.split(":")[1] + "responses/disease/"],
            cwd=ROOT, check=True, capture_output=True, text=True).stdout.split()
        saved = [p for p in listing if p.endswith(f"_{d['id']}.json")][0]
        record = json.loads(show(saved[len(P5.split(":")[1]):]))["data"]["disease"]
        d["exact_synonyms"] = sorted({t for s in record["synonyms"] or []
                                      if s["relation"] == "hasExactSynonym" for t in s["terms"]})
        print(d["id"], d["name"], len(d["targets"]), "proteins")
    (HERE / "diseases.json").write_text(json.dumps(
        {"from": P5, "rule": PICK, "diseases": chosen}, indent=1) + "\n", encoding="utf-8")
    genes = {}
    for d in chosen:
        for t in d["targets"]:
            genes.setdefault(t["id"], t["symbol"])
    print(len(genes), "different proteins")
    for i, (gene, symbol) in enumerate(genes.items(), 1):
        first = RESPONSES / f"{gene}.json.gz"
        if first.exists():
            continue
        n = ask(gene, f"xref:ensembl-{gene} AND reviewed:true AND organism_id:9606", first)
        how = "by Ensembl id"
        if n == 0:
            n = ask(gene, f"gene_exact:{symbol} AND reviewed:true AND organism_id:9606",
                    RESPONSES / f"{gene}.byname.json.gz")
            how = "by gene name"
        print(f"  {i:3d} {gene} {symbol}: {n} entr{'y' if n == 1 else 'ies'} {how}", flush=True)


if __name__ == "__main__":
    main()
