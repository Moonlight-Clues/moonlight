"""Ticket 3.1. Why each gene is linked to the disease.

Kashish's decisions (25 Nov 2026, 10:05 to 10:06 am, spoken). Under each
gene on a clue card, one line says what kinds of evidence link that gene to
the disease:

    Linked to this disease by: <names, joined by ", ">.

The six names, in this order, one for each Open Targets "datatypeScores" id:

    genetic_association  inherited gene changes
    somatic_mutation     gene changes found in tumours
    animal_model         studies in animals
    affected_pathway     a body process the gene is part of
    rna_expression       how active the gene is in the disease
    literature           found together in research papers

A kind counts when its score for that gene and disease is at least 0.5 (one
constant in engine.py). At most three names, in the table's order. A gene
linked only by papers still gets the line. Nothing at the cut-off: no line.
"known_drug" is never named: it is the medicine itself. Any other id is
ignored. (In the live data, release 26.09, that id is called "clinical".)

Decisions of 25 Nov, after the first review of PR 80:
1. "somatic_mutation" counts only when the disease is a cancer: its Open
   Targets therapeutic areas include MONDO_0045024 ("cancer or benign
   tumor"), read on the same proteins question.
2. "genetic_literature" counts as "inherited gene changes". With both at
   the cut-off, the name appears once, in its own place.

The engine sends only the ids. The page types the words once; engine.py
keeps a copy, and a test here checks the two match.

How these tests work. The first part hands hand-built proteins to the
engine's rule. The second reads the saved answers in fixtures/gene_evidence/
(asked live on 2026-11-25, data 26.09) and builds /api/clues from them, never
from the network. The third reads web/index.html as text. The fourth opens
it in a real browser (Chromium) that is never let outside, at phone width
(390), as tests/test_protein_sentence.py does.
"""

import copy
import json
import pathlib
import re
import shutil
import subprocess
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from moonlight import api, engine, fetch
from moonlight.filter import sort_paths
from moonlight.records import Disease, Medicine, MedicineForm, Path, Target

ROOT = pathlib.Path(__file__).resolve().parent.parent
SAVED = ROOT / "fixtures" / "gene_evidence"
PAGE_FILE = ROOT / "web" / "index.html"
PAGE = PAGE_FILE.read_text(encoding="utf-8")

HUNTINGTON = "MONDO_0007739"
T2D = "MONDO_0005148"
NMO = "MONDO_0019100"  # neuromyelitis optica: genes linked by papers alone
PAH = "MONDO_0015924"  # pulmonary arterial hypertension: CPS1, linked by curated genetics only
BREAST_CANCER = "MONDO_0007254"  # a cancer: only its proteins question is saved
CANCER = "MONDO_0045024"  # Open Targets' therapeutic area "cancer or benign tumor"
KEY = "evidence"  # the one new key on a protein of a clue card

# Kashish's words, exactly.
START = "Linked to this disease by: "
NAMES = (
    ("genetic_association", "inherited gene changes"),
    ("somatic_mutation", "gene changes found in tumours"),
    ("animal_model", "studies in animals"),
    ("affected_pathway", "a body process the gene is part of"),
    ("rna_expression", "how active the gene is in the disease"),
    ("literature", "found together in research papers"),
)
SAFETY_LINE = ("For learning and research exploration, not medical advice. Never start, stop or "
               "change any medicine without a doctor.")
DIRECTION_LINE = "The data does not say which direction this disease needs."


def gene(**scores):
    """A hand-built protein with these evidence scores, for a cancer, so
    every one of the six kinds can count (decision 1 of 25 Nov)."""
    return Target("ENSG00000000001", "ABC1", "test protein", 0.6,
                  evidence_scores=tuple(scores.items()), disease_areas=(CANCER,))


def not_cancer_gene(**scores):
    """The same, for a disease whose therapeutic areas hold no cancer."""
    return Target("ENSG00000000001", "ABC1", "test protein", 0.6,
                  evidence_scores=tuple(scores.items()),
                  disease_areas=("MONDO_0005151", "OTAR_0000020"))


def line_for(target):
    return engine.evidence_line(engine.evidence_ids(target))


# ---- 1. the rule, on hand-built proteins ----

def test_example_inherited_gene_changes_and_studies_in_animals():
    target = gene(genetic_association=0.8, animal_model=0.6)
    assert engine.evidence_ids(target) == ("genetic_association", "animal_model")
    assert line_for(target) == (
        "Linked to this disease by: inherited gene changes, studies in animals.")


def test_example_known_drug_alone_gives_no_line():
    for medicine_itself in ("known_drug", "clinical"):
        target = gene(**{medicine_itself: 1.0})
        assert engine.evidence_ids(target) == ()
        assert line_for(target) is None


def test_example_literature_alone_at_0_6():
    target = gene(literature=0.6)
    assert engine.evidence_ids(target) == ("literature",)
    assert line_for(target) == (
        "Linked to this disease by: found together in research papers.")


