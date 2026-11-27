"""Ticket 2.66 (sheet W3). The public corrections page, /corrections.

One row per entry of the hand-written lists, newest first: date, disease
name, medicine name, what the card now shows (in the card's own words) and
the source link. Built from the lists at start-up; no network at request time.

Most tests use small made-up lists, so they do not depend on the real files.
The tests at the end read the real files: they fail while any list ID has no
name in moonlight/names.json, or any row has no link (Kashish's decisions of
27 Nov, A and B: New Bot's data PR adds both, and merges first).
"""

import json
import pathlib
import re
import shutil
import subprocess
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from moonlight import api, corrections_page, engine

ROOT = pathlib.Path(__file__).resolve().parent.parent
PAGE_FILE = ROOT / "web" / "index.html"
HEADING = ("Every change we made by hand to the database's list, with the label we "
           "read. If you find a mistake, tell us.")
DAILYMED = "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=codeine-label"

# Small made-up lists, one entry or more of each kind.
LISTS = {
    "corrections": [
        {"medicine_id": "CHEMBL485", "disease_id": "MONDO_0005277", "date": "2026-11-26",
         "note": engine.SECOND_NOTE, "label": DAILYMED},
        {"medicine_id": "CHEMBL641", "disease_id": "MONDO_0004975", "date": "2026-11-16",
         "note": engine.CORRECTION_NOTE, "label": "https://example.org/a"},
    ],
    "approvals": [
        {"medicine_id": "CHEMBL27", "name": "Propranolol", "disease_id": "MONDO_0003233",
         "date": "2026-11-23", "label": "https://example.org/b", "limited": True},
    ],
    "limits": [
        {"medicine_id": "CHEMBL27", "disease_id": "MONDO_0004975", "date": "2026-11-24",
         "label": "https://example.org/c"},
    ],
    "confirmed": [
        {"medicine_id": "CHEMBL641", "disease_id": "MONDO_0003233", "date": "2026-11-24",
         "label": "https://example.org/d"},
    ],
    "withdrawals": [
        {"medicine_id": "CHEMBL485", "disease_id": "MONDO_0004975", "date": "2026-11-25",
         "source": "https://example.org/e"},
        {"medicine_id": "CHEMBL641", "disease_id": "MONDO_0005277", "date": "2026-11-25",
         "source": "https://example.org/f", "region": "US"},
    ],
    "salt_parents": {
        "CHEMBL9001": {"parent": "CHEMBL27", "source": "https://example.org/g",
                       "date": "2026-11-27"},
    },
    "discontinued": [
        {"medicine_id": "CHEMBL641", "date": "2026-11-20", "source": "https://example.org/h"},
    ],
    "pmda_summaries": [
        {"medicine_id": "CHEMBL27", "disease_id": "MONDO_0005277", "date": "2026-11-26",
         "summary_date": "2013-06-28", "date_source": "PMDA list, page 1",
         "approval_type": "original", "link": "https://www.pmda.go.jp/files/x.pdf"},
    ],
}
NAMES = {
    "CHEMBL485": "CODEINE", "CHEMBL641": "MEMANTINE", "CHEMBL27": "PROPRANOLOL",
    "CHEMBL9001": "PROPRANOLOL HYDROCHLORIDE",
    "MONDO_0005277": "migraine", "MONDO_0004975": "Alzheimer disease",
    "MONDO_0003233": "hemangioma",
}
LINK_FIELD = {"corrections": "label", "approvals": "label", "limits": "label",
              "confirmed": "label", "withdrawals": "source", "salt_parents": "source",
              "discontinued": "source", "pmda_summaries": "link"}


def entries(lists):
    """Every entry of the lists, with its list's name and its link."""
    found = []
    for name, entries_ in lists.items():
        if name == "salt_parents":
            for salt, row in entries_.items():
                found.append((name, dict(row, medicine_id=salt), row["source"]))
        else:
            for entry in entries_:
                found.append((name, entry, entry[LINK_FIELD[name]]))
    return found


@pytest.fixture
def lists():
    """Replace the one read function with the made-up lists and names."""
    data = json.loads(json.dumps(LISTS))
    names = dict(NAMES)

    def read(name):
        if name == "names":
            return names
        return data.get(name)

    with patch.object(corrections_page, "_read", side_effect=read):
        yield data, names


def test_one_row_per_entry_of_every_list(lists):
    data, _ = lists
    assert len(corrections_page.rows()) == len(entries(data)) == 10


