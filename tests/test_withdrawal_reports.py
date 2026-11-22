"""Ticket 2.22. Withdrawal reports hide a card on the Approved tab.

Kashish's decisions, 22 Nov 2026:

1. On the Approved tab (the main list and both folded boxes), a medicine is
   not shown when any report on the disease's own list has stage WITHDRAWAL.
2. A card in a folded box is judged by either list: the list of the disease
   the person searched for, or the list of the narrower or wider disease
   the card came from. (Her answer in this session, 22 Nov.)
3. The line, her words exactly:
   "3 medicines are not shown here. The database records a withdrawal for
   them somewhere."
   With one medicine:
   "1 medicine is not shown here. The database records a withdrawal for it
   somewhere."
4. The number counts medicines hidden by the old withdrawn flag or by the
   new report. A medicine hidden by both is one medicine.
5. No line when the number is zero.

Her example: haemophilia A (MONDO_0010602). Octocog alfa is hidden.
Roctavian stays.

A WITHDRAWAL report is one entry of "clinicalReports" whose "clinicalStage"
is "WITHDRAWAL". The old withdrawn flag is a different field: a
"drugWarnings" entry whose "warningType" is "Withdrawn".

Every test asks the way the page does, GET /api/clues, so nothing here
says how the engine must work inside. The two names this file chooses are
the place the API sends the line, "not_shown_line", and the page's place
for it, id="not-shown-line".

Checked against fixtures/probe_p5/withdrawn_reports.csv on the branch
probe-baseline: its rows for haemophilia A (1), asthma (5), breast cancer
(2) and Duchenne muscular dystrophy (1) are the medicines these tests
expect to be hidden. Acute lymphoblastic leukemia is not one of that
study's 50 diseases, so its test was worked out from the saved lists only.

Saved files only: fixtures/withdrawal_reports/ (haemophilia A, copied from
probe-baseline), fixtures/narrower_box/ (ticket 2.14) and
fixtures/no_regulator/ (ticket 2.17). No network.
"""

import json
import pathlib
import re
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from moonlight import api, explain

ROOT = pathlib.Path(__file__).resolve().parent.parent
FIXTURES = ROOT / "fixtures"
HAEMOPHILIA_FILES = FIXTURES / "withdrawal_reports"
NARROWER_BOX_FILES = FIXTURES / "narrower_box"
NO_REGULATOR_FILES = FIXTURES / "no_regulator"
PAGE = (ROOT / "web" / "index.html").read_text(encoding="utf-8")

# (the folder its saved answers are in, the disease id)
HAEMOPHILIA_A = (HAEMOPHILIA_FILES, "MONDO_0010602")
ASTHMA = (NARROWER_BOX_FILES, "MONDO_0004979")
BREAST_CANCER = (NARROWER_BOX_FILES, "MONDO_0007254")
PAH = (NARROWER_BOX_FILES, "MONDO_0015924")  # pulmonary arterial hypertension
ALL = (NARROWER_BOX_FILES, "MONDO_0004967")  # acute lymphoblastic leukemia
DUCHENNE = (NO_REGULATOR_FILES, "MONDO_0010679")
SARCOIDOSIS = (NO_REGULATOR_FILES, "MONDO_0019338")

# Kashish's words, exactly. Changing them needs her approval.
MANY = " medicines are not shown here. The database records a withdrawal for them somewhere."
ONE_LINE = "1 medicine is not shown here. The database records a withdrawal for it somewhere."
THREE_LINE = "3" + MANY

LINE_KEY = "not_shown_line"  # where /api/clues sends the line
LINE_ID = "not-shown-line"  # the page's place for it