def test_example_literature_alone_even_when_others_are_below_the_cut_off():
    target = gene(genetic_association=0.49, animal_model=0.3, literature=0.7, known_drug=0.9)
    assert line_for(target) == (
        "Linked to this disease by: found together in research papers.")


def test_example_nothing_at_0_5_or_above_gives_no_line():
    target = gene(genetic_association=0.49, somatic_mutation=0.4, animal_model=0.1,
                  affected_pathway=0.2, rna_expression=0.3, literature=0.499)
    assert engine.evidence_ids(target) == ()
    assert line_for(target) is None
    assert line_for(gene()) is None  # no scores at all


def test_exactly_the_cut_off_counts():
    assert engine.evidence_ids(gene(animal_model=0.5)) == ("animal_model",)


def test_example_at_most_three_names_in_the_tables_order():
    # sent in the opposite order, all six high
    target = gene(literature=0.9, rna_expression=0.9, affected_pathway=0.9,
                  animal_model=0.9, somatic_mutation=0.9, genetic_association=0.9)
    assert engine.evidence_ids(target) == (
        "genetic_association", "somatic_mutation", "animal_model")
    assert line_for(target) == (
        "Linked to this disease by: inherited gene changes, gene changes found in tumours, "
        "studies in animals.")


def test_the_tables_order_wins_over_the_scores():
    target = gene(literature=0.99, rna_expression=0.95, affected_pathway=0.51)
    assert line_for(target) == (
        "Linked to this disease by: a body process the gene is part of, how active the "
        "gene is in the disease, found together in research papers.")


def test_literature_can_be_one_of_the_three():
    target = gene(literature=0.9, genetic_association=0.6)
    assert line_for(target) == (
        "Linked to this disease by: inherited gene changes, found together in research "
        "papers.")


def test_any_other_id_is_ignored():
    target = gene(clinical=0.99, known_drug=1.0, something_new=0.9, rna_expression=0.8)
    assert engine.evidence_ids(target) == ("rna_expression",)


def test_the_cut_off_is_one_constant_in_the_engine():
    assert engine.EVIDENCE_CUTOFF == 0.5
    target = gene(genetic_association=0.8, animal_model=0.6)
    with patch.object(engine, "EVIDENCE_CUTOFF", 0.7):
        assert engine.evidence_ids(target) == ("genetic_association",)
    with patch.object(engine, "EVIDENCE_CUTOFF", 0.3):
        assert engine.evidence_ids(gene(literature=0.35)) == ("literature",)


def test_the_engines_copy_of_the_words_is_kashishs():
    assert engine.EVIDENCE_START == START
    assert tuple(engine.EVIDENCE_NAMES.items()) == NAMES
    assert "known_drug" not in engine.EVIDENCE_NAMES
    assert "clinical" not in engine.EVIDENCE_NAMES


def test_a_target_made_the_old_way_has_no_scores_and_no_line():
    old = Target("ENSG_TEST", "TEST1", "test protein", 0.5)
    assert old.evidence_scores == ()
    assert old.disease_areas == ()
    assert engine.evidence_ids(old) == ()


# ---- decision 1 (25 Nov): tumours only for cancers ----

def test_tumours_are_not_named_for_a_disease_that_is_not_a_cancer():
    target = not_cancer_gene(genetic_association=0.9, somatic_mutation=0.9,
                             animal_model=0.6, literature=0.8)
    assert engine.evidence_ids(target) == (
        "genetic_association", "animal_model", "literature")
    assert "tumours" not in line_for(target)


def test_tumours_alone_for_a_disease_that_is_not_a_cancer_gives_no_line():
    assert engine.evidence_ids(not_cancer_gene(somatic_mutation=0.9)) == ()


def test_tumours_are_named_for_a_cancer():
    target = gene(genetic_association=0.9, somatic_mutation=0.9)
    assert line_for(target) == (
        "Linked to this disease by: inherited gene changes, gene changes found in tumours.")


def test_with_no_therapeutic_areas_sent_tumours_do_not_count():
    """An answer saved before this change says nothing about the disease's
    areas. Nothing is guessed: it is not known to be a cancer."""
    target = Target("ENSG_TEST", "TEST1", "test protein", 0.5,
                    evidence_scores=(("somatic_mutation", 0.9), ("literature", 0.6)))
    assert engine.evidence_ids(target) == ("literature",)


def test_the_cancer_area_is_one_constant_in_the_engine():
    assert engine.CANCER_AREA == CANCER


# ---- decision 2 (25 Nov): genetic_literature counts as inherited gene changes ----

def test_genetic_literature_alone_is_inherited_gene_changes():
    target = gene(genetic_literature=0.61)
    assert engine.evidence_ids(target) == ("genetic_association",)
    assert line_for(target) == "Linked to this disease by: inherited gene changes."


def test_both_genetic_kinds_name_inherited_gene_changes_once_in_its_place():
    target = gene(literature=0.9, animal_model=0.7, genetic_literature=0.8,
                  genetic_association=0.6)
    assert engine.evidence_ids(target) == (
        "genetic_association", "animal_model", "literature")
    assert line_for(target).count("inherited gene changes") == 1


