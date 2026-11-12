# this_file: tests/_wp03_proof.py
"""Real App proof panels over the original Scriptmix native kerning fixture."""

import importlib
from types import SimpleNamespace as NS

import pytest
from _cov_b_support import Painter, make_package
from PySide6 import QtCore, QtGui, QtWidgets

APP = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])


@pytest.fixture
def proof_env(monkeypatch, real_app):
    package = make_package()
    env = NS(package=package, notified=[], shells=[], qt=None, patch=monkeypatch)
    native = NS(flWorkspace=NS(instance=lambda: NS(currentPackage=env.package, activeFontPanel=None)),
                flItems=NS(notifyChangesApplied=lambda name, objects: env.notified.append((name, objects))))
    namespaces = {}
    for source in (QtCore, QtGui, QtWidgets):
        namespaces.update({name: getattr(source, name) for name in dir(source) if name.startswith('Q')})
    qt = NS(QtCore=QtCore, QtGui=NS(**namespaces))
    env.qt = qt
    real_app(qt=qt, fontlab=native)
    for glyph in package.glyphs.values():
        width = glyph.findLayer('Bold').advanceWidth
        path = QtGui.QPainterPath()
        path.addRect(0, 0, width, 700)
        shape = NS(getContours=lambda path=path: [NS(path=lambda: path)], transform=QtGui.QTransform())
        glyph.findLayer = lambda master, width=width, shape=shape: NS(isNull=False, advanceWidth=width, shapes=[shape])
    module = importlib.import_module('fontlabapp.studios.kerning_proof')

    def open_panel(title, no_font=False):
        if no_font:
            env.package = None
        shell = module.show(package=lambda: env.package, font=lambda: None)
        env.shells.append(shell)
        env.shell = shell
        panel = shell.kerning_proof_tabs[title]
        shell.tabs.setCurrentIndex(list(shell.kerning_proof_tabs).index(title))
        return panel

    env.open = open_panel
    env.text = importlib.import_module('fontlabapp.studios.kerning_proof.text')
    env.pairs = importlib.import_module('fontlabapp.studios.kerning_proof.pairs')

    class RecordingPainter(Painter):
        created = []
        Antialiasing = QtGui.QPainter.Antialiasing

    env.painter = RecordingPainter
    yield env
    for shell in reversed(env.shells):
        shell.close()
    QtCore.QCoreApplication.sendPostedEvents(None, QtCore.QEvent.DeferredDelete)


def texts(grid):
    return [[grid.model.item(row, column).text() for column in range(grid.model.columnCount())]
            for row in range(grid.model.rowCount())]


def replace(env):
    env.package = NS(id=99, isNull=False)


def tick(panel, pairs):
    panel.grid.model.blockSignals(True)
    for index, pair in enumerate(panel.pairs):
        panel.grid.model.item(index, 0).setCheckState(QtCore.Qt.Checked if pair in pairs else QtCore.Qt.Unchecked)
    panel.grid.model.blockSignals(False)
    panel.count()


def identity(title):
    """Keep original hashes as data while testing the mapped active menu separately."""
    import json
    from pathlib import Path
    from menu_layout import source_bytes

    root = Path(__file__).parents[1]
    path = f'Scripts/Kerning/{title}.py'
    records = json.loads((root / 'menu-consolidations.json').read_text())['transitions']
    record = next(row for row in records if row['source']['path'] == path)
    assert source_bytes(root, record['source'])
    assert (root / record['destination']['path']).is_file()


def close_owner(env, title):
    panel = env.open(title)
    shell = env.shell
    table = panel.grid if hasattr(panel, 'grid') else None
    assert shell.connections
    shell.close_button.click()
    assert shell.closed and shell._close_complete and not shell.connections and not shell.children
    assert shell._delete_scheduled and not shell.widget.isVisible()
    if table is not None:
        assert table.closed and not table.row_selected.slots


def launch(env):
    import runpy
    from pathlib import Path
    import sys

    calls = []
    env.patch.setitem(sys.modules, 'fly.ap.studios.kerning_proof', NS(show=lambda: calls.append(env.open('Text Preview'))))
    runpy.run_path(str(Path(__file__).parents[1] / 'Scripts/Kerning/Kerning Proof.py'), run_name='__main__')
    assert len(calls) == 1 and env.shell.kerning_proof_tabs['Text Preview'] is calls[0]


def snapshot_refusal(env, change):
    panel = env.open('Pairs From Text')
    panel.value.setValue(-90)
    panel.preview_changes()
    if change == 'font':
        replace(env)
    elif change == 'closed':
        env.package = None
    elif change == 'masters':
        env.package.masters.reverse()
    elif change == 'pairs':
        env.package.kerning('Bold').items = list
    else:
        env.package.kerning('Bold').groups['L_A'] = (['T'], 'KernLeft')
    with pytest.raises(ValueError, match='stale|current'):
        panel.apply()
    assert panel.snapshot is None and not panel.values and not panel.grid.rows and not panel.ready()
    assert not env.notified


def completed_failure(env, phase='preview'):
    panel = env.open('Pairs From Text')
    panel.value.setValue(-90)
    panel.preview_changes()
    completed = []

    def write(*args):
        completed.append(args)
        return True

    panel.tool.write = write
    def fail(*args):
        raise RuntimeError(f'native {phase} failed')
    if phase == 'update':
        panel.tool.preview = NS(refresh=fail)
    else:
        panel.refresh = fail
    env.shell.apply_button.click()
    assert completed
    assert panel.snapshot is None and not panel.values and not panel.ready()
    message = env.shell.status.text()
    assert all(text in message for text in ('Kerning was applied', f'native {phase} failed', 'Undo', 'Refresh'))
    assert not message.startswith('Wrote')


def partial_failure(env):
    panel = env.open('Pairs From Text')
    panel.value.setValue(-90)
    panel.preview_changes()
    def fail(*args):
        raise RuntimeError('Kerning may be partially changed; use Undo and Refresh. setter failed')
    panel.tool.write = fail
    env.shell.apply_button.click()
    assert panel.snapshot is None and not panel.ready()
    message = env.shell.status.text()
    assert 'partially changed' in message and 'setter failed' in message
    assert 'Kerning was applied' not in message


def preflight_and_partial(env):
    panel = env.open('Pairs From Text')
    panel.clear()
    with pytest.raises(ValueError, match='Preview'):
        panel.apply()
    assert not env.notified
    assert 'Kerning was applied' not in env.shell.status.text()
    partial_failure(env)


def postwrite_ticks(env):
    panel = env.open('Pairs From Text')
    panel.value.setValue(-90)
    panel.preview_changes()
    written = []
    original = panel.ticked
    def ticks():
        if written:
            raise RuntimeError('postwrite check state failed')
        return original()
    panel.ticked = ticks
    def write(*args):
        written.append(True)
        return True
    panel.tool.write = write
    env.shell.apply_button.click()
    assert written and panel.snapshot is None and not panel.ready()
    assert all(text in env.shell.status.text() for text in
               ('Kerning was applied', 'postwrite check state failed', 'Undo', 'Refresh'))
