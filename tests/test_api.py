"""Ticket 5.1. The small API and Sidha's designed page, medicine first.

Each EXAMPLE in the ticket is a test here. Saved files only, no network:
fetch._post_json and explain._gemini_request are swapped for fakes, and any
real HTTP call is an error.
"""

import json
import pathlib
import re
from unittest.mock import patch

import pytest
import requests
from fastapi.testclient import TestClient

from moonlight import api, engine, explain, fetch
from moonlight.rank import RULE_TEXT
from moonlight.records import Disease

ROOT = pathlib.Path(__file__).resolve().parent.parent
GOLDEN = ROOT / "fixtures" / "MONDO_0015924"
PAH_ID = "MONDO_0015924"
PAH = Disease(id=PAH_ID, name="pulmonary arterial hypertension")

SAFETY_LINE = (
    "For learning and research exploration, not medical advice. "
    "Never start, stop or change any medicine without a doctor."
)
ENDING = (
    "But there is a catch. Nobody knows from our information if the "
    "disease needs this protein turned up or down. So this is a clue to "
    "read about. Never start, stop or change any medicine without a doctor."
)
ENDING_MANY = ENDING.replace("this protein", "these proteins")

FIVE = ("BMPR2", "KCNK3", "ACVRL1", "EDNRA", "PDE5A")
GUCY1 = ("GUCY1A1", "GUCY1B1", "GUCY1A2")
NEW_ORDER = [
    "Dibotermin Alfa", "Eptotermin Alfa", "Sevoflurane", "Desflurane",
    "Isoflurane", "Doxapram", "Enflurane", "Halothane", "Atrasentan",
    "Sparsentan", "Aprocitentan", "Clazosentan", "Pentoxifylline",
    "Dipyridamole", "Avanafil", "Ibudilast",
]
SAVED_IDS = {
    path.name.split(".")[0].split("_")[-1]
    for path in (GOLDEN / "target_drugs").glob("*.response.json")
}


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def fake_post_json(body):
    """Stands in for fetch._post_json: picks the saved response for a request."""
    assert set(body) == {"query", "variables"}
    query, variables = body["query"], body["variables"]
    if "text" in variables:
        saved = load(GOLDEN / "disease_search.request.json")["variables"]
        assert variables["text"] == saved["text"], "no saved search for this text"
        return load(GOLDEN / "disease_search.response.json")
    if "targetId" in variables:
        matches = list(
            (GOLDEN / "target_drugs").glob(f"*_{variables['targetId']}.response.json")
        )
        assert len(matches) == 1, f"no saved file for target {variables['targetId']}"
        return load(matches[0])
    if variables["diseaseId"] != PAH_ID:
        return {"data": {"disease": None}}  # a disease Open Targets does not know
    if "associatedTargets" in query:
        return load(GOLDEN / "associated_targets.response.json")
    if "drugAndClinicalCandidates" in query:
        return load(GOLDEN / "disease_drugs.response.json")
    return load(GOLDEN / "disease_description.response.json")


@pytest.fixture(autouse=True)
def offline():
    """Saved files instead of Open Targets. Real HTTP is an error."""
    explain.forget_everything()
    with patch("moonlight.fetch._post_json", side_effect=fake_post_json), \
            patch("requests.request", side_effect=AssertionError("network used")), \
            patch("requests.post", side_effect=AssertionError("network used")), \
            patch("requests.get", side_effect=AssertionError("network used")), \
            patch("requests.sessions.Session.request",
                  side_effect=AssertionError("network used")), \
            patch("moonlight.explain.time.sleep"):
        yield
    explain.forget_everything()


@pytest.fixture
def client():
    return TestClient(api.app)


def targets_named(*symbols):
    by_symbol = {t.symbol: t for t in fetch.fetch_targets(PAH)}
    return [by_symbol[symbol] for symbol in symbols]


def with_targets(*symbols):
    """The API looks at only these proteins, as in Kashish's answer key."""
    return patch("moonlight.api.fetch_targets", return_value=targets_named(*symbols))


def with_saved_targets():
    """The API looks at every protein that has a saved file."""
    saved = [t for t in fetch.fetch_targets(PAH) if t.id in SAVED_IDS]
    return patch("moonlight.api.fetch_targets", return_value=saved)


def gemini_unreachable(method, path, body=None, timeout=None):
    raise requests.ConnectionError("no network")


def gemini_says(text, model="gemini-3.5-flash"):
    """Stands in for explain._gemini_request with one good answer."""
    def fake(method, path, body=None, timeout=None):
        if method == "GET":
            return 200, {"models": [{
                "name": f"models/{model}",
                "supportedGenerationMethods": ["generateContent"],
            }]}
        return 200, {"candidates": [{"content": {"parts": [{"text": text}]}}]}
    return fake


def clues_json(client, *symbols):
    with with_targets(*symbols):
        response = client.get("/api/clues", params={"disease_id": PAH_ID})
    assert response.status_code == 200
    return response.json()


def clue_named(clues, name):
    found = [clue for clue in clues if clue["medicine"] == name]
    assert len(found) == 1, f"expected one {name}, found {len(found)}"
    return found[0]


# ---- Example 1 ----

def test_five_proteins_give_16_new_clues_in_kashishs_order(client):
    data = clues_json(client, *FIVE)
    assert [clue["medicine"] for clue in data["new_clues"]] == NEW_ORDER
    assert len(data["new_clues"]) == 16
    assert data["new_clues"][0]["medicine"] == "Dibotermin Alfa"


def test_five_proteins_give_2_being_studied_udenafil_then_vardenafil(client):
    data = clues_json(client, *FIVE)
    assert [clue["medicine"] for clue in data["being_studied"]] == ["Udenafil", "Vardenafil"]


def test_the_api_order_is_the_engines_order(client):
    ranked = engine.find_ranked_clues(PAH, targets_named(*FIVE))
    data = clues_json(client, *FIVE)
    for key, clues in (("new_clues", ranked.new_clues), ("being_studied", ranked.being_studied)):
        assert [c["medicine"].upper() for c in data[key]] == [
            clue.medicine.name.upper() for clue in clues
        ]
        assert [c["reports"] for c in data[key]] == [clue.reports for clue in clues]


def test_clues_carry_the_disease_and_the_rule_text_word_for_word(client):
    data = clues_json(client, *FIVE)
    assert data["disease"] == {"id": PAH_ID, "name": "pulmonary arterial hypertension"}
    assert data["rule_text"] == RULE_TEXT


def test_each_clue_has_its_facts_and_no_explanation(client):
    data = clues_json(client, *FIVE)
    ids = set()
    for clue in data["new_clues"] + data["being_studied"]:
        assert set(clue) == {
            "id", "medicine", "forms", "proteins", "reports", "source",
            "trial_phase", "ending",
        }
        assert clue["id"] and clue["forms"] and clue["proteins"]
        assert isinstance(clue["reports"], int)
        for protein in clue["proteins"]:
            assert set(protein) == {"symbol", "points", "direction", "machine", "piece_of_machine"}
            assert protein["direction"] in ("up", "down", "mixed", "unknown")
        ids.add(clue["id"])
    assert len(ids) == 18  # every clue has its own id


def test_forms_are_shown_inside_the_medicine(client):
    data = clues_json(client, *FIVE)
    assert clue_named(data["new_clues"], "Doxapram")["forms"] == [
        "Doxapram", "Doxapram Hydrochloride",
    ]


def test_one_source_link_or_none(client):
    data = clues_json(client, *FIVE)
    for clue in data["new_clues"] + data["being_studied"]:
        assert clue["source"] is None or clue["source"].startswith("https://")
    assert clue_named(data["new_clues"], "Sevoflurane")["source"].startswith("https://")


def test_trial_phase_is_only_for_being_studied(client):
    data = clues_json(client, *FIVE)
    assert all(clue["trial_phase"] is None for clue in data["new_clues"])
    assert clue_named(data["being_studied"], "Vardenafil")["trial_phase"] == "Phase 3"
    assert all(clue["trial_phase"].startswith("Phase ") or
               clue["trial_phase"].startswith("Early Phase ")
               for clue in data["being_studied"])


def test_one_protein_gets_the_ending_word_for_word(client):
    data = clues_json(client, *FIVE)
    assert clue_named(data["new_clues"], "Sevoflurane")["ending"] == ENDING


# ---- Example 2 ----

def all_api_text(client):
    """Everything the API can say about PAH, joined, in capitals."""
    said = [client.get("/").text]
    said.append(client.get("/api/search", params={"q": "pulmonary arterial hypertension"}).text)
    with with_saved_targets():
        clues = client.get("/api/clues", params={"disease_id": PAH_ID})
        said.append(clues.text)
        with patch("moonlight.explain._gemini_request", side_effect=gemini_unreachable):
            for clue in clues.json()["new_clues"] + clues.json()["being_studied"]:
                api.forget_visitors()  # this test is not about the limit
                answer = client.get(
                    "/api/explain", params={"disease_id": PAH_ID, "clue_id": clue["id"]}
                )
                assert answer.status_code == 200
                said.append(answer.text)
    return "\n".join(said).upper()


def test_sildenafil_and_tadalafil_are_only_in_the_approved_list(client):
    with with_saved_targets():
        data = client.get("/api/clues", params={"disease_id": PAH_ID}).json()
    approved = [item["medicine"] for item in data["approved"]]
    assert "Sildenafil" in approved and "Tadalafil" in approved
    others = json.dumps([data["new_clues"], data["being_studied"]]).upper()
    assert "VARDENAFIL" in others  # it really answered
    assert "SILDENAFIL" not in others and "TADALAFIL" not in others


def test_no_response_names_any_medicine_from_a_hidden_group(client):
    saved = [t for t in fetch.fetch_targets(PAH) if t.id in SAVED_IDS]
    tray = engine.find_clues(PAH, saved)
    hidden = set()
    for group in ("not_approved", "unclear_link"):
        for path in tray[group]:
            hidden.add(path.medicine.name.upper())
            hidden.update(form.name.upper() for form in path.medicine.forms)
    assert len(hidden) > 10
    text = all_api_text(client)
    assert [name for name in sorted(hidden) if name in text] == []


