# this_file: tests/test_fontui_master_browsers_menus.py
"""Capture-once dispatch and additive provenance for master browser menus."""
import ast
import hashlib
import importlib
import json
from pathlib import Path
import runpy
import sys
from types import ModuleType

import pytest

ROOT = Path(__file__).resolve().parents[1]
CASES = (
    ("Open Fonts and Master Overview", "open_fonts_overview"),
    ("Master Compatibility Browser", "master_compatibility"),
    ("Node Counts Across Masters", "node_counts_masters"),
)


@pytest.mark.parametrize("title,module", CASES)
@pytest.mark.parametrize("font", [None, object()])
@pytest.mark.parametrize("route", ["inspection", "__main__"])
def test_menu_when_dispatched_then_captures_once_and_returns_owner(monkeypatch, title, module, font, route):
    calls = []
    owner = object()
    app = ModuleType("fontlabapp.fontui." + module)
    app.show = lambda value: calls.append(("show", value)) or owner
    world = ModuleType("fontlab_fontport.world")

    class FontWorld:
        def __init__(self):
            calls.append(("world", self))

        def CurrentFont(self):
            calls.append(("current",))
            return font

    world.FontWorld = FontWorld
    monkeypatch.setitem(sys.modules, app.__name__, app)
    monkeypatch.setitem(sys.modules, world.__name__, world)
    monkeypatch.setitem(sys.modules, "fly.ap.fontui." + module, app)
    monkeypatch.setitem(sys.modules, "fly.fp.world", world)
    path = ROOT / "Scripts/Font UI Lab" / f"{title}.py"
    namespace = runpy.run_path(str(path), run_name=route)
    if route == "inspection":
        assert calls == []
        assert namespace["main"]() is owner
    target = calls[0][1]
    expected = [("world", target), ("show", target)] if module == "open_fonts_overview" else [("world", target), ("current",), ("show", font)]
    assert calls == expected


@pytest.mark.parametrize("title,module", CASES)
def test_menu_when_catalogued_then_exact_source_and_lazy_fly_imports(title, module):
    path = ROOT / "Scripts/Font UI Lab" / f"{title}.py"
    tree = ast.parse(path.read_text(), feature_version=(3, 11))
    assert not any(isinstance(node, (ast.Import, ast.ImportFrom)) for node in tree.body)
    assert {node.module for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)} == {
        "fly.fp.world", "fly.ap.fontui." + module,
    }
    rows = json.loads((ROOT / "additional-tools.json").read_text())
    row, = [row for row in rows if row["key"] == "font_ui_lab_" + module]
    assert row["destination"] == str(path.relative_to(ROOT))
    assert row["destination_sha256"] == hashlib.sha256(path.read_bytes()).hexdigest()
    assert row["app_api"] == f"fontlabapp.fontui.{module}.show"
    assert row["native_acceptance"] == "pending" and row["license"] == "Apache-2.0"
    assert row["source_body_redistributed"] is False
    assert row["counted_in_130_sample_migration"] is False
    assert "app_minimum" not in row and "source_url" not in row
    assert "reviewed commit" in row["provenance_pending"]


@pytest.mark.parametrize("title,module", CASES)
def test_menu_when_paired_app_loaded_then_shared_show_exists(title, module):
    loaded = importlib.import_module("fontlabapp.fontui." + module)
    assert callable(loaded.show)
    assert "show" in loaded.__all__
