"""Ticket 3.21. Print the build fingerprint of this checkout.

Run it from the repo root:

    python3 scripts/fingerprint.py

It prints the same 12 characters the live site shows at /api/version when
the site serves this checkout. It uses moonlight/version.py; nothing is
copied. Read-only.
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from moonlight import version  # noqa: E402

if __name__ == "__main__":
    print(version.FINGERPRINT)
