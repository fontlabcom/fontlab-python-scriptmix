# this_file: tests/_wp03_studio_support.py
"""Reuse App's offscreen fixture for old menu assertions on actual studio widgets."""

import importlib
import importlib.util
import sys
from types import SimpleNamespace as NS

import pytest
from conftest import resolve_app_sources


@pytest.fixture
def studio_host(monkeypatch):
    source = resolve_app_sources().parent.parent / "tests" / "_studio_qt.py"
    spec = importlib.util.spec_from_file_location("wp03_app_qt_fixture", source)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    fixture = module.studio_qt.__wrapped__(monkeypatch)
    qt = next(fixture)
    from fontlabapp.core import scripting
    import fontlabapp.kerning.batch as batch

    state = NS(package=None, notified=[], updates=0, qt=qt)

    def update():
        state.updates += 1

    native = NS(
        flWorkspace=NS(instance=lambda: NS(currentPackage=state.package)),
        flItems=NS(notifyChangesApplied=lambda *args: state.notified.append(args)),
        fl=NS(font=None), UpdateAll=update,
    )
    monkeypatch.setattr(scripting, "_native", lambda _name: native)
    monkeypatch.setattr(batch, "_native", lambda _name: native)

    def open_studio(name="kerning_batch"):
        studio = importlib.import_module("fontlabapp.studios." + name)
        shell = studio.show(package=lambda: state.package, font=lambda: {},
                            preview=lambda *_args: None, consolidated=True)
        qt.owned.append(shell)
        tool = shell.kerning_tool
        panels = {view.__self__.__class__.__name__: view.__self__ for view in tool.views}
        return NS(shell=shell, tool=tool, panels=panels)

    state.open = open_studio
    yield state
    try:
        next(fixture)
    except StopIteration:
        pass
    for name in tuple(sys.modules):
        if name.startswith("fontlabapp.studios."):
            monkeypatch.delitem(sys.modules, name, raising=False)


def rows(panel):
    """Actual model rows, in source-plan order before the user changes sorting."""
    return [[row.glyph_name, *map(str, row.values)] for row in panel.grid.rows]
