# Night order 1: the baseline (probe P5)

Read-only study, 21 Nov 2026. Nothing in `moonlight/`, `web/` or `tests/` was changed. Every number below was counted by `analyse.py` from saved files. **Nothing here is labelled right or wrong.** The same numbers are in `baseline.json`, one object per disease, so a later night can diff against it.

## What was done

- Open Targets data version: **26.09**. Asked 2026-11-21T15:05:15Z to 2026-11-21T16:08:47Z (UTC).
- Diseases: **50** of the 50 in `fixtures/probe_p4/diseases.json` (branch `probe-direction`), read with `git show`.
- Moonlight's code: commit `06b8eb6` (the last change to `moonlight/` or `web/` on `main`). For each disease the probe ran the same functions, in the same order, as `moonlight/api.py`'s `_find`: `fetch_disease`, `fetch_targets` (top 25), `engine.find_clues`, `fetch_approved`, `fetch_withdrawn`, `engine.fetch_neighbours`, then `api._Found` (which calls `engine.sort_into_tabs`). The cards were then checked against what `api.clues()` itself answers: same cards, same order, same links, same opposite-way lines. Diseases where they differed: **0**.
- Requests to Open Targets: **2738** (1792 target_drugs, 794 disease_drugs, 50 disease, 50 targets, 50 family, 2 data_version), one at a time, at least one second apart. Different raw answers saved under `responses/`: 1444. `responses/index.jsonl` has one line per request and names the file holding its answer. Times Open Targets refused or the network failed: **1**. Answers carrying an error: 0.
- Source links: **2520** different links on 5403 cards. Each was asked once (HEAD, then GET if HEAD was refused; GET was needed for 0). 2992 requests in all, counting redirect hops and tries after "slow down", from 2026-11-21T15:08:58Z to 2026-11-21T16:09:20Z. Every link's line is in `links.jsonl`.

## Summary table

One row per disease. Column names:

- **Cards**: Approved main list / narrower-disease box / wider-group box / In trials / New clues.
- **Links**: different source links on the disease's cards / of them dead (404, 410 or DNS failure) / cards with no link at all.
- **Withdrawn**: main-list Approved cards with a WITHDRAWAL report: that also have an APPROVAL report / that have none.
- **Trials**: medicines Open Targets lists in trials for the disease / shown in In trials (of them on that list) / listed and not shown, by rule: not approved elsewhere / not on a top-25 protein / other.
- **Proof**: main-list Approved cards in probe_p3's groups A / B / C / D / E / F, then N (not on the disease's own list).
- **Opposite**: cards opposite to the Approved medicines on a one-way protein, counted probe_p4's way: New clues / In trials.
- **Unknown**: cards with at least one "unknown" direction: Approved main list / In trials / New clues.

