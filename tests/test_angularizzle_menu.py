# this_file: tests/test_angularizzle_menu.py
"""Inspect the practical entry point without executing reference or host code."""

import ast
import runpy
import sys
from pathlib import Path
from types import ModuleType

MENU = Path(__file__).parents[1] / "Scripts/Contours/Angularizzle.py"


def test_angularizzle_menu_is_lazy_typed_and_dispatches_one_owned_panel(monkeypatch):
    for name in ("fly", "fly.ap"):
        module = ModuleType(name)
        module.__path__ = []
        monkeypatch.setitem(sys.modules, name, module)
    helper, calls = ModuleType("fly.ap.scripting"), []
    helper.angularizzle_dialog_type = lambda: type("Panel", (), {"KEY": "angularizzle"})
    helper.show_script_dialog = lambda panel, key: calls.append((panel.KEY, key))
    monkeypatch.setitem(sys.modules, "fly.ap.scripting", helper)
    namespace = runpy.run_path(str(MENU), run_name="inspection")
    assert calls == [], "Importing the script must leave the host untouched"
    namespace["main"]()
    assert calls == [("angularizzle", "angularizzle")]
    calls.clear()
    runpy.run_path(str(MENU), run_name="__main__")
    assert calls == [("angularizzle", "angularizzle")]
    tree = ast.parse(MENU.read_text(), feature_version=(3, 11))
    main = next(node for node in tree.body if isinstance(node, ast.FunctionDef))
    assert main.returns.value is None
