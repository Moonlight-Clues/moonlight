"""Ticket 2.69. "First approved" takes the earliest year of the table and PMDA.

A card's "First approved" year is the earliest of two: its entry in
moonlight/approval_years.json and its entry in moonlight/pmda_summaries.json
for the page's disease. When the Japan year is strictly earlier, the line reads
"First approved: [year] (Japan)" and the year links to the PMDA summary.

Decided by MAIN 5, 26 Nov:
  * A PMDA year later than the table's year: the card keeps the table's year.
    No log, no flag. A tie keeps the table's year and region too.
  * A PMDA entry with no table year: it sets the year ("(Japan)"), but only if
    it is the medicine's original approval.
  * New field in pmda_summaries.json: approval_type, "original" or "new use".
    An entry without it counts as "new use", so it never sets a year.
  * A card with no PMDA entry keeps its table entry exactly as it was.

Saved answers and made-up entries only. No network. "Japan" as a region word
is new wording: it ships only on MAIN 5's go.
"""

import json
import logging
import pathlib
import shutil
import subprocess
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from moonlight import api, approval_years, engine

import test_approval_year_3_22 as year_322
import test_narrower_box as saved_pages

pytestmark = pytest.mark.approval_years  # the real table is read where a test says so

ROOT = pathlib.Path(__file__).resolve().parent.parent
REAL_PMDA = ROOT / "moonlight" / "pmda_summaries.json"

LINK = "https://www.pmda.go.jp/files/000000069.pdf"  # made up for the tests
US_2023 = {"year": 2023, "region": "US", "source": "https://example.org/us"}


def entry(medicine_id, disease_id, year="2014", **extra):
    row = {"medicine_id": medicine_id, "disease_id": disease_id, "date": "2026-11-27",
           "summary_date": f"{year}-12-26", "link": LINK}
    row.update(extra)
    return row


def with_pmda(entries):
    return patch.object(engine, "_read_pmda_summaries", return_value=entries)


def japan(year, link=LINK):
    return {"year": year, "region": "Japan", "source": link}


# ---- 1. the new field ----

@pytest.mark.parametrize("kind", ["original", "new use"])
def test_approval_type_original_or_new_use_is_accepted(kind):
    with with_pmda([entry("A", "D", approval_type=kind)]):
        assert engine.pmda_summaries() == {("A", "D"): (LINK, "2014")}  # the old answer is unchanged


@pytest.mark.parametrize("bad", ["Original", "new_use", "", "first", None, 1, True])
def test_any_other_approval_type_is_refused(bad):
    with with_pmda([entry("A", "D", approval_type=bad)]):
        with pytest.raises(ValueError):
            engine.pmda_summaries()
        with pytest.raises(ValueError):
            engine.pmda_original_approvals()


def test_it_can_sit_beside_date_source():
    with with_pmda([entry("A", "D", approval_type="original", date_source="the list, row 6")]):
        assert engine.pmda_original_approvals() == {("A", "D"): (LINK, 2014)}


def test_only_original_entries_count_and_a_missing_field_is_new_use():
    rows = [entry("A", "D", approval_type="original"),
            entry("B", "D", approval_type="new use"),
            entry("C", "D")]  # no field: new use
    with with_pmda(rows):
        assert engine.pmda_original_approvals() == {("A", "D"): (LINK, 2014)}


@pytest.mark.pmda_summaries  # read the real file (conftest empties it otherwise)
def test_the_real_file_counts_exactly_the_entries_that_say_original():
    rows = json.loads(REAL_PMDA.read_text(encoding="utf-8"))
    said = {(r["medicine_id"], r["disease_id"]) for r in rows if r.get("approval_type") == "original"}
    assert set(engine.pmda_original_approvals()) == said
    assert set(engine.pmda_summaries()) == {(r["medicine_id"], r["disease_id"]) for r in rows}


# ---- 2. the rule ----

def test_japan_strictly_earlier_wins_and_links_the_summary():
    assert engine.earliest_first_approved(US_2023, (LINK, 2014)) == japan(2014)


