"""Ticket 3.6. Two things every test starts with.

1. The finished /api/clues answers kept in memory (api._answers) are
   emptied before and after each test. Many old tests ask for the same
   disease with different pretend proteins; without this one test's page
   would be handed to the next.
2. The Firestore part of the cache is switched off
   (MOONLIGHT_FIRESTORE_CACHE=0), so no test can reach the real Firestore
   by accident. The tests of that part switch it on with a fake store.

No line of any old test was changed for this.

Ticket 3.22. A third thing: moonlight.approval_years.load returns {} for every
test, so no card carries first_approved and every old test sees the site
exactly as before (A to Z, no year line). A test that needs the years opts out
with @pytest.mark.approval_years (or pytestmark for a whole file) and then
reads the list through approval_years.load as the app does.
"""

import pytest

from moonlight import api, approval_years, cache


@pytest.fixture(autouse=True)
def _speed_set_up(monkeypatch):
    monkeypatch.setenv("MOONLIGHT_FIRESTORE_CACHE", "0")
    cache.forget_firestore_trouble()
    api.forget_answers()
    yield
    api.forget_answers()
    cache.forget_firestore_trouble()


def pytest_configure(config):
    config.addinivalue_line(
        "markers", "approval_years: read the real approval_years.json (ticket 3.22); "
        "without it approval_years.load returns {}")


_real_load = approval_years.load
_years_on = False  # True only while a test marked approval_years runs


@pytest.fixture(autouse=True, scope="session")
def _approval_years_off_by_default():
    """Session-wide, so module-scoped fixtures of old tests build their pages with no
    years too (a per-test fixture would run after them)."""
    mine = pytest.MonkeyPatch()
    mine.setattr(approval_years, "load", lambda: _real_load() if _years_on else {})
    yield
    mine.undo()


@pytest.fixture(autouse=True)
def _approval_years_on_when_marked(request):
    global _years_on
    _years_on = request.node.get_closest_marker("approval_years") is not None
    yield
    _years_on = False
