# this_file: tests/test_qt_window_flags.py
"""Qt doubles preserve existing window flags when adding panel priority."""

import importlib

import pytest


@pytest.mark.parametrize("module_name", ['_cov_a_support', '_cov_b_support', 'test_proof', 'test_issue122_S6', 'test_issue122_G16', 'test_issue122_G12', 'test_issue122_S5', 'test_issue122_S4', 'test_issue122_G15', 'test_issue122_G4'])
def test_window_flags_preserve_type_and_chrome_when_priority_added(module_name):
    widget = importlib.import_module(module_name).Widget()
    original = 0x08000003
    widget.setWindowFlags(original)
    widget.setWindowFlags(widget.windowFlags() | 0x40000)
    assert widget.windowFlags() == original | 0x40000
    widget.setWindowFlags(original)
    assert widget.windowFlags() == original, "Flags must be replaceable per instance"
    assert type(widget)().windowFlags() == 0, "Flags must not leak between widgets"