| Disease | Cards (A / narrower / wider / T / N) | Links (different / dead / cards with none) | Withdrawn (with / without approval report) | Trials (listed / shown (on list) / not approved elsewhere / not top-25 / other) | Proof (A / B / C / D / E / F / N) | Opposite (N / T) | Unknown (A / T / N) |
|---|---|---|---|---|---|---|---|
| **ALL 50 TOGETHER** | 1131 / 143 / 525 / 559 / 3079 | 2520 / 0 / 34 | 67 / 12 | 8244 / 559 (559) / 3745 / 3930 / 10 | 744 / 195 / 57 / 66 / 14 / 55 / 0 | 392 / 25 | 69 / 60 / 203 |
| asthma | 70 / 0 / 0 / 13 / 126 | 199 / 0 / 5 | 4 / 1 | 288 / 13 (13) / 170 / 105 / 0 | 50 / 19 / 0 / 0 / 1 / 0 / 0 | 26 / 2 | 0 / 0 / 2 |
| type 2 diabetes mellitus | 59 / 0 / 44 / 11 / 11 | 111 / 0 / 0 | 9 / 0 | 440 / 11 (11) / 217 / 212 / 0 | 49 / 2 / 6 / 0 / 0 / 2 / 0 | 2 / 2 | 0 / 0 / 0 |
| epilepsy | 54 / 1 / 4 / 3 / 74 | 133 / 0 / 0 | 3 / 0 | 62 / 3 (3) / 28 / 31 / 0 | 22 / 3 / 1 / 13 / 0 / 15 / 0 | 5 / 0 | 2 / 2 / 3 |
| rheumatoid arthritis | 69 / 8 / 61 / 21 / 76 | 215 / 0 / 5 | 2 / 0 | 330 / 21 (21) / 184 / 124 / 1 | 55 / 11 / 2 / 0 / 0 / 1 / 0 | 3 / 0 | 0 / 0 / 1 |
| psoriasis | 43 / 5 / 61 / 15 / 65 | 170 / 0 / 5 | 3 / 0 | 119 / 15 (15) / 63 / 41 / 0 | 36 / 0 / 0 / 7 / 0 / 0 / 0 | 2 / 0 | 1 / 0 / 0 |
| atopic eczema | 41 / 4 / 68 / 26 / 100 | 215 / 0 / 4 | 2 / 0 | 165 / 26 (26) / 77 / 62 / 0 | 24 / 2 / 12 / 2 / 0 / 1 / 0 | 5 / 0 | 2 / 0 / 8 |
| ulcerative colitis | 28 / 0 / 1 / 10 / 100 | 129 / 0 / 0 | 2 / 0 | 182 / 10 (10) / 91 / 80 / 1 | 26 / 1 / 1 / 0 / 0 / 0 / 0 | 2 / 0 | 2 / 1 / 0 |
| osteoporosis | 33 / 2 / 0 / 8 / 50 | 81 / 0 / 4 | 2 / 0 | 55 / 8 (8) / 23 / 24 / 0 | 17 / 12 / 4 / 0 / 0 / 0 / 0 | 10 / 0 | 3 / 2 / 9 |
| gout | 21 / 0 / 37 / 3 / 52 | 103 / 0 / 0 | 3 / 0 | 32 / 3 (3) / 11 / 17 / 1 | 14 / 0 / 2 / 4 / 0 / 1 / 0 | 0 / 0 | 0 / 0 / 2 |
| heart failure | 43 / 28 / 3 / 26 / 113 | 203 / 0 / 1 | 1 / 0 | 196 / 26 (26) / 61 / 108 / 1 | 33 / 9 / 0 / 0 / 0 / 1 / 0 | 10 / 1 | 0 / 0 / 6 |
| atrial fibrillation | 17 / 0 / 28 / 15 / 72 | 131 / 0 / 0 | 2 / 0 | 72 / 15 (15) / 18 / 38 / 1 | 14 / 3 / 0 / 0 / 0 / 0 / 0 | 0 / 0 | 0 / 0 / 6 |
| chronic obstructive pulmonary disease | 29 / 16 / 10 / 14 / 142 | 197 / 0 / 5 | 10 / 0 | 246 / 14 (14) / 120 / 111 / 1 | 22 / 7 / 0 / 0 / 0 / 0 / 0 | 22 / 2 | 0 / 0 / 5 |
| chronic kidney disease | 51 / 2 / 4 / 22 / 49 | 113 / 0 / 0 | 2 / 1 | 235 / 22 (22) / 50 / 162 / 1 | 46 / 1 / 2 / 0 / 2 / 0 / 0 | 5 / 0 | 0 / 0 / 2 |
| hypothyroidism | 8 / 0 / 1 / 0 / 16 | 24 / 0 / 0 | 0 / 0 | 4 / 0 (0) / 0 / 4 / 0 | 6 / 2 / 0 / 0 / 0 / 0 / 0 | 0 / 0 | 0 / 0 / 1 |
| depressive disorder | 33 / 46 / 1 / 31 / 170 | 267 / 0 / 0 | 0 / 1 | 177 / 31 (31) / 40 / 106 / 0 | 4 / 23 / 2 / 0 / 1 / 3 / 0 | 26 / 4 | 2 / 7 / 15 |
| schizophrenia | 45 / 0 / 31 / 15 / 48 | 135 / 0 / 0 | 2 / 3 | 224 / 15 (15) / 91 / 118 / 0 | 25 / 16 / 1 / 0 / 3 / 0 / 0 | 20 / 4 | 6 / 5 / 4 |
| bipolar disorder | 19 / 1 / 2 / 28 / 150 | 197 / 0 / 0 | 1 / 0 | 118 / 28 (28) / 22 / 68 / 0 | 16 / 2 / 0 / 0 / 1 / 0 / 0 | 8 / 1 | 2 / 8 / 16 |
| Parkinson disease | 43 / 0 / 0 / 9 / 94 | 141 / 0 / 0 | 6 / 0 | 239 / 9 (9) / 110 / 120 / 0 | 19 / 4 / 2 / 10 / 0 / 8 / 0 | 48 / 3 | 0 / 3 / 7 |
| Alzheimer disease | 21 / 0 / 5 / 7 / 41 | 70 / 0 / 0 | 2 / 0 | 363 / 7 (7) / 184 / 172 / 0 | 12 / 5 / 4 / 0 / 0 / 0 / 0 | 1 / 0 | 4 / 1 / 4 |
| glaucoma | 39 / 0 / 26 / 1 / 76 | 139 / 0 / 0 | 0 / 0 | 32 / 1 (1) / 8 / 23 / 0 | 11 / 0 / 1 / 21 / 0 / 6 / 0 | 9 / 0 | 0 / 0 / 4 |
| endometriosis | 10 / 0 / 0 / 18 / 82 | 102 / 0 / 0 | 0 / 0 | 61 / 18 (18) / 11 / 31 / 1 | 5 / 1 / 3 / 0 / 0 / 1 / 0 | 12 / 2 | 0 / 1 / 9 |
| tuberculosis | 22 / 7 / 2 / 5 / 62 | 93 / 0 / 0 | 1 / 0 | 102 / 5 (5) / 19 / 78 / 0 | 11 / 0 / 0 / 8 / 0 / 3 / 0 | 0 / 0 | 0 / 0 / 1 |
| malaria | 29 / 0 / 0 / 0 / 97 | 119 / 0 / 0 | 2 / 0 | 44 / 0 (0) / 12 / 32 / 0 | 15 / 6 / 1 / 1 / 0 / 6 / 0 | 1 / 0 | 0 / 0 / 4 |
| breast cancer | 73 / 2 / 5 / 29 / 27 | 121 / 0 / 0 | 0 / 1 | 871 / 29 (29) / 462 / 379 / 1 | 38 / 27 / 5 / 0 / 1 / 2 / 0 | 0 / 0 | 7 / 5 / 3 |
| prostate cancer | 30 / 6 / 3 / 17 / 18 | 74 / 0 / 0 | 0 / 1 | 668 / 17 (17) / 319 / 332 / 0 | 16 / 11 / 1 / 0 / 1 / 1 / 0 | 8 / 4 | 2 / 2 / 0 |
| colorectal cancer | 19 / 3 / 6 / 44 / 23 | 81 / 0 / 0 | 0 / 0 | 681 / 44 (44) / 368 / 269 / 0 | 4 / 11 / 2 / 0 / 0 / 2 / 0 | 2 / 0 | 1 / 3 / 4 |
| lung cancer | 8 / 0 / 0 / 38 / 46 | 81 / 0 / 0 | 0 / 0 | 236 / 38 (38) / 85 / 113 / 0 | 5 / 3 / 0 / 0 / 0 / 0 / 0 | 0 / 0 | 0 / 0 / 5 |
| melanoma | 20 / 2 / 0 / 17 / 8 | 47 / 0 / 0 | 1 / 0 | 547 / 17 (17) / 306 / 224 / 0 | 16 / 4 / 0 / 0 / 0 / 0 / 0 | 0 / 0 | 0 / 0 / 0 |
| chronic myeloid leukemia | 9 / 0 / 4 / 14 / 28 | 55 / 0 / 0 | 2 / 1 | 155 / 14 (14) / 48 / 93 / 0 | 8 / 0 / 0 / 0 / 1 / 0 / 0 | 2 / 0 | 0 / 0 / 0 |
| acute myeloid leukemia | 15 / 7 / 5 / 19 / 21 | 60 / 0 / 0 | 1 / 0 | 532 / 19 (19) / 285 / 228 / 0 | 15 / 0 / 0 / 0 / 0 / 0 / 0 | 1 / 0 | 0 / 0 / 0 |
| cystic fibrosis | 15 / 0 / 15 / 1 / 2 | 31 / 0 / 0 | 1 / 0 | 112 / 1 (1) / 37 / 74 / 0 | 14 / 1 / 0 / 0 / 0 / 0 / 0 | 1 / 0 | 1 / 1 / 0 |
| Duchenne muscular dystrophy | 8 / 0 / 0 / 5 / 68 | 75 / 0 / 0 | 0 / 1 | 50 / 5 (5) / 24 / 21 / 0 | 7 / 0 / 0 / 0 / 1 / 0 / 0 | 5 / 0 | 1 / 1 / 0 |
| spinal muscular atrophy | 4 / 0 / 0 / 0 / 0 | 4 / 0 / 0 | 0 / 0 | 15 / 0 (0) / 7 / 8 / 0 | 3 / 1 / 0 / 0 / 0 / 0 / 0 | 0 / 0 | 1 / 0 / 0 |
| Huntington disease | 5 / 0 / 5 / 6 / 175 | 183 / 0 / 0 | 0 / 0 | 48 / 6 (6) / 19 / 23 / 0 | 1 / 0 / 4 / 0 / 0 / 0 / 0 | 9 / 0 | 1 / 1 / 16 |
| amyotrophic lateral sclerosis | 5 / 0 / 0 / 2 / 23 | 29 / 0 / 0 | 0 / 0 | 166 / 2 (2) / 48 / 116 / 0 | 3 / 0 / 1 / 0 / 0 / 1 / 0 | 0 / 0 | 1 / 0 / 3 |
| Gaucher disease | 6 / 0 / 26 / 0 / 23 | 55 / 0 / 0 | 0 / 0 | 6 / 0 (0) / 3 / 3 / 0 | 5 / 1 / 0 / 0 / 0 / 0 / 0 | 0 / 0 | 0 / 0 / 0 |
| Fabry disease | 4 / 0 / 0 / 1 / 48 | 50 / 0 / 0 | 0 / 0 | 7 / 1 (1) / 6 / 0 / 0 | 4 / 0 / 0 / 0 / 0 / 0 / 0 | 0 / 0 | 1 / 0 / 3 |
| phenylketonuria | 3 / 0 / 0 / 0 / 69 | 64 / 0 / 0 | 0 / 0 | 4 / 0 (0) / 2 / 2 / 0 | 3 / 0 / 0 / 0 / 0 / 0 / 0 | 0 / 0 | 0 / 0 / 8 |
| hemophilia A | 18 / 0 / 11 / 10 / 38 | 73 / 0 / 0 | 1 / 0 | 23 / 10 (10) / 7 / 6 / 0 | 18 / 0 / 0 / 0 / 0 / 0 / 0 | 4 / 0 | 15 / 7 / 7 |
| hemophilia B | 11 / 0 / 15 / 7 / 21 | 46 / 0 / 0 | 0 / 2 | 12 / 7 (7) / 5 / 0 / 0 | 9 / 0 / 0 / 0 / 2 / 0 / 0 | 0 / 0 | 9 / 7 / 10 |
| myasthenia gravis | 12 / 0 / 0 / 3 / 20 | 34 / 0 / 0 | 0 / 0 | 50 / 3 (3) / 15 / 32 / 0 | 10 / 2 / 0 / 0 / 0 / 0 / 0 | 1 / 0 | 1 / 0 / 0 |
| narcolepsy | 5 / 3 / 2 / 3 / 65 | 77 / 0 / 0 | 0 / 0 | 10 / 3 (3) / 4 / 3 / 0 | 3 / 1 / 0 / 0 / 0 / 1 / 0 | 0 / 0 | 2 / 0 / 8 |
| Wilson disease | 4 / 0 / 1 / 0 / 18 | 23 / 0 / 0 | 0 / 0 | 6 / 0 (0) / 4 / 2 / 0 | 4 / 0 / 0 / 0 / 0 / 0 / 0 | 0 / 0 | 0 / 0 / 0 |
| hereditary angioedema | 9 / 0 / 2 / 1 / 61 | 69 / 0 / 0 | 0 / 0 | 4 / 1 (1) / 3 / 0 / 0 | 8 / 1 / 0 / 0 / 0 / 0 / 0 | 9 / 0 | 1 / 0 / 4 |
| acromegaly | 6 / 0 / 0 / 4 / 125 | 130 / 0 / 0 | 1 / 0 | 11 / 4 (4) / 6 / 1 / 0 | 6 / 0 / 0 / 0 / 0 / 0 / 0 | 52 / 0 | 0 / 1 / 18 |
| Cushing syndrome | 3 / 0 / 4 / 2 / 102 | 106 / 0 / 0 | 0 / 0 | 6 / 2 (2) / 4 / 0 / 0 | 3 / 0 / 0 / 0 / 0 / 0 / 0 | 72 / 0 | 0 / 0 / 2 |
| sarcoidosis | 5 / 0 / 0 / 13 / 58 | 69 / 0 / 0 | 0 / 0 | 35 / 13 (13) / 6 / 16 / 0 | 4 / 1 / 0 / 0 / 0 / 0 / 0 | 2 / 0 | 1 / 1 / 2 |
| systemic sclerosis | 4 / 0 / 32 / 2 / 38 | 63 / 0 / 0 | 0 / 0 | 103 / 2 (2) / 31 / 69 / 1 | 3 / 1 / 0 / 0 / 0 / 0 / 0 | 3 / 0 | 0 / 0 / 0 |
| Behcet disease | 2 / 0 / 0 / 10 / 71 | 73 / 0 / 5 | 0 / 0 | 35 / 10 (10) / 5 / 20 / 0 | 1 / 1 / 0 / 0 / 0 / 0 / 0 | 4 / 0 | 0 / 0 / 1 |
| hidradenitis suppurativa | 1 / 0 / 0 / 10 / 17 | 23 / 0 / 0 | 1 / 0 | 65 / 10 (10) / 26 / 29 / 0 | 1 / 0 / 0 / 0 / 0 / 0 / 0 | 0 / 0 | 0 / 1 / 0 |

