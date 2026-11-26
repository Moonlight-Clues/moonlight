"""Saved answers for ticket 2.63 (fixtures/wider_labels_2_63/).

Every Open Targets question /api/clues asks for three pages: type 2 diabetes
(MONDO_0005148), haemophilia A (MONDO_0010602) and acute intermittent
porphyria (MONDO_0008294). Saved live on 26 Nov 2026 (Open Targets data
26.09), as sent, without indentation. answers/index.json says which file
answers which question.

clues_before_2.63_<disease>.json is what main 401018f sent for each page from
these same answers, before this ticket: salt list off (as every unmarked test
sees it), and for AIP also with the salt list on (_salt.json).
"""

import json
import pathlib
from unittest.mock import patch

from fastapi.testclient import TestClient

from moonlight import api, engine, fetch

ROOT = pathlib.Path(__file__).resolve().parent.parent
SAVED = ROOT / "fixtures" / "wider_labels_2_63"
ANSWERS = SAVED / "answers"

T2D, HAEMOPHILIA_A, AIP = "MONDO_0005148", "MONDO_0010602", "MONDO_0008294"
PAGES = (T2D, HAEMOPHILIA_A, AIP)

KINDS = {
    fetch.DISEASE_QUERY: "disease",
    fetch.FAMILY_QUERY: "family",
    fetch.TARGETS_QUERY: "targets",
    fetch.TARGET_DRUGS_QUERY: "target_drugs",
    fetch.DISEASE_DRUGS_QUERY: "disease_drugs",
}


def _key(kind, variables):
    return kind + " " + json.dumps(variables, sort_keys=True)


_INDEX = {_key(entry["kind"], entry["variables"]): entry["file"]
          for entry in json.loads((ANSWERS / "index.json").read_text(encoding="utf-8"))}


def saved_post_json(body):
    """Stands in for fetch._post_json. A question with no saved answer is an error."""
    assert set(body) == {"query", "variables"}
    kind = KINDS.get(body["query"])
    assert kind is not None, "a question the saved answers never heard"
    key = _key(kind, body["variables"])
    assert key in _INDEX, f"no saved answer for {key}"
    return json.loads((ANSWERS / _INDEX[key]).read_text(encoding="utf-8"))


def no_network():
    return [patch(name, side_effect=AssertionError("network used")) for name in (
        "requests.request", "requests.post", "requests.get",
        "requests.sessions.Session.request")]


def page_answer(disease_id, extra=()):
    """What /api/clues sends, from the saved answers and the real hand-written
    files. extra: more patches a test needs (a hand list read as something else)."""
    api.forget_visitors()
    api.forget_answers()
    guards = no_network() + [patch.object(fetch, "_post_json", side_effect=saved_post_json)]
    guards += list(extra)
    for guard in guards:
        guard.start()
    try:
        response = TestClient(api.app).get("/api/clues", params={"disease_id": disease_id})
    finally:
        for guard in guards:
            guard.stop()
        api.forget_visitors()
        api.forget_answers()
    assert response.status_code == 200, response.text
    return response.json()


def before(disease_id, salt=False):
    name = f"clues_before_2.63_{disease_id}" + ("_salt" if salt else "") + ".json"
    return json.loads((SAVED / name).read_text(encoding="utf-8"))
