# Night watch P4: can the "up or down" data be trusted?

Read-only study. Nothing in moonlight/, web/ or tests/ was changed. Only Open Targets was asked. Every number below was counted by `analyse.py` from the saved answers. **Nothing here is labelled right or wrong.**

## What was done

- Open Targets data version: **26.09**. Run started 2026-11-18T15:46:30Z, finished 2026-11-18T16:51:30Z.
- Diseases studied: **50** (23 COMMON, 7 CANCER, 20 RARE). Ids were read from `fixtures/probe_p3/diseases.json` on the branch `probe-approval-proof`.
- Requests sent to Open Targets: **2728** (1782 target_drugs, 794 disease_drugs, 50 disease, 50 targets, 50 family, 2 data_version), one second apart. Distinct raw answers saved under `responses/`: 1440. `responses/index.jsonl` has one line per request and names the file holding its answer.
- For each disease the probe ran the same functions as `moonlight/api.py`'s `_find`: top 25 proteins, the medicines on each, the disease's own list, one step up and one step down, then `engine.sort_into_tabs`.

## PART A. The direction data

### How Moonlight works out a direction (read from the code)

`moonlight/records.py`, `direction_from_action_types`. Two lists, compared in capital letters:

- **down**: ANTAGONIST, BLOCKER, INHIBITOR
- **up**: ACTIVATOR, AGONIST, OPENER, POSITIVE ALLOSTERIC MODULATOR, POSITIVE MODULATOR
- words from both lists on one medicine-protein pair: **mixed**
- no word from either list: **unknown**

The action words come from one field only: `actionType` in the medicine's `mechanismsOfAction.rows`, and only from rows whose `targets` name this protein (`fetch.py`, `_action_types_on`). A medicine and its tablet forms are one item, so the words of all its forms are pooled.

### A1. Every actionType value met

Counted over **6992** distinct medicine-protein pairs: every medicine family Moonlight met on the 890 proteins it looked at, shown or not (3752 of the pairs are on at least one card). A pair with two action words is counted under both.

| actionType | pairs carrying it | of those, on a card | Moonlight turns it into | on one of Moonlight's two lists? |
|---|---|---|---|---|
| INHIBITOR | 3117 | 1248 | down | yes |
| ANTAGONIST | 797 | 468 | down | yes |
| AGONIST | 771 | 493 | up | yes |
| BLOCKER | 752 | 617 | down | yes |
| POSITIVE ALLOSTERIC MODULATOR | 656 | 509 | up | yes |
| MODULATOR | 183 | 75 | unknown | **NO, not mapped** |
| POSITIVE MODULATOR | 138 | 114 | up | yes |
| STABILISER | 133 | 17 | unknown | **NO, not mapped** |
| PARTIAL AGONIST | 84 | 16 | unknown | **NO, not mapped** |
| DISRUPTING AGENT | 71 | 15 | unknown | **NO, not mapped** |
| ACTIVATOR | 60 | 33 | up | yes |
| BINDING AGENT | 50 | 18 | unknown | **NO, not mapped** |
| EXOGENOUS PROTEIN | 31 | 29 | unknown | **NO, not mapped** |
| INVERSE AGONIST | 29 | 10 | unknown | **NO, not mapped** |
| NEGATIVE ALLOSTERIC MODULATOR | 29 | 23 | unknown | **NO, not mapped** |
| HYDROLYTIC ENZYME | 21 | 21 | unknown | **NO, not mapped** |
| ALLOSTERIC ANTAGONIST | 14 | 14 | unknown | **NO, not mapped** |
| ANTISENSE INHIBITOR | 13 | 1 | unknown | **NO, not mapped** |
| OPENER | 13 | 13 | up | yes |
| RELEASING AGENT | 13 | 8 | unknown | **NO, not mapped** |
| EXOGENOUS GENE | 11 | 9 | unknown | **NO, not mapped** |
| OTHER | 8 | 3 | unknown | **NO, not mapped** |
| DEGRADER | 7 | 2 | unknown | **NO, not mapped** |
| RNAI INHIBITOR | 6 | 1 | unknown | **NO, not mapped** |
| SUBSTRATE | 6 | 5 | unknown | **NO, not mapped** |
| CROSS-LINKING AGENT | 5 | 2 | unknown | **NO, not mapped** |
| VACCINE ANTIGEN | 3 | 0 | unknown | **NO, not mapped** |
| NEGATIVE MODULATOR | 2 | 1 | unknown | **NO, not mapped** |

**Values Moonlight does not map** (they are on neither list, so alone they give "unknown"): MODULATOR (183 pairs), STABILISER (133 pairs), PARTIAL AGONIST (84 pairs), DISRUPTING AGENT (71 pairs), BINDING AGENT (50 pairs), EXOGENOUS PROTEIN (31 pairs), INVERSE AGONIST (29 pairs), NEGATIVE ALLOSTERIC MODULATOR (29 pairs), HYDROLYTIC ENZYME (21 pairs), ALLOSTERIC ANTAGONIST (14 pairs), ANTISENSE INHIBITOR (13 pairs), RELEASING AGENT (13 pairs), EXOGENOUS GENE (11 pairs), OTHER (8 pairs), DEGRADER (7 pairs), RNAI INHIBITOR (6 pairs), SUBSTRATE (6 pairs), CROSS-LINKING AGENT (5 pairs), VACCINE ANTIGEN (3 pairs), NEGATIVE MODULATOR (2 pairs).

Words on Moonlight's lists that were never met on these pairs: none.

Direction of the pairs:

| Moonlight's direction | all pairs | pairs on a card |
|---|---|---|
| down | 4661 | 2331 |
| up | 1636 | 1161 |
| mixed | 1 | 0 |
| unknown | 694 | 260 |

For completeness, every `actionType` in the raw answers, including mechanism rows about proteins Moonlight did not look at (one count per distinct medicine form and mechanism row):

| actionType | mechanism rows | on one of Moonlight's two lists? |
|---|---|---|
| INHIBITOR | 1992 | yes |
| ANTAGONIST | 767 | yes |
| AGONIST | 724 | yes |
| BLOCKER | 187 | yes |
| MODULATOR | 99 | **NO** |
| BINDING AGENT | 92 | **NO** |
| POSITIVE ALLOSTERIC MODULATOR | 76 | yes |
| ACTIVATOR | 60 | yes |
| PARTIAL AGONIST | 51 | **NO** |
| POSITIVE MODULATOR | 35 | yes |
| OPENER | 34 | yes |
| EXOGENOUS PROTEIN | 34 | **NO** |
| RELEASING AGENT | 29 | **NO** |
| STABILISER | 18 | **NO** |
| INVERSE AGONIST | 15 | **NO** |
| NEGATIVE ALLOSTERIC MODULATOR | 14 | **NO** |
| ANTISENSE INHIBITOR | 11 | **NO** |
| EXOGENOUS GENE | 10 | **NO** |
| CROSS-LINKING AGENT | 10 | **NO** |
| SUBSTRATE | 8 | **NO** |
| DEGRADER | 8 | **NO** |
| RNAI INHIBITOR | 7 | **NO** |
| DISRUPTING AGENT | 7 | **NO** |
| OTHER | 7 | **NO** |
| HYDROLYTIC ENZYME | 3 | **NO** |
| VACCINE ANTIGEN | 3 | **NO** |
| NEGATIVE MODULATOR | 2 | **NO** |
| ALLOSTERIC ANTAGONIST | 1 | **NO** |
| PROTEOLYTIC ENZYME | 1 | **NO** |

### A2. Every pair whose direction is "mixed" or "unknown"

**695 pairs** (1 mixed, 694 unknown). 260 of them are on at least one card. Also in `mixed_unknown_pairs.csv`.

