"""Ticket 2.6. The engine joins fetch and filter.

Examples 1 and 2 from Kashish's answer key (docs/paper-graph-answer-key.jpg)
are tests here. They use the saved files only and never touch the network.
"""

from unittest.mock import patch

import pytest

from moonlight import engine, fetch
from moonlight.filter import GROUPS

# The saved-file stand-in for the network, shared with the fetch tests.
# Importing `offline` (an autouse fixture) switches it on for this file too.
from test_fetch import PAH, fake_post_json, offline  # noqa: F401

FIVE = ("BMPR2", "KCNK3", "ACVRL1", "EDNRA", "PDE5A")


def targets_named(*symbols):
    by_symbol = {t.symbol: t for t in fetch.fetch_targets(PAH)}
    return [by_symbol[symbol] for symbol in symbols]


def counts(tray):
    return {group: len(paths) for group, paths in tray.items()}


# Example 1
def test_five_proteins_together_give_16_2_6_12():
    tray = engine.find_clues(PAH, targets_named(*FIVE))
    assert counts(tray) == {
        "new_clue": 16,
        "being_studied": 2,
        "already_approved": 6,
        "not_approved": 12,
        "unclear_link": 0,
    }
    assert sum(counts(tray).values()) == 36


# Example 2
@pytest.mark.parametrize(
    "symbol, expected",
    [
        ("BMPR2", {"new_clue": 2}),
        ("KCNK3", {"new_clue": 6}),
        ("ACVRL1", {"not_approved": 2}),
        ("EDNRA", {"new_clue": 4, "already_approved": 4, "not_approved": 7}),
        ("PDE5A", {"new_clue": 4, "being_studied": 2, "already_approved": 2,
                   "not_approved": 3}),
    ],
)
def test_counts_by_protein(symbol, expected):
    tray = engine.find_clues(PAH, targets_named(symbol))
    everything = {group: 0 for group in GROUPS}
    everything.update(expected)
    assert counts(tray) == everything


def test_every_group_is_there_even_with_no_targets():
    assert engine.find_clues(PAH, []) == {group: [] for group in GROUPS}


def test_paths_keep_the_order_they_were_fetched_in():
    targets = targets_named("PDE5A", "BMPR2", "KCNK3")  # not score order
    fetched = [p for t in targets for p in fetch.fetch_paths(PAH, t)]
    tray = engine.find_clues(PAH, targets)
    for group, paths in tray.items():
        assert paths == [p for p in fetched if p in paths], group
    # PDE5A was handed in first, so its new clues come before BMPR2's.
    symbols = [p.target.symbol for p in tray["new_clue"]]
    assert symbols == ["PDE5A"] * 4 + ["BMPR2"] * 2 + ["KCNK3"] * 6


def test_each_target_is_fetched_once_with_the_disease():
    targets = targets_named(*FIVE)
    with patch("moonlight.engine.fetch_paths", wraps=fetch.fetch_paths) as spy:
        engine.find_clues(PAH, targets)
    assert [call.args for call in spy.call_args_list] == [(PAH, t) for t in targets]


# ---- Ticket 2.7. The engine hands back the clues in Kashish's ranked order ----

from moonlight.rank import Clue, rank_clues  # noqa: E402
from moonlight.records import Medicine, MedicineForm, Path, Target  # noqa: E402

NEW_ORDER = [
    "DIBOTERMIN ALFA", "EPTOTERMIN ALFA", "SEVOFLURANE", "DESFLURANE",
    "ISOFLURANE", "DOXAPRAM", "ENFLURANE", "HALOTHANE", "ATRASENTAN",
    "SPARSENTAN", "APROCITENTAN", "CLAZOSENTAN", "PENTOXIFYLLINE",
    "DIPYRIDAMOLE", "AVANAFIL", "IBUDILAST",
]


def names(clues):
    return [clue.medicine.name.upper() for clue in clues]


# Example 1
def test_ranked_new_clues_come_in_kashishs_order():
    ranked = engine.find_ranked_clues(PAH, targets_named(*FIVE))
    assert all(isinstance(clue, Clue) for clue in ranked.new_clues)
    assert names(ranked.new_clues) == NEW_ORDER


