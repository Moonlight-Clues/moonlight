# fixtures/labels_read/2.52: nitric oxide on PAH, six odd cards and two links on type 2 diabetes

Ticket 2.52, read on 2026-11-25 (Open Targets data 26.09). Lists only
(`moonlight/corrections.json`, `moonlight/confirmed.json`) plus tests.
Grok's final live check of 25 Nov, 4 pm, read every Source record on the main
Approved list of the ten audited diseases; these ten cards did not hold up.

**Result: nine list changes, one report.** Seven red warnings (corrections.json:
109 entries, was 102) and two confirmed links (confirmed.json: 28 entries, was
26). Card 10 (simvastatin) is changed in no list.

"Current label" means a label DailyMed's own list returns today
(`services/v2/spls.json`, by UNII code of the ingredient). Every label that list
returns for each medicine was read: `sweeps/<medicine>.tsv` has one line per
label (setid, date, category, the sentences naming diabetes), and `labels/` holds
the whole indications text of the labels that matter, in the same four parts as
`../README.md` (the link, the date, the product line, the INDICATIONS AND USAGE
text word for word, spacing tidied).

card | change | quoted label sentence | link | value replaced
---|---|---|---|---
Nitric oxide (CHEMBL1200689), pulmonary arterial hypertension (MONDO_0015924) | red warning added to corrections.json: all 12 current nitric oxide labels read; the seven labels of the gas as a medicine are for newborns with hypoxic respiratory failure and pulmonary hypertension, none of the 12 names pulmonary arterial hypertension | Noxivent™ is a vasodilator indicated to improve oxygenation and reduce the need for extracorporeal membrane oxygenation in term and near-term (>34 weeks gestation) neonates with hypoxic respiratory failure associated with clinical or echocardiographic evidence of pulmonary hypertension in conjunction with ventilatory support and other appropriate agents. | https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=27586e4f-66f1-4583-981c-e0bccb8b02e0 | no warning
Biotin (CHEMBL857), type 2 diabetes (MONDO_0005148) | red warning added to corrections.json: the card's label (Divista) is not a current label; no current label of biotin (302 read) names type 2 diabetes as an indication | DivistaTM is specially designed as a once a day nutritional adjuvant to the current standard of care for patients with, or at risk of developing type 2 diabetes mellitus (T2DM). | https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=06c485cd-ee30-44f2-be63-bb98f8d1a907 | no warning
Cyanocobalamin (CHEMBL2110563), type 2 diabetes (MONDO_0005148) | red warning added to corrections.json: the card's label (Divista) is not a current label; no current label of cyanocobalamin (465 read) names type 2 diabetes as an indication | DivistaTM is specially designed as a once a day nutritional adjuvant to the current standard of care for patients with, or at risk of developing type 2 diabetes mellitus (T2DM). | https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=06c485cd-ee30-44f2-be63-bb98f8d1a907 | no warning
Folic acid (CHEMBL1622), type 2 diabetes (MONDO_0005148) | red warning added to corrections.json: the card's label (Divista) is not a current label; no current label of folic acid (551 read) names type 2 diabetes as an indication | DivistaTM is specially designed as a once a day nutritional adjuvant to the current standard of care for patients with, or at risk of developing type 2 diabetes mellitus (T2DM). | https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=06c485cd-ee30-44f2-be63-bb98f8d1a907 | no warning
OMEGA-3-ACID Ethyl Esters (CHEMBL1200711), type 2 diabetes (MONDO_0005148) | red warning added to corrections.json: the card's label (Divista) is not a current label; no current label of omega-3-acid ethyl esters (43 read) names type 2 diabetes as an indication, only as a cause to control first | DivistaTM is specially designed as a once a day nutritional adjuvant to the current standard of care for patients with, or at risk of developing type 2 diabetes mellitus (T2DM). | https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=06c485cd-ee30-44f2-be63-bb98f8d1a907 | no warning
Pyridoxine (CHEMBL1364), type 2 diabetes (MONDO_0005148) | red warning added to corrections.json: the card's label (Divista) is not a current label; no current label of pyridoxine (534 read) names type 2 diabetes as an indication | DivistaTM is specially designed as a once a day nutritional adjuvant to the current standard of care for patients with, or at risk of developing type 2 diabetes mellitus (T2DM). | https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=06c485cd-ee30-44f2-be63-bb98f8d1a907 | no warning
Tyrosine (CHEMBL925), type 2 diabetes (MONDO_0005148) | red warning added to corrections.json: the card's label (Appformin, a kit of metformin and tyrosine) names type 2 diabetes only for its metformin tablets; its tyrosine capsule (AppTrim) is for obesity; none of the 41 current tyrosine labels names type 2 diabetes for tyrosine | Metformin hydrochloride tablets, USP are indicated as an adjunct to diet and exercise to improve glycemic control in adults and children with type 2 diabetes mellitus. | https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=0569d5d5-70df-46d7-954a-fe00542a7191 | no warning
Liraglutide (CHEMBL4084119), type 2 diabetes (MONDO_0005148) | confirmed link added to confirmed.json: Victoza, a liraglutide-alone label that names type 2 diabetes | as an adjunct to diet and exercise to improve glycemic control in adults and pediatric patients aged 10 years and older with type 2 diabetes mellitus, | https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=5a9ef4ea-c76a-4d34-a604-27c5b505f5a4 | https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=21335fe4-d395-4501-ac2a-2f20d7520da9 (Xultophy)
Canagliflozin (CHEMBL2048484, the card's id; its tablet form is CHEMBL4594217), type 2 diabetes (MONDO_0005148) | confirmed link added to confirmed.json: Invokana (Janssen), a canagliflozin-alone label that names type 2 diabetes | as an adjunct to diet and exercise to improve glycemic control in adults and pediatric patients aged 10 years and older with type 2 diabetes mellitus. | https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=b9057d3b-b104-4f09-8a61-c61ef9d4a3f3 | https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=6868666b-c25e-40d1-9d1f-306bbe9390c1 (Invokamet)
Simvastatin (CHEMBL1064), type 2 diabetes (MONDO_0005148) | none: reported only, combination products are Kashish's decision. Of 182 current simvastatin labels, none says simvastatin is indicated to treat type 2 diabetes; 175 name diabetes only as a risk group (see below); the quote is Juvisync's own, for sitagliptin, the card's label | Sitagliptin is a dipeptidyl peptidase-4 (DPP-4) inhibitor indicated as an adjunct to diet and exercise to improve glycemic control in adults with type 2 diabetes mellitus. (1.1) | https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=2062b3d3-580f-46f8-94b6-4bdecb7b53b1 | nothing replaced (the card still links Juvisync)

## Every id was found on the live API (26.09)

`disease_drugs/MONDO_0015924.response.json` and `disease_drugs/MONDO_0005148.response.json`
are each disease's own list, asked live on 2026-11-25 with fetch.py's
DISEASE_DRUGS_QUERY. `page_answers/` is what `/api/clues` sent for the two diseases
on main (cb 1cf4616), before this ticket. Every card was on the main Approved list,
with no grey line. The ids are the card ids on those pages: nitric oxide
CHEMBL1200689, biotin CHEMBL857, cyanocobalamin CHEMBL2110563 (its forms
CHEMBL2096655, CHEMBL2104118), folic acid CHEMBL1622, omega-3-acid ethyl esters
CHEMBL1200711, pyridoxine CHEMBL1364 (form CHEMBL1200756), tyrosine CHEMBL925,
liraglutide CHEMBL4084119, simvastatin CHEMBL1064. **Canagliflozin's card id is
CHEMBL2048484** (canagliflozin anhydrous), the parent of CHEMBL4594217; a
confirmed.json entry for CHEMBL4594217 would not match the card.

## Cards 2 to 6: what the card's label really is (for Kashish)

The card's link (Divista, `labels/not_current/divista-chromium-picolinate-capsule.txt`)
says "for patients with, or at risk of developing type 2 diabetes mellitus", not
only "at risk of developing" as the ticket quotes it. It still does not stand as
a label that names the disease, for the stated test, because:

- it is not a current label: DailyMed's list does not return it (0 results for its
  setid), and its own page says marketing ended 09/30/2011;
