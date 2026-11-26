# Sources for moonlight/approval_years.json

**What the year means:** the year the active ingredient (moiety) was first approved, in any salt or form — earliest US or EU approval, for any use.

It is not the year the medicine was approved for the disease on the page, and it is not a judgement of how good or current the medicine is.

`build.py` has two one-line switches. `REGION_RULE` is `earliest` (default; tie goes to the US) or `us_only`. `ESTER_RULE` is `moiety` (default; trailing salt and ester words are stripped from a fixed list) or `chembl_parent` (merge only names ChEMBL links as one parent molecule; esters that are themselves a ChEMBL parent keep their own year). Friday's published table uses `earliest` and `moiety`. The two ester values are compared in `compare_ester_rules.md`.

## Judgement calls (word for word, from MAIN 4)

- Ties go to the US.
- Withdrawn EU authorisations count, refused ones don't.
- Combinations count only with a single-ingredient product on the same application.
- Deuterated forms are separate ingredients.
- The FDA Purple Book is the US source for CBER biologics (products not in Drugs@FDA, such as FEIBA and human factor VIII).

How these are applied in practice: "ties go to the US" is decided by year (same year → US, even if the EU date was earlier that year). "Withdrawn" EU covers the EMA statuses Withdrawn, Lapsed, Expired, Revoked and Suspended; Refused, Application withdrawn and Opinion-only do not count. A combination product counts for an ingredient only if the same Drugs@FDA application also has a product whose only active ingredient is that ingredient. Deuterated analogues (for example deutetrabenazine) are not counted for the parent ingredient.

## How each entry is made

Shape: `{"CHEMBL...": {"year": 2001, "region": "US" | "EU", "source": "<url>"}}`

1. **Ingredient.** The card's ChEMBL id is mapped to its parent molecule and all its salt/hydrate forms using the ChEMBL API (molecule and molecule_form endpoints), with their INN/USAN/BAN/FDA/USP/JAN names and the preferred name. Under the default `ESTER_RULE=moiety`, salts and listed ester forms of the same active moiety count as the same ingredient, so a card for testosterone cypionate takes the year testosterone was first approved. Esters not on the strip list (for example undecanoate, furoate) are not merged. Under `ESTER_RULE=chembl_parent`, only forms ChEMBL links to the same parent are merged. Weaker ChEMBL synonym types (OTHER, DCF, BNF, INN_SPANISH) are not used to assign a year; those ingredients are listed in `no_entry.md` under "weak synonym, pending hand-check" until they are checked by hand.
2. **Name matching.** Names are compared after a small, documented clean-up, so the same ingredient is not missed because of typography or a manufacturing qualifier:
   - In EMA's medicines list, iodine-123 is often written `(123l)` with a letter L; that is treated as `(123I)`.
   - Parenthetical `(rDNA)` and `(activated)` are ignored for matching only, so "parathyroid hormone (rDNA)" matches "parathyroid hormone", and "drotrecogin alfa (activated)" matches Purple Book "drotrecogin alfa". Species or source phrases such as "(human recombinant)" or "(bovine)" are not stripped.
   - "Albumin (Human)" and "Albumin Human" are treated as the same name (Purple Book vs ChEMBL / Drugs@FDA). The word "concentrate" is ignored, so "Fibrinogen Concentrate (Human)" matches "Fibrinogen (Human)".