| direction | medicine | protein | action words behind it | where it is shown |
|---|---|---|---|---|
| mixed | DILEVALOL | ADRB2 | ANTAGONIST, AGONIST | not shown on any card |
| unknown | ABBV-3373 | NR3C1 | MODULATOR | not shown on any card |
| unknown | ABBV-3373 | TNF | BINDING AGENT | not shown on any card |
| unknown | ABT-560 | CHRNA4 | MODULATOR | not shown on any card |
| unknown | ACOLBIFENE | ESR1 | MODULATOR | not shown on any card |
| unknown | ACOLBIFENE | ESR2 | MODULATOR | not shown on any card |
| unknown | ADIPIPLON | GABRA1 | PARTIAL AGONIST | not shown on any card |
| unknown | ADIPIPLON | GABRA2 | PARTIAL AGONIST | not shown on any card |
| unknown | ADIPIPLON | GABRA3 | PARTIAL AGONIST | not shown on any card |
| unknown | ADIPIPLON | GABRA5 | PARTIAL AGONIST | not shown on any card |
| unknown | ADIPIPLON | GABRA6 | PARTIAL AGONIST | not shown on any card |
| unknown | ADIPIPLON | GABRB1 | PARTIAL AGONIST | not shown on any card |
| unknown | ADIPIPLON | GABRB2 | PARTIAL AGONIST | not shown on any card |
| unknown | ADIPIPLON | GABRB3 | PARTIAL AGONIST | not shown on any card |
| unknown | ADIPIPLON | GABRD | PARTIAL AGONIST | not shown on any card |
| unknown | ADIPIPLON | GABRG1 | PARTIAL AGONIST | not shown on any card |
| unknown | ADIPIPLON | GABRG2 | PARTIAL AGONIST | not shown on any card |
| unknown | ADIPIPLON | GABRG3 | PARTIAL AGONIST | not shown on any card |
| unknown | ADIPIPLON | GABRP | PARTIAL AGONIST | not shown on any card |
| unknown | ADIPIPLON | GABRQ | PARTIAL AGONIST | not shown on any card |
| unknown | ADUCANUMAB | APP | BINDING AGENT | Approved: Alzheimer disease |
| unknown | AFEGOSTAT | GBA1 | STABILISER | not shown on any card |
| unknown | AFELETECAN | TOP1 | STABILISER | not shown on any card |
| unknown | AFIMOXIFENE | ESR1 | MODULATOR | not shown on any card |
| unknown | AFIMOXIFENE | ESR2 | MODULATOR | not shown on any card |
| unknown | AGANIRSEN | IRS1 | ANTISENSE INHIBITOR | not shown on any card |
| unknown | AGN-211745 | FLT1 | RNAI INHIBITOR | not shown on any card |
| unknown | AGS-16C3F | TUBA1B | DISRUPTING AGENT | not shown on any card |
| unknown | AGS-16C3F | TUBA1C | DISRUPTING AGENT | not shown on any card |
| unknown | AGS-16C3F | TUBA3C | DISRUPTING AGENT | not shown on any card |
| unknown | AGS-16C3F | TUBA3E | DISRUPTING AGENT | not shown on any card |
| unknown | AGS-16C3F | TUBA4A | DISRUPTING AGENT | not shown on any card |
| unknown | AGS-16C3F | TUBB | DISRUPTING AGENT | not shown on any card |
| unknown | AGS-16C3F | TUBB1 | DISRUPTING AGENT | not shown on any card |
| unknown | AGS-16C3F | TUBB2A | DISRUPTING AGENT | not shown on any card |
| unknown | AGS-16C3F | TUBB2B | DISRUPTING AGENT | not shown on any card |
| unknown | AGS-16C3F | TUBB3 | DISRUPTING AGENT | not shown on any card |
| unknown | AGS-16C3F | TUBB4A | DISRUPTING AGENT | not shown on any card |
| unknown | AGS-16C3F | TUBB4B | DISRUPTING AGENT | not shown on any card |
| unknown | AGS-16C3F | TUBB6 | DISRUPTING AGENT | not shown on any card |
| unknown | AGS-16C3F | TUBB8 | DISRUPTING AGENT | not shown on any card |
| unknown | ALBUTREPENONACOG ALFA | F9 | EXOGENOUS PROTEIN | Approved: hemophilia B; New clues: hemophilia A |
| unknown | AMCENESTRANT | ESR1 | DEGRADER | not shown on any card |
| unknown | AMG553 | FLT3 | BINDING AGENT | not shown on any card |
| unknown | AMILOMOTIDE | APP | VACCINE ANTIGEN | not shown on any card |
| unknown | AMISELIMOD | S1PR1 | MODULATOR | not shown on any card |
| unknown | AMISELIMOD | S1PR4 | MODULATOR | not shown on any card |
| unknown | AMISELIMOD | S1PR5 | MODULATOR | not shown on any card |
| unknown | AMPHETAMINE | SLC6A2 | RELEASING AGENT | In trials: depressive disorder; Narrower box: narcolepsy; New clues: Huntington disease, atopic eczema, bipolar disorder |
| unknown | AMPHETAMINE | SLC6A3 | RELEASING AGENT | In trials: depressive disorder; Narrower box: narcolepsy; New clues: Alzheimer disease, Huntington disease |
| unknown | ANTIHEMOPHILIC FACTOR, PEGYLATED (MW 20000) HUMAN SEQUENCE RECOMBINANT | F8 | EXOGENOUS PROTEIN | Approved: hemophilia A; In trials: hemophilia B; Wider box: hemophilia B |
| unknown | ANVATABART OPADOTIN | ERBB2 | BINDING AGENT | not shown on any card |
| unknown | APATORSEN | HSPB1 | ANTISENSE INHIBITOR | not shown on any card |
| unknown | APATORSEN SODIUM | HSPB1 | ANTISENSE INHIBITOR | not shown on any card |
| unknown | APIMOSTINEL | GRIN1 | PARTIAL AGONIST | not shown on any card |
| unknown | APIMOSTINEL | GRIN2A | PARTIAL AGONIST | not shown on any card |
| unknown | APIMOSTINEL | GRIN2B | PARTIAL AGONIST | not shown on any card |
| unknown | APIMOSTINEL | GRIN2C | PARTIAL AGONIST | not shown on any card |
| unknown | APIMOSTINEL | GRIN2D | PARTIAL AGONIST | not shown on any card |
| unknown | APIMOSTINEL | GRIN3A | PARTIAL AGONIST | not shown on any card |
| unknown | APIMOSTINEL | GRIN3B | PARTIAL AGONIST | not shown on any card |
| unknown | APLINDORE | DRD2 | PARTIAL AGONIST | not shown on any card |
| unknown | APRUTUMAB IXADOTIN | FGFR2 | BINDING AGENT | not shown on any card |
| unknown | ARHALOFENATE | PPARG | MODULATOR | not shown on any card |
| unknown | ARIPIPRAZOLE | DRD2 | PARTIAL AGONIST | Approved: bipolar disorder, schizophrenia; Narrower box: depressive disorder; New clues: Huntington disease, Parkinson disease, acromegaly |
| unknown | ARIPIPRAZOLE | HTR1A | PARTIAL AGONIST | Approved: bipolar disorder, schizophrenia; Narrower box: depressive disorder |
| unknown | ARIPIPRAZOLE LAUROXIL | DRD2 | PARTIAL AGONIST | Approved: schizophrenia; New clues: Huntington disease, Parkinson disease, acromegaly, bipolar disorder, depressive disorder |
| unknown | ARIPIPRAZOLE LAUROXIL | HTR1A | PARTIAL AGONIST | Approved: schizophrenia; New clues: bipolar disorder, depressive disorder |
| unknown | ARZOXIFENE | ESR1 | MODULATOR | Approved: breast cancer; In trials: osteoporosis; New clues: acromegaly, endometriosis |
| unknown | ARZOXIFENE | ESR2 | MODULATOR | In trials: osteoporosis |
| unknown | ASOPRISNIL | PGR | MODULATOR | not shown on any card |
| unknown | ATAGABALIN | CACNA1A | MODULATOR | not shown on any card |
| unknown | ATAGABALIN | CACNA1C | MODULATOR | not shown on any card |
| unknown | ATAGABALIN | CACNA1D | MODULATOR | not shown on any card |
| unknown | ATALUREN | RPL13 | MODULATOR | In trials: hemophilia B |
| unknown | ATALUREN | RPL13A | MODULATOR | Approved: Duchenne muscular dystrophy |
| unknown | ATALUREN | RPL17 | MODULATOR | In trials: hemophilia A |
| unknown | ATALUREN | RPL18A | MODULATOR | In trials: hemophilia A, hemophilia B |
| unknown | ATALUREN | RPL23A | MODULATOR | In trials: hemophilia B |
| unknown | ATALUREN | RPL27 | MODULATOR | In trials: hemophilia B |
| unknown | ATALUREN | RPL3 | MODULATOR | Approved: Duchenne muscular dystrophy |
| unknown | ATALUREN | RPL30 | MODULATOR | Approved: Duchenne muscular dystrophy |
| unknown | ATALUREN | RPL31 | MODULATOR | In trials: hemophilia A |
| unknown | ATALUREN | RPL35 | MODULATOR | In trials: hemophilia B |
| unknown | ATALUREN | RPL36 | MODULATOR | In trials: hemophilia A, hemophilia B |
| unknown | ATALUREN | RPL36A | MODULATOR | Approved: Duchenne muscular dystrophy |
| unknown | ATALUREN | RPL38 | MODULATOR | In trials: cystic fibrosis |
| unknown | ATALUREN | RPL41 | MODULATOR | In trials: hemophilia B |
| unknown | ATALUREN | RPL5 | MODULATOR | In trials: hemophilia A, hemophilia B |
| unknown | ATALUREN | RPL7 | MODULATOR | In trials: hemophilia B |
| unknown | ATALUREN | RPLP1 | MODULATOR | Approved: Duchenne muscular dystrophy; In trials: hemophilia B |
| unknown | ATALUREN | RPS10 | MODULATOR | In trials: hemophilia A |
| unknown | ATALUREN | RPS12 | MODULATOR | In trials: hemophilia B |
| unknown | ATALUREN | RPS13 | MODULATOR | Approved: Duchenne muscular dystrophy |
| unknown | ATALUREN | RPS15 | MODULATOR | In trials: hemophilia B |
| unknown | ATALUREN | RPS17 | MODULATOR | In trials: hemophilia A |
| unknown | ATALUREN | RPS19 | MODULATOR | Approved: Duchenne muscular dystrophy |
| unknown | ATALUREN | RPS20 | MODULATOR | In trials: hemophilia A, hemophilia B |
| unknown | ATALUREN | RPS21 | MODULATOR | In trials: hemophilia A, hemophilia B |
| unknown | ATALUREN | RPS27 | MODULATOR | In trials: hemophilia B |
| unknown | ATALUREN | RPS27A | MODULATOR | Approved: Duchenne muscular dystrophy; In trials: cystic fibrosis; New clues: tuberculosis |
| unknown | ATALUREN | RPS3 | MODULATOR | In trials: hemophilia B |
| unknown | ATALUREN | RPS4Y1 | MODULATOR | In trials: hemophilia A, hemophilia B |
| unknown | ATALUREN | RPS5 | MODULATOR | Approved: Duchenne muscular dystrophy |
| unknown | ATALUREN | RPS6 | MODULATOR | Approved: Duchenne muscular dystrophy; In trials: hemophilia A, hemophilia B |
| unknown | ATALUREN | RPS7 | MODULATOR | In trials: hemophilia B |
| unknown | ATALUREN | RPS9 | MODULATOR | In trials: hemophilia B |
| unknown | ATALUREN | RPSA | MODULATOR | Approved: Duchenne muscular dystrophy |
| unknown | ATX08-001 | PPARG | MODULATOR | not shown on any card |
| unknown | AUTOLOGOUS CD34+ ENRICHED CELL FRACTION THAT CONTAINS CD34+ CELLS TRANSDUCED WITH RETROVIRAL VECTOR THAT ENCODES FOR THE HUMAN ADA CDNA SEQUENCE | ADA | EXOGENOUS GENE | New clues: Fabry disease |
| unknown | AVE-9633 | CD33 | BINDING AGENT | not shown on any card |
| unknown | AZD-5423 | NR3C1 | MODULATOR | not shown on any card |
| unknown | AZD3514 | AR | MODULATOR | not shown on any card |
| unknown | BALAGLITAZONE | PPARG | PARTIAL AGONIST | not shown on any card |
| unknown | BALCINRENONE | NR3C2 | MODULATOR | not shown on any card |
| unknown | BAMOSIRAN | ADRB2 | RNAI INHIBITOR | not shown on any card |
| unknown | BAPINEUZUMAB | APP | BINDING AGENT | not shown on any card |
| unknown | BAZEDOXIFENE | ESR1 | MODULATOR | Approved: osteoporosis; In trials: breast cancer; New clues: acromegaly, endometriosis |
| unknown | BAZEDOXIFENE | ESR2 | MODULATOR | Approved: osteoporosis |
| unknown | BENZPHETAMINE | SLC6A2 | RELEASING AGENT | New clues: Huntington disease, atopic eczema, bipolar disorder, depressive disorder, narcolepsy |
| unknown | BENZQUINAMIDE | DRD2 | MODULATOR | New clues: Huntington disease, Parkinson disease, acromegaly, bipolar disorder, depressive disorder, schizophrenia |
| unknown | BEREMAGENE GEPERPAVEC | COL7A1 | EXOGENOUS GENE | New clues: hereditary angioedema |
| unknown | BETHANIDINE | SLC6A2 | SUBSTRATE | New clues: Huntington disease, atopic eczema, bipolar disorder, depressive disorder, narcolepsy |
| unknown | BETIBEGLOGENE AUTOTEMCEL | HBB | EXOGENOUS GENE | New clues: malaria |
| unknown | BEVASIRANIB | VEGFA | RNAI INHIBITOR | not shown on any card |
| unknown | BIFEPRUNOX | DRD2 | PARTIAL AGONIST | not shown on any card |
| unknown | BIFEPRUNOX | HTR1A | PARTIAL AGONIST | not shown on any card |
| unknown | BILASTINE | HRH1 | INVERSE AGONIST | Approved: atopic eczema |
| unknown | BINTRAFUSP ALFA | TGFB1 | BINDING AGENT | not shown on any card |
| unknown | BINTRAFUSP ALFA | TGFB3 | BINDING AGENT | not shown on any card |
| unknown | BMS-275183 | TUBA1B | STABILISER | not shown on any card |
| unknown | BMS-275183 | TUBA1C | STABILISER | not shown on any card |
| unknown | BMS-275183 | TUBA3C | STABILISER | not shown on any card |
| unknown | BMS-275183 | TUBA3E | STABILISER | not shown on any card |
| unknown | BMS-275183 | TUBA4A | STABILISER | not shown on any card |
| unknown | BMS-275183 | TUBB | STABILISER | not shown on any card |
| unknown | BMS-275183 | TUBB1 | STABILISER | not shown on any card |
| unknown | BMS-275183 | TUBB2A | STABILISER | not shown on any card |
| unknown | BMS-275183 | TUBB2B | STABILISER | not shown on any card |
| unknown | BMS-275183 | TUBB3 | STABILISER | not shown on any card |
| unknown | BMS-275183 | TUBB4A | STABILISER | not shown on any card |
| unknown | BMS-275183 | TUBB4B | STABILISER | not shown on any card |
| unknown | BMS-275183 | TUBB6 | STABILISER | not shown on any card |
| unknown | BMS-275183 | TUBB8 | STABILISER | not shown on any card |
| unknown | BRETYLIUM | SLC6A2 | SUBSTRATE | New clues: Huntington disease, atopic eczema, bipolar disorder, depressive disorder, narcolepsy |
| unknown | BREXPIPRAZOLE | DRD2 | PARTIAL AGONIST | Approved: schizophrenia; In trials: bipolar disorder, depressive disorder; Narrower box: depressive disorder; New clues: Huntington disease, Parkinson disease, acromegaly |
| unknown | BREXPIPRAZOLE | HTR1A | PARTIAL AGONIST | Approved: schizophrenia; In trials: bipolar disorder, depressive disorder; Narrower box: depressive disorder |
| unknown | BRILANESTRANT | ESR1 | DEGRADER | not shown on any card |
| unknown | BUSPIRONE | HTR1A | PARTIAL AGONIST | Approved: depressive disorder; In trials: schizophrenia; New clues: bipolar disorder |
| unknown | CAMIZESTRANT | ESR1 | DEGRADER | not shown on any card |
| unknown | CAPADENOSON | ADORA1 | PARTIAL AGONIST | not shown on any card |
| unknown | CAPESEROD | HTR4 | PARTIAL AGONIST | not shown on any card |
| unknown | CAPROMAB | KLK3 | BINDING AGENT | Approved: prostate cancer |
| unknown | CARIPRAZINE | DRD2 | MODULATOR | Approved: bipolar disorder, schizophrenia; New clues: Huntington disease, Parkinson disease, acromegaly, depressive disorder |
| unknown | CARIPRAZINE | DRD3 | MODULATOR | Approved: bipolar disorder, schizophrenia; New clues: Huntington disease, Parkinson disease, acromegaly, depressive disorder |
| unknown | CATUMAXOMAB | EPCAM | CROSS-LINKING AGENT | New clues: colorectal cancer |
| unknown | CELIPROLOL | ADRB2 | PARTIAL AGONIST | New clues: asthma, chronic obstructive pulmonary disease, glaucoma, heart failure |
| unknown | CEMDISIRAN | C5 | RNAI INHIBITOR | not shown on any card |
| unknown | CENERIMOD | S1PR1 | MODULATOR | not shown on any card |
| unknown | CENERSEN | TP53 | ANTISENSE INHIBITOR | not shown on any card |
| unknown | CENERSEN SODIUM | TP53 | ANTISENSE INHIBITOR | not shown on any card |
| unknown | CETUXIMAB SAROTALOCAN | EGFR | BINDING AGENT | New clues: breast cancer, colorectal cancer, hereditary angioedema, lung cancer |
| unknown | CHF4227 | ESR1 | MODULATOR | not shown on any card |
| unknown | CHF4227 | ESR2 | MODULATOR | not shown on any card |
| unknown | CHLORMADINONE ACETATE | PGR | MODULATOR | not shown on any card |
| unknown | CHLOROTRIANISENE | ESR2 | MODULATOR | New clues: osteoporosis |
| unknown | CHLORPHENTERMINE | SLC6A4 | SUBSTRATE | not shown on any card |
| unknown | CINTREDEKIN BESUDOTOX | IL4R | BINDING AGENT | not shown on any card |
| unknown | CITATUZUMAB BOGATOX | EPCAM | BINDING AGENT | not shown on any card |
| unknown | CJM-112 | IL17A | BINDING AGENT | not shown on any card |
| unknown | CLOMIPHENE | ESR1 | MODULATOR | In trials: acromegaly; New clues: breast cancer, osteoporosis |
| unknown | COAGULATION FACTOR IX HUMAN | F9 | EXOGENOUS PROTEIN | Approved: hemophilia B; Wider box: hemophilia A |
| unknown | COAGULATION FACTOR IX RECOMBINANT HUMAN | F9 | EXOGENOUS PROTEIN | Approved: hemophilia B; In trials: hemophilia A; Wider box: hemophilia A |
| unknown | COAGULATION FACTOR VII HUMAN | F7 | EXOGENOUS PROTEIN | not shown on any card |
| unknown | COAGULATION FACTOR X HUMAN | F10 | EXOGENOUS PROTEIN | New clues: atrial fibrillation, hemophilia A |
| unknown | COFIRASERSEN | SCNN1A | ANTISENSE INHIBITOR | not shown on any card |
| unknown | COFIRASERSEN | SCNN1B | ANTISENSE INHIBITOR | not shown on any card |
| unknown | COFIRASERSEN | SCNN1G | ANTISENSE INHIBITOR | not shown on any card |
| unknown | COLLAGENASE CLOSTRIDIUM HISTOLYTICUM | COL11A1 | HYDROLYTIC ENZYME | Approved: sarcoidosis |
| unknown | COLLAGENASE CLOSTRIDIUM HISTOLYTICUM | COL18A1 | HYDROLYTIC ENZYME | Approved: sarcoidosis; New clues: glaucoma, hereditary angioedema |
| unknown | COLLAGENASE CLOSTRIDIUM HISTOLYTICUM | COL1A1 | HYDROLYTIC ENZYME | Approved: sarcoidosis; New clues: osteoporosis, phenylketonuria |
| unknown | COLLAGENASE CLOSTRIDIUM HISTOLYTICUM | COL1A2 | HYDROLYTIC ENZYME | Approved: sarcoidosis; New clues: osteoporosis |
| unknown | COLLAGENASE CLOSTRIDIUM HISTOLYTICUM | COL27A1 | HYDROLYTIC ENZYME | Approved: sarcoidosis |
| unknown | COLLAGENASE CLOSTRIDIUM HISTOLYTICUM | COL2A1 | HYDROLYTIC ENZYME | Approved: sarcoidosis |
| unknown | COLLAGENASE CLOSTRIDIUM HISTOLYTICUM | COL4A1 | HYDROLYTIC ENZYME | Approved: sarcoidosis |
| unknown | COLLAGENASE CLOSTRIDIUM HISTOLYTICUM | COL4A3 | HYDROLYTIC ENZYME | New clues: chronic kidney disease |
| unknown | COLLAGENASE CLOSTRIDIUM HISTOLYTICUM | COL4A4 | HYDROLYTIC ENZYME | New clues: chronic kidney disease |
| unknown | COLLAGENASE CLOSTRIDIUM HISTOLYTICUM | COL5A2 | HYDROLYTIC ENZYME | Approved: sarcoidosis |
| unknown | CONESTAT ALFA | SERPING1 | EXOGENOUS PROTEIN | Approved: hereditary angioedema |
| unknown | CONTUSUGENE LADENOVEC | TP53 | EXOGENOUS GENE | not shown on any card |
| unknown | CP-601927 | CHRNA4 | PARTIAL AGONIST | not shown on any card |
| unknown | CRAVACITINIB | TYK2 | NEGATIVE ALLOSTERIC MODULATOR | Approved: psoriasis; In trials: hidradenitis suppurativa, sarcoidosis, ulcerative colitis; New clues: hypothyroidism, rheumatoid arthritis |
| unknown | CYCLOFENIL | ESR1 | MODULATOR | not shown on any card |
| unknown | CYCLOFENIL | ESR2 | MODULATOR | not shown on any card |
| unknown | CYTISINICLINE | CHRNA4 | PARTIAL AGONIST | New clues: chronic obstructive pulmonary disease |
| unknown | DAMOCTOCOG ALFA PEGOL | F8 | EXOGENOUS PROTEIN | Approved: hemophilia A; New clues: hemophilia B |
| unknown | DAVUNETIDE | TUBA1B | STABILISER | not shown on any card |
| unknown | DAVUNETIDE | TUBA1C | STABILISER | not shown on any card |
| unknown | DAVUNETIDE | TUBA3C | STABILISER | not shown on any card |
| unknown | DAVUNETIDE | TUBA3E | STABILISER | not shown on any card |
| unknown | DAVUNETIDE | TUBA4A | STABILISER | not shown on any card |
| unknown | DAVUNETIDE | TUBB | STABILISER | not shown on any card |
| unknown | DAVUNETIDE | TUBB1 | STABILISER | not shown on any card |
| unknown | DAVUNETIDE | TUBB2A | STABILISER | not shown on any card |
| unknown | DAVUNETIDE | TUBB2B | STABILISER | not shown on any card |
| unknown | DAVUNETIDE | TUBB3 | STABILISER | not shown on any card |
| unknown | DAVUNETIDE | TUBB4A | STABILISER | not shown on any card |
| unknown | DAVUNETIDE | TUBB4B | STABILISER | not shown on any card |
| unknown | DAVUNETIDE | TUBB6 | STABILISER | not shown on any card |
| unknown | DAVUNETIDE | TUBB8 | STABILISER | not shown on any card |
| unknown | DECOGLURANT | GRM3 | MODULATOR | not shown on any card |
| unknown | DELANDISTROGENE MOXEPARVOVEC | DMD | EXOGENOUS GENE | In trials: Duchenne muscular dystrophy |
| unknown | DEPATUXIZUMAB MAFODOTIN | EGFR | BINDING AGENT | not shown on any card |
| unknown | DEXTROAMPHETAMINE | SLC6A2 | RELEASING AGENT | Approved: narcolepsy; In trials: bipolar disorder, depressive disorder; New clues: Huntington disease, atopic eczema |
| unknown | DEXTROAMPHETAMINE | SLC6A3 | RELEASING AGENT | Approved: narcolepsy; In trials: depressive disorder; New clues: Alzheimer disease, Huntington disease |
| unknown | DIANICLINE | CHRNA4 | PARTIAL AGONIST | not shown on any card |
| unknown | DIMETHYLCURCUMIN | AR | DEGRADER | not shown on any card |
| unknown | DISITAMAB VEDOTIN | ERBB2 | BINDING AGENT | In trials: breast cancer, colorectal cancer; New clues: lung cancer |
| unknown | DISITAMAB VEDOTIN | TUBA1B | DISRUPTING AGENT | New clues: gout |
| unknown | DISITAMAB VEDOTIN | TUBA1C | DISRUPTING AGENT | In trials: prostate cancer; New clues: gout |
| unknown | DISITAMAB VEDOTIN | TUBA3C | DISRUPTING AGENT | New clues: gout |
| unknown | DISITAMAB VEDOTIN | TUBA3E | DISRUPTING AGENT | New clues: gout |
| unknown | DISITAMAB VEDOTIN | TUBA4A | DISRUPTING AGENT | New clues: amyotrophic lateral sclerosis, gout |
| unknown | DISITAMAB VEDOTIN | TUBB | DISRUPTING AGENT | New clues: gout |
| unknown | DISITAMAB VEDOTIN | TUBB1 | DISRUPTING AGENT | New clues: gout |
| unknown | DISITAMAB VEDOTIN | TUBB2A | DISRUPTING AGENT | New clues: gout |
| unknown | DISITAMAB VEDOTIN | TUBB2B | DISRUPTING AGENT | New clues: gout |
| unknown | DISITAMAB VEDOTIN | TUBB3 | DISRUPTING AGENT | New clues: gout |
| unknown | DISITAMAB VEDOTIN | TUBB4A | DISRUPTING AGENT | New clues: gout |
| unknown | DISITAMAB VEDOTIN | TUBB4B | DISRUPTING AGENT | New clues: gout |
| unknown | DISITAMAB VEDOTIN | TUBB6 | DISRUPTING AGENT | New clues: gout |
| unknown | DISITAMAB VEDOTIN | TUBB8 | DISRUPTING AGENT | New clues: gout |
| unknown | DONANEMAB | APP | DISRUPTING AGENT | Approved: Alzheimer disease |
| unknown | DROLOXIFENE | ESR1 | MODULATOR | not shown on any card |
| unknown | DROLOXIFENE | ESR2 | MODULATOR | not shown on any card |
| unknown | EBASTINE | HRH1 | INVERSE AGONIST | Wider box: atopic eczema |
| unknown | EDRECOLOMAB | EPCAM | CROSS-LINKING AGENT | Approved: colorectal cancer |
| unknown | EFANESOCTOCOG ALFA | F8 | EXOGENOUS PROTEIN | Approved: hemophilia A; New clues: hemophilia B |
| unknown | EFAPROXIRAL | HBB | NEGATIVE MODULATOR | New clues: malaria |
| unknown | EFMOROCTOCOG ALFA | F8 | EXOGENOUS PROTEIN | Approved: hemophilia A; In trials: hemophilia B; Wider box: hemophilia B |
| unknown | EFTRENONACOG ALFA | F9 | EXOGENOUS PROTEIN | Approved: hemophilia B; In trials: hemophilia A |
| unknown | ELACESTRANT | ESR1 | DEGRADER | Approved: breast cancer; New clues: acromegaly, endometriosis, osteoporosis |
| unknown | ELADOCAGENE EXUPARVOVEC | DDC | EXOGENOUS GENE | In trials: Parkinson disease |
| unknown | ELX-02 | RPL13 | MODULATOR | not shown on any card |
| unknown | ELX-02 | RPL13A | MODULATOR | not shown on any card |
| unknown | ELX-02 | RPL17 | MODULATOR | not shown on any card |
| unknown | ELX-02 | RPL18A | MODULATOR | not shown on any card |
| unknown | ELX-02 | RPL23A | MODULATOR | not shown on any card |
| unknown | ELX-02 | RPL27 | MODULATOR | not shown on any card |
| unknown | ELX-02 | RPL3 | MODULATOR | not shown on any card |
| unknown | ELX-02 | RPL30 | MODULATOR | not shown on any card |
| unknown | ELX-02 | RPL31 | MODULATOR | not shown on any card |
| unknown | ELX-02 | RPL35 | MODULATOR | not shown on any card |
| unknown | ELX-02 | RPL36 | MODULATOR | not shown on any card |
| unknown | ELX-02 | RPL36A | MODULATOR | not shown on any card |
| unknown | ELX-02 | RPL38 | MODULATOR | not shown on any card |
| unknown | ELX-02 | RPL41 | MODULATOR | not shown on any card |
| unknown | ELX-02 | RPL5 | MODULATOR | not shown on any card |
| unknown | ELX-02 | RPL7 | MODULATOR | not shown on any card |
| unknown | ELX-02 | RPLP1 | MODULATOR | not shown on any card |
| unknown | ELX-02 | RPS10 | MODULATOR | not shown on any card |
| unknown | ELX-02 | RPS12 | MODULATOR | not shown on any card |
| unknown | ELX-02 | RPS13 | MODULATOR | not shown on any card |
| unknown | ELX-02 | RPS15 | MODULATOR | not shown on any card |
| unknown | ELX-02 | RPS17 | MODULATOR | not shown on any card |
| unknown | ELX-02 | RPS19 | MODULATOR | not shown on any card |
| unknown | ELX-02 | RPS20 | MODULATOR | not shown on any card |
| unknown | ELX-02 | RPS21 | MODULATOR | not shown on any card |
| unknown | ELX-02 | RPS27 | MODULATOR | not shown on any card |
| unknown | ELX-02 | RPS27A | MODULATOR | not shown on any card |
| unknown | ELX-02 | RPS3 | MODULATOR | not shown on any card |
| unknown | ELX-02 | RPS4Y1 | MODULATOR | not shown on any card |
| unknown | ELX-02 | RPS5 | MODULATOR | not shown on any card |
| unknown | ELX-02 | RPS6 | MODULATOR | not shown on any card |
| unknown | ELX-02 | RPS7 | MODULATOR | not shown on any card |
| unknown | ELX-02 | RPS9 | MODULATOR | not shown on any card |
| unknown | ELX-02 | RPSA | MODULATOR | not shown on any card |
| unknown | EMICIZUMAB | F10 | OTHER | Approved: hemophilia A; New clues: atrial fibrillation |
| unknown | EMICIZUMAB | F9 | OTHER | Approved: hemophilia A; New clues: hemophilia B |
| unknown | ENCLOMIPHENE | ESR1 | MODULATOR | not shown on any card |
| unknown | ENOBOSARM | AR | MODULATOR | not shown on any card |
| unknown | EPOTHILONE D | TUBA1B | STABILISER | not shown on any card |
| unknown | EPOTHILONE D | TUBA1C | STABILISER | not shown on any card |
| unknown | EPOTHILONE D | TUBA3C | STABILISER | not shown on any card |
| unknown | EPOTHILONE D | TUBA3E | STABILISER | not shown on any card |
| unknown | EPOTHILONE D | TUBA4A | STABILISER | not shown on any card |
| unknown | EPOTHILONE D | TUBB | STABILISER | not shown on any card |
| unknown | EPOTHILONE D | TUBB1 | STABILISER | not shown on any card |
| unknown | EPOTHILONE D | TUBB2A | STABILISER | not shown on any card |
| unknown | EPOTHILONE D | TUBB2B | STABILISER | not shown on any card |
| unknown | EPOTHILONE D | TUBB3 | STABILISER | not shown on any card |
| unknown | EPOTHILONE D | TUBB4A | STABILISER | not shown on any card |
| unknown | EPOTHILONE D | TUBB4B | STABILISER | not shown on any card |
| unknown | EPOTHILONE D | TUBB6 | STABILISER | not shown on any card |
| unknown | EPOTHILONE D | TUBB8 | STABILISER | not shown on any card |
| unknown | EPRENETAPOPT | TP53 | STABILISER | not shown on any card |
| unknown | EPTACOG ALFA (ACTIVATED) | F7 | EXOGENOUS PROTEIN | Approved: hemophilia A, hemophilia B |
| unknown | EPTACOG BETA (ACTIVATED) | F7 | EXOGENOUS PROTEIN | Approved: hemophilia A, hemophilia B |
| unknown | ERTUMAXOMAB | ERBB2 | CROSS-LINKING AGENT | not shown on any card |
| unknown | ESKETAMINE | GRIN1 | NEGATIVE ALLOSTERIC MODULATOR | Approved: depressive disorder; New clues: Alzheimer disease |
| unknown | ESKETAMINE | GRIN2A | NEGATIVE ALLOSTERIC MODULATOR | Approved: depressive disorder; In trials: bipolar disorder, schizophrenia; New clues: Alzheimer disease, epilepsy |
| unknown | ESKETAMINE | GRIN2B | NEGATIVE ALLOSTERIC MODULATOR | Approved: depressive disorder; New clues: Alzheimer disease, phenylketonuria |
| unknown | ESKETAMINE | GRIN2C | NEGATIVE ALLOSTERIC MODULATOR | New clues: Alzheimer disease |
| unknown | ESKETAMINE | GRIN2D | NEGATIVE ALLOSTERIC MODULATOR | New clues: Alzheimer disease |
| unknown | ESKETAMINE | GRIN3A | NEGATIVE ALLOSTERIC MODULATOR | Approved: depressive disorder; New clues: Alzheimer disease |
| unknown | ESKETAMINE | GRIN3B | NEGATIVE ALLOSTERIC MODULATOR | New clues: Alzheimer disease |
| unknown | ESTRAMUSTINE PHOSPHATE | ESR2 | MODULATOR | New clues: osteoporosis |
| unknown | ESTRIOL | ESR1 | MODULATOR | In trials: breast cancer; New clues: acromegaly, endometriosis, osteoporosis |
| unknown | ESTRIOL | ESR2 | MODULATOR | New clues: osteoporosis |
| unknown | ETOKIMAB | IL33 | BINDING AGENT | not shown on any card |
| unknown | ETRANACOGENE DEZAPARVOVEC | F9 | EXOGENOUS PROTEIN | Approved: hemophilia B; New clues: hemophilia A |
| unknown | ETRASIMOD | S1PR4 | MODULATOR | Approved: ulcerative colitis |
| unknown | ETRASIMOD | S1PR5 | MODULATOR | Approved: ulcerative colitis |
| unknown | FIDANACOGENE ELAPARVOVEC | F9 | EXOGENOUS GENE | Approved: hemophilia B; New clues: hemophilia A |
| unknown | FISPEMIFENE | ESR1 | MODULATOR | not shown on any card |
| unknown | FISPEMIFENE | ESR2 | MODULATOR | not shown on any card |
| unknown | FITUSIRAN | SERPINC1 | RNAI INHIBITOR | In trials: hemophilia A, hemophilia B |
| unknown | FLUMAZENIL | GABRA1 | ALLOSTERIC ANTAGONIST | New clues: depressive disorder, epilepsy, malaria |
| unknown | FLUMAZENIL | GABRA2 | ALLOSTERIC ANTAGONIST | New clues: depressive disorder |
| unknown | FLUMAZENIL | GABRA3 | ALLOSTERIC ANTAGONIST | New clues: malaria |
| unknown | FLUMAZENIL | GABRA5 | ALLOSTERIC ANTAGONIST | New clues: depressive disorder, malaria |
| unknown | FLUMAZENIL | GABRA6 | ALLOSTERIC ANTAGONIST | New clues: depressive disorder, malaria |
| unknown | FLUMAZENIL | GABRB1 | ALLOSTERIC ANTAGONIST | New clues: depressive disorder, malaria |
| unknown | FLUMAZENIL | GABRB2 | ALLOSTERIC ANTAGONIST | New clues: depressive disorder, epilepsy |
| unknown | FLUMAZENIL | GABRB3 | ALLOSTERIC ANTAGONIST | New clues: epilepsy, malaria |
| unknown | FLUMAZENIL | GABRD | ALLOSTERIC ANTAGONIST | New clues: malaria |
| unknown | FLUMAZENIL | GABRG1 | ALLOSTERIC ANTAGONIST | New clues: malaria |
| unknown | FLUMAZENIL | GABRG2 | ALLOSTERIC ANTAGONIST | New clues: depressive disorder, epilepsy, malaria |
| unknown | FLUMAZENIL | GABRG3 | ALLOSTERIC ANTAGONIST | New clues: depressive disorder |
| unknown | FLUMAZENIL | GABRP | ALLOSTERIC ANTAGONIST | New clues: malaria |
| unknown | FLUMAZENIL | GABRQ | ALLOSTERIC ANTAGONIST | New clues: malaria |
| unknown | FOSDAGROCORAT | NR3C1 | MODULATOR | not shown on any card |
| unknown | GABAPENTIN | CACNA1A | MODULATOR | Approved: epilepsy; New clues: phenylketonuria |
| unknown | GABAPENTIN | CACNA1C | MODULATOR | In trials: bipolar disorder; New clues: atrial fibrillation |
| unknown | GABAPENTIN | CACNA1D | MODULATOR | New clues: atrial fibrillation, heart failure |
| unknown | GABAPENTIN ENACARBIL | CACNA1A | MODULATOR | New clues: epilepsy, phenylketonuria |
| unknown | GABAPENTIN ENACARBIL | CACNA1C | MODULATOR | New clues: atrial fibrillation, bipolar disorder |
| unknown | GABAPENTIN ENACARBIL | CACNA1D | MODULATOR | New clues: atrial fibrillation, heart failure |
| unknown | GANCOTAMAB | ERBB2 | BINDING AGENT | not shown on any card |
| unknown | GANTENERUMAB | APP | BINDING AGENT | not shown on any card |
| unknown | GEMTUZUMAB | CD33 | BINDING AGENT | not shown on any card |
| unknown | GEMTUZUMAB OZOGAMICIN | CD33 | BINDING AGENT | not shown on any card |
| unknown | GEVOKIZUMAB | IL1B | NEGATIVE ALLOSTERIC MODULATOR | not shown on any card |
| unknown | GIREDESTRANT | ESR1 | DEGRADER | not shown on any card |
| unknown | GIROCTOCOGENE FITELPARVOVEC | F8 | EXOGENOUS GENE | not shown on any card |
| unknown | GLPG0492 | AR | MODULATOR | not shown on any card |
| unknown | GS-9667 | ADORA1 | PARTIAL AGONIST | not shown on any card |
| unknown | GSK2849466 | AR | MODULATOR | not shown on any card |
| unknown | GSK2881078 | AR | MODULATOR | not shown on any card |
| unknown | GSK933776 | APP | BINDING AGENT | not shown on any card |
| unknown | GTI-2040 | RRM2 | ANTISENSE INHIBITOR | not shown on any card |
| unknown | GUANADREL | SLC6A2 | SUBSTRATE | New clues: Huntington disease, atopic eczema, bipolar disorder, depressive disorder, narcolepsy |
| unknown | GUANETHIDINE | SLC6A2 | SUBSTRATE | New clues: Huntington disease, atopic eczema, bipolar disorder, depressive disorder, narcolepsy |
| unknown | HALOPERIDOL | DRD2 | INVERSE AGONIST | Approved: schizophrenia; In trials: Huntington disease, bipolar disorder; New clues: Parkinson disease, acromegaly, depressive disorder |
| unknown | HALOPERIDOL | DRD3 | INVERSE AGONIST | Approved: schizophrenia; In trials: Huntington disease, bipolar disorder; New clues: Parkinson disease, acromegaly, depressive disorder |
| unknown | HALOPERIDOL | DRD4 | INVERSE AGONIST | Approved: schizophrenia; In trials: Huntington disease, bipolar disorder; New clues: acromegaly, depressive disorder |
| unknown | HALOPERIDOL DECANOATE | DRD2 | INVERSE AGONIST | Approved: schizophrenia; New clues: Huntington disease, Parkinson disease, acromegaly, bipolar disorder, depressive disorder |
| unknown | HALOPERIDOL DECANOATE | DRD3 | INVERSE AGONIST | Approved: schizophrenia; New clues: Huntington disease, Parkinson disease, acromegaly, bipolar disorder, depressive disorder |
| unknown | HALOPERIDOL DECANOATE | DRD4 | INVERSE AGONIST | Approved: schizophrenia; New clues: Huntington disease, acromegaly, bipolar disorder, depressive disorder |
| unknown | HE3235 | AR | MODULATOR | not shown on any card |
| unknown | HUMAN COAGULATION FACTOR VIII | F8 | EXOGENOUS PROTEIN | In trials: hemophilia A; New clues: hemophilia B |
| unknown | IBERDOMIDE | CRBN | MODULATOR | not shown on any card |
| unknown | IBERDOMIDE | CUL4A | MODULATOR | not shown on any card |
| unknown | IBERDOMIDE | DDB1 | MODULATOR | not shown on any card |
| unknown | IBERDOMIDE | RBX1 | MODULATOR | not shown on any card |
| unknown | IDOXIFENE | ESR1 | MODULATOR | not shown on any card |
| unknown | IDOXIFENE | ESR2 | MODULATOR | not shown on any card |
| unknown | IGN-101 | EPCAM | BINDING AGENT | not shown on any card |
| unknown | IMAGABALIN | CACNA1A | MODULATOR | not shown on any card |
| unknown | IMAGABALIN | CACNA1C | MODULATOR | not shown on any card |
| unknown | IMAGABALIN | CACNA1D | MODULATOR | not shown on any card |
| unknown | ING-1 | EPCAM | OTHER | not shown on any card |
| unknown | INT131 | PPARG | MODULATOR | not shown on any card |
| unknown | IOBENGUANE | SLC6A2 | SUBSTRATE | New clues: Huntington disease, atopic eczema, bipolar disorder, depressive disorder, narcolepsy |
| unknown | ISPRONICLINE | CHRNA4 | PARTIAL AGONIST | not shown on any card |
| unknown | KETAMINE | GRIN1 | NEGATIVE ALLOSTERIC MODULATOR | In trials: Parkinson disease, depressive disorder; New clues: Alzheimer disease |
| unknown | KETAMINE | GRIN2A | NEGATIVE ALLOSTERIC MODULATOR | In trials: Parkinson disease, bipolar disorder, depressive disorder, epilepsy, schizophrenia; New clues: Alzheimer disease |
| unknown | KETAMINE | GRIN2B | NEGATIVE ALLOSTERIC MODULATOR | In trials: Parkinson disease, depressive disorder; New clues: Alzheimer disease, phenylketonuria |
| unknown | KETAMINE | GRIN2C | NEGATIVE ALLOSTERIC MODULATOR | New clues: Alzheimer disease |
| unknown | KETAMINE | GRIN2D | NEGATIVE ALLOSTERIC MODULATOR | New clues: Alzheimer disease |
| unknown | KETAMINE | GRIN3A | NEGATIVE ALLOSTERIC MODULATOR | In trials: depressive disorder; New clues: Alzheimer disease |
| unknown | KETAMINE | GRIN3B | NEGATIVE ALLOSTERIC MODULATOR | New clues: Alzheimer disease |
| unknown | KOS-1584 | TUBA1B | STABILISER | not shown on any card |
| unknown | KOS-1584 | TUBA1C | STABILISER | not shown on any card |
| unknown | KOS-1584 | TUBA3C | STABILISER | not shown on any card |
| unknown | KOS-1584 | TUBA3E | STABILISER | not shown on any card |
| unknown | KOS-1584 | TUBA4A | STABILISER | not shown on any card |
| unknown | KOS-1584 | TUBB | STABILISER | not shown on any card |
| unknown | KOS-1584 | TUBB1 | STABILISER | not shown on any card |
| unknown | KOS-1584 | TUBB2A | STABILISER | not shown on any card |
| unknown | KOS-1584 | TUBB2B | STABILISER | not shown on any card |
| unknown | KOS-1584 | TUBB3 | STABILISER | not shown on any card |
| unknown | KOS-1584 | TUBB4A | STABILISER | not shown on any card |
| unknown | KOS-1584 | TUBB4B | STABILISER | not shown on any card |
| unknown | KOS-1584 | TUBB6 | STABILISER | not shown on any card |
| unknown | KOS-1584 | TUBB8 | STABILISER | not shown on any card |
| unknown | LADARIXIN | CXCR2 | MODULATOR | not shown on any card |
| unknown | LARAZOTIDE | CHRNA3 | PARTIAL AGONIST | not shown on any card |
| unknown | LAROTAXEL | TUBA1B | STABILISER | not shown on any card |
| unknown | LAROTAXEL | TUBA1C | STABILISER | not shown on any card |
| unknown | LAROTAXEL | TUBA3C | STABILISER | not shown on any card |
| unknown | LAROTAXEL | TUBA3E | STABILISER | not shown on any card |
| unknown | LAROTAXEL | TUBA4A | STABILISER | not shown on any card |
| unknown | LAROTAXEL | TUBB | STABILISER | not shown on any card |
| unknown | LAROTAXEL | TUBB1 | STABILISER | not shown on any card |
| unknown | LAROTAXEL | TUBB2A | STABILISER | not shown on any card |
| unknown | LAROTAXEL | TUBB2B | STABILISER | not shown on any card |
| unknown | LAROTAXEL | TUBB3 | STABILISER | not shown on any card |
| unknown | LAROTAXEL | TUBB4A | STABILISER | not shown on any card |
| unknown | LAROTAXEL | TUBB4B | STABILISER | not shown on any card |
| unknown | LAROTAXEL | TUBB6 | STABILISER | not shown on any card |
| unknown | LAROTAXEL | TUBB8 | STABILISER | not shown on any card |
| unknown | LASOFOXIFENE | ESR1 | MODULATOR | Approved: osteoporosis; In trials: breast cancer; New clues: acromegaly, endometriosis |
| unknown | LASOFOXIFENE | ESR2 | MODULATOR | Approved: osteoporosis |
| unknown | LGD-2941 | AR | MODULATOR | not shown on any card |
| unknown | LINTUZUMAB | CD33 | OTHER | not shown on any card |
| unknown | LISDEXAMFETAMINE | SLC6A2 | RELEASING AGENT | Approved: Huntington disease, atopic eczema; In trials: bipolar disorder; New clues: depressive disorder, narcolepsy |
| unknown | LISDEXAMFETAMINE | SLC6A3 | RELEASING AGENT | Approved: Alzheimer disease, Huntington disease; New clues: depressive disorder, narcolepsy |
| unknown | LONOCTOCOG ALFA | F8 | EXOGENOUS PROTEIN | Approved: hemophilia A; In trials: hemophilia B; Wider box: hemophilia B |
| unknown | LOSATUXIZUMAB VEDOTIN | EGFR | BINDING AGENT | not shown on any card |
| unknown | LOVOTIBEGLOGENE AUTOTEMCEL | HBB | EXOGENOUS GENE | New clues: malaria |
| unknown | LUMACAFTOR | CFTR | STABILISER | Approved: cystic fibrosis; New clues: chronic obstructive pulmonary disease |
| unknown | LUTETIUM OXODOTREOTIDE | SSTR1 | BINDING AGENT | New clues: Cushing syndrome, acromegaly |
| unknown | LUTETIUM OXODOTREOTIDE | SSTR2 | BINDING AGENT | New clues: Cushing syndrome, acromegaly |
| unknown | LUTETIUM OXODOTREOTIDE | SSTR3 | BINDING AGENT | New clues: Cushing syndrome, acromegaly |
| unknown | LUTETIUM OXODOTREOTIDE | SSTR4 | BINDING AGENT | New clues: acromegaly |
| unknown | LUTETIUM OXODOTREOTIDE | SSTR5 | BINDING AGENT | New clues: Cushing syndrome, acromegaly |
| unknown | LY2452473 | AR | MODULATOR | not shown on any card |
| unknown | LYM-1 | HLA-DRB1 | OTHER | not shown on any card |
| unknown | MBX-2044 | PPARG | MODULATOR | not shown on any card |
| unknown | MDX-447 | EGFR | CROSS-LINKING AGENT | not shown on any card |
| unknown | MECAMYLAMINE | CHRNA3 | NEGATIVE ALLOSTERIC MODULATOR | New clues: chronic obstructive pulmonary disease |
| unknown | MEMANTINE | GRIN1 | NEGATIVE ALLOSTERIC MODULATOR | Approved: Alzheimer disease; In trials: Parkinson disease, depressive disorder |
| unknown | MEMANTINE | GRIN2A | NEGATIVE ALLOSTERIC MODULATOR | Approved: Alzheimer disease; In trials: Parkinson disease, bipolar disorder, depressive disorder, epilepsy, schizophrenia |
| unknown | MEMANTINE | GRIN2B | NEGATIVE ALLOSTERIC MODULATOR | Approved: Alzheimer disease; In trials: Parkinson disease, depressive disorder; New clues: phenylketonuria |
| unknown | MEMANTINE | GRIN2C | NEGATIVE ALLOSTERIC MODULATOR | Approved: Alzheimer disease |
| unknown | MEMANTINE | GRIN2D | NEGATIVE ALLOSTERIC MODULATOR | Approved: Alzheimer disease |
| unknown | MEMANTINE | GRIN3A | NEGATIVE ALLOSTERIC MODULATOR | Approved: Alzheimer disease; In trials: depressive disorder |
| unknown | MEMANTINE | GRIN3B | NEGATIVE ALLOSTERIC MODULATOR | Approved: Alzheimer disease |
| unknown | METHYLERGONOVINE | HTR2B | PARTIAL AGONIST | New clues: schizophrenia |
| unknown | METHYSERGIDE | HTR1A | PARTIAL AGONIST | New clues: bipolar disorder, depressive disorder, schizophrenia |
| unknown | MIDOMAFETAMINE | SLC6A2 | RELEASING AGENT | not shown on any card |
| unknown | MIDOMAFETAMINE | SLC6A3 | RELEASING AGENT | not shown on any card |
| unknown | MIDOMAFETAMINE | SLC6A4 | RELEASING AGENT | not shown on any card |
| unknown | MIFAMURTIDE ACID | NOD2 | OTHER | New clues: Behcet disease, sarcoidosis |
| unknown | MIGALASTAT | GLA | STABILISER | Approved: Fabry disease |
| unknown | MK-0249 | HRH3 | INVERSE AGONIST | not shown on any card |
| unknown | MK-0533 | PPARG | MODULATOR | not shown on any card |
| unknown | MK-0773 | AR | MODULATOR | not shown on any card |
| unknown | MOC31-PE | EPCAM | BINDING AGENT | not shown on any card |
| unknown | MOFAROTENE | RARA | MODULATOR | not shown on any card |
| unknown | MOFAROTENE | RARB | MODULATOR | not shown on any card |
| unknown | MOFAROTENE | RARG | MODULATOR | not shown on any card |
| unknown | MOFAROTENE | RXRA | MODULATOR | not shown on any card |
| unknown | MOROCTOCOG ALFA | F8 | EXOGENOUS PROTEIN | Approved: hemophilia A; In trials: hemophilia B; Wider box: hemophilia B |
| unknown | NELOTANSERIN | HTR2A | INVERSE AGONIST | not shown on any card |
| unknown | NETOGLITAZONE | PPARG | MODULATOR | not shown on any card |
| unknown | NONACOG BETA PEGOL | F9 | EXOGENOUS PROTEIN | Approved: hemophilia B; New clues: hemophilia A |
| unknown | OCRIPLASMIN | COL11A1 | HYDROLYTIC ENZYME | New clues: sarcoidosis |
| unknown | OCRIPLASMIN | COL18A1 | HYDROLYTIC ENZYME | New clues: hereditary angioedema, sarcoidosis; Wider box: glaucoma |
| unknown | OCRIPLASMIN | COL1A1 | HYDROLYTIC ENZYME | New clues: osteoporosis, phenylketonuria, sarcoidosis |
| unknown | OCRIPLASMIN | COL1A2 | HYDROLYTIC ENZYME | New clues: osteoporosis, sarcoidosis |
| unknown | OCRIPLASMIN | COL27A1 | HYDROLYTIC ENZYME | New clues: sarcoidosis |
| unknown | OCRIPLASMIN | COL2A1 | HYDROLYTIC ENZYME | New clues: sarcoidosis |
| unknown | OCRIPLASMIN | COL4A1 | HYDROLYTIC ENZYME | New clues: sarcoidosis |
| unknown | OCRIPLASMIN | COL4A3 | HYDROLYTIC ENZYME | New clues: chronic kidney disease |
| unknown | OCRIPLASMIN | COL4A4 | HYDROLYTIC ENZYME | New clues: chronic kidney disease |
| unknown | OCRIPLASMIN | COL5A2 | HYDROLYTIC ENZYME | New clues: sarcoidosis |
| unknown | OCRIPLASMIN | LAMB4 | HYDROLYTIC ENZYME | New clues: Fabry disease |
| unknown | OCTOCOG ALFA | F8 | EXOGENOUS PROTEIN | Approved: hemophilia A; In trials: hemophilia B; Wider box: hemophilia B |
| unknown | OMFILOCTOCOG ALFA | F8 | EXOGENOUS PROTEIN | In trials: hemophilia A; New clues: hemophilia B |
| unknown | ONASEMNOGENE ABEPARVOVEC | SMN1 | EXOGENOUS GENE | Approved: spinal muscular atrophy |
| unknown | ONASEMNOGENE ABEPARVOVEC | SMN2 | EXOGENOUS GENE | Approved: spinal muscular atrophy |
| unknown | ONCOLYSIN M | CD33 | BINDING AGENT | not shown on any card |
| unknown | ONVITRELIN UCALONTIDE | GNRHR | BINDING AGENT | not shown on any card |
| unknown | OPORTUZUMAB MONATOX | EPCAM | BINDING AGENT | New clues: colorectal cancer |
| unknown | ORDOPIDINE | DRD2 | MODULATOR | not shown on any card |
| unknown | OSOCIMAB | F11 | NEGATIVE ALLOSTERIC MODULATOR | not shown on any card |
| unknown | OSPEMIFENE | ESR1 | MODULATOR | New clues: acromegaly, breast cancer, endometriosis, osteoporosis |
| unknown | OSPEMIFENE | ESR2 | MODULATOR | New clues: osteoporosis |
| unknown | OZANIMOD | S1PR1 | MODULATOR | Approved: ulcerative colitis |
| unknown | OZANIMOD | S1PR5 | MODULATOR | Approved: ulcerative colitis |
| unknown | PACLITAXEL DOCOSAHEXAENOIC ACID | TUBA1B | STABILISER | not shown on any card |
| unknown | PACLITAXEL DOCOSAHEXAENOIC ACID | TUBA1C | STABILISER | not shown on any card |
| unknown | PACLITAXEL DOCOSAHEXAENOIC ACID | TUBA3C | STABILISER | not shown on any card |
| unknown | PACLITAXEL DOCOSAHEXAENOIC ACID | TUBA3E | STABILISER | not shown on any card |
| unknown | PACLITAXEL DOCOSAHEXAENOIC ACID | TUBA4A | STABILISER | not shown on any card |
| unknown | PACLITAXEL DOCOSAHEXAENOIC ACID | TUBB | STABILISER | not shown on any card |
| unknown | PACLITAXEL DOCOSAHEXAENOIC ACID | TUBB1 | STABILISER | not shown on any card |
| unknown | PACLITAXEL DOCOSAHEXAENOIC ACID | TUBB2A | STABILISER | not shown on any card |
| unknown | PACLITAXEL DOCOSAHEXAENOIC ACID | TUBB2B | STABILISER | not shown on any card |
| unknown | PACLITAXEL DOCOSAHEXAENOIC ACID | TUBB3 | STABILISER | not shown on any card |
| unknown | PACLITAXEL DOCOSAHEXAENOIC ACID | TUBB4A | STABILISER | not shown on any card |
| unknown | PACLITAXEL DOCOSAHEXAENOIC ACID | TUBB4B | STABILISER | not shown on any card |
| unknown | PACLITAXEL DOCOSAHEXAENOIC ACID | TUBB6 | STABILISER | not shown on any card |
| unknown | PACLITAXEL DOCOSAHEXAENOIC ACID | TUBB8 | STABILISER | not shown on any card |
| unknown | PACLITAXEL POLIGLUMEX | TUBA1B | STABILISER | New clues: gout |
| unknown | PACLITAXEL POLIGLUMEX | TUBA1C | STABILISER | In trials: prostate cancer; New clues: gout |
| unknown | PACLITAXEL POLIGLUMEX | TUBA3C | STABILISER | New clues: gout |
| unknown | PACLITAXEL POLIGLUMEX | TUBA3E | STABILISER | New clues: gout |
| unknown | PACLITAXEL POLIGLUMEX | TUBA4A | STABILISER | New clues: amyotrophic lateral sclerosis, gout |
| unknown | PACLITAXEL POLIGLUMEX | TUBB | STABILISER | New clues: gout |
| unknown | PACLITAXEL POLIGLUMEX | TUBB1 | STABILISER | New clues: gout |
| unknown | PACLITAXEL POLIGLUMEX | TUBB2A | STABILISER | New clues: gout |
| unknown | PACLITAXEL POLIGLUMEX | TUBB2B | STABILISER | New clues: gout |
| unknown | PACLITAXEL POLIGLUMEX | TUBB3 | STABILISER | New clues: gout |
| unknown | PACLITAXEL POLIGLUMEX | TUBB4A | STABILISER | New clues: gout |
| unknown | PACLITAXEL POLIGLUMEX | TUBB4B | STABILISER | New clues: gout |
| unknown | PACLITAXEL POLIGLUMEX | TUBB6 | STABILISER | New clues: gout |
| unknown | PACLITAXEL POLIGLUMEX | TUBB8 | STABILISER | New clues: gout |
| unknown | PADSEVONIL | GABRA1 | PARTIAL AGONIST | not shown on any card |
| unknown | PADSEVONIL | GABRA2 | PARTIAL AGONIST | not shown on any card |
| unknown | PADSEVONIL | GABRA3 | PARTIAL AGONIST | not shown on any card |
| unknown | PADSEVONIL | GABRA5 | PARTIAL AGONIST | not shown on any card |
| unknown | PADSEVONIL | GABRA6 | PARTIAL AGONIST | not shown on any card |
| unknown | PADSEVONIL | GABRB1 | PARTIAL AGONIST | not shown on any card |
| unknown | PADSEVONIL | GABRB2 | PARTIAL AGONIST | not shown on any card |
| unknown | PADSEVONIL | GABRB3 | PARTIAL AGONIST | not shown on any card |
| unknown | PADSEVONIL | GABRD | PARTIAL AGONIST | not shown on any card |
| unknown | PADSEVONIL | GABRG1 | PARTIAL AGONIST | not shown on any card |
| unknown | PADSEVONIL | GABRG2 | PARTIAL AGONIST | not shown on any card |
| unknown | PADSEVONIL | GABRG3 | PARTIAL AGONIST | not shown on any card |
| unknown | PADSEVONIL | GABRP | PARTIAL AGONIST | not shown on any card |
| unknown | PADSEVONIL | GABRQ | PARTIAL AGONIST | not shown on any card |
| unknown | PARDOPRUNOX | DRD2 | PARTIAL AGONIST | not shown on any card |
| unknown | PARDOPRUNOX | DRD3 | PARTIAL AGONIST | not shown on any card |
| unknown | PATUPILONE | TUBA1B | STABILISER | not shown on any card |
| unknown | PATUPILONE | TUBA1C | STABILISER | not shown on any card |
| unknown | PATUPILONE | TUBA3C | STABILISER | not shown on any card |
| unknown | PATUPILONE | TUBA3E | STABILISER | not shown on any card |
| unknown | PATUPILONE | TUBA4A | STABILISER | not shown on any card |
| unknown | PATUPILONE | TUBB | STABILISER | not shown on any card |
| unknown | PATUPILONE | TUBB1 | STABILISER | not shown on any card |
| unknown | PATUPILONE | TUBB2A | STABILISER | not shown on any card |
| unknown | PATUPILONE | TUBB2B | STABILISER | not shown on any card |
| unknown | PATUPILONE | TUBB3 | STABILISER | not shown on any card |
| unknown | PATUPILONE | TUBB4A | STABILISER | not shown on any card |
| unknown | PATUPILONE | TUBB4B | STABILISER | not shown on any card |
| unknown | PATUPILONE | TUBB6 | STABILISER | not shown on any card |
| unknown | PATUPILONE | TUBB8 | STABILISER | not shown on any card |
| unknown | PENTAZOCINE | SIGMAR1 | MODULATOR | New clues: amyotrophic lateral sclerosis |
| unknown | PF-00217830 | DRD2 | PARTIAL AGONIST | not shown on any card |
| unknown | PHENTERMINE | SLC6A2 | RELEASING AGENT | not shown on any card |
| unknown | PHENYLPROPANOLAMINE | SLC6A2 | RELEASING AGENT | not shown on any card |
| unknown | PIFUSERTIB | AKT1 | NEGATIVE ALLOSTERIC MODULATOR | not shown on any card |
| unknown | PIFUSERTIB | AKT2 | NEGATIVE ALLOSTERIC MODULATOR | not shown on any card |
| unknown | PIMAVANSERIN | HTR2A | INVERSE AGONIST | In trials: depressive disorder, schizophrenia; New clues: Huntington disease, bipolar disorder; Wider box: schizophrenia |
| unknown | PINDOLOL | ADRB1 | PARTIAL AGONIST | New clues: glaucoma, heart failure |
| unknown | PINDOLOL | ADRB2 | PARTIAL AGONIST | New clues: asthma, chronic obstructive pulmonary disease, glaucoma, heart failure |
| unknown | PITOLISANT | HRH3 | INVERSE AGONIST | Approved: narcolepsy |
| unknown | PLOVAMER ACETATE | HLA-DRB1 | MODULATOR | not shown on any card |
| unknown | PONEZUMAB | APP | BINDING AGENT | not shown on any card |
| unknown | POZANICLINE | CHRNA4 | PARTIAL AGONIST | not shown on any card |
| unknown | PRASINEZUMAB | SNCA | BINDING AGENT | not shown on any card |
| unknown | PREGABALIN | CACNA1A | MODULATOR | Approved: epilepsy; New clues: phenylketonuria |
| unknown | PREGABALIN | CACNA1C | MODULATOR | New clues: atrial fibrillation, bipolar disorder |
| unknown | PREGABALIN | CACNA1D | MODULATOR | New clues: atrial fibrillation, heart failure |
| unknown | PREXIGEBERSEN | GRB2 | ANTISENSE INHIBITOR | not shown on any card |
| unknown | PRIDOPIDINE | DRD2 | MODULATOR | not shown on any card |
| unknown | PRILIXIMAB | CD4 | NEGATIVE MODULATOR | not shown on any card |
| unknown | PROTHROMBIN COMPLEX CONCENTRATE | F10 | EXOGENOUS PROTEIN | New clues: atrial fibrillation, hemophilia A |
| unknown | PROTHROMBIN COMPLEX CONCENTRATE | F7 | EXOGENOUS PROTEIN | New clues: hemophilia A, hemophilia B |
| unknown | PROTHROMBIN COMPLEX CONCENTRATE | F9 | EXOGENOUS PROTEIN | New clues: hemophilia A, hemophilia B |
| unknown | PRX-03140 | HTR4 | PARTIAL AGONIST | not shown on any card |
| unknown | PSEUDOEPHEDRINE | SLC6A2 | RELEASING AGENT | New clues: Huntington disease, bipolar disorder, depressive disorder, narcolepsy; Wider box: atopic eczema |
| unknown | PUMOSETRAG | HTR3A | PARTIAL AGONIST | not shown on any card |
| unknown | PUMOSETRAG | HTR3B | PARTIAL AGONIST | not shown on any card |
| unknown | PUMOSETRAG | HTR3C | PARTIAL AGONIST | not shown on any card |
| unknown | PUMOSETRAG | HTR3D | PARTIAL AGONIST | not shown on any card |
| unknown | PUMOSETRAG | HTR3E | PARTIAL AGONIST | not shown on any card |
| unknown | RALOXIFENE | ESR1 | MODULATOR | Approved: breast cancer, osteoporosis; In trials: endometriosis; New clues: acromegaly |
| unknown | RALOXIFENE | ESR2 | MODULATOR | Approved: osteoporosis |
| unknown | RAPASTINEL | GRIN1 | PARTIAL AGONIST | not shown on any card |
| unknown | RAPASTINEL | GRIN2A | PARTIAL AGONIST | not shown on any card |
| unknown | RAPASTINEL | GRIN2B | PARTIAL AGONIST | not shown on any card |
| unknown | RAPASTINEL | GRIN2C | PARTIAL AGONIST | not shown on any card |
| unknown | RAPASTINEL | GRIN2D | PARTIAL AGONIST | not shown on any card |
| unknown | RAPASTINEL | GRIN3A | PARTIAL AGONIST | not shown on any card |
| unknown | RAPASTINEL | GRIN3B | PARTIAL AGONIST | not shown on any card |
| unknown | REPARIXIN | CXCR2 | MODULATOR | not shown on any card |
| unknown | RESEQUINIL | GABRA1 | INVERSE AGONIST | not shown on any card |
| unknown | RESEQUINIL | GABRA2 | INVERSE AGONIST | not shown on any card |
| unknown | RESEQUINIL | GABRA3 | INVERSE AGONIST | not shown on any card |
| unknown | RESEQUINIL | GABRA5 | INVERSE AGONIST | not shown on any card |
| unknown | RESEQUINIL | GABRA6 | INVERSE AGONIST | not shown on any card |
| unknown | RESEQUINIL | GABRB1 | INVERSE AGONIST | not shown on any card |
| unknown | RESEQUINIL | GABRB2 | INVERSE AGONIST | not shown on any card |
| unknown | RESEQUINIL | GABRB3 | INVERSE AGONIST | not shown on any card |
| unknown | RESEQUINIL | GABRD | INVERSE AGONIST | not shown on any card |
| unknown | RESEQUINIL | GABRG1 | INVERSE AGONIST | not shown on any card |
| unknown | RESEQUINIL | GABRG2 | INVERSE AGONIST | not shown on any card |
| unknown | RESEQUINIL | GABRG3 | INVERSE AGONIST | not shown on any card |
| unknown | RESEQUINIL | GABRP | INVERSE AGONIST | not shown on any card |
| unknown | RESEQUINIL | GABRQ | INVERSE AGONIST | not shown on any card |
| unknown | RG-7636 | EDNRB | BINDING AGENT | not shown on any card |
| unknown | RINDOPEPIMUT | EGFR | VACCINE ANTIGEN | not shown on any card |
| unknown | SAGOPILONE | TUBA1B | STABILISER | not shown on any card |
| unknown | SAGOPILONE | TUBA1C | STABILISER | not shown on any card |
| unknown | SAGOPILONE | TUBA3C | STABILISER | not shown on any card |
| unknown | SAGOPILONE | TUBA3E | STABILISER | not shown on any card |
| unknown | SAGOPILONE | TUBA4A | STABILISER | not shown on any card |
| unknown | SAGOPILONE | TUBB | STABILISER | not shown on any card |
| unknown | SAGOPILONE | TUBB1 | STABILISER | not shown on any card |
| unknown | SAGOPILONE | TUBB2A | STABILISER | not shown on any card |
| unknown | SAGOPILONE | TUBB2B | STABILISER | not shown on any card |
| unknown | SAGOPILONE | TUBB3 | STABILISER | not shown on any card |
| unknown | SAGOPILONE | TUBB4A | STABILISER | not shown on any card |
| unknown | SAGOPILONE | TUBB4B | STABILISER | not shown on any card |
| unknown | SAGOPILONE | TUBB6 | STABILISER | not shown on any card |
| unknown | SAGOPILONE | TUBB8 | STABILISER | not shown on any card |
| unknown | SARIZOTAN | DRD2 | PARTIAL AGONIST | not shown on any card |
| unknown | SDX-101 | RXRA | MODULATOR | not shown on any card |
| unknown | SERIDOPIDINE | DRD2 | MODULATOR | not shown on any card |
| unknown | SIMOCTOCOG ALFA | F8 | EXOGENOUS PROTEIN | Approved: hemophilia A; New clues: hemophilia B |
| unknown | SIPAGLADENANT | ADORA2A | INVERSE AGONIST | not shown on any card |
| unknown | SIPULEUCEL-T | ACP3 | BINDING AGENT | Approved: prostate cancer |
| unknown | SOLANEZUMAB | APP | BINDING AGENT | not shown on any card |
| unknown | SOLITOMAB | EPCAM | CROSS-LINKING AGENT | not shown on any card |
| unknown | SUSOCTOCOG ALFA | F8 | EXOGENOUS PROTEIN | Approved: hemophilia A; New clues: hemophilia B |
| unknown | SUVN-G3031 | HRH3 | INVERSE AGONIST | not shown on any card |
| unknown | T-62 | ADORA1 | MODULATOR | not shown on any card |
| unknown | T-900607 | TUBA1B | DISRUPTING AGENT | not shown on any card |
| unknown | T-900607 | TUBA1C | DISRUPTING AGENT | not shown on any card |
| unknown | T-900607 | TUBA3C | DISRUPTING AGENT | not shown on any card |
| unknown | T-900607 | TUBA3E | DISRUPTING AGENT | not shown on any card |
| unknown | T-900607 | TUBA4A | DISRUPTING AGENT | not shown on any card |
| unknown | T-900607 | TUBB | DISRUPTING AGENT | not shown on any card |
| unknown | T-900607 | TUBB1 | DISRUPTING AGENT | not shown on any card |
| unknown | T-900607 | TUBB2A | DISRUPTING AGENT | not shown on any card |
| unknown | T-900607 | TUBB2B | DISRUPTING AGENT | not shown on any card |
| unknown | T-900607 | TUBB3 | DISRUPTING AGENT | not shown on any card |
| unknown | T-900607 | TUBB4A | DISRUPTING AGENT | not shown on any card |
| unknown | T-900607 | TUBB4B | DISRUPTING AGENT | not shown on any card |
| unknown | T-900607 | TUBB6 | DISRUPTING AGENT | not shown on any card |
| unknown | T-900607 | TUBB8 | DISRUPTING AGENT | not shown on any card |
| unknown | TALSACLIDINE | CHRM2 | PARTIAL AGONIST | not shown on any card |
| unknown | TALSACLIDINE | CHRM3 | PARTIAL AGONIST | not shown on any card |
| unknown | TAMOXIFEN | ESR1 | MODULATOR | Approved: breast cancer; In trials: osteoporosis; New clues: acromegaly, endometriosis |
| unknown | TARENFLURBIL | APH1B | MODULATOR | not shown on any card |
| unknown | TARENFLURBIL | NCSTN | MODULATOR | not shown on any card |
| unknown | TARENFLURBIL | PSEN1 | MODULATOR | not shown on any card |
| unknown | TARENFLURBIL | PSEN2 | MODULATOR | not shown on any card |
| unknown | TARENFLURBIL | PSENEN | MODULATOR | not shown on any card |
| unknown | TAVAPADON | DRD1 | PARTIAL AGONIST | not shown on any card |
| unknown | TEGASEROD | HTR4 | PARTIAL AGONIST | not shown on any card |
| unknown | TELAPRISTONE ACETATE | PGR | MODULATOR | not shown on any card |
| unknown | TELISOTUZUMAB VEDOTIN | MET | BINDING AGENT | not shown on any card |
| unknown | TEMANOGREL | HTR2A | INVERSE AGONIST | not shown on any card |
| unknown | TEPRASIRAN | TP53 | RNAI INHIBITOR | not shown on any card |
| unknown | TESIDOLUMAB | C5 | BINDING AGENT | not shown on any card |
| unknown | TIVANISIRAN | TRPV1 | ANTISENSE INHIBITOR | not shown on any card |
| unknown | TOFERSEN | SOD1 | ANTISENSE INHIBITOR | Approved: amyotrophic lateral sclerosis |
| unknown | TOMINERSEN | HTT | ANTISENSE INHIBITOR | not shown on any card |
| unknown | TOREMIFENE | ESR1 | MODULATOR | Approved: breast cancer; New clues: acromegaly, endometriosis, osteoporosis |
| unknown | TOREMIFENE | ESR2 | MODULATOR | New clues: osteoporosis |
| unknown | TRAMIPROSATE | APP | STABILISER | In trials: Alzheimer disease |
| unknown | TRASTUZUMAB BOTIDOTIN | ERBB2 | BINDING AGENT | not shown on any card |
| unknown | TRASTUZUMAB DERUXTECAN | ERBB2 | BINDING AGENT | Approved: breast cancer; In trials: colorectal cancer; New clues: lung cancer |
| unknown | TRASTUZUMAB DUOCARMAZINE | ERBB2 | BINDING AGENT | In trials: breast cancer; New clues: colorectal cancer, lung cancer |
| unknown | TRASTUZUMAB EMTANSINE | ERBB2 | BINDING AGENT | Approved: breast cancer; In trials: colorectal cancer; New clues: lung cancer |
| unknown | TRENONACOG ALFA | F9 | EXOGENOUS PROTEIN | not shown on any card |
| unknown | TUCOTUZUMAB CELMOLEUKIN | EPCAM | OTHER | not shown on any card |
| unknown | TUROCTOCOG ALFA | F8 | EXOGENOUS PROTEIN | Approved: hemophilia A; Wider box: hemophilia B |
| unknown | TUROCTOCOG ALFA PEGOL | F8 | EXOGENOUS PROTEIN | Approved: hemophilia A; New clues: hemophilia B |
| unknown | TUXOBERTINIB | EGFR | NEGATIVE ALLOSTERIC MODULATOR | not shown on any card |
| unknown | TUXOBERTINIB | ERBB2 | NEGATIVE ALLOSTERIC MODULATOR | not shown on any card |
| unknown | ULIPRISTAL | PGR | MODULATOR | New clues: Cushing syndrome, acromegaly, endometriosis |
| unknown | ULIPRISTAL ACETATE | PGR | MODULATOR | not shown on any card |
| unknown | VALILTRAMIPROSATE | APP | STABILISER | not shown on any card |
| unknown | VALOCTOCOGENE ROXAPARVOVEC | F9 | EXOGENOUS PROTEIN | Approved: hemophilia A; New clues: hemophilia B |
| unknown | VANUTIDE CRIDIFICAR | APP | VACCINE ANTIGEN | not shown on any card |
| unknown | VELSECORAT | NR3C1 | MODULATOR | not shown on any card |
| unknown | VERUBULIN | TUBA1B | DISRUPTING AGENT | not shown on any card |
| unknown | VERUBULIN | TUBA1C | DISRUPTING AGENT | not shown on any card |
| unknown | VERUBULIN | TUBA3C | DISRUPTING AGENT | not shown on any card |
| unknown | VERUBULIN | TUBA3E | DISRUPTING AGENT | not shown on any card |
| unknown | VERUBULIN | TUBA4A | DISRUPTING AGENT | not shown on any card |
| unknown | VERUBULIN | TUBB | DISRUPTING AGENT | not shown on any card |
| unknown | VERUBULIN | TUBB1 | DISRUPTING AGENT | not shown on any card |
| unknown | VERUBULIN | TUBB2A | DISRUPTING AGENT | not shown on any card |
| unknown | VERUBULIN | TUBB2B | DISRUPTING AGENT | not shown on any card |
| unknown | VERUBULIN | TUBB3 | DISRUPTING AGENT | not shown on any card |
| unknown | VERUBULIN | TUBB4A | DISRUPTING AGENT | not shown on any card |
| unknown | VERUBULIN | TUBB4B | DISRUPTING AGENT | not shown on any card |
| unknown | VERUBULIN | TUBB6 | DISRUPTING AGENT | not shown on any card |
| unknown | VERUBULIN | TUBB8 | DISRUPTING AGENT | not shown on any card |
| unknown | VILAPRISAN | PGR | MODULATOR | not shown on any card |
| unknown | VILAZODONE | HTR1A | PARTIAL AGONIST | In trials: depressive disorder; Narrower box: depressive disorder; New clues: schizophrenia |
| unknown | VK5211 | AR | MODULATOR | not shown on any card |
| unknown | VON WILLEBRAND FACTOR HUMAN | VWF | EXOGENOUS PROTEIN | In trials: hemophilia A; Wider box: hemophilia A |
| unknown | VONICOG ALFA | VWF | EXOGENOUS PROTEIN | New clues: hemophilia A |
| unknown | VRC-01LS | CD4 | BINDING AGENT | not shown on any card |
| unknown | XAMOTEROL | ADRB1 | PARTIAL AGONIST | New clues: glaucoma, heart failure |
| unknown | ZANOLIMUMAB | CD4 | OTHER | not shown on any card |
| unknown | ZILUCOPLAN SODIUM | C5 | BINDING AGENT | Approved: myasthenia gravis; New clues: Fabry disease |

