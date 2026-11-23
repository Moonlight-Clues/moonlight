# fixtures/new_in_trials: saved answers for ticket 2.24

One disease, with a whole search:

- MONDO_0016971 limb-girdle muscular dystrophy (1 parent, 2 children)

Copied, not changed, from the branch `probe-lgmd`, folder
`fixtures/probe_p10/opentargets/` (study P10, saved live on 2026-11-23,
Open Targets data 26.09):

- `family/MONDO_0016971.*`: from the probe's `family/`.
- `associated_targets/MONDO_0016971.*`: from the probe's `top_targets/`, top 25.
- `disease_drugs/MONDO_0016971.*`, `MONDO_0015151.*`, `MONDO_0015152.*`: the
  disease's own list and its two children's lists (both empty).
- `target_drugs/<protein id>.*`: one for each of the 25 proteins.

The probe asked wider questions than fetch.py does, so these answers hold
more fields than Moonlight reads (for example the parent's and the tablet
forms' own `maximumClinicalStage`). Moonlight's question is not changed and
those extra fields are never read.

Two answers the probe did not save. They were asked live on 2026-11-23
(the same day, the same data 26.09), each twice with the same answer, with
fetch.py's own questions word for word:

- `disease/MONDO_0016971.*`: DISEASE_QUERY (the description and names).
- `disease_drugs/MONDO_0016106.*`: DISEASE_DRUGS_QUERY for the one parent,
  progressive muscular dystrophy. Its list is empty.
