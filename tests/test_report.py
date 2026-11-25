"""Ticket 3.3. The "Report" link: POST /api/report, saved to Firestore.

Like a suggestion box by the pool door: a doctor drops in a slip that
says which card is wrong and why, and nothing about who they are.

No test here reaches the network. Firestore is replaced by FakeClient
(moonlight.reports._get_client is patched), and the Open Targets release
by a fixed "26.09" (moonlight.api.data_version is patched). The clock of
the report counter is api._now, moved by hand, as in test_hall_problem.py.
"""

import datetime
import sys
import types
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from moonlight import api, reports

DISEASE = "MONDO_0005148"
GOOD = {
    "disease_id": DISEASE,
    "medicine_id": "CHEMBL1431",
    "medicine_name": "Metformin",
    "tab": "approved",
    "box": None,
    "reason": "not_approved",
    "note": "The label is for adults only.",
    "website": "",
}
STORED_KEYS = {"disease_id", "medicine_id", "medicine_name", "tab", "box", "reason", "note",
               "created_at", "release", "revision", "status"}


class FakeCollection:
    def __init__(self, client, name):
        self.client, self.name = client, name

    def add(self, doc):
        if self.client.broken:
            raise RuntimeError("Firestore is down")
        self.client.saved.append((self.name, dict(doc)))
        return None, None


class FakeClient:
    """Stands in for a Firestore client. Keeps what it is handed in a list."""

    def __init__(self, broken=False):
        self.saved, self.broken = [], broken

    def collection(self, name):
        return FakeCollection(self, name)


class Clock:
    def __init__(self):
        self.now = 1000.0

    def __call__(self):
        return self.now


@pytest.fixture(autouse=True)
def fresh(monkeypatch):
    api.forget_visitors()
    monkeypatch.delenv("K_REVISION", raising=False)
    yield
    api.forget_visitors()


@pytest.fixture
def clock():
    held = Clock()
    with patch("moonlight.api._now", side_effect=held):
        yield held


@pytest.fixture
def store():
    fake = FakeClient()
    with patch("moonlight.reports._get_client", return_value=fake), \
            patch("moonlight.api.data_version", return_value="26.09"):
        yield fake


@pytest.fixture
def client():
    return TestClient(api.app)


def send(client, body=None, address="203.0.113.7", **changes):
    body = dict(GOOD if body is None else body, **changes)
    return client.post("/api/report", json=body, headers={"x-forwarded-for": address})


# ---- what is kept ----

def test_33_the_four_reasons_are_fixed():
    assert reports.REASONS == ("wrong_disease", "not_approved", "wrong_link", "other")


def test_33_a_good_report_is_saved_with_exactly_the_listed_fields(client, store, clock, monkeypatch):
    monkeypatch.setenv("K_REVISION", "moonlight-00042-abc")
    answer = send(client)
    assert answer.status_code == 200
    assert len(store.saved) == 1
    collection, doc = store.saved[0]
    assert collection == "reports"
    assert set(doc) == STORED_KEYS  # nothing more: no address, no browser, no cookie
    assert doc["disease_id"] == DISEASE
    assert doc["medicine_id"] == "CHEMBL1431"
    assert doc["medicine_name"] == "Metformin"
    assert doc["tab"] == "approved"
    assert doc["box"] is None
    assert doc["reason"] == "not_approved"
    assert doc["note"] == "The label is for adults only."
    assert doc["release"] == "26.09"
    assert doc["revision"] == "moonlight-00042-abc"
    assert doc["status"] == "new"
    assert isinstance(doc["created_at"], datetime.datetime)
    assert doc["created_at"].utcoffset() == datetime.timedelta(0)
    print("\nSTORED DOCUMENT:", doc)  # pasted in the pull request


def test_33_nothing_about_the_visitor_is_stored(client, store, clock):
    client.cookies.set("who", "me")
    client.post("/api/report", json=GOOD,
                headers={"x-forwarded-for": "198.51.100.23", "user-agent": "DoctorPhone/1.0"})
    stored = repr(store.saved)
    for thing in ("198.51.100.23", "DoctorPhone", "who", "website"):
        assert thing not in stored


def test_33_a_box_is_kept(client, store, clock):
    send(client, tab="approved", box="wrong")
    assert store.saved[0][1]["box"] == "wrong"


def test_33_no_revision_when_not_on_cloud_run(client, store, clock):
    send(client)
    assert store.saved[0][1]["revision"] is None


def test_33_a_report_is_still_kept_when_the_release_cannot_be_read(client, clock):
    fake = FakeClient()
    with patch("moonlight.reports._get_client", return_value=fake), \
            patch("moonlight.api.data_version", side_effect=api.FetchError("down")):
        assert send(client).status_code == 200
    assert fake.saved[0][1]["release"] is None


# ---- the note ----

def test_33_a_long_note_is_cut_to_200(client, store, clock):
    send(client, note="a" * 500)
    assert store.saved[0][1]["note"] == "a" * 200


def test_33_the_note_is_stripped_and_control_characters_dropped(client, store, clock):
    send(client, note="  wrong\x00 link\x07\n here \t ")
    assert store.saved[0][1]["note"] == "wrong link here"


def test_33_no_note_is_kept_as_none(client, store, clock):
    body = dict(GOOD)
    del body["note"]
    send(client, body)
    assert store.saved[0][1]["note"] is None
    send(client, note="   ")
    assert store.saved[1][1]["note"] is None