In the ALL row, "different links" counts a link once even when two diseases show it, so it is smaller than the sum of the column. Counted, never named, as on the live site: 3386 medicines not approved anywhere (or withdrawn), 77 with an unclear link, and 0 new clues left out by hand (`moonlight/left_out.json`), summed over the diseases.

## 1. LINKS

Every card shows one link, "Source record" (or the words "No source link in the data"). That one link per card is what was asked. Approved cards in the two folded boxes are counted too.

| Tab | Cards | Cards with no link |
|---|---|---|
| Approved (main list) | 1131 | 0 |
| Approved: narrower-disease box | 143 | 1 |
| Approved: wider-group box | 525 | 0 |
| In trials | 559 | 1 |
| New clues | 3079 | 32 |

| What happened | Different links |
|---|---|
| answered 2xx (after redirects, if any) | 2520 |
| **Total** | 2520 |

### Dead links by host (404, 410 or DNS failure)

**No link answered 404 or 410, and no DNS failure was met.** `dead_links.csv` is empty.

### Every host, by the last status its links gave

| Host | Links | 200 |
|---|---|---|
| dailymed.nlm.nih.gov | 692 | 692 |
| ttd.idrblab.cn | 576 | 576 |
| clinicaltrials.gov | 540 | 540 |
| www.whocc.no | 461 | 461 |
| www.ema.europa.eu | 218 | 218 |
| www.accessdata.fda.gov | 26 | 26 |
| www.fda.gov | 4 | 4 |
| searchusan.ama-assn.org | 2 | 2 |
| www.pmda.go.jp | 1 | 1 |

A number is the last HTTP status after following redirects. Words mean no final status was reached. `links_by_status.csv` has one row per link.

### Links that answered 2xx only after a redirect

| Host | Where the redirect ended | Links |
|---|---|---|
| dailymed.nlm.nih.gov | dailymed.nlm.nih.gov/dailymed/index.cfm | 2 |
| www.whocc.no | atcddd.fhi.no/atc_ddd_index/ | 461 |

### What these hosts answer for a link that cannot exist

To know what a status means, one made-up link per host was asked as well (not a card link; saved in `link_controls.jsonl`):

| Host | Made-up link | Answer |
|---|---|---|
| clinicaltrials.gov | https://clinicaltrials.gov/study/NCT99999999 | 200 |
| dailymed.nlm.nih.gov | https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=00000000-0000-0000-0000-000000000000 | 200, after a redirect to https://dailymed.nlm.nih.gov/dailymed/index.cfm |
| ttd.idrblab.cn | https://ttd.idrblab.cn/data/drug/details/DZZZZZZ | 200 |
| www.ema.europa.eu | https://www.ema.europa.eu/en/medicines/human/EPAR/not-a-medicine-xyz | 404 |
| www.whocc.no | https://www.whocc.no/atc_ddd_index/?code=Z99ZZ99 | 200, after a redirect to https://atcddd.fhi.no/atc_ddd_index/?code=Z99ZZ99 |
| www.accessdata.fda.gov | https://www.accessdata.fda.gov/drugsatfda_docs/label/2099/000000s000lbl.pdf | 404 |
| searchusan.ama-assn.org | https://searchusan.ama-assn.org/finder/usan/search/NOTAMEDICINEXYZ/relevant/1/ | 200 |

## 2. WITHDRAWN

A WITHDRAWAL report is one entry of `clinicalReports` whose `clinicalStage` is `WITHDRAWAL`, on the medicine's rows of the disease's own list (all its forms together). Moonlight does not use these reports: it leaves a medicine out when it carries a `Withdrawn` drug warning, which is a different field.

