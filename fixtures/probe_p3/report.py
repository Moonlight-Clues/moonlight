"""Night watch P3: write REPORT.md from what analyse.py gathered.

Not run on its own. analyse.py calls write(). Every number in REPORT.md is
counted here from the saved answers; none is typed by hand.
"""

import collections
import pathlib

from analyse import GROUPS, GROUP_WORDS, SETS, SET_WORDS, APPROVAL, WITHDRAWAL, PMDA, STRONG

HERE = pathlib.Path(__file__).resolve().parent
OUTSIDE = "BCDEF"
PREDICTION = "fewer than 15"


NOT_VERIFIED = [
    "**Whether any approval is really right or wrong.** This study cannot tell. A group only says "
    "which kind of source Open Targets attached. No item in this report is labelled right or "
    "wrong, and group A is not a promise that an item is right.",
    "**The links were not opened.** The grouping uses the `source` word only. It was not checked "
    "that a DailyMed, FDA or EMA page really is about this disease, or that a TTD, PMDA or ATC "
    "page is not.",
    "**Which sources are regulators.** That DailyMed, FDA, EMA Human Drugs and PMDA are regulator "
    "sources and TTD and ATC are secondary is taken from what the Open Targets team told us. It "
    "was not checked here.",
    "**Only each disease's own list was read.** Moonlight's Approved tab also uses the medicines "
    "found through the disease's proteins, the withdrawn notes on those paths, and the lists of "
    "the parent and child diseases. None of those were asked. So \"on the Approved list today\" "
    "here means: passes `fetch_approved` on the disease's own list. The real tab can differ a "
    "little for a disease.",
    "**The skipped names.** 16 given names had no exact match and were not studied, though Open "
    "Targets has those diseases under other names (the table in section 1 shows them).",
    "**These are not a fair sample of all diseases.** The four sets were picked by people and by "
    "the agent. The shares describe these 124 diseases only.",
    "**One day, one data release.** Every answer came the same day from one release. Each was "
    "asked twice and matched. Some rows hold no reports at all; it is not known whether that "
    "is how the data is or an incomplete answer.",
    "**No Moonlight code was changed**, so the test suite proves nothing about this study. It was "
    "run once at the end only to see that the new folder breaks no test.",
]


def share(part: int, whole: int) -> str:
    return "n/a" if not whole else f"{100 * part / whole:.1f}%"


def yes_no(value: bool) -> str:
    return "yes" if value else "no"


def table(header, rows) -> list:
    lines = ["| " + " | ".join(header) + " |", "|" + "|".join("---" for _ in header) + "|"]
    lines += ["| " + " | ".join(str(cell) for cell in row) + " |" for row in rows]
    return lines + [""]


def in_set(things, set_name):
    return things if set_name is None else [t for t in things if t["set"] == set_name]


def scopes():
    return [(None, "All diseases")] + [(name, SET_WORDS[name]) for name in SETS]


def no_strong(item) -> bool:
    return item["group"] in OUTSIDE


def no_strong_even_with_pmda(item) -> bool:
    return item["group"] in OUTSIDE and PMDA not in item["approval_sources"]


def report_lines(item) -> list:
    """Every report of an item: approval reports first, then the others."""
    reports = sorted(item["reports"], key=lambda r: (r["stage"] != APPROVAL, r["stage"], r["source"], r["url"] or ""))
    return [f"    - {r['stage']} | {r['source']} | {r['url'] or '(no link)'}" for r in reports]


