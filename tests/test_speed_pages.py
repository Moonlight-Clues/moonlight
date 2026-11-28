"""Ticket 3.6, parts 1, 2 and 4: squeezed answers, finished pages kept in
memory, and the warm-up script. No network: Open Targets is replaced by the
saved files test_api.py already uses.
"""

import gzip
import importlib.util
import json
import pathlib
from unittest.mock import MagicMock, patch

import pytest
import requests
from fastapi import HTTPException
from fastapi.testclient import TestClient

import test_api as saved
from moonlight import api, cache, fetch

ROOT = pathlib.Path(__file__).resolve().parent.parent
PAH_ID = saved.PAH_ID


@pytest.fixture(autouse=True)
def offline(tmp_path, monkeypatch):
    """Saved files for Open Targets, data version 26.09, a throwaway cache."""
    monkeypatch.setenv("MOONLIGHT_CACHE_DIR", str(tmp_path / "saved"))
    cache.forget_memory()
    fetch.forget_version()
    with patch("moonlight.fetch._post_json", side_effect=saved.fake_post_json), \
            patch("moonlight.fetch._send", side_effect=saved.fake_send), \
            patch("requests.sessions.Session.request",
                  side_effect=AssertionError("network used")), \
            patch("moonlight.explain.time.sleep"):
        # Like a server that has already talked to Open Targets: the data
        # version is known. (Here _post_json is faked, so nothing else reads it.)
        fetch.data_version()
        yield
    cache.forget_memory()
    fetch.forget_version()


@pytest.fixture
def client():
    return TestClient(api.app)


def ask(client, disease_id=PAH_ID, **headers):
    with saved.with_targets(*saved.FIVE):
        return client.get("/api/clues", params={"disease_id": disease_id}, headers=headers)


# ---- Part 1: compress ----

def test_36_clues_come_back_gzip_encoded_and_decode_to_the_same_json(client):
    plain = ask(client, **{"Accept-Encoding": "identity"})
    squeezed = ask(client, **{"Accept-Encoding": "gzip"})
    assert plain.status_code == squeezed.status_code == 200
    assert "content-encoding" not in plain.headers
    assert squeezed.headers["content-encoding"] == "gzip"
    assert squeezed.json() == plain.json()


def test_36_the_bytes_on_the_wire_are_really_gzip_and_smaller(client):
    api.forget_answers()
    with saved.with_targets(*saved.FIVE), TestClient(api.app) as live:
        with live.stream("GET", "/api/clues", params={"disease_id": PAH_ID},
                         headers={"Accept-Encoding": "gzip"}) as response:
            wire = b"".join(response.iter_raw())
    body = gzip.decompress(wire)
    plain = ask(client, **{"Accept-Encoding": "identity"}).json()
    # ticket R2: recruiting is set aside (the live app has the trials file open, this client does not)
    assert {k: v for k, v in json.loads(body).items() if k != "recruiting"} == {
        k: v for k, v in plain.items() if k != "recruiting"}
    assert len(wire) < len(body)


def test_36_a_small_answer_is_not_compressed(client):
    # minimum_size is 1000 bytes: a tiny reply is sent as it is.
    response = client.get("/api/clues", params={"disease_id": "nonsense"},
                          headers={"Accept-Encoding": "gzip"})
    assert response.status_code == 404
    assert "content-encoding" not in response.headers


# ---- Part 2: finished answers in memory ----

def test_36_a_second_ask_for_the_same_disease_does_not_call_the_engine(client):
    with patch("moonlight.api._find", wraps=api._find) as engine:
        first = ask(client)
        second = ask(client)
    assert engine.call_count == 1
    assert first.status_code == second.status_code == 200
    assert first.json() == second.json()


def test_36_a_different_data_version_rebuilds_the_answer(client):
    with patch("moonlight.api._find", wraps=api._find) as engine:
        ask(client)
        fetch.forget_version()
        newer = {"data": {"meta": {"dataVersion": {"year": "26", "month": "12",
                                                   "iteration": None}}}}
        with patch("moonlight.fetch._send", return_value=newer):
            fetch.data_version()  # Open Targets has released 26.12
            ask(client)
            ask(client)
    assert engine.call_count == 2  # the 26.12 answer is then kept, too


def test_36_an_answer_past_the_use_by_age_is_rebuilt(client):
    clock = MagicMock(return_value=1000.0)
    with patch("moonlight.api._now", clock), \
            patch("moonlight.api._find", wraps=api._find) as engine:
        ask(client)
        clock.return_value = 1000.0 + fetch.USE_BY_SECONDS - 1
        ask(client)
        assert engine.call_count == 1
        clock.return_value = 1000.0 + fetch.USE_BY_SECONDS + 1
        ask(client)
        assert engine.call_count == 2


def test_36_the_age_limit_is_the_same_number_fetch_uses():
    assert api.ANSWER_USE_BY_SECONDS == fetch.USE_BY_SECONDS


def test_36_an_error_is_not_kept(client):
    broken = HTTPException(status_code=502, detail="Could not get the data from Open Targets.")
    with patch("moonlight.api._find", side_effect=broken) as engine:
        assert ask(client).status_code == 502
        assert ask(client).status_code == 502
    assert engine.call_count == 2  # asked again, not remembered
    with patch("moonlight.api._find", wraps=api._find) as engine:
        assert ask(client).status_code == 200  # and the next good one is built
    assert engine.call_count == 1


def test_36_a_404_is_not_kept(client):
    with patch("moonlight.api._find", wraps=api._find) as engine:
        assert ask(client, "MONDO_0000000").status_code == 404
        assert ask(client, "MONDO_0000000").status_code == 404
    assert engine.call_count == 2
    assert api._answers == {}


