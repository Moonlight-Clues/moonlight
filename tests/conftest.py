"""Ticket 3.6. Two things every test starts with.

1. The finished /api/clues answers kept in memory (api._answers) are
   emptied before and after each test. Many old tests ask for the same
   disease with different pretend proteins; without this one test's page
   would be handed to the next.
2. The Firestore part of the cache is switched off
   (MOONLIGHT_FIRESTORE_CACHE=0), so no test can reach the real Firestore
   by accident. The tests of that part switch it on with a fake store.

No line of any old test was changed for this.
"""

import pytest

from moonlight import api, cache


@pytest.fixture(autouse=True)
def _speed_set_up(monkeypatch):
    monkeypatch.setenv("MOONLIGHT_FIRESTORE_CACHE", "0")
    cache.forget_firestore_trouble()
    api.forget_answers()
    yield
    api.forget_answers()
    cache.forget_firestore_trouble()
