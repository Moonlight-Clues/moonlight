"""Ticket T5d. A slash in an other-name can be a list of aliases.

MAIN 5: in a "/" list among the other-names, an unknown part counts as an
alias only when it looks like a brand name: letters only, no digits.
A trademark mark is not a digit. An unknown part with a digit, such as
VX-445, is a different medicine, so the list is a combination.

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


def test_an_unknown_code_with_a_digit_makes_the_slash_list_a_combination():
    """VX-445 and VX-661 are unknown and contain digits. VX-770 is ivacaftor.
    The list matches nothing."""
    ivacaftor = _medicine("CHEMBL2010601", "IVACAFTOR", ("Ivacaftor", "VX-770"))
    assert match.match(
        ["Ivacaftor", "VX-445/VX-661/VX-770"], [ivacaftor]) is None


def test_a_slash_list_with_a_different_medicine_matches_nothing():
    drugs = [
        _medicine(TOBRAMYCIN, "TOBRAMYCIN", ("Tobramycin", "Bramitob")),
        _medicine(IMATINIB, "IMATINIB", ("Imatinib",)),
    ]
    assert match.match(["tobramycin", "Bramitob/imatinib"], drugs) is None
    assert match.match(["ELX/TEZ/IVA"], drugs) is None
    assert match.match(["tobramycin/imatinib"], drugs) is None
