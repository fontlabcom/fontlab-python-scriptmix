# this_file: tests/conftest.py
"""Resolve helper sources without importing FontLab or Qt binaries."""

import os
from importlib.metadata import distribution
from pathlib import Path

import pytest


def pytest_addoption(parser):
    parser.addoption(
        "--original-source-root",
        type=Path,
        default=None,
        help="Audit every original hash relative to this workspace root",
    )


def resolve_app_sources():
    """Resolve before per-test module doubles replace fontlabapp."""
    override = os.environ.get("SCRIPTMIX_APP_SOURCE")
    root = (
        Path(override)
        if override
        else Path(distribution("fontlab-fontlabapp").locate_file("fontlabapp"))
    )
    for name in ("scripting", "_font_info_dialog", "_features_dialog", "feature_code"):
        assert (root / f"{name}.py").is_file(), f"Missing App helper: {root / name}"
    return root


@pytest.fixture(scope="session")
def app_sources():
    return resolve_app_sources()
