# this_file: tests/test_wp05_consolidation.py
"""Accept the complete outline package separately from its historical inventory."""

from pathlib import Path

from menu_layout import active_menu_paths, consolidation_rows


ROOT = Path(__file__).resolve().parents[1]
TARGETS = {
    f"Scripts/Contours/{title}.py"
    for title in (
        "Outline Doctor", "Curve Editor", "Transform Studio", "Align and Nudge",
        "Node Editor", "Contour Selection", "Outline Compatibility",
        "Derived Glyphs", "Shape Generators", "Hint Tools",
    )
}


def test_wp05_all_49_routes_have_ten_implemented_destinations():
    rows = [row for row in consolidation_rows(ROOT)
            if row["destination"] and row["destination"]["path"] in TARGETS]
    assert len(rows) == 49
    assert {row["destination"]["path"] for row in rows} == TARGETS
    for row in rows:
        assert row["acceptance"]["state"] == "implemented", row["source"]["path"]
        assert row["acceptance"]["behavior_parity"] is True, row["source"]["path"]
        assert row["acceptance"]["native"] is False
        assert not (ROOT / row["source"]["path"]).exists(), row["source"]["path"]
    actual = {str(path.relative_to(ROOT)) for path in (ROOT / "Scripts").glob("*/*.py")}
    assert actual == active_menu_paths(ROOT)
    assert len(actual) == 227 - 38 + 8, "249 WP05 menus, minus 31 WP07 retired plus nine WP07 App launchers (227), minus 38 WP03 retired (Zero-Width Marks kept) plus eight WP03 launchers"
