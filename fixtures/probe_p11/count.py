"""Night order 2 (study P11): what the older "Withdrawn" flag hides.

Read-only study. It never talks to Open Targets, Gemini or any other host.
It writes only under fixtures/probe_p11/.

Run from the repo root:

    python3 fixtures/probe_p11/count.py

What it does, for each of the 50 diseases of the baseline (probe P5):

1. It does what moonlight/api.py's _find does, with the same functions in
   the same order, using today's code. Every question Moonlight asks is
   answered from the answers saved on the branch probe-baseline, in
   fixtures/probe_p5/responses/ (read with "git show", nothing is merged).
   A question with no saved answer stops that disease: nothing is fetched.
2. It does the same again with the older flag switched off: wherever
   fetch._was_withdrawn says True ("this medicine carries a Withdrawn
   warning"), it is made to say False. Nothing else is different.
3. A medicine with a card on the Approved tab (main list, narrower box or
   wider-group box) in run 2 and no card there in run 1 is "hidden by the
   older flag". One CSV row is written for it.

Only two things in Moonlight are swapped, both while this script runs and
neither in a file: fetch._post_json (the one function every question goes
through; the tests swap it too) and, for run 2 only, fetch._was_withdrawn.
"""

import collections
import csv
import functools
import json
import pathlib
import subprocess
import sys
import threading

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from moonlight import api, engine, fetch  # noqa: E402

HERE = pathlib.Path(__file__).resolve().parent
P5 = "fixtures/probe_p5"
SAVED_ON = ("origin/probe-baseline", "probe-baseline")  # the first one git knows is used
# Earlier saved answers on main (15 Nov) that asked for the whole warning.
# They are about six medicines only. Read if a hidden medicine is one of them.
FULL_WARNINGS = ROOT / "fixtures" / "withdrawn_probe"
NOT_HELD = "the saved answers do not hold it"

KINDS = {
    fetch.DISEASE_QUERY: "disease",
    fetch.FAMILY_QUERY: "family",
    fetch.TARGETS_QUERY: "targets",
    fetch.TARGET_DRUGS_QUERY: "target_drugs",
    fetch.DISEASE_DRUGS_QUERY: "disease_drugs",
}
PLACES = (("approved", "main list"), ("narrower", "narrower box"),
          ("wider_group", "wider-group box"))


class NotSaved(fetch.FetchError):
    """Moonlight asked a question the baseline has no saved answer for."""


def _branch() -> str:
    for name in SAVED_ON:
        found = subprocess.run(["git", "rev-parse", "--verify", "--quiet", name],
                               cwd=ROOT, capture_output=True)
        if found.returncode == 0:
            return name
    raise SystemExit("The branch probe-baseline is not here. Fetch it by name first.")


BRANCH = _branch()


def git_show(path: str) -> str:
    return subprocess.run(["git", "show", f"{BRANCH}:{path}"], cwd=ROOT, check=True,
                          capture_output=True).stdout.decode("utf-8")


def _key(kind: str, variables: dict) -> str:
    return kind + " " + json.dumps(variables, sort_keys=True)


def read_index() -> dict:
    """question -> the files that hold its saved answers, in the order asked."""
    files = collections.defaultdict(list)
    for line in git_show(f"{P5}/responses/index.jsonl").splitlines():
        entry = json.loads(line)
        if entry["has_errors"]:
            continue
        found = files[_key(entry["kind"], entry["variables"])]
        if entry["file"] not in found:
            found.append(entry["file"])
    return files


INDEX = read_index()
_lock = threading.Lock()
_answers = {}  # question -> the saved answer Moonlight is handed
_served = threading.local()


@functools.lru_cache(maxsize=None)
def _file(name: str) -> dict:
    return json.loads(git_show(f"{P5}/responses/{name}"))


def saved_answer(body: dict) -> dict:
    """Stands in for fetch._post_json. The saved answer, never the network.

    The baseline asked each "which medicines?" question twice, as Moonlight
    does. If it saved two different answers, the one with the most clinical
    reports is handed over, the earlier one if they are equally full: the
    same choice fetch._send_keeping_the_fullest makes.
    """
    kind = KINDS.get(body["query"])
    if kind is None:
        raise NotSaved("A question the baseline never asked (its words are not known).")
    key = _key(kind, body["variables"])
    with _lock:
        if key not in _answers:
            names = INDEX.get(key)
            if not names:
                raise NotSaved(f"No saved answer for: {key}")
            answers = [_file(name) for name in names]
            _answers[key] = max(answers, key=fetch._report_count) \
                if body["query"] in fetch.MEDICINE_QUERIES else answers[0]
        USED[key] = _answers[key]
        return _answers[key]


