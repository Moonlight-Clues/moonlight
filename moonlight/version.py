"""Ticket 3.21. Which build is live.

The image has no .git, so there is no commit hash inside the container.
Instead: a fingerprint of the files the image actually serves, a SHA-256
over every moonlight/*.json, moonlight/*.py and web/index.html, read in
sorted path order, each file fed as "<relative path>\\n<bytes>\\n". The
fingerprint is the first 12 hex characters. Files under tests/, docs/ and
fixtures/ are not part of it.

REVISION is the Cloud Run revision (K_REVISION), or "local".
scripts/fingerprint.py prints the same 12 characters for a checkout.
"""

import hashlib
import os
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
LENGTH = 12


def served_files(root: pathlib.Path) -> list:
    """Relative paths (with "/"), sorted, of the files the image serves."""
    root = pathlib.Path(root)
    found = [*root.glob("moonlight/*.json"), *root.glob("moonlight/*.py"),
             root / "web" / "index.html"]
    return sorted(path.relative_to(root).as_posix() for path in found if path.is_file())


def fingerprint(root: pathlib.Path = ROOT) -> str:
    feed = hashlib.sha256()
    for rel in served_files(root):
        feed.update(rel.encode("utf-8") + b"\n" + (pathlib.Path(root) / rel).read_bytes() + b"\n")
    return feed.hexdigest()[:LENGTH]


def read_revision() -> str:
    return os.environ.get("K_REVISION") or "local"


FINGERPRINT = fingerprint()
REVISION = read_revision()
