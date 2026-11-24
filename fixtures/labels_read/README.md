# fixtures/labels_read: official labels saved for ticket 2.41

Every entry that ticket 2.41 adds to `moonlight/corrections.json` (Part A,
red warnings) or `moonlight/approvals.json` (Part B, missing approvals) is
backed by one saved label below. Fetched on 2026-11-24 from DailyMed. Each
`.txt` file holds, in this order:

1. the link that was fetched,
2. the date it was fetched,
3. the product name line as the page shows it ("NAME- medicine form"),
4. the whole INDICATIONS AND USAGE section, word for word.

Only the spacing was tidied (one line per paragraph, list item or table
cell). No word was changed. These entries are proposals until MAIN 3 has
read the saved label text.

Part A asks: is the disease named as something this medicine is indicated
to treat? Where the disease appears in the section, the quote is the
sentence that names it (as a cause, a setting, a population studied, an
exclusion or a warning). Where it does not appear at all, the quote is the
sentence that says what the medicine is indicated for.

Part B asks: does the current label name the disease as an indication? The
quote is that sentence.

`disease_drugs/`: each disease's own list, asked live on 2026-11-24 (Open
Targets data 26.09) with fetch.py's DISEASE_DRUGS_QUERY, the way fetch.py
asks it. Saved as sent; the four large ones without indentation. The
myasthenia gravis list is not saved again: `fixtures/approvals_by_hand/`
already holds it, letter for letter the live answer of 2026-11-24.
`MONDO_0015128` and `MONDO_0015129` are saved only to show why hydrocortisone
for Addison disease was not added.