# Example 2
def test_ranked_being_studied_is_udenafil_then_vardenafil():
    ranked = engine.find_ranked_clues(PAH, targets_named(*FIVE))
    assert all(isinstance(clue, Clue) for clue in ranked.being_studied)
    assert names(ranked.being_studied) == ["UDENAFIL", "VARDENAFIL"]


def test_ranked_order_does_not_depend_on_the_order_of_the_targets():
    forwards = engine.find_ranked_clues(PAH, targets_named(*FIVE))
    backwards = engine.find_ranked_clues(PAH, targets_named(*reversed(FIVE)))
    assert names(backwards.new_clues) == names(forwards.new_clues) == NEW_ORDER
    assert names(backwards.being_studied) == names(forwards.being_studied)


def test_ranked_clues_are_what_rank_clues_makes_of_the_tray():
    targets = targets_named(*FIVE)
    tray = engine.find_clues(PAH, targets)
    ranked = engine.find_ranked_clues(PAH, targets)
    assert ranked.new_clues == rank_clues(tray["new_clue"])
    assert ranked.being_studied == rank_clues(tray["being_studied"])


def test_left_out_counts_are_by_group_and_name_no_medicine():
    ranked = engine.find_ranked_clues(PAH, targets_named(*FIVE))
    assert ranked.left_out == {
        "not_approved": 12,
        "already_approved": 6,
        "unclear_link": 0,
    }


def test_ranked_with_no_targets_is_empty_but_complete():
    ranked = engine.find_ranked_clues(PAH, [])
    assert ranked.new_clues == []
    assert ranked.being_studied == []
    assert ranked.left_out == {
        "not_approved": 0, "already_approved": 0, "unclear_link": 0,
    }


def made_up_paths(disease, target):
    """Stands in for fetch_paths: one made-up medicine acting on any protein,
    and one made-up medicine that is not approved anywhere."""
    def one(name, stage):
        form = MedicineForm(id="ID_" + name.upper(), name=name, best_stage=stage)
        return Path(
            medicine=Medicine(name=name, forms=(form,)),
            target=target,
            disease=disease,
            action_types=("INHIBITOR",),
            score=target.score,
            sources=(f"https://example.org/{name}/{target.symbol}",),
        )
    return [one("MADEUPINE", "APPROVAL"), one("NOTYETINE", "PHASE_2")]


# Example 4
def test_a_medicine_on_two_proteins_is_one_clue_with_the_scores_added():
    weak = Target(id="ENSG_AAA", symbol="AAA", name="AAA", score=0.5)
    strong = Target(id="ENSG_BBB", symbol="BBB", name="BBB", score=0.9)
    with patch("moonlight.engine.fetch_paths", side_effect=made_up_paths):
        ranked = engine.find_ranked_clues(PAH, [weak, strong])
    (clue,) = ranked.new_clues
    assert clue.medicine.name == "MADEUPINE"
    assert [p.target.symbol for p in clue.paths] == ["BBB", "AAA"]
    assert clue.total_score == pytest.approx(1.4)
    assert clue.reports == 2
    # Left out on two proteins, but still one medicine.
    assert ranked.left_out["not_approved"] == 1


# ---- Ticket 6.1. Several proteins are fetched at the same time ----

import threading  # noqa: E402
import time  # noqa: E402

from moonlight.filter import sort_paths  # noqa: E402


class SlowOpenTargets:
    """fake_post_json, made slow, counting how many calls run at once."""

    def __init__(self, seconds_for):
        self.seconds_for = seconds_for  # target id -> seconds to wait
        self.lock = threading.Lock()
        self.running = 0
        self.most_at_once = 0
        self.finished = []  # target ids, in the order their answers came back

    def __call__(self, body):
        target_id = body["variables"]["targetId"]
        with self.lock:
            self.running += 1
            self.most_at_once = max(self.most_at_once, self.running)
        try:
            time.sleep(self.seconds_for(target_id))
            return fake_post_json(body)
        finally:
            with self.lock:
                self.running -= 1
                self.finished.append(target_id)


