## Things to know when reading the numbers

These are facts about how the study was run. None of them is a judgement.

- **More requests than expected.** The task guessed about 1,300 requests. The main run sent
  2,728. Moonlight's own code asks every "which medicines?" question twice (a third time if
  the two answers differ), and it also asks for the medicine list of each disease one step up
  and one step down. 890 different proteins were asked about (1,782 requests) and 397
  disease lists (794 requests). The alfuzosin step added 119 more.
- **Open Targets gave two different answers twice.** For 2 of the 1,287 "which medicines?"
  questions (proteins ENSG00000105650 and ENSG00000160752) the first two answers were not
  letter for letter the same, so Moonlight asked a third time and kept the fullest, as its
  rule says. All answers are saved. The medicines named were the same each time.
- **Which diseases.** 23 COMMON, 7 CANCER, 20 RARE: the ones probe P3 had *found* by exact
  name, in P3's order. P3's COMMON set has 30 names but 7 were not found there
  (hypertension, migraine, Crohn's disease, multiple sclerosis, HIV infection, hepatitis B,
  hepatitis C), so they have no id to take and are not here. Acromegaly was already among
  the first 20 RARE, so nothing was added by search.
- **Every pair had at least one action word.** No medicine-protein pair came with an empty
  action list. Every "unknown" in A2 comes from a word that is on neither of Moonlight's lists.
- **Words that are on neither list but contain a listed word.** Moonlight compares whole
  values. So INVERSE AGONIST, PARTIAL AGONIST, ALLOSTERIC ANTAGONIST, ANTISENSE INHIBITOR,
  RNAI INHIBITOR, NEGATIVE ALLOSTERIC MODULATOR and NEGATIVE MODULATOR all give "unknown",
  not up or down. Whether any of them should count as up or down is Kashish's decision with
  a doctor. This report does not say.
- **A pair with one listed word and one unlisted word takes the listed word's direction.**
  Example from the data: FULVESTRANT on ESR1 has ANTAGONIST and DEGRADER and shows "down".
- **Alfuzosin.** The tester's "up" was reproduced, in benign prostatic hyperplasia and
  erectile dysfunction. The word behind it is Open Targets' own `actionType` for alfuzosin,
  AGONIST, on ADRA1A, ADRA1B and ADRA1D. Moonlight's mapping did what it was written to do
  with that word. A3 also lists the other medicines on those three proteins with their
  words, for a doctor to compare.
- **Part B compares cards with the main Approved list only.** Medicines in the two folded
  boxes (narrower disease, wider group) were not used to decide one-way or both-ways. An In
  trials card can also be a medicine that sits in one of those boxes; it is still counted as
  an In trials card.
- **Part B only sees proteins among the top 25 for the disease.** An Approved medicine whose
  proteins are not among them has no path, so it decides nothing. 4 diseases have no
  Approved medicine with an up or down path at all, so they cannot have an opposite card.

## What I did not verify

- **Whether any direction is pharmacologically right.** I cannot tell. Every "up", "down",
  "mixed" and "unknown" in this report is what Moonlight's code makes of Open Targets'
  `actionType` word. Nothing here is labelled right or wrong, including alfuzosin.
- **Whether any opposite pair is a real problem or normal practice.** I cannot tell. Some
  medicines for one disease do turn the same protein opposite ways on purpose (B9 lists the
  proteins where the Approved medicines themselves disagree). The B8 list is a list of what
  the data says, not a list of mistakes. A doctor has to judge it.
- **Which direction each disease needs.** The data does not say, and this study did not try
  to work it out.
- **The live site.** As instructed, the Moonlight site and Gemini were not called. The cards
  here were built by the repo's code at commit 1f0f639 on the day of the run (Open Targets
  data 26.09). If the deployed site runs other code or other data, its cards may differ. I
  did not check what the page draws, or what Gemini's text says about direction.
- **The diseases outside these 50.** The counts describe these 50 only. They are not a
  random sample, so "34 of 50" should not be read as "68% of all diseases".
- **Open Targets' completeness.** A missing mechanism row, a missing medicine, or a short
  answer on both asks would not be noticed here.
- **The A4 doctor table is unreviewed.** No doctor has looked at it yet.
- **The tests.** No code under moonlight/, web/ or tests/ was touched, and the test suite was
  not run, because nothing it tests changed.
