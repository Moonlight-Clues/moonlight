"""Ticket 6.1. The hall problem: the cost guard counts only what costs.

At an event everyone shares one Wi-Fi, so Moonlight sees one visitor.
Kashish's decisions:
1. One visitor may make 60 searches a minute (was 10).
2. The explanations notepad counts only a request that needs a NEW Gemini
   call. A request answered from a saved explanation is never counted and
   never refused, even when the visitor is over the limit. New ones stay
   at 30 a minute.
3. Everything else stays: TOO_MANY, the 429, the 100-letter limit, how an
   address is read, and that an address is never printed or written down.

Saved files only, no network, no sleeping. Open Targets is the saved
golden files (test_api's fakes), Gemini is a fake _gemini_request, and the
clock is api._now, moved by hand. The addresses are from the ranges kept
for examples (RFC 5737), so they belong to nobody.
"""

from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

import test_api
from moonlight import api, cache, explain, fetch

TOO_MANY = "Too many requests. Please wait a minute."
VISITOR_A = {"X-Forwarded-For": "203.0.113.7"}
VISITOR_B = {"X-Forwarded-For": "198.51.100.23"}
PAH_ID = test_api.PAH_ID
FIVE = test_api.FIVE


@pytest.fixture(autouse=True)
def offline_and_fresh(tmp_path, monkeypatch):
    """Saved files instead of Open Targets, a pretend data version (26.09),
    a throwaway folder for saved results, nothing remembered, nobody has
    visited yet. Any real HTTP call is an error."""
    monkeypatch.setenv("MOONLIGHT_CACHE_DIR", str(tmp_path / "saved"))
    explain.forget_everything()
    cache.forget_memory()
    fetch.forget_version()
    api.forget_visitors()
    with patch("moonlight.fetch._post_json", side_effect=test_api.fake_post_json), \
            patch("moonlight.fetch._send", side_effect=test_api.fake_send), \
            patch("requests.request", side_effect=AssertionError("network used")), \
            patch("requests.post", side_effect=AssertionError("network used")), \
            patch("requests.get", side_effect=AssertionError("network used")), \
            patch("requests.sessions.Session.request",
                  side_effect=AssertionError("network used")), \
            patch("moonlight.explain.time.sleep"):
        yield
    explain.forget_everything()
    cache.forget_memory()
    fetch.forget_version()
    api.forget_visitors()


class Clock:
    """Stands in for api._now. It only moves when a test moves it."""

    def __init__(self):
        self.now = 5000.0

    def __call__(self):
        return self.now


@pytest.fixture
def clock():
    held = Clock()
    with patch("moonlight.api._now", side_effect=held):
        yield held


@pytest.fixture
def client():
    return TestClient(api.app)


@pytest.fixture
def ids(client):
    """The clue ids of the New clues tab for the five proteins, by name."""
    data = test_api.clues_json(client, *FIVE)
    return {clue["medicine"]: clue["id"] for clue in data["new_clues"]}


def ask(client, visitor, clue_id, gemini):
    """One /api/explain request, with gemini standing in for Gemini."""
    with test_api.with_targets(*FIVE), \
            patch("moonlight.explain._gemini_request", side_effect=gemini):
        return client.get(
            "/api/explain", params={"disease_id": PAH_ID, "clue_id": clue_id}, headers=visitor
        )


def ask_new(client, visitor, clue_id):
    """A request that needs a NEW Gemini call. Gemini cannot be reached, so
    the template answers, and template answers are never saved: every one
    of these asks Gemini again."""
    return ask(client, visitor, clue_id, test_api.gemini_unreachable)


def save_sevoflurane(client, visitor, ids):
    """Sevoflurane, explained by Gemini once and saved. Counts as one new."""
    gemini = test_api.CountingGemini()
    answer = ask(client, visitor, ids["Sevoflurane"], gemini)
    assert answer.status_code == 200
    assert answer.json()["source"] == "gemini"
    assert gemini.generate_calls == 1
    return answer.json()


