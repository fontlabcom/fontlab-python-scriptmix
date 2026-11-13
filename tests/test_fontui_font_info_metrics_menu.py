# this_file: tests/test_fontui_font_info_metrics_menu.py
"""Menu captures once, imports lazily and dispatches the shared workflow."""
import runpy
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

ENTRY = Path(__file__).resolve().parents[1] / 'Scripts/Font UI Lab/Font Info and Vertical Metrics.py'


@pytest.mark.parametrize('script', [False, True])
def test_menu_when_invoked_then_captures_once(monkeypatch, script):
    font, handle = object(), object()
    world = Mock()
    world.CurrentFont.return_value = font
    factory, show = Mock(return_value=world), Mock(return_value=handle)
    monkeypatch.setitem(sys.modules, 'fontlab_fontport.world', SimpleNamespace(FontWorld=factory))
    monkeypatch.setitem(sys.modules, 'fontlabapp.fontui.font_info_metrics', SimpleNamespace(show=show))
    monkeypatch.setitem(sys.modules, 'fly.fp.world', sys.modules['fontlab_fontport.world'])
    monkeypatch.setitem(sys.modules, 'fly.ap.fontui.font_info_metrics', sys.modules['fontlabapp.fontui.font_info_metrics'])
    namespace = runpy.run_path(str(ENTRY), run_name='__main__' if script else 'menu')
    if not script:
        factory.assert_not_called()
        assert namespace['main']() is handle
    factory.assert_called_once_with()
    world.CurrentFont.assert_called_once_with()
    show.assert_called_once_with(font)
