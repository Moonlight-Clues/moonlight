# fixtures/more_in_trials: saved answers for ticket 2.21

Copied, not changed, from the branch `probe-key-diseases`, folder
`fixtures/probe_p6/responses/` (night order 2, saved live on 2026-11-21,
Open Targets data 26.09). That folder's `index.jsonl` says which question
each answer belongs to. Only the files the tests of ticket 2.21 need are
here, filed by question, then by the id asked about.

One disease, with a whole search:

- MONDO_0005388 primary biliary cholangitis (2 parents, no children)

- `disease/<disease id>.*`: fetch.py's DISEASE_QUERY.
- `associated_targets/<disease id>.*`: TARGETS_QUERY, top 25.
- `family/<disease id>.*`: FAMILY_QUERY.
- `disease_drugs/<disease id>.*`: DISEASE_DRUGS_QUERY for the disease's own
  entry and for its two parents.
- `target_drugs/<protein id>.*`: TARGET_DRUGS_QUERY for each of the 25
  proteins.

`clues_before_2.21.json` is not an Open Targets answer. It is what the code
on main (commit 7734f6f, before ticket 2.21) answers on `/api/clues` for
this disease, worked out from the saved answers here. The "every old key
answers what it answered before" test compares today's answer with it.

Breast cancer (365 box cards) is not here: the tests read it from
`fixtures/narrower_box/`.
