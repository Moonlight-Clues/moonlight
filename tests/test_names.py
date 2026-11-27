"""moonlight/names.json names every medicine and disease id in the hand lists.

No network. The file is built by scripts/build_names.py from Open Targets 26.09.
"""

import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent


def _builder():
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "build_names", ROOT / "scripts" / "build_names.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_every_hand_list_id_has_an_open_targets_name():
    builder = _builder()
    names = json.loads((ROOT / "moonlight" / "names.json").read_text(encoding="utf-8"))
    missing = []
    for name, ids in builder.ids_by_list().items():
        for one in sorted(ids):
            if not isinstance(names.get(one), str) or not names[one]:
                missing.append(f"{name} {one}")
    assert missing == []


def test_names_json_is_sorted_so_a_second_dump_is_the_same_bytes():
    builder = _builder()
    path = ROOT / "moonlight" / "names.json"
    text = path.read_text(encoding="utf-8")
    data = json.loads(text)
    assert list(data) == sorted(data)
    assert text == builder.dumps(data)
    assert all(isinstance(value, str) and value for value in data.values())
