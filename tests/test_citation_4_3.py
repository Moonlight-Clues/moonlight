"""Ticket 4.3. CITATION.cff for the Zenodo release.

Reads the file as plain text, line by line. No YAML library is needed.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _lines(name):
    return (ROOT / name).read_text(encoding="utf-8").splitlines()


def test_citation_file():
    lines = _lines("CITATION.cff")
    assert "cff-version: 1.2.0" in lines
    assert 'title: "Moonlight"' in lines
    assert "license: MIT" in lines
    assert 'date-released: "2026-11-26"' in lines
    for key in ("message:", "type: software", "authors:", "repository-code:",
                "url:", 'version: "audit-v1.0"', "keywords:"):
        assert any(line.startswith(key) for line in lines), key

    given = [line.strip() for line in lines if "given-names:" in line]
    family = [line.strip() for line in lines if "family-names:" in line]
    assert given == ["- given-names: Kashish", "- given-names: Shreshth"]
    assert family == ["family-names: Dugar", "family-names: Dugar"]

    assert _lines("LICENSE")[0].startswith("MIT License")
