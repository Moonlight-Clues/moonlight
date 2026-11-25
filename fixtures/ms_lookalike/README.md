# fixtures/ms_lookalike: saved answers for ticket 3.14

Asked live on 2026-11-25, Open Targets data 26.09 (`data_version.*`).
Every search, disease and family question is fetch.py's own question,
word for word (SEARCH_QUERY with size 10, DISEASE_QUERY, FAMILY_QUERY).
Nothing here was edited by hand.

## What they show

- `search/multiple_sclerosis.*`: the first hit is EFO_0803536,
  "multiple sclerosis symptom measurement", groups phenotype, immune
  system disorder, measurement, nervous system disorder. "multiple
  sclerosis" is on its exact "also called" list. No other hit is named
  "multiple sclerosis".
- `disease/MONDO_0005301.*`, `disease/EFO_0003885.*`: `disease` is null.
- `search/mondo_0005301.*`, `search/efo_0003885.*`: no hits.
- `map_ids.*`: `mapIds` finds nothing for the two ids either, and maps the
  words "multiple sclerosis" to EFO_0803536.
- `old_ids/EFO_0803536.*`: `obsoleteTerms` is MONDO_0005301 and
  EFO_0003885, and `dbXRefs` is MONDO:0005301. It has 6,347 linked
  proteins and 279 medicines on its own list. So in 26.09 this entry is
  Open Targets' record for multiple sclerosis, under a measurement name.
- `disease/EFO_0803536.*`: its description is Open Targets' description
  of a measurement ("Quantification of some aspect of multiple sclerosis
  symptoms ...").
- `family/*`: EFO_0803536's parents include EFO_0001444 "measurement" and
  four disease groups. Its children are MONDO_0005284 (chronic
  progressive MS) and MONDO_0005314 (relapsing-remitting MS).
- `old_ids/MONDO_0004979.*` and `disease/EFO_0000270.*`: asthma's old id
  EFO_0000270 is on asthma's `obsoleteTerms`, and asking for it directly
  also gives null. Old ids failing is not only a multiple sclerosis thing.
- `old_ids/MONDO_0005284.*`, `old_ids/MONDO_0005314.*`: the MS kinds,
  with their own old ids.
- `disease_fields.*`: the live list of fields on Disease, where
  `obsoleteTerms` and `dbXRefs` were read.
- `search/*` (the rest): ordinary searches whose Open Targets answers hold
  "measurement" or "symptom" look-alike entries (asthma, migraine,
  schizophrenia, COPD, autism, heart failure and others). In every one of
  them today's search already puts the real disease first.
  `search/asthma.*` holds the same hits, in the same order, as
  `fixtures/probe_p2/search/asthma.*` (16 Nov).
