# this_file: tests/_wp03_pair_editor.py
"""Pair Editor contracts on the actual consolidated App shell and widgets."""
from types import SimpleNamespace as NS

import pytest
from _cov_b_support import make_package
import _wp03_studio_support as support

studio_host = support.studio_host


@pytest.fixture
def pair_env(studio_host, monkeypatch):
    from fontlabapp.core import scripting

    studio_host.package = make_package()
    selection = ["A"]
    monkeypatch.setattr(scripting, "names_selected_names", lambda: list(selection))
    import fontlabapp.studios._kerning as tool_module
    monkeypatch.setattr(tool_module, "names_selected_names", lambda: list(selection))
    import importlib
    pairs = importlib.import_module("fontlabapp.studios.kerning_studio.pairs")
    monkeypatch.setattr(pairs, "current_glyph_name", lambda package: selection[0] if package is not None and selection else None)
    env = NS(state=studio_host, selection=selection)
    def open_panel(no_font=False):
        if no_font:
            studio_host.package = None
        app = studio_host.open("kerning_studio")
        env.shell, env.tool = app.shell, app.tool
        panel = app.panels["PairEditorPanel"]
        env.shell.tabs.setCurrentWidget(panel.widget)
        return panel
    env.open = open_panel
    yield env


def texts(panel):
    return [[panel.table.item(row, column).text() for column in range(panel.table.columnCount())]
            for row in range(panel.table.rowCount())]


def replace(env):
    env.state.package = NS(id=99, isNull=False)


def close_owner(env):
    env.open()
    env.shell.close_button.click()
    assert env.shell.closed and env.shell._close_complete and not env.shell.connections
    assert not env.shell.children and env.shell._delete_scheduled
    assert not env.shell.widget.isVisible()


def snapshot_refusal(env, change):
    panel = env.open()
    panel.set_cell("A", "V", "Bold", "-120")
    if change == "font":
        replace(env)
    elif change == "closed":
        env.state.package = None
    elif change == "masters":
        env.state.package.masters.reverse()
    elif change == "pairs":
        env.state.package.kerning("Bold").items = list
    else:
        env.state.package.kerning("Bold").groups["L_A"] = (["T"], "KernLeft")
    env.shell.apply_button.click()
    assert not panel.staged and panel.snapshot is None and not panel.ready()
    assert panel.table.rowCount() == 0
    assert any(word in env.shell.status.text() for word in ("stale", "current"))
    assert not env.state.notified
