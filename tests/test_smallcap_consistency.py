# this_file: tests/test_smallcap_consistency.py
"""The real Fly facade routes a fresh detached report into the owned report UI."""

import runpy
from pathlib import Path

import pytest

import fontlabapp.smallcap_capture as capture
import fontlabapp.reports as reports
from fontlabapp.smallcap_consistency import GlyphFact, analyze

SCRIPT = Path(__file__).resolve().parents[1] / "Scripts/Reports/Smallcap Consistency.py"


def test_menu_when_rerun_then_refreshes_snapshot_under_same_owned_key(monkeypatch):
    calls = []
    facts = [GlyphFact("a", True, "lower", "a")]
    monkeypatch.setattr(capture, "current_report", lambda: analyze(facts))
    monkeypatch.setattr(
        reports, "show_report", lambda report, **kw: calls.append((report, kw))
    )
    module = runpy.run_path(str(SCRIPT), run_name="smallcaps_test")
    module["main"]()
    facts.append(GlyphFact("a.smcp", True, "smallcap", "a"))
    module["main"]()
    assert calls[0][0]["missing_lowercase_smallcaps"] == ["a"], (
        'Expected calls[0][0]["missing_lowercase_smallcaps"] == ["a"]'
    )
    assert calls[1][0]["missing_lowercase_smallcaps"] == [], (
        'Expected calls[1][0]["missing_lowercase_smallcaps"] == []'
    )
    assert (
        calls[0][1]
        == calls[1][1]
        == {"title": "Smallcap Consistency", "key": "report_smallcap_consistency"}
    ), (
        'Expected calls[0][1] == calls[1][1] == {         "title": "Smallcap Consistency", "key": "report_smallcap_consistency"}'
    )


def test_menu_when_no_font_or_timeout_then_does_not_open_panel(monkeypatch):
    calls = []
    monkeypatch.setattr(reports, "show_report", lambda *a, **kw: calls.append(a))
    for error in (
        ValueError("Open a font first"),
        TimeoutError("complete report expired"),
    ):

        def refuse():
            raise error

        monkeypatch.setattr(capture, "current_report", refuse)
        with pytest.raises(type(error), match=str(error)):
            runpy.run_path(str(SCRIPT), run_name="__main__")
    assert calls == [], "Expected calls == []"
