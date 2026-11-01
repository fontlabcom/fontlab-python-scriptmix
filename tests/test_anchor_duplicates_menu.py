# this_file: tests/test_anchor_duplicates_menu.py
"""Complete duplicate-anchor route and immutable original provenance."""

import hashlib
import json
import runpy
import sys
from pathlib import Path
from types import ModuleType


def test_complete_candidate_is_lazy_and_dispatches_through_fly(monkeypatch):
    root = Path(__file__).resolve().parents[1]
    path = root / "Scripts/Anchors/Duplicates Finder.py"
    calls = []
    module = ModuleType("fly.ap.anchor_duplicates")
    module.show = lambda: calls.append("complete writer")
    monkeypatch.setitem(sys.modules, module.__name__, module)
    loaded = runpy.run_path(str(path), run_name="inspection")
    assert not calls
    loaded["main"]()
    runpy.run_path(str(path), run_name="__main__")
    assert calls == ["complete writer", "complete writer"]
    row = next(row for row in json.loads((root / "additional-tools.json").read_text()) if row["key"] == "anchors_duplicates_finder")
    assert row["destination_sha256"] == hashlib.sha256(path.read_bytes()).hexdigest()
    index = json.loads((root / "rescue-index.json").read_text())
    original = next(entry for entry in index["menus"] if entry["menu"] == row["destination"])
    assert (row["source_path"], row["source_sha256"]) == (original["target"], original["target_sha256"])
    assert row["native_acceptance"] == "pending"
    assert row["counted_in_130_sample_migration"] is False
    assert row["rescued_original_menu"] == "Scripts/Anchors/Duplicates Finder.py"
