# Study P10: limb-girdle muscular dystrophy

Date: 2026-11-23. Branch `probe-lgmd`, made from `main` at commit 7734f6f.
Open Targets data version 26.09. Read-only study: no Moonlight code and no
test was changed. Everything is under `fixtures/probe_p10/`.

## The short answer

Think of Moonlight as a torch that only lights the first 25 proteins of a
disease, and a doorman who only lets in medicines that are approved for
something. A medicine has to be in the torch light AND get past the doorman.

- Open Targets lists **43** diseases here: the parent (MONDO_0016971) and
  **42** narrower ones.
- Only **3** of the 43 medicine lists have anything on them. **40** are empty.
- Those 3 lists hold **6** entries, which are **5** different medicines
  (ribitol is on two lists). All 6 are in trials. **0** are approved for
  limb-girdle muscular dystrophy.
- Moonlight today shows **1** of the 6 (deflazacort, on the type 2B page,
  in the In trials tab). It hides **5**.
- ClinicalTrials.gov gave **42** trials. **5** of their numbers are on the
  Open Targets lists. **37** are not.

## 1. Open Targets' own medicine lists

Saved in `opentargets/disease_drugs/`, one question file and one answer file
for each of the 43 diseases. Each list was asked for 3 times, and the 3
answers were the same size every time.

| Disease | Medicines on its list |
|---|---|
| MONDO_0016971 limb-girdle muscular dystrophy (the parent) | 4 |
| MONDO_0009676 autosomal recessive limb-girdle muscular dystrophy type 2B | 1 |
| MONDO_0011787 autosomal recessive limb-girdle muscular dystrophy type 2I | 1 |
| the other 40 narrower diseases | 0 each |

The parent has 2 direct children (autosomal dominant, autosomal recessive).
Both of their lists are empty. The other 40 narrower diseases sit under those two.

## 2. Every medicine on any list

"Stage" is the word Open Targets uses. "Trial numbers" are only the ones
Open Targets itself gives. The same table is in `medicines_table.csv`.

| Medicine | Listed under | Stage for that disease | Approved for anything? | Trial numbers given | Protein it acts on | Does Moonlight show it on that page? | Rule that keeps it out |
|---|---|---|---|---|---|---|---|
| Prednisone | parent | PHASE_2 | yes | NCT04054375 | NR3C1 | **no** | top-25 rule. NR3C1 is at place 56 of 2145 for the parent |
| Ribitol | parent | PHASE_3 | no (PHASE_3 is its best) | none (the report is from TTD) | none named | **no** | top-25 rule and approved-elsewhere rule |
| Bidridistrogene xeboparvovec | parent | PHASE_1_2 | no (PHASE_3 is its best) | none (the report is from TTD) | none named | **no** | top-25 rule and approved-elsewhere rule |
| ATYR-1940 | parent | PHASE_1_2 | no (PHASE_1_2 is its best) | NCT02579239, NCT02836418 | none named | **no** | top-25 rule and approved-elsewhere rule |
| Deflazacort | type 2B | PHASE_2_3 | yes | NCT00527228 | NR3C1 | **yes**, In trials tab | none. NR3C1 is protein number 4 on the 2B page |
| Ribitol | type 2I | PHASE_2 | no (PHASE_3 is its best) | NCT04800874 | none named | **no** | top-25 rule and approved-elsewhere rule |

None of the 5 medicines has a withdrawn note, and none has a tablet form in
the database.

Three things I noticed and did not expect:

1. **Three medicines have no protein in the database at all** (ribitol,
   bidridistrogene xeboparvovec, ATYR-1940). Moonlight walks
   disease -> protein -> medicine. A medicine with no protein is like a house
   with no road to it. Making the 25 bigger would never reach these three.
2. **Prednisone is hidden on the parent page but shown on the type 2B page,
   as a New clue.** The 2B page has NR3C1 in its first 25, so it meets
   prednisone. The database does not link prednisone to 2B itself, only to
   the parent, so the 2B page files it under New clues. But it IS in a trial
   for limb-girdle muscular dystrophy (NCT04054375). Today's rules only look
   up and down one step for approvals, not for trials.
3. **Deflazacort's trial is not on the parent page.** It is only listed
   under type 2B, and the parent page does not have NR3C1 in its first 25.
   What real Moonlight shows on the parent page today: Approved 0,
   In trials 0, New clues 1 (ocriplasmin).

