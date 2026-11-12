# this_file: tests/test_wp03_launchers.py
"""The eight WP03 menus dispatch lazily to their distinct shared App studios."""

import builtins
import runpy
import sys
from pathlib import Path
from types import ModuleType

import pytest

ROOT = Path(__file__).resolve().parents[1]
ROUTES = {
    "Font Info/Font Metrics": ("vertical_metrics.app", "show_font_metrics", {}),
    "Metrics/Spacing Studio": ("spacing_studio", "show", {}),
    "Metrics/Advance Widths": ("advance_widths", "show", {}),
    "Metrics/Vertical Metrics": ("vertical_metrics.app", "show_vertical_metrics", {}),
    "Kerning/Kerning Studio": ("kerning_studio", "show", {"consolidated": True}),
    "Kerning/Kerning Batch": ("kerning_batch", "show", {"consolidated": True}),
    "Kerning/Kerning Browser": ("kerning_browser", "show", {"consolidated": True}),
    "Kerning/Kerning Proof": ("kerning_proof", "show", {}),
}


@pytest.mark.parametrize("route", ROUTES)
def test_menu_import_and_main_preserve_exact_studio_result(monkeypatch, route):
    module, entry, arguments = ROUTES[route]
    calls, result = [], object()
    fake = ModuleType("fly.ap.studios." + module)
    setattr(fake, entry, lambda **kwargs: calls.append(kwargs) or result)
    monkeypatch.setitem(sys.modules, fake.__name__, fake)
    path = ROOT / "Scripts" / (route + ".py")
    loaded = runpy.run_path(str(path), run_name="inspection")
    assert calls == [], "Menu discovery must not open a window or capture a font"
    assert loaded["main"]() is result
    assert calls == [arguments]
    runpy.run_path(str(path), run_name="__main__")
    assert calls == [arguments, arguments]
    assert path.read_text().splitlines()[0] == "# this_file: Scripts/" + route + ".py"


@pytest.mark.parametrize("route", ROUTES)
def test_menu_preserves_studio_failure_without_retry(monkeypatch, route):
    module, entry, _arguments = ROUTES[route]
    calls = []

    def fail(**kwargs):
        calls.append(kwargs)
        raise RuntimeError("captured font closed")

    fake = ModuleType("fly.ap.studios." + module)
    setattr(fake, entry, fail)
    monkeypatch.setitem(sys.modules, fake.__name__, fake)
    loaded = runpy.run_path(str(ROOT / "Scripts" / (route + ".py")), run_name="inspection")
    with pytest.raises(RuntimeError, match="captured font closed"):
        loaded["main"]()
    assert len(calls) == 1


def test_spacing_preserves_missing_tmetrics_dependency_guidance(monkeypatch, capsys):
    path = ROOT / "Scripts/Metrics/Spacing Studio.py"
    loaded = runpy.run_path(str(path), run_name="inspection")
    real_import = builtins.__import__

    def unavailable(name, *args, **kwargs):
        if name == "fly.ap.studios.spacing_studio":
            raise ImportError("Fontport is unavailable")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", unavailable)
    assert loaded["main"]() is None
    output = capsys.readouterr().out
    assert "fontlabapp.fontui.tmetrics" in output
    assert "fontlab-fontlabapp[fontport]" in output and "fontlab-fly" in output
    assert "Fontport is unavailable" in output