# ---- haemophilia A ----
OCTOCOG_ALFA = "CHEMBL4297873"
ROCTAVIAN = "CHEMBL4297579"  # its database name is valoctocogene roxaparvovec
HEMOPHILIA = "MONDO_0018660"  # a wider group haemophilia A is filed under
# The links of octocog alfa's three WITHDRAWAL reports, as the CSV has them.
OCTOCOG_WITHDRAWAL_LINKS = [
    "https://www.ema.europa.eu/en/medicines/human/EPAR/kogenate-bayer",
    "https://www.ema.europa.eu/en/medicines/human/EPAR/helixate-nexgen",
    "https://www.ema.europa.eu/en/medicines/human/EPAR/iblias",
]
# The main list today without octocog alfa, in today's A to Z order.
HAEMOPHILIA_MAIN_17 = [
    "CHEMBL4594584",  # antihemophilic factor, pegylated
    "CHEMBL4297730",  # concizumab
    "CHEMBL5315069",  # damoctocog alfa pegol
    "CHEMBL5095275",  # efanesoctocog alfa
    "CHEMBL4297945",  # efmoroctocog alfa
    "CHEMBL3833393",  # emicizumab
    "CHEMBL2108334",  # eptacog alfa (activated)
    "CHEMBL5315078",  # eptacog beta (activated)
    "CHEMBL4594603",  # lonoctocog alfa
    "CHEMBL3990039",  # marstacimab
    "CHEMBL2109137",  # moroctocog alfa
    "CHEMBL2108319",  # simoctocog alfa
    "CHEMBL5315075",  # susoctocog alfa
    "CHEMBL877",      # tranexamic acid
    "CHEMBL2108286",  # turoctocog alfa
    "CHEMBL5315071",  # turoctocog alfa pegol
    ROCTAVIAN,
]
# The wider-group box today. None of these has a WITHDRAWAL report.
HAEMOPHILIA_WIDER_11 = [
    "CHEMBL1046", "CHEMBL2108282", "CHEMBL4297986", "CHEMBL2109205", "CHEMBL1466",
    "CHEMBL3989529", "CHEMBL2108122", "CHEMBL1550", "CHEMBL1201651", "CHEMBL2108110",
    "CHEMBL4298126",
]

# ---- asthma: the five the CSV names, all on the main list today ----
ASTHMA_FIVE = {
    "CHEMBL1201295": "bitolterol",
    "CHEMBL1370": "budesonide",
    "CHEMBL1473": "fluticasone propionate",
    "CHEMBL1256786": "formoterol",
    "CHEMBL1263": "salmeterol",
}

# ---- breast cancer ----
FORMESTANE = "CHEMBL132530"  # main list today. WITHDRAWAL report on breast cancer's list.
IBANDRONIC_ACID = "CHEMBL997"  # wider-group box today. WITHDRAWAL report on the wider list.
NOMIFENSINE = "CHEMBL273575"  # the old flag AND a WITHDRAWAL report. Hidden already.
# On the main list. Their only WITHDRAWAL reports are on a narrower or wider
# disease's list, not on breast cancer's own. They stay.
BREAST_CANCER_STAY = {
    "CHEMBL1201583": "bevacizumab",
    "CHEMBL1773": "capecitabine",
    "CHEMBL92": "docetaxel",
    "CHEMBL53463": "doxorubicin",
    "CHEMBL428647": "paclitaxel",
}

# ---- acute lymphoblastic leukemia ----
ALL_NARROWER_GO = {
    "CHEMBL1201587": "alemtuzumab",
    "CHEMBL3039502": "duvelisib",
    "CHEMBL1201836": "ofatumumab",
}
PIXANTRONE = "CHEMBL167731"  # wider-group box today
RITUXIMAB = "CHEMBL1201576"  # main list. A WITHDRAWAL report only on another list.

SITAXENTAN = "CHEMBL282724"  # PAH: the old flag AND a WITHDRAWAL report
ATALUREN = "CHEMBL256997"  # Duchenne: a WITHDRAWAL report and no approval report


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def saved_post_json(folder):
    """Stands in for fetch._post_json with the files in one fixtures folder."""
    def post_json(body):
        assert set(body) == {"query", "variables"}
        query, variables = body["query"], body["variables"]
        if "targetId" in variables:
            return load(folder / "target_drugs" / f"{variables['targetId']}.response.json")
        disease_id = variables["diseaseId"]
        if "parents" in query:
            return load(folder / "family" / f"{disease_id}.response.json")
        if "associatedTargets" in query:
            return load(folder / "associated_targets" / f"{disease_id}.response.json")
        if "drugAndClinicalCandidates" in query:
            return load(folder / "disease_drugs" / f"{disease_id}.response.json")
        return load(folder / "disease" / f"{disease_id}.response.json")
    return post_json


