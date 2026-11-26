"""Ticket 3.17. Every card in the saved pages whose Source record link moves.

An Approved card (main list and both folded boxes) that
moonlight/source_overrides.json names for its page now opens the medicine's
own current label as its Source record. Nothing else on any card changes.

The older tests compare whole saved pages letter for letter. They call
back_to_before(page) first, which puts back the link from before 3.17 on
exactly these cards, and only if the card now shows exactly the new link.
Any other change still fails those tests. Call it before the 2.53 and 3.11
helpers: it puts back the link those helpers expect to find.

Found by running the whole suite with the batch and with an empty list, on
the saved answers in fixtures/ (no network): 20 cards. Ticket 2.60 added a 21st.
"""

import copy

# (disease id, medicine id, link before 3.17, link from 3.17)
MOVED = (
    ("MONDO_0005180", "CHEMBL1009",
     "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=043db807-8381-4df8-b3a3-825988d63ef5",
     "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=077c0f39-a3a2-4b2b-a184-09131889dcfb"),
    ("MONDO_0005148", "CHEMBL1055",
     "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=4c7b43e9-d6f1-45e6-5699-5f5f2d075449",
     "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=08b7ee65-53a5-ffbb-e063-6294a90ad4ee"),
    ("MONDO_0005148", "CHEMBL1064",
     "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=2062b3d3-580f-46f8-94b6-4bdecb7b53b1",
     "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=8f55d5de-5a4f-4a39-8c84-c53976dd6af9"),
    ("MONDO_0004979", "CHEMBL1161",
     "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=116464ce-cfd8-4b9f-8b5a-3a114b6ff2b1",
     "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=0c6d63da-41bc-4894-bead-198e66c848ac"),
    ("MONDO_0003233", "CHEMBL117785",
     "https://www.ema.europa.eu/en/medicines/human/EPAR/austedo",
     "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=ac768bab-8afa-4446-bc7f-caeeffec0cda"),
    ("MONDO_0005148", "CHEMBL1200711",
     "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=06c485cd-ee30-44f2-be63-bb98f8d1a907",
     "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=21cfa4ce-0b05-47ed-b268-339eb1b83b75"),
    ("MONDO_0005180", "CHEMBL1201236",
     "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=043db807-8381-4df8-b3a3-825988d63ef5",
     "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=55b99f22-9eb2-4df6-9979-bc4c3af5e454"),
    ("MONDO_0004979", "CHEMBL1201404",
     "https://www.ema.europa.eu/en/medicines/human/EPAR/enerzair-breezhaler",
     "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=0c6d63da-41bc-4894-bead-198e66c848ac"),
    ("MONDO_0005148", "CHEMBL1237",
     "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=0d3a966f-f937-05a8-a90f-5aa52ebbd613",
     "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=838c2d78-d2d8-4981-9ec9-e50ef9e1a5d8"),
    ("MONDO_0004979", "CHEMBL1263",
     "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=0bfe9d76-1b0e-47a4-831d-097168d66577",
     "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=12d9728e-6b5c-4aee-bfb0-745e542ed2e4"),
    ("MONDO_0008383", "CHEMBL139",
     "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=1cdede45-4e2b-490a-bd22-eca5315af316",
     "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=08e41a9d-644c-4ac6-aba3-38d7c3f36d36"),
    ("MONDO_0005148", "CHEMBL1622",
     "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=06c485cd-ee30-44f2-be63-bb98f8d1a907",
     "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=b1cca8e7-3177-421e-a49c-478ed766f643"),
    ("MONDO_0005148", "CHEMBL2107869",
     "https://www.ema.europa.eu/en/medicines/human/EPAR/xultophy",
     "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=456c5e87-3dfd-46fa-8ac0-c6128d4c97c6"),
    ("MONDO_0005148", "CHEMBL2110563",
     "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=06c485cd-ee30-44f2-be63-bb98f8d1a907",
     "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=c6436212-9246-4e29-8540-9af992b667eb"),
    ("MONDO_0004979", "CHEMBL211456",
     "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=172e970d-6773-4796-a280-3370e2f46c69",
     "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=e338deef-efad-1d82-e053-2995a90a1bf9"),
    ("MONDO_0005148", "CHEMBL24",
     "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=4c7b43e9-d6f1-45e6-5699-5f5f2d075449",
     "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=6e850b1e-28a4-4ff8-8ed7-bb0b29faa28a"),
    ("MONDO_0005148", "CHEMBL376359",
     "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=4c619ed9-fe3e-4158-9938-80c6c3493d55",
     "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=a3768c7e-aa4c-44d3-bc53-43bb7346c0b0"),
    ("MONDO_0005148", "CHEMBL435",
     "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=0d3a966f-f937-05a8-a90f-5aa52ebbd613",
     "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=01f1f478-5493-439f-9b99-f4f82023781c"),
    ("MONDO_0004979", "CHEMBL714",
     "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=1700a5b8-4029-424a-bfed-15f6737dd210",
     "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=32474c0e-af35-69d1-e063-6394a90a53c6"),
    ("MONDO_0008383", "CHEMBL90593",
     "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=d509cc4f-d92f-4216-a117-16b467a29126",
     "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=ada639d4-bac0-2ad0-e053-2a95a90afce7"),
    # Ticket 2.60 (MAIN 4, 26 Nov, approved 7:35 am): Roctavian on haemophilia A.
    ("MONDO_0010602", "CHEMBL4297579",
     "https://www.fda.gov/media/169937/download?attachment",
     "https://www.fda.gov/media/169937/download"),
)

# Only Approved cards choose their link this way.
APPROVED_PARTS = ("approved", "narrower", "wider_group")

_NEW_TO_OLD = {(disease_id, medicine_id, new): old for disease_id, medicine_id, old, new in MOVED}


def back_to_before(page):
    """A copy of the page with the link from before 3.17 put back on the cards above."""
    plain = copy.deepcopy(page)
    disease_id = (plain.get("disease") or {}).get("id")
    for where in APPROVED_PARTS:
        for card in plain.get(where, []):
            if not isinstance(card, dict):
                continue
            key = (disease_id, card.get("id"), card.get("source"))
            if key in _NEW_TO_OLD:
                card["source"] = _NEW_TO_OLD[key]
    return plain
