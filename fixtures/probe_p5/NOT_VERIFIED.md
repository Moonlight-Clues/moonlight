## Things to know when reading the numbers

Facts about how the night went. None is a judgement.

- **The session could not reach Open Targets or the link hosts at first.** Its network rules
  blocked them. Kashish approved a new environment, `night-watch-links`, that allows Open
  Targets and the link hosts met in the earlier studies' saved answers, and later one more
  host, `atcddd.fhi.no`, because every `www.whocc.no` link redirects there.
- **The session's machine restarted once, at 15:17:33 UTC.** It cut off both scripts. Both
  were started again and went on from what was saved. One Open Targets request and five link
  requests failed at that moment, inside the session's own proxy, before reaching any host.
  The Open Targets question was asked again by the second run. The five links were asked
  again at the end (`check_links.py --retry-unreached`); their failed tries are kept in
  `links.jsonl`.
- **The first 34 `www.whocc.no` links were asked in two parts.** The first hop (a 301) was
  asked before `atcddd.fhi.no` was allowed, and the second hop after. No hop was asked twice.
- **One host said "slow down".** `www.ema.europa.eu` answered 429 4 times during the link
  check (and once more for the made-up link). Each time the script waited a minute, doubled
  its gap for that host and asked that link again. Every link was finished. Open Targets never
  refused.
- **Open Targets was asked each "which medicines?" question twice**, and a third time if the
  two answers differed, because that is what Moonlight's own code does. That is why there are
  many more requests than questions.
- **A card shows one link.** Its medicine may have many more report links in the data. Only
  the one link the card shows ("Source record") was asked.
- **A link shown by cards of several diseases was asked once.**
- **TRIALS counts medicine families**, the way Moonlight does: a medicine and its tablet forms
  are one. "Open Targets lists it in trials" was read from the disease's own list only.

## Things I did not verify

- **Whether a link that answers 200 shows the right page, or any real page.** I only read the
  status. The table "What these hosts answer for a link that cannot exist" shows that some
  hosts answer 200 for a made-up link, or redirect it to their front page. For those hosts a
  count of 404s cannot find a dead link. So "0 dead" for such a host means "no 404, 410 or DNS
  failure", not "every link works".
- **What a person's browser would see.** The links were asked from this session's machine,
  through its proxy, with a plain program, not a browser. A host may answer a browser, another
  country or another day differently. DNS was looked up by the proxy, not by this machine, so
  a DNS failure might have looked like a different error here. None was met.
- **Whether any withdrawal, approval, trial, proof group or direction is right or wrong.** I
  cannot tell, and nothing here is labelled so. Each number says what Open Targets' data holds
  and what Moonlight's code makes of it.
- **Whether a medicine "not approved elsewhere" is truly approved nowhere.** For a medicine on
  one of the top 25 proteins, this is Moonlight's own finding from all the forms it met. For a
  medicine on none of them, only the forms on the disease's own list could be looked at;
  another form of the same medicine might be approved.
- **Trials Open Targets does not list.** Only Open Targets was asked. ClinicalTrials.gov itself
  was not searched.
- **The live site.** As in probe_p4, Moonlight's site and Gemini were not called. The cards
  were built by the repo's code at the commit named above, and matched what `api.clues()`
  returns when run here. If the deployed site runs other code, other data, or has other saved
  answers, its cards may differ. What the page draws on screen was not looked at.
- **Explanations.** No Gemini text was made or read, so nothing here says what an explanation
  says about direction, trials or proof.
- **Open Targets' completeness.** A missing medicine, report or mechanism row, or an answer
  that was short on both asks, would not be noticed.
- **Why malaria has 5 more New clues cards than in probe_p4.** The data version is the same
  (26.09) and the code changed in between. I counted the difference and did not look into it.
- **The diseases outside these 50.** They are probe_p4's 50, picked by people. The counts
  describe them only.
- **The proof groups for box cards** were read from the lists of the narrower or wider
  entries that name the medicine, all together. probe_p3 never looked at those.
- **The tests.** No code under `moonlight/`, `web/` or `tests/` was touched. The test suite
  was run once at the end only to see that the new folder breaks nothing; it proves nothing
  about this study.
