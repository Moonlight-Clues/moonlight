"""Ticket 2.4. Each EXAMPLE from Kashish's paper graph is one test here.

These tests build Medicine records by hand. They read no files and use no
network.
"""

import pytest

from moonlight.filter import GROUPS, SHOWN_GROUPS, group_of, sort_paths
from moonlight.records import Disease, Medicine, MedicineForm, Path, Target


def form(name, best_stage, disease_stage=None, parent_id=None):
    return MedicineForm(
        id="ID_" + name.upper().replace(" ", "_"),
        name=name,
        best_stage=best_stage,
        disease_stage=disease_stage,
        parent_id=parent_id,
    )


def single(name, best_stage, disease_stage=None):
    """A medicine with only one form."""
    return Medicine(name=name, forms=(form(name, best_stage, disease_stage),))


def family(name, *forms):
    return Medicine(name=name, forms=forms)


# Example 1
def test_avanafil_approved_with_no_link_is_a_new_clue():
    assert group_of(single("Avanafil", "APPROVAL")) == "new_clue"


# Example 2
def test_tadalafil_approved_for_the_disease_is_already_approved():
    assert group_of(single("Tadalafil", "APPROVAL", "APPROVAL")) == "already_approved"


# Example 3
def test_udenafil_in_trials_for_the_disease_is_being_studied():
    assert group_of(single("Udenafil", "APPROVAL", "PHASE_2_3")) == "being_studied"


# Example 4
def test_gisadenafil_not_approved_anywhere_is_not_approved():
    assert group_of(single("Gisadenafil", "PHASE_2")) == "not_approved"


# Example 5
def test_bq123_question_1_wins_even_though_it_has_a_link():
    assert group_of(single("BQ-123", "PHASE_2", "PHASE_2")) == "not_approved"


# Example 6
def test_sparsentan_best_stage_is_not_the_link():
    assert group_of(single("Sparsentan", "APPROVAL")) == "new_clue"


# Example 7
def test_sildenafil_family_is_already_approved():
    sildenafil = family(
        "Sildenafil",
        form("Sildenafil", "APPROVAL", "PHASE_3"),
        form("Sildenafil Citrate", "APPROVAL", "APPROVAL", parent_id="ID_SILDENAFIL"),
    )
    assert group_of(sildenafil) == "already_approved"


# Example 8
def test_vardenafil_family_is_being_studied_and_tablet_form_is_not_a_new_clue():
    vardenafil = family(
        "Vardenafil",
        form("Vardenafil", "APPROVAL", "PHASE_3"),
        form("Vardenafil Hydrochloride", "APPROVAL", None, parent_id="ID_VARDENAFIL"),
    )
    assert group_of(vardenafil) == "being_studied"

    # The whole family travels as ONE path, so the tablet form cannot turn
    # up in the new-clue list on its own.
    sorted_paths = sort_paths([path_for(vardenafil)])
    assert sorted_paths["new_clue"] == []
    assert [p.medicine.name for p in sorted_paths["being_studied"]] == ["Vardenafil"]


# Example 9
def test_sitaxentan_family_is_already_approved():
    sitaxentan = family(
        "Sitaxentan",
        form("Sitaxentan", "APPROVAL", "APPROVAL"),
        form("Sitaxentan Sodium", "APPROVAL", "PHASE_3", parent_id="ID_SITAXENTAN"),
    )
    assert group_of(sitaxentan) == "already_approved"


# Example 10
def test_doxapram_family_with_no_link_is_a_new_clue():
    doxapram = family(
        "Doxapram",
        form("Doxapram", "APPROVAL"),
        form("Doxapram Hydrochloride", "APPROVAL", parent_id="ID_DOXAPRAM"),
    )
    assert group_of(doxapram) == "new_clue"


# The rest of the CONTRACT


@pytest.mark.parametrize(
    "stage",
    ["PHASE_4", "PHASE_3", "PHASE_2_3", "PHASE_2", "PHASE_1_2", "PHASE_1", "EARLY_PHASE_1"],
)
def test_every_phase_stage_for_the_disease_is_being_studied(stage):
    assert group_of(single("Testamil", "APPROVAL", stage)) == "being_studied"


