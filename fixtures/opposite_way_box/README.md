# fixtures/opposite_way_box: saved answers for ticket 2.28

One disease, with a whole search: MONDO_0004691 autosomal dominant
polycystic kidney disease, ADPKD (2 parents, 6 children). Asked live on
2026-11-23 (Open Targets data 26.09) with fetch.py's own questions, word
for word. Every answer is saved as sent. The `target_drugs` answers are
saved without indentation, because they are large. The "which medicines?"
questions were asked the way fetch.py asks them (twice, the fullest answer
kept).

Filed by question, then by the id asked about, like
`fixtures/approvals_by_hand/`:

- `disease/<disease id>.*`: DISEASE_QUERY.
- `family/<disease id>.*`: FAMILY_QUERY.
- `associated_targets/<disease id>.*`: TARGETS_QUERY, top 25.
- `disease_drugs/<disease id>.*`: DISEASE_DRUGS_QUERY, for the disease's
  own list and its parents' and children's lists.
- `target_drugs/<protein id>.*`: TARGET_DRUGS_QUERY.

Not saved again: 1 answer that `fixtures/narrower_box/` already holds,
letter for letter the same as the live answer of 2026-11-23. The tests read
it from there:

- `target_drugs`: ENSG00000185379, one of ADPKD's 25 proteins.

So this folder holds 36 answers: 1 + 1 + 1, 9 lists and 24 proteins.

- `clues_before_2.28_MONDO_0004691.json`: what `/api/clues` on main
  (7eb4cd4) answered for this page from these saved answers, before the
  ticket. It is letter for letter what main's code answered from the live
  API the same day.

What the answers say about the example

- The main Approved list holds one medicine, CHEMBL344159 TOLVAPTAN. It
  turns the protein AVPR2 down. So AVPR2 is a one-way protein: down.
- Seven new clues act on AVPR2. Four turn it up, and carry "Opposite way to
  the approved medicines for this disease.": CHEMBL1429 DESMOPRESSIN,
  CHEMBL373742 VASOPRESSIN, CHEMBL2108986 ARGIPRESSIN TANNATE and
  CHEMBL1200690 LYPRESSIN. They are numbers 1, 3, 5 and 6 of the 42 new
  clues.
- CHEMBL2135460 TERLIPRESSIN (number 2) turns AVPR2 "unknown". CHEMBL1755
  CONIVAPTAN (number 4) and CHEMBL420762 MOZAVAPTAN (number 7) turn it
  down. None of the three carries the line.
