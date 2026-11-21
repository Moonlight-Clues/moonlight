"""Night order 1 (probe P5), step 3: count. Reads saved files, never the network.

Run from the repo root, after probe.py and check_links.py:

    python3 fixtures/probe_p5/analyse.py

It reads results/*.json, links.jsonl, link_controls.jsonl, runs.json and
responses/index.jsonl, and writes baseline.json, REPORT.md and four lists:
dead_links.csv, links_by_status.csv, withdrawn_reports.csv, trials_missing.csv.

It labels nothing right or wrong. It counts.

The comparison numbers of the two earlier studies are read with "git show"
from their branches (probe-direction and probe-approval-proof). If a branch
is not there, that comparison is left out and the report says so.
"""

import collections
import csv
import json
import pathlib
import subprocess
import urllib.parse

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
APPROVAL, WITHDRAWAL = "APPROVAL", "WITHDRAWAL"
STRONG = ("DailyMed", "FDA", "EMA Human Drugs")  # group A, as in probe_p3
OPPOSITE = {"up": "down", "down": "up"}
APPROVED_TABS = ("approved", "narrower", "wider_group")
TABS = APPROVED_TABS + ("being_studied", "new_clues")
TAB_WORDS = {"approved": "Approved (main list)", "narrower": "Approved: narrower-disease box",
             "wider_group": "Approved: wider-group box", "being_studied": "In trials",
             "new_clues": "New clues"}
PROOF_GROUPS = "ABCDEFN"
PROOF_WORDS = {
    "A": "at least one approval report from DailyMed, FDA or EMA",
    "B": "approval reports only from TTD",
    "C": "approval reports only from PMDA",
    "D": "approval reports only from ATC",
    "E": "no APPROVAL report at all",
    "F": "anything else",
    "N": "the card's medicine is not on the list(s) at all, so it has no reports to group",
}
DEAD = ("dead_404", "dead_410", "dead_dns_failure")
NOT_APPROVED_ELSEWHERE = "not approved elsewhere"
NOT_TOP_25 = "not on a top-25 protein"
OTHER = "other"
REASONS = (NOT_APPROVED_ELSEWHERE, NOT_TOP_25, OTHER)


def load(path):
    return json.loads(pathlib.Path(path).read_text(encoding="utf-8"))


def lines(path):
    path = pathlib.Path(path)
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def git_json(spec):
    done = subprocess.run(["git", "show", spec], cwd=ROOT, capture_output=True, text=True)
    return json.loads(done.stdout) if done.returncode == 0 else None


def cell(text):
    return str(text).replace("|", "\\|").replace("\n", " ")


