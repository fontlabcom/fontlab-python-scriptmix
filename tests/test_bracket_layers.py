# this_file: tests/test_bracket_layers.py
"""First-party bracket-layer menu contracts; never execute source originals."""

import ast
import hashlib
import json
import runpy
import sys
from pathlib import Path
from types import ModuleType

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("folder,method", [("Reports", "show"), ("Proof", "open_tab")])
def test_menu_when_imported_and_run_then_lazy_exact_fly_dispatch(
    monkeypatch, folder, method
):
    path = ROOT / "Scripts" / folder / "Bracket Layers and Components.py"
    calls = []
    for name in ("fly", "fly.ap", "fly.ap.bracket_layers"):
        monkeypatch.setitem(sys.modules, name, ModuleType(name))
    setattr(sys.modules["fly.ap.bracket_layers"], method, lambda: calls.append(method))
    values = runpy.run_path(str(path), run_name="inspection")
    assert calls == [], "Importing a menu must not access the host"
    values["main"]()
    runpy.run_path(str(path), run_name="__main__")
    assert calls == [method, method]
    tree = ast.parse(path.read_text(), feature_version=(3, 11))
    main = next(n for n in tree.body if isinstance(n, ast.FunctionDef))
    assert main.returns.value is None
    assert "App>=0.2.53.dev0" in ast.get_docstring(tree)


@pytest.mark.parametrize(
    "key,folder",
    [("bracket_layers_report", "Reports"), ("bracket_layers_tab", "Proof")],
)
def test_provenance_when_two_workflows_added_then_license_source_repairs_and_pending_native(
    key, folder
):
    rows = json.loads((ROOT / "additional-tools.json").read_text())
    row = next(v for v in rows if v["key"] == key)
    path = ROOT / "Scripts" / folder / "Bracket Layers and Components.py"
    assert row["destination"] == str(path.relative_to(ROOT))
    assert row["destination_sha256"] == hashlib.sha256(path.read_bytes()).hexdigest()
    assert row["license"] == "Apache-2.0" and row["native_acceptance"] == "pending"
    assert row["counted_in_130_sample_migration"] is False
    assert len(row["source_sha256"]) == 64 and len(row["license_sha256"]) == 64
    assert row["license_declaration"] == "README.md lines104-111"
    assert row["source_repairs"]
    assert "Fernando Díaz" in (ROOT / "NOTICE").read_text()
