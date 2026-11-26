# Sources for moonlight/approval_years.json

**What the year means:** earliest US or EU approval of this active ingredient, for any use.

It is not the year the medicine was approved for the disease on the page, and it is not a judgement of how good or current the medicine is.

## How each entry is made

Shape: `{"CHEMBL...": {"year": 2001, "region": "US" | "EU", "source": "<url>"}}`

1. **Ingredient.** The card's ChEMBL id is mapped to its parent molecule and all its salt/hydrate forms using the ChEMBL API (molecule and molecule_form endpoints), with their INN/USAN/BAN/FDA names. Salts and forms count as the same ingredient. Deuterated analogues (for example deutetrabenazine) are a different ingredient and are not counted.
2. **US year.** Drugs@FDA, read from the openFDA `drug/drugsfda` bulk export. Only NDA and BLA applications count (no ANDAs). The date is the approval date of the application's ORIGINAL submission (`submission_type` ORIG, status AP); supplements do not count. The application must contain a product whose only active ingredient is this ingredient; combination-only products do not count. Source = the Drugs@FDA application page (`accessdata.fda.gov/scripts/cder/daf/...ApplNo=`).
3. **EU year.** EMA's published medicines list (`medicines-output-medicines-report_en.xlsx`), human medicines, centrally authorised only. The date is the "Marketing authorisation date". Medicines that were authorised and later withdrawn, lapsed, expired, revoked or suspended still count; refused medicines and withdrawn applications do not. Single-substance medicines only. Source = the medicine's EPAR page on ema.europa.eu.
4. **Region.** Whichever year is earlier. If both are the same year, US. If only one exists, that one.
5. **No entry.** If neither exists, the ingredient has no entry. Nothing is guessed. Medicines approved only elsewhere (for example only in Japan) have no entry.

## Known limits

- Drugs@FDA covers medicines reviewed by FDA's CDER. Many blood products, vaccines and gene therapies are licensed by CBER and are not in Drugs@FDA, so their US approval cannot be seen by this rule. For those the EU year is used, or there is no entry.
- Very old US approvals are as recorded in Drugs@FDA.

## Data versions used

- openFDA drugsfda export dated 2026-11-25 (https://download.open.fda.gov/drug/drugsfda/drug-drugsfda-0001-of-0001.json.zip)
- EMA medicines list generated 26/11/2026 06:00 (https://www.ema.europa.eu/en/documents/report/medicines-output-medicines-report_en.xlsx)
- ChEMBL API (https://www.ebi.ac.uk/chembl/api/data/), read 26 Nov 2026
