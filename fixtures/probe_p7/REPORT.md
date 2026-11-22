# Probe P7: ClinicalTrials.gov

Read-only study, 22 Nov 2026, branch `probe-ctgov` (from `main`). Only files under `fixtures/probe_p7/` were written. No code and no test was changed. Every number below was counted by `analyse.py` from saved files and is also in `counts.json`. **Nothing here is labelled right or wrong.**

## What was done

- **Step 1.** The first try, earlier in the session, never reached the register: this session's own network rules refused it (403 from the session's gate, not from ClinicalTrials.gov). After `clinicaltrials.gov` was allowed, one request for `NCT05965700` answered 200. It is saved whole in `responses/step1/`.
- **Register.** ClinicalTrials.gov API v2, `https://clinicaltrials.gov/api/v2/`. It says of itself: API version 2.0.5, data stamped 2026-11-20T10:00:05.
- **Requests.** 912 in all, from 2026-11-22T12:46:38Z to 2026-11-22T13:05:58Z, one at a time, at least one second apart: 1 step1, 3 control, 564 card, 321 own_batch, 13 known, 10 count. Answers: 911 with status 200, 1 with status 404. The one 404 is the made-up control number. Times the register said "slow down" or the connection failed: 0. Every answer is saved byte for byte under `responses/`, with one line per request in `responses/index.jsonl`.
- **Where P5 and P6 came from.** They are not on `main`. They were read with `git show` from `probe-baseline` at `3bc6dac` (P5, 50 diseases) and `probe-key-diseases` at `23962bc` (P6, 9 diseases). `extract_inputs.py` copied the NCT links into `inputs/nct_links.json`. Its own-list numbers were compared with the raw Open Targets answers saved in P5 and P6: 0 of 59 diseases differed.
- **Fields.** Each request asked only for: NCT number, status, status-verified date, last-update date, primary completion date and its type, completion date and its type, study type, phase, conditions, intervention type and name. The names were checked against the Step 1 answer.

## How "cards and own lists" was read

- **Cards**: the one "Source record" link each card shows (Approved main list, the two folded boxes, In trials, New clues), when it is a ClinicalTrials.gov link.
- **Own lists**: every ClinicalTrials.gov link among the reports of every medicine on the disease's own Open Targets list, as saved by P5 and P6.

| | Count |
|---|---|
| Diseases | 59 |
| Cards in all | 6079 |
| Cards whose link is an NCT link | 1883 |
| Different NCT numbers on cards | 564 |
| Different NCT numbers on own lists | 32155 |
| On both | 142 |
| On cards only (not on the own list of any of the 59) | 422 |
| Different NCT numbers on either | 32577 |

**One thing done differently from the order.** The order says "fetch that one record". The 564 card numbers were each asked alone, one request per record. The other 32013 numbers (on own lists only) were asked in 321 lists of up to 100 numbers per request, because asking them alone would have been about 32,000 requests to a public register. A number a list did not return was to be asked alone afterwards; that happened 0 times. The same fields were asked for both ways.

## A. Status of every NCT link

- NCT numbers the register does not know (404): **0** on cards, **0** on own lists, **0** on either.
- Numbers with no record for any other reason: 0.
- Records that came back under a different number from the one asked: 0.
- Control: the made-up number `NCT99999999` asked alone answered 404; in a list of two with a real number, only the real one came back.

The status words are the register's own (`overallStatus`). `UNKNOWN` is one of the register's words, not a gap in this study.

### A1. Different NCT numbers, by the register's status word

| Status | On cards | On own lists | On either |
|---|---|---|---|
| COMPLETED | 395 | 19389 | 19687 |
| TERMINATED | 37 | 3542 | 3568 |
| UNKNOWN | 61 | 3266 | 3314 |
| RECRUITING | 19 | 2444 | 2459 |
| ACTIVE_NOT_RECRUITING | 17 | 1542 | 1552 |
| WITHDRAWN | 20 | 1082 | 1098 |
| NOT_YET_RECRUITING | 6 | 585 | 590 |
| SUSPENDED | 3 | 87 | 89 |
| ENROLLING_BY_INVITATION | 1 | 80 | 81 |
| NO_LONGER_AVAILABLE | 1 | 72 | 72 |
| APPROVED_FOR_MARKETING | 4 | 41 | 42 |
| AVAILABLE | 0 | 23 | 23 |
| TEMPORARILY_NOT_AVAILABLE | 0 | 2 | 2 |
| **Total** | 564 | 32155 | 32577 |

