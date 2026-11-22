"""Study P8 follow-up, step 2: compare Open Targets' function text with
UniProt's. Reads only saved files. No network, no Moonlight code.

Run from the repo root:

    python3 fixtures/probe_p8/open_targets_function/recount.py

It prints every count in the follow-up section of ../REPORT.md and rewrites
counts.json and compare.csv in this folder. Run it twice: they must not change.

Each protein lands in exactly one group, tried in this order:

  missing in both      neither side has any function text
  missing in OT        UniProt has text, Open Targets has none
  identical as sent    the two lists of texts are the same, letter for letter
  identical words      the same words in the same order once the packaging
                       is taken off both sides (see clean() below)
  hyphens only         the same letters in the same order; the only
                       differences are hyphens and spaces ("proinflammatory"
                       against "pro-inflammatory", "3'- processing" against
                       "3'-processing"). These too look like line-wrap leftovers.
  same first sentence  the first sentence matches, the rest does not
  different            not even the first sentence matches

"Packaging" is not wording. Open Targets' copy carries leftovers from
UniProt's text-file format: evidence tags in curly brackets
("{ECO:0000269|PubMed:123}"), an extra full stop at the end, a label such
as "[Isoform 1]: " in front, and a space after a hyphen where a line was
wrapped ("T-cell- attracting"). UniProt's JSON carries none of these.
"""

import csv
import gzip
import json
import pathlib
import re

HERE = pathlib.Path(__file__).resolve().parent
P8 = HERE.parent
ECO = re.compile(r"\s*\{ECO:[^}]*\}\.?")
LABEL = re.compile(r"^\[[^\]]+\]:\s*")
SENTENCE = re.compile(r"(?<=[a-z0-9\)])\. (?=[A-Z])")


def clean(text: str) -> str:
    """Take the packaging off one text. Words are not changed."""
    text = LABEL.sub("", ECO.sub("", text))
    text = re.sub(r"(?<=\w)- (?=\w)", "-", text)       # line-wrap space after a hyphen
    text = re.sub(r"(?<=/) (?=\w)", "", text)          # line-wrap space after a slash
    text = " ".join(text.split())
    return re.sub(r"[ .]+$", "", text)                 # full stops and spaces at the very end


def letters(texts: list) -> str:
    """Everything except hyphens and spaces."""
    return re.sub(r"[-\s]", "", " ".join(texts))


def first_sentence(text: str) -> str:
    return SENTENCE.split(text, maxsplit=1)[0]


def main() -> None:
    study = json.loads((P8 / "diseases.json").read_text(encoding="utf-8"))["diseases"]
    genes = {}
    for d in study:
        for t in d["targets"]:
            genes.setdefault(t["id"], t["symbol"])
    groups = ["missing in both", "missing in OT", "identical as sent", "identical words",
              "hyphens only", "same first sentence", "different"]
    tally = dict.fromkeys(groups, 0)
    packaging = {"evidence tag in curly brackets": 0, "isoform or form label in front": 0,
                 "extra full stop at the end": 0}
    extra = {"errors_in_answer": 0, "target_not_found": 0, "swissprot_id_same_as_uniprot_entry": 0,
             "number_of_texts_differs": 0, "first_sentence_same_after_cleaning": 0}
    rows, examples = [], {g: [] for g in groups}
    for gene, symbol in genes.items():
        answer = json.loads((HERE / "responses" / f"{gene}.json").read_text(encoding="utf-8"))
        extra["errors_in_answer"] += bool(answer.get("errors"))
        target = (answer.get("data") or {}).get("target")
        extra["target_not_found"] += target is None
        ot = target["functionDescriptions"] if target else []
        entry = json.loads(gzip.decompress((P8 / "responses" / f"{gene}.json.gz").read_bytes()))["results"][0]
        up = [t["value"] for c in entry.get("comments", [])
              if c["commentType"] == "FUNCTION" for t in c["texts"]]
        swiss = [p["id"] for p in (target or {}).get("proteinIds", []) if p["source"] == "uniprot_swissprot"]
        extra["swissprot_id_same_as_uniprot_entry"] += swiss == [entry["primaryAccession"]]
        extra["number_of_texts_differs"] += len(ot) != len(up)
        packaging["evidence tag in curly brackets"] += any(ECO.search(x) for x in ot)
        packaging["isoform or form label in front"] += any(LABEL.search(x) for x in ot)
        packaging["extra full stop at the end"] += any(x.rstrip().endswith(" .") for x in ot)
        ot_clean, up_clean = [clean(x) for x in ot], [clean(x) for x in up]
        ot_first = first_sentence(ot_clean[0]) if ot_clean else ""
        up_first = first_sentence(up_clean[0]) if up_clean else ""
        if not ot and not up:
            group = "missing in both"
        elif not ot:
            group = "missing in OT"
        elif ot == up:
            group = "identical as sent"
        elif " ".join(ot_clean).split() == " ".join(up_clean).split():
            group = "identical words"
        elif letters(ot_clean) == letters(up_clean):
            group = "hyphens only"
        elif ot_first == up_first:
            group = "same first sentence"
        else:
            group = "different"
        extra["first_sentence_same_after_cleaning"] += bool(ot) and ot_first == up_first
        tally[group] += 1
        a, b = " ".join(ot_clean), " ".join(up_clean)
        split = next((i for i, (x, y) in enumerate(zip(a, b)) if x != y), min(len(a), len(b)))
        rows.append([gene, symbol, entry["primaryAccession"], group, len(ot), len(up),
                     len(a), len(b), ot_first, up_first])
        if len(examples[group]) < 3:
            examples[group].append({
                "symbol": symbol, "uniprot": entry["primaryAccession"],
                "open_targets_texts": len(ot), "uniprot_texts": len(up),
                "same_for_the_first_n_characters": split,
                "open_targets_from_there": a[max(0, split - 60):split + 160],
                "uniprot_from_there": b[max(0, split - 60):split + 160],
            })
    version = json.loads((HERE / "data_version_before.json").read_text())["data"]["meta"]
    after = json.loads((HERE / "data_version_after.json").read_text())["data"]["meta"]
    schema = json.loads((HERE / "schema" / "target_type.json").read_text())["data"]["__type"]["fields"]
    field = next(f for f in schema if f["name"] == "functionDescriptions")
    uniprot_release = sorted({json.loads(l)["release"] for l in (P8 / "index.jsonl").read_text().splitlines()})
    counts = {
        "proteins": len(genes),
        "open_targets": {"data_version": version["dataVersion"], "api_version": version["apiVersion"],
                         "same_version_after_the_run": version == after},
        "uniprot_release": uniprot_release,
        "schema_field": {"name": field["name"], "description": field["description"]},
        "groups": tally,
        "open_targets_has_text": len(genes) - tally["missing in both"] - tally["missing in OT"],
        "packaging_seen_in_open_targets_text": packaging,
        "other": extra,
        "examples": {g: examples[g] for g in ("identical words", "hyphens only", "same first sentence", "different")},
    }
    assert sum(tally.values()) == len(genes)
    (HERE / "counts.json").write_text(json.dumps(counts, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    with (HERE / "compare.csv").open("w", newline="", encoding="utf-8") as out:
        w = csv.writer(out)
        w.writerow(["gene", "symbol", "uniprot", "group", "open_targets_texts", "uniprot_texts",
                    "open_targets_chars_cleaned", "uniprot_chars_cleaned",
                    "open_targets_first_sentence", "uniprot_first_sentence"])
        w.writerows(rows)
    print(json.dumps(counts, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