## 3. The counts

| What | Count |
|---|---|
| Medicines in trials listed under the parent | **4** |
| Medicines in trials listed under type 2B (MONDO_0009676) | **1** |
| Medicines in trials listed under type 2I (MONDO_0011787) | **1** |
| Medicines in trials listed under each of the other 40 narrower diseases | **0** |
| All entries in trials | 6 entries, 5 different medicines |
| Hidden by the approved-elsewhere rule | **4** entries, 3 different medicines (ribitol twice, bidridistrogene xeboparvovec, ATYR-1940) |
| Hidden by the top-25 rule | **5** entries, 4 different medicines (the same 4 entries, and prednisone) |
| ... of those, no protein named at all | 4 entries, 3 medicines |
| ... of those, protein named but outside the first 25 | 1 entry (prednisone, NR3C1 at place 56) |
| Hidden by both rules at once | 4 entries, 3 medicines |
| Hidden by the top-25 rule only | 1 entry (prednisone) |
| Hidden by the approved-elsewhere rule only | 0 |
| Shown | 1 entry (deflazacort on the 2B page) |

I counted the two rules separately, so the 4 and the 5 overlap. 4 + 5 is not
9 hidden medicines: 4 entries are stopped by both rules. In the real code the
top-25 step comes first, so those 4 are never even met.

NR3C1 for the parent: place 56, score 0.2137. The protein at place 25 has
score 0.7668.

## 4. ClinicalTrials.gov

Search: condition "limb-girdle muscular dystrophy" (in quote marks), study
type interventional. Saved in `clinicaltrials/` exactly as it came, with the
status, phase, conditions and interventions as written. I asked only for
those parts, so no person's contact details are saved.

- Trials returned: **42** (all 42 interventional).
- Status: COMPLETED 18, ACTIVE_NOT_RECRUITING 8, TERMINATED 5, WITHDRAWN 4,
  UNKNOWN 3, NOT_YET_RECRUITING 2, RECRUITING 1, ENROLLING_BY_INVITATION 1.
- Phase: PHASE1 13, NA 8, PHASE1/PHASE2 8, PHASE3 8, PHASE2 3, PHASE2/PHASE3 2.
- Kinds of intervention (a trial can have more than one): DRUG 20,
  BIOLOGICAL 9, GENETIC 7, OTHER 6, BEHAVIORAL 3, DEVICE 3, COMBINATION_PRODUCT 1.
- Open Targets gives **5** trial numbers on its lists. All 5 are among the 42.
- So **5 of 42** ClinicalTrials.gov trials are on an Open Targets list, and
  **37 are not**.

Be careful with the 42. The search is wider than the words:

| Group | How the trial matched | Trials | On an Open Targets list |
|---|---|---|---|
| A | "limb girdle" or "LGMD" is in the conditions as written | 32 | 5 |
| B | only in the title or keywords | 3 | 0 |
| C | only in a label ClinicalTrials.gov added by itself | 7 | 0 |

Group C looks wrong to me: its conditions are written as migraine, type 2
diabetes, lymphoma, kidney failure, a cancer vaccine, and two heart trials.
I saved them as they came and did not remove them. If you only count group A,
it is **5 of 32**. Of the 14 group A trials with a DRUG intervention, 4 are on
an Open Targets list.

All 42 trials (group, then number). Also in `trials_table.csv`.

