#!/usr/bin/env python3
"""Submit a Moonlight label-check JSONL file to the Anthropic Message Batches API.

Checked against Anthropic docs on 24 Nov 2026:
  POST {base}/v1/messages/batches          body {"requests": [{"custom_id", "params"}]}
  GET  {base}/v1/messages/batches/{id}     processing_status: in_progress | canceling | ended
  GET  {base}/v1/messages/batches/{id}/results   JSONL, one {"custom_id","result":{"type":...}} per line
  POST {base}/v1/messages/batches/{id}/cancel
  Headers: x-api-key, anthropic-version (2026-10-21), content-type: application/json
Limits: 100,000 requests or 256 MB per batch; custom_id ^[a-zA-Z0-9_-]{1,64}$;
max_tokens >= 1; stream/temperature/top_p/top_k/speed/fallbacks rejected.

Usage:
  python3 submit_batch.py requests.jsonl --dry-run          # no key needed
  python3 submit_batch.py requests.jsonl --pilot 20 --yes   # submit first 20 only
  python3 submit_batch.py requests.jsonl --yes              # submit, poll, download
  python3 submit_batch.py --resume                          # poll + download saved batch
The key is read from ANTHROPIC_API_KEY and is never printed, logged or written.
"""
import argparse, json, os, re, sys, time, urllib.request, urllib.error

BASE = "https://api.anthropic.com"
API_VERSION = "2026-10-21"
CUSTOM_ID = re.compile(r"^[a-zA-Z0-9_-]{1,64}$")
FORBIDDEN = {"stream", "temperature", "top_p", "top_k", "speed", "fallbacks"}
MAX_REQUESTS, MAX_BYTES = 100_000, 256 * 1024 * 1024
STATE = "batch_state.json"
# Batch prices, USD per million tokens (Anthropic pricing page, 24 Nov 2026).
PRICES = {"claude-sonnet-5-5": (1.0, 5.0), "claude-haiku-5-5": (0.05, 0.25),
          "claude-opus-5-5": (2.0, 10.0), "claude-haiku-4-5": (0.5, 2.5)}


class BatchFileError(ValueError):
    pass


def load_requests(path, limit=None):
    """Read and validate a JSONL file. Returns the list of requests."""
    if os.path.getsize(path) > MAX_BYTES:
        raise BatchFileError("file is over 256 MB")
    reqs, seen = [], set()
    with open(path, encoding="utf-8") as f:
        for n, line in enumerate(f, 1):
            if not line.strip():
                continue
            try:
                r = json.loads(line)
            except json.JSONDecodeError as e:
                raise BatchFileError(f"line {n}: not JSON ({e.msg})")
            validate_request(r, n)
            if r["custom_id"] in seen:
                raise BatchFileError(f"line {n}: duplicate custom_id {r['custom_id']}")
            seen.add(r["custom_id"])
            reqs.append(r)
            if limit and len(reqs) >= limit:
                break
    if not reqs:
        raise BatchFileError("no requests in file")
    if len(reqs) > MAX_REQUESTS:
        raise BatchFileError("more than 100,000 requests")
    return reqs


def validate_request(r, n=0):
    if not isinstance(r, dict) or set(r) != {"custom_id", "params"}:
        raise BatchFileError(f"line {n}: needs exactly custom_id and params")
    if not isinstance(r["custom_id"], str) or not CUSTOM_ID.match(r["custom_id"]):
        raise BatchFileError(f"line {n}: bad custom_id")
    p = r["params"]
    if not isinstance(p, dict):
        raise BatchFileError(f"line {n}: params must be an object")
    bad = FORBIDDEN & set(p)
    if bad:
        raise BatchFileError(f"line {n}: not allowed in a batch: {sorted(bad)}")
    if not isinstance(p.get("model"), str) or not p["model"]:
        raise BatchFileError(f"line {n}: missing model")
    if not isinstance(p.get("max_tokens"), int) or p["max_tokens"] < 1:
        raise BatchFileError(f"line {n}: max_tokens must be an integer >= 1")
    msgs = p.get("messages")
    if not isinstance(msgs, list) or not msgs or msgs[0].get("role") != "user":
        raise BatchFileError(f"line {n}: messages must be a list starting with a user turn")