def test_genetic_literature_below_the_cut_off_does_not_count():
    assert engine.evidence_ids(gene(genetic_literature=0.49, literature=0.6)) == (
        "literature",)


def test_genetic_literature_is_never_sent_as_its_own_id():
    assert "genetic_literature" not in engine.EVIDENCE_NAMES
    assert engine.EVIDENCE_SAME_AS == {"genetic_literature": "genetic_association"}


# ---- 2. fetch.py and api.py, from the saved answers ----

def load(file):
    return json.loads(file.read_text(encoding="utf-8"))


def saved_post_json(body):
    """Stands in for fetch._post_json with the saved files."""
    assert set(body) == {"query", "variables"}
    query, variables = body["query"], body["variables"]
    if "targetId" in variables:
        kind, asked = "target_drugs", variables["targetId"]
    else:
        asked = variables["diseaseId"]
        if "parents" in query:
            kind = "family"
        elif "associatedTargets" in query:
            kind = "associated_targets"
            # the saved answer was asked with the question fetch.py asks now
            assert load(SAVED / kind / f"{asked}.request.json")["query"] == fetch.TARGETS_QUERY
        elif "drugAndClinicalCandidates" in query:
            kind = "disease_drugs"
        else:
            kind = "disease"
    file = SAVED / kind / f"{asked}.response.json"
    assert file.exists(), f"no saved answer for {kind} {asked}"
    return load(file)


def without_scores(body):
    """The same saved answers with every "datatypeScores" taken out."""
    answer = copy.deepcopy(saved_post_json(body))
    if "associatedTargets" in body["query"]:
        for row in answer["data"]["disease"]["associatedTargets"]["rows"]:
            del row["datatypeScores"]
    return answer


def no_network():
    return [patch(name, side_effect=AssertionError("network used")) for name in (
        "requests.request", "requests.post", "requests.get",
        "requests.sessions.Session.request")]


def page_answer(disease_id, answers=saved_post_json):
    """What /api/clues sends, from saved answers and the real hand-written files."""
    api.forget_visitors()
    guards = no_network()
    for guard in guards:
        guard.start()
    try:
        with patch("moonlight.fetch._post_json", side_effect=answers):
            response = TestClient(api.app).get("/api/clues", params={"disease_id": disease_id})
    finally:
        for guard in guards:
            guard.stop()
        api.forget_visitors()
    assert response.status_code == 200
    return response.json()


@pytest.fixture(scope="module")
def huntington():
    return page_answer(HUNTINGTON)


@pytest.fixture(scope="module")
def t2d():
    return page_answer(T2D)


@pytest.fixture(scope="module")
def nmo():
    return page_answer(NMO)


@pytest.fixture(scope="module")
def pah():
    return page_answer(PAH)


def saved_scores(disease_id):
    """symbol -> {id: score}, as Open Targets sent them."""
    answer = load(SAVED / "associated_targets" / f"{disease_id}.response.json")
    return {row["target"]["approvedSymbol"]: {kind["id"]: kind["score"]
                                              for kind in row["datatypeScores"]}
            for row in answer["data"]["disease"]["associatedTargets"]["rows"]}


def clue(answer, name, part="new_clues"):
    found = [item for item in answer[part] if item["medicine"] == name]
    assert len(found) == 1, name
    return found[0]


def evidence_of(item):
    return {found["symbol"]: found.get(KEY) for found in item["proteins"]}


def test_the_question_asks_for_the_scores_on_the_same_rows():
    rows = fetch.TARGETS_QUERY[fetch.TARGETS_QUERY.index("rows {"):]
    assert "datatypeScores { id score }" in rows
    # and, on the same disease, its therapeutic areas (decision 1 of 25 Nov)
    assert "therapeuticAreas { id }" in fetch.TARGETS_QUERY[
        :fetch.TARGETS_QUERY.index("associatedTargets")]
    assert "target { id approvedSymbol approvedName functionDescriptions }" in rows
    assert fetch.TARGETS_QUERY.count("query ") == 1  # no new question
    for query in (fetch.DISEASE_QUERY, fetch.FAMILY_QUERY, fetch.TARGET_DRUGS_QUERY,
                  fetch.DISEASE_DRUGS_QUERY):
        assert "datatypeScores" not in query
        assert "therapeuticAreas" not in query


def test_a_target_carries_its_diseases_therapeutic_areas():
    with patch("moonlight.fetch._post_json", side_effect=saved_post_json):
        diabetes = fetch.fetch_targets(Disease(T2D, "type 2 diabetes mellitus"), 25)
        cancer = fetch.fetch_targets(Disease(BREAST_CANCER, "breast cancer"), 25)
    assert all(CANCER not in target.disease_areas for target in diabetes)
    assert all(target.disease_areas == diabetes[0].disease_areas for target in diabetes)
    assert all(CANCER in target.disease_areas for target in cancer)


