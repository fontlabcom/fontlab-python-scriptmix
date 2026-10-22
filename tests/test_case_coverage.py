# this_file: tests/test_case_coverage.py
"""Menu entry uses real Fly App routing and caller-owned GlyphData metadata."""

import runpy
import sys
from pathlib import Path
from types import SimpleNamespace as NS
from unittest.mock import Mock
import pytest
import fontlabapp.case_coverage_controller as controller

SCRIPT = Path(__file__).resolve().parents[1] / "Scripts/Reports/Case Coverage.py"


@pytest.fixture
def menu(monkeypatch):
    categories = Mock(return_value=("Letter", "Uppercase"))
    monkeypatch.setitem(
        sys.modules, "fly.gp.glyphsapp.glyph_info", NS(glyph_categories=categories)
    )
    data = NS(
        unicodes={
            "0041": {"name": "A"},
            "0069": {"name": "i"},
            "0307": {"name": "dotaccentcomb"},
            "004A": {"name": "J"},
            "030C": {"name": "caroncomb"},
        }
    )
    glyphdata = NS(get_glyph=Mock(), GLYPHDATA=data)
    monkeypatch.setitem(sys.modules, "glyphsLib", NS(glyphdata=glyphdata))
    return runpy.run_path(str(SCRIPT), run_name="case_menu_test"), categories


def test_caller_metadata_and_whole_expansion_policy(menu):
    module, categories = menu
    assert module["metadata"]("A", (65, 66)) == ("Uppercase", None)
    assert categories.call_args.args == ("A", ["0041", "0042"])
    categories.return_value = ("Punctuation", None)
    assert module["metadata"]("period", ()) == ("", None)
    categories.return_value = (None, None)
    assert module["metadata"]("mystery", ()) == (None, None)
    assert module["preferred"]("A") == "A"
    assert module["preferred"]("i̇") == "i_dotaccentcomb"
    assert module["preferred"]("SS") == "SS"
    assert module["preferred"]("J̌") == "J_caroncomb"
    assert module["preferred"]("unknown") is None
    assert module["preferred"]("") is None


def test_menu_launch_and_errors_pass_through_real_app_alias(menu, monkeypatch):
    module, _ = menu
    launch = Mock(return_value="owned panel")
    monkeypatch.setattr(controller, "show", launch)
    assert module["main"]() == "owned panel"
    assert launch.call_args.args == (module["metadata"], module["preferred"])
    launch.side_effect = ValueError("native source unavailable")
    with pytest.raises(ValueError, match="native source"):
        module["main"]()


def test_main_entrypoint_launches_without_executing_font_or_output_writers(
    menu, monkeypatch
):
    show = Mock(return_value="owned")
    monkeypatch.setattr(controller, "show", show)
    runpy.run_path(str(SCRIPT), run_name="__main__")
    assert show.call_count == 1


def test_caller_metadata_and_preferred_names_propagate_cooperative_cancellation(menu):
    module,categories=menu
    calls=[]
    def cancel():
        calls.append(1)
        if len(calls)==4:raise InterruptedError("caller cancelled")
    with pytest.raises(InterruptedError,match="caller"):
        module["metadata"]("A",(65,)*100,checkpoint=cancel)
    assert not categories.called
    calls.clear()
    with pytest.raises(InterruptedError,match="caller"):
        module["preferred"]("A"*100,checkpoint=cancel)
