# Sources for moonlight/approval_years.json

**What the year means:** earliest US or EU approval of this active ingredient, for any use.

It is not the year the medicine was approved for the disease on the page, and it is not a judgement of how good or current the medicine is.

## Judgement calls (word for word, from MAIN 4)

- Ties go to the US.
- Withdrawn EU authorisations count, refused ones don't.
- Combinations count only with a single-ingredient product on the same application.
- Deuterated forms are separate ingredients.
- The FDA Purple Book is the US source for CBER biologics (products not in Drugs@FDA, such as FEIBA and human factor VIII).

How these are applied in practice: "ties go to the US" is decided by year (same year → US, even if the EU date was earlier that year). "Withdrawn" EU covers the EMA statuses Withdrawn, Lapsed, Expired, Revoked and Suspended; Refused, Application withdrawn and Opinion-only do not count. A combination product counts for an ingredient only if the same Drugs@FDA application also has a product whose only active ingredient is that ingredient. Deuterated analogues (for example deutetrabenazine) are not counted for the parent ingredient.

## How each entry is made

Shape: `{"CHEMBL...": {"year": 2001, "region": "US" | "EU", "source": "<url>"}}`

1. **Ingredient.** The card's ChEMBL id is mapped to its parent molecule and all its salt/hydrate forms using the ChEMBL API (molecule and molecule_form endpoints), with their INN/USAN/BAN/FDA/USP/JAN names (and a few weaker synonym types, flagged in `anomalies.csv` when they are the only link). Salts and forms count as the same ingredient.
2. **US year, small-molecule and CDER products.** Drugs@FDA, read from the openFDA `drug/drugsfda` bulk export. Only NDA and BLA applications count (no ANDAs). The date is the approval date of the application's ORIGINAL submission (`submission_type` ORIG, status AP); supplements do not count. The application must contain a product whose only active ingredient is this ingredient. Source = the Drugs@FDA application page (`accessdata.fda.gov/scripts/cder/daf/...ApplNo=`).
3. **US year, CBER biologics.** The FDA Purple Book (monthly data download, October 2026 file). Only rows with Submission Type "Original" and License Type 351(a) count; the date is the Approval Date of the earliest such row for the BLA. A BLA whose Original row is not in the Purple Book gives no date (nothing is guessed). Blood-factor products have US proper names that differ from the INN (for example "Antihemophilic Factor (Recombinant)" for octocog alfa), so for these the ChEMBL id is tied to its BLA numbers in `purplebook_aliases.json`, with the INN/brand evidence written there. The Purple Book has no stable page per product, so its source link is the Purple Book advanced search with the BLA number as the query (`purplebooksearch.fda.gov/advanced-search?query=<BLA number>`); the BLA number is in the link. When Drugs@FDA and the Purple Book give the same date, Drugs@FDA is used.
4. **EU year.** EMA's published medicines list (`medicines-output-medicines-report_en.xlsx`), human medicines, centrally authorised only. The date is the "Marketing authorisation date". Single-substance medicines only. Source = the medicine's EPAR page on ema.europa.eu.
5. **Region.** Whichever year is earlier. If both are the same year, US. If only one exists, that one. (`build.py` has one switch, `REGION_RULE`, to produce US-only instead.)
6. **No entry.** If neither exists, the ingredient has no entry. Nothing is guessed. The list is in `no_entry.md`.

## Known limits

- Drugs@FDA covers medicines reviewed by FDA's CDER. Plasma-derived products, vaccines and gene therapies are licensed by CBER and are read from the Purple Book instead; very old CBER licences are as recorded there.
- Very old US approvals are as recorded in Drugs@FDA.
- Medicines approved only nationally in the EU, or only in countries such as Japan, have no entry.

## Data versions used

- openFDA drugsfda export dated 2026-11-25 (https://download.open.fda.gov/drug/drugsfda/drug-drugsfda-0001-of-0001.json.zip)
- FDA Purple Book monthly data download, October 2026 (https://www.accessdata.fda.gov/drugsatfda_docs/PurpleBook/2026/purplebook-search-October-data-download.csv)
- EMA medicines list generated 26/11/2026 06:00 (https://www.ema.europa.eu/en/documents/report/medicines-output-medicines-report_en.xlsx)
- ChEMBL API (https://www.ebi.ac.uk/chembl/api/data/), read 26 Nov 2026
- The list of Approved cards is read from the live Moonlight API (`/api/clues?disease_id=...`, read-only) on 26 Nov 2026.
