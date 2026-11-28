"""Ticket R2. The disease answer gets one new key, "recruiting".

No network. The disease answer itself is replaced by a small fixed one, so
the tests look only at what R2 adds. The real trials file is used for PAH
and PSC.
"""

import datetime
import pathlib
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from moonlight import api, trials

ROOT = pathlib.Path(__file__).resolve().parent.parent
REAL_FILE = ROOT / "moonlight" / "trials.sqlite"
TODAY = datetime.date(2026, 11, 27)
PAH = "MONDO_0015924"
PSC = "MONDO_0018646"
BASE = {"disease": {"id": "D", "name": "d"}, "approved": [], "new_clues": []}


def trial(nct, *countries):
    return {"nct_id": nct, "title": nct, "phases": ["Phase 2"], "countries": list(countries),
            "url": f"https://clinicaltrials.gov/study/{nct}#contacts-and-locations"}


class Fake:
    def __init__(self, checked, items):
        self.checked, self._items = checked, items

    def recruiting_for(self, disease_id, today=None):
        return list(self._items)


class Broken(Fake):
    def recruiting_for(self, disease_id, today=None):
        raise ValueError("damaged")


def ask(file):
    api.forget_answers()
    with patch.object(api, "_trials", file), patch.object(api, "_build_clues", return_value=dict(BASE)), \
            patch.object(api, "remembered_version", return_value=None):
        response = TestClient(api.app).get("/api/clues", params={"disease_id": "D"})
    assert response.status_code == 200
    return response.json()


def test_file_missing_gives_null_and_every_other_key_is_mains_answer():
    answer = ask(None)
    assert answer["recruiting"] is None
    assert {k: v for k, v in answer.items() if k != "recruiting"} == BASE


def test_a_file_that_cannot_be_read_gives_null_and_the_rest_is_served():
    answer = ask(Broken(TODAY.isoformat(), []))
    assert answer["recruiting"] is None
    assert {k: v for k, v in answer.items() if k != "recruiting"} == BASE


def test_shape_countries_a_to_z_and_a_trial_counts_in_each_country():
    items = [trial("NCT3", "United States", "Canada", "Peru"), trial("NCT2", "United States"),
             trial("NCT1")]  # a trial with no country is a trial, but in no country
    got = api._recruiting("D", Fake(TODAY.isoformat(), items), today=TODAY)
    assert got == {"checked": "2026-11-27", "total": 3,
                   "countries": [{"name": "Canada", "count": 1}, {"name": "Peru", "count": 1},
                                 {"name": "United States", "count": 2}],
                   "trials": items}


def test_no_trials_gives_zero_total_and_no_countries():
    got = api._recruiting("D", Fake(TODAY.isoformat(), []), today=TODAY)
    assert got["total"] == 0 and got["countries"] == [] and got["trials"] == []


def test_15_days_old_is_null_and_14_days_old_is_not():
    for days, expected_null in ((15, True), (14, False), (0, False)):
        checked = (TODAY - datetime.timedelta(days=days)).isoformat()
        got = api._recruiting("D", Fake(checked, [trial("NCT1", "Peru")]), today=TODAY)
        assert (got is None) is expected_null, days


def test_a_checked_date_nobody_can_read_is_null():
    assert api._recruiting("D", Fake("last tuesday", [trial("NCT1")]), today=TODAY) is None


def test_the_answer_uses_todays_date_each_time_not_the_date_it_was_kept():
    one = Fake("2026-11-26", [trial("NCT1", "Peru")])
    with patch.object(api, "_today", return_value=datetime.date(2026, 12, 10)):
        assert ask(one)["recruiting"]["total"] == 1
    with patch.object(api, "_today", return_value=datetime.date(2026, 12, 11)):
        assert ask(one)["recruiting"] is None


@pytest.mark.skipif(not REAL_FILE.is_file(), reason="no trials file")
@pytest.mark.parametrize("disease_id", [PAH, PSC])
def test_real_file_counts_add_up(disease_id):
    file = trials.Trials.open()
    try:
        got = api._recruiting(disease_id, file, today=TODAY)
        assert got is not None and got["checked"] == file.checked
        assert got["total"] == len(got["trials"]) > 0
        names = [c["name"] for c in got["countries"]]
        assert names == sorted(names) and len(names) == len(set(names))
        assert all(c["count"] > 0 for c in got["countries"])
        for c in got["countries"]:
            assert c["count"] == sum(c["name"] in t["countries"] for t in got["trials"])
        assert sum(c["count"] for c in got["countries"]) == sum(len(t["countries"]) for t in got["trials"])
        assert got["trials"] == file.recruiting_for(disease_id, today=TODAY)
    finally:
        file.close()