| Trial | Status | Phase | Conditions as written | Interventions as written | Group | On Open Targets list |
|---|---|---|---|---|---|---|
| NCT00104078 | COMPLETED | PHASE1/PHASE2 | Becker Muscular Dystrophy / Facioscapulohumeral Muscular Dystrophy / Limb-Girdle Muscular Dystrophy | DRUG: MYO-029 | A | no |
| NCT00527228 | COMPLETED | PHASE2/PHASE3 | LGMD2B / Miyoshi Myopathy / Dysferlinopathy | DRUG: deflazacort / DRUG: placebo | A | DEFLAZACORT @ MONDO_0009676 |
| NCT00873782 | COMPLETED | PHASE1 | Muscular Dystrophies / Duchenne Muscular Dystrophy / Becker Muscular Dystrophy / Limb-Girdle Muscular Dystrophy | OTHER: Retrograde high pressure transvenous perfusion with normal saline | A | no |
| NCT01126697 | COMPLETED | PHASE2/PHASE3 | Duchenne Muscular Dystrophy / Becker Muscular Dystrophy / Limb Girdle Muscular Dystrophy | DRUG: Coenzyme Q10 and Lisinopril | A | no |
| NCT01344798 | COMPLETED | PHASE1 | Limb Girdle Muscular Dystrophy Type 2C / Gamma-sarcoglycanopathy | BIOLOGICAL: AAV1-gamma-sarcoglycan vector injection | A | no |
| NCT01976091 | COMPLETED | PHASE1/PHASE2 | Limb-Girdle Muscular Dystrophy, Type 2D | GENETIC: SRP-9004 | A | no |
| NCT02050776 | WITHDRAWN | PHASE1 | Limb Girdle Muscular Dystrophy | BIOLOGICAL: Autologous bone marrow mononuclear cell transplantation | A | no |
| NCT02245711 | WITHDRAWN | PHASE1 | Limb Girdle Muscular Dystrophy | BIOLOGICAL: Stem Cell | A | no |
| NCT02579239 | COMPLETED | PHASE1/PHASE2 | Limb-Girdle Muscular Dystrophies / Facioscapulohumeral Muscular Dystrophy | BIOLOGICAL: ATYR1940 / BIOLOGICAL: Placebo | A | ATYR-1940 @ MONDO_0016971 |
| NCT02836418 | COMPLETED | PHASE1/PHASE2 | Facioscapulohumeral Muscular Dystrophy / Limb Girdle Muscular Dystrophy | DRUG: ATYR1940 | A | ATYR-1940 @ MONDO_0016971 |
| NCT02841267 | COMPLETED | PHASE1/PHASE2 | LGMD2I | DRUG: PF 06252616 | A | no |
| NCT03127241 | COMPLETED | NA | Muscular Dystrophies / Muscular Dystrophy, Duchenne / Muscular Dystrophy, Becker / Muscular Dystrophy, Limb-Girdle Type 2 | DEVICE: Assistive device (Armon Ayura) test / DEVICE: Assistive device (Jaeco Wrex) test | A | no |
| NCT03652259 | TERMINATED | PHASE1/PHASE2 | Limb-Girdle Muscular Dystrophy, Type 2E | GENETIC: SRP-9003 | A | no |
| NCT03783923 | TERMINATED | PHASE3 | Limb-Girdle Muscular Dystrophy | DRUG: Deflazacort | A | no |
| NCT04054375 | COMPLETED | PHASE2 | Limb-girdle Muscular Dystrophy / Becker Muscular Dystrophy | DRUG: Prednisone | A | PREDNISONE @ MONDO_0016971 |
| NCT04800874 | ACTIVE_NOT_RECRUITING | PHASE2 | LGMD2I | DRUG: BBP-418 | A | RIBITOL @ MONDO_0011787 |
| NCT05224505 | ACTIVE_NOT_RECRUITING | PHASE1 | LGMDR9 | BIOLOGICAL: ATA-100 (AAV9 encoding FKRP gene) | A | no |
| NCT05230459 | ACTIVE_NOT_RECRUITING | PHASE1/PHASE2 | Limb Girdle Muscular Dystrophy / Limb-Girdle Muscular Dystrophy Type 2 / LGMD2I / Muscular Dystrophy / LGMD2 / LGMD / FKRP / FKRP Mutation / Fukutin Related Protein | GENETIC: AB-1003 dose level 1 / GENETIC: AB-1003 dose level 2 / DRUG: Placebo | A | no |
| NCT05409079 | UNKNOWN | NA | Muscular Dystrophies / Spinal Muscular Atrophy / Duchenne Muscular Dystrophy / Limb Girdle Muscular Dystrophy / FSHD / Cerebral Palsy / Becker Muscular Dystrophy | DEVICE: Abilitech Assist | A | no |
| NCT05588401 | UNKNOWN | PHASE1/PHASE2 | LGMD | BIOLOGICAL: GenPHSat injection (Safety) / BIOLOGICAL: GenPHSat injection (Efficacy) / OTHER: Muscle Biopsy (Safety) | A | no |
| NCT05775848 | ACTIVE_NOT_RECRUITING | PHASE3 | Limb-Girdle Muscular Dystrophy Type 2I (LGMD2I) | DRUG: BBP-418 (ribitol) / OTHER: Placebo | A | no |
| NCT05876780 | ACTIVE_NOT_RECRUITING | PHASE1 | Limb Girdle Muscular Dystrophy | GENETIC: SRP-9003 | A | no |
| NCT05906251 | TERMINATED | PHASE1 | Limb Girdle Muscular Dystrophy | GENETIC: SRP-6004 | A | no |
| NCT05973630 | ACTIVE_NOT_RECRUITING | PHASE1 | LGMD2C | BIOLOGICAL: ATA-200 | A | no |
| NCT06246513 | ACTIVE_NOT_RECRUITING | PHASE3 | Limb-girdle Muscular Dystrophy | BIOLOGICAL: SRP-9003 / DRUG: Glucocorticoid | A | no |
| NCT06378203 | UNKNOWN | NA | Muscular Dystrophies / Limb Girdle Muscular Dystrophy / Facio-Scapulo-Humeral Dystrophy / Becker Muscular Dystrophy | OTHER: tele-rehabilitation system with virtual reality Home Kit - Virtual Reality Rehabilitation System (VRRS KHYMEIA) | A | no |
| NCT06747273 | TERMINATED | PHASE1 | Limb Girdle Muscular Dystrophy / Limb Girdle Muscular Dystrophy Type 2D/R3 | DRUG: SRP-9004 | A | no |
| NCT06952686 | WITHDRAWN | PHASE3 | Muscular Dystrophies, Limb-Girdle | BIOLOGICAL: SRP-9005 / DRUG: Corticosteroid | A | no |
| NCT07072676 | ENROLLING_BY_INVITATION | NA | Inclusion Body Myositis / Myotonic Dystrophy 1 / Myotonic Dystrophy 2 / Facio-Scapulo-Humeral Dystrophy / Limb Girdle Muscular Dystrophies / Pompe Disease (Infantile-Onset) / Myasthaenia Gravis / Lambert Eaton (LEMS) / Spinal Muscular Atrophy (SMA) / Guillain Barré Syndrome / Chronic Inflammatory Demyelinating Polyneuropathy / Friedreich Ataxia / Hereditary Motor and Sensory Neuropathies | DEVICE: Assistive gait devices combined with physiotherapy | A | no |
| NCT07678775 | ACTIVE_NOT_RECRUITING | PHASE3 | Limb-Girdle Muscular Dystrophy Type 2I (LGMD2I) | DRUG: BBP-418 (ribitol) | A | no |
| NCT07711730 | RECRUITING | NA | Limb-Girdle Muscular Dystrophy / Social Competence / Self Esteem / Health Related Quality of Life / Social Skills | BEHAVIORAL: Neuro-psychosocial teleassistance program | A | no |
| NCT07874516 | NOT_YET_RECRUITING | PHASE1 | Limb Girdle Muscular Dystrophy Type 2D/R3 | GENETIC: BBM-L101 Injection | A | no |
| NCT00494195 | COMPLETED | PHASE1 | Muscular Dystrophies | GENETIC: rAAV1.tMCK.human-alpha-sarcoglycan- First cohort / GENETIC: Genetic: rAAV1.tMCK.human-alpha-sarcoglycan- Second cohort | B | no |
| NCT02710500 | COMPLETED | PHASE1 | Dysferlinopathy | DRUG: rAAVrh74.MHCK7.DYSF.DV | B | no |
| NCT02810028 | COMPLETED | NA | Muscle Diseases | BEHAVIORAL: Acceptance and Commitment Therapy (ACT) | B | no |
| NCT00786019 | COMPLETED | NA | Type 2 Diabetes | BEHAVIORAL: Exercise program / DRUG: Ascorbic Acid (Vitamin C) | C | no |
| NCT01035983 | COMPLETED | PHASE3 | Migraine | DRUG: Frovatriptan 2.5 mg | C | no |
| NCT02285062 | COMPLETED | PHASE3 | Lymphoma, Large B-Cell, Diffuse | DRUG: lenalidomide / DRUG: Placebo / DRUG: Rituximab / DRUG: Cyclophosphamide / DRUG: Doxorubicin / DRUG: prednisone / DRUG: vincristine | C | no |
| NCT03439514 | TERMINATED | PHASE3 | Dilated Cardiomyopathy / Lamin A/C Gene Mutation | DRUG: ARRY-371797 (PF-07265803) / OTHER: Placebo | C | no |
| NCT05286281 | COMPLETED | PHASE1 | Healthy | DRUG: PF-07265803 | C | no |
| NCT05952388 | WITHDRAWN | NA | End Stage Renal Disease | OTHER: Behavioral Patient care | C | no |
| NCT07859592 | NOT_YET_RECRUITING | PHASE2 | Type and Grade of Toxicities, Demographic and Background Characteristics / Advanced, Metastatic, Recurrent Adenocarcinoma and Malignant Solid Neoplasm | COMBINATION_PRODUCT: LabVax 3(22)-23 and GM-CSF (adjuvant) in combination with pembrolizumab | C | no |