- it is an "unapproved drug other" ("This drug has not been found by FDA to be safe
  and effective");
- it is one product of six ingredients (chromium picolinate, biotin, pyridoxine,
  cyanocobalamin, folic acid, omega-3-acid ethyl esters), not a label of any one of them.

Where the current labels do say "diabetes" for these five medicines, it is a warning,
a precaution or a cause to control first, never an indication (`sweeps/`): for
example omega-3-acid ethyl esters (Lovaza and every generic): "Every attempt should be
made to control serum lipids with appropriate diet, exercise, weight loss in obese
patients, and control of any medical problems such as diabetes mellitus and
hypothyroidism that are contributing to the lipid abnormalities."

## Card 7: tyrosine

The card's label is the Appformin kit (metformin hydrochloride tablets + tyrosine
capsules, AppTrim, 2011). It is in DailyMed's current list. The one sentence that
names type 2 diabetes is the metformin tablets' indication; AppTrim is "intended for
the clinical nutritional management of the metabolic processes in patients with obesity,
morbid obesity, and metabolic syndrome". Appformin-D (setid 63f7ac0f) says the same.
No other tyrosine label names diabetes. This is the same kind of combination-product
question as card 10; it is treated here as ticket 7 expected (red warning), and flagged.

## Cards 8 and 9: the confirmed links

