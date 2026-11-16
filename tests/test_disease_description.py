"""Ticket 5.5. The disease in Open Targets' own words.

Each EXAMPLE in the ticket is a test here. Saved files only, no network:
fetch._post_json and explain._gemini_request are swapped for fakes, and any
real HTTP call is an error.

The saved answers were read from the live API on 2026-11-16 with the exact
question in fixtures/<id>/disease_about.request.json:

    MONDO_0015924  pulmonary arterial hypertension: a long description
    MONDO_0100338  urinary tract infection: Open Targets sends no description
"""

import json
import pathlib
import re
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from moonlight import api, cache, explain, fetch
from moonlight.filter import NEW_CLUE, sort_paths
from moonlight.rank import rank_clues
from moonlight.records import Disease

FIXTURES = pathlib.Path(__file__).resolve().parent.parent / "fixtures"
GOLDEN = FIXTURES / "MONDO_0015924"
PAH_ID = "MONDO_0015924"
UTI_ID = "MONDO_0100338"  # Open Targets has no description for this one
VERSION = "26.09"

# Word for word from earlier tickets. This ticket must not change them.
KASHISH_EXAMPLE = (
    "Sevoflurane is a medicine. Doctors already use it for something else. "
    "It grabs a protein called KCNK3. A protein is a tiny machine in your "
    "body. Sevoflurane turns KCNK3 up, like a volume knob. KCNK3 is linked to "
    "pulmonary arterial hypertension. That is high blood pressure in the "
    "arteries of the lungs. An artery is like a pipe for blood. The link "
    "score is 0.79. That is like 79 points out of 100. Sevoflurane has no "
    "link to this disease in the database. The database is a huge web with "
    "lots of information."
)
ENDING = (
    "But there is a catch. Nobody knows from our information if the "
    "disease needs this protein turned up or down. So this is a clue to "
    "read about. It is not a treatment. Do not try it."
)
SAFETY_LINE = (
    "For learning and research exploration, not medical advice. "
    "Never start, stop or change any medicine without a doctor."
)
STAYS = (
    "What open research data says about medicines and this disease. "
    "Nothing here is medical advice."
)
SOURCE_LINE = "Source: Open Targets"


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def saved_about(disease_id):
    return load(FIXTURES / disease_id / "disease_about.response.json")["data"]["disease"]


def exact_names(disease_id):
    """Open Targets' exact "also called" names in the saved answer, in its order."""
    names = []
    for group in saved_about(disease_id)["synonyms"]:
        if group["relation"] == "hasExactSynonym":
            names.extend(group["terms"])
    return names


PAH_DESCRIPTION = saved_about(PAH_ID)["description"]


def fake_post_json(body):
    """Stands in for fetch._post_json: picks the saved response for a request."""
    assert set(body) == {"query", "variables"}
    query, variables = body["query"], body["variables"]
    if "targetId" in variables:
        matches = list(
            (GOLDEN / "target_drugs").glob(f"*_{variables['targetId']}.response.json")
        )
        assert len(matches) == 1, f"no saved file for target {variables['targetId']}"
        return load(matches[0])
    if "associatedTargets" in query:
        assert variables["diseaseId"] == PAH_ID
        return load(GOLDEN / "associated_targets.response.json")
    if "drugAndClinicalCandidates" in query:
        assert variables["diseaseId"] == PAH_ID
        return load(GOLDEN / "disease_drugs.response.json")
    if "parents" in query:
        # Ticket 2.12: the family question. No parents, no children.
        return {"data": {"disease": {
            "id": variables["diseaseId"], "name": "", "parents": [], "children": []}}}
    # The disease record. The question must be the one that was saved.
    folder = FIXTURES / variables["diseaseId"]
    assert body == load(folder / "disease_about.request.json")
    return load(folder / "disease_about.response.json")


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


@pytest.fixture
def pah():
    return fetch.fetch_disease(PAH_ID)


@pytest.fixture
def sevoflurane(pah):
    targets = [t for t in fetch.fetch_targets(pah) if t.symbol == "KCNK3"]
    paths = [p for t in targets for p in fetch.fetch_paths(pah, t)]
    clues = {clue.medicine.name: clue for clue in rank_clues(sort_paths(paths)[NEW_CLUE])}
    return clues["SEVOFLURANE"]


