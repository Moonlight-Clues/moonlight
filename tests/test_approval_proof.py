"""Ticket 2.13. Honest proof on Approved cards.

Kashish's decisions, 16 Nov (Rule B):

1. An Approved card whose only APPROVAL receipt is the link to Japan's
   general list of approved medicines stays, and shows JAPAN_LINE. Trial
   receipts do not count as proof of approval.
2. A corrections list lives in moonlight/corrections.json. It starts empty.
3. A card on the corrections list stays in its place and shows WARNING.
4. Both lines can be on cards in the main list and in the wider-group box.
   Nothing is hidden, moved or re-ordered.
5. Cards in In trials and New clues are not changed.

Saved files only (fixtures/approval_proof/, asked live on 2026-11-16).
No network. The corrections file is read through engine._read_corrections,
which these tests replace.
"""

import json
import pathlib
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from moonlight import api, cache, engine, explain, fetch
from moonlight.engine import Neighbour, sort_into_tabs
from moonlight.fetch import Listed
from moonlight.filter import sort_paths
from moonlight.records import Disease, Medicine, MedicineForm, Path, Target

REAL_POST_JSON = fetch._post_json  # kept before any test swaps it
REAL_READ_CORRECTIONS = engine._read_corrections

ROOT = pathlib.Path(__file__).resolve().parent.parent
PROOF = ROOT / "fixtures" / "approval_proof"
PAGE = (ROOT / "web" / "index.html").read_text(encoding="utf-8")

ALZHEIMER = Disease(id="MONDO_0004975", name="Alzheimer disease")
HUNTINGTON = Disease(id="MONDO_0007739", name="Huntington disease")
ECZEMA = Disease(id="MONDO_0004980", name="atopic eczema")
PAH = Disease(id="MONDO_0015924", name="pulmonary arterial hypertension")

# Kashish's words, exactly.
JAPAN_LINE = ("Approved in Japan, according to the database. Moonlight could not "
              "find the exact record for this disease.")
WARNING = "A doctor has told us this looks like a mistake in the database."
NOTE = "A doctor confirmed this looks wrong."
JAPAN_LINK = ("https://www.pmda.go.jp/english/review-services/reviews/"
              "approved-information/drugs/0001.html")

THE_FOUR = ["ATOMOXETINE", "GUANFACINE", "LISDEXAMFETAMINE", "METHYLPHENIDATE"]
ECZEMA_TWELVE = [
    "ATOMOXETINE", "BARICITINIB", "BILASTINE", "DESLORATADINE", "EPINASTINE",
    "FEXOFENADINE", "GUANFACINE", "LEVOCETIRIZINE", "LISDEXAMFETAMINE",
    "METHYLPHENIDATE", "OLOPATADINE", "TAPINAROF",
]
ATOMOXETINE_ID = "CHEMBL641"


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def one_file(folder, pattern):
    (file,) = folder.glob(pattern)
    return file


_searched = {"id": None}


def proof_post_json(body):
    """Stands in for fetch._post_json with the files saved for this ticket."""
    assert set(body) == {"query", "variables"}
    query, variables = body["query"], body["variables"]
    folder = PROOF / _searched["id"]
    if "targetId" in variables:
        return load(one_file(folder / "target_drugs",
                             f"*_{variables['targetId']}.response.json"))
    disease_id = variables["diseaseId"]
    if "parents" in query:
        return load(PROOF / disease_id / "family.response.json")
    if "associatedTargets" in query:
        return load(PROOF / disease_id / "associated_targets.response.json")
    if "drugAndClinicalCandidates" in query:
        return load(one_file(folder / "disease_drugs", f"*_{disease_id}.response.json"))
    return load(PROOF / disease_id / "disease.response.json")


@pytest.fixture(autouse=True)
def offline():
    """Saved files instead of Open Targets. Real HTTP is an error."""
    explain.forget_everything()
    api.forget_visitors()
    with patch("moonlight.fetch._post_json", side_effect=proof_post_json) as fake, \
            patch("requests.request", side_effect=AssertionError("network used")), \
            patch("requests.post", side_effect=AssertionError("network used")), \
            patch("requests.get", side_effect=AssertionError("network used")), \
            patch("requests.sessions.Session.request",
                  side_effect=AssertionError("network used")):
        yield fake
    explain.forget_everything()


