"""Night watch P4, step 1: ask Open Targets through Moonlight's own code.

Read-only study. It talks to Open Targets only. It never calls Moonlight's
site or Gemini, and it writes only under fixtures/probe_p4/ (and Moonlight's
saved-results notebook, in the folder named by MOONLIGHT_CACHE_DIR).

Run from the repo root:

    MOONLIGHT_CACHE_DIR=<a scratch folder> python3 fixtures/probe_p4/probe.py

The disease ids come from fixtures/probe_p3/diseases.json on the branch
probe-approval-proof (read with "git show", never typed in): every found
disease of the COMMON set, the first 7 found of CANCER, the first 20 found
of RARE. Acromegaly is added by exact-name search if it is not among them.

For each disease it does what moonlight/api.py's _find does, with the same
functions: fetch_disease, fetch_targets (top 25), find_clues, fetch_approved,
fetch_withdrawn, fetch_neighbours, then engine.sort_into_tabs.

The only thing swapped is fetch._send, the one place Moonlight talks to
Open Targets. The swap sends the very same request, but waits one second
after the last one, tries again on network trouble, and saves the raw
answer under responses/. Moonlight asks each "which medicines?" question
twice; an answer that is letter for letter the same as one already saved is
not saved twice: index.jsonl says which file holds it.

It can be stopped and started again: the notebook remembers good answers
for a day, so they are not asked again.
"""

import hashlib
import json
import pathlib
import subprocess
import sys
import threading
import time

import requests

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from moonlight import engine, fetch  # noqa: E402
from moonlight.filter import GROUPS  # noqa: E402
from moonlight.records import Disease  # noqa: E402

HERE = pathlib.Path(__file__).resolve().parent
RESPONSES = HERE / "responses"
RESULTS = HERE / "results"
INDEX = RESPONSES / "index.jsonl"
WAIT_SECONDS = 1.0
TIMEOUT_SECONDS = 120
TOP_TARGETS = engine.PRELOAD_TARGETS  # 25, the same number api.py's TOP_TARGETS holds
P3 = "origin/probe-approval-proof:fixtures/probe_p3/diseases.json"
TAKE = (("COMMON", None), ("CANCER", 7), ("RARE", 20))

KINDS = {
    fetch.VERSION_QUERY: "data_version",
    fetch.SEARCH_QUERY: "search",
    fetch.DISEASE_QUERY: "disease",
    fetch.FAMILY_QUERY: "family",
    fetch.TARGETS_QUERY: "targets",
    fetch.TARGET_DRUGS_QUERY: "target_drugs",
    fetch.DISEASE_DRUGS_QUERY: "disease_drugs",
}

_lock = threading.Lock()
_last_sent = [0.0]
_count = [0]
_by_hash = {}  # sha256 of the raw answer -> the file that holds it


def _read_index() -> None:
    if INDEX.exists():
        for line in INDEX.read_text(encoding="utf-8").splitlines():
            entry = json.loads(line)
            _count[0] = max(_count[0], entry["n"])
            _by_hash.setdefault(entry["sha256"], entry["file"])


def send(body: dict) -> dict:
    """Stands in for fetch._send. Same request, one second apart, answer saved."""
    with _lock:
        wait = WAIT_SECONDS - (time.monotonic() - _last_sent[0])
        if wait > 0:
            time.sleep(wait)
        for attempt in range(5):
            try:
                response = requests.post(fetch.URL, json=body, timeout=TIMEOUT_SECONDS)
                response.raise_for_status()
                answer = response.json()
                break
            except (requests.RequestException, ValueError) as error:
                _last_sent[0] = time.monotonic()
                if attempt == 4:
                    raise
                print(f"    network trouble ({error!r}), trying again", flush=True)
                time.sleep(5 * 2 ** attempt)
        _last_sent[0] = time.monotonic()
        _count[0] += 1
        raw = response.content
        digest = hashlib.sha256(raw).hexdigest()
        kind = KINDS.get(body["query"], "other")
        about = "_".join(str(v) for v in body["variables"].values()) or "none"
        about = "".join(c if c.isalnum() or c in "_-" else "_" for c in about)[:60]
        file = _by_hash.get(digest)
        if file is None:
            file = f"{kind}/{_count[0]:05d}_{about}.json"
            path = RESPONSES / file
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(raw)  # exactly as sent
            _by_hash[digest] = file
        with INDEX.open("a", encoding="utf-8") as index:
            index.write(json.dumps({
                "n": _count[0], "at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "kind": kind, "variables": body["variables"], "bytes": len(raw),
                "sha256": digest, "file": file,
                "has_errors": bool(answer.get("errors")),
            }) + "\n")
        return answer