def no_saved_answer(body):
    raise AssertionError(f"A test asked Open Targets with no saved answer: {body['variables']}")


@pytest.fixture(autouse=True)
def offline():
    """No test may reach Open Targets or Gemini. Real HTTP is an error."""
    explain.forget_everything()
    api.forget_visitors()
    with patch("moonlight.fetch._post_json", side_effect=no_saved_answer), \
            patch("requests.request", side_effect=AssertionError("network used")), \
            patch("requests.post", side_effect=AssertionError("network used")), \
            patch("requests.get", side_effect=AssertionError("network used")), \
            patch("requests.sessions.Session.request",
                  side_effect=AssertionError("network used")):
        yield
    explain.forget_everything()


def clues_answer(post_json, disease_id):
    """What GET /api/clues answers, with Open Targets replaced by post_json."""
    api.forget_visitors()
    with patch("moonlight.fetch._post_json", side_effect=post_json):
        response = TestClient(api.app).get("/api/clues", params={"disease_id": disease_id})
    assert response.status_code == 200
    return response.json()


@pytest.fixture(scope="module")
def page_of():
    """Each saved disease's /api/clues answer, worked out once."""
    made = {}

    def get(where):
        folder, disease_id = where
        if disease_id not in made:
            made[disease_id] = clues_answer(saved_post_json(folder), disease_id)
        return made[disease_id]

    return get


def ids(cards):
    return [card["id"] for card in cards]


def main_list(answer):
    return ids(answer["approved"])


def narrower_box(answer):
    return ids(answer.get("narrower", []))


def wider_box(answer):
    return ids(answer.get("wider_group", []))


def approved_tab(answer):
    """Every card on the Approved tab: the main list and both folded boxes."""
    return main_list(answer) + narrower_box(answer) + wider_box(answer)


def anywhere(answer):
    """Every card on the page, in all three tabs."""
    return approved_tab(answer) + ids(answer["being_studied"]) + ids(answer["new_clues"])


def rows_of(folder, disease_id):
    answer = load(folder / "disease_drugs" / f"{disease_id}.response.json")
    return answer["data"]["disease"]["drugAndClinicalCandidates"]["rows"]


def reports_of(folder, disease_id, family_id):
    """Read straight from a saved list: every report on the rows of one
    medicine and its tablet forms."""
    found = []
    for row in rows_of(folder, disease_id):
        drug = row["drug"]
        parent = drug["parentMolecule"]
        if (parent["id"] if parent else drug["id"]) == family_id:
            found += row["clinicalReports"]
    return found


def withdrawal_links(folder, disease_id, family_id):
    return [report["url"] for report in reports_of(folder, disease_id, family_id)
            if report["clinicalStage"] == "WITHDRAWAL"]


def has_old_flag(folder, disease_id, family_id):
    """Read straight from a saved list: does the medicine, or a form of it,
    carry the old "Withdrawn" warning?"""
    for row in rows_of(folder, disease_id):
        drug = row["drug"]
        parent = drug["parentMolecule"]
        if (parent["id"] if parent else drug["id"]) != family_id:
            continue
        for molecule in [drug] + ([parent] if parent else []) + drug["childMolecules"]:
            for warning in molecule.get("drugWarnings") or []:
                if warning["warningType"].lower() == "withdrawn":
                    return True
    return False


# ---- the saved answers say what the ticket says (these read the files only) ----

def test_the_saved_list_gives_octocog_alfa_the_three_withdrawal_reports_in_the_csv():
    folder, disease_id = HAEMOPHILIA_A
    assert withdrawal_links(folder, disease_id, OCTOCOG_ALFA) == OCTOCOG_WITHDRAWAL_LINKS
    # It is not a medicine the old flag already hides.
    assert not has_old_flag(folder, disease_id, OCTOCOG_ALFA)


