# this_file: tests/_wp03_browser.py
"""Original Browser oracles on actual consolidated App panels."""
import importlib
from types import SimpleNamespace as NS

import pytest
from _wp03_proof import proof_env  # noqa: F401

TABS = {'Classes Browser': 'ClassesPanel', 'Compare Masters': 'MastersPanel',
        'Pair List Browser': 'PairsPanel', 'Missing Pairs': 'MissingPanel',
        'Exceptions Finder': 'ExceptionsPanel'}
MODULES = {'Classes Browser': 'classes', 'Compare Masters': 'masters',
           'Pair List Browser': 'pairs', 'Missing Pairs': 'missing',
           'Exceptions Finder': 'exceptions'}


@pytest.fixture
def browser_env(proof_env, monkeypatch):  # noqa: F811
    env = proof_env
    env.updates = 0
    env.selected = set()
    env.glyph_list = [NS(name=name) for name in env.package.glyphs]
    monkeypatch.setitem(__import__('sys').modules, 'FL', NS(fl=NS(
        font=env.glyph_list, Unselect=env.selected.clear, Select=env.selected.add,
        Selected=lambda i: i in env.selected)))
    from fontlabapp.core import scripting
    native = scripting._native('fontlab')
    native.fl = __import__('sys').modules['FL'].fl
    native.CurrentGlyph = lambda: None
    frame = NS(inherits=lambda name: name == 'YFrameWindow', parentWidget=lambda: None)
    panel = NS(inherits=lambda name: name == 'FontWindow', parentWidget=lambda: frame)
    native.flWorkspace = NS(instance=lambda: NS(currentPackage=env.package, activeFontPanel=panel))
    from PythonQt import QtGui
    env.clipboard = QtGui.QApplication.clipboard()
    env.clipboard.clear()
    env.patch = monkeypatch

    proof_open = env.open

    def open_panel(title, no_font=False):
        if title not in TABS:
            return proof_open(title, no_font)
        if no_font:
            env.package = None
        module = importlib.import_module('fontlabapp.studios.kerning_browser')
        env.shell = module.show(package=lambda: env.package, font=lambda: {}, preview=lambda *_: None, consolidated=True)
        env.shells.append(env.shell)
        env.tool = env.shell.kerning_tool
        panels = {view.__self__.__class__.__name__: view.__self__ for view in env.tool.views}
        panel = panels[TABS[title]]
        for index in range(env.shell.tabs.count()):
            if env.shell.tabs.widget(index) is panel.widget:
                env.shell.tabs.setCurrentIndex(index)
        panel.refresh()
        return panel

    env.open = open_panel
    env.load = lambda title: importlib.import_module('fontlabapp.studios.kerning_browser.' + MODULES[title])
    return env


def texts(table):
    if hasattr(table, 'model') and not callable(table.model):
        return [[table.model.item(r, c).text() for c in range(table.model.columnCount())]
                for r in range(table.model.rowCount())]
    table = getattr(table, 'view', table)
    return [[table.item(r, c).text() for c in range(table.columnCount())]
            for r in range(table.rowCount())]


def items(widget):
    return [widget.item(i).text() for i in range(widget.count())]


def button(panel, title):
    from PythonQt import QtGui
    return next(item for item in panel.widget.findChildren(QtGui.QPushButton) if item.text() == title)


def clean(panel):
    assert not panel.tool.status.startswith('Kerning Browser:'), panel.tool.status


def replace(env):
    env.package = NS(id=99, isNull=False)


def checked():
    from PythonQt import QtCore
    return QtCore.Qt.Checked


def close_owner(env, title):
    panel = env.open(title)
    shell = env.shell
    assert shell.connections
    shell.close_button.click()
    assert shell.closed and shell._close_complete and shell._delete_scheduled
    assert not shell.widget.isVisible() and not shell.connections and not shell.children
    if hasattr(panel, 'grid') and hasattr(panel.grid, 'closed'):
        assert panel.grid.closed and not panel.grid.row_selected.slots


def launch(env):
    import runpy
    import sys
    from pathlib import Path
    calls = []
    env.patch.setitem(sys.modules, 'fly.ap.studios.kerning_browser', NS(show=lambda **kw: calls.append(env.open('Classes Browser'))))
    runpy.run_path(str(Path(__file__).parents[1] / 'Scripts/Kerning/Kerning Browser.py'), run_name='__main__')
    assert len(calls) == 1 and calls[0].tool is env.tool


def exception_panel(env):
    panel = env.open('Exceptions Finder')
    panel.grid.set_ticked({0})
    return panel


def snapshot_refusal(env, change):
    panel = exception_panel(env)
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
    assert not panel.apply()
    assert 'stale' in panel.tool.status or 'current' in panel.tool.status
    assert panel.snapshot is None and not panel.rows and not panel.apply_button.isEnabled()
    assert not env.notified


def completed_failure(env, phase='preview'):
    panel = exception_panel(env)
    completed = []
    env.patch.setattr(panel.tool, 'write', lambda *args: completed.append(args) or True)
    def fail(*args):
        raise RuntimeError(f'native {phase} failed')
    if phase == 'update':
        panel.tool.preview = NS(refresh=fail)
    else:
        env.patch.setattr(panel, 'refresh', fail)
    env.shell.apply_button.click()
    assert completed, 'The owned write must complete before display failure'
    assert panel.snapshot is None and not panel.rows and not panel.apply_button.isEnabled()
    assert all(text in panel.tool.status for text in ('Kerning was applied', f'native {phase} failed', 'Undo', 'Refresh'))
    assert not panel.tool.status.startswith(('Wrote', 'Removed'))


def partial_failure(env):
    panel = exception_panel(env)
    def fail(*args):
        raise RuntimeError('Kerning may be partially changed; use Undo and Refresh. setter failed')
    env.patch.setattr(panel.tool, 'write', fail)
    env.shell.apply_button.click()
    assert panel.snapshot is None and not panel.rows and not panel.apply_button.isEnabled()
    assert 'partially changed' in panel.tool.status and 'setter failed' in panel.tool.status
    assert 'Kerning was applied' not in panel.tool.status


def preflight_and_partial(env):
    panel = exception_panel(env)
    panel.snapshot = None
    assert not panel.apply()
    assert 'Kerning was applied' not in panel.tool.status
    assert not env.notified
    partial_failure(env)
