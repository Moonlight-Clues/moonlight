# fixtures/labels_read/2.46: approvals reported missing, added from their labels

Ticket 2.46 (MAIN 3, 25 Nov 2026). Feedback log rows 14, 42, 45, 59. Every
entry the ticket adds to `moonlight/approvals.json` is backed by one saved
label in this folder, fetched on 2026-11-25. Each `.txt` file holds, in this
order (the same four parts as `../README.md`):

1. the link that was fetched,
2. the date it was fetched,
3. the product line,
4. the whole INDICATIONS AND USAGE section, word for word.

Only the spacing was tidied (one line per paragraph, list item or table
cell). No word was changed. DailyMed labels were read from DailyMed's SPL
file. Otiprio is not on DailyMed or openFDA: its label is the PDF that
Drugs@FDA holds (NDA 207986). These entries are proposals until MAIN 3 has
read the saved label text.

The question for each card: does the current label name the disease as an
indication? The quote is that sentence.

The "limited" rule (Kashish, signed 24 Nov): `"limited": true` only when the
label requires a test result, or an earlier treatment to have failed. Adults
only, an age, a weight or "severe" alone do not count.

`disease_drugs/`: each disease's own list, asked live on 2026-11-25 with
fetch.py's DISEASE_DRUGS_QUERY, the way fetch.py asks it. Saved as sent,
without indentation. `MONDO_0001516` (spinal muscular atrophy), `MONDO_0008294`
(acute intermittent porphyria), `MONDO_0010602` (haemophilia A) and
`MONDO_0005892` (otitis media with effusion) hold the added cards.
`MONDO_0019079` (proximal spinal muscular atrophy) is saved only to show the
second page that fits apitegromab; it gets no entry.

card | change | quoted label sentence | link | value replaced
---|---|---|---|---
Apitegromab (CHEMBL4594326), spinal muscular atrophy (MONDO_0001516) | added under Approved | ISEMBYLD is indicated for the treatment of spinal muscular atrophy (SMA) in adults and pediatric patients 2 years of age and older who are currently receiving a survival motor neuron 2 (SMN2)-targeted treatment. | https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=b1cd8ab8-8a10-48ed-9806-75a44f22b963 | in the box "New in trials", not under Approved
Hemin (CHEMBL1200662), acute intermittent porphyria (MONDO_0008294) | added under Approved, limited | PANHEMATIN is a hemin for injection indicated for the amelioration of recurrent attacks of acute intermittent porphyria temporally related to the menstrual cycle in susceptible women, after initial carbohydrate therapy is known or suspected to be inadequate. | https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=9984267a-4d57-4444-9bb5-16bca7dea691 | no card on the page (hemin is not on this disease's list)
Fitusiran (CHEMBL4297754), haemophilia A (MONDO_0010602) | added under Approved | QFITLIA is indicated for routine prophylaxis to prevent or reduce the frequency of bleeding episodes in adult and pediatric patients aged 12 years and older with hemophilia A or B with or without factor VIII or IX inhibitors. | https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=6dd2f8ac-6f90-4cbf-b197-97d74964135c | in the box "Already being studied for this disease", not under Approved
Anti-Inhibitor Coagulant Complex (CHEMBL4297953), haemophilia A (MONDO_0010602) | added under Approved, limited | FEIBA is an Anti-Inhibitor Coagulant Complex indicated for use in hemophilia A and B patients with inhibitors for: | https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=752604e5-4ea2-44f4-83ed-1569373f6412 | in the box "More medicines in trials", not under Approved
Human Coagulation Factor VIII (CHEMBL2108175), haemophilia A (MONDO_0010602) | added under Approved | HEMOFIL M is indicated in hemophilia A (classical hemophilia) for the prevention and control of hemorrhagic episodes. | https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=b8953ff7-3bba-4a0b-a486-f26fb81f05d9 | in the box "Already being studied for this disease", not under Approved
Desmopressin (CHEMBL1429), haemophilia A (MONDO_0010602) | added under Approved, limited | DDAVP Injection is indicated for patients with hemophilia A with factor VIII coagulant activity levels greater than 5% without factor VIII antibodies to: | https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=651f6fee-a2c7-431b-8d5d-58b156c72244 | no card on the page (its row on the list has stage UNKNOWN, shown nowhere)
Ciprofloxacin (CHEMBL8), otitis media with effusion (MONDO_0005892) | added under Approved, limited flag left off for MAIN 3 | The treatment of pediatric patients (6 months of age and older) with bilateral otitis media with effusion undergoing tympanostomy tube placement. | https://www.accessdata.fda.gov/drugsatfda_docs/label/2018/207986s002lbl.pdf | no card on the page (ciprofloxacin is not on this disease's list)

## Read, not added

`also_read/koate-antihemophilic-factor.txt`: Koate (Kedrion), the second
product the ticket names on the antihemophilic factor, human card. Its
Open Targets medicine is the same one as Hemofil M's (CHEMBL2108175), so
one entry covers both. Koate's sentence: "KOĀTE® is a human plasma-derived
antihemophilic factor indicated for the control and prevention of bleeding
episodes or in order to perform emergency and elective surgery in patients
with hemophilia A (hereditary Factor VIII deficiency)."

`skipped/`: Alphanate, Humate-P and Wilate. Each label names haemophilia A,
but Open Targets has no medicine for the complex itself (see the pull
request report). Nothing was added.

`report_only/`: Roctavian (FDA package insert; DailyMed has no Roctavian
page) and Obizur, for the ticket's ALSO REPORT. Nothing was changed.
