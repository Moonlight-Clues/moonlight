# fixtures/withdrawal_reports: saved answers for ticket 2.22

Copied, not changed, from the branch `probe-baseline`, folder
`fixtures/probe_p5/responses/` (night order 1, probe P5, saved live on
2026-11-21, Open Targets data 26.09). Read that folder's `REPORT.md` for how
they were asked. Only the files the tests of ticket 2.22 need are here, in
the layout of `fixtures/narrower_box/`: filed by question, then by the id
asked about. Every file is byte for byte the probe's file under a new name.
The probe's `responses/index.jsonl` says which probe file answers which
question.

One disease, with a whole search:

- MONDO_0010602 hemophilia A (4 parents, 4 children)

For it:

- `disease/MONDO_0010602.response.json`: fetch.py's DISEASE_QUERY.
- `associated_targets/MONDO_0010602.response.json`: TARGETS_QUERY, top 25.
- `family/MONDO_0010602.response.json`: FAMILY_QUERY.
- `disease_drugs/<disease id>.response.json`: DISEASE_DRUGS_QUERY for the
  disease's own entry and for every direct parent and child (9 files).
- `target_drugs/<protein id>.response.json`: TARGET_DRUGS_QUERY for each of
  the 25 proteins.

There are no `.request.json` files. The probe saved the answers and, in its
index, the variables of each question. It did not save the request bodies.

Kashish's example for ticket 2.22 is in `disease_drugs/MONDO_0010602`:
octocog alfa (CHEMBL4297873) has three reports whose `clinicalStage` is
`WITHDRAWAL`. Valoctocogene roxaparvovec (CHEMBL4297579, Roctavian) has none.
