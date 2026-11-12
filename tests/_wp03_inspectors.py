# this_file: tests/_wp03_inspectors.py
"""Original width-inspection facts exercised through the consolidated shell."""
import importlib
from types import SimpleNamespace as NS

import pytest
from _fgpackage_support import FgPackage
from _wp03_proof import proof_env  # noqa: F401


@pytest.fixture
def width_env(proof_env):  # noqa: F811
    env = proof_env
    env.selected = {0, 1, 2}
    env.layers = {name: {master: NS(isNull=False, advanceWidth=width, shapes=[], autoLayer=False, boundingBox=NS(x=lambda: 0, width=lambda: 20, height=lambda: 20), metricsLeft="", metricsRight="", metricsWidth="")
                        for master, width in [('Bold', 200), ('Light', 100)]}
                  for name in ['H', 'O', 'n']}
    glyphs = {name: NS(name=name, isNull=False, codes=[ord(name)], findLayer=layers.get, layers=list(layers.values()))
              for name, layers in env.layers.items()}
    env.glyphs = list(glyphs.values())
    for index, glyph in enumerate(env.glyphs):
        glyph.id = index + 1
        for offset, (name, layer) in enumerate(env.layers[glyph.name].items()):
            layer.name, layer.id, layer.isMasterLayer = name, index * 10 + offset, True
    env.package = NS(id=7, fgId=7, isNull=False, master='Bold', masters=['Bold', 'Light'], axes=[],
                     findName=glyphs.get, findUnicode=lambda code: glyphs.get(chr(code)),
                     fgPackage=FgPackage(glyphs))
    from fontlabapp.core import scripting
    native = scripting._native('fontlab')
    frame = NS(inherits=lambda name: name == 'YFrameWindow', parentWidget=lambda: None)
    panel = NS(inherits=lambda name: name == 'FontWindow', parentWidget=lambda: frame)
    native.flWorkspace = NS(instance=lambda: NS(currentPackage=env.package, activeFontPanel=panel))
    native.CurrentGlyph = lambda: None
    native.CurrentFont = lambda: NS(id=7, glyphs=env.glyphs)
    native.fl = NS(font=env.glyphs, Unselect=env.selected.clear, Select=env.selected.add,
                   Selected=lambda index: index in env.selected)
    env.patch.setitem(__import__('sys').modules, 'FL', NS(fl=native.fl))
    env.module = importlib.import_module('fontlabapp.studios.advance_widths.table')
    env.widths = importlib.import_module('fontlabapp.studios.advance_widths.widths')

    env.getter = lambda: env.package
    import fontlabapp.fontui as fontui
    original_shell = fontui.app_shell
    def shell_created(*args, **kwargs):
        env.shell = original_shell(*args, **kwargs)
        return env.shell
    env.patch.setattr(fontui, 'app_shell', shell_created)

    def open_panel():
        app = importlib.import_module('fontlabapp.studios.advance_widths')
        shell = app.show(package=lambda: env.getter(), font=lambda: None, preview=lambda *_: None)
        env.shells.append(shell)
        env.shell = shell
        env.tool = shell.kerning_tool
        panel = next(view.__self__ for view in env.tool.views if isinstance(view.__self__, env.module.TablePanel))
        shell.tabs.setCurrentWidget(panel.widget)
        return panel

    env.open = open_panel
    return env


def close(env):
    env.shell.close_button.click()
    assert env.shell.closed and env.shell._delete_scheduled and not env.shell.widget.isVisible()
    assert not env.shell.connections and not env.shell.children


def values(panel):
    return {row.glyph_name: list(row.values[:-1]) for row in panel.grid.rows}


def identity(title):
    import json
    from pathlib import Path
    from menu_layout import source_bytes
    root = Path(__file__).parents[1]
    path = f'Scripts/Metrics/{title}.py'
    record = next(row for row in json.loads((root / 'menu-consolidations.json').read_text())['transitions']
                  if row['source']['path'] == path)
    assert source_bytes(root, record['source'])
    assert (root / record['destination']['path']).is_file()


def initial_failure(env, stage):
    package = env.package
    def fail(*args):
        assert hasattr(env.shell, 'status') and hasattr(env.shell, 'close_button')
        raise RuntimeError('initial ' + stage)
    class Broken:
        def __getattr__(self, name):
            return fail() if name == ('id' if stage == 'identity' else stage) else getattr(package, name)
    with env.patch.context() as broken:
        if stage == 'binding':
            broken.setattr(env, 'getter', fail)
        elif stage in ('identity', 'masters', 'master'):
            env.package = Broken()
        elif stage == 'selection':
            from fontlabapp.studios._kerning import Tool
            broken.setattr(Tool, 'selected_names', fail)
        else:
            broken.setattr(env.widths, 'width_report', fail)
        panel = env.open()
        assert 'initial ' + stage in env.shell.status.text()
        assert panel.source is None and not panel.rows
    env.package = package
    env.shell.refresh_button.click()
    assert panel.source is not None and panel.rows
    assert 'initial ' + stage not in panel.subtitle.text()
    close(env)


def stale_refresh(env, closed):
    package = env.package
    panel = env.open()
    env.package = None if closed else NS(id=9, isNull=False)
    package.findName = lambda name: pytest.fail('stale wrapper access')
    env.shell.refresh_button.click()
    assert 'original font' in env.shell.status.text(), env.shell.status.text()
    assert panel.source is None and not panel.rows and panel.tool.package is None
    close(env)


def domain_during_scan(env, final=False):
    package = env.package
    with env.patch.context() as broken:
        if final:
            original = env.module.TablePanel.source_values
            def changed(self):
                result = original(self)
                package.masters.append('Late')
                return result
            broken.setattr(env.module.TablePanel, 'source_values', changed)
        else:
            original = env.widths.width_report
            def changed(*args):
                result = original(*args)
                package.masters = ['Light', 'Bold', 'New']
                return result
            broken.setattr(env.widths, 'width_report', changed)
        panel = env.open()
    assert 'Masters changed' in panel.subtitle.text(), panel.subtitle.text()
    assert panel.source is None and not panel.rows and panel.domain is None
    env.shell.refresh_button.click()
    assert panel.source is not None and panel.rows
