# Nightly flagger (spec A8)

Checks a slice of Approved cards against their own label and lists the suspect ones for a person to read.
It never changes the site, `moonlight/*.py`, `moonlight/*.json` or `web/`. A flag is evidence, never an entry.

    python3 tools/flagger/flagger.py plan             # walk live /api/clues, read labels, pick the slice (no money spent)
    python3 tools/flagger/flagger.py submit --yes     # Message Batches API; needs ANTHROPIC_API_KEY in the environment
    python3 tools/flagger/flagger.py report           # flags/<date>.csv, flags/<date>-no-label.csv, flags/<date>.md, checked.json
    python3 tools/flagger/flagger.py combos           # list combo sources that Q22 would replace (no model call)

- Reuses `docs/benchmarks/2026-11-24/` (prompt, batch calls and prices, quote check). Model: the benchmark's, low effort.
- Cards: Approved tab of each page in `diseases.txt` (main list and both folded boxes), minus cards already red.
  Order: oldest `checked.json` date first, never checked first, ties by a fixed hash.
- Labels: the card's own source link. Read: DailyMed (indications section), FDA label PDF, EMA EPAR page. Anything else
  (WHO ATC, TTD, PMDA list, trial pages) is NO_LABEL: no model call.
- Combination products (Kashish, Q22): a combination pill's label does not count for one of its parts. The flagger
  decides a label is a combination when it names two or more distinct active ingredients (DailyMed SPL `ACTIB`
  moieties, the DailyMed "Active Ingredient/Active Moiety" table, EMA "Active substances", or a product title such
  as "ezetimibe and simvastatin"). If the card is only one of those parts, it looks up that medicine's own
  single-ingredient DailyMed SPL (search by drug name, skip combination titles, confirm the ingredients, prefer the
  most recently published). If none is found, the original source is kept. Tonight's dry-run cards were not re-sent.
- Cost: input tokens at the batch price plus 250 output tokens a card; cards are taken until the estimate reaches USD 0.90
  (hard cap 1.00). The actual cost comes from the API's usage figures.
- Flags: NO, UNCLEAR, and any card whose verdict changed since its last check. NO_LABEL cards go in
  `flags/<date>-no-label.csv`, sorted by source type, with a per-source count in the md file; they are not flags.
  Cards whose source is a combination with no single-ingredient label are added to that file as
  `combination only`; they keep their source and this does not by itself change the flag count.
  Cards that will switch to a single-ingredient label are marked not-yet-checked in `checked.json`
  (no date, `pending: combo-relabel`) so the next run reads them first.
- `ANTHROPIC_API_KEY` is read from the environment only and never printed or written. Missing key: stops, writes nothing.
- `diseases.txt` is the 522 pages walked on 26 Nov 2026. The site has no list of every page; extend this file to widen the net.
