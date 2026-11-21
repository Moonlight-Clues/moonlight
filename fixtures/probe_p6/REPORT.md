# Night order 2: eight key diseases (probe P6)

Read-only study, run 21 Nov 2026. Nothing in `moonlight/`, `web/` or `tests/` was changed. Every number below was counted by `analyse.py` from saved files. **Nothing here is labelled right or wrong.** The same numbers are in `baseline.json`, one object per disease, so a later night can diff against it.

## What was done

- Open Targets data version: **26.09**. Asked 2026-11-21T16:23:30Z to 2026-11-21T17:42:50Z (UTC).
- Diseases studied: **9**. 6 of the 8 names asked in night order 2, each id found with Moonlight's own search (section 0). Then, in night order 2b, three ids Kashish gave: `EFO_1000642`, which Open Targets calls "hemochromatosis"; `MONDO_0015129`, which Open Targets calls "chronic primary adrenal insufficiency"; `HP_0410149`, which Open Targets calls "Drug-induced anaphylaxis".
- Moonlight's code: commit `06b8eb6` (the last change to `moonlight/` or `web/` on `main`). For each disease the probe ran the same functions, in the same order, as `moonlight/api.py`'s `_find`: `fetch_disease`, `fetch_targets` (top 25), `engine.find_clues`, `fetch_approved`, `fetch_withdrawn`, `engine.fetch_neighbours`, then `api._Found` (which calls `engine.sort_into_tabs`). The cards were then checked against what `api.clues()` itself answers: same cards, same order, same links, same opposite-way lines. Diseases where they differed: **0**.
- Requests to Open Targets: **492** (372 target_drugs, 82 disease_drugs, 9 search, 9 disease, 9 targets, 9 family, 2 data_version), one at a time, at least one second apart. Different raw answers saved under `responses/`: 264. `responses/index.jsonl` has one line per request and names the file holding its answer. Times Open Targets refused or the network failed: **0**. Answers carrying an error: 0.
- Source links: **506** different links on 642 cards. Each was asked once (HEAD, then GET if HEAD was refused; GET was needed for 0). 614 requests in all, counting redirect hops and tries after "slow down", from 2026-11-21T16:25:23Z to 2026-11-21T17:43:27Z. Every link's line is in `links.jsonl`.

## Summary table

One row per disease. Column names:

- **Disease**: the name Open Targets gives the entry, and its id.
- **Cards**: Approved main list / narrower-disease box / wider-group box / In trials / New clues.
- **Links**: different source links on the disease's cards / of them dead (404, 410 or DNS failure) / cards with no link at all.
- **Withdrawn**: main-list Approved cards with a WITHDRAWAL report: that also have an APPROVAL report / that have none.
- **Trials**: medicines Open Targets lists in trials for the disease / shown in In trials (of them on that list) / listed and not shown, by rule: not approved elsewhere / not on a top-25 protein / other.
- **Proof**: main-list Approved cards in probe_p3's groups A / B / C / D / E / F, then N (not on the disease's own list).
- **Opposite**: cards opposite to the Approved medicines on a one-way protein, counted probe_p4's way: New clues / In trials.
- **Unknown**: cards with at least one "unknown" direction: Approved main list / In trials / New clues.

### Table 1. The six diseases found by search (night order 2)