def test_each_rows_source_is_its_entrys_link(lists):
    data, _ = lists
    links = sorted(link for _, _, link in entries(data))
    assert sorted(row.source for row in corrections_page.rows()) == links


def test_no_list_entry_is_missing(lists):
    data, _ = lists
    shown = {(row.date, row.source) for row in corrections_page.rows()}
    for _, entry, link in entries(data):
        assert (entry["date"], link) in shown


def test_newest_first(lists):
    dates = [row.date for row in corrections_page.rows()]
    assert dates == sorted(dates, reverse=True)


def test_the_example_row(lists):
    """EXAMPLE: 26 Nov 2026 · migraine · Codeine · red warning · DailyMed label."""
    row = next(r for r in corrections_page.rows() if r.source == DAILYMED)
    assert (row.shown_date, row.disease, row.medicine) == ("26 Nov 2026", "migraine", "Codeine")
    assert row.shows == engine.SECOND_NOTE  # the card's red sentence, exactly


def by_source(source):
    return next(r for r in corrections_page.rows() if r.source == source)


def test_each_list_shows_the_cards_own_words(lists):
    assert by_source("https://example.org/a").shows == engine.WRONG_WARNING
    assert by_source("https://example.org/b").shows == (  # limited: both lines
        "This approval is missing from the database. We added it from the official label.\n"
        "The label covers only some people with this disease.")
    assert by_source("https://example.org/c").shows == (
        "The label covers only some people with this disease.")
    assert by_source("https://example.org/d").shows == "Source record opens the label we read."
    assert by_source("https://example.org/e").shows == engine.HAND_WITHDRAWAL_LINE
    assert by_source("https://example.org/f").shows == engine.REGION_LINES["US"]
    assert by_source("https://www.pmda.go.jp/files/x.pdf").shows == engine.pmda_line("2013")
    assert by_source("https://example.org/h").shows == engine.DISCONTINUED_LINE


def test_an_approval_for_only_some_people_shows_both_lines(lists):
    """Kashish, 27 Nov: both lines, as the card shows them."""
    data, _ = lists
    data["approvals"].append(
        {"medicine_id": "CHEMBL485", "name": "Codeine", "disease_id": "MONDO_0003233",
         "date": "2026-11-23", "label": "https://example.org/b2"})
    assert by_source("https://example.org/b").lines == (engine.ADDED_LINE, engine.LIMITED_LINE)
    assert by_source("https://example.org/b2").lines == (engine.ADDED_LINE,)
    page = corrections_page.page_html()
    assert f"{engine.ADDED_LINE}<br>{engine.LIMITED_LINE}" in page


def test_a_withdrawal_with_a_region_is_on_all_pages(lists):
    """Kashish, 27 Nov: "All pages", as 2.65 shows the region line on every page."""
    assert by_source("https://example.org/f").disease == "All pages"
    assert by_source("https://example.org/e").disease == "Alzheimer disease"


def test_a_salt_row_lists_the_forms_on_all_pages(lists):
    row = by_source("https://example.org/g")
    assert row.disease == "All pages"
    assert row.medicine == "Propranolol"
    assert row.shows == "Forms: Propranolol, Propranolol Hydrochloride"


def test_a_list_that_is_not_there_or_empty_adds_no_row(lists):
    data, _ = lists
    del data["pmda_summaries"]
    data["discontinued"] = []
    assert len(corrections_page.rows()) == 8


def test_an_id_with_no_name_stops_the_build(lists):
    _, names = lists
    del names["MONDO_0003233"]
    with pytest.raises(ValueError, match="MONDO_0003233"):
        corrections_page.rows()


def test_a_salt_parent_with_no_name_stops_the_build(lists):
    _, names = lists
    del names["CHEMBL9001"]
    with pytest.raises(ValueError, match="CHEMBL9001"):
        corrections_page.rows()


def test_an_entry_with_no_link_stops_the_build(lists):
    data, _ = lists
    del data["corrections"][1]["label"]
    with pytest.raises(ValueError, match="CHEMBL641"):
        corrections_page.rows()


def test_the_page_has_the_heading_safety_line_and_every_row(lists):
    page = corrections_page.page_html()
    assert HEADING.replace("'", "&#x27;") in page
    assert ("For learning and research exploration, not medical advice. Never start, "
            "stop or change any medicine without a doctor.") in page
    for row in corrections_page.rows():
        assert f'href="{row.source}"' in page
    assert page.count('<tr class="row">') == 10
    assert "CHEMBL" not in page and "MONDO_" not in page  # no IDs on a public page