# Example 3
def test_parallel_gives_the_same_clues_in_the_same_order_as_one_at_a_time(offline):
    targets = targets_named(*FIVE)
    one_at_a_time = sort_paths([p for t in targets for p in fetch.fetch_paths(PAH, t)])

    # The first protein answers slowest and the last one fastest, so the
    # answers come back in the opposite order to the one they were asked in.
    wait = {t.id: 0.05 * (len(targets) - n) for n, t in enumerate(targets)}
    slow = SlowOpenTargets(wait.get)
    offline.side_effect = slow
    together = engine.find_clues(PAH, targets)

    assert slow.finished == [t.id for t in reversed(targets)]
    assert slow.most_at_once == 5  # they really did run at the same time
    assert together == one_at_a_time
    for group in GROUPS:  # same clues, same order, written out plainly
        assert [(p.medicine.name, p.target.symbol) for p in together[group]] == \
               [(p.medicine.name, p.target.symbol) for p in one_at_a_time[group]]


def test_parallel_ranked_clues_are_the_same_as_one_at_a_time(offline):
    targets = targets_named(*FIVE)
    tray = sort_paths([p for t in targets for p in fetch.fetch_paths(PAH, t)])
    offline.side_effect = SlowOpenTargets(lambda target_id: 0.01)
    ranked = engine.find_ranked_clues(PAH, targets)
    assert ranked.new_clues == rank_clues(tray["new_clue"])
    assert ranked.being_studied == rank_clues(tray["being_studied"])


def test_at_most_5_proteins_are_fetched_at_once(offline):
    targets = fetch.fetch_targets(PAH)[:10]  # the ten with saved files
    slow = SlowOpenTargets(lambda target_id: 0.03)
    offline.side_effect = slow
    engine.find_clues(PAH, targets)
    assert engine.AT_ONCE == 5
    assert slow.most_at_once == 5


def test_parallel_calls_start_in_the_order_the_targets_were_given():
    targets = targets_named(*FIVE) * 4
    for _ in range(20):
        with patch("moonlight.engine.fetch_paths", wraps=fetch.fetch_paths) as spy:
            engine.find_clues(PAH, targets)
        assert [call.args for call in spy.call_args_list] == [(PAH, t) for t in targets]


def test_a_problem_with_one_protein_is_still_raised(offline):
    targets = targets_named(*FIVE)

    def broken(body):
        if body["variables"]["targetId"] == targets[2].id:
            return {"errors": [{"message": "boom"}]}
        return fake_post_json(body)

    offline.side_effect = broken
    with pytest.raises(fetch.FetchError):
        engine.find_clues(PAH, targets)


# =====================================================================
# Ticket 5.3: three tabs. Approved medicines are shown, in A to Z order
# =====================================================================
#
# New tests only. Saved files, no network.

from moonlight.engine import ApprovedMedicine, sort_into_tabs  # noqa: E402
from moonlight.fetch import Listed  # noqa: E402
from test_fetch import LISTED_APPROVED, fake_with_the_disease_list  # noqa: E402


@pytest.fixture
def pah_tabs(offline):
    """The three tabs for PAH and Kashish's five answer-key proteins."""
    offline.side_effect = fake_with_the_disease_list
    tray = engine.find_clues(PAH, targets_named(*FIVE))
    return sort_into_tabs(tray, fetch.fetch_approved(PAH))


def approved_named(tabs, name):
    found = [m for m in tabs.approved if m.name.upper() == name.upper()]
    assert len(found) == 1, f"expected one {name}, found {len(found)}"
    return found[0]


# Example 1
def test_53_approved_holds_sildenafil_and_tadalafil_a_to_z_each_once(pah_tabs):
    assert all(isinstance(m, ApprovedMedicine) for m in pah_tabs.approved)
    approved = [m.name for m in pah_tabs.approved]
    assert approved.count("SILDENAFIL") == 1 and approved.count("TADALAFIL") == 1
    assert approved == sorted(approved, key=str.casefold)
    assert approved.index("SILDENAFIL") < approved.index("TADALAFIL")
    assert len(set(m.id for m in pah_tabs.approved)) == len(approved)


def test_53_approved_is_the_two_sources_joined_with_no_medicine_twice(pah_tabs):
    # Six through the five proteins, and all six are also on the disease's
    # own list of 14. Joined, that is 14, not 20.
    assert [m.name for m in pah_tabs.approved] == LISTED_APPROVED
    through_proteins = [m.name for m in pah_tabs.approved if m.clue is not None]
    assert through_proteins == [
        "AMBRISENTAN", "BOSENTAN", "MACITENTAN", "SILDENAFIL", "SITAXENTAN", "TADALAFIL",
    ]


