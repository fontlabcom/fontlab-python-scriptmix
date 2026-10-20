# this_file: tests/test_menu_layout.py
"""Keep immutable release metadata while validating only reviewed header moves."""

import hashlib
import json

import pytest
from menu_layout import current_rows, released_bytes


def fixture(tmp_path):
    old = b"# this_file: Scripts/Old/One.py\n# license\n# FLM: Old\nvalue=1\n"
    new = old.replace(b"Scripts/Old/", b"Scripts/New/").replace(
        b"# FLM: Old", b"# FLM: New"
    )
    sha = lambda value: hashlib.sha256(value).hexdigest()
    row = {
        "destination": "Scripts/Old/One.py",
        "destination_sha256": sha(old),
        "source_sha256": "a" * 64,
    }
    move = {
        "original": row["destination"],
        "destination": "Scripts/New/One.py",
        "original_sha256": sha(old),
        "destination_sha256": sha(new),
        "original_header": b"".join(old.splitlines(keepends=True)[:3]).decode(),
        "destination_header": b"".join(new.splitlines(keepends=True)[:3]).decode(),
    }
    path = tmp_path / move["destination"]
    path.parent.mkdir(parents=True)
    path.write_bytes(new)
    (tmp_path / "migration.json").write_text(json.dumps([row]))
    (tmp_path / "menu-moves.json").write_text(json.dumps({"moves": [move]}))
    return old, new, row, move, path


def test_move_retains_exact_historical_bytes_rows_and_actual_destination(tmp_path):
    old, new, row, move, path = fixture(tmp_path)
    before = (tmp_path / "migration.json").read_bytes()
    assert released_bytes(tmp_path, row) == old
    assert current_rows(tmp_path) == [
        {
            **row,
            "destination": move["destination"],
            "destination_sha256": move["destination_sha256"],
        }
    ]
    assert (
        path.read_bytes() == new
        and (tmp_path / "migration.json").read_bytes() == before
    )


@pytest.mark.parametrize(
    "failure",
    ["row_hash", "new_hash", "prefix", "body", "unknown", "escape", "duplicate"],
)
def test_invalid_or_non_header_change_is_rejected(tmp_path, failure):
    _old, new, _row, move, path = fixture(tmp_path)
    if failure == "row_hash":
        move["original_sha256"] = "b" * 64
    if failure == "new_hash":
        move["destination_sha256"] = "b" * 64
    if failure == "prefix":
        move["destination_header"] = "wrong"
    if failure == "body":
        path.write_bytes(new.replace(b"value=1", b"value=2"))
        move["destination_sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
    if failure == "unknown":
        move["original"] = "Scripts/Other/Absent.py"
    if failure == "escape":
        move["destination"] = "../outside.py"
    (tmp_path / "menu-moves.json").write_text(
        json.dumps({"moves": [move] * (2 if failure == "duplicate" else 1)})
    )
    with pytest.raises(ValueError):
        current_rows(tmp_path)


def test_unmoved_and_old_release_snapshots_require_no_overlay(tmp_path):
    path = tmp_path / "Scripts/Plain/One.py"
    path.parent.mkdir(parents=True)
    path.write_bytes(b"value=1\n")
    row = {
        "destination": str(path.relative_to(tmp_path)),
        "destination_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
    }
    assert released_bytes(tmp_path, row) == path.read_bytes()
    (tmp_path / "menu-moves.json").write_text('{"moves":[]}')
    (tmp_path / "migration.json").write_text(json.dumps([row]))
    assert current_rows(tmp_path) == [row]
