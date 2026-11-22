"""Probe P7: ask the ClinicalTrials.gov register. Read-only study.

Every request goes through ask(): one request at a time, at least GAP seconds
apart, and every answer is saved byte for byte under responses/ with one line
in responses/index.jsonl. The script can be stopped and started again: a
request that already has a saved answer is not asked again.

    python3 fixtures/probe_p7/probe.py controls   # data version + how the register answers a made-up number
    python3 fixtures/probe_p7/probe.py cards      # part A: one request per NCT link on a card
    python3 fixtures/probe_p7/probe.py own        # part A: the own-list NCT links, 100 numbers per request
    python3 fixtures/probe_p7/probe.py missing    # part A: every number a 100-request did not return, asked alone
    python3 fixtures/probe_p7/probe.py known      # part B
    python3 fixtures/probe_p7/probe.py counts     # part C

Only the fields this study needs are asked for (FIELDS below), so that the
saved answers stay small. Field names were checked against the register's
own answers, not assumed.
"""

import hashlib
import json
import pathlib
import re
import sys
import time

import requests

HERE = pathlib.Path(__file__).resolve().parent
RESP = HERE / "responses"
INDEX = RESP / "index.jsonl"
API = "https://clinicaltrials.gov/api/v2/"
GAP = 1.0
TIMEOUT = 60
TRIES = 4
BATCH = 100
# A plain name with no project or person in it.
HEADERS = {"User-Agent": "register-read/1.0 (python-requests; one request at a time)",
           "Accept": "application/json"}
FIELDS = ("NCTId|NCTIdAlias|OverallStatus|StatusVerifiedDate|LastUpdatePostDate|"
          "PrimaryCompletionDate|PrimaryCompletionDateType|CompletionDate|CompletionDateType|"
          "StudyType|Phase|Condition|InterventionType|InterventionName")

session = requests.Session()
session.headers.update(HEADERS)
_last = [0.0]


def now():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def load_index():
    done = {}
    if INDEX.exists():
        for line in INDEX.read_text().splitlines():
            row = json.loads(line)
            if row.get("final"):
                done[(row["kind"], row["name"])] = row
    return done


DONE = load_index()
N = [sum(1 for _ in INDEX.open()) if INDEX.exists() else 0]


def http_get(url, params):
    """The one function that touches the network."""
    wait = _last[0] + GAP - time.time()
    if wait > 0:
        time.sleep(wait)
    try:
        return session.get(url, params=params, timeout=TIMEOUT)
    finally:
        _last[0] = time.time()


def ask(kind, name, path, params=None):
    """Ask once (again only if told to slow down or the connection fails), save, index."""
    key = (kind, name)
    if key in DONE:
        return DONE[key]
    row = None
    for attempt in range(1, TRIES + 1):
        N[0] += 1
        row = {"n": N[0], "at": now(), "kind": kind, "name": name, "path": path,
               "params": params or {}, "try": attempt}
        try:
            r = http_get(API + path, params)
        except requests.RequestException as e:
            row.update({"status": None, "error": type(e).__name__, "final": attempt == TRIES})
            with INDEX.open("a") as f:
                f.write(json.dumps(row) + "\n")
            time.sleep(10 * attempt)
            continue
        body = r.content
        slow = r.status_code in (429, 500, 502, 503, 504)
        row.update({"status": r.status_code, "bytes": len(body),
                    "sha256": hashlib.sha256(body).hexdigest(),
                    "final": (not slow) or attempt == TRIES})
        folder = RESP / kind
        folder.mkdir(parents=True, exist_ok=True)
        fname = f"{name}.json" if attempt == 1 else f"{name}.try{attempt}.json"
        (folder / fname).write_bytes(body)
        row["file"] = f"{kind}/{fname}"
        with INDEX.open("a") as f:
            f.write(json.dumps(row) + "\n")
        if not slow:
            break
        time.sleep(30 * attempt)
    DONE[key] = row
    return row


def body_of(row):
    return json.loads((RESP / row["file"]).read_bytes())


def inputs():
    return json.loads((HERE / "inputs" / "nct_links.json").read_text())


