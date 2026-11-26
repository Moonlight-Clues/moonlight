"""T5 follow-up. Brackets and "(drug)", 26 Nov 2026.

MAIN 5: a name in brackets is an extra name, and "(drug)" is dropped.
"Erlotinib (Tarceva)" is tried as "Erlotinib" and as "Tarceva".
"Fenofibrate (drug)" is tried as "Fenofibrate".

Combinations and "placebo for X" still match nothing. Form words such as
"tablets" are not changed here: the older test
test_form_words_stay_and_stop_a_match still says they stop a match.

No test touches the network. The Erlotinib and Fenofibrate records are the
smallest shape the matcher reads (id, name, ChEMBL synonym or trade name).
"""

from moonlight import match

ERLOTINIB = "CHEMBL553"
FENOFIBRATE = "CHEMBL672"
IMATINIB = "CHEMBL941"
METFORMIN = "CHEMBL1431"


def _medicine(chembl_id, name, synonyms=(), trade_names=()):
    return {
        "id": chembl_id,
        "name": name,
        "synonyms": [{"label": label, "source": "ChEMBL"} for label in synonyms],
        "tradeNames": [{"label": label, "source": "ChEMBL"} for label in trade_names],
    }


def test_a_name_in_brackets_is_an_extra_name():
    drugs = [_medicine(ERLOTINIB, "ERLOTINIB", synonyms=("Erlotinib",), trade_names=("Tarceva",))]
    assert match.match(["Erlotinib (Tarceva)"], drugs) == ERLOTINIB
    assert match.match(["Tarceva (Erlotinib)"], drugs) == ERLOTINIB


def test_drug_in_brackets_is_dropped():
    drugs = [_medicine(FENOFIBRATE, "FENOFIBRATE", synonyms=("Fenofibrate",))]
    assert match.match(["Fenofibrate (drug)"], drugs) == FENOFIBRATE
    assert match.match(["Fenofibrate (DRUG)"], drugs) == FENOFIBRATE


def test_brackets_that_name_two_medicines_match_nothing():
    drugs = [
        _medicine(ERLOTINIB, "ERLOTINIB", synonyms=("Erlotinib",)),
        _medicine(FENOFIBRATE, "FENOFIBRATE", synonyms=("Fenofibrate",)),
    ]
    assert match.match(["Erlotinib (Fenofibrate)"], drugs) is None


def test_a_combination_and_placebo_for_x_still_match_nothing():
    drugs = [
        _medicine(ERLOTINIB, "ERLOTINIB", synonyms=("Erlotinib",), trade_names=("Tarceva",)),
        _medicine(METFORMIN, "METFORMIN", synonyms=("Metformin",)),
    ]
    assert match.match(["Erlotinib/Tarceva"], drugs) is None
    assert match.match(["placebo for metformin"], drugs) is None
    assert match.match(["Erlotinib (Tarceva/placebo)"], drugs) is None


def test_the_word_drug_without_brackets_is_left_as_it_is():
    drugs = [_medicine(IMATINIB, "IMATINIB", synonyms=("Imatinib",))]
    assert match.match(["investigational drug"], drugs) is None
    assert match.match(["study drug"], drugs) is None
