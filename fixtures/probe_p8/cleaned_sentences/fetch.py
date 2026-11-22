"""Study P8b, step 1: ask Open Targets for functionDescriptions. Read-only.
No Moonlight code runs. UniProt is not asked.

It talks to Open Targets only. It writes only under
fixtures/probe_p8/cleaned_sentences/.

Run from the repo root:

    python3 fixtures/probe_p8/cleaned_sentences/fetch.py

Which proteins: the top 25 of every disease in
fixtures/probe_p5/diseases.json (branch probe-baseline, 50 diseases) and
fixtures/probe_p6/diseases.json (branch probe-key-diseases, 9 diseases),
read with "git show" from those probes' saved results/<disease>.json. No id
is typed in. The list is saved as proteins.json.

The field names (functionDescriptions, biotype, approvedSymbol,
approvedName) are in the live schema saved by the P8 follow-up at
../open_targets_function/schema/target_type.json. This script refuses to
run if any is missing there.

One request at a time, at least one second apart. Each raw answer is saved
as responses/<gene id>.json, exactly as sent. index.jsonl has one line per
request. A gene already saved is skipped, so it can be stopped and started
again. The data version is asked before and after.
"""

import json
import pathlib
import subprocess
import time

import requests

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RESPONSES = HERE / "responses"
INDEX = HERE / "index.jsonl"
URL = "https://api.platform.opentargets.org/api/v4/graphql"
PROBES = ["origin/probe-baseline:fixtures/probe_p5/", "origin/probe-key-diseases:fixtures/probe_p6/"]
FIELDS = ["id", "approvedSymbol", "approvedName", "biotype", "functionDescriptions"]
VERSION_QUERY = "query DataVersion { meta { name apiVersion { x y z } dataVersion { year month iteration } } }"
TARGET_QUERY = """
query TargetFunction($targetId: String!) {
  target(ensemblId: $targetId) {
    id
    approvedSymbol
    approvedName
    biotype
    functionDescriptions
  }
}
"""
WAIT_SECONDS = 1.0
_last = [0.0]


def show(spec: str) -> str:
    return subprocess.run(["git", "show", spec], cwd=ROOT, check=True,
                          capture_output=True, text=True).stdout


def send(body: dict) -> requests.Response:
    for attempt in range(6):
        wait = WAIT_SECONDS - (time.monotonic() - _last[0])
        if wait > 0:
            time.sleep(wait)
        try:
            r = requests.post(URL, json=body, timeout=120)
            _last[0] = time.monotonic()
            if r.status_code == 200:
                return r
            trouble = f"HTTP {r.status_code}"
        except requests.RequestException as error:
            _last[0] = time.monotonic()
            trouble = type(error).__name__
        print(f"    trouble ({trouble}), waiting", flush=True)
        with (HERE / "refusals.jsonl").open("a", encoding="utf-8") as noted:
            noted.write(json.dumps({"at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                                    "variables": body["variables"], "what": trouble}) + "\n")
        time.sleep(30 * 2 ** attempt)
    raise SystemExit(f"Open Targets would not answer: {trouble}")


def main() -> None:
    schema = json.loads((HERE.parent / "open_targets_function" / "schema" / "target_type.json")
                        .read_text(encoding="utf-8"))
    names = {f["name"] for f in schema["data"]["__type"]["fields"]}
    missing = [f for f in FIELDS if f not in names]
    if missing:
        raise SystemExit(f"The saved schema has no field called {missing}. Stop.")
    RESPONSES.mkdir(parents=True, exist_ok=True)
    diseases, genes = [], {}
    for probe in PROBES:
        for d in json.loads(show(probe + "diseases.json"))["diseases"]:
            targets = json.loads(show(f"{probe}results/{d['id']}.json"))["targets"]
            diseases.append({"probe": probe.split("/")[-2], "id": d["id"], "name": d["name"],
                             "targets": [t["id"] for t in targets]})
            for t in targets:
                genes.setdefault(t["id"], t["symbol"])
    (HERE / "proteins.json").write_text(json.dumps(
        {"from": PROBES, "diseases": diseases, "proteins": genes}, indent=1) + "\n", encoding="utf-8")
    print(len(diseases), "diseases,", sum(len(d["targets"]) for d in diseases), "slots,",
          len(genes), "different proteins", flush=True)
    (HERE / "data_version_before.json").write_bytes(
        send({"query": VERSION_QUERY, "variables": {}}).content)
    for i, (gene, symbol) in enumerate(genes.items(), 1):
        file = RESPONSES / f"{gene}.json"
        if file.exists():
            continue
        r = send({"query": TARGET_QUERY, "variables": {"targetId": gene}})
        answer = r.json()
        file.write_bytes(r.content)  # exactly as sent
        target = (answer.get("data") or {}).get("target")
        with INDEX.open("a", encoding="utf-8") as index:
            index.write(json.dumps({
                "gene": gene, "symbol": symbol, "file": file.name, "bytes": len(r.content),
                "has_errors": bool(answer.get("errors")), "target_found": target is not None,
                "texts": len(target["functionDescriptions"]) if target else None,
                "at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            }) + "\n")
        if i % 100 == 0:
            print(f"  {i} asked", flush=True)
    (HERE / "data_version_after.json").write_bytes(
        send({"query": VERSION_QUERY, "variables": {}}).content)
    print("done", flush=True)


if __name__ == "__main__":
    main()
