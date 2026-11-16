"""Ticket 5.9. Search shows real diseases the database filed under "measurement".

Saved files only, no network. The searches are the probe's saved answers in
fixtures/probe_p2/search/ and Gemini's names are in fixtures/probe_p2/gemini/
(both read from the live APIs on 2026-11-16, Open Targets data 26.09).
Open Targets is replaced at fetch._post_json and Gemini at
translate._gemini_request. Any real HTTP call is an error.

Kashish's decisions, 2026-11-16:
1. A match is hidden only when "measurement" is its ONLY group.
2. A match whose name, or exact "also called" name, is exactly what the
   person typed (capitals and spaces at the ends do not count) is never hidden.
3. Such an exact match is always first in the list.
4. When the typed words are an exact "also called" name and not the
   database's own name, the list shows the typed name as the big name,
   written as the database writes it, and under it "Database name: <name>".
   Asked on 2026-11-16: this is so for every such match (diabetes, lupus
   and flu too), not only for the ones filed under "measurement".
5. "Did you mean" follows the same rules.
6. Moonlight still never picks a disease for the person.
"""

import json
import pathlib
import re
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from moonlight import api, fetch, translate

ROOT = pathlib.Path(__file__).resolve().parent.parent
PROBE = ROOT / "fixtures" / "probe_p2"
SEARCHES = PROBE / "search"

MS = "EFO_0803536"
MS_DATABASE_NAME = "multiple sclerosis symptom measurement"
MS_KINDS = {
    "MONDO_0005284": "chronic progressive multiple sclerosis",
    "MONDO_0005314": "relapsing-remitting multiple sclerosis",
    "MONDO_0000451": "primary progressive multiple sclerosis",
    "MONDO_0000450": "secondary progressive multiple sclerosis",
}
ASTHMA = "MONDO_0004979"
ASTHMA_MEASUREMENTS = [
    "age of onset of asthma",
    "age of onset of childhood onset asthma",
    "asthma exacerbation measurement",
    "asthma symptoms measurement",
]
SAME_AS_BEFORE = ["diabetes", "breast cancer", "epilepsy", "lupus"]


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def slug(text):
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")


def saved_hits(words):
    return load(SEARCHES / f"{slug(words)}.response.json")["data"]["search"]["hits"]


def fake_post_json(body):
    """Stands in for fetch._post_json: the probe's saved search for these words."""
    assert set(body) == {"query", "variables"}
    saved = SEARCHES / f"{slug(body['variables']['text'])}.response.json"
    assert saved.exists(), f"no saved search for {body['variables']['text']!r}"
    return load(saved)


def gemini_says(text):
    """Stands in for translate._gemini_request: Gemini writes this text."""
    answer = {"candidates": [{"content": {"parts": [{"text": text}]}}]}

    def fake(method, path, body=None, timeout=None):
        if method == "GET":
            return 200, {"models": [{
                "name": "models/gemini-3.5-flash",
                "supportedGenerationMethods": ["generateContent"],
            }]}
        return 200, answer
    return fake


def gemini_saved(words):
    """The probe's saved Gemini answer for these words."""
    saved = load(PROBE / "gemini" / f"names_{slug(words)}.response.json")
    assert saved["status"] == 200
    answer = saved["answer"]

    def fake(method, path, body=None, timeout=None):
        if method == "GET":
            return 200, {"models": [{
                "name": "models/gemini-3.5-flash",
                "supportedGenerationMethods": ["generateContent"],
            }]}
        return 200, answer
    return fake


def with_gemini(fake):
    return patch("moonlight.translate._gemini_request", side_effect=fake)


def hits_answer(*hits):
    return {"data": {"search": {"total": len(hits), "hits": list(hits)}}}


def hit(id, name, groups, also_called=()):
    return {"id": id, "entity": "disease", "name": name, "category": list(groups),
            "object": {"synonyms": [
                {"relation": "hasExactSynonym", "terms": list(also_called)}]}}


@pytest.fixture(autouse=True)
def offline(tmp_path, monkeypatch):
    """Saved files instead of Open Targets. Real HTTP is an error."""
    monkeypatch.setenv("MOONLIGHT_CACHE_DIR", str(tmp_path))
    translate.forget_everything()
    api.forget_visitors()
    with patch("moonlight.fetch._post_json", side_effect=fake_post_json), \
            patch("requests.request", side_effect=AssertionError("network used")), \
            patch("requests.post", side_effect=AssertionError("network used")), \
            patch("requests.get", side_effect=AssertionError("network used")), \
            patch("requests.sessions.Session.request",
                  side_effect=AssertionError("network used")):
        yield
    translate.forget_everything()