| Disease | Cards (A / narrower / wider / T / N) | Links (different / dead / cards with none) | Withdrawn (with / without approval report) | Trials (listed / shown (on list) / not approved elsewhere / not top-25 / other) | Proof (A / B / C / D / E / F / N) | Opposite (N / T) | Unknown (A / T / N) |
|---|---|---|---|---|---|---|---|
| **THESE 6 TOGETHER** | 10 / 1 / 88 / 41 / 402 | 474 / 0 / 0 | 0 / 0 | 207 / 41 (41) / 52 / 114 / 0 | 7 / 2 / 1 / 0 / 0 / 0 / 0 | 36 / 0 | 0 / 3 / 32 |
| sclerosing cholangitis (MONDO_0018646) | 0 / 0 / 1 / 5 / 17 | 23 / 0 / 0 | 0 / 0 | 46 / 5 (5) / 16 / 25 / 0 | 0 / 0 / 0 / 0 / 0 / 0 / 0 | 0 / 0 | 0 / 0 / 1 |
| chronic interstitial cystitis (EFO_1000869) | 2 / 0 / 1 / 7 / 127 | 132 / 0 / 0 | 0 / 0 | 38 / 7 (7) / 6 / 25 / 0 | 1 / 0 / 1 / 0 / 0 / 0 / 0 | 0 / 0 | 0 / 1 / 25 |
| primary biliary cholangitis (MONDO_0005388) | 2 / 0 / 0 / 7 / 16 | 23 / 0 / 0 | 0 / 0 | 43 / 7 (7) / 10 / 26 / 0 | 0 / 2 / 0 / 0 / 0 / 0 / 0 | 0 / 0 | 0 / 0 / 1 |
| neurofibromatosis type 1 (MONDO_0018975) | 2 / 0 / 0 / 4 / 55 | 60 / 0 / 0 | 0 / 0 | 36 / 4 (4) / 7 / 25 / 0 | 2 / 0 / 0 / 0 / 0 / 0 / 0 | 0 / 0 | 0 / 0 / 0 |
| dermatomyositis (MONDO_0016367) | 3 / 1 / 85 / 18 / 95 | 188 / 0 / 0 | 0 / 0 | 43 / 18 (18) / 13 / 12 / 0 | 3 / 0 / 0 / 0 / 0 / 0 / 0 | 2 / 0 | 0 / 2 / 2 |
| anaphylaxis (MONDO_0100053) | 1 / 0 / 1 / 0 / 92 | 92 / 0 / 0 | 0 / 0 | 1 / 0 (0) / 0 / 1 / 0 | 1 / 0 / 0 / 0 / 0 / 0 / 0 | 34 / 0 | 0 / 0 / 3 |

### Table 2. The three diseases given by id (night order 2b)

| Disease | Cards (A / narrower / wider / T / N) | Links (different / dead / cards with none) | Withdrawn (with / without approval report) | Trials (listed / shown (on list) / not approved elsewhere / not top-25 / other) | Proof (A / B / C / D / E / F / N) | Opposite (N / T) | Unknown (A / T / N) |
|---|---|---|---|---|---|---|---|
| **THESE 3 TOGETHER** | 3 / 2 / 11 / 1 / 83 | 91 / 0 / 0 | 0 / 0 | 4 / 1 (1) / 2 / 1 / 0 | 2 / 1 / 0 / 0 / 0 / 0 / 0 | 9 / 0 | 0 / 0 / 2 |
| hemochromatosis (EFO_1000642) | 1 / 0 / 6 / 0 / 8 | 13 / 0 / 0 | 0 / 0 | 3 / 0 (0) / 2 / 1 / 0 | 1 / 0 / 0 / 0 / 0 / 0 / 0 | 0 / 0 | 0 / 0 / 1 |
| chronic primary adrenal insufficiency (MONDO_0015129) | 2 / 2 / 5 / 1 / 75 | 79 / 0 / 0 | 0 / 0 | 1 / 1 (1) / 0 / 0 / 0 | 1 / 1 / 0 / 0 / 0 / 0 / 0 | 9 / 0 | 0 / 0 / 1 |
| Drug-induced anaphylaxis (HP_0410149) | 0 / 0 / 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 | 0 / 0 (0) / 0 / 0 / 0 | 0 / 0 / 0 / 0 / 0 / 0 / 0 | 0 / 0 | 0 / 0 / 0 |

Sections 1 to 5 below count **all the diseases of both tables together**, and their per-disease tables have a row for each.

In a TOGETHER row, "different links" counts a link once even when two diseases show it, so it is smaller than the sum of the column. Counted, never named, as on the live site: 396 medicines not approved anywhere (or withdrawn), 4 with an unclear link, and 4 new clues left out by hand (`moonlight/left_out.json`), summed over the diseases.

## 0. SEARCH: how each disease id was found

Moonlight's own search was asked for each name, word for word: `fetch.search_matches`, the Open Targets part of `/api/search`. Gemini's "did you mean" side lane was not called. A name was taken only if the search put **exactly one** entry on top as *exactly what was typed*: the entry's name, or one of its exact "also called" names, is the name asked (Moonlight's own test, `fetch._is_what_was_typed`). Every answer is saved in `responses/search/` and, read out, in `searches.json`.