Victoza (setid 5a9ef4ea, Novo Nordisk, effective 2025-10-14) names type 2 diabetes for
liraglutide alone. Invokana (setid b9057d3b, Janssen, effective 2026-06-11) names it for
canagliflozin alone; it is also one of the Invokana links Open Targets itself lists for
the medicine. DailyMed holds four more Invokana labels (repackagers A-S Medication
Solutions, Cardinal Health, and a newer A-S Medication one, 4e946ba3, 2026-09-21);
Janssen's own label was chosen. Xultophy (insulin degludec and liraglutide) and Invokamet
(canagliflozin and metformin) are saved as `*-REPLACED.txt`.

## Card 10: simvastatin, report only (nothing changed)

The card's link opens Juvisync (sitagliptin with simvastatin, Merck,
`labels/not_current/juvisync-sitagliptin-simvastatin.txt`). Juvisync is not a current
label either: not in DailyMed's list, marketing ended 07/31/2014.

Every current simvastatin label (182, `sweeps/simvastatin.tsv`; this count includes
ezetimibe-and-simvastatin and other products that hold simvastatin) says this about diabetes:

- 175 name diabetes in the indications, always as a risk group of people who are at high
  risk of heart events, never as a condition simvastatin treats:
  - 72 older labels: "In patients at high risk of coronary events because of existing
    coronary heart disease, diabetes, peripheral vessel disease, history of stroke or other
    cerebrovascular disease, simvastatin tablets are indicated to:"
  - 103 current-wording labels: "To reduce the risk of total mortality by reducing risk of
    coronary heart disease death, non-fatal myocardial infarction and stroke, and the need for
    coronary and non-coronary revascularization procedures in adults with established coronary
    heart disease, cerebrovascular disease, peripheral vascular disease, and/or diabetes, who
    are at high risk of coronary heart disease events."
- 7 do not name diabetes at all in the indications.
- No simvastatin-alone label has "glycemic control" or "type 2 diabetes" as something to
  treat. The only label that does is Juvisync (sitagliptin's own indication), which is no
  longer current.

Kashish decides whether "a risk group" counts as naming the disease and whether any
combination label counts.