## Recount

```
python3 fixtures/probe_p10/recount.py
```

It reads only the saved files, never the network, and imports nothing from
Moonlight. It prints every number above and rewrites the two tables. Its
full output on 2026-11-23:

```
Open Targets data version 26.09
Diseases looked at: 43 = 1 parent + 42 narrower
Direct children of the parent: 2

1. MEDICINE LISTS
   MONDO_0016971  limb-girdle muscular dystrophy: 4
   MONDO_0009676  autosomal recessive limb-girdle muscular dystrophy type 2B: 1
   MONDO_0011787  autosomal recessive limb-girdle muscular dystrophy type 2I: 1
   lists with no medicine at all: 40 of 43

2. EVERY MEDICINE ON ANY LIST
   BIDRIDISTROGENE XEBOPARVOVEC (CHEMBL4650240, Gene) on MONDO_0016971
      stage for this disease: PHASE_1_2; strongest stage anywhere: PHASE_3; approved for anything: no
      trial numbers: none given; reports: TTD:d3rt4a/limb girdle muscular dystrophy:PHASE_1_2, USAN:bidridistrogene xeboparvovec:UNKNOWN
      acts on: no protein named; the database names no protein for this medicine at all
      Moonlight shows it on this disease's page: no (top-25 rule and approved-elsewhere rule)
   PREDNISONE (CHEMBL635, Small molecule) on MONDO_0016971
      stage for this disease: PHASE_2; strongest stage anywhere: APPROVAL; approved for anything: yes
      trial numbers: NCT04054375; reports: ClinicalTrials.gov:nct04054375:PHASE_2
      acts on: NR3C1; NR3C1 is at place 56 of 2145
      Moonlight shows it on this disease's page: no (top-25 rule)
   ATYR-1940 (CHEMBL4297550, Unknown) on MONDO_0016971
      stage for this disease: PHASE_1_2; strongest stage anywhere: PHASE_1_2; approved for anything: no
      trial numbers: NCT02579239, NCT02836418; reports: ClinicalTrials.gov:nct02579239:PHASE_1_2, ClinicalTrials.gov:nct02836418:PHASE_1_2
      acts on: no protein named; the database names no protein for this medicine at all
      Moonlight shows it on this disease's page: no (top-25 rule and approved-elsewhere rule)
   RIBITOL (CHEMBL3137744, Small molecule) on MONDO_0016971
      stage for this disease: PHASE_3; strongest stage anywhere: PHASE_3; approved for anything: no
      trial numbers: none given; reports: TTD:d5lzo9/limb-girdle muscular dystrophy:PHASE_3, USAN:ribitol:UNKNOWN
      acts on: no protein named; the database names no protein for this medicine at all
      Moonlight shows it on this disease's page: no (top-25 rule and approved-elsewhere rule)
   DEFLAZACORT (CHEMBL1201891, Small molecule) on MONDO_0009676
      stage for this disease: PHASE_2_3; strongest stage anywhere: APPROVAL; approved for anything: yes
      trial numbers: NCT00527228; reports: ClinicalTrials.gov:nct00527228:PHASE_2_3
      acts on: NR3C1; met through NR3C1
      Moonlight shows it on this disease's page: yes: In trials tab
   RIBITOL (CHEMBL3137744, Small molecule) on MONDO_0011787
      stage for this disease: PHASE_2; strongest stage anywhere: PHASE_3; approved for anything: no
      trial numbers: NCT04800874; reports: ClinicalTrials.gov:nct04800874:PHASE_2
      acts on: no protein named; the database names no protein for this medicine at all
      Moonlight shows it on this disease's page: no (top-25 rule and approved-elsewhere rule)

3. COUNTS
   list entries (medicine on a list): 6; different medicines: 5
   entries whose stage is a trial phase: 6; approved for that disease: 0
   in trials, listed under the parent: 4
   in trials, listed under MONDO_0009676 autosomal recessive limb-girdle muscular dystrophy type 2B: 1
   in trials, listed under MONDO_0011787 autosomal recessive limb-girdle muscular dystrophy type 2I: 1
   narrower diseases with 0 in trials: 40
   hidden by the approved-elsewhere rule: 4 entries, 3 different medicines (ATYR-1940, BIDRIDISTROGENE XEBOPARVOVEC, RIBITOL)
   hidden by the top-25 rule: 5 entries, 4 different medicines (ATYR-1940, BIDRIDISTROGENE XEBOPARVOVEC, PREDNISONE, RIBITOL)
      of those, no protein named at all: 4 entries, 3 different medicines (ATYR-1940, BIDRIDISTROGENE XEBOPARVOVEC, RIBITOL)
      of those, protein named but outside the 25: 1 entries, 1 different medicines (PREDNISONE)
   hidden by both rules at once: 4 entries, 3 different medicines (ATYR-1940, BIDRIDISTROGENE XEBOPARVOVEC, RIBITOL)
   hidden by the top-25 rule only: 1 entries, 1 different medicines (PREDNISONE)
   hidden by the approved-elsewhere rule only: 0 entries, 0 different medicines (none)
   shown: 1 entries, 1 different medicines (DEFLAZACORT)
   NR3C1 for the parent: place 56 of 2145, score 0.2137; place 25 has score 0.7668

   Extra: the same medicines on the OTHER pages of this family (met through the 25 proteins)
      DEFLAZACORT: met on 1 of 43 pages; being_studied on 1 (MONDO_0009676)
      RIBITOL: met on 0 of 43 pages; never met
      ATYR-1940: met on 0 of 43 pages; never met
      BIDRIDISTROGENE XEBOPARVOVEC: met on 0 of 43 pages; never met
      PREDNISONE: met on 1 of 43 pages; new_clue on 1 (MONDO_0009676)
      pages with NR3C1 in the first 25: 1 (MONDO_0009676)
      recount agrees with moonlight_live_run.json for every entry on the pages saved there

4. CLINICALTRIALS.GOV
   trials returned: 42 (ClinicalTrials.gov's own total: 42); all interventional: True
   status: COMPLETED 18, ACTIVE_NOT_RECRUITING 8, TERMINATED 5, WITHDRAWN 4, UNKNOWN 3, NOT_YET_RECRUITING 2, RECRUITING 1, ENROLLING_BY_INVITATION 1
   phase: PHASE1 13, NA 8, PHASE1/PHASE2 8, PHASE3 8, PHASE2 3, PHASE2/PHASE3 2
   how each one matched:
      A: in the conditions as written: 32
      B: only in the title or keywords: 3
      C: only in a label ClinicalTrials.gov added itself: 7
   kinds of intervention (a trial can have more than one): DRUG 20, BIOLOGICAL 9, GENETIC 7, OTHER 6, BEHAVIORAL 3, DEVICE 3, COMBINATION_PRODUCT 1
   trial numbers on the Open Targets lists: 5 (NCT00527228, NCT02579239, NCT02836418, NCT04054375, NCT04800874)
   of the 42 ClinicalTrials.gov trials, on an Open Targets list: 5; not on any: 37
   Open Targets trial numbers missing from the ClinicalTrials.gov answer: none
   group A: 32 trials, 5 on an Open Targets list
   group B: 3 trials, 0 on an Open Targets list
   group C: 7 trials, 0 on an Open Targets list
   group A trials with a DRUG intervention: 14, 4 on an Open Targets list
```

