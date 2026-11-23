"""Study P10 recount: every number in REPORT.md, counted again from the saved files.

Run from anywhere:   python3 fixtures/probe_p10/recount.py
It never touches the network and imports nothing from Moonlight. It reads
the saved answers in opentargets/ and clinicaltrials/, applies Moonlight's
rules as they are on main today (commit 7734f6f), prints the numbers and
writes two tables: medicines_table.csv and trials_table.csv.

Moonlight's rules, copied here in small:
  - the page looks at the disease's first 25 proteins (api.TOP_TARGETS);
  - a medicine is only met if it acts on one of those proteins
    (fetch.fetch_paths) or is APPROVED on the disease's own list, or on
    the list of a direct parent or child (fetch.fetch_approved);
  - a medicine and its tablet forms are one family;
  - not approved for anything, or withdrawn anywhere: left out (filter.group_of);
  - approved, in trials for this exact disease: "In trials";
  - approved, no link to this exact disease: "New clues".
"""
import csv
import json
import pathlib
import re
from collections import Counter

HERE = pathlib.Path(__file__).resolve().parent
OT = HERE / "opentargets"
PARENT = "MONDO_0016971"
LADDER = ("APPROVAL", "PHASE_4", "PHASE_3", "PHASE_2_3", "PHASE_2", "PHASE_1_2", "PHASE_1",
          "EARLY_PHASE_1", "IND", "PRECLINICAL", "WITHDRAWAL", "UNKNOWN")  # records.STAGE_ORDER


def load(folder, name):
    return json.loads((OT / folder / f"{name}.response.json").read_text())["data"]


def stronger(a, b):
    def place(stage):
        return LADDER.index(stage) if stage in LADDER else len(LADDER)
    if a is None:
        return b
    if b is None:
        return a
    return a if place(a) <= place(b) else b


def in_trials(stage):
    return bool(stage) and (stage.startswith("PHASE_") or stage.startswith("EARLY_PHASE_"))


def withdrawn(drug):
    """True if the form, its parent or a tablet form has a "Withdrawn" warning."""
    molecules = [drug, drug.get("parentMolecule")] + list(drug.get("childMolecules") or [])
    return any(
        (warning.get("warningType") or "").strip().lower() == "withdrawn"
        for molecule in molecules if molecule
        for warning in molecule.get("drugWarnings") or []
    )


def family_of(drug):
    parent = drug.get("parentMolecule")
    return (parent["id"], parent["name"]) if parent else (drug["id"], drug["name"])


# ---------------------------------------------------------------- the diseases
family = load("family", PARENT)
version = family["meta"]["dataVersion"]
disease_ids = [PARENT] + family["disease"]["descendants"]
names, lists, top25 = {}, {}, {}
for disease_id in disease_ids:
    answer = load("disease_drugs", disease_id)["disease"]
    names[disease_id] = answer["name"]
    lists[disease_id] = answer["drugAndClinicalCandidates"]
    rows = load("top_targets", disease_id)["disease"]["associatedTargets"]["rows"]
    top25[disease_id] = [(row["target"]["id"], row["target"]["approvedSymbol"]) for row in rows]

_target_rows = {}


def target_rows(target_id):
    if target_id not in _target_rows:
        answer = load("target_drugs", target_id)["target"]
        _target_rows[target_id] = answer["drugAndClinicalCandidates"]["rows"] if answer else []
    return _target_rows[target_id]


def on_page(disease_id, family_id):
    """What Moonlight meets of one family through the page's 25 proteins."""
    proteins, best, link, gone = [], None, None, False
    for target_id, symbol in top25[disease_id]:
        for row in target_rows(target_id):
            drug = row["drug"]
            if drug is None or family_of(drug)[0] != family_id:
                continue
            if symbol not in proteins:
                proteins.append(symbol)
            best = stronger(best, drug["maximumClinicalStage"])
            gone = gone or withdrawn(drug)
            for indication in drug["indications"]["rows"]:
                if indication["disease"] and indication["disease"]["id"] == disease_id:
                    link = stronger(link, indication["maxClinicalStage"])
    return proteins, best, link, gone


def group(best, link, gone):
    """filter.group_of, word for word in meaning."""
    if best != "APPROVAL" or gone:
        return "not_approved"
    if link is None:
        return "new_clue"
    if link == "APPROVAL":
        return "already_approved"
    if in_trials(link):
        return "being_studied"
    return "unclear_link"


