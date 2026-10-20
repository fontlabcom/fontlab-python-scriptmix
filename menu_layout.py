# this_file: menu_layout.py
"""Resolve reviewed path/header moves while retaining immutable release metadata."""

import hashlib
import json
from pathlib import Path


def _moves(root: Path) -> dict[str, dict]:
    """Read the explicit move overlay; reject ambiguous or escaping menu paths."""
    rows = json.loads((root / "menu-moves.json").read_text())["moves"]
    for row in rows:
        for key in ("original", "destination"):
            parts = Path(row[key]).parts
            if (
                len(parts) != 3
                or parts[0] != "Scripts"
                or ".." in parts
                or Path(row[key]).suffix != ".py"
            ):
                raise ValueError("A menu move must remain inside one Scripts category.")
    result = {row["original"]: row for row in rows}
    if len(result) != len(rows) or len({row["destination"] for row in rows}) != len(
        rows
    ):
        raise ValueError("Duplicate menu move.")
    return result


def released_bytes(root: Path, row: dict) -> bytes:
    """Recover exact historical bytes only through a verified comment-header move."""
    move = (
        _moves(root).get(row["destination"])
        if (root / "menu-moves.json").is_file()
        else None
    )
    if move is None:
        return (root / row["destination"]).read_bytes()
    raw = (root / move["destination"]).read_bytes()
    if (
        row["destination_sha256"] != move["original_sha256"]
        or hashlib.sha256(raw).hexdigest() != move["destination_sha256"]
    ):
        raise ValueError("Moved menu source hash differs from its reviewed provenance.")
    old, new = move["original_header"].encode(), move["destination_header"].encode()
    if not raw.startswith(new):
        raise ValueError("Moved menu header differs from its reviewed prefix.")
    original = old + raw[len(new) :]
    if hashlib.sha256(original).hexdigest() != move["original_sha256"]:
        raise ValueError("Moved menu changed more than its reviewed header.")
    return original


def current_rows(root: Path) -> list[dict]:
    """Return actual current destinations; never mutate historical migration rows."""
    rows = json.loads((root / "migration.json").read_text())
    moves = _moves(root)
    if not moves.keys() <= {row["destination"] for row in rows}:
        raise ValueError("Menu move has no historical migration identity.")
    result = []
    for row in rows:
        move = moves.get(row["destination"])
        if move is None:
            result.append(dict(row))
        else:
            released_bytes(root, row)
            result.append(
                {
                    **row,
                    "destination": move["destination"],
                    "destination_sha256": move["destination_sha256"],
                }
            )
    return result