### A3. Alfuzosin

**In the 50 study diseases:** rows naming alfuzosin in the saved protein answers: **0**. None of the 890 proteins looked at for those diseases has alfuzosin among its medicines, so it is on no card there.

So one extra step was taken, for this question only (`probe_alfuzosin.py`). The medicine lists saved by probe P3 name alfuzosin under these diseases: erectile dysfunction (MONDO_0005362), benign prostatic hyperplasia (MONDO_0010811), urinary tract infection (MONDO_0100338). The same Moonlight steps were run for them (119 more requests). **These extra diseases are not counted in A1, A2, A4 or Part B.**

Every card naming alfuzosin:

| disease | tab | medicine | protein | action words | Moonlight's direction |
|---|---|---|---|---|---|
| erectile dysfunction | In trials | ALFUZOSIN | ADRA1A | AGONIST | up |
| erectile dysfunction | In trials | ALFUZOSIN | ADRA1B | AGONIST | up |
| erectile dysfunction | In trials | ALFUZOSIN | ADRA1D | AGONIST | up |
| benign prostatic hyperplasia | Approved | ALFUZOSIN | ADRA1A | AGONIST | up |
| benign prostatic hyperplasia | Approved | ALFUZOSIN | ADRA1D | AGONIST | up |
| benign prostatic hyperplasia | Approved | ALFUZOSIN | ADRA1B | AGONIST | up |

**Alfuzosin is shown as "up"** on ADRA1A (benign prostatic hyperplasia), ADRA1A (erectile dysfunction), ADRA1B (benign prostatic hyperplasia), ADRA1B (erectile dysfunction), ADRA1D (benign prostatic hyperplasia), ADRA1D (erectile dysfunction).

**Exactly which field made it so.** Every raw row naming alfuzosin in the saved answers to "which medicines act on this protein?" (`target.drugAndClinicalCandidates.rows[].drug`). The field Moonlight reads is `drug.mechanismsOfAction.rows[].actionType`. Moonlight asks each question twice; answers that were letter for letter the same are saved once.

| saved file (under responses/) | protein asked about | form (id) | ALL its mechanism rows, as sent: actionType -> proteins | action words Moonlight takes for this protein | direction |
|---|---|---|---|---|---|
| target_drugs/02733_ENSG00000120907.json | ADRA1A | ALFUZOSIN HYDROCHLORIDE (CHEMBL1723) | AGONIST -> ADRA1A, ADRA1D, ADRA1B | AGONIST | up |
| target_drugs/02733_ENSG00000120907.json | ADRA1A | ALFUZOSIN (CHEMBL709) | AGONIST -> ADRA1A, ADRA1D, ADRA1B | AGONIST | up |
| target_drugs/02734_ENSG00000171873.json | ADRA1D | ALFUZOSIN HYDROCHLORIDE (CHEMBL1723) | AGONIST -> ADRA1A, ADRA1D, ADRA1B | AGONIST | up |
| target_drugs/02734_ENSG00000171873.json | ADRA1D | ALFUZOSIN (CHEMBL709) | AGONIST -> ADRA1A, ADRA1D, ADRA1B | AGONIST | up |
| target_drugs/02735_ENSG00000170214.json | ADRA1B | ALFUZOSIN HYDROCHLORIDE (CHEMBL1723) | AGONIST -> ADRA1A, ADRA1D, ADRA1B | AGONIST | up |
| target_drugs/02735_ENSG00000170214.json | ADRA1B | ALFUZOSIN (CHEMBL709) | AGONIST -> ADRA1A, ADRA1D, ADRA1B | AGONIST | up |

So the word behind "up" is the database's own `actionType` value for alfuzosin on these proteins, as printed above. Moonlight's list turns that word into "up"; it did not pick a different word or mix up two medicines. Whether the database's word is pharmacologically right is for a doctor to say.

For comparison only, every other shown card on the same proteins in the same diseases:

| disease | protein | tab | medicine | action words | Moonlight's direction |
|---|---|---|---|---|---|
| benign prostatic hyperplasia | ADRA1A | Approved | DOXAZOSIN | ANTAGONIST | down |
| benign prostatic hyperplasia | ADRA1A | Approved | PRAZOSIN | ANTAGONIST | down |
| benign prostatic hyperplasia | ADRA1A | Approved | SILODOSIN | ANTAGONIST | down |
| benign prostatic hyperplasia | ADRA1A | Approved | TAMSULOSIN | ANTAGONIST | down |
| benign prostatic hyperplasia | ADRA1A | Approved | TERAZOSIN | ANTAGONIST | down |
| benign prostatic hyperplasia | ADRA1A | New clues | ALSEROXYLON | ANTAGONIST | down |
| benign prostatic hyperplasia | ADRA1A | New clues | BUCINDOLOL | ANTAGONIST | down |
| benign prostatic hyperplasia | ADRA1A | New clues | BUNAZOSIN | ANTAGONIST | down |
| benign prostatic hyperplasia | ADRA1A | New clues | CARVEDILOL | ANTAGONIST | down |
| benign prostatic hyperplasia | ADRA1A | New clues | DAPIPRAZOLE | ANTAGONIST | down |
| benign prostatic hyperplasia | ADRA1A | New clues | DIPIVEFRIN | AGONIST | up |
| benign prostatic hyperplasia | ADRA1A | New clues | DROXIDOPA | AGONIST | up |
| benign prostatic hyperplasia | ADRA1A | New clues | EPINEPHRINE | AGONIST | up |
| benign prostatic hyperplasia | ADRA1A | New clues | ERGOLOID | ANTAGONIST | down |
| benign prostatic hyperplasia | ADRA1A | New clues | HYDROXYAMPHETAMINE | AGONIST | up |
| benign prostatic hyperplasia | ADRA1A | New clues | ISOXSUPRINE | ANTAGONIST | down |
| benign prostatic hyperplasia | ADRA1A | New clues | LABETALOL | ANTAGONIST | down |
| benign prostatic hyperplasia | ADRA1A | New clues | MEPHENTERMINE | AGONIST | up |
| benign prostatic hyperplasia | ADRA1A | New clues | METARAMINOL | AGONIST | up |
| benign prostatic hyperplasia | ADRA1A | New clues | METHOXAMINE | AGONIST | up |
| benign prostatic hyperplasia | ADRA1A | New clues | MIDODRINE | AGONIST | up |
| benign prostatic hyperplasia | ADRA1A | New clues | NAPHAZOLINE | AGONIST | up |
| benign prostatic hyperplasia | ADRA1A | New clues | NOREPINEPHRINE | AGONIST | up |
| benign prostatic hyperplasia | ADRA1A | New clues | OXYMETAZOLINE | AGONIST | up |
| benign prostatic hyperplasia | ADRA1A | New clues | PHENOXYBENZAMINE | ANTAGONIST | down |
| benign prostatic hyperplasia | ADRA1A | New clues | PHENTOLAMINE | ANTAGONIST | down |
| benign prostatic hyperplasia | ADRA1A | New clues | PHENYLEPHRINE | AGONIST | up |
| benign prostatic hyperplasia | ADRA1A | New clues | RAUWOLFIA SERPENTINA | ANTAGONIST | down |
| benign prostatic hyperplasia | ADRA1A | New clues | TETRAHYDROZOLINE | AGONIST | up |
| benign prostatic hyperplasia | ADRA1A | New clues | TOLAZOLINE | ANTAGONIST | down |
| benign prostatic hyperplasia | ADRA1A | New clues | TRIMIPRAMINE | ANTAGONIST | down |
| benign prostatic hyperplasia | ADRA1A | New clues | XYLOMETAZOLINE | AGONIST | up |
| benign prostatic hyperplasia | ADRA1B | Approved | DOXAZOSIN | ANTAGONIST | down |
| benign prostatic hyperplasia | ADRA1B | Approved | PRAZOSIN | ANTAGONIST | down |
| benign prostatic hyperplasia | ADRA1B | Approved | TAMSULOSIN | ANTAGONIST | down |
| benign prostatic hyperplasia | ADRA1B | Approved | TERAZOSIN | ANTAGONIST | down |
| benign prostatic hyperplasia | ADRA1B | New clues | ALSEROXYLON | ANTAGONIST | down |
| benign prostatic hyperplasia | ADRA1B | New clues | BUCINDOLOL | ANTAGONIST | down |
| benign prostatic hyperplasia | ADRA1B | New clues | BUNAZOSIN | ANTAGONIST | down |
| benign prostatic hyperplasia | ADRA1B | New clues | CARVEDILOL | ANTAGONIST | down |
| benign prostatic hyperplasia | ADRA1B | New clues | DIPIVEFRIN | AGONIST | up |
| benign prostatic hyperplasia | ADRA1B | New clues | DROXIDOPA | AGONIST | up |
| benign prostatic hyperplasia | ADRA1B | New clues | EPINEPHRINE | AGONIST | up |
| benign prostatic hyperplasia | ADRA1B | New clues | ERGOLOID | ANTAGONIST | down |
| benign prostatic hyperplasia | ADRA1B | New clues | HYDROXYAMPHETAMINE | AGONIST | up |
| benign prostatic hyperplasia | ADRA1B | New clues | ISOXSUPRINE | ANTAGONIST | down |
| benign prostatic hyperplasia | ADRA1B | New clues | LABETALOL | ANTAGONIST | down |
| benign prostatic hyperplasia | ADRA1B | New clues | MEPHENTERMINE | AGONIST | up |
| benign prostatic hyperplasia | ADRA1B | New clues | METARAMINOL | AGONIST | up |
| benign prostatic hyperplasia | ADRA1B | New clues | METHOXAMINE | AGONIST | up |
| benign prostatic hyperplasia | ADRA1B | New clues | MIDODRINE | AGONIST | up |
| benign prostatic hyperplasia | ADRA1B | New clues | NAPHAZOLINE | AGONIST | up |
| benign prostatic hyperplasia | ADRA1B | New clues | NOREPINEPHRINE | AGONIST | up |
| benign prostatic hyperplasia | ADRA1B | New clues | OXYMETAZOLINE | AGONIST | up |
| benign prostatic hyperplasia | ADRA1B | New clues | PHENOXYBENZAMINE | ANTAGONIST | down |
| benign prostatic hyperplasia | ADRA1B | New clues | PHENTOLAMINE | ANTAGONIST | down |
| benign prostatic hyperplasia | ADRA1B | New clues | PHENYLEPHRINE | AGONIST | up |
| benign prostatic hyperplasia | ADRA1B | New clues | RAUWOLFIA SERPENTINA | ANTAGONIST | down |
| benign prostatic hyperplasia | ADRA1B | New clues | TETRAHYDROZOLINE | AGONIST | up |
| benign prostatic hyperplasia | ADRA1B | New clues | TOLAZOLINE | ANTAGONIST | down |
| benign prostatic hyperplasia | ADRA1B | New clues | TRIMIPRAMINE | ANTAGONIST | down |
| benign prostatic hyperplasia | ADRA1B | New clues | XYLOMETAZOLINE | AGONIST | up |
| benign prostatic hyperplasia | ADRA1D | Approved | DOXAZOSIN | ANTAGONIST | down |
| benign prostatic hyperplasia | ADRA1D | Approved | PRAZOSIN | ANTAGONIST | down |
| benign prostatic hyperplasia | ADRA1D | Approved | TAMSULOSIN | ANTAGONIST | down |
| benign prostatic hyperplasia | ADRA1D | Approved | TERAZOSIN | ANTAGONIST | down |
| benign prostatic hyperplasia | ADRA1D | In trials | NAFTOPIDIL | ANTAGONIST | down |
| benign prostatic hyperplasia | ADRA1D | New clues | ALSEROXYLON | ANTAGONIST | down |
| benign prostatic hyperplasia | ADRA1D | New clues | BUCINDOLOL | ANTAGONIST | down |
| benign prostatic hyperplasia | ADRA1D | New clues | BUNAZOSIN | ANTAGONIST | down |
| benign prostatic hyperplasia | ADRA1D | New clues | CARVEDILOL | ANTAGONIST | down |
| benign prostatic hyperplasia | ADRA1D | New clues | DIPIVEFRIN | AGONIST | up |
| benign prostatic hyperplasia | ADRA1D | New clues | DROXIDOPA | AGONIST | up |
| benign prostatic hyperplasia | ADRA1D | New clues | EPINEPHRINE | AGONIST | up |
| benign prostatic hyperplasia | ADRA1D | New clues | ERGOLOID | ANTAGONIST | down |
| benign prostatic hyperplasia | ADRA1D | New clues | HYDROXYAMPHETAMINE | AGONIST | up |
| benign prostatic hyperplasia | ADRA1D | New clues | ISOXSUPRINE | ANTAGONIST | down |
| benign prostatic hyperplasia | ADRA1D | New clues | LABETALOL | ANTAGONIST | down |
| benign prostatic hyperplasia | ADRA1D | New clues | MEPHENTERMINE | AGONIST | up |
| benign prostatic hyperplasia | ADRA1D | New clues | METARAMINOL | AGONIST | up |
| benign prostatic hyperplasia | ADRA1D | New clues | METHOXAMINE | AGONIST | up |
| benign prostatic hyperplasia | ADRA1D | New clues | MIDODRINE | AGONIST | up |
| benign prostatic hyperplasia | ADRA1D | New clues | NAPHAZOLINE | AGONIST | up |
| benign prostatic hyperplasia | ADRA1D | New clues | NOREPINEPHRINE | AGONIST | up |
| benign prostatic hyperplasia | ADRA1D | New clues | OXYMETAZOLINE | AGONIST | up |
| benign prostatic hyperplasia | ADRA1D | New clues | PHENOXYBENZAMINE | ANTAGONIST | down |
| benign prostatic hyperplasia | ADRA1D | New clues | PHENTOLAMINE | ANTAGONIST | down |
| benign prostatic hyperplasia | ADRA1D | New clues | PHENYLEPHRINE | AGONIST | up |
| benign prostatic hyperplasia | ADRA1D | New clues | RAUWOLFIA SERPENTINA | ANTAGONIST | down |
| benign prostatic hyperplasia | ADRA1D | New clues | TETRAHYDROZOLINE | AGONIST | up |
| benign prostatic hyperplasia | ADRA1D | New clues | TOLAZOLINE | ANTAGONIST | down |
| benign prostatic hyperplasia | ADRA1D | New clues | TRIMIPRAMINE | ANTAGONIST | down |
| benign prostatic hyperplasia | ADRA1D | New clues | XYLOMETAZOLINE | AGONIST | up |
| erectile dysfunction | ADRA1A | In trials | PHENTOLAMINE | ANTAGONIST | down |
| erectile dysfunction | ADRA1A | In trials | TAMSULOSIN | ANTAGONIST | down |
| erectile dysfunction | ADRA1A | New clues | ALSEROXYLON | ANTAGONIST | down |
| erectile dysfunction | ADRA1A | New clues | BUCINDOLOL | ANTAGONIST | down |
| erectile dysfunction | ADRA1A | New clues | BUNAZOSIN | ANTAGONIST | down |
| erectile dysfunction | ADRA1A | New clues | CARVEDILOL | ANTAGONIST | down |
| erectile dysfunction | ADRA1A | New clues | DAPIPRAZOLE | ANTAGONIST | down |
| erectile dysfunction | ADRA1A | New clues | DIPIVEFRIN | AGONIST | up |
| erectile dysfunction | ADRA1A | New clues | DOXAZOSIN | ANTAGONIST | down |
| erectile dysfunction | ADRA1A | New clues | DROXIDOPA | AGONIST | up |
| erectile dysfunction | ADRA1A | New clues | EPINEPHRINE | AGONIST | up |
| erectile dysfunction | ADRA1A | New clues | ERGOLOID | ANTAGONIST | down |
| erectile dysfunction | ADRA1A | New clues | HYDROXYAMPHETAMINE | AGONIST | up |
| erectile dysfunction | ADRA1A | New clues | ISOXSUPRINE | ANTAGONIST | down |
| erectile dysfunction | ADRA1A | New clues | LABETALOL | ANTAGONIST | down |
| erectile dysfunction | ADRA1A | New clues | MEPHENTERMINE | AGONIST | up |
| erectile dysfunction | ADRA1A | New clues | METARAMINOL | AGONIST | up |
| erectile dysfunction | ADRA1A | New clues | METHOXAMINE | AGONIST | up |
| erectile dysfunction | ADRA1A | New clues | MIDODRINE | AGONIST | up |
| erectile dysfunction | ADRA1A | New clues | NAPHAZOLINE | AGONIST | up |
| erectile dysfunction | ADRA1A | New clues | NOREPINEPHRINE | AGONIST | up |
| erectile dysfunction | ADRA1A | New clues | OXYMETAZOLINE | AGONIST | up |
| erectile dysfunction | ADRA1A | New clues | PHENOXYBENZAMINE | ANTAGONIST | down |
| erectile dysfunction | ADRA1A | New clues | PHENYLEPHRINE | AGONIST | up |
| erectile dysfunction | ADRA1A | New clues | PRAZOSIN | ANTAGONIST | down |
| erectile dysfunction | ADRA1A | New clues | RAUWOLFIA SERPENTINA | ANTAGONIST | down |
| erectile dysfunction | ADRA1A | New clues | SILODOSIN | ANTAGONIST | down |
| erectile dysfunction | ADRA1A | New clues | TERAZOSIN | ANTAGONIST | down |
| erectile dysfunction | ADRA1A | New clues | TETRAHYDROZOLINE | AGONIST | up |
| erectile dysfunction | ADRA1A | New clues | TOLAZOLINE | ANTAGONIST | down |
| erectile dysfunction | ADRA1A | New clues | TRIMIPRAMINE | ANTAGONIST | down |
| erectile dysfunction | ADRA1A | New clues | XYLOMETAZOLINE | AGONIST | up |
| erectile dysfunction | ADRA1B | In trials | PHENTOLAMINE | ANTAGONIST | down |
| erectile dysfunction | ADRA1B | In trials | TAMSULOSIN | ANTAGONIST | down |
| erectile dysfunction | ADRA1B | New clues | ALSEROXYLON | ANTAGONIST | down |
| erectile dysfunction | ADRA1B | New clues | BUCINDOLOL | ANTAGONIST | down |
| erectile dysfunction | ADRA1B | New clues | BUNAZOSIN | ANTAGONIST | down |
| erectile dysfunction | ADRA1B | New clues | CARVEDILOL | ANTAGONIST | down |
| erectile dysfunction | ADRA1B | New clues | DIPIVEFRIN | AGONIST | up |
| erectile dysfunction | ADRA1B | New clues | DOXAZOSIN | ANTAGONIST | down |
| erectile dysfunction | ADRA1B | New clues | DROXIDOPA | AGONIST | up |
| erectile dysfunction | ADRA1B | New clues | EPINEPHRINE | AGONIST | up |
| erectile dysfunction | ADRA1B | New clues | ERGOLOID | ANTAGONIST | down |
| erectile dysfunction | ADRA1B | New clues | HYDROXYAMPHETAMINE | AGONIST | up |
| erectile dysfunction | ADRA1B | New clues | ISOXSUPRINE | ANTAGONIST | down |
| erectile dysfunction | ADRA1B | New clues | LABETALOL | ANTAGONIST | down |
| erectile dysfunction | ADRA1B | New clues | MEPHENTERMINE | AGONIST | up |
| erectile dysfunction | ADRA1B | New clues | METARAMINOL | AGONIST | up |
| erectile dysfunction | ADRA1B | New clues | METHOXAMINE | AGONIST | up |
| erectile dysfunction | ADRA1B | New clues | MIDODRINE | AGONIST | up |
| erectile dysfunction | ADRA1B | New clues | NAPHAZOLINE | AGONIST | up |
| erectile dysfunction | ADRA1B | New clues | NOREPINEPHRINE | AGONIST | up |
| erectile dysfunction | ADRA1B | New clues | OXYMETAZOLINE | AGONIST | up |
| erectile dysfunction | ADRA1B | New clues | PHENOXYBENZAMINE | ANTAGONIST | down |
| erectile dysfunction | ADRA1B | New clues | PHENYLEPHRINE | AGONIST | up |
| erectile dysfunction | ADRA1B | New clues | PRAZOSIN | ANTAGONIST | down |
| erectile dysfunction | ADRA1B | New clues | RAUWOLFIA SERPENTINA | ANTAGONIST | down |
| erectile dysfunction | ADRA1B | New clues | TERAZOSIN | ANTAGONIST | down |
| erectile dysfunction | ADRA1B | New clues | TETRAHYDROZOLINE | AGONIST | up |
| erectile dysfunction | ADRA1B | New clues | TOLAZOLINE | ANTAGONIST | down |
| erectile dysfunction | ADRA1B | New clues | TRIMIPRAMINE | ANTAGONIST | down |
| erectile dysfunction | ADRA1B | New clues | XYLOMETAZOLINE | AGONIST | up |
| erectile dysfunction | ADRA1D | In trials | PHENTOLAMINE | ANTAGONIST | down |
| erectile dysfunction | ADRA1D | In trials | TAMSULOSIN | ANTAGONIST | down |
| erectile dysfunction | ADRA1D | New clues | ALSEROXYLON | ANTAGONIST | down |
| erectile dysfunction | ADRA1D | New clues | BUCINDOLOL | ANTAGONIST | down |
| erectile dysfunction | ADRA1D | New clues | BUNAZOSIN | ANTAGONIST | down |
| erectile dysfunction | ADRA1D | New clues | CARVEDILOL | ANTAGONIST | down |
| erectile dysfunction | ADRA1D | New clues | DIPIVEFRIN | AGONIST | up |
| erectile dysfunction | ADRA1D | New clues | DOXAZOSIN | ANTAGONIST | down |
| erectile dysfunction | ADRA1D | New clues | DROXIDOPA | AGONIST | up |
| erectile dysfunction | ADRA1D | New clues | EPINEPHRINE | AGONIST | up |
| erectile dysfunction | ADRA1D | New clues | ERGOLOID | ANTAGONIST | down |
| erectile dysfunction | ADRA1D | New clues | HYDROXYAMPHETAMINE | AGONIST | up |
| erectile dysfunction | ADRA1D | New clues | ISOXSUPRINE | ANTAGONIST | down |
| erectile dysfunction | ADRA1D | New clues | LABETALOL | ANTAGONIST | down |
| erectile dysfunction | ADRA1D | New clues | MEPHENTERMINE | AGONIST | up |
| erectile dysfunction | ADRA1D | New clues | METARAMINOL | AGONIST | up |
| erectile dysfunction | ADRA1D | New clues | METHOXAMINE | AGONIST | up |
| erectile dysfunction | ADRA1D | New clues | MIDODRINE | AGONIST | up |
| erectile dysfunction | ADRA1D | New clues | NAFTOPIDIL | ANTAGONIST | down |
| erectile dysfunction | ADRA1D | New clues | NAPHAZOLINE | AGONIST | up |
| erectile dysfunction | ADRA1D | New clues | NOREPINEPHRINE | AGONIST | up |
| erectile dysfunction | ADRA1D | New clues | OXYMETAZOLINE | AGONIST | up |
| erectile dysfunction | ADRA1D | New clues | PHENOXYBENZAMINE | ANTAGONIST | down |
| erectile dysfunction | ADRA1D | New clues | PHENYLEPHRINE | AGONIST | up |
| erectile dysfunction | ADRA1D | New clues | PRAZOSIN | ANTAGONIST | down |
| erectile dysfunction | ADRA1D | New clues | RAUWOLFIA SERPENTINA | ANTAGONIST | down |
| erectile dysfunction | ADRA1D | New clues | TERAZOSIN | ANTAGONIST | down |
| erectile dysfunction | ADRA1D | New clues | TETRAHYDROZOLINE | AGONIST | up |
| erectile dysfunction | ADRA1D | New clues | TOLAZOLINE | ANTAGONIST | down |
| erectile dysfunction | ADRA1D | New clues | TRIMIPRAMINE | ANTAGONIST | down |
| erectile dysfunction | ADRA1D | New clues | XYLOMETAZOLINE | AGONIST | up |

### A4. Review table for a doctor

For each disease, the first 5 medicines of the main Approved list (A to Z, the order the page uses) that have at least one path, with every protein of theirs among the 25 looked at. **No row is marked right or wrong. A doctor will judge.** Also in `doctor_review.csv`.

