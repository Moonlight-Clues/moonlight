#!/usr/bin/env python3
"""Moonlight nightly flagger (spec A8). Reads the live site, writes a list of suspect cards.

It never touches the site, moonlight/*.py, moonlight/*.json or web/. Output goes to
flags/<date>.csv, flags/<date>.md and checked.json in the repo root (branch `flagger` only).

  python3 tools/flagger/flagger.py plan   [--budget 0.90]   # walk live site, read labels, write requests; no money spent
  python3 tools/flagger/flagger.py submit --yes             # send the batch, poll, download (needs ANTHROPIC_API_KEY)
  python3 tools/flagger/flagger.py report                   # results -> flags/<date>.csv, .md, checked.json

Work files (labels, cards, requests, results) live in --work (default /workspace/flagger/work), outside git.
Key: ANTHROPIC_API_KEY from the environment only. It is never printed, logged or written.
Reuses docs/benchmarks/2026-11-24/: prompt (build_requests.SYSTEM), submit_batch (batch calls, prices), score (parse, norm).
"""
import argparse, concurrent.futures as cf, csv, hashlib, importlib.util, json, os, re, subprocess, sys, time
import threading
import xml.etree.ElementTree as ET
import requests

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
BENCH = os.path.join(REPO, "docs", "benchmarks", "2026-11-24")
LIVE = "https://moonlightclues.com"
UA = {"User-Agent": "MoonlightFlagger/0.1 (+https://github.com/Moonlight-Clues/moonlight)"}
TAB_LISTS = ("approved", "narrower", "wider_group")   # the Approved tab: main list and both folded boxes
MAX_LABEL_CHARS = 15000
OUT_ALLOWANCE = 250        # output tokens per card used in the estimate (JSON answer is ~100)
MAX_TOKENS = 700           # per request ceiling (benchmark used 1500)
HARD_CAP = 1.00
FLAG_VERDICTS = ("NO", "UNCLEAR", "NO_LABEL")


def _load(name, filename):
    spec = importlib.util.spec_from_file_location(name, os.path.join(BENCH, filename))
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    return mod


def bench():
    return _load("bench_build", "build_requests.py"), _load("bench_submit", "submit_batch.py"), _load("bench_score", "score.py")


# ---------------------------------------------------------------- live site
def get_json(path, params=None, tries=4):
    last = None
    for i in range(tries):
        try:
            r = requests.get(LIVE + path, params=params, headers=UA, timeout=180)
            if r.status_code == 200:
                return r.json()
            last = f"HTTP {r.status_code}"
        except requests.RequestException as e:
            last = type(e).__name__
        time.sleep(2 * (i + 1))
    raise RuntimeError(f"{path} {params}: {last}")


def fingerprint():
    v = get_json("/api/version")
    return v.get("fingerprint", ""), v.get("revision", "")


def walk_cards(disease_ids, workers=4):
    """Every card on the Approved tab of every page. Returns (cards, failed_disease_ids)."""
    cards, failed = [], []

    def one(d):
        return d, get_json("/api/clues", {"disease_id": d})

    with cf.ThreadPoolExecutor(workers) as ex:
        futs = [ex.submit(one, d) for d in disease_ids]
        for fu in futs:
            try:
                d, page = fu.result()
            except Exception as e:  # keep going; report the page
                failed.append(str(e)[:120]); continue
            red = set(page.get("wrong_approvals_box") or [])
            seen = set()
            for lst in TAB_LISTS:
                for m in page.get(lst) or []:
                    if m["id"] in seen:
                        continue
                    seen.add(m["id"])
                    cards.append({
                        "disease_id": page["disease"]["id"], "disease": page["disease"]["name"],
                        "medicine_id": m["id"], "medicine": m["medicine"], "forms": m.get("forms") or [],
                        "source": m.get("source") or "", "list": lst,
                        "red": bool(m.get("warning")) or m["id"] in red,
                        "also_called": ((page.get("about_disease") or {}).get("also_called") or [])[:12],
                    })
    return cards, failed


def card_key(c):
    return f"{c['disease_id']}|{c['medicine_id']}"


# ---------------------------------------------------------------- labels
_ema_lock = threading.Lock()


