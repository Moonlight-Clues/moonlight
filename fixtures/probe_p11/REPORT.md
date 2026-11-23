# Night order 2, study P11: what the older "Withdrawn" flag hides

Read-only study, 23 Nov 2026. Nothing in `moonlight/`, `web/` or `tests/` was changed. Open Targets was not asked anything. **No number here is to be said in public.** Nothing here is labelled right or wrong.

## The short answer

With today's code and the answers saved on 21 Nov, the older flag keeps **88** cards off the Approved tab, across the 50 diseases. They are **76** different medicines (11 of them are hidden on more than one disease). **26** of the 50 diseases have at least one; 24 have none.

| Where the card would be | Cards hidden |
|---|---|
| Approved, main list | 35 |
| Approved, narrower-disease box | 11 |
| Approved, wider-group box | 42 |
| **Total** | **88** |

For scale: the Approved tab shows 1132 / 143 / 524 cards today (main / narrower / wider). Without the flag it would show 1167 / 154 / 566. No other Approved card would move or vanish.

None of the 88 has any card anywhere on the page today. None was added by hand.

### The 35 main-list cards, by what the disease's own list says

| The disease's own list holds | Cards |
|---|---|
| an APPROVAL report, and no WITHDRAWAL report | 26 |
| an APPROVAL report and a WITHDRAWAL report | 1 |
| no APPROVAL report, only a WITHDRAWAL report | 8 |

Of the 27 with an APPROVAL report, **8** have one from a regulator (`DailyMed`, `FDA`, `EMA Human Drugs` or `PMDA`, as `fetch.py` reads `source`). The other 19 have approval reports only from `TTD` and `ATC`: 13 from `TTD` alone, 3 from `ATC` alone, 3 from both.

The 9 WITHDRAWAL reports come from `TTD` (6) and `EMA Human Drugs` (3).

### The 53 box cards

A box card comes from a parent's or child's list, so the CSV gives two answers: the searched disease's own list, and the list the card came from.

- On the searched disease's own list: 7 of the 53 are there, all with a trial stage or `UNKNOWN`. None has an APPROVAL or WITHDRAWAL report on it. The other 46 are not on it.
- On the list the card came from: approval reports from `ATC` only for 37, `TTD` only for 9, both for 1, `DailyMed` for 4, and no APPROVAL report at all for 2. Three have a WITHDRAWAL report there (all `TTD`).

## The ten diseases with the most hidden medicines

| Disease | Hidden | Main list | Narrower box | Wider-group box |
|---|---|---|---|---|
| rheumatoid arthritis | 17 | 3 | 0 | 14 |
| depressive disorder | 11 | 6 | 5 | 0 |
| atopic eczema | 8 | 0 | 1 | 7 |
| psoriasis | 7 | 2 | 1 | 4 |
| type 2 diabetes mellitus | 6 | 1 | 0 | 5 |
| schizophrenia | 5 | 3 | 0 | 2 |
| asthma | 4 | 4 | 0 | 0 |
| gout | 4 | 3 | 0 | 1 |
| atrial fibrillation | 4 | 1 | 0 | 3 |
| chronic obstructive pulmonary disease | 3 | 2 | 1 | 0 |

Every disease's count is in `summary.json` (`per_disease`).

## The warning itself: country, year, description

**The saved answers do not hold them.** Moonlight's questions ask for one field of a warning, `warningType`, and nothing else. I checked every warning entry in every saved answer the study read (22,118 entries): `warningType` is the only field. So for 86 of the 88 rows the CSV says "the saved answers do not hold it". I stopped there and did not fetch.

One exception, clearly marked in the CSV. On 15 Nov six medicines were asked about in full, and those answers are in `fixtures/withdrawn_probe/` on main. One of the six, nomifensine, is among the hidden medicines (2 rows). For it the older answer says: country "Worldwide", year 1986, and three descriptions about a blood illness (haemolytic anaemia), allergic reactions and liver harm. That answer is from a different day than the baseline.

What the saved answers do say about the flag:

- Which molecule carries it (column `flag_is_on`): the medicine, one of its tablet forms, or both.
- Where Moonlight saw it (column `flag_seen_in`): the disease's own list, a protein's list, a parent's or child's list.
- For 16 of the 88, the same medicine also carries a second warning type, `Black Box Warning`. For 72 the only type is `Withdrawn`.

