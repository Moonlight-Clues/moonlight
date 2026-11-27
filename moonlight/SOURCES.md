# Sources for moonlight/approval_years.json

**What the year means:** the year the active ingredient (moiety) was first approved, in any salt or form — earliest US or EU approval, for any use.

It is not the year the medicine was approved for the disease on the page, and it is not a judgement of how good or current the medicine is.

`build.py` has two one-line switches. `REGION_RULE` is `earliest` (default; tie goes to the US) or `us_only`. `ESTER_RULE` is `moiety` (default, and the rule decided by MAIN 5 on 26 Nov 2026 after Product hand-checked all 73 rows where the two rules differ: the moiety rule was right on 70, the ChEMBL-parent rule on none; trailing salt and ester words are stripped from a fixed list) or `chembl_parent` (merge only names ChEMBL links as one parent molecule; esters that are themselves a ChEMBL parent keep their own year). Friday's published table uses `earliest` and `moiety`. The two ester values are compared in `compare_ester_rules.md`.

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

## Hand-checked rows and fixes (26 Nov 2026, MAIN 5 order)

What "First approved" means: the medicine (the active moiety), not the exact salt or ester on the card. For example, a card for hydrocortisone butyrate shows the year hydrocortisone was first approved.

**Strip list.** Three more words were added to the list of trailing salt and ester words, because they hid a same-moiety US record: `phenpropionate` (nandrolone phenpropionate, Durabolin NDA 011891, 30 Oct 1959), `sorbitex` (patiromer sorbitex calcium, Veltassa NDA 205739, 21 Oct 2015) and `kamedoxomil` (azilsartan kamedoxomil, Edarbi NDA 200796, 25 Feb 2011). `mofetil` was added for the same reason (mycophenolate mofetil, CellCept NDA 050722, 1995, now also the year for mycophenolic acid).

**Hand-set years** (FDA gives no date in Drugs@FDA, or the record is not in Drugs@FDA or the Purple Book):