| disease | Approved medicine | protein | action words | Moonlight's direction |
|---|---|---|---|---|
| asthma | ACLIDINIUM | CHRM3 | ANTAGONIST | down |
| asthma | ALBUTEROL | ADRB2 | AGONIST | up |
| asthma | BAMBUTEROL | ADRB2 | AGONIST | up |
| asthma | BECLOMETHASONE DIPROPIONATE | NR3C1 | AGONIST | up |
| asthma | BENRALIZUMAB | IL5RA | INHIBITOR | down |
| type 2 diabetes mellitus | ALBIGLUTIDE | GLP1R | AGONIST | up |
| type 2 diabetes mellitus | CHLORPROPAMIDE | KCNJ11 | BLOCKER | down |
| type 2 diabetes mellitus | CHLORPROPAMIDE | ABCC8 | BLOCKER | down |
| type 2 diabetes mellitus | DULAGLUTIDE | GLP1R | AGONIST | up |
| type 2 diabetes mellitus | EXENATIDE | GLP1R | AGONIST | up |
| type 2 diabetes mellitus | GLIMEPIRIDE | KCNJ11 | BLOCKER | down |
| type 2 diabetes mellitus | GLIMEPIRIDE | ABCC8 | BLOCKER | down |
| epilepsy | CARBAMAZEPINE | SCN1A | BLOCKER | down |
| epilepsy | CARBAMAZEPINE | SCN2A | BLOCKER | down |
| epilepsy | CARBAMAZEPINE | SCN8A | BLOCKER | down |
| epilepsy | CARBAMAZEPINE | SCN3A | BLOCKER | down |
| epilepsy | CENOBAMATE | SCN1A | INHIBITOR | down |
| epilepsy | CENOBAMATE | SCN2A | INHIBITOR | down |
| epilepsy | CENOBAMATE | SCN8A | INHIBITOR | down |
| epilepsy | CENOBAMATE | GABRG2 | POSITIVE ALLOSTERIC MODULATOR | up |
| epilepsy | CENOBAMATE | SCN3A | INHIBITOR | down |
| epilepsy | CENOBAMATE | GABRA1 | POSITIVE ALLOSTERIC MODULATOR | up |
| epilepsy | CENOBAMATE | GABRB3 | POSITIVE ALLOSTERIC MODULATOR | up |
| epilepsy | CENOBAMATE | GABRB2 | POSITIVE ALLOSTERIC MODULATOR | up |
| epilepsy | CLOBAZAM | GABRG2 | POSITIVE ALLOSTERIC MODULATOR | up |
| epilepsy | CLOBAZAM | GABRA1 | POSITIVE ALLOSTERIC MODULATOR | up |
| epilepsy | CLOBAZAM | GABRB3 | POSITIVE ALLOSTERIC MODULATOR | up |
| epilepsy | CLOBAZAM | GABRB2 | POSITIVE ALLOSTERIC MODULATOR | up |
| epilepsy | CLONAZEPAM | GABRG2 | POSITIVE ALLOSTERIC MODULATOR | up |
| epilepsy | CLONAZEPAM | GABRA1 | POSITIVE ALLOSTERIC MODULATOR | up |
| epilepsy | CLONAZEPAM | GABRB3 | POSITIVE ALLOSTERIC MODULATOR | up |
| epilepsy | CLONAZEPAM | GABRB2 | POSITIVE ALLOSTERIC MODULATOR | up |
| epilepsy | DIAZEPAM | GABRG2 | POSITIVE ALLOSTERIC MODULATOR | up |
| epilepsy | DIAZEPAM | GABRA1 | POSITIVE ALLOSTERIC MODULATOR | up |
| epilepsy | DIAZEPAM | GABRB3 | POSITIVE ALLOSTERIC MODULATOR | up |
| epilepsy | DIAZEPAM | GABRB2 | POSITIVE ALLOSTERIC MODULATOR | up |
| rheumatoid arthritis | ABATACEPT | CD80 | INHIBITOR | down |
| rheumatoid arthritis | ABATACEPT | CD86 | INHIBITOR | down |
| rheumatoid arthritis | ACECLOFENAC | PTGS2 | INHIBITOR | down |
| rheumatoid arthritis | ADALIMUMAB | TNF | INHIBITOR | down |
| rheumatoid arthritis | BARICITINIB | JAK1 | INHIBITOR | down |
| rheumatoid arthritis | BARICITINIB | JAK2 | INHIBITOR | down |
| rheumatoid arthritis | CELECOXIB | PTGS2 | INHIBITOR | down |
| psoriasis | ACITRETIN | RXRA | AGONIST | up |
| psoriasis | ACITRETIN | RARA | AGONIST | up |
| psoriasis | ACITRETIN | RARB | AGONIST | up |
| psoriasis | ACITRETIN | RARG | AGONIST | up |
| psoriasis | ADALIMUMAB | TNF | INHIBITOR | down |
| psoriasis | APREMILAST | PDE4A | INHIBITOR | down |
| psoriasis | APREMILAST | PDE4D | INHIBITOR | down |
| psoriasis | APREMILAST | PDE4B | INHIBITOR | down |
| psoriasis | APREMILAST | PDE4C | INHIBITOR | down |
| psoriasis | BETAMETHASONE DIPROPIONATE | NR3C1 | AGONIST | up |
| psoriasis | BIMEKIZUMAB | IL17A | INHIBITOR | down |
| atopic eczema | ABROCITINIB | JAK1 | INHIBITOR | down |
| atopic eczema | ATOMOXETINE | SLC6A2 | INHIBITOR | down |
| atopic eczema | BARICITINIB | JAK1 | INHIBITOR | down |
| atopic eczema | BARICITINIB | JAK2 | INHIBITOR | down |
| atopic eczema | BILASTINE | HRH1 | INVERSE AGONIST | unknown |
| atopic eczema | CORTISONE ACETATE | NR3C1 | AGONIST | up |
| ulcerative colitis | ADALIMUMAB | TNF | INHIBITOR | down |
| ulcerative colitis | AZATHIOPRINE | PPAT | INHIBITOR | down |
| ulcerative colitis | BALSALAZIDE | PPARG | AGONIST | up |
| ulcerative colitis | BALSALAZIDE | PTGS2 | INHIBITOR | down |
| ulcerative colitis | BALSALAZIDE | PTGS1 | INHIBITOR | down |
| ulcerative colitis | BALSALAZIDE | ALOX5 | INHIBITOR | down |
| ulcerative colitis | BETAMETHASONE ACETATE | NR3C1 | AGONIST | up |
| ulcerative colitis | BETAMETHASONE PHOSPHORIC ACID | NR3C1 | AGONIST | up |
| osteoporosis | ABALOPARATIDE | PTH1R | AGONIST | up |
| osteoporosis | ALENDRONIC ACID | FDPS | INHIBITOR | down |
| osteoporosis | BAZEDOXIFENE | ESR1 | MODULATOR | unknown |
| osteoporosis | BAZEDOXIFENE | ESR2 | MODULATOR | unknown |
| osteoporosis | CHOLECALCIFEROL | VDR | AGONIST | up |
| osteoporosis | DENOSUMAB | TNFSF11 | INHIBITOR | down |
| gout | ALLOPURINOL | XDH | INHIBITOR | down |
| gout | COLCHICINE | TUBA1B | INHIBITOR | down |
| gout | COLCHICINE | TUBB | INHIBITOR | down |
| gout | COLCHICINE | TUBA1C | INHIBITOR | down |
| gout | COLCHICINE | TUBA3C | INHIBITOR | down |
| gout | COLCHICINE | TUBA3E | INHIBITOR | down |
| gout | COLCHICINE | TUBA4A | INHIBITOR | down |
| gout | COLCHICINE | TUBB1 | INHIBITOR | down |
| gout | COLCHICINE | TUBB2A | INHIBITOR | down |
| gout | COLCHICINE | TUBB2B | INHIBITOR | down |
| gout | COLCHICINE | TUBB3 | INHIBITOR | down |
| gout | COLCHICINE | TUBB4A | INHIBITOR | down |
| gout | COLCHICINE | TUBB4B | INHIBITOR | down |
| gout | COLCHICINE | TUBB6 | INHIBITOR | down |
| gout | COLCHICINE | TUBB8 | INHIBITOR | down |
| gout | DOTINURAD | SLC22A12 | INHIBITOR | down |
| gout | FEBUXOSTAT | XDH | INHIBITOR | down |
| gout | INDOMETHACIN | PTGS2 | INHIBITOR | down |
| gout | INDOMETHACIN | PTGS1 | INHIBITOR | down |
| heart failure | AMLODIPINE | CACNA1D | BLOCKER | down |
| heart failure | CANDESARTAN CILEXETIL | AGTR1 | ANTAGONIST | down |
| heart failure | CAPTOPRIL | ACE | INHIBITOR | down |
| heart failure | CARVEDILOL | ADRB3 | ANTAGONIST | down |
| heart failure | CARVEDILOL | ADRB1 | ANTAGONIST | down |
| heart failure | CARVEDILOL | ADRB2 | ANTAGONIST | down |
| heart failure | DAPAGLIFLOZIN | SLC5A2 | INHIBITOR | down |
| atrial fibrillation | APIXABAN | F10 | INHIBITOR | down |
| atrial fibrillation | DIGOXIN | ATP1B2 | INHIBITOR | down |
| atrial fibrillation | DILTIAZEM | CACNA1D | BLOCKER | down |
| atrial fibrillation | DILTIAZEM | CACNA1C | BLOCKER | down |
| atrial fibrillation | DOFETILIDE | KCNH2 | BLOCKER | down |
| atrial fibrillation | DRONEDARONE | SCN5A | BLOCKER | down |
| atrial fibrillation | DRONEDARONE | KCNJ2 | BLOCKER | down |
| atrial fibrillation | DRONEDARONE | HCN4 | BLOCKER | down |
| atrial fibrillation | DRONEDARONE | SCN10A | BLOCKER | down |
| atrial fibrillation | DRONEDARONE | CACNA1D | BLOCKER | down |
| atrial fibrillation | DRONEDARONE | CACNA1C | BLOCKER | down |
| chronic obstructive pulmonary disease | ACLIDINIUM | CHRM3 | ANTAGONIST | down |
| chronic obstructive pulmonary disease | ALBUTEROL | ADRB2 | AGONIST | up |
| chronic obstructive pulmonary disease | ARFORMOTEROL | ADRB2 | AGONIST | up |
| chronic obstructive pulmonary disease | BECLOMETHASONE DIPROPIONATE | NR3C1 | AGONIST | up |
| chronic obstructive pulmonary disease | BITOLTEROL | ADRB2 | AGONIST | up |
| chronic kidney disease | CALCIFEDIOL ANHYDROUS | VDR | AGONIST | up |
| chronic kidney disease | CALCITRIOL | VDR | AGONIST | up |
| chronic kidney disease | CHLOROTHIAZIDE | SLC12A3 | INHIBITOR | down |
| chronic kidney disease | CHLORTHALIDONE | SLC12A3 | INHIBITOR | down |
| chronic kidney disease | CINACALCET | CASR | POSITIVE ALLOSTERIC MODULATOR | up |
| hypothyroidism | LEVOTHYROXINE | THRA | AGONIST | up |
| hypothyroidism | LEVOTHYROXINE | THRB | AGONIST | up |
| hypothyroidism | LIOTHYRONINE | THRA | AGONIST | up |
| hypothyroidism | LIOTHYRONINE | THRB | AGONIST | up |
| hypothyroidism | THYROTROPIN | TSHR | AGONIST | up |
| depressive disorder | AMITRIPTYLINE | SLC6A4 | INHIBITOR | down |
| depressive disorder | AMITRIPTYLINE | SLC6A2 | INHIBITOR | down |
| depressive disorder | BREXANOLONE | GABRA1 | POSITIVE ALLOSTERIC MODULATOR | up |
| depressive disorder | BREXANOLONE | GABRB1 | POSITIVE ALLOSTERIC MODULATOR | up |
| depressive disorder | BREXANOLONE | GABRA6 | POSITIVE ALLOSTERIC MODULATOR | up |
| depressive disorder | BREXANOLONE | GABRA2 | POSITIVE ALLOSTERIC MODULATOR | up |
| depressive disorder | BREXANOLONE | GABRG3 | POSITIVE ALLOSTERIC MODULATOR | up |
| depressive disorder | BREXANOLONE | GABRB2 | POSITIVE ALLOSTERIC MODULATOR | up |
| depressive disorder | BREXANOLONE | GABRG2 | POSITIVE ALLOSTERIC MODULATOR | up |
| depressive disorder | BREXANOLONE | GABRA5 | POSITIVE ALLOSTERIC MODULATOR | up |
| depressive disorder | BUPROPION | SLC6A3 | INHIBITOR | down |
| depressive disorder | BUPROPION | SLC6A2 | INHIBITOR | down |
| depressive disorder | BUSPIRONE | HTR1A | PARTIAL AGONIST | unknown |
| depressive disorder | CITALOPRAM | SLC6A4 | INHIBITOR | down |
| schizophrenia | AMISULPRIDE | DRD2 | ANTAGONIST | down |
| schizophrenia | AMISULPRIDE | DRD3 | ANTAGONIST | down |
| schizophrenia | AMISULPRIDE | HTR1A | ANTAGONIST | down |
| schizophrenia | AMISULPRIDE | HTR2A | ANTAGONIST | down |
| schizophrenia | AMISULPRIDE | HTR2C | ANTAGONIST | down |
| schizophrenia | AMISULPRIDE | HTR4 | ANTAGONIST | down |
| schizophrenia | AMISULPRIDE | HTR1B | ANTAGONIST | down |
| schizophrenia | AMISULPRIDE | HTR5A | ANTAGONIST | down |
| schizophrenia | AMISULPRIDE | HTR6 | ANTAGONIST | down |
| schizophrenia | AMISULPRIDE | HTR3A | ANTAGONIST | down |
| schizophrenia | AMISULPRIDE | HTR7 | ANTAGONIST | down |
| schizophrenia | AMISULPRIDE | HTR3B | ANTAGONIST | down |
| schizophrenia | AMISULPRIDE | HTR3C | ANTAGONIST | down |
| schizophrenia | AMISULPRIDE | HTR3D | ANTAGONIST | down |
| schizophrenia | AMISULPRIDE | HTR3E | ANTAGONIST | down |
| schizophrenia | AMISULPRIDE | HTR2B | ANTAGONIST | down |
| schizophrenia | AMISULPRIDE | HTR1F | ANTAGONIST | down |
| schizophrenia | AMISULPRIDE | HTR1D | ANTAGONIST | down |
| schizophrenia | ARIPIPRAZOLE | DRD2 | PARTIAL AGONIST | unknown |
| schizophrenia | ARIPIPRAZOLE | HTR1A | PARTIAL AGONIST | unknown |
| schizophrenia | ARIPIPRAZOLE | HTR2A | ANTAGONIST | down |
| schizophrenia | ARIPIPRAZOLE LAUROXIL | DRD2 | PARTIAL AGONIST | unknown |
| schizophrenia | ARIPIPRAZOLE LAUROXIL | HTR1A | PARTIAL AGONIST | unknown |
| schizophrenia | ARIPIPRAZOLE LAUROXIL | HTR2A | ANTAGONIST | down |
| schizophrenia | ASENAPINE | DRD2 | ANTAGONIST | down |
| schizophrenia | ASENAPINE | HTR2A | ANTAGONIST | down |
| schizophrenia | BENPERIDOL | DRD2 | ANTAGONIST | down |
| bipolar disorder | ACETOPHENAZINE | DRD2 | ANTAGONIST | down |
| bipolar disorder | ARIPIPRAZOLE | DRD2 | PARTIAL AGONIST | unknown |
| bipolar disorder | ARIPIPRAZOLE | HTR1A | PARTIAL AGONIST | unknown |
| bipolar disorder | ARIPIPRAZOLE | HTR2A | ANTAGONIST | down |
| bipolar disorder | ASENAPINE | DRD2 | ANTAGONIST | down |
| bipolar disorder | ASENAPINE | HTR2A | ANTAGONIST | down |
| bipolar disorder | CARBAMAZEPINE | SCN2A | BLOCKER | down |
| bipolar disorder | CARBAMAZEPINE | SCN8A | BLOCKER | down |
| bipolar disorder | CARBAMAZEPINE | SCN9A | BLOCKER | down |
| bipolar disorder | CARBAMAZEPINE | SCN11A | BLOCKER | down |
| bipolar disorder | CARBAMAZEPINE | SCN1A | BLOCKER | down |
| bipolar disorder | CARBAMAZEPINE | SCN5A | BLOCKER | down |
| bipolar disorder | CARBAMAZEPINE | SCN3A | BLOCKER | down |
| bipolar disorder | CARBAMAZEPINE | SCN10A | BLOCKER | down |
| bipolar disorder | CARBAMAZEPINE | SCN4A | BLOCKER | down |
| bipolar disorder | CARBAMAZEPINE | SCN7A | BLOCKER | down |
| bipolar disorder | CARIPRAZINE | DRD2 | MODULATOR | unknown |
| bipolar disorder | CARIPRAZINE | DRD3 | MODULATOR | unknown |
| Parkinson disease | AMANTADINE | GRIN1 | ANTAGONIST | down |
| Parkinson disease | AMANTADINE | GRIN2B | ANTAGONIST | down |
| Parkinson disease | AMANTADINE | GRIN2A | ANTAGONIST | down |
| Parkinson disease | APOMORPHINE | DRD2 | AGONIST | up |
| Parkinson disease | APOMORPHINE | DRD3 | AGONIST | up |
| Parkinson disease | ATROPINE | CHRM1 | ANTAGONIST | down |
| Parkinson disease | BENZTROPINE | CHRM1 | ANTAGONIST | down |
| Parkinson disease | BIPERIDEN | CHRM1 | ANTAGONIST | down |
| Alzheimer disease | ADUCANUMAB | APP | BINDING AGENT | unknown |
| Alzheimer disease | DONANEMAB | APP | DISRUPTING AGENT | unknown |
| Alzheimer disease | DONEPEZIL | ACHE | INHIBITOR | down |
| Alzheimer disease | GALANTAMINE | ACHE | INHIBITOR | down |
| Alzheimer disease | HUPERZINE A | ACHE | INHIBITOR | down |
| glaucoma | ACETAZOLAMIDE | CA2 | INHIBITOR | down |
| glaucoma | ACETAZOLAMIDE | CA12 | INHIBITOR | down |
| glaucoma | ACETAZOLAMIDE | CA1 | INHIBITOR | down |
| glaucoma | ACETAZOLAMIDE | CA4 | INHIBITOR | down |
| glaucoma | APRACLONIDINE | ADRA2A | AGONIST | up |
| glaucoma | APRACLONIDINE | ADRA2B | AGONIST | up |
| glaucoma | APRACLONIDINE | ADRA2C | AGONIST | up |
| glaucoma | BETAXOLOL | ADRB1 | ANTAGONIST | down |
| glaucoma | BIMATOPROST | PTGFR | AGONIST | up |
| glaucoma | BRIMONIDINE | ADRA2A | AGONIST | up |
| glaucoma | BRIMONIDINE | ADRA2B | AGONIST | up |
| glaucoma | BRIMONIDINE | ADRA2C | AGONIST | up |
| endometriosis | DANAZOL | PGR | AGONIST | up |
| endometriosis | DANAZOL | AR | AGONIST | up |
| endometriosis | DROSPIRENONE | PGR | AGONIST | up |
| endometriosis | DROSPIRENONE | NR3C2 | ANTAGONIST | down |
| endometriosis | ELAGOLIX | GNRHR | ANTAGONIST | down |
| endometriosis | ETHINYL ESTRADIOL | ESR1 | AGONIST | up |
| endometriosis | HISTRELIN | GNRHR | AGONIST | up |
| malaria | DOXYCYCLINE ANHYDROUS | MMP8 | INHIBITOR | down |
| malaria | DOXYCYCLINE ANHYDROUS | MMP1 | INHIBITOR | down |
| malaria | DOXYCYCLINE ANHYDROUS | MMP7 | INHIBITOR | down |
| malaria | DOXYCYCLINE ANHYDROUS | MMP13 | INHIBITOR | down |
| malaria | HYDROXYCHLOROQUINE | TLR9 | ANTAGONIST | down |
| malaria | HYDROXYCHLOROQUINE | TLR7 | ANTAGONIST | down |
| malaria | QUINIDINE | SCN8A | BLOCKER | down |
| malaria | QUINIDINE | SCN1A | BLOCKER | down |
| malaria | QUINIDINE | SCN3A | BLOCKER | down |
| breast cancer | ABEMACICLIB | CDK6 | INHIBITOR | down |
| breast cancer | ABEMACICLIB | CDK4 | INHIBITOR | down |
| breast cancer | ALPELISIB | PIK3CA | INHIBITOR | down |
| breast cancer | ARZOXIFENE | ESR1 | MODULATOR | unknown |
| breast cancer | CAPIVASERTIB | AKT1 | INHIBITOR | down |
| breast cancer | ELACESTRANT | ESR1 | DEGRADER | unknown |
| prostate cancer | ABIRATERONE | AR | ANTAGONIST | down |
| prostate cancer | ABIRATERONE | CYP17A1 | INHIBITOR | down |
| prostate cancer | ABIRATERONE ACETATE | CYP17A1 | INHIBITOR | down |
| prostate cancer | APALUTAMIDE | AR | ANTAGONIST | down |
| prostate cancer | BICALUTAMIDE | AR | ANTAGONIST | down |
| prostate cancer | CABAZITAXEL | TUBA1C | INHIBITOR | down |
| colorectal cancer | CETUXIMAB | EGFR | INHIBITOR | down |
| colorectal cancer | EDRECOLOMAB | EPCAM | CROSS-LINKING AGENT | unknown |
| colorectal cancer | FRUQUINTINIB | FLT4 | INHIBITOR | down |
| colorectal cancer | FRUQUINTINIB | KDR | INHIBITOR | down |
| colorectal cancer | NECITUMUMAB | EGFR | INHIBITOR | down |
| colorectal cancer | NINTEDANIB | FGFR2 | INHIBITOR | down |
| colorectal cancer | NINTEDANIB | FLT4 | INHIBITOR | down |
| colorectal cancer | NINTEDANIB | KDR | INHIBITOR | down |
| colorectal cancer | NINTEDANIB | FGFR3 | INHIBITOR | down |
| lung cancer | ALECTINIB | ALK | INHIBITOR | down |
| lung cancer | ALECTINIB | RET | INHIBITOR | down |
| lung cancer | ALECTINIB | EML4 | INHIBITOR | down |
| lung cancer | OLMUTINIB | EGFR | INHIBITOR | down |
| melanoma | BINIMETINIB | MAP2K1 | INHIBITOR | down |
| melanoma | BINIMETINIB | MAP2K2 | INHIBITOR | down |
| melanoma | COBIMETINIB | MAP2K1 | INHIBITOR | down |
| melanoma | COBIMETINIB | MAP2K2 | INHIBITOR | down |
| melanoma | DABRAFENIB | BRAF | INHIBITOR | down |
| melanoma | ENCORAFENIB | BRAF | INHIBITOR | down |
| melanoma | IPILIMUMAB | CTLA4 | INHIBITOR | down |
| chronic myeloid leukemia | ASCIMINIB | ABL1 | INHIBITOR | down |
| chronic myeloid leukemia | ASCIMINIB | BCR | INHIBITOR | down |
| chronic myeloid leukemia | BOSUTINIB | ABL1 | INHIBITOR | down |
| chronic myeloid leukemia | BOSUTINIB | BCR | INHIBITOR | down |
| chronic myeloid leukemia | BOSUTINIB | LYN | INHIBITOR | down |
| chronic myeloid leukemia | BOSUTINIB | SRC | INHIBITOR | down |
| chronic myeloid leukemia | BOSUTINIB | HCK | INHIBITOR | down |
| chronic myeloid leukemia | DASATINIB ANHYDROUS | ABL1 | INHIBITOR | down |
| chronic myeloid leukemia | DASATINIB ANHYDROUS | BCR | INHIBITOR | down |
| chronic myeloid leukemia | DASATINIB ANHYDROUS | KIT | INHIBITOR | down |
| chronic myeloid leukemia | DASATINIB ANHYDROUS | PDGFRB | INHIBITOR | down |
| chronic myeloid leukemia | DASATINIB ANHYDROUS | FYN | INHIBITOR | down |
| chronic myeloid leukemia | DASATINIB ANHYDROUS | LYN | INHIBITOR | down |
| chronic myeloid leukemia | DASATINIB ANHYDROUS | BLK | INHIBITOR | down |
| chronic myeloid leukemia | DASATINIB ANHYDROUS | SRC | INHIBITOR | down |
| chronic myeloid leukemia | DASATINIB ANHYDROUS | HCK | INHIBITOR | down |
| chronic myeloid leukemia | DASATINIB ANHYDROUS | FGR | INHIBITOR | down |
| chronic myeloid leukemia | DASATINIB ANHYDROUS | YES1 | INHIBITOR | down |
| chronic myeloid leukemia | DASATINIB ANHYDROUS | EPHA2 | INHIBITOR | down |
| chronic myeloid leukemia | DASATINIB ANHYDROUS | LCK | INHIBITOR | down |
| chronic myeloid leukemia | DASATINIB ANHYDROUS | FRK | INHIBITOR | down |
| chronic myeloid leukemia | DASATINIB ANHYDROUS | SRMS | INHIBITOR | down |
| chronic myeloid leukemia | HYDROXYUREA | RRM2 | INHIBITOR | down |
| chronic myeloid leukemia | HYDROXYUREA | RRM1 | INHIBITOR | down |
| chronic myeloid leukemia | HYDROXYUREA | RRM2B | INHIBITOR | down |
| chronic myeloid leukemia | IMATINIB | ABL1 | INHIBITOR | down |
| chronic myeloid leukemia | IMATINIB | BCR | INHIBITOR | down |
| chronic myeloid leukemia | IMATINIB | KIT | INHIBITOR | down |
| chronic myeloid leukemia | IMATINIB | PDGFRB | INHIBITOR | down |
| acute myeloid leukemia | AZACITIDINE | DNMT3A | INHIBITOR | down |
| acute myeloid leukemia | ENASIDENIB | IDH2 | INHIBITOR | down |
| acute myeloid leukemia | GILTERITINIB | FLT3 | INHIBITOR | down |
| acute myeloid leukemia | IVOSIDENIB | IDH1 | INHIBITOR | down |
| acute myeloid leukemia | MIDOSTAURIN | FLT3 | INHIBITOR | down |
| acute myeloid leukemia | MIDOSTAURIN | KIT | INHIBITOR | down |
| acute myeloid leukemia | MIDOSTAURIN | PDGFRB | INHIBITOR | down |
| acute myeloid leukemia | MIDOSTAURIN | PDGFRA | INHIBITOR | down |
| cystic fibrosis | ELEXACAFTOR | CFTR | POSITIVE MODULATOR | up |
| cystic fibrosis | INTERFERON GAMMA-1B | IFNGR1 | AGONIST | up |
| cystic fibrosis | INTERFERON GAMMA-1B | IFNGR2 | AGONIST | up |
| cystic fibrosis | IVACAFTOR | CFTR | ACTIVATOR, POSITIVE MODULATOR | up |
| cystic fibrosis | LUMACAFTOR | CFTR | STABILISER | unknown |
| cystic fibrosis | TEZACAFTOR | CFTR | POSITIVE MODULATOR | up |
| Duchenne muscular dystrophy | ATALUREN | RPS6 | MODULATOR | unknown |
| Duchenne muscular dystrophy | ATALUREN | RPL3 | MODULATOR | unknown |
| Duchenne muscular dystrophy | ATALUREN | RPL30 | MODULATOR | unknown |
| Duchenne muscular dystrophy | ATALUREN | RPLP1 | MODULATOR | unknown |
| Duchenne muscular dystrophy | ATALUREN | RPS5 | MODULATOR | unknown |
| Duchenne muscular dystrophy | ATALUREN | RPSA | MODULATOR | unknown |
| Duchenne muscular dystrophy | ATALUREN | RPS27A | MODULATOR | unknown |
| Duchenne muscular dystrophy | ATALUREN | RPL13A | MODULATOR | unknown |
| Duchenne muscular dystrophy | ATALUREN | RPS19 | MODULATOR | unknown |
| Duchenne muscular dystrophy | ATALUREN | RPL36A | MODULATOR | unknown |
| Duchenne muscular dystrophy | ATALUREN | RPS13 | MODULATOR | unknown |
| Duchenne muscular dystrophy | CASIMERSEN | DMD | POSITIVE MODULATOR | up |
| Duchenne muscular dystrophy | DEFLAZACORT | NR3C1 | AGONIST | up |
| Duchenne muscular dystrophy | ETEPLIRSEN | DMD | POSITIVE MODULATOR | up |
| Duchenne muscular dystrophy | GIVINOSTAT | HDAC4 | INHIBITOR | down |
| Duchenne muscular dystrophy | GIVINOSTAT | HDAC9 | INHIBITOR | down |
| Duchenne muscular dystrophy | GIVINOSTAT | HDAC2 | INHIBITOR | down |
| Duchenne muscular dystrophy | GIVINOSTAT | HDAC11 | INHIBITOR | down |
| Duchenne muscular dystrophy | GIVINOSTAT | HDAC8 | INHIBITOR | down |
| Duchenne muscular dystrophy | GIVINOSTAT | HDAC6 | INHIBITOR | down |
| Duchenne muscular dystrophy | GIVINOSTAT | HDAC5 | INHIBITOR | down |
| Duchenne muscular dystrophy | GIVINOSTAT | HDAC3 | INHIBITOR | down |
| Duchenne muscular dystrophy | GIVINOSTAT | HDAC1 | INHIBITOR | down |
| Duchenne muscular dystrophy | GIVINOSTAT | HDAC10 | INHIBITOR | down |
| Duchenne muscular dystrophy | GIVINOSTAT | HDAC7 | INHIBITOR | down |
| spinal muscular atrophy | NUSINERSEN | SMN2 | POSITIVE MODULATOR | up |
| spinal muscular atrophy | ONASEMNOGENE ABEPARVOVEC | SMN1 | EXOGENOUS GENE | unknown |
| spinal muscular atrophy | ONASEMNOGENE ABEPARVOVEC | SMN2 | EXOGENOUS GENE | unknown |
| spinal muscular atrophy | RISDIPLAM | SMN2 | POSITIVE MODULATOR | up |
| Huntington disease | ATOMOXETINE | SLC6A2 | INHIBITOR | down |
| Huntington disease | GUANFACINE | ADRA2B | AGONIST | up |
| Huntington disease | GUANFACINE | ADRA2A | AGONIST | up |
| Huntington disease | GUANFACINE | ADRA2C | AGONIST | up |
| Huntington disease | LISDEXAMFETAMINE | SLC18A2 | INHIBITOR | down |
| Huntington disease | LISDEXAMFETAMINE | SLC6A2 | RELEASING AGENT | unknown |
| Huntington disease | LISDEXAMFETAMINE | SLC6A3 | RELEASING AGENT | unknown |
| Huntington disease | METHYLPHENIDATE | SLC6A2 | INHIBITOR | down |
| Huntington disease | METHYLPHENIDATE | SLC6A3 | INHIBITOR | down |
| Huntington disease | TETRABENAZINE | SLC18A2 | INHIBITOR | down |
| amyotrophic lateral sclerosis | TOFERSEN | SOD1 | ANTISENSE INHIBITOR | unknown |
| Gaucher disease | ELIGLUSTAT | UGCG | INHIBITOR | down |
| Gaucher disease | MIGLUSTAT | UGCG | INHIBITOR | down |
| Fabry disease | MIGALASTAT | GLA | STABILISER | unknown |
| phenylketonuria | SAPROPTERIN | PAH | ACTIVATOR | up |
| hemophilia A | ANTIHEMOPHILIC FACTOR, PEGYLATED (MW 20000) HUMAN SEQUENCE RECOMBINANT | F8 | EXOGENOUS PROTEIN | unknown |
| hemophilia A | CONCIZUMAB | TFPI | INHIBITOR | down |
| hemophilia A | DAMOCTOCOG ALFA PEGOL | F8 | EXOGENOUS PROTEIN | unknown |
| hemophilia A | EFANESOCTOCOG ALFA | F8 | EXOGENOUS PROTEIN | unknown |
| hemophilia A | EFMOROCTOCOG ALFA | F8 | EXOGENOUS PROTEIN | unknown |
| hemophilia B | ALBUTREPENONACOG ALFA | F9 | EXOGENOUS PROTEIN | unknown |
| hemophilia B | COAGULATION FACTOR IX HUMAN | F9 | EXOGENOUS PROTEIN | unknown |
| hemophilia B | COAGULATION FACTOR IX RECOMBINANT HUMAN | F9 | EXOGENOUS PROTEIN | unknown |
| hemophilia B | CONCIZUMAB | TFPI | INHIBITOR | down |
| hemophilia B | EFTRENONACOG ALFA | F9 | EXOGENOUS PROTEIN | unknown |
| myasthenia gravis | AMBENONIUM | ACHE | INHIBITOR | down |
| myasthenia gravis | AMIFAMPRIDINE | KCND3 | BLOCKER | down |
| myasthenia gravis | AMIFAMPRIDINE | KCNH5 | BLOCKER | down |
| myasthenia gravis | AMIFAMPRIDINE | KCNS3 | BLOCKER | down |
| myasthenia gravis | AMIFAMPRIDINE | KCNV2 | BLOCKER | down |
| myasthenia gravis | AMIFAMPRIDINE | KCNA4 | BLOCKER | down |
| myasthenia gravis | AMIFAMPRIDINE | KCNA1 | BLOCKER | down |
| myasthenia gravis | AMIFAMPRIDINE | KCNA3 | BLOCKER | down |
| myasthenia gravis | AMIFAMPRIDINE | KCNA10 | BLOCKER | down |
| myasthenia gravis | AMIFAMPRIDINE | KCNA5 | BLOCKER | down |
| myasthenia gravis | AMIFAMPRIDINE | KCNC2 | BLOCKER | down |
| myasthenia gravis | AMIFAMPRIDINE | KCNC3 | BLOCKER | down |
| myasthenia gravis | AMIFAMPRIDINE | KCNC4 | BLOCKER | down |
| myasthenia gravis | AMIFAMPRIDINE | KCND1 | BLOCKER | down |
| myasthenia gravis | AMIFAMPRIDINE | KCND2 | BLOCKER | down |
| myasthenia gravis | AMIFAMPRIDINE | KCNG2 | BLOCKER | down |
| myasthenia gravis | AMIFAMPRIDINE | KCNG3 | BLOCKER | down |
| myasthenia gravis | AMIFAMPRIDINE | KCNH3 | BLOCKER | down |
| myasthenia gravis | AMIFAMPRIDINE | KCNH4 | BLOCKER | down |
| myasthenia gravis | AMIFAMPRIDINE | KCNH6 | BLOCKER | down |
| myasthenia gravis | AMIFAMPRIDINE | KCNH7 | BLOCKER | down |
| myasthenia gravis | AMIFAMPRIDINE | KCNH8 | BLOCKER | down |
| myasthenia gravis | AMIFAMPRIDINE | KCNQ4 | BLOCKER | down |
| myasthenia gravis | EDROPHONIUM | ACHE | INHIBITOR | down |
| myasthenia gravis | EFGARTIGIMOD ALFA | FCGRT | ANTAGONIST | down |
| myasthenia gravis | GUANIDINE | KCND3 | BLOCKER | down |
| myasthenia gravis | GUANIDINE | KCNH5 | BLOCKER | down |
| myasthenia gravis | GUANIDINE | KCNS3 | BLOCKER | down |
| myasthenia gravis | GUANIDINE | KCNV2 | BLOCKER | down |
| myasthenia gravis | GUANIDINE | KCNA4 | BLOCKER | down |
| myasthenia gravis | GUANIDINE | KCNA1 | BLOCKER | down |
| myasthenia gravis | GUANIDINE | KCNA3 | BLOCKER | down |
| myasthenia gravis | GUANIDINE | KCNA10 | BLOCKER | down |
| myasthenia gravis | GUANIDINE | KCNA5 | BLOCKER | down |
| myasthenia gravis | GUANIDINE | KCNC2 | BLOCKER | down |
| myasthenia gravis | GUANIDINE | KCNC3 | BLOCKER | down |
| myasthenia gravis | GUANIDINE | KCNC4 | BLOCKER | down |
| myasthenia gravis | GUANIDINE | KCND1 | BLOCKER | down |
| myasthenia gravis | GUANIDINE | KCND2 | BLOCKER | down |
| myasthenia gravis | GUANIDINE | KCNG2 | BLOCKER | down |
| myasthenia gravis | GUANIDINE | KCNG3 | BLOCKER | down |
| myasthenia gravis | GUANIDINE | KCNH3 | BLOCKER | down |
| myasthenia gravis | GUANIDINE | KCNH4 | BLOCKER | down |
| myasthenia gravis | GUANIDINE | KCNH6 | BLOCKER | down |
| myasthenia gravis | GUANIDINE | KCNH7 | BLOCKER | down |
| myasthenia gravis | GUANIDINE | KCNH8 | BLOCKER | down |
| myasthenia gravis | GUANIDINE | KCNQ4 | BLOCKER | down |
| narcolepsy | DEXTROAMPHETAMINE | SLC6A3 | RELEASING AGENT | unknown |
| narcolepsy | DEXTROAMPHETAMINE | SLC6A2 | RELEASING AGENT | unknown |
| narcolepsy | DEXTROAMPHETAMINE | SLC18A2 | INHIBITOR | down |
| narcolepsy | MODAFINIL | SLC6A3 | INHIBITOR | down |
| narcolepsy | OXYBATE | GABBR1 | AGONIST | up |
| narcolepsy | OXYBATE | GABBR2 | AGONIST | up |
| narcolepsy | PITOLISANT | HRH3 | INVERSE AGONIST | unknown |
| hereditary angioedema | BEROTRALSTAT | KLKB1 | INHIBITOR | down |
| hereditary angioedema | CONESTAT ALFA | SERPING1 | EXOGENOUS PROTEIN | unknown |
| hereditary angioedema | ECALLANTIDE | KLKB1 | INHIBITOR | down |
| hereditary angioedema | HUMAN C1-ESTERASE INHIBITOR | F12 | INHIBITOR | down |
| hereditary angioedema | HUMAN C1-ESTERASE INHIBITOR | KLKB1 | INHIBITOR | down |
| hereditary angioedema | HUMAN C1-ESTERASE INHIBITOR | C1S | INHIBITOR | down |
| hereditary angioedema | HUMAN C1-ESTERASE INHIBITOR | F11 | INHIBITOR | down |
| hereditary angioedema | ICATIBANT | BDKRB2 | ANTAGONIST | down |
| acromegaly | BROMOCRIPTINE | DRD2 | AGONIST | up |
| acromegaly | BROMOCRIPTINE | DRD3 | AGONIST | up |
| acromegaly | BROMOCRIPTINE | DRD4 | AGONIST | up |
| acromegaly | LANREOTIDE | SSTR5 | AGONIST | up |
| acromegaly | LANREOTIDE | SSTR2 | AGONIST | up |
| acromegaly | OCTREOTIDE | SSTR5 | AGONIST | up |
| acromegaly | OCTREOTIDE | SSTR2 | AGONIST | up |
| acromegaly | OCTREOTIDE | SSTR1 | AGONIST | up |
| acromegaly | OCTREOTIDE | SSTR3 | AGONIST | up |
| acromegaly | OCTREOTIDE | SSTR4 | AGONIST | up |
| acromegaly | PALTUSOTINE | SSTR2 | AGONIST | up |
| acromegaly | PASIREOTIDE | SSTR5 | AGONIST | up |
| acromegaly | PASIREOTIDE | SSTR2 | AGONIST | up |
| acromegaly | PASIREOTIDE | SSTR1 | AGONIST | up |
| acromegaly | PASIREOTIDE | SSTR3 | AGONIST | up |
| Cushing syndrome | LEVOKETOCONAZOLE | CYP11B1 | INHIBITOR | down |
| Cushing syndrome | LEVOKETOCONAZOLE | CYP11A1 | INHIBITOR | down |
| Cushing syndrome | LEVOKETOCONAZOLE | CYP11B2 | INHIBITOR | down |
| Cushing syndrome | LEVOKETOCONAZOLE | CYP17A1 | INHIBITOR | down |
| Cushing syndrome | MIFEPRISTONE | NR3C1 | ANTAGONIST | down |
| Cushing syndrome | MIFEPRISTONE | PGR | ANTAGONIST | down |
| Cushing syndrome | OSILODROSTAT | CYP11B1 | INHIBITOR | down |
| sarcoidosis | COLLAGENASE CLOSTRIDIUM HISTOLYTICUM | COL4A1 | HYDROLYTIC ENZYME | unknown |
| sarcoidosis | COLLAGENASE CLOSTRIDIUM HISTOLYTICUM | COL2A1 | HYDROLYTIC ENZYME | unknown |
| sarcoidosis | COLLAGENASE CLOSTRIDIUM HISTOLYTICUM | COL1A1 | HYDROLYTIC ENZYME | unknown |
| sarcoidosis | COLLAGENASE CLOSTRIDIUM HISTOLYTICUM | COL1A2 | HYDROLYTIC ENZYME | unknown |
| sarcoidosis | COLLAGENASE CLOSTRIDIUM HISTOLYTICUM | COL5A2 | HYDROLYTIC ENZYME | unknown |
| sarcoidosis | COLLAGENASE CLOSTRIDIUM HISTOLYTICUM | COL27A1 | HYDROLYTIC ENZYME | unknown |
| sarcoidosis | COLLAGENASE CLOSTRIDIUM HISTOLYTICUM | COL18A1 | HYDROLYTIC ENZYME | unknown |
| sarcoidosis | COLLAGENASE CLOSTRIDIUM HISTOLYTICUM | COL11A1 | HYDROLYTIC ENZYME | unknown |
| sarcoidosis | DEXAMETHASONE | NR3C1 | AGONIST | up |
| sarcoidosis | DEXAMETHASONE PHOSPHORIC ACID | NR3C1 | AGONIST | up |
| sarcoidosis | PREDNISOLONE | NR3C1 | AGONIST | up |
| sarcoidosis | PREDNISONE | NR3C1 | AGONIST | up |
| systemic sclerosis | BOSENTAN | EDNRA | ANTAGONIST | down |
| systemic sclerosis | BOSENTAN | EDNRB | ANTAGONIST | down |
| systemic sclerosis | NINTEDANIB | PDGFRB | INHIBITOR | down |
| systemic sclerosis | NINTEDANIB | PDGFRA | INHIBITOR | down |
| systemic sclerosis | NINTEDANIB | KDR | INHIBITOR | down |
| systemic sclerosis | NINTEDANIB | FGFR2 | INHIBITOR | down |
| systemic sclerosis | NINTEDANIB | FLT4 | INHIBITOR | down |
| systemic sclerosis | NINTEDANIB | FLT1 | INHIBITOR | down |
| systemic sclerosis | NINTEDANIB | FGFR3 | INHIBITOR | down |
| systemic sclerosis | NINTEDANIB | FGFR1 | INHIBITOR | down |
| systemic sclerosis | NINTEDANIB | FGFR4 | INHIBITOR | down |
| systemic sclerosis | POMALIDOMIDE | CRBN | INHIBITOR | down |
| systemic sclerosis | POMALIDOMIDE | CUL4A | INHIBITOR | down |
| systemic sclerosis | POMALIDOMIDE | DDB1 | INHIBITOR | down |
| systemic sclerosis | POMALIDOMIDE | RBX1 | INHIBITOR | down |
| systemic sclerosis | TOCILIZUMAB | IL6R | INHIBITOR | down |
| Behcet disease | APREMILAST | PDE4A | INHIBITOR | down |
| Behcet disease | APREMILAST | PDE4B | INHIBITOR | down |
| Behcet disease | APREMILAST | PDE4C | INHIBITOR | down |
| Behcet disease | APREMILAST | PDE4D | INHIBITOR | down |
| Behcet disease | EZOGABINE | KCNQ3 | OPENER | up |
| Behcet disease | EZOGABINE | KCNQ2 | OPENER | up |
| Behcet disease | EZOGABINE | KCNQ1 | OPENER | up |
| Behcet disease | EZOGABINE | KCNQ4 | OPENER | up |
| Behcet disease | EZOGABINE | KCNQ5 | OPENER | up |
| hidradenitis suppurativa | ADALIMUMAB | TNF | INHIBITOR | down |

Diseases with no Approved medicine that has a path (2): tuberculosis, Wilson disease.

## PART B. Opposite directions

Rules used, as asked. For each disease, a protein counts if at least one medicine of the **main Approved list** (not the two folded boxes) acts on it with direction up or down. Approved medicines whose direction on that protein is mixed or unknown are not used to decide. **One-way**: all those Approved medicines have the same direction. **Both-ways**: they disagree. A card is one medicine; a medicine acting on two proteins is one card, and is counted once in each column it belongs to.

### B7. The numbers, all diseases together

|  | New clues | In trials |
|---|---|---|
| cards in total | 3074 | 559 |
| cards pointing OPPOSITE to the Approved medicines on a one-way protein | 392 | 25 |
| cards pointing the SAME way on a one-way protein (for comparison) | 1501 | 327 |
| cards with mixed or unknown direction on a one-way protein | 104 | 26 |
| cards sitting on a both-ways protein | 143 | 19 |

- Diseases with at least one opposite card: **34 of 50** (34 have an opposite New clues card, 10 an opposite In trials card).
- Diseases with at least one one-way protein: 46. With at least one both-ways protein: 6. With no Approved medicine that has an up or down path at all: 4.
- One-way proteins in all (disease by disease): 450. Both-ways proteins: 8.
- The same counts by card-and-protein pair instead of by card: New clues opposite 540, same 3258, mixed or unknown 169, on both ways 176; In trials opposite 33, same 535, mixed or unknown 36, on both ways 21.

### B7. The numbers, disease by disease

NC = New clues cards, IT = In trials cards. "opp" = opposite on a one-way protein, "same" = same way on a one-way protein, "both" = on a both-ways protein.