def no_gemini(method, path, body=None, timeout=None):
    raise AssertionError("Gemini was asked")


# ---- Example a: 60 searches a minute ----

def test_61_example_a_60_searches_are_answered_the_61st_is_429(client, clock):
    assert api.MAX_A_MINUTE["search"] == 60
    for _ in range(60):
        clock.now += 0.5  # sixty searches inside 30 seconds
        assert test_api.one_search(client, VISITOR_A).status_code == 200
    refused = test_api.one_search(client, VISITOR_A)
    assert refused.status_code == 429
    assert refused.json() == {"detail": TOO_MANY}
    clock.now += 60  # the minute has passed
    assert test_api.one_search(client, VISITOR_A).status_code == 200


# ---- Example b: 30 new explanations a minute ----

def test_61_example_b_30_new_explanations_are_answered_the_31st_new_is_429(
        client, clock, ids):
    assert api.MAX_A_MINUTE["explain"] == 30
    for _ in range(30):
        clock.now += 1
        assert ask_new(client, VISITOR_A, ids["Desflurane"]).status_code == 200
    refused = ask_new(client, VISITOR_A, ids["Desflurane"])
    assert refused.status_code == 429
    assert refused.json() == {"detail": TOO_MANY}
    clock.now += 60
    assert ask_new(client, VISITOR_A, ids["Desflurane"]).status_code == 200


# ---- Example c: over the limit, a saved explanation is still answered ----

def test_61_example_c_after_30_new_a_saved_explanation_is_answered_with_no_gemini_call(
        client, clock, ids):
    first = save_sevoflurane(client, VISITOR_A, ids)  # new number 1
    for _ in range(29):  # new numbers 2 to 30
        assert ask_new(client, VISITOR_A, ids["Desflurane"]).status_code == 200
    assert ask_new(client, VISITOR_A, ids["Desflurane"]).status_code == 429  # over the limit

    again = ask(client, VISITOR_A, ids["Sevoflurane"], no_gemini)
    assert again.status_code == 200
    assert again.json() == first  # the very same words, source and model


def test_61_over_the_limit_many_saved_requests_are_all_answered(client, clock, ids):
    first = save_sevoflurane(client, VISITOR_A, ids)
    for _ in range(29):
        ask_new(client, VISITOR_A, ids["Desflurane"])
    for _ in range(50):
        again = ask(client, VISITOR_A, ids["Sevoflurane"], no_gemini)
        assert again.status_code == 200
        assert again.json() == first
    # Still over the limit for new ones.
    assert ask_new(client, VISITOR_A, ids["Desflurane"]).status_code == 429


def test_61_over_the_limit_a_saved_explanation_asks_open_targets_nothing(
        client, clock, ids):
    first = save_sevoflurane(client, VISITOR_A, ids)
    for _ in range(29):
        ask_new(client, VISITOR_A, ids["Desflurane"])
    with patch("moonlight.fetch._post_json") as open_targets, \
            patch("moonlight.fetch._send") as open_targets_send, \
            patch("moonlight.explain._gemini_request") as gemini:
        again = client.get("/api/explain", headers=VISITOR_A,
                           params={"disease_id": PAH_ID, "clue_id": ids["Sevoflurane"]})
    assert again.status_code == 200
    assert again.json() == first
    for door in (open_targets, open_targets_send, gemini):
        door.assert_not_called()


# ---- Example d: 200 saved requests are never counted ----

def test_61_example_d_200_saved_requests_are_answered_and_a_new_one_still_can_be(
        client, clock, ids):
    first = save_sevoflurane(client, VISITOR_A, ids)  # new number 1
    for _ in range(200):
        clock.now += 0.1  # all 200 inside 20 seconds
        again = ask(client, VISITOR_A, ids["Sevoflurane"], no_gemini)
        assert again.status_code == 200
        assert again.json() == first
    # None of the 200 was counted: 29 more new ones fit, the 31st does not.
    for _ in range(29):
        assert ask_new(client, VISITOR_A, ids["Desflurane"]).status_code == 200
    assert ask_new(client, VISITOR_A, ids["Desflurane"]).status_code == 429


