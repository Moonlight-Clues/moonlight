# fixtures/withdrawal_wording_2_65: ticket 2.65

- `withdrawal_lines_before_2.65.json`: every Approved-tab card's
  `withdrawal_note` (main list, narrower box, wider-group box) on the nine
  saved pages of `tests/old_flag_saved.py`, made by main a8eb384 before this
  ticket, under the test set-up of `tests/conftest.py`. Missing note: null.
- `screenshots/`: 390 px wide cards (deviceScaleFactor 2), drawn by
  `web/index.html` from the saved type 2 diabetes page.
  Files marked TEST-ENTRY use entries that exist only in the tests
  (`moonlight/discontinued.json` ships empty and no real W4 card sits in a
  folded box on a saved page). They show how the lines look, not real data.
  `w4-main-list-tolazamide-real-390px.png` is the real card, unchanged.