def test_a_hidden_medicine_cannot_be_explained(client):
    (pde5a,) = targets_named("PDE5A")
    sildenafil = [
        p for p in fetch.fetch_paths(PAH, pde5a) if p.medicine.name.upper() == "SILDENAFIL"
    ][0]
    with with_targets(*FIVE), \
            patch("moonlight.explain._gemini_request", side_effect=gemini_unreachable):
        answer = client.get(
            "/api/explain",
            params={"disease_id": PAH_ID, "clue_id": sildenafil.medicine.forms[0].id},
        )
    assert answer.status_code == 404
    assert "SILDENAFIL" not in answer.text.upper()


def test_gemini_naming_a_hidden_medicine_is_thrown_away(client):
    data = clues_json(client, *FIVE)
    avanafil = clue_named(data["new_clues"], "Avanafil")
    sneaky = (
        "Avanafil is a medicine. Sildenafil is a medicine too. "
        "It grabs a protein called PDE5A. A protein is a tiny machine in your body."
    )
    with with_targets(*FIVE), \
            patch("moonlight.explain._gemini_request", side_effect=gemini_says(sneaky)):
        answer = client.get(
            "/api/explain", params={"disease_id": PAH_ID, "clue_id": avanafil["id"]}
        )
    assert answer.status_code == 200
    assert answer.json()["source"] == "template"
    assert "SILDENAFIL" not in answer.text.upper()


# ---- Example 3 ----

def test_left_out_is_two_numbers_12_0(client):
    data = clues_json(client, *FIVE)
    assert data["left_out"] == {"not_approved": 12, "unclear_link": 0}
    assert list(data["left_out"].values()) == [12, 0]


# ---- Example 4 ----

def test_sevoflurane_kcnk3_score_is_79(client):
    data = clues_json(client, *FIVE)
    sevoflurane = clue_named(data["new_clues"], "Sevoflurane")
    assert sevoflurane["proteins"] == [{
        "symbol": "KCNK3", "points": 79, "direction": "up",
        "machine": 1, "piece_of_machine": False,
    }]


def test_points_are_the_same_whole_numbers_the_explainer_uses(client):
    ranked = engine.find_ranked_clues(PAH, targets_named(*FIVE))
    data = clues_json(client, *FIVE)
    shown = data["new_clues"] + data["being_studied"]
    for clue, sent in zip(ranked.new_clues + ranked.being_studied, shown):
        facts = explain.facts_for(clue, PAH)
        assert [f"{p['points']} points out of 100" for p in sent["proteins"]] == [
            p["link_score_as_points"] for p in facts["proteins"]
        ]
        assert all(isinstance(p["points"], int) for p in sent["proteins"])


# ---- Example 5 ----

def test_isosorbide_mononitrate_is_one_clue_with_three_pieces_of_one_machine(client):
    data = clues_json(client, *GUCY1)
    isosorbide = clue_named(data["new_clues"], "Isosorbide Mononitrate")  # insists on one
    assert [p["symbol"] for p in isosorbide["proteins"]] == list(GUCY1)
    assert [p["points"] for p in isosorbide["proteins"]] == [60, 58, 58]
    assert [p["machine"] for p in isosorbide["proteins"]] == [1, 1, 1]
    assert all(p["piece_of_machine"] for p in isosorbide["proteins"])
    assert [p["direction"] for p in isosorbide["proteins"]] == ["up", "up", "up"]


def test_more_than_one_protein_gets_the_these_proteins_ending(client):
    data = clues_json(client, *GUCY1)
    assert clue_named(data["new_clues"], "Isosorbide Mononitrate")["ending"] == ENDING_MANY


# ---- Example 6 ----

GOOD_ANSWER = load(ROOT / "fixtures" / "gemini" / "sevoflurane_generate.response.json")[
    "candidates"][0]["content"]["parts"][0]["text"]


def explain_sevoflurane(client, gemini):
    data = clues_json(client, *FIVE)
    sevoflurane = clue_named(data["new_clues"], "Sevoflurane")
    with with_targets(*FIVE), patch("moonlight.explain._gemini_request", side_effect=gemini):
        answer = client.get(
            "/api/explain", params={"disease_id": PAH_ID, "clue_id": sevoflurane["id"]}
        )
    assert answer.status_code == 200
    return sevoflurane, answer.json()


def test_explain_gives_gemini_text_ending_with_the_ending(client):
    sevoflurane, answer = explain_sevoflurane(client, gemini_says(GOOD_ANSWER))
    assert set(answer) == {"clue_id", "text", "source", "model"}
    assert answer["clue_id"] == sevoflurane["id"]
    assert answer["text"] == GOOD_ANSWER + " " + ENDING
    assert answer["text"].endswith(ENDING)
    assert answer["source"] == "gemini"
    assert answer["model"] == "gemini-3.5-flash"


def test_explain_gives_the_template_when_gemini_cannot_be_reached(client):
    _, answer = explain_sevoflurane(client, gemini_unreachable)
    assert answer["source"] == "template"
    assert answer["model"] is None
    assert answer["text"].startswith("Sevoflurane is a medicine.")
    assert answer["text"].endswith(ENDING)


def test_explain_for_a_clue_that_is_not_there_is_404(client):
    with with_targets(*FIVE), \
            patch("moonlight.explain._gemini_request", side_effect=gemini_unreachable):
        answer = client.get(
            "/api/explain", params={"disease_id": PAH_ID, "clue_id": "CHEMBL0"}
        )
    assert answer.status_code == 404


# ---- Example 7 ----