def test_the_saved_list_gives_roctavian_no_withdrawal_report():
    folder, disease_id = HAEMOPHILIA_A
    reports = reports_of(folder, disease_id, ROCTAVIAN)
    # The id is Roctavian's: one of its reports is the regulator's Roctavian page.
    assert any(report["url"].endswith("/EPAR/roctavian-0") for report in reports)
    assert withdrawal_links(folder, disease_id, ROCTAVIAN) == []


# ---- Kashish's example: haemophilia A ----

def test_example_octocog_alfa_is_not_shown_on_the_approved_tab(page_of):
    answer = page_of(HAEMOPHILIA_A)
    assert OCTOCOG_ALFA not in main_list(answer)


def test_example_octocog_alfa_does_not_move_into_a_folded_box(page_of):
    # The wider group "hemophilia" lists octocog alfa as approved too, and that
    # list has no WITHDRAWAL report for it. It must not pop up in the box.
    folder, _ = HAEMOPHILIA_A
    assert withdrawal_links(folder, HEMOPHILIA, OCTOCOG_ALFA) == []
    answer = page_of(HAEMOPHILIA_A)
    assert OCTOCOG_ALFA not in approved_tab(answer)


def test_example_octocog_alfa_is_on_no_tab_and_is_never_named(page_of):
    answer = page_of(HAEMOPHILIA_A)
    assert OCTOCOG_ALFA not in anywhere(answer)
    # It is approved for this disease, so it is not a clue either.
    cards = (answer["approved"] + answer.get("narrower", []) + answer.get("wider_group", [])
             + answer["being_studied"] + answer["new_clues"])
    names = {card["medicine"].lower() for card in cards}
    names |= {form.lower() for card in cards for form in card.get("forms", [])}
    assert "octocog alfa" not in names


def test_example_roctavian_stays(page_of):
    answer = page_of(HAEMOPHILIA_A)
    assert main_list(answer).count(ROCTAVIAN) == 1
    (card,) = [card for card in answer["approved"] if card["id"] == ROCTAVIAN]
    assert card["medicine"] == "Valoctocogene Roxaparvovec"


def test_example_the_other_seventeen_stay_in_the_same_a_to_z_order(page_of):
    assert main_list(page_of(HAEMOPHILIA_A)) == HAEMOPHILIA_MAIN_17


def test_example_the_wider_group_box_keeps_its_eleven_cards(page_of):
    answer = page_of(HAEMOPHILIA_A)
    assert wider_box(answer) == HAEMOPHILIA_WIDER_11
    assert narrower_box(answer) == []


def test_example_the_line_counts_two_for_haemophilia_a(page_of):
    # Octocog alfa: hidden by the new report.
    # Aprotinin: approved for a wider group (hemorrhagic disease) and hidden
    # by the old withdrawn flag. It is counted and never named.
    assert page_of(HAEMOPHILIA_A)[LINE_KEY] == "2" + MANY


# ---- the main list: asthma, the five in the CSV ----

@pytest.mark.parametrize("medicine_id", sorted(ASTHMA_FIVE), ids=lambda i: ASTHMA_FIVE[i])
def test_asthma_each_of_the_five_in_the_csv_is_not_shown(page_of, medicine_id):
    folder, disease_id = ASTHMA
    assert withdrawal_links(folder, disease_id, medicine_id)  # the saved list says so
    assert not has_old_flag(folder, disease_id, medicine_id)
    assert medicine_id not in anywhere(page_of(ASTHMA))


def test_asthma_the_main_list_goes_from_70_cards_to_65(page_of):
    answer = page_of(ASTHMA)
    assert len(main_list(answer)) == 65
    assert narrower_box(answer) == [] and wider_box(answer) == []


def test_asthma_the_line_counts_the_old_flag_and_the_new_report_together(page_of):
    # 4 hidden by the old flag (ephedrine, fenoterol, iodinated glycerol and
    # metaproterenol, all approved for asthma) + 5 hidden by the new report.
    assert page_of(ASTHMA)[LINE_KEY] == "9" + MANY


# ---- the main list and a box: breast cancer ----

def test_breast_cancer_formestane_is_not_shown(page_of):
    folder, disease_id = BREAST_CANCER
    assert withdrawal_links(folder, disease_id, FORMESTANE)
    assert FORMESTANE not in anywhere(page_of(BREAST_CANCER))