### A2. Cards with an NCT link, counting every card, by tab

| Status | approved | being_studied | narrower | new_clues | All tabs |
|---|---|---|---|---|---|
| COMPLETED | 2 | 262 | 1 | 1095 | 1360 |
| UNKNOWN | 1 | 36 | 0 | 169 | 206 |
| TERMINATED | 1 | 29 | 0 | 62 | 92 |
| ACTIVE_NOT_RECRUITING | 0 | 13 | 0 | 57 | 70 |
| WITHDRAWN | 0 | 14 | 0 | 40 | 54 |
| RECRUITING | 0 | 15 | 0 | 37 | 52 |
| NOT_YET_RECRUITING | 0 | 4 | 0 | 13 | 17 |
| ENROLLING_BY_INVITATION | 0 | 0 | 0 | 13 | 13 |
| SUSPENDED | 0 | 0 | 0 | 13 | 13 |
| APPROVED_FOR_MARKETING | 4 | 0 | 1 | 0 | 5 |
| NO_LONGER_AVAILABLE | 1 | 0 | 0 | 0 | 1 |
| **Total** | 9 | 373 | 2 | 1499 | 1883 |


### A3. By disease

`a_by_disease.csv` has one row per disease (59 rows) with the status counts for its cards and its own list. `a_records.csv` has one row per NCT number (32577 rows) with status, both dates, conditions and interventions.

### A4. Blank fields

| | Records | No primary completion date | No completion date | No conditions | No interventions |
|---|---|---|---|---|---|
| On cards | 564 | 87 | 30 | 0 | 0 |
| On either | 32577 | 1925 | 1612 | 3 | 0 |

