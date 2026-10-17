# this_file: tests/test_portability.py
"""Regression coverage for dependency resolution before module replacement."""

import sys
from types import SimpleNamespace

import pytest
from conftest import resolve_app_sources


def test_installed_sources_resolve_with_module_double(monkeypatch):
    monkeypatch.delenv("SCRIPTMIX_APP_SOURCE", raising=False)
    monkeypatch.setitem(sys.modules, "fontlabapp", SimpleNamespace())
    before = set(sys.modules)
    root = resolve_app_sources(required_helpers=("scripting",))
    assert (root / "scripting.py").is_file(), "Installed helper must be real source"
    assert not ({"fontlab", "PythonQt"} & (set(sys.modules) - before)), (
        "Resolution imported native binaries"
    )


def test_explicit_missing_source_refused(monkeypatch, tmp_path):
    monkeypatch.setenv("SCRIPTMIX_APP_SOURCE", str(tmp_path))
    with pytest.raises(AssertionError, match="Missing App helper"):
        resolve_app_sources()


def test_explicit_source_override_used(monkeypatch, app_sources):
    monkeypatch.setenv("SCRIPTMIX_APP_SOURCE", str(app_sources))
    assert resolve_app_sources() == app_sources, "Explicit source directory ignored"


def test_pre_kerning_source_tree_refused(monkeypatch, tmp_path):
    """A current baseline wheel alone cannot satisfy forthcoming panel helpers."""
    for name in (
        "scripting",
        "_font_info_dialog",
        "_features_dialog",
        "feature_code",
        "_names_dialog",
    ):
        (tmp_path / (name + ".py")).write_text("# Existing helper\n")
    monkeypatch.setenv("SCRIPTMIX_APP_SOURCE", str(tmp_path))
    with pytest.raises(AssertionError, match="_kerning_dialog"):
        resolve_app_sources()