def test_breast_cancer_ibandronic_acid_leaves_the_wider_group_box(page_of):
    # Breast cancer's own list has no WITHDRAWAL report for it. The wider
    # disease's list it came from has one. Either list is enough.
    folder, disease_id = BREAST_CANCER
    assert withdrawal_links(folder, disease_id, IBANDRONIC_ACID) == []
    answer = page_of(BREAST_CANCER)
    assert IBANDRONIC_ACID not in approved_tab(answer)
    assert len(wider_box(answer)) == 4


def test_breast_cancer_a_main_list_card_is_judged_by_its_own_list_only(page_of):
    # These five have a WITHDRAWAL report only on a narrower or wider
    # disease's list. Breast cancer's own list has none for them. They stay.
    folder, disease_id = BREAST_CANCER
    answer = page_of(BREAST_CANCER)
    for medicine_id in BREAST_CANCER_STAY:
        assert withdrawal_links(folder, disease_id, medicine_id) == []
        assert main_list(answer).count(medicine_id) == 1


def test_breast_cancer_the_tab_goes_from_73_2_and_5_cards_to_72_2_and_4(page_of):
    answer = page_of(BREAST_CANCER)
    assert len(main_list(answer)) == 72
    assert narrower_box(answer) == ["CHEMBL88", "CHEMBL417"]  # unchanged
    assert len(wider_box(answer)) == 4


def test_breast_cancer_the_line_is_kashishs_sentence_with_three(page_of):
    # Formestane (new report), ibandronic acid (new report, in a box) and
    # nomifensine. Nomifensine has the old flag AND a WITHDRAWAL report. It
    # is one medicine, so it is counted once.
    folder, disease_id = BREAST_CANCER
    assert has_old_flag(folder, disease_id, NOMIFENSINE)
    assert withdrawal_links(folder, disease_id, NOMIFENSINE)
    answer = page_of(BREAST_CANCER)
    assert NOMIFENSINE not in anywhere(answer)
    assert answer[LINE_KEY] == THREE_LINE


# ---- both folded boxes: acute lymphoblastic leukemia ----

@pytest.mark.parametrize("medicine_id", sorted(ALL_NARROWER_GO),
                         ids=lambda i: ALL_NARROWER_GO[i])
def test_all_a_card_leaves_the_narrower_box(page_of, medicine_id):
    assert medicine_id not in approved_tab(page_of(ALL))


def test_all_pixantrone_leaves_the_wider_group_box(page_of):
    assert PIXANTRONE not in approved_tab(page_of(ALL))


def test_all_the_tab_goes_from_15_13_and_12_cards_to_15_10_and_11(page_of):
    answer = page_of(ALL)
    assert len(main_list(answer)) == 15
    assert RITUXIMAB in main_list(answer)  # its WITHDRAWAL report is on another list
    assert len(narrower_box(answer)) == 10
    assert len(wider_box(answer)) == 11


def test_all_the_line_counts_the_four_box_cards(page_of):
    assert page_of(ALL)[LINE_KEY] == "4" + MANY


# ---- one medicine ----

def test_one_medicine_hidden_by_the_new_report_alone_gets_the_one_medicine_line(page_of):
    folder, disease_id = DUCHENNE
    assert withdrawal_links(folder, disease_id, ATALUREN)
    assert not has_old_flag(folder, disease_id, ATALUREN)
    answer = page_of(DUCHENNE)
    assert ATALUREN not in anywhere(answer)
    assert len(main_list(answer)) == 7  # 8 today
    assert answer[LINE_KEY] == ONE_LINE


def test_one_medicine_hidden_by_the_old_flag_gets_the_one_medicine_line(page_of):
    # Sitaxentan is approved for PAH and has the old flag. It is hidden
    # today, with no line. It has a WITHDRAWAL report too: still one medicine.
    folder, disease_id = PAH
    assert has_old_flag(folder, disease_id, SITAXENTAN)
    assert withdrawal_links(folder, disease_id, SITAXENTAN)
    answer = page_of(PAH)
    assert SITAXENTAN not in anywhere(answer)
    assert answer[LINE_KEY] == ONE_LINE


