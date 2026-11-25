"""Ticket 3.3. Keeping a visitor's report about one card.

Like a suggestion box by the pool door: the slip says which card and
what looks wrong, and nothing about who dropped it in. api.py checks
the slip; this module only cleans the note and puts the slip in the box.

The box is the Firestore collection REPORTS_COLLECTION. The database is
named by the environment variable FIRESTORE_DB (default "default"): it was
made with that id, in asia-south1, project gen-lang-client-0778260408.
The project and the credentials come from the environment (on Cloud Run,
the service's own account). The client is made the first time a report
is kept, and only once.

If Firestore cannot be reached (no credentials on a laptop, or Google is
down), save_report raises StoreUnavailable and writes ONE log line. The
line names the kind of problem only: never the report, never the visitor.
"""

import logging
import os
import threading
import unicodedata
from typing import Optional

# The four reasons the page offers, in the page's order. Kashish, 25 Nov (2B).
REASONS = ("wrong_disease", "not_approved", "wrong_link", "other")

REPORTS_COLLECTION = "reports"
DEFAULT_DATABASE = "default"
NOTE_LIMIT = 200  # the page's box stops here too

_log = logging.getLogger(__name__)
_client = None
_client_lock = threading.Lock()


class StoreUnavailable(Exception):
    """Firestore could not take the report."""


def _get_client():
    """The Firestore client, made once. Tests replace this function."""
    global _client
    with _client_lock:
        if _client is None:
            try:
                from google.cloud import firestore
                _client = firestore.Client(database=os.environ.get("FIRESTORE_DB", DEFAULT_DATABASE))
            except Exception as problem:  # no package, no credentials, no project
                raise StoreUnavailable(type(problem).__name__) from None
        return _client


def clean_note(text) -> Optional[str]:
    """The note as it is kept: control characters dropped (a tab or a new
    line becomes a space), spaces at the ends taken off, cut to NOTE_LIMIT.
    Nothing left: None."""
    if not isinstance(text, str):
        return None
    kept = []
    for letter in text:
        if letter in "\t\n\r":
            kept.append(" ")
        elif unicodedata.category(letter) != "Cc":
            kept.append(letter)
    note = " ".join("".join(kept).split())[:NOTE_LIMIT].strip()
    return note or None


def save_report(doc: dict) -> None:
    """Put one report in the box. Raises StoreUnavailable if it cannot."""
    try:
        _get_client().collection(REPORTS_COLLECTION).add(doc)
    except StoreUnavailable as problem:
        _log.warning("Report not saved: Firestore unavailable (%s).", problem)
        raise
    except Exception as problem:
        _log.warning("Report not saved: Firestore unavailable (%s).", type(problem).__name__)
        raise StoreUnavailable(type(problem).__name__) from None
