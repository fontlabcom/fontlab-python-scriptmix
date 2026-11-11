# this_file: tests/test_contour_selection_menus.py
"""Retained callable selection routes and the consolidated studio launcher."""

import runpy
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize(
    "title,function,result",
    [
        ("Select Contours", "select_contours", 2),
        ("Select Partial Contours", "select_partial_contours", 1),
        ("Select Small Contours", "show_small_contours", object()),
    ],
)
def test_actual_fly_facades_dispatch_public_app_actions(
    monkeypatch, title, function, result
):
    import fly.ap.contours.selection.model as alias
    import fontlabapp.contours.selection.model as canonical

    assert alias is canonical
    calls = []
    monkeypatch.setattr(canonical, function, lambda: calls.append(function) or result)
    assert getattr(alias, function)() is result
    assert getattr(alias, function)() is result
    assert calls == [function, function]


def test_consolidated_menu_opens_owned_studio(monkeypatch):
    import sys
    from types import ModuleType

    module = ModuleType("fontlabapp.fontui.contour_selection")
    calls = []
    result = object()
    module.show = lambda: calls.append("show") or result
    monkeypatch.setitem(sys.modules, module.__name__, module)
    monkeypatch.setitem(sys.modules, "fly.ap.fontui.contour_selection", module)
    script = ROOT / "Scripts/Contours/Contour Selection.py"
    namespace = runpy.run_path(str(script))
    assert namespace["main"]() is result
    runpy.run_path(str(script), run_name="__main__")
    assert calls == ["show", "show"]
