"""Probe P7: recount everything from the saved answers. No network.

Reads inputs/nct_links.json (the NCT links copied out of P5 and P6),
responses/index.jsonl and the saved answers under responses/. Writes:

  counts.json          every number in REPORT.md
  a_records.csv        part A, one row per different NCT number
  a_by_disease.csv     part A, one row per disease
  b_known.csv          part B, one row per trial found
  c_counts.csv         part C, one row per disease
  tables.md            the same numbers as tables, pasted into REPORT.md

    python3 fixtures/probe_p7/analyse.py
"""

import collections
import csv
import json
import pathlib
import re

HERE = pathlib.Path(__file__).resolve().parent
RESP = HERE / "responses"


def slug(text):
    return re.sub(r"[^A-Za-z0-9]+", "_", text).strip("_")


def read(row):
    return json.loads((RESP / row["file"]).read_bytes())


def record(study):
    """The five things the order asks for, from one study as the register wrote it."""
    p = study["protocolSection"]
    st = p.get("statusModule", {})
    pc = st.get("primaryCompletionDateStruct", {})
    c = st.get("completionDateStruct", {})
    return {
        "nct_in_answer": p["identificationModule"]["nctId"],
        "status": st.get("overallStatus"),
        "status_verified": st.get("statusVerifiedDate"),
        "last_update_posted": st.get("lastUpdatePostDateStruct", {}).get("date"),
        "primary_completion_date": pc.get("date"),
        "primary_completion_type": pc.get("type"),
        "completion_date": c.get("date"),
        "completion_type": c.get("type"),
        "study_type": p.get("designModule", {}).get("studyType"),
        "phases": p.get("designModule", {}).get("phases", []),
        "conditions": p.get("conditionsModule", {}).get("conditions", []),
        "interventions": [{"type": i.get("type"), "name": i.get("name")}
                          for i in p.get("armsInterventionsModule", {}).get("interventions", [])],
    }


