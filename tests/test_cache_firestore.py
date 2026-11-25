"""Ticket 3.6, part 3: saved answers that survive deploys (Firestore).

No test here reaches the real Firestore. The client from reports.py is
replaced by FakeClient, which keeps documents in a dict.
"""

import base64
import gzip
import hashlib
import json
import logging
from unittest.mock import patch

import pytest

from moonlight import cache, reports

KIND, VERSION = "open-targets", "26.09"
KEY = {"query": "q", "variables": {"id": "ENSG1"}}
VALUE = {"data": {"target": {"id": "ENSG1", "rows": [1, 2, 3]}}}


class FakeDocument:
    def __init__(self, store, name):
        self.store, self.name = store, name

    def get(self):
        if self.store.broken:
            raise RuntimeError("Firestore is down")
        self.store.reads.append(self.name)
        data = self.store.docs.get(self.name)
        return FakeSnapshot(data)

    def set(self, data):
        if self.store.broken:
            raise RuntimeError("Firestore is down")
        self.store.docs[self.name] = dict(data)


class FakeSnapshot:
    def __init__(self, data):
        self.data = data
        self.exists = data is not None

    def to_dict(self):
        return dict(self.data)


class FakeClient:
    """Stands in for the Firestore client, for the "cache" collection."""

    def __init__(self):
        self.docs, self.reads, self.broken, self.collections = {}, [], False, []

    def collection(self, name):
        self.collections.append(name)
        store = self

        class Collection:
            def document(self, doc_id):
                return FakeDocument(store, doc_id)
        return Collection()


def doc_id(kind=KIND, version=VERSION, key=KEY):
    return hashlib.sha256(
        f"{kind}|{version}|{json.dumps(key, sort_keys=True)}".encode("utf-8")).hexdigest()


def unpack(text):
    return json.loads(gzip.decompress(base64.b64decode(text)))


@pytest.fixture
def store(tmp_path, monkeypatch):
    """Firestore switched on, with a fake store; a throwaway disk folder."""
    fake = FakeClient()
    monkeypatch.setenv("MOONLIGHT_FIRESTORE_CACHE", "1")
    monkeypatch.setenv("MOONLIGHT_CACHE_DIR", str(tmp_path / "disk"))
    monkeypatch.delenv("FIRESTORE_DB", raising=False)
    cache.forget_memory()
    cache.forget_firestore_trouble()
    with patch.object(reports, "_get_client", return_value=fake):
        yield fake
    cache.forget_memory()


def restart():
    """A new deploy: empty memory (the disk folder is also new in Cloud Run)."""
    cache.forget_memory()


def wipe_disk(tmp_path):
    import shutil
    shutil.rmtree(tmp_path / "disk", ignore_errors=True)


# ---- what is stored ----

def test_36_save_puts_the_entry_in_the_cache_collection_with_the_right_fields(store):
    with patch("moonlight.cache._now", return_value=1234.5):
        cache.save(KIND, VERSION, KEY, VALUE)
    assert store.collections == ["cache"]
    assert list(store.docs) == [doc_id()]
    doc = store.docs[doc_id()]
    assert set(doc) == {"kind", "version", "saved_at", "value"}
    assert (doc["kind"], doc["version"], doc["saved_at"]) == (KIND, VERSION, 1234.5)
    assert isinstance(doc["value"], str)
    assert unpack(doc["value"]) == VALUE  # JSON, gzip, base64


def test_36_only_open_targets_answers_go_to_firestore(store):
    for kind in ("explanation", "finished-page", "visitor", "anything"):
        cache.save(kind, VERSION, KEY, VALUE)
        assert cache.load(kind, VERSION, KEY) == VALUE  # memory and disk still work
    assert store.docs == {} and store.reads == []


def test_36_the_database_is_the_one_reports_py_uses(store, monkeypatch):
    # No second client style: cache.py asks reports.py for the client.
    import inspect
    source = inspect.getsource(cache)
    assert "firestore.Client" not in source
    assert "reports._get_client" in source


# ---- loading ----