@pytest.mark.parametrize("stage", ["WITHDRAWAL", "UNKNOWN"])
def test_withdrawal_or_unknown_link_is_unclear_link(stage):
    assert group_of(single("Testamil", "APPROVAL", stage)) == "unclear_link"


def test_not_approved_wins_over_an_unclear_link():
    assert group_of(single("Testamil", "PHASE_3", "WITHDRAWAL")) == "not_approved"


def test_only_new_clue_and_being_studied_are_shown():
    assert GROUPS == (
        "not_approved",
        "new_clue",
        "being_studied",
        "already_approved",
        "unclear_link",
    )
    assert SHOWN_GROUPS == ("new_clue", "being_studied")


PAH = Disease(id="MONDO_0015924", name="pulmonary arterial hypertension")
PDE5A = Target(id="ENSG00000138735", symbol="PDE5A", name="phosphodiesterase 5A", score=0.6)


def path_for(medicine):
    return Path(
        medicine=medicine,
        target=PDE5A,
        disease=PAH,
        action_types=("INHIBITOR",),
        score=0.6,
        sources=("Open Targets",),
    )


def test_sort_paths_puts_each_path_in_its_medicines_group():
    avanafil = path_for(single("Avanafil", "APPROVAL"))
    tadalafil = path_for(single("Tadalafil", "APPROVAL", "APPROVAL"))
    udenafil = path_for(single("Udenafil", "APPROVAL", "PHASE_2_3"))
    gisadenafil = path_for(single("Gisadenafil", "PHASE_2"))
    sparsentan = path_for(single("Sparsentan", "APPROVAL"))
    withdrawn = path_for(single("Testamil", "APPROVAL", "WITHDRAWAL"))

    result = sort_paths([avanafil, tadalafil, udenafil, gisadenafil, sparsentan, withdrawn])

    assert result == {
        "not_approved": [gisadenafil],
        "new_clue": [avanafil, sparsentan],  # same order they came in
        "being_studied": [udenafil],
        "already_approved": [tadalafil],
        "unclear_link": [withdrawn],
    }


def test_sort_paths_with_nothing_gives_every_group_empty():
    assert sort_paths([]) == {group: [] for group in GROUPS}


# =====================================================================
# Ticket 2.9. Withdrawn medicines are left out
# Kashish's decision, 2026-11-15: if any country took a medicine off the
# shelves, Moonlight leaves it out, even if other countries still sell it.
# =====================================================================

import json  # noqa: E402
import pathlib  # noqa: E402
from unittest.mock import patch  # noqa: E402

import requests  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

import cli  # noqa: E402
from moonlight import api, cache, engine, explain, fetch  # noqa: E402

from test_fetch import FIBRO, SIX, fibro_post_json, fibro_targets  # noqa: E402

FIXTURES = pathlib.Path(__file__).resolve().parent.parent / "fixtures"
PROBE = FIXTURES / "withdrawn_probe" / "fibromyalgia"
THREE = ("SLC6A4", "CACNA1H", "SLC6A2")


def told(name, best_stage, disease_stage=None, withdrawn=False, parent_id=None):
    """A form Open Targets was asked about: withdrawn is True or False."""
    return MedicineForm(
        id="ID_" + name.upper().replace(" ", "_"), name=name, best_stage=best_stage,
        disease_stage=disease_stage, parent_id=parent_id, withdrawn=withdrawn,
    )


def one(name, best_stage, disease_stage=None, withdrawn=False):
    return Medicine(name=name, forms=(told(name, best_stage, disease_stage, withdrawn),))


@pytest.fixture
def fibro_files():
    """The fibromyalgia files saved on 2026-11-15. Real HTTP is an error."""
    with patch("moonlight.fetch._post_json", side_effect=fibro_post_json), \
            patch("requests.request", side_effect=AssertionError("network used")), \
            patch("requests.post", side_effect=AssertionError("network used")), \
            patch("requests.get", side_effect=AssertionError("network used")), \
            patch("requests.sessions.Session.request",
                  side_effect=AssertionError("network used")):
        yield


