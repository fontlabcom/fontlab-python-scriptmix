# this_file: tests/test_master_point_counts_menu.py
"""Typed lazy entry point keeps the Reza workflow distinct from the Slob report."""

import ast
import runpy
import sys
from pathlib import Path
from types import ModuleType

ROOT = Path(__file__).resolve().parents[1]
MENU = ROOT / "Scripts/Reports/Point Counter (Master Layers).py"


def test_master_point_counter_menu_when_called_then_one_public_Fly_dispatch(
    monkeypatch,
):
    calls = []
    for name in ("fly", "fly.ap"):
        module = ModuleType(name)
        module.__path__ = []
        monkeypatch.setitem(sys.modules, name, module)
    module = ModuleType("fly.ap.master_point_counts")
    module.show = lambda: calls.append(True)
    monkeypatch.setitem(sys.modules, module.__name__, module)
    ns = runpy.run_path(str(MENU), run_name="inspection")
    assert calls == []
    ns["main"]()
    assert calls == [True]
    runpy.run_path(str(MENU), run_name="__main__")
    assert calls == [True, True]
    ast.parse(MENU.read_text(), feature_version=(3, 11))
