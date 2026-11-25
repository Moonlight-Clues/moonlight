"""Ticket 2.53. Every card in the saved pages whose Source record link moves.

A card's Source record now opens a regulator's approval receipt (DailyMed,
FDA, EMA Human Drugs or PMDA, read from the report's "source" field) before
a second-hand list's (TTD, ATC). Nothing else on any card changes.

The older tests compare whole saved pages letter for letter. They call
back_to_before(page) first, which puts back the old link on exactly these
Approved
cards (main list and both folded boxes), and only if the card now shows exactly the new link. Any other
change still fails those tests.

Found by running the whole suite with the new rule and the old rule side by
side, on the saved answers in fixtures/ (no network): 40 cards.
"""

import copy

# (medicine id, name, link before 2.53, link from 2.53)
MOVED = (
    ("CHEMBL494", "iloprost",
     "https://ttd.idrblab.cn/data/drug/details/D05ZTH",
     "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=d3bebc1c-f032-402a-bbc9-aff024276ed1"),
    ("CHEMBL117785", "tetrabenazine",
     "https://ttd.idrblab.cn/data/drug/details/D0E7ZU",
     "https://www.ema.europa.eu/en/medicines/human/EPAR/austedo"),
    ("CHEMBL1808388", "bexagliflozin",
     "https://ttd.idrblab.cn/data/drug/details/D0OR3G",
     "https://www.accessdata.fda.gov/drugsatfda_docs/label/2023/214373s000lbl.pdf"),
    ("CHEMBL429910", "dapagliflozin",
     "https://ttd.idrblab.cn/data/drug/details/D01TNW",
     "https://www.ema.europa.eu/en/medicines/human/EPAR/forxiga"),
    ("CHEMBL1770248", "ertugliflozin",
     "https://ttd.idrblab.cn/data/drug/details/D0Q3VE",
     "https://www.ema.europa.eu/en/medicines/human/EPAR/steglujan"),
    ("CHEMBL385517", "saxagliptin anhydrous",
     "https://ttd.idrblab.cn/data/drug/details/D0K9MY",
     "https://www.ema.europa.eu/en/medicines/human/EPAR/onglyza"),
    ("CHEMBL1422", "sitagliptin",
     "https://ttd.idrblab.cn/data/drug/details/D0U2JP",
     "https://www.ema.europa.eu/en/medicines/human/EPAR/januvia"),
    ("CHEMBL4297839", "tirzepatide",
     "https://ttd.idrblab.cn/data/drug/details/DA69JF",
     "https://www.ema.europa.eu/en/medicines/human/EPAR/mounjaro"),
    ("CHEMBL142703", "vildagliptin",
     "https://ttd.idrblab.cn/data/drug/details/D0L3DK",
     "https://www.ema.europa.eu/en/medicines/human/EPAR/galvus"),
    ("CHEMBL1201613", "insulin glulisine",
     "https://www.whocc.no/atc_ddd_index/?code=A10AB06",
     "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=e7af6a7a-8046-4fb4-9979-4ec4230b23aa"),
    ("CHEMBL1201538", "insulin lispro",
     "https://www.whocc.no/atc_ddd_index/?code=A10AB04",
     "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=b34cd3ff-d0af-4852-b4ef-2a8b4a93aeae"),
    ("CHEMBL2109334", "inebilizumab",
     "https://ttd.idrblab.cn/data/drug/details/D0XH3V",
     "https://www.ema.europa.eu/en/medicines/human/EPAR/uplizna"),
    ("CHEMBL3833307", "satralizumab",
     "https://ttd.idrblab.cn/data/drug/details/D0MD0T",
     "https://www.ema.europa.eu/en/medicines/human/EPAR/enspryng"),
    ("CHEMBL5315069", "damoctocog alfa pegol",
     "https://ttd.idrblab.cn/data/drug/details/D8B9KJ",
     "https://www.ema.europa.eu/en/medicines/human/EPAR/jivi"),
    ("CHEMBL5095275", "efanesoctocog alfa",
     "https://ttd.idrblab.cn/data/drug/details/DMU9P2",
     "https://www.ema.europa.eu/en/medicines/human/EPAR/altuvoct"),
    ("CHEMBL4297945", "efmoroctocog alfa",
     "https://ttd.idrblab.cn/data/drug/details/D0UQ1R",
     "https://www.ema.europa.eu/en/medicines/human/EPAR/elocta"),
    ("CHEMBL3833393", "emicizumab",
     "https://ttd.idrblab.cn/data/drug/details/D09XTN",
     "https://www.ema.europa.eu/en/medicines/human/EPAR/hemlibra"),
    ("CHEMBL5315075", "susoctocog alfa",
     "https://ttd.idrblab.cn/data/drug/details/D0G0AI",
     "https://www.ema.europa.eu/en/medicines/human/EPAR/obizur"),
    ("CHEMBL1342", "oxybate",
     "https://ttd.idrblab.cn/data/drug/details/D40IXR",
     "https://www.ema.europa.eu/en/medicines/human/EPAR/xyrem"),
    ("CHEMBL2348780", "vamorolone",
     "https://ttd.idrblab.cn/data/drug/details/D0F6YM",
     "https://www.ema.europa.eu/en/medicines/human/EPAR/agamree"),
    ("CHEMBL1742991", "benralizumab",
     "https://ttd.idrblab.cn/data/drug/details/D02PIO",
     "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=da6aca1a-19ed-44a4-abb7-696c7d58b784"),
    ("CHEMBL978", "methacholine",
     "https://ttd.idrblab.cn/data/drug/details/D04MWJ",
     "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=e8983096-65e6-41f2-8b6f-bbf0a7227307"),
    ("CHEMBL1094966", "pirbuterol",
     "https://ttd.idrblab.cn/data/drug/details/D0SS4P",
     "https://www.accessdata.fda.gov/drugsatfda_docs/label/2001/19009s6lbl.pdf"),
    ("CHEMBL1201754", "rufinamide",
     "https://ttd.idrblab.cn/data/drug/details/D0MD2L",
     "https://www.ema.europa.eu/en/medicines/human/EPAR/inovelon"),
    ("CHEMBL1201570", "anakinra",
     "https://ttd.idrblab.cn/data/drug/details/D02DES",
     "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=d9d74915-6606-4570-9c52-c4001d3177de"),
    ("CHEMBL221959", "tofacitinib",
     "https://ttd.idrblab.cn/data/drug/details/D08ICX",
     "https://www.ema.europa.eu/en/medicines/human/EPAR/xeljanz"),
    ("CHEMBL660", "amantadine",
     "https://www.whocc.no/atc_ddd_index/?code=N04BB01",
     "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=01417f60-dbf3-4041-bf3c-51e6c9216f06"),
    ("CHEMBL53", "apomorphine",
     "https://ttd.idrblab.cn/data/drug/details/D0H6QU",
     "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=3235535d-9ef9-4657-8b2a-176a807d091c"),
    ("CHEMBL1201203", "benztropine",
     "https://ttd.idrblab.cn/data/drug/details/D0HQ6N",
     "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=0bd33841-6ae2-407d-92d7-015ea0ad7777"),
    ("CHEMBL1945778", "ioflupane",
     "https://ttd.idrblab.cn/data/drug/details/D02GJZ",
     "https://www.ema.europa.eu/en/medicines/human/EPAR/datscan"),
    ("CHEMBL2111101", "pimavanserin",
     "https://ttd.idrblab.cn/data/drug/details/D0J8JP",
     "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=1e6bea44-57d6-4bac-9328-46e1ee59f83b"),
    ("CHEMBL301265", "pramipexole",
     "https://ttd.idrblab.cn/data/drug/details/D0G8NN",
     "https://www.ema.europa.eu/en/medicines/human/EPAR/sifrol"),
    ("CHEMBL589", "ropinirole",
     "https://ttd.idrblab.cn/data/drug/details/D0R9EQ",
     "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=0fa94d3d-ec03-4eb7-93b2-8e1d7ff6c3e0"),
    ("CHEMBL972", "selegiline",
     "https://ttd.idrblab.cn/data/drug/details/D0J2MJ",
     "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=380d7717-2a79-42f3-a712-efe5e7696ba0"),
    ("CHEMBL668", "protriptyline",
     "https://ttd.idrblab.cn/data/drug/details/D00MYQ",
     "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=700abc58-9362-4ef5-9d7a-dd3c4d364d0a"),
    ("CHEMBL284092", "gepirone",
     "https://ttd.idrblab.cn/data/drug/details/D0R5GS",
     "https://www.accessdata.fda.gov/drugsatfda_docs/label/2023/021164s000lbl.pdf"),
    ("CHEMBL99946", "levomilnacipran",
     "https://www.whocc.no/atc_ddd_index/?code=N06AX28",
     "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=bcbc5d92-e022-4a0d-ab4d-2b0d7aa68c58"),
    ("CHEMBL21731", "maprotiline",
     "https://ttd.idrblab.cn/data/drug/details/D03KQF",
     "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=c3ca69e6-1ea0-4c2c-abcb-7264b2e79a87"),
    ("CHEMBL3989843", "tranylcypromine",
     "https://ttd.idrblab.cn/data/drug/details/D0H0HJ",
     "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=b72d8187-dfcc-4ea0-b5e9-c0be95b69a27"),
    ("CHEMBL4105630", "zuranolone",
     "https://www.whocc.no/atc_ddd_index/?code=N06AX31",
     "https://www.ema.europa.eu/en/medicines/human/EPAR/zurzuvae"),
)

# Only Approved cards choose their link this way. An In trials or New clue
# card that happens to carry the same link is never touched.
APPROVED_PARTS = ("approved", "narrower", "wider_group")

_NEW_TO_OLD = {(medicine_id, new): old for medicine_id, _, old, new in MOVED}


def back_to_before(page):
    """A copy of the page with the old link put back on the cards above."""
    plain = copy.deepcopy(page)
    for where in APPROVED_PARTS:
        for card in plain.get(where, []):
            if isinstance(card, dict) and (card.get("id"), card.get("source")) in _NEW_TO_OLD:
                card["source"] = _NEW_TO_OLD[(card["id"], card["source"])]
    return plain