def test_36_a_hit_in_firestore_fills_memory_and_disk(store, tmp_path):
    cache.save(KIND, VERSION, KEY, VALUE)
    restart()
    wipe_disk(tmp_path)
    assert cache.load(KIND, VERSION, KEY) == VALUE
    assert len(store.reads) == 1
    # Memory: asking again does not read Firestore again.
    assert cache.load(KIND, VERSION, KEY) == VALUE
    assert len(store.reads) == 1
    # Disk: with memory emptied and Firestore broken, the file still answers.
    restart()
    store.broken = True
    assert cache.load(KIND, VERSION, KEY) == VALUE


def test_36_memory_and_disk_are_asked_before_firestore(store):
    cache.save(KIND, VERSION, KEY, VALUE)
    store.reads.clear()
    assert cache.load(KIND, VERSION, KEY) == VALUE  # memory
    restart()
    assert cache.load(KIND, VERSION, KEY) == VALUE  # disk
    assert store.reads == []


def test_36_a_miss_everywhere_is_none(store):
    assert cache.load(KIND, VERSION, KEY) is None
    assert store.reads == [doc_id()]


def test_36_a_new_data_version_misses(store, tmp_path):
    cache.save(KIND, VERSION, KEY, VALUE)
    restart()
    wipe_disk(tmp_path)
    assert cache.load(KIND, "26.12", KEY) is None
    assert cache.load(KIND, VERSION, {"other": "key"}) is None


def test_36_an_entry_whose_fields_do_not_match_is_not_used(store, tmp_path):
    cache.save(KIND, VERSION, KEY, VALUE)
    store.docs[doc_id()]["version"] = "25.03"
    restart()
    wipe_disk(tmp_path)
    assert cache.load(KIND, VERSION, KEY) is None


def test_36_a_damaged_value_is_a_miss_and_never_an_error(store, tmp_path):
    cache.save(KIND, VERSION, KEY, VALUE)
    store.docs[doc_id()]["value"] = "!!! not base64 gzip !!!"
    restart()
    wipe_disk(tmp_path)
    assert cache.load(KIND, VERSION, KEY) is None


# ---- age limit ----

def test_36_the_age_limit_is_respected_for_firestore_entries(store, tmp_path):
    with patch("moonlight.cache._now", return_value=1000.0):
        cache.save(KIND, VERSION, KEY, VALUE)
    restart()
    wipe_disk(tmp_path)
    with patch("moonlight.cache._now", return_value=1000.0 + 100):
        assert cache.load(KIND, VERSION, KEY, max_age_seconds=200) == VALUE
    restart()
    wipe_disk(tmp_path)
    with patch("moonlight.cache._now", return_value=1000.0 + 300):
        assert cache.load(KIND, VERSION, KEY, max_age_seconds=200) is None


def test_36_a_firestore_entry_with_no_date_fails_an_age_limit(store, tmp_path):
    cache.save(KIND, VERSION, KEY, VALUE)
    del store.docs[doc_id()]["saved_at"]
    restart()
    wipe_disk(tmp_path)
    assert cache.load(KIND, VERSION, KEY, max_age_seconds=200) is None


def test_36_an_old_file_on_disk_does_not_hide_a_newer_firestore_entry(store, tmp_path):
    with patch("moonlight.cache._now", return_value=1000.0):
        cache.save(KIND, VERSION, KEY, {"old": True})
    store.docs[doc_id()].update(
        saved_at=9000.0, value=base64.b64encode(gzip.compress(b'{"new": true}')).decode())
    restart()
    with patch("moonlight.cache._now", return_value=9100.0):
        assert cache.load(KIND, VERSION, KEY, max_age_seconds=500) == {"new": True}


# ---- size ----

def test_36_a_value_over_900_kb_skips_firestore_only(store):
    # Random-looking text does not shrink much when gzipped.
    big = {"data": base64.b64encode(hashlib.sha256(b"x").digest() * 40000).decode()
           + "".join(hashlib.sha256(str(n).encode()).hexdigest() for n in range(40000))}
    cache.save(KIND, VERSION, KEY, big)
    assert store.docs == {}
    assert cache.load(KIND, VERSION, KEY) == big  # memory and disk have it


