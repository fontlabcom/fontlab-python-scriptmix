# this_file: tests/test_issue208_app_reach_tools.py
"""Each Issue 208 menu tool calls exactly one shared App entry point, lazily."""

import ast
import hashlib
import json
import runpy
import sys
from pathlib import Path
from types import ModuleType

import pytest

ROOT = Path(__file__).resolve().parents[1]

# script -> (App module path under fly.ap, entry point it must call)
SHOW_TOOLS = {
    "Scripts/Names/Glyph Metadata Tree.py": ("glyphs.tree.model", "show_tree"),
    "Scripts/Names/Glyph Name Completion.py": ("glyphs.completion.model", "show"),
    "Scripts/Components/Component Graph.py": ("components.graph.model", "show"),
    "Scripts/Metrics/Sidebearing Offset Preview.py": ("metrics.offset.model", "show"),
    "Scripts/Proof/Character Map.py": ("glyphs.character_map.model", "show"),
    "Scripts/Utilities/Find Font Files.py": ("qt.find_files.model", "show"),
    "Scripts/Utilities/Reference Image Viewer.py": ("qt.images.viewer.model", "show"),
}
RINGS = ROOT / "Scripts/Anchors/Duplicate Anchor Rings.py"
ALL_TOOLS = [*SHOW_TOOLS, str(RINGS.relative_to(ROOT))]


def stub_show(monkeypatch, module: str, entry: str) -> tuple[list, object]:
    """Install a fake App module; return its call log and the sentinel it returns."""
    calls, sentinel = [], object()
    fake = ModuleType("fly.ap." + module)
    setattr(fake, entry, lambda *args: calls.append(args) or sentinel)
    monkeypatch.setitem(sys.modules, "fly.ap." + module, fake)
    return calls, sentinel


@pytest.mark.parametrize("script", SHOW_TOOLS)
def test_main_when_called_then_opens_the_one_app_entry_point(monkeypatch, script):
    module, entry = SHOW_TOOLS[script]
    calls, sentinel = stub_show(monkeypatch, module, entry)
    namespace = runpy.run_path(str(ROOT / script), run_name="inspection")
    assert calls == [], "importing the script must not open a panel"
    assert namespace["main"]() is sentinel, "main returns the panel the App opened"
    assert calls == [()], "the entry point takes no arguments"


@pytest.mark.parametrize("script", SHOW_TOOLS)
def test_script_when_run_as_main_then_opens_once(monkeypatch, script):
    module, entry = SHOW_TOOLS[script]
    calls, _ = stub_show(monkeypatch, module, entry)
    runpy.run_path(str(ROOT / script), run_name="__main__")
    assert calls == [()]


def stub_rings(monkeypatch) -> tuple[list, type]:
    calls, panel = [], type("RingsPanel", (), {})
    fake = ModuleType("fly.ap.core.scripting")
    fake.canvas_anchor_rings_dialog_type = lambda: panel
    fake.show_script_dialog = lambda kind, key: calls.append((kind, key)) or "shown"
    monkeypatch.setitem(sys.modules, "fly.ap.core.scripting", fake)
    return calls, panel


def test_rings_main_when_called_then_shows_the_panel_under_its_key(monkeypatch):
    calls, panel = stub_rings(monkeypatch)
    namespace = runpy.run_path(str(RINGS), run_name="inspection")
    assert calls == [], "importing the script must not open a panel"
    assert namespace["main"]() == "shown"
    assert calls == [(panel, "canvas_duplicate_anchor_rings")]


def test_rings_script_when_run_as_main_then_shows_once(monkeypatch):
    calls, panel = stub_rings(monkeypatch)
    runpy.run_path(str(RINGS), run_name="__main__")
    assert calls == [(panel, "canvas_duplicate_anchor_rings")]


@pytest.mark.parametrize("script", ALL_TOOLS)
def test_module_level_when_parsed_then_imports_only_the_standard_library(script):
    tree = ast.parse((ROOT / script).read_text(), feature_version=(3, 11))
    for node in tree.body:
        if isinstance(node, ast.Import):
            roots = [alias.name.split(".")[0] for alias in node.names]
        elif isinstance(node, ast.ImportFrom):
            roots = [(node.module or "").split(".")[0]]
        else:
            continue
        assert set(roots) <= sys.stdlib_module_names, f"{script}: lazy imports only"


@pytest.mark.parametrize("script", ALL_TOOLS)
def test_row_when_indexed_then_matches_the_final_script_bytes(script):
    rows = [r for r in json.loads((ROOT / "additional-tools.json").read_text())
            if r["destination"] == script]
    assert len(rows) == 1, f"{script}: exactly one additional-tools row"
    row = rows[0]
    assert row["destination_sha256"] == hashlib.sha256((ROOT / script).read_bytes()).hexdigest()
    assert row["kind"] == "independent-original-workflow-implementation"
    assert row["native_acceptance"] == "pending" and row["app_minimum"] == "1.2.0"
    assert row["counted_in_130_sample_migration"] is False
    assert row["license"] == "Apache-2.0" and row["source_body_redistributed"] is False
