# fixtures/narrower_box: saved answers for ticket 2.14

Copied, not changed, from the branch `probe-search-and-children`, folder
`fixtures/probe_p2/` (ticket P2, saved live on 2026-11-16, Open Targets
data 26.09). Read that folder's README for how they were asked. Only the
files the tests of ticket 2.14 need are here, in the probe's own layout:
filed by question, then by the id asked about.

Four diseases, each with a whole search:

- MONDO_0004967 acute lymphoblastic leukemia (5 parents, 11 children)
- MONDO_0015924 pulmonary arterial hypertension (1 parent, 6 children)
- MONDO_0004979 asthma (3 parents, 9 children)
- MONDO_0007254 breast cancer (2 parents, 6 children)

For each:

- `disease/<disease id>.*`: fetch.py's DISEASE_QUERY.
- `associated_targets/<disease id>.*`: TARGETS_QUERY, top 25.
- `family/<disease id>.*`: FAMILY_QUERY.
- `disease_drugs/<disease id>.*`: DISEASE_DRUGS_QUERY for the disease's own
  entry and for every direct parent and child.
- `target_drugs/<protein id>.*`: TARGET_DRUGS_QUERY for each of the 25
  proteins.

Amyloidosis, atopic eczema and Pre-B ALL are not here: ticket 2.14's tests
read them from `fixtures/family/`, where ticket 2.12 saved them.

`approved_tab_before_2.14.json` is not an Open Targets answer. It is what
the code on main (commit 022a7e4, before ticket 2.14) put in the Approved
tab for seven diseases, worked out from the saved answers here and in
`fixtures/family/`: the id and name of every card in the main list and in
the wider-group box, in the order shown. The "nobody goes missing" test
compares today's tab with it.
