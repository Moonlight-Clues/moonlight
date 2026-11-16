# fixtures/probe_p2: ticket P2 probes, saved 2026-11-16 (Open Targets data 26.09)

Live answers, saved as sent, only re-indented. Each `.request.json` is the
exact body that was posted. No code in moonlight/ or web/ was changed.
Files are filed by question, then by the id asked about, so no answer is
saved twice.

Moonlight's own questions, word for word from fetch.py:

- `search/<words>.*`: SEARCH_QUERY, size 10. The eight typed words of
  Probe A, and every name Gemini offered for them.
- `disease/<disease id>.*`, `associated_targets/<disease id>.*` (top 25),
  `family/<disease id>.*`: DISEASE_QUERY, TARGETS_QUERY, FAMILY_QUERY.
- `disease_drugs/<disease id>.*`: DISEASE_DRUGS_QUERY for a disease's own
  entry and for every direct parent and child. Asked twice (the ask-twice
  rule), the kept answer saved.
- `target_drugs/<protein id>.*`: TARGET_DRUGS_QUERY. Asked twice, the kept
  answer saved, without indentation because they are large.
- `gemini/names_<words>.*`: translate.py's "which diseases might they
  mean?" request and Gemini's answer (status and JSON body only, never a
  header). `gemini/model_list.*`: the API's model list.

Probe-only questions. Moonlight does not ask these. Asked once.

- `search_size_50/<words>.*`: SEARCH_QUERY with size 50 instead of 10.
- `probe_only/search_paged_multiple_sclerosis_page_<n>.*`: the same search,
  50 at a time, through all 521 matches.
- `probe_only/disease_<id>.*`: one entry with its `therapeuticAreas`,
  synonyms, parents and children. `MONDO_0005301` is not known (null).
- `probe_only/disease_drug_reports_MONDO_0019438.*`: AL amyloidosis' list
  with everything about each report (the question from
  fixtures/approval_proof/).
- `probe_only/target_report_stages/<protein id>.*`: each report on a
  protein's medicines with its `clinicalStage` and `source`.

The ten diseases whose whole page was fetched: MONDO_0004967 acute
lymphoblastic leukemia, MONDO_0019438 AL amyloidosis, MONDO_0019065
amyloidosis, MONDO_0004980 atopic eczema, MONDO_0015924 pulmonary arterial
hypertension, MONDO_0004979 asthma, MONDO_0007254 breast cancer,
MONDO_0005148 type 2 diabetes mellitus, MONDO_0005027 epilepsy,
MONDO_0004975 Alzheimer disease. Also the own entry of EFO_0803536.

What the probes found

- Probe A. Open Targets 26.09 has no entry named "multiple sclerosis". The
  entry that stands for it is EFO_0803536 "multiple sclerosis symptom
  measurement": "multiple sclerosis" is on its exact "also called" list, it
  has 35 approved medicines, and the four kinds of multiple sclerosis sit
  under it. One of its parents is "measurement", so it and all four kinds
  carry "measurement" in `category` next to "nervous system disorder" and
  "immune system disorder". The hide-measurements rule hides all five.
  In 1342 saved search hits, 73 have `category` exactly ["measurement"];
  6 have "measurement" plus other areas: these five and OBA_2050328.
- "Pre-B ALL" gets 0 matches from Open Targets (total 0).
- Probe B. MONDO_0004948 B-cell chronic lymphocytic leukemia is a direct
  child of MONDO_0004967 acute lymphoblastic leukemia in the database.
- AL amyloidosis' own list has 29 rows; two are APPROVAL: tafamidis and
  tafamidis meglumine, one medicine. Their only receipt is one FDA label
  link, whose report names "al amyloidosis", "amyloidosis" and
  "cardiomyopathy".
- Probe C. `clinicalReports` on a protein's medicines came back with a
  different number of reports on repeat asks (PDE5A: 7, 11 and 7 in three
  further asks that were not saved; Moonlight's kept answer has 8).
