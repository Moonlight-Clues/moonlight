"""Night order 2 (probe P6, eight key diseases), step 1: ask Open Targets
through Moonlight's own code. Read-only study. A copy of probe_p5's
probe.py; only the way the diseases are chosen is new.

It talks to Open Targets only. It never calls Moonlight's site or Gemini.
It writes only under fixtures/probe_p6/ (and Moonlight's saved-results
notebook, in the scratch folder named by MOONLIGHT_CACHE_DIR).

Run from the repo root:

    MOONLIGHT_CACHE_DIR=<a scratch folder> python3 fixtures/probe_p6/probe.py

The eight disease names are in NAMES below. Each id is found with
Moonlight's own search (fetch.search_matches, the Open Targets part of
/api/search), never typed in. A name is taken only if the search puts
exactly one entry on top as "exactly what was typed": the entry's name, or
one of its exact "also called" names, is the name asked (capitals and
spaces aside). That is Moonlight's own test, fetch._is_what_was_typed.
More than one such entry, or none: the matches are listed in
searches.json and the name is not studied. Gemini's "did you mean" side
lane is not called. Every search answer is saved under responses/search/.

For each disease it does what moonlight/api.py's _find does, with the same
functions and in the same order: fetch_disease, fetch_targets (top 25),
engine.find_clues, fetch_approved, fetch_withdrawn, engine.fetch_neighbours,
then api._Found (which calls engine.sort_into_tabs). The cards are then
read off with the API's own helpers, and checked against what
api.clues(disease_id) itself answers.

The only thing swapped is fetch._send, the one place Moonlight talks to
Open Targets. The swap sends the very same request, but one at a time, at
least one second after the last one, slows down if Open Targets refuses,
and saves the raw answer under responses/. responses/index.jsonl has one
line per request. An answer that is letter for letter the same as one
already saved is not saved twice: the index line names the file.

It can be stopped and started again: a disease whose results file exists
is skipped, and the notebook remembers good answers for a day.
"""

import hashlib
import json
import logging
import pathlib
import subprocess
import sys
import threading
import time

import requests

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from moonlight import api, engine, fetch, translate  # noqa: E402
from moonlight.filter import GROUPS  # noqa: E402
from moonlight.records import stronger_stage  # noqa: E402

HERE = pathlib.Path(__file__).resolve().parent
RESPONSES = HERE / "responses"
RESULTS = HERE / "results"
INDEX = RESPONSES / "index.jsonl"
WAIT_SECONDS = 1.0
TIMEOUT_SECONDS = 120
TOP_TARGETS = api.TOP_TARGETS  # the number the live site uses
NAMES = (
    "primary sclerosing cholangitis", "interstitial cystitis",
    "primary biliary cholangitis", "neurofibromatosis type 1", "Addison's disease",
    "dermatomyositis", "hemochromatosis", "anaphylaxis",
)
# Also saved, as asked: what the search returns for these exact words.
ALSO_SEARCH = ("anaphylaxis", "drug anaphylaxis")
SLOW_DOWN = (429, 500, 502, 503, 504)  # Open Targets is refusing or busy

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
_refusals = []  # every time Open Targets refused or the network failed
_by_hash = {}  # sha256 of the raw answer -> the file that holds it


def _read_index() -> None:
    if INDEX.exists():
        for line in INDEX.read_text(encoding="utf-8").splitlines():
            entry = json.loads(line)
            _count[0] = max(_count[0], entry["n"])
            _by_hash.setdefault(entry["sha256"], entry["file"])