def test_pah_shows_the_same_cards_as_today(page_of):
    # No card on PAH's Approved tab has a WITHDRAWAL report. Nothing moves.
    answer = page_of(PAH)
    assert len(main_list(answer)) == 13
    assert narrower_box(answer) == []
    assert wider_box(answer) == ["CHEMBL770"]  # tolazoline


# ---- zero ----

def test_no_line_when_nothing_is_hidden(page_of):
    answer = page_of(SARCOIDOSIS)
    assert LINE_KEY not in answer
    assert len(main_list(answer)) == 5  # the same five as today


# ---- the line: Kashish's words, and nothing named ----

def test_the_words_in_this_file_are_kashishs_exactly():
    assert THREE_LINE == ("3 medicines are not shown here. The database records a "
                          "withdrawal for them somewhere.")
    assert ONE_LINE == ("1 medicine is not shown here. The database records a "
                        "withdrawal for it somewhere.")


@pytest.mark.parametrize("where", [HAEMOPHILIA_A, ASTHMA, BREAST_CANCER, ALL, DUCHENNE, PAH],
                         ids=["haemophilia A", "asthma", "breast cancer", "ALL", "Duchenne",
                              "PAH"])
def test_the_line_is_a_number_and_her_words_and_names_no_medicine(page_of, where):
    line = page_of(where)[LINE_KEY]
    assert re.fullmatch(r"(1 medicine is not shown here\. The database records a withdrawal "
                        r"for it somewhere\.|([2-9]|[1-9][0-9]+) medicines are not shown here\. "
                        r"The database records a withdrawal for them somewhere\.)", line)


def test_the_line_does_not_change_the_counts_under_the_other_tabs(page_of):
    # "left_out" is still there with its two numbers. This ticket does not
    # say what they become, so only their shape is checked.
    answer = page_of(HAEMOPHILIA_A)
    assert set(answer["left_out"]) == {"not_approved", "unclear_link"}
    assert all(isinstance(number, int) for number in answer["left_out"].values())


# ---- either list: a made-up disease ----
#
# In the 50 diseases of the study, every row with a WITHDRAWAL report is a
# row the database also calls approved. So no saved answer has a box card
# whose WITHDRAWAL report is on the searched disease's own list. These
# answers are made up to test that half of "either list".
#
# TESTOSIS has one narrower disease and one wider group.
#   NARROWINE: approved for the narrower disease. On TESTOSIS's own list it
#              has only a WITHDRAWAL report. Today: in the narrower box.
#   WIDINE:    the same, for the wider group. Today: in the wider-group box.
#   STAYINE:   approved for the narrower disease. No WITHDRAWAL report on
#              either list. It stays.

TESTOSIS, NARROW_TESTOSIS, WIDE_TESTOSIS = "T1", "T2", "T3"


def made_up_row(drug_id, name, stage, reports):
    return {
        "maxClinicalStage": stage,
        "drug": {"id": drug_id, "name": name, "maximumClinicalStage": "APPROVAL",
                 "drugWarnings": [], "parentMolecule": None, "childMolecules": []},
        "clinicalReports": reports,
    }


def made_up_report(stage, number):
    return {"url": f"https://example.org/record/{number}", "clinicalStage": stage,
            "source": "EMA Human Drugs"}


def made_up_approved(drug_id, name, number):
    return made_up_row(drug_id, name, "APPROVAL", [made_up_report("APPROVAL", number)])


def made_up_withdrawn_only(drug_id, name, number):
    return made_up_row(drug_id, name, "WITHDRAWAL", [made_up_report("WITHDRAWAL", number)])


def made_up_lists(own_rows):
    return {
        TESTOSIS: own_rows,
        NARROW_TESTOSIS: [made_up_approved("M1", "NARROWINE", 1),
                          made_up_approved("M3", "STAYINE", 3)],
        WIDE_TESTOSIS: [made_up_approved("M2", "WIDINE", 2)],
    }