# All places for the parent, to say how far outside the 25 a protein sits.
all_parent = load("top_targets", PARENT + ".all")["disease"]["associatedTargets"]
parent_place = {row["target"]["approvedSymbol"]: (place, row["score"])
                for place, row in enumerate(all_parent["rows"], start=1)}

# ------------------------------------------------- every medicine on every list
entries = []
for disease_id in disease_ids:
    families = {}
    for row in lists[disease_id]["rows"]:
        drug = row["drug"]
        if drug is None:
            continue
        family_id, family_name = family_of(drug)
        item = families.setdefault(family_id, {
            "disease_id": disease_id, "disease": names[disease_id], "family_id": family_id,
            "medicine": family_name, "forms": [], "stage_here": None, "best_anywhere": None,
            "withdrawn": False, "reports": [], "trial_numbers": [], "type": drug["drugType"]})
        item["forms"].append(drug["name"])
        item["stage_here"] = stronger(item["stage_here"], row["maxClinicalStage"])
        item["best_anywhere"] = stronger(item["best_anywhere"], drug["maximumClinicalStage"])
        item["withdrawn"] = item["withdrawn"] or withdrawn(drug)
        for report in row["clinicalReports"]:
            item["reports"].append(f'{report["source"]}:{report["id"]}:{report["clinicalStage"]}')
            if re.fullmatch(r"nct\d{8}", report["id"] or "", re.I):
                number = report["id"].upper()
                if number not in item["trial_numbers"]:
                    item["trial_numbers"].append(number)
    entries.extend(families.values())

for item in entries:
    record = load("drug", item["family_id"])["drug"]
    mechanisms = (record["mechanismsOfAction"] or {}).get("rows") or []
    item["acts_on"] = sorted({t["approvedSymbol"] for m in mechanisms for t in m["targets"]})
    proteins, best, link, gone = on_page(item["disease_id"], item["family_id"])
    item["met_through"] = proteins
    item["approved_anywhere"] = item["best_anywhere"] == "APPROVAL"
    # The two rules are checked separately, so a medicine can be kept out by both.
    item["kept_out_by_top25"] = not proteins
    item["kept_out_by_approved_elsewhere"] = not item["approved_anywhere"]
    approved_here = item["stage_here"] == "APPROVAL" and item["approved_anywhere"]
    if item["withdrawn"] or gone:
        item["shown"], item["why"] = "no", "withdrawn rule"
    elif approved_here:
        item["shown"], item["why"] = "yes: Approved tab", ""
    elif proteins:
        which = group(best, link, gone)
        item["shown"] = {"being_studied": "yes: In trials tab", "new_clue": "yes: New clues tab"}.get(which, "no")
        item["why"] = "" if item["shown"] != "no" else (
            "approved-elsewhere rule" if which == "not_approved" else "unclear link")
    else:
        rules = ["top-25 rule"] + ([] if item["approved_anywhere"] else ["approved-elsewhere rule"])
        item["shown"], item["why"] = "no", " and ".join(rules)
    if not proteins:
        if not item["acts_on"]:
            item["top25_detail"] = "the database names no protein for this medicine at all"
        else:
            places = [f"{s} is at place {parent_place[s][0]} of {all_parent['count']}"
                      if item["disease_id"] == PARENT and s in parent_place else f"{s} is not in the first 25"
                      for s in item["acts_on"]]
            item["top25_detail"] = "; ".join(places)
    else:
        item["top25_detail"] = "met through " + ", ".join(proteins)

print(f"Open Targets data version {version['year']}.{version['month']}")
print(f"Diseases looked at: {len(disease_ids)} = 1 parent + {len(disease_ids) - 1} narrower")
print(f"Direct children of the parent: {len(family['disease']['children'])}")
print()
print("1. MEDICINE LISTS")
for disease_id in disease_ids:
    count, rows = lists[disease_id]["count"], len(lists[disease_id]["rows"])
    assert count == rows, (disease_id, count, rows)
    if count:
        print(f"   {disease_id}  {names[disease_id]}: {count}")
empty = [d for d in disease_ids if not lists[d]["count"]]
print(f"   lists with no medicine at all: {len(empty)} of {len(disease_ids)}")
print()
print("2. EVERY MEDICINE ON ANY LIST")
for item in entries:
    print(f"   {item['medicine']} ({item['family_id']}, {item['type']}) on {item['disease_id']}")
    print(f"      stage for this disease: {item['stage_here']}; strongest stage anywhere: {item['best_anywhere']}"
          f"; approved for anything: {'yes' if item['approved_anywhere'] else 'no'}")
    print(f"      trial numbers: {', '.join(item['trial_numbers']) or 'none given'}; reports: {', '.join(item['reports'])}")
    print(f"      acts on: {', '.join(item['acts_on']) or 'no protein named'}; {item['top25_detail']}")
    print(f"      Moonlight shows it on this disease's page: {item['shown']}"
          + (f" ({item['why']})" if item["why"] else ""))
