# this_file: tests/conftest.py
"""Resolve helper sources without importing FontLab or Qt binaries."""

import os
from importlib.metadata import distribution
from pathlib import Path

import pytest


def original_source(root: Path, relative: str) -> Path:
    """Read preserved originals after the authorized archive relocation."""
    current = root / relative
    if current.is_file():
        return current
    return root / relative.replace("/_old/", "/rescued/", 1)


def pytest_addoption(parser):
    parser.addoption(
        "--original-source-root",
        type=Path,
        default=None,
        help="Audit every original hash relative to this workspace root",
    )


def resolve_app_sources(required_helpers=None):
    """Resolve before per-test module doubles replace fontlabapp."""
    override = os.environ.get("SCRIPTMIX_APP_SOURCE")
    root = (
        Path(override)
        if override
        else Path(distribution("fontlab-fontlabapp").locate_file("fontlabapp"))
    )
    required_helpers = required_helpers or (
        "scripting",
        "_font_info_dialog",
        "_features_dialog",
        "feature_code",
        "_names_dialog",
        "_kerning_dialog",
        "kerning_edit",
        "kerning_batch",
        "_kerning_edit_dialog",
        "_kerning_value_dialog",
        "kerning_selection",
        "proof",
        "_proof_dialog",
        "_proof_views",
        "masters",
        "_masters_dialog",
        "_masters_views",
        "inspectors",
        "_inspectors_dialog",
        "_inspectors_views",
        "components",
        "_components_dialog",
        "_components_views",
        "anchors",
        "_anchors_dialog",
        "_anchors_views",
        "unreferenced",
        "interpolation",
        "_review_dialog",
        "_interpolation_view",
        "node_coordinates",
        "master_switcher",
        "_switcher_dialog",
        "guides",
        "_guides_sources",
        "_guides_dialog",
        "_guides_views",
        "guide_records",
        "guide_rewrite",
        "_guide_rewrite_dialog",
        "_guide_editor_dialog",
        "anchor_copy",
        "_anchor_copy_dialog",
        "script_completion",
    )
    for name in required_helpers:
        assert (root / f"{name}.py").is_file(), f"Missing App helper: {root / name}"
    return root


@pytest.fixture(scope="session")
def app_sources():
    """Load the real host-free completion helper before replacing package namespaces."""
    import importlib
    import importlib.util
    import sys

    root = resolve_app_sources()
    importlib.import_module("fontlabapp")
    name = "fontlabapp.script_completion"
    spec = importlib.util.spec_from_file_location(name, root / "script_completion.py")
    module = importlib.util.module_from_spec(spec)
    with pytest.MonkeyPatch.context() as patch:
        patch.setitem(sys.modules, name, module)
        spec.loader.exec_module(module)
        yield root
