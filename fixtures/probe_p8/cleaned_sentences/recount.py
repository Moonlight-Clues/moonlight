"""Study P8b, step 2: recount. Reads only saved files in this folder.
No network, no Moonlight code.

Run from the repo root:

    python3 fixtures/probe_p8/cleaned_sentences/recount.py

It runs clean.py on every saved answer and rewrites:

    counts.json      every number in REPORT.md
    sentences.csv    one row per protein: raw text, cleaned sentence, length, flags
    odd_cases.md     every flagged case, in full, grouped by flag
    extremes.md      the 20 shortest and 20 longest cleaned sentences, in full

Run it twice: the four files must not change.

A FLAG is a machine check that says "a person should look at this one".
It is not a verdict. Flags never change the sentence.
"""

import csv
import json
import pathlib
import re
import statistics
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from clean import ABBREVIATIONS, clean  # noqa: E402

# flag -> what it means. "odd" flags are the ones step 3 of the order asks for.
FLAGS = {
    "leftover_curly": "a curly brace is still in the sentence",
    "leftover_eco": "the letters ECO: are still in the sentence",
    "leftover_square_label": "a square-bracket label is still there (\"]:\" inside, or \"[\" at the front)",
    "no_final_stop": "the sentence does not end with a full stop (possible cut-off, or the text never had one)",
    "unbalanced_brackets": "round or square brackets do not pair up (possible cut inside a bracket)",
    "ends_like_abbreviation": "the last word before the full stop is very short or a known abbreviation (the cut may be at an abbreviation, not a sentence end)",
    "inner_full_stop": "a full stop followed by a space is inside the sentence (a sentence end the rule did not take, or an abbreviation)",
    "abbreviation_stop_skipped": "the rule saw a full stop, judged it an abbreviation, and carried on",
    "starts_oddly": "the sentence does not start with a capital letter or a digit",
    "hyphen_space_left": "a hyphen followed by a space is still there (a real hanging hyphen, or a line-wrap mark the rule left)",
    "slash_space_left": "a slash followed by a space is still there",
    "space_before_hyphen": "a space sits in front of a hyphen (\"14 -18\"); this is how the text arrived",
    "double_punctuation": "two punctuation marks in a row that look like a slip (\"..\", \",,\", \" ,\", \"( \", \" )\")",
    "wrap_joined": "the line-wrap rule joined something in this sentence (check it was right to)",
    "label_removed": "a label such as [Isoform 1] was removed, so the sentence is about that form only",
    "under_25_chars": "shorter than 25 characters",
    "pubmed_citation": "a (PubMed:...) citation in round brackets is still there; the order did not ask to remove these",
    "similarity_note": "a note such as (By similarity) or (Probable) is still there; the order did not ask to remove these",
}
NOT_ODD = ("pubmed_citation", "similarity_note")


def flags_for(sentence: str, notes: dict) -> list:
    if not sentence:
        return []
    found = []
    def add(name, yes):
        if yes:
            found.append(name)
    add("leftover_curly", "{" in sentence or "}" in sentence)
    add("leftover_eco", "ECO:" in sentence)
    add("leftover_square_label", "]:" in sentence or sentence.startswith("["))
    add("no_final_stop", not sentence.endswith("."))
    add("unbalanced_brackets", sentence.count("(") != sentence.count(")")
        or sentence.count("[") != sentence.count("]"))
    last = re.split(r"[\s(\[/]", sentence.rstrip("."))[-1]
    add("ends_like_abbreviation", sentence.endswith(".") and (
        last.lower() in ABBREVIATIONS or (len(last) <= 2 and last.isalpha())))
    add("inner_full_stop", bool(re.search(r"\.\s", sentence)))
    add("abbreviation_stop_skipped", bool(notes["abbreviation_stops_skipped"]))
    add("starts_oddly", not re.match(r"[A-Z0-9]", sentence))
    add("hyphen_space_left", bool(re.search(r"\S- ", sentence)))
    add("slash_space_left", bool(re.search(r"\S/ ", sentence)))
    add("space_before_hyphen", bool(re.search(r"\s-\S", sentence)))
    add("double_punctuation", bool(re.search(r"\.\.|,,|\s[,;.]|\(\s|\s\)", sentence)))
    add("wrap_joined", bool(notes["wraps_joined"]))
    add("label_removed", bool(notes["label_removed"]))
    add("under_25_chars", len(sentence) < 25)
    add("pubmed_citation", "PubMed:" in sentence)
    add("similarity_note", bool(re.search(r"\((By similarity|Probable|Potential)\)", sentence)))
    return found


def spread(numbers: list) -> dict:
    numbers = sorted(numbers)
    return {"n": len(numbers), "shortest": numbers[0], "middle": statistics.median(numbers),
            "longest": numbers[-1], "average": round(statistics.mean(numbers), 1)}