# ---- Example e: two addresses, two notepads ----

def test_61_example_e_two_addresses_each_get_their_own_30(client, clock, ids):
    for _ in range(30):
        assert ask_new(client, VISITOR_A, ids["Desflurane"]).status_code == 200
    assert ask_new(client, VISITOR_A, ids["Desflurane"]).status_code == 429
    for _ in range(30):
        assert ask_new(client, VISITOR_B, ids["Desflurane"]).status_code == 200
    assert ask_new(client, VISITOR_B, ids["Desflurane"]).status_code == 429


# ---- Example f: a refused request asks nobody anything ----

def test_61_example_f_a_refused_explanation_asks_open_targets_and_gemini_nothing(
        client, clock, ids):
    for _ in range(30):
        ask_new(client, VISITOR_A, ids["Desflurane"])
    with patch("moonlight.fetch._post_json") as open_targets, \
            patch("moonlight.fetch._send") as open_targets_send, \
            patch("moonlight.explain._gemini_request") as gemini, \
            patch("moonlight.api.explain.explain") as explainer:
        refused = client.get("/api/explain", headers=VISITOR_A,
                             params={"disease_id": PAH_ID, "clue_id": ids["Isoflurane"]})
    assert refused.status_code == 429
    assert refused.json() == {"detail": TOO_MANY}  # no text, no template
    for door in (open_targets, open_targets_send, gemini, explainer):
        door.assert_not_called()


def test_61_example_f_a_refused_search_asks_open_targets_and_gemini_nothing(client, clock):
    for _ in range(60):
        test_api.one_search(client, VISITOR_A)
    with patch("moonlight.fetch._post_json") as open_targets, \
            patch("moonlight.fetch._send") as open_targets_send, \
            patch("moonlight.translate._gemini_request") as gemini:
        refused = client.get("/api/search", params={"q": "flu"}, headers=VISITOR_A)
    assert refused.status_code == 429
    assert refused.json() == {"detail": TOO_MANY}
    for door in (open_targets, open_targets_send, gemini):
        door.assert_not_called()


# ---- what stays the same ----

def test_61_a_saved_explanation_after_a_restart_is_not_counted(client, clock, ids):
    # Only the disk holds Sevoflurane's explanation now. Asking for it is
    # answered from the disk, makes no Gemini call and is not counted.
    first = save_sevoflurane(client, VISITOR_A, ids)  # new number 1
    explain.forget_everything()
    cache.forget_memory()
    for _ in range(40):
        again = ask(client, VISITOR_A, ids["Sevoflurane"], no_gemini)
        assert again.status_code == 200
        assert again.json() == first
    for _ in range(29):
        assert ask_new(client, VISITOR_A, ids["Desflurane"]).status_code == 200
    assert ask_new(client, VISITOR_A, ids["Desflurane"]).status_code == 429


def test_61_a_template_answer_is_not_saved_so_asking_again_is_new(client, clock, ids):
    # A template answer means Gemini could not be reached. It is not saved,
    # so the next request for that clue asks Gemini again: it is counted.
    for _ in range(30):
        ask_new(client, VISITOR_A, ids["Desflurane"])
    refused = ask(client, VISITOR_A, ids["Desflurane"], no_gemini)
    assert refused.status_code == 429


def test_61_the_other_rules_are_unchanged():
    assert api.TOO_MANY == TOO_MANY
    assert api.MAX_SEARCH_LETTERS == 100
    assert api.PROXIES_IN_FRONT == 1
    assert api.MINUTE_SECONDS == 60
    assert api.MAX_A_MINUTE == {"search": 60, "explain": 30}


def test_61_the_api_never_logs_or_prints_and_explain_never_logs():
    import re
    for name in ("api.py", "explain.py"):
        source = (test_api.ROOT / "moonlight" / name).read_text(encoding="utf-8")
        assert "logging" not in source
        assert not re.search(r"(?<![\w.])print\(", source)
