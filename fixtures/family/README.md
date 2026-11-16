# fixtures/family: ticket 2.12 probe, saved 2026-11-16 (Open Targets data 26.09)

Live answers, saved as sent, only re-indented. Each `.request.json` is the
exact body that was posted.

- `disease_type.*`: the Disease type's fields. `parents` and `children` are
  the direct ones (lists of Disease). `ancestors` / `descendants` go further.
- `search_*.*`: fetch.py's SEARCH_QUERY for four of the names.
- `<disease id>/family.*`: `disease { id name parents { id name } children { id name } }`.
- `<disease id>/disease_drugs/own_<id>.*`, `parent_<lane>_<id>.*`,
  `child_<lane>_<id>.*`: fetch.py's DISEASE_DRUGS_QUERY, word for word, for
  the disease's own entry and each direct parent and child. The lane number
  is the entry's place in the `parents` / `children` list. Each was asked
  twice (the ask-twice rule) and the kept answer saved.
- `drug_daratumumab_CHEMBL1743007.*`: daratumumab's own list of diseases.
  It is PHASE_3 for AL amyloidosis and PHASE_2 for amyloidosis, not APPROVAL.

The five diseases: MONDO_0019065 amyloidosis, MONDO_0020511 precursor B-cell
acute lymphoblastic leukemia, MONDO_0004980 atopic eczema, MONDO_0015924
pulmonary arterial hypertension, MONDO_0004979 asthma.