def made_up_post_json(lists):
    def post_json(body):
        assert set(body) == {"query", "variables"}
        query, disease_id = body["query"], body["variables"]["diseaseId"]
        if "parents" in query:
            return {"data": {"disease": {
                "id": TESTOSIS, "name": "testosis",
                "parents": [{"id": WIDE_TESTOSIS, "name": "wide testosis"}],
                "children": [{"id": NARROW_TESTOSIS, "name": "narrow testosis"}]}}}
        if "associatedTargets" in query:
            return {"data": {"disease": {
                "id": TESTOSIS, "associatedTargets": {"count": 0, "rows": []}}}}
        if "drugAndClinicalCandidates" in query:
            rows = lists[disease_id]
            return {"data": {"disease": {"id": disease_id, "drugAndClinicalCandidates": {
                "count": len(rows), "rows": rows}}}}
        return {"data": {"disease": {
            "id": TESTOSIS, "name": "testosis", "description": "", "synonyms": []}}}
    return post_json


def test_made_up_with_no_withdrawal_report_all_three_are_in_their_boxes():
    # The made-up answers are read the way real ones are: this is today's page.
    answer = clues_answer(made_up_post_json(made_up_lists([])), TESTOSIS)
    assert main_list(answer) == []
    assert narrower_box(answer) == ["M1", "M3"]
    assert wider_box(answer) == ["M2"]
    assert LINE_KEY not in answer


def test_made_up_a_report_on_the_searched_diseases_own_list_hides_a_box_card():
    own_rows = [made_up_withdrawn_only("M1", "NARROWINE", 11),
                made_up_withdrawn_only("M2", "WIDINE", 12)]
    answer = clues_answer(made_up_post_json(made_up_lists(own_rows)), TESTOSIS)
    assert narrower_box(answer) == ["M3"]  # STAYINE stays
    assert wider_box(answer) == []
    assert "M1" not in anywhere(answer) and "M2" not in anywhere(answer)
    assert answer[LINE_KEY] == "2" + MANY


def test_made_up_one_box_card_hidden_gets_the_one_medicine_line():
    own_rows = [made_up_withdrawn_only("M2", "WIDINE", 12)]
    answer = clues_answer(made_up_post_json(made_up_lists(own_rows)), TESTOSIS)
    assert narrower_box(answer) == ["M1", "M3"]
    assert wider_box(answer) == []
    assert answer[LINE_KEY] == ONE_LINE


def test_made_up_a_report_of_any_other_stage_hides_nothing():
    # Only the stage word WITHDRAWAL counts, letter for letter.
    own_rows = [made_up_row("M1", "NARROWINE", "UNKNOWN", [made_up_report("UNKNOWN", 11)]),
                made_up_row("M2", "WIDINE", "UNKNOWN", [made_up_report("Withdrawn", 12)])]
    answer = clues_answer(made_up_post_json(made_up_lists(own_rows)), TESTOSIS)
    assert narrower_box(answer) == ["M1", "M3"]
    assert wider_box(answer) == ["M2"]
    assert LINE_KEY not in answer


# ---- the page: one place for the line, on the Approved tab ----

def approved_panel():
    return PAGE[PAGE.index('id="panel-approved"'):PAGE.index('id="panel-trials"')]


def test_the_page_has_one_place_for_the_line_on_the_approved_tab():
    assert PAGE.count(f'id="{LINE_ID}"') == 1
    assert approved_panel().count(f'id="{LINE_ID}"') == 1
    # Hidden, with no words in it, until the API sends some.
    assert re.search(rf'<p [^>]*id="{LINE_ID}"[^>]* hidden></p>', approved_panel())


def test_the_page_shows_the_apis_words_and_types_none_of_its_own():
    assert f'byId("{LINE_ID}").textContent = data.{LINE_KEY} || "";' in PAGE
    assert f'byId("{LINE_ID}").hidden = !data.{LINE_KEY};' in PAGE
    assert "not shown here" not in PAGE
    assert "records a withdrawal" not in PAGE


def test_the_safety_line_is_still_on_the_page():
    assert ("For learning and research exploration, not medical advice. Never start, "
            "stop or change any medicine without a doctor.") in PAGE
