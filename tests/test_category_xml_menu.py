# this_file: tests/test_category_xml_menu.py
"""Check the full lazy Fly route and exact supplied category policy."""

import runpy
import sys
from pathlib import Path
from types import ModuleType


def test_menu_preserves_category_policy_and_shared_panel(monkeypatch):
    calls = []
    for name in ("fly", "fly.ap", "fly.gp", "fly.gp.glyphsapp"):
        module = ModuleType(name)
        module.__path__ = []
        monkeypatch.setitem(sys.modules, name, module)
    policy = lambda *_: (None, None)
    info = ModuleType("fly.gp.glyphsapp.glyph_info")
    info.glyph_categories = policy
    api = ModuleType("fly.ap.category_xml")

    def show(classifier):
        assert classifier is policy
        calls.append("category_xml")

    api.show = show
    for module in (info, api):
        monkeypatch.setitem(sys.modules, module.__name__, module)
    path = Path(__file__).parents[1] / "Scripts/Reports/Categories to XML Lib Key.py"
    result = runpy.run_path(str(path), run_name="inspection")
    assert calls == []
    result["main"]()
    assert calls == ["category_xml"]
    calls.clear()
    runpy.run_path(str(path), run_name="__main__")
    assert calls == ["category_xml"]
