# fixtures/withdrawal_region: ticket 3.19

`entries.json` holds two TEST-ONLY withdrawals.json entries. They are not
real withdrawals and must never be copied into `moonlight/withdrawals.json`.
Their sources are example.org placeholders.

- Emicizumab (CHEMBL3833393) on haemophilia A (MONDO_0010602), region "US"
- Tranexamic acid (CHEMBL877) on haemophilia A (MONDO_0010602), region "EU"

Both cards sit on haemophilia A's main Approved list in the saved answers
the other withdrawal tests use (tests/test_withdrawal_line.py). The real
entries for the "region" field come with ticket 2.59.
