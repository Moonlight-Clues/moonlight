"""Study P8 (UniProt), step 2: recount. Reads only the saved files in this
folder. No network, no Moonlight code.

Run from the repo root:

    python3 fixtures/probe_p8/recount.py

It prints every count in REPORT.md and rewrites counts.json, pairs.csv and
proteins.csv. Run it twice: the three files must not change.

Words used here:
  protein = one Ensembl gene id from Moonlight's top 25 (231 different ones)
  slot    = one disease + one protein (10 diseases x 25 = 250 slots)
"""

import csv
import gzip
import json
import pathlib
import re
import statistics

HERE = pathlib.Path(__file__).resolve().parent
PUBMED = re.compile(r"\s*\((?:PubMed:\d+|By similarity|Probable|Potential)(?:, (?:PubMed:\d+|ECO:\d+))*\)")
DIRECTION = {
    "gain of function": re.compile(r"gain[- ]of[- ]function", re.I),
    "loss of function": re.compile(r"loss[- ]of[- ]function", re.I),
}
WIDER = {
    "dominant negative": re.compile(r"dominant[- ]negative", re.I),
    "haploinsufficiency": re.compile(r"haploinsufficien", re.I),
    "constitutive activation": re.compile(r"constitutive(ly)?[- ]activ", re.I),
    "activating / inactivating": re.compile(r"\b(in)?activating\b", re.I),
}


def load(gene: str) -> list:
    for name in (f"{gene}.json.gz", f"{gene}.byname.json.gz"):
        path = HERE / "responses" / name
        if path.exists():
            results = json.loads(gzip.decompress(path.read_bytes()))["results"]
            if results:
                return results
    return []


def values(thing) -> list:
    """Every "value" string anywhere inside a comment."""
    if isinstance(thing, dict):
        return [v for k, x in thing.items()
                for v in ([x] if k == "value" and isinstance(x, str) else values(x))]
    if isinstance(thing, list):
        return [v for x in thing for v in values(x)]
    return []


def norm(text: str) -> str:
    return " " + " ".join(re.sub(r"[^a-z0-9]+", " ", text.lower()).split()) + " "


def first_sentence(text: str) -> str:
    clean = PUBMED.sub("", text)
    return re.split(r"(?<=[a-z0-9\)])\. (?=[A-Z])", clean, maxsplit=1)[0].rstrip(".") + "."


def look(entry: dict) -> dict:
    comments = entry.get("comments", [])
    function = [t["value"] for c in comments if c["commentType"] == "FUNCTION" for t in c["texts"]]
    diseases = [c for c in comments if c["commentType"] == "DISEASE"]
    named = [c for c in diseases if "disease" in c]
    where = {}
    places = {
        "function text": " ".join(function),
        "disease note": " ".join(
            " ".join([c.get("disease", {}).get("description", "")] + values(c.get("note", {})))
            for c in diseases),
        "other comment": " ".join(v for c in comments
                                  if c["commentType"] not in ("FUNCTION", "DISEASE") for v in values(c)),
        "variant or mutagenesis line": " ".join(
            f.get("description", "") for f in entry.get("features", [])),
    }
    for word, pattern in {**DIRECTION, **WIDER}.items():
        where[word] = [place for place, text in places.items() if pattern.search(text)]
    return {
        "accession": entry["primaryAccession"],
        "entry_type": entry["entryType"],
        "taxon": entry["organism"]["taxonId"],
        "function": " ".join(function),
        "first_sentence": first_sentence(function[0]) if function else "",
        "disease_comments": diseases,
        "disease_names": [c["disease"]["diseaseId"] for c in named],
        "note_only": len(diseases) - len(named),
        "variant_lines": [f.get("description", "") for f in entry.get("features", [])
                          if f["type"] == "Natural variant"],
        "where": where,
    }


def spread(numbers: list) -> dict:
    numbers = sorted(numbers)
    return {"n": len(numbers), "min": numbers[0], "median": statistics.median(numbers),
            "max": numbers[-1], "mean": round(statistics.mean(numbers), 1)}