# ---- refused ----

@pytest.mark.parametrize("reason", ["", "bad", "WRONG_LINK", None, 3])
def test_33_a_bad_reason_is_400(client, store, clock, reason):
    assert send(client, reason=reason).status_code == 400
    assert store.saved == []


@pytest.mark.parametrize("field", ["disease_id", "medicine_id"])
@pytest.mark.parametrize("value", [None, "", "x" * 65, 12])
def test_33_a_missing_or_long_id_is_400(client, store, clock, field, value):
    assert send(client, **{field: value}).status_code == 400
    assert store.saved == []


@pytest.mark.parametrize("field", ["disease_id", "medicine_id"])
def test_33_an_id_left_out_is_400(client, store, clock, field):
    body = dict(GOOD)
    del body[field]
    assert send(client, body).status_code == 400


def test_33_an_id_of_64_is_kept(client, store, clock):
    assert send(client, medicine_id="x" * 64).status_code == 200


def test_33_a_body_that_is_not_json_is_400(client, store, clock):
    answer = client.post("/api/report", content=b"not json", headers={"content-type": "application/json"})
    assert answer.status_code == 400


def test_33_an_unknown_tab_or_box_is_400(client, store, clock):
    assert send(client, tab="anything I like").status_code == 400
    assert send(client, box="my name is").status_code == 400
    assert store.saved == []


# ---- the honeypot ----

def test_33_a_filled_honeypot_is_200_and_nothing_is_saved(client, store, clock):
    answer = send(client, website="http://spam.example")
    assert answer.status_code == 200
    assert store.saved == []


# ---- the counter: 5 in 10 minutes ----

def test_33_the_sixth_report_in_ten_minutes_is_429(client, store, clock):
    for _ in range(5):
        assert send(client).status_code == 200
        clock.now += 60
    assert send(client).status_code == 429
    assert len(store.saved) == 5


def test_33_after_ten_minutes_a_report_can_be_sent_again(client, store, clock):
    for _ in range(5):
        send(client)
    clock.now += api.REPORT_WINDOW_SECONDS + 1
    assert send(client).status_code == 200


def test_33_each_address_has_its_own_five(client, store, clock):
    for _ in range(5):
        send(client, address="203.0.113.7")
    assert send(client, address="203.0.113.8").status_code == 200


def test_33_the_report_counter_is_apart_from_the_cost_guard():
    assert api.MAX_REPORTS == 5
    assert api.REPORT_WINDOW_SECONDS == 600
    assert api.MAX_A_MINUTE == {"search": 60, "explain": 30}


def test_33_forget_visitors_also_forgets_the_report_counter(client, store, clock):
    for _ in range(5):
        send(client)
    api.forget_visitors()
    assert send(client).status_code == 200


# ---- Firestore not there ----

def test_33_a_store_failure_is_503_and_does_not_use_up_a_place(client, clock, caplog):
    broken = FakeClient(broken=True)
    with patch("moonlight.reports._get_client", return_value=broken), \
            patch("moonlight.api.data_version", return_value="26.09"):
        for _ in range(6):
            assert send(client, address="198.51.100.23").status_code == 503
    records = [r for r in caplog.records if r.name == "moonlight.reports"]
    assert records and all("198.51.100.23" not in r.getMessage() for r in records)
    assert all("\n" not in r.getMessage() for r in records)  # one line each
    fine = FakeClient()
    with patch("moonlight.reports._get_client", return_value=fine), \
            patch("moonlight.api.data_version", return_value="26.09"):
        assert send(client, address="198.51.100.23").status_code == 200


def test_33_no_credentials_is_503(client, clock):
    def no_client():
        raise reports.StoreUnavailable("no credentials")
    with patch("moonlight.reports._get_client", side_effect=no_client), \
            patch("moonlight.api.data_version", return_value="26.09"):
        assert send(client).status_code == 503


# ---- the Firestore client ----

def test_33_the_client_is_made_once_with_the_database_from_the_environment(monkeypatch):
    made = []

    class Client:
        def __init__(self, **kwargs):
            made.append(kwargs)

    firestore = types.ModuleType("google.cloud.firestore")
    firestore.Client = Client
    monkeypatch.setitem(sys.modules, "google.cloud.firestore", firestore)
    monkeypatch.setattr(reports, "_client", None)
    monkeypatch.setenv("FIRESTORE_DB", "reports-db")
    first, second = reports._get_client(), reports._get_client()
    assert first is second
    assert made == [{"database": "reports-db"}]


def test_33_the_database_name_defaults_to_default(monkeypatch):
    made = []

    class Client:
        def __init__(self, **kwargs):
            made.append(kwargs)

    firestore = types.ModuleType("google.cloud.firestore")
    firestore.Client = Client
    monkeypatch.setitem(sys.modules, "google.cloud.firestore", firestore)
    monkeypatch.setattr(reports, "_client", None)
    monkeypatch.delenv("FIRESTORE_DB", raising=False)
    reports._get_client()
    assert made == [{"database": "default"}]


def test_33_the_api_still_never_logs():
    source = (api.PAGE.parent.parent / "moonlight" / "api.py").read_text(encoding="utf-8")
    assert "logging" not in source


def test_33_firestore_is_in_requirements():
    text = (api.PAGE.parent.parent / "requirements.txt").read_text(encoding="utf-8")
    assert "google-cloud-firestore" in text
