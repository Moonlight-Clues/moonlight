"""Ticket T5c. A dose is taken out before a name is checked for joining marks.

", 2.5 mg", "10 mg/kg" and "N mg" are amounts, not a second medicine.
"Omaveloxolone Capsules, 2.5 mg" is Omaveloxolone. A real combination
still matches nothing: "ELX/TEZ/IVA", "A + B", or a comma between two
medicine names.

No test touches the network.
"""

from moonlight import match

OMAVELOXOLONE = "CHEMBL4303525"
METFORMIN = "CHEMBL1431"
IMATINIB = "CHEMBL941"


def _medicine(chembl_id, name, synonyms=()):
    return {
        "id": chembl_id,
        "name": name,
        "synonyms": [{"label": label, "source": "ChEMBL"} for label in synonyms],
        "tradeNames": [],
    }


def test_a_dose_after_a_comma_is_not_a_second_medicine():
    drugs = [_medicine(OMAVELOXOLONE, "OMAVELOXOLONE", ("Omaveloxolone",))]
    assert match.match(["Omaveloxolone Capsules, 2.5 mg"], drugs) == OMAVELOXOLONE
    assert match.match(["Omaveloxolone Capsules, 10 mg"], drugs) == OMAVELOXOLONE


def test_a_dose_per_kilogram_is_not_a_joining_slash():
    drugs = [_medicine(METFORMIN, "METFORMIN", ("Metformin",))]
    assert match.match(["Metformin 10 mg/kg"], drugs) == METFORMIN
    assert match.match(["Metformin 500 mg"], drugs) == METFORMIN


def test_a_real_combination_still_matches_nothing():
    drugs = [
        _medicine(METFORMIN, "METFORMIN", ("Metformin",)),
        _medicine(IMATINIB, "IMATINIB", ("Imatinib",)),
        _medicine(OMAVELOXOLONE, "OMAVELOXOLONE", ("Omaveloxolone",)),
    ]
    assert match.match(["ELX/TEZ/IVA"], drugs) is None
    assert match.match(["DrugA + DrugB"], drugs) is None
    assert match.match(["metformin, imatinib"], drugs) is None
    assert match.match(["Omaveloxolone, imatinib"], drugs) is None
