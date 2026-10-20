# this_file: tests/test_rescued_menus.py
"""Verify archived menu contracts without importing a host or running originals."""

import ast
import builtins
import hashlib
import json
import os
import runpy
import sys
from pathlib import Path
from types import ModuleType

import pytest

ROOT = Path(__file__).parents[1]
ARCHIVE = Path(os.environ.get("FONTLAB_PRESERVED_ROOT", str(ROOT)))
INDEX = json.loads((ROOT / "rescue-index.json").read_text())
MENUS = INDEX["menus"]


@pytest.fixture
def dispatch_calls(monkeypatch):
    """Isolate Fly and App from any real packages installed by the owner."""
    calls = []
    for name in list(sys.modules):
        if name.split(".")[0] in {"fly", "fontlabapp"}:
            monkeypatch.delitem(sys.modules, name)
    for name in ("fly", "fly.ap"):
        package = ModuleType(name)
        package.__path__ = []
        monkeypatch.setitem(sys.modules, name, package)
    helper = ModuleType("fly.ap.rescued_examples")
    helper.launch = lambda path: calls.append(Path(path).resolve())
    monkeypatch.setitem(sys.modules, helper.__name__, helper)
    return calls


@pytest.mark.parametrize("entry", MENUS, ids=lambda row: row["menu"])
def test_rescued_menu_import_is_lazy_and_main_dispatches_once(
    monkeypatch, dispatch_calls, entry
):
    imported = []
    real_import = builtins.__import__

    def observe_import(name, *args, **kwargs):
        if name.split(".")[0] in {"fly", "fontlabapp"}:
            imported.append(name)
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", observe_import)
    namespace = runpy.run_path(str(ROOT / entry["menu"]))
    assert imported == [], "Importing a menu must not import Fly or App"
    assert dispatch_calls == [], "Importing a menu must not launch preserved code"
    assert namespace["main"]() is None, "The launcher has no return value contract"
    assert imported == ["fly.ap.rescued_examples"], "Use the qualified Fly helper"
    assert dispatch_calls == [(ROOT / entry["target"]).resolve()], (
        "main() must dispatch exactly once to the indexed preserved target"
    )


@pytest.mark.parametrize("entry", MENUS, ids=lambda row: row["menu"])
def test_rescued_menu_main_guard_dispatches_once(dispatch_calls, entry):
    runpy.run_path(str(ROOT / entry["menu"]), run_name="__main__")
    assert dispatch_calls == [(ROOT / entry["target"]).resolve()], (
        "Script execution must launch exactly once through the main guard"
    )


@pytest.mark.parametrize("entry", MENUS, ids=lambda row: row["menu"])
def test_rescued_menu_documents_and_types_its_python311_contract(entry):
    path = ROOT / entry["menu"]
    text = path.read_text()
    tree = ast.parse(text, filename=str(path), feature_version=(3, 11))
    main = [node for node in tree.body if isinstance(node, ast.FunctionDef)]
    assert len(main) == 1 and main[0].name == "main", "Keep the menu a tiny facade"
    assert (
        isinstance(main[0].returns, ast.Constant) and main[0].returns.value is None
    ), "main must declare -> None"
    assert not main[0].args.args, "main takes no arguments"
    documentation = " ".join((ast.get_docstring(tree) or "").split())
    for phrase in (
        "Purpose:",
        "Setup:",
        "Use:",
        "Result:",
        "native compatibility is pending",
    ):
        assert phrase in documentation, f"Missing honest menu documentation: {phrase}"
    assert entry["target"] in documentation, "Identify the retained source to inspect"
    assert f"# this_file: {entry['menu']}" in text, "Track the actual menu path"


def test_rescue_inventory_preserves_source_hashes_and_menu_layout():
    assert len(MENUS) == INDEX["new_menu_count"] == 61, "Audit all 61 rescue menus"
    assert len({entry["menu"] for entry in MENUS}) == 61, "Menu paths must be unique"
    for entry in MENUS:
        target = ARCHIVE / entry["target"]
        assert target.is_file(), f"Missing retained target: {target}"
        assert (
            hashlib.sha256(target.read_bytes()).hexdigest() == entry["target_sha256"]
        ), f"Retained target bytes changed: {target}"
    for source in INDEX["preserved_sources"].values():
        target = ARCHIVE / source["path"]
        assert hashlib.sha256(target.read_bytes()).hexdigest() == source["sha256"], (
            f"Preserved source bytes changed: {target}"
        )
    for path in (ROOT / "Scripts").rglob("*.py"):
        relative = path.relative_to(ROOT / "Scripts")
        assert len(relative.parts) == 2, f"Menu exceeds one folder level: {relative}"
        assert relative.parts[0] == relative.parts[0].title(), (
            f"Menu category must use Title Case: {relative}"
        )
        ast.parse(path.read_text(), filename=str(path), feature_version=(3, 11))
