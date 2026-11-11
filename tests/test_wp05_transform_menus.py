# this_file: tests/test_wp05_transform_menus.py
"""The two active menus lazily open their exact original-task compositions."""
import runpy
import sys
from pathlib import Path
from types import ModuleType

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize('title', ['Transform Studio', 'Align and Nudge'])
def test_menu_when_loaded_and_run_then_one_lazy_public_call(title, monkeypatch):
    module = ModuleType('fly.ap.fontui')
    seen = []
    module.outline_studio = lambda name: seen.append(name) or 'shell'
    monkeypatch.setitem(sys.modules, module.__name__, module)
    path = ROOT / 'Scripts/Contours' / (title + '.py')
    route = runpy.run_path(str(path))
    assert not seen
    assert route['main']() == 'shell'
    runpy.run_path(str(path), run_name='__main__')
    assert seen == [title, title]
