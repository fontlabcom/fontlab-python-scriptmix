# this_file: tests/test_common_glyphs_menu.py
"""Thin Fly entry and real GlyphData mappings never disguise unknown fallback."""

from pathlib import Path
import runpy
from unittest.mock import Mock
import pytest
import fontlabapp.common_glyphs_controller as controller

SCRIPT = Path(__file__).resolve().parents[1] / "Scripts/Masters/Common Glyphs.py"


def test_menu_routes_complete_report_and_contains_refusals(monkeypatch, capsys):
    show = Mock(return_value="owned panel")
    monkeypatch.setattr(controller, "show", show)
    menu = runpy.run_path(str(SCRIPT), run_name="test_common_menu")
    assert menu["main"]() == "owned panel"
    assert show.call_args.args == (menu["metadata"],)
    for error in (
        ValueError("Open fonts"),
        RuntimeError("held native writer"),
        TimeoutError("deadline"),
    ):
        show.side_effect = error
        assert menu["main"]() is None and str(error) in capsys.readouterr().out
    show.side_effect = None
    runpy.run_path(str(SCRIPT), run_name="__main__")
    assert show.call_count == 5


@pytest.mark.parametrize(
    "name,production,status",
    [
        ("A", "A", "database"),
        ("A-cy", "uni0410", "database"),
        ("afii10017", "uni0410", "database"),
        ("fi", "fi", "database"),
        ("A-cy.alt", "uni0410.alt", "derived"),
        ("f_i", "f_i", "derived"),
        ("_helper", None, "unknown"),
        ("unknown_custom_thing", None, "unknown"),
    ],
)
def test_actual_public_glyphdata_field_and_explicit_unknown_mapping(
    name, production, status
):
    menu = runpy.run_path(str(SCRIPT), run_name="test_common_metadata")
    calls = []
    record = menu["metadata"](name, checkpoint=lambda: calls.append(1))
    assert (record.name, record.status) == (production, status), (
        "Use verified production metadata; never silent stored-name fallback"
    )
    assert len(calls) >= 3, "Propagate budget through metadata lookup"


def test_metadata_cancellation_and_dependency_failure_remain_explicit(monkeypatch):
    menu = runpy.run_path(str(SCRIPT), run_name="test_common_metadata")

    def cancel():
        raise InterruptedError("cancelled")

    with pytest.raises(InterruptedError):
        menu["metadata"]("A", checkpoint=cancel)
    from glyphsLib import glyphdata

    monkeypatch.setattr(
        glyphdata, "get_glyph", Mock(side_effect=RuntimeError("metadata read failed"))
    )
    with pytest.raises(RuntimeError, match="metadata read failed"):
        menu["metadata"]("A")