| disease | Approved cards (with a path) | one-way proteins | both-ways proteins | NC total | NC opp | NC same | NC both | IT total | IT opp | IT same | IT both |
|---|---|---|---|---|---|---|---|---|---|---|---|
| asthma | 70 (54) | 20 | 1 | 126 | 26 | 81 | 28 | 13 | 2 | 9 | 0 |
| type 2 diabetes mellitus | 59 (23) | 10 | 0 | 11 | 2 | 7 | 0 | 11 | 2 | 8 | 0 |
| epilepsy | 54 (26) | 10 | 0 | 74 | 5 | 64 | 0 | 3 | 0 | 1 | 0 |
| rheumatoid arthritis | 69 (47) | 16 | 0 | 76 | 3 | 59 | 0 | 21 | 0 | 11 | 0 |
| psoriasis | 43 (29) | 18 | 0 | 65 | 2 | 59 | 0 | 15 | 0 | 13 | 0 |
| atopic eczema | 41 (34) | 15 | 0 | 100 | 5 | 78 | 0 | 26 | 0 | 24 | 0 |
| ulcerative colitis | 28 (25) | 17 | 0 | 100 | 2 | 98 | 0 | 10 | 0 | 9 | 0 |
| osteoporosis | 33 (21) | 9 | 0 | 50 | 10 | 31 | 0 | 8 | 0 | 6 | 0 |
| gout | 21 (10) | 19 | 0 | 52 | 0 | 50 | 0 | 3 | 0 | 3 | 0 |
| heart failure | 43 (30) | 19 | 2 | 113 | 10 | 61 | 39 | 26 | 1 | 17 | 6 |
| atrial fibrillation | 17 (11) | 14 | 0 | 72 | 0 | 61 | 0 | 15 | 0 | 15 | 0 |
| chronic obstructive pulmonary disease | 29 (24) | 15 | 0 | 142 | 22 | 106 | 0 | 14 | 2 | 8 | 0 |
| chronic kidney disease | 51 (26) | 12 | 0 | 49 | 5 | 33 | 0 | 22 | 0 | 17 | 0 |
| hypothyroidism | 8 (3) | 3 | 0 | 16 | 0 | 4 | 0 | 0 | 0 | 0 | 0 |
| depressive disorder | 33 (28) | 19 | 0 | 170 | 26 | 97 | 0 | 31 | 4 | 19 | 0 |
| schizophrenia | 45 (37) | 19 | 0 | 48 | 20 | 25 | 0 | 15 | 4 | 6 | 0 |
| bipolar disorder | 19 (19) | 21 | 0 | 150 | 8 | 104 | 0 | 28 | 1 | 17 | 0 |
| Parkinson disease | 43 (24) | 10 | 0 | 94 | 48 | 38 | 0 | 9 | 3 | 3 | 0 |
| Alzheimer disease | 21 (11) | 4 | 0 | 41 | 1 | 18 | 0 | 7 | 0 | 2 | 0 |
| glaucoma | 39 (21) | 10 | 2 | 76 | 9 | 23 | 47 | 1 | 0 | 0 | 1 |
| endometriosis | 10 (9) | 4 | 1 | 82 | 12 | 41 | 3 | 18 | 2 | 8 | 7 |
| tuberculosis | 22 (0) | 0 | 0 | 62 | 0 | 0 | 0 | 5 | 0 | 0 | 0 |
| malaria | 29 (3) | 9 | 0 | 92 | 1 | 41 | 0 | 0 | 0 | 0 | 0 |
| breast cancer | 73 (23) | 8 | 1 | 27 | 0 | 11 | 13 | 29 | 0 | 15 | 5 |
| prostate cancer | 30 (11) | 3 | 0 | 18 | 8 | 8 | 0 | 17 | 4 | 11 | 0 |
| colorectal cancer | 19 (7) | 6 | 0 | 23 | 2 | 12 | 0 | 44 | 0 | 30 | 0 |
| lung cancer | 8 (2) | 4 | 0 | 46 | 0 | 11 | 0 | 38 | 0 | 21 | 0 |
| melanoma | 20 (7) | 4 | 0 | 8 | 0 | 0 | 0 | 17 | 0 | 6 | 0 |
| chronic myeloid leukemia | 9 (8) | 20 | 0 | 28 | 2 | 21 | 0 | 14 | 0 | 10 | 0 |
| acute myeloid leukemia | 15 (7) | 7 | 0 | 21 | 1 | 7 | 0 | 19 | 0 | 13 | 0 |
| cystic fibrosis | 15 (6) | 3 | 0 | 2 | 1 | 0 | 0 | 1 | 0 | 0 | 0 |
| Duchenne muscular dystrophy | 8 (8) | 14 | 0 | 68 | 5 | 63 | 0 | 5 | 0 | 4 | 0 |
| spinal muscular atrophy | 4 (3) | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Huntington disease | 5 (5) | 6 | 0 | 175 | 9 | 52 | 0 | 6 | 0 | 0 | 0 |
| amyotrophic lateral sclerosis | 5 (1) | 0 | 0 | 23 | 0 | 0 | 0 | 2 | 0 | 0 | 0 |
| Gaucher disease | 6 (2) | 1 | 0 | 23 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Fabry disease | 4 (1) | 0 | 0 | 48 | 0 | 0 | 0 | 1 | 0 | 0 | 0 |
| phenylketonuria | 3 (1) | 1 | 0 | 69 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| hemophilia A | 18 (18) | 2 | 0 | 38 | 4 | 1 | 0 | 10 | 0 | 0 | 0 |
| hemophilia B | 11 (11) | 1 | 0 | 21 | 0 | 1 | 0 | 7 | 0 | 0 | 0 |
| myasthenia gravis | 12 (12) | 24 | 1 | 20 | 1 | 6 | 13 | 3 | 0 | 3 | 0 |
| narcolepsy | 5 (4) | 4 | 0 | 65 | 0 | 13 | 0 | 3 | 0 | 2 | 0 |
| Wilson disease | 4 (0) | 0 | 0 | 18 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| hereditary angioedema | 9 (7) | 6 | 0 | 61 | 9 | 12 | 0 | 1 | 0 | 0 | 0 |
| acromegaly | 6 (6) | 9 | 0 | 125 | 52 | 7 | 0 | 4 | 0 | 1 | 0 |
| Cushing syndrome | 3 (3) | 6 | 0 | 102 | 72 | 4 | 0 | 2 | 0 | 2 | 0 |
| sarcoidosis | 5 (5) | 1 | 0 | 58 | 2 | 44 | 0 | 13 | 0 | 8 | 0 |
| systemic sclerosis | 4 (4) | 16 | 0 | 38 | 3 | 35 | 0 | 2 | 0 | 2 | 0 |
| Behcet disease | 2 (2) | 9 | 0 | 71 | 4 | 10 | 0 | 10 | 0 | 1 | 0 |
| hidradenitis suppurativa | 1 (1) | 1 | 0 | 17 | 0 | 4 | 0 | 10 | 0 | 2 | 0 |

### B5 and B6. Every one-way protein, with its counts

