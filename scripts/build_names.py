"""Build moonlight/names.json from the hand lists and Open Targets 26.09.

Every medicine id (ChEMBL) and disease id (MONDO, Orphanet, EFO, and the
other Open Targets disease prefixes) written in the hand lists is mapped to
the name Open Targets Platform 26.09 sends. The script asks the Platform
GraphQL API and checks meta.dataVersion is 26.09 before it trusts a name.
A medicine name is drug(chemblId).name. A disease name is disease(efoId).name.
Both are stored as sent.

The file is one JSON object with the ids in sorted order, so a second run
writes the same bytes.

    python scripts/build_names.py
"""

import json
import re
import urllib.request

ROOT_LISTS = (
    "corrections.json",
    "approvals.json",
    "limits.json",
    "confirmed.json",
    "withdrawals.json",
    "pmda_summaries.json",
    "salt_parents.json",
)
# Open Targets disease ids use these prefixes. CHEMBL is a medicine.
ID_RE = re.compile(
    r"\b(CHEMBL\d+|MONDO_\d+|Orphanet_\d+|EFO_\d+|DOID_\d+|HP_\d+|GO_\d+|MP_\d+|OTAR_\d+|OBA_\d+)\b"
)
ENDPOINT = "https://api.platform.opentargets.org/api/v4/graphql"
RELEASE = "26.09"
BATCH = 40


def hand_list_dir():
    from pathlib import Path
    return Path(__file__).resolve().parent.parent / "moonlight"


def ids_in(text):
    return set(ID_RE.findall(text))


def ids_by_list():
    folder = hand_list_dir()
    found = {}
    for name in ROOT_LISTS:
        found[name] = ids_in((folder / name).read_text(encoding="utf-8"))
    return found


def _post(query):
    body = json.dumps({"query": query}).encode("utf-8")
    request = urllib.request.Request(
        ENDPOINT, data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(request, timeout=60) as response:
        payload = json.loads(response.read().decode("utf-8"))
    if payload.get("errors"):
        raise SystemExit(f"Open Targets returned an error: {payload['errors']!r}")
    return payload["data"]


def require_release():
    data = _post("{ meta { dataVersion { year month } } }")
    version = data["meta"]["dataVersion"]
    got = f"{version['year']}.{version['month']}"
    if got != RELEASE:
        raise SystemExit(f"Open Targets data version is {got}, not {RELEASE}.")
    return got


def fetch_names(ids):
    """id -> name, as Open Targets sent it. An id with no record is omitted."""
    names = {}
    ordered = sorted(ids)
    for start in range(0, len(ordered), BATCH):
        chunk = ordered[start:start + BATCH]
        fields = []
        for index, one in enumerate(chunk):
            if one.startswith("CHEMBL"):
                fields.append(f'i{index}: drug(chemblId: "{one}") {{ name }}')
            else:
                fields.append(f'i{index}: disease(efoId: "{one}") {{ name }}')
        data = _post("query { " + " ".join(fields) + " }")
        for index, one in enumerate(chunk):
            row = data.get(f"i{index}")
            if row and isinstance(row.get("name"), str) and row["name"]:
                names[one] = row["name"]
    return names


def dumps(names):
    return json.dumps(names, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def main():
    by_list = ids_by_list()
    every = set().union(*by_list.values())
    release = require_release()
    names = fetch_names(every)
    missing = sorted(every - set(names))
    folder = hand_list_dir()
    (folder / "names.json").write_text(dumps(names), encoding="utf-8")
    print(f"release {release}")
    print(f"ids {len(every)} named {len(names)} missing {len(missing)}")
    for name in ROOT_LISTS:
        print(f"  {name}: {len(by_list[name])}")
    if missing:
        print("no Open Targets name:")
        for one in missing:
            print(f"  {one}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