def main():
    inp = json.loads((HERE / "inputs" / "nct_links.json").read_text())
    rows = [json.loads(l) for l in (RESP / "index.jsonl").read_text().splitlines()]
    final = {(r["kind"], r["name"]): r for r in rows if r.get("final")}
    out = {}

    # ---- what was asked ------------------------------------------------
    out["requests"] = {
        "lines_in_index": len(rows),
        "by_kind": dict(collections.Counter(r["kind"] for r in rows)),
        "by_status": {str(k): v for k, v in collections.Counter(r.get("status") for r in rows).items()},
        "tries_after_the_first": sum(1 for r in rows if r["try"] > 1),
        "first_at": min(r["at"] for r in rows), "last_at": max(r["at"] for r in rows),
        "register_version": read(final[("control", "version")]),
    }
    out["controls"] = {
        "made_up_number_alone_status": final[("control", "made_up_NCT99999999")]["status"],
        "made_up_number_in_a_list_of_two_came_back":
            [s["protocolSection"]["identificationModule"]["nctId"]
             for s in read(final[("control", "made_up_in_a_list")])["studies"]],
    }

    # ---- part A --------------------------------------------------------
    diseases = inp["diseases"]
    card_ncts = {c["nct"] for d in diseases for c in d["card_links"]}
    own_ncts = {n for d in diseases for n in d["own_list_ncts"]}
    every = card_ncts | own_ncts

    answer = {}  # nct -> {"how", "http", "rec"}
    for n in card_ncts:
        r = final.get(("card", n))
        if r is None:
            answer[n] = {"how": "not asked", "http": None, "rec": None}
        else:
            answer[n] = {"how": "alone", "http": r["status"],
                         "rec": record(read(r)) if r["status"] == 200 else None}
    batch_asked = set()
    for (kind, name), r in final.items():
        if kind != "own_batch":
            continue
        ids = r["params"]["filter.ids"].split(",")
        batch_asked |= set(ids)
        if r["status"] != 200:
            continue
        for s in read(r)["studies"]:
            rec = record(s)
            answer[rec["nct_in_answer"]] = {"how": "in a list of 100", "http": 200, "rec": rec}
    for (kind, name), r in final.items():
        if kind == "own_single":
            answer[name] = {"how": "in a list of 100, then alone", "http": r["status"],
                            "rec": record(read(r)) if r["status"] == 200 else None}
    for n in every:
        answer.setdefault(n, {"how": "not asked", "http": None, "rec": None})

    def outcome(n):
        a = answer[n]
        if a["rec"]:
            return a["rec"]["status"]
        if a["http"] == 404:
            return "NOT KNOWN TO THE REGISTER (404)"
        if a["http"] is None:
            return "NOT ASKED OR NO ANSWER"
        return f"HTTP {a['http']}"

    def by_status(ncts):
        return dict(sorted(collections.Counter(outcome(n) for n in ncts).items(),
                           key=lambda kv: (-kv[1], kv[0])))

    card_links = [(d, c) for d in diseases for c in d["card_links"]]
    a = {
        "diseases": len(diseases),
        "cards_in_all": sum(d["cards_in_all"] for d in diseases),
        "cards_whose_link_is_an_nct_link": len(card_links),
        "different_nct_on_cards": len(card_ncts),
        "different_nct_on_own_lists": len(own_ncts),
        "different_nct_on_both": len(card_ncts & own_ncts),
        "different_nct_on_cards_only": len(card_ncts - own_ncts),
        "different_nct_on_either": len(every),
        "asked_alone_for_cards": sum(1 for k in final if k[0] == "card"),
        "lists_of_100_asked": sum(1 for k in final if k[0] == "own_batch"),
        "numbers_asked_in_lists": len(batch_asked),
        "numbers_a_list_did_not_return_then_asked_alone": sum(1 for k in final if k[0] == "own_single"),
        "answer_number_differs_from_asked_number":
            sorted(n for n in every if answer[n]["rec"] and answer[n]["rec"]["nct_in_answer"] != n),
        "status_of_different_nct_on_cards": by_status(card_ncts),
        "status_of_different_nct_on_own_lists": by_status(own_ncts),
        "status_of_different_nct_on_either": by_status(every),
        "status_of_card_links_counting_every_card": by_status([c["nct"] for _, c in card_links]),
        "status_of_card_links_by_tab": {
            tab: by_status([c["nct"] for _, c in card_links if c["tab"] == tab])
            for tab in sorted({c["tab"] for _, c in card_links})},
        "not_known_to_the_register": {
            "on_cards": sorted(n for n in card_ncts if answer[n]["http"] == 404),
            "on_own_lists": sorted(n for n in own_ncts if answer[n]["http"] == 404),
            "on_either": sorted(n for n in every if answer[n]["http"] == 404),
        },
        "no_record_for_another_reason": sorted(
            n for n in every if not answer[n]["rec"] and answer[n]["http"] != 404),
    }

    def blanks(ncts):
        recs = [answer[n]["rec"] for n in ncts if answer[n]["rec"]]
        return {
            "records": len(recs),
            "no_primary_completion_date": sum(1 for r in recs if not r["primary_completion_date"]),
            "no_completion_date": sum(1 for r in recs if not r["completion_date"]),
            "no_conditions": sum(1 for r in recs if not r["conditions"]),
            "no_interventions": sum(1 for r in recs if not r["interventions"]),
            "primary_completion_type": dict(collections.Counter(
                str(r["primary_completion_type"]) for r in recs)),
            "completion_type": dict(collections.Counter(str(r["completion_type"]) for r in recs)),
            "study_type": dict(collections.Counter(str(r["study_type"]) for r in recs)),
        }
    a["fields_on_cards"] = blanks(card_ncts)
    a["fields_on_either"] = blanks(every)
    out["A"] = a

    with (HERE / "a_records.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["nct", "on a card", "on an own list", "how asked", "http", "status",
                    "primary completion date", "type", "completion date", "type",
                    "study type", "phases", "conditions", "interventions"])
        for n in sorted(every):
            r = answer[n]["rec"] or {}
            w.writerow([n, "yes" if n in card_ncts else "no", "yes" if n in own_ncts else "no",
                        answer[n]["how"], answer[n]["http"], outcome(n),
                        r.get("primary_completion_date") or "", r.get("primary_completion_type") or "",
                        r.get("completion_date") or "", r.get("completion_type") or "",
                        r.get("study_type") or "", " | ".join(r.get("phases", [])),
                        " | ".join(r.get("conditions", [])),
                        " | ".join(f"{i['type']}: {i['name']}" for i in r.get("interventions", []))])

    statuses = sorted({outcome(n) for n in every})
    with (HERE / "a_by_disease.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["probe", "id", "disease", "cards", "cards with an NCT link",
                    "different NCT on cards", "different NCT on own list"]
                   + [f"cards: {s}" for s in statuses] + [f"own list: {s}" for s in statuses])
        per = []
        for d in diseases:
            cn = {c["nct"] for c in d["card_links"]}
            cs = collections.Counter(outcome(n) for n in cn)
            os_ = collections.Counter(outcome(n) for n in d["own_list_ncts"])
            w.writerow([d["probe"], d["id"], d["name"], d["cards_in_all"], len(d["card_links"]),
                        len(cn), len(d["own_list_ncts"])]
                       + [cs.get(s, 0) for s in statuses] + [os_.get(s, 0) for s in statuses])
            per.append({"probe": d["probe"], "id": d["id"], "name": d["name"],
                        "cards_with_an_nct_link": len(d["card_links"]),
                        "different_nct_on_cards": len(cn),
                        "different_nct_on_own_list": len(d["own_list_ncts"]),
                        "cards": dict(cs), "own_list": dict(os_)})
        a["by_disease"] = per

    # ---- part B --------------------------------------------------------
    own_by_id = {d["id"]: set(d["own_list_ncts"]) for d in diseases}
    kq = json.loads((HERE / "known_questions.json").read_text())
    b = {"searches": []}
    if ("known", "NCT05965700_fields") in final:
        b["NCT05965700"] = record(read(final[("known", "NCT05965700_fields")]))
        b["NCT05965700"]["on_a_card_in_P5_or_P6"] = "NCT05965700" in card_ncts
        b["NCT05965700"]["on_an_own_list_in_P5_or_P6"] = "NCT05965700" in own_ncts

    def search(name):
        got, total, pages = [], None, 0
        for (kind, nm), r in sorted(final.items()):
            if kind == "known" and re.fullmatch(re.escape(name) + r"\.p\d{3}", nm):
                pages += 1
                if r["status"] == 200:
                    j = read(r)
                    total = j.get("totalCount", total)
                    got += [record(s) for s in j["studies"]]
        return got, total, pages

    with (HERE / "b_known.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["searched intervention words", "nct", "status", "primary completion date",
                    "completion date", "study type", "phases", "conditions as written",
                    "interventions as written", "also found with the condition words",
                    "condition words", "on the Open Targets list saved for that disease",
                    "on any P5/P6 card", "on any P5/P6 own list"])
        for q in kq["searches"]:
            base = "intr_" + slug(q["intervention"])
            alone, total, pages = search(base)
            both, total2, pages2 = search(base + "__cond_" + slug(q["condition"]))
            both_ids = {r["nct_in_answer"] for r in both}
            saved = q["open_targets_list_saved"]
            trials = []
            for r in sorted(alone, key=lambda r: r["nct_in_answer"]):
                n = r["nct_in_answer"]
                on_list = ("no list saved" if not saved else
                           "yes" if n in own_by_id[saved] else "no")
                trials.append(dict(r, found_with_condition_words=n in both_ids,
                                   on_saved_open_targets_list=on_list,
                                   on_any_card=n in card_ncts, on_any_own_list=n in own_ncts))
                w.writerow([q["intervention"], n, r["status"], r["primary_completion_date"] or "",
                            r["completion_date"] or "", r["study_type"] or "",
                            " | ".join(r["phases"]), " | ".join(r["conditions"]),
                            " | ".join(f"{i['type']}: {i['name']}" for i in r["interventions"]),
                            "yes" if n in both_ids else "no", q["condition"], on_list,
                            "yes" if n in card_ncts else "no", "yes" if n in own_ncts else "no"])
            b["searches"].append({
                "intervention_words": q["intervention"], "condition_words": q["condition"],
                "open_targets_list_saved": saved,
                "register_total_intervention_words_alone": total, "trials_saved": len(alone),
                "pages": pages,
                "register_total_with_condition_words": total2, "trials_saved_with_condition_words": len(both),
                "of_those_on_the_saved_open_targets_list":
                    None if not saved else sum(1 for t in trials if t["found_with_condition_words"]
                                               and t["on_saved_open_targets_list"] == "yes"),
                "trials": trials})
    out["B"] = b

    # ---- part C --------------------------------------------------------
    ten = json.loads((HERE / "ten_diseases.json").read_text())
    names = {d["id"]: d["name"] for d in diseases}
    c_rows = []
    for d in ten["diseases"]:
        got, total, pages, types = set(), None, 0, collections.Counter()
        for (kind, nm), r in sorted(final.items()):
            if kind == "count" and re.fullmatch(re.escape(slug(d["id"])) + r"\.p\d{3}", nm):
                pages += 1
                if r["status"] == 200:
                    j = read(r)
                    total = j.get("totalCount", total)
                    for s in j["studies"]:
                        got.add(s["protocolSection"]["identificationModule"]["nctId"])
                        types[s["protocolSection"].get("designModule", {}).get("studyType")] += 1
        own = own_by_id[d["id"]]
        c_rows.append({
            "probe": d["probe"], "id": d["id"], "open_targets_name": names[d["id"]],
            "search_words": d["search_words"], "pages": pages,
            "register_total_count": total, "different_nct_saved": len(got),
            "study_types_in_the_answers": dict(types),
            "nct_on_open_targets_own_list": len(own),
            "registered_and_on_the_list": len(got & own),
            "registered_and_absent_from_the_list": len(got - own),
            "on_the_list_and_not_in_this_search": len(own - got),
        })
    with (HERE / "c_counts.csv").open("w", newline="") as f:
        if c_rows:
            w = csv.DictWriter(f, fieldnames=list(c_rows[0]))
            w.writeheader()
            for r in c_rows:
                w.writerow(r)
    out["C"] = {"diseases": c_rows,
                "all_ten": {k: sum(r[k] or 0 for r in c_rows) for k in (
                    "register_total_count", "different_nct_saved", "nct_on_open_targets_own_list",
                    "registered_and_on_the_list", "registered_and_absent_from_the_list",
                    "on_the_list_and_not_in_this_search")}}

    (HERE / "counts.json").write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")

    # ---- tables --------------------------------------------------------
    t = []

    def table(head, lines):
        t.append("| " + " | ".join(head) + " |")
        t.append("|" + "---|" * len(head))
        for l in lines:
            t.append("| " + " | ".join(str(x) for x in l) + " |")
        t.append("")

    keys = list(a["status_of_different_nct_on_either"])
    t.append("### A1. Different NCT numbers, by the register's status word\n")
    table(["Status", "On cards", "On own lists", "On either"],
          [[k, a["status_of_different_nct_on_cards"].get(k, 0),
            a["status_of_different_nct_on_own_lists"].get(k, 0),
            a["status_of_different_nct_on_either"][k]] for k in keys]
          + [["**Total**", len(card_ncts), len(own_ncts), len(every)]])
    tabs = list(a["status_of_card_links_by_tab"])
    t.append("### A2. Cards with an NCT link, counting every card, by tab\n")
    ck = list(a["status_of_card_links_counting_every_card"])
    table(["Status"] + tabs + ["All tabs"],
          [[k] + [a["status_of_card_links_by_tab"][tab].get(k, 0) for tab in tabs]
           + [a["status_of_card_links_counting_every_card"][k]] for k in ck]
          + [["**Total**"] + [sum(a["status_of_card_links_by_tab"][tab].values()) for tab in tabs]
             + [len(card_links)]])
    t.append("### A3. By disease\n")
    short = [s for s in keys]
    table(["Disease", "Cards with an NCT link", "Different NCT on cards", "Different NCT on own list"]
          + [f"own: {s}" for s in short],
          [[p["name"], p["cards_with_an_nct_link"], p["different_nct_on_cards"],
            p["different_nct_on_own_list"]] + [p["own_list"].get(s, 0) for s in short]
           for p in a["by_disease"]])
    t.append("### B. Known answers\n")
    for s in b["searches"]:
        t.append(f"**{s['intervention_words']}**: {s['register_total_intervention_words_alone']} trials "
                 f"by intervention words alone; {s['register_total_with_condition_words']} together with "
                 f"the condition words \"{s['condition_words']}\".\n")
        table(["NCT", "Status", "Primary completion", "Completion", "Conditions as written",
               "Interventions as written", "Found with condition words",
               "On the saved Open Targets list"],
              [[x["nct_in_answer"], x["status"], x["primary_completion_date"] or "",
                x["completion_date"] or "", "; ".join(x["conditions"]),
                "; ".join(f"{i['type']}: {i['name']}" for i in x["interventions"]),
                "yes" if x["found_with_condition_words"] else "no",
                x["on_saved_open_targets_list"]] for x in s["trials"]])
    t.append("### C. Ten diseases\n")
    table(["Disease (search words)", "Register's count of interventional trials",
           "NCT numbers saved", "NCT numbers on Open Targets' own list",
           "Registered and on the list", "Registered and absent from the list",
           "On the list and not in this search"],
          [[r["search_words"], r["register_total_count"], r["different_nct_saved"],
            r["nct_on_open_targets_own_list"], r["registered_and_on_the_list"],
            r["registered_and_absent_from_the_list"], r["on_the_list_and_not_in_this_search"]]
           for r in c_rows])
    (HERE / "tables.md").write_text("\n".join(t) + "\n")
    print(json.dumps({k: v for k, v in a.items() if k not in ("by_disease",)}, indent=1)[:6000])
    print(json.dumps(out["requests"], indent=1))


if __name__ == "__main__":
    main()