def _get(url, tries=6, spaced=False):
    """GET with a back-off on 429 and 5xx. spaced=True: one at a time, 1.5 s apart (EMA rate-limits)."""
    r = None
    for i in range(tries):
        if spaced:
            with _ema_lock:
                r = requests.get(url, headers=UA, timeout=120)
                time.sleep(1.5)
        else:
            r = requests.get(url, headers=UA, timeout=180)
        if r.status_code not in (429, 500, 502, 503, 504):
            return r
        wait = r.headers.get("Retry-After", "")
        time.sleep(min(60, int(wait)) if wait.isdigit() else 5 * (i + 1))
    return r


def _squash(s):
    return re.sub(r"[ \t\r\f\v]+", " ", re.sub(r"\n\s*\n+", "\n", s)).strip()


def _dailymed(url):
    m = re.search(r"setid=([0-9a-fA-F-]{36})", url)
    if not m:
        return None, "no setid"
    r = _get(f"https://dailymed.nlm.nih.gov/dailymed/services/v2/spls/{m.group(1)}.xml")
    if r.status_code == 404:        # not in the v2 services copy: read the label's own web page instead
        return _dailymed_page(url)
    if r.status_code != 200:
        return None, f"dailymed HTTP {r.status_code}"
    ns = "{urn:hl7-org:v3}"
    root = ET.fromstring(r.content)
    best = ""
    for s in root.iter(ns + "section"):
        c = s.find(ns + "code")
        if c is not None and c.get("code") == "34067-9":      # LOINC: indications and usage
            t = _squash("".join(s.itertext()))
            if len(t) > len(best):
                best = t
    return (best, "") if len(best) >= 40 else (None, "no indications section")


def _dailymed_page(url):
    import lxml.html
    r = _get(url)
    if r.status_code != 200:
        return None, f"dailymed HTTP {r.status_code}"
    doc = lxml.html.fromstring(r.content)
    best = ""
    for el in doc.xpath('//*[@data-sectioncode="34067-9"]'):
        t = _squash(el.text_content())
        if len(t) > len(best):
            best = t
    return (best, "") if len(best) >= 40 else (None, "no indications section")


def _fda_pdf(url):
    r = _get(url)
    if r.status_code != 200 or not r.content.startswith(b"%PDF"):
        return None, f"fda HTTP {r.status_code}"
    p = subprocess.run(["pdftotext", "-layout", "-", "-"], input=r.content, capture_output=True, timeout=120)
    t = p.stdout.decode("utf-8", "ignore")
    starts = [m.start() for m in re.finditer(r"INDICATIONS\s*(?:AND|&)\s*USAGE", t, re.I)]
    # the highlights page names the heading first; the full section comes later and is the longest stretch
    best = ""
    for s in starts:
        seg = t[s:s + 40000]
        e = re.search(r"\n\s*(?:2\s+)?DOSAGE\s*(?:AND|&)\s*ADMINISTRATION", seg[30:], re.I)
        seg = seg[: e.start() + 30] if e else seg[:MAX_LABEL_CHARS]
        seg = _squash(seg)
        if len(seg) > len(best):
            best = seg
    return (best, "") if len(best) >= 60 else (None, "no indications section")


def _ema(url):
    r = _get(url, spaced=True)
    if r.status_code != 200:
        return None, f"ema HTTP {r.status_code}"
    t = re.sub(r"<[^>]+>", "\n", r.text)
    import html as _h
    t = _h.unescape(t)
    m = re.search(r"Therapeutic indication(.*?)(?:Authorisation details|Pharmacotherapeutic group)", t, re.S | re.I)
    txt = _squash(m.group(1)) if m else ""
    return (txt, "") if len(txt) >= 40 else (None, "no indication text")


def read_label(url, labels_dir):
    """-> {status: 'label'|'no_label', text, reason}. Cached by URL."""
    os.makedirs(labels_dir, exist_ok=True)
    f = os.path.join(labels_dir, hashlib.sha1(url.encode()).hexdigest()[:16] + ".json")
    if os.path.exists(f):
        return json.load(open(f))
    host = re.match(r"https?://([^/]+)", url or "")
    host = host.group(1) if host else ""
    text, why = None, "source is not a readable label page"
    try:
        if host == "dailymed.nlm.nih.gov":
            text, why = _dailymed(url)
        elif host == "www.accessdata.fda.gov" and url.lower().endswith(".pdf"):
            text, why = _fda_pdf(url)
        elif host == "www.ema.europa.eu":
            text, why = _ema(url)
    except Exception as e:
        text, why = None, f"fetch error {type(e).__name__}"
    out = {"url": url, "status": "label" if text else "no_label", "text": (text or "")[:MAX_LABEL_CHARS], "reason": why}
    if not text and re.search(r"fetch error|HTTP (429|5\d\d)", why):
        return out                      # transient: not cached
    json.dump(out, open(f, "w"))
    return out