def test_the_route_serves_the_page_with_no_network(lists):
    def no_network(*args, **kwargs):
        raise AssertionError("the corrections page reached the network")

    with patch("moonlight.fetch._post_json", side_effect=no_network), \
            patch("requests.Session.request", side_effect=no_network), \
            patch("requests.request", side_effect=no_network):
        api._corrections_page = corrections_page.page_html()  # built at start-up
        try:
            answer = TestClient(api.app).get("/corrections")
        finally:
            api._corrections_page = None
    assert answer.status_code == 200
    assert "text/html" in answer.headers["content-type"]
    assert answer.text.count('<tr class="row">') == 10


def test_the_footer_links_to_it_at_the_end_of_the_last_line():
    """MAIN 5, 27 Nov. Top to bottom: contact line; "Moonlight · Research
    exploration only · ..." ending with " · Corrections" as a link; the Build
    line; "Trial details checked ..."."""
    page = PAGE_FILE.read_text(encoding="utf-8")
    footer = page[page.index('<footer class="site-footer"'):page.index("</footer>")]
    order = [footer.index('class="contact"'),
             footer.index('<div class="footer-note">Moonlight · Research exploration only · '),
             footer.index(' · <a href="/corrections">Corrections</a></div>'),
             footer.index('id="build-line"'),
             footer.index('id="trials-checked-line"')]
    assert order == sorted(order)
    assert footer.count('href="/corrections"') == 1


WIDTH_SCRIPT = r"""
"use strict";
const fs = require("fs");
const { chromium } = require("playwright");
(async () => {
  const browser = await chromium.launch();
  try {
    const page = await browser.newPage({ viewport: { width: 390, height: 844 } });
    await page.route("**/*", route => route.abort());  // never the network
    await page.setContent(fs.readFileSync(process.argv[1], "utf-8"));
    const seen = await page.evaluate(() => ({
      scroll: document.documentElement.scrollWidth,
      rows: [...document.querySelectorAll("tr.row")].map(r => r.getBoundingClientRect().width),
    }));
    process.stdout.write(JSON.stringify(seen));
  } finally { await browser.close(); }
})().catch(e => { console.error(e); process.exit(1); });
"""


def test_the_page_fits_390px_with_no_sideways_scroll(lists, tmp_path):
    node = shutil.which("node")
    if not node or subprocess.run(
            [node, "-e", "require('playwright')"], capture_output=True).returncode:
        pytest.skip("needs node with playwright to open a real browser")
    page_file = tmp_path / "corrections.html"
    page_file.write_text(corrections_page.page_html(), encoding="utf-8")
    run = subprocess.run([node, "-e", WIDTH_SCRIPT, str(page_file)],
                         capture_output=True, text=True, timeout=120, cwd=str(ROOT))
    assert run.returncode == 0, run.stderr[-3000:]
    seen = json.loads(run.stdout)
    assert seen["scroll"] <= 390
    assert len(seen["rows"]) == 10 and all(width <= 390 for width in seen["rows"])


# ---- the real files (fail until New Bot's data PR lands: names and labels) ----

def real_lists():
    found = {}
    for name in corrections_page.LISTS:
        path = ROOT / "moonlight" / f"{name}.json"
        if path.exists():
            found[name] = json.loads(path.read_text(encoding="utf-8"))
    return found


def test_real_every_list_id_has_a_name():
    names_file = ROOT / "moonlight" / "names.json"
    assert names_file.exists(), "moonlight/names.json is not there yet (New Bot's data PR)"
    names = json.loads(names_file.read_text(encoding="utf-8"))
    missing = sorted(corrections_page.ids_needing_names(real_lists()) - set(names))
    assert not missing, f"no name in names.json for: {missing}"


def test_real_every_row_has_a_link():
    missing = [(name, entry["medicine_id"], entry.get("disease_id"))
               for name, entry, _ in corrections_page.entries_of(real_lists())
               if not corrections_page.link_of(name, entry)]
    assert not missing, f"entries with no link: {missing}"


def test_real_row_count_equals_the_lists_entries():
    lists = real_lists()
    assert len(corrections_page.rows()) == len(corrections_page.entries_of(lists))
