# this_file: tests/test_master_text_menu.py
"""The practical menu must route through installed App via Fly."""

from pathlib import Path
import runpy
from unittest.mock import Mock
import fontlabapp.master_text_controller as controller

SCRIPT = (
    Path(__file__).resolve().parents[1] / "Scripts/Masters/Master Text Comparison.py"
)


def test_main_uses_shared_complete_workflow_and_reports_refusals(monkeypatch, capsys):
    launch = Mock(return_value="owned panel")
    monkeypatch.setattr(controller, "show", launch)
    menu = runpy.run_path(str(SCRIPT), run_name="test_master_menu")
    assert menu["main"]() == "owned panel"
    for error in (
        ValueError("Open a font"),
        RuntimeError("native binding held"),
        TimeoutError("deadline"),
    ):
        launch.side_effect = error
        assert menu["main"]() is None and str(error) in capsys.readouterr().out
    launch.side_effect = None
    runpy.run_path(str(SCRIPT), run_name="__main__")
    assert launch.call_count == 5