## What is in this folder

- `opentargets/family/` the parent, its children and its 42 narrower diseases.
- `opentargets/disease_drugs/` the 43 medicine lists (question and answer).
- `opentargets/top_targets/` the first 25 proteins of each of the 43
  diseases, and `MONDO_0016971.all` with all 2145 for the parent.
- `opentargets/target_drugs/` the medicines acting on each of the 191
  proteins, asked with Moonlight's own question, word for word.
- `opentargets/drug/` the 5 medicines' own records.
- `clinicaltrials/` the search and its one page of 42 trials.
- `moonlight_live_run.json` what Moonlight's real engine answered for 5 of
  the pages on the day. This is worked out, not an Open Targets answer.
- `fetch_probe.py` how the files were fetched. `recount.py` the recount.
- `medicines_table.csv`, `trials_table.csv` written by the recount.

## What I ran

```
python3 fixtures/probe_p10/fetch_probe.py     # fetched and saved everything
43 diseases, 5 medicine ids, 191 proteins
ClinicalTrials.gov page 1 42 of 42
python3 fixtures/probe_p10/recount.py         # output above
```

I also ran Moonlight's own engine functions (fetch_disease, fetch_targets,
find_clues, fetch_approved, fetch_withdrawn, fetch_neighbours,
sort_into_tabs, leave_out) live for 5 pages: the parent, its 2 children,
type 2B and type 2I. The saved results went to a scratch folder, not the repo.
The recount agrees with it for all 6 entries.