def names_in(paths):
    """Every medicine name and form name in these paths, in capitals."""
    names = set()
    for path in paths:
        names.add(path.medicine.name.upper())
        names.update(form.name.upper() for form in path.medicine.forms)
    return names


# ---- Change 4: "is it approved?" No. STOP. ----

def test_29_a_withdrawn_medicine_with_no_link_is_not_approved_not_a_new_clue():
    assert group_of(one("Testamil", "APPROVAL")) == "new_clue"
    assert group_of(one("Testamil", "APPROVAL", withdrawn=True)) == "not_approved"


@pytest.mark.parametrize("link", [
    None, "APPROVAL", "PHASE_4", "PHASE_3", "PHASE_2_3", "PHASE_2", "PHASE_1_2",
    "PHASE_1", "EARLY_PHASE_1", "WITHDRAWAL", "UNKNOWN",
])
def test_29_a_withdrawn_medicine_is_not_approved_whatever_its_link(link):
    assert group_of(one("Testamil", "APPROVAL", link, withdrawn=True)) == "not_approved"


def test_29_a_medicine_that_was_asked_about_and_not_withdrawn_sorts_as_before():
    assert group_of(one("Testamil", "APPROVAL")) == "new_clue"
    assert group_of(one("Testamil", "APPROVAL", "APPROVAL")) == "already_approved"
    assert group_of(one("Testamil", "APPROVAL", "PHASE_3")) == "being_studied"
    assert group_of(one("Testamil", "PHASE_2")) == "not_approved"
    assert group_of(one("Testamil", "APPROVAL", "UNKNOWN")) == "unclear_link"


# Example 3
def test_29_example_3_a_family_with_one_withdrawn_form_is_left_out_as_a_whole():
    testamil = family(
        "Testamil",
        told("Testamil", "APPROVAL"),
        told("Testamil Sodium", "APPROVAL", parent_id="ID_TESTAMIL", withdrawn=True),
    )
    assert group_of(testamil) == "not_approved"

    tray = sort_paths([path_for(testamil)])
    assert [p.medicine.name for p in tray["not_approved"]] == ["Testamil"]
    assert tray["new_clue"] == [] and tray["being_studied"] == []


# Change 5
def test_29_change_5_when_it_is_not_known_the_filter_does_not_guess_withdrawn():
    # "Not known" is not "withdrawn". fetch.py is the one that says so.
    not_told = single("Testamil", "APPROVAL")
    assert not_told.withdrawn is None
    assert group_of(not_told) == "new_clue"


# Example 1
@pytest.mark.parametrize("symbol, name", [
    ("SLC6A4", "Sibutramine"),
    ("SLC6A4", "Nomifensine"),
    ("SLC6A4", "Indalpine"),
    ("CACNA1H", "Mibefradil"),
    ("CACNA1H", "Terodiline"),
    ("SLC6A2", "Phenylpropanolamine"),
])
def test_29_example_1_each_of_the_six_lands_in_not_approved(fibro_files, symbol, name):
    tray = engine.find_clues(FIBRO, fibro_targets(symbol))
    assert name.upper() in {p.medicine.name.upper() for p in tray["not_approved"]}
    for group in ("new_clue", "being_studied", "already_approved", "unclear_link"):
        assert not any(name.upper() in found for found in names_in(tray[group]))


def test_29_example_1_all_six_are_found_and_none_is_in_a_shown_group(fibro_files):
    tray = engine.find_clues(FIBRO, fibro_targets(*THREE))
    assert set(SIX) <= {p.medicine.name.upper() for p in tray["not_approved"]}
    shown = names_in(tray["new_clue"]) | names_in(tray["being_studied"])
    assert len(shown) > 10  # it really found clues
    assert [name for name in sorted(shown) if any(six in name for six in SIX)] == []


def test_29_no_shown_medicine_has_a_withdrawn_form(fibro_files):
    tray = engine.find_clues(FIBRO, fibro_targets(*THREE))
    for group in ("new_clue", "being_studied"):
        for path in tray[group]:
            assert path.medicine.withdrawn is False, path.medicine.name