3. **US year, small-molecule and CDER products.** Drugs@FDA, read from the openFDA `drug/drugsfda` bulk export. Only NDA and BLA applications count (no ANDAs). The date is the approval date of the application's ORIGINAL submission (`submission_type` ORIG, status AP); supplements do not count. The application must contain a product whose only active ingredient is this ingredient. Source = the Drugs@FDA application page (`accessdata.fda.gov/scripts/cder/daf/...ApplNo=`).
4. **US year, biologics (CBER and CDER).** The FDA Purple Book (monthly data download, October 2026 file). Only rows with Submission Type "Original" and License Type 351(a) count; the date is the Approval Date of the earliest such row for the BLA. This includes CDER therapeutic biologics, including pre-2006 BLAs that Drugs@FDA omits (for example Xigris, BLA 125029, voluntarily revoked). A BLA whose Original row is not in the Purple Book gives no date (nothing is guessed). Blood-factor products have US proper names that differ from the INN (for example "Antihemophilic Factor (Recombinant)" for octocog alfa), so for these the ChEMBL id is tied to its BLA numbers in `purplebook_aliases.json`, with the INN/brand evidence written there. The Purple Book has no stable page per product, so its source link is the Purple Book advanced search with the BLA number as the query (`purplebooksearch.fda.gov/advanced-search?query=<BLA number>`); the BLA number is in the link. When Drugs@FDA and the Purple Book give the same date, Drugs@FDA is used.
5. **EU year.** EMA's published medicines list (`medicines-output-medicines-report_en.xlsx`), human medicines, centrally authorised only. The date is the "Marketing authorisation date". Single-substance medicines only. Withdrawn, lapsed, expired, revoked and suspended authorisations are in this list and count (for example Preotact, Xigris, Natpar). Source = the medicine's EPAR page on ema.europa.eu.
6. **Region.** Whichever year is earlier. If both are the same year, US. If only one exists, that one. (`build.py` has one switch, `REGION_RULE`, to produce US-only instead.)
7. **No entry.** If neither exists, the ingredient has no entry. Nothing is guessed. The list is in `no_entry.md`. An old product whose original approval date is not in Drugs@FDA or the Purple Book is not given a later product's year. ANDAs are never used as the year; a file of 21 ingredients where an ANDA is dated earlier than the NDA/BLA we used (`anda_earlier_than_nda.csv`) is kept for review and was not applied, because many 1960s antibiotic "ANDAs" are the historical original approvals.

## Known limits

- Drugs@FDA covers medicines reviewed by FDA's CDER. Plasma-derived products, vaccines and gene therapies are licensed by CBER and are read from the Purple Book instead; very old CBER licences are as recorded there. Some pre-2006 CDER BLAs are absent from Drugs@FDA and are read from the Purple Book instead.
- Very old US approvals are as recorded in Drugs@FDA. Some pre-1982 products are missing from the openFDA Drugs@FDA export, or appear only as ANDAs with no dated original NDA. Wydase (hyaluronidase, NDA 006343) is not in Drugs@FDA or the Purple Book (openFDA returns no match). Secondary FDA documents disagree on the date (a 2007 FDA testimony says 1948; the 2005 Hydase review says March 1950), so no year is assigned to animal-derived hyaluronidase. The Moonlight card is hyaluronidase (human recombinant) / vorhyaluronidase alfa, whose first dated approval in these sources is Hylenex, BLA 021859, 2 December 2005.
- Medicines approved only nationally in the EU, or only in countries such as Japan, have no entry.
- Under `chembl_parent`, a salt is missed if ChEMBL does not list that salt as a form of the parent (fitusiran sodium is the audited example).

## Data versions used

- openFDA drugsfda export dated 2026-11-25 (https://download.open.fda.gov/drug/drugsfda/drug-drugsfda-0001-of-0001.json.zip)
- FDA Purple Book monthly data download, October 2026 (https://www.accessdata.fda.gov/drugsatfda_docs/PurpleBook/2026/purplebook-search-October-data-download.csv)
- EMA medicines list generated 26/11/2026 06:00 (https://www.ema.europa.eu/en/documents/report/medicines-output-medicines-report_en.xlsx)
- ChEMBL API (https://www.ebi.ac.uk/chembl/api/data/), read 26 Nov 2026
- The list of Approved cards is read from the live Moonlight API (`/api/clues?disease_id=...`, read-only) on 26 Nov 2026.