def send(body: dict) -> dict:
    """Stands in for fetch._send. Same request, one at a time, answer saved."""
    with _lock:
        for attempt in range(6):
            wait = WAIT_SECONDS - (time.monotonic() - _last_sent[0])
            if wait > 0:
                time.sleep(wait)
            trouble = None
            try:
                response = requests.post(fetch.URL, json=body, timeout=TIMEOUT_SECONDS)
                _last_sent[0] = time.monotonic()
                if response.status_code in SLOW_DOWN:
                    trouble = f"HTTP {response.status_code}"
                else:
                    response.raise_for_status()
                    answer = response.json()
                    break
            except (requests.RequestException, ValueError) as error:
                _last_sent[0] = time.monotonic()
                trouble = type(error).__name__
                if attempt == 5:
                    raise
            _refusals.append({"at": _now(), "variables": body["variables"], "what": trouble})
            with (HERE / "refusals.jsonl").open("a", encoding="utf-8") as noted:
                noted.write(json.dumps(_refusals[-1]) + "\n")  # kept even if the run is cut off
            if attempt == 5:
                response.raise_for_status()
            pause = 30 * 2 ** attempt  # slow down: 30 s, 1 min, 2 min, 4 min, 8 min
            print(f"    Open Targets trouble ({trouble}), waiting {pause} s", flush=True)
            time.sleep(pause)
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
                "n": _count[0], "at": _now(), "kind": kind, "variables": body["variables"],
                "bytes": len(raw), "sha256": digest, "file": file,
                "has_errors": bool(answer.get("errors")),
            }) + "\n")
        return answer