# Example 2
def test_29_example_2_a_medicine_with_another_kind_of_warning_stays_where_it_was(fibro_files):
    # "Where it was": the groups worked out from the answers the probe saved
    # before this ticket, which hold no withdrawn field.
    def old_post_json(body):
        (file,) = PROBE.glob(f"*_{body['variables']['targetId']}.response.json")
        return json.loads(file.read_text(encoding="utf-8"))

    targets = fibro_targets(*THREE)
    with patch("moonlight.fetch._post_json", side_effect=old_post_json):
        before = {p.medicine.name: group_of(p.medicine)
                  for p in sum((fetch.fetch_paths(FIBRO, t) for t in targets), [])}
    after_paths = sum((fetch.fetch_paths(FIBRO, t) for t in targets), [])
    after = {p.medicine.name: group_of(p.medicine) for p in after_paths}

    assert before["DULOXETINE"] == after["DULOXETINE"] == "already_approved"
    assert before["VORTIOXETINE"] == after["VORTIOXETINE"] == "new_clue"

    # And for every medicine: the only ones that moved are the withdrawn
    # ones, and they all moved to not_approved.
    assert before.keys() == after.keys()
    moved = {name for name in after if after[name] != before[name]}
    withdrawn = {p.medicine.name for p in after_paths if p.medicine.withdrawn}
    assert moved <= withdrawn
    assert all(after[name] == "not_approved" for name in withdrawn)
    assert {name.upper() for name in moved} >= set(SIX)


# Example 4
def test_29_example_4_the_runner_prints_none_of_the_six(fibro_files):
    printed = []
    with patch("cli.search_diseases", return_value=[FIBRO]), \
            patch("cli.fetch_targets", return_value=fibro_targets(*THREE)), \
            patch("builtins.print", side_effect=lambda *a, **k: printed.append(
                " ".join(str(x) for x in a))):
        code = cli.main(["fibromyalgia"])
    text = "\n".join(printed).upper()
    assert code == 0
    assert "NEW CLUES" in text and "VORTIOXETINE" in text  # it really printed
    assert [name for name in SIX if name in text] == []
    assert "- NOT APPROVED ANYWHERE: " in text  # they are counted, not named


def test_29_example_4_no_api_response_names_any_of_the_six(
        fibro_files, tmp_path, monkeypatch):
    # A throwaway folder for saved results and a pretend data version, the
    # same set-up tests/test_api.py uses.
    monkeypatch.setenv("MOONLIGHT_CACHE_DIR", str(tmp_path / "saved"))
    cache.forget_memory()
    explain.forget_everything()
    client = TestClient(api.app)

    def gemini_unreachable(method, path, body=None, timeout=None):
        raise requests.ConnectionError("no network")

    with patch("moonlight.api.fetch_targets", return_value=fibro_targets(*THREE)), \
            patch("moonlight.api.data_version", return_value="26.09"), \
            patch("moonlight.explain._gemini_request", side_effect=gemini_unreachable), \
            patch("moonlight.explain.time.sleep"):
        clues = client.get("/api/clues", params={"disease_id": FIBRO.id})
        assert clues.status_code == 200
        data = clues.json()
        texts = [clues.text]
        for clue in data["new_clues"] + data["being_studied"]:
            api.forget_visitors()  # this test is not about the limit
            answer = client.get(
                "/api/explain", params={"disease_id": FIBRO.id, "clue_id": clue["id"]})
            assert answer.status_code == 200
            texts.append(answer.text)
        # Asking for one of the six by its id gives "not found", with no name.
        for chembl_id in ("CHEMBL1419", "CHEMBL45816", "CHEMBL273575", "CHEMBL363295",
                          "CHEMBL276520", "CHEMBL61006"):
            answer = client.get(
                "/api/explain", params={"disease_id": FIBRO.id, "clue_id": chembl_id})
            assert answer.status_code == 404
            texts.append(answer.text)
    explain.forget_everything()
    cache.forget_memory()

    everything = "\n".join(texts).upper()
    assert "VORTIOXETINE" in everything  # it really answered
    assert [name for name in SIX if name in everything] == []
    assert data["left_out"]["not_approved"] >= 6