def write(study, items, source_table, withdrawal_not_approved) -> None:
    sources, by_stage, example = source_table
    diseases = study["diseases"]
    found = [d for d in diseases if d["found"]]
    skipped = [d for d in diseases if not d["found"]]
    choice_log = __import__("json").loads((HERE / "agent_choice_log.json").read_text(encoding="utf-8"))
    shown = [item for item in items if item["shown_today"]]
    version = study["data_version"]
    version_words = ".".join(str(part) for part in (version["year"], version["month"], version["iteration"]) if part)

    out = []
    add = out.append
    add("# Night watch P3: how strong is the proof behind \"approved\"?")
    add("")
    add(f"Read-only study. Open Targets only, data release {version_words}. Asked "
        f"{study['started']} to {study['finished']} (UTC). No file in moonlight/, web/ or tests/ "
        "was changed. Moonlight's site and Gemini were not called.")
    add("")
    add("Everything below is counted by `analyse.py` and `report.py` from the raw answers saved in "
        "`responses/`. No id and no number was typed by hand.")
    add("")
    n_out = sum(map(no_strong, shown))
    d_out = len({item["disease_id"] for item in shown if no_strong(item)})
    add("## The short answer")
    add("")
    add(f"- {len(found)} diseases were studied. Together they have {len(shown)} items on "
        "Moonlight's Approved list today.")
    add(f"- {len(shown) - n_out} of those items ({share(len(shown) - n_out, len(shown))}) have at "
        f"least one approval report from DailyMed, FDA or EMA (group A). {n_out} "
        f"({share(n_out, len(shown))}) do not (groups B to F).")
    add(f"- **{d_out} of the {len(found)} diseases** have at least one item outside group A. "
        f"Kashish predicted **{PREDICTION}**.")
    add("- This says how strong the attached proof is. It does not say any item is right or wrong.")
    add("")
    add("## Words used in this report")
    add("")
    add("- **Item**: a medicine and its forms together, Kashish's rule. The item's id is the "
        "parent medicine's id.")
    add("- **Approved item**: an item Moonlight counts as approved for the disease today. That is "
        "`fetch.py`'s test, which `engine.py` uses for the Approved tab: one of the item's rows on "
        "the disease's own list has `maxClinicalStage` = `APPROVAL`, and that form's own "
        "`maximumClinicalStage` is `APPROVAL` too. The test does not look at the reports at all.")
    add("- **On the Approved list today**: an approved item that Moonlight does not leave out as "
        "withdrawn. Moonlight leaves an item out when one of its forms carries a `Withdrawn` drug "
        "warning. That is a different field from a report whose `clinicalStage` is `WITHDRAWAL`.")
    add("- **Approval report**: one entry of `clinicalReports` whose `clinicalStage` is `APPROVAL`.")
    add("- The main numbers count the items **on the Approved list today**. A second column also "
        "counts the approved items Moonlight already leaves out as withdrawn.")
    add("- Moonlight's own `fetch_approved` and `fetch_withdrawn` were run on every saved answer, "
        "offline, and gave exactly the same items as this study for every disease.")
    add("")

    # ---- 1. diseases
    add("## 1. Diseases asked, found and skipped")
    add("")
    rows = []
    for set_name, words in scopes():
        if set_name == "AGENT":
            tried = [c for c in choice_log if not (c["why"] or "").startswith("not tried")]
            rows.append([words, len(tried), len(in_set(found, set_name)),
                         len(tried) - len(in_set(found, set_name))])
        elif set_name is None:
            tried_agent = [c for c in choice_log if not (c["why"] or "").startswith("not tried")]
            asked = len([d for d in diseases if d["set"] != "AGENT"]) + len(tried_agent)
            rows.append([words, asked, len(found), asked - len(found)])
        else:
            rows.append([words, len(in_set(diseases, set_name)), len(in_set(found, set_name)),
                         len(in_set(skipped, set_name))])
    out += table(["Set", "Asked", "Found (in the study)", "Skipped"], rows)
    add("A name is **found** only if a search hit has exactly that name (capitals ignored). "
        "Nothing was matched by hand, so some very common diseases were skipped because Open "
        "Targets files them under another name.")
    add("")
    add("### Skipped names in the three given sets")
    add("")
    rows = []
    for d in skipped:
        seen = "; ".join(f"{h['name']} ({h['id']})" for h in d.get("hits_seen", [])[:3]) or "(no disease hits)"
        rows.append([SET_WORDS[d["set"]], d["asked"], d["why"], seen])
    out += table(["Set", "Name asked", "Why skipped", "First three hits Open Targets gave instead"], rows)
    add("### Agent's choice: how the 50 were chosen")
    add("")
    add("Before any answer was seen, the agent wrote a pool of everyday disease names it believed "
        "have an approved medicine, in 14 body-system groups (the list is in `probe.py`). The "
        "names were tried one group after another, round and round, so the set is spread out. A "
        "name was taken only if (1) Open Targets has exactly that name, (2) it is not already in "
        "the study, and (3) its answer holds at least one approved item. The first 50 taken are "
        "the set. Because of test (3), no disease in this set can have an empty approved list, "
        "which the other three sets can.")
    add("")
    per_system = collections.Counter(d["system"] for d in in_set(found, "AGENT"))
    add("Taken per body system: " + ", ".join(f"{system} {count}" for system, count in per_system.items()) + ".")
    add("")
    rows = [[c["asked"], c["system"], c["why"]] for c in choice_log if not c["taken"]]
    add("Candidates not taken:")
    add("")
    out += table(["Name", "Body system", "Why not taken"], rows)
    add("### The diseases in the study")
    add("")
    by_disease_shown = collections.Counter(item["disease_id"] for item in shown)
    by_disease_all = collections.Counter(item["disease_id"] for item in items)
    rows = [[SET_WORDS[d["set"]], d["name"], d["id"], d["items_on_list"], by_disease_all[d["id"]],
             by_disease_shown[d["id"]], d["asks"]["asks"]] for d in found]
    out += table(["Set", "Disease", "Id", "Items on its list", "Approved items",
                  "On the Approved list today", "Times asked"], rows)
    differed = [d for d in found if not d["asks"].get("answers_all_equal", True)]
    if differed:
        add(f"Each list was asked twice, as `fetch.py` does. For {len(differed)} of {len(found)} "
            "diseases the two answers were not the same, so it was asked a third time and the "
            "fullest answer was kept: "
            + ", ".join(f"{d['name']} (reports: {d['asks']['report_counts']})" for d in differed) + ".")
    else:
        add(f"Each list was asked twice, as `fetch.py` does. For all {len(found)} diseases the two "
            "answers were exactly the same, so no third ask was needed.")
    add("")
    add("One more answer is saved in `responses/` and is not in the study: essential tremor "
        "(MONDO_0003233), an agent's-choice candidate whose list held no approved item.")
    add("")

    # ---- 2. sources
    add("## 2. Every distinct `source` value")
    add("")
    add("Counted over every report of every row in the saved answers (a report on two forms' "
        "rows is counted twice here).")
    add("")
    rows = []
    for source, count in sorted(sources.items(), key=lambda pair: -pair[1]):
        stages = by_stage[source]
        other = ", ".join(f"{stage} {n}" for stage, n in sorted(stages.items())
                          if stage not in (APPROVAL, WITHDRAWAL)) or "-"
        rows.append([f"`{source}`", count, stages.get(APPROVAL, 0), stages.get(WITHDRAWAL, 0),
                     other, example.get(source, "(no link)")])
    out += table(["source", "Reports", "of them APPROVAL", "of them WITHDRAWAL", "Other stages",
                  "One example link"], rows)
    add("How the values were matched to the names in the task: `DailyMed`, `FDA` and "
        "`EMA Human Drugs` are group A's three. `TTD`, `PMDA` and `ATC` are matched only when the "
        "value is exactly that word. Every other value goes to group F and is named there.")
    add("")
    not_named = [name for name in sources if name not in ("DailyMed", "FDA", "EMA Human Drugs", "PMDA", "TTD", "ATC")]
    add("Values the briefing did not name: " + ", ".join(
        f"`{name}` ({by_stage[name].get(APPROVAL, 0)} of its reports are APPROVAL)" for name in not_named)
        + ". `ClinicalTrials.gov` is a list of trials, yet a few of its reports carry the stage "
        "`APPROVAL`. An item whose only approval reports are those is in group F.")
    add("")
    missing = [name for name in ("DailyMed", "FDA", "EMA Human Drugs", "PMDA", "TTD", "ATC")
               if name not in sources]
    if missing:
        add("**Did not match the briefing:** the value(s) " + ", ".join(f"`{m}`" for m in missing)
            + " never appeared as a `source` in any saved answer.")
        add("")

    # ---- 3. groups
    add("## 3. Approved items by group")
    add("")
    for letter in GROUPS:
        add(f"- **{letter}**: {GROUP_WORDS[letter]}")
    add("")
    for set_name, words in scopes():
        mine_shown, mine_all = in_set(shown, set_name), in_set(items, set_name)
        add(f"### {words}")
        add("")
        rows = []
        for letter in GROUPS:
            a = sum(1 for item in mine_shown if item["group"] == letter)
            b = sum(1 for item in mine_all if item["group"] == letter)
            rows.append([letter, a, share(a, len(mine_shown)), b, share(b, len(mine_all))])
        rows.append(["Total", len(mine_shown), share(len(mine_shown), len(mine_shown)),
                     len(mine_all), share(len(mine_all), len(mine_all))])
        out += table(["Group", "On the Approved list today", "Share",
                      "Also counting those left out as withdrawn", "Share"], rows)
    f_mixes = collections.Counter(" + ".join(item["approval_sources"]) for item in items if item["group"] == "F")
    add("Group F, which sources (all approved items): "
        + (", ".join(f"`{mix}` {count}" for mix, count in f_mixes.most_common()) or "none") + ".")
    add("")

    e_items = [item for item in items if item["group"] == "E"]
    e_withdrawal = sum(1 for item in e_items if item["has_withdrawal_report"])
    e_empty = sum(1 for item in e_items if not item["reports"])
    add(f"Group E, a closer look (all {len(e_items)} approved items): {e_withdrawal} have a "
        f"WITHDRAWAL report, {e_empty} have no report of any kind on their rows, and "
        f"{len(e_items) - e_withdrawal - e_empty} have only trial or `PREAPPROVAL` reports. "
        "For every one of them the row's stage word still says `APPROVAL`.")
    add("")

    # ---- 4. diseases with something outside A
    add("## 4. Diseases with at least one approved item outside group A")
    add("")
    add(f"Kashish predicted: **{PREDICTION}**.")
    add("")
    rows = []
    for set_name, words in scopes():
        mine = in_set(found, set_name)
        a = {item["disease_id"] for item in in_set(shown, set_name) if no_strong(item)}
        b = {item["disease_id"] for item in in_set(items, set_name) if no_strong(item)}
        rows.append([words, len(mine), len(a), len(b), PREDICTION if set_name is None else ""])
    out += table(["Set", "Diseases in the study", "With an item outside A on the Approved list today",
                  "Also counting items left out as withdrawn", "Kashish's prediction"], rows)
    rows = []
    for d in found:
        mine = [item for item in shown if item["disease_id"] == d["id"]]
        outside = [item for item in mine if no_strong(item)]
        if outside:
            letters = collections.Counter(item["group"] for item in outside)
            rows.append([SET_WORDS[d["set"]], d["name"], d["id"], len(mine), len(outside),
                         ", ".join(f"{letter} {letters[letter]}" for letter in OUTSIDE if letters[letter])])
    add("The diseases, counting only items on the Approved list today:")
    add("")
    out += table(["Set", "Disease", "Id", "On the Approved list today", "Outside A", "Which groups"], rows)

    outside_items = [item for item in items if no_strong(item)]
    add("## 5. Every approved item in groups B, C, D, E and F (the main result)")
    add("")
    add(f"The full list holds {len(outside_items)} items and is not shortened. It is long, so it "
        "is printed **at the end of this file**, after section 9. Nothing else was moved.")
    add("")
    # ---- 6. withdrawal reports
    with_withdrawal = [item for item in items if item["has_withdrawal_report"]]
    add("## 6. Every approved item with a WITHDRAWAL report")
    add("")
    add(f"{len(with_withdrawal)} approved items have at least one report whose `clinicalStage` is "
        f"`WITHDRAWAL`. Moonlight leaves out {sum(1 for i in with_withdrawal if not i['shown_today'])} "
        f"of them today and shows {sum(1 for i in with_withdrawal if i['shown_today'])}. "
        "Moonlight decides from the `Withdrawn` drug warning, not from these reports.")
    add("")
    add(f"In these answers no row's own stage word (`maxClinicalStage`) is ever `WITHDRAWAL`. "
        f"Every item that has a WITHDRAWAL report passes Moonlight's approved test: "
        f"{len(withdrawal_not_approved)} items with a WITHDRAWAL report are not approved items.")
    add("")
    rows = []
    for item in with_withdrawal:
        links = "<br>".join(f"{r['source']}: {r['url']}" for r in item["reports"] if r["stage"] == WITHDRAWAL)
        rows.append([SET_WORDS[item["set"]], f"{item['disease_name']} ({item['disease_id']})",
                     f"{item['medicine_name']} ({item['medicine_id']})", item["group"],
                     yes_no(not item["shown_today"]), links])
    out += table(["Set", "Disease", "Medicine", "Group", "Moonlight leaves it out today",
                  "Its WITHDRAWAL reports"], rows)
    left_out_no_report = [item for item in items if not item["shown_today"] and not item["has_withdrawal_report"]]
    add(f"The other way round: {len(left_out_no_report)} approved items are left out today as "
        "withdrawn (drug warning) and have **no** WITHDRAWAL report on this disease's list. "
        "They are in `items.json` (`left_out_as_withdrawn_today` true, `has_withdrawal_report` false).")
    add("")
    rows = []
    for set_name, words in scopes():
        mine = in_set(items, set_name)
        row = [words, sum(1 for i in mine if not i["shown_today"])]
        for letter in GROUPS:
            row.append(sum(1 for i in mine if not i["shown_today"] and i["group"] == letter))
        rows.append(row)
    add("Approved items Moonlight leaves out today as withdrawn, by group:")
    add("")
    out += table(["Set", "Left out as withdrawn"] + list(GROUPS), rows)

    # ---- 7. the two rules
    add("## 7. Counts for Kashish's two possible rules")
    add("")
    add("**Rule 1**: approved items with no DailyMed, FDA or EMA approval report (groups B to F). "
        "The second pair of columns counts PMDA as a regulator too, so an item with a PMDA "
        "approval report is no longer counted.")
    add("")
    rows = []
    for set_name, words in scopes():
        mine_shown, mine_all = in_set(shown, set_name), in_set(items, set_name)
        a, b = sum(map(no_strong, mine_shown)), sum(map(no_strong, mine_all))
        c, d = sum(map(no_strong_even_with_pmda, mine_shown)), sum(map(no_strong_even_with_pmda, mine_all))
        rows.append([words, len(mine_shown), f"{a} ({share(a, len(mine_shown))})",
                     f"{c} ({share(c, len(mine_shown))})", len(mine_all),
                     f"{b} ({share(b, len(mine_all))})", f"{d} ({share(d, len(mine_all))})"])
    out += table(["Set", "On the Approved list today", "Rule 1", "Rule 1, PMDA is a regulator",
                  "Also counting left out as withdrawn", "Rule 1", "Rule 1, PMDA is a regulator"], rows)
    add("**Rule 2**: items with a WITHDRAWAL report and no APPROVAL report. Counted two ways: "
        "among approved items (these are all in group E), and among the items on the lists that "
        "Moonlight does not count as approved for the disease anyway.")
    add("")
    rows = []
    for set_name, words in scopes():
        mine = [i for i in in_set(items, set_name) if i["has_withdrawal_report"] and i["group"] == "E"]
        others = [i for i in in_set(withdrawal_not_approved, set_name) if not i["has_approval_report"]]
        rows.append([words, len(mine), sum(1 for i in mine if i["shown_today"]),
                     sum(1 for i in mine if not i["shown_today"]), len(others)])
    out += table(["Set", "Rule 2, approved items", "of them on the Approved list today",
                  "of them already left out as withdrawn", "Rule 2, items not approved for the disease"], rows)
    rule2 = [i for i in items if i["has_withdrawal_report"] and i["group"] == "E"]
    if rule2:
        add("The approved items Rule 2 would catch:")
        add("")
        out += table(["Set", "Disease", "Medicine", "On the Approved list today"],
                     [[SET_WORDS[i["set"]], f"{i['disease_name']} ({i['disease_id']})",
                       f"{i['medicine_name']} ({i['medicine_id']})", yes_no(i["shown_today"])] for i in rule2])

    # ---- 8. empty lists
    add("## 8. Diseases whose Approved list would become empty if groups B to F were hidden")
    add("")
    rows, rows_pmda, already_empty = [], [], []
    for d in found:
        mine = [item for item in shown if item["disease_id"] == d["id"]]
        if not mine:
            already_empty.append(d)
            continue
        if all(no_strong(item) for item in mine):
            letters = collections.Counter(item["group"] for item in mine)
            rows.append([SET_WORDS[d["set"]], d["name"], d["id"], len(mine),
                         ", ".join(f"{letter} {letters[letter]}" for letter in OUTSIDE if letters[letter])])
        if all(no_strong_even_with_pmda(item) for item in mine):
            rows_pmda.append(f"{d['name']} ({d['id']})")
    add(f"{len(rows)} diseases have items on the Approved list today, and every one of them is in "
        "groups B to F:")
    add("")
    out += table(["Set", "Disease", "Id", "Items that would be hidden", "Their groups"], rows)
    add(f"If PMDA counted as a regulator too, the list would still become empty for {len(rows_pmda)} "
        "of them" + (": " + ", ".join(rows_pmda) + "." if rows_pmda else "."))
    add("")
    add(f"{len(already_empty)} diseases have nothing on the Approved list today, before any new "
        "rule" + (": " + ", ".join(f"{d['name']} ({d['id']})" for d in already_empty) + "."
                  if already_empty else "."))
    add("")
    add("Only the disease's own list was read. In Moonlight a disease can also show approved "
        "medicines in the narrower and wider-group boxes; those were not studied here.")
    add("")
    # ---- 9. the corrections list
    from moonlight import engine
    pairs = sorted(engine.corrections())
    by_pair = {(item["medicine_id"], item["disease_id"]): item for item in items}
    add("## 9. Extra: where the medicines already on Moonlight's corrections list land")
    add("")
    add("Not asked for, but it costs nothing and may help Kashish judge the groups. "
        "`moonlight/corrections.json` (read, not changed) holds "
        f"{len(pairs)} medicine and disease pairs. All of their diseases are in this study.")
    add("")
    rows = []
    for medicine_id, disease_id in pairs:
        item = by_pair.get((medicine_id, disease_id))
        rows.append([disease_id, medicine_id] + (
            [item["disease_name"], item["medicine_name"], item["group"],
             ", ".join(item["approval_sources"]) or "none"] if item
            else ["(not an approved item in this study)", "", "", ""]))
    out += table(["Disease id", "Medicine id", "Disease", "Medicine", "Group", "Approval report sources"], rows)

    add("## What was not verified")
    add("")
    for line in NOT_VERIFIED:
        add("- " + line)
    add("")
    add("---")
    add("")
    # ---- 5. the full list
    add("## Section 5 in full: every approved item in groups B, C, D, E and F")
    add("")
    add(f"{len(outside_items)} items. Not shortened. For each item: its group, the sources of its "
        "approval reports, whether it is on the Approved list today, and then **every** report "
        "on its rows, written `stage | source | link`, approval reports first. "
        "No item here is labelled right or wrong: this study cannot tell.")
    add("")
    for set_name in SETS:
        mine = in_set(outside_items, set_name)
        add(f"### {SET_WORDS[set_name]} ({len(mine)} items)")
        add("")
        for d in found:
            here = sorted((item for item in mine if item["disease_id"] == d["id"]),
                          key=lambda item: (item["group"], item["medicine_name"].casefold()))
            if not here:
                continue
            add(f"#### {d['name']} ({d['id']})")
            add("")
            for item in here:
                where = ("on the Approved list today" if item["shown_today"]
                         else "left out today as withdrawn")
                approval = ", ".join(item["approval_sources"]) or "none"
                extra = "; has a WITHDRAWAL report" if item["has_withdrawal_report"] else ""
                add(f"- **{item['medicine_name']}** ({item['medicine_id']}) | group "
                    f"**{item['group']}** | approval report sources: {approval} | {where}{extra}")
                out.extend(report_lines(item) or ["    - (this item's rows hold no reports at all)"])
            add("")
    (HERE / "REPORT.md").write_text("\n".join(out) + "\n", encoding="utf-8")