def test_53_a_medicine_found_through_a_protein_carries_its_paths(pah_tabs):
    sildenafil = approved_named(pah_tabs, "Sildenafil")
    assert [p.target.symbol for p in sildenafil.clue.paths] == ["PDE5A"]
    assert sildenafil.clue.paths[0].direction == "down"
    assert round(sildenafil.clue.paths[0].score, 2) == 0.61
    assert sildenafil.forms == ("SILDENAFIL", "SILDENAFIL CITRATE")
    assert sildenafil.reports == sildenafil.clue.reports > 0
    bosentan = approved_named(pah_tabs, "Bosentan")
    assert [p.target.symbol for p in bosentan.clue.paths] == ["EDNRA"]


# Example 2
def test_53_new_clues_and_being_studied_are_what_they_were(pah_tabs):
    assert names(pah_tabs.new_clues) == NEW_ORDER
    assert names(pah_tabs.being_studied) == ["UDENAFIL", "VARDENAFIL"]
    ranked = engine.find_ranked_clues(PAH, targets_named(*FIVE))
    assert pah_tabs.new_clues == ranked.new_clues
    assert pah_tabs.being_studied == ranked.being_studied


# Example 5
def test_53_a_medicine_only_on_the_diseases_own_list_has_no_paths(pah_tabs):
    beraprost = approved_named(pah_tabs, "Beraprost")
    assert beraprost.clue is None
    assert beraprost.forms == ("BERAPROST", "BERAPROST SODIUM")
    assert beraprost.reports == len(beraprost.sources) > 0


# Example 6
def test_53_left_out_has_exactly_two_numbers(pah_tabs):
    assert pah_tabs.left_out == {"not_approved": 12, "unclear_link": 0}


def test_53_no_tab_holds_a_medicine_that_is_not_approved_anywhere(pah_tabs, offline):
    tray = engine.find_clues(PAH, targets_named(*FIVE))
    hidden = set()
    for path in tray["not_approved"]:
        hidden.add(path.medicine.name)
        hidden.update(form.name for form in path.medicine.forms)
    assert len(hidden) > 10
    shown = set()
    for medicine in pah_tabs.approved:
        shown.add(medicine.name)
        shown.update(medicine.forms)
    for clue in pah_tabs.new_clues + pah_tabs.being_studied:
        shown.add(clue.medicine.name)
        shown.update(form.name for form in clue.medicine.forms)
    assert hidden & shown == set()


def test_53_with_no_proteins_and_no_list_every_tab_is_empty():
    tabs = sort_into_tabs(engine.find_clues(PAH, []), [])
    assert tabs.approved == [] and tabs.new_clues == [] and tabs.being_studied == []
    assert tabs.left_out == {"not_approved": 0, "unclear_link": 0}


def test_53_with_no_proteins_the_approved_tab_is_the_diseases_own_list(offline):
    offline.side_effect = fake_with_the_disease_list
    tabs = sort_into_tabs(engine.find_clues(PAH, []), fetch.fetch_approved(PAH))
    assert [m.name for m in tabs.approved] == LISTED_APPROVED
    assert all(m.clue is None for m in tabs.approved)


def tray_of(*paths):
    return sort_paths(paths)


def made_up_path(name, best_stage="APPROVAL", disease_stage=None, symbol="AAA", score=0.5,
                 medicine_id=None, parent_id=None):
    form = MedicineForm(id=medicine_id or "ID_" + name.upper(), name=name,
                        best_stage=best_stage, disease_stage=disease_stage,
                        parent_id=parent_id)
    return Path(
        medicine=Medicine(name=name, forms=(form,)),
        target=Target(id="ENSG_" + symbol, symbol=symbol, name=symbol, score=score),
        disease=PAH,
        action_types=("INHIBITOR",),
        score=score,
        sources=(f"https://example.org/{name}/{symbol}",),
    )


def test_53_approved_is_a_to_z_ignoring_capitals_and_never_by_score():
    tray = tray_of(
        made_up_path("zeta", disease_stage="APPROVAL", score=0.9),
        made_up_path("Alpha", disease_stage="APPROVAL", score=0.1),
    )
    listed = [Listed(id="C9", name="MIDDLE", forms=(("C9", "MIDDLE"),), sources=())]
    tabs = sort_into_tabs(tray, listed)
    assert [m.name for m in tabs.approved] == ["Alpha", "MIDDLE", "zeta"]