print()
print("3. COUNTS")
trial_entries = [item for item in entries if in_trials(item["stage_here"])]
print(f"   list entries (medicine on a list): {len(entries)}; different medicines: "
      f"{len({item['family_id'] for item in entries})}")
print(f"   entries whose stage is a trial phase: {len(trial_entries)}; approved for that disease: "
      f"{sum(1 for item in entries if item['stage_here'] == 'APPROVAL')}")
print(f"   in trials, listed under the parent: {sum(1 for i in trial_entries if i['disease_id'] == PARENT)}")
for disease_id in disease_ids[1:]:
    count = sum(1 for i in trial_entries if i["disease_id"] == disease_id)
    if count:
        print(f"   in trials, listed under {disease_id} {names[disease_id]}: {count}")
print(f"   narrower diseases with 0 in trials: "
      f"{sum(1 for d in disease_ids[1:] if not any(i['disease_id'] == d for i in trial_entries))}")
by_approved = [i for i in trial_entries if i["kept_out_by_approved_elsewhere"]]
by_top25 = [i for i in trial_entries if i["kept_out_by_top25"]]
both = [i for i in trial_entries if i["kept_out_by_top25"] and i["kept_out_by_approved_elsewhere"]]
def say(items):
    return f"{len(items)} entries, {len({i['family_id'] for i in items})} different medicines " \
           f"({', '.join(sorted({i['medicine'] for i in items})) or 'none'})"
print(f"   hidden by the approved-elsewhere rule: {say(by_approved)}")
print(f"   hidden by the top-25 rule: {say(by_top25)}")
print(f"      of those, no protein named at all: {say([i for i in by_top25 if not i['acts_on']])}")
print(f"      of those, protein named but outside the 25: {say([i for i in by_top25 if i['acts_on']])}")
print(f"   hidden by both rules at once: {say(both)}")
print(f"   hidden by the top-25 rule only: {say([i for i in by_top25 if i not in both])}")
print(f"   hidden by the approved-elsewhere rule only: {say([i for i in by_approved if i not in both])}")
print(f"   shown: {say([i for i in trial_entries if i['shown'].startswith('yes')])}")
print(f"   NR3C1 for the parent: place {parent_place['NR3C1'][0]} of {all_parent['count']}, "
      f"score {parent_place['NR3C1'][1]:.4f}; place 25 has score {all_parent['rows'][24]['score']:.4f}")
print()
print("   Extra: the same medicines on the OTHER pages of this family (met through the 25 proteins)")
for family_id, medicine in sorted({(i["family_id"], i["medicine"]) for i in entries}):
    seen = Counter()
    where = {}
    for disease_id in disease_ids:
        proteins, best, link, gone = on_page(disease_id, family_id)
        if proteins:
            which = group(best, link, gone)
            seen[which] += 1
            where.setdefault(which, []).append(disease_id)
    print(f"      {medicine}: met on {sum(seen.values())} of {len(disease_ids)} pages; "
          + ("; ".join(f"{k} on {len(v)} ({', '.join(v)})" for k, v in where.items()) or "never met"))
pages_with_nr3c1 = [d for d in disease_ids if any(s == "NR3C1" for _, s in top25[d])]
print(f"      pages with NR3C1 in the first 25: {len(pages_with_nr3c1)} ({', '.join(pages_with_nr3c1)})")

# A check against what Moonlight's real engine said on the day (saved, not re-run).
live = json.loads((HERE / "moonlight_live_run.json").read_text())["pages"]
for item in entries:
    page = live.get(item["disease_id"])
    if page:
        really = item["medicine"] in page["in_trials"] + page["new_clues"] + page["approved"] \
            + page["narrower_box"] + page["wider_group_box"]
        assert really == item["shown"].startswith("yes"), item
print("      recount agrees with moonlight_live_run.json for every entry on the pages saved there")

with open(HERE / "medicines_table.csv", "w", newline="") as handle:
    columns = ["disease_id", "disease", "family_id", "medicine", "type", "stage_here", "best_anywhere",
               "approved_anywhere", "trial_numbers", "reports", "acts_on", "top25_detail",
               "kept_out_by_top25", "kept_out_by_approved_elsewhere", "shown", "why"]
    writer = csv.DictWriter(handle, columns, extrasaction="ignore")
    writer.writeheader()
    for item in entries:
        writer.writerow({k: " | ".join(v) if isinstance(v, list) else v for k, v in item.items()})

