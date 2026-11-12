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
from _wp07_routes import behavior_path
from menu_layout import released_bytes
from conftest import app_names_used, app_source_path, resolve_app_sources

ROOT = Path(__file__).resolve().parents[1]

# script -> (App module path under fly.ap, entry point it must call)
SHOW_TOOLS = {
    "Scripts/Components/Component Graph.py": ("components.graph.model", "show"),
    "Scripts/Metrics/Sidebearing Offset Preview.py": ("studios.spacing_studio", "show"),
    "Scripts/Proof/Character Map.py": ("glyphs.character_map.model", "show"),
    "Scripts/Utilities/Find Font Files.py": ("qt.find_files.model", "show"),
    "Scripts/Utilities/Reference Image Viewer.py": ("qt.images.viewer.model", "show"),
}
RINGS = ROOT / "Scripts/Anchors/Duplicate Anchor Rings.py"
ALL_TOOLS = [*SHOW_TOOLS, str(RINGS.relative_to(ROOT))]


def active_path(script: str) -> Path:
    """Resolve the retired offset menu to its actual consolidated entry point."""
    if script == "Scripts/Metrics/Sidebearing Offset Preview.py":
        return ROOT / "Scripts/Metrics/Spacing Studio.py"
    return ROOT / script


def original_bytes(script: str) -> bytes:
    """Keep immutable original provenance independent of current menu placement."""
    if script != "Scripts/Metrics/Sidebearing Offset Preview.py":
        return (ROOT / script).read_bytes()
    from menu_layout import source_bytes

    rows = json.loads((ROOT / "menu-consolidations.json").read_text())["transitions"]
    source = next(row["source"] for row in rows if row["source"]["path"] == script)
    return source_bytes(ROOT, source)


def stub_show(monkeypatch, module: str, entry: str) -> tuple[list, object]:
    """Install a fake App module; return its call log and the sentinel it returns."""
    calls, sentinel = [], object()
    fake = ModuleType("fly.ap." + module)
    setattr(fake, entry, lambda *args: calls.append(args) or sentinel)
    monkeypatch.setitem(sys.modules, "fly.ap." + module, fake)
    monkeypatch.setitem(sys.modules, "fontlabapp." + module, fake)
    return calls, sentinel


@pytest.mark.parametrize("script", SHOW_TOOLS)
def test_main_when_called_then_opens_the_one_app_entry_point(monkeypatch, script):
    module, entry = SHOW_TOOLS[script]
    calls, sentinel = stub_show(monkeypatch, module, entry)
    namespace = runpy.run_path(str(behavior_path(active_path(script))), run_name="inspection")
    assert calls == [], "importing the script must not open a panel"
    assert namespace["main"]() is sentinel, "main returns the panel the App opened"
    assert calls == [()], "the entry point takes no arguments"


@pytest.mark.parametrize("script", SHOW_TOOLS)
def test_script_when_run_as_main_then_opens_once(monkeypatch, script):
    module, entry = SHOW_TOOLS[script]
    calls, _ = stub_show(monkeypatch, module, entry)
    runpy.run_path(str(behavior_path(active_path(script))), run_name="__main__")
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
    tree = ast.parse(active_path(script).read_text(), feature_version=(3, 11))
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
    assert row["destination_sha256"] == hashlib.sha256(original_bytes(script) if script == "Scripts/Metrics/Sidebearing Offset Preview.py" else released_bytes(ROOT, row)).hexdigest()
    assert row["kind"] == "independent-original-workflow-implementation"
    assert row["native_acceptance"] == "pending" and row["app_minimum"] == "1.2.0"
    assert row["counted_in_130_sample_migration"] is False
    assert row["license"] == "Apache-2.0" and row["source_body_redistributed"] is False


def top_level_names(path: Path) -> set[str]:
    """Names a module file binds at top level; parsed only, so no PythonQt import."""
    names: set[str] = set()
    for node in ast.parse(path.read_text()).body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            names.add(node.name)
        elif isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            names.update(n.id for t in targets for n in ast.walk(t) if isinstance(n, ast.Name))
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            names.update((a.asname or a.name).split(".")[0] for a in node.names)
    return names


@pytest.mark.parametrize("script", ALL_TOOLS)
def test_entry_points_when_app_scanned_then_every_name_the_tool_calls_is_defined(script):
    """Names come from the script's own imports, so an edited tool is rechecked."""
    used = app_names_used([behavior_path(active_path(script))])
    assert used and all(used.values()), f"{script}: no fly.ap names found to check"
    root = resolve_app_sources()  # SCRIPTMIX_APP_SOURCE, else the installed App
    for module, wanted in used.items():
        path = app_source_path(root, module.removeprefix("fly.ap."))
        if not path.is_file():
            path = path.with_suffix("") / "__init__.py"
        assert path.is_file(), f"{script}: App has no module {module}"
        missing = wanted - top_level_names(path)
        assert not missing, f"{script}: {module} does not define {sorted(missing)} ({path})"
