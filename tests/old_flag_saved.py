"""Saved answers for ticket 2.40 (fixtures/old_withdrawn_flag/).

Every question /api/clues asks for nine diseases, answered from the answers
study P11 replayed: saved on 21 Nov 2026 (Open Targets data 26.09) on the
branch probe-baseline, fixtures/probe_p5/responses/. Where that run saved
two answers to one question, the fuller one was kept, as fetch.py does.
Copied as sent, without indentation. index.json says which file answers
which question.
"""

import json
import pathlib
from unittest.mock import patch

from fastapi.testclient import TestClient

from moonlight import api, engine, fetch

ROOT = pathlib.Path(__file__).resolve().parent.parent
SAVED = ROOT / "fixtures" / "old_withdrawn_flag"
ANSWERS = SAVED / "answers"

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


def page_answer(disease_id, post_json=saved_post_json, wrong=None):
    """What /api/clues sends, from the saved answers. The hand-written files
    are the real ones unless a test hands in its own corrections."""
    api.forget_visitors()
    guards = no_network() + [patch("moonlight.fetch._post_json", side_effect=post_json)]
    if wrong is not None:
        guards.append(patch.object(engine, "_read_corrections", return_value=wrong))
    for guard in guards:
        guard.start()
    try:
        response = TestClient(api.app).get("/api/clues", params={"disease_id": disease_id})
    finally:
        for guard in guards:
            guard.stop()
        api.forget_visitors()
    assert response.status_code == 200, response.text
    return response.json()


def before(disease_id):
    """What main (af4e14d) sent before ticket 2.40, from the same saved answers."""
    return json.loads((SAVED / f"clues_before_2.40_{disease_id}.json").read_text(encoding="utf-8"))
