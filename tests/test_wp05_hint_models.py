# this_file: tests/test_wp05_hint_models.py
"""Run unchanged S7 numeric/history oracles against the moved App hint writers."""
import importlib

import pytest
import test_issue122_S7 as original
from test_issue122_S7 import world  # noqa: F401


ORACLES = (
    'test_autohint_when_applied_then_counts_and_readback_one_step',
    'test_remove_hints_survey_when_direction_chosen_then_no_hints_note',
    'test_remove_hints_when_applied_then_counts_zero_one_step',
    'test_remove_hints_when_layer_keeps_hints_then_mismatch',
    'test_autohint_when_no_planned_layers_then_no_history',
)


@pytest.mark.parametrize('oracle', ORACLES)
def test_existing_hint_oracle_against_app_writer(world, monkeypatch, oracle):  # noqa: F811
    modules = {
        'Autohint Selected Layers': importlib.import_module('fontlabapp.studios.hint_tools.autohint'),
        'Remove PostScript Hints': importlib.import_module('fontlabapp.studios.hint_tools.removal'),
    }
    monkeypatch.setattr(original, 'load', modules.__getitem__)
    getattr(original, oracle)(world)


@pytest.mark.parametrize('guides', [[], [original.Guide(False)], [original.Guide(horizontal=False)]])
def test_empty_autohint_result_retains_original_readback_oracle(world, monkeypatch, guides):  # noqa: F811
    module = importlib.import_module('fontlabapp.studios.hint_tools.autohint')
    monkeypatch.setattr(original, 'load', lambda title: module)
    original.test_autohint_when_native_succeeds_without_hints_then_readback_mismatch(world, guides)


@pytest.mark.parametrize('title,word', [('Autohint Selected Layers', 'Nothing to autohint'),
                                       ('Remove PostScript Hints', 'Nothing to remove')])
def test_retained_panel_empty_result_and_direct_entry(world, title, word):  # noqa: F811
    import runpy
    world.use([])
    module = original.load(title)
    panel = module.panel_type()(None)
    assert panel.result_text({'layers': 0}) == word
    runpy.run_path(module.__file__, run_name='__main__')


@pytest.mark.parametrize('relative', ['fontui/hint_autohint.py', 'fontui/hint_removal.py',
                                     'studios/hint_tools/autohint.py', 'studios/hint_tools/removal.py'])
def test_current_hint_routes_retain_source_safety_oracles(relative):
    import ast
    import re
    from conftest import installed_app_root
    source = (installed_app_root() / relative).read_text()
    tree = ast.parse(source, feature_version=(3, 11))
    body = '\n'.join(ast.get_source_segment(source, node) for node in tree.body[1:])
    for pattern in (r'\bUpdateAll\(', r'notifyChangesApplied', r'\bFL\.fl\b', r'import FL\b',
                    r'\.fgGlyph\b(?!Id)', r'removeAllShapes', r'\.clone\(\)', r'\bround\(',
                    r'except Exception\b', r'\bglobal\b', r'\baddGlyph\b', r'\bflGlyph\(',
                    r'findLayerCreate', r'\.unicodes\s*='):
        assert not re.search(pattern, body), (relative, pattern)
    for cls in [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef) and 'Panel' in n.name]:
        assigned = {n.attr for n in ast.walk(cls) if isinstance(n, ast.Attribute)
                    and isinstance(n.ctx, ast.Store) and isinstance(n.value, ast.Name)
                    and n.value.id == 'self'}
        methods = {n.name for n in cls.body if isinstance(n, ast.FunctionDef)}
        assert not (assigned | methods) & original.NATIVE_MEMBERS


def test_hint_tools_launcher_calls_public_studio(monkeypatch):
    import runpy
    import types
    import sys
    route = types.ModuleType('fly.ap.studios.hint_tools')
    calls = []
    route.show = lambda: calls.append('show') or 'window'
    monkeypatch.setitem(sys.modules, route.__name__, route)
    path = original.ROOT / 'Scripts/Contours/Hint Tools.py'
    namespace = runpy.run_path(str(path))
    assert namespace['main']() == 'window'
    runpy.run_path(str(path), run_name='__main__')
    assert calls == ['show', 'show']
