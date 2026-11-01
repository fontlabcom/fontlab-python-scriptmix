# this_file: tests/test_contour_selection_menus.py
"""All three actual menu facades resolve the installed App/Fly module aliases."""

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
    import fly.ap.contour_selection as alias
    import fontlabapp.contour_selection as canonical

    assert alias is canonical
    calls = []
    monkeypatch.setattr(canonical, function, lambda: calls.append(function) or result)
    script = ROOT / "Scripts" / "Contours" / f"{title}.py"
    namespace = runpy.run_path(str(script))
    assert namespace["main"]() is result
    runpy.run_path(str(script), run_name="__main__")
    assert calls == [function, function]
