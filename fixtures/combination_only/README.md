# fixtures/combination_only: saved answers for ticket 3.15

Saved live from Open Targets on 2026-11-25 (data 26.09, see `version.*`),
as sent. Each question is saved as `<name>.request.json` (the POST body)
and `<name>.response.json` (the answer).

- `search_cystic_fibrosis.*`: fetch.py's SEARCH_QUERY for "cystic fibrosis".
  The first match is MONDO_0009061 cystic fibrosis.
- `disease_drugs_MONDO_0009061.*`: fetch.py's DISEASE_DRUGS_QUERY for it.
- `search_<medicine>.*`: a drug search for lumacaftor, tezacaftor and
  elexacaftor.
- `drug_<id>.*`: the drug record (id, name, maximumClinicalStage) for each.

They confirm the three ids of moonlight/combination_only.json:
lumacaftor CHEMBL2103870, tezacaftor CHEMBL3544914, elexacaftor CHEMBL4298128.
