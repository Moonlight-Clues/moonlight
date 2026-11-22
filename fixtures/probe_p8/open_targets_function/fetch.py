"""Study P8 follow-up, step 1: ask Open Targets for its protein function text.
Read-only study. No Moonlight code runs.

It talks to Open Targets only. It writes only under
fixtures/probe_p8/open_targets_function/.

Run from the repo root:

    python3 fixtures/probe_p8/open_targets_function/fetch.py

The field name was not typed from memory. schema/target_type.json is the
live schema's own list of fields on a target, and it holds
"functionDescriptions" with the description "Functional descriptions of
the target gene sourced from UniProt". This script refuses to run if that
field is not in the saved schema file.

The 231 proteins are read from ../diseases.json (the same ones study P8
asked UniProt about). One request at a time, at least one second apart.
Each raw answer is saved as responses/<gene id>.json, exactly as sent.
index.jsonl has one line per request. A gene already saved is skipped.
The data version is asked once before and once after, saved in
data_version_before.json and data_version_after.json.
"""

import json
import pathlib
import time

import requests

HERE = pathlib.Path(__file__).resolve().parent
RESPONSES = HERE / "responses"
INDEX = HERE / "index.jsonl"
URL = "https://api.platform.opentargets.org/api/v4/graphql"
FIELD = "functionDescriptions"
VERSION_QUERY = "query DataVersion { meta { name apiVersion { x y z } dataVersion { year month iteration } } }"
TARGET_QUERY = """
query TargetFunction($targetId: String!) {
  target(ensemblId: $targetId) {
    id
    approvedSymbol
    functionDescriptions
    proteinIds { id source }
  }
}
"""
WAIT_SECONDS = 1.0
_last = [0.0]


def send(body: dict) -> requests.Response:
    for attempt in range(5):
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
        time.sleep(30 * 2 ** attempt)
    raise SystemExit(f"Open Targets would not answer: {trouble}")


def main() -> None:
    schema = json.loads((HERE / "schema" / "target_type.json").read_text(encoding="utf-8"))
    names = [f["name"] for f in schema["data"]["__type"]["fields"]]
    if FIELD not in names:
        raise SystemExit(f"The saved schema has no field called {FIELD}. Stop.")
    RESPONSES.mkdir(parents=True, exist_ok=True)
    (HERE / "data_version_before.json").write_bytes(
        send({"query": VERSION_QUERY, "variables": {}}).content)
    study = json.loads((HERE.parent / "diseases.json").read_text(encoding="utf-8"))["diseases"]
    genes = {}
    for d in study:
        for t in d["targets"]:
            genes.setdefault(t["id"], t["symbol"])
    print(len(genes), "different proteins")
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
                "texts": len(target[FIELD]) if target else None,
                "at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            }) + "\n")
        if i % 25 == 0:
            print(f"  {i} asked", flush=True)
    (HERE / "data_version_after.json").write_bytes(
        send({"query": VERSION_QUERY, "variables": {}}).content)


if __name__ == "__main__":
    main()