# =====================================================================
# Ticket 2.9, part 2 (Kashish, 15 Nov). Approved medicines are now shown
# in the Approved tab. Sitaxentan is approved for pulmonary arterial
# hypertension and was withdrawn. With the withdrawn note present it must
# not be named in any tab, from either source of the Approved tab: the
# proteins, or Open Targets' own list for the disease.
# With the live data Kashish's answer key is 16, 2, 5, 13.
# =====================================================================

from test_fetch import PAH as PAH_GOLDEN, noted_post_json  # noqa: E402

FIVE = ("BMPR2", "KCNK3", "ACVRL1", "EDNRA", "PDE5A")
SITAXENTAN_ID = "CHEMBL282724"  # read from fixtures/withdrawn/MONDO_0015924/


@pytest.fixture
def noted_files(tmp_path, monkeypatch):
    """The PAH answers that hold the withdrawn note. Real HTTP is an error."""
    monkeypatch.setenv("MOONLIGHT_CACHE_DIR", str(tmp_path / "saved"))
    cache.forget_memory()
    explain.forget_everything()
    with patch("moonlight.fetch._post_json", side_effect=noted_post_json), \
            patch("moonlight.api.data_version", return_value="26.09"), \
            patch("moonlight.explain.time.sleep"), \
            patch("requests.request", side_effect=AssertionError("network used")), \
            patch("requests.post", side_effect=AssertionError("network used")), \
            patch("requests.get", side_effect=AssertionError("network used")), \
            patch("requests.sessions.Session.request",
                  side_effect=AssertionError("network used")):
        yield
    explain.forget_everything()
    cache.forget_memory()


def pah_targets(*symbols):
    by_symbol = {t.symbol: t for t in fetch.fetch_targets(PAH_GOLDEN)}
    return [by_symbol[symbol] for symbol in symbols]


def test_29_with_the_note_the_five_proteins_give_16_2_5_13(noted_files):
    tray = engine.find_clues(PAH_GOLDEN, pah_targets(*FIVE))
    assert {group: len(paths) for group, paths in tray.items()} == {
        "new_clue": 16,
        "being_studied": 2,
        "already_approved": 5,
        "not_approved": 13,
        "unclear_link": 0,
    }
    assert "SITAXENTAN" in {p.medicine.name for p in tray["not_approved"]}
    for path in sum(tray.values(), []):
        assert path.medicine.withdrawn is not None  # every answer held the note


def test_29_with_the_note_sitaxentan_is_in_no_tab_and_is_counted_not_approved(noted_files):
    tray = engine.find_clues(PAH_GOLDEN, pah_targets(*FIVE))
    tabs = engine.sort_into_tabs(tray, fetch.fetch_approved(PAH_GOLDEN))

    def named(clues):
        return names_in(path for clue in clues for path in clue.paths)

    approved = set()
    for medicine in tabs.approved:
        approved.add(medicine.name.upper())
        approved.update(name.upper() for name in medicine.forms)
    for shown in (approved, named(tabs.being_studied), named(tabs.new_clues)):
        assert shown  # each tab really holds medicines
        assert not any("SITAXENTAN" in name for name in shown)
    assert len(tabs.approved) == 13  # the 14 of the old files, without Sitaxentan
    assert len(tabs.new_clues) == 16 and len(tabs.being_studied) == 2
    assert tabs.left_out == {"not_approved": 13, "unclear_link": 0}


