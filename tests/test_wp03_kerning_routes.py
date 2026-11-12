# this_file: tests/test_wp03_kerning_routes.py
"""Retain original kerning oracles against the callable studio implementations."""

import importlib
import math
import sys
from types import SimpleNamespace as NS

import pytest
import test_issue122_G13 as original


@pytest.fixture
def studio_algorithms(monkeypatch):
    """Import actual App modules without constructing a native or standalone Qt UI."""
    monkeypatch.setitem(sys.modules, "PythonQt", NS(QtCore=NS(), QtGui=NS(QTableWidgetItem=object)))
    modules = {
        "report": importlib.import_module("fontlabapp.studios.kerning_browser.energy"),
        "punctuation": importlib.import_module("fontlabapp.studios.kerning_batch.punctuation"),
    }
    monkeypatch.setattr(original, "load", modules.__getitem__)
    yield modules
    for name in tuple(sys.modules):
        if name.startswith("fontlabapp.studios."):
            monkeypatch.delitem(sys.modules, name, raising=False)


@pytest.mark.parametrize("oracle", [
    "test_report_exact_zero_and_exception_precedence",
    "test_report_rejects_ambiguous_groups",
    "test_unbundle_keeps_overrides_and_materializes_zero",
    "test_unbundle_both_sides_and_one_sided_override",
    "test_punctuation_uses_unicode_categories",
    "test_ambiguous_partner_keeps_only_affected_pair",
    "test_report_ambiguity_is_pair_local_and_explicit_zero_wins",
])
def test_original_report_and_expansion_assertions_on_studio_modules(studio_algorithms, oracle):
    getattr(original, oracle)()


@pytest.mark.parametrize("value,upm", [
    (2.5, 1000), (math.nan, 1000), (math.inf, 1000), (-math.inf, 1000),
    (2**31, 2**31), (True, 1000), (2001, 1000), (-2001, 1000),
])
def test_original_numeric_pair_refusals_on_studio(studio_algorithms, value, upm):
    original.test_master_problem_names_invalid_numeric_pair(None, value, upm)


@pytest.mark.parametrize("upm", [0, -1, True, math.nan, math.inf, "1000", 10**400])
def test_original_invalid_upm_refusals_on_studio(studio_algorithms, upm):
    original.test_master_problem_rejects_invalid_upm(None, upm)


@pytest.mark.parametrize("value", [-2000, 0, 2000])
def test_original_persistence_boundary_on_studio(studio_algorithms, value):
    original.test_master_problem_accepts_inclusive_twice_upm_limit(None, value)


@pytest.mark.parametrize("operation", ["export", "copy"])
def test_stale_browser_refuses_before_file_or_clipboard(studio_algorithms, tmp_path, monkeypatch, operation):
    """Original stale-export/copy oracle against the studio's actual public action."""
    pairs = importlib.import_module("fontlabapp.studios.kerning_browser.pairs")
    missing = importlib.import_module("fontlabapp.studios.kerning_browser.missing")
    target, copied = tmp_path / "must-not-exist.csv", []

    def stale():
        raise ValueError("stale")

    tool = NS(shell=NS(package=stale), package=object(), say=lambda _text: None)
    monkeypatch.setattr(missing, "clipboard", copied.append)
    panel_type = pairs.PairsPanel if operation == "export" else missing.MissingPanel
    panel = panel_type.__new__(panel_type)
    panel.tool, panel.rows, panel.missing = tool, [("A", "V", -80)], [("A", "V")]
    with pytest.raises(ValueError, match="stale"):
        if operation == "export":
            pairs.PairsPanel.write(panel, str(target))
        else:
            missing.MissingPanel.copy(panel)
    assert not target.exists() and copied == [], "Refusal must precede both external writes"
