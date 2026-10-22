# this_file: tests/test_anchor_menu_polish.py
"""Check exact helper typing without adding native annotation lookups."""

import ast
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace as NS

import pytest
from test_anchor_copy import copying  # noqa: F401
from test_components import components  # noqa: F401
from test_guides import guides  # noqa: F401
from test_masters import masters  # noqa: F401

from menu_layout import current_rows, released_bytes

MENU = Path(__file__).parents[1] / "Scripts/Anchors/Copy Anchors From Glyph.py"


def test_helpers_explain_their_exact_existing_runtime_types():
    tree = ast.parse(MENU.read_text(), feature_version=(3, 11))
    fmt = next(
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name == "fmt"
    )
    owner = next(
        node
        for node in tree.body
        if isinstance(node, ast.ClassDef) and node.name == "CopyAnchors"
    )
    source = next(
        node
        for node in owner.body
        if isinstance(node, ast.FunctionDef) and node.name == "source_glyph"
    )
    assert ast.unparse(fmt.args.args[0].annotation) == "tuple[int, int] | None"
    assert ast.unparse(fmt.returns) == "str"
    assert ast.literal_eval(source.returns) == "fontlab.flGlyph | None"
    assert ast.get_docstring(fmt) and ast.get_docstring(source)


@pytest.mark.parametrize(
    "point,expected", [(None, "removed"), ((0, 0), "0, 0"), ((-17, 688), "-17, 688")]
)
def test_format_preserves_existing_integer_point_and_removal_text(
    copying, point, expected  # noqa: F811
):
    menu = copying.menu()
    assert menu.fmt(point) == expected
    assert (
        menu.CopyAnchors.source_glyph.__annotations__["return"]
        == "fontlab.flGlyph | None"
    )


@pytest.mark.parametrize(
    "name,has_package", [("", True), ("  ", True), ("n", False), (" n ", True)]
)
def test_source_lookup_preserves_optional_result_and_exact_native_object(
    copying, name, has_package  # noqa: F811
):
    menu = copying.menu()
    calls = []
    glyph = object()
    package = (
        NS(findName=lambda value: calls.append(value) or glyph) if has_package else None
    )
    panel = NS(package=package, source=NS(text=name))
    result = menu.CopyAnchors.source_glyph(panel)
    assert result is (glyph if has_package and name.strip() else None)
    assert calls == ([name.strip()] if has_package and name.strip() else [])


def test_revision_preserves_historical_source_and_all_executable_ast():

    root = MENU.parents[2]
    manifest = (root / "migration.json").read_bytes()
    row = next(
        row
        for row in json.loads(manifest)
        if row["destination"] == str(MENU.relative_to(root))
    )
    historical = released_bytes(root, row)
    assert hashlib.sha256(historical).hexdigest() == row["destination_sha256"]
    current = next(
        item for item in current_rows(root) if item["destination"] == row["destination"]
    )
    assert current["source_sha256"] == row["source_sha256"]
    assert (
        current["destination_sha256"] == hashlib.sha256(MENU.read_bytes()).hexdigest()
    )
    assert (root / "migration.json").read_bytes() == manifest

    class Executable(ast.NodeTransformer):
        def visit_Module(self, node):
            self.generic_visit(node)
            if node.body and isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, ast.Constant) and isinstance(node.body[0].value.value, str):
                node.body = node.body[1:]
            return node

        def visit_FunctionDef(self, node):
            self.generic_visit(node)
            node.returns = None
            for argument in (
                node.args.posonlyargs + node.args.args + node.args.kwonlyargs
            ):
                argument.annotation = None
            if node.args.vararg:
                node.args.vararg.annotation = None
            if node.args.kwarg:
                node.args.kwarg.annotation = None
            if (
                node.body
                and isinstance(node.body[0], ast.Expr)
                and isinstance(node.body[0].value, ast.Constant)
                and isinstance(node.body[0].value.value, str)
            ):
                node.body = node.body[1:]
            return node

    normalize = lambda data: ast.dump(
        Executable().visit(ast.parse(data, feature_version=(3, 11))),
        include_attributes=False,
    )
    assert normalize(historical) == normalize(MENU.read_bytes()), (
        "Only annotations and module/function docstrings may change"
    )


@pytest.mark.parametrize(
    "failure", ["source", "row_hash", "body", "edit", "duplicate", "unknown"]
)
def test_revision_rejects_changed_source_hash_body_or_edit_ledger(tmp_path, failure):

    root = MENU.parents[2]
    row = next(
        row
        for row in json.loads((root / "migration.json").read_text())
        if row["destination"] == str(MENU.relative_to(root))
    )
    ledger = json.loads((root / "menu-revisions.json").read_text())
    destination = tmp_path / row["destination"]
    destination.parent.mkdir(parents=True)
    destination.write_bytes(MENU.read_bytes())
    if failure == "source":
        row["source_sha256"] = "0" * 64
    if failure == "row_hash":
        row["destination_sha256"] = "0" * 64
    if failure == "body":
        destination.write_bytes(
            destination.read_bytes().replace(b'return "removed"', b'return "changed"')
        )
        ledger["revisions"][0]["current_sha256"] = hashlib.sha256(
            destination.read_bytes()
        ).hexdigest()
    if failure == "edit":
        ledger["revisions"][0]["edits"][0]["current"] = "absent edit"
    if failure == "duplicate":
        ledger["revisions"] *= 2
    if failure == "unknown":
        ledger["revisions"][0]["destination"] = "Scripts/Unknown/Unknown.py"
    (tmp_path / "migration.json").write_text(json.dumps([row]))
    (tmp_path / "menu-moves.json").write_text('{"moves": []}')
    (tmp_path / "menu-revisions.json").write_text(json.dumps(ledger))
    with pytest.raises(ValueError):
        current_rows(tmp_path)


def test_revision_accepts_current_hash_without_rewriting_either_manifest_form(tmp_path):

    root = MENU.parents[2]
    original = next(
        row
        for row in json.loads((root / "migration.json").read_text())
        if row["destination"] == str(MENU.relative_to(root))
    )
    current = next(
        row
        for row in current_rows(root)
        if row["destination"] == original["destination"]
    )
    destination = tmp_path / current["destination"]
    destination.parent.mkdir(parents=True)
    destination.write_bytes(MENU.read_bytes())
    (tmp_path / "migration.json").write_text(json.dumps([current]))
    (tmp_path / "menu-moves.json").write_text('{"moves": []}')
    # Keep only this menu's revision: the copied manifest has only its row.
    ledger = json.loads((root / "menu-revisions.json").read_text())
    ledger["revisions"] = [
        row for row in ledger["revisions"] if row["destination"] == current["destination"]
    ]
    (tmp_path / "menu-revisions.json").write_text(json.dumps(ledger))
    before = (tmp_path / "migration.json").read_bytes()
    assert current_rows(tmp_path) == [current]
    assert (tmp_path / "migration.json").read_bytes() == before
    assert released_bytes(tmp_path, current) == MENU.read_bytes()
    assert released_bytes(tmp_path, original) == released_bytes(root, original)
