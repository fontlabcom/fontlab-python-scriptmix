# this_file: tests/test_node_editor_launcher.py
# SPDX-License-Identifier: Apache-2.0
"""Execute the real Node Editor launcher through its installed Fly/App route."""

import importlib
import runpy
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LAUNCHER = ROOT / "Scripts/Contours/Node Editor.py"


def test_node_editor_launcher_when_imported_and_executed_then_calls_app_show(monkeypatch):
    api = importlib.import_module("fly.ap.studios.node_editor")
    calls = []
    window = object()

    def show():
        calls.append(window)
        return window

    monkeypatch.setattr(api, "show", show)
    namespace = runpy.run_path(str(LAUNCHER), run_name="inspection")
    assert calls == [], "Importing the menu must not open a window"
    assert namespace["main"]() is window
    assert calls == [window]
    runpy.run_path(str(LAUNCHER), run_name="__main__")
    assert calls == [window, window], "Running the real menu file must dispatch once"
