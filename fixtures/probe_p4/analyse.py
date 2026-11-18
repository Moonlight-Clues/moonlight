"""Night watch P4, step 2: count, and write REPORT.md. No network.

Run from the repo root:   python3 fixtures/probe_p4/analyse.py

It reads only what probe.py saved: results/ (what Moonlight's own code made
of the answers) and responses/ (the raw answers). It writes analysis.json,
five .csv tables and REPORT.md, all under fixtures/probe_p4/.

It labels nothing right or wrong. It only counts what the data says.
"""

import collections
import csv
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from moonlight.records import (  # noqa: E402
    DOWN_ACTION_TYPES, UP_ACTION_TYPES, direction_from_action_types)

HERE = pathlib.Path(__file__).resolve().parent
RESPONSES = HERE / "responses"
OPPOSITE = {"up": "down", "down": "up"}
REVIEW_ROWS = 5


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def words(actions):
    return ", ".join(actions) if actions else "(no action words)"


def cell(text):
    return str(text).replace("|", "\\|").replace("\n", " ")


def table(head, rows):
    out = ["| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
    out += ["| " + " | ".join(cell(c) for c in row) + " |" for row in rows]
    return "\n".join(out)


def write_csv(name, head, rows):
    with (HERE / name).open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(head)
        writer.writerows(rows)


chosen = load(HERE / "diseases.json")
runs = load(HERE / "runs.json")
results = []
missing = []
for entry in chosen["diseases"]:
    path = HERE / "results" / f"{entry['id']}.json"
    if path.exists():
        results.append(load(path))
    else:
        missing.append(entry)
all_requests = [json.loads(line) for line in (RESPONSES / "index.jsonl").read_text().splitlines()]
MAIN_REQUESTS = runs[-1]["requests_sent_in_all"]
index = [e for e in all_requests if e["n"] <= MAIN_REQUESTS]  # the 50 study diseases
extra_requests = [e for e in all_requests if e["n"] > MAIN_REQUESTS]  # A3 only, see probe_alfuzosin.py
main_files = {e["file"] for e in index}
extra_results = [load(path) for path in sorted((HERE / "results_extra").glob("*.json"))]
symbol_of = {t["id"]: t["symbol"] for r in results for t in r["targets"]}
symbol_any = dict(symbol_of)
symbol_any.update({t["id"]: t["symbol"] for r in extra_results for t in r["targets"]})

# ---------------------------------------------------------------- Part A
# Every medicine-protein pair Moonlight built, shown or not. The same pair
# met under two diseases is one pair: its action words do not depend on
# the disease.
pairs = {}
for r in results:
    for p in r["tray"]:
        key = (p["medicine_id"], p["target_id"])
        old = pairs.setdefault(key, {
            "medicine_id": p["medicine_id"], "medicine": p["medicine"],
            "target_id": p["target_id"], "target": p["target"],
            "action_types": p["action_types"], "direction": p["direction"],
            "shown": collections.defaultdict(set)})
        if old["action_types"] != p["action_types"]:
            raise SystemExit(f"one pair, two sets of action words: {key}")
TABS = (("approved", "Approved"), ("narrower", "Narrower box"), ("wider_group", "Wider box"),
        ("being_studied", "In trials"), ("new_clues", "New clues"))
for r in results:
    for tab, label in TABS:
        for card in r[tab]:
            for p in card["paths"]:
                pairs[(p["medicine_id"], p["target_id"])]["shown"][label].add(r["name"])

by_value = collections.Counter()
by_value_shown = collections.Counter()
for pair in pairs.values():
    for value in pair["action_types"] or ["(no action words)"]:
        by_value[value] += 1
        if pair["shown"]:
            by_value_shown[value] += 1
by_direction = collections.Counter(p["direction"] for p in pairs.values())
by_direction_shown = collections.Counter(p["direction"] for p in pairs.values() if p["shown"])


def mapped_to(value):
    if value == "(no action words)":
        return "unknown"
    return direction_from_action_types([value])


def is_mapped(value):
    return value.strip().upper() in DOWN_ACTION_TYPES | UP_ACTION_TYPES


# Every actionType in the raw answers, also on proteins Moonlight did not look at.
raw_values = collections.Counter()
seen_mechanisms = set()
alfuzosin_rows = []
alfuzosin_listed = []
files = sorted(main_files)
for name in sorted({e["file"] for e in all_requests}):
    kind = name.split("/")[0]
    if kind not in ("target_drugs", "disease_drugs"):
        continue
    answer = load(RESPONSES / name)
    data = answer.get("data") or {}
    if kind == "disease_drugs":
        disease = data.get("disease") or {}
        for row in (disease.get("drugAndClinicalCandidates") or {}).get("rows") or []:
            drug = row.get("drug") or {}
            names = [drug.get("name") or "", (drug.get("parentMolecule") or {}).get("name") or ""]
            if any("ALFUZOSIN" in n.upper() for n in names):
                alfuzosin_listed.append({"file": name, "disease_id": disease.get("id"),
                                         "drug_id": drug.get("id"), "drug": drug.get("name"),
                                         "maxClinicalStage": row.get("maxClinicalStage")})
        continue
    target = data.get("target") or {}
    for row in (target.get("drugAndClinicalCandidates") or {}).get("rows") or []:
        drug = row.get("drug") or {}
        mechanisms = (drug.get("mechanismsOfAction") or {}).get("rows") or []
        for place, mechanism in enumerate(mechanisms):
            ids = tuple(t["id"] for t in mechanism.get("targets") or [])
            key = (drug.get("id"), place, mechanism.get("actionType"), ids)
            if name in main_files and key not in seen_mechanisms:
                seen_mechanisms.add(key)
                raw_values[mechanism.get("actionType") or "(empty)"] += 1
        parent = drug.get("parentMolecule") or {}
        names = [drug.get("name") or "", parent.get("name") or ""]
        if any("ALFUZOSIN" in n.upper() for n in names):
            on_target = []
            for mechanism in mechanisms:
                if any(t["id"] == target["id"] for t in mechanism.get("targets") or []):
                    if mechanism["actionType"] and mechanism["actionType"] not in on_target:
                        on_target.append(mechanism["actionType"])
            alfuzosin_rows.append({
                "file": name, "target_id": target["id"],
                "target": symbol_any.get(target["id"], target["id"]),
                "in_the_50_study_diseases": name in main_files,
                "drug_id": drug.get("id"), "drug": drug.get("name"),
                "parent": parent.get("name"),
                "mechanism_rows": [
                    {"actionType": m.get("actionType"),
                     "targets": [symbol_any.get(t["id"], t["id"]) for t in m.get("targets") or []]}
                    for m in mechanisms],
                "action_words_on_this_protein": on_target,
                "direction_of_this_row_alone": direction_from_action_types(on_target),
            })
alfuzosin_cards = []  # every card naming alfuzosin, study diseases and extra ones
alfuzosin_company = []  # every shown card on the same proteins, in the same diseases
for r in results + extra_results:
    proteins = set()
    for tab, label in TABS:
        for card in r[tab]:
            if "ALFUZOSIN" in card["medicine"].upper():
                for p in card["paths"]:
                    proteins.add(p["target_id"])
                    alfuzosin_cards.append([r["name"], label, card["medicine"], p["target"],
                                            words(p["action_types"]), p["direction"]])
                if not card["paths"]:
                    alfuzosin_cards.append([r["name"], label, card["medicine"],
                                            "(no path: none of its proteins is in the 25)", "-", "-"])
    for tab, label in TABS:
        for card in r[tab]:
            for p in card["paths"]:
                if p["target_id"] in proteins and "ALFUZOSIN" not in card["medicine"].upper():
                    alfuzosin_company.append([r["name"], p["target"], label, card["medicine"],
                                              words(p["action_types"]), p["direction"]])
alfuzosin_company.sort(key=lambda row: (row[0], row[1], row[2], row[3]))

mixed_unknown = sorted((p for p in pairs.values() if p["direction"] in ("mixed", "unknown")),
                       key=lambda p: (p["direction"], p["medicine"].casefold(), p["target"]))


def where_shown(pair):
    if not pair["shown"]:
        return "not shown on any card"
    return "; ".join(f"{label}: {', '.join(sorted(names))}"
                     for label, names in sorted(pair["shown"].items()))


# ---------------------------------------------------------------- Part B
per_disease = []
opposite_rows = []
both_ways_rows = []
one_way_rows = []
for r in results:
    on_protein = collections.defaultdict(list)  # target id -> approved paths, up or down
    for card in r["approved"]:  # the main Approved list only, not the two boxes
        for p in card["paths"]:
            if p["direction"] in OPPOSITE:
                on_protein[p["target_id"]].append(p)
    kind_of = {}
    for target_id, approved in on_protein.items():
        directions = {p["direction"] for p in approved}
        kind_of[target_id] = "one-way" if len(directions) == 1 else "both-ways"
        if len(directions) > 1:
            both_ways_rows.append({
                "disease": r["name"], "disease_id": r["id"],
                "target": approved[0]["target"], "target_id": target_id,
                "up": [(p["medicine"], p["action_types"]) for p in approved if p["direction"] == "up"],
                "down": [(p["medicine"], p["action_types"]) for p in approved if p["direction"] == "down"],
            })
    row = {"disease": r["name"], "disease_id": r["id"], "set": r["set"],
           "approved_cards": len(r["approved"]),
           "approved_cards_with_a_path": sum(1 for c in r["approved"] if c["paths"]),
           "one_way_proteins": sum(1 for k in kind_of.values() if k == "one-way"),
           "both_ways_proteins": sum(1 for k in kind_of.values() if k == "both-ways")}
    tally = collections.defaultdict(collections.Counter)  # one-way protein -> counts
    for tab, label in (("new_clues", "New clues"), ("being_studied", "In trials")):
        cards = r[tab]
        opposite_cards, same_cards, both_cards, other_cards = set(), set(), set(), set()
        pair_counts = collections.Counter()
        for card in cards:
            for p in card["paths"]:
                kind = kind_of.get(p["target_id"])
                if kind == "both-ways":
                    both_cards.add(card["medicine_id"])
                    pair_counts["on_both_ways"] += 1
                elif kind == "one-way":
                    approved = on_protein[p["target_id"]]
                    way = approved[0]["direction"]
                    if p["direction"] == OPPOSITE[way]:
                        what = "opposite"
                        opposite_cards.add(card["medicine_id"])
                        opposite_rows.append({
                            "disease": r["name"], "disease_id": r["id"], "tab": label,
                            "target": p["target"], "target_id": p["target_id"],
                            "approved": [(a["medicine"], a["direction"], a["action_types"])
                                         for a in approved],
                            "medicine": p["medicine"], "medicine_id": p["medicine_id"],
                            "direction": p["direction"], "action_types": p["action_types"],
                        })
                    elif p["direction"] == way:
                        what = "same"
                        same_cards.add(card["medicine_id"])
                    else:
                        what = "mixed_or_unknown"
                        other_cards.add(card["medicine_id"])
                    pair_counts[what] += 1
                    tally[p["target_id"]][f"{label}: {what}"] += 1
        row[label] = {
            "cards": len(cards),
            "cards_opposite_on_a_one_way_protein": len(opposite_cards),
            "cards_same_on_a_one_way_protein": len(same_cards),
            "cards_mixed_or_unknown_on_a_one_way_protein": len(other_cards),
            "cards_on_a_both_ways_protein": len(both_cards),
            "card_protein_pairs": dict(pair_counts),
        }
    for target_id, kind in kind_of.items():
        if kind == "one-way":
            approved = on_protein[target_id]
            one_way_rows.append({
                "disease": r["name"], "target": approved[0]["target"],
                "direction": approved[0]["direction"],
                "approved": sorted({a["medicine"] for a in approved}),
                "counts": dict(tally[target_id])})
    per_disease.append(row)


def total(label, key):
    return sum(row[label][key] for row in per_disease)


def pair_total(label, key):
    return sum(row[label]["card_protein_pairs"].get(key, 0) for row in per_disease)


totals = {
    label: {key: total(label, key) for key in (
        "cards", "cards_opposite_on_a_one_way_protein", "cards_same_on_a_one_way_protein",
        "cards_mixed_or_unknown_on_a_one_way_protein", "cards_on_a_both_ways_protein")}
    for label in ("New clues", "In trials")}
for label in totals:
    totals[label]["card_protein_pairs"] = {
        key: pair_total(label, key) for key in ("opposite", "same", "mixed_or_unknown", "on_both_ways")}
with_opposite = [row["disease"] for row in per_disease
                 if row["New clues"]["cards_opposite_on_a_one_way_protein"]
                 or row["In trials"]["cards_opposite_on_a_one_way_protein"]]
with_opposite_clue = [row["disease"] for row in per_disease
                      if row["New clues"]["cards_opposite_on_a_one_way_protein"]]
with_opposite_trial = [row["disease"] for row in per_disease
                       if row["In trials"]["cards_opposite_on_a_one_way_protein"]]

# ---------------------------------------------------------------- files
kinds = collections.Counter(e["kind"] for e in index)
(HERE / "analysis.json").write_text(json.dumps({
    "data_version": chosen["data_version"], "diseases_studied": len(results),
    "diseases_missing": missing, "requests": len(index), "requests_by_kind": kinds,
    "distinct_answers_saved": len(files),
    "pairs": len(pairs), "pairs_shown": sum(1 for p in pairs.values() if p["shown"]),
    "action_values": {v: {"pairs": n, "pairs_shown": by_value_shown[v],
                          "moonlight": mapped_to(v), "on_a_list": v == "(no action words)" or is_mapped(v)}
                      for v, n in by_value.most_common()},
    "raw_action_values_any_protein": raw_values,
    "pairs_by_direction": by_direction, "pairs_shown_by_direction": by_direction_shown,
    "alfuzosin_rows": alfuzosin_rows, "alfuzosin_on_disease_lists": alfuzosin_listed,
    "totals": totals, "diseases_with_an_opposite_card": with_opposite,
    "per_disease": per_disease, "opposite_cards": opposite_rows,
    "both_ways_proteins": both_ways_rows, "one_way_proteins": one_way_rows,
}, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")

write_csv("action_types.csv",
          ["actionType", "pairs", "pairs shown on a card", "Moonlight turns it into",
           "on one of Moonlight's two lists"],
          [[v, n, by_value_shown[v], mapped_to(v),
            "-" if v == "(no action words)" else ("yes" if is_mapped(v) else "NO")]
           for v, n in by_value.most_common()])
write_csv("mixed_unknown_pairs.csv",
          ["direction", "medicine", "medicine id", "protein", "protein id", "action words", "where shown"],
          [[p["direction"], p["medicine"], p["medicine_id"], p["target"], p["target_id"],
            words(p["action_types"]), where_shown(p)] for p in mixed_unknown])


def approved_words(approved):
    return "; ".join(f"{name} ({way}: {words(actions)})" for name, way, actions in approved)


write_csv("opposite_cards.csv",
          ["disease", "tab", "protein", "Approved medicines on this protein (direction: action words)",
           "card medicine", "card direction", "card action words"],
          [[o["disease"], o["tab"], o["target"], approved_words(o["approved"]),
            o["medicine"], o["direction"], words(o["action_types"])] for o in opposite_rows])
write_csv("both_ways_proteins.csv", ["disease", "protein", "Approved, up", "Approved, down"],
          [[b["disease"], b["target"],
            "; ".join(f"{m} ({words(a)})" for m, a in b["up"]),
            "; ".join(f"{m} ({words(a)})" for m, a in b["down"])] for b in both_ways_rows])
review = []
for r in results:
    with_path = [c for c in r["approved"] if c["paths"]][:REVIEW_ROWS]
    for card in with_path:
        for p in card["paths"]:
            review.append([r["name"], card["medicine"], p["target"], p["target_name"],
                           words(p["action_types"]), p["direction"]])
write_csv("doctor_review.csv",
          ["disease", "Approved medicine", "protein", "protein name", "action words",
           "Moonlight's direction"], review)

# ---------------------------------------------------------------- REPORT.md
L = []
add = L.append
first, last = runs[0], runs[-1]
add("# Night watch P4: can the \"up or down\" data be trusted?\n")
add("Read-only study. Nothing in moonlight/, web/ or tests/ was changed. Only Open Targets "
    "was asked. Every number below was counted by `analyse.py` from the saved answers. "
    "**Nothing here is labelled right or wrong.**\n")
add("## What was done\n")
add(f"- Open Targets data version: **{chosen['data_version']}**. "
    f"Run started {first['started']}, finished {last['finished']}.")
add(f"- Diseases studied: **{len(results)}** "
    f"({', '.join(f'{n} {s}' for s, n in collections.Counter(r['set'] for r in results).items())}). "
    "Ids were read from `fixtures/probe_p3/diseases.json` on the branch `probe-approval-proof`.")
if missing:
    add(f"- **Not studied, because Moonlight's code stopped on them:** "
        + "; ".join(f"{m['name']} ({m['id']})" for m in missing) + ". See \"What I did not verify\".")
add(f"- Requests sent to Open Targets: **{len(index)}** "
    f"({', '.join(f'{n} {k}' for k, n in kinds.most_common())}), one second apart. "
    f"Distinct raw answers saved under `responses/`: {len(files)}. "
    "`responses/index.jsonl` has one line per request and names the file holding its answer.")
add("- For each disease the probe ran the same functions as `moonlight/api.py`'s `_find`: "
    "top 25 proteins, the medicines on each, the disease's own list, one step up and one step "
    "down, then `engine.sort_into_tabs`.\n")

add("## PART A. The direction data\n")
add("### How Moonlight works out a direction (read from the code)\n")
add("`moonlight/records.py`, `direction_from_action_types`. Two lists, compared in capital letters:\n")
add(f"- **down**: {', '.join(sorted(DOWN_ACTION_TYPES))}")
add(f"- **up**: {', '.join(sorted(UP_ACTION_TYPES))}")
add("- words from both lists on one medicine-protein pair: **mixed**")
add("- no word from either list: **unknown**\n")
add("The action words come from one field only: `actionType` in the medicine's "
    "`mechanismsOfAction.rows`, and only from rows whose `targets` name this protein "
    "(`fetch.py`, `_action_types_on`). A medicine and its tablet forms are one item, so the "
    "words of all its forms are pooled.\n")
add("### A1. Every actionType value met\n")
add(f"Counted over **{len(pairs)}** distinct medicine-protein pairs: every medicine family "
    f"Moonlight met on the {len(symbol_of)} proteins it looked at, shown or not "
    f"({sum(1 for p in pairs.values() if p['shown'])} of the pairs are on at least one card). "
    "A pair with two action words is counted under both.\n")
add(table(["actionType", "pairs carrying it", "of those, on a card", "Moonlight turns it into",
           "on one of Moonlight's two lists?"],
          [[v, n, by_value_shown[v], mapped_to(v),
            "-" if v == "(no action words)" else ("yes" if is_mapped(v) else "**NO, not mapped**")]
           for v, n in by_value.most_common()]))
unmapped = [v for v in by_value if v != "(no action words)" and not is_mapped(v)]
add("")
add("**Values Moonlight does not map** (they are on neither list, so alone they give \"unknown\"): "
    + (", ".join(f"{v} ({by_value[v]} pair{'s' if by_value[v] != 1 else ''})" for v in sorted(unmapped, key=lambda v: -by_value[v]))
       or "none") + ".\n")
never = sorted((DOWN_ACTION_TYPES | UP_ACTION_TYPES) - {v.strip().upper() for v in by_value})
add("Words on Moonlight's lists that were never met on these pairs: "
    + (", ".join(never) or "none") + ".\n")
add("Direction of the pairs:\n")
add(table(["Moonlight's direction", "all pairs", "pairs on a card"],
          [[d, by_direction[d], by_direction_shown[d]] for d in ("down", "up", "mixed", "unknown")]))
add("")
add("For completeness, every `actionType` in the raw answers, including mechanism rows about "
    "proteins Moonlight did not look at (one count per distinct medicine form and mechanism row):\n")
add(table(["actionType", "mechanism rows", "on one of Moonlight's two lists?"],
          [[v, n, "yes" if is_mapped(v) else "**NO**"] for v, n in raw_values.most_common()]))
add("")
MIXED_UNKNOWN_PLACEHOLDER = len(L)
add("")
add("### A3. Alfuzosin\n")
ALFUZOSIN_PLACEHOLDER = len(L)
add("")
add("### A4. Review table for a doctor\n")
add(f"For each disease, the first {REVIEW_ROWS} medicines of the main Approved list (A to Z, the "
    "order the page uses) that have at least one path, with every protein of theirs among the 25 "
    "looked at. **No row is marked right or wrong. A doctor will judge.** Also in `doctor_review.csv`.\n")
add(table(["disease", "Approved medicine", "protein", "action words", "Moonlight's direction"],
          [[row[0], row[1], row[2], row[4], row[5]] for row in review]))
no_path = [r["name"] for r in results if not any(c["paths"] for c in r["approved"])]
add("")
add(f"Diseases with no Approved medicine that has a path ({len(no_path)}): "
    + (", ".join(no_path) or "none") + ".\n")

add("## PART B. Opposite directions\n")
add("Rules used, as asked. For each disease, a protein counts if at least one medicine of the "
    "**main Approved list** (not the two folded boxes) acts on it with direction up or down. "
    "Approved medicines whose direction on that protein is mixed or unknown are not used to "
    "decide. **One-way**: all those Approved medicines have the same direction. **Both-ways**: "
    "they disagree. A card is one medicine; a medicine acting on two proteins is one card, and "
    "is counted once in each column it belongs to.\n")
add("### B7. The numbers, all diseases together\n")
add(table(["", "New clues", "In trials"],
          [["cards in total", totals["New clues"]["cards"], totals["In trials"]["cards"]],
           ["cards pointing OPPOSITE to the Approved medicines on a one-way protein",
            totals["New clues"]["cards_opposite_on_a_one_way_protein"],
            totals["In trials"]["cards_opposite_on_a_one_way_protein"]],
           ["cards pointing the SAME way on a one-way protein (for comparison)",
            totals["New clues"]["cards_same_on_a_one_way_protein"],
            totals["In trials"]["cards_same_on_a_one_way_protein"]],
           ["cards with mixed or unknown direction on a one-way protein",
            totals["New clues"]["cards_mixed_or_unknown_on_a_one_way_protein"],
            totals["In trials"]["cards_mixed_or_unknown_on_a_one_way_protein"]],
           ["cards sitting on a both-ways protein",
            totals["New clues"]["cards_on_a_both_ways_protein"],
            totals["In trials"]["cards_on_a_both_ways_protein"]]]))
add("")
add(f"- Diseases with at least one opposite card: **{len(with_opposite)} of {len(results)}** "
    f"({len(with_opposite_clue)} have an opposite New clues card, {len(with_opposite_trial)} an "
    "opposite In trials card).")
add(f"- Diseases with at least one one-way protein: "
    f"{sum(1 for r in per_disease if r['one_way_proteins'])}. With at least one both-ways protein: "
    f"{sum(1 for r in per_disease if r['both_ways_proteins'])}. "
    f"With no Approved medicine that has an up or down path at all: "
    f"{sum(1 for r in per_disease if not r['one_way_proteins'] and not r['both_ways_proteins'])}.")
add(f"- One-way proteins in all (disease by disease): {len(one_way_rows)}. "
    f"Both-ways proteins: {len(both_ways_rows)}.")
add("- The same counts by card-and-protein pair instead of by card: New clues "
    + ", ".join(f"{k.replace('_', ' ')} {v}" for k, v in totals["New clues"]["card_protein_pairs"].items())
    + "; In trials "
    + ", ".join(f"{k.replace('_', ' ')} {v}" for k, v in totals["In trials"]["card_protein_pairs"].items())
    + ".\n")
add("### B7. The numbers, disease by disease\n")
add("NC = New clues cards, IT = In trials cards. \"opp\" = opposite on a one-way protein, "
    "\"same\" = same way on a one-way protein, \"both\" = on a both-ways protein.\n")
add(table(["disease", "Approved cards (with a path)", "one-way proteins", "both-ways proteins",
           "NC total", "NC opp", "NC same", "NC both", "IT total", "IT opp", "IT same", "IT both"],
          [[row["disease"], f"{row['approved_cards']} ({row['approved_cards_with_a_path']})",
            row["one_way_proteins"], row["both_ways_proteins"],
            row["New clues"]["cards"], row["New clues"]["cards_opposite_on_a_one_way_protein"],
            row["New clues"]["cards_same_on_a_one_way_protein"],
            row["New clues"]["cards_on_a_both_ways_protein"],
            row["In trials"]["cards"], row["In trials"]["cards_opposite_on_a_one_way_protein"],
            row["In trials"]["cards_same_on_a_one_way_protein"],
            row["In trials"]["cards_on_a_both_ways_protein"]] for row in per_disease]))
add("")
add("### B5 and B6. Every one-way protein, with its counts\n")
add(table(["disease", "protein", "direction of its Approved medicines", "Approved medicines",
           "NC opposite", "NC same", "IT opposite", "IT same"],
          [[o["disease"], o["target"], o["direction"], ", ".join(o["approved"]),
            o["counts"].get("New clues: opposite", 0), o["counts"].get("New clues: same", 0),
            o["counts"].get("In trials: opposite", 0), o["counts"].get("In trials: same", 0)]
           for o in one_way_rows]))
add("")
add("### B8. Every opposite card. The main result\n")
add(f"**{len(opposite_rows)} opposite cards** (card-and-protein pairs), on "
    f"{len({(o['disease_id'], o['target_id']) for o in opposite_rows})} one-way proteins. They are "
    "grouped by disease and protein so the Approved medicines are written once per group, not "
    "once per row. Every Approved medicine on the protein is named, with its direction and "
    "action words, and every opposite card is listed. Nothing was left out. The same list, one "
    "full row per card, is in `opposite_cards.csv`. **No row is labelled a problem or not a problem.**\n")
groups = collections.OrderedDict()
for o in opposite_rows:
    groups.setdefault((o["disease"], o["target"]), []).append(o)
number = 0
for (disease_name, target_name), rows in groups.items():
    way = rows[0]["approved"][0][1]
    add(f"**{disease_name} / {target_name}.** Approved medicines turn it **{way}**: "
        + "; ".join(f"{name} ({words(actions)})" for name, _, actions in rows[0]["approved"]) + ".\n")
    body = []
    for o in rows:
        number += 1
        body.append([number, o["tab"], o["medicine"], o["direction"], words(o["action_types"])])
    add(table(["#", "tab", "card medicine", "card direction", "card action words"], body))
    add("")
add("")
add("### B9. Every both-ways protein\n")
add(f"**{len(both_ways_rows)} rows.** Also in `both_ways_proteins.csv`.\n")
add(table(["disease", "protein", "Approved medicines turning it UP", "Approved medicines turning it DOWN"],
          [[b["disease"], b["target"],
            "; ".join(f"{m} ({words(a)})" for m, a in b["up"]),
            "; ".join(f"{m} ({words(a)})" for m, a in b["down"])] for b in both_ways_rows]))
add("")

# A2, filled in here so the long list sits in its place.
a2 = ["### A2. Every pair whose direction is \"mixed\" or \"unknown\"\n",
      f"**{len(mixed_unknown)} pairs** ({by_direction['mixed']} mixed, {by_direction['unknown']} unknown). "
      f"{sum(1 for p in mixed_unknown if p['shown'])} of them are on at least one card. "
      "Also in `mixed_unknown_pairs.csv`.\n",
      table(["direction", "medicine", "protein", "action words behind it", "where it is shown"],
            [[p["direction"], p["medicine"], p["target"], words(p["action_types"]), where_shown(p)]
             for p in mixed_unknown])]
L[MIXED_UNKNOWN_PLACEHOLDER] = "\n".join(a2) + "\n"

a3 = []
in_main = [a for a in alfuzosin_rows if a["in_the_50_study_diseases"]]
a3.append(f"**In the 50 study diseases:** rows naming alfuzosin in the saved protein answers: "
          f"**{len(in_main)}**. None of the {len(symbol_of)} proteins looked at for those diseases "
          "has alfuzosin among its medicines, so it is on no card there.\n" if not in_main else
          f"**In the 50 study diseases:** {len(in_main)} rows name alfuzosin.\n")
if extra_results:
    a3.append("So one extra step was taken, for this question only (`probe_alfuzosin.py`). The "
              "medicine lists saved by probe P3 name alfuzosin under these diseases: "
              + ", ".join(f"{r['name']} ({r['id']})" for r in extra_results)
              + f". The same Moonlight steps were run for them ({len(extra_requests)} more requests). "
              "**These extra diseases are not counted in A1, A2, A4 or Part B.**\n")
a3.append("Every card naming alfuzosin:\n")
a3.append(table(["disease", "tab", "medicine", "protein", "action words", "Moonlight's direction"],
                alfuzosin_cards))
a3.append("")
ups = [row for row in alfuzosin_cards if row[5] == "up"]
a3.append("**Alfuzosin is shown as \"up\"** on " + (
    ", ".join(sorted({f"{row[3]} ({row[0]})" for row in ups})) if ups else "no card") + ".\n")
a3.append("**Exactly which field made it so.** Every raw row naming alfuzosin in the saved "
          "answers to \"which medicines act on this protein?\" (`target.drugAndClinicalCandidates"
          ".rows[].drug`). The field Moonlight reads is `drug.mechanismsOfAction.rows[].actionType`. "
          "Moonlight asks each question twice; answers that were letter for letter the same are "
          "saved once.\n")
a3.append(table(
    ["saved file (under responses/)", "protein asked about", "form (id)",
     "ALL its mechanism rows, as sent: actionType -> proteins",
     "action words Moonlight takes for this protein", "direction"],
    [[a["file"], a["target"], f"{a['drug']} ({a['drug_id']})",
      "; ".join(f"{m['actionType']} -> {', '.join(m['targets'])}" for m in a["mechanism_rows"])
      or "(none)",
      words(a["action_words_on_this_protein"]), a["direction_of_this_row_alone"]]
     for a in alfuzosin_rows]))
a3.append("")
a3.append("So the word behind \"up\" is the database's own `actionType` value for alfuzosin on "
          "these proteins, as printed above. Moonlight's list turns that word into \"up\"; it did "
          "not pick a different word or mix up two medicines. Whether the database's word is "
          "pharmacologically right is for a doctor to say.\n")
a3.append("For comparison only, every other shown card on the same proteins in the same diseases:\n")
a3.append(table(["disease", "protein", "tab", "medicine", "action words", "Moonlight's direction"],
                alfuzosin_company))
L[ALFUZOSIN_PLACEHOLDER] = "\n".join(a3) + "\n"

tail = HERE / "REPORT_NOTES.md"  # the hand-written end of the report
(HERE / "REPORT.md").write_text(
    "\n".join(L) + "\n" + (tail.read_text(encoding="utf-8") if tail.exists() else ""),
    encoding="utf-8")
print("diseases:", len(results), "missing:", len(missing), "requests:", len(index))
print("pairs:", len(pairs), dict(by_direction))
print("unmapped:", unmapped)
print("mixed/unknown pairs:", len(mixed_unknown))
print("alfuzosin raw rows:", len(alfuzosin_rows), "cards:", alfuzosin_cards)
print("totals:", json.dumps(totals))
print("diseases with an opposite card:", len(with_opposite))
print("opposite rows:", len(opposite_rows), "both-ways proteins:", len(both_ways_rows))