# ---------------------------------------------------------------- order, estimate, plan
def order_cards(cards, checked):
    """Oldest-checked first; never checked first. Ties: a fixed hash, so the slice is spread over the diseases."""
    def k(c):
        last = (checked.get(card_key(c)) or {}).get("date", "")
        return (last, hashlib.sha1(card_key(c).encode()).hexdigest())
    return sorted(cards, key=k)


def user_message(c, label_url, text):
    names = (c["medicine"],) + tuple(x for x in c["forms"] if x and x != c["medicine"])
    syn = "; ".join(c["also_called"])
    return (f"MEDICINE: {c['medicine']}\nFORMS: {', '.join(names)}\n"
            f"DISEASE: {c['disease']} ({c['disease_id']})\nDISEASE ALSO CALLED: {syn or 'none listed'}\n"
            f"LABEL SOURCE: {label_url}\n\nLABEL TEXT:\n{text}")


def est_cost(user, system, prices):
    tin = (len(user) + len(system)) // 3 + 20          # ~3 chars per token: the benchmark's conservative rule
    return tin, tin / 1e6 * prices[0] + OUT_ALLOWANCE / 1e6 * prices[1]


def cmd_plan(a):
    if not os.environ.get("ANTHROPIC_API_KEY", "").strip():
        sys.exit("ANTHROPIC_API_KEY is not set. Nothing was written.")
    B, S, _ = bench()
    model = B.MODEL
    prices = S.PRICES[model]
    W = a.work; os.makedirs(W, exist_ok=True)
    fp0, rev0 = fingerprint()
    ids = [l.strip() for l in open(os.path.join(HERE, "diseases.txt")) if l.strip()]
    cards, failed = walk_cards(ids)
    fp1, rev1 = fingerprint()
    json.dump(cards, open(os.path.join(W, "cards.json"), "w"))
    checked = json.load(open(a.checked)) if os.path.exists(a.checked) else {}
    live_red = [c for c in cards if c["red"]]
    pool = [c for c in cards if not c["red"]]
    ordered = order_cards(pool, checked)

    chosen, reqs, est_total, tin_total = [], [], 0.0, 0
    n_label = n_nolabel = 0
    i = 0
    stop = False
    while i < len(ordered) and not stop:
        chunk = ordered[i:i + 48]; i += 48
        with cf.ThreadPoolExecutor(4) as ex:
            labs = list(ex.map(lambda c: read_label(c["source"], os.path.join(W, "labels")) if c["source"] else
                               {"status": "no_label", "text": "", "reason": "no source link"}, chunk))
        for c, lab in zip(chunk, labs):
            if lab["status"] != "label":
                chosen.append({**c, "custom_id": "", "label_status": "no_label", "label_url": c["source"], "reason": lab["reason"]})
                n_nolabel += 1
                continue
            user = user_message(c, c["source"], lab["text"])
            tin, cost = est_cost(user, B.SYSTEM, prices)
            if est_total + cost > a.budget:
                stop = True; break
            cid = f"fl-{len(reqs) + 1:05d}"
            reqs.append({"custom_id": cid, "params": {"model": model, "max_tokens": MAX_TOKENS,
                         "output_config": {"effort": "low"}, "system": B.SYSTEM,
                         "messages": [{"role": "user", "content": user}]}})
            chosen.append({**c, "custom_id": cid, "label_status": "label", "label_url": c["source"], "reason": ""})
            est_total += cost; tin_total += tin; n_label += 1
        print(f"  planned {len(chosen)} cards ({n_label} to the model, {n_nolabel} no label), est ${est_total:.3f}", flush=True)

    S.load_requests  # (validated below)
    with open(os.path.join(W, "requests.jsonl"), "w") as f:
        for r in reqs:
            f.write(json.dumps(r) + "\n")
    for r in reqs:
        S.validate_request(r)
    plan = {"date": a.date, "model": model, "fingerprint_start": fp0, "fingerprint_end": fp1, "revision_start": rev0,
            "revision_end": rev1, "diseases_listed": len(ids), "diseases_failed": failed, "cards_on_pages": len(cards),
            "cards_red_skipped": len(live_red), "cards_planned": len(chosen), "requests": len(reqs), "no_label": n_nolabel,
            "input_tokens_est": tin_total, "output_allowance_per_card": OUT_ALLOWANCE, "estimate_usd": round(est_total, 4),
            "budget_usd": a.budget, "hard_cap_usd": HARD_CAP, "max_tokens": MAX_TOKENS}
    json.dump(plan, open(os.path.join(W, "plan.json"), "w"), indent=1)
    json.dump(chosen, open(os.path.join(W, "chosen.json"), "w"))
    print(json.dumps(plan, indent=1))