def estimate(reqs):
    """Rough cost: ~3 characters per token (newer tokenizer), output = max_tokens ceiling."""
    by_model = {}
    for r in reqs:
        p = r["params"]
        chars = len(json.dumps(p.get("messages"))) + len(json.dumps(p.get("system", "")))
        m = by_model.setdefault(p["model"], [0, 0, 0])
        m[0] += 1; m[1] += chars // 3; m[2] += p["max_tokens"]
    out = {}
    for model, (count, tin, tout) in by_model.items():
        pin, pout = PRICES.get(model, (None, None))
        cost = None if pin is None else round(tin / 1e6 * pin + tout / 1e6 * pout, 2)
        out[model] = {"requests": count, "input_tokens_est": tin,
                      "output_tokens_ceiling": tout, "usd_ceiling": cost}
    return out


def _key():
    k = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if not k:
        sys.exit("ANTHROPIC_API_KEY is not set. Nothing was sent.")
    return k


def http(method, url, body=None, raw=False):
    """The one function that touches the network. Tests replace it."""
    headers = {"x-api-key": _key(), "anthropic-version": API_VERSION,
               "content-type": "application/json"}
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=300) as resp:
            payload = resp.read()
    except urllib.error.HTTPError as e:
        # Print the API's error body only; never the request headers.
        raise SystemExit(f"HTTP {e.code} from {url}: {e.read()[:500].decode(errors='replace')}")
    return payload if raw else json.loads(payload)


def submit(reqs, base=BASE):
    batch = http("POST", f"{base}/v1/messages/batches", {"requests": reqs})
    json.dump({"id": batch["id"], "submitted": time.strftime("%Y-%m-%d %H:%M %Z"),
               "requests": len(reqs)}, open(STATE, "w"))
    print(f"Submitted batch {batch['id']} with {len(reqs)} requests.")
    return batch["id"]


def poll(batch_id, base=BASE, every=60, sleep=time.sleep, max_wait=26 * 3600):
    waited = 0
    while True:
        b = http("GET", f"{base}/v1/messages/batches/{batch_id}")
        print(f"{time.strftime('%H:%M')} {b['processing_status']} {b.get('request_counts')}", flush=True)
        if b["processing_status"] == "ended":
            return b
        if waited >= max_wait:
            raise SystemExit("Gave up waiting; run --resume later.")
        sleep(every); waited += every


def download(batch, out="results.jsonl", base=BASE):
    url = batch.get("results_url") or f"{base}/v1/messages/batches/{batch['id']}/results"
    raw = http("GET", url, raw=True)
    with open(out, "wb") as f:
        f.write(raw)
    counts, usage = {}, {}
    for line in raw.decode().splitlines():
        if not line.strip():
            continue
        r = json.loads(line)
        t = r["result"]["type"]
        counts[t] = counts.get(t, 0) + 1
        if t == "succeeded":
            msg = r["result"]["message"]
            u = usage.setdefault(msg.get("model", "?"), [0, 0])
            u[0] += msg["usage"].get("input_tokens", 0)
            u[1] += msg["usage"].get("output_tokens", 0)
    cost = 0.0
    for model, (i, o) in usage.items():
        key = next((k for k in PRICES if model.startswith(k)), None)
        if key:
            cost += i / 1e6 * PRICES[key][0] + o / 1e6 * PRICES[key][1]
    print(f"Wrote {out}: {counts}. Tokens {usage}. Approx cost ${cost:.2f}")
    return counts


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("jsonl", nargs="?")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--pilot", type=int, help="submit only the first N requests")
    ap.add_argument("--yes", action="store_true", help="required to spend money")
    ap.add_argument("--resume", action="store_true")
    ap.add_argument("--out", default="results.jsonl")
    ap.add_argument("--every", type=int, default=60)
    a = ap.parse_args(argv)
    if a.resume:
        bid = json.load(open(STATE))["id"]
        download(poll(bid, every=a.every), a.out)
        return 0
    if not a.jsonl:
        ap.error("give a JSONL file, or --resume")
    try:
        reqs = load_requests(a.jsonl, a.pilot)
    except BatchFileError as e:
        print(f"INVALID: {e}"); return 2
    print(f"Valid: {len(reqs)} requests.")
    print(json.dumps(estimate(reqs), indent=1))
    if a.dry_run:
        print("Dry run: nothing sent."); return 0
    if not a.yes:
        print("Add --yes to submit (this spends Console credit)."); return 1
    bid = submit(reqs)
    download(poll(bid, every=a.every), a.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
