# Study P8: what could UniProt add to a Moonlight card?

Read-only study. No Moonlight code or test was changed. Everything here is
under `fixtures/probe_p8/`. UniProt release 2026_04 (4 November 2026),
fetched 22 November 2026.

## The one question

**What plain fact about a protein could a Moonlight card gain that it lacks today?**

**One fact: a sentence saying what the protein does.** Today a card knows a
protein's short code, its name and its score (for example `FLG`,
"filaggrin", 0.75). It does not say what the protein is for. UniProt has
that sentence for 230 of the 231 proteins we looked at.

**For everything else the answer is "little".** UniProt's disease notes
mostly repeat what Open Targets already told us, and UniProt almost never
says which way a disease needs a protein turned (see section 3). It does
not fill the gap in our safety rule about direction.

A caution about "plain": the sentences are plain for a scientist, not for
a nine-year-old. Some are easy ("Receptor for adenosine."). Some are not
("Component of N-methyl-D-aspartate (NMDA) receptors (NMDARs) that function
as heterotetrameric, ligand-gated cation channels..."). All 230 first
sentences are in `proteins.csv` so Kashish can read them and judge.

## What was looked at

- Ten diseases from `fixtures/probe_p5/diseases.json` (branch
  `probe-baseline`). The order did not say which ten, so I took the first
  4 COMMON, first 3 CANCER and first 3 RARE in that file's order: asthma,
  type 2 diabetes mellitus, epilepsy, rheumatoid arthritis, breast cancer,
  prostate cancer, colorectal cancer, cystic fibrosis, Duchenne muscular
  dystrophy, spinal muscular atrophy.
- Their top 25 proteins, read from probe_p5's saved results: 250
  disease-and-protein **slots**, 231 different **proteins** (some proteins
  are in two diseases' lists).
- For each protein, one question to UniProt: "which reviewed human entry
  points at this Ensembl gene id?" 231 requests, one per second.

Result: **231 of 231 proteins have exactly one reviewed human entry.** None
had zero, none had two. For 230 the gene code matches Open Targets'. The
one difference is a naming one: Open Targets says `IL33R`, UniProt says
`IL1RL1` (entry Q01638) for the same Ensembl gene.

## 1. Function sentence

| | count |
|---|---|
| Proteins with function text | 230 of 231 (missing: CLN6) |
| Slots with function text | 249 of 250 |

Length, in characters:

| | shortest | middle (median) | longest | average |
|---|---|---|---|---|
| Whole function text | 39 | 901 | 7,088 | 1,118 |
| First sentence only | 17 | 130 | 691 | 138 |

The first sentence has 18 words in the middle case (2 to 95). 138 of 230
first sentences are 150 characters or less; 227 of 230 are 300 or less.
The whole text is far too long for a card; only the first sentence is
card-sized. "First sentence" is cut by a simple rule in `recount.py` (text
up to the first full stop followed by a capital letter, with the
"(PubMed:...)" tags removed), so a few cuts are imperfect.

## 2. Disease-involvement notes

| | count |
|---|---|
| Proteins with any disease note | 168 of 231 |
| ...with at least one named disease | 165 |
| ...with only a free-text note | 3 |
| Named diseases per protein that has one | 1 to 15, middle 2 |

Does the note name **our** disease? Counted per slot. "Names ours" means
our disease's name, or one of Open Targets' exact other names for it,
appears inside UniProt's disease name. That also catches named sub-types
("Colorectal cancer 12", "Developmental and epileptic encephalopathy 11").

| Disease | Slots | Has a note | Names ours | Only mentions ours in the text |
|---|---|---|---|---|
| asthma | 25 | 8 | 0 | 1 |
| type 2 diabetes mellitus | 25 | 20 | 12 | 1 |
| epilepsy | 25 | 25 | 20 | 2 |
| rheumatoid arthritis | 25 | 17 | 5 | 0 |
| breast cancer | 25 | 24 | 8 | 2 |
| prostate cancer | 25 | 20 | 5 | 0 |
| colorectal cancer | 25 | 25 | 8 | 4 |
| cystic fibrosis | 25 | 11 | 1 | 0 |
| Duchenne muscular dystrophy | 25 | 10 | 1 | 0 |
| spinal muscular atrophy | 25 | 25 | 9 | 2 |
| **All** | **250** | **185** | **69** | **12** |

So 185 slots have a note, but only 69 name our disease (81 if text-only
mentions count). The other notes are about a *different* disease. In
asthma, for example, the notes are about ichthyosis, allergic rhinitis and
depression, never asthma. Showing them on an asthma card would put another
disease's name next to a medicine, which could confuse a reader.

UniProt's notes are mostly about inherited diseases caused by a change in
one gene. That is why epilepsy scores high and asthma scores zero. Every
row is in `pairs.csv`.

## 3. Gain or loss of function

Does the entry use the words "gain of function" or "loss of function"?

| | proteins (of 231) |
|---|---|
| "gain of function" anywhere | 13 |
| "loss of function" anywhere | 15 |
| Either one, anywhere | 24 |
| Both in the same entry | 4 |
| In the function text | 0 |
| In a disease note | 1 (SCN2A) |
| Only on variant or lab-mutation lines | 23 |

Where the words appear: 75 natural-variant lines and 8 lab-mutation lines.
A variant line describes **one spelling change in one family's gene**, for
example "in DRVT; loss-of-function mutation resulting in complete absence
of sodium current". It is not a statement about the whole disease.

Per slot: in **8 of 250** slots a variant line tagged with our own disease
says gain or loss. Seven are epilepsy (SCN1A, SCN2A, SCN8A, SCN3A, KCNQ2,
GRIN2A, KCNT1) and one is spinal muscular atrophy (GARS1). Three of those
eight say **both** gain and loss, for different variants. In **0 of 250**
slots does the disease note for our disease itself use any direction word.

Wider words were also counted (in any part of the entry): "dominant
negative" 8 proteins, "haploinsufficiency" 1, "constitutive activation"
12, "activating / inactivating" 32. The last one is mostly ordinary
function wording ("activating kinase"), not a direction for a disease.

Plain reading: UniProt does not tell us which way a disease needs the
protein turned. Where it says anything, it is about single inherited
variants, it covers about 3 slots in 100, and it sometimes says both ways.
A volume-knob picture: UniProt sometimes tells us one family's knob was
stuck high or low; it does not tell us where the knob should be set.

## 4. Licence and attribution

Saved in `licence/`, fetched from UniProt itself.

- Licence page (`help_license.json`): "We have chosen to apply the
  Creative Commons Attribution 4.0 International (CC BY 4.0) License to all
  copyrightable parts of our databases."
- Each entry in text form (`P20930.txt`) carries: "Copyrighted by the
  UniProt Consortium, see https://www.uniprot.org/terms / Distributed under
  the Creative Commons Attribution (CC BY 4.0) License".
- How to cite (`help_publications.json`): "The UniProt Consortium. UniProt:
  the Universal Protein Knowledgebase in 2025. Nucleic Acids Res.
  53:D609–D617 (2025)", https://doi.org/10.1093/nar/gkae1010. The page
  says "please consider citing"; it does not give a fixed credit line for
  a website.
- UniProt's own disclaimer: "We make no warranties regarding the
  correctness of the data..." and "Any medical or genetic information is
  provided for research, educational and informational purposes only. It
  is not in any way intended to be used as a substitute for professional
  medical advice, diagnosis, treatment or care." This fits Moonlight's
  safety line.

What CC BY 4.0 asks in general is: give credit, link to the licence, and
say if you changed the text. That last part matters if Gemini rewrites a
UniProt sentence into simpler words. This general summary is from my
memory of CC BY 4.0, not from a page I fetched (see below).

## 5. Things Kashish would need to decide before any of this is used

- CLAUDE.md says Open Targets and Gemini are the only two outside data
  sources. Using UniProt on a card means changing that rule.
- Something to check first, which could avoid a third source: I believe
  Open Targets has its own protein-function field that is copied from
  UniProt. **I did not check this.** It is from memory, and the project
  rule is never to trust a field name from memory. A small Open Targets
  probe would settle it.
- If a function sentence is shown, it needs its own source label, and it
  must not sit where a reader could take it as a reason the medicine works.

## What I did not verify

- Whether the ten diseases I picked are the ten Kashish meant.
- Whether the first sentences are plain enough. I read about 20, not all
  230. No reading-level measure was run.
- The "names our disease" count is word matching, not a doctor's
  judgement. It can miss a disease written differently (HNF1A's
  "Maturity-onset diabetes of the young 3" is not counted for type 2
  diabetes) and it counts named sub-types as a match.
- The gain/loss count looks for those exact words (and four wider
  phrases). An entry could describe direction in other words and be missed.
- The variant-line matching by disease short code was not hand-checked
  beyond the eight hits.
- Whether each UniProt entry is the right protein for the gene, beyond
  "UniProt says this reviewed human entry points at this Ensembl gene id"
  and the gene code matching for 230 of 231.
- Proteins outside the top 25, and the other 40 diseases in probe_p5.
- The full CC BY 4.0 legal text and https://www.uniprot.org/terms were not
  fetched. Only rest.uniprot.org was contacted.
- Whether Open Targets already carries the UniProt function text (see
  section 5).
- Nothing was tried on a real card, with Gemini, or with the grounding check.

## Files and how to recount

| File | What it is |
|---|---|
| `fetch.py` | Asks UniProt. Skips proteins already saved. |
| `recount.py` | Recounts everything from the saved files. No network. |
| `responses/*.json.gz` | 231 raw UniProt answers, gzipped (24.8 MB unzipped, 4.6 MB zipped) |
| `index.jsonl` | One line per request: question, size, release, time |
| `diseases.json` | The ten diseases, their 25 proteins, their other names |
| `counts.json` | Every number in this report |
| `pairs.csv` | 250 rows, one per slot |
| `proteins.csv` | 231 rows, one per protein, with its first function sentence |
| `licence/` | UniProt's licence page, cite page, and one entry in text form |

```bash
python3 fixtures/probe_p8/recount.py
```

Run it twice: `counts.json`, `pairs.csv` and `proteins.csv` must not
change. `fetch.py` reads the disease list with `git show` from
`origin/probe-baseline`, so that branch must be fetched to run it again.

Three extra requests were made that are not in `index.jsonl`: two reach
tests before the run (entry P04637 and one search, not kept) and the three
files in `licence/`.