class FakeGemini:
    """Stands in for explain._gemini_request. Remembers every prompt."""

    def __init__(self, text=None):
        self.text = text  # None: Gemini is busy every time
        self.prompts = []

    def __call__(self, method, path, body=None, timeout=None):
        if method == "GET":
            return 200, {"models": [{
                "name": "models/gemini-3.5-flash",
                "supportedGenerationMethods": ["generateContent"],
            }]}
        self.prompts.append(body["contents"][0]["parts"][0]["text"])
        if self.text is None:
            return 503, {"error": {"code": 503, "status": "UNAVAILABLE"}}
        return 200, {"candidates": [{"content": {"parts": [{"text": self.text}]}}]}


def use(fake):
    return patch("moonlight.explain._gemini_request", side_effect=fake)


# ---- the saved answers really are what the code asks for ----

def test_the_saved_question_is_the_question_fetch_asks():
    for disease_id in (PAH_ID, UTI_ID):
        asked = load(FIXTURES / disease_id / "disease_about.request.json")
        assert asked == {"query": fetch.DISEASE_QUERY, "variables": {"diseaseId": disease_id}}


def test_the_field_names_are_in_the_saved_live_answer():
    record = saved_about(PAH_ID)
    assert set(record) == {"id", "name", "description", "synonyms"}
    for group in record["synonyms"]:
        assert set(group) == {"relation", "terms"}
    assert "hasExactSynonym" in [group["relation"] for group in record["synonyms"]]


# ---- fetch: the record keeps Open Targets' own words ----

def test_fetch_disease_keeps_the_description_word_for_word(pah):
    assert pah.description == PAH_DESCRIPTION
    assert pah.description.startswith("Pulmonary arterial hypertension (PAH) is a group of")
    assert pah.description.endswith("(PAH associated with other disease).")


def test_fetch_disease_keeps_the_exact_also_called_names(pah):
    assert list(pah.also_called) == exact_names(PAH_ID)
    assert pah.also_called[:3] == ("PAH", "pulmonary arterial hypertension",
                                   "Ayerza Arrilaga Syndrome")
    # Names from the other groups (related, narrow, broad) are not "exact".
    assert "PPH" not in pah.also_called
    assert "PVOD/PCH" not in pah.also_called


def test_a_disease_with_no_description_keeps_none_and_still_has_its_names():
    assert saved_about(UTI_ID)["description"] is None
    disease = fetch.fetch_disease(UTI_ID)
    assert disease.name == "urinary tract infection"
    assert disease.description == ""
    assert disease.also_called == (
        "urinary tract infection (disease)",
        "INFECTION, URINARY TRACT",
        "TRACT, INFECTION OF URINARY",
    )


def test_an_older_saved_answer_with_no_synonyms_has_no_also_called_names():
    older = load(GOLDEN / "disease_description.response.json")
    assert "synonyms" not in older["data"]["disease"]
    with patch("moonlight.fetch._post_json", side_effect=lambda body: older):
        disease = fetch.fetch_disease(PAH_ID)
    assert disease.also_called == ()
    assert disease.description == PAH_DESCRIPTION


def test_a_disease_record_has_no_also_called_names_by_default():
    assert Disease(id="D1", name="d").also_called == ()
    assert Disease(id="D1", name="d", also_called=["a", "b"]).also_called == ("a", "b")


# ---- EXAMPLE 1: /api/clues carries the description, word for word ----

def clues_for(client, disease_id):
    """The /api/clues answer. Only the disease record is being tested, so the
    proteins and the disease's own medicine list are left empty."""
    with patch("moonlight.api.fetch_targets", return_value=[]), \
            patch("moonlight.api.fetch_approved", return_value=[]), \
            patch("moonlight.api.fetch_withdrawn", return_value=[]):
        response = client.get("/api/clues", params={"disease_id": disease_id})
    assert response.status_code == 200
    return response.json()


def test_api_clues_carries_the_pah_description_word_for_word(client):
    about = clues_for(client, PAH_ID)["about_disease"]
    assert about["description"] == PAH_DESCRIPTION
    assert about["source"] == "Open Targets"


def test_api_clues_carries_the_exact_also_called_names(client):
    data = clues_for(client, PAH_ID)
    # Every exact name, as Open Targets spells it and in its order. The
    # disease's own name is not repeated as an "also called" name.
    wanted = [name for name in exact_names(PAH_ID) if name != "pulmonary arterial hypertension"]
    assert data["about_disease"]["also_called"] == wanted
    assert len(wanted) == 17
    assert "pulmonary arterial hypertension" not in data["about_disease"]["also_called"]


def test_api_clues_still_sends_the_disease_as_before(client):
    data = clues_for(client, PAH_ID)
    assert data["disease"] == {"id": PAH_ID, "name": "pulmonary arterial hypertension"}