def test_a_later_japan_year_keeps_the_table_entry_exactly(caplog):
    with caplog.at_level(logging.DEBUG):
        assert engine.earliest_first_approved(US_2023, (LINK, 2024)) is US_2023
    assert caplog.records == []  # no log, no flag


def test_a_tie_keeps_the_table_year_and_region(caplog):
    with caplog.at_level(logging.DEBUG):
        assert engine.earliest_first_approved(US_2023, (LINK, 2023)) is US_2023
    assert caplog.records == []


def test_an_original_japan_year_with_no_table_year_sets_the_year():
    assert engine.earliest_first_approved(None, (LINK, 2014)) == japan(2014)


def test_no_pmda_original_leaves_the_table_entry_or_nothing():
    assert engine.earliest_first_approved(US_2023, None) is US_2023
    assert engine.earliest_first_approved(None, None) is None


def test_the_region_word_is_japan():
    assert engine.JAPAN_REGION == "Japan"


# ---- 3. the API, on the saved pulmonary arterial hypertension page ----

def page_with(table, pmda_rows):
    with patch("moonlight.fetch._post_json", side_effect=saved_pages.saved_post_json), \
            patch("requests.post", side_effect=AssertionError("network used")), \
            patch.object(approval_years, "_read", return_value=table), with_pmda(pmda_rows):
        return saved_pages.clues_json(TestClient(api.app), saved_pages.PAH)


@pytest.fixture(scope="module")
def plain():
    return page_with({}, [])


def cards_of(plain):
    ids = [c["id"] for c in plain["approved"]]
    assert len(ids) >= 5
    return ids


def test_api_cases_one_card_each(plain):
    ids = cards_of(plain)
    disease = saved_pages.PAH.id
    table = {ids[0]: US_2023, ids[1]: US_2023, ids[2]: US_2023, ids[3]: US_2023}
    rows = [
        entry(ids[0], disease, "2014", approval_type="original"),  # earlier: Japan wins
        entry(ids[1], disease, "2024", approval_type="original"),  # later: table stays
        entry(ids[2], disease, "2023", approval_type="original"),  # tie: table stays
        entry(ids[3], disease, "2014", approval_type="new use"),   # new use: never sets a year
        entry(ids[4], disease, "2014", approval_type="original"),  # no table year: Japan sets it
        entry(ids[5 % len(ids)] if len(ids) > 5 else "NOT_ON_THE_PAGE", disease, "2010"),  # no field
    ]
    page = page_with(table, rows)
    got = {c["id"]: c.get("first_approved") for c in page["approved"]}
    assert got[ids[0]] == japan(2014)
    assert got[ids[1]] == US_2023
    assert got[ids[2]] == US_2023
    assert got[ids[3]] == US_2023
    assert got[ids[4]] == japan(2014)
    if len(ids) > 5:
        assert got[ids[5]] is None  # no table year and no "original": no line


def test_api_a_card_without_a_pmda_entry_keeps_its_table_entry(plain):
    ids = cards_of(plain)
    table = {ids[0]: US_2023, ids[1]: {"year": 1999, "region": "EU"}}
    rows = [entry(ids[2], saved_pages.PAH.id, "2001", approval_type="original")]
    page = page_with(table, rows)
    got = {c["id"]: c.get("first_approved") for c in page["approved"]}
    assert got[ids[0]] == US_2023 and got[ids[1]] == {"year": 1999, "region": "EU"}
    assert got[ids[2]] == japan(2001)
    assert [i for i, v in got.items() if v is None] == [i for i in ids if i not in ids[:3]]


def test_api_an_entry_for_another_disease_does_nothing(plain):
    ids = cards_of(plain)
    rows = [entry(ids[0], "MONDO_NOT_THIS_PAGE", "1990", approval_type="original")]
    assert page_with({ids[0]: US_2023}, rows)["approved"][0].get("first_approved") == US_2023