def no_network(body: dict) -> dict:
    raise NotSaved("This study never asks Open Targets anything.")


USED = {}  # every saved answer handed over for the disease now being studied
_flag = fetch._was_withdrawn  # the older flag, as fetch.py reads it


def _flag_off(drug: dict):
    """The older flag switched off: a True becomes False. A "not said" (None)
    stays "not said"."""
    said = _flag(drug)
    return False if said is True else said


def tabs_for(disease_id: str, flag_exists: bool):
    """What api.py's _find does, with the same functions, in the same order."""
    fetch._was_withdrawn = _flag if flag_exists else _flag_off
    try:
        disease = fetch.fetch_disease(disease_id)
        if disease is None:
            raise NotSaved(f"The saved answer does not know {disease_id}")
        targets = fetch.fetch_targets(disease, api.TOP_TARGETS)
        tray = engine.find_clues(disease, targets)
        neighbours = engine.fetch_neighbours(disease)
        tabs = engine.sort_into_tabs(
            tray, fetch.fetch_approved(disease), fetch.fetch_withdrawn(disease), neighbours,
            fetch.fetch_listed_medicines(disease), engine.added_by_hand(disease.id))
        return disease, tabs, neighbours, tray
    finally:
        fetch._was_withdrawn = _flag


def families_of(answer: dict) -> dict:
    """Family id -> what one saved "which medicines?" answer says about it,
    read from the raw rows. Families are joined as fetch._list_families
    joins them: a form goes with the medicine it is a form of."""
    families = {}
    for row in fetch._rows(answer):
        drug = row.get("drug")
        if drug is None:
            continue
        parent = drug.get("parentMolecule")
        family = families.setdefault(parent["id"] if parent else drug["id"], {
            "stages": set(), "approved_here": False, "approval_sources": set(),
            "withdrawal_sources": set(), "flagged": {}, "warning_types": set(),
            "warning_fields": set()})
        if "maxClinicalStage" in row:  # only a disease's list has this on the row
            family["stages"].add(row["maxClinicalStage"])
            if row["maxClinicalStage"] == fetch.APPROVAL and \
                    drug["maximumClinicalStage"] == fetch.APPROVAL:
                family["approved_here"] = True
        for report in row.get("clinicalReports") or []:
            if report.get("clinicalStage") == fetch.APPROVAL:
                family["approval_sources"].add(report.get("source") or "(no source said)")
            if report.get("clinicalStage") == fetch.WITHDRAWAL:
                family["withdrawal_sources"].add(report.get("source") or "(no source said)")
        for molecule in [drug, parent] + list(drug.get("childMolecules") or []):
            for warning in (molecule or {}).get("drugWarnings") or []:
                family["warning_fields"].update(warning)
                kind = (warning.get("warningType") or "").strip()
                family["warning_types"].add(kind)
                if kind.lower() == fetch.WITHDRAWN:
                    family["flagged"][molecule["id"]] = molecule["name"]
    return families


def full_warnings() -> dict:
    """Molecule id -> its Withdrawn warnings with country, year and
    description, from the six medicines asked about in full on 15 Nov."""
    found = {}
    for path in sorted(FULL_WARNINGS.glob("drug_*.response.json")):
        drug = (json.loads(path.read_text(encoding="utf-8")).get("data") or {}).get("drug")
        if not drug:
            continue
        for molecule in [drug, drug.get("parentMolecule")] + list(drug.get("childMolecules") or []):
            for warning in (molecule or {}).get("drugWarnings") or []:
                if (warning.get("warningType") or "").strip().lower() == fetch.WITHDRAWN:
                    found.setdefault(molecule["id"], []).append(
                        (warning, path.relative_to(ROOT).as_posix()))
    return found


def joined(things) -> str:
    return "; ".join(sorted(things))


def yes_no(value: bool) -> str:
    return "yes" if value else "no"