# ---- EXAMPLE 2: no description, so no description and no source ----

def test_api_clues_with_no_description_sends_none_and_no_source(client):
    about = clues_for(client, UTI_ID)["about_disease"]
    assert about["description"] == ""
    assert about["source"] is None
    assert about["also_called"] == [
        "urinary tract infection (disease)",
        "INFECTION, URINARY TRACT",
        "TRACT, INFECTION OF URINARY",
    ]


def test_nobody_writes_a_description_when_open_targets_has_none(client):
    gemini = FakeGemini(KASHISH_EXAMPLE)
    with use(gemini):
        clues_for(client, UTI_ID)
    assert gemini.prompts == []  # Gemini is not asked anything for this


# ---- EXAMPLE 3: Gemini gets no description and is told not to describe ----

def test_the_facts_for_a_clue_hold_no_disease_description(sevoflurane, pah):
    assert pah.description == PAH_DESCRIPTION  # the record has it
    facts = explain.facts_for(sevoflurane, pah)
    assert facts["disease"] == {"name": "pulmonary arterial hypertension"}
    written = json.dumps(facts)
    assert "description" not in written
    assert "mmHg" not in written
    assert "Ayerza" not in written  # nor the "also called" names


def test_the_prompt_holds_no_description_and_says_not_to_describe(sevoflurane, pah):
    gemini = FakeGemini(KASHISH_EXAMPLE)
    with use(gemini):
        explain.explain(sevoflurane, pah)
    prompt = gemini.prompts[0]
    assert "do not describe it" in prompt
    assert "Never say what the disease is" in prompt
    for words in ("mmHg", "right heart failure", "progressive and potentially fatal", "Ayerza"):
        assert words not in prompt
    assert "Say what the disease is" not in prompt  # the old instruction is gone


def test_the_prompt_says_not_to_describe_in_every_case(sevoflurane, pah):
    plain = Disease(id=PAH_ID, name=pah.name)
    with_description = explain._prompt(explain.facts_for(sevoflurane, pah), [])
    without = explain._prompt(explain.facts_for(sevoflurane, plain), [])
    assert with_description == without
    assert "do not describe it" in with_description
    # Also when Gemini is asked to try again.
    again = explain._prompt(explain.facts_for(sevoflurane, pah), ["Rule 1: too long."])
    assert "do not describe it" in again


def test_the_reserve_explanation_does_not_describe_the_disease(sevoflurane, pah):
    with use(FakeGemini(None)):
        result = explain.explain(sevoflurane, pah)
    assert result.source == "template"
    assert result.problems == ()
    # Word for word: the only sentence with the disease's name is the link.
    assert result.text == (
        "Sevoflurane is a medicine. Doctors already use it for something else. "
        "It grabs a protein called KCNK3. A protein is a tiny machine in your body. "
        "Sevoflurane turns KCNK3 up, like a volume knob. "
        "KCNK3 is linked to pulmonary arterial hypertension. "
        "The link score is 0.79. That is like 79 points out of 100. "
        "Sevoflurane has no link to this disease in the database. "
        "The database is a huge web with lots of information. " + ENDING
    )


# ---- EXAMPLE 4: Kashish's example and the fixed ending are unchanged ----

def test_kashishs_example_and_the_ending_are_unchanged():
    assert explain.KASHISH_EXAMPLE == KASHISH_EXAMPLE
    assert explain.ENDING == ENDING
    assert explain.ENDING_MANY == ENDING.replace("this protein", "these proteins")


def test_kashishs_example_is_still_the_pattern_and_still_passes(sevoflurane, pah):
    gemini = FakeGemini(KASHISH_EXAMPLE)
    with use(gemini):
        result = explain.explain(sevoflurane, pah)
    assert KASHISH_EXAMPLE in gemini.prompts[0]
    assert result.source == "gemini"
    assert result.text == KASHISH_EXAMPLE + " " + ENDING
    assert explain.check_explanation(KASHISH_EXAMPLE, explain.facts_for(sevoflurane, pah)) == []


def test_the_grounding_check_now_refuses_words_from_the_description(sevoflurane, pah):
    # The check is unchanged. The description is no longer in the facts, so
    # a capital word or a number that only the description holds is a stranger.
    facts = explain.facts_for(sevoflurane, pah)
    problems = explain.check_explanation("It is a kind of PAH above 20.", facts)
    assert problems == ["Rule 4: not in the facts: PAH, 20."]


# ---- Careful: explanations saved under the old prompt are never served ----