def _now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def save(path: pathlib.Path, thing) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(thing, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")


def search(words: str) -> dict:
    """What Moonlight's search finds for these exact words, in its order."""
    matches = fetch.search_matches(words)
    listed = [{"id": m.disease.id, "name": m.disease.name,
               "also_called_exactly": list(m.also_called),
               "exactly_what_was_typed": fetch._is_what_was_typed(words, m),
               "small_print": translate.small_print(words, m)} for m in matches]
    return {"words": words, "matches": listed,
            "exactly_what_was_typed": [m for m in listed if m["exactly_what_was_typed"]]}


def choose_diseases() -> list:
    searches, chosen = [], []
    for name in NAMES:
        found = search(name)
        exact = found["exactly_what_was_typed"]
        if len(exact) == 1:
            found["decision"] = "studied"
            chosen.append({"set": "KEY", "id": exact[0]["id"], "name": exact[0]["name"],
                           "asked_as": name})
        elif exact:
            found["decision"] = "stopped: more than one entry is exactly what was typed"
        else:
            found["decision"] = "stopped: no entry is exactly what was typed"
        searches.append(found)
        print(f"search {name!r}: {found['decision']} "
              f"{[(m['id'], m['name']) for m in exact]}", flush=True)
    extra = [search(words) for words in ALSO_SEARCH]
    save(HERE / "searches.json", {"names": searches, "also_saved": extra})
    return chosen


def list_families(disease_id: str) -> dict:
    """Every medicine family on a disease's own list, from the answer
    Moonlight kept (read back from its notebook, so nothing new is asked).
    Families are joined the way fetch._list_families joins them. Each one
    also keeps every report's source, stage and link."""
    answer = fetch._post_json(
        {"query": fetch.DISEASE_DRUGS_QUERY, "variables": {"diseaseId": disease_id}})
    record = (answer.get("data") or {}).get("disease")
    families = {}
    if record is None:
        return families
    for row in record["drugAndClinicalCandidates"]["rows"]:
        drug = row["drug"]
        if drug is None:
            continue
        parent = drug["parentMolecule"]
        family_id = parent["id"] if parent else drug["id"]
        family = families.setdefault(family_id, {
            "id": family_id, "name": None, "forms": [], "approved_for_disease": False,
            "stage_for_disease": None, "best_stage_of_listed_forms": None,
            "withdrawn_notes": [], "reports": []})
        family["withdrawn_notes"].append(fetch._was_withdrawn(drug))
        if parent:
            family["name"] = family["name"] or parent["name"]
        else:
            family["name"] = drug["name"]
        form = [drug["id"], drug["name"]]
        if form not in family["forms"]:
            family["forms"].append(form)
        if row["maxClinicalStage"] == fetch.APPROVAL and \
                drug["maximumClinicalStage"] == fetch.APPROVAL:
            family["approved_for_disease"] = True
        family["stage_for_disease"] = stronger_stage(
            family["stage_for_disease"], row["maxClinicalStage"])
        family["best_stage_of_listed_forms"] = stronger_stage(
            family["best_stage_of_listed_forms"], drug["maximumClinicalStage"])
        for report in row["clinicalReports"]:
            kept = {"source": report["source"], "stage": report["clinicalStage"],
                    "url": report["url"]}
            if kept not in family["reports"]:
                family["reports"].append(kept)
    return families


def proteins_json(clue, opposite=()) -> list:
    return [{"target_id": path.target.id, "symbol": path.target.symbol,
             "score": path.score, "action_types": list(path.action_types),
             "direction": path.direction, "opposite_way": path.target.id in opposite}
            for path in (clue.paths if clue else ())]


def approved_card(tab: str, medicine, wrong, words) -> dict:
    card = {"tab": tab, "id": medicine.id, "medicine": medicine.name,
            "source": medicine.source_record, "proteins": proteins_json(medicine.clue),
            "label": medicine.label, "proof_note": medicine.proof_note,
            "warning": (words.get(medicine.id, engine.WRONG_WARNING)
                        if medicine.id in wrong else None),
            "approval_sources": list(medicine.approval_sources),
            "regulator_record": medicine.regulator_record}
    return card


def clue_card(tab: str, clue, one_way) -> dict:
    medicine = clue.medicine
    return {"tab": tab, "id": api._clue_id(clue), "medicine": medicine.name,
            "source": api._one_source(clue),
            "proteins": proteins_json(clue, engine.opposite_way(clue, one_way)),
            "disease_stage": medicine.disease_stage}


def same_as_the_api(disease_id: str, cards: list) -> list:
    """Ask api.clues itself (answered from the notebook) and compare: the
    same cards, in the same order, with the same links and the same
    opposite-way lines. -> a list of differences, [] if none."""
    answer = api.clues(disease_id)
    differences = []
    for tab in ("approved", "narrower", "wider_group", "being_studied", "new_clues"):
        mine = [(c["id"], c["source"], [p["symbol"] for p in c["proteins"]],
                 [p["symbol"] for p in c["proteins"] if p["opposite_way"]])
                for c in cards if c["tab"] == tab]
        theirs = [(c["id"], c["source"], [p["symbol"] for p in c["proteins"]],
                   [p["symbol"] for p in c["proteins"] if "opposite_way" in p])
                  for c in answer.get(tab, [])]
        if mine != theirs:
            differences.append(tab)
    return differences


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
    found = api._Found(disease, tray, listed, withdrawn_listed, neighbours)

    wrong = engine.looks_wrong(disease.id)
    words = engine.warning_words(disease.id)
    new_clues, by_hand = api._shown_new_clues(found)
    one_way = engine.one_way_proteins(found.approved, wrong)
    cards = [approved_card("approved", m, wrong, words) for m in found.approved]
    cards += [approved_card("narrower", m, wrong, words) for m in found.narrower]
    cards += [approved_card("wider_group", m, wrong, words) for m in found.wider_group]
    cards += [clue_card("being_studied", clue, one_way) for clue in found.being_studied]
    cards += [clue_card("new_clues", clue, one_way) for clue in new_clues]

    # The lists behind the cards, with every report's source and stage.
    own_list = list_families(disease.id)
    box_ids = {m.id for m in found.narrower + found.wider_group}
    box_lists = {}
    for neighbour in neighbours:
        families = list_families(neighbour.disease.id)
        for family_id in box_ids & set(families):
            box_lists.setdefault(family_id, []).append({
                "role": neighbour.role, "disease_id": neighbour.disease.id,
                "disease": neighbour.disease.name, **families[family_id]})

    in_tray = {}
    for group in GROUPS:
        for path in tray[group]:
            family_id = engine._family_id(path.medicine)
            seen = in_tray.setdefault(family_id, {
                "name": path.medicine.name, "tray_group": group, "targets": [],
                "best_stage": None, "disease_stage": None, "withdrawn": []})
            seen["targets"].append(path.target.symbol)
            seen["best_stage"] = stronger_stage(seen["best_stage"], path.medicine.best_stage)
            seen["disease_stage"] = stronger_stage(
                seen["disease_stage"], path.medicine.disease_stage)
            seen["withdrawn"].append(path.medicine.withdrawn)
            if seen["tray_group"] != group:
                seen["tray_group"] = "more than one"

    return {
        "id": disease.id, "name": disease.name, "set": entry["set"],
        "targets": [{"id": t.id, "symbol": t.symbol, "score": t.score} for t in targets],
        "neighbours": [{"role": n.role, "id": n.disease.id, "name": n.disease.name}
                       for n in neighbours],
        "cards": cards,
        "left_out": found.left_out,
        "new_clues_left_out_by_hand": by_hand,
        "red_warning_ids": sorted(wrong),
        "one_way": one_way,
        "one_way_without_leaving_out_red_warnings": engine.one_way_proteins(found.approved),
        "withdrawn_on_own_list": sorted(entry.id for entry in withdrawn_listed),
        "withdrawn_on_a_neighbour_list": sorted(
            {entry.id for n in neighbours for entry in n.withdrawn}),
        "own_list": own_list,
        "box_lists": box_lists,
        "in_tray": in_tray,
        "differences_from_api_clues": same_as_the_api(disease.id, cards),
    }


def main() -> int:
    _read_index()
    fetch._send = send  # the one swap. fetch.py itself is not changed.
    handler = logging.FileHandler(HERE / "fetch_warnings.log", encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s %(message)s"))
    logging.getLogger("moonlight").addHandler(handler)
    started = _now()
    start_count = _count[0]
    version = fetch.data_version()
    diseases = choose_diseases()
    problems = []
    for number, entry in enumerate(diseases, start=1):
        out = RESULTS / f"{entry['id']}.json"
        if out.exists():
            print(f"{number}/{len(diseases)} {entry['name']}: already done", flush=True)
            continue
        handler.stream.write(f"--- {entry['id']} {entry['name']}\n")
        for attempt in (1, 2, 3):
            try:
                result = study(entry)
                break
            except Exception as error:  # written down, never hidden
                print(f"    {entry['name']}: attempt {attempt} failed: {error!r}"[:400], flush=True)
                result = {"id": entry["id"], "name": entry["name"], "problem": repr(error)[:400]}
                time.sleep(60)
        if "problem" in result:
            problems.append(result)
        else:
            save(out, result)
        tabs = {}
        for card in result.get("cards", []):
            tabs[card["tab"]] = tabs.get(card["tab"], 0) + 1
        print(f"{number}/{len(diseases)} {entry['name']} ({entry['id']}): "
              f"{result.get('problem') or tabs} [requests so far {_count[0]}]", flush=True)
    run = {"started": started, "finished": _now(), "data_version": version,
           "top_targets": TOP_TARGETS,
           "code_commit": subprocess.run(["git", "log", "-1", "--format=%H", "--", "moonlight", "web"], cwd=ROOT,
                                         capture_output=True, text=True).stdout.strip(),
           "requests_sent_this_run": _count[0] - start_count,
           "requests_sent_in_all": _count[0],
           "times_open_targets_refused_or_failed": _refusals, "problems": problems}
    runs = HERE / "runs.json"
    earlier = json.loads(runs.read_text(encoding="utf-8")) if runs.exists() else []
    save(runs, earlier + [run])
    save(HERE / "diseases.json", {"data_version": version, "diseases": diseases})
    print("requests sent this run:", run["requests_sent_this_run"], "problems:", len(problems))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