def test_example_a_cancer_still_names_tumours():
    """Breast cancer, saved live: its top genes' tumour evidence counts."""
    with patch("moonlight.fetch._post_json", side_effect=saved_post_json):
        targets = fetch.fetch_targets(Disease(BREAST_CANCER, "breast cancer"), 25)
    named = [target.symbol for target in targets
             if "somatic_mutation" in engine.evidence_ids(target)]
    assert named  # at least one
    for target in targets:
        if target.symbol in named:
            assert dict(target.evidence_scores)["somatic_mutation"] >= 0.5
            assert "gene changes found in tumours" in line_for(target)


def test_example_cps1_in_pah_now_gets_the_line(pah):
    """CPS1: genetic_literature 0.61, papers 0.24. Decision 2 of 25 Nov."""
    scores = saved_scores(PAH)["CPS1"]
    assert scores.get("genetic_literature", 0) >= 0.5
    assert scores.get("genetic_association", 0) < 0.5
    found = [protein for item in pah["new_clues"] + pah["being_studied"]
             for protein in item["proteins"] if protein["symbol"] == "CPS1"]
    assert found
    for protein in found:
        assert protein[KEY] == ["genetic_association"]
    target = Target("x", "CPS1", "x", 0.5, evidence_scores=tuple(scores.items()))
    assert line_for(target) == "Linked to this disease by: inherited gene changes."


def test_a_target_carries_the_scores_as_open_targets_sent_them():
    with patch("moonlight.fetch._post_json", side_effect=saved_post_json):
        targets = fetch.fetch_targets(Disease(HUNTINGTON, "Huntington disease"), 25)
    assert len(targets) == 25
    sent = saved_scores(HUNTINGTON)
    for target in targets:
        assert dict(target.evidence_scores) == sent[target.symbol], target.symbol
    by_symbol = {target.symbol: target for target in targets}
    assert dict(by_symbol["SCN4A"].evidence_scores) == pytest.approx(
        {"literature": 0.64, "animal_model": 0.55, "clinical": 0.43}, abs=0.005)


def test_an_old_saved_answer_without_the_field_still_loads():
    old = load(ROOT / "fixtures" / "protein_sentence" / "associated_targets"
               / "MONDO_0005364.response.json")
    assert "datatypeScores" not in json.dumps(old)
    with patch("moonlight.fetch._post_json", return_value=old):
        targets = fetch.fetch_targets(Disease("MONDO_0005364", "Graves disease"), 25)
    assert len(targets) == 25
    assert all(target.evidence_scores == () for target in targets)


def test_example_huntington_lamotrigine(huntington):
    """SCN4A: animal 0.55, papers 0.64. SCN8A: animal 0.70. SCN1A: animal 0.52.
    SCN9A (animal 0.35) and SCN11A (papers 0.18) reach nothing."""
    assert evidence_of(clue(huntington, "Lamotrigine")) == {
        "SCN4A": ["animal_model", "literature"],
        "SCN8A": ["animal_model"],
        "SCN1A": ["animal_model"],
        "SCN9A": None,
        "SCN11A": None,
    }


def test_example_huntington_metformin_in_trials(huntington):
    item = clue(huntington, "Metformin", "being_studied")
    found = evidence_of(item)
    assert found["NDUFS4"] == ["animal_model"]
    assert [symbol for symbol, ids in found.items() if ids] == ["NDUFS4"]


def test_example_t2d_no_tumours_for_a_disease_that_is_not_a_cancer(t2d):
    """ABCC8: inherited 0.92, tumours 0.62, animals 0.55, papers 0.78.
    KCNJ11: inherited 0.92, tumours 0.71, papers 0.94. Type 2 diabetes is
    not a cancer, so the tumour evidence is not named (decision 1)."""
    scores = saved_scores(T2D)
    assert scores["ABCC8"]["somatic_mutation"] >= 0.5
    assert scores["KCNJ11"]["somatic_mutation"] >= 0.5
    item = clue(t2d, "Gliclazide", "being_studied")
    assert evidence_of(item) == {
        "KCNJ11": ["genetic_association", "literature"],
        "ABCC8": ["genetic_association", "animal_model", "literature"],
    }
    assert "somatic_mutation" not in json.dumps(t2d)
    assert evidence_of(clue(t2d, "Mesalamine")) == {
        "PPARG": ["genetic_association", "animal_model", "literature"]}


def test_example_nmo_papers_alone(nmo):
    assert evidence_of(clue(nmo, "Siltuximab")) == {"IL6": ["literature"]}
    assert evidence_of(clue(nmo, "Blinatumomab")) == {"CD19": ["literature"]}