- Teriparatide acetate and teriparatide: 1987, US. Parathar (teriparatide acetate), NDA 019498, Marketing Approval Date 12/23/1987 in the FDA Orphan Drug database (https://www.accessdata.fda.gov/scripts/opdlisting/oopd/detailedIndex.cfm?cfgridkey=14486). Drugs@FDA lists NDA 019498 with no approval date. Forteo (2002) is FDA class Type 3, new dosage form.
- Fibrinogen (human): 1947, US. Citation: *Fibrinogen (Human); Revocation of Licenses*, 43 Fed. Reg. 1131, 1132 (Jan. 6, 1978) (Docket No. 77N-0409; FR Doc. 78-84), notice dated December 27, 1977 by the Associate Commissioner for Compliance, Food and Drug Administration. Page 1132: "Fibrinogen (human) is a biological product that has been licensed since 1947." Page 1131: all licences for fibrinogen (human) were revoked as of December 7, 1977. The notice gives the year only. Link (the whole issue; the notice is on pages 1131 to 1132): https://www.govinfo.gov/content/pkg/FR-1978-01-06/pdf/FR-1978-01-06.pdf

**Entries removed, because no year is supported:**

- Arginine and arginine hydrochloride (two cards): the only dated record is R-Gene 10 (1973), FDA class Type 5 (new formulation), so an earlier approval existed.
- Norethindrone acetate and norethindrone: 1973 (Micronor, Type 3) is later than the Norlutin (NDA 010895) and Norlutate (NDA 012184) applications, which Drugs@FDA lists with no date.
- Edetate disodium: the 1953 record is edetate calcium disodium (Calcium Disodium Versenate, NDA 008922), a different drug.
- Carbinoxamine: the table had 2013 (NDA 022556), but Drugs@FDA lists Clistin (NDA 008955) with a supplement approved 27 Dec 1974, so the original is earlier; the original has no date.

**Entries removed, because the year was probably too late (MAIN 5, 26 Nov 2026).** A year that is probably too late is worse than no year. Drugs@FDA lists some old NDAs with no approval date, so the build cannot use them. 31 entries had an earlier-numbered undated NDA for the same ingredient, so the dated year in the table may have been later than the true first approval. Those 31 rows were dropped. The removed rows are in `fault2_unsure_removed.json` (kept with the build files, not in this repository) for later checking. The original flag list, including the rows that were fixed or reviewed and kept, is `fault2_undated_nda_candidates.csv` in the same folder.

**Not applied.** 13 cards that would gain a new year after a name-word fix were left out, for Product to hand-check. They are in `fault1_new_entry_candidates_NOT_APPLIED.csv` (kept with the build files, not in this repository).

## Known limits

- Drugs@FDA covers medicines reviewed by FDA's CDER. Plasma-derived products, vaccines and gene therapies are licensed by CBER and are read from the Purple Book instead; very old CBER licences are as recorded there. Some pre-2006 CDER BLAs are absent from Drugs@FDA and are read from the Purple Book instead.
- Very old US approvals are as recorded in Drugs@FDA. Some pre-1982 products are missing from the openFDA Drugs@FDA export, or appear only as ANDAs with no dated original NDA. Wydase (hyaluronidase, NDA 006343) is not in Drugs@FDA or the Purple Book (openFDA returns no match). Secondary FDA documents disagree on the date (a 2007 FDA testimony says 1948; the 2005 Hydase review says March 1950), so no year is assigned to animal-derived hyaluronidase. The Moonlight card is hyaluronidase (human recombinant) / vorhyaluronidase alfa, whose first dated approval in these sources is Hylenex, NDA 021859, 2 December 2005 (approved as an NDA; FDA deemed it a BLA on 23 March 2020, so Drugs@FDA now calls it BLA 021859).
- Medicines approved only nationally in the EU, or only in countries such as Japan, have no entry.
- Under `chembl_parent`, a salt is missed if ChEMBL does not list that salt as a form of the parent (fitusiran sodium is the audited example).

# Sources for moonlight/trials.sqlite

Built by `scripts/build_trials.py`. One row for every ClinicalTrials.gov study that Open Targets Platform 26.09 links to a disease (dataset `clinical_report`, a row whose source is ClinicalTrials.gov and that names a disease id). The study text is ClinicalTrials.gov API v2. Observational records and expanded-access records are left out.

Kept interventional studies: 161,149. Open Targets clinical-report NCT ids linked to a disease: 170,575, all found. Run date 2026-11-26. ClinicalTrials.gov API version 2.0.5. ClinicalTrials.gov data timestamp 2026-11-25. File size 38,572,032 bytes.

## Data versions used

- openFDA drugsfda export dated 2026-11-25 (https://download.open.fda.gov/drug/drugsfda/drug-drugsfda-0001-of-0001.json.zip)
- FDA Purple Book monthly data download, October 2026 (https://www.accessdata.fda.gov/drugsatfda_docs/PurpleBook/2026/purplebook-search-October-data-download.csv)
- EMA medicines list generated 26/11/2026 06:00 (https://www.ema.europa.eu/en/documents/report/medicines-output-medicines-report_en.xlsx)
- ChEMBL API (https://www.ebi.ac.uk/chembl/api/data/), read 26 Nov 2026
- The list of Approved cards is read from the live Moonlight API (`/api/clues?disease_id=...`, read-only) on 26 Nov 2026.

# Permanent ids on the hand lists

Every entry of these seven lists carries an `"id"` like `C-001`:

`corrections.json`, `approvals.json`, `limits.json`, `confirmed.json`, `withdrawals.json`, `pmda_summaries.json`, `salt_parents.json`.

The numbers are one sequence across all seven. They were assigned once, in date order. Entries from the same day keep that list order, then the entry's place in its file. A number is never reused and never renumbered.

A new entry takes the next number. Print it with:

```bash
python -m moonlight.correction_ids
```

Write that id on the entry. Do not fill a gap. `fixtures/correction_ids.json` pins each id to the entry, and `tests/test_correction_ids.py` fails if one changes.

# Sources for moonlight/names.json

Built by `scripts/build_names.py`. One name for every medicine id (ChEMBL) and disease id (MONDO, Orphanet, EFO, and the other Open Targets disease prefixes) found in these hand lists: `corrections.json`, `approvals.json`, `limits.json`, `confirmed.json`, `withdrawals.json`, `pmda_summaries.json`, `salt_parents.json`.

The repo's saved Open Targets answers do not hold a name for every one of those ids, so the names were read from the Open Targets Platform GraphQL API (`https://api.platform.opentargets.org/api/v4/graphql`). Before any name is kept, the script reads `meta.dataVersion` and stops unless it is 26.09. A medicine name is `drug(chemblId).name`. A disease name is `disease(efoId).name`. Both are stored as sent. The file's keys are sorted, so a second run writes the same bytes.

`discontinued.json` is empty, so it is not read.
