"""pairs.csv + labels/ -> requests.jsonl and requests_index.csv (one row per card)."""
import csv, json, sys, hashlib, os
MODEL = "claude-sonnet-5-5"
SYSTEM = """You read one official medicine label. Answer only from the label text given.
Question: does this label say MEDICINE is approved or indicated for DISEASE?
Reply with JSON only, no other text:
{"verdict": "YES|NO|PARTIAL|UNCLEAR", "quote": "<one exact sentence or phrase copied character for character from the label text, or empty>", "label_product": "<product and active ingredient named on the label>", "note": "<20 words max>"}
YES = the label indicates the medicine for DISEASE (or a listed synonym of it) without a material restriction beyond adults/children.
PARTIAL = indicated only for a subset of people with DISEASE (a stage, a subtype, a gene or mutation, after another treatment failed, add-on only, one symptom or complication of it).
NO = the label names other diseases only.
UNCLEAR = the text is cut off, is not a label, or is about a different product or ingredient.
If the active ingredient on the label is a different salt or substance from MEDICINE and its FORMS (for example zinc acetate on the label when MEDICINE is zinc sulfate), answer UNCLEAR and name both in note.
The quote must be copied exactly from the label text, so it can be found by plain text search."""

def build(pairs="pairs.csv", out="requests.jsonl", index="requests_index.csv"):
    P = list(csv.DictReader(open(pairs)))
    also = {}
    for d in {p["disease_id"] for p in P}:
        j = json.load(open(f"live/{d}.json"))
        also[d] = (j.get("about_disease") or {}).get("also_called") or []
    rows, n_req = [], 0
    with open(out, "w") as f:
        for i, p in enumerate(P, 1):
            names = (p["medicine"],) + tuple(x for x in p["forms"].split("|") if x and x != p["medicine"])
            meta = "labels/" + hashlib.sha1((p["source"] + "|" + names[0]).encode()).hexdigest()[:16] + ".txt.json"
            m = json.load(open(meta)) if os.path.exists(meta) else {"status": "no_label", "file": "", "label_url": "", "kind": ""}
            cid = f"flc-{i:04d}-s"
            rows.append({**p, "row": i, "custom_id": cid if m["file"] else "", "label_status": m["status"],
                         "label_kind": m.get("kind", ""), "label_url": m.get("label_url", ""), "label_file": m["file"]})
            if not m["file"]:
                continue
            text = open(m["file"]).read()
            syn = "; ".join(also[p["disease_id"]][:12])
            user = (f"MEDICINE: {p['medicine']}\nFORMS: {', '.join(names)}\n"
                    f"DISEASE: {p['disease']} ({p['disease_id']})\nDISEASE ALSO CALLED: {syn or 'none listed'}\n"
                    f"LABEL SOURCE: {m['label_url']}\n\nLABEL TEXT:\n{text}")
            f.write(json.dumps({"custom_id": cid, "params": {
                "model": MODEL, "max_tokens": 1500, "output_config": {"effort": "low"},
                "system": SYSTEM, "messages": [{"role": "user", "content": user}]}}) + "\n")
            n_req += 1
    w = csv.DictWriter(open(index, "w", newline=""), fieldnames=list(rows[0].keys()))
    w.writeheader(); w.writerows(rows)
    print(f"{n_req} requests, {len(rows) - n_req} no_label, {len(rows)} cards")

if __name__ == "__main__":
    build()
