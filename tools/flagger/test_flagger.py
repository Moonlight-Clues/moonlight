"""Plain checks of the flagger. No network, no key. Run: python3 -m pytest tools/flagger"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
import flagger as f


def card(d, m, forms=None, source=""):
    return {"disease_id": d, "medicine_id": m, "medicine": m, "forms": forms or [],
            "disease": d, "also_called": [], "source": source}


def test_never_checked_first_then_oldest():
    cards = [card("D1", "M1"), card("D1", "M2"), card("D1", "M3")]
    checked = {"D1|M1": {"date": "2026-11-20"}, "D1|M2": {"date": "2026-11-10"}}
    assert [c["medicine_id"] for c in f.order_cards(cards, checked)] == ["M3", "M2", "M1"]


def test_order_is_stable():
    cards = [card("D%d" % i, "M") for i in range(20)]
    assert f.order_cards(cards, {}) == f.order_cards(list(reversed(cards)), {})


def test_estimate_grows_with_text():
    a = f.est_cost("x" * 3000, "s", (1.0, 5.0))[1]
    b = f.est_cost("x" * 30000, "s", (1.0, 5.0))[1]
    assert b > a > 0


def test_missing_key_writes_nothing(tmp_path, monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    try:
        f.main(["plan", "--work", str(tmp_path / "w")])
    except SystemExit as e:
        assert "not set" in str(e)
    assert not (tmp_path / "w").exists()


# --- flags and no-label sources (MAIN 5, 26 Nov 2026)

def test_no_label_is_not_a_flag():
    assert f.flag_reason("NO_LABEL", "") == ""
    assert f.flag_reason("NO_LABEL", "NO_LABEL") == ""
    assert f.flag_reason("YES", "") == ""
    assert f.flag_reason("PARTIAL", "") == ""
    assert f.flag_reason("NO", "") == "NO"
    assert f.flag_reason("UNCLEAR", "") == "UNCLEAR"


def test_changed_verdict_is_a_flag_even_for_yes():
    assert f.flag_reason("YES", "NO") == "changed since last check"
    assert f.flag_reason("NO", "YES") == "NO; changed since last check"
    assert f.flag_reason("NO_LABEL", "NO") == "changed since last check"


def test_source_kind_names():
    assert f.source_kind("https://www.whocc.no/atc_ddd_index/?code=J01MB08") == "WHO ATC"
    assert f.source_kind("https://ttd.idrblab.cn/data/drug/details/D08GJO") == "TTD"
    assert f.source_kind("https://www.pmda.go.jp/english/review-services/reviews/approved-information/drugs/0001.html") == "PMDA general list"
    assert f.source_kind("https://clinicaltrials.gov/study/NCT02412566") == "trial page"
    assert f.source_kind("", "no source link") == "missing link"
    assert f.source_kind("https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=abc",
                         "no indications section") == "DailyMed, no indications section"
    assert f.source_kind("https://searchusan.ama-assn.org/finder/usan/search/X") == "USAN name page"
    # sort puts the named kinds first, in the agreed order
    assert f.kind_sort_key("WHO ATC") < f.kind_sort_key("TTD") < f.kind_sort_key("PMDA general list")
    assert f.kind_sort_key("trial page") < f.kind_sort_key("missing link")


# --- Q22: a combination pill's label does not count for one of its parts

VYTORIN_SPL = """<?xml version="1.0"?>
<document xmlns="urn:hl7-org:v3">
  <ingredient classCode="ACTIB">
    <ingredientSubstance><name>ezetimibe</name>
      <activeMoiety><activeMoiety><name>ezetimibe</name></activeMoiety></activeMoiety>
    </ingredientSubstance>
  </ingredient>
  <ingredient classCode="ACTIB">
    <ingredientSubstance><name>simvastatin</name>
      <activeMoiety><activeMoiety><name>simvastatin</name></activeMoiety></activeMoiety>
    </ingredientSubstance>
  </ingredient>
  <ingredient classCode="IACT">
    <ingredientSubstance><name>lactose</name></ingredientSubstance>
  </ingredient>
</document>"""

SIMVASTATIN_SPL = """<?xml version="1.0"?>
<document xmlns="urn:hl7-org:v3">
  <ingredient classCode="ACTIB">
    <ingredientSubstance><name>simvastatin</name>
      <activeMoiety><activeMoiety><name>simvastatin</name></activeMoiety></activeMoiety>
    </ingredientSubstance>
  </ingredient>
