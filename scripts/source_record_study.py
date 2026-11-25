"""Ticket 2.53 study (read-only): which Source record links move.

For each disease, builds the /api/clues page from live Open Targets (as the
site does) and, for every main-list Approved card, notes the link the card
showed before ticket 2.53 and the link it shows now, and whether the link
it shows now is a regulator's (a hand-written label, or an approval report
whose "source" is in fetch.REGULATOR_SOURCES).

"Main list" means the Approved tab's own list: cards in the key "approved"
that are not moved into a folded box (no_regulator_box, wrong_approvals_box).

    python3 scripts/source_record_study.py            # the 10 audited diseases
    python3 scripts/source_record_study.py --json     # the same, as JSON

Needs the network (api.platform.opentargets.org). Writes nothing. Gemini is
never called: the page answer does not need it.
"""

import json
import pathlib
import sys
from dataclasses import replace

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from fastapi.testclient import TestClient  # noqa: E402

from moonlight import api, engine, fetch  # noqa: E402
from warm import AUDITED  # noqa: E402

_rule = engine.ApprovedMedicine.source_record.fget
_seen = {}  # card id -> (old link, new link, regulator?)


def _old(card):
    return _rule(replace(card, regulator_sources=()))


def _watched(card):
    new = _rule(card)
    by_hand = bool(card.added_from_label or card.confirmed_from_label)
    _seen[card.id] = (_old(card), new, by_hand or new in card.regulator_sources)
    return new


def study(disease_id):
    _seen.clear()
    api.forget_answers()
    page = TestClient(api.app).get("/api/clues", params={"disease_id": disease_id}).json()
    boxed = set(page.get("no_regulator_box", [])) | set(page.get("wrong_approvals_box", []))
    rows = []
    for card in page.get("approved", []):
        if card["id"] in boxed:
            continue
        old, new, regulator = _seen[card["id"]]
        assert new == card.get("source")
        rows.append({"id": card["id"], "medicine": card["medicine"], "before": old,
                     "after": new, "changed": old != new, "regulator": regulator})
    return {"disease_id": disease_id, "data_version": fetch.data_version(), "cards": rows}


def main(argv):
    engine.ApprovedMedicine.source_record = property(_watched)
    results = []
    for disease_id, name in AUDITED:
        one = study(disease_id)
        one["disease"] = name
        results.append(one)
    if "--json" in argv:
        print(json.dumps(results, indent=1))
        return 0
    total = changed = still = 0
    for one in results:
        cards = one["cards"]
        moved = [c for c in cards if c["changed"]]
        left = [c for c in cards if not c["regulator"]]
        total, changed, still = total + len(cards), changed + len(moved), still + len(left)
        print(f"{one['disease']} ({one['disease_id']}, data {one['data_version']}): "
              f"{len(cards)} main-list cards, {len(moved)} change link, "
              f"{len(left)} still not a regulator")
        for c in moved:
            print(f"   moves  {c['medicine']}: {c['before']} -> {c['after']}")
        for c in left:
            print(f"   needs a label  {c['medicine']}: {c['after']}")
    print(f"\nAll ten: {total} main-list Approved cards, {changed} change link, "
          f"{still} still show a non-regulator link.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
