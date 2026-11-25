"""Ticket 3.6, part 4. Warm the live site, by hand.

Asks https://www.moonlightclues.com/api/clues for a list of diseases, one at
a time, and prints the time each took. Read-only: GET requests and nothing
else. Run it from the repo root after a deploy:

    python3 scripts/warm.py                       # the 10 audited diseases
    python3 scripts/warm.py MONDO_0010200 EFO_1   # and these two as well

The first of the 10 is the page's quick-start disease. A disease that
fails is reported and the rest carry on. Nothing is changed in Cloud Build
or Cloud Run, and nothing is written anywhere.
"""

import sys
import time
from typing import List, Sequence

import requests

URL = "https://www.moonlightclues.com/api/clues"
TIMEOUT_SECONDS = 120

# The 10 audited diseases (docs/benchmarks/2026-11-24-per-disease.csv). The
# first is also the quick-start chip on the page.
AUDITED = (
    ("MONDO_0015924", "pulmonary arterial hypertension"),
    ("MONDO_0007739", "Huntington disease"),
    ("MONDO_0016971", "limb-girdle muscular dystrophy"),
    ("MONDO_0005342", "IgA glomerulonephritis"),
    ("MONDO_0019100", "neuromyelitis optica"),
    ("MONDO_0003233", "essential tremor"),
    ("MONDO_0019438", "AL amyloidosis"),
    ("MONDO_0004691", "autosomal dominant polycystic kidney disease"),
    ("EFO_0803536", "multiple sclerosis symptom measurement"),
    ("MONDO_0009061", "cystic fibrosis"),
)
QUICK_START = "MONDO_0015924"


def disease_ids(extra: Sequence[str]) -> List[str]:
    """The quick-start disease, the audited ones, then any given, each once."""
    ids: List[str] = []
    for disease_id in [QUICK_START] + [i for i, _ in AUDITED] + list(extra):
        if disease_id not in ids:
            ids.append(disease_id)
    return ids


def main(argv: Sequence[str]) -> int:
    names = dict(AUDITED)
    failed = 0
    for disease_id in disease_ids(argv):
        label = f"{disease_id:<16} {names.get(disease_id, '')}"
        started = time.monotonic()
        try:
            response = requests.get(URL, params={"disease_id": disease_id}, timeout=TIMEOUT_SECONDS)
            took = time.monotonic() - started
            note = "" if response.status_code == 200 else f"  HTTP {response.status_code}"
            failed += response.status_code != 200
            print(f"{label} {took:7.2f} s  {len(response.content) / 1024:7.1f} KB{note}")
        except requests.RequestException as problem:
            failed += 1
            print(f"{label} {time.monotonic() - started:7.2f} s  failed ({type(problem).__name__})")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