| Date type (the register's word) | Primary completion: cards | Primary completion: either | Completion: cards | Completion: either |
|---|---|---|---|---|
| ACTUAL | 370 | 22991 | 393 | 22115 |
| ESTIMATED | 107 | 7657 | 112 | 8377 |
| no type given | 87 | 1929 | 59 | 2085 |

Study type: on cards 558 INTERVENTIONAL, 1 OBSERVATIONAL, 5 EXPANDED_ACCESS; on either 30461 INTERVENTIONAL, 1977 OBSERVATIONAL, 139 EXPANDED_ACCESS.

## B. Known answers

### NCT05965700

Asked by number. Exactly as the register writes it:

- Status: `COMPLETED`. Primary completion date 2025-12-31 (ACTUAL). Completion date 2026-01-21 (ACTUAL).
- Conditions: "Spinal Cord Injuries"; "Chronic Spinal Cord Injury"; "Subacute Spinal Cord Injury"
- Interventions: DRUG: "NVG-291"; DRUG: "Placebo Injection"
- Among the P5/P6 card links: no. Among the P5/P6 own-list links: no.

### The six medicines

Each name was sent to the register's intervention search (`query.intr`) exactly as written in `known_questions.json`, once alone and once together with condition words (`query.cond`). The register does its own word matching, so a trial can come back whose intervention is written under another name. The tables list every trial the name-alone search returned. "On the saved Open Targets list" compares the NCT number with the own list P6 saved for hemochromatosis, sclerosing cholangitis or neurofibromatosis type 1; no list was saved for mastocytosis. `b_known.csv` has the same rows.

The order wrote "haemochromatosis" and "NF1"; the words sent were "hemochromatosis" and "neurofibromatosis type 1" (the Open Targets names).


**rusfertide**: 6 trials by intervention words alone; 1 together with the condition words "hemochromatosis".

| NCT | Status | Primary completion | Completion | Conditions as written | Interventions as written | Found with condition words | On the saved Open Targets list |
|---|---|---|---|---|---|---|---|
| NCT04202965 | COMPLETED | 2021-10-06 | 2022-02-15 | Hereditary Hemochromatosis | DRUG: PTG-300 | yes | no |
| NCT04767802 | COMPLETED | 2023-03-15 | 2023-03-15 | Polycythemia Vera | DRUG: PTG-300 | no | no |
| NCT05210790 | ACTIVE_NOT_RECRUITING | 2025-02-21 | 2028-08-31 | Polycythemia Vera | DRUG: Rusfertide; DRUG: Placebo | no | no |
| NCT06033586 | ACTIVE_NOT_RECRUITING | 2026-04-01 | 2027-04-01 | Polycythemia Vera | DRUG: Open-label rusfertide | no | no |
| NCT07648030 | RECRUITING | 2027-10-28 | 2030-05-17 | Polycythemia Vera | DRUG: Rusfertide | no | no |
| NCT07765602 | NOT_YET_RECRUITING | 2028-07-01 | 2028-08-01 | Polycythemia Vera | DRUG: Rusfertide | no | no |

**bezuclastinib**: 7 trials by intervention words alone; 3 together with the condition words "mastocytosis".

| NCT | Status | Primary completion | Completion | Conditions as written | Interventions as written | Found with condition words | On the saved Open Targets list |
|---|---|---|---|---|---|---|---|
| NCT04996875 | RECRUITING | 2025-09-19 | 2027-07 | Advanced Systemic Mastocytosis (AdvSM); SM With an Associated Hematologic Neoplasm (SM-AHN); Mast Cell Leukemia (MCL); Aggressive Systemic Mastocytosis (ASM) | DRUG: bezuclastinib | yes | no list saved |
| NCT05186753 | ACTIVE_NOT_RECRUITING | 2025-05-22 | 2030-01 | SSM; Mastocytosis, Indolent; Mastocytosis, Systemic; Mastocytosis; ISM; BMM; Smoldering Systemic Mastocytosis; Bone Marrow Mastocytosis | DRUG: Bezuclastinib Tablets (Formulation A); DRUG: Bezuclastinib Tablets (Formulation B); DRUG: Placebo Tablets | yes | no list saved |
| NCT05208047 | RECRUITING | 2025-09-30 | 2030-01 | Advanced Gastrointestinal Stromal Tumors; Metastatic Cancer | DRUG: Bezuclastinib; DRUG: Bezuclastinib; DRUG: Sunitinib; DRUG: Sunitinib; DRUG: Midazolam; DRUG: Bezuclastinib; DRUG: Sunitinib; DRUG: Bezuclastinib; DRUG: Sunitinib | no | no list saved |
| NCT05489237 | ACTIVE_NOT_RECRUITING | 2027-03-10 | 2027-03-26 | Gastrointestinal Neoplasms; Gastrointestinal Stromal Tumor (GIST); Digestive System Disease; Gastrointestinal Diseases; Metastatic Cancer | DRUG: IDRX-42 | no | no list saved |
| NCT06208748 | ACTIVE_NOT_RECRUITING | 2026-06 | 2027-06 | Gastrointestinal Stromal Tumors; GIST | DRUG: Bezuclastinib in combination with sunitinib | no | no list saved |
| NCT06915766 | AVAILABLE |  |  | Systemic Mastocytoses, Indolent; Systemic Mastocytoses, Aggressive | DRUG: Bezuclastinib | yes | no list saved |
| NCT06948955 | AVAILABLE |  |  | Gastrointestinal Neoplasms, Gastrointestinal Stromal Tumors | DRUG: Bezuclastinib; DRUG: Sunitinib | no | no list saved |

**masitinib**: 38 trials by intervention words alone; 4 together with the condition words "mastocytosis".

| NCT | Status | Primary completion | Completion | Conditions as written | Interventions as written | Found with condition words | On the saved Open Targets list |
|---|---|---|---|---|---|---|---|
| NCT00789633 | COMPLETED | 2011-12-23 | 2012-08-31 | Pancreatic Cancer | DRUG: Masitinib; DRUG: Placebo; DRUG: Gemcitabine | no | no list saved |
| NCT00812240 | TERMINATED | 2018-07 | 2018-07 | Gastrointestinal Stromal Tumors | DRUG: Masitinib; DRUG: Imatinib | no | no list saved |
| NCT00814073 | COMPLETED | 2015-11 | 2015-11 | Indolent Systemic Mastocytosis | DRUG: Masitinib; DRUG: Placebo; OTHER: Best Supportive Care | yes | no list saved |
| NCT00831922 | COMPLETED | 2006-10 |  | Rheumatoid Arthritis | DRUG: masitinib (AB1010); DRUG: masitinib (AB1010) | no | no list saved |
| NCT00831974 | COMPLETED | 2007-02 |  | Mastocytosis | DRUG: masitinib (AB1010); DRUG: masitinib (AB1010) | yes | no list saved |
| NCT00842270 | COMPLETED | 2007-07 |  | Asthma | DRUG: AB1010; DRUG: AB1010; DRUG: AB1010; DRUG: placebo | no | no list saved |
| NCT00866138 | COMPLETED | 2011-01 | 2011-01 | Multiple Myeloma | DRUG: masitinib (AB1010) | no | no list saved |
| NCT00913432 | COMPLETED | 2009-06 | 2010-09 | Rheumatoid Arthritis | DRUG: masitinib; DRUG: masitinib | no | no list saved |
| NCT00976118 | COMPLETED | 2008-07 | 2009-02 | Alzheimer's Disease | DRUG: masitinib (AB1010); DRUG: placebo | no | no list saved |
| NCT00998751 | COMPLETED | 2013-06 | 2013-06 | Gastro-intestinal Stromal Tumours | DRUG: oral masitinib | no | no list saved |
| NCT01045577 | COMPLETED | 2006-01 | 2008-02 | Psoriasis | DRUG: Masitinib; DRUG: Masitinib; DRUG: Placebo | no | no list saved |
| NCT01266369 | COMPLETED | 2007-11 | 2010-05 | Mastocytosis | DRUG: masitinib | yes | no list saved |
| NCT01280565 | TERMINATED | 2019-08 | 2019-08 | Metastatic Melanoma | DRUG: Masitinib; DRUG: Dacarbazine | no | no list saved |
| NCT01410695 | TERMINATED | 2015-10 | 2015-10 | Rheumatoid Arthritis (RA) | DRUG: masitinib 3 mg; DRUG: masitinib 6.0 mg; DRUG: methotrexate; DRUG: Placebo (methotrexate); DRUG: Placebo (masitinib) | no | no list saved |
| NCT01433497 | COMPLETED | 2019-09 | 2020-02 | Multiple Sclerosis, Secondary Progressive; Multiple Sclerosis, Primary Progressive; Multiple Sclerosis, Relapse Free | DRUG: Masitinib; DRUG: Placebo | no | no list saved |
| NCT01449162 | COMPLETED | 2019-11 | 2019-11 | Asthma | DRUG: Masitinib; DRUG: Placebo | no | no list saved |
| NCT01450488 | COMPLETED | 2007-07 | 2010-01 | Multiple Sclerosis | DRUG: masitinib; DRUG: masitinib | no | no list saved |
| NCT01470131 | TERMINATED | 2017-01-04 | 2017-02-01 | Multiple Myeloma | DRUG: Masitinib; DRUG: Placebo; DRUG: Bortezomib; DRUG: Dexamethasone | no | no list saved |
| NCT01506336 | COMPLETED | 2011-09 | 2012-04 | Gastro Intestinal Stromal Tumor | DRUG: masitinib; DRUG: sunitinib | no | no list saved |
| NCT01694277 | COMPLETED | 2020-12 | 2020-12 | Gastrointestinal Stromal Tumors | DRUG: Masitinib; DRUG: Sunitinib | no | no list saved |
| NCT01872598 | COMPLETED | 2020-12 | 2020-12 | Alzheimer Disease | DRUG: Masitinib; DRUG: Placebo; DRUG: Standard of care | no | no list saved |
| NCT02009423 | TERMINATED | 2015-11 | 2015-11 | Gastro-Intestinal Stromal Tumour | DRUG: Masitinib; DRUG: Placebo | no | no list saved |
| NCT02490488 | COMPLETED | 2020-12 | 2020-12 | Ovarian Cancer | DRUG: Masitinib; DRUG: Gemcitabine; DRUG: Placebo | no | no list saved |
| NCT02588677 | COMPLETED | 2016-12-05 | 2018-03 | Amyotrophic Lateral Sclerosis (ALS) | DRUG: Masitinib (4.5); DRUG: Riluzole; DRUG: Placebo; DRUG: Masitinib (3.0) | no | no list saved |
| NCT02605044 | TERMINATED | 2017-12 | 2017-12 | Metastatic Colorectal Cancer | DRUG: Masitinib (AB1010); DRUG: FOLFIRI | no | no list saved |
| NCT03127267 | RECRUITING | 2027-12 | 2027-12 | Amyotrophic Lateral Sclerosis | DRUG: Masitinib (6.0); DRUG: Riluzole; DRUG: Placebo; DRUG: Masitinib (4.5) | no | no list saved |
| NCT03556956 | COMPLETED | 2020-12 | 2020-12 | Colorectal Cancer Metastatic | DRUG: Masitinib | no | no list saved |
| NCT03761225 | COMPLETED | 2020-12-15 | 2020-12-15 | Metastatic Castrate Resistant Prostate Cancer | DRUG: Masitinib; DRUG: Docetaxel; DRUG: Prednisone; DRUG: Placebo | no | no list saved |
| NCT03766295 | COMPLETED | 2020-12 | 2020-12 | Locally Advanced or Metastatic Pancreatic Cancer | DRUG: Masitinib; DRUG: Gemcitabine; DRUG: Placebo | no | no list saved |
| NCT03771040 | COMPLETED | 2020-09 | 2020-09 | Asthma | DRUG: Masitinib; DRUG: Placebo | no | no list saved |
| NCT04333108 | UNKNOWN | 2024-12 | 2025-06 | Indolent Systemic Mastocytosis | DRUG: Masitinib; OTHER: Placebo; OTHER: Best Supportive Care | yes | no list saved |
| NCT04622865 | UNKNOWN | 2023-12 | 2023-12 | SARS-CoV 2; COVID-19; Coronavirus Disease 2019 | DRUG: Masitinib; DRUG: Isoquercetin; DRUG: Best Supportive Care | no | no list saved |
| NCT05047783 | UNKNOWN | 2023-12 | 2023-12 | Covid19; SARS-CoV2 Infection; Coronavirus Disease 2019 | DRUG: Masitinib Mesylate; DRUG: Placebo | no | no list saved |
| NCT05200169 | COMPLETED | 2017-09-01 | 2017-09-01 | Healthy Volunteers | DRUG: 14C-AB1010 | no | no list saved |
| NCT05441488 | SUSPENDED | 2028-12 | 2028-12 | Progressive Multiple Sclerosis | DRUG: Placebo; DRUG: Masitinib (4.5) | no | no list saved |
| NCT05449444 | UNKNOWN | 2024-12-31 | 2024-12-31 | Mast Cell Activation Syndrome | DRUG: Masitinib 4.5 mg/kg/day; DRUG: Placebo; OTHER: Best supportive care; DRUG: Masitinib 6.0 mg/kg/day | no | no list saved |
| NCT05564169 | NOT_YET_RECRUITING | 2028-12 | 2029-12 | Alzheimer Disease | DRUG: Placebo; DRUG: Masitinib (4.5); DRUG: Standard of care | no | no list saved |
| NCT07174492 | NOT_YET_RECRUITING | 2028-12-31 | 2029-12-31 | Amyotrophic Lateral Sclerosis (ALS) | DRUG: Masitinib 4.5 mg/kg/day; DRUG: Placebo; DRUG: Riluzole (100 mg) | no | no list saved |

**norucholic acid**: 4 trials by intervention words alone; 3 together with the condition words "sclerosing cholangitis".

| NCT | Status | Primary completion | Completion | Conditions as written | Interventions as written | Found with condition words | On the saved Open Targets list |
|---|---|---|---|---|---|---|---|
| NCT01755507 | COMPLETED | 2015-10 | 2015-12 | Primary Sclerosing Cholangitis | DRUG: norUDCA; DRUG: Placebo | yes | yes |
| NCT03872921 | UNKNOWN | 2025-01 | 2026-06 | Primary Sclerosing Cholangitis | DRUG: norUrsodeoxycholic Acid | yes | yes |
| NCT05083390 | UNKNOWN | 2025-01 | 2025-04 | Nonalcoholic Steatohepatitis | DRUG: norUrsodeoxycholic acid | no | no |
| NCT06886360 | NOT_YET_RECRUITING | 2027-09 | 2027-09 | Primary Sclerosing Cholangitis | DRUG: norucholic acid | yes | yes |

**PAS-004**: 2 trials by intervention words alone; 1 together with the condition words "neurofibromatosis type 1".

| NCT | Status | Primary completion | Completion | Conditions as written | Interventions as written | Found with condition words | On the saved Open Targets list |
|---|---|---|---|---|---|---|---|
| NCT06299839 | RECRUITING | 2027-09 | 2027-09 | RAS Mutation; NF1 Mutation; RAF Mutation; Advanced Solid Tumors | DRUG: PAS-004 Capsules; DRUG: PAS-004 Tablets | no | no |
| NCT06961565 | RECRUITING | 2028-02 | 2028-02 | NF1 Mutation; Neurofibroma Plexiform; Neurofibroma, Plexiform; Neurofibromatosis Type 1 (NF1)-Related Plexiform Neurofibromas (PNs); Neurofibromatosis Type 1 (NF1) | DRUG: PAS-004 Tablets; DRUG: PAS-004 Capsule | yes | no |

**HLX-1502**: 1 trials by intervention words alone; 1 together with the condition words "neurofibromatosis type 1".

| NCT | Status | Primary completion | Completion | Conditions as written | Interventions as written | Found with condition words | On the saved Open Targets list |
|---|---|---|---|---|---|---|---|
| NCT06541847 | RECRUITING | 2027-06 | 2028-01 | Neurofibromatosis Type 1 | DRUG: HLX-1502 | yes | no |


## C. Ten diseases: registered interventional trials against Open Targets' list

The ten are named in `ten_diseases.json`: five from P6 and five from P5. For each, one search: condition words (`query.cond`) = the disease's Open Targets name unchanged, limited to study type INTERVENTIONAL (`filter.advanced=AREA[StudyType]INTERVENTIONAL`). The register's own total (`totalCount`) is shown beside the NCT numbers actually saved. "Open Targets' list" is the set of NCT numbers on the disease's own list as saved by P5 or P6. NCT numbers only were compared; no name was matched to any medicine.


| Disease (search words) | Register's count of interventional trials | NCT numbers saved | NCT numbers on Open Targets' own list | Registered and on the list | Registered and absent from the list | On the list and not in this search |
|---|---|---|---|---|---|---|
| sclerosing cholangitis | 111 | 111 | 68 | 64 | 47 | 4 |
| primary biliary cholangitis | 251 | 251 | 111 | 102 | 149 | 9 |
| neurofibromatosis type 1 | 191 | 191 | 62 | 55 | 136 | 7 |
| dermatomyositis | 141 | 141 | 68 | 61 | 80 | 7 |
| hemochromatosis | 55 | 55 | 1 | 1 | 54 | 0 |
| Wilson disease | 46 | 46 | 20 | 16 | 30 | 4 |
| Fabry disease | 118 | 118 | 82 | 69 | 49 | 13 |
| narcolepsy | 134 | 134 | 46 | 42 | 92 | 4 |
| hidradenitis suppurativa | 213 | 213 | 125 | 115 | 98 | 10 |
| myasthenia gravis | 237 | 237 | 116 | 110 | 127 | 6 |


All ten together: 1497 registered, 635 of them on the list, **862 absent from the list**; 64 on the list and not in the search. `c_counts.csv` has the same rows.

## What was not verified

- **The register's word matching.** Parts B and C rest on the register's own search. How it matches words (other spellings, other names of a medicine, wider or narrower condition words) was not examined. Other search words would give other counts.
- **Other names of the six medicines.** Only the names in the order were searched. No other name or code was searched on purpose.
- **Why a number is absent or present in part C.** Not looked at. A trial with no medicine, a trial filed under other condition words, and a trial of a medicine Open Targets does not hold would all count the same way here.
- **The two "not in this search" columns.** An own-list number that the condition search did not return was not looked at one by one.
- **Records asked in lists of 100 against records asked alone.** Not compared field by field, beyond the control and the fact that all 32013 came back.
- **Whether a record changed number.** No answer came back under a different number, but old numbers folded into newer records (`NCTIdAlias`) were not searched for.
- **The dates themselves.** Dates are saved as written (some are a year and month only). No date was compared with today or with the status word.
- **P5 and P6.** Their files were taken as they are on their branches. Open Targets was not asked again (data version 26.09, asked 21 Nov 2026). The register's data is stamped 2026-11-20T10:00:05, so the two are a day or two apart.
- **Only fields asked for were saved** for parts A to C. The whole record was saved only for `NCT05965700` (Step 1).
- **The live Moonlight site** was not opened. "Cards" means the cards P5 and P6 built and saved.

## Recount

```
python3 fixtures/probe_p7/analyse.py
```

It uses no network. It reads `inputs/nct_links.json`, `responses/index.jsonl` and the saved answers, and rewrites `counts.json`, `a_records.csv`, `a_by_disease.csv`, `b_known.csv`, `c_counts.csv` and `tables.md`. The tables in this report are pasted from `tables.md`.

`extract_inputs.py` rebuilds `inputs/nct_links.json` from the two branches (needs them fetched). `probe.py` is the script that asked the register; started again, it asks nothing that already has a saved answer.