card | change | quoted label sentence | link | value replaced
---|---|---|---|---
Cholestyramine (CHEMBL1201625), hypothyroidism (MONDO_0005420) | red warning | Prior to initiating therapy with QUESTRAN secondary causes of hypercholesterolemia (e.g., poorly controlled diabetes mellitus, hypothyroidism, nephrotic syndrome, dysproteinemias, obstructive liver disease, other drug therapy, alcoholism), should be excluded, and a lipid profile performed to assess Total cholesterol, HDL-C, and triglycerides (TG). | https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=362ddd91-a63f-4ec6-841a-75785dd208c8 | no warning
Fenofibrate (CHEMBL672), hypothyroidism (MONDO_0005420) | red warning | Diseases contributory to hyperlipidemia, such as hypothyroidism or diabetes mellitus should be looked for and adequately treated. | https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=66d2c555-2880-4ac6-80f8-69a00f1fbc4c | no warning
Mecasermin (CHEMBL1201716), hypothyroidism (MONDO_0005420) | red warning | INCRELEX is not indicated for use in patients with secondary forms of IGF-1 deficiency, such as GH deficiency, malnutrition, hypothyroidism, or chronic treatment with pharmacologic doses of anti-inflammatory corticosteroids. | https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=a8b27a1b-a611-4f91-ad22-76d4b390c3ae | no warning
OMEGA-3-ACID Ethyl Esters (CHEMBL1200711), hypothyroidism (MONDO_0005420) | red warning | Every attempt should be made to control serum lipids with appropriate diet, exercise, weight loss in obese patients, and control of any medical problems such as diabetes mellitus and hypothyroidism that are contributing to the lipid abnormalities. | https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=0d842966-26bc-4521-b401-635a83618012 | no warning
Hydroxyurea (CHEMBL467), melanoma (MONDO_0005105) | red warning | Hydroxyurea capsules are indicated for the treatment of: | https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=0a5c7030-5fac-4708-b309-f9d07103285a | no warning
Butalbital (CHEMBL454), migraine disorder (MONDO_0005277) | red warning | Butalbital, Aspirin, Caffeine and Codeine Phosphate Capsules are indicated for the relief of the symptom complex of tension (or muscle contraction) headache. | https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=04bddbc4-86c7-4bac-9327-010568020568 | no warning
Fentanyl (CHEMBL596), migraine disorder (MONDO_0005277) | red warning | For this reason, ABSTRAL is contraindicated in the management of acute or postoperative pain, including headache/migraine, dental pain, or use in the emergency room. | https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=4906457e-30ad-4da7-b3ac-bb9e6651a670 | no warning
Amifampridine (CHEMBL354077), myasthenia gravis (MONDO_0009688) | red warning | RUZURGI is indicated for the treatment of Lambert-Eaton myasthenic syndrome (LEMS) in patients 6 to less than 17 years of age. | https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=2731310a-c060-4d3e-ba41-763d791f63a9 | no warning
Guanidine (CHEMBL821), myasthenia gravis (MONDO_0009688) | red warning | It is not indicated for treating myasthenia gravis. | https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=903fbd33-e5d9-41fb-9414-7bd6f42a8593 | no warning
Pralidoxime (CHEMBL1420), myasthenia gravis (MONDO_0009688) | red warning | in the control of overdosage by anticholinesterase drugs used in the treatment of myasthenia gravis. | https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=2741d8fd-51c2-46be-880b-99f2b20a6137 | no warning
Trientine (CHEMBL609), rheumatoid arthritis (MONDO_0008383) | red warning | Unlike penicillamine, Syprine is not recommended in cystinuria or rheumatoid arthritis. | https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=c34f77a7-996b-4470-b5df-d946a7fe5dbe | no warning
Fenofibrate (CHEMBL672), type 2 diabetes mellitus (MONDO_0005148) | red warning | Fenofibrate did not reduce coronary heart disease morbidity and mortality in two large, randomized controlled trials of patients with type 2 diabetes mellitus [see Warnings and Precautions (5.1) and Clinical Studies (14.4)]. | https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=0f958942-1504-40a1-8ad8-43df2c3f717e | no warning
Fenofibric Acid (CHEMBL981), type 2 diabetes mellitus (MONDO_0005148) | red warning | Fenofibrate at a dose equivalent to 105 mg of FIBRICOR was not shown to reduce coronary heart disease morbidity and mortality in patients with type 2 diabetes mellitus [see Warnings and Precautions (5.1)]. | https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=31c80f84-0169-4659-b9cf-8f897ed319eb | no warning
Ticagrelor (CHEMBL398435), type 2 diabetes mellitus (MONDO_0005148) | red warning | While use is not limited to this setting, the efficacy of BRILINTA was established in a population with type 2 diabetes mellitus (T2DM). | https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=4f9bd52a-99a7-4606-92b4-456a917aabef | no warning
Ravulizumab (CHEMBL3989986), myasthenia gravis (MONDO_0009688) | added under Approved, limited | ULTOMIRIS is indicated for the treatment of adult patients with generalized myasthenia gravis (gMG) who are anti-acetylcholine receptor (AChR) antibody-positive. | https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=a9a590d9-0217-43c7-908d-e62a71279791 | In trials: "Already being studied for this disease", Phase 3
Ravulizumab (CHEMBL3989986), atypical hemolytic-uremic syndrome (MONDO_0016244) | added under Approved | ULTOMIRIS is indicated for the treatment of adult and pediatric patients one month of age and older with atypical hemolytic uremic syndrome (aHUS) to inhibit complement-mediated thrombotic microangiopathy (TMA). | https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=a9a590d9-0217-43c7-908d-e62a71279791 | In trials: "Already being studied for this disease", Phase 3
Dupilumab (CHEMBL2108675), eosinophilic esophagitis (MONDO_0005361) | added under Approved | DUPIXENT is indicated for the treatment of adult and pediatric patients aged 1 year and older, weighing at least 15 kg, with eosinophilic esophagitis (EoE). | https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=595f437d-2729-40bb-9c62-c8ece1f82780 | In trials: "Already being studied for this disease", Phase 3; and Approved: the wider-group folded box (esophagitis)
Budesonide (CHEMBL1370), eosinophilic esophagitis (MONDO_0005361) | added under Approved | EOHILIA™ is indicated for 12 weeks of treatment in adult and pediatric patients 11 years of age and older with eosinophilic esophagitis (EoE). | https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=56f2023a-69b2-4470-b4ad-af7ec1be527a | In trials: "Already being studied for this disease", Phase 3; and Approved: the wider-group folded box (esophagitis)
Delandistrogene Moxeparvovec (CHEMBL4650241), Duchenne muscular dystrophy (MONDO_0010679) | added under Approved, limited (MAIN 3 decides) | ELEVIDYS is indicated for the treatment of patients 4 years of age and older with Duchenne muscular dystrophy (DMD), who are ambulatory and have a confirmed mutation in the DMD gene [see Clinical Pharmacology (12.2), Clinical Studies (14)]. | https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=3525abcd-fbd2-46c5-9706-cffdf2e8a361 | In trials: "Already being studied for this disease", Phase 1
Corticotropin (CHEMBL1201610), dermatomyositis (MONDO_0016367) | added under Approved | During an exacerbation or as maintenance therapy in selected cases of: systemic lupus erythematosus, systemic dermatomyositis (polymyositis). | https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=7b48ddec-e815-45f4-9ca0-5c0daaf56f30 | In trials: the "more in trials" box, Phase 2
