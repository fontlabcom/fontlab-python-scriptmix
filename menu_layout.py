# this_file: menu_layout.py
"""Resolve reviewed path/header moves while retaining immutable release metadata."""

import hashlib
import json
import os
import re
import subprocess
from datetime import date
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
    """Recover exact historical bytes through verified moves and recorded edits."""
    move = (
        _moves(root).get(row["destination"])
        if (root / "menu-moves.json").is_file()
        else None
    )
    if move is None:
        raw = _menu_bytes(root, row["destination"])
        revision = _revisions(root).get(row["destination"])
        if revision is None:
            if ((root / "menu-consolidations.json").is_file()
                    and hashlib.sha256(raw).hexdigest() != row["destination_sha256"]):
                raise ValueError("Unknown released menu hash.")
            return raw
        if (
            row.get("source_sha256") != revision.get("source_sha256")
            or row["destination_sha256"] not in {
                revision["historical_sha256"], revision["current_sha256"]
            }
            or hashlib.sha256(raw).hexdigest() != revision["current_sha256"]
        ):
            raise ValueError("Menu revision differs from its source or destination provenance.")
        historical = raw
        for edit in reversed(revision["edits"]):
            current, previous = edit["current"].encode(), edit["historical"].encode()
            if historical.count(current) != 1:
                raise ValueError("Menu revision edit is absent or ambiguous.")
            historical = historical.replace(current, previous, 1)
        if hashlib.sha256(historical).hexdigest() != revision["historical_sha256"]:
            raise ValueError("Menu revision changed more than its recorded edits.")
        return historical if row["destination_sha256"] == revision["historical_sha256"] else raw
    raw = _menu_bytes(root, move["destination"])
    if (
        row["destination_sha256"] != move["original_sha256"]
        or hashlib.sha256(raw).hexdigest() != move["destination_sha256"]
    ):
        raise ValueError("Moved menu source hash differs from its reviewed provenance.")
    revision = _revisions(root).get(move["destination"])
    if revision is not None:
        # Undo recorded docstring edits before undoing the historical path move.
        raw = released_bytes(root, {
            **row,
            "destination": move["destination"],
            "destination_sha256": revision["historical_sha256"],
        })
    old, new = move["original_header"].encode(), move["destination_header"].encode()
    if not raw.startswith(new):
        raise ValueError("Moved menu header differs from its reviewed prefix.")
    original = old + raw[len(new) :]
    if hashlib.sha256(original).hexdigest() != move["original_sha256"]:
        raise ValueError("Moved menu changed more than its reviewed header.")
    return original


def _revisions(root: Path) -> dict[str, dict]:
    """Read the optional exact edit ledger without rewriting historical rows."""
    path = root / "menu-revisions.json"
    rows = json.loads(path.read_text())["revisions"] if path.is_file() else []
    result = {row["destination"]: row for row in rows}
    if len(result) != len(rows):
        raise ValueError("Duplicate menu revision.")
    return result


def current_rows(root: Path) -> list[dict]:
    """Resolve historical or already-current routes without rewriting the manifest."""
    rows = json.loads((root / "migration.json").read_text())
    moves = _moves(root)
    destinations = {move["destination"]: move for move in moves.values()}
    represented = {row["destination"] for row in rows}
    for original, move in moves.items():
        if len({original, move["destination"]} & represented) != 1:
            raise ValueError("Menu move needs one known migration identity.")
    result = []
    for row in rows:
        move = moves.get(row["destination"])
        current = destinations.get(row["destination"])
        if current is not None and move is None:
            if row["destination_sha256"] != current["destination_sha256"]:
                raise ValueError("Current menu hash differs from its reviewed provenance.")
            move = current
            historical = {
                **row,
                "destination": move["original"],
                "destination_sha256": move["original_sha256"],
            }
        else:
            historical = row
        if move is None:
            result.append(dict(row))
        else:
            released_bytes(root, historical)
            result.append(
                {
                    **row,
                    "destination": move["destination"],
                    "destination_sha256": move["destination_sha256"],
                }
            )
    revisions = _revisions(root)
    additional_path = root / "additional-tools.json"
    additional = json.loads(additional_path.read_text()) if additional_path.is_file() else []
    if not revisions.keys() <= {row["destination"] for row in [*result, *additional]}:
        raise ValueError("Menu revision has no known migration identity.")
    for row in additional:
        if row["destination"] in revisions:
            released_bytes(root, row)
    for row in result:
        if row["destination"] in revisions:
            released_bytes(root, row)
            row["destination_sha256"] = revisions[row["destination"]]["current_sha256"]
    return result


def active_menu_paths(root: Path) -> set[str]:
    """Project validated transitions without replacing immutable historical rows."""
    transitions = consolidation_rows(root)
    additional = json.loads((root / "additional-tools.json").read_text())
    paths = {row["destination"] for row in [*current_rows(root), *additional]}
    implemented = [row for row in transitions if row["acceptance"]["state"] == "implemented"]
    paths.difference_update(row["source"]["path"] for row in implemented)
    paths.update(row["destination"]["path"] for row in implemented if row["destination"])
    return paths


def _inside(root: Path, relative: str, *, menu: bool = True) -> Path:
    """Reject traversal and symlink escapes before reading a recorded identity."""
    path = Path(relative)
    if (not relative or "\\" in relative or path.is_absolute()
            or ".." in path.parts or str(path) != relative
            or (menu and (len(path.parts) != 3 or path.parts[0] != "Scripts"
                          or path.suffix != ".py"))
            or not (root / path).resolve().is_relative_to(root.resolve())):
        raise ValueError("Invalid or escaping recorded path.")
    return root / path


