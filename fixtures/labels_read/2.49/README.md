# Ticket 2.49: four cards from public feedback. Look first, fix only with existing rules

Read on 2026-11-25 (Open Targets data 26.09). Nothing in moonlight/ was changed:
no list entry, no code, no test. For every card the existing lists and rules
either do not cover it, or the answer is not what the ticket expected (below).
Nothing here is a clue, a link or a claim made by Moonlight: it is what a person
read, written down.

## One line per card

card | what the page shows now | what the source says | change made or "none"
---|---|---|---
1. ADPKD (MONDO_0004691), vasopressin agonists | Desmopressin, Vasopressin, Argipressin Tannate, Lypressin: in the API's `new_clues` AND in `opposite_way_box`; the page puts each of them once, in the folded opposite-way box. Terlipressin: main New clues (rank 2), no opposite line. Tolvaptan: Approved. | Open Targets: AVPR2 is linked to ADPKD (score 58). Desmopressin and its relatives are AGONISTs of AVPR2 (direction up); tolvaptan is the approved medicine, direction down; terlipressin's action type is "BINDING AGENT" (direction unknown). | none (the cause is engine code and ticket 2.28's design, not a list)
1b. ADPKD, "In trials" cards with a completed study in another disease | Pasireotide, Everolimus, Sirolimus and Lisinopril Anhydrous show a link to a COMPLETED trial in a different disease (list below). Somatostatin's link is a trial of status UNKNOWN in a different disease. | ClinicalTrials.gov, read by hand. | none (report only)
2. Fluoxetine (CHEMBL41), bipolar II disorder (EFO_0009964) | Fluoxetine sits in the folded box "Approved for a wider group (18)". Source record: the PAR olanzapine-and-fluoxetine label. | None of the 254 current fluoxetine labels on DailyMed (251 fluoxetine alone, 3 olanzapine-and-fluoxetine) names bipolar II. The combination labels name only "Bipolar I Disorder". Fluoxetine-alone labels name it only to say monotherapy is not indicated for it. | none (nothing to confirm; decision for tonight)
3. Tranexamic Acid (CHEMBL877), hereditary angioedema (MONDO_0019623) | In trials, Phase 3, Source record NCT00670345 (prostatectomy study). | HAE's own list holds tranexamic acid with one trial, NCT00500656 (Phase 3, condition "Hereditary Angioedema", completed): icatibant versus oral tranexamic acid. The prostatectomy study is the link the card shows. | none (the condition "every linked trial is for a different condition" is not met; left_out.json would also not take the card off In trials)
4. Masitinib (CHEMBL1908391) | "Being studied" (main In trials list) on 8 diseases. Also in the folded "more in trials" box on 13 more diseases, and on the Approved tab for "neoplasm". | See the table under card 4. | none (no rule yet for ended trials)

## Card 1. ADPKD and the vasopressin medicines

Live page answer saved: `page_answers/MONDO_0004691.clues.json`. The disease's
own list, asked the way fetch.py asks it: `disease_drugs/MONDO_0004691.response.json`.

Where each card shows (position on the API's New clues list):

medicine | id | position | direction on AVPR2 | opposite-way line | where the page shows it
---|---|---|---|---|---
Desmopressin | CHEMBL1429 | 1 | up (agonist) | yes | folded opposite-way box
Terlipressin | CHEMBL2135460 | 2 | unknown (BINDING AGENT) | no | main New clues
Vasopressin | CHEMBL373742 | 3 | up | yes | folded opposite-way box
Conivaptan | CHEMBL1755 | 4 | down | no (same way as tolvaptan) | main New clues
Argipressin Tannate | CHEMBL2108986 | 5 | up | yes | folded opposite-way box
Lypressin | CHEMBL1200690 | 6 | up | yes | folded opposite-way box
Mozavaptan | CHEMBL420762 | 7 | down | no (same way as tolvaptan) | main New clues

Why, in plain order:

1. Open Targets links the protein AVPR2 to ADPKD (score 58, evidence "animal_model").
   Any approved medicine that acts on AVPR2 and is not on ADPKD's own list is a new clue.
   That includes the agonists. The rule does not know that "up" is the wrong way for this disease.
2. Tolvaptan is the only card on the Approved tab. It turns AVPR2 down. Ticket 3.7
   (`engine.one_way_proteins`) says AVPR2 is one-way "down" because the Approved list is all down.
   `engine.opposite_way` then gives every new clue that turns AVPR2 up the line
   "Opposite way to the approved medicines for this disease.", and `engine.opposite_box`
   names those clues. Ticket 2.28 says nothing is removed: the API keeps them in `new_clues`
   and lists their ids in `opposite_way_box`. The page (`aboveAndBox` in web/index.html)
   then draws each of them once, in the folded box under the New clues list.
   So "both in New clues and in the opposite-way box" is true of the API answer and of
   the tab (the box is part of the tab), not of the number of cards drawn.
3. Terlipressin is not in the box because Open Targets calls what it does to AVPR2 a
   "BINDING AGENT" (checked live, CHEMBL2135460), and `fetch.py` turns that into direction
   "unknown". Only up against down counts.
4. The cause is engine code and the 2.28 design (boxed, never removed). No list changes it.
   `left_out.json` could take these four out of New clues, but: (a) its entries hold exactly
   medicine, disease and date, so the reason cannot be written down; (b) the line it adds
   says "N medicines left out because they push the wrong way for this disease", a decision
   about ticket 2.28's box that is Kashish's. Changed nothing.

"In trials" cards whose trial link is a COMPLETED study in a different disease.
Read from ClinicalTrials.gov on 2026-11-25 (`registry/trial_reads.json`). These are
the cards on the main In trials list. The card's phase is the one Open Targets gives
for the disease; the register's phase for the linked study can differ.

card | link | study title | status | study conditions
---|---|---|---|---
Pasireotide (CHEMBL3349607), card says Phase 2 | https://clinicaltrials.gov/study/NCT02527993 | Treatment of Hypoglycemia Following Gastric Bypass Surgery | COMPLETED | Hypoglycemia, Obesity, Surgery
Everolimus (CHEMBL1908360), card says Phase 3 | https://clinicaltrials.gov/study/NCT00154297 | Efficacy and Safety of Early Versus Delayed Administration of Everolimus in de Novo Renal Transplant Patients | COMPLETED | Renal Transplantation
Sirolimus (CHEMBL413), card says Phase 3 | https://clinicaltrials.gov/study/NCT00044720 | Study Evaluating Sirolimus in End Stage Renal Disease in High Risk Kidney Transplant Recipients | COMPLETED | Chronic Kidney Failure, Graft vs Host Disease, Kidney Transplantation
Lisinopril Anhydrous (CHEMBL1237), card says Phase 3 | https://clinicaltrials.gov/study/NCT00000542 | Antihypertensive and Lipid-Lowering Treatment to Prevent Heart Attack Trial (ALLHAT) | COMPLETED | Cardiovascular Diseases, Coronary Disease, Diabetes Mellitus, Heart Diseases, Hypercholesterolemia, Hypertension, Myocardial Infarction, Myocardial Ischemia, Heart Failure

Not "completed" but also a different disease: Somatostatin (CHEMBL1823872), card says Phase 3,
https://clinicaltrials.gov/study/NCT00863837 "Prevention of Esophageal Variceal Rebleeding",
status UNKNOWN, condition "Esophageal Variceal Rebleeding".

In every one of these five, ADPKD's own list holds a different trial for the same
medicine whose conditions name ADPKD or polycystic kidney disease (pasireotide
NCT01670110, everolimus NCT02134899 and NCT01009957, sirolimus NCT00346918, NCT02055079,
NCT00920309, NCT01223755, NCT01680250, NCT00491517, NCT00286156 and NCT01632605, lisinopril
NCT00283686 and NCT01885559, somatostatin NCT00309283; all read in registry/trial_reads.json),
but the link the card shows is not one of them. The choice of the link is made in engine code.

Other main-list cards whose link is not a trial at all: Lanreotide (a PMDA page), Octreotide (an
EMA page, Mycapssa), Telmisartan (an EMA page), Metformin (an EMA page, Avandamet).
In the two folded boxes every link that is a study names ADPKD or polycystic kidney
disease among its conditions (Rotigotine: "Kidney Diseases"; Venglustat:
"Congenital Cystic Kidney Disease"); RGLS-4326's link is a TTD page. Two oddities, not
wrong disease: Sodium Chloride's link is the lanreotide study NCT02127437, and Phenylbutanoic
Acid's is the probenecid study NCT05190744 (conditions ADPKD and nephrogenic diabetes insipidus).

## Card 2. Fluoxetine and bipolar II disorder

Live page answer saved: `page_answers/EFO_0009964.clues.json`.

- Where it shows: the folded box "Approved for a wider group (18)", under the Approved tab
  (not on the main Approved list, not a new clue).
- The exact "wider group" sentence on the card:
  `Not listed as approved for this exact disease. Approved for bipolar disorder, a wider group the database puts this disease in.`
  (The same sentence is on all 18 cards of that box.)
- Source record on the card:
  https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=2f6ceda3-3edc-4427-98a6-23e3c930c44d
  = OLANZAPINE AND FLUOXETINE capsules (PAR Health USA), label dated 2025-12-10.
  Its INDICATIONS AND USAGE is saved word for word in `labels/olanzapine-and-fluoxetine-par.txt`.
  It names "Acute depressive episodes in Bipolar I Disorder" and "Treatment resistant depression".
  Not bipolar II, and not "bipolar disorder" in general.
- Fluoxetine alone: DailyMed lists 254 current labels for the name "fluoxetine" on 2026-11-25
  (`labels/fluoxetine_all_254_scan.tsv`: id, title, date, bipolar sentences). 251 are fluoxetine alone
  (Prozac, generic capsules, tablets, liquids; Reconcile and a kit included), 3 are olanzapine-and-fluoxetine.
  The INDICATIONS AND USAGE of every one was read by a short script and searched for
  "bipolar II" / "bipolar 2" / "bipolar type II": 0 hits. 56 of the 251 do not say "bipolar" at all.
  The others say it only as: "PROZAC and Olanzapine in Combination is indicated for ... depressive
  episodes associated with Bipolar I Disorder" and "monotherapy is not indicated for the treatment of
  depressive episodes associated with Bipolar I Disorder". Prozac's section is saved in
  `labels/prozac-fluoxetine.txt`.
- Answer to the ticket's question: no current fluoxetine-alone label names bipolar II, so nothing goes in
  confirmed.json. Even the combination names only bipolar I. Changed nothing. Decision for tonight:
  the card's Source record is a label that does not name bipolar II (nor, strictly, bipolar disorder
  as a whole), and the box sentence says "Approved for bipolar disorder".
  Note: this is a wider-group card, not an Approved card, so confirmed.json (which is for the
  main Approved list) would not have moved it anyway.

## Card 3. Tranexamic acid and hereditary angioedema

Live page answer saved: `page_answers/MONDO_0019623.clues.json`. The disease's own list:
`disease_drugs/MONDO_0019623.response.json`.

- Where it shows: the main In trials list ("being_studied"), Phase 3, protein PLG (direction down),
  Source record https://clinicaltrials.gov/study/NCT00670345. Not in a folded box.
- That link: "Tranexamic Acid in Urologic Surgery", COMPLETED, register phase PHASE4, conditions
  "Bleeding", "Prostatectomy". Official title: "Efficacy of Tranexamic Acid in Reducing Perioperative
  Bleeding in Patients Undergoing Radical Prostatectomy. A Randomized Controlled Double-blind Study."
- HAE's own list (Open Targets, asked live) holds tranexamic acid, stage PHASE_3, with exactly one report:
  https://clinicaltrials.gov/study/NCT00500656, "Subcutaneous Treatment With Icatibant for Acute Attacks of
  Hereditary Angioedema (HAE)", COMPLETED, PHASE3, condition "Hereditary Angioedema". Its official title:
  "Randomised Double Blind, Controlled, Parallel Group, Multicentre Study of a Subcutaneous Formulation of
  Icatibant Versus Oral Tranexamic Acid for the Treatment of Hereditary Angioedema (HAE)".
  Tranexamic acid is the comparison arm there, not the medicine being tested.
- So the Phase 3 on the card comes from an HAE study and the link beside it is a prostatectomy study.
  Not every linked trial is for a different condition, so the ticket's condition for a left_out.json entry
  is not met. Two more reasons not to write one: `left_out.json` takes cards off New clues and the two
  folded in-trials boxes only (api.py `_shown_new_clues`, `keep_out`), not the main In trials list this
  card is on; and its entries cannot hold a reason. Changed nothing. For a decision: the link shown is
  chosen by engine code (the target-side record), the same cause as the five ADPKD cards above.

## Card 4. Masitinib

Open Targets knows masitinib as CHEMBL1908391 (`disease_drugs/CHEMBL1908391.masitinib.drug.response.json`).
It linked masitinib to 22 diseases. The live page answer was run for each; the summary is in
`page_answers/masitinib_22_diseases.summary.json`, and masitinib's own reports on each disease's list in
`disease_drugs/masitinib_reports_on_each_disease_list.json`. Trial facts are from ClinicalTrials.gov,
read by hand on 2026-11-25 (`registry/trial_reads.json`).

"Being studied" (main In trials list), 8 diseases. Phase = the card's; the card's Source record is, for all
8, the WHO ATC page https://www.whocc.no/atc_ddd_index/?code=L01EX06, not a trial.

disease | card phase | trial on the disease's list | register phase | status | study conditions
---|---|---|---|---|---
mastocytosis (MONDO_0007950) | Phase 2 | NCT01266369 | PHASE2 | COMPLETED | Mastocytosis
 | | NCT05449444 | PHASE2 | UNKNOWN | Mast Cell Activation Syndrome
cutaneous mastocytosis (MONDO_0019023) | Phase 3 | NCT00814073 | PHASE3 | COMPLETED | Indolent Systemic Mastocytosis
systemic mastocytosis (MONDO_0016586) | Phase 3 | NCT00814073 | PHASE3 | COMPLETED | Indolent Systemic Mastocytosis
 | | NCT04333108 | PHASE3 | UNKNOWN | Indolent Systemic Mastocytosis
 | | NCT00831974 | PHASE2 | COMPLETED | Mastocytosis
plasma cell myeloma (MONDO_0009693) | Phase 3 | NCT01470131 | PHASE3 | TERMINATED | Multiple Myeloma
 | | NCT00866138 | PHASE2 | COMPLETED | Multiple Myeloma
colorectal cancer (MONDO_0005575) | Phase 3 | NCT02605044 | PHASE3 | TERMINATED | Metastatic Colorectal Cancer
 | | NCT03556956 | PHASE2/PHASE3 | COMPLETED | Colorectal Cancer Metastatic
gastrointestinal stromal tumor (MONDO_0011719) | Phase 3 | NCT00812240 | PHASE3 | TERMINATED | Gastrointestinal Stromal Tumors
 | | NCT01694277 | PHASE3 | COMPLETED | Gastrointestinal Stromal Tumors
 | | NCT02009423 | PHASE3 | TERMINATED | Gastro-Intestinal Stromal Tumour
 | | NCT00998751 | PHASE2 | COMPLETED | Gastro-intestinal Stromal Tumours
 | | NCT01506336 | PHASE2 | COMPLETED | Gastro Intestinal Stromal Tumor
 | | (also a TTD page, PHASE_3, and an EMA page, stage UNKNOWN) | | |
melanoma (MONDO_0005105) | Phase 3 | NCT01280565 | PHASE3 | TERMINATED | Metastatic Melanoma
ovarian cancer (MONDO_0008170) | Phase 3 | only a TTD page (https://ttd.idrblab.cn/data/drug/details/D0MW0N), no trial id | | not readable | not readable

Noted, not acted on: the cutaneous mastocytosis card's only trial is a study of indolent
SYSTEMIC mastocytosis; none of the 8 cards says its trial has ended, though most of the studies
read are completed or terminated.

Also on the page, for the record: masitinib is in the folded "more in trials" box on 11 diseases
(pancreatic neoplasm, psoriasis vulgaris, rheumatoid arthritis, ALS, asthma, exocrine pancreatic
carcinoma, Alzheimer disease, multiple sclerosis symptom measurement, ovarian carcinoma, COVID-19,
malignant pancreatic neoplasm, malignant epithelial tumor of ovary, prostate cancer), and on the Approved tab for "neoplasm" (MONDO_0005070,
source the same ATC page). Changed nothing: no rule exists for ended trials.

## Not verified

- The page was not drawn in a browser. "Each of them once, in the folded box" is read from
  `aboveAndBox` in web/index.html and the API answer, not seen.
- The trials in the folded masitinib boxes were not read; only the 8 "being studied" diseases were.
- Registry statuses and phases are those of 2026-11-25.
- The label scan searched the INDICATIONS AND USAGE section of each label only.