# ------------------------------------------------------------ ClinicalTrials.gov
print()
print("4. CLINICALTRIALS.GOV")
studies = []
for page in sorted((HERE / "clinicaltrials").glob("search.page*.response.json")):
    answer = json.loads(page.read_text())
    total = answer.get("totalCount", None) if "totalCount" in answer else None
    studies.extend(answer["studies"])
on_lists = {}
for item in entries:
    for number in item["trial_numbers"]:
        on_lists.setdefault(number, []).append(f"{item['medicine']} @ {item['disease_id']}")
WORDS = re.compile(r"limb[\s-]*girdle|LGMD", re.I)
table = []
for study in studies:
    protocol = study["protocolSection"]
    conditions = protocol["conditionsModule"].get("conditions", [])
    keywords = protocol["conditionsModule"].get("keywords", [])
    titles = [protocol["identificationModule"].get("briefTitle", ""),
              protocol["identificationModule"].get("officialTitle", "")]
    labels = [m["term"] for m in study.get("derivedSection", {}).get("conditionBrowseModule", {}).get("meshes", [])]
    if any(WORDS.search(text) for text in conditions):
        how = "A: in the conditions as written"
    elif any(WORDS.search(text) for text in keywords + titles):
        how = "B: only in the title or keywords"
    elif any(WORDS.search(text) for text in labels):
        how = "C: only in a label ClinicalTrials.gov added itself"
    else:
        how = "D: not in any saved field"
    interventions = protocol.get("armsInterventionsModule", {}).get("interventions", [])
    number = protocol["identificationModule"]["nctId"]
    table.append({
        "nct": number,
        "status": protocol["statusModule"]["overallStatus"],
        "phase": "/".join(protocol["designModule"].get("phases", [])) or "not given",
        "study_type": protocol["designModule"]["studyType"],
        "conditions": " | ".join(conditions),
        "interventions": " | ".join(f"{i['type']}: {i['name']}" for i in interventions),
        "intervention_types": sorted({i["type"] for i in interventions}),
        "how_matched": how,
        "on_open_targets_list": " | ".join(on_lists.get(number, [])) or "no",
    })
assert len(studies) == len({row["nct"] for row in table})
print(f"   trials returned: {len(table)} (ClinicalTrials.gov's own total: {total}); "
      f"all interventional: {all(row['study_type'] == 'INTERVENTIONAL' for row in table)}")
print("   status: " + ", ".join(f"{k} {v}" for k, v in Counter(r["status"] for r in table).most_common()))
print("   phase: " + ", ".join(f"{k} {v}" for k, v in Counter(r["phase"] for r in table).most_common()))
print("   how each one matched:")
for how, count in sorted(Counter(r["how_matched"] for r in table).items()):
    print(f"      {how}: {count}")
print("   kinds of intervention (a trial can have more than one): "
      + ", ".join(f"{k} {v}" for k, v in Counter(t for r in table for t in r["intervention_types"]).most_common()))
found = [r for r in table if r["on_open_targets_list"] != "no"]
print(f"   trial numbers on the Open Targets lists: {len(on_lists)} ({', '.join(sorted(on_lists))})")
print(f"   of the {len(table)} ClinicalTrials.gov trials, on an Open Targets list: {len(found)}; not on any: {len(table) - len(found)}")
print(f"   Open Targets trial numbers missing from the ClinicalTrials.gov answer: "
      f"{sorted(set(on_lists) - {r['nct'] for r in table}) or 'none'}")
for letter in "ABCD":
    part = [r for r in table if r["how_matched"].startswith(letter)]
    if part:
        print(f"   group {letter}: {len(part)} trials, {sum(1 for r in part if r['on_open_targets_list'] != 'no')} on an Open Targets list")
drugs_a = [r for r in table if r["how_matched"].startswith("A") and "DRUG" in r["intervention_types"]]
print(f"   group A trials with a DRUG intervention: {len(drugs_a)}, "
      f"{sum(1 for r in drugs_a if r['on_open_targets_list'] != 'no')} on an Open Targets list")
with open(HERE / "trials_table.csv", "w", newline="") as handle:
    columns = ["nct", "status", "phase", "conditions", "interventions", "how_matched", "on_open_targets_list"]
    writer = csv.DictWriter(handle, columns, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(table)
