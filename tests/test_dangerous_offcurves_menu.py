# this_file: tests/test_dangerous_offcurves_menu.py
"""Typed lazy entry point keeps the complete all-font action behind its public facade."""

import ast
import runpy
import sys
from pathlib import Path
from types import ModuleType

ROOT = Path(__file__).resolve().parents[1]
MENU = ROOT / "Scripts/Reports/Dangerous Offcurves.py"


def test_master_point_counter_menu_when_called_then_one_public_Fly_dispatch(
    monkeypatch,
):
    calls = []
    for name in ("fly", "fly.ap"):
        module = ModuleType(name)
        module.__path__ = []
        monkeypatch.setitem(sys.modules, name, module)
    module = ModuleType("fly.ap.dangerous_offcurves")
    module.show = lambda: calls.append(True)
    monkeypatch.setitem(sys.modules, module.__name__, module)
    ns = runpy.run_path(str(MENU), run_name="inspection")
    assert calls == []
    ns["main"]()
    assert calls == [True]
    runpy.run_path(str(MENU), run_name="__main__")
    assert calls == [True, True]
    ast.parse(MENU.read_text(), feature_version=(3, 11))