def test_every_clue_gene_follows_the_rule(huntington, t2d, nmo, pah):
    """None of the four diseases is a cancer, so tumours never count."""
    for disease_id, answer in ((HUNTINGTON, huntington), (T2D, t2d), (NMO, nmo), (PAH, pah)):
        scores = saved_scores(disease_id)
        for part in ("new_clues", "being_studied"):
            for item in answer[part]:
                for found in item["proteins"]:
                    got = dict(scores[found["symbol"]])
                    got["genetic_association"] = max(
                        got.get("genetic_association", 0), got.get("genetic_literature", 0))
                    counted = [kind for kind, _ in NAMES if kind != "somatic_mutation"
                               and got.get(kind, 0) >= 0.5][:3]
                    assert found.get(KEY) == (counted or None), (item["medicine"], found)


def test_the_key_is_never_empty_and_holds_only_the_six_ids(huntington, t2d, nmo):
    known = dict(NAMES)
    seen = 0
    for answer in (huntington, t2d, nmo):
        for part in ("new_clues", "being_studied"):
            for item in answer[part]:
                for found in item["proteins"]:
                    if KEY in found:
                        seen += 1
                        assert found[KEY] and len(found[KEY]) <= 3
                        assert all(kind in known for kind in found[KEY])
    assert seen > 10


def test_the_api_sends_only_the_ids_never_the_words(huntington, t2d, nmo):
    for answer in (huntington, t2d, nmo):
        sent = json.dumps(answer)
        assert "Linked to this disease by" not in sent
        for _, name in NAMES:
            assert name not in sent


def test_no_approved_card_has_the_key(huntington, t2d, nmo):
    for answer in (huntington, t2d, nmo):
        assert answer["approved"]
        for part in ("approved", "narrower", "wider_group"):
            for item in answer.get(part, []):
                for found in item["proteins"]:
                    assert KEY not in found, (part, item["medicine"])
        for part in ("more_in_trials", "new_in_trials"):
            for item in answer.get(part, []):
                assert "proteins" not in item


def test_no_approved_card_has_the_key_on_hand_built_cards():
    disease = Disease("TEST_0000001", "test disease")
    target = gene(genetic_association=0.9, literature=0.9)

    def path(name, medicine_id, link):
        form = MedicineForm(medicine_id, name, best_stage="APPROVAL", disease_stage=link,
                            withdrawn=False)
        return Path(Medicine(name, (form,)), target, disease, ("ANTAGONIST",), 0.6,
                    (f"https://example.org/{medicine_id}",))

    found = api._Found(disease, sort_paths([
        path("NEWONE", "CHEMBL9001", None),
        path("STUDIED", "CHEMBL9002", "PHASE_2"),
        path("APPROVEDHERE", "CHEMBL9003", "APPROVAL"),
    ]), [], [], [])
    with patch.object(api, "_find", return_value=found), \
            patch.object(api, "looks_wrong", return_value=set()), \
            patch.object(api, "pushes_wrong_way", return_value=set()):
        answer = TestClient(api.app).get(
            "/api/clues", params={"disease_id": disease.id}).json()
    both = ["genetic_association", "literature"]
    assert answer["new_clues"][0]["proteins"][0][KEY] == both
    assert answer["being_studied"][0]["proteins"][0][KEY] == both
    assert [item["medicine"] for item in answer["approved"]] == ["Approvedhere"]
    assert KEY not in answer["approved"][0]["proteins"][0]


def test_the_clue_order_and_the_points_do_not_change(huntington, t2d, nmo):
    for disease_id, answer in ((HUNTINGTON, huntington), (T2D, t2d), (NMO, nmo)):
        before = page_answer(disease_id, without_scores)
        after = copy.deepcopy(answer)
        for part in ("new_clues", "being_studied"):
            for item in after[part]:
                for found in item["proteins"]:
                    found.pop(KEY, None)
        assert after == before, disease_id


# ---- 3. the page, as text ----

def test_the_page_types_the_start_words_and_six_names_once_and_they_match_the_engine():
    assert PAGE.count(START) == 1
    assert f'const EVIDENCE_START = "{engine.EVIDENCE_START}";' in PAGE
    block = PAGE[PAGE.index("const EVIDENCE_NAMES = {"):]
    block = block[:block.index("};")]
    pairs = tuple(re.findall(r'^\s*(\w+): "([^"]*)",?$', block, flags=re.M))
    assert pairs == tuple(engine.EVIDENCE_NAMES.items()) == NAMES
    for _, name in NAMES:
        assert PAGE.count(f'"{name}"') == 1


def test_the_page_never_names_the_medicine_itself():
    block = PAGE[PAGE.index("const EVIDENCE_NAMES = {"):]
    block = block[:block.index("};")]
    assert "known_drug" not in block and "clinical" not in block


def test_the_line_has_its_own_template_with_no_words_in_it():
    template = PAGE[PAGE.index('<template id="protein-evidence-template">'):]
    template = template[:template.index("</template>") + len("</template>")]
    assert template == ('<template id="protein-evidence-template">'
                        '<p class="protein-evidence" data-slot="protein-evidence"></p></template>')


def test_the_safety_and_direction_lines_are_unchanged():
    assert SAFETY_LINE in re.sub(r"\s+", " ", PAGE)
    card = PAGE[PAGE.index('<template id="card-template">'):]
    card = card[:card.index("</template>")]
    assert '<p class="direction-note">' + DIRECTION_LINE + "</p>" in card