def controls():
    ask("control", "version", "version")
    ask("control", "made_up_NCT99999999", "studies/NCT99999999", {"fields": FIELDS})
    ask("control", "made_up_in_a_list", "studies",
        {"filter.ids": "NCT05965700,NCT99999999", "fields": FIELDS, "pageSize": 100,
         "countTotal": "true"})


def cards():
    ncts = sorted({c["nct"] for d in inputs()["diseases"] for c in d["card_links"]})
    for i, n in enumerate(ncts, 1):
        row = ask("card", n, f"studies/{n}", {"fields": FIELDS})
        if i % 50 == 0:
            print(f"cards {i}/{len(ncts)} last status {row['status']}", flush=True)


def own_only():
    data = inputs()["diseases"]
    on_cards = {c["nct"] for d in data for c in d["card_links"]}
    return sorted({n for d in data for n in d["own_list_ncts"]} - on_cards)


def own():
    ncts = own_only()
    groups = [ncts[i:i + BATCH] for i in range(0, len(ncts), BATCH)]
    for i, g in enumerate(groups, 1):
        row = ask("own_batch", f"{i:04d}_{g[0]}_{g[-1]}", "studies",
                  {"filter.ids": ",".join(g), "fields": FIELDS, "pageSize": BATCH,
                   "countTotal": "true"})
        if i % 20 == 0:
            print(f"own batches {i}/{len(groups)} last status {row['status']}", flush=True)


def missing():
    asked, got = set(), set()
    for (kind, name), row in sorted(DONE.items()):
        if kind != "own_batch":
            continue
        asked |= set(row["params"]["filter.ids"].split(","))
        if row["status"] == 200:
            for s in body_of(row).get("studies", []):
                got.add(s["protocolSection"]["identificationModule"]["nctId"])
    left = sorted(asked - got)
    print(f"asked in lists {len(asked)}, came back {len(got)}, to ask alone {len(left)}", flush=True)
    for i, n in enumerate(left, 1):
        ask("own_single", n, f"studies/{n}", {"fields": FIELDS})
        if i % 50 == 0:
            print(f"alone {i}/{len(left)}", flush=True)


def pages(kind, name, params):
    """Ask a search and every following page. Returns the rows of the pages."""
    rows, token, page = [], None, 1
    while True:
        p = dict(params)
        if token:
            p["pageToken"] = token
        row = ask(kind, f"{name}.p{page:03d}", "studies", p)
        rows.append(row)
        if row["status"] != 200:
            break
        token = body_of(row).get("nextPageToken")
        if not token:
            break
        page += 1
    return rows


KNOWN = json.loads((HERE / "known_questions.json").read_text()) if (HERE / "known_questions.json").exists() else {}
TEN = json.loads((HERE / "ten_diseases.json").read_text()) if (HERE / "ten_diseases.json").exists() else {}


def slug(text):
    return re.sub(r"[^A-Za-z0-9]+", "_", text).strip("_")


def known():
    ask("known", "NCT05965700_fields", "studies/NCT05965700", {"fields": FIELDS})
    for q in KNOWN["searches"]:
        base = {"fields": FIELDS, "pageSize": 1000, "countTotal": "true"}
        pages("known", "intr_" + slug(q["intervention"]),
              dict(base, **{"query.intr": q["intervention"]}))
        pages("known", "intr_" + slug(q["intervention"]) + "__cond_" + slug(q["condition"]),
              dict(base, **{"query.intr": q["intervention"], "query.cond": q["condition"]}))


def counts():
    for d in TEN["diseases"]:
        rows = pages("count", slug(d["id"]),
                     {"query.cond": d["search_words"],
                      "filter.advanced": "AREA[StudyType]INTERVENTIONAL",
                      "fields": "NCTId|StudyType", "pageSize": 1000, "countTotal": "true"})
        print(d["id"], d["search_words"], "pages", len(rows), flush=True)


if __name__ == "__main__":
    RESP.mkdir(exist_ok=True)
    for step in sys.argv[1:]:
        {"controls": controls, "cards": cards, "own": own, "missing": missing,
         "known": known, "counts": counts}[step]()