## What I did not verify

- **One day only.** Everything is a snapshot of 2026-11-23, data version 26.09.
- **The web page.** I did not open Moonlight in a browser. FastAPI is not
  installed in this session, so I ran the engine's functions, which is what
  the page calls, but not the page itself.
- **The tests.** `python3 -m pytest` cannot start here (24 collection
  errors, "No module named 'fastapi'"). That is the session, not this
  branch: no code or test changed.
- **38 of the 43 pages were not run in real Moonlight.** For those the
  recount applied the rules to the saved files. Their lists are all empty,
  so no number above depends on them, except "prednisone is met on 1 of 43 pages".
- **Short answers.** Open Targets sometimes gives a short answer. I asked
  for each list 3 times and each protein twice and saw no difference, but I
  cannot prove the 40 empty lists are truly empty.
- **Whether a trial is about the same medicine.** I matched by trial number
  only. I did not match medicine names. Example: ClinicalTrials.gov has 3
  trials of "SRP-9003" (NCT03652259, NCT05876780, NCT06246513). Open
  Targets' report for bidridistrogene xeboparvovec is titled "Srp-9003", but
  it gives no trial number, so those 3 count as "not on a list". I did not
  check they are the same thing.
- **Why 37 trials are not on the lists.** I only counted. Many are gene
  therapies, devices and exercise programmes, but I did not check each one.
