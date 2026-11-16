# fixtures/approval_proof: ticket 2.13 probe, saved 2026-11-16 (Open Targets data 26.09)

Live answers, saved as sent, only re-indented. Each `.request.json` is the
exact body that was posted.

The three diseases: MONDO_0004975 Alzheimer disease, MONDO_0007739 Huntington
disease, MONDO_0004980 atopic eczema.

- `clinical_report_type.*`: the fields of one clinical report (the
  `ClinicalReport` type), as the API lists them.
- `search_*.*`: fetch.py's SEARCH_QUERY for the three names.
- `<disease id>/disease.*`, `family.*`, `associated_targets.*` (top 25),
  `target_drugs/<place>_<symbol>_<id>.*`: fetch.py's DISEASE_QUERY,
  FAMILY_QUERY, TARGETS_QUERY and TARGET_DRUGS_QUERY, word for word, so a
  whole search can run offline. The `target_drugs` answers are saved without
  indentation, because they are large.
- `<disease id>/disease_drugs/own_<id>.*`, `parent_<lane>_<id>.*`,
  `child_<lane>_<id>.*`: fetch.py's DISEASE_DRUGS_QUERY, word for word, for
  the disease's own entry and each direct parent and child. Each was asked
  twice (the ask-twice rule) and the kept answer saved. Part 2 of the ticket
  added `clinicalStage` to the question's reports, so these 20 lists were
  asked again the same day with the new words. Every new answer was the old
  one plus `clinicalStage` on each report, and nothing else.
- `<disease id>/disease_drug_reports/<same names>.*`: a probe-only question
  about the same entries. Moonlight does not ask it. It shows more about each
  report than its link: `source`, `provider`, `origin`, `clinicalStage`,
  `title`, and `diseases { diseaseFromSource }` (the words the source itself
  used for the disease). Asked once.

What the probe found

- An approved medicine's links are `clinicalReports[].url` on its rows in
  `disease.drugAndClinicalCandidates.rows`. Every saved report has a `url`.
- Every report whose `source` is `PMDA` (52 of them) has the same `url`,
  Japan's general list:
  https://www.pmda.go.jp/english/review-services/reviews/approved-information/drugs/0001.html
  No report from any other source has that `url`.
- A row's reports are a mix: approval records and trials. A trial link is an
  exact record, but it is not proof of approval. `clinicalStage` on the
  report says which it is.
- Atomoxetine, guanfacine, lisdexamfetamine and methylphenidate: their only
  approval report for these three diseases is the PMDA one. Its
  `diseaseFromSource` is `ad` (matched to both Alzheimer disease and atopic
  eczema) or `hd` (matched to Huntington disease).
