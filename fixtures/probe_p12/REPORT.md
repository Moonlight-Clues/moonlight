# Study P12: clutter, duplication and housekeeping (read-only)

Run on 24 Nov 2026, on `main` at `7005d7d` (pull requests 68 and 72 to 76 merged).
Nothing in the app was changed. Everything here is in `fixtures/probe_p12/`.
Every wording on the page is Kashish's. This report only proposes. **K** marks
a proposal that changes page wording, so it needs Kashish's yes.

Branch: this session could only push to `ccr-8f12ff80-i8lssz`, not to
`p12-clutter-study`. It is the closest name allowed. No pull request was opened.

---

## HARM: read these first

**H1. A blood thinner on the haemophilia A Approved tab.** Dicumarol, which stops
blood from clotting, sits in the "Approved for a wider group" box on the
haemophilia A page. Its label says: "Not listed as approved for this exact
disease. Approved for hemorrhagic disease, a wider group the database puts this
disease in." Its only source is TTD (`ttd.idrblab.cn/.../D02TJS`), with the
"no regulator record" line. Rule R1 (ticket 2.43) takes blood thinners out of
New clues only. Its test says it "never touches the Approved tab"
(`tests/test_left_out_r1_r6.py:10`). So a reader with haemophilia A sees a
blood thinner under "Approved". Pentastarch and Ethanolamine Oleate are in the
same box, also from TTD only, and also look odd for haemophilia A. Proposal: a
doctor checks the haemophilia A wider-group box, then a red warning or a hand
left-out entry is added (Kashish decides).
Picture: `pictures/06_haemophiliaA_approved_all_open.jpg`.