| disease | protein | direction of its Approved medicines | Approved medicines | NC opposite | NC same | IT opposite | IT same |
|---|---|---|---|---|---|---|---|
| asthma | ADRB2 | up | ALBUTEROL, BAMBUTEROL, BITOLTEROL, EPINEPHRINE, FORMOTEROL, INDACATEROL, ISOETHARINE, LEVOSALBUTAMOL, PIRBUTEROL, PROCATEROL, PROTOKYLOL, RIMITEROL, SALMETEROL, TERBUTALINE, VILANTEROL | 11 | 12 | 2 | 2 |
| asthma | NR3C1 | up | BECLOMETHASONE DIPROPIONATE, BETAMETHASONE ACETATE, BUDESONIDE, CICLESONIDE, CORTISONE ACETATE, DEXAMETHASONE, DEXAMETHASONE PHOSPHORIC ACID, FLUNISOLIDE, FLUPREDNISOLONE, FLUTICASONE FUROATE, FLUTICASONE PROPIONATE, HYDROCORTISONE, HYDROCORTISONE HEMISUCCINATE ANHYDROUS, METHYLPREDNISOLONE, METHYLPREDNISOLONE ACETATE, METHYLPREDNISOLONE HEMISUCCINATE, MOMETASONE FUROATE, PREDNISOLONE, PREDNISOLONE PHOSPHORIC ACID, PREDNISONE, TRIAMCINOLONE ACETONIDE | 2 | 29 | 0 | 6 |
| asthma | IL5RA | down | BENRALIZUMAB | 0 | 0 | 0 | 0 |
| asthma | IL5 | down | DEPEMOKIMAB, MEPOLIZUMAB, RESLIZUMAB | 0 | 0 | 0 | 0 |
| asthma | IL4R | down | DUPILUMAB | 0 | 0 | 0 | 0 |
| asthma | ADRA2A | up | EPINEPHRINE | 9 | 19 | 0 | 0 |
| asthma | CHRM2 | down | GLYCOPYRRONIUM | 2 | 9 | 0 | 0 |
| asthma | CYSLTR1 | down | MONTELUKAST, PRANLUKAST, ZAFIRLUKAST | 0 | 0 | 0 | 0 |
| asthma | IGHE | down | OMALIZUMAB | 0 | 0 | 0 | 0 |
| asthma | PDE4D | down | ROFLUMILAST, THEOPHYLLINE ANHYDROUS | 0 | 9 | 0 | 1 |
| asthma | PDE4A | down | ROFLUMILAST, THEOPHYLLINE ANHYDROUS | 0 | 9 | 0 | 1 |
| asthma | PDE4B | down | ROFLUMILAST, THEOPHYLLINE ANHYDROUS | 0 | 9 | 0 | 1 |
| asthma | PDE4C | down | ROFLUMILAST, THEOPHYLLINE ANHYDROUS | 0 | 9 | 0 | 1 |
| asthma | TSLP | down | TEZEPELUMAB | 0 | 0 | 0 | 0 |
| asthma | ADORA1 | down | THEOPHYLLINE ANHYDROUS | 2 | 1 | 0 | 0 |
| asthma | ADORA2A | down | THEOPHYLLINE ANHYDROUS | 3 | 3 | 0 | 0 |
| asthma | ADORA2B | down | THEOPHYLLINE ANHYDROUS | 2 | 2 | 0 | 0 |
| asthma | ADORA3 | down | THEOPHYLLINE ANHYDROUS | 1 | 1 | 0 | 0 |
| asthma | PDE3B | down | THEOPHYLLINE ANHYDROUS | 0 | 5 | 0 | 1 |
| asthma | PDE3A | down | THEOPHYLLINE ANHYDROUS | 0 | 10 | 0 | 1 |
| type 2 diabetes mellitus | GLP1R | up | ALBIGLUTIDE, DULAGLUTIDE, EXENATIDE, LIRAGLUTIDE, LIXISENATIDE, SEMAGLUTIDE, TIRZEPATIDE | 0 | 0 | 1 | 0 |
| type 2 diabetes mellitus | KCNJ11 | down | CHLORPROPAMIDE, GLIMEPIRIDE, GLIPIZIDE, GLYBURIDE, MITIGLINIDE CALCIUM DIHYDRATE, NATEGLINIDE, REPAGLINIDE, TOLAZAMIDE, TOLBUTAMIDE | 2 | 0 | 1 | 2 |
| type 2 diabetes mellitus | ABCC8 | down | CHLORPROPAMIDE, GLIMEPIRIDE, GLIPIZIDE, GLYBURIDE, MITIGLINIDE CALCIUM DIHYDRATE, NATEGLINIDE, REPAGLINIDE, TOLAZAMIDE, TOLBUTAMIDE | 0 | 0 | 0 | 2 |
| type 2 diabetes mellitus | INSR | up | INSULIN DEGLUDEC, INSULIN DETEMIR, INSULIN GLARGINE, INSULIN HUMAN, INSULIN ICODEC | 0 | 2 | 0 | 6 |
| type 2 diabetes mellitus | GPD2 | down | METFORMIN | 0 | 0 | 0 | 0 |
| type 2 diabetes mellitus | NDUFS4 | down | METFORMIN | 0 | 0 | 0 | 0 |
| type 2 diabetes mellitus | MT-ND1 | down | METFORMIN | 0 | 0 | 0 | 0 |
| type 2 diabetes mellitus | NDUFB8 | down | METFORMIN | 0 | 0 | 0 | 0 |
| type 2 diabetes mellitus | PPARG | up | PIOGLITAZONE | 0 | 5 | 0 | 0 |
| type 2 diabetes mellitus | GIPR | up | TIRZEPATIDE | 0 | 0 | 0 | 0 |
| epilepsy | SCN1A | down | CARBAMAZEPINE, CENOBAMATE, ESLICARBAZEPINE, ESLICARBAZEPINE ACETATE, ETHOTOIN, FOSPHENYTOIN, LACOSAMIDE, LAMOTRIGINE, MEPHENYTOIN, OXCARBAZEPINE, PHENACEMIDE, PHENYTOIN, PRIMIDONE, RUFINAMIDE, TOPIRAMATE, ZONISAMIDE | 0 | 26 | 0 | 0 |
| epilepsy | SCN2A | down | CARBAMAZEPINE, CENOBAMATE, ESLICARBAZEPINE, ESLICARBAZEPINE ACETATE, ETHOTOIN, FOSPHENYTOIN, LACOSAMIDE, LAMOTRIGINE, MEPHENYTOIN, OXCARBAZEPINE, PHENACEMIDE, PHENYTOIN, PRIMIDONE, RUFINAMIDE, TOPIRAMATE, ZONISAMIDE | 0 | 26 | 0 | 0 |
| epilepsy | SCN8A | down | CARBAMAZEPINE, CENOBAMATE, ESLICARBAZEPINE, ESLICARBAZEPINE ACETATE, ETHOTOIN, FOSPHENYTOIN, LACOSAMIDE, LAMOTRIGINE, MEPHENYTOIN, OXCARBAZEPINE, PHENACEMIDE, PHENYTOIN, PRIMIDONE, RUFINAMIDE, TOPIRAMATE, ZONISAMIDE | 0 | 26 | 0 | 0 |
| epilepsy | SCN3A | down | CARBAMAZEPINE, CENOBAMATE, ESLICARBAZEPINE, ESLICARBAZEPINE ACETATE, ETHOTOIN, FOSPHENYTOIN, LACOSAMIDE, LAMOTRIGINE, MEPHENYTOIN, OXCARBAZEPINE, PHENACEMIDE, PHENYTOIN, PRIMIDONE, RUFINAMIDE, TOPIRAMATE, ZONISAMIDE | 0 | 26 | 0 | 0 |
| epilepsy | GABRG2 | up | CENOBAMATE, CLOBAZAM, CLONAZEPAM, DIAZEPAM, GANAXOLONE, METHARBITAL, MIDAZOLAM, PRIMIDONE, TOPIRAMATE | 1 | 34 | 0 | 1 |
| epilepsy | GABRA1 | up | CENOBAMATE, CLOBAZAM, CLONAZEPAM, DIAZEPAM, GANAXOLONE, METHARBITAL, MIDAZOLAM, PRIMIDONE, TOPIRAMATE | 1 | 35 | 0 | 1 |
| epilepsy | GABRB3 | up | CENOBAMATE, CLOBAZAM, CLONAZEPAM, DIAZEPAM, GANAXOLONE, METHARBITAL, MIDAZOLAM, PRIMIDONE, TOPIRAMATE | 1 | 33 | 0 | 1 |
| epilepsy | GABRB2 | up | CENOBAMATE, CLOBAZAM, CLONAZEPAM, DIAZEPAM, GANAXOLONE, METHARBITAL, MIDAZOLAM, PRIMIDONE, TOPIRAMATE | 1 | 32 | 0 | 1 |
| epilepsy | KCNQ2 | up | EZOGABINE | 4 | 0 | 0 | 0 |
| epilepsy | GRIN2A | down | FELBAMATE | 0 | 4 | 0 | 0 |
| rheumatoid arthritis | CD80 | down | ABATACEPT | 0 | 0 | 0 | 1 |
| rheumatoid arthritis | CD86 | down | ABATACEPT | 0 | 0 | 0 | 1 |
| rheumatoid arthritis | PTGS2 | down | ACECLOFENAC, CELECOXIB, DICLOFENAC, DIFLUNISAL, ETODOLAC, ETORICOXIB, FENOPROFEN, FLURBIPROFEN, IBUPROFEN, IGURATIMOD, INDOMETHACIN, KETOPROFEN, MECLOFENAMIC ACID, MELOXICAM, NABUMETONE, NAPROXEN, OXAPROZIN, PIROXICAM, SULFASALAZINE, SULINDAC, TOLMETIN | 0 | 9 | 0 | 1 |
| rheumatoid arthritis | TNF | down | ADALIMUMAB, CERTOLIZUMAB PEGOL, ETANERCEPT, GOLIMUMAB, INFLIXIMAB, OZORALIZUMAB | 0 | 1 | 0 | 0 |
| rheumatoid arthritis | JAK1 | down | BARICITINIB, FILGOTINIB, PEFICITINIB, TOFACITINIB, UPADACITINIB | 0 | 3 | 0 | 1 |
| rheumatoid arthritis | JAK2 | down | BARICITINIB, FILGOTINIB, PEFICITINIB, TOFACITINIB, UPADACITINIB | 0 | 5 | 0 | 1 |
| rheumatoid arthritis | NR3C1 | up | CORTISONE ACETATE, DEXAMETHASONE, DEXAMETHASONE PHOSPHORIC ACID, HYDROCORTISONE, METHYLPREDNISOLONE, METHYLPREDNISOLONE ACETATE, METHYLPREDNISOLONE HEMISUCCINATE, PREDNISOLONE, PREDNISONE, TRIAMCINOLONE ACETONIDE | 2 | 40 | 0 | 5 |
| rheumatoid arthritis | PTGS1 | down | DICLOFENAC, DIFLUNISAL, FENOPROFEN, FLURBIPROFEN, IBUPROFEN, INDOMETHACIN, KETOPROFEN, MECLOFENAMIC ACID, NAPROXEN, OXAPROZIN, PIROXICAM, SULFASALAZINE, SULINDAC, TOLMETIN | 0 | 9 | 0 | 1 |
| rheumatoid arthritis | TYK2 | down | FILGOTINIB, PEFICITINIB, TOFACITINIB, UPADACITINIB | 0 | 1 | 0 | 1 |
| rheumatoid arthritis | JAK3 | down | FILGOTINIB, PEFICITINIB, TOFACITINIB, UPADACITINIB | 0 | 1 | 0 | 2 |
| rheumatoid arthritis | TLR7 | down | HYDROXYCHLOROQUINE | 1 | 0 | 0 | 0 |
| rheumatoid arthritis | TLR9 | down | HYDROXYCHLOROQUINE | 0 | 0 | 0 | 0 |
| rheumatoid arthritis | TRAF3IP2 | down | IGURATIMOD | 0 | 0 | 0 | 0 |
| rheumatoid arthritis | MIF | down | IGURATIMOD | 0 | 0 | 0 | 0 |
| rheumatoid arthritis | DHFR | down | METHOTREXATE | 0 | 2 | 0 | 0 |
| rheumatoid arthritis | IL6R | down | SARILUMAB, TOCILIZUMAB | 0 | 0 | 0 | 2 |
| psoriasis | RXRA | up | ACITRETIN | 0 | 2 | 0 | 0 |
| psoriasis | RARA | up | ACITRETIN, TAZAROTENE | 0 | 4 | 0 | 0 |
| psoriasis | RARB | up | ACITRETIN, TAZAROTENE | 0 | 4 | 0 | 0 |
| psoriasis | RARG | up | ACITRETIN, TAZAROTENE | 0 | 6 | 0 | 0 |
| psoriasis | TNF | down | ADALIMUMAB, ETANERCEPT, INFLIXIMAB | 0 | 1 | 0 | 1 |
| psoriasis | PDE4A | down | APREMILAST, ROFLUMILAST | 0 | 10 | 0 | 0 |
| psoriasis | PDE4D | down | APREMILAST, ROFLUMILAST | 0 | 10 | 0 | 0 |
| psoriasis | PDE4B | down | APREMILAST, ROFLUMILAST | 0 | 10 | 0 | 0 |
| psoriasis | PDE4C | down | APREMILAST, ROFLUMILAST | 0 | 10 | 0 | 0 |
| psoriasis | NR3C1 | up | BETAMETHASONE DIPROPIONATE, CLOBETASOL PROPIONATE, DESOXIMETASONE, DEXAMETHASONE, DEXAMETHASONE PHOSPHORIC ACID, FLUOCINOLONE ACETONIDE, HYDROCORTISONE, PREDNISOLONE, PREDNISONE | 2 | 32 | 0 | 8 |
| psoriasis | IL17A | down | BIMEKIZUMAB, IXEKIZUMAB, SECUKINUMAB | 0 | 1 | 0 | 0 |
| psoriasis | IL17RA | down | BRODALUMAB | 0 | 0 | 0 | 0 |
| psoriasis | VDR | up | CALCIPOTRIENE, CALCITRIOL | 0 | 6 | 0 | 2 |
| psoriasis | IL12B | down | GUSELKUMAB, RISANKIZUMAB, TILDRAKIZUMAB, USTEKINUMAB | 0 | 0 | 0 | 2 |
| psoriasis | IL23A | down | GUSELKUMAB, RISANKIZUMAB, TILDRAKIZUMAB, USTEKINUMAB | 0 | 0 | 0 | 2 |
| psoriasis | DHFR | down | METHOTREXATE | 0 | 2 | 0 | 0 |
| psoriasis | AHR | up | TAPINAROF | 0 | 0 | 0 | 0 |
| psoriasis | IL12A | down | USTEKINUMAB | 0 | 0 | 0 | 1 |
| atopic eczema | JAK1 | down | ABROCITINIB, BARICITINIB, DELGOCITINIB, RUXOLITINIB, UPADACITINIB | 0 | 2 | 0 | 1 |
| atopic eczema | SLC6A2 | down | ATOMOXETINE, DOXEPIN, METHYLPHENIDATE | 0 | 26 | 0 | 0 |
| atopic eczema | JAK2 | down | BARICITINIB, DELGOCITINIB, RUXOLITINIB, UPADACITINIB | 0 | 5 | 0 | 1 |
| atopic eczema | NR3C1 | up | CORTISONE ACETATE, DESONIDE, DEXAMETHASONE, DEXAMETHASONE PHOSPHORIC ACID, FLUOCINOLONE ACETONIDE, FLUTICASONE PROPIONATE, HYDROCORTISONE, HYDROCORTISONE BUTYRATE, METHYLPREDNISOLONE, PREDNISOLONE, PREDNISONE | 2 | 27 | 0 | 16 |
| atopic eczema | PDE4A | down | CRISABOROLE | 0 | 9 | 0 | 2 |
| atopic eczema | PDE4D | down | CRISABOROLE | 0 | 9 | 0 | 2 |
| atopic eczema | PDE4B | down | CRISABOROLE | 0 | 9 | 0 | 2 |
| atopic eczema | PDE4C | down | CRISABOROLE | 0 | 9 | 0 | 2 |
| atopic eczema | TYK2 | down | DELGOCITINIB, RUXOLITINIB, UPADACITINIB | 0 | 1 | 0 | 1 |
| atopic eczema | JAK3 | down | DELGOCITINIB, RUXOLITINIB, UPADACITINIB | 0 | 2 | 0 | 1 |
| atopic eczema | HRH1 | down | DESLORATADINE, DOXEPIN, EPINASTINE, FEXOFENADINE, LEVOCETIRIZINE, OLOPATADINE, PROMETHAZINE | 3 | 8 | 0 | 5 |
| atopic eczema | IL4R | down | DUPILUMAB | 0 | 0 | 0 | 0 |
| atopic eczema | IL13 | down | LEBRIKIZUMAB, TRALOKINUMAB | 0 | 0 | 0 | 0 |
| atopic eczema | IL31RA | down | NEMOLIZUMAB | 0 | 0 | 0 | 0 |
| atopic eczema | FKBP1A | down | PIMECROLIMUS, TACROLIMUS ANHYDROUS | 0 | 4 | 0 | 0 |
| ulcerative colitis | TNF | down | ADALIMUMAB, GOLIMUMAB, INFLIXIMAB | 0 | 3 | 0 | 1 |
| ulcerative colitis | PPAT | down | AZATHIOPRINE | 0 | 0 | 0 | 1 |
| ulcerative colitis | PPARG | up | BALSALAZIDE, MESALAMINE, OLSALAZINE | 0 | 3 | 0 | 0 |
| ulcerative colitis | PTGS2 | down | BALSALAZIDE, MESALAMINE, OLSALAZINE, SULFASALAZINE | 0 | 39 | 0 | 0 |
| ulcerative colitis | PTGS1 | down | BALSALAZIDE, MESALAMINE, OLSALAZINE, SULFASALAZINE | 0 | 30 | 0 | 0 |
| ulcerative colitis | ALOX5 | down | BALSALAZIDE, MESALAMINE, OLSALAZINE, SULFASALAZINE | 0 | 2 | 0 | 0 |
| ulcerative colitis | NR3C1 | up | BETAMETHASONE ACETATE, BETAMETHASONE PHOSPHORIC ACID, BUDESONIDE, DEXAMETHASONE, DEXAMETHASONE PHOSPHORIC ACID, HYDROCORTISONE, METHYLPREDNISOLONE, PREDNISOLONE, PREDNISONE | 2 | 37 | 0 | 4 |
| ulcerative colitis | S1PR1 | up | ETRASIMOD | 0 | 3 | 0 | 0 |
| ulcerative colitis | IL12B | down | GUSELKUMAB, MIRIKIZUMAB, RISANKIZUMAB, USTEKINUMAB | 0 | 2 | 0 | 0 |
| ulcerative colitis | IL23A | down | GUSELKUMAB, MIRIKIZUMAB, RISANKIZUMAB, USTEKINUMAB | 0 | 2 | 0 | 0 |
| ulcerative colitis | JAK2 | down | UPADACITINIB | 0 | 7 | 0 | 2 |
| ulcerative colitis | JAK3 | down | UPADACITINIB | 0 | 2 | 0 | 3 |
| ulcerative colitis | TYK2 | down | UPADACITINIB | 0 | 2 | 0 | 2 |
| ulcerative colitis | JAK1 | down | UPADACITINIB | 0 | 5 | 0 | 2 |
| ulcerative colitis | IL12A | down | USTEKINUMAB | 0 | 1 | 0 | 0 |
| ulcerative colitis | ITGA4 | down | VEDOLIZUMAB | 0 | 1 | 0 | 0 |
| ulcerative colitis | ITGB7 | down | VEDOLIZUMAB | 0 | 1 | 0 | 0 |
| osteoporosis | PTH1R | up | ABALOPARATIDE, TERIPARATIDE, TERIPARATIDE ACETATE | 0 | 1 | 0 | 1 |
| osteoporosis | FDPS | down | ALENDRONIC ACID, IBANDRONIC ACID, MINODRONIC ACID, RISEDRONIC ACID, ZOLEDRONIC ACID ANHYDROUS | 0 | 0 | 0 | 1 |
| osteoporosis | VDR | up | CHOLECALCIFEROL, ELDECALCITOL | 0 | 5 | 0 | 3 |
| osteoporosis | TNFSF11 | down | DENOSUMAB | 0 | 0 | 0 | 0 |
| osteoporosis | ESR1 | up | ESTRADIOL, ESTROGENS, CONJUGATED, ESTROGENS, CONJUGATED SYNTHETIC A, ESTRONE SULFURIC ACID | 1 | 13 | 0 | 0 |
| osteoporosis | ESR2 | up | ESTROGENS, CONJUGATED, ESTROGENS, CONJUGATED SYNTHETIC A | 0 | 5 | 0 | 0 |
| osteoporosis | SOST | down | ROMOSOZUMAB | 0 | 0 | 0 | 0 |
| osteoporosis | CALCR | up | SMC021 | 0 | 2 | 0 | 1 |
| osteoporosis | AR | up | TESTOSTERONE | 9 | 10 | 0 | 0 |
| gout | XDH | down | ALLOPURINOL, FEBUXOSTAT, TOPIROXOSTAT | 0 | 0 | 0 | 0 |
| gout | TUBA1B | down | COLCHICINE | 0 | 16 | 0 | 0 |
| gout | TUBB | down | COLCHICINE | 0 | 16 | 0 | 0 |
| gout | TUBA1C | down | COLCHICINE | 0 | 16 | 0 | 0 |
| gout | TUBA3C | down | COLCHICINE | 0 | 16 | 0 | 0 |
| gout | TUBA3E | down | COLCHICINE | 0 | 16 | 0 | 0 |
| gout | TUBA4A | down | COLCHICINE | 0 | 16 | 0 | 0 |
| gout | TUBB1 | down | COLCHICINE | 0 | 16 | 0 | 0 |
| gout | TUBB2A | down | COLCHICINE | 0 | 16 | 0 | 0 |
| gout | TUBB2B | down | COLCHICINE | 0 | 16 | 0 | 0 |
| gout | TUBB3 | down | COLCHICINE | 0 | 16 | 0 | 0 |
| gout | TUBB4A | down | COLCHICINE | 0 | 16 | 0 | 0 |
| gout | TUBB4B | down | COLCHICINE | 0 | 16 | 0 | 0 |
| gout | TUBB6 | down | COLCHICINE | 0 | 16 | 0 | 0 |
| gout | TUBB8 | down | COLCHICINE | 0 | 16 | 0 | 0 |
| gout | SLC22A12 | down | DOTINURAD, LESINURAD, SULFINPYRAZONE | 0 | 0 | 0 | 0 |
| gout | PTGS2 | down | INDOMETHACIN, NAPROXEN | 0 | 33 | 0 | 3 |
| gout | PTGS1 | down | INDOMETHACIN, NAPROXEN | 0 | 27 | 0 | 1 |
| gout | SLC22A11 | down | PROBENECID | 0 | 0 | 0 | 0 |
| heart failure | CACNA1D | down | AMLODIPINE | 0 | 21 | 0 | 2 |
| heart failure | AGTR1 | down | CANDESARTAN CILEXETIL, OLMESARTAN MEDOXOMIL, VALSARTAN | 1 | 8 | 0 | 2 |
| heart failure | ACE | down | CAPTOPRIL, ENALAPRIL, FOSINOPRIL, LISINOPRIL ANHYDROUS, QUINAPRIL, RAMIPRIL, TRANDOLAPRIL | 0 | 6 | 0 | 1 |
| heart failure | ADRB3 | down | CARVEDILOL | 5 | 2 | 1 | 0 |
| heart failure | SLC5A2 | down | DAPAGLIFLOZIN, EMPAGLIFLOZIN, SOTAGLIFLOZIN | 0 | 4 | 0 | 3 |
| heart failure | ATP1B1 | down | DESLANOSIDE, DIGITOXIN, DIGOXIN | 0 | 1 | 0 | 0 |
| heart failure | ATP1A1 | down | DESLANOSIDE, DIGITOXIN, DIGOXIN | 0 | 1 | 0 | 0 |
| heart failure | ATP1A3 | down | DESLANOSIDE, DIGITOXIN, DIGOXIN | 0 | 1 | 0 | 0 |
| heart failure | FXYD2 | down | DESLANOSIDE, DIGITOXIN, DIGOXIN | 0 | 1 | 0 | 0 |
| heart failure | ATP1A2 | down | DESLANOSIDE, DIGITOXIN, DIGOXIN | 0 | 1 | 0 | 0 |
| heart failure | ATP1A4 | down | DESLANOSIDE, DIGITOXIN, DIGOXIN | 0 | 1 | 0 | 0 |
| heart failure | ATP1B2 | down | DESLANOSIDE, DIGITOXIN, DIGOXIN | 0 | 1 | 0 | 0 |
| heart failure | NR3C2 | down | EPLERENONE, FINERENONE, SPIRONOLACTONE | 3 | 6 | 0 | 0 |
| heart failure | SLC12A3 | down | HYDROCHLOROTHIAZIDE | 0 | 5 | 0 | 2 |
| heart failure | GUCY1A1 | up | ISOSORBIDE DINITRATE, NITROGLYCERIN, VERICIGUAT | 1 | 2 | 0 | 2 |
| heart failure | GUCY1B1 | up | ISOSORBIDE DINITRATE, NITROGLYCERIN, VERICIGUAT | 1 | 2 | 0 | 2 |
| heart failure | PDE3A | down | MILRINONE | 0 | 7 | 0 | 3 |
| heart failure | MME | down | SACUBITRIL | 0 | 1 | 0 | 0 |
| heart failure | SLC12A1 | down | TORSEMIDE | 0 | 0 | 0 | 2 |
| atrial fibrillation | F10 | down | APIXABAN, EDOXABAN, RIVAROXABAN | 0 | 2 | 0 | 1 |
| atrial fibrillation | ATP1B2 | down | DIGOXIN | 0 | 2 | 0 | 0 |
| atrial fibrillation | CACNA1D | down | DILTIAZEM, DRONEDARONE | 0 | 20 | 0 | 1 |
| atrial fibrillation | CACNA1C | down | DILTIAZEM, DRONEDARONE | 0 | 20 | 0 | 1 |
| atrial fibrillation | KCNH2 | down | DOFETILIDE, IBUTILIDE, VERNAKALANT | 0 | 3 | 0 | 2 |
| atrial fibrillation | SCN5A | down | DRONEDARONE, PROPAFENONE, VERNAKALANT | 0 | 33 | 0 | 7 |
| atrial fibrillation | KCNJ2 | down | DRONEDARONE | 0 | 0 | 0 | 0 |
| atrial fibrillation | HCN4 | down | DRONEDARONE | 0 | 0 | 0 | 1 |
| atrial fibrillation | SCN10A | down | DRONEDARONE, PROPAFENONE | 0 | 33 | 0 | 5 |
| atrial fibrillation | KCNJ5 | down | VERNAKALANT | 0 | 0 | 0 | 0 |
| atrial fibrillation | KCNA5 | down | VERNAKALANT | 0 | 3 | 0 | 0 |
| atrial fibrillation | KCND3 | down | VERNAKALANT | 0 | 3 | 0 | 0 |
| atrial fibrillation | KCNJ3 | down | VERNAKALANT | 0 | 0 | 0 | 0 |
| atrial fibrillation | VKORC1 | down | WARFARIN | 0 | 1 | 0 | 3 |
| chronic obstructive pulmonary disease | CHRM3 | down | ACLIDINIUM, GLYCOPYRRONIUM, IPRATROPIUM, REVEFENACIN, TIOTROPIUM, UMECLIDINIUM | 5 | 21 | 1 | 1 |
| chronic obstructive pulmonary disease | ADRB2 | up | ALBUTEROL, ARFORMOTEROL, BITOLTEROL, FORMOTEROL, INDACATEROL, OLODATEROL, SALMETEROL, VILANTEROL | 10 | 19 | 1 | 2 |
| chronic obstructive pulmonary disease | NR3C1 | up | BECLOMETHASONE DIPROPIONATE, BUDESONIDE, FLUOROMETHOLONE, FLUTICASONE FUROATE, FLUTICASONE PROPIONATE, MEPREDNISONE, PREDNISOLONE PHOSPHORIC ACID | 2 | 39 | 0 | 5 |
| chronic obstructive pulmonary disease | PDE4A | down | ENSIFENTRINE, ROFLUMILAST, THEOPHYLLINE ANHYDROUS | 0 | 9 | 0 | 0 |
| chronic obstructive pulmonary disease | PDE4D | down | ENSIFENTRINE, ROFLUMILAST, THEOPHYLLINE ANHYDROUS | 0 | 9 | 0 | 0 |
| chronic obstructive pulmonary disease | PDE4B | down | ENSIFENTRINE, ROFLUMILAST, THEOPHYLLINE ANHYDROUS | 0 | 9 | 0 | 0 |
| chronic obstructive pulmonary disease | PDE4C | down | ENSIFENTRINE, ROFLUMILAST, THEOPHYLLINE ANHYDROUS | 0 | 9 | 0 | 0 |
| chronic obstructive pulmonary disease | PDE3A | down | ENSIFENTRINE, THEOPHYLLINE ANHYDROUS | 0 | 10 | 0 | 0 |
| chronic obstructive pulmonary disease | PDE3B | down | ENSIFENTRINE, THEOPHYLLINE ANHYDROUS | 0 | 5 | 0 | 0 |
| chronic obstructive pulmonary disease | CHRM1 | down | GLYCOPYRRONIUM | 3 | 23 | 0 | 0 |
| chronic obstructive pulmonary disease | CHRM2 | down | GLYCOPYRRONIUM | 2 | 8 | 0 | 1 |
| chronic obstructive pulmonary disease | CHRM4 | down | GLYCOPYRRONIUM | 1 | 1 | 0 | 0 |
| chronic obstructive pulmonary disease | CHRM5 | down | GLYCOPYRRONIUM | 0 | 1 | 0 | 0 |
| chronic obstructive pulmonary disease | ADORA1 | down | THEOPHYLLINE ANHYDROUS | 2 | 1 | 0 | 0 |
| chronic obstructive pulmonary disease | ADORA2A | down | THEOPHYLLINE ANHYDROUS | 3 | 3 | 0 | 0 |
| chronic kidney disease | VDR | up | CALCIFEDIOL ANHYDROUS, CALCITRIOL, DOXERCALCIFEROL, PARICALCITOL | 0 | 3 | 0 | 3 |
| chronic kidney disease | SLC12A3 | down | CHLOROTHIAZIDE, CHLORTHALIDONE, HYDROCHLOROTHIAZIDE | 0 | 9 | 0 | 1 |
| chronic kidney disease | CASR | up | CINACALCET, ETELCALCETIDE | 0 | 1 | 0 | 0 |
| chronic kidney disease | SLC5A2 | down | DAPAGLIFLOZIN, EMPAGLIFLOZIN, SOTAGLIFLOZIN | 0 | 1 | 0 | 5 |
| chronic kidney disease | EGLN2 | down | DAPRODUSTAT, ROXADUSTAT, VADADUSTAT | 0 | 0 | 0 | 1 |
| chronic kidney disease | EGLN1 | down | DAPRODUSTAT, ROXADUSTAT, VADADUSTAT | 0 | 0 | 0 | 2 |
| chronic kidney disease | EGLN3 | down | DAPRODUSTAT, ROXADUSTAT, VADADUSTAT | 0 | 0 | 0 | 1 |
| chronic kidney disease | P4HTM | down | DAPRODUSTAT, ROXADUSTAT | 0 | 0 | 0 | 0 |
| chronic kidney disease | EPOR | up | DARBEPOETIN ALFA, EPOETIN ALFA, EPOETIN BETA, EPOETIN DELTA, EPOETIN THETA, EPOETIN ZETA, METHOXY POLYETHYLENE GLYCOL-EPOETIN BETA | 0 | 0 | 0 | 1 |
| chronic kidney disease | NR3C2 | down | FINERENONE | 3 | 6 | 0 | 2 |
| chronic kidney disease | AGTR1 | down | IRBESARTAN, LOSARTAN | 1 | 9 | 0 | 3 |
| chronic kidney disease | GHR | up | SOMATROPIN | 1 | 4 | 0 | 0 |
| hypothyroidism | THRA | up | LEVOTHYROXINE, LIOTHYRONINE | 0 | 2 | 0 | 0 |
| hypothyroidism | THRB | up | LEVOTHYROXINE, LIOTHYRONINE | 0 | 3 | 0 | 0 |
| hypothyroidism | TSHR | up | THYROTROPIN | 0 | 1 | 0 | 0 |
| depressive disorder | SLC6A4 | down | AMITRIPTYLINE, CITALOPRAM, CLOMIPRAMINE, DULOXETINE, ESCITALOPRAM, FLUOXETINE, FLUVOXAMINE, IMIPRAMINE, MILNACIPRAN, NORTRIPTYLINE, PAROXETINE, PROTRIPTYLINE, SERTRALINE, TRAZODONE, VENLAFAXINE, VORTIOXETINE | 0 | 4 | 0 | 3 |
| depressive disorder | SLC6A2 | down | AMITRIPTYLINE, BUPROPION, DESIPRAMINE, DOXEPIN, DULOXETINE, IMIPRAMINE, MILNACIPRAN, NORTRIPTYLINE, PROTRIPTYLINE, REBOXETINE, VENLAFAXINE | 0 | 9 | 0 | 2 |
| depressive disorder | GABRA1 | up | BREXANOLONE | 1 | 32 | 0 | 7 |
| depressive disorder | GABRB1 | up | BREXANOLONE | 1 | 31 | 0 | 7 |
| depressive disorder | GABRA6 | up | BREXANOLONE | 1 | 30 | 0 | 6 |
| depressive disorder | GABRA2 | up | BREXANOLONE | 1 | 31 | 0 | 6 |
| depressive disorder | GABRG3 | up | BREXANOLONE | 1 | 30 | 0 | 6 |
| depressive disorder | GABRB2 | up | BREXANOLONE | 1 | 30 | 0 | 6 |
| depressive disorder | GABRG2 | up | BREXANOLONE | 1 | 31 | 0 | 7 |
| depressive disorder | GABRA5 | up | BREXANOLONE | 1 | 30 | 0 | 6 |
| depressive disorder | SLC6A3 | down | BUPROPION | 0 | 7 | 0 | 2 |
| depressive disorder | HTR2A | down | CYCLOBENZAPRINE, MIRTAZAPINE, OLANZAPINE, TRAZODONE | 0 | 21 | 0 | 6 |
| depressive disorder | HTR2C | down | CYCLOBENZAPRINE, MIRTAZAPINE, OLANZAPINE, TRAZODONE | 0 | 7 | 0 | 4 |
| depressive disorder | ADRA2A | down | MIRTAZAPINE | 18 | 8 | 1 | 0 |
| depressive disorder | MAOA | down | MOCLOBEMIDE, PHENELZINE | 0 | 1 | 0 | 1 |
| depressive disorder | DRD2 | down | OLANZAPINE | 6 | 37 | 2 | 5 |
| depressive disorder | DRD3 | down | OLANZAPINE | 4 | 9 | 3 | 0 |
| depressive disorder | DRD4 | down | OLANZAPINE | 4 | 7 | 2 | 0 |
| depressive disorder | HTR1A | up | VORTIOXETINE | 1 | 1 | 0 | 0 |
| schizophrenia | DRD2 | down | AMISULPRIDE, ASENAPINE, BENPERIDOL, BLONANSERIN, BROMPERIDOL, CARPHENAZINE, CHLORPROMAZINE, CLOZAPINE, FLUPHENAZINE DECANOATE, FLUSPIRILENE, ILOPERIDONE, LOXAPINE, LUMATEPERONE, LURASIDONE, MESORIDAZINE, MOLINDONE, OLANZAPINE, PALIPERIDONE, PALIPERIDONE PALMITATE, PERPHENAZINE, PIMOZIDE, PIPERACETAZINE, PROCHLORPERAZINE, QUETIAPINE, RISPERIDONE, SULPIRIDE, THIOTHIXENE, TRIFLUOPERAZINE, TRIFLUPROMAZINE, ZIPRASIDONE | 7 | 10 | 1 | 3 |
| schizophrenia | DRD3 | down | AMISULPRIDE, BLONANSERIN, CHLORPROMAZINE, LOXAPINE, OLANZAPINE, PIMOZIDE, TRIFLUOPERAZINE | 5 | 1 | 2 | 1 |
| schizophrenia | HTR1A | down | AMISULPRIDE | 2 | 1 | 1 | 0 |
| schizophrenia | HTR2A | down | AMISULPRIDE, ARIPIPRAZOLE, ARIPIPRAZOLE LAUROXIL, ASENAPINE, BLONANSERIN, BREXPIPRAZOLE, CARPHENAZINE, CHLORPROMAZINE, CLOTHIAPINE, CLOZAPINE, HALOPERIDOL, HALOPERIDOL DECANOATE, ILOPERIDONE, LOXAPINE, LUMATEPERONE, LURASIDONE, MESORIDAZINE, MOLINDONE, OLANZAPINE, PALIPERIDONE, PALIPERIDONE PALMITATE, PIMOZIDE, QUETIAPINE, RISPERIDONE, THIOTHIXENE, TRIFLUOPERAZINE, ZIPRASIDONE | 0 | 5 | 0 | 0 |
| schizophrenia | HTR2C | down | AMISULPRIDE, CARPHENAZINE, CLOTHIAPINE, LOXAPINE, OLANZAPINE, QUETIAPINE, RISPERIDONE, TRIFLUOPERAZINE, ZIPRASIDONE | 0 | 7 | 0 | 0 |
| schizophrenia | HTR4 | down | AMISULPRIDE | 3 | 0 | 1 | 0 |
| schizophrenia | HTR1B | down | AMISULPRIDE | 8 | 0 | 0 | 0 |
| schizophrenia | HTR5A | down | AMISULPRIDE | 0 | 0 | 0 | 0 |
| schizophrenia | HTR6 | down | AMISULPRIDE | 0 | 0 | 0 | 0 |
| schizophrenia | HTR3A | down | AMISULPRIDE, CLOTHIAPINE | 0 | 8 | 0 | 3 |
| schizophrenia | HTR7 | down | AMISULPRIDE | 0 | 0 | 0 | 0 |
| schizophrenia | HTR3B | down | AMISULPRIDE, CLOTHIAPINE | 0 | 3 | 0 | 1 |
| schizophrenia | HTR3C | down | AMISULPRIDE, CLOTHIAPINE | 0 | 2 | 0 | 1 |
| schizophrenia | HTR3D | down | AMISULPRIDE, CLOTHIAPINE | 0 | 2 | 0 | 1 |
| schizophrenia | HTR3E | down | AMISULPRIDE, CLOTHIAPINE | 0 | 2 | 0 | 1 |
| schizophrenia | HTR2B | down | AMISULPRIDE, CLOTHIAPINE | 0 | 1 | 0 | 0 |
| schizophrenia | HTR1F | down | AMISULPRIDE | 3 | 0 | 0 | 0 |
| schizophrenia | HTR1D | down | AMISULPRIDE | 8 | 0 | 0 | 0 |
| schizophrenia | DRD4 | down | CHLORPROMAZINE, CLOTHIAPINE, LOXAPINE, OLANZAPINE, PIMOZIDE, TRIFLUOPERAZINE | 5 | 1 | 1 | 1 |
| bipolar disorder | DRD2 | down | ACETOPHENAZINE, ASENAPINE, ILOPERIDONE, LEVOMEPROMAZINE, LOXAPINE, LURASIDONE, OLANZAPINE, QUETIAPINE, RISPERIDONE, ZIPRASIDONE | 7 | 32 | 1 | 4 |
| bipolar disorder | HTR2A | down | ARIPIPRAZOLE, ASENAPINE, ILOPERIDONE, LOXAPINE, LURASIDONE, OLANZAPINE, QUETIAPINE, RISPERIDONE, ZIPRASIDONE | 0 | 18 | 0 | 6 |
| bipolar disorder | SCN2A | down | CARBAMAZEPINE, LAMOTRIGINE | 0 | 35 | 0 | 4 |
| bipolar disorder | SCN8A | down | CARBAMAZEPINE, LAMOTRIGINE | 0 | 35 | 0 | 4 |
| bipolar disorder | SCN9A | down | CARBAMAZEPINE, LAMOTRIGINE | 0 | 35 | 0 | 4 |
| bipolar disorder | SCN11A | down | CARBAMAZEPINE, LAMOTRIGINE | 0 | 35 | 0 | 4 |
| bipolar disorder | SCN1A | down | CARBAMAZEPINE, LAMOTRIGINE | 0 | 35 | 0 | 4 |
| bipolar disorder | SCN5A | down | CARBAMAZEPINE, LAMOTRIGINE | 0 | 39 | 0 | 4 |
| bipolar disorder | SCN3A | down | CARBAMAZEPINE, LAMOTRIGINE | 0 | 35 | 0 | 4 |
| bipolar disorder | SCN10A | down | CARBAMAZEPINE, LAMOTRIGINE | 0 | 36 | 0 | 4 |
| bipolar disorder | SCN4A | down | CARBAMAZEPINE, LAMOTRIGINE | 0 | 38 | 0 | 4 |
| bipolar disorder | SCN7A | down | CARBAMAZEPINE, LAMOTRIGINE | 0 | 35 | 0 | 4 |
| bipolar disorder | SLC6A2 | down | DOXEPIN | 0 | 23 | 0 | 3 |
| bipolar disorder | SLC6A4 | down | FLUOXETINE | 0 | 14 | 0 | 6 |
| bipolar disorder | DRD4 | down | LEVOMEPROMAZINE, LOXAPINE, OLANZAPINE | 5 | 6 | 1 | 0 |
| bipolar disorder | DRD3 | down | LEVOMEPROMAZINE, LOXAPINE, OLANZAPINE | 6 | 8 | 1 | 1 |
| bipolar disorder | GSK3B | down | LITHIUM CARBONATE, LITHIUM CITRATE ANHYDROUS | 0 | 0 | 0 | 0 |
| bipolar disorder | IMPA1 | down | LITHIUM CARBONATE, LITHIUM CITRATE ANHYDROUS | 0 | 0 | 0 | 0 |
| bipolar disorder | GSK3A | down | LITHIUM CARBONATE, LITHIUM CITRATE ANHYDROUS | 0 | 0 | 0 | 0 |
| bipolar disorder | HTR2C | down | LOXAPINE, OLANZAPINE, QUETIAPINE, RISPERIDONE, ZIPRASIDONE | 0 | 10 | 0 | 1 |
| bipolar disorder | ALDH5A1 | down | VALPROIC ACID | 0 | 0 | 0 | 0 |
| Parkinson disease | GRIN1 | down | AMANTADINE, ORPHENADRINE | 0 | 2 | 0 | 0 |
| Parkinson disease | GRIN2B | down | AMANTADINE, ORPHENADRINE | 0 | 2 | 0 | 0 |
| Parkinson disease | GRIN2A | down | AMANTADINE, ORPHENADRINE | 0 | 2 | 0 | 1 |
| Parkinson disease | DRD2 | up | APOMORPHINE, BROMOCRIPTINE, CABERGOLINE, PRAMIPEXOLE, ROPINIROLE, ROTIGOTINE | 45 | 2 | 2 | 0 |
| Parkinson disease | DRD3 | up | APOMORPHINE, BROMOCRIPTINE, LEVODOPA, PRAMIPEXOLE, ROPINIROLE, ROTIGOTINE | 12 | 1 | 0 | 0 |
| Parkinson disease | CHRM1 | down | ATROPINE, BENZTROPINE, BIPERIDEN, CYCRIMINE, ETHOPROPAZINE, METHIXENE, PROCYCLIDINE, TRIHEXYPHENIDYL | 2 | 16 | 1 | 0 |
| Parkinson disease | DDC | down | CARBIDOPA ANHYDROUS | 0 | 0 | 0 | 1 |
| Parkinson disease | COMT | down | ENTACAPONE, OPICAPONE | 0 | 0 | 0 | 0 |
| Parkinson disease | MAOB | down | RASAGILINE, SAFINAMIDE, SELEGILINE | 0 | 4 | 0 | 0 |
| Parkinson disease | ACHE | down | RIVASTIGMINE | 1 | 14 | 0 | 1 |
| Alzheimer disease | ACHE | down | DONEPEZIL, GALANTAMINE, HUPERZINE A, RIVASTIGMINE, TACRINE | 1 | 11 | 0 | 0 |
| Alzheimer disease | APP | down | LECANEMAB | 0 | 0 | 0 | 0 |
| Alzheimer disease | SLC6A3 | down | METHYLPHENIDATE | 0 | 7 | 0 | 2 |
| Alzheimer disease | BCHE | down | RIVASTIGMINE, TACRINE | 0 | 0 | 0 | 0 |
| glaucoma | CA2 | down | ACETAZOLAMIDE, BRINZOLAMIDE, DICHLORPHENAMIDE, DORZOLAMIDE, METHAZOLAMIDE | 0 | 4 | 0 | 0 |
| glaucoma | CA12 | down | ACETAZOLAMIDE, DICHLORPHENAMIDE | 0 | 2 | 0 | 0 |
| glaucoma | CA1 | down | ACETAZOLAMIDE, DICHLORPHENAMIDE, METHAZOLAMIDE | 0 | 4 | 0 | 0 |
| glaucoma | CA4 | down | ACETAZOLAMIDE, DICHLORPHENAMIDE, METHAZOLAMIDE | 0 | 3 | 0 | 0 |
| glaucoma | ADRA2A | up | APRACLONIDINE, BRIMONIDINE, CLONIDINE, DIPIVEFRIN, EPINEPHRINE | 9 | 14 | 0 | 0 |
| glaucoma | ADRA2B | up | APRACLONIDINE, BRIMONIDINE, CLONIDINE, DIPIVEFRIN, EPINEPHRINE | 9 | 14 | 0 | 0 |
| glaucoma | ADRA2C | up | APRACLONIDINE, BRIMONIDINE, CLONIDINE, DIPIVEFRIN, EPINEPHRINE | 9 | 14 | 0 | 0 |
| glaucoma | PTGFR | up | BIMATOPROST, LATANOPROST, LATANOPROSTENE BUNOD, TAFLUPROST, TRAVOPROST | 0 | 2 | 0 | 0 |
| glaucoma | ROCK2 | down | NETARSUDIL, RIPASUDIL | 0 | 2 | 0 | 0 |
| glaucoma | ROCK1 | down | NETARSUDIL, RIPASUDIL | 0 | 2 | 0 | 0 |
| endometriosis | PGR | up | DANAZOL, DROSPIRENONE, MEDROXYPROGESTERONE ACETATE, NORETHINDRONE, NORETHINDRONE ACETATE | 0 | 8 | 1 | 6 |
| endometriosis | AR | up | DANAZOL | 8 | 11 | 1 | 0 |
| endometriosis | NR3C2 | down | DROSPIRENONE | 3 | 8 | 0 | 0 |
| endometriosis | ESR1 | up | ETHINYL ESTRADIOL | 1 | 14 | 0 | 2 |
| malaria | MMP8 | down | DOXYCYCLINE ANHYDROUS | 0 | 0 | 0 | 0 |
| malaria | MMP1 | down | DOXYCYCLINE ANHYDROUS | 0 | 0 | 0 | 0 |
| malaria | MMP7 | down | DOXYCYCLINE ANHYDROUS | 0 | 0 | 0 | 0 |
| malaria | MMP13 | down | DOXYCYCLINE ANHYDROUS | 0 | 0 | 0 | 0 |
| malaria | TLR9 | down | HYDROXYCHLOROQUINE | 0 | 0 | 0 | 0 |
| malaria | TLR7 | down | HYDROXYCHLOROQUINE | 1 | 0 | 0 | 0 |
| malaria | SCN8A | down | QUINIDINE | 0 | 41 | 0 | 0 |
| malaria | SCN1A | down | QUINIDINE | 0 | 41 | 0 | 0 |
| malaria | SCN3A | down | QUINIDINE | 0 | 41 | 0 | 0 |
| breast cancer | CDK6 | down | ABEMACICLIB, PALBOCICLIB, RIBOCICLIB | 0 | 0 | 0 | 1 |
| breast cancer | CDK4 | down | ABEMACICLIB, PALBOCICLIB, RIBOCICLIB | 0 | 0 | 0 | 1 |
| breast cancer | PIK3CA | down | ALPELISIB | 0 | 0 | 0 | 2 |
| breast cancer | AKT1 | down | CAPIVASERTIB | 0 | 0 | 0 | 0 |
| breast cancer | ERBB2 | down | LAPATINIB, MARGETUXIMAB, NERATINIB, PERTUZUMAB, TRASTUZUMAB, TUCATINIB | 0 | 2 | 0 | 5 |
| breast cancer | EGFR | down | LAPATINIB, NERATINIB | 0 | 10 | 0 | 10 |
| breast cancer | ERBB4 | down | NERATINIB | 0 | 1 | 0 | 2 |
| breast cancer | CCND1 | down | PALBOCICLIB | 0 | 0 | 0 | 0 |
| prostate cancer | AR | down | ABIRATERONE, APALUTAMIDE, BICALUTAMIDE, DAROLUTAMIDE, ENZALUTAMIDE, FLUTAMIDE, NILUTAMIDE | 8 | 1 | 4 | 1 |
| prostate cancer | CYP17A1 | down | ABIRATERONE, ABIRATERONE ACETATE | 0 | 1 | 0 | 0 |
| prostate cancer | TUBA1C | down | CABAZITAXEL | 0 | 6 | 0 | 10 |
| colorectal cancer | EGFR | down | CETUXIMAB, NECITUMUMAB, PANITUMUMAB | 0 | 8 | 0 | 11 |
| colorectal cancer | FLT4 | down | FRUQUINTINIB, NINTEDANIB, REGORAFENIB | 0 | 0 | 0 | 10 |
| colorectal cancer | KDR | down | FRUQUINTINIB, NINTEDANIB, REGORAFENIB | 0 | 0 | 0 | 14 |
| colorectal cancer | FGFR2 | down | NINTEDANIB, REGORAFENIB | 2 | 3 | 0 | 2 |
| colorectal cancer | FGFR3 | down | NINTEDANIB | 0 | 3 | 0 | 4 |
| colorectal cancer | BRAF | down | REGORAFENIB | 0 | 1 | 0 | 4 |
| lung cancer | ALK | down | ALECTINIB | 0 | 2 | 0 | 4 |
| lung cancer | RET | down | ALECTINIB | 0 | 5 | 0 | 3 |
| lung cancer | EML4 | down | ALECTINIB | 0 | 0 | 0 | 3 |
| lung cancer | EGFR | down | OLMUTINIB | 0 | 6 | 0 | 14 |
| melanoma | MAP2K1 | down | BINIMETINIB, COBIMETINIB, TRAMETINIB | 0 | 0 | 0 | 2 |
| melanoma | MAP2K2 | down | BINIMETINIB, COBIMETINIB, TRAMETINIB | 0 | 0 | 0 | 2 |
| melanoma | BRAF | down | DABRAFENIB, ENCORAFENIB, VEMURAFENIB | 0 | 0 | 0 | 3 |
| melanoma | CTLA4 | down | IPILIMUMAB | 0 | 0 | 0 | 1 |
| chronic myeloid leukemia | ABL1 | down | ASCIMINIB, BOSUTINIB, DASATINIB ANHYDROUS, IMATINIB, NILOTINIB, PONATINIB | 0 | 1 | 0 | 1 |
| chronic myeloid leukemia | BCR | down | ASCIMINIB, BOSUTINIB, DASATINIB ANHYDROUS, IMATINIB, NILOTINIB, PONATINIB | 0 | 0 | 0 | 0 |
| chronic myeloid leukemia | LYN | down | BOSUTINIB, DASATINIB ANHYDROUS | 0 | 0 | 0 | 0 |
| chronic myeloid leukemia | SRC | down | BOSUTINIB, DASATINIB ANHYDROUS | 0 | 2 | 0 | 0 |
| chronic myeloid leukemia | HCK | down | BOSUTINIB, DASATINIB ANHYDROUS | 0 | 0 | 0 | 0 |
| chronic myeloid leukemia | KIT | down | DASATINIB ANHYDROUS, IMATINIB | 0 | 10 | 0 | 2 |
| chronic myeloid leukemia | PDGFRB | down | DASATINIB ANHYDROUS, IMATINIB | 1 | 8 | 0 | 2 |
| chronic myeloid leukemia | FYN | down | DASATINIB ANHYDROUS | 0 | 0 | 0 | 0 |
| chronic myeloid leukemia | BLK | down | DASATINIB ANHYDROUS | 0 | 0 | 0 | 0 |
| chronic myeloid leukemia | FGR | down | DASATINIB ANHYDROUS | 0 | 0 | 0 | 0 |
| chronic myeloid leukemia | YES1 | down | DASATINIB ANHYDROUS | 0 | 0 | 0 | 0 |
| chronic myeloid leukemia | EPHA2 | down | DASATINIB ANHYDROUS | 0 | 2 | 0 | 0 |
| chronic myeloid leukemia | LCK | down | DASATINIB ANHYDROUS | 0 | 1 | 0 | 0 |
| chronic myeloid leukemia | FRK | down | DASATINIB ANHYDROUS | 0 | 1 | 0 | 0 |
| chronic myeloid leukemia | SRMS | down | DASATINIB ANHYDROUS | 0 | 0 | 0 | 0 |
| chronic myeloid leukemia | RRM2 | down | HYDROXYUREA | 0 | 2 | 0 | 3 |
| chronic myeloid leukemia | RRM1 | down | HYDROXYUREA | 0 | 2 | 0 | 3 |
| chronic myeloid leukemia | RRM2B | down | HYDROXYUREA | 0 | 2 | 0 | 3 |
| chronic myeloid leukemia | IFNAR2 | up | INTERFERON ALFA-2B | 0 | 6 | 0 | 4 |
| chronic myeloid leukemia | IFNAR1 | up | INTERFERON ALFA-2B | 1 | 6 | 0 | 4 |
| acute myeloid leukemia | DNMT3A | down | AZACITIDINE | 0 | 0 | 0 | 1 |
| acute myeloid leukemia | IDH2 | down | ENASIDENIB | 0 | 1 | 0 | 0 |
| acute myeloid leukemia | FLT3 | down | GILTERITINIB, MIDOSTAURIN, QUIZARTINIB | 0 | 1 | 0 | 5 |
| acute myeloid leukemia | IDH1 | down | IVOSIDENIB, OLUTASIDENIB | 0 | 1 | 0 | 0 |
| acute myeloid leukemia | KIT | down | MIDOSTAURIN, QUIZARTINIB | 0 | 4 | 0 | 9 |
| acute myeloid leukemia | PDGFRB | down | MIDOSTAURIN, QUIZARTINIB | 1 | 3 | 0 | 8 |
| acute myeloid leukemia | PDGFRA | down | MIDOSTAURIN, QUIZARTINIB | 1 | 3 | 0 | 6 |
| cystic fibrosis | CFTR | up | ELEXACAFTOR, IVACAFTOR, TEZACAFTOR, VANZACAFTOR | 1 | 0 | 0 | 0 |
| cystic fibrosis | IFNGR1 | up | INTERFERON GAMMA-1B | 0 | 0 | 0 | 0 |
| cystic fibrosis | IFNGR2 | up | INTERFERON GAMMA-1B | 0 | 0 | 0 | 0 |
| Duchenne muscular dystrophy | DMD | up | CASIMERSEN, ETEPLIRSEN, GOLODIRSEN, VILTOLARSEN | 0 | 0 | 0 | 0 |
| Duchenne muscular dystrophy | NR3C1 | up | DEFLAZACORT, VAMOROLONE | 2 | 52 | 0 | 2 |
| Duchenne muscular dystrophy | HDAC4 | down | GIVINOSTAT | 0 | 4 | 0 | 0 |
| Duchenne muscular dystrophy | HDAC9 | down | GIVINOSTAT | 0 | 4 | 0 | 0 |
| Duchenne muscular dystrophy | HDAC2 | down | GIVINOSTAT | 0 | 5 | 0 | 0 |
| Duchenne muscular dystrophy | HDAC11 | down | GIVINOSTAT | 0 | 4 | 0 | 0 |
| Duchenne muscular dystrophy | HDAC8 | down | GIVINOSTAT | 0 | 4 | 0 | 0 |
| Duchenne muscular dystrophy | HDAC6 | down | GIVINOSTAT | 0 | 5 | 0 | 0 |
| Duchenne muscular dystrophy | HDAC5 | down | GIVINOSTAT | 0 | 4 | 0 | 0 |
| Duchenne muscular dystrophy | HDAC3 | down | GIVINOSTAT | 0 | 5 | 0 | 0 |
| Duchenne muscular dystrophy | HDAC1 | down | GIVINOSTAT | 0 | 5 | 0 | 0 |
| Duchenne muscular dystrophy | HDAC10 | down | GIVINOSTAT | 0 | 4 | 0 | 0 |
| Duchenne muscular dystrophy | HDAC7 | down | GIVINOSTAT | 0 | 4 | 0 | 0 |
| Duchenne muscular dystrophy | NR3C2 | down | VAMOROLONE | 3 | 6 | 0 | 2 |
| spinal muscular atrophy | SMN2 | up | NUSINERSEN, RISDIPLAM | 0 | 0 | 0 | 0 |
| Huntington disease | SLC6A2 | down | ATOMOXETINE, METHYLPHENIDATE | 0 | 27 | 0 | 0 |
| Huntington disease | ADRA2B | up | GUANFACINE | 9 | 19 | 0 | 0 |
| Huntington disease | ADRA2A | up | GUANFACINE | 9 | 19 | 0 | 0 |
| Huntington disease | ADRA2C | up | GUANFACINE | 9 | 19 | 0 | 0 |
| Huntington disease | SLC18A2 | down | LISDEXAMFETAMINE, TETRABENAZINE | 0 | 4 | 0 | 0 |
| Huntington disease | SLC6A3 | down | METHYLPHENIDATE | 0 | 9 | 0 | 0 |
| Gaucher disease | UGCG | down | ELIGLUSTAT, MIGLUSTAT | 0 | 0 | 0 | 0 |
| phenylketonuria | PAH | up | SAPROPTERIN | 0 | 0 | 0 | 0 |
| hemophilia A | TFPI | down | CONCIZUMAB, MARSTACIMAB | 0 | 1 | 0 | 0 |
| hemophilia A | PLG | down | TRANEXAMIC ACID | 4 | 0 | 0 | 0 |
| hemophilia B | TFPI | down | CONCIZUMAB, MARSTACIMAB | 0 | 1 | 0 | 0 |
| myasthenia gravis | KCND3 | down | AMIFAMPRIDINE, GUANIDINE | 0 | 3 | 0 | 0 |
| myasthenia gravis | KCNH5 | down | AMIFAMPRIDINE, GUANIDINE | 0 | 2 | 0 | 0 |
| myasthenia gravis | KCNS3 | down | AMIFAMPRIDINE, GUANIDINE | 0 | 2 | 0 | 0 |
| myasthenia gravis | KCNV2 | down | AMIFAMPRIDINE, GUANIDINE | 0 | 2 | 0 | 0 |
| myasthenia gravis | KCNA4 | down | AMIFAMPRIDINE, GUANIDINE | 0 | 2 | 0 | 0 |
| myasthenia gravis | KCNA1 | down | AMIFAMPRIDINE, GUANIDINE | 0 | 2 | 0 | 0 |
| myasthenia gravis | KCNA3 | down | AMIFAMPRIDINE, GUANIDINE | 0 | 2 | 0 | 0 |
| myasthenia gravis | KCNA10 | down | AMIFAMPRIDINE, GUANIDINE | 0 | 2 | 0 | 0 |
| myasthenia gravis | KCNA5 | down | AMIFAMPRIDINE, GUANIDINE | 0 | 3 | 0 | 0 |
| myasthenia gravis | KCNC2 | down | AMIFAMPRIDINE, GUANIDINE | 0 | 2 | 0 | 0 |
| myasthenia gravis | KCNC3 | down | AMIFAMPRIDINE, GUANIDINE | 0 | 2 | 0 | 0 |
| myasthenia gravis | KCNC4 | down | AMIFAMPRIDINE, GUANIDINE | 0 | 2 | 0 | 0 |
| myasthenia gravis | KCND1 | down | AMIFAMPRIDINE, GUANIDINE | 0 | 2 | 0 | 0 |
| myasthenia gravis | KCND2 | down | AMIFAMPRIDINE, GUANIDINE | 0 | 2 | 0 | 0 |
| myasthenia gravis | KCNG2 | down | AMIFAMPRIDINE, GUANIDINE | 0 | 2 | 0 | 0 |
| myasthenia gravis | KCNG3 | down | AMIFAMPRIDINE, GUANIDINE | 0 | 2 | 0 | 0 |
| myasthenia gravis | KCNH3 | down | AMIFAMPRIDINE, GUANIDINE | 0 | 2 | 0 | 0 |
| myasthenia gravis | KCNH4 | down | AMIFAMPRIDINE, GUANIDINE | 0 | 2 | 0 | 0 |
| myasthenia gravis | KCNH6 | down | AMIFAMPRIDINE, GUANIDINE | 0 | 2 | 0 | 0 |
| myasthenia gravis | KCNH7 | down | AMIFAMPRIDINE, GUANIDINE | 0 | 2 | 0 | 0 |
| myasthenia gravis | KCNH8 | down | AMIFAMPRIDINE, GUANIDINE | 0 | 2 | 0 | 0 |
| myasthenia gravis | KCNQ4 | down | AMIFAMPRIDINE, GUANIDINE | 1 | 2 | 0 | 0 |
| myasthenia gravis | FCGRT | down | EFGARTIGIMOD ALFA, NIPOCALIMAB, ROZANOLIXIZUMAB | 0 | 0 | 0 | 0 |
| myasthenia gravis | C5 | down | ZILUCOPLAN | 0 | 3 | 0 | 3 |
| narcolepsy | SLC18A2 | down | DEXTROAMPHETAMINE | 0 | 6 | 0 | 0 |
| narcolepsy | SLC6A3 | down | MODAFINIL | 0 | 6 | 0 | 2 |
| narcolepsy | GABBR1 | up | OXYBATE | 0 | 1 | 0 | 0 |
| narcolepsy | GABBR2 | up | OXYBATE | 0 | 1 | 0 | 0 |
| hereditary angioedema | KLKB1 | down | BEROTRALSTAT, ECALLANTIDE, HUMAN C1-ESTERASE INHIBITOR, LANADELUMAB | 0 | 0 | 0 | 0 |
| hereditary angioedema | F12 | down | HUMAN C1-ESTERASE INHIBITOR | 0 | 0 | 0 | 0 |
| hereditary angioedema | C1S | down | HUMAN C1-ESTERASE INHIBITOR | 0 | 1 | 0 | 0 |
| hereditary angioedema | F11 | down | HUMAN C1-ESTERASE INHIBITOR | 0 | 0 | 0 | 0 |
| hereditary angioedema | BDKRB2 | down | ICATIBANT | 0 | 0 | 0 | 0 |
| hereditary angioedema | AR | up | STANOZOLOL | 9 | 11 | 0 | 0 |
| acromegaly | DRD2 | up | BROMOCRIPTINE | 47 | 6 | 0 | 1 |
| acromegaly | DRD3 | up | BROMOCRIPTINE | 12 | 6 | 0 | 0 |
| acromegaly | DRD4 | up | BROMOCRIPTINE | 9 | 5 | 0 | 0 |
| acromegaly | SSTR5 | up | LANREOTIDE, OCTREOTIDE, PASIREOTIDE | 0 | 0 | 0 | 0 |
| acromegaly | SSTR2 | up | LANREOTIDE, OCTREOTIDE, PALTUSOTINE, PASIREOTIDE | 0 | 0 | 0 | 0 |
| acromegaly | SSTR1 | up | OCTREOTIDE, PASIREOTIDE | 0 | 0 | 0 | 0 |
| acromegaly | SSTR3 | up | OCTREOTIDE, PASIREOTIDE | 0 | 0 | 0 | 0 |
| acromegaly | SSTR4 | up | OCTREOTIDE | 0 | 0 | 0 | 0 |
| acromegaly | GHR | down | PEGVISOMANT | 4 | 0 | 0 | 0 |
| Cushing syndrome | CYP11B1 | down | LEVOKETOCONAZOLE, OSILODROSTAT | 0 | 1 | 0 | 1 |
| Cushing syndrome | CYP11A1 | down | LEVOKETOCONAZOLE | 0 | 2 | 0 | 0 |
| Cushing syndrome | CYP11B2 | down | LEVOKETOCONAZOLE | 0 | 0 | 0 | 0 |
| Cushing syndrome | CYP17A1 | down | LEVOKETOCONAZOLE | 0 | 1 | 0 | 1 |
| Cushing syndrome | NR3C1 | down | MIFEPRISTONE | 52 | 1 | 0 | 0 |
| Cushing syndrome | PGR | down | MIFEPRISTONE | 20 | 0 | 0 | 0 |
| sarcoidosis | NR3C1 | up | DEXAMETHASONE, DEXAMETHASONE PHOSPHORIC ACID, PREDNISOLONE, PREDNISONE | 2 | 44 | 0 | 8 |
| systemic sclerosis | EDNRA | down | BOSENTAN | 0 | 4 | 0 | 1 |
| systemic sclerosis | EDNRB | down | BOSENTAN | 0 | 1 | 0 | 1 |
| systemic sclerosis | PDGFRB | down | NINTEDANIB | 1 | 11 | 0 | 1 |
| systemic sclerosis | PDGFRA | down | NINTEDANIB | 1 | 10 | 0 | 0 |
| systemic sclerosis | KDR | down | NINTEDANIB | 0 | 16 | 0 | 0 |
| systemic sclerosis | FGFR2 | down | NINTEDANIB | 2 | 6 | 0 | 0 |
| systemic sclerosis | FLT4 | down | NINTEDANIB | 0 | 12 | 0 | 0 |
| systemic sclerosis | FLT1 | down | NINTEDANIB | 0 | 11 | 0 | 0 |
| systemic sclerosis | FGFR3 | down | NINTEDANIB | 0 | 7 | 0 | 0 |
| systemic sclerosis | FGFR1 | down | NINTEDANIB | 0 | 8 | 0 | 0 |
| systemic sclerosis | FGFR4 | down | NINTEDANIB | 0 | 3 | 0 | 0 |
| systemic sclerosis | CRBN | down | POMALIDOMIDE | 0 | 1 | 0 | 0 |
| systemic sclerosis | CUL4A | down | POMALIDOMIDE | 0 | 1 | 0 | 0 |
| systemic sclerosis | DDB1 | down | POMALIDOMIDE | 0 | 1 | 0 | 0 |
| systemic sclerosis | RBX1 | down | POMALIDOMIDE | 0 | 1 | 0 | 0 |
| systemic sclerosis | IL6R | down | TOCILIZUMAB | 0 | 3 | 0 | 0 |
| Behcet disease | PDE4A | down | APREMILAST | 0 | 10 | 0 | 1 |
| Behcet disease | PDE4B | down | APREMILAST | 0 | 10 | 0 | 1 |
| Behcet disease | PDE4C | down | APREMILAST | 0 | 10 | 0 | 1 |
| Behcet disease | PDE4D | down | APREMILAST | 0 | 10 | 0 | 1 |
| Behcet disease | KCNQ3 | up | EZOGABINE | 4 | 0 | 0 | 0 |
| Behcet disease | KCNQ2 | up | EZOGABINE | 4 | 0 | 0 | 0 |
| Behcet disease | KCNQ1 | up | EZOGABINE | 4 | 0 | 0 | 0 |
| Behcet disease | KCNQ4 | up | EZOGABINE | 4 | 0 | 0 | 0 |
| Behcet disease | KCNQ5 | up | EZOGABINE | 4 | 0 | 0 | 0 |
| hidradenitis suppurativa | TNF | down | ADALIMUMAB | 0 | 4 | 0 | 2 |

### B8. Every opposite card. The main result

**573 opposite cards** (card-and-protein pairs), on 106 one-way proteins. They are grouped by disease and protein so the Approved medicines are written once per group, not once per row. Every Approved medicine on the protein is named, with its direction and action words, and every opposite card is listed. Nothing was left out. The same list, one full row per card, is in `opposite_cards.csv`. **No row is labelled a problem or not a problem.**

**asthma / ADORA1.** Approved medicines turn it **down**: THEOPHYLLINE ANHYDROUS (ANTAGONIST).

| # | tab | card medicine | card direction | card action words |
|---|---|---|---|---|
| 1 | New clues | DEFIBROTIDE | up | AGONIST |
| 2 | New clues | ADENOSINE | up | AGONIST |

**asthma / ADORA2A.** Approved medicines turn it **down**: THEOPHYLLINE ANHYDROUS (ANTAGONIST).

| # | tab | card medicine | card direction | card action words |
|---|---|---|---|---|
| 3 | New clues | DEFIBROTIDE | up | AGONIST |
| 4 | New clues | ADENOSINE | up | AGONIST |
| 5 | New clues | REGADENOSON ANHYDROUS | up | AGONIST |

**asthma / ADORA2B.** Approved medicines turn it **down**: THEOPHYLLINE ANHYDROUS (ANTAGONIST).

| # | tab | card medicine | card direction | card action words |
|---|---|---|---|---|
| 6 | New clues | DEFIBROTIDE | up | AGONIST |
| 7 | New clues | ADENOSINE | up | AGONIST |

**asthma / ADRA2A.** Approved medicines turn it **up**: EPINEPHRINE (AGONIST).

| # | tab | card medicine | card direction | card action words |
|---|---|---|---|---|
| 8 | New clues | CELIPROLOL | down | ANTAGONIST |
| 9 | New clues | LABETALOL | down | ANTAGONIST |
| 10 | New clues | MIRTAZAPINE | down | ANTAGONIST |
| 11 | New clues | PHENTOLAMINE | down | ANTAGONIST |
| 12 | New clues | PHENOXYBENZAMINE | down | ANTAGONIST |
| 13 | New clues | RAUWOLFIA SERPENTINA | down | ANTAGONIST |
| 14 | New clues | ERGOLOID | down | ANTAGONIST |
| 15 | New clues | TOLAZOLINE | down | ANTAGONIST |
| 16 | New clues | ALSEROXYLON | down | ANTAGONIST |

**asthma / CHRM2.** Approved medicines turn it **down**: GLYCOPYRRONIUM (INHIBITOR).

| # | tab | card medicine | card direction | card action words |
|---|---|---|---|---|
| 17 | New clues | BETHANECHOL | up | AGONIST |
| 18 | New clues | ALCURONIUM | up | POSITIVE ALLOSTERIC MODULATOR |

**asthma / ADORA3.** Approved medicines turn it **down**: THEOPHYLLINE ANHYDROUS (ANTAGONIST).

| # | tab | card medicine | card direction | card action words |
|---|---|---|---|---|
| 19 | New clues | ADENOSINE | up | AGONIST |

**asthma / NR3C1.** Approved medicines turn it **up**: BECLOMETHASONE DIPROPIONATE (AGONIST); BETAMETHASONE ACETATE (AGONIST); BUDESONIDE (AGONIST); CICLESONIDE (AGONIST); CORTISONE ACETATE (AGONIST); DEXAMETHASONE (AGONIST); DEXAMETHASONE PHOSPHORIC ACID (AGONIST); FLUNISOLIDE (AGONIST); FLUPREDNISOLONE (AGONIST); FLUTICASONE FUROATE (AGONIST); FLUTICASONE PROPIONATE (AGONIST); HYDROCORTISONE (AGONIST); HYDROCORTISONE HEMISUCCINATE ANHYDROUS (AGONIST); METHYLPREDNISOLONE (AGONIST); METHYLPREDNISOLONE ACETATE (AGONIST); METHYLPREDNISOLONE HEMISUCCINATE (AGONIST); MOMETASONE FUROATE (AGONIST); PREDNISOLONE (AGONIST); PREDNISOLONE PHOSPHORIC ACID (AGONIST); PREDNISONE (AGONIST); TRIAMCINOLONE ACETONIDE (AGONIST).

| # | tab | card medicine | card direction | card action words |
|---|---|---|---|---|
| 20 | New clues | MIFEPRISTONE | down | ANTAGONIST |
| 21 | New clues | CYPROTERONE ACETATE | down | ANTAGONIST |

**asthma / ADRB2.** Approved medicines turn it **up**: ALBUTEROL (AGONIST); BAMBUTEROL (AGONIST); BITOLTEROL (AGONIST); EPINEPHRINE (AGONIST); FORMOTEROL (AGONIST); INDACATEROL (AGONIST); ISOETHARINE (AGONIST); LEVOSALBUTAMOL (AGONIST); PIRBUTEROL (AGONIST); PROCATEROL (AGONIST); PROTOKYLOL (AGONIST); RIMITEROL (AGONIST); SALMETEROL (AGONIST); TERBUTALINE (AGONIST); VILANTEROL (AGONIST).

