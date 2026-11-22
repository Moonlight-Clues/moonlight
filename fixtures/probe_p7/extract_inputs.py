"""Probe P7, step 0: copy the NCT links out of probe P5 and probe P6.

Read-only. P5 and P6 are not on main, so their files are read straight from
their own branches with "git show", at the exact commits named below. Nothing
is checked out and nothing outside fixtures/probe_p7/ is written.

For every disease it reads results/<disease id>.json (written by that probe's
probe.py) and keeps two things:

  card links  the "Source record" link of every card (Approved main list, the
              two folded boxes, In trials, New clues) when that link is a
              ClinicalTrials.gov link
  own list    every ClinicalTrials.gov link among the reports of every
              medicine on the disease's own Open Targets list

    python3 fixtures/probe_p7/extract_inputs.py     # writes inputs/nct_links.json
"""

import json
import pathlib
import re
import subprocess

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "inputs" / "nct_links.json"
SOURCES = [
    {"probe": "P5", "branch": "probe-baseline", "folder": "fixtures/probe_p5",
     "commit": "3bc6dacc56841e5a6b7f35dfd76c3006ce24bf98"},
    {"probe": "P6", "branch": "probe-key-diseases", "folder": "fixtures/probe_p6",
     "commit": "23962bc503fefae45a5fa9eaf339f11ade805efc"},
]
NCT = re.compile(r"NCT\d{8}")
CTGOV_LINK = re.compile(r"^https://clinicaltrials\.gov/study/(NCT\d{8})$")


def show(commit, path):
    return subprocess.run(["git", "show", f"{commit}:{path}"], check=True,
                          capture_output=True, cwd=HERE).stdout.decode("utf-8")


def nct_of(url):
    """The NCT number of a ClinicalTrials.gov link, or None for any other link."""
    if not url or "clinicaltrials.gov" not in url:
        return None
    m = CTGOV_LINK.match(url)
    if not m:
        raise SystemExit(f"a ClinicalTrials.gov link of a shape not seen before: {url}")
    return m.group(1)


def main():
    out = {"sources": SOURCES, "diseases": []}
    for src in SOURCES:
        listed = json.loads(show(src["commit"], src["folder"] + "/diseases.json"))
        for d in listed["diseases"]:
            res = json.loads(show(src["commit"], f"{src['folder']}/results/{d['id']}.json"))
            cards = []
            for c in res["cards"]:
                n = nct_of(c.get("source"))
                if n:
                    cards.append({"nct": n, "tab": c["tab"], "medicine_id": c["id"]})
            own = set()
            for med in res["own_list"].values():
                for r in med["reports"]:
                    n = nct_of(r.get("url"))
                    if n:
                        own.add(n)
            out["diseases"].append({
                "probe": src["probe"], "id": d["id"], "name": d["name"],
                "cards_in_all": len(res["cards"]),
                "card_links": cards,
                "medicines_on_own_list": len(res["own_list"]),
                "own_list_ncts": sorted(own),
            })
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(out, indent=1) + "\n")
    cards = {c["nct"] for d in out["diseases"] for c in d["card_links"]}
    own = {n for d in out["diseases"] for n in d["own_list_ncts"]}
    print(f"diseases {len(out['diseases'])}, different NCT on cards {len(cards)}, "
          f"on own lists {len(own)}, on either {len(cards | own)}")


if __name__ == "__main__":
    main()
