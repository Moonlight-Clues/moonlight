"""Study P12. Save what /api/clues sends for the five pages, from saved
fixtures only (the same helpers the tests use). No network.

    python fixtures/probe_p12/make_answers.py
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(ROOT / "tests")]

import old_flag_saved  # noqa: E402
import test_approvals_fourth_batch as mg_files  # noqa: E402
import test_approvals_third_batch as hd_files  # noqa: E402
import test_narrower_box as pah_files  # noqa: E402
import test_withdrawal_line as hem_files  # noqa: E402

from moonlight import fetch  # noqa: E402

MG = "MONDO_0009688"


def mg_post_json(body):
    """Myasthenia gravis: only its own medicine list is saved
    (fixtures/approvals_by_hand/disease_drugs/). The disease record, its
    proteins and its family are NOT saved, so they are answered as empty
    here: no description, no proteins, no parents or children. The page
    drawn from this shows the list-only parts (Approved, the In trials
    boxes) and no New clues. Study use only."""
    if body["query"] == fetch.DISEASE_QUERY:
        return {"data": {"disease": {"id": MG, "name": "myasthenia gravis",
                                     "description": None, "synonyms": []}}}
    if body["query"] == fetch.FAMILY_QUERY:
        return {"data": {"disease": {"id": MG, "name": "myasthenia gravis",
                                     "parents": [], "children": []}}}
    if body["query"] == fetch.TARGETS_QUERY:
        return {"data": {"disease": {"id": MG, "associatedTargets": {"count": 0, "rows": []}}}}
    return mg_files.saved_post_json(body)


OUT = pathlib.Path(__file__).resolve().parent / "answers"
PAGES = {
    "huntington": ("MONDO_0007739", hd_files.saved_post_json),
    "type2diabetes": ("MONDO_0005148", old_flag_saved.saved_post_json),
    "pah": ("MONDO_0015924", pah_files.saved_post_json),
    "myasthenia": (MG, mg_post_json),
    "haemophiliaA": ("MONDO_0010602", hem_files.saved_post_json),
}
for name, (disease_id, post_json) in PAGES.items():
    answer = hem_files.page_answer(disease_id, post_json)
    (OUT / f"{name}.json").write_text(json.dumps(answer, indent=1), encoding="utf-8")
    print(name, disease_id, "approved", len(answer["approved"]),
          "narrower", len(answer.get("narrower", [])), "wider", len(answer.get("wider_group", [])),
          "noreg", len(answer.get("no_regulator_box", [])), "red", len(answer.get("wrong_approvals_box", [])),
          "studied", len(answer["being_studied"]), "more", len(answer.get("more_in_trials", [])),
          "new", len(answer.get("new_in_trials", [])), "clues", len(answer["new_clues"]),
          "opposite", len(answer.get("opposite_way_box", [])))
