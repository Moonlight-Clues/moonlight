# fixtures/source_overrides: ticket 3.17

`source_overrides_batch1.csv` is the first batch, given by Product and checked
by MAIN 4 (25 Nov 2026), saved byte for byte as given: 54 rows.

`moonlight/source_overrides.json` holds the same 54 rows, in the same order:
`medicine_id`, `disease_id` and `url` as given, `date` from `label_date`, `note`
from `quote` word for word, and `evidence_file` as given (MAIN 4's answer,
25 Nov). `tests/test_source_overrides.py` checks the two match.
