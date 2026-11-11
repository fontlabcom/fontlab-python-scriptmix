# this_file: tests/test_wp05_generator_launchers.py
"""Generator menus dispatch only to their retained App studios."""
import runpy
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize('title,module', [
    ('Derived Glyphs', 'fly.ap.studios.derived_glyphs.outline'),
    ('Shape Generators', 'fly.ap.studios.shape_generators.app'),
])
def test_generator_launcher_dispatch(title, module, monkeypatch):
    calls = []
    monkeypatch.setitem(sys.modules, module, SimpleNamespace(show=lambda: calls.append(title)))
    path = ROOT / 'Scripts/Contours' / f'{title}.py'
    runpy.run_path(str(path), run_name='__main__')
    assert calls == [title]
    runpy.run_path(str(path), run_name='imported_menu')
    assert calls == [title]
