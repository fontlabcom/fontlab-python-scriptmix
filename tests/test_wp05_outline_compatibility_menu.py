# this_file: tests/test_wp05_outline_compatibility_menu.py
"""The single S17 menu opens the real public App composition lazily."""
import runpy
from pathlib import Path

import pytest

ROOT = Path(__file__).parents[1]


@pytest.mark.parametrize('run_name', ['menu_test', '__main__'])
def test_outline_compatibility_menu_dispatches_public_factory(monkeypatch, run_name):
    import fontlabapp.fontui as fontui
    calls = []
    marker = object()
    monkeypatch.setattr(fontui, 'show_outline_compatibility', lambda: calls.append('open') or marker)
    scope = runpy.run_path(str(ROOT / 'Scripts/Contours/Outline Compatibility.py'), run_name=run_name)
    if run_name != '__main__':
        assert not calls
        assert scope['main']() is marker
    assert calls == ['open']