def test_the_page_has_the_safety_line_word_for_word(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    assert SAFETY_LINE in response.text
    assert SAFETY_LINE in (ROOT / "CLAUDE.md").read_text(encoding="utf-8").replace(
        "\n  ", " "
    )


def test_the_safety_line_is_in_the_html_before_any_script(client):
    page = client.get("/").text
    assert page.index(SAFETY_LINE) < page.index("<script")
    assert 'data-slot="safety-line"' in page[: page.index(SAFETY_LINE)]


def test_the_page_has_the_rule_text_slot_and_sidhas_other_slots(client):
    page = client.get("/").text
    for slot in (
        "rule-text", "safety-line", "search", "matches", "chips", "new-clues",
        "studied", "left-out", "card", "medicine-name", "forms", "reports",
        "path", "protein", "score", "direction", "explanation", "ending",
        "source", "phase", "loading", "empty",
    ):
        assert f'data-slot="{slot}"' in page, slot


# Kashish's decision, 2026-11-16 (ticket 8.3, asked under STOP). The page
# loads one thing from outside: Umami's script, in exactly this tag. The two
# "nothing from outside" tests lift this one tag out and then check
# everything else as before. Any other outside address still fails them.
UMAMI_TAG = (
    '<script defer crossorigin="anonymous" src="https://cloud.umami.is/script.js"'
    ' data-website-id="dad3a425-ea8e-4028-9768-88a183fc9140"'
    ' data-domains="moonlightclues.com,www.moonlightclues.com,'
    'moonlight-1038733794937.asia-south1.run.app"'
    ' data-exclude-search="true" data-exclude-hash="true"'
    ' data-do-not-track="true" data-before-send="moonlightVisit"></script>'
)


def without_the_umami_script(page):
    assert page.count(UMAMI_TAG) == 1
    return page.replace(UMAMI_TAG, "")


def words_people_can_see(page):
    """The page without its styles, scripts, notes and tags."""
    page = re.sub(r"(?s)<(script|style)\b.*?</\1>|<!--.*?-->", " ", page)
    return re.sub(r"<[^>]+>", " ", page)


def test_the_page_has_no_outside_link(client):
    page = without_the_umami_script(client.get("/").text)
    assert "http" not in page.lower()  # no font, script, stylesheet or any other outside address
    assert "//" not in re.sub(r"(?s)<script>.*?</script>", "", page)  # no "//host" address either
    assert "@import" not in page
    assert "<link" not in page.lower()
    assert not re.search(r"<script[^>]+src", page, flags=re.IGNORECASE)
    assert "target=" not in page  # nothing opens in a new tab
    assert "window.open" not in page


def test_the_page_wording(client):
    page = client.get("/").text
    assert 'placeholder="Type a disease name"' in page
    assert "Search by disease name<" in page
    assert (
        "An explorer that shows which existing medicines act on the proteins "
        "linked to a disease, using open research data."
    ) in page
    assert "Please wait, fetching data" in page
    assert "Already being studied for this disease" in page
    assert "The data does not say which direction this disease needs." in page
    assert "Read explanation" in page


def test_the_only_quick_start_chip_is_pah_by_its_id(client):
    page = client.get("/").text
    chips = re.findall(r'<button class="chip"[^>]*>(.*?)</button>', page)
    assert chips == ["Pulmonary arterial hypertension"]
    assert 'data-disease-id="MONDO_0015924"' in page


def test_the_page_names_no_medicine_before_a_search(client):
    # Kashish's decision, 2026-11-15 (ticket 5.4): the guide shows one real
    # card, Doxapram. Outside the guide the page names no medicine. Inside
    # the guide the only medicine named is Doxapram, with its form.
    page = client.get("/").text
    guide = guide_of(page)
    assert page.count(guide) == 1
    outside = page.replace(guide, "").upper()
    for name in NEW_ORDER + ["Udenafil", "Vardenafil", "Sildenafil", "Tadalafil"]:
        assert name.upper() not in outside, name
        if name != "Doxapram":
            assert name.upper() not in guide.upper(), name


# ---- /api/search ----

def test_search_gives_matches_best_first(client):
    response = client.get("/api/search", params={"q": "pulmonary arterial hypertension"})
    assert response.status_code == 200
    matches = response.json()["matches"]
    assert matches[0] == {"id": PAH_ID, "name": "pulmonary arterial hypertension"}
    assert all(set(match) == {"id", "name"} for match in matches)
    assert [m["id"] for m in matches] == [
        d.id for d in fetch.search_diseases("pulmonary arterial hypertension")
    ]


def test_search_with_nothing_typed_asks_nothing_and_matches_nothing(client):
    with patch("moonlight.api.search_diseases") as spy:
        response = client.get("/api/search", params={"q": "   "})
    assert response.json() == {"matches": []}
    spy.assert_not_called()


# ---- when things go wrong ----

def test_a_disease_open_targets_does_not_know_is_404(client):
    response = client.get("/api/clues", params={"disease_id": "MONDO_0000000"})
    assert response.status_code == 404


def test_a_disease_with_no_clues_gives_empty_lists_and_zero_counts(client):
    with patch("moonlight.api.fetch_targets", return_value=[]):
        data = client.get("/api/clues", params={"disease_id": PAH_ID}).json()
    assert data["new_clues"] == [] and data["being_studied"] == []
    assert data["left_out"] == {"not_approved": 0, "unclear_link": 0}


def test_open_targets_being_down_is_a_502_not_a_crash(client):
    with patch("moonlight.fetch._post_json", side_effect=requests.ConnectionError("down")):
        response = client.get("/api/clues", params={"disease_id": PAH_ID})
    assert response.status_code == 502
    assert "detail" in response.json()


def test_the_api_asks_for_the_top_25_proteins(client):
    with patch("moonlight.api.fetch_targets", return_value=[]) as spy:
        client.get("/api/clues", params={"disease_id": PAH_ID})
    assert spy.call_args.args[1:] == (25,) or spy.call_args.kwargs.get("limit") == 25


# =====================================================================
# Ticket 6.3: the API gives explain() the data version, so a finished
# explanation is saved
# =====================================================================

from moonlight import cache  # noqa: E402

NEW_ENDING = "This is only a clue to read about. Do not try it."


def fake_send(body):
    """Stands in for fetch._send. Only the data version is ever asked for
    here, because fetch._post_json is already swapped for saved files.
    The shape was copied from the live API on 2026-11-12."""
    assert "dataVersion" in body["query"], "only the data version may be asked"
    return {"data": {"meta": {"dataVersion": {"year": "26", "month": "09",
                                              "iteration": None}}}}


@pytest.fixture(autouse=True)
def pretend_data_version_and_throwaway_folder(tmp_path, monkeypatch):
    """Every test in this file gets data version 26.09 and a throwaway
    folder for the saved results.

    Kashish's decision, 2026-11-13 (asked under STOP AND ASK). The API now
    reads the data version for /api/explain. The ticket 5.1 tests above
    block the network and had no pretend version, so five of them failed.
    This is new set-up. No line of those tests was changed.
    """
    monkeypatch.setenv("MOONLIGHT_CACHE_DIR", str(tmp_path / "saved"))
    cache.forget_memory()
    fetch.forget_version()
    with patch("moonlight.fetch._send", side_effect=fake_send):
        yield tmp_path / "saved"
    cache.forget_memory()
    fetch.forget_version()


@pytest.fixture
def saved_results(pretend_data_version_and_throwaway_folder):
    """The throwaway folder the saved results go in."""
    return pretend_data_version_and_throwaway_folder


def new_program():
    """What a restarted server starts with: nothing in memory."""
    explain.forget_everything()
    cache.forget_memory()
    fetch.forget_version()


class CountingGemini:
    """Stands in for explain._gemini_request. Counts the generate calls."""

    def __init__(self, text=GOOD_ANSWER):
        self.text = text
        self.calls = 0  # every call, the model list too
        self.generate_calls = 0

    def __call__(self, method, path, body=None, timeout=None):
        self.calls += 1
        if method == "GET":
            return 200, {"models": [{
                "name": "models/gemini-3.5-flash",
                "supportedGenerationMethods": ["generateContent"],
            }]}
        self.generate_calls += 1
        return 200, {"candidates": [{"content": {"parts": [{"text": self.text}]}}]}


def sevoflurane_id(client):
    return clue_named(clues_json(client, *FIVE)["new_clues"], "Sevoflurane")["id"]


def ask_explain(client, clue_id):
    with with_targets(*FIVE):
        return client.get("/api/explain", params={"disease_id": PAH_ID, "clue_id": clue_id})


# Example 3
def test_63_example_3_two_explain_requests_for_the_same_clue_make_one_gemini_call(
        client, saved_results):
    clue_id = sevoflurane_id(client)
    gemini = CountingGemini()
    with patch("moonlight.explain._gemini_request", side_effect=gemini):
        first = ask_explain(client, clue_id)
        second = ask_explain(client, clue_id)
    assert first.status_code == second.status_code == 200
    assert gemini.generate_calls == 1
    assert second.json() == first.json()
    assert first.json()["source"] == "gemini"


def test_63_example_3_still_one_gemini_call_after_the_server_restarts(client, saved_results):
    clue_id = sevoflurane_id(client)
    gemini = CountingGemini()
    with patch("moonlight.explain._gemini_request", side_effect=gemini):
        first = ask_explain(client, clue_id)
        calls = gemini.calls
        new_program()  # only the disk holds the explanation now
        second = ask_explain(client, clue_id)
    assert gemini.calls == calls  # no Gemini call at all, not even the model list
    assert gemini.generate_calls == 1
    assert second.json() == first.json()
    assert second.json()["source"] == "gemini"


def test_63_the_api_gives_explain_the_data_version(client, saved_results):
    clue_id = sevoflurane_id(client)
    with patch("moonlight.api.explain.explain", wraps=explain.explain) as spy, \
            patch("moonlight.explain._gemini_request", side_effect=CountingGemini()):
        ask_explain(client, clue_id)
    arguments = spy.call_args
    given = arguments.kwargs.get("data_version") or arguments.args[3]
    assert given == "26.09"
    # The explanation is filed under that data version on disk.
    saved = [json.loads(file.read_text(encoding="utf-8"))
             for file in saved_results.rglob("*.json")]
    assert [(entry["kind"], entry["version"]) for entry in saved] == [("explanation", "26.09")]


# Example 4
def test_63_example_4_changing_the_ending_means_a_saved_explanation_is_not_reused(
        client, saved_results):
    clue_id = sevoflurane_id(client)
    gemini = CountingGemini()
    with patch("moonlight.explain._gemini_request", side_effect=gemini):
        old = ask_explain(client, clue_id).json()
        assert gemini.generate_calls == 1

        new_program()  # only the disk holds the old text now
        with patch("moonlight.explain.ENDING", NEW_ENDING):
            new = ask_explain(client, clue_id).json()
    assert gemini.generate_calls == 2  # asked afresh, the saved one was not reused
    assert old["text"].endswith(ENDING)
    assert new["text"].endswith(NEW_ENDING)
    assert ENDING not in new["text"]


def test_63_example_4_changing_the_ending_without_a_restart_is_not_reused_either(
        client, saved_results):
    clue_id = sevoflurane_id(client)
    gemini = CountingGemini()
    with patch("moonlight.explain._gemini_request", side_effect=gemini):
        ask_explain(client, clue_id)
        with patch("moonlight.explain.ENDING", NEW_ENDING):
            new = ask_explain(client, clue_id).json()
    assert gemini.generate_calls == 2
    assert new["text"].endswith(NEW_ENDING)
    assert ENDING not in new["text"]


def test_63_a_template_explanation_is_not_saved_so_gemini_gets_another_go(client, saved_results):
    clue_id = sevoflurane_id(client)
    with patch("moonlight.explain._gemini_request", side_effect=gemini_unreachable):
        first = ask_explain(client, clue_id).json()
    assert first["source"] == "template"
    assert not list(saved_results.rglob("*.json"))
    gemini = CountingGemini()
    with patch("moonlight.explain._gemini_request", side_effect=gemini):
        second = ask_explain(client, clue_id).json()
    assert second["source"] == "gemini"
    assert gemini.generate_calls == 1


def test_63_if_the_data_version_cannot_be_read_it_is_a_502_not_a_crash(client, saved_results):
    clue_id = sevoflurane_id(client)
    gemini = CountingGemini()
    with patch("moonlight.fetch._send", side_effect=requests.ConnectionError("down")), \
            patch("moonlight.explain._gemini_request", side_effect=gemini):
        response = ask_explain(client, clue_id)
    assert response.status_code == 502
    assert "detail" in response.json()
    assert gemini.calls == 0


# ==== Ticket 5.2: search that understands people ====
#
# New tests only. Saved files, no network: the searches come from
# fixtures/search/ and Gemini's names from fixtures/gemini/names_*.

import contextlib
import threading
import time

from moonlight import translate

SEARCHES = ROOT / "fixtures" / "search"
FLU_ENTRY = {"id": "EFO_0007411", "name": "Orthomyxoviridae infectious disease"}
AVIAN = {"id": "MONDO_0018695", "name": "avian influenza"}
SWINE = {"id": "MONDO_0005460", "name": "swine influenza"}
MEASUREMENT_NAMES = [
    "diastolic blood pressure", "pulse pressure measurement",
    "systolic blood pressure", "blood pressure trait",
    "blood pressure change measurement",
    "diastolic blood pressure change measurement",
]


def _slug(text):
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")


def saved_search(body):
    """Stands in for fetch._post_json: the saved search for these words."""
    words = body["variables"]["text"]
    if words == "pulmonary arterial hypertension":
        return load(GOLDEN / "disease_search.response.json")
    saved = SEARCHES / f"{_slug(words)}.response.json"
    assert saved.exists(), f"no saved search for {words!r}"
    return load(saved)


def gemini_names(words=None, text=None):
    """Stands in for translate._gemini_request: a saved answer, or this text."""
    if text is None:
        answer = load(ROOT / "fixtures" / "gemini" / f"names_{_slug(words)}.response.json")
    else:
        answer = {"candidates": [{"content": {"parts": [{"text": text}]}}]}

    def fake(method, path, body=None, timeout=None):
        if method == "GET":
            return 200, {"models": [{
                "name": "models/gemini-3.5-flash",
                "supportedGenerationMethods": ["generateContent"],
            }]}
        return 200, answer
    return fake


@contextlib.contextmanager
def search_world(gemini, open_targets=saved_search):
    translate.forget_everything()
    with patch("moonlight.fetch._post_json", side_effect=open_targets), \
            patch("moonlight.translate._gemini_request", side_effect=gemini):
        yield
    translate.forget_everything()


def search_json(client, words, gemini, **more):
    with search_world(gemini, **more):
        response = client.get("/api/search", params={"q": words})
    assert response.status_code == 200
    return response.json()


# ---- Example 1 ----
# Open Targets has no entry called "influenza". Its own entry for
# influenza is "Orthomyxoviridae infectious disease", and it is already
# the first match for "flu". Kashish, 2026-11-13: show Open Targets'
# "also called" word beside it, and do not repeat it in did_you_mean.

def test_flu_first_match_is_the_influenza_entry_with_its_small_print(client):
    data = search_json(client, "flu", gemini_names("flu"))
    assert data["matches"][0] == FLU_ENTRY
    assert data["also_called"][FLU_ENTRY["id"]] == "flu"


def test_flu_did_you_mean_holds_open_targets_entries_and_no_repeat(client):
    data = search_json(client, "flu", gemini_names("flu"))
    assert data["did_you_mean"] == [AVIAN, SWINE]
    assert FLU_ENTRY not in data["did_you_mean"]  # already the first match


def test_the_answer_has_three_parts_and_entries_are_id_and_name_only(client):
    data = search_json(client, "flu", gemini_names("flu"))
    assert set(data) == {"matches", "did_you_mean", "also_called"}
    for entry in data["matches"] + data["did_you_mean"]:
        assert set(entry) == {"id", "name"}
    shown = {entry["id"] for entry in data["matches"] + data["did_you_mean"]}
    assert set(data["also_called"]) <= shown


# ---- Example 2 ----

def test_diabaties_did_you_mean_holds_open_targets_entry_for_diabetes(client):
    data = search_json(client, "Diabaties", gemini_names("Diabaties"))
    assert data["matches"] == []
    assert data["did_you_mean"][0] == {"id": "MONDO_0005015", "name": "diabetes mellitus"}
    assert data["did_you_mean"][1] == {"id": "MONDO_0004782", "name": "diabetes insipidus"}


# ---- Example 3 ----

def test_high_blood_pressure_matches_hold_the_disease_and_no_measurement(client):
    data = search_json(client, "high blood pressure", gemini_names("high blood pressure"))
    names = [match["name"] for match in data["matches"]]
    assert names[0] == "hypertensive disorder"  # the page shows "Hypertensive disorder"
    for measurement in MEASUREMENT_NAMES:
        assert measurement not in names
    assert not [name for name in names if "measurement" in name or "trait" in name]
    assert data["also_called"]["MONDO_0005044"] == "high blood pressure"


def test_did_you_mean_never_holds_a_measurement(client):
    data = search_json(client, "high blood pressure", gemini_names("high blood pressure"))
    for entry in data["did_you_mean"]:
        assert entry["name"] not in MEASUREMENT_NAMES
    assert [entry["id"] for entry in data["did_you_mean"]] == ["MONDO_0001134", "MONDO_0001200"]


# ---- Example 4 ----

def test_a_disease_gemini_made_up_is_not_in_the_answer(client):
    made_up = gemini_names(text='["Zorblax fever", "Swine influenza"]')
    with search_world(made_up):
        response = client.get("/api/search", params={"q": "flu"})
    assert response.status_code == 200
    assert response.json()["did_you_mean"] == [SWINE]
    assert "zorblax" not in response.text.lower()


# ---- Example 5 ----

def test_gemini_unreachable_matches_still_come_back(client):
    def unreachable(method, path, body=None, timeout=None):
        raise requests.ConnectionError("no network")
    data = search_json(client, "flu", unreachable)
    assert data["matches"][0] == FLU_ENTRY and len(data["matches"]) == 10
    assert data["did_you_mean"] == []


def test_gemini_busy_matches_still_come_back(client):
    def busy(method, path, body=None, timeout=None):
        return 503, {"error": {"status": "UNAVAILABLE"}}
    data = search_json(client, "flu", busy)
    assert data["matches"][0] == FLU_ENTRY
    assert data["did_you_mean"] == []


def test_gemini_breaking_in_a_strange_way_shows_no_error(client):
    def broken(method, path, body=None, timeout=None):
        raise RuntimeError("something odd")
    data = search_json(client, "flu", broken)
    assert data["matches"][0] == FLU_ENTRY
    assert data["did_you_mean"] == []


def test_gemini_slow_matches_come_back_without_waiting_for_it(client):
    let_go = threading.Event()

    def slow(method, path, body=None, timeout=None):
        let_go.wait(10)
        raise requests.ConnectionError("too late")
    try:
        with patch("moonlight.api.DID_YOU_MEAN_SECONDS", 0.2):
            began = time.monotonic()
            data = search_json(client, "flu", slow)
            took = time.monotonic() - began
    finally:
        let_go.set()
    assert data["matches"][0] == FLU_ENTRY
    assert data["did_you_mean"] == []
    assert took < 5


def test_the_wait_is_three_seconds_for_gemini_and_a_little_for_looking_up():
    assert translate.GEMINI_SECONDS == 3
    assert translate.GEMINI_SECONDS < api.DID_YOU_MEAN_SECONDS <= 6


def test_open_targets_down_is_still_a_502_for_search(client):
    def down(body):
        raise requests.ConnectionError("down")
    with search_world(gemini_names("flu"), open_targets=down):
        response = client.get("/api/search", params={"q": "flu"})
    assert response.status_code == 502


# ---- Gemini and Open Targets run at the same time ----

def test_gemini_and_the_search_run_at_the_same_time(client):
    # Two runners who must both be on the track before either may go.
    # One after the other, the first would wait for ever and the gate breaks.
    gate = threading.Barrier(2, timeout=5)
    passed = []

    def gemini(method, path, body=None, timeout=None):
        if method == "POST":
            gate.wait()
            passed.append("gemini")
        return gemini_names("flu")(method, path, body, timeout)

    def open_targets(body):
        if body["variables"]["text"] == "flu" and "search" not in passed:
            gate.wait()
            passed.append("search")
        return saved_search(body)

    data = search_json(client, "flu", gemini, open_targets=open_targets)
    assert sorted(passed) == ["gemini", "search"]
    assert data["did_you_mean"] == [AVIAN, SWINE]


# ---- Example 6 ----

def test_pah_first_match_is_mondo_0015924_as_before(client):
    words = "pulmonary arterial hypertension"
    data = search_json(client, words, gemini_names(text=json.dumps([words])))
    assert data["matches"][0] == {"id": PAH_ID, "name": words}
    assert data["did_you_mean"] == []  # it is the first match already
    assert data["also_called"] == {}


def test_nothing_typed_asks_gemini_nothing(client):
    with patch("moonlight.translate.did_you_mean") as spy, \
            patch("moonlight.api.search_matches") as other:
        response = client.get("/api/search", params={"q": "   "})
    assert response.json() == {"matches": []}
    spy.assert_not_called()
    other.assert_not_called()


# ---- the page ----

def page_script(client):
    return re.search(r"(?s)<script>(.*?)</script>", client.get("/").text).group(1)


def test_did_you_mean_sits_above_the_matches_on_the_page(client):
    page = client.get("/").text
    assert 'data-slot="did-you-mean"' in page
    assert "Did you mean" in page
    assert page.index('data-slot="search"') < page.index('data-slot="did-you-mean"') \
        < page.index('data-slot="matches"')


def test_did_you_mean_is_hidden_until_there_is_a_suggestion(client):
    page = client.get("/").text
    tag = re.search(r'<[^>]*data-slot="did-you-mean"[^>]*>', page).group(0)
    assert " hidden" in tag


def test_a_new_search_removes_the_old_results_before_it_asks(client):
    script = page_script(client)
    search = script[script.index("async function search("):]
    assert "clearResults()" in search
    assert search.index("clearResults()") < search.index('ask("/api/search"')


def test_the_page_never_picks_a_disease_by_itself(client):
    # showClues is only ever called from a tap ("click") handler.
    script = page_script(client)
    calls = [m.start() for m in re.finditer(r"showClues\(", script)]
    # Its own definition, the quick-start chip, and choice(), the one
    # function that makes both the match buttons and the did-you-mean buttons.
    assert len(calls) == 4   # the fourth is the link
    for at in calls:
        before = script[:at]
        if before.endswith("async function "):
            continue
        last_tap = before.rfind('addEventListener("click"')
        from_a_tap = last_tap != -1 and "\n  }\n" not in before[last_tap:]
        from_a_link = before.endswith('if (linked.get("disease")) ')
        assert from_a_tap or from_a_link


# =====================================================================
# Ticket 5.3: three tabs, and approved medicines shown
# =====================================================================
#
# New tests only. Saved files, no network. The disease's own medicine list
# comes from fixtures/MONDO_0015924/disease_drugs.response.json.

APPROVED_14 = [
    "Ambrisentan", "Beraprost", "Bosentan", "Epoprostenol", "Iloprost",
    "Macitentan", "Nitric Oxide", "Riociguat", "Selexipag", "Sildenafil",
    "Sitaxentan", "Sotatercept", "Tadalafil", "Treprostinil",
]
DOCTOR_LINE = "Talk to your doctor before changing any medicine."
APPROVED_WORDS = (
    "Already approved for this disease in at least one country, according to "
    "the database. Nothing here says how well any of them works. Listed A to Z."
)
APPROVED_EMPTY = (
    "The database lists no approved medicine under this exact name. That "
    "does not mean there is none. Ask a doctor."
)
TRIALS_WORDS = (
    "Approved for another disease and now being tested for this one. A "
    "separate research category, not a prediction of effectiveness. Not "
    "every trial is listed. Only medicines that act on one of the proteins "
    "most linked to this disease."
)
CLUES_WORDS = (
    "Approved for another disease, with no recorded link to this one. "
    "Connections worth reading about, never treatments."
)
NO_PATH_WORDS = (
    "This medicine does not act on one of the 25 proteins most linked to "
    "this disease, so no path is shown."
)


def fake_with_the_disease_list(body):
    """fake_post_json, and also the saved "medicines for this disease" answer."""
    variables = body["variables"]
    if "diseaseId" in variables and "drugAndClinicalCandidates" in body["query"]:
        if variables["diseaseId"] != PAH_ID:
            return {"data": {"disease": None}}
        return load(GOLDEN / "disease_drugs.response.json")
    return fake_post_json(body)


@pytest.fixture
def disease_list():
    """The pretend Open Targets also holds the disease's own medicine list."""
    with patch("moonlight.fetch._post_json", side_effect=fake_with_the_disease_list):
        yield


def everything_the_api_says(client):
    """Every answer the API can give about PAH, as (what it is, text in capitals)."""
    said = [("page", client.get("/").text)]
    said.append(("search", client.get(
        "/api/search", params={"q": "pulmonary arterial hypertension"}).text))
    with with_saved_targets():
        clues = client.get("/api/clues", params={"disease_id": PAH_ID})
        assert clues.status_code == 200
        said.append(("clues", clues.text))
        with patch("moonlight.explain._gemini_request", side_effect=gemini_unreachable):
            for clue in clues.json()["new_clues"] + clues.json()["being_studied"]:
                api.forget_visitors()  # this test is not about the limit
                answer = client.get(
                    "/api/explain", params={"disease_id": PAH_ID, "clue_id": clue["id"]}
                )
                assert answer.status_code == 200
                said.append(("explain", answer.text))
    return [(what, text.upper()) for what, text in said]


# ---- Example 1 ----

def test_53_example_1_approved_holds_sildenafil_and_tadalafil_a_to_z_each_once(
        client, disease_list):
    data = clues_json(client, *FIVE)
    approved = [item["medicine"] for item in data["approved"]]
    assert approved.count("Sildenafil") == 1 and approved.count("Tadalafil") == 1
    assert approved == sorted(approved, key=str.casefold)
    assert approved == APPROVED_14
    assert len({item["id"] for item in data["approved"]}) == 14


def test_53_an_approved_item_has_its_facts_and_no_rank_explanation_or_ending(
        client, disease_list):
    data = clues_json(client, *FIVE)
    for item in data["approved"]:
        assert set(item) - {"proof_note"} == {"id", "medicine", "forms", "proteins", "reports", "source"}
        assert item["id"] and item["forms"]
        assert isinstance(item["reports"], int)
        assert item["source"] is None or item["source"].startswith("https://")
        for protein in item["proteins"]:
            assert set(protein) == {"symbol", "points", "direction", "machine", "piece_of_machine"}
            assert protein["direction"] in ("up", "down", "mixed", "unknown")
    assert ENDING.upper() not in json.dumps(data["approved"]).upper()
    assert "DO NOT TRY IT" not in json.dumps(data["approved"]).upper()


def test_53_sildenafil_carries_its_protein_points_direction_forms_and_source(
        client, disease_list):
    data = clues_json(client, *FIVE)
    sildenafil = clue_named(data["approved"], "Sildenafil")
    assert sildenafil["id"] == "CHEMBL192"
    assert sildenafil["forms"] == ["Sildenafil", "Sildenafil Citrate"]
    assert sildenafil["proteins"] == [{
        "symbol": "PDE5A", "points": 61, "direction": "down",
        "machine": 1, "piece_of_machine": False,
    }]
    assert sildenafil["reports"] > 0
    assert sildenafil["source"].startswith("https://")


def test_53_riociguat_is_one_item_with_three_pieces_of_one_machine(client, disease_list):
    data = clues_json(client, *GUCY1)
    riociguat = clue_named(data["approved"], "Riociguat")
    assert [p["symbol"] for p in riociguat["proteins"]] == list(GUCY1)
    assert [p["machine"] for p in riociguat["proteins"]] == [1, 1, 1]
    assert all(p["piece_of_machine"] for p in riociguat["proteins"])


def test_53_an_approved_medicine_is_in_no_other_list(client, disease_list):
    with with_saved_targets():
        data = client.get("/api/clues", params={"disease_id": PAH_ID}).json()
    approved = {item["id"] for item in data["approved"]}
    others = {clue["id"] for clue in data["new_clues"] + data["being_studied"]}
    assert len(approved) == 14 and others
    assert approved & others == set()


# ---- Example 2 ----

def test_53_example_2_new_clues_are_the_same_16_and_being_studied_the_same_2(
        client, disease_list):
    data = clues_json(client, *FIVE)
    assert [clue["medicine"] for clue in data["new_clues"]] == NEW_ORDER
    assert [clue["medicine"] for clue in data["being_studied"]] == ["Udenafil", "Vardenafil"]
    for clue in data["new_clues"] + data["being_studied"]:
        assert set(clue) == {
            "id", "medicine", "forms", "proteins", "reports", "source",
            "trial_phase", "ending",
        }


def test_53_the_answer_has_these_parts_in_this_order(client, disease_list):
    data = clues_json(client, *FIVE)
    assert list(data) == [
        "disease", "about_disease", "rule_text", "approved", "being_studied", "new_clues",
        "left_out",
    ]
    assert data["rule_text"] == RULE_TEXT


# ---- Example 3 ----

def test_53_example_3_no_response_names_a_medicine_that_is_not_approved_anywhere(
        client, disease_list):
    saved = [t for t in fetch.fetch_targets(PAH) if t.id in SAVED_IDS]
    tray = engine.find_clues(PAH, saved)
    hidden = set()
    for group in ("not_approved", "unclear_link"):
        for path in tray[group]:
            hidden.add(path.medicine.name.upper())
            hidden.update(form.name.upper() for form in path.medicine.forms)
    assert len(hidden) > 10
    said = everything_the_api_says(client)
    assert any("SILDENAFIL" in text for what, text in said)  # it really answered
    for what, text in said:
        assert [name for name in sorted(hidden) if name in text] == [], what


def test_53_approved_names_are_only_ever_in_the_clues_answer(client, disease_list):
    # Not on the page before a search, not in the search, not in any explanation.
    said = everything_the_api_says(client)
    assert sum(1 for what, text in said if what == "explain") >= 18
    for what, text in said:
        for name in APPROVED_14:
            assert (name.upper() in text) == (what == "clues"), (what, name)


# ---- Example 4 ----

def test_53_example_4_explain_for_sildenafil_is_still_refused(client, disease_list):
    data = clues_json(client, *FIVE)
    sildenafil = clue_named(data["approved"], "Sildenafil")
    gemini = CountingGemini()
    with with_targets(*FIVE), patch("moonlight.explain._gemini_request", side_effect=gemini):
        refused = [
            client.get("/api/explain", params={"disease_id": PAH_ID, "clue_id": clue_id})
            for clue_id in (sildenafil["id"], "CHEMBL1737")  # the medicine and its tablet form
        ]
    for answer in refused:
        assert answer.status_code == 404
        assert "SILDENAFIL" not in answer.text.upper()
    assert gemini.calls == 0  # Gemini was never asked about it


def test_53_no_approved_medicine_can_be_explained(client, disease_list):
    data = clues_json(client, *FIVE)
    gemini = CountingGemini()
    with with_targets(*FIVE), patch("moonlight.explain._gemini_request", side_effect=gemini):
        for item in data["approved"]:
            api.forget_visitors()  # this test is not about the limit
            answer = client.get(
                "/api/explain", params={"disease_id": PAH_ID, "clue_id": item["id"]})
            assert answer.status_code == 404, item["medicine"]
    assert gemini.calls == 0


def test_53_gemini_naming_a_medicine_from_the_approved_tab_is_thrown_away(client, disease_list):
    # Beraprost is only on the disease's own list. It is still a name
    # Moonlight met, so an explanation may not bring it up.
    data = clues_json(client, *FIVE)
    avanafil = clue_named(data["new_clues"], "Avanafil")
    sneaky = (
        "Avanafil is a medicine. Beraprost is a medicine too. "
        "It grabs a protein called PDE5A. A protein is a tiny machine in your body."
    )
    with with_targets(*FIVE), \
            patch("moonlight.explain._gemini_request", side_effect=gemini_says(sneaky)):
        answer = client.get(
            "/api/explain", params={"disease_id": PAH_ID, "clue_id": avanafil["id"]}
        )
    assert answer.status_code == 200
    assert answer.json()["source"] == "template"
    assert "BERAPROST" not in answer.text.upper()


# ---- Example 5 ----

def test_53_example_5_a_medicine_only_on_the_diseases_own_list_has_no_proteins(
        client, disease_list):
    with with_saved_targets():
        data = client.get("/api/clues", params={"disease_id": PAH_ID}).json()
    beraprost = clue_named(data["approved"], "Beraprost")
    assert beraprost["proteins"] == []
    assert beraprost["id"] == "CHEMBL1207745"
    assert beraprost["forms"] == ["Beraprost", "Beraprost Sodium"]
    assert beraprost["reports"] > 0
    assert beraprost["source"].startswith("https://")


def test_53_with_no_proteins_at_all_approved_is_still_the_diseases_own_list(
        client, disease_list):
    with patch("moonlight.api.fetch_targets", return_value=[]):
        data = client.get("/api/clues", params={"disease_id": PAH_ID}).json()
    assert [item["medicine"] for item in data["approved"]] == APPROVED_14
    assert all(item["proteins"] == [] for item in data["approved"])
    assert data["new_clues"] == [] and data["being_studied"] == []


def test_53_a_disease_with_nothing_approved_gives_an_empty_approved_list(client, disease_list):
    with patch("moonlight.api.fetch_targets", return_value=[]), \
            patch("moonlight.api.fetch_approved", return_value=[]):
        data = client.get("/api/clues", params={"disease_id": PAH_ID}).json()
    assert data["approved"] == []


# ---- Example 6 ----

def test_53_example_6_left_out_has_exactly_two_numbers(client, disease_list):
    data = clues_json(client, *FIVE)
    assert data["left_out"] == {"not_approved": 12, "unclear_link": 0}
    assert list(data["left_out"].values()) == [12, 0]


def test_53_open_targets_failing_on_the_disease_list_is_a_502_not_a_crash(client):
    def no_list(body):
        if "drugAndClinicalCandidates" in body["query"] and "diseaseId" in body["variables"]:
            raise requests.ConnectionError("down")
        return fake_post_json(body)
    with with_targets(*FIVE), patch("moonlight.fetch._post_json", side_effect=no_list):
        response = client.get("/api/clues", params={"disease_id": PAH_ID})
    assert response.status_code == 502
    assert "detail" in response.json()


# ---- Example 7: the page ----

def tag_of(page, slot):
    return re.search(r'<[^>]*data-slot="%s"[^>]*>' % slot, page).group(0)


def test_53_example_7_the_page_holds_the_tab_labels_the_doctor_line_and_the_safety_line(client):
    page = client.get("/").text
    assert SAFETY_LINE in page
    assert DOCTOR_LINE in page
    labels = re.findall(r'<button[^>]*role="tab"[^>]*>\s*([^<]+?)\s*<', page)
    assert labels == ["Approved", "In trials", "New clues"]


def test_53_the_words_under_each_tab_are_exact(client):
    page = client.get("/").text
    for words in (APPROVED_WORDS, DOCTOR_LINE, APPROVED_EMPTY, TRIALS_WORDS, CLUES_WORDS,
                  NO_PATH_WORDS, "Already being studied for this disease"):
        assert words in page, words
    # The doctor line is on its own line: an element of its own.
    assert re.search(r">\s*%s\s*<" % re.escape(DOCTOR_LINE), page)
    assert re.search(r">\s*%s\s*<" % re.escape(APPROVED_WORDS), page)


def test_53_the_tabs_are_one_row_under_the_disease_name_and_above_the_lists(client):
    page = client.get("/").text
    order = [page.index(mark) for mark in (
        'data-slot="safety-line"', 'id="disease-title"', 'data-slot="tabs"',
        'data-slot="approved"', 'data-slot="studied"', 'data-slot="new-clues"',
        'data-slot="left-out"',
    )]
    assert order == sorted(order)
    assert len(re.findall(r'<button[^>]*role="tab"', page)) == 3
    assert len(re.findall(r'<section[^>]*role="tabpanel"', page)) == 3
    assert len(re.findall(r'<div[^>]*role="tablist"', page)) == 1


def test_53_approved_opens_first_and_the_other_two_tabs_start_hidden(client):
    page = client.get("/").text
    assert " hidden" not in tag_of(page, "approved")
    assert " hidden" in tag_of(page, "studied")
    assert " hidden" in tag_of(page, "new-clues")
    tabs = re.findall(r'<button[^>]*role="tab"[^>]*>', page)
    assert ['aria-selected="true"' in tab for tab in tabs] == [True, False, False]
    script = page_script(client)
    assert 'const FIRST_TAB = "approved"' in script


def test_53_a_link_can_open_a_tab(client):
    script = page_script(client)
    assert 'get("disease")' in script and 'get("tab")' in script
    for name in ("approved", "trials", "clues"):
        assert 'data-tab="%s"' % name in client.get("/").text


def test_53_left_out_shows_two_numbers_on_the_page(client):
    page = client.get("/").text
    left_out = page[page.index('data-slot="left-out"'):]
    left_out = left_out[:left_out.index("</section>")]
    assert left_out.count('class="count"') == 2
    assert "Not approved anywhere" in left_out and "Unclear link" in left_out
    assert "Already approved for this disease" not in left_out


def test_53_approved_cards_get_no_number_no_explanation_and_no_ending(client):
    script = page_script(client)
    approved_card = script[script.index("function approvedCard("):]
    approved_card = approved_card[:approved_card.index("\n  }\n")]
    for gone in ('slot(el, "explanation").remove()', 'slot(el, "ending").remove()',
                 'slot(el, "rank").remove()'):
        assert gone in approved_card, gone
    assert "/api/explain" not in approved_card and "readExplanation" not in approved_card


def test_53_the_page_still_names_no_medicine_before_a_search(client):
    # Kashish's decision, 2026-11-15 (ticket 5.4): the guide shows one real
    # card, Doxapram. Outside the guide the page names no medicine. Inside
    # the guide the only medicine named is Doxapram, with its form.
    page = client.get("/").text
    guide = guide_of(page)
    assert page.count(guide) == 1
    outside = page.replace(guide, "").upper()
    for name in APPROVED_14 + NEW_ORDER + ["Udenafil", "Vardenafil"]:
        assert name.upper() not in outside, name
        if name != "Doxapram":
            assert name.upper() not in guide.upper(), name


# =====================================================================
# Ticket 5.4: the "How to use Moonlight" guide
# =====================================================================
#
# New tests only. They read the page from GET / and touch no network.

# Ticket 5.8: the guide is condensed. It has seven headings now. The parts
# for doctors and the sources are folded, with titles that are not headings.
GUIDE_HEADINGS = [
    "How to read what Moonlight finds.",
    "A medicine for one disease may act on a protein linked to another.",
    "Three steps",
    "The three tabs",
    "How to read a card",
    "What Moonlight can and cannot tell you",
    "Doctor, pharmacist or researcher?",
]
FOOTER_LINE = "Made with care by a family in Kochi"
FOOTER_NOTE = (
    "Moonlight · Research exploration only · Not clinical findings · "
    "Data from Open Targets"
)


def guide_of(page):
    """The guide's own piece of the page, from its opening tag to its end mark."""
    start = page.index('<section id="guide"')
    return page[start:page.index("<!-- end of the guide -->")]


def plain(html):
    """The words a reader sees: tags taken out, spaces tidied."""
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html)).strip()