@pytest.fixture
def client():
    return TestClient(api.app)


def search_json(client, words, gemini):
    with with_gemini(gemini):
        response = client.get("/api/search", params={"q": words})
    assert response.status_code == 200
    return response.json()


def page_script(client):
    return client.get("/").text


# ---- the saved answers really hold what the examples say ----

def test_the_saved_answers_hold_the_groups_the_ticket_talks_about():
    groups = {h["id"]: h["category"] for h in saved_hits("multiple sclerosis")}
    for entry in [MS, *MS_KINDS]:
        assert "measurement" in groups[entry] and len(groups[entry]) > 1
    said = {h["name"]: h["category"] for h in saved_hits("asthma")}
    for measurement in ASTHMA_MEASUREMENTS:
        assert said[measurement] == ["measurement"]
    first = saved_hits("multiple sclerosis")[0]
    assert first["id"] == MS and first["name"] == MS_DATABASE_NAME


# ---- EXAMPLE: "multiple sclerosis" ----

def test_multiple_sclerosis_first_match_is_the_entry_that_stands_for_it():
    found = fetch.search_matches("multiple sclerosis")
    assert found[0].disease.id == MS
    assert found[0].disease.name == MS_DATABASE_NAME
    assert "multiple sclerosis" in found[0].also_called


def test_the_four_kinds_of_multiple_sclerosis_are_shown_too():
    shown = {d.id: d.name for d in fetch.search_diseases("multiple sclerosis")}
    for entry, name in MS_KINDS.items():
        assert shown.get(entry) == name


def test_multiple_sclerosis_shows_all_ten_saved_matches_in_the_database_order():
    assert [d.id for d in fetch.search_diseases("multiple sclerosis")] == [
        h["id"] for h in saved_hits("multiple sclerosis")
    ]


def test_api_multiple_sclerosis_big_name_and_database_name(client):
    data = search_json(client, "multiple sclerosis", gemini_saved("multiple sclerosis"))
    # The entry is still Open Targets' own id and own name...
    assert data["matches"][0] == {"id": MS, "name": MS_DATABASE_NAME}
    # ...and the big name is Open Targets' own "also called" word.
    assert data["also_called"][MS] == "multiple sclerosis"
    shown = [match["id"] for match in data["matches"]]
    for entry in MS_KINDS:
        assert entry in shown
    # Gemini's one name is the first match already: not repeated.
    assert data["did_you_mean"] == []


def test_typed_capitals_and_spaces_do_not_change_the_big_name(client):
    data = search_json(client, "  MULTIPLE Sclerosis ", gemini_says("[]"))
    assert data["matches"][0]["id"] == MS
    assert data["also_called"][MS] == "multiple sclerosis"  # as the database writes it


# ---- EXAMPLE: "asthma" ----

def test_asthma_is_first_and_the_four_true_measurements_stay_hidden():
    found = fetch.search_diseases("asthma")
    assert found[0].id == ASTHMA and found[0].name == "asthma"
    names = [d.name for d in found]
    for measurement in ASTHMA_MEASUREMENTS:
        assert measurement not in names
    assert len(found) == 6


def test_api_asthma_looks_as_it_does_today(client):
    data = search_json(client, "asthma", gemini_saved("asthma"))
    assert data["matches"][0] == {"id": ASTHMA, "name": "asthma"}
    assert ASTHMA not in data["also_called"]  # typed its own name: no swap
    for entry in data["matches"] + data["did_you_mean"]:
        assert entry["name"] not in ASTHMA_MEASUREMENTS


# ---- EXAMPLE: the same matches in the same order as before ----

@pytest.mark.parametrize("words", SAME_AS_BEFORE)
def test_the_matches_and_their_order_are_the_same_as_before(words):
    before = [h["id"] for h in saved_hits(words) if "measurement" not in h["category"]]
    assert len(before) == 10
    assert [d.id for d in fetch.search_diseases(words)] == before


@pytest.mark.parametrize("words", SAME_AS_BEFORE)
def test_api_matches_are_the_same_as_before(client, words):
    data = search_json(client, words, gemini_saved(words))
    assert data["matches"] == [
        {"id": h["id"], "name": h["name"]} for h in saved_hits(words)
    ]


# ---- rule 1: hidden only when "measurement" is the ONLY group ----

