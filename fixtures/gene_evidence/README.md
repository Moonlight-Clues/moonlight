# fixtures/gene_evidence: saved answers for ticket 3.1

Four whole searches, asked live on 2026-11-25 (Open Targets data 26.09)
with fetch.py's own questions, word for word, after ticket 3.1 added
`datatypeScores { id score }` to each row of the proteins question
(TARGETS_QUERY) and `therapeuticAreas { id }` to its disease:

- MONDO_0007739 Huntington disease
- MONDO_0005148 type 2 diabetes mellitus
- MONDO_0019100 neuromyelitis optica (its clue genes are often linked by
  research papers alone)
- MONDO_0015924 pulmonary arterial hypertension (CPS1 is linked by
  `genetic_literature` only)

and one proteins answer alone, for a cancer:

- `associated_targets/MONDO_0007254.*` breast cancer. Its therapeutic areas
  include MONDO_0045024 ("cancer or benign tumor").

Every answer is saved as fetch.py kept it (the "which medicines?" questions
asked twice, the fuller answer kept). The `target_drugs` answers are saved
without indentation, because they are large. Filed by question, then by the
id asked about, like `fixtures/protein_sentence/`:

- `disease/<disease id>.*`: DISEASE_QUERY.
- `family/<disease id>.*`: FAMILY_QUERY.
- `associated_targets/<disease id>.*`: TARGETS_QUERY, top 25, WITH
  `datatypeScores` on each row.
- `disease_drugs/<disease id>.*`: DISEASE_DRUGS_QUERY, for each disease's
  own list and its parents' and children's lists.
- `target_drugs/<protein id>.*`: TARGET_DRUGS_QUERY.

What the answers say about `datatypeScores`

- The ids seen are `genetic_association`, `somatic_mutation`,
  `animal_model`, `affected_pathway`, `rna_expression`, `literature`,
  `genetic_literature` (counted as `genetic_association`, decision of
  25 Nov) and `clinical` (the medicine itself, ignored; the ticket calls it
  `known_drug`, a name this release does not send).
- None of the four whole searches is a cancer, so `somatic_mutation` is
  never named for them (decision of 25 Nov).
- A kind with no evidence is left out of the list, not sent as zero.
