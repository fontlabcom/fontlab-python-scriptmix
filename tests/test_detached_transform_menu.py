# this_file: tests/test_detached_transform_menu.py
"""Actual source dispatch through FontWorld and the detached composition."""
import importlib
import importlib.util
import json
from pathlib import Path
import runpy
import subprocess
import sys
from types import SimpleNamespace

import pytest
from conftest import resolve_app_sources

APP_SOURCE = resolve_app_sources(('fontui.detached_transform',))
APP_TESTS = APP_SOURCE.parents[1] / 'tests'
assert (APP_TESTS / '_detached_transform_fixture.py').is_file(), 'The paired App source tests are required'
sys.path.insert(0, str(APP_TESTS))
try:
    from _detached_transform_fixture import scene as _scene_fixture, LAYER, TARGET
finally:
    sys.path.pop(0)
ROOT = Path(__file__).resolve().parents[1]
ENTRY = ROOT / 'Scripts/Font UI Lab/Detached Transform Preview.py'
MODULE = APP_SOURCE / 'fontui/detached_transform.py'

scene = _scene_fixture


@pytest.mark.parametrize('entry', ['menu.py'])
@pytest.mark.parametrize('target', ['none', 'empty', 'rich'])
@pytest.mark.parametrize('dispatch', ['main', 'script'])
def test_entry_when_once_captured_then_actual_world_and_composition(scene, monkeypatch, entry, target, dispatch):
    from PySide6.QtWidgets import QMainWindow
    from PySide6.QtCore import QObject
    from fontlab_fontport import application
    from fontlab_fontport.memory import UFOBackend
    from ufoLib2 import Font

    parent = QMainWindow(); scene.parents.append(parent)
    items = QObject(parent)
    monkeypatch.setitem(sys.modules, 'fontlab', SimpleNamespace(
        MainWindow=lambda: parent,
        flItems=SimpleNamespace(instance=lambda: SimpleNamespace(qobject=items))))
    # An explicit owned application boundary drives the real FontWorld methods.
    # The UI, models, returned RFont and new show function are all actual objects.
    backend = UFOBackend(Font()) if target == 'empty' else scene.fonts[1]._backend
    calls = []
    selected = [None if target == 'none' else 2]
    def current():
        calls.append(selected[0])
        return selected[0]
    adapter = SimpleNamespace(font_ids=lambda: [2], current_font_id=current,
                              backend=lambda identifier, owned=False: backend)
    monkeypatch.setattr(application, 'NativeApplication', lambda: adapter)
    assert importlib.import_module('fontlabapp.fontui.detached_transform') is scene.module
    assert importlib.import_module('fly.ap.fontui.detached_transform') is scene.module
    before = list(scene.module._HANDLES)
    if dispatch == 'script':
        runpy.run_path(str(ENTRY), run_name='__main__')
        owner = next(item for item in scene.module._HANDLES if item not in before)
    else:
        spec = importlib.util.spec_from_file_location('source_entry', ENTRY)
        module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
        owner = module.main()
    scene.owners.append(owner)
    assert calls == [selected[0]]
    assert owner in scene.module._HANDLES and owner.active is None
    assert owner.layer_control.currentIndex == owner.glyph_control.currentIndex == -1
    if target == 'none':
        assert owner.font is None and not owner.capture()
    else:
        assert owner.font._backend is backend and owner.font._layers == {}
        if target == 'empty':
            assert not owner.capture() and owner.font is not None
        else:
            owner.layer_control.setCurrentIndex(owner.layer_control.findText(LAYER))
            owner.glyph_control.setCurrentIndex(owner.glyph_control.findText(TARGET))
            assert owner.capture(), owner.status.text
            selected[0] = None
            owner.active.editor.matrix['xx'].setText('2')
            assert owner.valid and owner.active.after.run.glyphs[0].advance == 1200.5
            assert calls == [2] and owner.font._backend is backend and owner.font._layers == {}
    assert owner._release_now() and not backend.closed
    if target == 'empty':
        backend.close()


def test_cold_import_when_optional_native_modules_blocked_then_inert(tmp_path):
    code = '''
import importlib.abc, importlib.util, sys
class Block(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname.split('.')[0] in ('fontlab', 'PythonQt', 'PySide6', 'PyQt6', 'fontlab_fontport', 'ufoLib2'):
            raise AssertionError('Cold import touched ' + fullname)
sys.meta_path.insert(0, Block())
for filename in sys.argv[1:]:
    spec = importlib.util.spec_from_file_location('cold_candidate', filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
assert module.main
print('Product and entry cold imports are inert')
'''
    argv = [sys.executable, '-B', '-c', code, str(MODULE), str(ENTRY)]
    (tmp_path / 'cold-request.json').write_text(json.dumps({'argv': argv, 'timeout': 20}) + '\n')
    result = subprocess.run(argv, capture_output=True, text=True, timeout=20)
    (tmp_path / 'cold-result.json').write_text(json.dumps({'returncode': result.returncode, 'stdout': result.stdout, 'stderr': result.stderr}) + '\n')
    assert result.returncode == 0, result.stderr