# ---------------------------------------------------------------- submit
def cmd_submit(a):
    B, S, _ = bench()
    W = a.work
    plan = json.load(open(os.path.join(W, "plan.json")))
    if plan["estimate_usd"] > HARD_CAP:
        sys.exit("Estimate is over the hard cap. Nothing sent.")
    if not a.yes:
        sys.exit("Add --yes to submit (this spends API credit).")
    reqs = S.load_requests(os.path.join(W, "requests.jsonl"))
    os.chdir(W)                                    # submit_batch writes its state file in the cwd
    state = "batch_state.json"
    if os.path.exists(state):
        bid = json.load(open(state))["id"]
        print(f"Resuming batch {bid}")
    else:
        bid = S.submit(reqs)
    deadline = time.time() + a.max_wait
    while True:
        b = S.http("GET", f"{S.BASE}/v1/messages/batches/{bid}")
        print(f"{time.strftime('%H:%M')} {b['processing_status']} {b.get('request_counts')}", flush=True)
        if b["processing_status"] == "ended":
            break
        if time.time() > deadline:
            print(f"NOT FINISHED within the wait. Batch id: {bid}. Resume: submit --yes (same work dir).")
            return 3
        time.sleep(a.every)
    S.download(b, "results.jsonl")
    return 0


# ---------------------------------------------------------------- report
def usage_cost(result, prices):
    if result.get("type") != "succeeded":
        return 0.0, 0, 0
    u = result["message"]["usage"]
    i = u.get("input_tokens", 0) + u.get("cache_creation_input_tokens", 0) + u.get("cache_read_input_tokens", 0)
    o = u.get("output_tokens", 0)
    return i / 1e6 * prices[0] + o / 1e6 * prices[1], i, o


def decide(chosen, results, labels_dir, B, S, SC, prices):
    rows = []
    for c in chosen:
        r = {"disease_id": c["disease_id"], "disease": c["disease"], "medicine_id": c["medicine_id"], "medicine": c["medicine"],
             "verdict": "", "quote": "", "label_url": c["label_url"], "model": "", "cost": 0.0, "note": "", "list": c["list"]}
        if not c["custom_id"]:
            r.update(verdict="NO_LABEL", note=c["reason"])
        else:
            res = results.get(c["custom_id"])
            if res is None:
                r.update(verdict="UNCLEAR", note="no result in batch")
            else:
                r["cost"], _, _ = usage_cost(res, prices)
                if res.get("type") == "succeeded":
                    r["model"] = res["message"].get("model", "")
                d, why = SC.parse(res)
                if d is None:
                    r.update(verdict="UNCLEAR", note=why)
                else:
                    r.update(verdict=d["verdict"], quote=d.get("quote", ""), note=d.get("note", ""))
                    if d["verdict"] in ("YES", "PARTIAL"):
                        lab = read_label(c["label_url"], labels_dir)
                        q = SC.norm(d.get("quote", ""))
                        if not (q and q.strip('".') in SC.norm(lab["text"])):
                            r.update(verdict="UNCLEAR", note=f"quote not in label (model said {d['verdict']})")
        rows.append(r)
    return rows


