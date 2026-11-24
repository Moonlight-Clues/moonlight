# fixtures/labels_read/ticket_2.40: the eight cards the older "Withdrawn" flag hid

Kashish's answer B (24 Nov): eight cards come back on the Approved main
list, each with the withdrawal line. Before any code was written, the label
behind each card's regulator approval reports (the reports on the disease's
own list whose stage is APPROVAL and whose source is in
`fetch.REGULATOR_SOURCES`) was fetched on 2026-11-24 and saved in this folder, in
the same four parts as `../README.md` describes. The links are the ones in the saved list of
21 Nov (`fixtures/old_withdrawn_flag/`). DailyMed labels still listed were
read from DailyMed's SPL file; those no longer listed (archived) from their
drugInfo page. EMA labels: the "Therapeutic indication" of the EPAR page.

The question, as in Part A of `../README.md`: does the label name the disease as
something the medicine is indicated for? A card whose labels do not gets a
red warning in `moonlight/corrections.json` with the label note (Kashish's
signed rule 6). These entries are proposals until MAIN 3 has read the saved
label text.

card | regulator report(s) | quoted label sentence | change
---|---|---|---
Ephedrine (CHEMBL211456), asthma (MONDO_0004979) | DailyMed ×6: `ephed-asthma-ephedrine-guaifenesin.txt`, `primatene-ephedrine.txt`, `vasopro-ephedrine-guaifenesin.txt`, `ephedrine-sulfate-injection-*.txt` (3) | for temporary relief of mild symptoms of intermittent asthma: wheezing tightness of chest shortness of breath (Primatene) | none: names asthma
Metaproterenol (CHEMBL776), asthma (MONDO_0004979) | DailyMed ×2: `metaproterenol-syrup.txt`, `metaproterenol-tablets.txt` | Metaproterenol sulfate tablets are indicated as a bronchodilator for bronchial asthma and for reversible bronchospasm which may occur in association with bronchitis and emphysema. | none: names asthma
Rosiglitazone (CHEMBL121), type 2 diabetes mellitus (MONDO_0005148) | DailyMed ×5: `avandia-rosiglitazone-*.txt` (3), `avandamet-rosiglitazone-metformin.txt`, `rosiglitazone-maleate-tablets.txt`; FDA ×1: http://www.accessdata.fda.gov/drugsatfda_docs/label/2015/200678s016lbledt.pdf answered 404, not saved | AVANDIA is indicated as an adjunct to diet and exercise to improve glycemic control in adults with type 2 diabetes mellitus. | none: names type 2 diabetes
Fenfluramine (CHEMBL87493), epilepsy (MONDO_0005027) | PMDA ×1: Japan's general list, `pmda-general-list-fenfluramine.txt` | (no label: the page is a list and does not name fenfluramine) | none: no label to read. MAIN 3 decides.
Prasterone (CHEMBL90593), rheumatoid arthritis (MONDO_0008383) | DailyMed ×1: `prastera-prasterone.txt` | PRASTERA® prasterone 200 mg oral softgels is indicated in female patients with mild to moderate, active (SLEDAI ≥2) systemic lupus erythematosus (SLE) to restore serum 5-dehydroandrosterone sulfate to levels typical of women without SLE. | **red warning**: the label names lupus, not rheumatoid arthritis
Tolcapone (CHEMBL1324), Parkinson disease (MONDO_0005180) | DailyMed ×1: `tasmar-tolcapone.txt`; EMA ×1: `tasmar-tolcapone-ema.txt` | TASMAR is indicated as an adjunct to levodopa and carbidopa for the treatment of the signs and symptoms of idiopathic Parkinson's disease. | none: names Parkinson's disease
Gemtuzumab Ozogamicin (CHEMBL1201506), acute myeloid leukemia (MONDO_0018874) | EMA ×1: `mylotarg-gemtuzumab-ozogamicin-ema.txt` | Mylotarg is indicated for combination therapy with daunorubicin (DNR) and cytarabine (AraC) for the treatment of patients age 15 years and above with previously untreated, de novo CD33-positive acute myeloid leukaemia (AML), except acute promyelocytic leukaemia (APL). | none: names AML
Ketoconazole (CHEMBL157101), Cushing syndrome (MONDO_0018912) | EMA ×1: `ketoconazole-esteve-ema.txt` | Ketoconazole Esteve is indicated for the treatment of endogenous Cushing's syndrome in adults and adolescents above the age of 12 years. | none: names Cushing's syndrome