def save(path: pathlib.Path, thing) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(thing, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")


def choose_diseases() -> list:
    text = subprocess.run(["git", "show", P3], cwd=ROOT, check=True,
                          capture_output=True, text=True).stdout
    listed = json.loads(text)["diseases"]
    chosen = []
    for set_name, how_many in TAKE:
        found = [d for d in listed if d["set"] == set_name and d["found"]]
        for d in found[:how_many]:
            chosen.append({"set": set_name, "id": d["id"], "name": d["name"],
                           "from": "fixtures/probe_p3/diseases.json"})
    if not any(fetch.plain_words(d["name"]) == "acromegaly" for d in chosen):
        exact = [m.disease for m in fetch.search_matches("acromegaly")
                 if fetch.plain_words(m.disease.name) == "acromegaly"]
        if len(exact) != 1:
            raise SystemExit(f"acromegaly: {len(exact)} exact search hits, stopping")
        chosen.append({"set": "ADDED", "id": exact[0].id, "name": exact[0].name,
                       "from": "Open Targets search, exact name"})
    return chosen


def path_json(path, group=None) -> dict:
    medicine = path.medicine
    out = {
        "medicine_id": engine._family_id(medicine),
        "medicine": medicine.name,
        "forms": [form.name for form in medicine.forms],
        "target_id": path.target.id,
        "target": path.target.symbol,
        "target_name": path.target.name,
        "score": path.score,
        "action_types": list(path.action_types),
        "direction": path.direction,
        "best_stage": medicine.best_stage,
        "disease_stage": medicine.disease_stage,
        "withdrawn": medicine.withdrawn,
    }
    if group:
        out["tray_group"] = group
    return out


def clue_json(clue) -> dict:
    return {"medicine_id": engine._family_id(clue.medicine), "medicine": clue.medicine.name,
            "paths": [path_json(path) for path in clue.paths]}


def approved_json(item) -> dict:
    return {"medicine_id": item.id, "medicine": item.name, "label": item.label,
            "paths": [path_json(path) for path in item.clue.paths] if item.clue else []}


def study(entry: dict) -> dict:
    """What api.py's _find does, with the same functions, in the same order."""
    disease = fetch.fetch_disease(entry["id"])
    if disease is None:
        return {"id": entry["id"], "problem": "Open Targets does not know this id"}
    targets = fetch.fetch_targets(disease, TOP_TARGETS)
    tray = engine.find_clues(disease, targets)
    listed = fetch.fetch_approved(disease)
    withdrawn_listed = fetch.fetch_withdrawn(disease)
    neighbours = engine.fetch_neighbours(disease)
    tabs = engine.sort_into_tabs(tray, listed, withdrawn_listed, neighbours)
    return {
        "id": disease.id, "name": disease.name, "set": entry["set"],
        "targets": [{"id": t.id, "symbol": t.symbol, "name": t.name, "score": t.score}
                    for t in targets],
        "neighbours": [{"role": n.role, "id": n.disease.id, "name": n.disease.name}
                       for n in neighbours],
        "tray": [path_json(path, group) for group in GROUPS for path in tray[group]],
        "approved": [approved_json(item) for item in tabs.approved],
        "narrower": [approved_json(item) for item in tabs.narrower],
        "wider_group": [approved_json(item) for item in tabs.wider_group],
        "being_studied": [clue_json(clue) for clue in tabs.being_studied],
        "new_clues": [clue_json(clue) for clue in tabs.new_clues],
        "left_out": tabs.left_out,
    }


def main() -> int:
    _read_index()
    fetch._send = send  # the one swap. fetch.py itself is not changed.
    started = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    start_count = _count[0]
    version = fetch.data_version()
    diseases = choose_diseases()
    problems = []
    for number, entry in enumerate(diseases, start=1):
        out = RESULTS / f"{entry['id']}.json"
        if out.exists():
            print(f"{number}/{len(diseases)} {entry['name']}: already done", flush=True)
            continue
        for attempt in (1, 2, 3):
            try:
                result = study(entry)
                break
            except (fetch.FetchError, requests.RequestException) as error:
                print(f"    {entry['name']}: attempt {attempt} failed: {error!r}"[:400], flush=True)
                result = {"id": entry["id"], "name": entry["name"],
                          "problem": repr(error)[:400]}
                time.sleep(30)
        if "problem" in result:
            problems.append(result)
        else:
            save(out, result)
        print(f"{number}/{len(diseases)} {entry['name']} ({entry['id']}): "
              + (result.get("problem") or
                 f"{len(result['approved'])} approved, {len(result['being_studied'])} in trials, "
                 f"{len(result['new_clues'])} new clues") + f"  [requests so far {_count[0]}]",
              flush=True)
    run = {"started": started, "finished": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "data_version": version, "top_targets": TOP_TARGETS,
           "requests_sent_this_run": _count[0] - start_count,
           "requests_sent_in_all": _count[0], "diseases": diseases, "problems": problems}
    runs = HERE / "runs.json"
    earlier = json.loads(runs.read_text(encoding="utf-8")) if runs.exists() else []
    save(runs, earlier + [run])
    save(HERE / "diseases.json", {"data_version": version, "diseases": diseases})
    print("requests sent this run:", run["requests_sent_this_run"], "problems:", len(problems))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
