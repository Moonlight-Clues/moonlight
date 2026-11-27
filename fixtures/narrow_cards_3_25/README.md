# fixtures/narrow_cards_3_25: saved answers for ticket 3.25

Open Targets answers for four whole searches, saved live on 2026-11-27 by
calling Moonlight's own `fetch.py` questions (nothing added or changed; only
the JSON was written on one line to save space):

- MONDO_0005105 melanoma
- MONDO_0018646 sclerosing cholangitis (the database's page that "primary
  sclerosing cholangitis" opens, see `moonlight/disease_search.py`)
- MONDO_0005148 type 2 diabetes mellitus
- MONDO_0008383 rheumatoid arthritis

Folders: `disease/`, `family/`, `associated_targets/`, `disease_drugs/` (one
file per disease) and `target_drugs/` (one per protein, shared by the four).
Used only by `tests/test_long_names_3_25.py`, which replaces
`fetch._post_json` with these files. No network.