def tabs_for(disease):
    """The whole search for one disease, offline, the way the API does it."""
    _searched["id"] = disease.id
    found = fetch.fetch_disease(disease.id)
    tray = engine.find_clues(found, fetch.fetch_targets(found, 25))
    return sort_into_tabs(tray, fetch.fetch_approved(found), fetch.fetch_withdrawn(found),
                          engine.fetch_neighbours(found))


@pytest.fixture(scope="module")
def saved_tabs():
    made = {}

    def get(disease):
        if disease.id not in made:
            with patch("moonlight.fetch._post_json", side_effect=proof_post_json):
                made[disease.id] = tabs_for(disease)
        return made[disease.id]

    return get


def with_line(medicines):
    return [medicine.name for medicine in medicines if medicine.proof_note]


# ---- fetch: the one extra thing asked about each report ----

def test_the_list_question_asks_for_each_reports_stage_by_its_live_name():
    assert "clinicalReports { url clinicalStage }" in fetch.DISEASE_DRUGS_QUERY
    # The name was read from the API's own list of a report's fields.
    fields = load(PROOF / "clinical_report_type.response.json")["data"]["__type"]["fields"]
    assert "clinicalStage" in [field["name"] for field in fields]


def test_the_saved_lists_were_made_with_the_question_fetch_asks_now():
    requests_saved = list(PROOF.glob("*/disease_drugs/*.request.json"))
    assert len(requests_saved) == 20  # 3 own entries, 6 parents and 11 children
    for file in requests_saved:
        assert load(file)["query"] == fetch.DISEASE_DRUGS_QUERY
    for file in PROOF.glob("*/disease_drugs/*.response.json"):
        for row in load(file)["data"]["disease"]["drugAndClinicalCandidates"]["rows"]:
            for report in row["clinicalReports"]:
                assert set(report) == {"url", "clinicalStage"}
                assert report["clinicalStage"]  # every saved report says its stage


def test_fetch_keeps_the_approval_receipts_apart_from_the_trial_receipts():
    _searched["id"] = ALZHEIMER.id
    listed = {entry.name: entry for entry in fetch.fetch_approved(ALZHEIMER)}
    atomoxetine = listed["ATOMOXETINE"]
    # Two links in all: Japan's general list and one trial.
    assert atomoxetine.sources == (JAPAN_LINK, "https://clinicaltrials.gov/study/NCT00191009")
    # Only one of them is an APPROVAL receipt.
    assert atomoxetine.approval_sources == (JAPAN_LINK,)
    donepezil = listed["DONEPEZIL"]
    assert JAPAN_LINK in donepezil.approval_sources
    assert len(donepezil.approval_sources) > 1
    assert all(link in donepezil.sources for link in donepezil.approval_sources)


def as_the_old_question_got_it(answer):
    """The same answer without each report's stage. On 2026-11-16 all 69
    saved lists were asked again with the new question, and every answer
    was the old saved one plus "clinicalStage" and nothing else."""
    old = json.loads(json.dumps(answer))
    for row in old["data"]["disease"]["drugAndClinicalCandidates"]["rows"]:
        for report in row["clinicalReports"]:
            del report["clinicalStage"]
    return old


def test_an_answer_to_the_old_question_has_no_approval_receipts_and_no_line(offline):
    file = PROOF / ALZHEIMER.id / "disease_drugs" / f"own_{ALZHEIMER.id}.response.json"
    old = as_the_old_question_got_it(load(file))
    offline.side_effect = lambda body: old
    listed = fetch.fetch_approved(ALZHEIMER)
    assert len(listed) == 21 and all(entry.sources for entry in listed)
    # Nothing is guessed: no stage was sent, so no link is called an approval receipt.
    assert all(entry.approval_sources == () for entry in listed)
    tabs = sort_into_tabs({}, listed)
    assert len(tabs.approved) == 21 and with_line(tabs.approved) == []


def test_an_old_answer_with_only_the_japan_link_shows_no_line(offline):
    old = {"data": {"disease": {"id": PAH.id, "drugAndClinicalCandidates": {"count": 1, "rows": [{
        "maxClinicalStage": "APPROVAL",
        "drug": {"id": "C1", "name": "OLDINE", "maximumClinicalStage": "APPROVAL",
                 "drugWarnings": [], "parentMolecule": None, "childMolecules": []},
        "clinicalReports": [{"url": JAPAN_LINK}],  # no clinicalStage: the old question
    }]}}}}
    offline.side_effect = lambda body: old
    tabs = sort_into_tabs({}, fetch.fetch_approved(PAH))
    assert [medicine.name for medicine in tabs.approved] == ["OLDINE"]
    assert tabs.approved[0].proof_note is None