def study(entry: dict, full: dict) -> dict:
    USED.clear()
    disease, with_flag, neighbours, tray = tabs_for(entry["id"], flag_exists=True)
    _, without_flag, neighbours_without, _ = tabs_for(entry["id"], flag_exists=False)

    shown = {m.id: place for attr, place in PLACES for m in getattr(with_flag, attr)}
    would = {m.id: (place, m) for attr, place in PLACES for m in getattr(without_flag, attr)}
    # A card that is on the Approved tab in both runs must be in the same place.
    moved = sorted(i for i in shown if i in would and would[i][0] != shown[i])
    gone = sorted(i for i in shown if i not in would)
    elsewhere = {engine._family_id(c.medicine) for c in with_flag.being_studied + with_flag.new_clues}
    elsewhere |= {m.id for m in with_flag.more_in_trials + with_flag.new_in_trials}

    own = families_of(USED[_key("disease_drugs", {"diseaseId": disease.id})])
    near = {n.disease.id: families_of(USED[_key("disease_drugs", {"diseaseId": n.disease.id})])
            for n in neighbours}
    paths = {}
    for key, answer in USED.items():
        if key.startswith("target_drugs "):
            for family_id, family in families_of(answer).items():
                paths.setdefault(family_id, []).append(family)
    on_a_path = {engine._family_id(p.medicine) for group in tray.values() for p in group}
    by_hand = {e.medicine_id for e in engine.added_by_hand(disease.id)}

    rows = []
    for family_id, (place, medicine) in would.items():
        if family_id in shown:
            continue
        seen = [("the disease's own list", own.get(family_id))]
        seen += [("a protein's list", f) for f in paths.get(family_id, [])]
        seen += [(f"the list of {n.role} {n.disease.name}", near[n.disease.id].get(family_id))
                 for n in neighbours]
        seen = [(where, f) for where, f in seen if f]
        flagged, flag_seen, types, fields = {}, [], set(), set()
        for where, family in seen:
            types |= family["warning_types"]
            fields |= family["warning_fields"]
            if family["flagged"]:
                flagged.update(family["flagged"])
                if where not in flag_seen:
                    flag_seen.append(where)
        mine = own.get(family_id)
        # For a box card: the parent or child lists that say "approved there".
        there = [(n, near[n.disease.id][family_id]) for n in neighbours_without
                 if family_id in {e.id for e in n.approved}]
        details = [w for i in sorted(flagged) for w in full.get(i, [])]
        row = {
            "disease_id": disease.id, "disease": disease.name,
            "medicine_id": family_id, "medicine": medicine.name,
            "place": place,
            "added_by_hand": yes_no(family_id in by_hand),
            "acts_on_one_of_the_25_proteins": yes_no(family_id in on_a_path),
            "on_own_list": yes_no(mine is not None),
            "own_list_stage_words": joined(mine["stages"]) if mine else "",
            "own_list_approval_report": yes_no(bool(mine and mine["approval_sources"])),
            "own_list_approval_sources": joined(mine["approval_sources"]) if mine else "",
            "own_list_regulator_approval_report": yes_no(bool(
                mine and mine["approval_sources"] & set(fetch.REGULATOR_SOURCES))),
            "own_list_withdrawal_report": yes_no(bool(mine and mine["withdrawal_sources"])),
            "own_list_withdrawal_sources": joined(mine["withdrawal_sources"]) if mine else "",
            "box_approved_on": joined(f"{n.disease.name} ({n.disease.id})" for n, _ in there)
            if place != "main list" else "",
            "box_list_approval_sources": joined(
                {s for _, f in there for s in f["approval_sources"]}) if place != "main list" else "",
            "box_list_withdrawal_report": yes_no(any(f["withdrawal_sources"] for _, f in there))
            if place != "main list" else "",
            "box_list_withdrawal_sources": joined(
                {s for _, f in there for s in f["withdrawal_sources"]}) if place != "main list" else "",
            "flag_is_on": joined(f"{name} ({i})" for i, name in flagged.items()),
            "flag_seen_in": "; ".join(flag_seen),
            "warning_types_in_saved_answers": joined(types),
            "warning_fields_in_saved_answers": joined(fields),
            "warning_country": NOT_HELD, "warning_year": NOT_HELD,
            "warning_description": NOT_HELD,
            "warning_details_from": "",
            "has_any_card_today": yes_no(family_id in elsewhere),
        }
        if details:  # one of the six medicines asked about in full on 15 Nov
            # The database repeats one warning many times. Each different
            # value is written once, in the order first met.
            for column, field in (("warning_country", "country"), ("warning_year", "year"),
                                  ("warning_description", "description")):
                values = []
                for warning, _ in details:
                    if str(warning.get(field)) not in values:
                        values.append(str(warning.get(field)))
                row[column] = " | ".join(values)
            row["warning_details_from"] = joined({path for _, path in details}) + \
                " (an older saved answer, 15 Nov, not the baseline)"
        rows.append(row)
    order = [place for _, place in PLACES]
    rows.sort(key=lambda r: (order.index(r["place"]), r["medicine"].casefold(), r["medicine_id"]))
    return {
        "id": disease.id, "name": disease.name, "rows": rows,
        "cards_today": {place: sum(1 for p in shown.values() if p == place) for _, place in PLACES},
        "cards_without_flag": {place: sum(1 for p, _ in would.values() if p == place)
                               for _, place in PLACES},
        "moved": moved, "gone": gone,
    }


