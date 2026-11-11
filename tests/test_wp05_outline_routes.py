# this_file: tests/test_wp05_outline_routes.py
"""Every old outline menu keeps a callable App route with its original strategy."""
import importlib

import pytest
from test_issue122_S6 import world as _world

world = _world

ROUTES = ('add_extremes', 'delete_close_points', 'delete_duplicate_contours',
          'delete_small_contours', 'fix_zero_handles', 'remove_overlap',
          'round_coordinates', 'curve_all_straights', 'straighten_all_curves',
          'straighten_short_curves', 'retract_handles', 'correct_contour_direction',
          'optimize_start_points', 'simplify_selected_nodes')


@pytest.mark.parametrize('name', ROUTES)
def test_original_callable_route_moves_to_app(world, name):
    module = importlib.import_module('fontlabapp.fontui.outline_routes.' + name)
    assert callable(module.main)
    assert module.TITLE and module.KEY


@pytest.mark.parametrize('title', ['Outline Doctor', 'Curve Editor'])
def test_consolidated_outline_menu_opens_matching_app_studio(monkeypatch, title):
    import runpy
    import sys
    from pathlib import Path
    from types import ModuleType

    module = ModuleType('fontlabapp.fontui.outline_editing')
    calls = []
    result = object()
    module.show = lambda name: calls.append(name) or result
    monkeypatch.setitem(sys.modules, module.__name__, module)
    monkeypatch.setitem(sys.modules, 'fly.ap.fontui.outline_editing', module)
    path = Path(__file__).parents[1] / 'Scripts' / 'Contours' / (title + '.py')
    namespace = runpy.run_path(str(path))
    assert namespace['main']() is result
    runpy.run_path(str(path), run_name='__main__')
    assert calls == [title, title]


@pytest.mark.parametrize('name', ROUTES)
def test_migrated_standalone_route_runs_public_dialog_factory(world, monkeypatch, name):
    import runpy

    import fontlabapp.core.scripting as scripting

    calls = []
    monkeypatch.setattr(scripting, 'show_script_dialog', lambda panel, key: calls.append((panel, key)))
    namespace = runpy.run_module('fontlabapp.fontui.outline_routes.' + name, run_name='__main__')
    assert len(calls) == 1 and calls[0][1] == namespace['KEY']
