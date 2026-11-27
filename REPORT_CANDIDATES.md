# Report-number candidates

A person has checked this list. `"report"` is written on the eight entries marked **added**. Every other entry here is **pending a planner decision** and has no `report` field. No id was changed.

How the list was made: every pull request title and body on Moonlight-Clues/moonlight (151 pull requests), and every commit message, was searched for a number like E36. An entry is here only when that record names the number and the entry together. If a number was not tied to an entry, it is left out.

Left out of the original list on purpose: pull request 72 names E16 (hydrocortisone, Addison disease) and says SKIPPED, so no entry was added. The same pull request's 14 red warnings are not given E numbers.

## E36

- **C-152** — `limits.json`: Roctavian, CHEMBL4297579, haemophilia A, MONDO_0010602. **Pending a planner decision.** No `report` field.
- Evidence: [pull request 88](https://github.com/Moonlight-Clues/moonlight/pull/88). Quote: "Ticket 2.50, reported error E36." and "`moonlight/limits.json` gets an entry for Roctavian and haemophilia A."

- **C-186** — `withdrawals.json`: Roctavian, CHEMBL4297579, haemophilia A, MONDO_0010602. **Pending a planner decision.** No `report` field. This is the withdrawal row, not the limits row above.

## E17

- **C-219** — `confirmed.json`: Givosiran, CHEMBL4297760, acute hepatic porphyria, Orphanet_95157. **Added** `"report": "E17"`.
- Evidence: [pull request 110](https://github.com/Moonlight-Clues/moonlight/pull/110), title "Ticket 2.61: givosiran on acute hepatic porphyria (E17, part)". Quote: "`moonlight/confirmed.json`: +1 row (33 -> 34), Givosiran / Orphanet_95157".

## E4, E6, E8, E11, E14

These numbers are the item labels in [pull request 72](https://github.com/Moonlight-Clues/moonlight/pull/72), in the table under "Part B". Each line below is quoted from that table, and the entry is the one that pull request added.

- **C-059** — `approvals.json`: Delandistrogene moxeparvovec (Elevidys), CHEMBL4650241, Duchenne muscular dystrophy, MONDO_0010679, `limited`: true. Report **E4**. **Added** `"report": "E4"`. Quote: "E4 Elevidys, DMD `MONDO_0010679` | ADDED with `limited: true`."
- **C-060** — `approvals.json`: Corticotropin (Acthar), CHEMBL1201610, dermatomyositis, MONDO_0016367. Report **E6**. **Added** `"report": "E6"`. Quote: "E6 Acthar (Corticotropin `CHEMBL1201610`), dermatomyositis `MONDO_0016367` | ADDED."
- **C-055** — `approvals.json`: Ravulizumab, CHEMBL3989986, myasthenia gravis, MONDO_0009688, `limited`: true. Report **E8**. **Added** `"report": "E8"`. Quote: "E8 Ravulizumab, myasthenia gravis | ADDED, `limited`".
- **C-056** — `approvals.json`: Ravulizumab, CHEMBL3989986, atypical hemolytic-uremic syndrome, MONDO_0016244. Report **E11**. **Added** `"report": "E11"`. Quote: "E11 Ravulizumab, aHUS `MONDO_0016244` | ADDED".
- **C-057** — `approvals.json`: Dupilumab, CHEMBL2108675, eosinophilic esophagitis, MONDO_0005361. Report **E14**. **Added** `"report": "E14"`. Quote: "E14 Dupilumab, EoE `MONDO_0005361` | ADDED".
- **C-058** — `approvals.json`: Budesonide, CHEMBL1370, eosinophilic esophagitis, MONDO_0005361. Report **E14**. **Added** `"report": "E14"`. Quote: "E14 Budesonide (Eohilia), EoE | ADDED".

## E52

[Pull request 114](https://github.com/Moonlight-Clues/moonlight/pull/114), title "Ticket 3.23: one card per medicine when Open Targets misses a salt form's parent (E52)". Quote: "`moonlight/salt_parents.json` (new): hand list of **10** salt -> parent pairs." Commit [738b28f](https://github.com/Moonlight-Clues/moonlight/commit/738b28f) has the same words in its subject.

- **C-278** — salt CHEMBL4594265, parent Givosiran CHEMBL4297760. **Added** `"report": "E52"`.
- **C-279** — salt CHEMBL4297536, parent Patisiran CHEMBL3989987. **Pending a planner decision.** No `report` field.
- **C-280** — salt CHEMBL4594335, parent Eplontersen CHEMBL4594334. **Pending a planner decision.** No `report` field.
- **C-281** — salt CHEMBL5095303, parent Vutrisiran CHEMBL4594511. **Pending a planner decision.** No `report` field.
- **C-282** — salt CHEMBL5315048, parent Zilucoplan CHEMBL4298207. **Pending a planner decision.** No `report` field.
- **C-283** — salt CHEMBL3707226, parent Defibrotide CHEMBL2108396. **Pending a planner decision.** No `report` field.
- **C-284** — salt CHEMBL4298005, parent Mitiglinide CHEMBL471498. **Pending a planner decision.** No `report` field.
- **C-285** — salt CHEMBL4297658, parent Ipragliflozin CHEMBL2018096. **Pending a planner decision.** No `report` field.
- **C-286** — salt CHEMBL3545432, parent Ixazomib CHEMBL2141296. **Pending a planner decision.** No `report` field.
- **C-287** — salt CHEMBL87992, parent Eslicarbazepine CHEMBL315985. **Pending a planner decision.** No `report` field.
