# this_file: tests/test_tabular_width.py
"""Verify menu delegation with an owned fake factory, never reference code."""

import ast
import runpy
import sys
from pathlib import Path
from types import ModuleType

ROOT = Path(__file__).parents[1]
MENU = ROOT / "Scripts/Metrics/Advance Widths.py"


def test_menu_is_lazy_typed_and_dispatches_once(monkeypatch):
    calls = []
    for name in ("fly", "fly.ap"):
        module = ModuleType(name)
        module.__path__ = []
        monkeypatch.setitem(sys.modules, name, module)
    api = ModuleType("fly.ap.studios.advance_widths")
    api.show = lambda: calls.append("Advance Widths")
    monkeypatch.setitem(sys.modules, "fly.ap.studios.advance_widths", api)
    namespace = runpy.run_path(str(MENU), run_name="inspection")
    assert calls == []
    namespace["main"]()
    assert calls == ["Advance Widths"]
    calls.clear()
    runpy.run_path(str(MENU), run_name="__main__")
    assert calls == ["Advance Widths"]
    from _wp03_metrics_tabs import historical_text
    tree = ast.parse(historical_text(ROOT / "Scripts/Metrics/Check Tabular Widths.py"), feature_version=(3, 11))
    main = next(node for node in tree.body if isinstance(node, ast.FunctionDef))
    assert isinstance(main.returns, ast.Constant) and main.returns.value is None
