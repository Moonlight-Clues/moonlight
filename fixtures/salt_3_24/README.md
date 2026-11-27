# Ticket 3.24: the 3.23 pages as main sent them

`before/<disease id>.json` is each page as main (6728bce) built it, with the
real `moonlight/salt_parents.json` on. It was written before any 3.24 code
change, by the builders in `tests/test_salt_loose_ends_3_24.py` (`PAGES`),
from saved answers only (no network).

- AL amyloidosis, Huntington disease, essential tremor and type 2 diabetes:
  the whole `/api/clues` answer.
- Acute hepatic porphyria, amyloidosis and myasthenia gravis: the Approved,
  narrower and wider-group cards built from the disease's own saved list
  alone (only the list is saved for these).

`test_every_other_card_on_the_3_23_pages_is_unchanged` compares today's pages
with these, letter for letter, except the changes the test file names
(`CHANGED`).