def links_to_the_guide(page):
    """(where it opens the guide, the words of the link), in page order."""
    return re.findall(r'<a [^>]*href="#(guide[a-z-]*)"[^>]*data-guide[^>]*>([^<]+)</a>', page)


# ---- Example 1 ----

# This test used to be
# test_54_example_1_the_page_holds_the_guides_ten_headings_and_the_safety_line.
def test_54_example_1_the_page_holds_the_guides_seven_headings_and_the_safety_line(client):
    page = client.get("/").text
    assert SAFETY_LINE in page
    guide = guide_of(page)
    headings = [plain(h) for h in re.findall(r"(?s)<h[12][^>]*>(.*?)</h[12]>", guide)]
    assert headings == GUIDE_HEADINGS
    assert len(headings) == 7


def test_54_the_guide_is_inside_the_page_and_hidden_until_opened(client):
    page = client.get("/").text
    tag = re.search(r'<section id="guide"[^>]*>', page).group(0)
    assert " hidden" in tag
    # Under the header and the pinned safety line, which are not copied again.
    assert page.index('class="site-header"') < page.index('data-slot="safety-line"') \
        < page.index('<section id="guide"')
    assert page.count(SAFETY_LINE) == 1
    assert page.count('class="site-header"') == 1


def test_54_back_to_search_closes_the_guide(client):
    guide = guide_of(client.get("/").text)
    assert re.search(r'<a [^>]*href="#home"[^>]*data-guide-close[^>]*>Back to search</a>', guide)
    script = page_script(client)
    assert "function closeGuide(" in script and "function openGuide(" in script