def test_29_with_the_note_no_api_response_names_sitaxentan(noted_files):
    client = TestClient(api.app)

    def gemini_unreachable(method, path, body=None, timeout=None):
        raise requests.ConnectionError("no network")

    with patch("moonlight.api.fetch_targets", return_value=pah_targets(*FIVE)), \
            patch("moonlight.explain._gemini_request", side_effect=gemini_unreachable):
        clues = client.get("/api/clues", params={"disease_id": PAH_GOLDEN.id})
        assert clues.status_code == 200
        data = clues.json()
        texts = [clues.text]
        for clue in data["new_clues"] + data["being_studied"]:
            api.forget_visitors()  # this test is not about the limit
            answer = client.get(
                "/api/explain", params={"disease_id": PAH_GOLDEN.id, "clue_id": clue["id"]})
            assert answer.status_code == 200
            texts.append(answer.text)
        gone = client.get(
            "/api/explain", params={"disease_id": PAH_GOLDEN.id, "clue_id": SITAXENTAN_ID})
        assert gone.status_code == 404
        texts.append(gone.text)

    for tab in ("approved", "being_studied", "new_clues"):
        assert data[tab]
        assert not any("SITAXENTAN" in item["medicine"].upper() for item in data[tab])
        assert not any("SITAXENTAN" in form.upper() for item in data[tab]
                       for form in item["forms"])
        assert SITAXENTAN_ID not in {item["id"] for item in data[tab]}
    assert len(data["approved"]) == 13
    assert "Sildenafil" in [item["medicine"] for item in data["approved"]]  # it really answered
    assert data["left_out"] == {"not_approved": 13, "unclear_link": 0}
    assert "SITAXENTAN" not in "\n".join(texts).upper()


def test_29_with_the_note_the_runner_does_not_print_sitaxentan(noted_files):
    printed = []
    with patch("cli.search_diseases", return_value=[PAH_GOLDEN]), \
            patch("cli.fetch_targets", return_value=pah_targets(*FIVE)), \
            patch("builtins.print", side_effect=lambda *a, **k: printed.append(
                " ".join(str(x) for x in a))):
        code = cli.main(["pulmonary arterial hypertension"])
    text = "\n".join(printed).upper()
    assert code == 0
    assert "VARDENAFIL" in text  # it really printed
    assert "SITAXENTAN" not in text
    assert "- NOT APPROVED ANYWHERE: 13" in text


# ---- Ticket 2.10: a link word that is not a phase and not APPROVAL ----
# Kashish's decision, 2026-11-15: such a link is "unclear link". It never raises.

# Real example, read from Open Targets on 2026-11-15: gabapentin is approved,
# and its link to anxiety disorder is IND.
def test_gabapentin_with_an_ind_link_is_unclear_link():
    assert group_of(single("Gabapentin", "APPROVAL", "IND")) == "unclear_link"


def test_a_preclinical_link_is_unclear_link():
    assert group_of(single("Testamil", "APPROVAL", "PRECLINICAL")) == "unclear_link"


def test_a_preapproval_link_is_unclear_link():
    assert group_of(single("Testamil", "APPROVAL", "PREAPPROVAL")) == "unclear_link"


def test_a_made_up_link_word_is_unclear_link_and_nothing_raises():
    moon = path_for(single("Moonamil", "APPROVAL", "MOON_LINK"))

    assert group_of(moon.medicine) == "unclear_link"
    assert sort_paths([moon])["unclear_link"] == [moon]


def test_a_family_with_an_ind_link_and_a_phase_link_is_still_being_studied():
    medicine = family(
        "Testamil",
        form("Testamil", "APPROVAL", "IND"),
        form("Testamil Sodium", "APPROVAL", "PHASE_2", parent_id="ID_TESTAMIL"),
    )
    assert group_of(medicine) == "being_studied"


def test_phases_approval_and_no_link_sort_exactly_as_before():
    assert group_of(single("Testamil", "APPROVAL")) == "new_clue"
    assert group_of(single("Testamil", "APPROVAL", "APPROVAL")) == "already_approved"
    for stage in ("PHASE_4", "PHASE_3", "PHASE_2_3", "PHASE_2", "PHASE_1_2", "PHASE_1", "EARLY_PHASE_1"):
        assert group_of(single("Testamil", "APPROVAL", stage)) == "being_studied"
    for stage in ("WITHDRAWAL", "UNKNOWN"):
        assert group_of(single("Testamil", "APPROVAL", stage)) == "unclear_link"
    for best in ("PHASE_3", "IND", "PRECLINICAL", "MOON_STAGE"):
        assert group_of(single("Testamil", best, "IND")) == "not_approved"
