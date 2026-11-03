# this_file: tests/test_default_figure_geometry_runtime.py
"""Production figure panel geometry with actual Qt and isolated INI settings.

Only the selection-preview base is reduced: no font or owner preferences are
accessed. Completion and close cleanup come from the real App dependency.
"""

import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
PROGRAM = r"""
import importlib, runpy, sys, types
binding, menu_path, ini, route, fault = sys.argv[1:]
C = importlib.import_module(binding + '.QtCore')
G = importlib.import_module(binding + '.QtGui')
W = importlib.import_module(binding + '.QtWidgets')
T = importlib.import_module(binding + '.QtTest')
app = W.QApplication.instance() or W.QApplication([])
qt = types.SimpleNamespace(QtCore=C, QtGui=types.SimpleNamespace(
    **{name: getattr(W, name) for name in dir(W) if name.startswith('Q')},
    QCloseEvent=G.QCloseEvent))
sys.modules['PythonQt'] = qt
import fly
fly.__dict__['qt'] = qt
sys.modules['fly.qt'] = qt
scripting = importlib.import_module('fontlabapp.core.scripting')
completion = importlib.import_module('fontlabapp.core.completion')
selection = importlib.import_module('fontlabapp.contours.selection.panel.model')
assert completion.__file__ and scripting.__file__

class Base(W.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(self.windowFlags() | C.Qt.WindowStaysOnTopHint)
        self.original_flags = self.windowFlags()
        self.original_modality = self.windowModality()
        self._connections = []
        self.setMinimumSize(240, 180)
        self.layout_box = W.QVBoxLayout(self)
        self.build_controls()
        self.status = W.QLabel('Ready')
        self.layout_box.addWidget(self.status)
        self.close_button = W.QPushButton('Close')
        self.layout_box.addWidget(self.close_button)
        self.watch(self.close_button.clicked, self.close)
        self.resize(360, 240)
    def add_row(self, label, widget):
        self.layout_box.addWidget(widget)
    def watch(self, signal, callback=None):
        slot = lambda *args: callback() if callback else None
        signal.connect(slot)
        self._connections.append((signal, slot))
    def refresh(self):
        pass
    def closeEvent(self, event):
        scripting.close_script_dialog(self, event, self.KEY)
selection.panel_type = lambda: Base

class Settings(C.QSettings):
    broken = False
    geometry_writes = 0
    def setValue(self, key, value):
        if self.broken and fault == 'write':
            raise OSError('injected geometry write failure')
        if key == 'geometry':
            self.geometry_writes += 1
        return super().setValue(key, value)
    def status(self):
        if self.broken and fault == 'sync':
            return C.QSettings.AccessError
        return super().status()

settings = Settings(ini, C.QSettings.IniFormat)
settings.setValue('optionFigures', 2)
settings.setValue('unrelated', 'keep')
if fault == 'malformed':
    settings.setValue('geometry', 'not a geometry byte array')
settings.sync()
settings.geometry_writes = 0
menu = runpy.run_path(menu_path)
Panel = menu['panel_type'](settings)
parent = W.QWidget()
sys.modules['fontlab'] = types.SimpleNamespace(MainWindow=lambda: parent)
panel = (scripting.show_script_dialog(Panel, menu['KEY'])
         if route == 'replace' else Panel(parent))
assert panel.parent() is parent
assert panel.windowFlags() == panel.original_flags
assert panel.windowModality() == panel.original_modality
assert panel.figure_family.currentIndex() == 2
assert not panel.replace_contours.isChecked()
assert not panel.isModal()
if fault == 'malformed':
    assert panel.settings_error, 'Malformed geometry must be diagnosed'
    assert panel.close_button.isEnabled()
assert hasattr(panel, '_completion_lifetime'), 'Production completion installed'
owner = panel._completion_lifetime
sys._fontlab_samples = {menu['KEY']: panel}
panel.show()
app.processEvents()
panel.move(80, 90)
panel.resize(420, 300)
app.processEvents()
expected = panel.geometry()
connections = panel._connections
removed = []
panel.destroyed.connect(lambda *args: removed.append(True))
settings.broken = fault in ('write', 'sync')
if fault == 'save':
    def fail_save():
        raise OSError('injected saveGeometry failure')
    panel.saveGeometry = fail_save
if route == 'replace':
    replacement = scripting.show_script_dialog(Panel, menu['KEY'])
    app.processEvents()
    assert replacement is not panel
    assert sys._fontlab_samples[menu['KEY']] is replacement
    assert replacement.geometry() == expected
    assert replacement.figure_family.currentIndex() == 2
    assert replacement.parent() is parent
    assert replacement.windowFlags() == replacement.original_flags
    assert replacement.windowModality() == replacement.original_modality
    replacement.close()
elif route == 'button':
    panel.close_button.click()
elif route == 'reject':
    panel.reject()
elif route == 'escape':
    T.QTest.keyClick(panel, C.Qt.Key_Escape)
else:
    panel.close()
assert owner.closed and owner.dialog is None
owner.complete()
owner.complete()
assert settings.geometry_writes == (
    0 if fault in ('write', 'save') else 2 if route == 'replace' else 1)
assert not connections, 'Owned control callbacks disconnected'
assert menu['KEY'] not in sys._fontlab_samples
if fault in ('write', 'sync', 'save'):
    assert getattr(panel, 'slot_error', '') or panel.settings_error
C.QCoreApplication.sendPostedEvents(None, C.QEvent.DeferredDelete)
app.processEvents()
assert removed, 'Panel deletion must survive dismissal and settings failures'
settings.broken = False
assert int(settings.value('optionFigures')) == 2
assert settings.value('unrelated') == 'keep'
if fault in ('none', 'malformed'):
    reopened_settings = C.QSettings(ini, C.QSettings.IniFormat)
    second = menu['panel_type'](reopened_settings)(parent)
    second.show()
    app.processEvents()
    assert second.parent() is parent
    assert second.windowFlags() == second.original_flags
    assert second.windowModality() == second.original_modality
    assert second.geometry() == expected, (second.geometry(), expected)
    assert second.figure_family.currentIndex() == 2
    assert not second.replace_contours.isChecked()
    second.close()
    C.QCoreApplication.sendPostedEvents(None, C.QEvent.DeferredDelete)
print('Qt', C.qVersion(), 'App completion', completion.__file__, route, fault, 'PASS')
"""


@pytest.mark.parametrize(
    "route,fault",
    [(route, "none") for route in ("close", "button", "reject", "escape", "replace")]
    + [("close", fault) for fault in ("malformed", "write", "sync", "save")],
)
def test_geometry_when_dismissed_then_persists_and_releases_owned_panel(
    tmp_path, route, fault
):
    binding = "PyQt5" if os.environ.get("FONTLABAPP_TEST_QT5") else "PySide6"
    pytest.importorskip(binding + ".QtCore")
    result = subprocess.run(
        [
            sys.executable,
            "-B",
            "-c",
            PROGRAM,
            binding,
            str(ROOT / "Scripts/Components/Set Default Figures.py"),
            str(tmp_path / "figures.ini"),
            route,
            fault,
        ],
        env={**os.environ, "QT_QPA_PLATFORM": "offscreen"},
        capture_output=True,
        text=True,
        timeout=25,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "PASS" in result.stdout
    print(result.stdout.strip())