def _hex(value: str, size: int) -> None:
    if not isinstance(value, str) or re.fullmatch(f"[0-9a-f]{{{size}}}", value) is None:
        raise ValueError("Expected a full immutable commit or SHA256 hash.")


def _committed_menu_paths(root: Path, commit: str) -> set[str]:
    _hex(commit, 40)
    try:
        result = subprocess.run(
            ["git", "-C", str(root), "ls-tree", "-r", "--name-only", "-z", commit, "--", "Scripts"],
            check=True, capture_output=True, timeout=30,
        )
    except (OSError, subprocess.SubprocessError) as error:
        raise ValueError("Committed inventory unavailable; accounting cannot be certified.") from error
    return {p for p in result.stdout.decode().split("\0") if p.endswith(".py")}


def source_bytes(root: Path, source: dict, *, committed: bool = False) -> bytes:
    """Read verified data, never execute archives; Git-less copies need an explicit archive."""
    path = _inside(root, source["path"])
    _hex(source["commit"], 40)
    _hex(source["sha256"], 64)
    if not committed and path.is_file():
        raw = path.read_bytes()
        if hashlib.sha256(raw).hexdigest() == source["sha256"]:
            return raw
    try:
        result = subprocess.run(
            ["git", "-C", str(root), "show", source["commit"] + ":" + source["path"]],
            check=True, capture_output=True, timeout=30,
        )
        raw = result.stdout
    except (OSError, subprocess.SubprocessError) as error:
        archive = os.environ.get("FONTLAB_MENU_ARCHIVE")
        path = Path(archive) / (source["sha256"] + ".bin") if archive else None
        if path is None or not path.is_file():
            raise ValueError("Historical menu unavailable in Git or the explicit archive.") from error
        raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != source["sha256"]:
        raise ValueError("Historical menu hash differs from the recorded identity.")
    return raw


def consolidation_rows(root: Path) -> list[dict]:
    """Validate proposed/implemented transitions without promoting behavior or native parity."""
    ledger = json.loads((root / "menu-consolidations.json").read_text())
    rows = ledger["transitions"]
    paths = [row["source"]["path"] for row in rows]
    if (ledger["schema_version"] != 1 or len(set(paths)) != len(paths)
            or len(rows) != ledger["source_count"]
            or set(paths) != _committed_menu_paths(root, ledger["source_commit"])):
        raise ValueError("Duplicate, unknown or unaccounted consolidation source.")
    targets = set()
    for row in rows:
        source, acceptance, destination = row["source"], row["acceptance"], row["destination"]
        path = _inside(root, source["path"])
        _hex(source["sha256"], 64)
        if source["commit"] != ledger["source_commit"]:
            raise ValueError("Consolidation source commit differs from its inventory.")
        source_bytes(root, source, committed=True)
        date.fromisoformat(acceptance["date"])
        if (acceptance["state"] not in {"proposed", "implemented"}
                or type(acceptance["behavior_parity"]) is not bool
                or type(acceptance["native"]) is not bool
                or (acceptance["state"] == "proposed"
                    and (acceptance["behavior_parity"] or acceptance["native"]))):
            raise ValueError("Invalid consolidation acceptance state.")
        if acceptance["state"] == "proposed":
            if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != source["sha256"]:
                raise ValueError("Proposed source is missing or changed.")
        else:
            source_bytes(root, source)
        if not row["test_routes"] or any(
            not _inside(root, route.split("::", 1)[0], menu=False).is_file()
            for route in row["test_routes"]
        ):
            raise ValueError("Missing consolidation test route.")
        if row["disposition"] == "retired":
            if (destination is not None or not isinstance(row["retirement_reason"], str)
                    or not row["retirement_reason"].strip() or acceptance["behavior_parity"]):
                raise ValueError("Retirement needs a reason and never implies behavior parity.")
            continue
        if row["disposition"] not in {"retained", "absorbed"} or not destination:
            raise ValueError("Missing consolidation destination.")
        target = _inside(root, destination["path"])
        if (not isinstance(destination["tab"], str) or not destination["tab"].strip()
                or ("action" in destination and (not isinstance(destination["action"], str)
                    or not destination["action"].strip()))
                or row["retirement_reason"] is not None
                or (row["disposition"] == "retained") != (source["path"] == destination["path"])):
            raise ValueError("Invalid destination tab or disposition.")
        route = (destination["path"], destination["tab"], destination.get("action"))
        if route in targets:
            raise ValueError("Duplicate consolidation destination tab.")
        targets.add(route)
        if acceptance["state"] == "proposed":
            if destination["sha256"] is not None:
                raise ValueError("Proposed destinations cannot claim implemented hashes.")
        else:
            _hex(destination["sha256"], 64)
            if not target.is_file() or hashlib.sha256(target.read_bytes()).hexdigest() != destination["sha256"]:
                raise ValueError("Implemented destination is missing or has an unknown hash.")
    return rows


def _menu_bytes(root: Path, destination: str) -> bytes:
    """Keep reversible old overlays working after a reviewed implementation removes a menu."""
    path = _inside(root, destination)
    ledger = root / "menu-consolidations.json"
    if ledger.is_file():
        rows = json.loads(ledger.read_text())["transitions"]
        matches = [row for row in rows if row["source"]["path"] == destination]
        if len(matches) > 1:
            raise ValueError("Duplicate consolidation source.")
        if matches and matches[0]["acceptance"]["state"] == "implemented":
            # Byte recovery is not full inventory or workflow acceptance.
            return source_bytes(root, matches[0]["source"], committed=True)
    return path.read_bytes()
