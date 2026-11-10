# this_file: tests/test_fontui_batch_recipes_menu.py
"""Actual public entrypoint dispatch; no replacement show or font model."""
import importlib
import importlib.util
from pathlib import Path
import runpy
import subprocess
import sys
from types import SimpleNamespace

import pytest
from conftest import resolve_app_sources
APP_SOURCE = resolve_app_sources(("fontui.batch_recipes",))
APP_TESTS = APP_SOURCE.parents[1] / "tests"
assert (APP_TESTS / "test_fontui_batch_recipes.py").is_file()
sys.path.insert(0, str(APP_TESTS))
try:
    importlib.import_module("_feature_source_qt")
    from test_fontui_batch_recipes import actual_qt as _actual_qt_fixture
finally:
    sys.path.pop(0)
actual_qt = _actual_qt_fixture
del _actual_qt_fixture
ROOT = Path(__file__).resolve().parents[1]
MODULE = APP_SOURCE / "fontui/batch_recipes.py"
ENTRY = ROOT / 'Scripts/Font UI Lab/Batch UFO Recipe Workbench.py'


@pytest.mark.parametrize("dispatch", ["main", "script"])
def test_entry_when_dispatched_then_actual_workbench_without_font_or_spawn(actual_qt, monkeypatch, dispatch):
    from PySide6.QtWidgets import QMainWindow
    from PySide6.QtCore import QObject

    _, _, app = actual_qt
    parent = QMainWindow()
    items = QObject(parent)
    def forbidden(*args):
        raise AssertionError("Entry must not capture a font")
    monkeypatch.setitem(sys.modules, "fontlab", SimpleNamespace(
        MainWindow=lambda: parent, CurrentFont=forbidden,
        flItems=SimpleNamespace(instance=lambda: SimpleNamespace(qobject=items))))
    module = importlib.import_module("fontlabapp.fontui.batch_recipes")
    before = list(module._HANDLES)
    owner = None
    try:
        if dispatch == "script":
            runpy.run_path(str(ENTRY), run_name="__main__")
            owner, = [x for x in module._HANDLES if x not in before]
        else:
            spec = importlib.util.spec_from_file_location("batch_recipe_entry", ENTRY)
            entry = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(entry)
            assert module._HANDLES == before
            owner = entry.main()
        assert owner.editor.font is None and owner.editor.result is None
        assert owner.panel.sources == [] and owner.panel.process is None
        assert owner.editor.diagnostic.text == "No font supplied"
        assert owner in module._HANDLES
    finally:
        if owner is not None:
            owner.release()
            app.processEvents()
            assert owner._released
        parent.deleteLater()
        app.processEvents()


def test_import_when_optional_modules_blocked_then_product_and_entry_are_cold(tmp_path):
    code = """
import importlib.abc, importlib.util, sys
class Block(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname.split('.')[0] in ('fontlab', 'PythonQt', 'PySide6', 'PyQt6', 'fontlab_fontport', 'ufoLib2'):
            raise AssertionError('Cold import touched ' + fullname)
sys.meta_path.insert(0, Block())
for filename in sys.argv[1:]:
    spec = importlib.util.spec_from_file_location('cold_recipe_entry', filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
print('Cold import complete')
"""
    result = subprocess.run([sys.executable, "-B", "-c", code, str(MODULE), str(ENTRY)],
                            capture_output=True, text=True, timeout=20)
    assert result.returncode == 0, result.stderr