| Name asked | Matches returned | Exactly what was typed | What was done |
|---|---|---|---|
| primary sclerosing cholangitis | 4 | sclerosing cholangitis (MONDO_0018646) | studied |
| interstitial cystitis | 2 | chronic interstitial cystitis (EFO_1000869) | studied |
| primary biliary cholangitis | 4 | primary biliary cholangitis (MONDO_0005388) | studied |
| neurofibromatosis type 1 | 1 | neurofibromatosis type 1 (MONDO_0018975) | studied |
| Addison's disease | 2 | none | stopped: no entry is exactly what was typed |
| dermatomyositis | 10 | dermatomyositis (MONDO_0016367) | studied |
| hemochromatosis | 10 | hemochromatosis (EFO_1000642); hemochromatosis type 1 (MONDO_0021001) | stopped: more than one entry is exactly what was typed |
| anaphylaxis | 5 | anaphylaxis (MONDO_0100053) | studied |

**Search for the exact words "primary sclerosing cholangitis"**. Matches, in Moonlight's order:

| # | Entry | Id | Exactly what was typed | Shown as (Open Targets' "also called" word) |
|---|---|---|---|---|
| 1 | sclerosing cholangitis | MONDO_0018646 | yes | primary sclerosing cholangitis |
| 2 | adenocarcinoma of gallbladder and extrahepatic biliary tract | MONDO_0018536 | no |  |
| 3 | Autosomal recessive hyper-IgE syndrome | Orphanet_169446 | no |  |
| 4 | immunodeficiency 92 | MONDO_0030498 | no |  |

**Search for the exact words "interstitial cystitis"**. Matches, in Moonlight's order:

| # | Entry | Id | Exactly what was typed | Shown as (Open Targets' "also called" word) |
|---|---|---|---|---|
| 1 | chronic interstitial cystitis | EFO_1000869 | yes | Interstitial cystitis |
| 2 | lower urinary tract symptom | EFO_0008008 | no |  |

**Search for the exact words "primary biliary cholangitis"**. Matches, in Moonlight's order:

| # | Entry | Id | Exactly what was typed | Shown as (Open Targets' "also called" word) |
|---|---|---|---|---|
| 1 | primary biliary cholangitis | MONDO_0005388 | yes |  |
| 2 | adenocarcinoma of gallbladder and extrahepatic biliary tract | MONDO_0018536 | no |  |
| 3 | sclerosing cholangitis | MONDO_0018646 | no |  |
| 4 | hepatobiliary disorder | MONDO_0002515 | no |  |

**Search for the exact words "neurofibromatosis type 1"**. Matches, in Moonlight's order:

| # | Entry | Id | Exactly what was typed | Shown as (Open Targets' "also called" word) |
|---|---|---|---|---|
| 1 | neurofibromatosis type 1 | MONDO_0018975 | yes |  |

**Search for the exact words "Addison's disease"**. Matches, in Moonlight's order:

| # | Entry | Id | Exactly what was typed | Shown as (Open Targets' "also called" word) |
|---|---|---|---|---|
| 1 | autoimmune polyendocrine syndrome type 1 | MONDO_0009411 | no |  |
| 2 | pernicious anemia | MONDO_0008228 | no |  |

**Search for the exact words "dermatomyositis"**. Matches, in Moonlight's order:

| # | Entry | Id | Exactly what was typed | Shown as (Open Targets' "also called" word) |
|---|---|---|---|---|
| 1 | dermatomyositis | MONDO_0016367 | yes |  |
| 2 | juvenile dermatomyositis | MONDO_0008054 | no |  |
| 3 | clinically amyopathic dermatomyositis | EFO_0008532 | no |  |
| 4 | adult dermatomyositis | MONDO_0001907 | no |  |
| 5 | Scleroderma Polymyositis Overlap Syndrome | EFO_1001994 | no |  |
| 6 | rheumatic disorder | MONDO_0005554 | no |  |
| 7 | autoinflammatory syndrome | MONDO_0019751 | no |  |
| 8 | type 1 interferonopathy | MONDO_0700264 | no |  |
| 9 | autoinflammatory syndrome of childhood | MONDO_0957018 | no |  |
| 10 | type 1 interferonopathy of childhood | MONDO_0957408 | no |  |

**Search for the exact words "hemochromatosis"**. Matches, in Moonlight's order:

| # | Entry | Id | Exactly what was typed | Shown as (Open Targets' "also called" word) |
|---|---|---|---|---|
| 1 | hemochromatosis | EFO_1000642 | yes |  |
| 2 | hemochromatosis type 1 | MONDO_0021001 | yes | hemochromatosis |
| 3 | hereditary hemochromatosis | MONDO_0006507 | no |  |
| 4 | hemochromatosis type 2 | MONDO_0019257 | no |  |
| 5 | Rare hereditary hemochromatosis | Orphanet_220489 | no |  |
| 6 | hemochromatosis type 2A | MONDO_0011216 | no |  |
| 7 | neonatal hemochromatosis | MONDO_0009275 | no |  |
| 8 | hemochromatosis type 5 | MONDO_0014225 | no |  |
| 9 | hemochromatosis type 3 | MONDO_0011417 | no |  |
| 10 | hemochromatosis type 4 | MONDO_0011631 | no |  |

**Search for the exact words "anaphylaxis"**. Matches, in Moonlight's order:

| # | Entry | Id | Exactly what was typed | Shown as (Open Targets' "also called" word) |
|---|---|---|---|---|
| 1 | anaphylaxis | MONDO_0100053 | yes |  |
| 2 | Drug-induced anaphylaxis | HP_0410149 | no |  |
| 3 | idiopathic anaphylaxis | MONDO_0100054 | no |  |
| 4 | non-allergic anaphylaxis | EFO_0020918 | no |  |
| 5 | Exercise induced anaphylaxis | HP_0410139 | no |  |

**Search for the exact words "anaphylaxis"** (saved as asked; not a disease choice). Matches, in Moonlight's order:

| # | Entry | Id | Exactly what was typed | Shown as (Open Targets' "also called" word) |
|---|---|---|---|---|
| 1 | anaphylaxis | MONDO_0100053 | yes |  |
| 2 | Drug-induced anaphylaxis | HP_0410149 | no |  |
| 3 | idiopathic anaphylaxis | MONDO_0100054 | no |  |
| 4 | non-allergic anaphylaxis | EFO_0020918 | no |  |
| 5 | Exercise induced anaphylaxis | HP_0410139 | no |  |

**Search for the exact words "drug anaphylaxis"** (saved as asked; not a disease choice). Matches, in Moonlight's order:

| # | Entry | Id | Exactly what was typed | Shown as (Open Targets' "also called" word) |
|---|---|---|---|---|
| 1 | Drug-induced anaphylaxis | HP_0410149 | no |  |
| 2 | anaphylaxis | MONDO_0100053 | no |  |

## 1. LINKS

Every card shows one link, "Source record" (or the words "No source link in the data"). That one link per card is what was asked. Approved cards in the two folded boxes are counted too.

| Tab | Cards | Cards with no link |
|---|---|---|
| Approved (main list) | 13 | 0 |
| Approved: narrower-disease box | 3 | 0 |
| Approved: wider-group box | 99 | 0 |
| In trials | 42 | 0 |
| New clues | 485 | 0 |

| What happened | Different links |
|---|---|
| answered 2xx (after redirects, if any) | 506 |
| **Total** | 506 |

### Dead links by host (404, 410 or DNS failure)

**No link answered 404 or 410, and no DNS failure was met.** `dead_links.csv` is empty.

### Every host, by the last status its links gave

| Host | Links | 200 |
|---|---|---|
| clinicaltrials.gov | 194 | 194 |
| www.whocc.no | 106 | 106 |
| dailymed.nlm.nih.gov | 84 | 84 |
| ttd.idrblab.cn | 79 | 79 |
| www.ema.europa.eu | 34 | 34 |
| www.accessdata.fda.gov | 8 | 8 |
| www.pmda.go.jp | 1 | 1 |

A number is the last HTTP status after following redirects. Words mean no final status was reached. `links_by_status.csv` has one row per link.

### Links that answered 2xx only after a redirect

| Host | Where the redirect ended | Links |
|---|---|---|
| www.whocc.no | atcddd.fhi.no/atc_ddd_index/ | 106 |

## 2. WITHDRAWN

A WITHDRAWAL report is one entry of `clinicalReports` whose `clinicalStage` is `WITHDRAWAL`, on the medicine's rows of the disease's own list (all its forms together). Moonlight does not use these reports: it leaves a medicine out when it carries a `Withdrawn` drug warning, which is a different field.