def test_a_match_only_in_measurement_is_hidden():
    answer = hits_answer(
        hit("X_1", "sneeze count", ["measurement"]),
        hit("X_2", "sneezing disease", ["respiratory or thoracic disease"]),
    )
    with patch("moonlight.fetch._post_json", return_value=answer):
        assert [d.id for d in fetch.search_diseases("sneeze")] == ["X_2"]


def test_a_match_in_measurement_and_another_group_is_shown():
    answer = hits_answer(
        hit("X_1", "sneezing disease", ["measurement", "respiratory or thoracic disease"]),
        hit("X_2", "sneeze count", ["measurement"]),
        hit("X_3", "sneezing fits", ["phenotype", "measurement"]),
    )
    with patch("moonlight.fetch._post_json", return_value=answer):
        assert [d.id for d in fetch.search_diseases("sneeze")] == ["X_1", "X_3"]


# ---- rule 2: the exact name a person typed is never hidden ----

def test_a_measurement_is_shown_when_the_person_typed_its_exact_name():
    answer = hits_answer(
        hit("X_1", "sneezing disease", ["respiratory or thoracic disease"]),
        hit("X_2", "Sneeze count", ["measurement"]),
        hit("X_3", "sneeze count change", ["measurement"]),
    )
    with patch("moonlight.fetch._post_json", return_value=answer):
        assert [d.id for d in fetch.search_diseases("  sneeze COUNT ")] == ["X_2", "X_1"]


def test_a_measurement_is_shown_when_the_person_typed_its_exact_also_called_name():
    answer = hits_answer(
        hit("X_1", "sneezing disease", ["respiratory or thoracic disease"]),
        hit("X_2", "sternutation tally", ["measurement"], also_called=["Sneeze Count"]),
    )
    with patch("moonlight.fetch._post_json", return_value=answer):
        found = fetch.search_matches("sneeze count")
    assert [m.disease.id for m in found] == ["X_2", "X_1"]
    assert translate.small_print("sneeze count", found[0]) == "Sneeze Count"


def test_asthma_measurement_shows_only_when_its_exact_name_is_typed():
    # The saved answer for "asthma" stands in for the answer to the
    # measurement's own name here.
    hits = saved_hits("asthma")
    with patch("moonlight.fetch._post_json", return_value=hits_answer(*hits)):
        found = fetch.search_diseases("Age of onset of asthma")
    assert found[0].name == "age of onset of asthma"
    for other in ASTHMA_MEASUREMENTS[1:]:
        assert other not in [d.name for d in found]


def test_a_name_that_only_nearly_matches_is_not_exact():
    answer = hits_answer(
        hit("X_1", "sneezing disease", ["respiratory or thoracic disease"]),
        hit("X_2", "sneeze count", ["measurement"]),
    )
    with patch("moonlight.fetch._post_json", return_value=answer):
        assert [d.id for d in fetch.search_diseases("sneeze coun")] == ["X_1"]
        assert [d.id for d in fetch.search_diseases("sneezecount")] == ["X_1"]


def test_two_spaces_between_words_count_as_one():
    # The same comparing as the small print has used since 2026-11-13
    # ("capitals and extra spaces do not count"), so the two always agree.
    answer = hits_answer(
        hit("X_1", "sneezing disease", ["respiratory or thoracic disease"]),
        hit("X_2", "sneeze count", ["measurement"]),
    )
    with patch("moonlight.fetch._post_json", return_value=answer):
        assert [d.id for d in fetch.search_diseases("sneeze  count")] == ["X_2", "X_1"]


def test_only_the_exact_also_called_group_counts():
    narrow = hit("X_2", "sneeze tally", ["measurement"])
    narrow["object"]["synonyms"] = [{"relation": "hasNarrowSynonym", "terms": ["sneeze count"]}]
    answer = hits_answer(hit("X_1", "sneezing disease", ["phenotype"]), narrow)
    with patch("moonlight.fetch._post_json", return_value=answer):
        assert [d.id for d in fetch.search_diseases("sneeze count")] == ["X_1"]


# ---- rule 3: an exact match is always first ----

def test_an_exact_match_moves_to_the_front_and_the_rest_keep_their_order():
    answer = hits_answer(
        hit("X_1", "sneezing disease", ["phenotype"]),
        hit("X_2", "sneezing fits", ["phenotype"]),
        hit("X_3", "sternutation", ["phenotype"], also_called=["sneezing"]),
        hit("X_4", "sneezing", ["phenotype"]),
        hit("X_5", "sneeze reflex", ["phenotype"]),
    )
    with patch("moonlight.fetch._post_json", return_value=answer):
        assert [d.id for d in fetch.search_diseases("Sneezing")] == [
            "X_3", "X_4", "X_1", "X_2", "X_5",
        ]


