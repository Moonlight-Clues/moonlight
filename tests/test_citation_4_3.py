"""Ticket 4.3. CITATION.cff for the Zenodo release."""

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent


def test_citation_file():
    data = yaml.safe_load((ROOT / "CITATION.cff").read_text(encoding="utf-8"))
    for key in ("cff-version", "message", "title", "type", "authors",
                "repository-code", "url", "license", "version",
                "date-released", "keywords"):
        assert key in data
    assert str(data["cff-version"]) == "1.2.0"
    assert data["title"] == "Moonlight"
    assert data["license"] == "MIT"
    assert (ROOT / "LICENSE").read_text(encoding="utf-8").startswith("MIT License")
    assert [(a["given-names"], a["family-names"]) for a in data["authors"]] == [
        ("Kashish", "Dugar"),
        ("Shreshth", "Dugar"),
    ]
