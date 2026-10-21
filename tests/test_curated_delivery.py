# this_file: tests/test_curated_delivery.py
"""Reject archive dispatchers and retain the complete source backlog."""

import ast
import hashlib
import json
import os
from pathlib import Path

from menu_layout import current_rows

ROOT = Path(__file__).resolve().parents[1]


ARCHIVE = Path(os.environ.get("FONTLAB_PRESERVED_ROOT", str(ROOT)))


def test_active_menu_contains_only_indexed_practical_tools():
    rows = current_rows(ROOT)
    extra = json.loads((ROOT / "additional-tools.json").read_text())
    expected = {row["destination"] for row in rows + extra}
    actual = {str(path.relative_to(ROOT)) for path in (ROOT / "Scripts").rglob("*.py")}
    assert actual == expected, "Only practical indexed tools belong in the active menu"
    assert len(rows) == 69 and len(extra) == 45 and len(actual) == 114
    for relative in actual:
        path = ROOT / relative
        assert len(Path(relative).parts) == 3, relative
        assert path.parent.name == path.parent.name.title(), relative
        source = path.read_text()
        ast.parse(source, filename=relative, feature_version=(3, 11))
        assert "rescued_examples" not in source, relative
        assert "# this_file: " + relative in source.splitlines()[:5], relative
        assert "native compatibility is pending" not in source, relative


def test_unported_sources_remain_a_complete_hashed_backlog():
    index = json.loads((ROOT / "rescue-index.json").read_text())
    assert len(index["menus"]) == index["new_menu_count"] == 61
    assert len(index["preserved_sources"]) == 69
    for row in index["menus"]:
        candidates = {r.get("rescued_original_menu"): r for r in json.loads((ROOT / "additional-tools.json").read_text()) if r.get("rescued_original_menu")}
        if row["menu"] in candidates:
            candidate = candidates[row["menu"]]
            assert candidate["destination"] == row["menu"]
            assert candidate["source_sha256"] == row["target_sha256"]
            assert candidate["native_acceptance"] == "pending"
            assert candidate["counted_in_130_sample_migration"] is False
        else:
            assert not (ROOT / row["menu"]).exists(), row["menu"]
        assert hashlib.sha256((ARCHIVE / row["target"]).read_bytes()).hexdigest() == row["target_sha256"]
    assert (ROOT / "PORTING-BACKLOG.md").is_file(), "Keep unfinished ports visible"


def test_active_menu_has_no_stale_sourceless_compiled_launchers():
    stale = [str(path.relative_to(ROOT)) for path in (ROOT / "Scripts").rglob("*.pyc")
             if "__pycache__" not in path.parts]
    assert not stale, f"Preserve and remove old compiled menu entries: {stale}"