# ---- 4. the page, in a real browser, at phone width ----

BROWSER_SCRIPT = r"""
"use strict";
const fs = require("fs");
const { chromium } = require("playwright");
const PAGE = fs.readFileSync(process.argv[1], "utf-8");
const ANSWERS = JSON.parse(fs.readFileSync(process.argv[2], "utf-8"));
const SITE = "http://moonlight.test";

function readTab(panel) {
  return [...document.querySelectorAll("#" + panel + " .card")].map(card => ({
    name: card.querySelector('[data-slot="medicine-name"]').textContent,
    rows: [...card.querySelectorAll('[data-slot="protein"]')].map(row => {
      const id = row.querySelector(".protein-id");
      const lines = [...row.querySelectorAll('[data-slot="protein-evidence"]')];
      const sentence = row.querySelector('[data-slot="protein-function"]');
      return {
        symbol: id.textContent,
        lines: lines.map(line => line.textContent),
        children: lines.map(line => line.children.length),
        underTheRow: lines.every(line => line.getBoundingClientRect().top
          >= id.getBoundingClientRect().bottom - 1 || !card.checkVisibility()),
        afterTheSentence: lines.every(line => !sentence
          || !!(sentence.compareDocumentPosition(line) & Node.DOCUMENT_POSITION_FOLLOWING)),
        insideTheCard: lines.every(line => line.getBoundingClientRect().right
          <= card.getBoundingClientRect().right + 1),
      };
    }),
  }));
}

async function oneSearch(browser, answer) {
  const context = await browser.newContext({ viewport: { width: 390, height: 844 } });
  const page = await context.newPage();
  const errors = [];
  page.on("pageerror", problem => errors.push(String(problem)));
  await context.route("**/*", route => {
    const url = route.request().url();
    if (url === SITE + "/" || url.startsWith(SITE + "/?"))
      return route.fulfill({ contentType: "text/html; charset=utf-8", body: PAGE });
    if (url.startsWith(SITE + "/api/clues?"))
      return route.fulfill({ contentType: "application/json", body: JSON.stringify(answer) });
    if (url.startsWith(SITE + "/api/explain?"))
      return route.fulfill({ status: 404, contentType: "application/json", body: "{}" });
    return route.abort();
  });
  await page.goto(SITE + "/?disease=MONDO_TEST");
  await page.waitForSelector("#found", { state: "visible" });
  const out = { errors };
  for (const box of await page.$$("details")) await box.evaluate(el => { el.open = true; });
  await page.click("#tab-clues");
  await page.waitForTimeout(300);
  out.clues = await page.evaluate(readTab, "panel-clues");
  await page.click("#tab-trials");
  await page.waitForTimeout(300);
  out.trials = await page.evaluate(readTab, "panel-trials");
  await page.click("#tab-approved");
  await page.waitForTimeout(300);
  out.approved = await page.evaluate(readTab, "panel-approved");
  out.linesOnThePage = await page.evaluate(
    () => document.querySelectorAll('[data-slot="protein-evidence"]').length);
  out.sideways = await page.evaluate(
    () => document.documentElement.scrollWidth > document.documentElement.clientWidth);
  await context.close();
  return out;
}

(async () => {
  const browser = await chromium.launch();
  const out = {};
  for (const name of Object.keys(ANSWERS)) out[name] = await oneSearch(browser, ANSWERS[name]);
  await browser.close();
  console.log(JSON.stringify(out));
})().catch(problem => { console.error(problem); process.exit(1); });
"""


@pytest.fixture(scope="module")
def seen(huntington, t2d, nmo, tmp_path_factory):
    node = shutil.which("node")
    if not node or subprocess.run(
            [node, "-e", "require('playwright')"], capture_output=True).returncode:
        pytest.skip("needs node with playwright to open a real browser")
    # An Approved card whose protein was sent the key by mistake still shows no line.
    tampered = copy.deepcopy(t2d)
    for item in tampered["approved"]:
        for found in item["proteins"]:
            found[KEY] = ["genetic_association"]
    answers = {"huntington": huntington, "t2d": t2d, "nmo": nmo, "tampered": tampered}
    answers_file = tmp_path_factory.mktemp("gene_evidence") / "answers.json"
    answers_file.write_text(json.dumps(answers), encoding="utf-8")
    run = subprocess.run(
        [node, "-e", BROWSER_SCRIPT, str(PAGE_FILE), str(answers_file)],
        capture_output=True, text=True, timeout=240, cwd=str(ROOT))
    assert run.returncode == 0, run.stderr[-3000:]
    out = json.loads(run.stdout)
    for name in answers:
        assert out[name]["errors"] == [], name
    return out


def card_in(read, name):
    found = [card for card in read if card["name"] == name]
    assert found, name
    return found[0]


def lines_by_symbol(card):
    return {row["symbol"]: row["lines"] for row in card["rows"]}


