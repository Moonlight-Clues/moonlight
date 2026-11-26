"""The full approval-year table (moonlight/approval_years.json), 26 Nov 2026.

Reads the real file only. No network. The values below were hand-checked by
Product (handcheck_ester63.csv) and ordered by MAIN 5: the moiety rule, five
wrong values fixed, three removals, fibrinogen 1947 (US) from the Federal Register.
31 unsure years (earlier-numbered undated NDAs) were then removed: a year that
is probably too late is worse than no year.
"""

import json
import pathlib

import pytest

from moonlight import approval_years

pytestmark = pytest.mark.approval_years  # read the real list (see conftest.py)

ROOT = pathlib.Path(__file__).resolve().parent.parent
TABLE = json.loads((ROOT / "moonlight" / "approval_years.json").read_text(encoding="utf-8"))
SOURCES = (ROOT / "moonlight" / "SOURCES.md").read_text(encoding="utf-8")

APPL = "https://www.accessdata.fda.gov/scripts/cder/daf/index.cfm?event=overview.process&ApplNo="


def test_the_whole_table_is_there_and_every_entry_loads():
    assert len(TABLE) == 2022
    assert approval_years.load() == TABLE


@pytest.mark.parametrize("medicine_id, year, region, source", [
    ("CHEMBL1201549", 1987, "US", "https://www.accessdata.fda.gov/scripts/opdlisting/oopd/detailedIndex.cfm?cfgridkey=14486"),  # teriparatide acetate
    ("CHEMBL757", 1959, "US", APPL + "011891"),     # nandrolone
    ("CHEMBL2104906", 1959, "US", APPL + "011891"),  # nandrolone cyclotate
    ("CHEMBL2107840", 2015, "US", APPL + "205739"),  # patiromer calcium
    ("CHEMBL57242", 2011, "US", APPL + "200796"),    # azilsartan
    ("CHEMBL2109072", 1947, "US", "https://www.govinfo.gov/content/pkg/FR-1978-01-06/pdf/FR-1978-01-06.pdf"),  # fibrinogen
])
def test_the_ordered_fixes(medicine_id, year, region, source):
    assert TABLE[medicine_id] == {"year": year, "region": region, "source": source}


def test_arginine_norethindrone_acetate_and_edetate_disodium_have_no_year():
    for medicine_id in ("CHEMBL1485", "CHEMBL1200381", "CHEMBL1201146", "CHEMBL1749"):
        assert medicine_id not in TABLE


def test_the_fibrinogen_citation_is_in_the_sources_file():
    assert "43 Fed. Reg. 1131, 1132 (Jan. 6, 1978)" in SOURCES
    assert "licensed since 1947" in SOURCES


def test_hylenex_is_called_an_nda_in_the_sources_file():
    assert "Hylenex, NDA 021859" in SOURCES
    assert "Hylenex, BLA 021859" not in SOURCES


UNSURE_REMOVED = (
    "CHEMBL105", "CHEMBL1169", "CHEMBL1199080",
    "CHEMBL1200600", "CHEMBL1200731", "CHEMBL1200848",
    "CHEMBL1201039", "CHEMBL1201170", "CHEMBL1201328",
    "CHEMBL1201347", "CHEMBL1236821", "CHEMBL1295",
    "CHEMBL1466", "CHEMBL1615439", "CHEMBL174",
    "CHEMBL177", "CHEMBL18", "CHEMBL2110563",
    "CHEMBL3559672", "CHEMBL395429", "CHEMBL3989767",
    "CHEMBL428880", "CHEMBL434", "CHEMBL5465559",
    "CHEMBL55643", "CHEMBL564085", "CHEMBL64",
    "CHEMBL660", "CHEMBL689", "CHEMBL819",
    "CHEMBL969",
)


def test_unsure_undated_nda_years_were_removed():
    # MAIN 5: a year that is probably too late is worse than no year.
    assert len(set(UNSURE_REMOVED)) == 31
    for medicine_id in UNSURE_REMOVED:
        assert medicine_id not in TABLE
