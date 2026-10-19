# this_file: tests/test_tabular_width.py
"""Verify menu delegation with an owned fake factory, never reference code."""

import ast
import runpy
import sys
from pathlib import Path
from types import ModuleType

ROOT = Path(__file__).parents[1]
MENU = ROOT / "Scripts/Metrics/Check Tabular Widths.py"


def test_menu_is_lazy_typed_and_dispatches_once(monkeypatch):
    calls = []
    for name in ("fly", "fly.ap"):
        module = ModuleType(name)
        module.__path__ = []
        monkeypatch.setitem(sys.modules, name, module)
    api = ModuleType("fly.ap.scripting")
    api.tabular_width_dialog_type = lambda: type(
        "Panel", (), {"KEY": "check_tabular_widths"}
    )
    api.show_script_dialog = lambda kind, key: calls.append(key)
    monkeypatch.setitem(sys.modules, "fly.ap.scripting", api)
    namespace = runpy.run_path(str(MENU), run_name="inspection")
    assert calls == []
    namespace["main"]()
    assert calls == ["check_tabular_widths"]
    calls.clear()
    runpy.run_path(str(MENU), run_name="__main__")
    assert calls == ["check_tabular_widths"]
    tree = ast.parse(MENU.read_text(), feature_version=(3, 11))
    main = next(node for node in tree.body if isinstance(node, ast.FunctionDef))
    assert isinstance(main.returns, ast.Constant) and main.returns.value is None