def test_browser_example_huntington_lamotrigine(seen):
    card = card_in(seen["huntington"]["clues"], "Lamotrigine")
    assert lines_by_symbol(card) == {
        "SCN4A": ["Linked to this disease by: studies in animals, found together in "
                  "research papers."],
        "SCN8A": ["Linked to this disease by: studies in animals."],
        "SCN1A": ["Linked to this disease by: studies in animals."],
        "SCN9A": [],
        "SCN11A": [],
    }


def test_browser_example_t2d_three_names_on_an_in_trials_card(seen):
    card = card_in(seen["t2d"]["trials"], "Gliclazide")
    assert lines_by_symbol(card) == {
        "KCNJ11": ["Linked to this disease by: inherited gene changes, found together "
                   "in research papers."],
        "ABCC8": ["Linked to this disease by: inherited gene changes, studies in animals, "
                  "found together in research papers."],
    }


def test_browser_example_nmo_papers_alone(seen):
    card = card_in(seen["nmo"]["clues"], "Siltuximab")
    assert lines_by_symbol(card) == {
        "IL6": ["Linked to this disease by: found together in research papers."]}


def test_browser_every_clue_card_shows_what_the_api_sent(seen, huntington, t2d, nmo):
    names = dict(NAMES)
    for key, answer in (("huntington", huntington), ("t2d", t2d), ("nmo", nmo)):
        for tab, part in (("clues", "new_clues"), ("trials", "being_studied")):
            sent = {item["medicine"]: item for item in answer[part]}
            for card in seen[key][tab]:
                if card["name"] not in sent:
                    continue
                for row, found in zip(card["rows"], sent[card["name"]]["proteins"]):
                    want = ([START + ", ".join(names[kind] for kind in found[KEY]) + "."]
                            if KEY in found else [])
                    assert row["lines"] == want, (key, card["name"], row["symbol"])
                    assert row["children"] == [2] * len(want)  # ticket 3.5: start and names in two parts
                    assert row["underTheRow"] and row["afterTheSentence"]
                    assert row["insideTheCard"]


def test_browser_no_approved_card_shows_the_line(seen):
    for key in ("huntington", "t2d", "nmo", "tampered"):
        assert seen[key]["approved"]
        for card in seen[key]["approved"]:
            for row in card["rows"]:
                assert row["lines"] == [], (key, card["name"])


def test_browser_nothing_runs_sideways_at_phone_width(seen):
    for key in ("huntington", "t2d", "nmo"):
        assert not seen[key]["sideways"], key


# ---- 5. the printed page (decision 3 of 25 Nov) ----
# The New clues table of the register shows, under each medicine, every
# protein whose card shows the protein sentence (ticket 3.8) or the evidence
# line, with those lines in the card's words. Approved rows get neither.

PRINT_SCRIPT = r"""
"use strict";
const fs = require("fs");
const { chromium } = require("playwright");
const PAGE = fs.readFileSync(process.argv[1], "utf-8");
const ANSWERS = JSON.parse(fs.readFileSync(process.argv[2], "utf-8"));
const SHOT = process.argv[3];
const SITE = "http://moonlight.test";

function readScreen() {
  return [...document.querySelectorAll("#panel-clues .card")].map(card => ({
    name: card.querySelector('[data-slot="medicine-name"]').textContent,
    proteins: [...card.querySelectorAll('[data-slot="protein"]')].map(row => ({
      symbol: row.querySelector(".protein-id").textContent,
      lines: [...row.querySelectorAll('[data-slot="protein-function"], [data-slot="protein-evidence"]')]
        .map(line => line.textContent),
    })),
  }));
}

function readRegister() {
  const table = id => [...document.querySelectorAll("#" + id + " > tbody")].map(body => ({
    name: body.rows[0].cells[0].innerText.trim(),
    notes: [...body.querySelectorAll('tr[data-row="protein-note"]')].map(row => ({
      symbol: row.querySelector(".register-protein-id").textContent,
      lines: [...row.querySelectorAll("[data-reg-line]")].map(line => line.textContent),
      spans: row.cells[0].colSpan,
    })),
  }));
  const approvedArea = [document.getElementById("register-approved"),
                        document.querySelector('#register [data-reg="approved-boxes"]')];
  return {
    clues: table("register-clues"),
    approved: table("register-approved"),
    approvedNotes: approvedArea.reduce((n, el) => n + el.querySelectorAll(
      'tr[data-row="protein-note"], [data-reg-line]').length, 0),
    approvedText: approvedArea.map(el => el.innerText).join("\n"),
    sideways: document.documentElement.scrollWidth > document.documentElement.clientWidth,
  };
}

(async () => {
  const browser = await chromium.launch();
  const out = {};
  for (const name of Object.keys(ANSWERS)) {
    const context = await browser.newContext({ viewport: { width: 390, height: 844 },
                                               deviceScaleFactor: SHOT ? 2 : 1 });
    const page = await context.newPage();
    const errors = [];
    page.on("pageerror", problem => errors.push(String(problem)));
    await page.addInitScript(() => { window.print = () => {}; });
    await context.route("**/*", route => {
      const url = route.request().url();
      if (url === SITE + "/" || url.startsWith(SITE + "/?"))
        return route.fulfill({ contentType: "text/html; charset=utf-8", body: PAGE });
      if (url.startsWith(SITE + "/api/clues?"))
        return route.fulfill({ contentType: "application/json", body: JSON.stringify(ANSWERS[name]) });
      if (url.startsWith(SITE + "/api/explain?"))
        return route.fulfill({ status: 404, contentType: "application/json", body: "{}" });
      return route.abort();
    });
    await page.goto(SITE + "/?disease=" + ANSWERS[name].disease.id);
    await page.waitForSelector("#found", { state: "visible" });
    await page.click("#tab-clues");
    await page.waitForTimeout(300);
    const screen = await page.evaluate(readScreen);
    await page.click("#print-page");
    await page.waitForTimeout(300);
    out[name] = { screen, register: await page.evaluate(readRegister), errors };
    if (SHOT && name === "t2d") {
      await page.emulateMedia({ media: "print" });
      const first = page.locator("#register-clues > tbody").first();
      await first.evaluate(el => el.scrollIntoView());
      await page.locator("#register-clues").screenshot({ path: SHOT });
    }
    await context.close();
  }
  await browser.close();
  console.log(JSON.stringify(out));
})().catch(problem => { console.error(problem); process.exit(1); });
"""


