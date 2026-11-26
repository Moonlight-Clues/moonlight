# Ticket T5 fixtures: live Open Targets drug records

Recorded 26 Nov 2026 from https://api.platform.opentargets.org/api/v4/graphql.
Each `<CHEMBL id>.request.json` is the exact POST body; `<CHEMBL id>.response.json`
is the answer as sent. Live field shape: `synonyms` and `tradeNames` are lists
of `{label, source}`; source is "ChEMBL" or "AACT".

Medicines: phenylpropanolamine (CHEMBL61006, salt children), metformin
(CHEMBL1431), imatinib (CHEMBL941), sacubitril (CHEMBL3137301), valsartan
(CHEMBL1069), eslicarbazepine acetate (CHEMBL87992, no parentMolecule, on
salt_parents.json) and eslicarbazepine (CHEMBL315985).