def test_an_answer_saved_for_the_old_question_is_never_read_for_the_new_one(tmp_path, monkeypatch):
    monkeypatch.setenv(cache.FOLDER_VARIABLE, str(tmp_path))
    cache.forget_memory()
    old_question = fetch.DISEASE_DRUGS_QUERY.replace(
        "clinicalReports { url clinicalStage }", "clinicalReports { url }")
    assert old_question != fetch.DISEASE_DRUGS_QUERY
    variables = {"diseaseId": ALZHEIMER.id}
    old_answer = {"data": {"disease": {"id": ALZHEIMER.id, "drugAndClinicalCandidates": {
        "count": 0, "rows": []}}, "asked": "old"}}
    new_answer = load(PROOF / ALZHEIMER.id / "disease_drugs" / f"own_{ALZHEIMER.id}.response.json")
    cache.save("open-targets", "26.09", {"query": old_question, "variables": variables}, old_answer)
    asked = []

    def send(body):
        asked.append(body)
        return new_answer

    with patch("moonlight.fetch.data_version", return_value="26.09"), \
            patch("moonlight.fetch._send", side_effect=send):
        answer = REAL_POST_JSON({"query": fetch.DISEASE_DRUGS_QUERY, "variables": variables})
    cache.forget_memory()
    assert asked, "the new question must go to Open Targets, not to the old saved answer"
    assert all(body["query"] == fetch.DISEASE_DRUGS_QUERY for body in asked)
    assert answer == new_answer


# ---- engine: Kashish's EXAMPLES, from the saved files ----

def test_example_alzheimer_disease_exactly_four_cards_show_the_line(saved_tabs):
    tabs = saved_tabs(ALZHEIMER)
    assert with_line(tabs.approved) == THE_FOUR
    assert with_line(tabs.wider_group) == []
    assert len(tabs.approved) == 21 and len(tabs.wider_group) == 5


def test_example_huntington_disease_exactly_four_cards_show_the_line(saved_tabs):
    tabs = saved_tabs(HUNTINGTON)
    assert with_line(tabs.approved) == THE_FOUR
    assert with_line(tabs.wider_group) == []
    assert len(tabs.approved) == 5 and len(tabs.wider_group) == 5


def test_example_atopic_eczema_exactly_twelve_cards_show_the_line(saved_tabs):
    tabs = saved_tabs(ECZEMA)
    assert with_line(tabs.approved) == ECZEMA_TWELVE
    assert with_line(tabs.wider_group) == []
    assert len(tabs.approved) == 41 and len(tabs.narrower) == 4 and len(tabs.wider_group) == 68


def test_the_line_is_kashishs_words_exactly(saved_tabs):
    assert engine.JAPAN_LINE == JAPAN_LINE
    for medicine in saved_tabs(HUNTINGTON).approved:
        assert medicine.proof_note in (None, JAPAN_LINE)


def test_the_approved_tab_is_still_a_to_z_and_nothing_left(saved_tabs):
    for disease in (ALZHEIMER, HUNTINGTON, ECZEMA):
        tabs = saved_tabs(disease)
        for box in (tabs.approved, tabs.wider_group):
            names = [medicine.name for medicine in box]
            assert names == sorted(names, key=str.casefold)
            assert len(set(names)) == len(names)


def listed(name, links, approval_links, **more):
    return Listed(id="ID_" + name, name=name, forms=(("ID_" + name, name),),
                  sources=tuple(links), approval_sources=tuple(approval_links), **more)


TRIAL = "https://clinicaltrials.gov/study/NCT00000001"
LABEL = "https://example.org/label/1"


def test_example_japan_link_plus_another_approval_receipt_no_line():
    tabs = sort_into_tabs({}, [listed("BOTHINE", [JAPAN_LINK, LABEL], [JAPAN_LINK, LABEL])])
    assert tabs.approved[0].proof_note is None


def test_example_japan_link_plus_only_trial_receipts_the_line_shows():
    tabs = sort_into_tabs({}, [listed("TRIALINE", [TRIAL, JAPAN_LINK], [JAPAN_LINK])])
    assert tabs.approved[0].proof_note == JAPAN_LINE