|  | With an APPROVAL report too | With no APPROVAL report | Cards not on the list (reports not known) |
|---|---|---|---|
| Approved main list | 0 | 0 | 0 |
| The two folded boxes (reports read from the narrower or wider entry's list) | 0 | 0 | 0 |

Every one of them (also in `withdrawn_reports.csv`, with the report links):

| Disease | Where | Medicine | APPROVAL report too | Proof group | WITHDRAWAL report from |
|---|---|---|---|---|---|

## 3. TRIALS

"Listed in trials" means: the medicine (all its forms together) is on the disease's own Open Targets list, and its strongest stage for this disease is a phase word (`PHASE_...` or `EARLY_PHASE_...`). That is the same test Moonlight's filter uses for "being studied".

- Listed in trials, all diseases: **211**. Shown in In trials: **42**, of which 42 are on that list.
- Listed and not shown: **169**.

| Rule that left it out | Medicines |
|---|---|
| not approved elsewhere: and not on a top-25 protein either | 49 |
| not approved elsewhere: on a top-25 protein | 5 |
| not on a top-25 protein | 112 |
| not on a top-25 protein: also withdrawn in some country | 3 |
| **Total** | 169 |

How a rule was chosen, in this order. (1) *Not approved elsewhere*: the stage word says the medicine is not approved for any disease. For a medicine on a top-25 protein that is Moonlight's own finding. For one that is not, only the forms on the disease's list could be looked at. (2) *Not on a top-25 protein*: approved somewhere, but it acts on none of the 25 proteins Moonlight looks at, so Moonlight never meets it. (3) *Other*: everything else, with the detail spelled out. Every medicine, with its rule, is in `trials_missing.csv`.

Every stage word on the lists (medicines, strongest stage for the disease): `PHASE_2` 114, `PHASE_3` 40, `PHASE_1` 23, `UNKNOWN` 22, `PHASE_2_3` 21, `APPROVAL` 14, `PHASE_1_2` 7, `EARLY_PHASE_1` 6.

| Disease | On the list | Listed in trials | Shown in In trials | Shown and listed | Not approved elsewhere | Not on a top-25 protein | Other |
|---|---|---|---|---|---|---|---|
| sclerosing cholangitis | 47 | 46 | 5 | 5 | 16 | 25 | 0 |
| chronic interstitial cystitis | 47 | 38 | 7 | 7 | 6 | 25 | 0 |
| primary biliary cholangitis | 50 | 43 | 7 | 7 | 10 | 26 | 0 |
| neurofibromatosis type 1 | 38 | 36 | 4 | 4 | 7 | 25 | 0 |
| dermatomyositis | 48 | 43 | 18 | 18 | 13 | 12 | 0 |
| anaphylaxis | 10 | 1 | 0 | 0 | 0 | 1 | 0 |
| hemochromatosis | 4 | 3 | 0 | 0 | 2 | 1 | 0 |
| chronic primary adrenal insufficiency | 3 | 1 | 1 | 1 | 0 | 0 | 0 |
| Drug-induced anaphylaxis | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

## 4. PROOF

probe_p3's groups, from the APPROVAL reports on the medicine's rows of the list:

- **A**: at least one approval report from DailyMed, FDA or EMA
- **B**: approval reports only from TTD
- **C**: approval reports only from PMDA
- **D**: approval reports only from ATC
- **E**: no APPROVAL report at all
- **F**: anything else
- **N**: the card's medicine is not on the list(s) at all, so it has no reports to group

| Group | Approved main list | Share | The two folded boxes | Share |
|---|---|---|---|---|
| A | 9 | 69.2% | 27 | 26.5% |
| B | 3 | 23.1% | 4 | 3.9% |
| C | 1 | 7.7% | 6 | 5.9% |
| D | 0 | 0.0% | 64 | 62.7% |
| E | 0 | 0.0% | 0 | 0.0% |
| F | 0 | 0.0% | 1 | 1.0% |
| N | 0 | 0.0% | 0 | 0.0% |
| Total | 13 | 100.0% | 102 | 100.0% |

Moonlight's own lines on Approved cards (main list and boxes): the Japan line on **7** cards, the "no regulator record" line on **72**, a red warning on **0**. Moonlight counts PMDA as a regulator; probe_p3's group A does not, so the two counts are not the same thing.

| Disease | Main list cards | A | B | C | D | E | F | N | Box cards | Box cards outside A |
|---|---|---|---|---|---|---|---|---|---|---|
| sclerosing cholangitis | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 |
| chronic interstitial cystitis | 2 | 1 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | 0 |
| primary biliary cholangitis | 2 | 0 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| neurofibromatosis type 1 | 2 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| dermatomyositis | 3 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 86 | 72 |
| anaphylaxis | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 |
| hemochromatosis | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 6 | 3 |
| chronic primary adrenal insufficiency | 2 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 7 | 0 |
| Drug-induced anaphylaxis | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

## 5. DIRECTION

Counted probe_p4's way. A protein is **one-way** for a disease if every main-list Approved medicine with an up or down direction on it points the same way, **both-ways** if they disagree. A card is one medicine.

|  | New clues | In trials |
|---|---|---|
| cards in total | 485 | 42 |
| cards pointing OPPOSITE to the Approved medicines on a one-way protein | 45 | 0 |
| cards pointing the SAME way on a one-way protein | 102 | 1 |
| cards with mixed or unknown direction on a one-way protein | 3 | 0 |
| cards sitting on a both-ways protein | 0 | 0 |
| cards carrying the live site's line "Opposite way to the approved medicines for this disease." | 45 | 0 |

- Diseases with at least one opposite card: **3 of 9**. One-way proteins (disease by disease): 14. Both-ways proteins: 0.
- The live site's line (ticket 3.7) leaves the red-warning Approved cards out before deciding one-way. probe_p4 did not. Where the last row differs from the second row, that is why.

### Unknown and mixed directions on cards

| Tab | Cards | No protein shown | At least one unknown | Every direction unknown | At least one mixed | Card-protein pairs | Pairs unknown | Pairs mixed |
|---|---|---|---|---|---|---|---|---|
| Approved (main list) | 13 | 4 | 0 | 0 | 0 | 19 | 0 | 0 |
| Approved: narrower-disease box | 3 | 0 | 0 | 0 | 0 | 4 | 0 | 0 |
| Approved: wider-group box | 99 | 86 | 0 | 0 | 0 | 16 | 0 | 0 |
| In trials | 42 | 0 | 3 | 3 | 0 | 85 | 19 | 0 |
| New clues | 485 | 0 | 34 | 33 | 0 | 1161 | 78 | 0 |

The action words behind every unknown or mixed pair on a card:

| Direction | Action words from Open Targets | Card-protein pairs |
|---|---|---|
| unknown | MODULATOR | 72 |
| unknown | BINDING AGENT | 7 |
| unknown | RELEASING AGENT | 5 |
| unknown | SUBSTRATE | 5 |
| unknown | PARTIAL AGONIST | 4 |
| unknown | NEGATIVE ALLOSTERIC MODULATOR | 2 |
| unknown | DEGRADER | 1 |
| unknown | EXOGENOUS GENE | 1 |

| Disease | Approved cards (with a path) | One-way proteins | Both-ways proteins | NC total | NC opp | NC same | NC both | NC line | IT total | IT opp | IT same | IT both | IT line |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| sclerosing cholangitis | 0 (0) | 0 | 0 | 17 | 0 | 0 | 0 | 0 | 5 | 0 | 0 | 0 | 0 |
| chronic interstitial cystitis | 2 (0) | 0 | 0 | 127 | 0 | 0 | 0 | 0 | 7 | 0 | 0 | 0 | 0 |
| primary biliary cholangitis | 2 (1) | 1 | 0 | 16 | 0 | 1 | 0 | 0 | 7 | 0 | 0 | 0 | 0 |
| neurofibromatosis type 1 | 2 (2) | 2 | 0 | 55 | 0 | 2 | 0 | 0 | 4 | 0 | 1 | 0 | 0 |
| dermatomyositis | 3 (3) | 1 | 0 | 95 | 2 | 47 | 0 | 2 | 18 | 0 | 0 | 0 | 0 |
| anaphylaxis | 1 (1) | 9 | 0 | 92 | 34 | 51 | 0 | 34 | 0 | 0 | 0 | 0 | 0 |
| hemochromatosis | 1 (0) | 0 | 0 | 8 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| chronic primary adrenal insufficiency | 2 (2) | 1 | 0 | 75 | 9 | 1 | 0 | 9 | 1 | 0 | 0 | 0 | 0 |
| Drug-induced anaphylaxis | 0 (0) | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

NC = New clues, IT = In trials, opp = opposite on a one-way protein, both = on a both-ways protein, line = carries the live site's opposite-way line.

## Things to know when reading the numbers

Facts about how the night went. None is a judgement.

- **Night order 2b added three diseases by id** (table 2). Kashish gave the ids; the names
  are Open Targets' own. `EFO_1000642` is "hemochromatosis", `MONDO_0015129` is "chronic
  primary adrenal insufficiency" (the one disease id in `moonlight/left_out.json`), and
  `HP_0410149` is "Drug-induced anaphylaxis". No search was asked again for them.
- **Drug-induced anaphylaxis has no cards at all.** Open Targets returned 1 linked protein
  for it (not 25), no medicine acting on that protein was shown, and its own medicine list
  is empty. So every count in its row is 0.
- **Chronic primary adrenal insufficiency: 4 new clues are left out by hand**, as on the
  live site (`moonlight/left_out.json`). Its 75 New clues cards are what is left. The 4 are
  counted, not named.
- **Two of the eight names were not studied in night order 2, as that order says.** "Addison's disease": the
  search put no entry on top as exactly what was typed (its two matches are listed in
  section 0). "hemochromatosis": two entries are exactly what was typed, `hemochromatosis`
  (EFO_1000642) and `hemochromatosis type 1` (MONDO_0021001, which Open Targets also calls
  "hemochromatosis"). I did not choose between them; in night order 2b Kashish chose the first
  (table 2).
- **Two names were found under another database name.** "primary sclerosing cholangitis" is
  an exact "also called" name of the entry `sclerosing cholangitis` (MONDO_0018646), and
  "interstitial cystitis" of `chronic interstitial cystitis` (EFO_1000869). Each was the
  only entry that was exactly what was typed, so by the rule it was studied. The cards are
  for the database entry.
- **"Anaphylaxis" was searched once.** It is both one of the eight names and one of the two
  extra searches. Moonlight kept the first answer in its notebook, so the second time
  nothing was sent. "drug anaphylaxis" was a search of its own. Both are in section 0.
- **The same scripts as probe_p5**, copied into this folder. Only the choice of diseases
  (search instead of a list) and this report's search section are new. probe_p5's folder
  was not touched.
- **Open Targets was asked each "which medicines?" question twice**, and a third time if the
  two answers differed, because that is what Moonlight's own code does.
- **One host said "slow down".** `www.ema.europa.eu` answered 429 twice during the link check.
  Each time the script waited a minute, doubled its gap for that host and asked that link
  again. Every link was finished. Open Targets never refused.
- **A card shows one link.** Only that link was asked. A link shown by cards of several
  diseases was asked once.

## Things I did not verify

- **Whether the entry the search found is the disease Kashish meant.** The id was taken by
  Moonlight's own rule only. I did not judge whether `sclerosing cholangitis` is the right
  entry for "primary sclerosing cholangitis", or `chronic interstitial cystitis` for
  "interstitial cystitis".
- **Gemini's "did you mean".** The live search page also asks Gemini for suggestions. That
  side lane was not called, so this study does not show what suggestions a visitor would see
  for these words.
- **Whether a link that answers 200 shows the right page, or any real page.** I only read the
  status. probe_p5 asked one made-up link per host (its `link_controls.jsonl`):
  ClinicalTrials.gov, TTD and the ATC site answered 200 for a link that cannot exist, and
  DailyMed sent it to its front page. That check was not repeated tonight. So "0 dead" means
  "no 404, 410 or DNS failure", not "every link works".
- **What a person's browser would see.** The links were asked from this session's machine,
  through its proxy, with a plain program.
- **Whether any withdrawal, approval, trial, proof group or direction is right or wrong.** I
  cannot tell, and nothing here is labelled so.
- **Whether a medicine "not approved elsewhere" is truly approved nowhere.** For a medicine on
  none of the top 25 proteins, only the forms on the disease's own list could be looked at.
- **The live site.** Moonlight's site was not called. The cards were built by the repo's code
  at the commit named above, and matched what `api.clues()` returns when run here, for all nine.
- **Open Targets' completeness**, and any disease outside these nine.
- **The tests.** No code under `moonlight/`, `web/` or `tests/` was touched. The test suite
  was run once at the end only to see that the new folder breaks nothing.
