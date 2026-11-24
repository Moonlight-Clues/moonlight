# Moonlight label benchmark 1: 24 November 2026

Published 24 November 2026. This file is a dated record. It is not edited after publication, except to fill the three items marked "not yet recorded". The next run gets its own file and is compared with this one.

## Headline

**81% of Approved cards matched the official label** (563 of 691 cards whose label could be read).

| Result | Cards | Share of 691 |
|---|---|---|
| Label supports the approval, fully (YES) | 210 | 30.4% |
| Label supports it for some patients only (PARTIAL) | 353 | 51.1% |
| Label does not support it (NO) | 107 | 15.5% |
| Could not tell (UNCLEAR) | 21 | 3.0% |
| **Read in total** | **691** | |
| No label found, not counted | 106 | |
| **All Approved cards in the 50 diseases** | **797** | |

Goal: 99%, confirmed by doctors.

## What was measured

One question per card: does the official medicine label say this medicine is approved for this disease?

- Snapshot of moonlightclues.com taken 24 Nov 2026, 10:14 IST. Open Targets data 26.09.
- 50 diseases: the ten audited ones and 40 others. How the 40 were picked: not yet recorded here.
- Every card under the Approved tab: 797 cards.
- The label came from the card's own source link where it had one (label_link), or was looked up by medicine name (label_by_name).
- The cards were sent as one offline batch job (a batch API: all requests are submitted together and the answers come back together, with no person steering in between). Each request held one card's label text and the same fixed question.
- An AI model answered (exact model name: not yet recorded here; it will be copied from the batch job's own record). It answered YES, PARTIAL, NO or UNCLEAR, with the sentence from the label it relied on. The prompt and the script: not yet recorded here.
- Code, not the model, then checked that each quoted sentence is present in the label text.
- A YES or PARTIAL counted only if the quoted sentence was found in the label text.

## What this number is not

- **Not checked by a doctor.** A blind sample of 50 cards is waiting for a clinician. Until then this is a machine's reading.
- **Only one direction.** It tests cards that are shown. It says nothing about approved medicines Moonlight fails to show.
- **Only the Approved tab.** Trials and research clues are not measured.
- **Some NO answers are false alarms.** Where the label was looked up by name, the model sometimes read a different product of the same medicine (an eye product, an inhaler for another disease). A hand review of the NO list puts true agreement nearer 85 to 90%. We publish the raw 81% because anyone can reproduce it.
- **PARTIAL is counted as a match.** The medicine is approved, but for a narrower group than the card's disease name suggests. If only YES counted, the figure would be 30%.
- **Mostly US labels.** A medicine approved only elsewhere can score NO or no label.
- 106 cards with no label are left out. Counted against us, the figure is 563 of 797, or 71%.

## How to repeat it

Same 50 diseases, same question, same counting, about once a week. Each run gets a new dated file here. Old files are never edited.

## By disease

The same counts are in `2026-11-24-per-disease.csv` beside this file.

| Disease | Approved cards | Label read | YES | PARTIAL | NO | UNCLEAR | No label |
|---|---|---|---|---|---|---|---|
| pulmonary arterial hypertension | 13 | 12 | 9 | 2 | 1 | 0 | 1 |
| Huntington disease | 6 | 6 | 0 | 2 | 4 | 0 | 0 |
| limb-girdle muscular dystrophy | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| IgA glomerulonephritis | 5 | 5 | 0 | 5 | 0 | 0 | 0 |
| neuromyelitis optica | 4 | 4 | 0 | 4 | 0 | 0 | 0 |
| essential tremor | 1 | 1 | 1 | 0 | 0 | 0 | 0 |
| AL amyloidosis | 2 | 2 | 0 | 1 | 1 | 0 | 0 |
| autosomal dominant polycystic kidney disease | 1 | 1 | 0 | 1 | 0 | 0 | 0 |
| multiple sclerosis symptom measurement | 35 | 35 | 3 | 27 | 2 | 3 | 0 |
| cystic fibrosis | 15 | 15 | 1 | 12 | 2 | 0 | 0 |
| phenylketonuria | 3 | 3 | 1 | 2 | 0 | 0 | 0 |
| Wilson disease | 4 | 3 | 1 | 1 | 0 | 1 | 1 |
| hemophilia A | 18 | 14 | 9 | 5 | 0 | 0 | 4 |
| paroxysmal nocturnal hemoglobinuria | 6 | 6 | 4 | 1 | 1 | 0 | 0 |
| acromegaly | 6 | 6 | 4 | 1 | 1 | 0 | 0 |
| systemic mastocytosis | 3 | 3 | 1 | 2 | 0 | 0 | 0 |
| Graves disease | 4 | 3 | 1 | 2 | 0 | 0 | 1 |
| primary biliary cholangitis | 2 | 1 | 0 | 0 | 1 | 0 | 1 |
| hereditary ATTR amyloidosis | 9 | 9 | 0 | 9 | 0 | 0 | 0 |
| Gaucher disease | 6 | 6 | 0 | 5 | 1 | 0 | 0 |
| Fabry disease | 4 | 3 | 2 | 1 | 0 | 0 | 1 |
| spinal muscular atrophy | 4 | 4 | 2 | 1 | 1 | 0 | 0 |
| Duchenne muscular dystrophy | 8 | 8 | 3 | 5 | 0 | 0 | 0 |
| myasthenia gravis | 12 | 10 | 1 | 5 | 4 | 0 | 2 |
| hereditary angioedema | 9 | 7 | 6 | 1 | 0 | 0 | 2 |
| sickle cell disease | 6 | 5 | 1 | 4 | 0 | 0 | 1 |
| beta thalassemia | 5 | 4 | 0 | 3 | 0 | 1 | 1 |
| amyotrophic lateral sclerosis | 5 | 4 | 2 | 1 | 1 | 0 | 1 |
| glycogen storage disease II | 4 | 4 | 1 | 3 | 0 | 0 | 0 |
| hereditary hemochromatosis | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| systemic lupus erythematosus | 8 | 8 | 7 | 1 | 0 | 0 | 0 |
| rheumatoid arthritis | 69 | 61 | 24 | 29 | 5 | 3 | 8 |
| fibromyalgia | 8 | 5 | 2 | 0 | 2 | 1 | 3 |
| migraine disorder | 44 | 33 | 14 | 10 | 9 | 0 | 11 |
| Crohn disease | 23 | 23 | 3 | 12 | 8 | 0 | 0 |
| ulcerative colitis | 28 | 27 | 9 | 13 | 3 | 2 | 1 |
| type 2 diabetes mellitus | 59 | 48 | 32 | 7 | 8 | 1 | 11 |
| asthma | 70 | 51 | 18 | 24 | 8 | 1 | 19 |
| psoriasis | 43 | 39 | 2 | 28 | 4 | 5 | 4 |
| atopic eczema | 41 | 38 | 4 | 19 | 15 | 0 | 3 |
| Alzheimer disease | 21 | 16 | 2 | 9 | 5 | 0 | 5 |
| gout | 21 | 15 | 3 | 11 | 1 | 0 | 6 |
| chronic obstructive pulmonary disease | 29 | 24 | 13 | 9 | 1 | 1 | 5 |
| hypothyroidism | 8 | 7 | 2 | 0 | 5 | 0 | 1 |
| chronic myeloid leukemia | 9 | 9 | 4 | 5 | 0 | 0 | 0 |
| plasma cell myeloma | 31 | 30 | 3 | 22 | 4 | 1 | 1 |
| melanoma | 20 | 20 | 3 | 13 | 3 | 1 | 0 |
| prostate cancer | 30 | 23 | 1 | 20 | 2 | 0 | 7 |
| colorectal cancer | 19 | 15 | 2 | 10 | 3 | 0 | 4 |
| renal cell carcinoma | 16 | 15 | 9 | 5 | 1 | 0 | 1 |