def main() -> None:
    study = json.loads((HERE / "proteins.json").read_text(encoding="utf-8"))
    genes = study["proteins"]
    rows = []
    problems = {"answer_missing": [], "errors_in_answer": [], "target_not_found": []}
    for gene, symbol in genes.items():
        path = HERE / "responses" / f"{gene}.json"
        if not path.exists():
            problems["answer_missing"].append(gene)
            continue
        answer = json.loads(path.read_text(encoding="utf-8"))
        if answer.get("errors"):
            problems["errors_in_answer"].append(gene)
        target = (answer.get("data") or {}).get("target")
        if target is None:
            problems["target_not_found"].append(gene)
        texts = target["functionDescriptions"] if target else []
        sentence, notes = clean(texts)
        rows.append({
            "gene": gene, "symbol": symbol,
            "open_targets_symbol": target["approvedSymbol"] if target else "",
            "name": target["approvedName"] if target else "",
            "biotype": target["biotype"] if target else "",
            "texts": texts, "sentence": sentence, "notes": notes,
            "flags": flags_for(sentence, notes),
        })
    have = [r for r in rows if r["sentence"]]
    none = [r for r in rows if not r["sentence"]]
    lengths = [len(r["sentence"]) for r in have]
    slots = [g for d in study["diseases"] for g in d["targets"]]
    by_gene = {r["gene"]: r for r in rows}
    before = json.loads((HERE / "data_version_before.json").read_text())["data"]["meta"]
    after_file = HERE / "data_version_after.json"
    after = json.loads(after_file.read_text())["data"]["meta"] if after_file.exists() else None
    biotypes = {}
    for r in none:
        biotypes[r["biotype"]] = biotypes.get(r["biotype"], 0) + 1
    counts = {
        "diseases": len(study["diseases"]),
        "diseases_with_fewer_than_25_proteins": {d["name"]: len(d["targets"])
                                                  for d in study["diseases"] if len(d["targets"]) != 25},
        "slots": len(slots),
        "proteins": len(genes),
        "problems": {k: len(v) for k, v in problems.items()},
        "open_targets": {"data_version": before["dataVersion"], "api_version": before["apiVersion"],
                         "same_version_after_the_run": before == after},
        "proteins_with_a_sentence": len(have),
        "proteins_with_none": len(none),
        "proteins_with_none_by_biotype": dict(sorted(biotypes.items())),
        "slots_with_a_sentence": sum(bool(by_gene[g]["sentence"]) for g in slots if g in by_gene),
        "slots_with_none": sum(not by_gene[g]["sentence"] for g in slots if g in by_gene),
        "proteins_with_more_than_one_text": sum(len(r["texts"]) > 1 for r in rows),
        "what_the_cleaning_did": {
            "curly_tags_removed_from_first_text": sum(r["notes"]["curly_removed"] > 0 for r in rows),
            "trailing_stop_removed": sum(r["notes"]["trailing_removed"] for r in rows),
            "label_removed": sum(bool(r["notes"]["label_removed"]) for r in rows),
            "line_wrap_joined_in_kept_sentence": sum(bool(r["notes"]["wraps_joined"]) for r in rows),
            "line_wrap_joins_in_kept_sentences_total": sum(len(r["notes"]["wraps_joined"]) for r in rows),
            "whole_first_text_is_one_sentence": sum(r["notes"]["rest_dropped_chars"] == 0 for r in have),
        },
        "cleaned_sentence_chars": spread(lengths),
        "over_150": sum(n > 150 for n in lengths),
        "over_200": sum(n > 200 for n in lengths),
        "over_300": sum(n > 300 for n in lengths),
        "flags": {f: sum(f in r["flags"] for r in have) for f in FLAGS},
        "proteins_with_any_odd_flag": sum(any(f not in NOT_ODD for f in r["flags"]) for r in have),
        "proteins_with_no_flag_at_all": sum(not r["flags"] for r in have),
    }
    (HERE / "counts.json").write_text(json.dumps(counts, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")

    with (HERE / "sentences.csv").open("w", newline="", encoding="utf-8") as out:
        w = csv.writer(out)
        w.writerow(["gene", "symbol", "biotype", "number_of_texts", "raw_first_text", "raw_other_texts",
                    "cleaned_first_sentence", "length", "flags"])
        for r in rows:
            w.writerow([r["gene"], r["symbol"], r["biotype"], len(r["texts"]),
                        r["texts"][0] if r["texts"] else "", " || ".join(r["texts"][1:]),
                        r["sentence"], len(r["sentence"]), "; ".join(r["flags"])])

    lines = ["# Study P8b: every flagged sentence", "",
             "Written by recount.py. A flag means \"a person should look\", not \"this is wrong\".",
             "My reading of each group is in REPORT.md.", ""]
    for flag, meaning in FLAGS.items():
        hit = [r for r in have if flag in r["flags"]]
        lines += [f"## {flag}: {len(hit)}", "", meaning[0].upper() + meaning[1:] + ".", ""]
        for r in hit:
            extra = ""
            if flag == "label_removed":
                extra = f" (label: [{r['notes']['label_removed']}])"
            if flag == "wrap_joined":
                extra = " (joined at: " + " | ".join(
                    "\"" + w.strip() + "\"" for w in r["notes"]["wraps_joined"]) + ")"
            if flag in ("abbreviation_stop_skipped",):
                extra = " (skipped at: " + " | ".join(
                    "\"" + s.strip() + "\"" for s in r["notes"]["abbreviation_stops_skipped"]) + ")"
            lines.append(f"- **{r['symbol']}** ({len(r['sentence'])}){extra}: {r['sentence']}")
        lines.append("")
    lines += [f"## no sentence at all: {len(none)}", "",
              "Open Targets sent an empty functionDescriptions list.", ""]
    for r in none:
        lines.append(f"- **{r['symbol']}** ({r['gene']}), {r['biotype']}, {r['name']}")
    (HERE / "odd_cases.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    ordered = sorted(have, key=lambda r: (len(r["sentence"]), r["symbol"]))
    lines = ["# Study P8b: the 20 shortest and 20 longest cleaned sentences", "",
             "Written by recount.py. In full, nothing trimmed.", "", "## 20 shortest", ""]
    lines += [f"{i}. **{r['symbol']}** ({len(r['sentence'])}): {r['sentence']}"
              for i, r in enumerate(ordered[:20], 1)]
    lines += ["", "## 20 longest", ""]
    lines += [f"{i}. **{r['symbol']}** ({len(r['sentence'])}): {r['sentence']}"
              for i, r in enumerate(reversed(ordered[-20:]), 1)]
    (HERE / "extremes.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(counts, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
