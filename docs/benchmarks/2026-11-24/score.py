"""results.jsonl + requests_index.csv -> scored.csv, disagreements.csv, clinician_sample.csv. Plain code."""
import csv, json, re, random, sys, unicodedata

def norm(s):
    s = unicodedata.normalize("NFKC", s or "").lower()
    s = s.replace("\u2019", "'").replace("\u2018", "'").replace("\u201c", '"').replace("\u201d", '"')
    s = re.sub(r"[\u2010-\u2015]", "-", s)
    s = re.sub(r"[•\*]", " ", s)
    return re.sub(r"\s+", " ", s).strip()

def parse(result):
    if result["type"] != "succeeded":
        return None, f"batch {result['type']}"
    text = "".join(b.get("text", "") for b in result["message"]["content"] if b.get("type") == "text")
    m = re.search(r"\{.*\}", text, re.S)
    if not m: return None, "no JSON"
    try:
        d = json.loads(m.group(0))
    except Exception:
        return None, "bad JSON"
    if d.get("verdict") not in ("YES", "NO", "PARTIAL", "UNCLEAR"):
        return None, "bad verdict"
    return d, ""

def score(index="requests_index.csv", results="results.jsonl", prefix=""):
    rows = list(csv.DictReader(open(index)))
    res = {}
    for line in open(results):
        if line.strip():
            r = json.loads(line); res[r["custom_id"]] = r["result"]
    out = []
    for r in rows:
        o = {k: r[k] for k in ("row", "disease_id", "disease", "medicine_id", "medicine", "forms", "source",
                               "label_status", "label_url", "red_warning", "proof_note", "limit_note")}
        o.update(verdict="", quote="", quote_found="", label_product="", note="", reason="")
        if not r["custom_id"]:
            o["verdict"] = "NO_LABEL"; o["reason"] = "no label found"
        elif r["custom_id"] not in res:
            o["verdict"] = "NOT_RUN"
        else:
            d, why = parse(res[r["custom_id"]])
            if d is None:
                o["verdict"] = "UNCLEAR"; o["reason"] = why
            else:
                o.update(verdict=d["verdict"], quote=d.get("quote", ""), label_product=d.get("label_product", ""), note=d.get("note", ""))
                if d["verdict"] in ("YES", "PARTIAL"):
                    label = norm(open(r["label_file"]).read())
                    q = norm(d.get("quote", ""))
                    found = bool(q) and q.strip('".') in label
                    o["quote_found"] = "yes" if found else "no"
                    if not found:
                        o["verdict"] = "UNCLEAR"; o["reason"] = f"quote not in label (model said {d['verdict']})"
        v = o["verdict"]
        hand = "from the official label" in (r["proof_note"] or "")
        dis = []
        if v in ("NO", "UNCLEAR", "NO_LABEL"): dis.append(v)
        if v == "PARTIAL" and not r["limit_note"]: dis.append("PARTIAL without limit line")
        if r["label_status"] == "label_by_name" and v in ("YES", "PARTIAL"): dis.append("label found by name only")
        if r["red_warning"] == "1" and v == "YES": dis.append("red-warning card but label says YES")
        o["disagreement"] = "; ".join(dis)
        o["priority"] = "1-hand-added" if hand and dis else ("2" if dis else "")
        out.append(o)
    if any(o["verdict"] != "NOT_RUN" for o in out):
        keep = [o for o in out if o["verdict"] != "NOT_RUN"]
        f = list(keep[0].keys())
        with open(prefix + "scored.csv", "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=f); w.writeheader(); w.writerows(keep)
        dis = sorted([o for o in keep if o["disagreement"]], key=lambda o: (o["priority"], o["disease"], o["medicine"]))
        with open(prefix + "disagreements.csv", "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=f); w.writeheader(); w.writerows(dis)
        return keep
    return []

def sample(index="requests_index.csv", n=50, seed=20261124):
    rows = list(csv.DictReader(open(index)))
    pick = sorted(random.Random(seed).sample(rows, n), key=lambda r: int(r["row"]))
    f = ["row", "disease", "disease_id", "medicine", "forms", "source", "doctor_verdict_YES_NO_PARTIAL_UNCLEAR", "doctor_note"]
    w = csv.DictWriter(open("clinician_sample.csv", "w", newline=""), fieldnames=f); w.writeheader()
    for r in pick:
        w.writerow({k: r.get(k, "") for k in f})
    return pick

if __name__ == "__main__":
    import collections
    prefix = sys.argv[2] if len(sys.argv) > 2 else ""
    keep = score(results=sys.argv[1] if len(sys.argv) > 1 else "results.jsonl", prefix=prefix)
    print(collections.Counter(o["verdict"] for o in keep), "disagreements:", sum(1 for o in keep if o["disagreement"]))
