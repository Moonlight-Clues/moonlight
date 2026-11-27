"""Ticket T5d. A slash in an other-name can be a list of aliases.

MAIN 5: a "/" piece whose parts are each either unknown or the same medicine
as the main name counts as aliases. If any part is a different known medicine,
it stays a combination and matches nothing.

The main name's own joining marks are unchanged, so "ELX/TEZ/IVA" still
matches nothing.

No test touches the network.
"""

from moonlight import match

TOBRAMYCIN = "CHEMBL1747"
IMATINIB = "CHEMBL941"


def _medicine(chembl_id, name, synonyms=()):
    return {
        "id": chembl_id,
        "name": name,
        "synonyms": [{"label": label, "source": "ChEMBL"} for label in synonyms],
        "tradeNames": [],
    }


def test_tobramycin_slash_brands_match_the_main_name():
    """NCT01111383 lists tobramycin, and other-names
    Tobrineb®/Actitob®/Bramitob®. Tobrineb and Actitob are unknown.
    Bramitob is the same medicine."""
    drugs = [_medicine(TOBRAMYCIN, "TOBRAMYCIN", ("Tobramycin", "Bramitob"))]
    assert match.match(
        ["tobramycin", "Tobrineb®/Actitob®/Bramitob®"], drugs) == TOBRAMYCIN


def test_a_slash_list_with_a_different_medicine_matches_nothing():
    drugs = [
        _medicine(TOBRAMYCIN, "TOBRAMYCIN", ("Tobramycin", "Bramitob")),
        _medicine(IMATINIB, "IMATINIB", ("Imatinib",)),
    ]
    assert match.match(["tobramycin", "Bramitob/imatinib"], drugs) is None
    assert match.match(["ELX/TEZ/IVA"], drugs) is None
    assert match.match(["tobramycin/imatinib"], drugs) is None