| # | tab | card medicine | card direction | card action words |
|---|---|---|---|---|
| 22 | New clues | TIMOLOL | down | ANTAGONIST |
| 23 | New clues | CARVEDILOL | down | ANTAGONIST |
| 24 | New clues | LABETALOL | down | ANTAGONIST |
| 25 | New clues | NEBIVOLOL | down | ANTAGONIST |
| 26 | New clues | SOTALOL | down | ANTAGONIST |
| 27 | New clues | PROPAFENONE | down | ANTAGONIST |
| 28 | New clues | CARTEOLOL | down | ANTAGONIST |
| 29 | New clues | LEVOBUNOLOL | down | ANTAGONIST |
| 30 | New clues | BUCINDOLOL | down | ANTAGONIST |
| 31 | New clues | OXPRENOLOL | down | ANTAGONIST |
| 32 | New clues | PENBUTOLOL | down | ANTAGONIST |
| 33 | In trials | PROPRANOLOL | down | ANTAGONIST |
| 34 | In trials | NADOLOL | down | ANTAGONIST |

**type 2 diabetes mellitus / KCNJ11.** Approved medicines turn it **down**: CHLORPROPAMIDE (BLOCKER); GLIMEPIRIDE (BLOCKER); GLIPIZIDE (BLOCKER); GLYBURIDE (BLOCKER); MITIGLINIDE CALCIUM DIHYDRATE (BLOCKER); NATEGLINIDE (BLOCKER); REPAGLINIDE (BLOCKER); TOLAZAMIDE (BLOCKER); TOLBUTAMIDE (BLOCKER).

| # | tab | card medicine | card direction | card action words |
|---|---|---|---|---|
| 35 | New clues | MINOXIDIL | up | OPENER |
| 36 | New clues | PINACIDIL ANHYDROUS | up | OPENER |
| 37 | In trials | DIAZOXIDE | up | OPENER |

**type 2 diabetes mellitus / GLP1R.** Approved medicines turn it **up**: ALBIGLUTIDE (AGONIST); DULAGLUTIDE (AGONIST); EXENATIDE (AGONIST); LIRAGLUTIDE (AGONIST); LIXISENATIDE (AGONIST); SEMAGLUTIDE (AGONIST); TIRZEPATIDE (AGONIST).

| # | tab | card medicine | card direction | card action words |
|---|---|---|---|---|
| 38 | In trials | AVEXITIDE | down | ANTAGONIST |

**epilepsy / GABRG2.** Approved medicines turn it **up**: CENOBAMATE (POSITIVE ALLOSTERIC MODULATOR); CLOBAZAM (POSITIVE ALLOSTERIC MODULATOR); CLONAZEPAM (POSITIVE ALLOSTERIC MODULATOR); DIAZEPAM (POSITIVE ALLOSTERIC MODULATOR); GANAXOLONE (POSITIVE ALLOSTERIC MODULATOR); METHARBITAL (POSITIVE ALLOSTERIC MODULATOR); MIDAZOLAM (POSITIVE ALLOSTERIC MODULATOR); PRIMIDONE (POSITIVE ALLOSTERIC MODULATOR); TOPIRAMATE (POSITIVE MODULATOR).

| # | tab | card medicine | card direction | card action words |
|---|---|---|---|---|
| 39 | New clues | ETIFOXINE | down | ANTAGONIST |

**epilepsy / GABRA1.** Approved medicines turn it **up**: CENOBAMATE (POSITIVE ALLOSTERIC MODULATOR); CLOBAZAM (POSITIVE ALLOSTERIC MODULATOR); CLONAZEPAM (POSITIVE ALLOSTERIC MODULATOR); DIAZEPAM (POSITIVE ALLOSTERIC MODULATOR); GANAXOLONE (POSITIVE ALLOSTERIC MODULATOR); METHARBITAL (POSITIVE ALLOSTERIC MODULATOR); MIDAZOLAM (POSITIVE ALLOSTERIC MODULATOR); PRIMIDONE (POSITIVE ALLOSTERIC MODULATOR); TOPIRAMATE (POSITIVE MODULATOR).

| # | tab | card medicine | card direction | card action words |
|---|---|---|---|---|
| 40 | New clues | ETIFOXINE | down | ANTAGONIST |

**epilepsy / GABRB3.** Approved medicines turn it **up**: CENOBAMATE (POSITIVE ALLOSTERIC MODULATOR); CLOBAZAM (POSITIVE ALLOSTERIC MODULATOR); CLONAZEPAM (POSITIVE ALLOSTERIC MODULATOR); DIAZEPAM (POSITIVE ALLOSTERIC MODULATOR); GANAXOLONE (POSITIVE ALLOSTERIC MODULATOR); METHARBITAL (POSITIVE ALLOSTERIC MODULATOR); MIDAZOLAM (POSITIVE ALLOSTERIC MODULATOR); PRIMIDONE (POSITIVE ALLOSTERIC MODULATOR); TOPIRAMATE (POSITIVE MODULATOR).

| # | tab | card medicine | card direction | card action words |
|---|---|---|---|---|
| 41 | New clues | ETIFOXINE | down | ANTAGONIST |

**epilepsy / GABRB2.** Approved medicines turn it **up**: CENOBAMATE (POSITIVE ALLOSTERIC MODULATOR); CLOBAZAM (POSITIVE ALLOSTERIC MODULATOR); CLONAZEPAM (POSITIVE ALLOSTERIC MODULATOR); DIAZEPAM (POSITIVE ALLOSTERIC MODULATOR); GANAXOLONE (POSITIVE ALLOSTERIC MODULATOR); METHARBITAL (POSITIVE ALLOSTERIC MODULATOR); MIDAZOLAM (POSITIVE ALLOSTERIC MODULATOR); PRIMIDONE (POSITIVE ALLOSTERIC MODULATOR); TOPIRAMATE (POSITIVE MODULATOR).

| # | tab | card medicine | card direction | card action words |
|---|---|---|---|---|
| 42 | New clues | ETIFOXINE | down | ANTAGONIST |

**epilepsy / KCNQ2.** Approved medicines turn it **up**: EZOGABINE (OPENER).

| # | tab | card medicine | card direction | card action words |
|---|---|---|---|---|
| 43 | New clues | DALFAMPRIDINE | down | BLOCKER |
| 44 | New clues | AMIFAMPRIDINE | down | BLOCKER |
| 45 | New clues | GUANIDINE | down | BLOCKER |
| 46 | New clues | TEDISAMIL | down | BLOCKER |

**rheumatoid arthritis / NR3C1.** Approved medicines turn it **up**: CORTISONE ACETATE (AGONIST); DEXAMETHASONE (AGONIST); DEXAMETHASONE PHOSPHORIC ACID (AGONIST); HYDROCORTISONE (AGONIST); METHYLPREDNISOLONE (AGONIST); METHYLPREDNISOLONE ACETATE (AGONIST); METHYLPREDNISOLONE HEMISUCCINATE (AGONIST); PREDNISOLONE (AGONIST); PREDNISONE (AGONIST); TRIAMCINOLONE ACETONIDE (AGONIST).

| # | tab | card medicine | card direction | card action words |
|---|---|---|---|---|
| 47 | New clues | MIFEPRISTONE | down | ANTAGONIST |
| 48 | New clues | CYPROTERONE ACETATE | down | ANTAGONIST |

**rheumatoid arthritis / TLR7.** Approved medicines turn it **down**: HYDROXYCHLOROQUINE (ANTAGONIST).

| # | tab | card medicine | card direction | card action words |
|---|---|---|---|---|
| 49 | New clues | IMIQUIMOD | up | AGONIST |

**psoriasis / NR3C1.** Approved medicines turn it **up**: BETAMETHASONE DIPROPIONATE (AGONIST); CLOBETASOL PROPIONATE (AGONIST); DESOXIMETASONE (AGONIST); DEXAMETHASONE (AGONIST); DEXAMETHASONE PHOSPHORIC ACID (AGONIST); FLUOCINOLONE ACETONIDE (AGONIST); HYDROCORTISONE (AGONIST); PREDNISOLONE (AGONIST); PREDNISONE (AGONIST).

| # | tab | card medicine | card direction | card action words |
|---|---|---|---|---|
| 50 | New clues | MIFEPRISTONE | down | ANTAGONIST |
| 51 | New clues | CYPROTERONE ACETATE | down | ANTAGONIST |

**atopic eczema / NR3C1.** Approved medicines turn it **up**: CORTISONE ACETATE (AGONIST); DESONIDE (AGONIST); DEXAMETHASONE (AGONIST); DEXAMETHASONE PHOSPHORIC ACID (AGONIST); FLUOCINOLONE ACETONIDE (AGONIST); FLUTICASONE PROPIONATE (AGONIST); HYDROCORTISONE (AGONIST); HYDROCORTISONE BUTYRATE (AGONIST); METHYLPREDNISOLONE (AGONIST); PREDNISOLONE (AGONIST); PREDNISONE (AGONIST).

| # | tab | card medicine | card direction | card action words |
|---|---|---|---|---|
| 52 | New clues | MIFEPRISTONE | down | ANTAGONIST |
| 53 | New clues | CYPROTERONE ACETATE | down | ANTAGONIST |

**atopic eczema / HRH1.** Approved medicines turn it **down**: DESLORATADINE (ANTAGONIST); DOXEPIN (ANTAGONIST); EPINASTINE (ANTAGONIST); FEXOFENADINE (ANTAGONIST); LEVOCETIRIZINE (ANTAGONIST); OLOPATADINE (ANTAGONIST); PROMETHAZINE (ANTAGONIST).

| # | tab | card medicine | card direction | card action words |
|---|---|---|---|---|
| 54 | New clues | BETAHISTINE | up | AGONIST |
| 55 | New clues | HISTAMINE | up | AGONIST |
| 56 | New clues | TOLAZOLINE | up | AGONIST |

**ulcerative colitis / NR3C1.** Approved medicines turn it **up**: BETAMETHASONE ACETATE (AGONIST); BETAMETHASONE PHOSPHORIC ACID (AGONIST); BUDESONIDE (AGONIST); DEXAMETHASONE (AGONIST); DEXAMETHASONE PHOSPHORIC ACID (AGONIST); HYDROCORTISONE (AGONIST); METHYLPREDNISOLONE (AGONIST); PREDNISOLONE (AGONIST); PREDNISONE (AGONIST).

| # | tab | card medicine | card direction | card action words |
|---|---|---|---|---|
| 57 | New clues | MIFEPRISTONE | down | ANTAGONIST |
| 58 | New clues | CYPROTERONE ACETATE | down | ANTAGONIST |

**osteoporosis / ESR1.** Approved medicines turn it **up**: ESTRADIOL (AGONIST); ESTROGENS, CONJUGATED (AGONIST); ESTROGENS, CONJUGATED SYNTHETIC A (AGONIST); ESTRONE SULFURIC ACID (AGONIST).

| # | tab | card medicine | card direction | card action words |
|---|---|---|---|---|
| 59 | New clues | FULVESTRANT | down | ANTAGONIST, DEGRADER |

**osteoporosis / AR.** Approved medicines turn it **up**: TESTOSTERONE (AGONIST).

| # | tab | card medicine | card direction | card action words |
|---|---|---|---|---|
| 60 | New clues | ENZALUTAMIDE | down | ANTAGONIST |
| 61 | New clues | BICALUTAMIDE | down | ANTAGONIST |
| 62 | New clues | APALUTAMIDE | down | ANTAGONIST |
| 63 | New clues | DAROLUTAMIDE | down | ANTAGONIST |
| 64 | New clues | ABIRATERONE | down | ANTAGONIST |
| 65 | New clues | FLUTAMIDE | down | ANTAGONIST |
| 66 | New clues | CYPROTERONE ACETATE | down | ANTAGONIST |
| 67 | New clues | CLASCOTERONE | down | ANTAGONIST |
| 68 | New clues | NILUTAMIDE | down | ANTAGONIST |

**heart failure / GUCY1A1.** Approved medicines turn it **up**: ISOSORBIDE DINITRATE (ACTIVATOR); NITROGLYCERIN (ACTIVATOR); VERICIGUAT (ACTIVATOR).

| # | tab | card medicine | card direction | card action words |
|---|---|---|---|---|
| 69 | New clues | METHYLENE BLUE CATION | down | INHIBITOR |

**heart failure / GUCY1B1.** Approved medicines turn it **up**: ISOSORBIDE DINITRATE (ACTIVATOR); NITROGLYCERIN (ACTIVATOR); VERICIGUAT (ACTIVATOR).

| # | tab | card medicine | card direction | card action words |
|---|---|---|---|---|
| 70 | New clues | METHYLENE BLUE CATION | down | INHIBITOR |

**heart failure / AGTR1.** Approved medicines turn it **down**: CANDESARTAN CILEXETIL (ANTAGONIST); OLMESARTAN MEDOXOMIL (ANTAGONIST); VALSARTAN (ANTAGONIST).

| # | tab | card medicine | card direction | card action words |
|---|---|---|---|---|
| 71 | New clues | ANGIOTENSIN II | up | AGONIST |

**heart failure / ADRB3.** Approved medicines turn it **down**: CARVEDILOL (ANTAGONIST).

| # | tab | card medicine | card direction | card action words |
|---|---|---|---|---|
| 72 | New clues | DROXIDOPA | up | AGONIST |
| 73 | New clues | VIBEGRON | up | AGONIST |
| 74 | New clues | MEPHENTERMINE | up | AGONIST |
| 75 | New clues | DIPIVEFRIN | up | AGONIST |
| 76 | New clues | HYDROXYAMPHETAMINE | up | AGONIST |
| 77 | In trials | MIRABEGRON | up | AGONIST |

**heart failure / NR3C2.** Approved medicines turn it **down**: EPLERENONE (ANTAGONIST); FINERENONE (ANTAGONIST); SPIRONOLACTONE (ANTAGONIST).

| # | tab | card medicine | card direction | card action words |
|---|---|---|---|---|
| 78 | New clues | FLUDROCORTISONE ACETATE | up | AGONIST |
| 79 | New clues | DESOXYCORTICOSTERONE ACETATE | up | AGONIST |
| 80 | New clues | DESOXYCORTICOSTERONE PIVALATE | up | AGONIST |

**chronic obstructive pulmonary disease / CHRM3.** Approved medicines turn it **down**: ACLIDINIUM (ANTAGONIST); GLYCOPYRRONIUM (INHIBITOR, ANTAGONIST); IPRATROPIUM (ANTAGONIST); REVEFENACIN (ANTAGONIST); TIOTROPIUM (ANTAGONIST); UMECLIDINIUM (ANTAGONIST).

| # | tab | card medicine | card direction | card action words |
|---|---|---|---|---|
| 81 | New clues | PILOCARPINE | up | AGONIST |
| 82 | New clues | CEVIMELINE | up | AGONIST |
| 83 | New clues | BETHANECHOL | up | AGONIST |
| 84 | New clues | CARBAMOYLCHOLINE | up | AGONIST |
| 85 | New clues | METHACHOLINE | up | AGONIST |
| 86 | In trials | ACETYLCHOLINE | up | AGONIST |

**chronic obstructive pulmonary disease / CHRM1.** Approved medicines turn it **down**: GLYCOPYRRONIUM (ANTAGONIST, INHIBITOR).

| # | tab | card medicine | card direction | card action words |
|---|---|---|---|---|
| 87 | New clues | PILOCARPINE | up | AGONIST |
| 88 | New clues | CEVIMELINE | up | AGONIST |
| 89 | New clues | XANOMELINE | up | AGONIST |

**chronic obstructive pulmonary disease / CHRM2.** Approved medicines turn it **down**: GLYCOPYRRONIUM (INHIBITOR).

| # | tab | card medicine | card direction | card action words |
|---|---|---|---|---|
| 90 | New clues | BETHANECHOL | up | AGONIST |
| 91 | New clues | ALCURONIUM | up | POSITIVE ALLOSTERIC MODULATOR |

**chronic obstructive pulmonary disease / CHRM4.** Approved medicines turn it **down**: GLYCOPYRRONIUM (INHIBITOR).

| # | tab | card medicine | card direction | card action words |
|---|---|---|---|---|
| 92 | New clues | XANOMELINE | up | AGONIST |

**chronic obstructive pulmonary disease / ADORA1.** Approved medicines turn it **down**: THEOPHYLLINE ANHYDROUS (ANTAGONIST).

| # | tab | card medicine | card direction | card action words |
|---|---|---|---|---|
| 93 | New clues | DEFIBROTIDE | up | AGONIST |
| 94 | New clues | ADENOSINE | up | AGONIST |

**chronic obstructive pulmonary disease / ADORA2A.** Approved medicines turn it **down**: THEOPHYLLINE ANHYDROUS (ANTAGONIST).

| # | tab | card medicine | card direction | card action words |
|---|---|---|---|---|
| 95 | New clues | DEFIBROTIDE | up | AGONIST |
| 96 | New clues | ADENOSINE | up | AGONIST |
| 97 | New clues | REGADENOSON ANHYDROUS | up | AGONIST |

**chronic obstructive pulmonary disease / NR3C1.** Approved medicines turn it **up**: BECLOMETHASONE DIPROPIONATE (AGONIST); BUDESONIDE (AGONIST); FLUOROMETHOLONE (AGONIST); FLUTICASONE FUROATE (AGONIST); FLUTICASONE PROPIONATE (AGONIST); MEPREDNISONE (AGONIST); PREDNISOLONE PHOSPHORIC ACID (AGONIST).

| # | tab | card medicine | card direction | card action words |
|---|---|---|---|---|
| 98 | New clues | MIFEPRISTONE | down | ANTAGONIST |
| 99 | New clues | CYPROTERONE ACETATE | down | ANTAGONIST |

**chronic obstructive pulmonary disease / ADRB2.** Approved medicines turn it **up**: ALBUTEROL (AGONIST); ARFORMOTEROL (AGONIST); BITOLTEROL (AGONIST); FORMOTEROL (AGONIST); INDACATEROL (AGONIST); OLODATEROL (AGONIST); SALMETEROL (AGONIST); VILANTEROL (AGONIST).

| # | tab | card medicine | card direction | card action words |
|---|---|---|---|---|
| 100 | New clues | TIMOLOL | down | ANTAGONIST |
| 101 | New clues | LABETALOL | down | ANTAGONIST |
| 102 | New clues | SOTALOL | down | ANTAGONIST |
| 103 | New clues | PROPAFENONE | down | ANTAGONIST |
| 104 | New clues | NADOLOL | down | ANTAGONIST |
| 105 | New clues | CARTEOLOL | down | ANTAGONIST |
| 106 | New clues | LEVOBUNOLOL | down | ANTAGONIST |
| 107 | New clues | BUCINDOLOL | down | ANTAGONIST |
| 108 | New clues | OXPRENOLOL | down | ANTAGONIST |
| 109 | New clues | PENBUTOLOL | down | ANTAGONIST |
| 110 | In trials | NEBIVOLOL | down | ANTAGONIST |

**chronic kidney disease / AGTR1.** Approved medicines turn it **down**: IRBESARTAN (ANTAGONIST); LOSARTAN (ANTAGONIST).

| # | tab | card medicine | card direction | card action words |
|---|---|---|---|---|
| 111 | New clues | ANGIOTENSIN II | up | AGONIST |

**chronic kidney disease / NR3C2.** Approved medicines turn it **down**: FINERENONE (ANTAGONIST).

| # | tab | card medicine | card direction | card action words |
|---|---|---|---|---|
| 112 | New clues | FLUDROCORTISONE ACETATE | up | AGONIST |
| 113 | New clues | DESOXYCORTICOSTERONE ACETATE | up | AGONIST |
| 114 | New clues | DESOXYCORTICOSTERONE PIVALATE | up | AGONIST |

**chronic kidney disease / GHR.** Approved medicines turn it **up**: SOMATROPIN (AGONIST).

| # | tab | card medicine | card direction | card action words |
|---|---|---|---|---|
| 115 | New clues | PEGVISOMANT | down | ANTAGONIST |

**depressive disorder / DRD2.** Approved medicines turn it **down**: OLANZAPINE (ANTAGONIST).

| # | tab | card medicine | card direction | card action words |
|---|---|---|---|---|
| 116 | New clues | ERGOLOID | up | AGONIST |
| 117 | New clues | ROTIGOTINE | up | AGONIST |
| 118 | New clues | APOMORPHINE | up | AGONIST |
| 119 | New clues | BROMOCRIPTINE | up | AGONIST |
| 120 | New clues | CABERGOLINE | up | AGONIST |
| 121 | New clues | QUINAGOLIDE | up | AGONIST |
| 122 | In trials | PRAMIPEXOLE | up | AGONIST |
| 123 | In trials | ROPINIROLE | up | AGONIST |

**depressive disorder / DRD3.** Approved medicines turn it **down**: OLANZAPINE (ANTAGONIST).

| # | tab | card medicine | card direction | card action words |
|---|---|---|---|---|
| 124 | New clues | ERGOLOID | up | AGONIST |
| 125 | New clues | ROTIGOTINE | up | AGONIST |
| 126 | New clues | APOMORPHINE | up | AGONIST |
| 127 | New clues | BROMOCRIPTINE | up | AGONIST |
| 128 | In trials | PRAMIPEXOLE | up | AGONIST |
| 129 | In trials | ROPINIROLE | up | AGONIST |
| 130 | In trials | LEVODOPA | up | AGONIST |

**depressive disorder / DRD4.** Approved medicines turn it **down**: OLANZAPINE (ANTAGONIST).

| # | tab | card medicine | card direction | card action words |
|---|---|---|---|---|
| 131 | New clues | ERGOLOID | up | AGONIST |
| 132 | New clues | ROTIGOTINE | up | AGONIST |
| 133 | New clues | APOMORPHINE | up | AGONIST |
| 134 | New clues | BROMOCRIPTINE | up | AGONIST |
| 135 | In trials | PRAMIPEXOLE | up | AGONIST |
| 136 | In trials | ROPINIROLE | up | AGONIST |

**depressive disorder / GABRA1.** Approved medicines turn it **up**: BREXANOLONE (POSITIVE ALLOSTERIC MODULATOR).

| # | tab | card medicine | card direction | card action words |
|---|---|---|---|---|
| 137 | New clues | ETIFOXINE | down | ANTAGONIST |

**depressive disorder / GABRB1.** Approved medicines turn it **up**: BREXANOLONE (POSITIVE ALLOSTERIC MODULATOR).

| # | tab | card medicine | card direction | card action words |
|---|---|---|---|---|
| 138 | New clues | ETIFOXINE | down | ANTAGONIST |

**depressive disorder / GABRA6.** Approved medicines turn it **up**: BREXANOLONE (POSITIVE ALLOSTERIC MODULATOR).

| # | tab | card medicine | card direction | card action words |
|---|---|---|---|---|
| 139 | New clues | ETIFOXINE | down | ANTAGONIST |

**depressive disorder / GABRA2.** Approved medicines turn it **up**: BREXANOLONE (POSITIVE ALLOSTERIC MODULATOR).

| # | tab | card medicine | card direction | card action words |
|---|---|---|---|---|
| 140 | New clues | ETIFOXINE | down | ANTAGONIST |

**depressive disorder / GABRG3.** Approved medicines turn it **up**: BREXANOLONE (POSITIVE ALLOSTERIC MODULATOR).

| # | tab | card medicine | card direction | card action words |
|---|---|---|---|---|
| 141 | New clues | ETIFOXINE | down | ANTAGONIST |

**depressive disorder / GABRB2.** Approved medicines turn it **up**: BREXANOLONE (POSITIVE ALLOSTERIC MODULATOR).

| # | tab | card medicine | card direction | card action words |
|---|---|---|---|---|
| 142 | New clues | ETIFOXINE | down | ANTAGONIST |

**depressive disorder / GABRG2.** Approved medicines turn it **up**: BREXANOLONE (POSITIVE ALLOSTERIC MODULATOR).

| # | tab | card medicine | card direction | card action words |
|---|---|---|---|---|
| 143 | New clues | ETIFOXINE | down | ANTAGONIST |

**depressive disorder / GABRA5.** Approved medicines turn it **up**: BREXANOLONE (POSITIVE ALLOSTERIC MODULATOR).

| # | tab | card medicine | card direction | card action words |
|---|---|---|---|---|
| 144 | New clues | ETIFOXINE | down | ANTAGONIST |

**depressive disorder / HTR1A.** Approved medicines turn it **up**: VORTIOXETINE (AGONIST).

| # | tab | card medicine | card direction | card action words |
|---|---|---|---|---|
| 145 | New clues | ALVERINE | down | ANTAGONIST |

**depressive disorder / ADRA2A.** Approved medicines turn it **down**: MIRTAZAPINE (ANTAGONIST).

| # | tab | card medicine | card direction | card action words |
|---|---|---|---|---|
| 146 | New clues | DEXMEDETOMIDINE | up | AGONIST |
| 147 | New clues | EPINEPHRINE | up | AGONIST |
| 148 | New clues | CLONIDINE | up | AGONIST |
| 149 | New clues | BRIMONIDINE | up | AGONIST |
| 150 | New clues | GUANFACINE | up | AGONIST |
| 151 | New clues | OXYMETAZOLINE | up | AGONIST |
| 152 | New clues | LOFEXIDINE | up | AGONIST |
| 153 | New clues | TIZANIDINE | up | AGONIST |
| 154 | New clues | METHYLDOPA | up | AGONIST |
| 155 | New clues | NAPHAZOLINE | up | AGONIST |
| 156 | New clues | XYLOMETAZOLINE | up | AGONIST |
| 157 | New clues | APRACLONIDINE | up | AGONIST |
| 158 | New clues | TETRAHYDROZOLINE | up | AGONIST |
| 159 | New clues | GUANABENZ | up | AGONIST |
| 160 | New clues | MEPHENTERMINE | up | AGONIST |
| 161 | New clues | DIPIVEFRIN | up | AGONIST |
| 162 | New clues | HYDROXYAMPHETAMINE | up | AGONIST |
| 163 | New clues | METHYLDOPATE | up | AGONIST |
| 164 | In trials | DROXIDOPA | up | AGONIST |

**schizophrenia / DRD2.** Approved medicines turn it **down**: AMISULPRIDE (ANTAGONIST); ASENAPINE (ANTAGONIST); BENPERIDOL (ANTAGONIST); BLONANSERIN (ANTAGONIST); BROMPERIDOL (ANTAGONIST); CARPHENAZINE (ANTAGONIST); CHLORPROMAZINE (ANTAGONIST); CLOZAPINE (ANTAGONIST); FLUPHENAZINE DECANOATE (ANTAGONIST); FLUSPIRILENE (INHIBITOR); ILOPERIDONE (ANTAGONIST); LOXAPINE (ANTAGONIST); LUMATEPERONE (ANTAGONIST); LURASIDONE (ANTAGONIST); MESORIDAZINE (ANTAGONIST); MOLINDONE (ANTAGONIST); OLANZAPINE (ANTAGONIST); PALIPERIDONE (ANTAGONIST); PALIPERIDONE PALMITATE (ANTAGONIST); PERPHENAZINE (ANTAGONIST); PIMOZIDE (ANTAGONIST); PIPERACETAZINE (ANTAGONIST); PROCHLORPERAZINE (ANTAGONIST); QUETIAPINE (ANTAGONIST); RISPERIDONE (ANTAGONIST); SULPIRIDE (ANTAGONIST); THIOTHIXENE (ANTAGONIST); TRIFLUOPERAZINE (ANTAGONIST); TRIFLUPROMAZINE (ANTAGONIST); ZIPRASIDONE (ANTAGONIST).

| # | tab | card medicine | card direction | card action words |
|---|---|---|---|---|
| 165 | New clues | ERGOLOID | up | AGONIST |
| 166 | New clues | ROTIGOTINE | up | AGONIST |
| 167 | New clues | ROPINIROLE | up | AGONIST |
| 168 | New clues | APOMORPHINE | up | AGONIST |
| 169 | New clues | BROMOCRIPTINE | up | AGONIST |
| 170 | New clues | CABERGOLINE | up | AGONIST |
| 171 | New clues | QUINAGOLIDE | up | AGONIST |
| 172 | In trials | PRAMIPEXOLE | up | AGONIST |

**schizophrenia / DRD3.** Approved medicines turn it **down**: AMISULPRIDE (ANTAGONIST); BLONANSERIN (ANTAGONIST); CHLORPROMAZINE (ANTAGONIST); LOXAPINE (ANTAGONIST); OLANZAPINE (ANTAGONIST); PIMOZIDE (ANTAGONIST); TRIFLUOPERAZINE (ANTAGONIST).

| # | tab | card medicine | card direction | card action words |
|---|---|---|---|---|
| 173 | New clues | ERGOLOID | up | AGONIST |
| 174 | New clues | ROTIGOTINE | up | AGONIST |
| 175 | New clues | ROPINIROLE | up | AGONIST |
| 176 | New clues | APOMORPHINE | up | AGONIST |
| 177 | New clues | BROMOCRIPTINE | up | AGONIST |
| 178 | In trials | PRAMIPEXOLE | up | AGONIST |
| 179 | In trials | LEVODOPA | up | AGONIST |

**schizophrenia / DRD4.** Approved medicines turn it **down**: CHLORPROMAZINE (ANTAGONIST); CLOTHIAPINE (ANTAGONIST); LOXAPINE (ANTAGONIST); OLANZAPINE (ANTAGONIST); PIMOZIDE (ANTAGONIST); TRIFLUOPERAZINE (ANTAGONIST).

| # | tab | card medicine | card direction | card action words |
|---|---|---|---|---|
| 180 | New clues | ERGOLOID | up | AGONIST |
| 181 | New clues | ROTIGOTINE | up | AGONIST |
| 182 | New clues | ROPINIROLE | up | AGONIST |
| 183 | New clues | APOMORPHINE | up | AGONIST |
| 184 | New clues | BROMOCRIPTINE | up | AGONIST |
| 185 | In trials | PRAMIPEXOLE | up | AGONIST |

**schizophrenia / HTR1A.** Approved medicines turn it **down**: AMISULPRIDE (ANTAGONIST).

| # | tab | card medicine | card direction | card action words |
|---|---|---|---|---|
| 186 | New clues | ERGOLOID | up | AGONIST |
| 187 | New clues | GEPIRONE | up | AGONIST |
| 188 | In trials | VORTIOXETINE | up | AGONIST |

**schizophrenia / HTR1B.** Approved medicines turn it **down**: AMISULPRIDE (ANTAGONIST).

| # | tab | card medicine | card direction | card action words |
|---|---|---|---|---|
| 189 | New clues | ERGOLOID | up | AGONIST |
| 190 | New clues | ELETRIPTAN | up | AGONIST |
| 191 | New clues | ALMOTRIPTAN | up | AGONIST |
| 192 | New clues | SUMATRIPTAN | up | AGONIST |
| 193 | New clues | RIZATRIPTAN | up | AGONIST |
| 194 | New clues | ZOLMITRIPTAN | up | AGONIST |
| 195 | New clues | NARATRIPTAN | up | AGONIST |
| 196 | New clues | FROVATRIPTAN | up | AGONIST |

**schizophrenia / HTR4.** Approved medicines turn it **down**: AMISULPRIDE (ANTAGONIST).

| # | tab | card medicine | card direction | card action words |
|---|---|---|---|---|
| 197 | New clues | METOCLOPRAMIDE | up | AGONIST |
| 198 | New clues | CLEBOPRIDE | up | AGONIST |
| 199 | New clues | MOSAPRIDE | up | AGONIST |
| 200 | In trials | LEVOSULPIRIDE | up | AGONIST |

**schizophrenia / HTR1F.** Approved medicines turn it **down**: AMISULPRIDE (ANTAGONIST).

| # | tab | card medicine | card direction | card action words |
|---|---|---|---|---|
| 201 | New clues | ELETRIPTAN | up | AGONIST |
| 202 | New clues | ALMOTRIPTAN | up | AGONIST |
| 203 | New clues | LASMIDITAN | up | AGONIST |

**schizophrenia / HTR1D.** Approved medicines turn it **down**: AMISULPRIDE (ANTAGONIST).

| # | tab | card medicine | card direction | card action words |
|---|---|---|---|---|
| 204 | New clues | ELETRIPTAN | up | AGONIST |
| 205 | New clues | ALMOTRIPTAN | up | AGONIST |
| 206 | New clues | SUMATRIPTAN | up | AGONIST |
| 207 | New clues | RIZATRIPTAN | up | AGONIST |
| 208 | New clues | ZOLMITRIPTAN | up | AGONIST |
| 209 | New clues | NARATRIPTAN | up | AGONIST |
| 210 | New clues | FROVATRIPTAN | up | AGONIST |
| 211 | New clues | DIHYDROERGOTAMINE | up | AGONIST |

**bipolar disorder / DRD2.** Approved medicines turn it **down**: ACETOPHENAZINE (ANTAGONIST); ASENAPINE (ANTAGONIST); ILOPERIDONE (ANTAGONIST); LEVOMEPROMAZINE (ANTAGONIST); LOXAPINE (ANTAGONIST); LURASIDONE (ANTAGONIST); OLANZAPINE (ANTAGONIST); QUETIAPINE (ANTAGONIST); RISPERIDONE (ANTAGONIST); ZIPRASIDONE (ANTAGONIST).

| # | tab | card medicine | card direction | card action words |
|---|---|---|---|---|
| 212 | New clues | ERGOLOID | up | AGONIST |
| 213 | New clues | ROTIGOTINE | up | AGONIST |
| 214 | New clues | ROPINIROLE | up | AGONIST |
| 215 | New clues | APOMORPHINE | up | AGONIST |
| 216 | New clues | BROMOCRIPTINE | up | AGONIST |
| 217 | New clues | CABERGOLINE | up | AGONIST |
| 218 | New clues | QUINAGOLIDE | up | AGONIST |
| 219 | In trials | PRAMIPEXOLE | up | AGONIST |

**bipolar disorder / DRD4.** Approved medicines turn it **down**: LEVOMEPROMAZINE (ANTAGONIST); LOXAPINE (ANTAGONIST); OLANZAPINE (ANTAGONIST).

| # | tab | card medicine | card direction | card action words |
|---|---|---|---|---|
| 220 | New clues | ERGOLOID | up | AGONIST |
| 221 | New clues | ROTIGOTINE | up | AGONIST |
| 222 | New clues | ROPINIROLE | up | AGONIST |
| 223 | New clues | APOMORPHINE | up | AGONIST |
| 224 | New clues | BROMOCRIPTINE | up | AGONIST |
| 225 | In trials | PRAMIPEXOLE | up | AGONIST |

**bipolar disorder / DRD3.** Approved medicines turn it **down**: LEVOMEPROMAZINE (ANTAGONIST); LOXAPINE (ANTAGONIST); OLANZAPINE (ANTAGONIST).

| # | tab | card medicine | card direction | card action words |
|---|---|---|---|---|
| 226 | New clues | ERGOLOID | up | AGONIST |
| 227 | New clues | ROTIGOTINE | up | AGONIST |
| 228 | New clues | ROPINIROLE | up | AGONIST |
| 229 | New clues | APOMORPHINE | up | AGONIST |
| 230 | New clues | BROMOCRIPTINE | up | AGONIST |
| 231 | New clues | LEVODOPA | up | AGONIST |
| 232 | In trials | PRAMIPEXOLE | up | AGONIST |

**Parkinson disease / DRD2.** Approved medicines turn it **up**: APOMORPHINE (AGONIST); BROMOCRIPTINE (AGONIST); CABERGOLINE (AGONIST); PRAMIPEXOLE (AGONIST); ROPINIROLE (AGONIST); ROTIGOTINE (AGONIST).

| # | tab | card medicine | card direction | card action words |
|---|---|---|---|---|
| 233 | New clues | BLONANSERIN | down | ANTAGONIST |
| 234 | New clues | TIAPRIDE | down | ANTAGONIST |
| 235 | New clues | CHLORPROTHIXENE | down | ANTAGONIST |
| 236 | New clues | ITOPRIDE | down | ANTAGONIST |
| 237 | New clues | OLANZAPINE | down | ANTAGONIST |
| 238 | New clues | RISPERIDONE | down | ANTAGONIST |
| 239 | New clues | ZIPRASIDONE | down | ANTAGONIST |
| 240 | New clues | PALIPERIDONE | down | ANTAGONIST |
| 241 | New clues | METOCLOPRAMIDE | down | ANTAGONIST |
| 242 | New clues | AMISULPRIDE | down | ANTAGONIST |
| 243 | New clues | LURASIDONE | down | ANTAGONIST |
| 244 | New clues | LOXAPINE | down | ANTAGONIST |
| 245 | New clues | PALIPERIDONE PALMITATE | down | ANTAGONIST |
| 246 | New clues | ASENAPINE | down | ANTAGONIST |
| 247 | New clues | CHLORPROMAZINE | down | ANTAGONIST |
| 248 | New clues | PERPHENAZINE | down | ANTAGONIST |
| 249 | New clues | DOMPERIDONE | down | ANTAGONIST |
| 250 | New clues | PIMOZIDE | down | ANTAGONIST |
| 251 | New clues | PROCHLORPERAZINE | down | ANTAGONIST |
| 252 | New clues | LUMATEPERONE | down | ANTAGONIST |
| 253 | New clues | ILOPERIDONE | down | ANTAGONIST |
| 254 | New clues | TRIFLUOPERAZINE | down | ANTAGONIST |
| 255 | New clues | AMOXAPINE | down | ANTAGONIST |
| 256 | New clues | FLUPHENAZINE | down | ANTAGONIST |
| 257 | New clues | MOLINDONE | down | ANTAGONIST |
| 258 | New clues | LEVOMEPROMAZINE | down | ANTAGONIST |
| 259 | New clues | SULPIRIDE | down | ANTAGONIST |
| 260 | New clues | THIOTHIXENE | down | ANTAGONIST |
| 261 | New clues | TRIMIPRAMINE | down | ANTAGONIST |
| 262 | New clues | FLUPHENAZINE DECANOATE | down | ANTAGONIST |
| 263 | New clues | PROMAZINE | down | ANTAGONIST |
| 264 | New clues | THIETHYLPERAZINE | down | ANTAGONIST |
| 265 | New clues | BROMOPRIDE | down | ANTAGONIST |
| 266 | New clues | LEVOSULPIRIDE | down | ANTAGONIST |
| 267 | New clues | TRIFLUPROMAZINE | down | ANTAGONIST |
| 268 | New clues | ACETOPHENAZINE | down | ANTAGONIST |
| 269 | New clues | ALIZAPRIDE | down | ANTAGONIST |
| 270 | New clues | BENPERIDOL | down | ANTAGONIST |
| 271 | New clues | BROMPERIDOL | down | ANTAGONIST |
| 272 | New clues | FLUSPIRILENE | down | INHIBITOR |
| 273 | New clues | MESORIDAZINE | down | ANTAGONIST |
| 274 | New clues | CARPHENAZINE | down | ANTAGONIST |
| 275 | New clues | CLEBOPRIDE | down | ANTAGONIST |
| 276 | New clues | FLUPHENAZINE ENANTHATE | down | ANTAGONIST |
| 277 | New clues | PIPERACETAZINE | down | ANTAGONIST |
| 278 | In trials | QUETIAPINE | down | ANTAGONIST |
| 279 | In trials | CLOZAPINE | down | ANTAGONIST |

