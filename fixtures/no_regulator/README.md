# fixtures/no_regulator: saved answers for ticket 2.17

Open Targets data 26.09. Every answer is saved as sent, only re-indented.
Each `.request.json` is the exact body that was posted. Filed by question,
then by the id asked about, like `fixtures/narrower_box/`.

Five diseases, each with a whole search:

- MONDO_0019338 sarcoidosis (1 parent, 7 children)
- MONDO_0007739 Huntington disease (2 parents, 1 child)
- MONDO_0010679 Duchenne muscular dystrophy (1 parent, no children)
- MONDO_0021107 narcolepsy (1 parent, 3 children)
- MONDO_0004425 hyperthyroidism (1 parent, 11 children)

One more list, with no whole search: MONDO_0100339 Friedreich ataxia. Its
answer holds 25 medicines and no reports at all.

Where the files came from

- `disease_drugs/<one of the five ids, or MONDO_0100339>.*`: copied, not changed, from the
  branch `probe-approval-proof`, folder
  `fixtures/probe_p3/responses/disease_drugs/` (the study of 124 diseases,
  saved live on 2026-11-17). The question is fetch.py's DISEASE_DRUGS_QUERY
  with `source` added to each report, which is the question fetch.py asks
  from ticket 2.17 on.
- Everything else was asked live on 2026-11-18, with fetch.py's own words:
  - `disease/<id>.*`: DISEASE_QUERY.
  - `associated_targets/<id>.*`: TARGETS_QUERY, top 25.
  - `family/<id>.*`: FAMILY_QUERY.
  - `disease_drugs/<parent or child id>.*`: the same list question as
    above, for every direct parent and child. Asked twice (the ask-twice
    rule); the two answers were the same every time.
  - `target_drugs/<protein id>.*`: TARGET_DRUGS_QUERY for each of the 25
    proteins. Asked twice. Saved without indentation, because they are large.
- The five own lists were also asked again live on 2026-11-18. Each answer
  was exactly the copy from the study.

What the saved lists show

- `source` is the field's name on a clinical report. Every saved report
  has one. The values in these 34 lists: `ClinicalTrials.gov`, `DailyMed`,
  `EMA Human Drugs`, `FDA`, `INN`, `PMDA`, `TTD`, `USAN`. The study met one
  more in its 124 lists: `ATC`.
- Sarcoidosis: collagenase clostridium histolyticum has one approval
  report, from `TTD`. Prednisone has 41, all from `DailyMed`.
- Huntington disease: methylphenidate (as methylphenidate hydrochloride)
  has one approval report, from `PMDA`, with the link to Japan's general
  list.
- Duchenne muscular dystrophy: ataluren has no report whose stage is
  `APPROVAL`. It has 13 trial reports and one `WITHDRAWAL` report from
  `EMA Human Drugs`. Its row's stage word still says `APPROVAL`.
- Friedreich ataxia: idebenone and omaveloxolone are approved by their
  rows' stage words, and neither has a report of any kind. No row on the
  list has one.
- Narcolepsy: aceprometazine is approved only on the parent entry
  sleep-wake disorder (MONDO_0003406), with one approval report, from `TTD`.
- Hyperthyroidism: potassium iodide is approved only on the child entry
  thyrotoxicosis (MONDO_0010138), with one approval report, from `TTD`.

`approved_tab_before_2.17.json` is not an Open Targets answer. It is what
the code on main (commit 825bbd3, before ticket 2.17) answered at
`/api/clues` for the five diseases, worked out from the saved answers
here and cut down to what ticket 2.17 must not change: for every card in
the Approved main list and both folded boxes its id, name, "Source record"
link, number of reports and grey line, in the order shown; the ids in In
trials and in New clues, in order; and the two left-out counts.
