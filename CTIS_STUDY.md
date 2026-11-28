# CTIS study: can Moonlight read the EU trial register, and how?

Research only. No code changed, nothing committed. All counts were made on
28 Nov 2026 unless a line says otherwise. "CTIS" is the EU register at
euclinicaltrials.eu. "CT.gov" is ClinicalTrials.gov.

Short answer: yes, it can be read, and reuse with credit is allowed. But there
is no official API, the "recruiting" label is not always true, and four out of
five recruiting CTIS trials in my sample are already on CT.gov.

## How I tested

- About 245 requests to euclinicaltrials.eu in total, one at a time, 1.5 to 3
  seconds apart: 25 search calls, 201 single-trial calls, about 17 page and
  script files, and one page load in a browser. No errors, no throttling seen.
- About 215 requests to the CT.gov API and 30 to Open Targets.
- Sample: 200 trials drawn at random (fixed seed) from the 4,754 CTIS trials
  whose overall status is a "recruiting" one.

## 1. Access

| Question | Finding | Evidence |
|---|---|---|
| Official API? | No. EMA slides of 22 Oct 2024 list "there should be an accessible API" as "Not yet!". | [EMA slides](https://www.ema.europa.eu/en/documents/presentation/presentation-session-1-new-ctis-transparency-rules-policy-reality-scotti-francesca_en.pdf) |
| Official routes | Download search results as .csv, download one trial, RSS feed. No row limit stated. | [Search tips](https://euclinicaltrials.eu/search-tips-and-guidance/) |
| What works in practice | The site's own data service answers plain requests with JSON, no key: `POST /ctis-public-api/search` and `GET /ctis-public-api/retrieve/{number}`. It is not documented by EMA. | My requests, HTTP 200 |
| Is it established use? | Yes. The R package ctrdata reads the same two addresses. CTIS also feeds the WHO registry. | [ctrdata source](https://raw.githubusercontent.com/rfhb/ctrdata/master/R/ctrLoadQueryIntoDbCtis.R) |
| robots file | None. `/robots.txt` returns 404. | My request |
| Terms of reuse | The site has no legal notice of its own (`/legal-notice/` is 404). Its footer says "© European Medicines Agency". The EMA legal notice allows reuse, commercial or not, "provided that EMA is always acknowledged as the source". This does not cover third-party content (sponsor documents) or the EMA logo. | [EMA legal notice](https://www.ema.europa.eu/en/about-us/legal-notice) |
| Rate limits | None stated. ctrdata's changelog mentions throttled CTIS answers. A search page of 500 rows answered in 2.5 seconds. | [ctrdata NEWS](https://raw.githubusercontent.com/rfhb/ctrdata/master/NEWS.md) |

So this is not scraping against the terms. It is reading an undocumented
service, with reuse allowed if EMA is credited. Two cautions: EMA can change
the service without notice, and it is an inference (from the footer) that the
EMA notice covers this site. The terms quotes came through a page-reading
tool; check the wording on the pages before quoting them publicly.

Sample record (trimmed; the full 64 KB record is not in the repo):

```json
{"ctNumber": "2025-524380-20-00", "ctStatus": "Authorised", "ctPublicStatusCode": 2,
 "publicTitle": "Imaging to Re-evaluate Elacestrant cliNical Application",
 "trialPhase": "Therapeutic exploratory (Phase II)", "sponsor": "Institut Jules Bordet",
 "medicalCondition": "ER-positive, HER2-negative advanced or metastatic breast cancer",
 "meddraConditionTerms": [{"termName": "Metastatic breast cancer", "level": "LLT",
                           "classificationCode": "10027475", "version": "27.0"}],
 "products": [{"productName": "ORSERDU 345 mg film-coated tablets", "activeSubstanceName": "ELACESTRANT"}],
 "estimatedRecruitmentStartDate": "2026-11-30", "estimatedEndDate": "2029-07-14",
 "memberStatesConcerned": [{"mscName": "France", "mscPublicStatusCode": 2}],
 "lastPublicationUpdate": "27/11/2026"}
```

## 2. Fields

Checked on the 200 full records.

| Field | Available? | Where, and how often |
|---|---|---|
| EU trial number | Yes | `ctNumber`, 200 of 200 |
| Title | Yes | `publicTitle`, `fullTitle`, `shortTitle`, with translations |
| Phase | Yes | `trialPhase`, in the EU's own words ("Therapeutic exploratory (Phase II)") |
| Overall status | Yes | `ctPublicStatusCode`, 1 to 12 |
| Status per country | Yes | one code per country, in the search row and the full record |
| Recruitment dates | Partly | Estimated start: 200 of 200. Real start date per country: 188 of 200. End of recruitment per country when it has happened. |
| Condition, free text | Yes | 200 of 200, but often a sentence about patients, not a disease name |
| Condition, MedDRA code | Partly | 125 of 200. 75 have none. |
| Medicine and substance | Mostly | product name 200; active substance 170 of 200 |
| Sponsor | Yes | 200 of 200 |
| Countries | Yes | 200 of 200 |
| Sites | Yes | 200 of 200, with address and a named investigator with phone and email |
| Public contact | Yes | sponsor "public contact" in 200 of 200 |
| Link to the trial page | Yes | `https://euclinicaltrials.eu/ctis-public/view/{number}` (route seen in the site's script; I did not load one) |
| NCT number | Partly | a set field, filled in 64 of 200 |

The search row has no NCT number and no MedDRA code. Those need one extra
request per trial.

## 3. Volume

Source: the search service's own `totalRecords`, one call per status code.

| Code | The site's label | Trials |
|---|---|---|
| 1 | Under evaluation | 5 |
| 2 | Authorised, recruitment pending | 1,354 |
| 3 | Authorised, recruiting | 797 |
| 4 | Ongoing, recruiting | 3,957 |
| 5 | Ongoing, recruitment ended | 2,215 |
| 6 | Temporarily halted | 117 |
| 7 | Suspended | 3 |
| 8 | Ended | 4,252 |
| 9 | Expired | 12 |
| 10 | Revoked | 1 |
| 11 | Not authorised | 225 |
| | **All public trials** | **12,938** |

- Recruiting now (codes 3 and 4): **4,754** trials.
- Countries with at least one of them recruiting there: **28**. Most: Spain
  1,606, France 1,596, Germany 1,221, Italy 1,195. Fewest: Cyprus 3,
  Luxembourg 3.
- Warning: 201 of the 4,754 have no country marked recruiting. In the sample,
  12 of 29 "Authorised, recruiting" trials had not started recruiting in any
  country. The label is not safe to trust alone.

## 4. Overlap with ClinicalTrials.gov

Sample of 200 recruiting CTIS trials.

| Step | Trials | How found |
|---|---|---|
| CTIS record carries an NCT number | 64 | set field in the record; all 64 exist on CT.gov |
| No NCT in CTIS, but CT.gov lists the EU number | 59 | CT.gov search by the EU number |
| No shared number at all, but same trial on CT.gov | 32 | CT.gov search by the CTIS short title, then sponsor and title checked by eye (2 false hits thrown out) |
| **On CT.gov** | **155 (77.5%)** | |
| **Not found on CT.gov (EU-only)** | **45 (22.5%)** | an upper limit, see "could not verify" |
| Already in trials.sqlite | 106 (53%) | 51 + 31 + 24 of the three rows above |

- If the sample holds for all 4,754, EU-only is about 1,070 trials. That is an
  estimate from a sample, not a count (roughly 17% to 29%).
- Only 64 of 200 carry an NCT number, so "has no NCT number" is a bad test for
  "EU-only". It would wrongly call 91 trials EU-only.
- A second gap showed up: 49 sample trials are on CT.gov but not in
  trials.sqlite, because Open Targets 26.09 has not linked them to a disease.
- The two registers disagree on status. The 155 trials match 156 CT.gov
  records: 117 RECRUITING, 14 not yet recruiting, 12 active not recruiting,
  7 unknown, 4 by invitation, 2 completed.

Reverse check: does CT.gov list the EU number? Sometimes.

- CT.gov has a secondary-ID type "CTIS" ("EU Trial (CTIS) Number"), used by
  2,495 studies (CT.gov's own field count, 28 Nov 2026).
- In the sample, 78 of the 155 shared trials list the EU number on CT.gov.
  For the 19 I could type-check: 10 under "CTIS", 5 under "OTHER", 4 under
  "REGISTRY". So the number must be searched in every secondary ID, not one type.

## 5. Linking to diseases

Simple approach tested: take each MedDRA term name on the CTIS record, ask
Open Targets' disease search, and accept a disease only if its name, an exact
synonym, or a MedDRA cross-reference matches the term exactly. No fuzzy match.
No use of the free text.

Result on 50 trials (every fourth of the sample), judged by me by reading:

| Outcome | Trials |
|---|---|
| Mapped, correct | 20 |
| Mapped, wrong | 0 |
| Not mapped | 30 |

- Of the 30 not mapped: 18 have no MedDRA term at all (3 of them are healthy
  volunteers or have no disease); 12 have a term with no exact match
  ("Advanced breast cancer", "Eosinophilic asthma", "Solid tumor").
- 2 of the 20 correct links are wider than the trial (a trial for one gene
  form of retinitis pigmentosa lands on "retinitis pigmentosa").
- This fits the rule that wrong is worse than missing: it stays silent on 60%.
- For trials that are also on CT.gov, no mapping is needed: use the disease
  link Open Targets already gives the NCT number.
- A second pass could add a hand-checked list of the commonest unmatched
  terms. I would not match the free text by machine.

## 6. Duplicates: proposed rule

A CTIS trial and a CT.gov study are the same trial if any of these is true:

1. The CTIS record's NCT number equals the CT.gov number.
2. The EU number (pattern `20NN-5NNNNN-NN`, with or without the last `-NN`)
   appears in any CT.gov secondary ID, whatever its type.
3. The CTIS short title equals the CT.gov sponsor study ID or acronym, and
   the sponsors match. These pairs go to a list checked by hand before use.

When they are the same: show one row, the CT.gov one, since it has the
disease link, and add "Also in the EU register" with the EU link. A CTIS
trial is shown as EU-only only when all three tests fail. If rule 3 gives a
maybe, do not show the CTIS row.

## 7. Freshness and size

- CTIS changes daily. Of the 4,754 recruiting trials, 154 had a publication
  update in the last day, 480 in the last 7 days, 1,397 in the last 30 days.
- Moonlight already hides the panel when its file is over 14 days old. A
  weekly read fits. The first full read is 10 search calls plus 4,754
  single-trial calls, about 2 hours at one call per 1.5 seconds. After that,
  about 500 calls a week.
- Size. trials.sqlite is 49,065,984 bytes; the limit is 52,428,800. That
  leaves 3.4 MB. A slim CTIS row (number, title, phase, status per country,
  conditions, substances, sponsor) compressed to 317 bytes on average.
  - EU-only recruiting, about 1,070 trials: about 0.4 MB.
  - All recruiting, 4,754: about 1.5 MB.
  - All 12,938: about 4.1 MB. This does not fit.
- Store it in its own file, `moonlight/ctis.sqlite`, with its own build
  script and its own "checked" date. Keep trials.sqlite untouched.

## 8. Risks

- **Status can mislead.** "Recruiting" in CTIS sometimes means recruiting has
  not begun, and it often differs from CT.gov. A patient could travel for a
  trial that is not open. Show a country only when that country has a real
  recruitment start date and no end date, and always say "check with the site".
- **Personal data.** Every record names site investigators with phone and
  email. Moonlight should store none of it and link to the EU page instead,
  as it does for CT.gov.
- **Undocumented service.** It can change or block us any day. The build must
  fail loudly and keep the last good file.
- **Terms.** Reuse needs "Source: EMA" credit. Sponsor documents are
  third-party; do not copy them. MedDRA term names are licensed by another
  body; I did not check whether showing or storing them needs a licence.
- **Data quality.** Conditions are free text with typos ("Dupuytren
  Concrature", "Acute Myeloid Luekemia"). 37.5% have no MedDRA code. 15% have
  no active substance name.
- **Hidden duplicates.** 32 of 200 trials are on both registers with no shared
  number. A weak rule shows the same trial twice.
- **Project rule.** CLAUDE.md allows two machine sources: Open Targets and
  "the trials register". CTIS is a second register. That needs Kashish's yes.
- **Phase 1 and healthy-volunteer trials** are in CTIS (about 13% of recruiting
  trials are plain phase 1). They are not for patients looking for treatment.

## Three options

### A. Link out

- **Gain:** European visitors learn the EU register exists and where it is.
  Nothing can go stale or be wrong on our page.
- **Limit found:** I could not make a link that opens the EU search already
  filled in for a condition. The one address form I tried was ignored by the
  site. So the line can only say: search for "<disease name>" under "Medical
  condition" on the EU register.
- **Tickets:**
  1. List of EU/EEA country names as CT.gov spells them. Sonnet 5.5.
  2. API: add the line and link when the picked country is on the list. Sonnet 5.5.
  3. Page: show the line. Sonnet 5.5.
- **Risks:** Low. The visitor has to type the search. The EU site is hard to use.
- **Product lead decides:** the exact words; whether it shows for every
  visitor or only after an EU country is picked.

### B. EU-only trials added

- **Gain:** about 1,070 more recruiting trials overall (estimate), but only
  about 40% of them will map to a disease page, so roughly 400 to 450 show up.
  Each marked "Source: EU Clinical Trials Register (EMA)".
- **Tickets:**
  1. Build script: read CTIS slowly, save answers, write `ctis.sqlite`. Sonnet 5.5.
  2. Same-trial rule (section 6), with the hand-check list. Opus 5.5.
  3. Recruiting-per-country rule from real start and end dates. Opus 5.5.
  4. MedDRA-to-disease exact match, with a test set of hand-judged trials. Opus 5.5.
  5. `ctis.py` reader and merge into `_recruiting`, with source and its own checked date. Sonnet 5.5.
  6. Page: source mark, EU link, wording. Sonnet 5.5.
  7. Weekly refresh and a loud failure when the service changes. Sonnet 5.5.
  8. Fill the nearer gap first: the CT.gov trials missing from trials.sqlite. Opus 5.5 to study, Sonnet 5.5 to build.
- **Risks:** wrong "recruiting" status; missed duplicates; undocumented
  service; MedDRA licence; a new machine source.
- **Product lead decides:** whether CTIS may be a source at all; what counts
  as recruiting; whether phase 1 trials show; how a maybe-duplicate is
  handled; the credit line; who reads the hand-check list.

### C. Full second registry

- **Gain:** EU status per country and EU numbers on every trial, across the
  site, including finished trials.
- **Tickets:** all of B, plus:
  1. Storage redesign; 4.1 MB does not fit beside trials.sqlite. Opus 5.5.
  2. Merge rules when the two registers disagree (status, phase, dates). Opus 5.5.
  3. Map EU phase words and substance names to Moonlight's medicines. Opus 5.5.
  4. Change the In trials boxes and trial counts to use both. Opus 5.5.
  5. Rework the tests and fixtures that assume one register. Sonnet 5.5.
- **Risks:** all of B, larger. It touches the medicine cards, where the safety
  rules live. 77.5% of the recruiting data would be a second copy of what
  CT.gov already gives.
- **Product lead decides:** which register wins a disagreement; whether trial
  counts on cards may change; the size limit.

## Recommendation

Do A now, because it is safe and small, and it is honest about the gap.
Before B, fix the nearer gap this study found: about a quarter of the sampled
trials are on CT.gov but missing from trials.sqlite. Then do B only if
Kashish accepts CTIS as a source and the strict "recruiting" rule; do not do C.

## The one thing I could not verify

Whether the 45 trials I call EU-only are truly absent from CT.gov. Thirty-two
trials had no shared number and were found only by short title, so more may
hide under different titles. 22.5% is a ceiling, not a firm count.

## Five plain sentences

1. Europe keeps its own big list of medicine trials, and Moonlight can read
   it, like borrowing a book from a second library.
2. Most trials on that list are also on the list Moonlight already uses, so
   only about one in five would be new.
3. The two lists often use different numbers for the same trial, like one
   runner wearing two bibs, so we need a careful rule to count each runner once.
4. The European list sometimes says "recruiting" when the doors are not open
   yet, so we must check the real opening date before we show it.
5. The safest first step is a signpost that points to the European list, and
   the bigger step waits for Kashish to decide.
