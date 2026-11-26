"""Ticket 3.23. A tiny pytest plugin, used only by test_salt_parents_pins_3_23.py.

It is loaded with "-p salt_pin_recorder" in a child pytest run. It writes, to
the file named in SALT_PIN_RECORD, (1) the outcome of every test and (2) every
page the engine built while the tests ran: each engine.Tabs (and each engine.RankedClues, the runner's answer), as the ids of the
medicines on each of its seven card lists, in the order shown. A page built
inside a module-scoped fixture is filed under that fixture, not under the test
that happened to run first.

It never changes anything the tests see. No network.
"""

import json
import os

import pytest

LISTS = ("approved", "narrower", "wider_group", "being_studied", "new_clues",
         "more_in_trials", "new_in_trials")

_pages = {}
_outcomes = {}
_key = [None]


def _card_id(card):
    if hasattr(card, "id"):  # ApprovedMedicine, TrialMedicine
        return card.id
    first = card.medicine.forms[0]  # Clue: the id its medicine and forms share
    return first.parent_id or first.id


def pytest_configure(config):
    from moonlight import engine

    def recording(cls):
        original = cls.__init__

        def recording_init(self, *args, **kwargs):
            original(self, *args, **kwargs)
            # A RankedClues (the runner's answer) has only two of the seven lists.
            page = {name: [_card_id(card) for card in getattr(self, name, [])] for name in LISTS}
            _pages.setdefault(_key[0] or "outside any test", []).append(page)

        cls.__init__ = recording_init

    recording(engine.Tabs)
    recording(engine.RankedClues)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_protocol(item, nextitem):
    before = _key[0]
    _key[0] = item.nodeid
    yield
    _key[0] = before


@pytest.hookimpl(hookwrapper=True)
def pytest_fixture_setup(fixturedef, request):
    if fixturedef.scope in ("module", "class", "session", "package"):
        before = _key[0]
        _key[0] = "fixture:%s@%s" % (fixturedef.argname, request.node.nodeid.split("::")[0])
        yield
        _key[0] = before
    else:
        yield


def pytest_runtest_logreport(report):
    if report.when == "call" or (report.when == "setup" and report.outcome != "passed"):
        _outcomes[report.nodeid] = report.outcome


def pytest_sessionfinish(session):
    with open(os.environ["SALT_PIN_RECORD"], "w", encoding="utf-8") as out:
        json.dump({"outcomes": _outcomes, "pages": _pages}, out)