@pytest.fixture
def saved_results(tmp_path, monkeypatch):
    """A throwaway folder for the saved results."""
    monkeypatch.setenv("MOONLIGHT_CACHE_DIR", str(tmp_path / "saved"))
    cache.forget_memory()
    yield tmp_path / "saved"
    cache.forget_memory()


def old_key(before):
    """The key explain.py filed an explanation under before this ticket."""
    return json.dumps(
        {"facts": before["facts"], "known": [], "ending": ENDING,
         "prompt": before["prompt"], "data_version": VERSION},
        sort_keys=True,
    )


@pytest.mark.parametrize("case", ["with_description", "without_description"])
def test_an_explanation_saved_under_the_old_prompt_is_not_served(
        case, sevoflurane, pah, saved_results):
    before = load(FIXTURES / "gemini" / "before_5_5_prompts.json")[case]
    old_text = (
        "Sevoflurane is a medicine. It grabs a protein called KCNK3. "
        "A protein is a tiny machine in your body. The disease is a kind of "
        "sick blood. " + ENDING
    )
    cache.save("explanation", VERSION, old_key(before),
               {"text": old_text, "model": "gemini-3.5-flash", "tries": 1})
    # The old explanation would still pass today's checks, so only its key
    # can keep it out.
    assert explain._problems(old_text, before["facts"], []) == []

    disease = pah if case == "with_description" else Disease(id=PAH_ID, name=pah.name)
    gemini = FakeGemini(KASHISH_EXAMPLE)
    with use(gemini):
        result = explain.explain(sevoflurane, disease, data_version=VERSION)
    assert len(gemini.prompts) == 1  # asked afresh
    assert "sick blood" not in result.text
    assert result.text == KASHISH_EXAMPLE + " " + ENDING


@pytest.mark.parametrize("case", ["with_description", "without_description"])
def test_the_prompt_text_is_not_the_old_prompt_text(case, sevoflurane, pah):
    before = load(FIXTURES / "gemini" / "before_5_5_prompts.json")[case]
    disease = pah if case == "with_description" else Disease(id=PAH_ID, name=pah.name)
    assert explain._prompt(explain.facts_for(sevoflurane, disease), []) != before["prompt"]


# ---- the page ----

@pytest.fixture
def page(client):
    return client.get("/").text


def page_script(page):
    return re.search(r"(?s)<script>(.*?)</script>", page).group(1)


def tag_with_id(page, name):
    return re.search(r'<[^>]*\bid="%s"[^>]*>' % name, page).group(0)


def test_the_page_has_the_description_under_the_name_with_its_source(page):
    found = page[page.index('<div id="found"'):]
    order = [
        found.index('id="disease-title"'),
        found.index('id="disease-also-called"'),
        found.index('id="disease-description"'),
        found.index(SOURCE_LINE),
        found.index(STAYS),
        found.index('data-slot="tabs"'),
    ]
    assert order == sorted(order)
    assert page.count(SOURCE_LINE) == 1


def test_the_description_and_its_source_are_hidden_until_there_is_one(page):
    # One box holds the description and its source line, so they can only
    # be shown or hidden together.
    box = tag_with_id(page, "disease-about")
    assert " hidden" in box
    inside = page[page.index(box):page.index(STAYS)]
    assert 'id="disease-description"' in inside
    assert SOURCE_LINE in inside
    assert " hidden" in tag_with_id(page, "disease-also-called")


def test_the_page_shows_the_box_only_when_there_is_a_description(page):
    script = page_script(page)
    assert 'byId("disease-about").hidden = !about.description;' in script
    assert 'byId("disease-also-called").hidden = !names.length;' in script


def test_the_page_writes_open_targets_words_as_plain_text(page):
    script = page_script(page)
    assert 'byId("disease-description").textContent = about.description;' in script
    # A semicolon between names, because some names hold a comma themselves.
    assert '"Also called: " + names.join("; ")' in script
    assert "innerHTML" not in script  # words from outside are never read as HTML


def test_a_new_search_takes_the_old_description_away(page):
    script = page_script(page)
    clear = script[script.index("function clearResults()"):]
    clear = clear[:clear.index("\n  }\n")]
    assert 'byId("disease-description").textContent = "";' in clear
    assert 'byId("disease-also-called").textContent = "";' in clear
    assert 'byId("disease-about").hidden = true;' in clear


def test_the_sentence_under_the_name_and_the_safety_line_stay(page):
    assert page.count(STAYS) == 1
    assert SAFETY_LINE in page