**H2. The printed page leaves out two safety lines and puts boxed cards back on
the main list.** In `web/index.html:1286-1296`, `cardLines` prints only
`proof_note` and `warning` under a row. The withdrawal line ("The database
records a withdrawal for this medicine in some country or region.") and the
"only some people" line are never printed. On paper, type 2 diabetes loses the
withdrawal line on 10 main-list cards (for example Metformin, Pioglitazone and
Rosiglitazone), and haemophilia A loses it on Octocog Alfa. The register also
prints all of `data.approved` (`index.html:1306`) under the APPROVED heading,
below the words "Already approved for this disease…". That includes the cards
the screen moves into the red "look like mistakes" box and the no-regulator
box. Each red card keeps its "Warning:" row on paper, but its sentence ("The
database lists these as approved for this disease. They look like mistakes.")
is gone. The "boxes" line counts only the narrower and wider boxes
(`index.html:1310`). Proposal: a ticket to make paper match the screen. The
code changes, and the wording stays the same.

**H3 (lower). An imaging tracer on the Huntington Approved tab.** Ioflupane
(Ioflupane I 123, a scan tracer) is in Huntington's wider-group box. The
DECISIONS line R6 says: "Imaging tracers and contrast agents are not shown in
the medicine lists." Ticket 2.43 applied it to New clues and the trial boxes
only. Either the decision line or the code needs to change. Kashish decides.

---

## PART 1: the page

### Pictures (390 px wide, saved fixtures, network blocked)

All are in `pictures/`. `*_as_opened` shows each box as the page leaves it.
`*_all_open` has every box on that tab opened. Where the two are the same,
only `as_opened` is kept. Pages taller than 65,000 px are cut into `_part1`
and `_part2`. The text of every picture is in `text/`, and the counts below
come from it (`count_text.py`, output in `counts.md`).

| # | Page | Disease id | Saved answers used |
|---|---|---|---|
| 00 | Front page | | |
| 01 | Guide, both folds open | | |
| 02 | Huntington disease | MONDO_0007739 | `tests/test_approvals_third_batch.py` |
| 03 | Type 2 diabetes | MONDO_0005148 | `tests/old_flag_saved.py` (fixtures/old_withdrawn_flag) |
| 04 | Pulmonary arterial hypertension | MONDO_0015924 | `tests/test_narrower_box.py` |
| 05 | Myasthenia gravis | MONDO_0009688 | **its medicine list only** (see "Not checked") |
| 06 | Haemophilia A | MONDO_0010602 | `tests/test_withdrawal_line.py` |

To make them again: `python fixtures/probe_p12/make_answers.py`, then
`node fixtures/probe_p12/take_pictures.js`.

### The fixed-text table

How often is given as Approved / In trials / New clues for the five pages, in
the order HD, T2D, PAH, MG, HemA, with every box open. "Page-wide" means the
text shows once on every tab. Line numbers are on `main` 7005d7d.
"≤2.9" means the text is older than the first commit on `main`'s rewritten
history (3c15923, ticket 2.9). Its real ticket is in the pre-rewrite branches
(5.1 to 5.4).

| # | Text, exactly | Where it shows | How often on one page | Defined | Ticket |
|---|---|---|---|---|---|
| T1 | A free, open-source explorer of medicines and trials for any disease, built from public research data. | header, every page | 1, page-wide | index.html:307 | 2.38 |
| T2 | For learning and research exploration, not medical advice. Never start, stop or change any medicine without a doctor. | pinned safety bar, every page | 1, page-wide | index.html:310 | ≤2.9 (safety rule) |
| T3 | Explore open research | front-page eyebrow, **also above every disease page** | 1, page-wide | index.html:316 | ≤2.9 |
| T4 | Research a disease: approved medicines, trials and new clues. | front-page heading, also above results | 1, page-wide | index.html:317 | 4.1 |
| T5 | Type a disease name to begin. Research clues, not treatment recommendations. | front page, also above results | 1, page-wide | index.html:318 | 5.7 |
| T6 | Search by disease name / Explore / Type a disease name | search box | 1, page-wide | index.html:321-325 | ≤2.9 |
| T7 | New here? How to use Moonlight. | under the search | 1, page-wide | index.html:328 | 5.4 |
| T8 | Quick start + the chip "Pulmonary arterial hypertension" | front page, also above results | 1, page-wide | index.html:335-336 | ≤2.9 |
| T9 | Searching… / Pick the disease you mean. / No disease matched "…". Try another name. / Moonlight could not search just now. Please try again. / Too many requests. Please wait a minute. | search note | 0–1 | index.html:778-800, 701 | ≤2.9, 8.2 |
| T10 | Did you mean: / Database name: … | search choices | 0–1 | index.html:331, 763 | 5.2 |
| T11 | Please wait, fetching data | loading | 0–1 | index.html:342 | ≤2.9 |
| T12 | Moonlight could not get the data. / Please try again in a moment. Nothing is wrong with what you typed. | error box | 0–1 | index.html:347, 844 | ≤2.9 |
| T13 | Disease results | eyebrow over the disease name | 1 | index.html:352 | ≤2.9 |
| T14 | Also called: … / Show more / Show less / Source: Open Targets | about box | 1 each (0 on MG: no record saved) | index.html:359, 893, 907 | 5.5 |
| T15 | What open research data says about medicines and this disease. Nothing here is medical advice. | under the disease name | 1 | index.html:362 | ≤2.9 (decision of 15 Nov) |
| T16 | Print this page | under T15 | 1 | index.html:364 | 5.1 |
| T17 | Approved (n) / In trials (n) / New clues (n) | tab buttons | 1 | index.html:367-369 | 5.3 |
| T18 | How to read a card | under the tabs | 1, page-wide | index.html:371 | 5.4 |
| T19 | Already approved for this disease in at least one country, according to the database. Nothing here says how well any of them works. Listed A to Z. | Approved, top | 1 | index.html:375 | ≤2.9 |
| T20 | Talk to your doctor before changing any medicine. | Approved top, **and again inside the narrower and wider boxes** | 2 / 2 / 2 / 1 / 2 | index.html:376, 387, 393 | ≤2.9, 2.12, 2.14 |
| T21 | 1 more approved medicine is in the folded box below. / N more approved medicines are in the folded boxes below. | Approved, above the cards | 1 / 1 / 1 / 0 / 1 | index.html:984-987 | 2.14 |
| T22 | The database lists no approved medicine under this exact name. That does not mean there is none. Ask a doctor. | Approved, when empty | 0 on all five | index.html:382 | 5.6 |
| T23 | Approved for a narrower disease (n) | Approved, box 1 | 0 on all five | index.html:386 | 2.14 |
| T24 | Approved for a wider group (n) | Approved, box 2 | 1 / 1 / 1 / 0 / 1 | index.html:392 | 2.12 |
| T25 | The database lists these as approved, but gives no regulator record for them. (n) | Approved, box 3 | 0 / 1 / 1 / 1 / 0 | index.html:400; engine.py:209 | 2.42 |
| T26 | The database lists these as approved for this disease. They look like mistakes. (n) | Approved, box 4 (red) | 1 / 1 / 0 / 1 / 0 | index.html:406; engine.py:203 | 2.27 |
| T27 | Tap to open / Tap to close | every folded box | one per box (HD 2/2/0, T2D 3/2/1, PAH 2/2/1, MG 2/2/0, HemA 1/2/1) | index.html:386 ff., 1026 | 2.14, 2.37 |
| T28 | Not listed as approved for this exact disease. Approved for X, a wider group the database puts this disease in. (child form: "…which the database lists under this disease.") | grey-bordered label, every card in the wider and narrower boxes | 4 / 44 / 1 / 0 / 11 | engine.py:510-528 | 2.12, 2.16 |
| T29 | The database lists this as approved, but gives no regulator record for it. | grey line, Approved cards (main, boxes) | 0 / 24 / 0 / 2 / 10 | engine.py:193 | 2.17 |
| T30 | Approved in Japan, according to the database. Moonlight could not find the exact record for this disease. | grey line | 4 / 6 / 1 / 0 / 0 | engine.py:186 | 2.13 |
| T31 | This approval is missing from the database. We added it from the official label. | grey line | 1 / 0 / 0 / 2 / 0 | engine.py:241 | 2.26 |
| T32 | The label covers only some people with this disease. | grey line | 2 / 0 / 0 / 2 / 0 | engine.py:255 | 2.33, 2.39 |
| T33 | The database records a withdrawal for this medicine in some country or region. | grey line | 0 / 12 / 0 / 0 / 1 | engine.py:249 | 2.31, 2.40 |
| T34 | A doctor has told us this looks like a mistake in the database. | red warning | 4 / 0 / 0 / 0 / 0 | engine.py:211 | 2.13 |
| T35 | This looks like a mistake in the database. The official label is for a different disease. | red warning | 0 / 3 / 0 / 3 / 0 | engine.py:215 | 2.18 |
| T36 | Forms: … | every card | one per card | index.html:1088, 1131 | ≤2.9 |
| T37 | n report / n reports | every card except trial-box cards | one per card | index.html:1132 | ≤2.9 |
| T38 | Research pathway / Research pathways | every card with a path | 6/6/175, 33/11/11, 12/4/51, 0/0/0, 22/10/28 | index.html:650, 1134 | ≤2.9 |
| T39 | Up / Down / Mixed / Unknown (+ hover titles) | protein rows | per protein | index.html:678-681 | ≤2.9 |
| T40 | n / 100 points | protein rows | per protein | index.html:1155 | ≤2.9 |
| T41 | X, Y and Z are pieces of one machine, counted once. | grey box on cards | 1/4/89, 13/2/0, 5/0/7, 0, 1/4/8 | index.html:1177 | ≤2.9 (2.8) |
| T42 | This medicine does not act on one of the 25 proteins most linked to this disease, so no path is shown. | grey box, Approved cards with no path | 4 / 71 / 2 / 14 / 7 | index.html:654 | ≤2.9 |
| T43 | The data does not say which direction this disease needs. | every card with a path, all tabs | 6/6/175, 33/11/11, 12/4/51, 0/0/0, 22/10/28 | index.html:655 | ≤2.9 (safety rule) |
| T44 | But there is a catch. Nobody knows from our information if the disease needs this protein (these proteins) turned up or down. So this is a clue to read about. Never start, stop or change any medicine without a doctor. | ending, every clue and In trials card | 0/6/175, 0/11/11, 0/4/51, 0, 0/10/28 | explain.py:58-63 | ≤2.9 (3.6) |
| T45 | Opposite way to the approved medicines for this disease. | under a protein | 0/0/0, 0/2/3, 0/0/4, 0, 0/0/5 | engine.py:196 | 3.7 |
| T46 | (UniProt's sentence on the protein) | under a protein | data, not fixed | api.py via protein.py | 3.8 |
| T47 | Source record | every card | one per card | index.html:658 | ≤2.9 |
| T48 | The database gives no source link for this medicine. | card foot | 0/0/0, 0, 0/0/2, 0, 0 | index.html:659 | 2.23 |
| T49 | Phase 1 / Phase 2 / Early Phase 1 / Phase 2/3 … | In trials cards | per card | explain.py:125-128 | ≤2.9 |
| T50 | Already being studied for this disease | In trials, heading | 1 | index.html:412 | ≤2.9 |
| T51 | Medicines being tested for this disease. A separate research category, not a prediction of effectiveness. Not every trial is listed. | In trials, under the heading | 1 | index.html:413 | ≤2.9, 2.16 |
| T52 | No medicine in this data is being studied for this disease. | In trials, when empty | 0 on all five | index.html:994 | ≤2.9 |
| T53 | More medicines in trials for this disease. They do not act on one of the 25 proteins. (n) | In trials, box 1 | 1 on all five | index.html:418; engine.py:224 | 2.21 |
| T54 | New medicines being tested for this disease. The database records no approval for them for any disease. (n) | In trials, box 2 | 1 on all five | index.html:424; engine.py:235 | 2.24 |
| T55 | Never start, stop or change any medicine without a doctor. | top of each In trials box (on its own; also inside T2 and T44) | 2 per page as a box line; 176 times in all on HD New clues | index.html:419, 425; engine.py:231 | 2.29 |
| T56 | Approved for another disease, with no recorded link to this one. Connections worth reading about, never treatments. | New clues, top | 1 | index.html:431 | ≤2.9 |
| T57 | Ordered by how strongly the proteins are linked to the disease. Pieces of the same machine count once. If a medicine acts on different machines, the scores are added. Ties: more reports first, then alphabetical. Being first on the list does not mean best. | New clues, rule box | 1 | rank.py:20 | ≤2.9 |
| T58 | Show only the medicines for one protein. Tap again to show all. | New clues, above the filter chips | 1 | index.html:434 | ≤2.9 |
| T59 | Showing only the medicines that act on X. The numbers are their places on the whole list. | New clues, while filtered | 0–1 | index.html:1220 | ≤2.9 |
| T60 | No new clues found for this disease. / There may not be enough information … This does not mean a treatment exists or does not exist. | New clues, when empty | MG only | index.html:440-441 | ≤2.9 |
| T61 | These push the opposite way to the approved medicines for this disease. (n) | New clues, box | 0 / 1 / 1 / 0 / 1 | index.html:446; engine.py:199 | 2.28 |
| T62 | n medicine(s) left out because it pushes / they push the wrong way for this disease. | New clues, bottom | HemA only | engine.py:1455-1456 | 2.18 |
| T63 | Left-out counts / Counts only. No medicine names are displayed here. / Not approved anywhere / Unclear link | under **every** tab | 1, page-wide | index.html:454-459 | ≤2.9 |
| T64 | New search | under the results | 1 | index.html:463 | ≤2.9 |
| T65 | Found something wrong or have any feedback? Contact hello@moonlightclues.com | footer | 1, page-wide | index.html:594 | 5.7 |
| T66 | Moonlight · Research exploration only · Not clinical findings · Data from Open Targets | footer | 1, page-wide | index.html:595 | ≤2.9 |
| T67 | Guide: How to use Moonlight / How to read what Moonlight finds. / Type a disease. See the medicines that act on its proteins. / Back to search | guide intro | 1 | index.html:469-473 | 5.4, 5.8 |
| T68 | A medicine for one disease may act on a protein linked to another. + Medicine / already approved, Protein / a tiny machine in the body, Disease / linked to that protein | guide | 1 | index.html:477-483 | 5.8 |
| T69 | Three steps: Type a disease / Not sure? Moonlight asks "Did you mean?" / Pick the one you mean / Moonlight never picks for you. / Open a tab / Three lists of medicines. | guide | 1 | index.html:488-492 | 5.8 |
| T70 | The three tabs: Approved / Approved for this disease. Listed A to Z. In trials / Being tested for it. Not a prediction. New clues / No recorded link yet. Worth reading about. | guide | 1 | index.html:497-502 | 5.8 |
| T71 | How to read a card / A real clue. Match the gold letters. + the Doxapram card + key A, B, C, D, E, G, H | guide | 1 (the card repeats T43 and T44) | index.html:507-534 | 5.4, 5.8 |
| T72 | What Moonlight can and cannot tell you / It can show (4 items) / It cannot tell you (4 items) | guide | 1 | index.html:538-551 | 5.7 |
| T73 | For doctors: how far to trust each part (8 lines) / Moonlight is not a prescribing reference. | guide fold 1 | 1 | index.html:558-569 | 5.8, 2.17 |
| T74 | Where the facts come from (4 lines) | guide fold 2 | 1 | index.html:572-578 | 5.8, 3.8 |
| T75 | Doctor, pharmacist or researcher? / Test a condition you know well. Tell us what is missing or wrong. | guide strip | 1 | index.html:583-585 | 5.7 |

That is **75 rows**. Some rows group several short fixed texts that always
show together (T6, T9, T63, T69, T70, T72 to T74). Counted one by one, there
are about **128 separate fixed texts**.

### 1. Duplicates (the same idea twice on one screen)

| # | Duplicate | Proposal | K |
|---|---|---|---|
| D1 | "Not medical advice" is said four ways on every disease page: T2 (pinned), T5 "Research clues, not treatment recommendations" (still above the results), T15 "Nothing here is medical advice", T66 "Research exploration only · Not clinical findings". | Keep T2 (safety rule). Hide T5 once results show. Remove the second sentence of T15. Footer becomes "Moonlight · Data from Open Targets". | K + safety |
| D2 | "Never start, stop or change any medicine without a doctor." is in T2 and again at the end of every clue and In trials card (T44): **176 times** on Huntington's New clues tab. | Remove the last sentence from T44 (T2 is pinned on screen). | K + safety |
| D3 | On every clue card, T43 "The data does not say which direction this disease needs." and T44 "Nobody knows from our information if the disease needs this protein turned up or down" say the same thing. | Keep T44 on clue cards and leave out T43 there. Keep T43 on Approved cards, which have no ending. | K + safety |
| D4 | The two In trials boxes each open with "Never start, stop or change any medicine without a doctor." (T55), word for word the second half of T2. | Remove both box lines (that would undo ticket 2.29). | K + safety |
| D5 | "Talk to your doctor before changing any medicine." at the top of Approved and again inside the narrower and wider boxes (T20). | Keep the tab-top line and remove the two box copies. | K |
| D6 | Wider box title "Approved for a wider group" and then every card in it says "Not listed as approved for this exact disease. Approved for X, a wider group…" (44 times on T2D). | Merge: title "Approved for a wider group (X), not for this exact disease (n)". The per-card label shows only when the box holds more than one group. | K |
| D7 | No-regulator box title (T25) and every card inside carries T29, the same sentence in the singular. | Inside that box, leave out T29 (keep T30, the Japan line, which says something different). | K |
| D8 | Red box title "They look like mistakes" (T26) and every card inside carries a red "looks like a mistake" (T34/T35). | Keep the red line on each card (Kashish's rule). Shorten the title to "These look like mistakes in the database (n)". | K |
| D9 | In trials heading "Already being studied for this disease" (T50) and "Medicines being tested for this disease." (T51). The tab is also called "In trials". | Merge into one line: "Medicines being tested for this disease. Not a prediction of effectiveness. Not every trial is listed." | K |
| D10 | Two links to the guide on one screen: T7 "New here? How to use Moonlight." and T18 "How to read a card". | Keep T18 on results and hide T7 once results show. | K |
| D11 | The front page's heading, search label and "Quick start" (T3 to T8) stay above every disease page. | Fold the hero away once results show (a design choice for Sidha). | design |
| D12 | The guide's example card shows both T43 and T44 (as in D3). | Follows D3. | K |

### 2. Stacks (cards with three or more grey lines)

A grey line here means a label box, a proof line, a limit line, a withdrawal
line, or the no-path note.

| Page | Card(s) | Lines |
|---|---|---|
| Type 2 diabetes, wider box | Beinaglutide, Carbutamide, Carfloglitazar, Enavogliflozin, Evogliptin, Gemigliptin, Glibornuride, Gliquidone, Glymidine, Guar Gum, Imeglimin, Ipragliflozin, Luseogliflozin, Metahexamide, Pramlintide, Teneligliptin (16) | T28 + T29 + T42 |
| Haemophilia A, wider box | Dicumarol, Ethanolamine Oleate, Pentastarch, Phytonadione, Protamine Sulfate, Thrombin (6) | T28 + T29 + T42 |
| Myasthenia gravis, main list | Eculizumab, Ravulizumab (2) | T31 + T32 + T42 |
| Huntington, main list | Valbenazine | T31 + T32 + T43 (direction note), three if T43 counts |
| Type 2 diabetes, wider box | Insulin Aspart, Insulin Lispro | T28 + T33 + T43, three if T43 counts |
| Huntington, red box | Atomoxetine, Guanfacine, Lisdexamfetamine, Methylphenidate | T30 + red T34 + T43 |

**24 cards** carry three grey boxes. With the direction note counted, about 30.
Proposal: D6 and D7 remove one line from 22 of the 24. The no-path note (T42)
could become one line at the top of a box ("Cards without a path act on none
of the 25 proteins most linked to this disease."). **K**

### 3. Box count (Approved tab)

| Page | Folded boxes drawn | Which | Empty but drawn |
|---|---|---|---|
| Huntington | 2 | wider (4), red (4) | 0 |
| Type 2 diabetes | 3 | wider (44), no-regulator (8), red (3) | 0 |
| PAH | 2 | wider (1), no-regulator (1) | 0 |
| Myasthenia gravis | 2 | no-regulator (2), red (3) | 0 |
| Haemophilia A | 1 | wider (11) | 0 |

The page can draw up to 4 boxes on Approved, 2 on In trials and 1 on New
clues. No empty box is ever drawn: each is `hidden` when its count is 0
(`index.html:965-1005`). The narrower box was empty on all five pages.

### 4. Dead text (defined, never shown)

| # | Where | What | Proposal |
|---|---|---|---|
| X1 | api.py:507, engine.py:231 | `"ending": MORE_IN_TRIALS_ENDING` is sent with every trial-box card, but the page removes the ending slot (`index.html:1089`). The words show only from the HTML copy at the box top. | Stop sending `ending` for box cards. Keep the constant only as the test's copy of the box line. |
| X2 | api.py:124, 523 | `about_disease.source` is sent, but the page types "Source: Open Targets" itself (`index.html:359`). | Use the API field or drop it. |
| X3 | engine.py:199, 203, 209, 224, 235 | The five box-title constants are never sent to the page. The page has its own copies, and only tests compare them. | Keep (tests guard them), or send them from the API so there is one copy. |
| X4 | index.html:220 | CSS comment "the key: eight small chips". The key has seven, and the letter F is missing (A to E, G, H): the F chip was removed and the others were not re-lettered. | Re-letter to A to G. **K** (visible letters) |
| X5 | api.py:679 `/api/explain`, explain.py (Gemini explanations), the "explain" rate lane (api.py:139) | The page has not asked for an explanation since ticket 3.8 (commit f2c48bc, "the explanation slot comes off the card"). No visitor can reach the Gemini explanation. | Kashish decides: remove it, or bring it back. Until then, CLAUDE.md step 5 and five DECISIONS lines describe a feature visitors never see. |
| X6 | index.html:1310 | The register's "boxes" line has no wording for the no-regulator or red box. | See H2. |
| X7 | index.html:378 comment | "Only when the main list and a box both hold cards" is true only for the narrower and wider boxes. | Fix the comment. |

T22, T23, T52 and T60 did not show on these five pages, but other pages can
show them, so they are not dead.

### 5. Words that disagree

| # | Text A | Text B | Proposal | K |
|---|---|---|---|---|
| W1 | T21 "4 more approved medicines are in the folded boxes below." (Huntington) | Huntington has 8 boxed cards (4 wider + 4 red). Type 2 diabetes says 44, with 55 boxed. Myasthenia shows no line with 5 boxed. Plural "boxes" for one box. | Count all boxes, or remove T21 (each box title shows its own count). | K |
| W2 | Guide T73 "Left out. Withdrawn anywhere, or approved nowhere: counted, never named." | Tickets 2.31 and 2.40 show withdrawn medicines on Approved, with the withdrawal line (12 cards on T2D). | "Left out. Approved nowhere, or hidden by the older Withdrawn flag: counted, never named." | K |
| W3 | Guide T70 "Approved: Approved for this disease. Listed A to Z." and tab top T19 "Already approved for this disease…" | The same tab holds boxes "Not listed as approved for this exact disease" and "They look like mistakes". | Add "Folded boxes hold the rest, each with its own label." | K |
| W4 | Count label T63 "Not approved anywhere" | That number also counts withdrawn medicines (decision of 15 Nov). | "Not approved, or withdrawn" | K |
| W5 | Guide T73 "Weak proof. … Approvals with no regulator record say so." | Since 2.42 those cards are also moved into their own box. | "…say so, in their own folded box." | K |
| W6 | Heading T50 "Already being studied for this disease" | Tab name "In trials" and guide T70 "In trials". | One name (see D9). | K |
| W7 | DECISIONS R6: tracers "are not shown in the medicine lists" | Ioflupane on the Huntington Approved tab (H3). | Kashish decides the scope. | K |
| W8 | README "Approved: … Each card says whether a DailyMed, FDA, EMA or PMDA record is attached." | Since 2.42 cards without one sit in a box. | Update the README. | no (not on the page) |

---

## PART 2: the repo

### 1. Rulebook vs code (13)

| # | Rule, quoted | Code or later line, quoted | Proposed action |
|---|---|---|---|
| R1 | CLAUDE.md: "5. explain.py  one path's records -> plain-language text (Gemini), then a grounding check". DECISIONS 12 Nov: "Moonlight waits at most 25 seconds for an explanation, and shows a "Please wait" message." | The page never calls `/api/explain` (removed in ticket 3.8, f2c48bc). | Kashish decides on X5, then update CLAUDE.md and add a DECISIONS line. |
| R2 | DECISIONS 16 Nov: "One visitor can make 10 searches a minute" | api.py:139 `MAX_A_MINUTE = {"search": 60, …}`; api.py:51 "each visitor may make 60 requests" (ticket 6.1, the hall problem) | Add a DECISIONS line for 60 (if Kashish agreed), or change the code back. |
| R3 | DECISIONS 16 Nov: "The guide says that Gemini, an AI, guesses the disease and writes the explanations" | Guide index.html:567: "Gemini suggests which disease you mean, and Open Targets confirms it." | New DECISIONS line. |
| R4 | DECISIONS 16 Nov: "Its heading is "Disease → protein → medicine. One search."" | index.html:317 "Research a disease: approved medicines, trials and new clues." (ticket 4.1) | New DECISIONS line. |
| R5 | DECISIONS 16 Nov: "a list for everyone and a list for doctors, both called "what Moonlight can and cannot tell you"" | The doctors' list is called "For doctors: how far to trust each part" (index.html:559). | New DECISIONS line. |
| R6 | DECISIONS 11 Nov: "Medicines already approved for the disease are removed." | DECISIONS 13 Nov: the Approved tab. | Mark the 11 Nov line as replaced. |
| R7 | DECISIONS 15 Nov: "If any country took a medicine off the shelves, Moonlight leaves it out, even if other countries still sell it." | DECISIONS 23 Nov (withdrawal report keeps the card) and 24 Nov (2.40). CLAUDE.md already has the new rule. | Mark the 15 Nov line as replaced. |
| R8 | DECISIONS 16 Nov: "When medicines sit in a folded box, the top of the Approved tab says how many" | index.html:984 counts only the narrower and wider boxes (W1). | Code fix, or a DECISIONS line saying which boxes count. |
| R9 | DECISIONS 24 Nov R6: "Imaging tracers and contrast agents are not shown in the medicine lists." | tests/test_left_out_r1_r6.py:10 "It never touches the Approved tab". Ioflupane is shown (H3). | Kashish decides. |
| R10 | DECISIONS 23 Nov: "A machine may also MOVE an opposite-way clue into a folded box." | Tickets 2.27 and 2.42 also move Approved cards by machine. | Widen the line: "A machine may move a card into a folded box." |
| R11 | CLAUDE.md: "Being studied: … Separate box labelled "Already being studied for this disease"" | It is a tab, "In trials" (DECISIONS 13 Nov). | Update CLAUDE.md. |
| R12 | CLAUDE.md: "Every result shows its source and evidence strength." | Trial-box cards show no points and no report count. Approved cards with no path show no points. | Kashish says what "evidence strength" means for those cards. |
| R13 | CLAUDE.md: "One ticket per branch, named ticket-<id>-<short-name>." | PRs 72 and 75 came from `claude/ticket-2-41-…` and `claude/ticket-2-42-…`. | Note only (the session tool picks the name). |

DECISIONS 23 Nov ("The eight medicines whose approval cannot be told stay
hidden") and the 2.40 commit ("eight cards come back") both say "eight". They
look like different groups of eight. I did not check this. Worth one sentence
in DECISIONS to keep them apart.

### 2. Engine and API docstrings that describe old behaviour

| File:line | Says | Now |
|---|---|---|
| engine.py:228-231 | MORE_IN_TRIALS_ENDING: "The last words on every card of that box" | Since 2.29 it is said once at the top of the box. |
| api.py:493-498 | `_more_in_trials_json`: "ending is the engine's one sentence…" | The page throws it away (X1). |
| api.py:430-433 | `_approved_json`: "proof_note is only there when Japan's general list is the card's only approval receipt … Neither moves the card" | Since 2.27 and 2.42, both lines move a card into a box. |
| engine.py:34-36 | "The line itself never moves a card: since ticket 2.42 the page moves…" | Contradicts itself. |
| engine.py:44 | Ticket 3.7: "Nothing is moved or hidden." | 2.28 moves those clues into a box. |
| api.py:51 | "60 requests to /api/search" | Matches the code, but not DECISIONS (R2). |
| api.py:3-31 | The route list ends mid-sentence ("They are still in "approved"") and still lists `/api/explain` as "one clue's explanation" | The page does not use it. |
| index.html:1056 | "the one grey line" | A card can carry up to three. |
| index.html:1286 | "The grey line and the red warning of an Approved card" | Leaves out the limit and withdrawal lines (H2). |
| index.html:220 | "eight small chips" | Seven (X4). |

### 3. Copies of page wording

Each sentence below is written in the page or engine, and copied into tests
(counted in `.py` files under `tests/`):

| Sentence | Defined | Test files that copy it |
|---|---|---|
| Safety line (T2) | index.html:310, cli.py:31 | 31 |
| "Never start, stop or change any medicine without a doctor." | explain.py:61, engine.py:231, index.html:419, 425, 522 | 19 |
| "This approval is missing from the database…" | engine.py:241 | 13 |
| "Talk to your doctor before changing any medicine." | index.html:376, 387, 393 | 11 |
| "Tap to open" | index.html (6 boxes + JS) | 10 (34 lines) |
| "The label covers only some people…" | engine.py:255 | 8 |
| "The data does not say which direction…" | index.html:521, 655 | 7 |
| No-regulator line, Japan line | engine.py:193, 186 | 5 each |
| Red box title, withdrawal line, opposite-way line and box title, "Not listed as approved…" | engine | 2 to 3 each |

**Drift:** none found. Every engine box-title constant equals its HTML copy,
letter for letter (checked in Python against `web/index.html`). The safety
line is also copied in `cli.py:31` and `README.md` (README's wording differs:
"Not medical advice. Moonlight is for learning and research.").
**Still checked?** Yes. The full suite passes (2262 tests). The
weak spot is that one sentence lives in 2 to 5 code places and 10 to 31 test
files. Proposal: one `page_words.py` (or a JSON file the page also reads) and
one test that compares it to the page. That would remove about 100 copies.

### 4. Tests

- Checking the same thing many times: the safety line is asserted in 31 test
  files. "Tap to open" is checked on 34 lines in 10 files. Proposal: one test
  per sentence, in one file.
- Tests that only check a fixture against itself:
  `tests/test_approvals_fourth_batch.py:337` `test_the_saved_lists_are_the_diseases_own`
  (counts rows in saved files) and
  `tests/test_box_labels.py:198` `test_example_5_the_before_picture_holds_all_seven_saved_diseases`
  (counts entries in `tests/cards_before_2.16.json`). They guard the fixtures,
  not Moonlight. Keep them, but move them into a "fixture health" file
  next to `scripts/check_fixtures.py`.
- The several `test_*_ids_are_the_ones_open_targets_uses_in_the_saved_*` tests
  cross-check the hand files against fixtures. They are useful, so keep them.
- 1,706 test functions in 54 files. Many files define their own
  `saved_post_json` and `page_answer` (14 copies of `saved_post_json`).
  Proposal: one shared helper in `tests/conftest.py`.

### 5. Branches on the remote (89, last commit date in brackets)

- **Merged into main, safe to delete (53):** every branch in
  `branches_merged.txt` except `main` and this study's branch.
- **PR merged, but main's history was rewritten so git does not see them as
  merged (20). Delete:** ticket-0.3-rulebook (11-10), ticket-1.1-schema-probe
  (11-10), ticket-1.3-records, ticket-1.3b-rulebook, ticket-1.4-housekeeping,
  ticket-2.1-2.3-fetch, ticket-2.4-filter (11-11), ticket-2.5-rank,
  ticket-2.6-runner, ticket-2.7-ranked-runner, ticket-2.8-one-machine,
  ticket-3.2-explain, ticket-3.5-explain-followups, ticket-5.1-page-api (11-12),
  docs-pitch-deck-13nov, ticket-6.1-speed, ticket-6.3-use-by,
  ticket-8.1-container (11-13), ticket-5.2-search, ticket-5.3-tabs (11-15).
- **PR closed without merging (abandoned, 2). Delete after a glance:**
  ticket-2.22-withdrawal-reports (11-23, PR 59), ticket-1.7-housekeeping (11-22, PR 50).
- **Never a PR. Abandoned drafts (3). Delete:** guide-draft (11-15),
  night-watch-2026-11-15 (11-15), probe-MONDO_0016971 (11-12).
- **Study branches (10). KEEP:** code, fixtures READMEs or README.md cite them
  as the origin of saved data: probe-withdrawn (11-15),
  probe-search-and-children (11-16), probe-approval-proof (11-17),
  probe-direction (11-18), probe-baseline, probe-key-diseases (11-21),
  probe-ctgov, probe-uniprot (11-22), probe-lgmd, probe-old-withdrawn-flag (11-23).
  Proposal: tag them (`study/p3` and so on) so they can be deleted as branches later.

Total proposed for deletion: **78**.

### 6. Fixtures

Every top-level folder in `fixtures/` is read by at least one test or module.
The least used: `MONDO_0007947`, `labels_confirmed`, `left_out_r1_r6`,
`probe_p2`, `stage_words` (1 reader each). The biggest: `old_withdrawn_flag`
(22 MB), `approval_proof` (15 MB), `family` (14 MB), `narrower_box` (13 MB).
I did not check file by file (see "Not checked").

### 7. Links

- `README.md:28` has two links to `github.com/kashishdugar2017/moonlight/blob/…`
  (the old home). Both branches still exist on `Moonlight-Clues/moonlight`.
  Proposal: change the owner to `Moonlight-Clues`.
- No other `kashishdugar2017` link was found. No link points to a branch that
  does not exist.

### 8. Dead code

| File:line | What | Proposal |
|---|---|---|
| api.py:679 + explain.py (explanation part) + rate lane "explain" | Not reached from the page (X5) | Kashish decides |
| api.py:507 `"ending"` on trial-box cards | Never drawn (X1) | Remove the key |
| api.py:523 `about_disease.source` | Never read by the page (X2) | Remove or use |
| engine.py:308 `RankedClues.moved_to_approved` | Only read by `cli.py:122` | Keep (the CLI uses it) |
| engine.py `approvals_left_out` | Read only by tests | Keep (a person runs it to fix the file) |
| engine.py:199-235 box-title constants | Read only by tests (X3) | Keep or send through the API |

---

## The ten changes that would remove the most clutter

1. On clue and In trials cards, drop the direction note (T43), because the ending (T44) says the same thing. That removes 175 lines from Huntington's New clues. **K + safety**
2. Drop "Never start, stop or change any medicine without a doctor." from the end of each card's ending. The pinned bar already says it. That removes 176 sentences on Huntington. **K + safety**
3. Put the wider-group name in the box title and drop the per-card "Not listed as approved…" label. That removes 44 lines on type 2 diabetes. **K**
4. Inside the no-regulator box, drop the card's "no regulator record" line, because the title says it. **K**
5. Remove the "Talk to your doctor" copies inside the wider and narrower boxes. **K**
6. Remove the "Never start…" lines at the top of the two In trials boxes. **K + safety**
7. One "not advice" line per page: keep the pinned bar, and drop "Nothing here is medical advice", "Research clues, not treatment recommendations" (on results) and "Research exploration only · Not clinical findings". **K + safety**
8. Fold the front-page hero (heading, search label, Quick start, "New here?") away once results show. **design**
9. Show the no-path note once at the top of a box, not on each card (71 times on type 2 diabetes). **K**
10. Fix or remove the "N more approved medicines…" line: it miscounts on 4 of 5 pages. Merge the In trials heading and its description into one line. **K**

## Counts

| What | Count |
|---|---|
| Fixed texts on the page | 75 table rows (about 128 separate texts) |
| Duplicates | 12 (D1 to D12) |
| Stacked cards (3+ grey lines) | 24 on these five pages (about 30 with the direction note) |
| Dead text | 7 (X1 to X7) |
| Words that disagree | 8 (W1 to W8) |
| Rulebook contradictions | 13 (R1 to R13) |
| Stale branches | 78 to delete, plus 10 study branches to keep |
| HARM | 3 (H1 to H3) |

## What was not checked

- **Myasthenia gravis is incomplete.** Only its medicine list is saved
  (`fixtures/approvals_by_hand/disease_drugs/MONDO_0009688`). Its disease
  record, proteins and family were stubbed as empty in `make_answers.py`, so
  its page has no description, no paths and no New clues. On the live site it
  would have more.
- The pictures use saved data (Open Targets 26.09, different dates per
  fixture), not the live site.
- Narrower box, empty Approved tab and empty In trials tab: none of the five
  pages has them, so they are not pictured.
- The register (print view) was read in code only, not printed or pictured.
- Fixtures were checked by folder, not file by file.
- Wider screens (only 390 px was taken).
- Whether Dicumarol, Pentastarch and Ethanolamine Oleate are really wrong for
  haemophilia A needs a doctor. The study only shows what the page says.
- The two groups of "eight" in DECISIONS (R-note above).

## What I ran

- `pip install -r requirements.txt` (fastapi was missing in this container).
- `python fixtures/probe_p12/make_answers.py`: five answers built from saved fixtures, with the network blocked by the tests' own `no_network()` guards.
- `node fixtures/probe_p12/take_pictures.js`: 32 pictures. Every request other than the page and `/api/clues` is refused, so Umami is never reached.
- `python fixtures/probe_p12/count_text.py > fixtures/probe_p12/counts.md`
- `python -m pytest -q -p no:cacheprovider` on main 7005d7d: **2262 passed in 274.01s**.
- `git fetch origin '+refs/heads/*:refs/remotes/origin/*'`, then `git merge-base --is-ancestor` for each branch, cross-checked against the list of pull requests on GitHub.

## Files in this folder

- `REPORT.md`: this report.
- `pictures/`: 32 phone-width pictures (JPEG, 390 px wide, scale 1).
- `text/`: the visible text of each picture.
- `answers/`: what `/api/clues` sent for each page, from saved fixtures.
- `counts.md`: per-page counts from `count_text.py`.
- `branches.txt`: every remote branch, date and merge state.
- `branches_merged.txt`: the 53 branches already in main.
- `make_answers.py`, `take_pictures.js`, `count_text.py`: how to rebuild all of it.