def test_54_the_sentence_about_the_data_release_is_not_copied(client):
    page = client.get("/").text
    assert "which release of the data" not in page
    assert "Open Targets Platform, a free and open research database." in page


# ---- Example 2 ----

def test_54_example_2_no_http_link_to_any_outside_font_script_or_stylesheet(client):
    page = without_the_umami_script(client.get("/").text)
    assert "http" not in page.lower()
    assert "<link" not in page.lower()
    assert "@import" not in page
    assert not re.search(r"<script[^>]+src", page, flags=re.IGNORECASE)
    assert "fonts.googleapis" not in page and "gstatic" not in page
    # Anything the styles fetch is held inside the page itself.
    addresses = re.findall(r"url\(\s*[\"']?([^\"')]{0,12})", page)
    assert all(address.startswith("data:") for address in addresses), addresses


# Kashish changed her mind on 2026-11-16 (ticket 8.3). This test used to be
# test_54_no_visitor_counter_on_the_page.
def test_54_the_only_visit_counter_is_umami(client):
    page = without_the_umami_script(client.get("/").text)
    seen = words_people_can_see(page).lower()
    assert "visitor" not in seen and "counter" not in seen
    assert seen.count("counted with umami") == 1


# ---- Example 3 ----

# Sidha's design decision, 2026-11-16 (ticket 5.8): the footer line "Made with
# care by a family in Kochi" is removed. This test used to be
# test_54_example_3_the_page_holds_the_two_links_to_the_guide_and_the_footer_line.
def test_54_example_3_the_page_holds_the_two_links_to_the_guide_and_not_the_footer_line(client):
    page = client.get("/").text
    assert links_to_the_guide(page) == [
        ("guide", "How to use Moonlight."),
        ("guide-card", "How to read a card"),
    ]
    assert FOOTER_LINE not in page