</document>"""


def test_spl_ingredients_detect_a_combination():
    assert f._ingredients_from_spl(VYTORIN_SPL.encode()) == ["ezetimibe", "simvastatin"]
    assert f._ingredients_from_spl(SIMVASTATIN_SPL.encode()) == ["simvastatin"]
    assert f.is_combination(["ezetimibe", "simvastatin"])
    assert not f.is_combination(["simvastatin"])
    assert not f.is_combination([])


def test_title_and_ema_ingredient_lists():
    assert f.ingredients_from_title("VYTORIN (ezetimibe/simvastatin) Tablets [Organon]") == ["ezetimibe", "simvastatin"]
    assert f.ingredients_from_title("VYTORIN (ezetimibe and simvastatin) tablet") == ["ezetimibe", "simvastatin"]
    assert f.ingredients_from_title("IRBESARTAN and HYDROCHLOROTHIAZIDE Tablets, for oral use") == [
        "IRBESARTAN", "HYDROCHLOROTHIAZIDE"]
    assert f.ingredients_from_title("Oxycodone and Acetaminophen Tablets USP") == ["Oxycodone", "Acetaminophen"]
    assert f.ingredients_from_title("SIMVASTATIN TABLET, FILM COATED [QPHARMA, INC.]") == []
    assert f.title_looks_combo("VYTORIN (EZETIMIBE AND SIMVASTATIN) TABLET [ORGANON LLC]")
    assert f.title_looks_combo("IRBESARTAN AND HYDROCHLOROTHIAZIDE TABLET [QUALITEST]")
    assert not f.title_looks_combo("SIMVASTATIN TABLET, FILM COATED [QPHARMA, INC.]")
    assert not f.title_looks_combo("ZOCOR (SIMVASTATIN) TABLET [ORGANON]")
    assert f._ema_active_substances(
        "Active substances ivacaftor, tezacaftor and elexacaftor. Expand section Therapeutic area Cystic Fibrosis"
    ) == ["ivacaftor", "tezacaftor", "elexacaftor"]
    assert f._ema_active_substances(
        "Active substance semaglutide      International non-proprietary name (INN) or common name      semaglutide"
    ) == ["semaglutide"]


def test_needs_own_label_for_a_part_of_a_combination():
    simva = card("MONDO_0005439", "Simvastatin")
    # Vytorin is ezetimibe + simvastatin: the simvastatin card needs its own label
    assert f.needs_own_label(simva, ["ezetimibe", "simvastatin"])
    assert not f.card_is_the_combination(simva, ["ezetimibe", "simvastatin"])
    # A card that is itself the combination keeps the combo label
    combo = card("D", "Irbesartan and Hydrochlorothiazide",
                 forms=["Irbesartan", "Hydrochlorothiazide"])
    assert f.card_is_the_combination(combo, ["irbesartan", "hydrochlorothiazide"])
    assert not f.needs_own_label(combo, ["irbesartan", "hydrochlorothiazide"])
    # A single-ingredient label is never replaced
    assert not f.needs_own_label(simva, ["simvastatin"])
    # Salt forms still match the same medicine
    assert f.names_match("Tenofovir Disoproxil", "tenofovir disoproxil fumarate")
    assert f.names_match("Simvastatin", "simvastatin calcium")
    assert not f.names_match("Simvastatin", "ezetimibe")


def test_pick_single_ingredient_hit_skips_combinations():
    hits = [
        {"setid": "combo", "title": "VYTORIN (EZETIMIBE AND SIMVASTATIN) TABLET [ORGANON]",
         "published_date": "Nov 25, 2026"},
        {"setid": "old", "title": "SIMVASTATIN TABLET [OLDCO]", "published_date": "Jan 01, 2010"},
        {"setid": "new", "title": "SIMVASTATIN TABLET, FILM COATED [QPHARMA, INC.]",
         "published_date": "Nov 25, 2026"},
    ]
    ings = {"combo": ["ezetimibe", "simvastatin"], "old": ["simvastatin"], "new": ["simvastatin"]}
    hit, got = f.pick_single_ingredient_hit(hits, card("D", "Simvastatin"), lambda s: ings[s])
    assert hit["setid"] == "new"
    assert got == ["simvastatin"]


def test_resolve_replaces_combo_with_the_medicines_own_label(tmp_path):
    labels = tmp_path / "labels"
    labels.mkdir()
    source = "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=65e1c3ae-a462-4345-8a28-c7d2c0388af8"
    own = "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=c80b823c-b30f-0a9d-e053-2995a90a31e9"
    # Pre-fill the cache so resolve does not touch the network.
    import hashlib, json
    def cache(url, text, ings):
        p = labels / (hashlib.sha1(url.encode()).hexdigest()[:16] + ".json")
        p.write_text(json.dumps({"url": url, "status": "label", "text": text,
                                 "reason": "", "ingredients": ings}))
    cache(source, "VYTORIN is indicated to reduce elevated cholesterol.", ["ezetimibe", "simvastatin"])
    cache(own, "SIMVASTATIN is indicated to reduce elevated cholesterol.", ["simvastatin"])
    lab, used, note = f.resolve_source_label(
        card("MONDO_0005439", "Simvastatin", source=source),
        str(labels),
        finder=lambda c, labels_dir, get=None, ingredients_of=None: own,
    )
    assert used == own
    assert "SIMVASTATIN is indicated" in lab["text"]
    assert note.startswith("replaced combo source")


def test_resolve_keeps_combo_when_no_single_ingredient_label_exists(tmp_path):
    labels = tmp_path / "labels"
    labels.mkdir()
    source = "https://www.ema.europa.eu/en/medicines/human/EPAR/kaftrio"
    import hashlib, json
    p = labels / (hashlib.sha1(source.encode()).hexdigest()[:16] + ".json")
    p.write_text(json.dumps({"url": source, "status": "label",
                             "text": "Kaftrio tablets are indicated in a combination regimen.",
                             "reason": "", "ingredients": ["ivacaftor", "tezacaftor", "elexacaftor"]}))
    lab, used, note = f.resolve_source_label(
        card("MONDO_0009061", "Elexacaftor", source=source),
        str(labels),
        finder=lambda *a, **k: None,
    )
    assert used == source
    assert note == "combo source, no single-ingredient label found"
    assert lab["status"] == "label"


def test_ema_stops_at_the_description_sentence():
    assert f._ema_active_substances(
        "Active substance febuxostat. It is available as tablets (80 and 120 mg). What is Adenuric used for?"
    ) == ["febuxostat"]
    assert f._ema_active_substances(
        "Active substance chenodeoxycholic acid. This is a ‘primary bile acid’, which is a main component of bile."
    ) == ["chenodeoxycholic acid"]
    assert f._ema_active_substances(
        "Active substance tacrolimus (0.1% and 0.03%). What is Protopic used for? Protopic is used to treat flare-ups."
    ) == ["tacrolimus"]
    # a real combination still splits
    assert f._ema_active_substances(
        "Active substances ivacaftor, tezacaftor and elexacaftor. Expand section Therapeutic area Cystic Fibrosis"
    ) == ["ivacaftor", "tezacaftor", "elexacaftor"]


def test_tidy_drops_section_numbers_and_prose():
    assert f.tidy_ingredients(["1.1", "14.1"]) == []
    assert f.tidy_ingredients(["canakinumab. How is Ilaris used? Ilaris is given as a single injection"]) == ["canakinumab"]
    assert f.tidy_ingredients(["insulin icodec", "a long-acting insulin"]) == ["insulin icodec"]
    assert f.is_combination(f.tidy_ingredients(["1.1", "14.1"])) is False
    assert not f.needs_own_label(card("D", "Acalabrutinib"), f.tidy_ingredients(["1.1", "14.1"]))


def test_ema_in_brand_then_inn_is_a_single_substance():
    assert f._ema_active_substances(
        "Active substance in Tegsedi, inotersen, is an ‘antisense oligonucleotide’, a very short piece of synthetic genetic material."
    ) == ["inotersen"]
    assert f._ema_active_substances(
        "Active substance in Eporatio, epoetin theta, is a copy of a human hormone called erythropoietin."
    ) == ["epoetin theta"]
    # a real two-ingredient EMA product is still a combination
    assert f._ema_active_substances(
        "Active substances arginine and lysine. Expand section Therapeutic area Radiation"
    ) == ["arginine", "lysine"]


def test_indications_microbiology_is_not_a_combination_title():
    text = ("Staphylococcus aureus (methicillin-susceptible and -resistant isolates) "
            "Streptococcus anginosus grp. (includes S. anginosus, S. intermedius, and S. constellatus)")
    assert f.ingredients_from_title(text) == []
    assert f.tidy_ingredients(["methicillin-susceptible", "resistant isolates"]) == []
    assert f.tidy_ingredients(["S", "and S"]) == []
    assert f.tidy_ingredients(["in Tegsedi", "inotersen"]) == ["inotersen"]


def test_search_falls_back_to_name_without_salt_words():
    queries = []
    def fake_get(url, spaced=False):
        queries.append(url)
        class R:
            status_code = 200
            def json(self):
                if "Carbidopa%20Anhydrous" in url or "Carbidopa+Anhydrous" in url:
                    return {"data": [], "metadata": {}}
                return {"data": [{"setid": "solo", "title": "CARBIDOPA TABLET [X]",
                                  "published_date": "Nov 01, 2026"}], "metadata": {}}
        return R()
    url = f.find_single_ingredient_label(
        card("D", "Carbidopa Anhydrous"),
        "/tmp",
        get=fake_get,
        ingredients_of=lambda s: ["carbidopa"] if s == "solo" else [],
    )
    assert "solo" in url
    assert any("Anhydrous" in q for q in queries)
    assert any("carbidopa" in q.lower() and "anhydrous" not in q.lower() for q in queries)
