# this_file: tests/test_issue122_G10.py
# SPDX-License-Identifier: Apache-2.0
"""Retain both master-menu source/import contracts after shared App extraction.

Common Glyphs behavioral/capture/lifecycle cases now live in App's expanded
common_glyphs tests; thin menu and actual metadata tests are in
 test_common_glyphs_menu.py. Source assertions below retain their original scope.
"""

import ast
import importlib.util
from pathlib import Path
from types import ModuleType
from typing import Any
import pytest
from conftest import app_names_used, check_real_app_names

ROOT = Path(__file__).resolve().parents[1]
TITLES = ("Master Text Comparison", "Common Glyphs")


def load(title: str) -> ModuleType:
    """Load a menu without running its entry point."""
    spec = importlib.util.spec_from_file_location(
        title, ROOT / "Scripts/Masters" / f"{title}.py"
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None, "A source loader is required"
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def menus() -> tuple[ModuleType, ModuleType]:
    return tuple(load(title) for title in TITLES)


def test_real_app_imports_use_installed_distribution() -> None:
    check_real_app_names(
        app_names_used([ROOT / "Scripts/Masters" / f"{title}.py" for title in TITLES])
    )


def test_public_files_are_python311_and_read_only(menus: Any) -> None:
    for title, module in zip(TITLES, menus, strict=True):
        path = ROOT / "Scripts/Masters" / f"{title}.py"
        text = path.read_text()
        ast.parse(text, feature_version=(3, 11))
        assert "Independent rewrite" in module.__doc__ and "MIT" in module.__doc__, (
            "Credit source behaviour"
        )
        assert not any(
            word in text.lower()
            for word in ("archived", "unresolved", "issue 122", "batch g10")
        ), "Public language only"
        assert not any(
            word in text
            for word in (
                "notifyChangesApplied",
                "initHistoryState",
                "set_glyph",
                "UpdateAll",
            )
        ), "Read-only tools must not write history"


def test_scripts_use_only_public_app_attributes() -> None:
    used = app_names_used(
        [ROOT / "Scripts/Masters" / f"{title}.py" for title in TITLES]
    )
    assert all(
        not part.startswith("_") for module in used for part in module.split(".")
    ), used
    assert all(not name.startswith("_") for names in used.values() for name in names), (
        "Keep App implementation details behind public helpers"
    )


def test_explicit_fly_app_paths_have_no_private_names() -> None:
    """Also catch full fly.ap.module._member paths without import aliases."""
    for path in [ROOT / "Scripts/Masters" / f"{title}.py" for title in TITLES]:
        for node in ast.walk(ast.parse(path.read_text())):
            if not isinstance(node, ast.Attribute):
                continue
            parts = []
            current = node
            while isinstance(current, ast.Attribute):
                parts.insert(0, current.attr)
                current = current.value
            if (
                isinstance(current, ast.Name)
                and current.id == "fly"
                and parts[0] == "ap"
            ):
                assert all(not part.startswith("_") for part in parts), (path, parts)