def test_54_the_small_line_is_under_the_search_box(client):
    page = client.get("/").text
    home = page[page.index('<section id="home"'):page.index('<section id="results"')]
    assert "New here? How to use Moonlight." in plain(home)
    assert home.index('class="search-box"') < home.index("New here?") \
        < home.index('data-slot="matches"')


def test_54_how_to_read_a_card_is_beside_the_tabs_and_opens_at_the_card_and_its_key(client):
    page = client.get("/").text
    at = page.index(">How to read a card</a>")
    assert page.index('data-slot="tabs"') < at < page.index('data-slot="approved"')
    guide = guide_of(page)
    card_part = guide[guide.index('id="guide-card"'):]
    assert card_part.index("How to read a card") < card_part.index('<article class="card"') \
        < card_part.index('<ul class="key"')


# Ticket 5.8: the handwritten line and its heart are removed. This test used to be
# test_54_the_footer_has_the_contact_line_the_handwritten_line_and_its_note.
def test_54_the_footer_has_the_contact_line_and_its_note_and_no_handwritten_line(client):
    page = client.get("/").text
    footer = page[page.index("<footer"):page.index("</footer>")]
    assert "About Us" not in page
    assert not re.search(r'<a [^>]*data-guide[^>]*>', footer)
    assert ("Found something wrong or have any feedback? Contact "
            '<a href="mailto:hello@moonlightclues.com">hello@moonlightclues.com</a>') in footer
    assert FOOTER_LINE not in footer
    assert 'class="made"' not in footer and "<svg" not in footer  # the small heart
    assert footer.index("Found something wrong") < footer.index(FOOTER_NOTE)