@pytest.fixture(scope="module")
def printed(huntington, t2d, nmo, pah, tmp_path_factory):
    node = shutil.which("node")
    if not node or subprocess.run(
            [node, "-e", "require('playwright')"], capture_output=True).returncode:
        pytest.skip("needs node with playwright to open a real browser")
    answers = {"huntington": huntington, "t2d": t2d, "nmo": nmo, "pah": pah}
    answers_file = tmp_path_factory.mktemp("gene_evidence_print") / "answers.json"
    answers_file.write_text(json.dumps(answers), encoding="utf-8")
    run = subprocess.run(
        [node, "-e", PRINT_SCRIPT, str(PAGE_FILE), str(answers_file), ""],
        capture_output=True, text=True, timeout=240, cwd=str(ROOT))
    assert run.returncode == 0, run.stderr[-3000:]
    out = json.loads(run.stdout)
    for name in answers:
        assert out[name]["errors"] == [], name
    return out


@pytest.mark.parametrize("name", ["huntington", "t2d", "nmo", "pah"])
def test_print_each_new_clue_shows_the_cards_protein_lines_word_for_word(printed, name):
    screen = {card["name"]: card for card in printed[name]["screen"]}
    rows = printed[name]["register"]["clues"]
    assert rows
    seen_lines = 0
    for row in rows:
        card = screen[row["name"]]
        want = [{"symbol": protein["symbol"], "lines": protein["lines"], "spans": 5}
                for protein in card["proteins"] if protein["lines"]]
        assert row["notes"] == want, (name, row["name"])
        seen_lines += sum(len(note["lines"]) for note in row["notes"])
    assert seen_lines > 0


def test_print_example_t2d_mesalamine(printed):
    (row,) = [row for row in printed["t2d"]["register"]["clues"] if row["name"] == "Mesalamine"]
    (note,) = row["notes"]
    assert note["symbol"] == "PPARG"
    # PPARG's card shows no protein sentence (UniProt's is over 200 letters),
    # so the printed row has only the evidence line, as the card does.
    assert note["lines"] == [
        "Linked to this disease by: inherited gene changes, studies in animals, found "
        "together in research papers."]


def test_print_example_t2d_insulin_sentence_then_evidence(printed):
    """Clue 9 of type 2 diabetes. The print page holds the first 10 new clues."""
    (row,) = [row for row in printed["t2d"]["register"]["clues"]
              if row["name"] == "Insulin Susp Isophane Recombinant Human"]
    assert row["notes"] == [{"symbol": "INSR", "spans": 5, "lines": [
        "Receptor tyrosine kinase which mediates the pleiotropic actions of insulin.",
        "Linked to this disease by: inherited gene changes, studies in animals, found "
        "together in research papers."]}]


def test_print_example_nmo_papers_alone(printed):
    rows = {row["name"]: row for row in printed["nmo"]["register"]["clues"]}
    lines = [line for row in rows.values() for note in row["notes"] for line in note["lines"]]
    assert "Linked to this disease by: found together in research papers." in lines


@pytest.mark.parametrize("name", ["huntington", "t2d", "nmo", "pah"])
def test_print_approved_rows_get_neither_line(printed, name):
    register = printed[name]["register"]
    assert register["approved"] or name == "x"
    assert register["approvedNotes"] == 0
    assert "Linked to this disease by" not in register["approvedText"]
    for row in register["approved"]:
        assert row["notes"] == []


def test_print_nothing_runs_sideways(printed):
    for name in printed:
        assert not printed[name]["register"]["sideways"], name