def test_lupus_has_two_exact_matches_and_they_keep_the_database_order():
    found = fetch.search_matches("lupus")
    assert [m.disease.name for m in found[:2]] == [
        "lupus erythematosus", "systemic lupus erythematosus",
    ]
    assert [translate.small_print("lupus", m) for m in found[:2]] == ["lupus", "lupus"]
    assert translate.small_print("lupus", found[2]) is None


# ---- an answer saved before 2026-11-13 has no groups: nothing is hidden ----

def test_a_hit_with_no_groups_is_shown():
    answer = hits_answer(
        {"id": "X_1", "entity": "disease", "name": "sneezing disease"},
        {"id": "X_2", "entity": "disease", "name": "sneeze count", "category": []},
    )
    with patch("moonlight.fetch._post_json", return_value=answer):
        assert [d.id for d in fetch.search_diseases("sneeze")] == ["X_1", "X_2"]


# ---- rule 4: the typed "also called" name is the big name ----

def test_api_diabetes_gives_the_page_the_typed_also_called_name(client):
    data = search_json(client, "diabetes", gemini_saved("diabetes"))
    assert data["matches"][0] == {"id": "MONDO_0005015", "name": "diabetes mellitus"}
    assert data["also_called"]["MONDO_0005015"] == "diabetes"


def test_the_page_shows_the_also_called_name_big_and_the_database_name_small(client):
    script = page_script(client)
    choice = script[script.index("function choice("):script.index("async function search(")]
    assert '"Database name: " + entry.name' in choice
    assert "capital(alsoCalled || entry.name)" in choice
    assert '"Also called: " + alsoCalled' not in choice
    # The disease page's own "Also called" line is not touched.
    assert '"Also called: " + names.join("; ")' in script


def test_a_match_with_no_also_called_word_looks_as_it_does_today(client):
    script = page_script(client)
    choice = script[script.index("function choice("):script.index("async function search(")]
    # No word: the big name is the database's name and the small print is the id.
    assert 'alsoCalled ? "Database name: " + entry.name + " · " : ""' in choice
    assert "+ entry.id" in choice


# ---- rule 5: "Did you mean" follows the same rules ----

def test_did_you_mean_finds_multiple_sclerosis_from_geminis_name():
    with with_gemini(gemini_says('["Multiple Sclerosis"]')):
        found = translate.did_you_mean("multipel sclerosys")
    assert len(found) == 1
    assert found[0].disease.id == MS
    assert found[0].disease.name == MS_DATABASE_NAME
    assert found[0].also_called == "multiple sclerosis"


def test_api_did_you_mean_carries_the_big_name_for_multiple_sclerosis(client):
    empty = hits_answer()

    def open_targets(body):
        if body["variables"]["text"] == "multipel sclerosys":
            return empty
        return fake_post_json(body)

    with patch("moonlight.fetch._post_json", side_effect=open_targets):
        data = search_json(client, "multipel sclerosys", gemini_says('["Multiple Sclerosis"]'))
    assert data["matches"] == []
    assert data["did_you_mean"] == [{"id": MS, "name": MS_DATABASE_NAME}]
    assert data["also_called"] == {MS: "multiple sclerosis"}


def test_did_you_mean_still_never_holds_a_true_measurement():
    with with_gemini(gemini_saved("asthma")):
        found = translate.did_you_mean("asthma")
    for suggestion in found:
        assert suggestion.disease.name not in ASTHMA_MEASUREMENTS
    assert found[0].disease.id == ASTHMA


# ---- rule 6: Moonlight still never picks a disease ----

def test_the_search_answer_still_only_offers(client):
    data = search_json(client, "multiple sclerosis", gemini_saved("multiple sclerosis"))
    assert set(data) == {"matches", "did_you_mean", "also_called"}
    for entry in data["matches"] + data["did_you_mean"]:
        assert set(entry) == {"id", "name"}


# ---- DECISIONS.md ----

def test_the_two_decisions_are_written_down():
    written = (ROOT / "DECISIONS.md").read_text(encoding="utf-8")
    assert ('- 2026-11-16: A disease is hidden from search only if "measurement" is its '
            "only group. The exact name a person typed is never hidden and always "
            "comes first.") in written
    assert ("- 2026-11-16: If the typed words are one of the database's \"also called\" "
            "names, the list shows those words first and the database's own name "
            "under them.") in written