def test_54_a_link_can_open_the_guide(client):
    script = page_script(client)
    assert 'linked.get("guide") === "1"' in script


# ---- Example 4 ----

# Ticket 5.8: the guide is condensed and its "Do not use it to" box is
# removed. The same words stay on every page, in the pinned safety line.
# This test used to be
# test_54_example_4_the_do_not_use_it_to_list_holds_start_stop_or_change_any_medicine.
def test_54_example_4_the_do_not_use_it_to_list_is_removed_and_the_safety_line_says_it(client):
    page = client.get("/").text
    guide = guide_of(page)
    assert "Do not use it to" not in guide
    assert "Never start, stop or change any medicine without a doctor." in page
    assert SAFETY_LINE not in guide  # it is pinned above the guide, not copied into it


# ---- Rules 5 and 6 for copying the draft ----

def test_54_the_example_card_is_doxapram_with_the_facts_checked_live(client):
    # Checked against the live API on 2026-11-15: sixth new clue for
    # pulmonary arterial hypertension, 8 reports, KCNK3 turned down, 79 points.
    guide = guide_of(client.get("/").text)
    card = guide[guide.index('<article class="card"'):guide.index("</article>")]
    words = plain(card)
    assert re.search(r'class="rank"[^>]*>6<', card)
    assert "Forms: Doxapram, Doxapram Hydrochloride" in words
    assert "8 reports" in words
    assert "Doxapram → KCNK3 → Pulmonary arterial hypertension" in words
    assert "Down" in words and "79 / 100 points" in words
    assert "The data does not say which direction this disease needs." in words
    assert ENDING in words


def test_54_the_example_cards_facts_match_the_saved_answer(client):
    data = clues_json(client, *FIVE)
    doxapram = clue_named(data["new_clues"], "Doxapram")
    assert NEW_ORDER.index("Doxapram") + 1 == 6
    assert doxapram["forms"] == ["Doxapram", "Doxapram Hydrochloride"]
    assert doxapram["reports"] == 8
    assert doxapram["proteins"] == [{
        "symbol": "KCNK3", "points": 79, "direction": "down",
        "machine": 1, "piece_of_machine": False,
    }]
    assert doxapram["ending"] == ENDING


# Ticket 5.8: the guide is condensed. Each tile holds a short line of its
# own, no longer the first sentence under the real tab. This test used to be
# test_54_the_words_under_the_three_tabs_say_what_the_real_tabs_say.
def test_54_the_three_tiles_are_named_after_the_real_tabs(client):
    page = client.get("/").text
    guide = guide_of(page)
    for words in (APPROVED_WORDS, TRIALS_WORDS, CLUES_WORDS):
        first = words.split(". ")[0] + "."
        assert page.count(first) == 1  # under the real tab only
    names = re.findall(r'<div class="tab-note"><h3>([^<]+)</h3>', guide)
    assert names == ["Approved", "In trials", "New clues"]
    assert "Not a prediction." in guide  # in trials: never hinted to be more likely to work


# Ticket 5.8: the guide is condensed. The long key is replaced by eight
# chips, a gold letter and a few words each, so Kashish's four corrected
# sentences of 2026-11-15 are no longer in it. The four wrong sentences of
# the draft must still never come back. This test used to be
# test_54_the_four_corrected_sentences_are_in_the_guides_key.
def test_54_the_guides_key_is_chips_and_the_four_wrong_sentences_stay_out(client):
    guide = guide_of(client.get("/").text)
    key = guide[guide.index('<ul class="key"'):]
    key = key[:key.index("</ul>")]
    for letter, words in (("C", "The path, in three steps"), ("D", "Up, down or unknown"),
                          ("F", "The clue in plain words"), ("G", "The catch, on every clue")):
        assert '>%s</span><span>%s</span>' % (letter, words) in key, letter
    for old in ("If any step is missing", "The same on every card",
                "a word Moonlight does not recognise", "Nothing is added that is not on the card"):
        assert old not in guide, old


# =====================================================================
# Ticket 2.11: withdrawn, mixed answers
# =====================================================================
#
# New tests only. Saved files, no network. The protein answers are the ones
# saved on 15 Nov WITH the withdrawn note. The disease's own list is the
# one saved on 10 Nov with NO note, and it names Sitaxentan as approved.

NOTED = ROOT / "fixtures" / "withdrawn" / "MONDO_0015924"
SITAXENTAN_ID = "CHEMBL282724"  # read from the saved files


def mixed_post_json(body):
    variables = body["variables"]
    if "targetId" in variables:
        (file,) = (NOTED / "target_drugs").glob(f"*_{variables['targetId']}.response.json")
        return load(file)
    return fake_with_the_disease_list(body)


def test_211_mixed_answers_no_response_names_sitaxentan(client):
    old_list = load(GOLDEN / "disease_drugs.response.json")
    assert "drugWarnings" not in json.dumps(old_list)  # the list has no note
    assert "SITAXENTAN" in json.dumps(old_list)

    with patch("moonlight.fetch._post_json", side_effect=mixed_post_json), \
            with_targets(*FIVE), \
            patch("moonlight.explain._gemini_request", side_effect=gemini_unreachable):
        clues = client.get("/api/clues", params={"disease_id": PAH_ID})
        assert clues.status_code == 200
        data = clues.json()
        gone = client.get(
            "/api/explain", params={"disease_id": PAH_ID, "clue_id": SITAXENTAN_ID})

    assert "SITAXENTAN" not in clues.text.upper()
    assert gone.status_code == 404 and "SITAXENTAN" not in gone.text.upper()
    assert SITAXENTAN_ID not in {item["id"] for item in data["approved"]}
    assert len(data["approved"]) == 13
    assert "Sildenafil" in [item["medicine"] for item in data["approved"]]  # it really answered
    assert len(data["new_clues"]) == 16 and len(data["being_studied"]) == 2
    assert data["left_out"] == {"not_approved": 13, "unclear_link": 0}


# ---- Ticket 2.11, the other half: the LIST says "withdrawn" ----

def list_noted_post_json(body):
    """The disease's own list saved on 15 Nov WITH the withdrawn note, and
    the protein answers saved on 10 Nov with NO note."""
    if "diseaseId" in body["variables"] and "drugAndClinicalCandidates" in body["query"]:
        return load(NOTED / "disease_drugs.response.json")
    return fake_post_json(body)


def all_noted_post_json(body):
    """Every "which medicines?" answer WITH the withdrawn note."""
    if "targetId" in body["variables"]:
        return mixed_post_json(body)
    return list_noted_post_json(body)


def clues_with(client, fake, *symbols):
    with patch("moonlight.fetch._post_json", side_effect=fake), with_targets(*symbols):
        clues = client.get("/api/clues", params={"disease_id": PAH_ID})
        gone = client.get(
            "/api/explain", params={"disease_id": PAH_ID, "clue_id": SITAXENTAN_ID})
    assert clues.status_code == 200
    assert "SITAXENTAN" not in clues.text.upper()
    assert gone.status_code == 404 and "SITAXENTAN" not in gone.text.upper()
    data = clues.json()
    assert "Sildenafil" in [item["medicine"] for item in data["approved"]]  # it really answered
    return data


def test_211_case_1_withdrawn_only_on_the_list_is_not_named_and_is_counted(client):
    # Only PDE5A is looked at, so Sitaxentan (EDNRA) is only on the list.
    data = clues_with(client, all_noted_post_json, "PDE5A")
    assert len(data["approved"]) == 13
    assert data["left_out"] == {"not_approved": 4, "unclear_link": 0}  # PDE5A's 3 and Sitaxentan


def test_211_case_2_the_list_says_withdrawn_and_the_protein_answer_has_no_note(client):
    data = clues_with(client, list_noted_post_json, *FIVE)
    assert len(data["approved"]) == 13
    assert len(data["new_clues"]) == 16 and len(data["being_studied"]) == 2
    assert data["left_out"] == {"not_approved": 13, "unclear_link": 0}


# ---------------------------------------------------------------------------
# Ticket 8.2: cost guard and privacy
# ---------------------------------------------------------------------------
# New tests only. Saved files, no network, and no sleeping: the clock is
# api._now, and every test here sets it by hand.
#
# A visitor is told apart by their address. On Cloud Run the address
# arrives in the X-Forwarded-For header, and the LAST entry is the one
# Google's front door wrote. Anything before it was sent by the visitor
# and can be made up. The addresses below are from the ranges kept for
# examples (RFC 5737), so they belong to nobody.

TOO_MANY = "Too many requests. Please wait a minute."
# Ticket 5.8: the guide is condensed. This is the line as it is now, in
# the folded part "Where the facts come from".
GUIDE_LINE = (
    "Explanations come from Google’s Gemini or Moonlight’s own template. "
    "What you type is sent to Gemini, so type no names or private details."
)
TOO_LONG = "That search is too long. Please use 100 letters or fewer."
VISITOR_A = {"X-Forwarded-For": "203.0.113.7"}
VISITOR_B = {"X-Forwarded-For": "198.51.100.23"}


@pytest.fixture(autouse=True)
def nobody_has_visited_yet():
    """Every test starts and ends with the visitor counters at zero."""
    api.forget_visitors()
    yield
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


def one_search(client, visitor, words="flu"):
    with search_world(gemini_names("flu")):
        return client.get("/api/search", params={"q": words}, headers=visitor)


def one_explain(client, visitor, clue_id):
    with with_targets("KCNK3"), \
            patch("moonlight.explain._gemini_request", side_effect=gemini_unreachable):
        return client.get(
            "/api/explain", params={"disease_id": PAH_ID, "clue_id": clue_id}, headers=visitor
        )


# ---- Example 1: 10 a minute, the 11th is 429, then the minute passes ----

