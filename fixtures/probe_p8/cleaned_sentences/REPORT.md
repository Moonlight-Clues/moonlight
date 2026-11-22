# Study P8b: cleaning the protein function sentence

Read-only study. No Moonlight code or test was changed. Everything is in
`fixtures/probe_p8/cleaned_sentences/`. Source: Open Targets'
`functionDescriptions` only, data version 26.09 (API 26.9.0, the same
before and after the run), asked on 22 November 2026. UniProt was not asked.

## Short answer

The four cleaning steps work: after cleaning, **no** sentence has a
leftover curly tag, a leftover label, a missing full stop or a cut inside
a bracket. Two things are still in the way of a card:

1. **Citations in round brackets stay**, because the order said to remove
   only curly-brace tags. 456 of 994 sentences still carry
   "(PubMed:12345, ...)". These make the longest sentences long.
2. **Four sentences are really two sentences**, because the second one
   starts with a small letter and the rule looks for a capital.

## What was asked

- 59 diseases: 50 from `fixtures/probe_p5` (branch `probe-baseline`) and 9
  from `fixtures/probe_p6` (branch `probe-key-diseases`).
- Their top-25 lists give **1,451 slots** (not 1,475: "Drug-induced
  anaphylaxis" has only 1 protein in its saved list) and **1,011 different
  proteins**.
- 1,011 requests, one at a time, one second apart. Every answer saved in
  `responses/`. No errors, no refusals, every protein found.

## The cleaning function

`clean.py`, one function, `clean(texts)`. It uses the **first** text in
Open Targets' list (155 proteins have more than one text). In order:

1. removes evidence tags in curly braces, with the full stop that closes them;
2. removes the trailing " .";
3. removes a label in square brackets at the very front;
4. removes line-wrap marks: the space after a hyphen or a slash, unless the
   next word is a joining word (and, or, to, nor, but, versus, vs, as, than,
   rather, through), which marks a real hanging hyphen like "alpha- and
   beta-tubulin";
5. keeps everything up to the first full stop that is followed by a space
   and a capital letter, digit or opening bracket. A full stop after a
   listed abbreviation ("e.g.", "i.e.", "approx." and so on) does not count.

It changes no word, shortens nothing else and adds nothing.

How often each step did something (of 1,011 proteins):

| Step | Proteins |
|---|---|
| Curly-brace tag removed from the first text | 703 |
| Trailing " ." removed | 200 |
| Label in square brackets removed | 14 |
| Line-wrap mark joined inside the kept sentence | 76 (82 joins) |
| The whole first text was already one sentence | 99 |

## 1. How many have a sentence

| | Proteins (of 1,011) | Slots (of 1,451) |
|---|---|---|
| Have a sentence | **994** | 1,432 |
| Have none | **17** | 19 |

The 17 with none got an empty list from Open Targets. 16 are
protein-coding genes and 1 is not a protein at all (HLA-H, a "lncRNA").
All 17 are named at the end of `odd_cases.md`: CLN6, FAM13A, SETBP1,
ADAMTS6, RPS4Y1, RASSF3, C1orf141, FAM117B, ACOXL, ACTL7B, MST1, EXOC3L4,
MRPS9, VWA3B, PHTF2, HLA-H, WBP1L.

The 994 sentences are 910 different sentences; some proteins share one
(sixteen tubulins have nearly the same sentence).

## 2. Length of the cleaned first sentence

| | Characters |
|---|---|
| Shortest | 17 |
| Middle (median) | 156 |
| Longest | 1,219 |
| Average | 166 |

| Longer than | Sentences (of 994) |
|---|---|
| 150 characters | 514 |
| 200 characters | 297 |
| 300 characters | 98 |

Study P8 reported a middle of 130. That count took the "(PubMed:...)"
citations out before measuring; this one keeps them, as ordered.

**A what-if, not part of the cleaning.** If the round-bracket PubMed
citations were removed as well, the same 994 sentences would run 15 to 398
characters, middle 128, with 392 over 150, 163 over 200 and 19 over 300.
Nothing was saved cleaned that way. It is only there so Kashish can see how
much of the length is citations.

## 3. Every case where the cleaning leaves something odd

`recount.py` puts a **flag** on any sentence a person should look at. A
flag is a question, not a verdict. `odd_cases.md` lists every flagged
sentence in full, grouped by flag. I read every group except the two
citation groups, which I read in part. Below is what I found in each.

### Checks that found nothing (0 sentences each)

Leftover curly brace; leftover "ECO:"; leftover square-bracket label;
sentence not ending in a full stop; brackets that do not pair up; a slash
followed by a space; doubled punctuation; a cut at a full stop followed by
a digit or bracket.

So: **no cut-off sentence, no leftover curly tag, and no abbreviation
mistaken for a full stop** were found.

### Really odd: 4 sentences that are two sentences

The second sentence starts with a small letter, so the rule did not see
the full stop as an ending. All four:

- **GUCY1A1** (171): Alpha subunit of soluble guanylate cyclase (sGC), a
  key enzyme in nitric oxide (NO) signaling. sGC functions as a heterodimer
  consisting of one alpha and one beta subunit.
- **GUCY1B1** (170): Beta subunit of soluble guanylate cyclase (sGC), a key
  enzyme in nitric oxide (NO) signaling. sGC functions as a heterodimer
  consisting of one alpha and one beta subunit.
- **CHRNA4** (350): Component of neuronal acetylcholine receptors (nAChRs)
  that function as pentameric, ligand-gated cation channels with high
  calcium permeability among other activities. nAChRs are excitatory
  neurotrasnmitter receptors formed by a collection of nAChR subunits known
  to mediate synaptic transmission in the nervous system and the
  neuromuscular junction.
- **CHRNA3** (350): the same sentence as CHRNA4.

("neurotrasnmitter" is a spelling slip in the source text. The cleaning
did not make it and does not fix it.)

### Really odd: citations and notes in round brackets stay

- **456** sentences still have "(PubMed:...)".
- **34** sentences still have "(By similarity)", "(Probable)" or "(Potential)".
- 489 sentences have one or the other.

These are evidence tags of a second kind. The order named only curly
braces, so the function leaves them. All are listed in `odd_cases.md`
under `pubmed_citation` and `similarity_note`, and marked in the CSV. The
worst case is SIRT1: 1,219 characters, most of it a list of paper numbers.

### Odd in meaning: 14 sentences where a label was removed

With the label gone, the sentence no longer says it is about one form of
the protein, or about a piece cut from it. All 14, with the removed label:

| Protein | Removed label | Cleaned sentence |
|---|---|---|
| TSLP | [Isoform 1] | Cytokine that induces the release of T-cell-attracting chemokines from monocytes and, in particular, enhances the maturation of CD11c(+) dendritic cells. |
| CLN5 | [Bis(monoacylglycero)phosphate synthase CLN5, secreted form] | Catalyzes the synthesis of bis(monoacylglycero)phosphate (BMP) via transacylation of 2 molecules of lysophosphatidylglycerol (LPG) (PubMed:37708259). |
| UMOD | [Uromodulin] | Functions in biogenesis and organization of the apical membrane of epithelial cells of the thick ascending limb of Henle's loop (TALH), where it promotes formation of complex filamentous gel-like structure that may play a role in the water barrier permeability (Probable). |
| THRA | [Isoform Alpha-1] | Nuclear hormone receptor that can act as a repressor or activator of transcription. |
| UBC | [Ubiquitin] | Exists either covalently attached to another protein, or free (unanchored). |
| UBA52 | [Ubiquitin] | Exists either covalently attached to another protein, or free (unanchored). |
| RPS27A | [Ubiquitin] | Exists either covalently attached to another protein, or free (unanchored). |
| UBB | [Ubiquitin] | Exists either covalently attached to another protein, or free (unanchored). |
| HTT | [Huntingtin] | May play a role in microtubule-mediated transport or vesicle function. |
| VEGFA | [N-VEGF] | Participates in the induction of key genes involved in the response to hypoxia and in the induction of angiogenesis such as HIF1A (PubMed:35455969). |
| PLG | [Plasmin] | Protease which primary function is to degrade fibrin, the main component of blood clots (PubMed:6094526, PubMed:6919539). |
| KCNA3 | [Isoform 1] | Mediates the voltage-dependent potassium ion permeability of excitable membranes. |
| GCG | [Glucagon] | Plays a key role in glucose metabolism and homeostasis. |
| CACNA1F | [Isoform 1] | Voltage-sensitive calcium channels (VSCC) mediate the entry of calcium ions into excitable cells and are also involved in a variety of calcium-dependent processes, including muscle contraction, hormone or neurotransmitter release, gene expression, cell motility, cell division and cell death. |

The four "[Ubiquitin]" ones read oddly on their own: "Exists either
covalently attached to another protein, or free" does not say what exists.

### Odd as it arrived: 4 sentences with a space before a hyphen

The cleaning did not cause these and has no rule for them.

- **PPT1** (212): Has thioesterase activity against fatty acid thioesters
  with 14 -18 carbons, including palmitoyl-CoA,
  S-palmitoyl-N-acetylcysteamine, and palmitoylated proteins
  (PubMed:12855696, PubMed:26731412, PubMed:8816748).
- **SSTR2** (37): Receptor for somatostatin-14 and -28.
- **SSTR1** (76): Receptor for somatostatin with higher affinity for
  somatostatin-14 than -28.
- **SSTR3** (37): Receptor for somatostatin-14 and -28.

Only PPT1 looks like a slip; the three SSTR ones are normal writing.

### Very short: 8 sentences under 25 characters

Correctly cleaned, but they say little: ADORA2B "Receptor for adenosine.",
WWOX "Putative oxidoreductase.", PLS3 "Actin-bundling protein.", MYH11
"Muscle contraction.", APC "Tumor suppressor.", LMAN1 "Mannose-specific
lectin.", BDKRB2 "Receptor for bradykinin.", LHX3 "Transcription factor."

### Flagged, read, and fine

- **Ends with a very short word (5):** KCNJ5 and KCNJ3 end "...than out of
  it.", F8 ends "...factor Xa.", F11 ends "...factor IX.", NDUFAF1 ends
  "...complex I." All five are true sentence ends, not abbreviations.
- **Abbreviation stop skipped (1):** BAG3 has "e.g." twice; the rule
  carried on past both, correctly. Its sentence (251 characters) is whole.
- **Full stop inside the sentence (5):** BAG3 (the "e.g." above, fine) and
  the four two-sentence cases listed above.
- **Does not start with a capital (2):** SECISBP2 starts "mRNA-binding
  protein..." and CDK5R1 starts "p35 is a neuron specific activator of
  CDK5." Both are how the names are written.
- **Hyphen and space left (23):** all 23 are real hanging hyphens: sixteen
  tubulins ("alpha- and beta-tubulin"), SLC6A2 and SLC6A3 ("sodium- and
  chloride-dependent"), PRKCQ ("phospholipid- and diacylglycerol"), CTSG
  ("trypsin- and chymotrypsin-like"), PTEN ("serine- and threonine-"),
  TLR4 ("pathogen- and damage-associated"), HR ("mono- and dimethylated"),
  LAT ("(T-cell antigen receptor)- and pre-TCR-mediated"), FUT2 ("O- and
  N-linked").
- **Line-wrap joins (76 sentences, 82 joins):** I read all 82. Each joined
  a word that had been split at a hyphen ("T-cell- attracting", "G
  protein- coupled", "1,4,5- trisphosphate"). I saw no wrong join. All 82
  are shown in `odd_cases.md` under `wrap_joined`.

### Totals

| | Sentences (of 994) |
|---|---|
| No flag at all | 429 |
| Only a citation or similarity-note flag | 433 |
| Any other flag | 132 |

Of the 132, the ones I judge really odd after reading are the 4
two-sentence cases, the 14 label cases and PPT1.

## 4. The 20 shortest and 20 longest

In full in `extremes.md`. The shortest is APC, "Tumor suppressor." (17).
The longest is SIRT1 (1,219). Every one of the 20 longest is long because
of its "(PubMed:...)" list.

## 5. The CSV

`sentences.csv`, 1,011 rows, one per protein: gene id, symbol, biotype,
number of texts, raw first text, raw other texts, cleaned first sentence,
length, flags.

## What I did not verify

- I did not read all 994 cleaned sentences. I read every flagged group
  except the citation groups, the 40 shortest and longest, and a few dozen
  others. An oddity that no flag looks for could be among the 429 unflagged.
- A hyphen lost at a line wrap leaves no mark ("proinflammatory" where
  UniProt writes "pro-inflammatory", seen in study P8). The cleaning cannot
  see or mend these, and I did not count them here because UniProt was not
  asked.
- Spelling slips in the source are not looked for. I met one by chance.
- Whether the first text in the list is the best one to use when a protein
  has several (155 do). I did not compare them.
- The abbreviation list was written by me. Only "e.g." came up in these
  1,011 proteins; the other entries were never tested by real text.
- Whether the rules hold for proteins outside these 1,011, or in another
  Open Targets release.
- Whether any sentence is true, plain enough for a card, or safe to show
  next to a medicine. This study is only about cleaning.
- Nothing was tried in Moonlight, with Gemini, or with the grounding check.
- The tests were not run: the session has no `fastapi`, and no code or
  test changed.

## Files and how to recount

| File | What it is |
|---|---|
| `fetch.py` | Asks Open Targets. Skips proteins already saved. |
| `clean.py` | The one cleaning function. |
| `recount.py` | Recounts everything from saved files. No network. |
| `proteins.json` | The 59 diseases, their lists, the 1,011 proteins |
| `responses/*.json` | 1,011 raw answers |
| `index.jsonl` | One line per request |
| `data_version_before.json`, `data_version_after.json` | Data version |
| `counts.json` | Every number in this report |
| `sentences.csv` | One row per protein |
| `odd_cases.md` | Every flagged sentence, in full, by flag |
| `extremes.md` | 20 shortest and 20 longest, in full |

```bash
python3 fixtures/probe_p8/cleaned_sentences/recount.py
```

Run it twice: `counts.json`, `sentences.csv`, `odd_cases.md` and
`extremes.md` must not change. `fetch.py` reads the disease lists with
`git show` from `origin/probe-baseline` and `origin/probe-key-diseases`,
so those branches must be fetched to run it again. It also checks the
field names against the schema saved in `../open_targets_function/schema/`.

Two extra requests are not in `index.jsonl`: the two data-version
questions (saved). A 20-second trial run before the main run asked the
first 13 proteins; those answers were kept and are in `index.jsonl`.
