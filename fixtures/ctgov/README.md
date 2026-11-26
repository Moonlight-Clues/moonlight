# fixtures/ctgov: saved ClinicalTrials.gov trials for ticket T1

Fetched once on 2026-11-26 from the public v2 API, one study per file:

    https://clinicaltrials.gov/api/v2/studies/<NCT id>?fields=NCTId,BriefTitle,OverallStatus,StudyType,Phase,CompletionDate,CompletionDateType,ArmGroupLabel,ArmGroupType,ArmGroupInterventionName,InterventionType,InterventionName,InterventionArmGroupLabel

The bytes are the API's answer for those fields. Nothing was edited.
The reader tests never fetch them again.

Each file is here for one gap in the reader's contract:

- NCT06758557 recruiting, estimated end, phases PHASE1 then PHASE2
- NCT07911579 not yet recruiting
- NCT01841723 active, not recruiting, one phase
- NCT05477862 invitation only, one medicine in two experimental groups
- NCT04123561 finished, actual end, a drug in both groups, a comparator-only drug, a placebo comparator under its own name
- NCT01340183 paused, a placebo group, a year-and-month date
- NCT00789659 withdrawn before starting
- NCT00645580 status unknown
- NCT02733523 no completion date
- NCT04118153 early phase 1
- NCT02006251 stopped early, no phases, a procedure in both groups
- NCT00188396 arms module present, no arm groups, a named medicine
- NCT03208946 a sham comparison group
- NCT03876223 observational, so the reader leaves it out
- NCT04921956 expanded access, so the reader leaves it out
