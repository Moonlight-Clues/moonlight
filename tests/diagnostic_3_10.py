"""Ticket 3.10, Q1 (decided by MAIN 4, 25 Nov). A scan medicine's Approved card
gains one key, "diagnostic_tag" (moonlight/diagnostic.json). Nothing else on
the card, or on the page, changes.

Older tests compare a whole page with an answer saved before the tag existed.
back_to_before takes the tag off so those comparisons still hold, and checks
the tag is only ever the engine's word, on an Approved-tab card.
"""

import copy

from moonlight import engine

APPROVED_PARTS = ("approved", "narrower", "wider_group")
KEY = "diagnostic_tag"


def back_to_before(page):
    """A copy of the page without the tag."""
    plain = copy.deepcopy(page)
    for where, cards in plain.items():
        if not isinstance(cards, list):
            continue
        for card in cards:
            if isinstance(card, dict) and KEY in card:
                assert where in APPROVED_PARTS, where
                assert card.pop(KEY) == engine.DIAGNOSTIC_TAG
    return plain
