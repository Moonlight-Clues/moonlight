## Things to know when reading the numbers

Facts about how the night went. None is a judgement.

- **Two of the eight names were not studied, as the order says.** "Addison's disease": the
  search put no entry on top as exactly what was typed (its two matches are listed in
  section 0). "hemochromatosis": two entries are exactly what was typed, `hemochromatosis`
  (EFO_1000642) and `hemochromatosis type 1` (MONDO_0021001, which Open Targets also calls
  "hemochromatosis"). I did not choose between them.
- **Two names were found under another database name.** "primary sclerosing cholangitis" is
  an exact "also called" name of the entry `sclerosing cholangitis` (MONDO_0018646), and
  "interstitial cystitis" of `chronic interstitial cystitis` (EFO_1000869). Each was the
  only entry that was exactly what was typed, so by the rule it was studied. The cards are
  for the database entry.
- **"Anaphylaxis" was searched once.** It is both one of the eight names and one of the two
  extra searches. Moonlight kept the first answer in its notebook, so the second time
  nothing was sent. "drug anaphylaxis" was a search of its own. Both are in section 0.
- **The same scripts as probe_p5**, copied into this folder. Only the choice of diseases
  (search instead of a list) and this report's search section are new. probe_p5's folder
  was not touched.
- **Open Targets was asked each "which medicines?" question twice**, and a third time if the
  two answers differed, because that is what Moonlight's own code does.
- **One host said "slow down".** `www.ema.europa.eu` answered 429 twice during the link check.
  Each time the script waited a minute, doubled its gap for that host and asked that link
  again. Every link was finished. Open Targets never refused.
- **A card shows one link.** Only that link was asked. A link shown by cards of several
  diseases was asked once.

## Things I did not verify

- **Whether the entry the search found is the disease Kashish meant.** The id was taken by
  Moonlight's own rule only. I did not judge whether `sclerosing cholangitis` is the right
  entry for "primary sclerosing cholangitis", or `chronic interstitial cystitis` for
  "interstitial cystitis".
- **Gemini's "did you mean".** The live search page also asks Gemini for suggestions. That
  side lane was not called, so this study does not show what suggestions a visitor would see
  for these words.
- **Whether a link that answers 200 shows the right page, or any real page.** I only read the
  status. probe_p5 asked one made-up link per host (its `link_controls.jsonl`):
  ClinicalTrials.gov, TTD and the ATC site answered 200 for a link that cannot exist, and
  DailyMed sent it to its front page. That check was not repeated tonight. So "0 dead" means
  "no 404, 410 or DNS failure", not "every link works".
- **What a person's browser would see.** The links were asked from this session's machine,
  through its proxy, with a plain program.
- **Whether any withdrawal, approval, trial, proof group or direction is right or wrong.** I
  cannot tell, and nothing here is labelled so.
- **Whether a medicine "not approved elsewhere" is truly approved nowhere.** For a medicine on
  none of the top 25 proteins, only the forms on the disease's own list could be looked at.
- **The live site.** Moonlight's site was not called. The cards were built by the repo's code
  at the commit named above, and matched what `api.clues()` returns when run here.
- **Open Targets' completeness**, and any disease outside these six.
- **The tests.** No code under `moonlight/`, `web/` or `tests/` was touched. The test suite
  was run once at the end only to see that the new folder breaks nothing.
