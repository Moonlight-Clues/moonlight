"""Cache: saved results, kept in memory, on disk and (Open Targets answers only) in Firestore.

    save(kind, version, key, value)   remember a value, and when it was saved
    load(kind, version, key)          the value, or None if it is not saved
    load(kind, version, key, max_age_seconds=...)
                                      the same, but None if it was saved
                                      longer ago than that
    forget_memory()                   empty the memory; the disk is kept
    forget_firestore_trouble()        make Firestore try again (tests use it)

It works like a notebook with one section per Open Targets data version.
An entry is found again only with the same kind, the same version and the
same key. When Open Targets releases new data the version changes, so the
old section is simply never opened again. Nothing here deletes files.

Every entry records when it was saved ("saved_at", seconds on the clock).
The cache does not decide how old is too old. The caller does, with
max_age_seconds. An entry past that age is not handed back, and the fresh
answer saved afterwards takes its place.

The notebook lives in the folder named by the environment variable
MOONLIGHT_CACHE_DIR (default ".moonlight-cache"). If the folder cannot be
written or a file cannot be read, Moonlight carries on from memory.

Ticket 3.6. A third place, Firestore, so saved answers survive a deploy, an
idle shutdown or a new Cloud Run instance (all of which start with an empty
memory and an empty /tmp). Load looks in memory, then disk, then Firestore;
save writes all three. Only kind "open-targets" goes to Firestore: raw Open
Targets answers, and nothing else (no explanations, no visitor facts, no
hand-written lists, no finished pages). The collection is "cache" in the
database reports.py uses, and the client is reports.py's own lazy client.
A document is named by the sha256 of "kind|version|key text" and holds kind,
version, saved_at and value (JSON, gzip, base64). A value that would be over
FIRESTORE_VALUE_LIMIT is left out of Firestore only. max_age_seconds is
checked on Firestore entries exactly as on the others. If Firestore fails
(no credentials, Google down) the search carries on from memory and disk: one
log line per process, naming the kind of problem only, and Firestore is
left alone for FIRESTORE_REST_SECONDS so a broken store cannot slow every
question. MOONLIGHT_FIRESTORE_CACHE=0 turns this part off.

Apart from that Firestore part, this module never talks to the network.
Values must be plain JSON.
"""

import base64
import gzip
import hashlib
import json
import logging
import os
import pathlib
import re
import threading
import time
from typing import Any, Dict, Optional, Tuple

from moonlight import reports

FOLDER_VARIABLE = "MOONLIGHT_CACHE_DIR"
DEFAULT_FOLDER = ".moonlight-cache"

FIRESTORE_VARIABLE = "MOONLIGHT_FIRESTORE_CACHE"  # "0" turns Firestore off
FIRESTORE_COLLECTION = "cache"
FIRESTORE_KINDS = ("open-targets",)  # the only kinds that go to Firestore
FIRESTORE_VALUE_LIMIT = 900 * 1024  # characters of the stored value; Firestore's own limit is 1 MiB
FIRESTORE_REST_SECONDS = 300  # after a failure, Firestore is left alone this long

_log = logging.getLogger(__name__)
_rest_until = 0.0  # on the _now clock; Firestore is skipped until then
_told = False  # the one log line of this process has been written

# place -> (value, when it was saved)
_memory: Dict[Tuple[str, str, str, str], Tuple[Any, Any]] = {}
_lock = threading.Lock()


def folder() -> pathlib.Path:
    """Where the saved results are kept on disk."""
    return pathlib.Path(os.environ.get(FOLDER_VARIABLE) or DEFAULT_FOLDER)


def forget_memory() -> None:
    """Empty the memory. Files on disk stay where they are."""
    with _lock:
        _memory.clear()


def _now() -> float:
    """The time on the clock, in seconds. Tests replace this."""
    return time.time()


def _in_date(saved_at: Any, max_age_seconds: Optional[float]) -> bool:
    """Is an entry saved at that time still good to use?

    With no max_age_seconds there is no use-by date, so yes. Otherwise no
    if it is too old, if it has no date, or if its date is in the future
    (the clock was wrong, so the age cannot be trusted).
    """
    if max_age_seconds is None:
        return True
    if isinstance(saved_at, bool) or not isinstance(saved_at, (int, float)):
        return False
    return 0 <= _now() - saved_at <= max_age_seconds


def _key_text(key: Any) -> str:
    return json.dumps(key, sort_keys=True)


def _safe(name: str) -> str:
    """A version or kind as a folder name that cannot leave the cache folder."""
    return "v-" + re.sub(r"[^A-Za-z0-9._-]", "_", name)


def _file(kind: str, version: str, key_text: str) -> pathlib.Path:
    digest = hashlib.sha256(key_text.encode("utf-8")).hexdigest()
    return folder() / _safe(version) / _safe(kind) / (digest + ".json")


