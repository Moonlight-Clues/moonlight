# fixtures/sickle_cell: ticket 3.19

Live Open Targets answers for sickle cell disease, saved as sent on
2026-11-25, Open Targets data 26.09.

**The disease id.** `MONDO_0011382`. It is the first hit, named "sickle cell
disease", of fetch.py's SEARCH_QUERY for the text "sickle cell disease"
(size 5), asked live on the same day.

**How they were saved.** `/api/clues?disease_id=MONDO_0011382` was asked once
through the api, with an empty notebook (MOONLIGHT_CACHE_DIR set to a new
folder) and the Firestore cache switched off, so every question went to
Open Targets. Each answer fetch._post_json returned was written here, in
the layout of `fixtures/withdrawal_reports/`, filed by question, then by the
id asked about:

- `disease/MONDO_0011382.response.json`: DISEASE_QUERY.
- `associated_targets/MONDO_0011382.response.json`: TARGETS_QUERY.
- `family/MONDO_0011382.response.json`: FAMILY_QUERY.
- `disease_drugs/<disease id>.response.json`: DISEASE_DRUGS_QUERY for the
  disease's own entry and its parents and children (4 files).
- `target_drugs/<protein id>.response.json`: TARGET_DRUGS_QUERY for each of
  the 25 proteins.

The files are JSON with sorted keys; no value was changed. There are no
`.request.json` files.

`clues_MONDO_0011382.json` is the page the api sent from those live answers,
with the hand-written lists of main at ac2024a. Asked again from the saved
files (tests/test_withdrawal_region_3_19.py), the answer is the same, letter
for letter.

On that page voxelotor (CHEMBL4101807) and crizanlizumab (CHEMBL4297734)
carry the database's withdrawal line. The tests of ticket 3.19 use only
test-only withdrawals entries for hydroxyurea, glutamine and deferiprone;
none of them is real.
