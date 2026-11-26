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

Ticket 2.63. A fourth thing: the hand list of wider labels
(moonlight/wider_labels.json) is empty for every test unless it is marked
@pytest.mark.wider_labels. See the setup hook below.
"""

import os

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
    # Both markers are registered here, once (a second pytest_configure in this
    # file would silently replace this one).
    config.addinivalue_line(
        "markers", "approval_years: read the real approval_years.json (ticket 3.22); "
        "without it approval_years.load returns {}")
    config.addinivalue_line(
        "markers", "salt_parents: use the real moonlight/salt_parents.json "
                   "(ticket 3.23). Without it the list is empty.")
    config.addinivalue_line(
        "markers", "wider_labels: use the real moonlight/wider_labels.json "
                   "(ticket 2.63). Without it the list is empty.")


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


# Ticket 3.23. The hand list of salt parents (moonlight/salt_parents.json) is
# EMPTY for every test, so every older test still sees the pages as they were
# before the list existed ("back to before"). A test that needs the real list
# opts in with @pytest.mark.salt_parents (or pytestmark = pytest.mark.salt_parents
# for a whole file). This marker is only for this list; it is not the marker of
# any other ticket.
#
# Why hooks and not a plain autouse fixture: many older tests build their page
# in a module-scoped fixture, and a function-scoped autouse fixture runs AFTER
# those. The setup hook below runs before any fixture of the test is built, so
# it covers them too. It does the job of one autouse fixture, switched by the
# marker.
_salt_parents_patch = []


@pytest.hookimpl(tryfirst=True)
def pytest_runtest_setup(item):
    from unittest.mock import patch

    from moonlight import fetch

    _salt_parents_stop()
    # MOONLIGHT_SALT_PARENTS=on leaves the real list on for a whole run. Only
    # test_salt_parents_pins_3_23.py sets it, for a child pytest run.
    if not item.get_closest_marker("salt_parents") \
            and os.environ.get("MOONLIGHT_SALT_PARENTS") != "on":
        started = patch.object(fetch, "_salt_parents", return_value={})
        started.start()
        _salt_parents_patch.append(started)
    # Ticket 2.63 (W1). The same switch for the hand list of wider labels
    # (moonlight/wider_labels.json): EMPTY for every test, so every older
    # test sees the cards as they were before the list existed. A test that
    # needs the real list opts in with @pytest.mark.wider_labels. Its own
    # marker, separate from every other ticket's. Undone with the salt patch.
    if not item.get_closest_marker("wider_labels"):
        from moonlight import engine

        started = patch.object(engine, "_read_wider_labels", return_value=[])
        started.start()
        _salt_parents_patch.append(started)


def _salt_parents_stop():
    while _salt_parents_patch:
        _salt_parents_patch.pop().stop()


@pytest.hookimpl(trylast=True)
def pytest_runtest_teardown(item, nextitem):
    # A module-scoped fixture is torn down inside the last test's teardown;
    # the list goes back after that, so nothing else sees the patch.
    _salt_parents_stop()