def _read_disk(kind: str, version: str, key_text: str) -> Optional[Tuple[Any, Any]]:
    """(value, saved_at) from the disk file, or None if there is none that fits."""
    try:
        entry = json.loads(_file(kind, version, key_text).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None  # not saved, or the file is damaged
    # The file says what it holds. If that is not what was asked for, it
    # is not used.
    if not isinstance(entry, dict) or "value" not in entry:
        return None
    if (entry.get("kind"), entry.get("version"), entry.get("key")) != (kind, version, key_text):
        return None
    return entry["value"], entry.get("saved_at")  # files from before ticket 6.3 have none


def _write_disk(kind: str, version: str, key_text: str, saved_at: Any, value: Any) -> None:
    file = _file(kind, version, key_text)
    entry = {"kind": kind, "version": version, "key": key_text,
             "saved_at": saved_at, "value": value}
    # Written under another name first and then renamed, so a file is never
    # read half written.
    part = file.with_name(f"{file.name}.{os.getpid()}.{threading.get_ident()}.part")
    try:
        file.parent.mkdir(parents=True, exist_ok=True)
        part.write_text(json.dumps(entry), encoding="utf-8")
        os.replace(part, file)
    except OSError:
        pass  # the disk is a bonus; memory still has it


# ---- Firestore (ticket 3.6) ----

def forget_firestore_trouble() -> None:
    """Forget an earlier Firestore failure: the rest ends and the one log
    line may be written again."""
    global _rest_until, _told
    _rest_until = 0.0
    _told = False


def _firestore_wanted(kind: str) -> bool:
    if kind not in FIRESTORE_KINDS:
        return False
    if os.environ.get(FIRESTORE_VARIABLE, "").strip() == "0":
        return False
    return _now() >= _rest_until


def _firestore_failed(problem: Exception) -> None:
    """Rest Firestore and say so once. The line names the kind of problem
    only: never a key, a value or a message that may hold one."""
    global _rest_until, _told
    _rest_until = _now() + FIRESTORE_REST_SECONDS
    if not _told:
        _told = True
        name = problem.args[0] if isinstance(problem, reports.StoreUnavailable) and problem.args \
            else type(problem).__name__
        _log.warning("Saved-answer store (Firestore) not used: %s. Carrying on from memory and disk.", name)


def _document(kind: str, version: str, key_text: str):
    name = hashlib.sha256(f"{kind}|{version}|{key_text}".encode("utf-8")).hexdigest()
    return reports._get_client().collection(FIRESTORE_COLLECTION).document(name)


def _firestore_load(kind: str, version: str, key_text: str) -> Optional[Tuple[Any, Any]]:
    """(value, saved_at) from Firestore, or None. Never raises."""
    if not _firestore_wanted(kind):
        return None
    try:
        snapshot = _document(kind, version, key_text).get()
        if not snapshot.exists:
            return None
        entry = snapshot.to_dict()
    except Exception as problem:  # no credentials, Google down, anything
        _firestore_failed(problem)
        return None
    try:
        if (entry.get("kind"), entry.get("version")) != (kind, version):
            return None
        value = json.loads(gzip.decompress(base64.b64decode(entry["value"])))
    except Exception:  # a damaged entry is a miss, not trouble with the store
        return None
    return value, entry.get("saved_at")


def _firestore_save(kind: str, version: str, key_text: str, saved_at: float, value: Any) -> None:
    """Put one entry in Firestore. Never raises."""
    if not _firestore_wanted(kind):
        return
    packed = base64.b64encode(gzip.compress(json.dumps(value).encode("utf-8"))).decode("ascii")
    if len(packed) > FIRESTORE_VALUE_LIMIT:
        return  # too big for a Firestore document: memory and disk still keep it
    try:
        _document(kind, version, key_text).set(
            {"kind": kind, "version": version, "saved_at": saved_at, "value": packed})
    except Exception as problem:
        _firestore_failed(problem)


def load(kind: str, version: str, key: Any,
         max_age_seconds: Optional[float] = None) -> Optional[Any]:
    """The saved value, or None. Memory is looked in first, then the disk,
    then (Open Targets answers only) Firestore.

    max_age_seconds: the use-by date. A value saved longer ago than this
    counts as not saved. Left out, a value is good however old it is.
    """
    key_text = _key_text(key)
    place = (str(folder()), version, kind, key_text)
    with _lock:
        found = _memory.get(place)
    if found is not None:
        value, saved_at = found
        return value if _in_date(saved_at, max_age_seconds) else None
    on_disk = _read_disk(kind, version, key_text)
    if on_disk is not None:
        with _lock:
            _memory[place] = on_disk
        if _in_date(on_disk[1], max_age_seconds):
            return on_disk[0]
    # Not on disk (a new Cloud Run instance has an empty /tmp), or too old
    # there: another instance may have saved a fresher one in Firestore.
    remote = _firestore_load(kind, version, key_text)
    if remote is None or not _in_date(remote[1], max_age_seconds):
        return None
    value, saved_at = remote
    with _lock:
        _memory[place] = (value, saved_at)
    _write_disk(kind, version, key_text, saved_at, value)
    return value


def save(kind: str, version: str, key: Any, value: Any) -> None:
    """Remember the value, and when it was saved: in memory, on disk and,
    for Open Targets answers, in Firestore."""
    key_text = _key_text(key)
    saved_at = _now()
    with _lock:
        _memory[(str(folder()), version, kind, key_text)] = (value, saved_at)
    _write_disk(kind, version, key_text, saved_at, value)
    _firestore_save(kind, version, key_text, saved_at, value)