def test_36_a_value_just_under_the_limit_is_stored(store):
    cache.save(KIND, VERSION, KEY, VALUE)
    assert len(store.docs[doc_id()]["value"]) < cache.FIRESTORE_VALUE_LIMIT == 900 * 1024


# ---- trouble ----

def test_36_a_store_failure_falls_back_silently_and_logs_one_line(store, caplog):
    store.broken = True
    with caplog.at_level(logging.WARNING, logger="moonlight.cache"):
        cache.save(KIND, VERSION, KEY, VALUE)          # does not raise
        assert cache.load(KIND, VERSION, KEY) == VALUE  # memory
        restart()
        assert cache.load(KIND, VERSION, KEY) == VALUE  # disk
        restart()
        cache.save(KIND, VERSION, {"k": 2}, VALUE)
        assert cache.load(KIND, VERSION, {"k": 3}) is None  # a plain miss
    lines = [r for r in caplog.records if r.name == "moonlight.cache"]
    assert len(lines) == 1
    text = lines[0].getMessage()
    assert "RuntimeError" in text and "Firestore is down" not in text
    assert "ENSG1" not in text


def test_36_no_credentials_is_the_same_quiet_fallback(tmp_path, monkeypatch, caplog):
    monkeypatch.setenv("MOONLIGHT_FIRESTORE_CACHE", "1")
    monkeypatch.setenv("MOONLIGHT_CACHE_DIR", str(tmp_path / "disk"))
    cache.forget_memory()
    cache.forget_firestore_trouble()
    with patch.object(reports, "_get_client", side_effect=reports.StoreUnavailable("DefaultCredentialsError")), \
            caplog.at_level(logging.WARNING, logger="moonlight.cache"):
        cache.save(KIND, VERSION, KEY, VALUE)
        restart()
        assert cache.load(KIND, VERSION, KEY) == VALUE
        assert cache.load(KIND, VERSION, {"nothing": 1}) is None
    assert len([r for r in caplog.records if r.name == "moonlight.cache"]) == 1


def test_36_after_a_failure_firestore_is_left_alone_for_a_while(store):
    store.broken = True
    clock = {"now": 100.0}
    with patch("moonlight.cache._now", side_effect=lambda: clock["now"]):
        cache.load(KIND, VERSION, KEY)           # fails, starts the rest
        store.broken = False
        cache.load(KIND, VERSION, {"k": 1})
        assert store.reads == []                  # not asked during the rest
        clock["now"] += cache.FIRESTORE_REST_SECONDS + 1
        cache.load(KIND, VERSION, {"k": 2})
        assert len(store.reads) == 1              # asked again after it


# ---- switch ----

@pytest.mark.parametrize("value", ["0", " 0 "])
def test_36_the_environment_switch_turns_firestore_off(store, monkeypatch, value):
    monkeypatch.setenv("MOONLIGHT_FIRESTORE_CACHE", value)
    cache.save(KIND, VERSION, KEY, VALUE)
    restart()
    cache.load(KIND, VERSION, KEY)
    assert store.docs == {} and store.reads == [] and store.collections == []


def test_36_firestore_is_on_when_the_switch_is_not_set(store, monkeypatch):
    monkeypatch.delenv("MOONLIGHT_FIRESTORE_CACHE", raising=False)
    cache.save(KIND, VERSION, KEY, VALUE)
    assert list(store.docs) == [doc_id()]


def test_36_the_tests_start_with_firestore_off(tmp_path, monkeypatch):
    # tests/conftest.py sets the switch. With it, the real client is never made.
    import os
    monkeypatch.setenv("MOONLIGHT_FIRESTORE_CACHE", "0")
    monkeypatch.setenv("MOONLIGHT_CACHE_DIR", str(tmp_path))
    with patch.object(reports, "_get_client", side_effect=AssertionError("real Firestore")):
        cache.save(KIND, VERSION, KEY, VALUE)
        cache.forget_memory()
        assert cache.load(KIND, VERSION, KEY) == VALUE
    assert os.environ["MOONLIGHT_FIRESTORE_CACHE"] == "0"