def test_api_nothing_else_changes_and_the_order_stays(plain):
    ids = cards_of(plain)
    rows = [entry(ids[0], saved_pages.PAH.id, "2014", approval_type="original")]
    page = page_with({ids[1]: US_2023}, rows)
    assert [c["id"] for c in page["approved"]] == ids
    strip = lambda cards: [{k: v for k, v in c.items() if k != "first_approved"} for c in cards]
    assert strip(page["approved"]) == strip(plain["approved"])
    assert {k: v for k, v in page.items() if k != "approved"} == \
        {k: v for k, v in plain.items() if k != "approved"}
    for part in ("narrower", "wider_group"):
        assert all("first_approved" not in c for c in page.get(part, []))


# ---- 4. the real example: vonoprazan on its disease (PMDA 2014, table 2023) ----

VONOPRAZAN = "CHEMBL2079130"


@pytest.mark.pmda_summaries
def test_vonoprazan_on_both_its_diseases_reads_2014_japan_once_the_entry_says_original():
    rows = json.loads(REAL_PMDA.read_text(encoding="utf-8"))
    mine = [r for r in rows if r["medicine_id"] == VONOPRAZAN]
    assert len(mine) == 2
    table = approval_years.load()[VONOPRAZAN]
    assert table["year"] == 2023  # the real table says 2023
    for r in mine:
        marked = [{**x, "approval_type": "original"} if x is r else x for x in rows]
        with with_pmda(marked):
            found = engine.pmda_original_approvals()[(VONOPRAZAN, r["disease_id"])]
            assert engine.earliest_first_approved(table, found) == japan(2014, r["link"])


@pytest.mark.pmda_summaries
def test_vonoprazan_keeps_2023_until_its_entry_says_original():
    rows = json.loads(REAL_PMDA.read_text(encoding="utf-8"))
    if any(r.get("approval_type") == "original" for r in rows if r["medicine_id"] == VONOPRAZAN):
        pytest.skip("New Bot has added approval_type to vonoprazan")
    with with_pmda(rows):
        assert not [k for k in engine.pmda_original_approvals() if k[0] == VONOPRAZAN]


# ---- 5. the page at 390 px ----

@pytest.fixture(scope="module")
def seen(tmp_path_factory):
    node = shutil.which("node")
    if not node or subprocess.run(
            [node, "-e", "require('playwright')"], capture_output=True).returncode:
        pytest.skip("needs node with playwright to open a real browser")
    with patch("moonlight.fetch._post_json", side_effect=saved_pages.saved_post_json), \
            patch.object(approval_years, "_read", return_value={}), with_pmda([]):
        base = saved_pages.clues_json(TestClient(api.app), saved_pages.PAH)
    entries = {0: japan(2014), 1: US_2023, 2: {"year": 1999, "region": "EU"}}
    cases = {"japan": {"answer": year_322.with_entries(base, entries)}}
    path = tmp_path_factory.mktemp("japan_2_69") / "cases.json"
    path.write_text(json.dumps(cases), encoding="utf-8")
    run = subprocess.run([node, "-e", year_322.BROWSER_SCRIPT, str(year_322.PAGE_FILE), str(path)],
                         capture_output=True, text=True, timeout=240, cwd=str(ROOT))
    assert run.returncode == 0, run.stderr[-3000:]
    out = json.loads(run.stdout)
    assert out["japan"]["errors"] == []
    return out["japan"]["opened"]


def test_browser_the_japan_line_reads_year_japan_and_the_year_links_the_summary(seen):
    line = year_322.draft_words()["card"]
    assert line.replace("{year}", "2014").replace("{region}", "Japan") == "First approved: 2014 (Japan)"
    assert "First approved: 2014 (Japan)" in seen["years"]
    assert LINK in seen["hrefs"]


def test_browser_the_other_cards_read_as_before_and_nothing_runs_sideways_at_390(seen):
    assert "First approved: 2023 (US)" in seen["years"]
    assert "First approved: 1999 (EU)" in seen["years"]
    assert not seen["sideways"]