- **Other ways to search.** I searched one wording. I did not search "LGMD",
  the type names (2A, 2B, R9...), or names like dysferlinopathy or
  sarcoglycanopathy, and no trial register other than ClinicalTrials.gov.
- **ClinicalTrials.gov's own labels.** I did not find out why it labels a
  migraine trial with a limb-girdle type. I only saw that it does.
- **The disease tree.** The 42 narrower diseases are Open Targets'
  "descendants" list, taken as given. It includes some surprising names
  (epidermolysis bullosa simplex 5B with muscular dystrophy, myofibrillar
  myopathy 3, Emery-Dreifuss muscular dystrophy 2). I did not question it.
- **No medical checking.** Nothing here says any medicine works or is safe.

## Two things to know

- CLAUDE.md says Moonlight uses only two outside data sources. This study
  asked for ClinicalTrials.gov, so I used it for this study only. Nothing in
  Moonlight calls it.
- `python3 scripts/check_fixtures.py` counts every non-JSON file in
  `fixtures/` as "broken". It already listed 4 README files on main. It now
  also lists this folder's 5 non-JSON files (this report, the 2 scripts,
  the 2 tables). It still exits without an error.

## Five plain sentences for Kashish

1. Open Targets has 43 drawers for limb-girdle muscular dystrophy, and only 3 of them have any medicine cards inside: 6 cards, 5 different medicines, all in trials and none approved for it.
2. Moonlight shows just 1 of those 6 cards, deflazacort on the type 2B page, and hides the other 5.
3. Three medicines (ribitol, bidridistrogene xeboparvovec, ATYR-1940) are stopped twice: they are not approved for anything, and the database names no protein for them, so there is no road from the disease to them at all.
4. Prednisone is stopped only by the torch: its protein NR3C1 is at place 56 for the parent and the torch stops at 25, yet on the type 2B page the same prednisone shows up as a New clue even though it is already in a trial for limb-girdle muscular dystrophy.
5. ClinicalTrials.gov has 42 trials for this search and only 5 of their numbers are on the Open Targets lists, so most of what is being tried for this disease (lots of it gene therapy) is something Moonlight cannot see today.