def table(head, rows):
    out = ["| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
    out += ["| " + " | ".join(cell(c) for c in row) + " |" for row in rows]
    return "\n".join(out) + "\n"


def write_csv(name, head, rows):
    with (HERE / name).open("w", newline="", encoding="utf-8") as out:
        writer = csv.writer(out)
        writer.writerow(head)
        writer.writerows(rows)


def is_trial_stage(stage):
    """Moonlight's own test (filter.group_of) for "in trials for the disease"."""
    return bool(stage) and (stage.startswith("PHASE_") or stage.startswith("EARLY_PHASE_"))


def proof_group(reports):
    """probe_p3's groups, from a medicine's reports."""
    sources = sorted({r["source"] for r in reports if r["stage"] == APPROVAL})
    if not sources:
        return "E"
    if any(source in STRONG for source in sources):
        return "A"
    if sources == ["TTD"]:
        return "B"
    if sources == ["PMDA"]:
        return "C"
    if sources == ["ATC"]:
        return "D"
    return "F"


# ------------------------------------------------------------------ read
study = load(HERE / "diseases.json")
runs = load(HERE / "runs.json")
results, missing_results = [], []
for entry in study["diseases"]:
    file = HERE / "results" / f"{entry['id']}.json"
    if file.exists():
        results.append(load(file))
    else:
        missing_results.append(entry)
link_of = {line["url"]: line for line in lines(HERE / "links.jsonl")}
controls = lines(HERE / "link_controls.jsonl")
index = lines(HERE / "responses" / "index.jsonl")


def outcome_of(url):
    return link_of[url]["outcome"] if url in link_of else "not_asked_yet"


# ---------------------------------------------------------------- 1 LINKS
def links_part(r):
    by_tab = {}
    urls = {}
    for card in r["cards"]:
        tab = by_tab.setdefault(card["tab"], {"cards": 0, "cards_with_no_link": 0})
        tab["cards"] += 1
        if card["source"]:
            urls.setdefault(card["source"], []).append(card)
        else:
            tab["cards_with_no_link"] += 1
    outcomes = collections.Counter(outcome_of(url) for url in urls)
    dead = sorted(url for url in urls if outcome_of(url) in DEAD)
    return {
        "cards": len(r["cards"]),
        "cards_with_a_link": sum(len(cards) for cards in urls.values()),
        "cards_with_no_link": sum(tab["cards_with_no_link"] for tab in by_tab.values()),
        "cards_with_no_link_by_tab": {t: by_tab[t]["cards_with_no_link"]
                                      for t in TABS if t in by_tab},
        "different_links": len(urls),
        "links_by_outcome": dict(sorted(outcomes.items())),
        "dead_links": len(dead),
        "cards_showing_a_dead_link": sum(len(urls[url]) for url in dead),
        "dead_link_list": dead,
    }


# ------------------------------------------------------------ 2 WITHDRAWN
def reports_for(r, card):
    """(the card's reports, True if the card's medicine is on a list)."""
    if card["tab"] == "approved":
        family = r["own_list"].get(card["id"])
        return (family["reports"], True) if family else ([], False)
    entries = r["box_lists"].get(card["id"], [])
    reports = []
    for entry in entries:
        reports += [rep for rep in entry["reports"] if rep not in reports]
    return reports, bool(entries)


def withdrawn_part(r, rows):
    part = {}
    for name, tabs in (("main_list", ("approved",)), ("boxes", ("narrower", "wider_group"))):
        with_approval, without_approval, not_listed = [], [], 0
        for card in r["cards"]:
            if card["tab"] not in tabs:
                continue
            reports, listed = reports_for(r, card)
            if not listed:
                not_listed += 1
                continue
            withdrawal = [rep for rep in reports if rep["stage"] == WITHDRAWAL]
            if not withdrawal:
                continue
            has_approval = any(rep["stage"] == APPROVAL for rep in reports)
            (with_approval if has_approval else without_approval).append(card["id"])
            rows.append([r["name"], r["id"], TAB_WORDS[card["tab"]], card["medicine"], card["id"],
                         "yes" if has_approval else "no", proof_group(reports),
                         "; ".join(sorted({rep["source"] for rep in withdrawal})),
                         " ".join(rep["url"] or "(no link)" for rep in withdrawal)])
        part[name] = {
            "cards_with_a_withdrawal_report_and_an_approval_report": len(with_approval),
            "cards_with_a_withdrawal_report_and_no_approval_report": len(without_approval),
            "with_approval_report_ids": sorted(with_approval),
            "without_approval_report_ids": sorted(without_approval),
            "cards_not_on_the_list_so_reports_not_known": not_listed,
        }
    return part


# --------------------------------------------------------------- 3 TRIALS
def trials_part(r, rows):
    shown = {card["id"] for card in r["cards"] if card["tab"] == "being_studied"}
    tabs_of = collections.defaultdict(list)
    for card in r["cards"]:
        tabs_of[card["id"]].append(card["tab"])
    withdrawn_ids = set(r["withdrawn_on_own_list"]) | set(r["withdrawn_on_a_neighbour_list"])
    stage_words = collections.Counter(f["stage_for_disease"] for f in r["own_list"].values())
    listed = {fid: f for fid, f in r["own_list"].items() if is_trial_stage(f["stage_for_disease"])}
    reasons = collections.Counter()
    details = collections.Counter()
    missing = []
    for fid, family in listed.items():
        if fid in shown:
            continue
        tray = r["in_tray"].get(fid)
        withdrawn = fid in withdrawn_ids or bool(tray and True in tray["withdrawn"])
        listed_approved = family["best_stage_of_listed_forms"] == APPROVAL
        if tray is None:
            if not listed_approved:
                reason, detail = NOT_APPROVED_ELSEWHERE, "and not on a top-25 protein either"
            else:
                reason = NOT_TOP_25
                detail = "also withdrawn in some country" if withdrawn else ""
        elif withdrawn:
            reason, detail = OTHER, "withdrawn in some country"
        elif tray["best_stage"] != APPROVAL:
            reason, detail = NOT_APPROVED_ELSEWHERE, "on a top-25 protein"
        else:
            reason = OTHER
            detail = (f"the protein route sorted it as {tray['tray_group']}"
                      f" (its stage for this disease there: {tray['disease_stage']})")
        reasons[reason] += 1
        details[f"{reason}: {detail}" if detail else reason] += 1
        missing.append({"id": fid, "reason": reason, "detail": detail,
                        "stage_on_the_list": family["stage_for_disease"],
                        "shown_in": tabs_of.get(fid, [])})
        rows.append([r["name"], r["id"], family["name"], fid, family["stage_for_disease"],
                     family["best_stage_of_listed_forms"], reason, detail,
                     ", ".join(TAB_WORDS[t] for t in tabs_of.get(fid, [])) or "nowhere"])
    not_listed_in_trials = collections.Counter()
    for fid in shown:
        if fid not in listed:
            family = r["own_list"].get(fid)
            not_listed_in_trials[
                f"list says {family['stage_for_disease']}" if family else "not on the list"] += 1
    return {
        "medicines_on_the_disease_list": len(r["own_list"]),
        "list_by_stage_word": dict(sorted(stage_words.items(), key=str)),
        "listed_in_trials": len(listed),
        "shown_in_in_trials": len(shown),
        "listed_in_trials_and_shown": len(set(listed) & shown),
        "listed_in_trials_and_not_shown": len(missing),
        "not_shown_by_rule": {reason: reasons.get(reason, 0) for reason in REASONS},
        "not_shown_by_rule_in_detail": dict(sorted(details.items())),
        "shown_in_in_trials_but_not_listed_in_trials": dict(not_listed_in_trials),
        "not_shown": sorted(missing, key=lambda m: m["id"]),
    }


# ---------------------------------------------------------------- 4 PROOF
def proof_part(r):
    part = {}
    for name, tabs in (("main_list", ("approved",)), ("boxes", ("narrower", "wider_group"))):
        groups = collections.Counter()
        ids = collections.defaultdict(list)
        for card in r["cards"]:
            if card["tab"] in tabs:
                reports, listed = reports_for(r, card)
                group = proof_group(reports) if listed else "N"
                groups[group] += 1
                ids[group].append(card["id"])
        part[name] = {"cards": sum(groups.values()),
                      "by_group": {g: groups.get(g, 0) for g in PROOF_GROUPS},
                      "ids_outside_group_A": {g: sorted(ids[g]) for g in PROOF_GROUPS
                                              if g != "A" and ids[g]}}
    approved = [c for c in r["cards"] if c["tab"] in APPROVED_TABS]
    part["moonlight_own_lines"] = {
        "japan_line": sum(1 for c in approved if (c["proof_note"] or "").startswith("Approved in Japan")),
        "no_regulator_line": sum(1 for c in approved if (c["proof_note"] or "").startswith("The database lists")),
        "red_warning": sum(1 for c in approved if c["warning"]),
    }
    # The same count on probe_p3's own base: the disease's own list only.
    p3_base = collections.Counter(
        proof_group(f["reports"]) for fid, f in r["own_list"].items()
        if f["approved_for_disease"] and True not in f["withdrawn_notes"])
    part["probe_p3_base_own_list_only"] = {g: p3_base.get(g, 0) for g in "ABCDEF"}
    return part


# ------------------------------------------------------------ 5 DIRECTION
def direction_part(r):
    on_protein = collections.defaultdict(set)
    approved = [c for c in r["cards"] if c["tab"] == "approved"]
    for card in approved:  # the main Approved list only, as in probe_p4
        for p in card["proteins"]:
            if p["direction"] in OPPOSITE:
                on_protein[p["target_id"]].add(p["direction"])
    kind = {t: ("one-way" if len(d) == 1 else "both-ways") for t, d in on_protein.items()}
    part = {
        "approved_cards": len(approved),
        "approved_cards_with_a_path": sum(1 for c in approved if c["proteins"]),
        "one_way_proteins": sum(1 for k in kind.values() if k == "one-way"),
        "both_ways_proteins": sum(1 for k in kind.values() if k == "both-ways"),
        "one_way_proteins_on_the_live_site": len(r["one_way"]),
    }
    for tab, label in (("new_clues", "New clues"), ("being_studied", "In trials")):
        cards = [c for c in r["cards"] if c["tab"] == tab]
        sets = collections.defaultdict(set)
        pairs = collections.Counter()
        opposite_list = []
        for card in cards:
            for p in card["proteins"]:
                if p["opposite_way"]:
                    sets["line"].add(card["id"])
                where = kind.get(p["target_id"])
                if where == "both-ways":
                    what = "on_both_ways"
                elif where == "one-way":
                    way = next(iter(on_protein[p["target_id"]]))
                    if p["direction"] == OPPOSITE[way]:
                        what = "opposite"
                        opposite_list.append([card["id"], p["symbol"]])
                    elif p["direction"] == way:
                        what = "same"
                    else:
                        what = "mixed_or_unknown"
                else:
                    continue
                sets[what].add(card["id"])
                pairs[what] += 1
        part[label] = {
            "cards": len(cards),
            "cards_opposite_on_a_one_way_protein": len(sets["opposite"]),
            "cards_same_on_a_one_way_protein": len(sets["same"]),
            "cards_mixed_or_unknown_on_a_one_way_protein": len(sets["mixed_or_unknown"]),
            "cards_on_a_both_ways_protein": len(sets["on_both_ways"]),
            "card_protein_pairs": dict(pairs),
            "cards_carrying_the_opposite_way_line_on_the_live_site": len(sets["line"]),
            "opposite_card_and_protein": sorted(opposite_list),
        }
    unknown = {}
    for tab in TABS:
        cards = [c for c in r["cards"] if c["tab"] == tab]
        if not cards and tab in ("narrower", "wider_group"):
            continue
        unknown[tab] = {
            "cards": len(cards),
            "cards_with_no_protein_shown": sum(1 for c in cards if not c["proteins"]),
            "cards_with_an_unknown_direction": sum(
                1 for c in cards if any(p["direction"] == "unknown" for p in c["proteins"])),
            "cards_where_every_direction_is_unknown": sum(
                1 for c in cards if c["proteins"]
                and all(p["direction"] == "unknown" for p in c["proteins"])),
            "cards_with_a_mixed_direction": sum(
                1 for c in cards if any(p["direction"] == "mixed" for p in c["proteins"])),
            "card_protein_pairs": sum(len(c["proteins"]) for c in cards),
            "card_protein_pairs_unknown": sum(
                1 for c in cards for p in c["proteins"] if p["direction"] == "unknown"),
            "card_protein_pairs_mixed": sum(
                1 for c in cards for p in c["proteins"] if p["direction"] == "mixed"),
        }
    part["unknown_directions"] = unknown
    words = collections.Counter()
    for card in r["cards"]:
        for p in card["proteins"]:
            if p["direction"] in ("unknown", "mixed"):
                words[(p["direction"], ", ".join(p["action_types"]) or "(no action word)")] += 1
    part["_words"] = words
    return part


withdrawn_rows, trial_rows = [], []
per_disease = []
all_words = collections.Counter()
for r in results:
    direction = direction_part(r)
    all_words.update(direction.pop("_words"))
    per_disease.append({
        "id": r["id"], "name": r["name"], "set": r["set"],
        "cards_by_tab": {t: sum(1 for c in r["cards"] if c["tab"] == t) for t in TABS},
        "counted_not_named": {**r["left_out"],
                              "new_clues_left_out_by_hand": r["new_clues_left_out_by_hand"]},
        "differences_from_api_clues": r["differences_from_api_clues"],
        "links": links_part(r),
        "withdrawn": withdrawn_part(r, withdrawn_rows),
        "trials": trials_part(r, trial_rows),
        "proof": proof_part(r),
        "direction": direction,
    })


def total(*keys):
    def dig(d):
        for key in keys:
            d = d[key]
        return d
    return sum(dig(d) for d in per_disease)


def total_dict(*keys):
    out = collections.Counter()
    for d in per_disease:
        inner = d
        for key in keys:
            inner = inner[key]
        out.update(inner)
    return dict(out)


# links, over all diseases together: each different link once
all_links = {}
for r in results:
    for card in r["cards"]:
        if card["source"]:
            use = all_links.setdefault(card["source"], {"cards": 0, "diseases": set()})
            use["cards"] += 1
            use["diseases"].add(r["name"])
host_table = collections.defaultdict(collections.Counter)
status_table = collections.defaultdict(collections.Counter)
redirect_ends = collections.Counter()
for url in all_links:
    host = urllib.parse.urlsplit(url).netloc.lower()
    outcome = outcome_of(url)
    host_table[host][outcome] += 1
    line = link_of.get(url)
    if line:
        first = next((s for s in line["steps"] if "status" in s or "error" in s), {})
        status_table[host][str(line["final_status"]) if line["final_status"] else outcome] += 1
        if line["hops"] and line["outcome"] == "ok":
            end = urllib.parse.urlsplit(line["final_url"])
            same_page = line["final_url"].split("?")[0].rstrip("/").lower().replace("http://", "https://") \
                == url.split("?")[0].rstrip("/").lower()
            redirect_ends[(host, "the same address, written a little differently" if same_page
                           else end.netloc + end.path)] += 1
dead_rows = []
for url, use in sorted(all_links.items()):
    if outcome_of(url) in DEAD:
        dead_rows.append([urllib.parse.urlsplit(url).netloc.lower(), outcome_of(url), url,
                          use["cards"], "; ".join(sorted(use["diseases"]))])
dead_by_host = collections.Counter(row[0] for row in dead_rows)
outcomes_all = collections.Counter(outcome_of(url) for url in all_links)
head_then_get = sum(1 for url in all_links if url in link_of
                    and any(s["method"] == "GET" for s in link_of[url]["steps"]))

totals = {
    "diseases": len(per_disease),
    "cards_by_tab": {t: total("cards_by_tab", t) for t in TABS},
    "counted_not_named": total_dict("counted_not_named"),
    "links": {
        "cards": total("links", "cards"),
        "cards_with_a_link": total("links", "cards_with_a_link"),
        "cards_with_no_link": total("links", "cards_with_no_link"),
        "cards_with_no_link_by_tab": total_dict("links", "cards_with_no_link_by_tab"),
        "different_links": len(all_links),
        "links_asked": sum(1 for url in all_links if url in link_of and link_of[url]["steps"]),
        "links_where_get_was_needed": head_then_get,
        "links_by_outcome": dict(sorted(outcomes_all.items())),
        "dead_links": len(dead_rows),
        "dead_links_by_host": dict(dead_by_host.most_common()),
        "cards_showing_a_dead_link": sum(row[3] for row in dead_rows),
        "links_by_host_and_outcome": {h: dict(c) for h, c in sorted(host_table.items())},
    },
    "withdrawn": {
        box: {key: total("withdrawn", box, key) for key in (
            "cards_with_a_withdrawal_report_and_an_approval_report",
            "cards_with_a_withdrawal_report_and_no_approval_report",
            "cards_not_on_the_list_so_reports_not_known")}
        for box in ("main_list", "boxes")},
    "trials": {
        "listed_in_trials": total("trials", "listed_in_trials"),
        "shown_in_in_trials": total("trials", "shown_in_in_trials"),
        "listed_in_trials_and_shown": total("trials", "listed_in_trials_and_shown"),
        "listed_in_trials_and_not_shown": total("trials", "listed_in_trials_and_not_shown"),
        "not_shown_by_rule": total_dict("trials", "not_shown_by_rule"),
        "not_shown_by_rule_in_detail": dict(sorted(total_dict(
            "trials", "not_shown_by_rule_in_detail").items())),
        "shown_in_in_trials_but_not_listed_in_trials": total_dict(
            "trials", "shown_in_in_trials_but_not_listed_in_trials"),
        "list_by_stage_word": dict(sorted(total_dict("trials", "list_by_stage_word").items(), key=str)),
    },
    "proof": {
        "main_list": total_dict("proof", "main_list", "by_group"),
        "boxes": total_dict("proof", "boxes", "by_group"),
        "moonlight_own_lines": total_dict("proof", "moonlight_own_lines"),
        "probe_p3_base_own_list_only": total_dict("proof", "probe_p3_base_own_list_only"),
    },
    "direction": {
        "one_way_proteins": total("direction", "one_way_proteins"),
        "both_ways_proteins": total("direction", "both_ways_proteins"),
        **{label: {key: total("direction", label, key) for key in (
            "cards", "cards_opposite_on_a_one_way_protein", "cards_same_on_a_one_way_protein",
            "cards_mixed_or_unknown_on_a_one_way_protein", "cards_on_a_both_ways_protein",
            "cards_carrying_the_opposite_way_line_on_the_live_site")}
           for label in ("New clues", "In trials")},
        "diseases_with_an_opposite_card": sum(
            1 for d in per_disease
            if d["direction"]["New clues"]["cards_opposite_on_a_one_way_protein"]
            or d["direction"]["In trials"]["cards_opposite_on_a_one_way_protein"]),
        "unknown_directions": {
            tab: {key: sum(d["direction"]["unknown_directions"].get(tab, {}).get(key, 0)
                           for d in per_disease)
                  for key in ("cards", "cards_with_no_protein_shown",
                              "cards_with_an_unknown_direction",
                              "cards_where_every_direction_is_unknown",
                              "cards_with_a_mixed_direction", "card_protein_pairs",
                              "card_protein_pairs_unknown", "card_protein_pairs_mixed")}
            for tab in TABS},
        "action_words_behind_unknown_and_mixed": [
            {"direction": d, "action_words": w, "card_protein_pairs": n}
            for (d, w), n in sorted(all_words.items(), key=lambda kv: (-kv[1], kv[0]))],
    },
}

requests_by_kind = collections.Counter(entry["kind"] for entry in index)
refusals = lines(HERE / "refusals.jsonl")  # written as they happen, by every run
meta = {
    "study": "Night order 1, 21 Nov 2026: the baseline (probe P5)",
    "open_targets_data_version": study["data_version"],
    "moonlight_code_commit": runs[0]["code_commit"],
    # From the index, so a run that was cut off before it could sign off counts too.
    "open_targets_run": {"started": index[0]["at"], "finished": index[-1]["at"],
                         "runs_that_finished": len(runs)},
    "open_targets_requests": len(index),
    "open_targets_requests_by_kind": dict(requests_by_kind),
    "open_targets_different_answers_saved": len({entry["file"] for entry in index}),
    "open_targets_answers_with_errors": sum(1 for entry in index if entry["has_errors"]),
    "open_targets_refusals_or_network_failures": len(refusals),
    "diseases_asked": len(study["diseases"]),
    "diseases_with_no_result": [d["name"] for d in missing_results],
    "top_proteins_looked_at": runs[0]["top_targets"],
    "link_check": {
        "first_request": min((s["at"] for line in link_of.values() for s in line["steps"]),
                             default=None),
        "last_request": max((s["at"] for line in link_of.values() for s in line["steps"]),
                            default=None),
        "requests_sent": sum(len(line["steps"]) for line in link_of.values()),
    },
}
(HERE / "baseline.json").write_text(json.dumps(
    {"meta": meta, "totals": totals, "diseases": per_disease}, indent=1, ensure_ascii=False) + "\n",
    encoding="utf-8")

write_csv("dead_links.csv", ["host", "outcome", "link", "cards showing it", "diseases"], dead_rows)
write_csv("links_by_status.csv",
          ["link", "host", "outcome", "final status", "final address", "redirect hops",
           "requests made", "cards showing it"],
          [[url, link_of[url]["host"], link_of[url]["outcome"], link_of[url]["final_status"],
            link_of[url]["final_url"], link_of[url]["hops"],
            " > ".join(f"{s['method']} {s.get('status') or s.get('error')}"
                       for s in link_of[url]["steps"]), use["cards"]]
           if url in link_of else [url, "", "not_asked_yet", "", "", "", "", use["cards"]]
           for url, use in sorted(all_links.items())])
write_csv("withdrawn_reports.csv",
          ["disease", "disease id", "where the card is", "medicine", "medicine id",
           "has an APPROVAL report too", "proof group", "sources of its WITHDRAWAL reports",
           "links of its WITHDRAWAL reports"], withdrawn_rows)
write_csv("trials_missing.csv",
          ["disease", "disease id", "medicine", "medicine id", "stage for this disease on the list",
           "best stage of the forms on the list", "rule", "detail", "shown elsewhere in"],
          trial_rows)

# ----------------------------------------------------------------- report
out = []
add = out.append
T = totals
add("# Night order 1: the baseline (probe P5)\n")
add("Read-only study, 21 Nov 2026. Nothing in `moonlight/`, `web/` or `tests/` was changed. "
    "Every number below was counted by `analyse.py` from saved files. "
    "**Nothing here is labelled right or wrong.** The same numbers are in `baseline.json`, "
    "one object per disease, so a later night can diff against it.\n")
add("## What was done\n")
add(f"- Open Targets data version: **{meta['open_targets_data_version']}**. "
    f"Asked {meta['open_targets_run']['started']} to {meta['open_targets_run']['finished']} (UTC).")
add(f"- Diseases: **{len(per_disease)}** of the {len(study['diseases'])} in "
    "`fixtures/probe_p4/diseases.json` (branch `probe-direction`), read with `git show`."
    + (f" No result for: {', '.join(meta['diseases_with_no_result'])}." if missing_results else ""))
add(f"- Moonlight's code: commit `{meta['moonlight_code_commit'][:7]}` (the last change to "
    "`moonlight/` or `web/` on `main`). For each disease the probe ran the same functions, in "
    "the same order, as `moonlight/api.py`'s `_find`: `fetch_disease`, `fetch_targets` (top "
    f"{meta['top_proteins_looked_at']}), `engine.find_clues`, `fetch_approved`, `fetch_withdrawn`, "
    "`engine.fetch_neighbours`, then `api._Found` (which calls `engine.sort_into_tabs`). The "
    "cards were then checked against what `api.clues()` itself answers: same cards, same order, "
    "same links, same opposite-way lines. Diseases where they differed: "
    f"**{sum(1 for d in per_disease if d['differences_from_api_clues'])}**.")
add(f"- Requests to Open Targets: **{meta['open_targets_requests']}** "
    f"({', '.join(f'{n} {k}' for k, n in requests_by_kind.most_common())}), one at a time, at "
    "least one second apart. Different raw answers saved under `responses/`: "
    f"{meta['open_targets_different_answers_saved']}. `responses/index.jsonl` has one line per "
    "request and names the file holding its answer. Times Open Targets refused or the network "
    f"failed: **{meta['open_targets_refusals_or_network_failures']}**. Answers carrying an "
    f"error: {meta['open_targets_answers_with_errors']}.")
add(f"- Source links: **{T['links']['different_links']}** different links on "
    f"{T['links']['cards_with_a_link']} cards. Each was asked once (HEAD, then GET if HEAD was "
    f"refused; GET was needed for {T['links']['links_where_get_was_needed']}). "
    f"{meta['link_check']['requests_sent']} requests in all, counting redirect hops and tries "
    f"after \"slow down\", from {meta['link_check']['first_request']} to "
    f"{meta['link_check']['last_request']}. Every link's line is in `links.jsonl`.\n")

add("## Summary table\n")
add("One row per disease. Column names:\n")
add("- **Cards**: Approved main list / narrower-disease box / wider-group box / In trials / New clues.\n"
    "- **Links**: different source links on the disease's cards / of them dead (404, 410 or DNS "
    "failure) / cards with no link at all.\n"
    "- **Withdrawn**: main-list Approved cards with a WITHDRAWAL report: that also have an "
    "APPROVAL report / that have none.\n"
    "- **Trials**: medicines Open Targets lists in trials for the disease / shown in In trials "
    "(of them on that list) / listed and not shown, by rule: not approved elsewhere / not on a "
    "top-25 protein / other.\n"
    "- **Proof**: main-list Approved cards in probe_p3's groups A / B / C / D / E / F, then N "
    "(not on the disease's own list).\n"
    "- **Opposite**: cards opposite to the Approved medicines on a one-way protein, counted "
    "probe_p4's way: New clues / In trials.\n"
    "- **Unknown**: cards with at least one \"unknown\" direction: Approved main list / In trials "
    "/ New clues.\n")


def summary_row(name, cards, links, w, t, proof, direction, unknown):
    rule = t["not_shown_by_rule"]
    return [
        name,
        " / ".join(str(cards[tab]) for tab in TABS),
        f"{links['different_links']} / {links['dead_links']} / {links['cards_with_no_link']}",
        f"{w['main_list']['cards_with_a_withdrawal_report_and_an_approval_report']} / "
        f"{w['main_list']['cards_with_a_withdrawal_report_and_no_approval_report']}",
        f"{t['listed_in_trials']} / {t['shown_in_in_trials']} ({t['listed_in_trials_and_shown']}) / "
        f"{rule.get(NOT_APPROVED_ELSEWHERE, 0)} / {rule.get(NOT_TOP_25, 0)} / {rule.get(OTHER, 0)}",
        " / ".join(str(proof.get(g, 0)) for g in PROOF_GROUPS),
        f"{direction['New clues']['cards_opposite_on_a_one_way_protein']} / "
        f"{direction['In trials']['cards_opposite_on_a_one_way_protein']}",
        " / ".join(str(unknown.get(tab, {}).get("cards_with_an_unknown_direction", 0))
                   for tab in ("approved", "being_studied", "new_clues")),
    ]


rows = [summary_row("**ALL 50 TOGETHER**" if len(per_disease) == 50 else "**ALL TOGETHER**",
                    T["cards_by_tab"], T["links"], T["withdrawn"], T["trials"],
                    T["proof"]["main_list"], T["direction"],
                    T["direction"]["unknown_directions"])]
rows += [summary_row(d["name"], d["cards_by_tab"], d["links"], d["withdrawn"], d["trials"],
                     d["proof"]["main_list"]["by_group"], d["direction"],
                     d["direction"]["unknown_directions"]) for d in per_disease]
add(table(["Disease", "Cards (A / narrower / wider / T / N)", "Links (different / dead / cards with none)",
           "Withdrawn (with / without approval report)",
           "Trials (listed / shown (on list) / not approved elsewhere / not top-25 / other)",
           "Proof (A / B / C / D / E / F / N)", "Opposite (N / T)", "Unknown (A / T / N)"], rows))
add("In the ALL row, \"different links\" counts a link once even when two diseases show it, "
    "so it is smaller than the sum of the column. Counted, never named, as on the live site: "
    f"{T['counted_not_named'].get('not_approved', 0)} medicines not approved anywhere (or "
    f"withdrawn), {T['counted_not_named'].get('unclear_link', 0)} with an unclear link, and "
    f"{T['counted_not_named'].get('new_clues_left_out_by_hand', 0)} new clues left out by hand "
    "(`moonlight/left_out.json`), summed over the diseases.\n")

# 1 LINKS
add("## 1. LINKS\n")
add("Every card shows one link, \"Source record\" (or the words \"No source link in the data\"). "
    "That one link per card is what was asked. Approved cards in the two folded boxes are "
    "counted too.\n")
add(table(["Tab", "Cards", "Cards with no link"],
          [[TAB_WORDS[t], T["cards_by_tab"][t], T["links"]["cards_with_no_link_by_tab"].get(t, 0)]
           for t in TABS]))
outcome_words = {
    "ok": "answered 2xx (after redirects, if any)",
    "dead_404": "404", "dead_410": "410", "dead_dns_failure": "DNS failure",
    "other_status": "another status (see the table by host)",
    "redirects_to_a_host_blocked_here": "redirects to a host this session's network rules do not allow: not finished",
    "blocked_here": "the link's own host is not allowed by this session's network rules: not asked",
    "redirects_to_a_plain_http_link_not_followed": "redirects to a plain http link: not followed",
    "host_kept_saying_slow_down": "the host kept saying \"slow down\" (429 or 503): not finished",
    "not_asked_host_kept_refusing": "not asked: the host had refused many links in a row",
    "not_asked_yet": "not asked",
    "too_many_redirects": "too many redirects",
}
add(table(["What happened", "Different links"],
          [[outcome_words.get(o, o.replace("_", " ")), n]
           for o, n in sorted(outcomes_all.items(), key=lambda kv: -kv[1])]
          + [["**Total**", len(all_links)]]))
add("### Dead links by host (404, 410 or DNS failure)\n")
if dead_rows:
    add(table(["Host", "Dead links", "Cards showing one"],
              [[host, n, sum(row[3] for row in dead_rows if row[0] == host)]
               for host, n in dead_by_host.most_common()]
              + [["**Total**", len(dead_rows), sum(row[3] for row in dead_rows)]]))
    add("Every dead link (also in `dead_links.csv`):\n")
    add(table(["Host", "Status", "Link", "Cards", "Diseases"],
              [[row[0], row[1].replace("dead_", "").replace("_", " "), row[2], row[3], row[4]]
               for row in dead_rows]))
else:
    add("**No link answered 404 or 410, and no DNS failure was met.** `dead_links.csv` is empty.\n")
add("### Every host, by the last status its links gave\n")
statuses = sorted({s for c in status_table.values() for s in c}, key=str)
add(table(["Host", "Links"] + statuses,
          [[host, sum(c.values())] + [c.get(s, 0) or "" for s in statuses]
           for host, c in sorted(status_table.items(), key=lambda kv: -sum(kv[1].values()))]))
add("A number is the last HTTP status after following redirects. Words mean no final status "
    "was reached. `links_by_status.csv` has one row per link.\n")
if redirect_ends:
    add("### Links that answered 2xx only after a redirect\n")
    add(table(["Host", "Where the redirect ended", "Links"],
              [[host, end, n] for (host, end), n in
               sorted(redirect_ends.items(), key=lambda kv: (kv[0][0], -kv[1]))]))
if controls:
    add("### What these hosts answer for a link that cannot exist\n")
    add("To know what a status means, one made-up link per host was asked as well (not a card "
        "link; saved in `link_controls.jsonl`):\n")
    add(table(["Host", "Made-up link", "Answer"],
              [[c["host"], c["url"],
                (f"{c['final_status']}" if c["final_status"] else c["outcome"].replace("_", " "))
                + (f", after a redirect to {c['final_url']}" if c["hops"] and c["final_status"] else "")]
               for c in controls]))

# 2 WITHDRAWN
add("## 2. WITHDRAWN\n")
wm, wb = T["withdrawn"]["main_list"], T["withdrawn"]["boxes"]
add("A WITHDRAWAL report is one entry of `clinicalReports` whose `clinicalStage` is `WITHDRAWAL`, "
    "on the medicine's rows of the disease's own list (all its forms together). Moonlight does "
    "not use these reports: it leaves a medicine out when it carries a `Withdrawn` drug warning, "
    "which is a different field.\n")
add(table(["", "With an APPROVAL report too", "With no APPROVAL report", "Cards not on the list (reports not known)"],
          [["Approved main list", wm["cards_with_a_withdrawal_report_and_an_approval_report"],
            wm["cards_with_a_withdrawal_report_and_no_approval_report"],
            wm["cards_not_on_the_list_so_reports_not_known"]],
           ["The two folded boxes (reports read from the narrower or wider entry's list)",
            wb["cards_with_a_withdrawal_report_and_an_approval_report"],
            wb["cards_with_a_withdrawal_report_and_no_approval_report"],
            wb["cards_not_on_the_list_so_reports_not_known"]]]))
add("Every one of them (also in `withdrawn_reports.csv`, with the report links):\n")
add(table(["Disease", "Where", "Medicine", "APPROVAL report too", "Proof group", "WITHDRAWAL report from"],
          [[row[0], row[2], f"{row[3]} ({row[4]})", row[5], row[6], row[7]]
           for row in withdrawn_rows]))

# 3 TRIALS
add("## 3. TRIALS\n")
tt = T["trials"]
add("\"Listed in trials\" means: the medicine (all its forms together) is on the disease's own "
    "Open Targets list, and its strongest stage for this disease is a phase word (`PHASE_...` or "
    "`EARLY_PHASE_...`). That is the same test Moonlight's filter uses for \"being studied\".\n")
add(f"- Listed in trials, all diseases: **{tt['listed_in_trials']}**. Shown in In trials: "
    f"**{tt['shown_in_in_trials']}**, of which {tt['listed_in_trials_and_shown']} are on that list.")
add(f"- Listed and not shown: **{tt['listed_in_trials_and_not_shown']}**.\n")
add(table(["Rule that left it out", "Medicines"],
          [[k, v] for k, v in tt["not_shown_by_rule_in_detail"].items()]
          + [["**Total**", tt["listed_in_trials_and_not_shown"]]]))
add("How a rule was chosen, in this order. (1) *Not approved elsewhere*: the stage word says the "
    "medicine is not approved for any disease. For a medicine on a top-25 protein that is "
    "Moonlight's own finding. For one that is not, only the forms on the disease's list could be "
    "looked at. (2) *Not on a top-25 protein*: approved somewhere, but it acts on none of the 25 "
    "proteins Moonlight looks at, so Moonlight never meets it. (3) *Other*: everything else, with "
    "the detail spelled out. Every medicine, with its rule, is in `trials_missing.csv`.\n")
if tt["shown_in_in_trials_but_not_listed_in_trials"]:
    add("In trials cards that are **not** \"listed in trials\" on the disease's own list (Moonlight "
        "reads the stage from the medicine's own record on the protein route): "
        + ", ".join(f"{n} ({k})" for k, n in tt["shown_in_in_trials_but_not_listed_in_trials"].items())
        + ".\n")
add("Every stage word on the 50 lists (medicines, strongest stage for the disease): "
    + ", ".join(f"`{k}` {v}" for k, v in sorted(tt["list_by_stage_word"].items(), key=lambda kv: -kv[1]))
    + ".\n")
add(table(["Disease", "On the list", "Listed in trials", "Shown in In trials", "Shown and listed",
           "Not approved elsewhere", "Not on a top-25 protein", "Other"],
          [[d["name"], d["trials"]["medicines_on_the_disease_list"], d["trials"]["listed_in_trials"],
            d["trials"]["shown_in_in_trials"], d["trials"]["listed_in_trials_and_shown"]]
           + [d["trials"]["not_shown_by_rule"][reason] for reason in REASONS]
           for d in per_disease]))

# 4 PROOF
add("## 4. PROOF\n")
add("probe_p3's groups, from the APPROVAL reports on the medicine's rows of the list:\n")
add("\n".join(f"- **{g}**: {PROOF_WORDS[g]}" for g in PROOF_GROUPS) + "\n")
pm, pb = T["proof"]["main_list"], T["proof"]["boxes"]
add(table(["Group", "Approved main list", "Share", "The two folded boxes", "Share"],
          [[g, pm.get(g, 0), f"{100 * pm.get(g, 0) / max(1, sum(pm.values())):.1f}%",
            pb.get(g, 0), f"{100 * pb.get(g, 0) / max(1, sum(pb.values())):.1f}%"]
           for g in PROOF_GROUPS]
          + [["Total", sum(pm.values()), "100.0%", sum(pb.values()), "100.0%"]]))
lines_ = T["proof"]["moonlight_own_lines"]
add(f"Moonlight's own lines on Approved cards (main list and boxes): the Japan line on "
    f"**{lines_.get('japan_line', 0)}** cards, the \"no regulator record\" line on "
    f"**{lines_.get('no_regulator_line', 0)}**, a red warning on **{lines_.get('red_warning', 0)}**. "
    "Moonlight counts PMDA as a regulator; probe_p3's group A does not, so the two counts are "
    "not the same thing.\n")
add(table(["Disease", "Main list cards", "A", "B", "C", "D", "E", "F", "N", "Box cards", "Box cards outside A"],
          [[d["name"], d["proof"]["main_list"]["cards"]]
           + [d["proof"]["main_list"]["by_group"][g] for g in PROOF_GROUPS]
           + [d["proof"]["boxes"]["cards"],
              d["proof"]["boxes"]["cards"] - d["proof"]["boxes"]["by_group"]["A"]]
           for d in per_disease]))

# 5 DIRECTION
add("## 5. DIRECTION\n")
dd = T["direction"]
add("Counted probe_p4's way. A protein is **one-way** for a disease if every main-list Approved "
    "medicine with an up or down direction on it points the same way, **both-ways** if they "
    "disagree. A card is one medicine.\n")
add(table(["", "New clues", "In trials"],
          [[words, dd["New clues"][key], dd["In trials"][key]] for words, key in (
              ("cards in total", "cards"),
              ("cards pointing OPPOSITE to the Approved medicines on a one-way protein",
               "cards_opposite_on_a_one_way_protein"),
              ("cards pointing the SAME way on a one-way protein", "cards_same_on_a_one_way_protein"),
              ("cards with mixed or unknown direction on a one-way protein",
               "cards_mixed_or_unknown_on_a_one_way_protein"),
              ("cards sitting on a both-ways protein", "cards_on_a_both_ways_protein"),
              ("cards carrying the live site's line \"Opposite way to the approved medicines for this disease.\"",
               "cards_carrying_the_opposite_way_line_on_the_live_site"))]))
add(f"- Diseases with at least one opposite card: **{dd['diseases_with_an_opposite_card']} of "
    f"{len(per_disease)}**. One-way proteins (disease by disease): {dd['one_way_proteins']}. "
    f"Both-ways proteins: {dd['both_ways_proteins']}.")
add("- The live site's line (ticket 3.7) leaves the red-warning Approved cards out before "
    "deciding one-way. probe_p4 did not. Where the last row differs from the second row, that "
    "is why.\n")
add("### Unknown and mixed directions on cards\n")
ud = dd["unknown_directions"]
add(table(["Tab", "Cards", "No protein shown", "At least one unknown", "Every direction unknown",
           "At least one mixed", "Card-protein pairs", "Pairs unknown", "Pairs mixed"],
          [[TAB_WORDS[t]] + [ud[t][k] for k in (
              "cards", "cards_with_no_protein_shown", "cards_with_an_unknown_direction",
              "cards_where_every_direction_is_unknown", "cards_with_a_mixed_direction",
              "card_protein_pairs", "card_protein_pairs_unknown", "card_protein_pairs_mixed")]
           for t in TABS]))
add("The action words behind every unknown or mixed pair on a card:\n")
add(table(["Direction", "Action words from Open Targets", "Card-protein pairs"],
          [[w["direction"], w["action_words"], w["card_protein_pairs"]]
           for w in dd["action_words_behind_unknown_and_mixed"]]))
add(table(["Disease", "Approved cards (with a path)", "One-way proteins", "Both-ways proteins",
           "NC total", "NC opp", "NC same", "NC both", "NC line", "IT total", "IT opp", "IT same",
           "IT both", "IT line"],
          [[d["name"], f"{d['direction']['approved_cards']} ({d['direction']['approved_cards_with_a_path']})",
            d["direction"]["one_way_proteins"], d["direction"]["both_ways_proteins"]]
           + [d["direction"][label][key] for label in ("New clues", "In trials") for key in (
               "cards", "cards_opposite_on_a_one_way_protein", "cards_same_on_a_one_way_protein",
               "cards_on_a_both_ways_protein", "cards_carrying_the_opposite_way_line_on_the_live_site")]
           for d in per_disease]))
add("NC = New clues, IT = In trials, opp = opposite on a one-way protein, both = on a both-ways "
    "protein, line = carries the live site's opposite-way line.\n")

# compare
add("## Tonight next to the two earlier studies\n")
p4 = git_json("origin/probe-direction:fixtures/probe_p4/analysis.json")
if p4:
    old = {row["disease_id"]: row for row in p4["per_disease"]}
    both = [d for d in per_disease if d["id"] in old]
    changed = []
    for d in both:
        o, n = old[d["id"]], d["direction"]
        pairs = [("Approved cards", o["approved_cards"], n["approved_cards"]),
                 ("one-way proteins", o["one_way_proteins"], n["one_way_proteins"]),
                 ("both-ways proteins", o["both_ways_proteins"], n["both_ways_proteins"])]
        for label in ("New clues", "In trials"):
            for key, word in (("cards", "cards"), ("cards_opposite_on_a_one_way_protein", "opposite"),
                              ("cards_same_on_a_one_way_protein", "same"),
                              ("cards_on_a_both_ways_protein", "on both-ways")):
                pairs.append((f"{label} {word}", o[label][key], n[label][key]))
        for what, before, after in pairs:
            if before != after:
                changed.append([d["name"], what, before, after])
    add(f"**probe_p4 (18 Nov, data {p4['data_version']}).** Same 50 diseases, same way of "
        "counting.\n")
    add(table(["", "probe_p4", "tonight"],
              [["Approved main-list cards", sum(o["approved_cards"] for o in old.values()),
                T["cards_by_tab"]["approved"]]]
              + [[f"{label}: {word}", p4["totals"][label][key], dd[label][key]]
                 for label in ("New clues", "In trials")
                 for key, word in (("cards", "cards"),
                                   ("cards_opposite_on_a_one_way_protein", "opposite cards"),
                                   ("cards_same_on_a_one_way_protein", "same-way cards"),
                                   ("cards_mixed_or_unknown_on_a_one_way_protein", "mixed or unknown on a one-way protein"),
                                   ("cards_on_a_both_ways_protein", "on a both-ways protein"))]))
    if changed:
        add("Every per-disease number that is not the same as in probe_p4:\n")
        add(table(["Disease", "What", "probe_p4", "tonight"], changed))
    else:
        add("Every per-disease number that both studies counted is the same tonight.\n")
else:
    add("probe_p4's numbers could not be read (branch `probe-direction` not found here).\n")
p3 = git_json("origin/probe-approval-proof:fixtures/probe_p3/items.json")
if p3:
    ids = {d["id"] for d in per_disease}
    then = collections.Counter(item["group"] for item in p3["approved_items"]
                               if item["disease_id"] in ids and item["shown_today"])
    covered = {item["disease_id"] for item in p3["approved_items"]} & ids
    now_ = T["proof"]["probe_p3_base_own_list_only"]
    add(f"**probe_p3 (17 Nov).** probe_p3 read only each disease's own list, so for this "
        "comparison tonight's answers were counted that way too (not by card). "
        f"{len(covered)} of tonight's diseases are in probe_p3.\n")
    add(table(["Group", "probe_p3, these diseases", "tonight, own list only"],
              [[g, then.get(g, 0), now_.get(g, 0)] for g in "ABCDEF"]
              + [["Total", sum(then.values()), sum(now_.values())]]))
else:
    add("probe_p3's numbers could not be read (branch `probe-approval-proof` not found here).\n")

notes = HERE / "NOT_VERIFIED.md"
add(notes.read_text(encoding="utf-8") if notes.exists() else "## Things I did not verify\n\n(to be written)\n")
(HERE / "REPORT.md").write_text("\n".join(out), encoding="utf-8")
print("diseases:", len(per_disease), "links:", len(all_links), "asked:", T["links"]["links_asked"],
      "dead:", len(dead_rows), "outcomes:", dict(outcomes_all))
