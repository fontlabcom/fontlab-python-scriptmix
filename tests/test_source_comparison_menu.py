# this_file: tests/test_source_comparison_menu.py
"""The menu captures one current font and delegates to the shared composition."""
import runpy
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace

import pytest

ENTRY = Path(__file__).resolve().parents[1] / 'Scripts/Font UI Lab/Designspace Source Comparison.py'


@pytest.mark.parametrize('script', [False, True])
def test_menu_when_invoked_then_captures_font_once(monkeypatch, script):
    calls = []
    font, owner = object(), object()
    world = ModuleType('fontlab_fontport.world')
    def current():
        calls.append('current')
        return font
    world.FontWorld = lambda: SimpleNamespace(CurrentFont=current)
    composition = ModuleType('fontlabapp.fontui.source_comparison')
    def show(value):
        assert value is font
        calls.append('show')
        return owner
    composition.show = show
    monkeypatch.setitem(sys.modules, world.__name__, world)
    monkeypatch.setitem(sys.modules, composition.__name__, composition)
    namespace = runpy.run_path(str(ENTRY), run_name='__main__' if script else 'menu_test')
    if not script:
        assert namespace['main']() is owner
    assert calls == ['current', 'show']