**The flag is on the medicine, not on a disease.** It does not say for which use, in which country, or whether the medicine came back later. That is why it cannot sort the cards by itself.

## How I counted

1. The 50 diseases are `fixtures/probe_p5/diseases.json` on branch `probe-baseline` (commit `3bc6dac`), data version 26.09. Read with `git show`. Nothing was merged or copied.
2. `count.py` does what `api.py`'s `_find` does, with today's code (commit `a868539`, the last change to `moonlight/`): `fetch_disease`, `fetch_targets` (top 25), `find_clues`, `fetch_approved`, `fetch_withdrawn`, `fetch_neighbours`, `fetch_listed_medicines`, `added_by_hand`, then `sort_into_tabs`.
3. Every question is answered from the saved answers through `fetch._post_json`, the same function the tests swap. Where the baseline saved two different answers to one question, the fuller one is used, as Moonlight does. `fetch._send` is swapped for a function that only raises an error, so the network cannot be reached. All 50 diseases found every answer they needed; 1439 saved answers were read.
4. Each disease is sorted twice. Run 1: as it is. Run 2: `_was_withdrawn` is made to say False wherever it says True. "Not said" stays "not said". Nothing else differs.
5. Hidden = has a card on the Approved tab (main list, narrower box, wider-group box) in run 2 and none in run 1. A medicine and its tablet forms are one item, as everywhere.
6. Reports are read from the raw rows of the list, all forms of the medicine together. An APPROVAL report is a report whose `clinicalStage` is `APPROVAL`; a WITHDRAWAL report is one whose `clinicalStage` is `WITHDRAWAL`; the source is its `source` field.

A check that the replay is faithful: run 1's Approved card counts match the baseline's for 49 of 50 diseases. The one difference is Huntington disease, where valbenazine moved from the wider-group box to the main list. That is today's hand-written approval (ticket 2.32), so it is expected.

## For Kashish: five examples

Think of the older flag as a red sticker on a medicine's box. The sticker says only one word: "Withdrawn". It does not say where, when or why. Moonlight sees the sticker and leaves the whole box out. Here are five boxes it leaves out.

1. **Zimeldine, for depressive disorder** (main list). The disease's list has no approval report for it at all, only a withdrawal report, from `TTD`. Here the sticker and the list tell the same story.
2. **Nomifensine, for depressive disorder** (narrower box, from major depressive disorder). This is the only medicine where we can read the sticker's small print, from the older saved answer: withdrawn worldwide, 1986, because of a dangerous blood illness. Its approval report comes from `ATC` only.
3. **Ketoconazole, for Cushing syndrome** (main list). The list has an approval report from a regulator, `EMA Human Drugs`, and no withdrawal report. The sticker is on the medicine all the same. The saved answers do not say what the sticker was about.
4. **Rosiglitazone, for type 2 diabetes** (main list). The list has both: approval reports from `DailyMed` and `FDA`, and a withdrawal report from `EMA Human Drugs`. Two offices, two different stories, on one list.
5. **Gemtuzumab ozogamicin, for acute myeloid leukemia** (main list; also hidden in the wider-group box of chronic myeloid leukemia). The list has an approval report from `EMA Human Drugs` and no withdrawal report.

Examples 1 and 2 look like medicines the flag is right to hide. Examples 3, 4 and 5 look like medicines a doctor might expect to see. **But I cannot tell which is which from the data alone.** The data holds the sticker and the reports, not the reason. A person, or the medicine's official label, has to say. All 88 are in the CSV for whoever does that reading.

One thing I noticed and did not act on: since ticket 2.31, a card with a WITHDRAWAL report stays and carries a line. The older flag still removes cards whose list has a regulator's approval report and no withdrawal report. Those two rules pull in different directions for the same kind of medicine. Whether that is wrong is Kashish's decision. I changed nothing.

## What this study did not look at

- Medicines the flag keeps out of In trials, New clues and the two boxes under In trials. The order asked about the Approved tab only.
- Whether any of the 88 really is, or is not, used for the disease today. No label was read.
- What Open Targets says today. The answers are from 21 Nov (data version 26.09).

## Files

- `hidden_by_old_flag.csv`: one row per medicine and disease, 88 rows.
- `count.py`: makes the CSV and `summary.json`. Run from the repo root: `python3 fixtures/probe_p11/count.py`.
- `summary.json`: every total in this report, and the count for each disease.