|  | With an APPROVAL report too | With no APPROVAL report | Cards not on the list (reports not known) |
|---|---|---|---|
| Approved main list | 67 | 12 | 0 |
| The two folded boxes (reports read from the narrower or wider entry's list) | 7 | 8 | 0 |

Every one of them (also in `withdrawn_reports.csv`, with the report links):

| Disease | Where | Medicine | APPROVAL report too | Proof group | WITHDRAWAL report from |
|---|---|---|---|---|---|
| asthma | Approved (main list) | BITOLTEROL (CHEMBL1201295) | no | E | TTD |
| asthma | Approved (main list) | BUDESONIDE (CHEMBL1370) | yes | A | EMA Human Drugs |
| asthma | Approved (main list) | FLUTICASONE PROPIONATE (CHEMBL1473) | yes | A | EMA Human Drugs |
| asthma | Approved (main list) | FORMOTEROL (CHEMBL1256786) | yes | A | EMA Human Drugs |
| asthma | Approved (main list) | SALMETEROL (CHEMBL1263) | yes | A | EMA Human Drugs |
| type 2 diabetes mellitus | Approved (main list) | ALBIGLUTIDE (CHEMBL2107841) | yes | A | EMA Human Drugs |
| type 2 diabetes mellitus | Approved (main list) | DAPAGLIFLOZIN (CHEMBL429910) | yes | A | EMA Human Drugs |
| type 2 diabetes mellitus | Approved (main list) | GLIMEPIRIDE (CHEMBL1481) | yes | A | EMA Human Drugs |
| type 2 diabetes mellitus | Approved (main list) | LIXISENATIDE (CHEMBL2108336) | yes | A | EMA Human Drugs |
| type 2 diabetes mellitus | Approved (main list) | METFORMIN (CHEMBL1431) | yes | A | EMA Human Drugs |
| type 2 diabetes mellitus | Approved (main list) | NATEGLINIDE (CHEMBL783) | yes | A | EMA Human Drugs |
| type 2 diabetes mellitus | Approved (main list) | PIOGLITAZONE (CHEMBL595) | yes | A | EMA Human Drugs |
| type 2 diabetes mellitus | Approved (main list) | SAXAGLIPTIN ANHYDROUS (CHEMBL385517) | yes | A | EMA Human Drugs |
| type 2 diabetes mellitus | Approved (main list) | SITAGLIPTIN (CHEMBL1422) | yes | A | EMA Human Drugs |
| type 2 diabetes mellitus | Approved: wider-group box | INSULIN ASPART (CHEMBL1201496) | yes | A | EMA Human Drugs |
| type 2 diabetes mellitus | Approved: wider-group box | INSULIN LISPRO (CHEMBL1201538) | yes | A | EMA Human Drugs |
| epilepsy | Approved (main list) | ESLICARBAZEPINE ACETATE (CHEMBL87992) | yes | A | EMA Human Drugs |
| epilepsy | Approved (main list) | EZOGABINE (CHEMBL41355) | yes | D | EMA Human Drugs; TTD |
| epilepsy | Approved (main list) | PREGABALIN (CHEMBL1059) | yes | A | EMA Human Drugs |
| epilepsy | Approved: wider-group box | IODAMIDE (CHEMBL1201239) | no | E | TTD |
| rheumatoid arthritis | Approved (main list) | ADALIMUMAB (CHEMBL1201580) | yes | A | EMA Human Drugs |
| rheumatoid arthritis | Approved (main list) | LEFLUNOMIDE (CHEMBL960) | yes | A | EMA Human Drugs |
| rheumatoid arthritis | Approved: narrower-disease box | USTEKINUMAB (CHEMBL1201835) | yes | A | EMA Human Drugs |
| rheumatoid arthritis | Approved: wider-group box | AUROTHIOGLUCOSE (CHEMBL1697725) | yes | D | TTD |
| rheumatoid arthritis | Approved: wider-group box | FLOCTAFENINE (CHEMBL2105075) | no | E | TTD |
| psoriasis | Approved (main list) | ADALIMUMAB (CHEMBL1201580) | yes | A | EMA Human Drugs |
| psoriasis | Approved (main list) | ETANERCEPT (CHEMBL1201572) | yes | A | EMA Human Drugs |
| psoriasis | Approved (main list) | USTEKINUMAB (CHEMBL1201835) | yes | A | EMA Human Drugs |
| atopic eczema | Approved (main list) | CRISABOROLE (CHEMBL484785) | yes | A | EMA Human Drugs |
| atopic eczema | Approved (main list) | TACROLIMUS ANHYDROUS (CHEMBL269732) | yes | A | EMA Human Drugs |
| ulcerative colitis | Approved (main list) | ADALIMUMAB (CHEMBL1201580) | yes | A | EMA Human Drugs |
| ulcerative colitis | Approved (main list) | USTEKINUMAB (CHEMBL1201835) | yes | A | EMA Human Drugs |
| osteoporosis | Approved (main list) | TERIPARATIDE (CHEMBL525610) | yes | A | EMA Human Drugs |
| osteoporosis | Approved (main list) | ZOLEDRONIC ACID ANHYDROUS (CHEMBL924) | yes | A | EMA Human Drugs |
| osteoporosis | Approved: narrower-disease box | PARATHYROID HORMONE (CHEMBL2108078) | no | E | EMA Human Drugs |
| gout | Approved (main list) | ALLOPURINOL (CHEMBL1467) | yes | A | EMA Human Drugs |
| gout | Approved (main list) | LESINURAD (CHEMBL2105720) | yes | D | EMA Human Drugs |
| gout | Approved (main list) | PEGLOTICASE (CHEMBL1237025) | yes | A | EMA Human Drugs |
| gout | Approved: wider-group box | AUROTHIOGLUCOSE (CHEMBL1697725) | no | E | TTD |
| gout | Approved: wider-group box | FLOCTAFENINE (CHEMBL2105075) | no | E | TTD |
| heart failure | Approved (main list) | IVABRADINE (CHEMBL471737) | yes | A | EMA Human Drugs |
| atrial fibrillation | Approved (main list) | DOFETILIDE (CHEMBL473) | yes | A | EMA Human Drugs |
| atrial fibrillation | Approved (main list) | DRONEDARONE (CHEMBL184412) | yes | A | TTD |
| chronic obstructive pulmonary disease | Approved (main list) | BECLOMETHASONE (CHEMBL1586) | yes | A | EMA Human Drugs |
| chronic obstructive pulmonary disease | Approved (main list) | BECLOMETHASONE DIPROPIONATE (CHEMBL1200500) | yes | A | EMA Human Drugs |
| chronic obstructive pulmonary disease | Approved (main list) | BUDESONIDE (CHEMBL1370) | yes | A | EMA Human Drugs |
| chronic obstructive pulmonary disease | Approved (main list) | FLUTICASONE FUROATE (CHEMBL1676) | yes | A | EMA Human Drugs |
| chronic obstructive pulmonary disease | Approved (main list) | FLUTICASONE PROPIONATE (CHEMBL1473) | yes | A | EMA Human Drugs |
| chronic obstructive pulmonary disease | Approved (main list) | FORMOTEROL (CHEMBL1256786) | yes | A | EMA Human Drugs |
| chronic obstructive pulmonary disease | Approved (main list) | ROFLUMILAST (CHEMBL193240) | yes | A | EMA Human Drugs; TTD |
| chronic obstructive pulmonary disease | Approved (main list) | SALMETEROL (CHEMBL1263) | yes | A | EMA Human Drugs |
| chronic obstructive pulmonary disease | Approved (main list) | UMECLIDINIUM (CHEMBL1187833) | yes | A | EMA Human Drugs |
| chronic obstructive pulmonary disease | Approved (main list) | VILANTEROL (CHEMBL1198857) | yes | A | EMA Human Drugs |
| chronic obstructive pulmonary disease | Approved: narrower-disease box | TELITHROMYCIN (CHEMBL1136) | no | E | EMA Human Drugs |
| chronic kidney disease | Approved (main list) | DARBEPOETIN ALFA (CHEMBL1201566) | yes | A | EMA Human Drugs |
| chronic kidney disease | Approved (main list) | EPOETIN DELTA (CHEMBL2109093) | no | E | EMA Human Drugs |
| chronic kidney disease | Approved (main list) | FERUMOXYTOL (CHEMBL1201867) | yes | B | EMA Human Drugs |
| depressive disorder | Approved (main list) | BENACTYZINE (CHEMBL70352) | no | E | TTD |
| depressive disorder | Approved: narrower-disease box | AGOMELATINE (CHEMBL10878) | yes | A | EMA Human Drugs; TTD |
| schizophrenia | Approved (main list) | CARPHENAZINE (CHEMBL1201328) | no | E | TTD |
| schizophrenia | Approved (main list) | CHLORPROMAZINE (CHEMBL71) | yes | A | TTD |
| schizophrenia | Approved (main list) | FLUPENTIXOL (CHEMBL6066864) | no | E | TTD |
| schizophrenia | Approved (main list) | OLANZAPINE (CHEMBL715) | yes | A | EMA Human Drugs |
| schizophrenia | Approved (main list) | TRIFLUPROMAZINE (CHEMBL570) | no | E | TTD |
| bipolar disorder | Approved (main list) | OLANZAPINE (CHEMBL715) | yes | A | EMA Human Drugs |
| Parkinson disease | Approved (main list) | CARBIDOPA ANHYDROUS (CHEMBL1201236) | yes | A | EMA Human Drugs |
| Parkinson disease | Approved (main list) | LEVODOPA (CHEMBL1009) | yes | A | EMA Human Drugs |
| Parkinson disease | Approved (main list) | OPICAPONE (CHEMBL1089318) | yes | A | EMA Human Drugs |
| Parkinson disease | Approved (main list) | PRAMIPEXOLE (CHEMBL301265) | yes | A | EMA Human Drugs |
| Parkinson disease | Approved (main list) | RIVASTIGMINE (CHEMBL636) | yes | A | EMA Human Drugs |
| Parkinson disease | Approved (main list) | ROTIGOTINE (CHEMBL1303) | yes | A | EMA Human Drugs |
| Alzheimer disease | Approved (main list) | MEMANTINE (CHEMBL807) | yes | A | EMA Human Drugs |
| Alzheimer disease | Approved (main list) | RIVASTIGMINE (CHEMBL636) | yes | A | EMA Human Drugs |
| tuberculosis | Approved (main list) | AMINOSALICYLIC ACID (CHEMBL1169) | yes | A | EMA Human Drugs |
| malaria | Approved (main list) | AMODIAQUINE (CHEMBL682) | yes | F | TTD |
| malaria | Approved (main list) | CHLOROQUINE (CHEMBL76) | yes | A | TTD |
| breast cancer | Approved (main list) | FORMESTANE (CHEMBL132530) | no | E | TTD |
| breast cancer | Approved: wider-group box | IBANDRONIC ACID (CHEMBL997) | yes | A | EMA Human Drugs |
| prostate cancer | Approved (main list) | ATRASENTAN (CHEMBL9194) | no | E | TTD |
| prostate cancer | Approved: wider-group box | DOCETAXEL ANHYDROUS (CHEMBL92) | yes | A | EMA Human Drugs |
| colorectal cancer | Approved: wider-group box | ARCITUMOMAB (CHEMBL2108253) | no | E | EMA Human Drugs |
| melanoma | Approved (main list) | INTERFERON ALFA-2B (CHEMBL1201558) | yes | A | EMA Human Drugs |
| chronic myeloid leukemia | Approved (main list) | DASATINIB ANHYDROUS (CHEMBL1421) | yes | A | EMA Human Drugs |
| chronic myeloid leukemia | Approved (main list) | IMATINIB (CHEMBL941) | yes | A | EMA Human Drugs |
| chronic myeloid leukemia | Approved (main list) | INTERFERON ALFA-2B (CHEMBL1201558) | no | E | EMA Human Drugs |
| acute myeloid leukemia | Approved (main list) | AZACITIDINE (CHEMBL1489) | yes | A | EMA Human Drugs |
| cystic fibrosis | Approved (main list) | TOBRAMYCIN (CHEMBL1747) | yes | A | EMA Human Drugs |
| cystic fibrosis | Approved: wider-group box | IBUPROXAM (CHEMBL292707) | no | E | TTD |
| Duchenne muscular dystrophy | Approved (main list) | ATALUREN (CHEMBL256997) | no | E | EMA Human Drugs |
| hemophilia A | Approved (main list) | OCTOCOG ALFA (CHEMBL4297873) | yes | A | EMA Human Drugs |
| hemophilia B | Approved (main list) | COAGULATION FACTOR IX HUMAN (CHEMBL4297986) | no | E | EMA Human Drugs |
| hemophilia B | Approved (main list) | FIDANACOGENE ELAPARVOVEC (CHEMBL3990034) | no | E | EMA Human Drugs |
| acromegaly | Approved (main list) | OCTREOTIDE (CHEMBL1680) | yes | A | EMA Human Drugs |
| hidradenitis suppurativa | Approved (main list) | ADALIMUMAB (CHEMBL1201580) | yes | A | EMA Human Drugs |

## 3. TRIALS

"Listed in trials" means: the medicine (all its forms together) is on the disease's own Open Targets list, and its strongest stage for this disease is a phase word (`PHASE_...` or `EARLY_PHASE_...`). That is the same test Moonlight's filter uses for "being studied".

- Listed in trials, all diseases: **8244**. Shown in In trials: **559**, of which 559 are on that list.
- Listed and not shown: **7685**.

| Rule that left it out | Medicines |
|---|---|
| not approved elsewhere: and not on a top-25 protein either | 3293 |
| not approved elsewhere: on a top-25 protein | 452 |
| not on a top-25 protein | 3827 |
| not on a top-25 protein: also withdrawn in some country | 103 |
| other: the protein route sorted it as new_clue (its stage for this disease there: None) | 1 |
| other: withdrawn in some country | 9 |
| **Total** | 7685 |

How a rule was chosen, in this order. (1) *Not approved elsewhere*: the stage word says the medicine is not approved for any disease. For a medicine on a top-25 protein that is Moonlight's own finding. For one that is not, only the forms on the disease's list could be looked at. (2) *Not on a top-25 protein*: approved somewhere, but it acts on none of the 25 proteins Moonlight looks at, so Moonlight never meets it. (3) *Other*: everything else, with the detail spelled out. Every medicine, with its rule, is in `trials_missing.csv`.

Every stage word on the 50 lists (medicines, strongest stage for the disease): `PHASE_2` 3850, `PHASE_3` 1773, `PHASE_1` 1361, `APPROVAL` 1166, `PHASE_1_2` 818, `UNKNOWN` 780, `PHASE_2_3` 312, `EARLY_PHASE_1` 130, `IND` 38, `PRECLINICAL` 21, `PREAPPROVAL` 6.

| Disease | On the list | Listed in trials | Shown in In trials | Shown and listed | Not approved elsewhere | Not on a top-25 protein | Other |
|---|---|---|---|---|---|---|---|
| asthma | 392 | 288 | 13 | 13 | 170 | 105 | 0 |
| type 2 diabetes mellitus | 582 | 440 | 11 | 11 | 217 | 212 | 0 |
| epilepsy | 133 | 62 | 3 | 3 | 28 | 31 | 0 |
| rheumatoid arthritis | 437 | 330 | 21 | 21 | 184 | 124 | 1 |
| psoriasis | 190 | 119 | 15 | 15 | 63 | 41 | 0 |
| atopic eczema | 231 | 165 | 26 | 26 | 77 | 62 | 0 |
| ulcerative colitis | 232 | 182 | 10 | 10 | 91 | 80 | 1 |
| osteoporosis | 111 | 55 | 8 | 8 | 23 | 24 | 0 |
| gout | 61 | 32 | 3 | 3 | 11 | 17 | 1 |
| heart failure | 295 | 196 | 26 | 26 | 61 | 108 | 1 |
| atrial fibrillation | 124 | 72 | 15 | 15 | 18 | 38 | 1 |
| chronic obstructive pulmonary disease | 306 | 246 | 14 | 14 | 120 | 111 | 1 |
| chronic kidney disease | 334 | 235 | 22 | 22 | 50 | 162 | 1 |
| hypothyroidism | 16 | 4 | 0 | 0 | 0 | 4 | 0 |
| depressive disorder | 279 | 177 | 31 | 31 | 40 | 106 | 0 |
| schizophrenia | 319 | 224 | 15 | 15 | 91 | 118 | 0 |
| bipolar disorder | 158 | 118 | 28 | 28 | 22 | 68 | 0 |
| Parkinson disease | 309 | 239 | 9 | 9 | 110 | 120 | 0 |
| Alzheimer disease | 417 | 363 | 7 | 7 | 184 | 172 | 0 |
| glaucoma | 84 | 32 | 1 | 1 | 8 | 23 | 0 |
| endometriosis | 84 | 61 | 18 | 18 | 11 | 31 | 1 |
| tuberculosis | 128 | 102 | 5 | 5 | 19 | 78 | 0 |
| malaria | 90 | 44 | 0 | 0 | 12 | 32 | 0 |
| breast cancer | 983 | 871 | 29 | 29 | 462 | 379 | 1 |
| prostate cancer | 717 | 668 | 17 | 17 | 319 | 332 | 0 |
| colorectal cancer | 722 | 681 | 44 | 44 | 368 | 269 | 0 |
| lung cancer | 253 | 236 | 38 | 38 | 85 | 113 | 0 |
| melanoma | 571 | 547 | 17 | 17 | 306 | 224 | 0 |
| chronic myeloid leukemia | 166 | 155 | 14 | 14 | 48 | 93 | 0 |
| acute myeloid leukemia | 554 | 532 | 19 | 19 | 285 | 228 | 0 |
| cystic fibrosis | 142 | 112 | 1 | 1 | 37 | 74 | 0 |
| Duchenne muscular dystrophy | 60 | 50 | 5 | 5 | 24 | 21 | 0 |
| spinal muscular atrophy | 20 | 15 | 0 | 0 | 7 | 8 | 0 |
| Huntington disease | 56 | 48 | 6 | 6 | 19 | 23 | 0 |
| amyotrophic lateral sclerosis | 177 | 166 | 2 | 2 | 48 | 116 | 0 |
| Gaucher disease | 12 | 6 | 0 | 0 | 3 | 3 | 0 |
| Fabry disease | 17 | 7 | 1 | 1 | 6 | 0 | 0 |
| phenylketonuria | 7 | 4 | 0 | 0 | 2 | 2 | 0 |
| hemophilia A | 42 | 23 | 10 | 10 | 7 | 6 | 0 |
| hemophilia B | 23 | 12 | 7 | 7 | 5 | 0 | 0 |
| myasthenia gravis | 73 | 50 | 3 | 3 | 15 | 32 | 0 |
| narcolepsy | 16 | 10 | 3 | 3 | 4 | 3 | 0 |
| Wilson disease | 12 | 6 | 0 | 0 | 4 | 2 | 0 |
| hereditary angioedema | 16 | 4 | 1 | 1 | 3 | 0 | 0 |
| acromegaly | 21 | 11 | 4 | 4 | 6 | 1 | 0 |
| Cushing syndrome | 13 | 6 | 2 | 2 | 4 | 0 | 0 |
| sarcoidosis | 44 | 35 | 13 | 13 | 6 | 16 | 0 |
| systemic sclerosis | 110 | 103 | 2 | 2 | 31 | 69 | 1 |
| Behcet disease | 40 | 35 | 10 | 10 | 5 | 20 | 0 |
| hidradenitis suppurativa | 76 | 65 | 10 | 10 | 26 | 29 | 0 |

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
| A | 744 | 65.8% | 246 | 36.8% |
| B | 195 | 17.2% | 110 | 16.5% |
| C | 57 | 5.0% | 19 | 2.8% |
| D | 66 | 5.8% | 268 | 40.1% |
| E | 14 | 1.2% | 8 | 1.2% |
| F | 55 | 4.9% | 17 | 2.5% |
| N | 0 | 0.0% | 0 | 0.0% |
| Total | 1131 | 100.0% | 668 | 100.0% |

Moonlight's own lines on Approved cards (main list and boxes): the Japan line on **76** cards, the "no regulator record" line on **712**, a red warning on **12**. Moonlight counts PMDA as a regulator; probe_p3's group A does not, so the two counts are not the same thing.

| Disease | Main list cards | A | B | C | D | E | F | N | Box cards | Box cards outside A |
|---|---|---|---|---|---|---|---|---|---|---|
| asthma | 70 | 50 | 19 | 0 | 0 | 1 | 0 | 0 | 0 | 0 |
| type 2 diabetes mellitus | 59 | 49 | 2 | 6 | 0 | 0 | 2 | 0 | 44 | 22 |
| epilepsy | 54 | 22 | 3 | 1 | 13 | 0 | 15 | 0 | 5 | 4 |
| rheumatoid arthritis | 69 | 55 | 11 | 2 | 0 | 0 | 1 | 0 | 69 | 52 |
| psoriasis | 43 | 36 | 0 | 0 | 7 | 0 | 0 | 0 | 66 | 55 |
| atopic eczema | 41 | 24 | 2 | 12 | 2 | 0 | 1 | 0 | 72 | 53 |
| ulcerative colitis | 28 | 26 | 1 | 1 | 0 | 0 | 0 | 0 | 1 | 1 |
| osteoporosis | 33 | 17 | 12 | 4 | 0 | 0 | 0 | 0 | 2 | 1 |
| gout | 21 | 14 | 0 | 2 | 4 | 0 | 1 | 0 | 37 | 19 |
| heart failure | 43 | 33 | 9 | 0 | 0 | 0 | 1 | 0 | 31 | 17 |
| atrial fibrillation | 17 | 14 | 3 | 0 | 0 | 0 | 0 | 0 | 28 | 19 |
| chronic obstructive pulmonary disease | 29 | 22 | 7 | 0 | 0 | 0 | 0 | 0 | 26 | 4 |
| chronic kidney disease | 51 | 46 | 1 | 2 | 0 | 2 | 0 | 0 | 6 | 3 |
| hypothyroidism | 8 | 6 | 2 | 0 | 0 | 0 | 0 | 0 | 1 | 1 |
| depressive disorder | 33 | 4 | 23 | 2 | 0 | 1 | 3 | 0 | 47 | 26 |
| schizophrenia | 45 | 25 | 16 | 1 | 0 | 3 | 0 | 0 | 31 | 30 |
| bipolar disorder | 19 | 16 | 2 | 0 | 0 | 1 | 0 | 0 | 3 | 1 |
| Parkinson disease | 43 | 19 | 4 | 2 | 10 | 0 | 8 | 0 | 0 | 0 |
| Alzheimer disease | 21 | 12 | 5 | 4 | 0 | 0 | 0 | 0 | 5 | 4 |
| glaucoma | 39 | 11 | 0 | 1 | 21 | 0 | 6 | 0 | 26 | 26 |
| endometriosis | 10 | 5 | 1 | 3 | 0 | 0 | 1 | 0 | 0 | 0 |
| tuberculosis | 22 | 11 | 0 | 0 | 8 | 0 | 3 | 0 | 9 | 3 |
| malaria | 29 | 15 | 6 | 1 | 1 | 0 | 6 | 0 | 0 | 0 |
| breast cancer | 73 | 38 | 27 | 5 | 0 | 1 | 2 | 0 | 7 | 0 |
| prostate cancer | 30 | 16 | 11 | 1 | 0 | 1 | 1 | 0 | 9 | 0 |
| colorectal cancer | 19 | 4 | 11 | 2 | 0 | 0 | 2 | 0 | 9 | 3 |
| lung cancer | 8 | 5 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| melanoma | 20 | 16 | 4 | 0 | 0 | 0 | 0 | 0 | 2 | 0 |
| chronic myeloid leukemia | 9 | 8 | 0 | 0 | 0 | 1 | 0 | 0 | 4 | 0 |
| acute myeloid leukemia | 15 | 15 | 0 | 0 | 0 | 0 | 0 | 0 | 12 | 8 |
| cystic fibrosis | 15 | 14 | 1 | 0 | 0 | 0 | 0 | 0 | 15 | 14 |
| Duchenne muscular dystrophy | 8 | 7 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 |
| spinal muscular atrophy | 4 | 3 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Huntington disease | 5 | 1 | 0 | 4 | 0 | 0 | 0 | 0 | 5 | 0 |
| amyotrophic lateral sclerosis | 5 | 3 | 0 | 1 | 0 | 0 | 1 | 0 | 0 | 0 |
| Gaucher disease | 6 | 5 | 1 | 0 | 0 | 0 | 0 | 0 | 26 | 26 |
| Fabry disease | 4 | 4 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| phenylketonuria | 3 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| hemophilia A | 18 | 18 | 0 | 0 | 0 | 0 | 0 | 0 | 11 | 10 |
| hemophilia B | 11 | 9 | 0 | 0 | 0 | 2 | 0 | 0 | 15 | 14 |
| myasthenia gravis | 12 | 10 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| narcolepsy | 5 | 3 | 1 | 0 | 0 | 0 | 1 | 0 | 5 | 1 |
| Wilson disease | 4 | 4 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 |
| hereditary angioedema | 9 | 8 | 1 | 0 | 0 | 0 | 0 | 0 | 2 | 0 |
| acromegaly | 6 | 6 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Cushing syndrome | 3 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 4 | 0 |
| sarcoidosis | 5 | 4 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| systemic sclerosis | 4 | 3 | 1 | 0 | 0 | 0 | 0 | 0 | 32 | 5 |
| Behcet disease | 2 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| hidradenitis suppurativa | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

## 5. DIRECTION

Counted probe_p4's way. A protein is **one-way** for a disease if every main-list Approved medicine with an up or down direction on it points the same way, **both-ways** if they disagree. A card is one medicine.

|  | New clues | In trials |
|---|---|---|
| cards in total | 3079 | 559 |
| cards pointing OPPOSITE to the Approved medicines on a one-way protein | 392 | 25 |
| cards pointing the SAME way on a one-way protein | 1505 | 327 |
| cards with mixed or unknown direction on a one-way protein | 104 | 26 |
| cards sitting on a both-ways protein | 143 | 19 |
| cards carrying the live site's line "Opposite way to the approved medicines for this disease." | 383 | 25 |

- Diseases with at least one opposite card: **34 of 50**. One-way proteins (disease by disease): 451. Both-ways proteins: 8.
- The live site's line (ticket 3.7) leaves the red-warning Approved cards out before deciding one-way. probe_p4 did not. Where the last row differs from the second row, that is why.

### Unknown and mixed directions on cards

| Tab | Cards | No protein shown | At least one unknown | Every direction unknown | At least one mixed | Card-protein pairs | Pairs unknown | Pairs mixed |
|---|---|---|---|---|---|---|---|---|
| Approved (main list) | 1131 | 451 | 69 | 60 | 0 | 1325 | 114 | 0 |
| Approved: narrower-disease box | 143 | 81 | 4 | 1 | 0 | 114 | 7 | 0 |
| Approved: wider-group box | 525 | 405 | 13 | 13 | 0 | 162 | 13 | 0 |
| In trials | 559 | 0 | 60 | 55 | 0 | 922 | 109 | 0 |
| New clues | 3079 | 0 | 203 | 184 | 0 | 6031 | 313 | 0 |

The action words behind every unknown or mixed pair on a card:

| Direction | Action words from Open Targets | Card-protein pairs |
|---|---|---|
| unknown | MODULATOR | 133 |
| unknown | EXOGENOUS PROTEIN | 62 |
| unknown | NEGATIVE ALLOSTERIC MODULATOR | 58 |
| unknown | PARTIAL AGONIST | 52 |
| unknown | INVERSE AGONIST | 42 |
| unknown | RELEASING AGENT | 37 |
| unknown | BINDING AGENT | 31 |
| unknown | HYDROLYTIC ENZYME | 31 |
| unknown | SUBSTRATE | 25 |
| unknown | ALLOSTERIC ANTAGONIST | 22 |
| unknown | STABILISER | 20 |
| unknown | DISRUPTING AGENT | 17 |
| unknown | EXOGENOUS GENE | 10 |
| unknown | OTHER | 6 |
| unknown | DEGRADER | 4 |
| unknown | CROSS-LINKING AGENT | 2 |
| unknown | RNAI INHIBITOR | 2 |
| unknown | ANTISENSE INHIBITOR | 1 |
| unknown | NEGATIVE MODULATOR | 1 |

| Disease | Approved cards (with a path) | One-way proteins | Both-ways proteins | NC total | NC opp | NC same | NC both | NC line | IT total | IT opp | IT same | IT both | IT line |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| asthma | 70 (54) | 20 | 1 | 126 | 26 | 81 | 28 | 26 | 13 | 2 | 9 | 0 | 2 |
| type 2 diabetes mellitus | 59 (23) | 10 | 0 | 11 | 2 | 7 | 0 | 2 | 11 | 2 | 8 | 0 | 2 |
| epilepsy | 54 (26) | 10 | 0 | 74 | 5 | 64 | 0 | 5 | 3 | 0 | 1 | 0 | 0 |
| rheumatoid arthritis | 69 (47) | 16 | 0 | 76 | 3 | 59 | 0 | 3 | 21 | 0 | 11 | 0 | 0 |
| psoriasis | 43 (29) | 18 | 0 | 65 | 2 | 59 | 0 | 2 | 15 | 0 | 13 | 0 | 0 |
| atopic eczema | 41 (34) | 15 | 0 | 100 | 5 | 78 | 0 | 5 | 26 | 0 | 24 | 0 | 0 |
| ulcerative colitis | 28 (25) | 17 | 0 | 100 | 2 | 98 | 0 | 2 | 10 | 0 | 9 | 0 | 0 |
| osteoporosis | 33 (21) | 9 | 0 | 50 | 10 | 31 | 0 | 10 | 8 | 0 | 6 | 0 | 0 |
| gout | 21 (10) | 19 | 0 | 52 | 0 | 50 | 0 | 0 | 3 | 0 | 3 | 0 | 0 |
| heart failure | 43 (30) | 19 | 2 | 113 | 10 | 61 | 39 | 10 | 26 | 1 | 17 | 6 | 1 |
| atrial fibrillation | 17 (11) | 14 | 0 | 72 | 0 | 61 | 0 | 0 | 15 | 0 | 15 | 0 | 0 |
| chronic obstructive pulmonary disease | 29 (24) | 15 | 0 | 142 | 22 | 106 | 0 | 22 | 14 | 2 | 8 | 0 | 2 |
| chronic kidney disease | 51 (26) | 12 | 0 | 49 | 5 | 33 | 0 | 5 | 22 | 0 | 17 | 0 | 0 |
| hypothyroidism | 8 (3) | 3 | 0 | 16 | 0 | 4 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| depressive disorder | 33 (28) | 19 | 0 | 170 | 26 | 97 | 0 | 26 | 31 | 4 | 19 | 0 | 4 |
| schizophrenia | 45 (37) | 19 | 0 | 48 | 20 | 25 | 0 | 20 | 15 | 4 | 6 | 0 | 4 |
| bipolar disorder | 19 (19) | 21 | 0 | 150 | 8 | 104 | 0 | 8 | 28 | 1 | 17 | 0 | 1 |
| Parkinson disease | 43 (24) | 10 | 0 | 94 | 48 | 38 | 0 | 48 | 9 | 3 | 3 | 0 | 3 |
| Alzheimer disease | 21 (11) | 4 | 0 | 41 | 1 | 18 | 0 | 1 | 7 | 0 | 2 | 0 | 0 |
| glaucoma | 39 (21) | 10 | 2 | 76 | 9 | 23 | 47 | 9 | 1 | 0 | 0 | 1 | 0 |
| endometriosis | 10 (9) | 4 | 1 | 82 | 12 | 41 | 3 | 12 | 18 | 2 | 8 | 7 | 2 |
| tuberculosis | 22 (0) | 0 | 0 | 62 | 0 | 0 | 0 | 0 | 5 | 0 | 0 | 0 | 0 |
| malaria | 29 (3) | 10 | 0 | 97 | 1 | 45 | 0 | 1 | 0 | 0 | 0 | 0 | 0 |
| breast cancer | 73 (23) | 8 | 1 | 27 | 0 | 11 | 13 | 0 | 29 | 0 | 15 | 5 | 0 |
| prostate cancer | 30 (11) | 3 | 0 | 18 | 8 | 8 | 0 | 8 | 17 | 4 | 11 | 0 | 4 |
| colorectal cancer | 19 (7) | 6 | 0 | 23 | 2 | 12 | 0 | 2 | 44 | 0 | 30 | 0 | 0 |
| lung cancer | 8 (2) | 4 | 0 | 46 | 0 | 11 | 0 | 0 | 38 | 0 | 21 | 0 | 0 |
| melanoma | 20 (7) | 4 | 0 | 8 | 0 | 0 | 0 | 0 | 17 | 0 | 6 | 0 | 0 |
| chronic myeloid leukemia | 9 (8) | 20 | 0 | 28 | 2 | 21 | 0 | 2 | 14 | 0 | 10 | 0 | 0 |
| acute myeloid leukemia | 15 (7) | 7 | 0 | 21 | 1 | 7 | 0 | 1 | 19 | 0 | 13 | 0 | 0 |
| cystic fibrosis | 15 (6) | 3 | 0 | 2 | 1 | 0 | 0 | 1 | 1 | 0 | 0 | 0 | 0 |
| Duchenne muscular dystrophy | 8 (8) | 14 | 0 | 68 | 5 | 63 | 0 | 5 | 5 | 0 | 4 | 0 | 0 |
| spinal muscular atrophy | 4 (3) | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Huntington disease | 5 (5) | 6 | 0 | 175 | 9 | 52 | 0 | 0 | 6 | 0 | 0 | 0 | 0 |
| amyotrophic lateral sclerosis | 5 (1) | 0 | 0 | 23 | 0 | 0 | 0 | 0 | 2 | 0 | 0 | 0 | 0 |
| Gaucher disease | 6 (2) | 1 | 0 | 23 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Fabry disease | 4 (1) | 0 | 0 | 48 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 |
| phenylketonuria | 3 (1) | 1 | 0 | 69 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| hemophilia A | 18 (18) | 2 | 0 | 38 | 4 | 1 | 0 | 4 | 10 | 0 | 0 | 0 | 0 |
| hemophilia B | 11 (11) | 1 | 0 | 21 | 0 | 1 | 0 | 0 | 7 | 0 | 0 | 0 | 0 |
| myasthenia gravis | 12 (12) | 24 | 1 | 20 | 1 | 6 | 13 | 1 | 3 | 0 | 3 | 0 | 0 |
| narcolepsy | 5 (4) | 4 | 0 | 65 | 0 | 13 | 0 | 0 | 3 | 0 | 2 | 0 | 0 |
| Wilson disease | 4 (0) | 0 | 0 | 18 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| hereditary angioedema | 9 (7) | 6 | 0 | 61 | 9 | 12 | 0 | 9 | 1 | 0 | 0 | 0 | 0 |
| acromegaly | 6 (6) | 9 | 0 | 125 | 52 | 7 | 0 | 52 | 4 | 0 | 1 | 0 | 0 |
| Cushing syndrome | 3 (3) | 6 | 0 | 102 | 72 | 4 | 0 | 72 | 2 | 0 | 2 | 0 | 0 |
| sarcoidosis | 5 (5) | 1 | 0 | 58 | 2 | 44 | 0 | 2 | 13 | 0 | 8 | 0 | 0 |
| systemic sclerosis | 4 (4) | 16 | 0 | 38 | 3 | 35 | 0 | 3 | 2 | 0 | 2 | 0 | 0 |
| Behcet disease | 2 (2) | 9 | 0 | 71 | 4 | 10 | 0 | 4 | 10 | 0 | 1 | 0 | 0 |
| hidradenitis suppurativa | 1 (1) | 1 | 0 | 17 | 0 | 4 | 0 | 0 | 10 | 0 | 2 | 0 | 0 |

NC = New clues, IT = In trials, opp = opposite on a one-way protein, both = on a both-ways protein, line = carries the live site's opposite-way line.

## Tonight next to the two earlier studies

**probe_p4 (18 Nov, data 26.09).** Same 50 diseases, same way of counting.

|  | probe_p4 | tonight |
|---|---|---|
| Approved main-list cards | 1131 | 1131 |
| New clues: cards | 3074 | 3079 |
| New clues: opposite cards | 392 | 392 |
| New clues: same-way cards | 1501 | 1505 |
| New clues: mixed or unknown on a one-way protein | 104 | 104 |
| New clues: on a both-ways protein | 143 | 143 |
| In trials: cards | 559 | 559 |
| In trials: opposite cards | 25 | 25 |
| In trials: same-way cards | 327 | 327 |
| In trials: mixed or unknown on a one-way protein | 26 | 26 |
| In trials: on a both-ways protein | 19 | 19 |

Every per-disease number that is not the same as in probe_p4:

| Disease | What | probe_p4 | tonight |
|---|---|---|---|
| malaria | one-way proteins | 9 | 10 |
| malaria | New clues cards | 92 | 97 |
| malaria | New clues same | 41 | 45 |

**probe_p3 (17 Nov).** probe_p3 read only each disease's own list, so for this comparison tonight's answers were counted that way too (not by card). 50 of tonight's diseases are in probe_p3.

| Group | probe_p3, these diseases | tonight, own list only |
|---|---|---|
| A | 744 | 744 |
| B | 195 | 195 |
| C | 57 | 57 |
| D | 66 | 66 |
| E | 14 | 14 |
| F | 55 | 55 |
| Total | 1131 | 1131 |

## Things to know when reading the numbers

Facts about how the night went. None is a judgement.

- **The session could not reach Open Targets or the link hosts at first.** Its network rules
  blocked them. Kashish approved a new environment, `night-watch-links`, that allows Open
  Targets and the link hosts met in the earlier studies' saved answers, and later one more
  host, `atcddd.fhi.no`, because every `www.whocc.no` link redirects there.
- **The session's machine restarted once, at 15:17:33 UTC.** It cut off both scripts. Both
  were started again and went on from what was saved. One Open Targets request and five link
  requests failed at that moment, inside the session's own proxy, before reaching any host.
  The Open Targets question was asked again by the second run. The five links were asked
  again at the end (`check_links.py --retry-unreached`); their failed tries are kept in
  `links.jsonl`.
- **The first 34 `www.whocc.no` links were asked in two parts.** The first hop (a 301) was
  asked before `atcddd.fhi.no` was allowed, and the second hop after. No hop was asked twice.
- **One host said "slow down".** `www.ema.europa.eu` answered 429 4 times during the link
  check (and once more for the made-up link). Each time the script waited a minute, doubled
  its gap for that host and asked that link again. Every link was finished. Open Targets never
  refused.
- **Open Targets was asked each "which medicines?" question twice**, and a third time if the
  two answers differed, because that is what Moonlight's own code does. That is why there are
  many more requests than questions.
- **A card shows one link.** Its medicine may have many more report links in the data. Only
  the one link the card shows ("Source record") was asked.
- **A link shown by cards of several diseases was asked once.**
- **TRIALS counts medicine families**, the way Moonlight does: a medicine and its tablet forms
  are one. "Open Targets lists it in trials" was read from the disease's own list only.

## Things I did not verify

- **Whether a link that answers 200 shows the right page, or any real page.** I only read the
  status. The table "What these hosts answer for a link that cannot exist" shows that some
  hosts answer 200 for a made-up link, or redirect it to their front page. For those hosts a
  count of 404s cannot find a dead link. So "0 dead" for such a host means "no 404, 410 or DNS
  failure", not "every link works".
- **What a person's browser would see.** The links were asked from this session's machine,
  through its proxy, with a plain program, not a browser. A host may answer a browser, another
  country or another day differently. DNS was looked up by the proxy, not by this machine, so
  a DNS failure might have looked like a different error here. None was met.
- **Whether any withdrawal, approval, trial, proof group or direction is right or wrong.** I
  cannot tell, and nothing here is labelled so. Each number says what Open Targets' data holds
  and what Moonlight's code makes of it.
- **Whether a medicine "not approved elsewhere" is truly approved nowhere.** For a medicine on
  one of the top 25 proteins, this is Moonlight's own finding from all the forms it met. For a
  medicine on none of them, only the forms on the disease's own list could be looked at;
  another form of the same medicine might be approved.
- **Trials Open Targets does not list.** Only Open Targets was asked. ClinicalTrials.gov itself
  was not searched.
- **The live site.** As in probe_p4, Moonlight's site and Gemini were not called. The cards
  were built by the repo's code at the commit named above, and matched what `api.clues()`
  returns when run here. If the deployed site runs other code, other data, or has other saved
  answers, its cards may differ. What the page draws on screen was not looked at.
- **Explanations.** No Gemini text was made or read, so nothing here says what an explanation
  says about direction, trials or proof.
- **Open Targets' completeness.** A missing medicine, report or mechanism row, or an answer
  that was short on both asks, would not be noticed.
- **Why malaria has 5 more New clues cards than in probe_p4.** The data version is the same
  (26.09) and the code changed in between. I counted the difference and did not look into it.
- **The diseases outside these 50.** They are probe_p4's 50, picked by people. The counts
  describe them only.
- **The proof groups for box cards** were read from the lists of the narrower or wider
  entries that name the medicine, all together. probe_p3 never looked at those.
- **The tests.** No code under `moonlight/`, `web/` or `tests/` was touched. The test suite
  was run once at the end only to see that the new folder breaks nothing; it proves nothing
  about this study.
