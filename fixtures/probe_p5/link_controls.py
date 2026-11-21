"""Night order 1 (probe P5), a small extra: what does each link host answer
for a link that cannot exist?

Not a card link. One made-up link per host, asked once, the same way
check_links.py asks (HEAD, then GET if HEAD is refused). It shows what a
status from that host can and cannot tell. Run it after check_links.py has
finished, so there is still only one request at a time:

    python3 fixtures/probe_p5/link_controls.py
"""

import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import check_links  # noqa: E402

MADE_UP = (
    "https://clinicaltrials.gov/study/NCT99999999",
    "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=00000000-0000-0000-0000-000000000000",
    "https://ttd.idrblab.cn/data/drug/details/DZZZZZZ",
    "https://www.ema.europa.eu/en/medicines/human/EPAR/not-a-medicine-xyz",
    "https://www.whocc.no/atc_ddd_index/?code=Z99ZZ99",
    "https://www.accessdata.fda.gov/drugsatfda_docs/label/2099/000000s000lbl.pdf",
    "https://searchusan.ama-assn.org/finder/usan/search/NOTAMEDICINEXYZ/relevant/1/",
)

if __name__ == "__main__":
    with (HERE / "link_controls.jsonl").open("w", encoding="utf-8") as out:
        for url in MADE_UP:
            line = check_links.check(url)
            out.write(json.dumps(line) + "\n")
            print(line["outcome"], line["final_status"], line["final_url"], flush=True)
