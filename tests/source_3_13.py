"""Ticket 3.13. Every In trials card in the saved pages whose Source record link moves.

The rule (MAIN 4's smaller ticket): when none of a main In trials card's own links
is a study of this disease, the card opens a study of this disease that the
disease's own list holds for the medicine (the first https one, A to Z). If there
is none, the card keeps its 3.11 link. Nothing else on any card changes.

The older tests compare whole saved pages letter for letter. Following that
decision (approved by MAIN 4, option b), and only that, they call back_to_before(page)
first, after 3.11's own back_to_before is undone: it puts back the 3.11 link on
exactly these cards of the main In trials list ("being_studied"), and only if the
card now shows exactly the new link. Any other change still fails those tests.

Found by running the whole suite on the saved answers in fixtures/ (no network),
logging every card whose link the new step changes: these four cards on the
rheumatoid arthritis page are the ones a letter-for-letter test compares (rows
approved by MAIN 4). Each new link is a report with source "ClinicalTrials.gov"
on rheumatoid arthritis's own saved list
(fixtures/old_withdrawn_flag/answers/disease_drugs/9a5d0cbae7806ce1.json) and is not
among the card's own records. The other cards the step moves (atopic eczema, and
two on MONDO_0015924 that had no link) are tested in test_trial_link_other_records.py.
"""

import copy

STUDY = "https://clinicaltrials.gov/study/"

# (page, medicine id, name, link before 3.13, link from 3.13)
MOVED = (
    ("MONDO_0008383", "CHEMBL514800", "Apremilast",
     STUDY + "NCT02735707",
     STUDY + "NCT01204138"),
    ("MONDO_0008383", "CHEMBL932", "Dipyridamole",
     STUDY + "NCT00223717",
     STUDY + "NCT00551707"),
    ("MONDO_0008383", "CHEMBL628", "Pentoxifylline",
     STUDY + "NCT01214226",
     STUDY + "NCT06998628"),
    ("MONDO_0008383", "CHEMBL193240", "Roflumilast",
     STUDY + "NCT02340520",
     STUDY + "NCT07566351"),
)

TRIAL_PARTS = ("being_studied",)

_NEW_TO_OLD = {(medicine_id, new): old for _, medicine_id, _, old, new in MOVED}


def back_to_before(page):
    """A copy of the page with the 3.11 link put back on the cards above."""
    plain = copy.deepcopy(page)
    for where in TRIAL_PARTS:
        for card in plain.get(where, []):
            if isinstance(card, dict) and (card.get("id"), card.get("source")) in _NEW_TO_OLD:
                card["source"] = _NEW_TO_OLD[(card["id"], card["source"])]
    return plain
