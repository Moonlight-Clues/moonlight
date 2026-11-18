"""Night watch P4, an extra step for question A3 only (alfuzosin).

Alfuzosin is in none of the answers saved for the 50 study diseases. So
this runs the very same steps (probe.study) for the diseases of
fixtures/probe_p3/diseases.json whose saved medicine list in probe_p3
names alfuzosin. Their results go to results_extra/ and are NOT counted in
Part A's tables or in Part B. The raw answers go to responses/ like all others.

Run from the repo root, after probe.py:

    MOONLIGHT_CACHE_DIR=<the same scratch folder> python3 fixtures/probe_p4/probe_alfuzosin.py
"""

import json
import pathlib
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import probe  # noqa: E402
from moonlight import fetch  # noqa: E402

BRANCH = "origin/probe-approval-proof"
FOLDER = "fixtures/probe_p3/responses/disease_drugs"


def main() -> int:
    hits = subprocess.run(["git", "grep", "-il", "alfuzosin", BRANCH, "--", FOLDER],
                          cwd=probe.ROOT, check=True, capture_output=True, text=True).stdout.split()
    ids = sorted({pathlib.PurePosixPath(hit).name.split(".")[0] for hit in hits})
    listed = json.loads(subprocess.run(["git", "show", probe.P3], cwd=probe.ROOT, check=True,
                                       capture_output=True, text=True).stdout)["diseases"]
    wanted = [d for d in listed if d.get("found") and d["id"] in ids]
    probe._read_index()
    fetch._send = probe.send
    start = probe._count[0]
    done = []
    for d in wanted:
        entry = {"set": "EXTRA (alfuzosin, " + d["set"] + ")", "id": d["id"], "name": d["name"]}
        result = probe.study(entry)
        probe.save(HERE / "results_extra" / f"{d['id']}.json", result)
        done.append(entry)
        print(d["name"], d["id"], "requests so far", probe._count[0], flush=True)
    probe.save(HERE / "extra_run.json", {"diseases": done,
                                         "requests_sent": probe._count[0] - start})
    return 0


if __name__ == "__main__":
    sys.exit(main())
