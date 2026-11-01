# this_file: tests/test_point_counts_menu.py
"""Check the typed lazy menu without loading FontLab or a reference body."""

import ast
import runpy
import sys
from pathlib import Path
from types import ModuleType

ROOT = Path(__file__).parents[1]
MENU = ROOT / "Scripts/Reports/Point Counter.py"


def test_menu_defers_host_import_and_dispatches_exactly_once(monkeypatch):
    for name in ("fly", "fly.ap"):
        mod = ModuleType(name)
        mod.__path__ = []
        monkeypatch.setitem(sys.modules, name, mod)
    helper = ModuleType("fly.ap.scripting")
    calls = []
    helper.point_counts_dialog_type = lambda: type(
        "Panel", (), {"KEY": "point_counter"}
    )
    helper.show_script_dialog = lambda kind, key: calls.append(key)
    monkeypatch.setitem(sys.modules, "fly.ap.scripting", helper)
    namespace = runpy.run_path(str(MENU), run_name="inspection")
    assert calls == []
    namespace["main"]()
    assert calls == ["point_counter"]
    calls.clear()
    runpy.run_path(str(MENU), run_name="__main__")
    assert calls == ["point_counter"]
    tree = ast.parse(MENU.read_text(), feature_version=(3, 11))
    main = next(n for n in tree.body if isinstance(n, ast.FunctionDef))
    assert main.returns.value is None
