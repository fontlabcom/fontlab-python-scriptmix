# this_file: tests/test_public_docstrings.py
"""Check the complete public menu documentation contract without native imports."""

import ast
from pathlib import Path

ROOT = Path(__file__).parents[1]


def test_every_menu_when_documented_then_has_complete_module_text() -> None:
    paths = sorted((ROOT / "Scripts").glob("*/*.py"))
    assert len(paths) == 240, "Inspect the full menu collection"
    for path in paths:
        text = path.read_text()
        doc = ast.get_docstring(ast.parse(text, feature_version=(3, 11))) or ""
        assert len(doc) >= 700, f"{path}: incomplete module documentation"
        for phrase in ("acceptance pending", "is pending", "Undo restores", "native qualification limits", "qualification remain pending", "qualification remains pending", "still require owned qualification"):
            assert phrase not in doc, f"{path}: public acceptance-status wording"
        for phrase in ("def _backup_master", "def restore_shape", "from fly.ap import", "removeAllShapes"):
            assert phrase not in text, f"{path}: use the shared App path"