def test_a_card_with_an_exact_approval_record_and_no_japan_link_has_no_line():
    tabs = sort_into_tabs({}, [listed("EXACTINE", [LABEL], [LABEL])])
    assert tabs.approved[0].proof_note is None


def test_a_card_with_no_approval_receipt_is_not_decided_and_is_left_as_it_is():
    tabs = sort_into_tabs({}, [listed("NOLINKINE", [], []), listed("TRIALONLY", [TRIAL], [])])
    assert [medicine.proof_note for medicine in tabs.approved] == [None, None]


def test_a_link_that_only_looks_like_the_japan_link_is_an_exact_record():
    near = JAPAN_LINK.replace("0001", "0002")
    tabs = sort_into_tabs({}, [listed("NEARINE", [near], [near])])
    assert tabs.approved[0].proof_note is None


def test_the_line_can_be_on_a_card_in_the_wider_group_box_and_on_a_child_card():
    wider = Disease(id="D_UP", name="wider disease")
    under = Disease(id="D_DOWN", name="narrower disease")
    neighbours = [
        Neighbour(engine.PARENT, wider, (listed("UPINE", [JAPAN_LINK], [JAPAN_LINK]),), ()),
        Neighbour(engine.CHILD, under, (listed("DOWNINE", [JAPAN_LINK, TRIAL], [JAPAN_LINK]),), ()),
    ]
    tabs = sort_into_tabs({}, [], (), neighbours)
    assert [(m.name, m.proof_note) for m in tabs.wider_group] == [("UPINE", JAPAN_LINE)]
    assert [(m.name, m.proof_note) for m in tabs.narrower] == [("DOWNINE", JAPAN_LINE)]
    assert tabs.wider_group[0].label and tabs.narrower[0].label  # the label stays too


def test_an_exact_record_on_a_second_parent_takes_the_line_away():
    one = Disease(id="D_UP1", name="first wider disease")
    two = Disease(id="D_UP2", name="second wider disease")
    neighbours = [
        Neighbour(engine.PARENT, one, (listed("UPINE", [JAPAN_LINK], [JAPAN_LINK]),), ()),
        Neighbour(engine.PARENT, two, (listed("UPINE", [LABEL], [LABEL]),), ()),
    ]
    tabs = sort_into_tabs({}, [], (), neighbours)
    assert tabs.wider_group[0].proof_note is None


def test_a_path_does_not_change_the_line_and_the_cards_path_is_kept(saved_tabs):
    # Lisdexamfetamine acts on one of Alzheimer disease's proteins, so its
    # card has a path with many links. They are about the medicine and the
    # protein, not proof that it is approved for this disease.
    card = {m.name: m for m in saved_tabs(ALZHEIMER).approved}["LISDEXAMFETAMINE"]
    assert card.clue is not None and len(card.sources) > 1
    assert card.approval_sources == (JAPAN_LINK,)
    assert card.proof_note == JAPAN_LINE


# ---- the corrections list ----

def correction(medicine_id, disease_id):
    return {"medicine_id": medicine_id, "disease_id": disease_id,
            "date": "2026-11-16", "note": NOTE}


def test_the_corrections_file_is_the_one_the_engine_reads():
    file = ROOT / "moonlight" / "corrections.json"
    assert engine.CORRECTIONS_FILE == file
    assert REAL_READ_CORRECTIONS() == json.loads(file.read_text(encoding="utf-8"))


def test_every_entry_in_the_real_file_has_the_four_things_and_names_no_doctor():
    # True today because the file is empty. It guards every later pull request.
    for entry in REAL_READ_CORRECTIONS():
        assert set(entry) == {"medicine_id", "disease_id", "date", "note"}
        assert entry["note"] == NOTE
    assert len(engine.corrections()) == len(REAL_READ_CORRECTIONS())


def test_example_with_an_empty_corrections_file_no_card_shows_the_warning():
    with patch("moonlight.engine._read_corrections", return_value=[]):
        assert engine.looks_wrong(ALZHEIMER.id) == set()


