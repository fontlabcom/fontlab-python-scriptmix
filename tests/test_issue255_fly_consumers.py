# this_file: tests/test_issue255_fly_consumers.py
"""Public scripts use Fly; native smoke is inspected without running it."""

import ast
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
PROVIDERS = {
    "fontlabapp", "fontlab_fontport", "fontlab_glyport", "fontlab_pens",
    "fontlab", "fontgate", "fontpr", "PythonQt", "echopy", "fontlab_echopy",
}


@pytest.mark.parametrize("path", sorted((ROOT / "Scripts").glob("*/*.py")))
def test_public_menu_when_inspected_then_provider_access_uses_fly(path):
    tree = ast.parse(path.read_text(), feature_version=(3, 11))
    imports = [node for node in ast.walk(tree)
               if isinstance(node, (ast.Import, ast.ImportFrom))]
    names = {node.module for node in imports if isinstance(node, ast.ImportFrom)}
    names.update(alias.name for node in imports if isinstance(node, ast.Import)
                 for alias in node.names)
    assert not {name for name in names if name.split(".")[0] in PROVIDERS}, path


def test_native_smoke_when_inspected_then_fly_routes_preserve_native_bindings():
    path = ROOT / "varia/HT-Letterspacer-FL/src/tests/fontlab_smoke.py"
    source = path.read_text()
    tree = ast.parse(source, feature_version=(3, 11))
    bindings = {
        (node.module, alias.name, alias.asname)
        for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)
        for alias in node.names if (node.module or "").startswith("fly")
    }
    assert bindings == {
        ("fly", "fl", None), ("fly", "fg", None), ("fly", "pr", "fontpr"),
        ("fly.qt", "QtCore", None), ("fly.qt", "QtGui", None),
    }
    assert not any(isinstance(node, ast.Import) and
                   any(alias.name in PROVIDERS for alias in node.names)
                   for node in ast.walk(tree))
    compile(source, str(path), "exec")
