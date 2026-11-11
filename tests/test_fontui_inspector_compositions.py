# this_file: tests/test_fontui_inspector_compositions.py
"""Menu dispatch into the real App compositions and their owned cleanup."""

import importlib
from pathlib import Path
import runpy
import sys
from types import SimpleNamespace

import pytest
from conftest import resolve_app_sources

APP_SOURCE = resolve_app_sources(("fontui.ufo_roundtrip", "fontui.representation_notifications"))
APP_TESTS = APP_SOURCE.parents[1] / "tests"
sys.path.insert(0, str(APP_TESTS))
try:
    _ufo = importlib.import_module("test_fontui_ufo_roundtrip")
    _representations = importlib.import_module("test_fontui_representation_notifications")
finally:
    sys.path.pop(0)
composition_env = _ufo.composition_env
ufo_env = _ufo.env
representation_env = _representations.env
ROOT = Path(__file__).resolve().parents[1]


def dispatch(monkeypatch, title, font, route):
    calls = []

    class World:
        def CurrentFont(self):
            calls.append(font)
            return font

    monkeypatch.setitem(sys.modules, "fontlab_fontport.world", SimpleNamespace(FontWorld=World))
    namespace = runpy.run_path(str(ROOT / "Scripts/Font UI Lab" / (title + ".py")), run_name=route)
    result = namespace["main"]() if route == "inspection" else None
    assert calls == [font]
    return result


@pytest.mark.parametrize("route", ("inspection", "__main__"))
def test_roundtrip_menu_when_dispatched_then_real_staging_report_and_cleanup(ufo_env, monkeypatch, route):
    monkeypatch.setitem(sys.modules, "fontlab", SimpleNamespace(MainWindow=lambda: ufo_env.parent))
    font = _ufo.RFont(_ufo.UFOBackend(_ufo.source()))
    result = dispatch(monkeypatch, "UFO Roundtrip Inspector", font, route)
    owner = ufo_env.module._HANDLES[-1]
    try:
        if route == "inspection":
            assert result is owner
        assert owner.font is font and owner.report is None
        owner.inspect_button.clicked.emit()
        assert owner.report and "source_to_imported" in owner.text.toPlainText()
        assert "Temporary staging removed" in owner.status.text
    finally:
        owner.close()
    assert owner._close_complete and owner not in ufo_env.module._HANDLES
    assert not font._backend.closed


@pytest.mark.parametrize("route", ("inspection", "__main__"))
def test_representation_menu_when_dispatched_then_real_notifications_and_cleanup(representation_env, monkeypatch, route):
    _qt, module = representation_env
    font = _representations.live_font()
    result = dispatch(monkeypatch, "Representation and Notification Explorer", font, route)
    owner = module._HANDLES[-1]
    model = font["A"].naked()
    try:
        if route == "inspection":
            assert result is owner
        _representations.choose(owner.browser, ["A"])
        assert owner.rows and owner.font is font
        assert model.hasObserver(owner, "Glyph.Changed")
        font["A"].scaleBy((2, 1))
        assert owner.notifications > 0
        assert "notification refresh completed" in owner.status.text
    finally:
        owner.close()
    assert owner._close_complete and owner not in module._HANDLES
    assert not model.hasObserver(owner, "Glyph.Changed")
