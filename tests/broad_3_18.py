"""Ticket 3.18. Every card the saved pages lose from the wider-group box.

Kashish's decision of 25 Nov (Q9): a card that reaches the folded box
"Approved for a wider group" only through a group on moonlight/broad_groups.json
is not shown. Nothing else on any page changes.

The older tests compare whole saved pages letter for letter. Following that
decision, and only that, they call back_to_before(page, disease_id) first: it
puts back exactly the cards below in the page's wider_group, A to Z as the
box sorts them, and only if the card is not on the page and its label names
one wider group, and that group is on the list. Any other change still fails
those tests.

Found by running every saved page in fixtures/broad_groups/answers and
fixtures/old_withdrawn_flag/answers with the list and with an empty list
side by side (no network): 91 cards on 8 of 16 pages. The cards, as the page
showed them before 3.18, are in fixtures/broad_groups/removed_3_18.json.
"""

import copy
import json
import pathlib

from moonlight.engine import parent_label

ROOT = pathlib.Path(__file__).resolve().parent.parent
REMOVED = json.loads(
    (ROOT / "fixtures" / "broad_groups" / "removed_3_18.json").read_text(encoding="utf-8"))
LISTED = {entry["name"] for entry in json.loads(
    (ROOT / "moonlight" / "broad_groups.json").read_text(encoding="utf-8"))}


def back_to_before(page, disease_id):
    """A copy of the page with the cards above put back in the wider-group box."""
    plain = copy.deepcopy(page)
    cards = REMOVED.get(disease_id, [])
    if not cards:
        return plain
    box = plain.get("wider_group", [])
    shown = {card["id"] for card in box}
    for card in cards:
        assert card["id"] not in shown, card["medicine"]
        assert card["label"] in {parent_label([name]) for name in LISTED}, card["medicine"]
    box = box + copy.deepcopy(cards)
    box.sort(key=lambda card: (card["medicine"].casefold(), card["medicine"], card["id"]))
    plain["wider_group"] = box
    return plain
