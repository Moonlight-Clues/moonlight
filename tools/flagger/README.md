# Nightly flagger (spec A8)

Checks a slice of Approved cards against their own label and lists the suspect ones for a person to read.
It never changes the site, `moonlight/*.py`, `moonlight/*.json` or `web/`. A flag is evidence, never an entry.

    python3 tools/flagger/flagger.py plan             # walk live /api/clues, read labels, pick the slice (no money spent)
    python3 tools/flagger/flagger.py submit --yes     # Message Batches API; needs ANTHROPIC_API_KEY in the environment
    python3 tools/flagger/flagger.py report           # flags/<date>.csv, flags/<date>.md, checked.json

- Reuses `docs/benchmarks/2026-11-24/` (prompt, batch calls and prices, quote check). Model: the benchmark's, low effort.
- Cards: Approved tab of each page in `diseases.txt` (main list and both folded boxes), minus cards already red.
  Order: oldest `checked.json` date first, never checked first, ties by a fixed hash.
- Labels: the card's own source link. Read: DailyMed (indications section), FDA label PDF, EMA EPAR page. Anything else
  (WHO ATC, TTD, PMDA list, trial pages) is NO_LABEL: no model call.
- Cost: input tokens at the batch price plus 250 output tokens a card; cards are taken until the estimate reaches USD 0.90
  (hard cap 1.00). The actual cost comes from the API's usage figures.
- Flags: NO, UNCLEAR, NO_LABEL, and any card whose verdict changed since its last check.
- `ANTHROPIC_API_KEY` is read from the environment only and never printed or written. Missing key: stops, writes nothing.
- `diseases.txt` is the 522 pages walked on 26 Nov 2026. The site has no list of every page; extend this file to widen the net.
