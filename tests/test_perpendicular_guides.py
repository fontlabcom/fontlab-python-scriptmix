# this_file: tests/test_perpendicular_guides.py
"""The real public Fly facade resolves the shared complete writer lazily."""

import importlib.util
from pathlib import Path


def test_public_menu_calls_complete_shared_action(monkeypatch, app_sources):
    import fontlabapp.perpendicular_guides as api

    seen = []
    monkeypatch.setattr(api, "run", lambda: seen.append("complete") or {"guides": 3})
    path = Path(__file__).parents[1] / "Scripts/Guides/Perpendicular Guides.py"
    spec = importlib.util.spec_from_file_location("owned_perpendicular_menu", path)
    menu = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(menu)
    assert menu.main() == {"guides": 3}
    assert seen == ["complete"]


def test_direct_menu_execution_uses_same_complete_fly_writer(monkeypatch, app_sources):
    import runpy
    import sys

    import fontlabapp.perpendicular_guides as api

    seen = []
    monkeypatch.setattr(api, "run", lambda: seen.append("whole action"))
    monkeypatch.delitem(sys.modules, "fly.ap.perpendicular_guides", raising=False)
    runpy.run_path(
        str(Path(__file__).parents[1] / "Scripts/Guides/Perpendicular Guides.py"),
        run_name="__main__",
    )
    assert seen == ["whole action"]
