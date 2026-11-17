"""Night watch P3, steps 3 and 4: read the saved answers, never the network.

Run from the repo root, after probe.py:   python3 fixtures/probe_p3/analyse.py

It writes items.json (every approved item of every disease, with its group
and all its reports), and REPORT.md.

How an item is made, and when it counts as approved, is fetch.py's
_list_families, line for line: a medicine and its forms are one item (the
parent's id is the item's id); the item is approved for the disease if one
of its rows has maxClinicalStage "APPROVAL" and that form's own
maximumClinicalStage is "APPROVAL" too. Moonlight leaves an approved item
out as withdrawn if any of its forms has a "Withdrawn" drug warning
(fetch._was_withdrawn). check_against_moonlight() runs Moonlight's own
fetch_approved and fetch_withdrawn on the saved answers and stops if the two
ever disagree.
"""

import collections
import json
import pathlib
import sys
from unittest import mock

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from moonlight import fetch  # noqa: E402
from moonlight.records import Disease  # noqa: E402

HERE = pathlib.Path(__file__).resolve().parent
RESPONSES = HERE / "responses"

APPROVAL = fetch.APPROVAL
WITHDRAWAL = "WITHDRAWAL"

# The "source" values, exactly as Open Targets writes them. Checked against
# the list of distinct values in the saved answers, not from memory.
STRONG = ("DailyMed", "FDA", "EMA Human Drugs")  # group A: DailyMed, FDA or EMA
TTD, PMDA, ATC = "TTD", "PMDA", "ATC"
SETS = ("COMMON", "CANCER", "RARE", "AGENT")
SET_WORDS = {"COMMON": "Common", "CANCER": "Cancer", "RARE": "Rare", "AGENT": "Agent's choice"}
GROUPS = "ABCDEF"
GROUP_WORDS = {
    "A": "at least one approval report from DailyMed, FDA or EMA",
    "B": "approval reports only from TTD",
    "C": "approval reports only from PMDA",
    "D": "approval reports only from ATC",
    "E": "no APPROVAL report at all",
    "F": "anything else",
}


def families_of(answer: dict) -> dict:
    """Every item on a disease's own list, by item id (fetch._list_families,
    plus each report's source and stage)."""
    families = {}
    for row in answer["data"]["disease"]["drugAndClinicalCandidates"]["rows"]:
        drug = row["drug"]
        if drug is None:
            continue
        parent = drug["parentMolecule"]
        family_id = parent["id"] if parent else drug["id"]
        family = families.setdefault(
            family_id, {"id": family_id, "name": None, "forms": [], "approved": False,
                        "withdrawn_notes": [], "reports": []})
        family["withdrawn_notes"].append(fetch._was_withdrawn(drug))
        if parent:
            family["name"] = family["name"] or parent["name"]
        else:
            family["name"] = drug["name"]
        form = [drug["id"], drug["name"]]
        if form not in family["forms"]:
            if parent:
                family["forms"].append(form)
            else:
                family["forms"].insert(0, form)
        if row["maxClinicalStage"] == APPROVAL and drug["maximumClinicalStage"] == APPROVAL:
            family["approved"] = True
        for report in row["clinicalReports"]:
            kept = {"source": report["source"], "stage": report["clinicalStage"],
                    "url": report["url"]}
            if kept not in family["reports"]:
                family["reports"].append(kept)
    return families


def group_of(family: dict):
    """(group letter, the sources of its APPROVAL reports, sorted)."""
    sources = sorted({r["source"] for r in family["reports"] if r["stage"] == APPROVAL})
    if not sources:
        return "E", sources
    if any(source in STRONG for source in sources):
        return "A", sources
    if sources == [TTD]:
        return "B", sources
    if sources == [PMDA]:
        return "C", sources
    if sources == [ATC]:
        return "D", sources
    return "F", sources


def load(path):
    return json.loads(pathlib.Path(path).read_text(encoding="utf-8"))


def answer_for(disease_id: str) -> dict:
    return load(RESPONSES / "disease_drugs" / f"{disease_id}.response.json")


def check_against_moonlight(disease: dict, families: dict) -> None:
    """Moonlight's own code, fed the saved answer, must agree with this file."""
    answer = answer_for(disease["id"])
    with mock.patch.object(fetch, "_post_json", return_value=answer):
        record = Disease(id=disease["id"], name=disease["name"])
        shown = {entry.id: entry for entry in fetch.fetch_approved(record)}
        withdrawn = {entry.id for entry in fetch.fetch_withdrawn(record)}
    mine_shown = {f["id"] for f in families.values()
                  if f["approved"] and True not in f["withdrawn_notes"]}
    mine_withdrawn = {f["id"] for f in families.values() if True in f["withdrawn_notes"]}
    assert set(shown) == mine_shown, disease
    assert withdrawn == mine_withdrawn, disease
    for family_id, entry in shown.items():
        mine = {r["url"] for r in families[family_id]["reports"] if r["stage"] == APPROVAL and r["url"]}
        assert set(entry.approval_sources) == mine, (disease, family_id)


def gather():
    """(study, items, all_families_count, source table)."""
    study = load(HERE / "diseases.json")
    items = []
    sources = collections.Counter()
    by_stage = collections.defaultdict(collections.Counter)
    example = {}
    withdrawal_not_approved = []
    for disease in study["diseases"]:
        if not disease["found"]:
            continue
        families = families_of(answer_for(disease["id"]))
        check_against_moonlight(disease, families)
        disease["items_on_list"] = len(families)
        for row in answer_for(disease["id"])["data"]["disease"]["drugAndClinicalCandidates"]["rows"]:
            for report in row["clinicalReports"]:
                sources[report["source"]] += 1
                by_stage[report["source"]][report["clinicalStage"]] += 1
                if report["url"]:
                    example.setdefault(report["source"], report["url"])
        for family in families.values():
            has_withdrawal = any(r["stage"] == WITHDRAWAL for r in family["reports"])
            has_approval = any(r["stage"] == APPROVAL for r in family["reports"])
            left_out = True in family["withdrawn_notes"]
            base = {
                "set": disease["set"], "disease_id": disease["id"], "disease_name": disease["name"],
                "medicine_id": family["id"], "medicine_name": family["name"],
                "forms": family["forms"],
                "has_withdrawal_report": has_withdrawal,
                "left_out_as_withdrawn_today": left_out,
                "withdrawn_note_not_known": (not left_out) and None in family["withdrawn_notes"],
                "reports": family["reports"],
            }
            if family["approved"]:
                group, approval_sources = group_of(family)
                items.append(dict(base, group=group, approval_sources=approval_sources,
                                  shown_today=not left_out))
            elif has_withdrawal:
                withdrawal_not_approved.append(dict(base, has_approval_report=has_approval))
    return study, items, (sources, by_stage, example), withdrawal_not_approved


def main() -> int:
    study, items, source_table, withdrawal_not_approved = gather()
    (HERE / "items.json").write_text(
        json.dumps({"approved_items": items,
                    "not_approved_items_with_a_withdrawal_report": withdrawal_not_approved},
                   indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    import report  # writes REPORT.md
    report.write(study, items, source_table, withdrawal_not_approved)
    return 0


if __name__ == "__main__":
    sys.path.insert(0, str(HERE))
    sys.exit(main())
