"""Ticket T0. The header tagline, without the word "free".

Change 7 wins. The header tagline reads, exactly:

    An open-source explorer of medicines and trials for any disease,
    built from public research data.

The tagline only. Saved files, no network.
"""

import pathlib
import re

from fastapi.testclient import TestClient

from moonlight import api

ROOT = pathlib.Path(__file__).resolve().parent.parent
PAGE_FILE = ROOT / "web" / "index.html"

TAGLINE = (
    "An open-source explorer of medicines and trials for any disease, "
    "built from public research data."
)


def tagline_of(html):
    """The words inside the header's tagline, and nothing around them."""
    found = re.findall(r'<p class="tagline">(.*?)</p>', html)
    assert len(found) == 1
    return found[0]


def test_the_header_tagline_is_change_7():
    page = PAGE_FILE.read_text(encoding="utf-8")
    assert tagline_of(page) == TAGLINE
    assert "free" not in tagline_of(page).lower()


def test_the_page_a_reader_opens_shows_that_tagline():
    page = TestClient(api.app).get("/").text
    assert tagline_of(page) == TAGLINE
    assert "free" not in tagline_of(page).lower()