def main() -> None:
    study = json.loads((HERE / "diseases.json").read_text(encoding="utf-8"))["diseases"]
    genes = {}
    for d in study:
        for t in d["targets"]:
            genes.setdefault(t["id"], t["symbol"])
    seen = {}
    counts = {"diseases": len(study), "slots": sum(len(d["targets"]) for d in study),
              "proteins": len(genes)}
    how_many = {"0": 0, "1": 0, "more": 0}
    for gene, symbol in genes.items():
        entries = load(gene)
        how_many["0" if not entries else "1" if len(entries) == 1 else "more"] += 1
        if entries:
            seen[gene] = look(entries[0])
            seen[gene]["symbol_matches"] = symbol in [
                g.get("geneName", {}).get("value") for g in entries[0].get("genes", [])]
    counts["reviewed_entries_found"] = how_many
    counts["all_reviewed_human"] = all(
        s["entry_type"] == "UniProtKB reviewed (Swiss-Prot)" and s["taxon"] == 9606 for s in seen.values())
    counts["gene_symbol_same_as_open_targets"] = sum(s["symbol_matches"] for s in seen.values())
    found_by_name = [json.loads(l)["gene"] for l in (HERE / "index.jsonl").read_text().splitlines()
                     if ".byname." in json.loads(l)["file"]]
    counts["found_only_by_gene_name"] = len(found_by_name)

    # 1. function text
    have = [s for s in seen.values() if s["function"]]
    counts["function"] = {
        "proteins_with_function_text": len(have),
        "slots_with_function_text": sum(1 for d in study for t in d["targets"]
                                        if seen.get(t["id"], {}).get("function")),
        "whole_text_chars": spread([len(s["function"]) for s in have]),
        "first_sentence_chars": spread([len(s["first_sentence"]) for s in have]),
        "first_sentence_words": spread([len(s["first_sentence"].split()) for s in have]),
        "first_sentence_150_chars_or_less": sum(len(s["first_sentence"]) <= 150 for s in have),
        "first_sentence_300_chars_or_less": sum(len(s["first_sentence"]) <= 300 for s in have),
    }

    # 2. disease-involvement notes
    with_note = [s for s in seen.values() if s["disease_comments"]]
    counts["disease_notes"] = {
        "proteins_with_any_disease_note": len(with_note),
        "proteins_with_a_named_disease": sum(bool(s["disease_names"]) for s in seen.values()),
        "proteins_with_only_free_text_notes": sum(
            bool(s["disease_comments"]) and not s["disease_names"] for s in seen.values()),
        "named_diseases_per_protein_that_has_one": spread(
            [len(s["disease_names"]) for s in seen.values() if s["disease_names"]]),
    }
    rows = []
    per_disease = []
    for d in study:
        terms = {norm(x) for x in [d["name"]] + d["exact_synonyms"] if len(x.strip()) >= 4}
        tally = {"disease": d["name"], "slots": 0, "has_note": 0, "names_ours": 0,
                 "mentions_ours_in_text_only": 0, "direction_word_in_matching_note": 0,
                 "gain_or_loss_on_variant_line_of_matching_disease": 0}
        for rank, t in enumerate(d["targets"], 1):
            s = seen.get(t["id"])
            tally["slots"] += 1
            if not s:
                rows.append([d["id"], d["name"], rank, t["id"], t["symbol"], "", "", "", "", "", "", ""])
                continue
            names_hit = [n for n in s["disease_names"] if any(term in norm(n) for term in terms)]
            text_hit = []
            direction_in_match = []
            acronyms = set()
            for c in s["disease_comments"]:
                text = " ".join([c.get("disease", {}).get("description", "")] + values(c.get("note", {})))
                name = c.get("disease", {}).get("diseaseId", "")
                is_ours = any(term in norm(name) for term in terms)
                if not is_ours and any(term in norm(text) for term in terms):
                    text_hit.append(name or "(free-text note)")
                if is_ours:
                    acronyms.add(c["disease"].get("acronym", ""))
                    direction_in_match += [w for w, p in {**DIRECTION, **WIDER}.items() if p.search(text)]
            # UniProt variant lines start "in ACRONYM; ..." naming the disease by its short code.
            on_variant = set()
            for line in s["variant_lines"]:
                head = re.split(r"[;,]| and ", line.split(";")[0].removeprefix("in "))
                if acronyms & {h.strip() for h in head}:
                    on_variant |= {w for w, p in DIRECTION.items() if p.search(line)}
            tally["gain_or_loss_on_variant_line_of_matching_disease"] += bool(on_variant)
            tally["has_note"] += bool(s["disease_comments"])
            tally["names_ours"] += bool(names_hit)
            tally["mentions_ours_in_text_only"] += bool(text_hit and not names_hit)
            tally["direction_word_in_matching_note"] += bool(direction_in_match)
            rows.append([d["id"], d["name"], rank, t["id"], t["symbol"], s["accession"],
                         len(s["disease_comments"]), "; ".join(s["disease_names"]),
                         "; ".join(names_hit), "; ".join(text_hit),
                         "; ".join(sorted(set(direction_in_match))), "; ".join(sorted(on_variant))])
        per_disease.append(tally)
    counts["per_disease"] = per_disease
    counts["slots_total"] = {k: sum(p[k] for p in per_disease) for k in per_disease[0] if k != "disease"}

    # 3. gain or loss of function
    direction = {}
    for word in list(DIRECTION) + list(WIDER):
        hits = [s for s in seen.values() if s["where"][word]]
        direction[word] = {"proteins": len(hits)}
        for place in ("function text", "disease note", "other comment", "variant or mutagenesis line"):
            direction[word][place] = sum(place in s["where"][word] for s in hits)
    either = [s for s in seen.values() if s["where"]["gain of function"] or s["where"]["loss of function"]]
    direction["gain or loss, anywhere"] = len(either)
    direction["both gain and loss in the same entry"] = sum(
        bool(s["where"]["gain of function"]) and bool(s["where"]["loss of function"]) for s in seen.values())
    direction["gain or loss, in function text or disease note"] = sum(
        any(p in ("function text", "disease note")
            for w in DIRECTION for p in s["where"][w]) for s in seen.values())
    direction["gain or loss, only in variant or mutagenesis lines"] = sum(
        all(p == "variant or mutagenesis line" for w in DIRECTION for p in s["where"][w])
        for s in either)
    counts["direction_words"] = direction

    (HERE / "counts.json").write_text(json.dumps(counts, indent=1) + "\n", encoding="utf-8")
    with (HERE / "pairs.csv").open("w", newline="", encoding="utf-8") as out:
        w = csv.writer(out)
        w.writerow(["disease_id", "disease", "rank", "gene", "symbol", "uniprot", "disease_notes",
                    "uniprot_named_diseases", "names_our_disease", "mentions_ours_in_text_only",
                    "direction_words_in_matching_note", "gain_or_loss_on_variant_line_of_matching_disease"])
        w.writerows(rows)
    with (HERE / "proteins.csv").open("w", newline="", encoding="utf-8") as out:
        w = csv.writer(out)
        w.writerow(["gene", "symbol", "uniprot", "function_chars", "first_sentence_chars",
                    "first_sentence", "named_diseases", "free_text_disease_notes",
                    "gain_of_function_where", "loss_of_function_where"])
        for gene, symbol in genes.items():
            s = seen.get(gene)
            if s:
                w.writerow([gene, symbol, s["accession"], len(s["function"]), len(s["first_sentence"]),
                            s["first_sentence"], len(s["disease_names"]), s["note_only"],
                            "; ".join(s["where"]["gain of function"]),
                            "; ".join(s["where"]["loss of function"])])
    print(json.dumps(counts, indent=1))


if __name__ == "__main__":
    main()