def test_82_example_1_sixty_searches_are_answered_the_61st_is_429_then_the_minute_passes(
        client, clock):
    for _ in range(60):
        clock.now += 0.5  # sixty searches inside 30 seconds
        assert one_search(client, VISITOR_A).status_code == 200
    clock.now += 5
    refused = one_search(client, VISITOR_A)
    assert refused.status_code == 429
    assert refused.json() == {"detail": TOO_MANY}
    clock.now += 60  # the minute has passed
    assert one_search(client, VISITOR_A).status_code == 200


def test_82_a_refused_search_asks_open_targets_and_gemini_nothing(client, clock):
    for _ in range(60):
        one_search(client, VISITOR_A)
    with patch("moonlight.fetch._post_json") as open_targets, \
            patch("moonlight.translate._gemini_request") as gemini:
        assert client.get("/api/search", params={"q": "flu"}, headers=VISITOR_A).status_code == 429
    open_targets.assert_not_called()
    gemini.assert_not_called()


def test_82_the_limit_is_60_in_any_60_seconds(client, clock):
    assert api.MAX_A_MINUTE == {"search": 60, "explain": 30}
    assert api.MINUTE_SECONDS == 60
    for _ in range(60):
        assert one_search(client, VISITOR_A).status_code == 200
    clock.now += 59.9
    assert one_search(client, VISITOR_A).status_code == 429
    clock.now += 0.1
    assert one_search(client, VISITOR_A).status_code == 200


def test_82_a_refused_request_does_not_make_the_wait_longer(client, clock):
    for _ in range(60):
        one_search(client, VISITOR_A)
    for _ in range(20):
        clock.now += 2
        assert one_search(client, VISITOR_A).status_code == 429
    clock.now += 20  # 60 seconds after the sixty that were answered
    assert one_search(client, VISITOR_A).status_code == 200


# ---- Example 2: visitor A is over the limit, visitor B is still answered ----

def test_82_example_2_visitor_b_is_answered_while_visitor_a_is_over_the_limit(client, clock):
    for _ in range(60):
        one_search(client, VISITOR_A)
    assert one_search(client, VISITOR_A).status_code == 429
    assert one_search(client, VISITOR_B).status_code == 200


def test_82_the_visitor_is_the_last_address_in_the_forwarding_header(client, clock):
    # The entries before the last one are whatever the visitor sent, so a
    # visitor who makes up a new one each time is still the same visitor.
    for number in range(60):
        made_up = {"X-Forwarded-For": f"192.0.2.{number}, 203.0.113.7"}
        assert one_search(client, made_up).status_code == 200
    assert one_search(client, {"X-Forwarded-For": "192.0.2.99, 203.0.113.7"}).status_code == 429
    # And two visitors who send the same made-up entry are still two visitors.
    assert one_search(client, {"X-Forwarded-For": "192.0.2.99, 198.51.100.23"}).status_code == 200


def test_82_with_no_forwarding_header_the_visitor_is_the_direct_caller(client, clock):
    # Running on a laptop: nothing sits in front, so there is no header.
    for _ in range(60):
        assert one_search(client, {}).status_code == 200
    assert one_search(client, {}).status_code == 429
    assert one_search(client, VISITOR_B).status_code == 200


# ---- Example 3: 10 searches do not use up the 30 explanations ----
# Kashish, 2026-11-16: explanations are 30 a minute, searches stay at 10.

def test_82_example_3_sixty_searches_do_not_use_up_the_thirty_explanations(client, clock):
    clue_id = clue_named(clues_json(client, "KCNK3")["new_clues"], "Sevoflurane")["id"]
    for _ in range(60):
        assert one_search(client, VISITOR_A).status_code == 200
    assert one_search(client, VISITOR_A).status_code == 429
    for _ in range(30):
        assert one_explain(client, VISITOR_A, clue_id).status_code == 200
    refused = one_explain(client, VISITOR_A, clue_id)  # the 31st
    assert refused.status_code == 429
    assert refused.json() == {"detail": TOO_MANY}
    assert one_explain(client, VISITOR_B, clue_id).status_code == 200
    clock.now += 60
    assert one_explain(client, VISITOR_A, clue_id).status_code == 200


def test_82_thirty_explanations_do_not_use_up_the_sixty_searches(client, clock):
    clue_id = clue_named(clues_json(client, "KCNK3")["new_clues"], "Sevoflurane")["id"]
    for _ in range(30):
        assert one_explain(client, VISITOR_A, clue_id).status_code == 200
    assert one_explain(client, VISITOR_A, clue_id).status_code == 429
    for _ in range(60):
        assert one_search(client, VISITOR_A).status_code == 200
    assert one_search(client, VISITOR_A).status_code == 429


def test_82_a_refused_explanation_is_not_the_template_and_asks_nothing(client, clock):
    clue_id = clue_named(clues_json(client, "KCNK3")["new_clues"], "Sevoflurane")["id"]
    for _ in range(30):
        one_explain(client, VISITOR_A, clue_id)
    with patch("moonlight.fetch._post_json") as open_targets, \
            patch("moonlight.explain._gemini_request") as gemini, \
            patch("moonlight.api.explain.explain") as explainer:
        refused = client.get(
            "/api/explain", params={"disease_id": PAH_ID, "clue_id": clue_id}, headers=VISITOR_A
        )
    assert refused.status_code == 429
    assert set(refused.json()) == {"detail"}  # no text, no "template"
    open_targets.assert_not_called()
    gemini.assert_not_called()
    explainer.assert_not_called()


def test_82_looking_at_the_clues_is_not_counted(client, clock):
    # The ticket limits /api/search and /api/explain. Nothing else.
    for _ in range(12):
        with with_targets("KCNK3"):
            answer = client.get("/api/clues", params={"disease_id": PAH_ID}, headers=VISITOR_A)
        assert answer.status_code == 200
    assert one_search(client, VISITOR_A).status_code == 200


# ---- Example 4: 100 characters is answered, 101 is refused ----

def test_82_example_4_a_search_of_100_characters_is_answered(client, clock):
    words = "a" * 100
    with patch("moonlight.api.search_diseases", return_value=[]) as asked, \
            patch("moonlight.api.search_matches", return_value=[]), \
            patch("moonlight.api.translate.did_you_mean", return_value=[]):
        answer = client.get("/api/search", params={"q": words}, headers=VISITOR_A)
    assert answer.status_code == 200
    assert answer.json() == {"matches": [], "did_you_mean": [], "also_called": {}}
    asked.assert_called_once_with(words)


def test_82_example_4_a_search_of_101_characters_is_refused_and_nothing_is_called(client, clock):
    assert api.MAX_SEARCH_LETTERS == 100
    with patch("moonlight.fetch._post_json") as open_targets, \
            patch("moonlight.translate._gemini_request") as translate_gemini, \
            patch("moonlight.explain._gemini_request") as explain_gemini, \
            patch("moonlight.api.search_diseases") as search_door, \
            patch("moonlight.api.search_matches") as matches_door, \
            patch("moonlight.api.translate.did_you_mean") as guess_door:
        answer = client.get("/api/search", params={"q": "a" * 101}, headers=VISITOR_A)
    assert answer.status_code == 400
    assert answer.json() == {"detail": TOO_LONG}
    for door in (open_targets, translate_gemini, explain_gemini,
                 search_door, matches_door, guess_door):
        door.assert_not_called()


def test_82_spaces_around_the_words_do_not_get_a_long_search_through(client, clock):
    with patch("moonlight.fetch._post_json") as open_targets, \
            patch("moonlight.translate._gemini_request") as gemini:
        answer = client.get("/api/search", params={"q": " " + "a" * 101 + " "}, headers=VISITOR_A)
    assert answer.status_code == 400
    open_targets.assert_not_called()
    gemini.assert_not_called()


def test_82_the_search_box_stops_at_100(client):
    box = re.search(r'<input id="disease-search"[^>]*>', client.get("/").text).group(0)
    assert 'maxlength="100"' in box


# ---- the page says the exact words ----

def test_82_the_page_shows_the_too_many_requests_words_exactly(client):
    script = page_script(client)
    assert script.count('"' + TOO_MANY + '"') == 1  # written once, used for both
    assert "429" in script


def test_82_the_page_does_not_show_the_template_explanation_for_too_many_requests(client):
    page = client.get("/").text
    block = re.search(r'(?s)<template id="explanation-too-many">(.*?)</template>', page).group(1)
    # The words are filled in by the script, and nothing here is the
    # code-written explanation.
    assert 'data-part="message"' in block
    assert "template" not in plain(block).lower()
    read = re.search(r"(?s)async function readExplanation\(.*?\n  }\n", page_script(client)).group(0)
    assert read.index("429") < read.index("explanation-failed")
    assert "explanation-too-many" in read


# ---- Example 6: the guide line ----

def test_82_example_6_the_page_holds_the_guide_line_inside_the_guide(client):
    page = client.get("/").text
    assert plain(page).count(GUIDE_LINE) == 1
    assert GUIDE_LINE in plain(guide_of(page))


# Ticket 5.8: the lines are list items in a folded part now. This test used
# to be test_82_the_guide_line_is_right_after_the_open_targets_paragraph.
def test_82_the_guide_line_is_right_after_the_open_targets_line(client):
    guide = guide_of(client.get("/").text)
    lines = [plain(line) for line in re.findall(r"(?s)<li>.*?</li>", guide)]
    place = lines.index("Words. " + GUIDE_LINE)
    assert lines[place - 1] == "Facts. Open Targets Platform, a free and open research database."


def test_82_the_safety_line_is_unchanged(client):
    assert SAFETY_LINE in client.get("/").text


# ---- nothing about a visitor is written down ----

def test_82_the_api_never_logs_or_prints():
    source = (ROOT / "moonlight" / "api.py").read_text(encoding="utf-8")
    assert "logging" not in source
    assert not re.search(r"(?<![\w.])print\(", source)


def test_82_addresses_are_forgotten_after_the_minute(client, clock):
    one_search(client, VISITOR_A)
    one_search(client, VISITOR_B)
    assert api.visitors_remembered() == 2
    clock.now += 61
    one_search(client, VISITOR_B)  # anyone's next visit sweeps the old ones out
    assert api.visitors_remembered() == 1
