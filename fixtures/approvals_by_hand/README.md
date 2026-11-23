# fixtures/approvals_by_hand: saved answers for ticket 2.26

Two diseases, each with a whole search. Asked live on 2026-11-23 (Open
Targets data 26.09) with fetch.py's own questions, word for word. Every
answer is saved as sent. The `target_drugs` answers are saved without
indentation, because they are large. The two "which medicines?" questions
were asked the way fetch.py asks them (twice, the fullest answer kept), and
every repeat gave the same answer.

- MONDO_0003233 essential tremor (3 parents, 5 children)
- MONDO_0005364 Graves disease (3 parents, 2 children)

Filed by question, then by the id asked about, like `fixtures/new_in_trials/`:

- `disease/<disease id>.*`: DISEASE_QUERY.
- `family/<disease id>.*`: FAMILY_QUERY.
- `associated_targets/<disease id>.*`: TARGETS_QUERY, top 25.
- `disease_drugs/<disease id>.*`: DISEASE_DRUGS_QUERY, for the disease's
  own list and its parents' and children's lists.
- `target_drugs/<protein id>.*`: TARGET_DRUGS_QUERY.

Not saved again: 23 answers that `fixtures/no_regulator/` already holds,
letter for letter the same as the live answers of 2026-11-23. The tests
read those from there:

- `target_drugs`: 4 of essential tremor's 25 proteins and 16 of Graves
  disease's 25.
- `disease_drugs`: MONDO_0005395 (movement disorder, a parent of essential
  tremor), MONDO_1060200 and MONDO_0001104 (two parents of Graves disease).

So this folder holds 48 answers: 32 for essential tremor (1 + 1 + 1, 8
lists, 21 proteins) and 16 for Graves disease (1 + 1 + 1, 4 lists, 9
proteins).

- `clues_before_2.26_<disease id>.json`: what `/api/clues` on main answered
  for each page from these saved answers, before the ticket. It is letter
  for letter what the live site's code answered the same day.

What the answers say about the two medicines

- CHEMBL27 PROPRANOLOL is on essential tremor's own list with the stage
  UNKNOWN and one report. It acts on none of the 25 proteins. It has one
  tablet form, CHEMBL1671, with no row on the list. Its only warning is a
  "Black Box Warning", which is not a withdrawal.
- CHEMBL1515 METHIMAZOLE is on Graves disease's own list with the stage
  PHASE_3 and 13 reports. It acts on none of the 25 proteins and has no
  warning.

## Added for ticket 2.30 (second batch)

One more answer, `disease_drugs/MONDO_0005342.response.json`, asked live on
2026-11-23 (Open Targets data 26.09) with DISEASE_DRUGS_QUERY, the way
fetch.py asks it. Saved as sent. Only the disease's own list: no whole
search this time.

- MONDO_0005342 IgA glomerulonephritis (73 medicines). CHEMBL9194 ATRASENTAN
  is on it with the stage PHASE_3 and 5 reports. It has one tablet form,
  CHEMBL2106068, with no row on the list. CHEMBL4594614 SIBEPRENLIMAB is on
  it with the stage PHASE_3 and 5 reports, and the database records it as
  approved for nothing yet. Neither has a warning.

Not saved again: AL amyloidosis (MONDO_0019438). `fixtures/tafamidis_warning/`
already holds its whole search, and its list is letter for letter the live
answer of 2026-11-23. CHEMBL1743007 DARATUMUMAB is on it with the stage
PHASE_3 and 13 reports. No tablet form, no warning.

So this folder now holds 49 answers.