def cmd_report(a):
    B, S, SC = bench()
    prices = S.PRICES[B.MODEL]
    W = a.work
    plan = json.load(open(os.path.join(W, "plan.json")))
    chosen = json.load(open(os.path.join(W, "chosen.json")))
    results = {}
    for line in open(os.path.join(W, "results.jsonl")):
        if line.strip():
            r = json.loads(line); results[r["custom_id"]] = r["result"]
    rows = decide(chosen, results, os.path.join(W, "labels"), B, S, SC, prices)
    actual = sum(r["cost"] for r in rows)
    tin = sum(usage_cost(v, prices)[1] for v in results.values())
    tout = sum(usage_cost(v, prices)[2] for v in results.values())
    checked = json.load(open(a.checked)) if os.path.exists(a.checked) else {}
    for r in rows:
        prev = (checked.get(f"{r['disease_id']}|{r['medicine_id']}") or {}).get("verdict")
        r["previous"] = prev or ""
        r["changed"] = bool(prev and prev != r["verdict"])
        r["flag"] = "; ".join(x for x in ([r["verdict"]] if r["verdict"] in FLAG_VERDICTS else []) +
                              (["changed since last check"] if r["changed"] else []))
    date = a.date
    os.makedirs(os.path.join(REPO, "flags"), exist_ok=True)
    cols = ["disease_id", "disease", "medicine_id", "medicine", "verdict", "quote", "label_url", "model", "cost", "flag", "note"]
    flags = [r for r in rows if r["flag"]]
    with open(os.path.join(REPO, "flags", f"{date}.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore"); w.writeheader()
        for r in flags:
            w.writerow({**r, "cost": f"{r['cost']:.6f}"})
    for r in rows:
        checked[f"{r['disease_id']}|{r['medicine_id']}"] = {"date": date, "verdict": r["verdict"]}
    json.dump(checked, open(a.checked, "w"), indent=0, sort_keys=True)
    cnt = {v: sum(1 for r in rows if r["verdict"] == v) for v in ("YES", "PARTIAL", "NO", "UNCLEAR", "NO_LABEL")}
    over = actual > HARD_CAP
    md = [f"# Flagger run {date}", "",
          f"- Build checked: `{plan['fingerprint_start']}` (revision {plan['revision_start']}); at the end of the card walk: `{plan['fingerprint_end']}`",
          f"- Model: `{plan['model']}`, low effort, Message Batches API (batch price)",
          f"- Cards on the {plan['diseases_listed']} listed pages' Approved tabs: {plan['cards_on_pages']} ({plan['cards_red_skipped']} already red, skipped)",
          f"- **Cards checked: {len(rows)}** ({plan['requests']} sent to the model, {plan['no_label']} with no readable label)",
          f"- Estimated cost: USD {plan['estimate_usd']:.4f} (budget {plan['budget_usd']:.2f}, hard cap {HARD_CAP:.2f})",
          f"- **Actual cost: USD {actual:.4f}** ({tin} input + {tout} output tokens)" + (" **OVER THE CAP: halve tomorrow's slice**" if over else ""),
          "", "## Verdicts", "", "| Verdict | Cards |", "|---|---|"]
    md += [f"| {k} | {v} |" for k, v in cnt.items()]
    md += ["", f"## Flags: {len(flags)}", "", "NO, UNCLEAR, NO_LABEL, and any card whose verdict changed since its last check. "
           f"Full list with the quoted sentences: `flags/{date}.csv`. A flag is evidence for a person to read, never a change to a card.", ""]
    if plan["diseases_failed"]:
        md += ["## Pages that could not be read", ""] + [f"- {x}" for x in plan["diseases_failed"]] + [""]
    open(os.path.join(REPO, "flags", f"{date}.md"), "w").write("\n".join(md) + "\n")
    json.dump(rows, open(os.path.join(W, "decided.json"), "w"))
    print(json.dumps({"checked": len(rows), "counts": cnt, "flags": len(flags), "estimate": plan["estimate_usd"],
                      "actual": round(actual, 4), "tokens": [tin, tout]}))
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["plan", "submit", "report"])
    ap.add_argument("--work", default="/workspace/flagger/work")
    ap.add_argument("--checked", default=os.path.join(REPO, "checked.json"))
    ap.add_argument("--date", default=time.strftime("%Y-%m-%d"))
    ap.add_argument("--budget", type=float, default=0.90)
    ap.add_argument("--yes", action="store_true")
    ap.add_argument("--every", type=int, default=120)
    ap.add_argument("--max-wait", type=int, default=2 * 3600)
    a = ap.parse_args(argv)
    if a.budget > HARD_CAP:
        sys.exit("budget is over the USD 1.00 hard cap")
    return {"plan": cmd_plan, "submit": cmd_submit, "report": cmd_report}[a.cmd](a) or 0


if __name__ == "__main__":
    sys.exit(main())
