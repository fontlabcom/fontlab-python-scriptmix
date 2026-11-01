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
        ("a_idotaccent", "a_i.loclTRK", "derived"),
        ("idotaccent.alt", "i.loclTRK.alt", "derived"),
        ("A-cy_a", "uni04100061", "derived"),
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


@pytest.mark.parametrize("name", ["idotaccent_a", "a_idotaccent_a", "idotaccent_a.alt"])
def test_nonfinal_dotted_component_when_glyphdata_punts_then_unknown(name):
    from glyphsLib import glyphdata

    assert glyphdata.get_glyph("idotaccent").production_name == "i.loclTRK"
    assert glyphdata.get_glyph(name).production_name == name, (
        "Real GlyphData deliberately sanitizes this invalid nonfinal-dot derivation"
    )
    menu = runpy.run_path(str(SCRIPT), run_name="test_common_metadata")
    record = menu["metadata"](name)
    assert (record.name, record.status) == (None, "unknown"), (
        "Known components do not prove conversion when GlyphData takes its fallback"
    )


@pytest.mark.parametrize(
    "name,fallback",
    [("CR_a", "CR_a"), ("descender-cy_a", "descendercy_a"), ("CR.alt", "CR.alt")],
)
def test_known_name_without_semantic_production_when_glyphdata_punts_then_unknown(
    name, fallback
):
    from glyphsLib import glyphdata

    assert glyphdata.get_glyph(name).production_name == fallback
    menu = runpy.run_path(str(SCRIPT), run_name="test_common_metadata")
    record = menu["metadata"](name)
    assert (record.name, record.status) == (None, "unknown"), (
        "A known component without a production entry or AGL meaning still falls back"
    )


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