def test_36_a_network_failure_is_not_kept(client):
    with patch("moonlight.api._find", side_effect=requests.ConnectionError("down")):
        with pytest.raises(requests.ConnectionError):
            ask(client)
    assert api._answers == {}


def test_36_the_201st_disease_drops_the_oldest(client):
    one = {"disease": {"id": "x", "name": "x"}}
    for number in range(200):
        api._keep_answer(f"D_{number}", "26.09", one)
    assert len(api._answers) == 200
    api._keep_answer("D_200", "26.09", one)
    assert len(api._answers) == 200
    assert api._kept_answer("D_0", "26.09") is None  # the oldest went
    assert api._kept_answer("D_1", "26.09") == one
    assert api._kept_answer("D_200", "26.09") == one


def test_36_keeping_a_disease_again_makes_it_the_newest_not_a_second_copy():
    one = {"disease": {"id": "x", "name": "x"}}
    for number in range(200):
        api._keep_answer(f"D_{number}", "26.09", one)
    api._keep_answer("D_0", "26.09", one)  # rebuilt: now the newest
    api._keep_answer("D_200", "26.09", one)
    assert len(api._answers) == 200
    assert api._kept_answer("D_0", "26.09") == one
    assert api._kept_answer("D_1", "26.09") is None


def test_36_the_same_disease_under_two_versions_is_two_entries():
    api._keep_answer("D", "26.09", {"v": 1})
    api._keep_answer("D", "26.12", {"v": 2})
    assert api._kept_answer("D", "26.09") == {"v": 1}
    assert api._kept_answer("D", "26.12") == {"v": 2}


def test_36_if_no_version_is_known_the_page_is_built_and_not_kept(client):
    fetch.forget_version()
    with patch("moonlight.fetch._send", side_effect=AssertionError("no question of its own")):
        response = ask(client)
    assert response.status_code == 200
    assert api._answers == {}


def test_36_a_first_ask_after_the_version_is_forgotten_is_kept_once_it_is_known(client):
    # A real build reads the version through _post_json -> data_version.
    def real_build(disease_id):
        fetch.data_version()
        return {"disease": {"id": disease_id, "name": "x"}}
    fetch.forget_version()
    with patch("moonlight.api._build_clues", side_effect=real_build) as build:
        ask(client)
        ask(client)
    assert build.call_count == 1


def test_36_a_page_built_while_the_version_changed_is_not_kept(client):
    def build_during_a_release(disease_id):
        fetch.forget_version()
        with patch("moonlight.fetch._send", return_value={"data": {"meta": {"dataVersion": {
                "year": "26", "month": "12", "iteration": None}}}}):
            fetch.data_version()
        return {"disease": {"id": disease_id, "name": "x"}}
    with patch("moonlight.api._build_clues", side_effect=build_during_a_release):
        ask(client)
    assert api._answers == {}


def test_36_remembered_version_never_asks_open_targets_and_forgets_after_an_hour():
    with patch("moonlight.fetch._send", side_effect=AssertionError("network")):
        assert fetch.remembered_version() == "26.09"
        with patch("moonlight.fetch.time.monotonic",
                   return_value=fetch._version_read_at + fetch.VERSION_CHECK_SECONDS + 1):
            assert fetch.remembered_version() is None
        fetch.forget_version()
        assert fetch.remembered_version() is None


# ---- Part 4: the warm-up script ----

def load_warm():
    spec = importlib.util.spec_from_file_location("warm", ROOT / "scripts" / "warm.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_36_warm_asks_the_ten_audited_diseases_and_the_quick_start_once_each():
    warm = load_warm()
    ids = warm.disease_ids([])
    assert len(ids) == 10 and len(set(ids)) == 10
    assert ids[0] == "MONDO_0015924"  # the page's quick-start disease
    audited = [line.split(",")[0] for line in
               (ROOT / "docs" / "benchmarks" / "2026-11-24-per-disease.csv")
               .read_text(encoding="utf-8").splitlines()[1:] if ",audited," in line]
    assert sorted(ids) == sorted(audited)


def test_36_warm_adds_the_ones_given_on_the_command_line_without_repeats():
    warm = load_warm()
    ids = warm.disease_ids(["MONDO_0010200", "MONDO_0015924", "EFO_0000000"])
    assert ids[-2:] == ["MONDO_0010200", "EFO_0000000"]
    assert ids.count("MONDO_0015924") == 1


def test_36_warm_reads_one_at_a_time_prints_each_time_and_only_uses_get(capsys):
    warm = load_warm()
    calls = []

    def fake_get(url, params=None, timeout=None, **kwargs):
        calls.append((url, params))
        assert not kwargs, "nothing but the address, the disease and a time limit"
        response = MagicMock(status_code=200)
        response.content = b"{}"
        return response

    with patch("requests.get", side_effect=fake_get), \
            patch("requests.post", side_effect=AssertionError("read-only")):
        warm.main(["MONDO_0010200"])
    assert len(calls) == 11
    assert all(url == "https://www.moonlightclues.com/api/clues" for url, _ in calls)
    assert [params["disease_id"] for _, params in calls][-1] == "MONDO_0010200"
    out = capsys.readouterr().out
    assert out.count("MONDO_0015924") == 1
    assert out.count(" s") >= 11  # a time on every line


def test_36_warm_carries_on_after_a_failed_disease(capsys):
    warm = load_warm()

    def fake_get(url, params=None, timeout=None):
        if params["disease_id"] == "MONDO_0015924":
            raise requests.ConnectionError("down")
        return MagicMock(status_code=200, content=b"{}")

    with patch("requests.get", side_effect=fake_get):
        warm.main([])
    out = capsys.readouterr().out
    assert "failed" in out and out.count("\n") >= 10
