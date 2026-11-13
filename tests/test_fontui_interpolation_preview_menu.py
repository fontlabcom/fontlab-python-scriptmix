# this_file: tests/test_fontui_interpolation_preview_menu.py
"""Menu dispatch captures one real FontWorld view and preserves failures."""

import ast
import hashlib
import json
from pathlib import Path
import runpy
import sys
from types import ModuleType

import pytest

ROOT = Path(__file__).resolve().parents[1]
ENTRY = ROOT / "Scripts/Font UI Lab/Interpolation Preview.py"


@pytest.mark.parametrize("active", [None, 1, 2])
@pytest.mark.parametrize("route", ["inspection", "__main__"])
def test_menu_when_invoked_then_one_real_world_capture(monkeypatch, active, route):
    from fontlab_fontport import application
    from fontlab_fontport.live import RFont
    from fontlab_fontport.memory import UFOBackend
    from ufoLib2 import Font

    backends = {identifier: UFOBackend(Font()) for identifier in (1, 2)}
    calls = []

    class Host:
        def __init__(self):
            calls.append("world")

        def font_ids(self):
            return [1, 2]

        def current_font_id(self):
            calls.append("current")
            return active

        def backend(self, identifier, *, owned):
            assert owned is False
            return backends[identifier]

    sentinel = object()
    app = ModuleType("fontlabapp.fontui.interpolation_preview")

    def show(font):
        calls.append("show")
        if active is None:
            assert font is None
        else:
            assert isinstance(font, RFont) and font._backend is backends[active]
        return sentinel

    app.show = show
    monkeypatch.setitem(sys.modules, app.__name__, app)
    monkeypatch.setitem(sys.modules, "fly.ap.fontui.interpolation_preview", app)
    monkeypatch.setattr(application, "NativeApplication", Host)
    namespace = runpy.run_path(str(ENTRY), run_name=route)
    if route == "inspection":
        assert not calls
        assert namespace["main"]() is sentinel
    assert calls == ["world", "current", "show"]
    assert all(not backend.closed for backend in backends.values())


@pytest.mark.parametrize("failure", ["capture", "show"])
def test_menu_when_boundary_fails_then_exception_is_not_hidden(monkeypatch, failure):
    calls = []
    world = ModuleType("fontlab_fontport.world")
    app = ModuleType("fontlabapp.fontui.interpolation_preview")

    class FontWorld:
        def CurrentFont(self):
            calls.append("capture")
            if failure == "capture":
                raise RuntimeError("capture failed")
            return None

    def show(font):
        calls.append("show")
        raise RuntimeError("show failed")

    world.FontWorld = FontWorld
    app.show = show
    monkeypatch.setitem(sys.modules, world.__name__, world)
    monkeypatch.setitem(sys.modules, app.__name__, app)
    monkeypatch.setitem(sys.modules, "fly.fp.world", world)
    monkeypatch.setitem(sys.modules, "fly.ap.fontui.interpolation_preview", app)
    namespace = runpy.run_path(str(ENTRY), run_name="inspection")
    assert not calls
    with pytest.raises(RuntimeError, match=f"{failure} failed"):
        namespace["main"]()
    assert calls == (["capture"] if failure == "capture" else ["capture", "show"])


def test_menu_when_catalogued_then_exact_source_and_pending_native():
    rows = json.loads((ROOT / "additional-tools.json").read_text())
    row, = [row for row in rows if row["key"] == "font_ui_lab_interpolation_preview"]
    assert row["destination"] == str(ENTRY.relative_to(ROOT))
    assert row["destination_sha256"] == hashlib.sha256(ENTRY.read_bytes()).hexdigest()
    assert row["app_api"] == "fontlabapp.fontui.interpolation_preview.show"
    assert row["native_acceptance"] == "pending"
    assert not row["source_body_redistributed"]
    assert not row["counted_in_130_sample_migration"]
    assert row["license"] == "Apache-2.0"
    assert "reviewed commit" in row["provenance_pending"]
    assert "app_minimum" not in row and "source_url" not in row
    tree = ast.parse(ENTRY.read_text(), feature_version=(3, 11))
    assert not any(isinstance(node, (ast.Import, ast.ImportFrom)) for node in tree.body)
    imports = [node for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)]
    assert {node.module for node in imports} == {
        "fly.fp.world", "fly.ap.fontui.interpolation_preview",
    }
