# fixtures/labels_read/2.47: four cards from public feedback

Ticket 2.47 (25 Nov 2026): avapritinib, imatinib, deferoxamine, Obizur. Lists
only (`moonlight/approvals.json`, `moonlight/corrections.json`) plus tests.

**Result: one list change.** Cards 1 to 3 are already in the lists, put there
by earlier tickets. Card 4's label does not say what the ticket expected (it never
says "not for congenital haemophilia A"); Kashish decided: the rule is "no current
label names the disease" and the label names only acquired haemophilia A, so
Obizur went into corrections.json (red box) on 25 Nov. Each
card's current label was read anyway (DailyMed SPL file, fetched 2026-11-25).
Each `.txt` file holds, in this order (the same four parts as `../README.md`):
the link that was fetched, the date, the product line, the whole INDICATIONS
AND USAGE section word for word (spacing tidied).

- `ayvakit-avapritinib.txt`, `gleevec-imatinib-mesylate.txt`: cards 1 and 2.
- `desferal-deferoxamine-novartis.txt` and `also_read/`: card 3. DailyMed holds
  seven deferoxamine labels. Six are saved here and each says it is not
  indicated for primary hemochromatosis. The seventh, Mitem's Desferal
  (published 23 Nov 2026), has no text in DailyMed or openFDA: see
  `unread/mitem-desferal-not-readable.txt`.
- `obizur-susoctocog-alfa.txt`: card 4.
- `disease_drugs/`: each page's own list, asked live on 2026-11-25 (Open Targets
  data 26.09) with fetch.py's DISEASE_DRUGS_QUERY. Saved as sent, no indentation.
  `MONDO_0016586` systemic mastocytosis, `EFO_1000642` hemochromatosis,
  `MONDO_0010602` haemophilia A. Every id below was found on the live API:
  avapritinib CHEMBL4204794, imatinib CHEMBL941 (its tablet form on the
  mastocytosis group page is CHEMBL1642), deferoxamine CHEMBL556 (the list row
  is its mesylate form CHEMBL1234), susoctocog alfa CHEMBL5315075.

card | change | quoted label sentence | link | value replaced
---|---|---|---|---
Avapritinib (CHEMBL4204794), systemic mastocytosis (MONDO_0016586) | none: already added under Approved on 23 Nov (approvals.json, 7th entry); the label still says it | AYVAKIT is indicated for the treatment of adult patients with indolent systemic mastocytosis (ISM). | https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=645c887c-8cd4-4623-8da9-ac223d71a8b9 | nothing replaced
Imatinib (CHEMBL941), systemic mastocytosis (MONDO_0016586) | none: already added under Approved, limited, on 23 Nov (approvals.json, 9th entry); the label still says it | Adult patients with aggressive systemic mastocytosis without the D816V c-Kit mutation or with c-Kit mutational status unknown. | https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=211ef2da-2868-4a77-8055-1cb2cd78e24b | nothing replaced
Deferoxamine (CHEMBL556), hemochromatosis (EFO_1000642) | none: red warning already on corrections.json since 22 Nov (ticket 2.19); six current labels read agree, Mitem's could not be read | Desferal is not indicated for the treatment of primary hemochromatosis (since phlebotomy is the method of choice for removing excess iron in this disorder). | https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=a7174843-5965-49fc-b842-f7eff7b48bbc | nothing replaced
Susoctocog alfa (CHEMBL5315075), hemophilia A (MONDO_0010602) | red warning added to corrections.json (Kashish's decision): the label names only acquired haemophilia A, and never says "not for congenital haemophilia A" | OBIZUR is not indicated for the treatment of von Willebrand disease. | https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=a69ccbb3-7648-4978-8c6d-7ca6b95a9b01 | no warning

Card 4, what the label does say (all in `obizur-susoctocog-alfa.txt` except the
contraindication, which is in section 4 of the same label):

- "indicated for the on-demand treatment and control of bleeding episodes in adults with acquired hemophilia A."
- Contraindicated "With congenital hemophilia A with inhibitors (CHAWI) due to the high incidence of anamnestic reactions to human factor VIII (hFVIII) and porcine factor VIII (pFVIII)": only congenital haemophilia A *with inhibitors*.
- No sentence says it is not indicated for congenital haemophilia A in general.
