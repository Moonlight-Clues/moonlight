"""Plain checks of the flagger's ordering and estimate. No network, no key. Run: python3 -m pytest tools/flagger"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
import flagger as f


def card(d, m):
    return {"disease_id": d, "medicine_id": m, "medicine": m, "forms": [], "disease": d, "also_called": []}


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