def test_example_the_warning_is_for_that_medicine_and_that_disease_only():
    entries = [correction(ATOMOXETINE_ID, ALZHEIMER.id)]
    with patch("moonlight.engine._read_corrections", return_value=entries):
        assert engine.looks_wrong(ALZHEIMER.id) == {ATOMOXETINE_ID}
        assert engine.looks_wrong(HUNTINGTON.id) == set()
        assert engine.looks_wrong(ECZEMA.id) == set()


@pytest.mark.parametrize("entry", [
    {"medicine_id": "C1", "disease_id": "D1", "date": "2026-11-16"},  # no note
    {"medicine_id": "C1", "disease_id": "D1", "date": "2026-11-16", "note": "Some other words."},
    {"medicine_id": "C1", "disease_id": "D1", "date": "2026-11-16", "note": NOTE,
     "doctor": "A Name"},  # no doctor is ever named
    {"medicine_id": "", "disease_id": "D1", "date": "2026-11-16", "note": NOTE},
    {"medicine_id": "C1", "disease_id": "D1", "date": "16 Nov", "note": NOTE},
    "C1",
])
def test_an_entry_that_is_not_written_the_agreed_way_is_refused_out_loud(entry):
    with patch("moonlight.engine._read_corrections", return_value=[entry]):
        with pytest.raises(ValueError):
            engine.corrections()


def test_the_corrections_note_and_the_warning_are_kashishs_words_exactly():
    assert engine.CORRECTION_NOTE == NOTE
    assert engine.WRONG_WARNING == WARNING


# ---- the API ----

@pytest.fixture
def client():
    return TestClient(api.app)


def clues_json(client, disease, corrections=()):
    _searched["id"] = disease.id
    with patch("moonlight.engine._read_corrections", return_value=list(corrections)):
        answer = client.get("/api/clues", params={"disease_id": disease.id})
    assert answer.status_code == 200
    return answer.json()


def test_api_alzheimer_disease_four_cards_carry_the_line_word_for_word(client):
    data = clues_json(client, ALZHEIMER)
    noted = [item for item in data["approved"] if "proof_note" in item]
    assert [item["medicine"] for item in noted] == [
        "Atomoxetine", "Guanfacine", "Lisdexamfetamine", "Methylphenidate"]
    assert all(item["proof_note"] == JAPAN_LINE for item in noted)
    assert all("proof_note" not in item for item in data["wider_group"])
    donepezil = next(item for item in data["approved"] if item["medicine"] == "Donepezil")
    assert "proof_note" not in donepezil and "warning" not in donepezil


def test_api_with_an_empty_corrections_list_no_card_has_the_warning(client):
    for disease in (ALZHEIMER, HUNTINGTON, ECZEMA):
        data = clues_json(client, disease)
        cards = data["approved"] + data.get("wider_group", [])
        assert cards and all("warning" not in item for item in cards)


def test_api_the_warning_is_on_that_card_for_that_disease_only(client):
    entries = [correction(ATOMOXETINE_ID, ALZHEIMER.id)]
    plain = clues_json(client, ALZHEIMER)
    data = clues_json(client, ALZHEIMER, entries)
    warned = [item for item in data["approved"] + data["wider_group"] if "warning" in item]
    assert [(item["id"], item["warning"]) for item in warned] == [(ATOMOXETINE_ID, WARNING)]
    # It stays in its place: same cards, same order, nothing hidden.
    assert [item["id"] for item in data["approved"]] == [item["id"] for item in plain["approved"]]
    assert data["wider_group"] == plain["wider_group"]
    names = [item["medicine"] for item in data["approved"]]
    assert names == sorted(names, key=str.casefold)
    # The same medicine under another disease has no warning.
    for other in (HUNTINGTON, ECZEMA):
        other_data = clues_json(client, other, entries)
        cards = other_data["approved"] + other_data["wider_group"]
        assert any(item["id"] == ATOMOXETINE_ID for item in cards)
        assert all("warning" not in item for item in cards)


def test_api_a_card_can_carry_both_lines_and_everything_else_is_unchanged(client):
    plain = clues_json(client, HUNTINGTON)
    data = clues_json(client, HUNTINGTON, [correction(ATOMOXETINE_ID, HUNTINGTON.id)])
    before = next(item for item in plain["approved"] if item["id"] == ATOMOXETINE_ID)
    after = next(item for item in data["approved"] if item["id"] == ATOMOXETINE_ID)
    assert after["proof_note"] == JAPAN_LINE and after["warning"] == WARNING
    assert {key: value for key, value in after.items() if key != "warning"} == before