def test_53_an_approved_medicine_on_two_proteins_is_one_item_with_both():
    tray = tray_of(
        made_up_path("Twoine", disease_stage="APPROVAL", symbol="AAA", score=0.5),
        made_up_path("Twoine", disease_stage="APPROVAL", symbol="BBB", score=0.9),
    )
    (twoine,) = sort_into_tabs(tray, []).approved
    assert [p.target.symbol for p in twoine.clue.paths] == ["BBB", "AAA"]


def test_53_forms_from_both_sources_are_joined_each_once_parent_first():
    tray = tray_of(made_up_path("REALINE SODIUM", disease_stage="APPROVAL",
                                medicine_id="C2", parent_id="C1"))
    listed = [Listed(id="C1", name="REALINE",
                     forms=(("C1", "REALINE"), ("C2", "REALINE SODIUM"), ("C3", "REALINE CITRATE")),
                     sources=("https://example.org/list",))]
    (realine,) = sort_into_tabs(tray, listed).approved
    assert realine.id == "C1"
    assert realine.forms == ("REALINE", "REALINE SODIUM", "REALINE CITRATE")


# The live data, 2026-11-15: for "hypertensive disorder" the protein records
# hold Celiprolol with no link to the disease, but the disease's own list
# says Celiprolol Hydrochloride is approved for it. A medicine and its forms
# are one item, and the item takes the strongest stage of its forms. So it
# is approved for the disease, and it is not a clue.
def test_53_a_medicine_the_list_says_is_approved_is_never_also_a_clue():
    tray = tray_of(
        made_up_path("CELIPROLOL", medicine_id="C1"),  # looks like a new clue
        made_up_path("TRIALINE", disease_stage="PHASE_2", medicine_id="C5"),
        made_up_path("ONLYNEW", medicine_id="C7"),
    )
    assert names(rank_clues(tray["new_clue"])) == ["CELIPROLOL", "ONLYNEW"]
    listed = [
        Listed(id="C1", name="CELIPROLOL",
               forms=(("C1", "CELIPROLOL"), ("C2", "CELIPROLOL HYDROCHLORIDE")), sources=()),
        Listed(id="C5", name="TRIALINE", forms=(("C6", "TRIALINE SODIUM"),), sources=()),
    ]
    tabs = sort_into_tabs(tray, listed)
    assert names(tabs.new_clues) == ["ONLYNEW"]
    assert tabs.being_studied == []
    assert [m.name for m in tabs.approved] == ["CELIPROLOL", "TRIALINE"]
    celiprolol = approved_named(tabs, "Celiprolol")
    assert [p.target.symbol for p in celiprolol.clue.paths] == ["AAA"]
    assert celiprolol.forms == ("CELIPROLOL", "CELIPROLOL HYDROCHLORIDE")


def test_53_a_left_out_medicine_the_list_says_is_approved_is_not_counted_as_left_out():
    tray = tray_of(
        made_up_path("ODDINE", best_stage="PHASE_3", medicine_id="C1"),
        made_up_path("GONEINE", disease_stage="WITHDRAWAL", medicine_id="C3"),
        made_up_path("NOTYETINE", best_stage="PHASE_2", medicine_id="C8"),
    )
    listed = [
        Listed(id="C1", name="ODDINE", forms=(("C2", "ODDINE SODIUM"),), sources=()),
        Listed(id="C3", name="GONEINE", forms=(("C4", "GONEINE SODIUM"),), sources=()),
    ]
    tabs = sort_into_tabs(tray, listed)
    assert [m.name for m in tabs.approved] == ["GONEINE", "ODDINE"]
    assert tabs.left_out == {"not_approved": 1, "unclear_link": 0}


def test_53_find_ranked_clues_still_counts_three_groups_for_the_terminal_runner():
    # cli.py is not part of this ticket and still prints three counts.
    ranked = engine.find_ranked_clues(PAH, targets_named(*FIVE))
    assert set(ranked.left_out) == {"not_approved", "already_approved", "unclear_link"}
