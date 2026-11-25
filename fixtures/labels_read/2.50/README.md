# fixtures/labels_read/2.50: Roctavian for haemophilia A (reported error E36)

Ticket 2.50, read on 2026-11-25 (Open Targets data 26.09). Roctavian is
valoctocogene roxaparvovec, CHEMBL4297579. Its id was confirmed on the live
API: a drug search for "roctavian" gives exactly one hit, CHEMBL4297579
"VALOCTOCOGENE ROXAPARVOVEC".

## What the page showed before this ticket

Live `/api/clues` for MONDO_0010602, saved as `page_answers/MONDO_0010602.clues.json`
(made on main at 05c7004, before the change):

- Tab: Approved, main list (not in a folded box, not in In trials).
- Grey line: none. No withdrawal line, no "only some people" line, no
  hand-added line.
- Source link: https://www.fda.gov/media/169937/download?attachment (the FDA
  package insert).

The disease's own list, asked live with fetch.py's DISEASE_DRUGS_QUERY:
`disease_drugs/MONDO_0010602.response.json`. Roctavian's row: stage APPROVAL,
`drugWarnings` empty, and ten reports (FDA APPROVAL, TTD and ClinicalTrials.gov
trials, and one "EMA Human Drugs" report with stage UNKNOWN). None has the stage
WITHDRAWAL.

## What was read

`labels/`:

- `roctavian-fda-package-insert.txt`: the current FDA label (Revised 06/2023).
  DailyMed has no Roctavian page (search and SPL service, no result).
- `roctavian-fda-product-page.txt`: FDA's product page, same indication. It
  says nothing of a withdrawal. No FDA revocation notice was found.
- `roctavian-ema-epar.txt`: EMA's page for the 2022 authorisation. It still
  says "Authorised" and was last updated 14/01/2026, before the Commission's
  decision below.
- `roctavian-ema-application-withdrawn-2020.txt`: the EMA link Open Targets
  gives (`.../EPAR/roctavian-0`). It is about BioMarin's FIRST application,
  withdrawn on 4 November 2020, before any approval. It is not a market
  withdrawal, but its page header says "Application withdrawn".

`withdrawal/`:

- `biomarin-statement-2026-02-23.txt`: the maker's own statement, 23 February
  2026: "BioMarin Pharmaceutical Inc. today announced that it will voluntarily
  remove ROCTAVIAN® (valoctocogene roxaparvovec-rvox) from the market."
  https://www.biomarin.com/news/company-statements/biomarin-voluntarily-withdraws-roctavian-from-the-market/
- `european-commission-decision-c-2026-3038.txt`: the regulator's own record.
  Commission Implementing Decision C(2026) 3038 of 30 April 2026 withdraws the
  EU authorisation at BioMarin's request, "with effect from 29 May 2026".
  https://ec.europa.eu/health/documents/community-register/2026/20260430169677/dec_169677_en.pdf

## One line

card | what the page shows | quoted sentence | link | change
---|---|---|---|---
Roctavian, valoctocogene roxaparvovec (CHEMBL4297579), haemophilia A (MONDO_0010602) | Approved tab, main list; no grey line; source link the FDA package insert | ROCTAVIAN is an adeno-associated virus vector-based gene therapy indicated for the treatment of adults with severe hemophilia A (congenital factor VIII deficiency with factor VIII activity < 1 IU/dL) without antibodies to adeno-associated virus serotype 5 (AAV5) detected by an FDA-approved test. | https://www.fda.gov/media/169937/download?attachment | added to moonlight/limits.json (label requires a test result): the card now carries "The label covers only some people with this disease."

## Reported, not changed: the withdrawal

The regulator's own record (European Commission, 30 April 2026) and the maker's
statement (23 February 2026) show the withdrawal. The withdrawal line (ticket
2.31) comes only from Open Targets: a report with stage WITHDRAWAL on the
disease's list, or the older "Withdrawn" warning flag. Open Targets 26.09 has
neither for Roctavian. So the card shows no withdrawal line, and nothing was
changed. No existing rule lets a hand-written list add the line or hide the
card. If Kashish wants one, that is a new rule. Open Targets may show it in a
later release.

Also seen, not changed: the card's protein is F9 (factor IX), though Roctavian
carries the factor VIII gene. That is how the database links it.