def test_api_the_warning_can_be_on_a_card_in_the_wider_group_box(client):
    plain = clues_json(client, HUNTINGTON)
    first = plain["wider_group"][0]
    data = clues_json(client, HUNTINGTON, [correction(first["id"], HUNTINGTON.id)])
    assert data["wider_group"][0] == {**first, "warning": WARNING}
    assert data["wider_group"][1:] == plain["wider_group"][1:]
    assert data["approved"] == plain["approved"]


def test_api_in_trials_and_new_clues_are_not_changed(client):
    for disease in (ALZHEIMER, HUNTINGTON):
        plain = clues_json(client, disease)
        clue_ids = [item["id"] for item in plain["being_studied"] + plain["new_clues"]]
        assert clue_ids
        entries = [correction(clue_id, disease.id) for clue_id in clue_ids]
        data = clues_json(client, disease, entries)
        for tab in ("being_studied", "new_clues"):
            assert data[tab] == plain[tab]
            for item in data[tab]:
                assert "proof_note" not in item and "warning" not in item
        assert data["left_out"] == plain["left_out"]


def test_api_no_approved_card_has_an_ending_or_do_not_try_it(client):
    data = clues_json(client, ECZEMA, [correction(ATOMOXETINE_ID, ECZEMA.id)])
    for item in data["approved"] + data["wider_group"]:
        assert "ending" not in item and "explanation" not in item
        assert "Do not try it" not in json.dumps(item)
    assert data["rule_text"] == api.RULE_TEXT


# ---- the page ----

def approved_card_script():
    script = PAGE[PAGE.index("function approvedCard("):]
    return script[:script.index("\n  }\n")]


def test_the_page_shows_both_lines_as_plain_text_from_the_api():
    assert 'data-slot="proof-note" hidden' in PAGE
    assert 'data-slot="warning" hidden' in PAGE
    script = approved_card_script()
    assert "textContent = medicine.proof_note" in script
    assert "textContent = medicine.warning" in script
    assert "innerHTML" not in script
    # Only an Approved card fills them. A clue's card never does.
    assert PAGE.count("medicine.proof_note") == 2 and PAGE.count("medicine.warning") == 2
    assert "clue.warning" not in PAGE and "clue.proof_note" not in PAGE
    # The words are written by the engine, not by the page.
    assert "Approved in Japan" not in PAGE
    assert "looks like a mistake" not in PAGE


def test_the_warning_is_bright_red_and_does_not_rely_on_colour_alone():
    start = PAGE.index('data-slot="warning"')
    tag = PAGE[PAGE.rindex("<", 0, start):PAGE.index("</p>", start)]
    # A warning sign with a name a screen reader says, then the words.
    assert "<svg" in tag and 'role="img"' in tag and 'aria-label="Warning"' in tag
    assert 'data-part="warning-words"' in tag
    assert 'role="alert"' not in tag  # it is said in its place, not shouted on load
    style = PAGE[PAGE.index(".wrong-warning{"):]
    style = style[:style.index("}")]
    assert "#D40000" in style  # red, outside the page's palette on purpose
    assert "font-weight" in style and "border" in style
    palette = PAGE[PAGE.index(":root{"):PAGE.index("}", PAGE.index(":root{"))]
    assert "#D40000" not in palette


def test_the_page_keeps_the_approved_tabs_two_sentences_and_the_doctor_line():
    assert ("Already approved for this disease in at least one country, according to "
            "the database. Nothing here says how well any of them works.") in PAGE
    panel = PAGE[PAGE.index('id="panel-approved"'):PAGE.index('id="panel-trials"')]
    assert panel.count("Talk to your doctor before changing any medicine.") == 3
    assert "Do not try it" not in panel
    assert ("For learning and research exploration, not medical advice. Never start, "
            "stop or change any medicine without a doctor.") in PAGE


def test_the_page_does_not_move_or_hide_a_card_with_a_line():
    script = approved_card_script()
    assert ".remove()" not in script[script.index("medicine.proof_note"):script.index(
        "if (!medicine.proteins.length)")]
    draw = PAGE[PAGE.index("function draw(data)"):]
    assert "data.approved.map(medicine => approvedCard(medicine, diseaseName))" in draw
    assert ".sort(" not in draw[:draw.index("byId(\"wider-box\").open")]