**Parkinson disease / DRD3.** Approved medicines turn it **up**: APOMORPHINE (AGONIST); BROMOCRIPTINE (AGONIST); LEVODOPA (AGONIST); PRAMIPEXOLE (AGONIST); ROPINIROLE (AGONIST); ROTIGOTINE (AGONIST).

| # | tab | card medicine | card direction | card action words |
|---|---|---|---|---|
| 280 | New clues | BLONANSERIN | down | ANTAGONIST |
| 281 | New clues | TIAPRIDE | down | ANTAGONIST |
| 282 | New clues | CHLORPROTHIXENE | down | ANTAGONIST |
| 283 | New clues | OLANZAPINE | down | ANTAGONIST |
| 284 | New clues | AMISULPRIDE | down | ANTAGONIST |
| 285 | New clues | LOXAPINE | down | ANTAGONIST |
| 286 | New clues | CHLORPROMAZINE | down | ANTAGONIST |
| 287 | New clues | PIMOZIDE | down | ANTAGONIST |
| 288 | New clues | TRIFLUOPERAZINE | down | ANTAGONIST |
| 289 | New clues | AMOXAPINE | down | ANTAGONIST |
| 290 | New clues | LEVOMEPROMAZINE | down | ANTAGONIST |
| 291 | New clues | PROMAZINE | down | ANTAGONIST |

**Parkinson disease / CHRM1.** Approved medicines turn it **down**: ATROPINE (ANTAGONIST); BENZTROPINE (ANTAGONIST); BIPERIDEN (ANTAGONIST); CYCRIMINE (ANTAGONIST); ETHOPROPAZINE (ANTAGONIST); METHIXENE (ANTAGONIST); PROCYCLIDINE (ANTAGONIST); TRIHEXYPHENIDYL (ANTAGONIST).

| # | tab | card medicine | card direction | card action words |
|---|---|---|---|---|
| 292 | New clues | PILOCARPINE | up | AGONIST |
| 293 | New clues | CEVIMELINE | up | AGONIST |
| 294 | In trials | XANOMELINE | up | AGONIST |

**Parkinson disease / ACHE.** Approved medicines turn it **down**: RIVASTIGMINE (INHIBITOR).

| # | tab | card medicine | card direction | card action words |
|---|---|---|---|---|
| 295 | New clues | PRALIDOXIME | up | ACTIVATOR |

**Alzheimer disease / ACHE.** Approved medicines turn it **down**: DONEPEZIL (INHIBITOR); GALANTAMINE (INHIBITOR); HUPERZINE A (INHIBITOR); RIVASTIGMINE (INHIBITOR); TACRINE (INHIBITOR).

| # | tab | card medicine | card direction | card action words |
|---|---|---|---|---|
| 296 | New clues | PRALIDOXIME | up | ACTIVATOR |

**glaucoma / ADRA2A.** Approved medicines turn it **up**: APRACLONIDINE (AGONIST); BRIMONIDINE (AGONIST); CLONIDINE (AGONIST); DIPIVEFRIN (AGONIST); EPINEPHRINE (AGONIST).

| # | tab | card medicine | card direction | card action words |
|---|---|---|---|---|
| 297 | New clues | CELIPROLOL | down | ANTAGONIST |
| 298 | New clues | LABETALOL | down | ANTAGONIST |
| 299 | New clues | MIRTAZAPINE | down | ANTAGONIST |
| 300 | New clues | PHENTOLAMINE | down | ANTAGONIST |
| 301 | New clues | PHENOXYBENZAMINE | down | ANTAGONIST |
| 302 | New clues | RAUWOLFIA SERPENTINA | down | ANTAGONIST |
| 303 | New clues | ERGOLOID | down | ANTAGONIST |
| 304 | New clues | TOLAZOLINE | down | ANTAGONIST |
| 305 | New clues | ALSEROXYLON | down | ANTAGONIST |

**glaucoma / ADRA2B.** Approved medicines turn it **up**: APRACLONIDINE (AGONIST); BRIMONIDINE (AGONIST); CLONIDINE (AGONIST); DIPIVEFRIN (AGONIST); EPINEPHRINE (AGONIST).

| # | tab | card medicine | card direction | card action words |
|---|---|---|---|---|
| 306 | New clues | CELIPROLOL | down | ANTAGONIST |
| 307 | New clues | LABETALOL | down | ANTAGONIST |
| 308 | New clues | MIRTAZAPINE | down | ANTAGONIST |
| 309 | New clues | PHENTOLAMINE | down | ANTAGONIST |
| 310 | New clues | PHENOXYBENZAMINE | down | ANTAGONIST |
| 311 | New clues | RAUWOLFIA SERPENTINA | down | ANTAGONIST |
| 312 | New clues | ERGOLOID | down | ANTAGONIST |
| 313 | New clues | TOLAZOLINE | down | ANTAGONIST |
| 314 | New clues | ALSEROXYLON | down | ANTAGONIST |

**glaucoma / ADRA2C.** Approved medicines turn it **up**: APRACLONIDINE (AGONIST); BRIMONIDINE (AGONIST); CLONIDINE (AGONIST); DIPIVEFRIN (AGONIST); EPINEPHRINE (AGONIST).

| # | tab | card medicine | card direction | card action words |
|---|---|---|---|---|
| 315 | New clues | CELIPROLOL | down | ANTAGONIST |
| 316 | New clues | LABETALOL | down | ANTAGONIST |
| 317 | New clues | MIRTAZAPINE | down | ANTAGONIST |
| 318 | New clues | PHENTOLAMINE | down | ANTAGONIST |
| 319 | New clues | PHENOXYBENZAMINE | down | ANTAGONIST |
| 320 | New clues | RAUWOLFIA SERPENTINA | down | ANTAGONIST |
| 321 | New clues | ERGOLOID | down | ANTAGONIST |
| 322 | New clues | TOLAZOLINE | down | ANTAGONIST |
| 323 | New clues | ALSEROXYLON | down | ANTAGONIST |

**endometriosis / ESR1.** Approved medicines turn it **up**: ETHINYL ESTRADIOL (AGONIST).

| # | tab | card medicine | card direction | card action words |
|---|---|---|---|---|
| 324 | New clues | FULVESTRANT | down | ANTAGONIST, DEGRADER |

**endometriosis / AR.** Approved medicines turn it **up**: DANAZOL (AGONIST).

| # | tab | card medicine | card direction | card action words |
|---|---|---|---|---|
| 325 | New clues | ENZALUTAMIDE | down | ANTAGONIST |
| 326 | New clues | BICALUTAMIDE | down | ANTAGONIST |
| 327 | New clues | APALUTAMIDE | down | ANTAGONIST |
| 328 | New clues | DAROLUTAMIDE | down | ANTAGONIST |
| 329 | New clues | ABIRATERONE | down | ANTAGONIST |
| 330 | New clues | FLUTAMIDE | down | ANTAGONIST |
| 331 | New clues | CLASCOTERONE | down | ANTAGONIST |
| 332 | New clues | NILUTAMIDE | down | ANTAGONIST |
| 333 | In trials | CYPROTERONE ACETATE | down | ANTAGONIST |

**endometriosis / NR3C2.** Approved medicines turn it **down**: DROSPIRENONE (ANTAGONIST).

| # | tab | card medicine | card direction | card action words |
|---|---|---|---|---|
| 334 | New clues | FLUDROCORTISONE ACETATE | up | AGONIST |
| 335 | New clues | DESOXYCORTICOSTERONE ACETATE | up | AGONIST |
| 336 | New clues | DESOXYCORTICOSTERONE PIVALATE | up | AGONIST |

**endometriosis / PGR.** Approved medicines turn it **up**: DANAZOL (AGONIST); DROSPIRENONE (AGONIST); MEDROXYPROGESTERONE ACETATE (AGONIST); NORETHINDRONE (AGONIST); NORETHINDRONE ACETATE (AGONIST).

| # | tab | card medicine | card direction | card action words |
|---|---|---|---|---|
| 337 | In trials | MIFEPRISTONE | down | ANTAGONIST |

**malaria / TLR7.** Approved medicines turn it **down**: HYDROXYCHLOROQUINE (ANTAGONIST).

| # | tab | card medicine | card direction | card action words |
|---|---|---|---|---|
| 338 | New clues | IMIQUIMOD | up | AGONIST |

**prostate cancer / AR.** Approved medicines turn it **down**: ABIRATERONE (ANTAGONIST); APALUTAMIDE (ANTAGONIST); BICALUTAMIDE (ANTAGONIST); DAROLUTAMIDE (ANTAGONIST); ENZALUTAMIDE (ANTAGONIST); FLUTAMIDE (ANTAGONIST); NILUTAMIDE (ANTAGONIST).

| # | tab | card medicine | card direction | card action words |
|---|---|---|---|---|
| 339 | New clues | DANAZOL | up | AGONIST |
| 340 | New clues | OXANDROLONE | up | AGONIST |
| 341 | New clues | METHYLTESTOSTERONE | up | AGONIST |
| 342 | New clues | FLUOXYMESTERONE | up | AGONIST |
| 343 | New clues | OXYMETHOLONE | up | AGONIST |
| 344 | New clues | ETHYLESTRENOL | up | AGONIST |
| 345 | New clues | STANOZOLOL | up | AGONIST |
| 346 | New clues | TESTOSTERONE PROPIONATE | up | AGONIST |
| 347 | In trials | TESTOSTERONE | up | AGONIST |
| 348 | In trials | TESTOSTERONE UNDECANOATE | up | AGONIST |
| 349 | In trials | TESTOSTERONE CYPIONATE | up | AGONIST |
| 350 | In trials | TESTOSTERONE ENANTHATE | up | AGONIST |

**colorectal cancer / FGFR2.** Approved medicines turn it **down**: NINTEDANIB (INHIBITOR); REGORAFENIB (INHIBITOR).

| # | tab | card medicine | card direction | card action words |
|---|---|---|---|---|
| 351 | New clues | PALIFERMIN | up | AGONIST |
| 352 | New clues | TRAFERMIN | up | AGONIST |

**chronic myeloid leukemia / PDGFRB.** Approved medicines turn it **down**: DASATINIB ANHYDROUS (INHIBITOR); IMATINIB (INHIBITOR).

| # | tab | card medicine | card direction | card action words |
|---|---|---|---|---|
| 353 | New clues | BECAPLERMIN | up | AGONIST |

**chronic myeloid leukemia / IFNAR1.** Approved medicines turn it **up**: INTERFERON ALFA-2B (AGONIST).

| # | tab | card medicine | card direction | card action words |
|---|---|---|---|---|
| 354 | New clues | ANIFROLUMAB | down | ANTAGONIST |

**acute myeloid leukemia / PDGFRB.** Approved medicines turn it **down**: MIDOSTAURIN (INHIBITOR); QUIZARTINIB (INHIBITOR).

| # | tab | card medicine | card direction | card action words |
|---|---|---|---|---|
| 355 | New clues | BECAPLERMIN | up | AGONIST |

**acute myeloid leukemia / PDGFRA.** Approved medicines turn it **down**: MIDOSTAURIN (INHIBITOR); QUIZARTINIB (INHIBITOR).

| # | tab | card medicine | card direction | card action words |
|---|---|---|---|---|
| 356 | New clues | BECAPLERMIN | up | AGONIST |

**cystic fibrosis / CFTR.** Approved medicines turn it **up**: ELEXACAFTOR (POSITIVE MODULATOR); IVACAFTOR (ACTIVATOR, POSITIVE MODULATOR); TEZACAFTOR (POSITIVE MODULATOR); VANZACAFTOR (POSITIVE MODULATOR).

| # | tab | card medicine | card direction | card action words |
|---|---|---|---|---|
| 357 | New clues | CROFELEMER | down | INHIBITOR |

**Duchenne muscular dystrophy / NR3C1.** Approved medicines turn it **up**: DEFLAZACORT (AGONIST); VAMOROLONE (AGONIST).

| # | tab | card medicine | card direction | card action words |
|---|---|---|---|---|
| 358 | New clues | MIFEPRISTONE | down | ANTAGONIST |
| 359 | New clues | CYPROTERONE ACETATE | down | ANTAGONIST |

**Duchenne muscular dystrophy / NR3C2.** Approved medicines turn it **down**: VAMOROLONE (ANTAGONIST).

| # | tab | card medicine | card direction | card action words |
|---|---|---|---|---|
| 360 | New clues | FLUDROCORTISONE ACETATE | up | AGONIST |
| 361 | New clues | DESOXYCORTICOSTERONE ACETATE | up | AGONIST |
| 362 | New clues | DESOXYCORTICOSTERONE PIVALATE | up | AGONIST |

**Huntington disease / ADRA2B.** Approved medicines turn it **up**: GUANFACINE (AGONIST).

| # | tab | card medicine | card direction | card action words |
|---|---|---|---|---|
| 363 | New clues | MIRTAZAPINE | down | ANTAGONIST |
| 364 | New clues | ERGOLOID | down | ANTAGONIST |
| 365 | New clues | LABETALOL | down | ANTAGONIST |
| 366 | New clues | PHENTOLAMINE | down | ANTAGONIST |
| 367 | New clues | PHENOXYBENZAMINE | down | ANTAGONIST |
| 368 | New clues | RAUWOLFIA SERPENTINA | down | ANTAGONIST |
| 369 | New clues | TOLAZOLINE | down | ANTAGONIST |
| 370 | New clues | CELIPROLOL | down | ANTAGONIST |
| 371 | New clues | ALSEROXYLON | down | ANTAGONIST |

**Huntington disease / ADRA2A.** Approved medicines turn it **up**: GUANFACINE (AGONIST).

| # | tab | card medicine | card direction | card action words |
|---|---|---|---|---|
| 372 | New clues | MIRTAZAPINE | down | ANTAGONIST |
| 373 | New clues | ERGOLOID | down | ANTAGONIST |
| 374 | New clues | LABETALOL | down | ANTAGONIST |
| 375 | New clues | PHENTOLAMINE | down | ANTAGONIST |
| 376 | New clues | PHENOXYBENZAMINE | down | ANTAGONIST |
| 377 | New clues | RAUWOLFIA SERPENTINA | down | ANTAGONIST |
| 378 | New clues | TOLAZOLINE | down | ANTAGONIST |
| 379 | New clues | CELIPROLOL | down | ANTAGONIST |
| 380 | New clues | ALSEROXYLON | down | ANTAGONIST |

**Huntington disease / ADRA2C.** Approved medicines turn it **up**: GUANFACINE (AGONIST).

| # | tab | card medicine | card direction | card action words |
|---|---|---|---|---|
| 381 | New clues | MIRTAZAPINE | down | ANTAGONIST |
| 382 | New clues | ERGOLOID | down | ANTAGONIST |
| 383 | New clues | LABETALOL | down | ANTAGONIST |
| 384 | New clues | PHENTOLAMINE | down | ANTAGONIST |
| 385 | New clues | PHENOXYBENZAMINE | down | ANTAGONIST |
| 386 | New clues | RAUWOLFIA SERPENTINA | down | ANTAGONIST |
| 387 | New clues | TOLAZOLINE | down | ANTAGONIST |
| 388 | New clues | CELIPROLOL | down | ANTAGONIST |
| 389 | New clues | ALSEROXYLON | down | ANTAGONIST |

**hemophilia A / PLG.** Approved medicines turn it **down**: TRANEXAMIC ACID (INHIBITOR).

| # | tab | card medicine | card direction | card action words |
|---|---|---|---|---|
| 390 | New clues | STREPTOKINASE | up | ACTIVATOR |
| 391 | New clues | DEFIBROTIDE | up | ACTIVATOR |
| 392 | New clues | DEFIBROTIDE SODIUM | up | ACTIVATOR |
| 393 | New clues | ANISTREPLASE | up | ACTIVATOR |

**myasthenia gravis / KCNQ4.** Approved medicines turn it **down**: AMIFAMPRIDINE (BLOCKER); GUANIDINE (BLOCKER).

| # | tab | card medicine | card direction | card action words |
|---|---|---|---|---|
| 394 | New clues | EZOGABINE | up | OPENER |

**hereditary angioedema / AR.** Approved medicines turn it **up**: STANOZOLOL (AGONIST).

| # | tab | card medicine | card direction | card action words |
|---|---|---|---|---|
| 395 | New clues | ENZALUTAMIDE | down | ANTAGONIST |
| 396 | New clues | BICALUTAMIDE | down | ANTAGONIST |
| 397 | New clues | APALUTAMIDE | down | ANTAGONIST |
| 398 | New clues | DAROLUTAMIDE | down | ANTAGONIST |
| 399 | New clues | ABIRATERONE | down | ANTAGONIST |
| 400 | New clues | FLUTAMIDE | down | ANTAGONIST |
| 401 | New clues | CYPROTERONE ACETATE | down | ANTAGONIST |
| 402 | New clues | CLASCOTERONE | down | ANTAGONIST |
| 403 | New clues | NILUTAMIDE | down | ANTAGONIST |

**acromegaly / DRD2.** Approved medicines turn it **up**: BROMOCRIPTINE (AGONIST).

| # | tab | card medicine | card direction | card action words |
|---|---|---|---|---|
| 404 | New clues | BLONANSERIN | down | ANTAGONIST |
| 405 | New clues | TIAPRIDE | down | ANTAGONIST |
| 406 | New clues | CHLORPROTHIXENE | down | ANTAGONIST |
| 407 | New clues | OLANZAPINE | down | ANTAGONIST |
| 408 | New clues | RISPERIDONE | down | ANTAGONIST |
| 409 | New clues | QUETIAPINE | down | ANTAGONIST |
| 410 | New clues | ZIPRASIDONE | down | ANTAGONIST |
| 411 | New clues | PALIPERIDONE | down | ANTAGONIST |
| 412 | New clues | METOCLOPRAMIDE | down | ANTAGONIST |
| 413 | New clues | AMISULPRIDE | down | ANTAGONIST |
| 414 | New clues | LOXAPINE | down | ANTAGONIST |
| 415 | New clues | CLOZAPINE | down | ANTAGONIST |
| 416 | New clues | LURASIDONE | down | ANTAGONIST |
| 417 | New clues | CHLORPROMAZINE | down | ANTAGONIST |
| 418 | New clues | PALIPERIDONE PALMITATE | down | ANTAGONIST |
| 419 | New clues | ASENAPINE | down | ANTAGONIST |
| 420 | New clues | PERPHENAZINE | down | ANTAGONIST |
| 421 | New clues | DOMPERIDONE | down | ANTAGONIST |
| 422 | New clues | PIMOZIDE | down | ANTAGONIST |
| 423 | New clues | PROCHLORPERAZINE | down | ANTAGONIST |
| 424 | New clues | LUMATEPERONE | down | ANTAGONIST |
| 425 | New clues | TRIFLUOPERAZINE | down | ANTAGONIST |
| 426 | New clues | ILOPERIDONE | down | ANTAGONIST |
| 427 | New clues | ITOPRIDE | down | ANTAGONIST |
| 428 | New clues | AMOXAPINE | down | ANTAGONIST |
| 429 | New clues | FLUPHENAZINE | down | ANTAGONIST |
| 430 | New clues | LEVOMEPROMAZINE | down | ANTAGONIST |
| 431 | New clues | MOLINDONE | down | ANTAGONIST |
| 432 | New clues | SULPIRIDE | down | ANTAGONIST |
| 433 | New clues | THIOTHIXENE | down | ANTAGONIST |
| 434 | New clues | TRIMIPRAMINE | down | ANTAGONIST |
| 435 | New clues | FLUPHENAZINE DECANOATE | down | ANTAGONIST |
| 436 | New clues | PROMAZINE | down | ANTAGONIST |
| 437 | New clues | THIETHYLPERAZINE | down | ANTAGONIST |
| 438 | New clues | BROMOPRIDE | down | ANTAGONIST |
| 439 | New clues | LEVOSULPIRIDE | down | ANTAGONIST |
| 440 | New clues | TRIFLUPROMAZINE | down | ANTAGONIST |
| 441 | New clues | ACETOPHENAZINE | down | ANTAGONIST |
| 442 | New clues | ALIZAPRIDE | down | ANTAGONIST |
| 443 | New clues | BENPERIDOL | down | ANTAGONIST |
| 444 | New clues | BROMPERIDOL | down | ANTAGONIST |
| 445 | New clues | FLUSPIRILENE | down | INHIBITOR |
| 446 | New clues | MESORIDAZINE | down | ANTAGONIST |
| 447 | New clues | CARPHENAZINE | down | ANTAGONIST |
| 448 | New clues | CLEBOPRIDE | down | ANTAGONIST |
| 449 | New clues | FLUPHENAZINE ENANTHATE | down | ANTAGONIST |
| 450 | New clues | PIPERACETAZINE | down | ANTAGONIST |

**acromegaly / DRD3.** Approved medicines turn it **up**: BROMOCRIPTINE (AGONIST).

| # | tab | card medicine | card direction | card action words |
|---|---|---|---|---|
| 451 | New clues | BLONANSERIN | down | ANTAGONIST |
| 452 | New clues | TIAPRIDE | down | ANTAGONIST |
| 453 | New clues | CHLORPROTHIXENE | down | ANTAGONIST |
| 454 | New clues | OLANZAPINE | down | ANTAGONIST |
| 455 | New clues | AMISULPRIDE | down | ANTAGONIST |
| 456 | New clues | LOXAPINE | down | ANTAGONIST |
| 457 | New clues | CHLORPROMAZINE | down | ANTAGONIST |
| 458 | New clues | PIMOZIDE | down | ANTAGONIST |
| 459 | New clues | TRIFLUOPERAZINE | down | ANTAGONIST |
| 460 | New clues | AMOXAPINE | down | ANTAGONIST |
| 461 | New clues | LEVOMEPROMAZINE | down | ANTAGONIST |
| 462 | New clues | PROMAZINE | down | ANTAGONIST |

**acromegaly / GHR.** Approved medicines turn it **down**: PEGVISOMANT (ANTAGONIST).

| # | tab | card medicine | card direction | card action words |
|---|---|---|---|---|
| 463 | New clues | SOMAPACITAN | up | AGONIST |
| 464 | New clues | SOMATROGON | up | AGONIST |
| 465 | New clues | LONAPEGSOMATROPIN | up | AGONIST |
| 466 | New clues | SOMATREM | up | AGONIST |

**acromegaly / DRD4.** Approved medicines turn it **up**: BROMOCRIPTINE (AGONIST).

| # | tab | card medicine | card direction | card action words |
|---|---|---|---|---|
| 467 | New clues | OLANZAPINE | down | ANTAGONIST |
| 468 | New clues | LOXAPINE | down | ANTAGONIST |
| 469 | New clues | CHLORPROMAZINE | down | ANTAGONIST |
| 470 | New clues | PIMOZIDE | down | ANTAGONIST |
| 471 | New clues | TRIFLUOPERAZINE | down | ANTAGONIST |
| 472 | New clues | AMOXAPINE | down | ANTAGONIST |
| 473 | New clues | LEVOMEPROMAZINE | down | ANTAGONIST |
| 474 | New clues | PROMAZINE | down | ANTAGONIST |
| 475 | New clues | CLOTHIAPINE | down | ANTAGONIST |

**Cushing syndrome / PGR.** Approved medicines turn it **down**: MIFEPRISTONE (ANTAGONIST).

| # | tab | card medicine | card direction | card action words |
|---|---|---|---|---|
| 476 | New clues | CYPROTERONE ACETATE | up | AGONIST |
| 477 | New clues | PROGESTERONE | up | AGONIST |
| 478 | New clues | LEVONORGESTREL | up | AGONIST |
| 479 | New clues | MEDROXYPROGESTERONE ACETATE | up | AGONIST |
| 480 | New clues | DROSPIRENONE | up | AGONIST |
| 481 | New clues | MEGESTROL ACETATE | up | AGONIST |
| 482 | New clues | DYDROGESTERONE | up | AGONIST |
| 483 | New clues | NORETHINDRONE ACETATE | up | AGONIST |
| 484 | New clues | DANAZOL | up | AGONIST |
| 485 | New clues | ETONOGESTREL | up | AGONIST |
| 486 | New clues | NORETHINDRONE | up | AGONIST |
| 487 | New clues | DESOGESTREL | up | AGONIST |
| 488 | New clues | NORGESTIMATE | up | AGONIST |
| 489 | New clues | NOMEGESTROL ACETATE | up | AGONIST |
| 490 | New clues | NORELGESTROMIN | up | AGONIST |
| 491 | New clues | GESTODENE | up | AGONIST |
| 492 | New clues | SEGESTERONE ACETATE | up | AGONIST |
| 493 | New clues | NORGESTREL | up | AGONIST |
| 494 | New clues | TRIMEGESTONE | up | AGONIST |
| 495 | New clues | ETHYNODIOL DIACETATE | up | AGONIST |

**Cushing syndrome / NR3C1.** Approved medicines turn it **down**: MIFEPRISTONE (ANTAGONIST).

| # | tab | card medicine | card direction | card action words |
|---|---|---|---|---|
| 496 | New clues | DEXAMETHASONE | up | AGONIST |
| 497 | New clues | BUDESONIDE | up | AGONIST |
| 498 | New clues | TRIAMCINOLONE ACETONIDE | up | AGONIST |
| 499 | New clues | FLUTICASONE PROPIONATE | up | AGONIST |
| 500 | New clues | TRIAMCINOLONE | up | AGONIST |
| 501 | New clues | BETAMETHASONE | up | AGONIST |
| 502 | New clues | BETAMETHASONE PHOSPHORIC ACID | up | AGONIST |
| 503 | New clues | BETAMETHASONE DIPROPIONATE | up | AGONIST |
| 504 | New clues | BECLOMETHASONE DIPROPIONATE | up | AGONIST |
| 505 | New clues | FLUTICASONE FUROATE | up | AGONIST |
| 506 | New clues | METHYLPREDNISOLONE ACETATE | up | AGONIST |
| 507 | New clues | MOMETASONE FUROATE | up | AGONIST |
| 508 | New clues | TRIAMCINOLONE HEXACETONIDE | up | AGONIST |
| 509 | New clues | CLOBETASOL PROPIONATE | up | AGONIST |
| 510 | New clues | CICLESONIDE | up | AGONIST |
| 511 | New clues | DEXAMETHASONE PHOSPHORIC ACID | up | AGONIST |
| 512 | New clues | PREDNISOLONE ACETATE | up | AGONIST |
| 513 | New clues | FLUOCINOLONE ACETONIDE | up | AGONIST |
| 514 | New clues | LOTEPREDNOL ETABONATE | up | AGONIST |
| 515 | New clues | METHYLPREDNISOLONE HEMISUCCINATE | up | AGONIST |
| 516 | New clues | HALOBETASOL PROPIONATE | up | AGONIST |
| 517 | New clues | DIFLUPREDNATE | up | AGONIST |
| 518 | New clues | PREDNISOLONE PHOSPHORIC ACID | up | AGONIST |
| 519 | New clues | BETAMETHASONE VALERATE | up | AGONIST |
| 520 | New clues | FLUOROMETHOLONE | up | AGONIST |
| 521 | New clues | HYDROCORTISONE BUTYRATE | up | AGONIST |
| 522 | New clues | DESONIDE | up | AGONIST |
| 523 | New clues | DESOXIMETASONE | up | AGONIST |
| 524 | New clues | VAMOROLONE | up | AGONIST |
| 525 | New clues | DEFLAZACORT | up | AGONIST |
| 526 | New clues | FLUOCINONIDE | up | AGONIST |
| 527 | New clues | HYDROCORTISONE ACETATE | up | AGONIST |
| 528 | New clues | FLUNISOLIDE | up | AGONIST |
| 529 | New clues | HYDROCORTISONE HEMISUCCINATE ANHYDROUS | up | AGONIST |
| 530 | New clues | PREDNICARBATE | up | AGONIST |
| 531 | New clues | FLURANDRENOLIDE | up | AGONIST |
| 532 | New clues | CORTISONE ACETATE | up | AGONIST |
| 533 | New clues | BETAMETHASONE ACETATE | up | AGONIST |
| 534 | New clues | ALCLOMETASONE DIPROPIONATE | up | AGONIST |
| 535 | New clues | HALCINONIDE | up | AGONIST |
| 536 | New clues | RIMEXOLONE | up | AGONIST |
| 537 | New clues | DEXAMETHASONE ACETATE | up | AGONIST |
| 538 | New clues | DIFLORASONE DIACETATE | up | AGONIST |
| 539 | New clues | FLUOROMETHOLONE ACETATE | up | AGONIST |
| 540 | New clues | MEDRYSONE | up | AGONIST |
| 541 | New clues | AMCINONIDE | up | AGONIST |
| 542 | New clues | BETAMETHASONE BENZOATE | up | AGONIST |
| 543 | New clues | FLUMETHASONE PIVALATE | up | AGONIST |
| 544 | New clues | FLUPREDNISOLONE | up | AGONIST |
| 545 | New clues | HYDROCORTAMATE | up | AGONIST |
| 546 | New clues | HYDROCORTISONE PROBUTATE | up | AGONIST |
| 547 | New clues | MEPREDNISONE | up | AGONIST |

**sarcoidosis / NR3C1.** Approved medicines turn it **up**: DEXAMETHASONE (AGONIST); DEXAMETHASONE PHOSPHORIC ACID (AGONIST); PREDNISOLONE (AGONIST); PREDNISONE (AGONIST).

| # | tab | card medicine | card direction | card action words |
|---|---|---|---|---|
| 548 | New clues | MIFEPRISTONE | down | ANTAGONIST |
| 549 | New clues | CYPROTERONE ACETATE | down | ANTAGONIST |

**systemic sclerosis / PDGFRB.** Approved medicines turn it **down**: NINTEDANIB (INHIBITOR).

| # | tab | card medicine | card direction | card action words |
|---|---|---|---|---|
| 550 | New clues | BECAPLERMIN | up | AGONIST |

**systemic sclerosis / PDGFRA.** Approved medicines turn it **down**: NINTEDANIB (INHIBITOR).

| # | tab | card medicine | card direction | card action words |
|---|---|---|---|---|
| 551 | New clues | BECAPLERMIN | up | AGONIST |

**systemic sclerosis / FGFR2.** Approved medicines turn it **down**: NINTEDANIB (INHIBITOR).

| # | tab | card medicine | card direction | card action words |
|---|---|---|---|---|
| 552 | New clues | PALIFERMIN | up | AGONIST |
| 553 | New clues | TRAFERMIN | up | AGONIST |

**Behcet disease / KCNQ3.** Approved medicines turn it **up**: EZOGABINE (OPENER).

| # | tab | card medicine | card direction | card action words |
|---|---|---|---|---|
| 554 | New clues | DALFAMPRIDINE | down | BLOCKER |
| 555 | New clues | AMIFAMPRIDINE | down | BLOCKER |
| 556 | New clues | GUANIDINE | down | BLOCKER |
| 557 | New clues | TEDISAMIL | down | BLOCKER |

**Behcet disease / KCNQ2.** Approved medicines turn it **up**: EZOGABINE (OPENER).

| # | tab | card medicine | card direction | card action words |
|---|---|---|---|---|
| 558 | New clues | DALFAMPRIDINE | down | BLOCKER |
| 559 | New clues | AMIFAMPRIDINE | down | BLOCKER |
| 560 | New clues | GUANIDINE | down | BLOCKER |
| 561 | New clues | TEDISAMIL | down | BLOCKER |

**Behcet disease / KCNQ1.** Approved medicines turn it **up**: EZOGABINE (OPENER).

| # | tab | card medicine | card direction | card action words |
|---|---|---|---|---|
| 562 | New clues | DALFAMPRIDINE | down | BLOCKER |
| 563 | New clues | AMIFAMPRIDINE | down | BLOCKER |
| 564 | New clues | GUANIDINE | down | BLOCKER |
| 565 | New clues | TEDISAMIL | down | BLOCKER |

**Behcet disease / KCNQ4.** Approved medicines turn it **up**: EZOGABINE (OPENER).

| # | tab | card medicine | card direction | card action words |
|---|---|---|---|---|
| 566 | New clues | DALFAMPRIDINE | down | BLOCKER |
| 567 | New clues | AMIFAMPRIDINE | down | BLOCKER |
| 568 | New clues | GUANIDINE | down | BLOCKER |
| 569 | New clues | TEDISAMIL | down | BLOCKER |

**Behcet disease / KCNQ5.** Approved medicines turn it **up**: EZOGABINE (OPENER).

| # | tab | card medicine | card direction | card action words |
|---|---|---|---|---|
| 570 | New clues | DALFAMPRIDINE | down | BLOCKER |
| 571 | New clues | AMIFAMPRIDINE | down | BLOCKER |
| 572 | New clues | GUANIDINE | down | BLOCKER |
| 573 | New clues | TEDISAMIL | down | BLOCKER |


### B9. Every both-ways protein

**8 rows.** Also in `both_ways_proteins.csv`.

| disease | protein | Approved medicines turning it UP | Approved medicines turning it DOWN |
|---|---|---|---|
| asthma | CHRM3 | METHACHOLINE (AGONIST) | ACLIDINIUM (ANTAGONIST); GLYCOPYRRONIUM (INHIBITOR, ANTAGONIST); IPRATROPIUM (ANTAGONIST); TIOTROPIUM (ANTAGONIST); UMECLIDINIUM (ANTAGONIST) |
| heart failure | ADRB1 | DOBUTAMINE (AGONIST) | CARVEDILOL (ANTAGONIST); METOPROLOL (ANTAGONIST) |
| heart failure | ADRB2 | DOBUTAMINE (AGONIST) | CARVEDILOL (ANTAGONIST) |
| glaucoma | ADRB1 | DIPIVEFRIN (AGONIST); EPINEPHRINE (AGONIST) | BETAXOLOL (ANTAGONIST); CARTEOLOL (ANTAGONIST); LEVOBUNOLOL (ANTAGONIST); TIMOLOL (ANTAGONIST) |
| glaucoma | ADRB2 | DIPIVEFRIN (AGONIST); EPINEPHRINE (AGONIST) | CARTEOLOL (ANTAGONIST); LEVOBUNOLOL (ANTAGONIST); TIMOLOL (ANTAGONIST) |
| endometriosis | GNRHR | HISTRELIN (AGONIST); NAFARELIN (AGONIST) | ELAGOLIX (ANTAGONIST) |
| breast cancer | ESR1 | ESTRADIOL (AGONIST); ESTROGENS, CONJUGATED (AGONIST); ESTROGENS, ESTERIFIED (AGONIST); QUINESTROL (AGONIST) | FULVESTRANT (ANTAGONIST, DEGRADER) |
| myasthenia gravis | ACHE | PRALIDOXIME (ACTIVATOR) | AMBENONIUM (INHIBITOR); EDROPHONIUM (INHIBITOR); NEOSTIGMINE (INHIBITOR); PYRIDOSTIGMINE (INHIBITOR) |

## Things to know when reading the numbers

These are facts about how the study was run. None of them is a judgement.

- **More requests than expected.** The task guessed about 1,300 requests. The main run sent
  2,728. Moonlight's own code asks every "which medicines?" question twice (a third time if
  the two answers differ), and it also asks for the medicine list of each disease one step up
  and one step down. 890 different proteins were asked about (1,782 requests) and 397
  disease lists (794 requests). The alfuzosin step added 119 more.
- **Open Targets gave two different answers twice.** For 2 of the 1,287 "which medicines?"
  questions (proteins ENSG00000105650 and ENSG00000160752) the first two answers were not
  letter for letter the same, so Moonlight asked a third time and kept the fullest, as its
  rule says. All answers are saved. The medicines named were the same each time.
- **Which diseases.** 23 COMMON, 7 CANCER, 20 RARE: the ones probe P3 had *found* by exact
  name, in P3's order. P3's COMMON set has 30 names but 7 were not found there
  (hypertension, migraine, Crohn's disease, multiple sclerosis, HIV infection, hepatitis B,
  hepatitis C), so they have no id to take and are not here. Acromegaly was already among
  the first 20 RARE, so nothing was added by search.
- **Every pair had at least one action word.** No medicine-protein pair came with an empty
  action list. Every "unknown" in A2 comes from a word that is on neither of Moonlight's lists.
- **Words that are on neither list but contain a listed word.** Moonlight compares whole
  values. So INVERSE AGONIST, PARTIAL AGONIST, ALLOSTERIC ANTAGONIST, ANTISENSE INHIBITOR,
  RNAI INHIBITOR, NEGATIVE ALLOSTERIC MODULATOR and NEGATIVE MODULATOR all give "unknown",
  not up or down. Whether any of them should count as up or down is Kashish's decision with
  a doctor. This report does not say.
- **A pair with one listed word and one unlisted word takes the listed word's direction.**
  Example from the data: FULVESTRANT on ESR1 has ANTAGONIST and DEGRADER and shows "down".
- **Alfuzosin.** The tester's "up" was reproduced, in benign prostatic hyperplasia and
  erectile dysfunction. The word behind it is Open Targets' own `actionType` for alfuzosin,
  AGONIST, on ADRA1A, ADRA1B and ADRA1D. Moonlight's mapping did what it was written to do
  with that word. A3 also lists the other medicines on those three proteins with their
  words, for a doctor to compare.
- **Part B compares cards with the main Approved list only.** Medicines in the two folded
  boxes (narrower disease, wider group) were not used to decide one-way or both-ways. An In
  trials card can also be a medicine that sits in one of those boxes; it is still counted as
  an In trials card.
- **Part B only sees proteins among the top 25 for the disease.** An Approved medicine whose
  proteins are not among them has no path, so it decides nothing. 4 diseases have no
  Approved medicine with an up or down path at all, so they cannot have an opposite card.

## What I did not verify

- **Whether any direction is pharmacologically right.** I cannot tell. Every "up", "down",
  "mixed" and "unknown" in this report is what Moonlight's code makes of Open Targets'
  `actionType` word. Nothing here is labelled right or wrong, including alfuzosin.
- **Whether any opposite pair is a real problem or normal practice.** I cannot tell. Some
  medicines for one disease do turn the same protein opposite ways on purpose (B9 lists the
  proteins where the Approved medicines themselves disagree). The B8 list is a list of what
  the data says, not a list of mistakes. A doctor has to judge it.
- **Which direction each disease needs.** The data does not say, and this study did not try
  to work it out.
- **The live site.** As instructed, the Moonlight site and Gemini were not called. The cards
  here were built by the repo's code at commit 1f0f639 on the day of the run (Open Targets
  data 26.09). If the deployed site runs other code or other data, its cards may differ. I
  did not check what the page draws, or what Gemini's text says about direction.
- **The diseases outside these 50.** The counts describe these 50 only. They are not a
  random sample, so "34 of 50" should not be read as "68% of all diseases".
- **Open Targets' completeness.** A missing mechanism row, a missing medicine, or a short
  answer on both asks would not be noticed here.
- **The A4 doctor table is unreviewed.** No doctor has looked at it yet.
- **The tests.** No code under moonlight/, web/ or tests/ was touched, and the test suite was
  not run, because nothing it tests changed.
