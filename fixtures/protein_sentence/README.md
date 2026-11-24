# fixtures/protein_sentence: saved answers for ticket 3.8

One disease, with a whole search: MONDO_0005364 Graves disease. Asked live
on 2026-11-24 (Open Targets data 26.09) with fetch.py's own questions, word
for word, after ticket 3.8 added `functionDescriptions` to the proteins
question (TARGETS_QUERY). Every answer is saved as sent. The `target_drugs`
answers are saved without indentation, because they are large. The "which
medicines?" questions were asked the way fetch.py asks them (twice, the
fullest answer kept). UniProt was not asked.

Filed by question, then by the id asked about, like
`fixtures/opposite_way_box/`:

- `disease/<disease id>.*`: DISEASE_QUERY.
- `family/<disease id>.*`: FAMILY_QUERY.
- `associated_targets/<disease id>.*`: TARGETS_QUERY, top 25, WITH the new
  field `functionDescriptions` on each target.
- `disease_drugs/<disease id>.*`: DISEASE_DRUGS_QUERY, for the disease's
  own list and its parents' and children's lists.
- `target_drugs/<protein id>.*`: TARGET_DRUGS_QUERY.

So this folder holds 34 answers: 1 + 1 + 1, 6 lists and 25 proteins.

What the answers say about the example

- New clues, the first card: CHEMBL1789844 IPILIMUMAB, protein CTLA4.
- CTLA4's first text starts "Inhibitory receptor acting as a major negative
  regulator of T-cell responses (PubMed:11279501, ...). Acts as a decoy
  receptor: ...". Cleaned, the sentence is "Inhibitory receptor acting as a
  major negative regulator of T-cell responses." (77 characters).
- Of the 25 proteins, 21 get a sentence, 3 are longer than 200 characters
  after cleaning and get none (CLNK, NFKB1, PTPN22), and 1 has no text at
  all (C1QTNF6, an empty list).
- The 10 new clues act on five proteins: CTLA4, IGF1R, TSHR, IL2RA and
  TGFB2. All five get a sentence.