def all_warning_fields() -> dict:
    """Every field name on every drugWarnings entry in every saved answer
    this study was handed, with how many entries carry it."""
    counts = collections.Counter()
    for answer in _answers.values():
        for row in fetch._rows(answer) if (answer.get("data") or {}).get("target") or \
                (answer.get("data") or {}).get("disease") else []:
            drug = row.get("drug") or {}
            for molecule in [drug, drug.get("parentMolecule")] + list(drug.get("childMolecules") or []):
                for warning in (molecule or {}).get("drugWarnings") or []:
                    counts.update(warning.keys())
    return dict(counts)


def main() -> int:
    fetch._post_json = saved_answer  # the swap the tests use. fetch.py is not changed.
    fetch._send = no_network  # and a locked door behind it
    diseases = json.loads(git_show(f"{P5}/diseases.json"))
    full = full_warnings()
    results, problems = [], []
    for number, entry in enumerate(diseases["diseases"], start=1):
        try:
            result = study(entry, full)
        except NotSaved as error:  # written down, never fetched
            problems.append({"id": entry["id"], "name": entry["name"], "problem": str(error)})
            print(f"{number}/50 {entry['name']}: STOPPED: {error}", flush=True)
            continue
        results.append(result)
        print(f"{number}/50 {result['name']}: hidden {len(result['rows'])}", flush=True)

    rows = [row for result in results for row in result["rows"]]
    with (HERE / "hidden_by_old_flag.csv").open("w", encoding="utf-8", newline="") as out:
        writer = csv.DictWriter(out, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    def count(key):
        return dict(sorted(collections.Counter(row[key] for row in rows).items()))

    main_rows = [row for row in rows if row["place"] == "main list"]
    summary = {
        "data_version": diseases["data_version"],
        "saved_answers_read_from": BRANCH,
        "saved_answers_commit": subprocess.run(
            ["git", "rev-parse", BRANCH], cwd=ROOT, capture_output=True, text=True).stdout.strip(),
        "code_commit": subprocess.run(
            ["git", "log", "-1", "--format=%H", "--", "moonlight", "web"], cwd=ROOT,
            capture_output=True, text=True).stdout.strip(),
        "diseases_studied": len(results),
        "diseases_stopped": problems,
        "saved_answers_handed_over": len(_answers),
        "rows": len(rows),
        "different_medicines": len({row["medicine_id"] for row in rows}),
        "diseases_with_a_hidden_medicine": sum(1 for r in results if r["rows"]),
        "by_place": count("place"),
        "main_list_by_approval_report_then_withdrawal_report": dict(sorted(collections.Counter(
            f"approval report {r['own_list_approval_report']}, "
            f"withdrawal report {r['own_list_withdrawal_report']}" for r in main_rows).items())),
        "main_list_with_a_regulator_approval_report": sum(
            1 for r in main_rows if r["own_list_regulator_approval_report"] == "yes"),
        "main_list_by_approval_sources": dict(sorted(collections.Counter(
            r["own_list_approval_sources"] or "(no APPROVAL report)" for r in main_rows).items())),
        "box_rows_on_own_list": count_where(rows, lambda r: r["place"] != "main list"
                                            and r["on_own_list"] == "yes"),
        "box_rows_by_withdrawal_report_on_the_box_list": dict(sorted(collections.Counter(
            r["box_list_withdrawal_report"] for r in rows if r["place"] != "main list").items())),
        "added_by_hand": count("added_by_hand"),
        "acts_on_one_of_the_25_proteins": count("acts_on_one_of_the_25_proteins"),
        "flag_seen_in": count("flag_seen_in"),
        "rows_with_country_year_description": count_where(
            rows, lambda r: r["warning_country"] != NOT_HELD),
        "hidden_medicine_has_some_card_today": count("has_any_card_today"),
        "warning_field_names_in_all_saved_answers": all_warning_fields(),
        "cards_that_changed_place": sum(len(r["moved"]) for r in results),
        "cards_only_there_with_the_flag": sum(len(r["gone"]) for r in results),
        "approved_tab_cards_today": {place: sum(r["cards_today"][place] for r in results)
                                     for _, place in PLACES},
        "approved_tab_cards_without_the_flag": {
            place: sum(r["cards_without_flag"][place] for r in results) for _, place in PLACES},
        "per_disease": [{"id": r["id"], "name": r["name"], "hidden": len(r["rows"]),
                         **{place: sum(1 for row in r["rows"] if row["place"] == place)
                            for _, place in PLACES},
                         "cards_today": r["cards_today"]} for r in results],
    }
    (HERE / "summary.json").write_text(
        json.dumps(summary, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in summary.items() if k != "per_disease"}, indent=1))
    return 1 if problems else 0


def count_where(rows, test) -> int:
    return sum(1 for row in rows if test(row))


if __name__ == "__main__":
    sys.exit(main())
