# this_file: tests/test_contour_menu_integration.py
"""Keep the curated menu and immutable migration identities during integration."""

import hashlib
import json
from pathlib import Path

from menu_layout import current_rows

ROOT = Path(__file__).resolve().parents[1]
TITLES = ("Select Contours", "Select Partial Contours", "Select Small Contours")


def test_three_contour_candidates_extend_curated_menu_without_archive_dispatchers():
    sample_rows = current_rows(ROOT)
    additional = json.loads((ROOT / "additional-tools.json").read_text())
    menus = {str(path.relative_to(ROOT)) for path in (ROOT / "Scripts").rglob("*.py")}
    assert len(sample_rows) == 69
    assert len(additional) == 171
    assert len(menus) == 240
    assert menus == {row["destination"] for row in sample_rows + additional}
    archive = json.loads((ROOT / "rescue-index.json").read_text())
    assert len(archive["menus"]) == 61
    candidates = {row["rescued_original_menu"] for row in additional if row.get("rescued_original_menu")}
    assert menus.intersection(row["menu"] for row in archive["menus"]) == candidates
    selected = [row for row in additional if row["title"] in TITLES]
    assert {row["title"] for row in selected} == set(TITLES)
    for row in selected:
        assert row["counted_in_130_sample_migration"] is False
        assert row["native_acceptance"] == "pending"
        assert row["license"] == "Apache-2.0"
        assert (
            hashlib.sha256((ROOT / row["destination"]).read_bytes()).hexdigest()
            == row["destination_sha256"]
        )


def test_current_rows_accepts_already_current_owner_routes_without_rewriting(tmp_path):
    """Exercise the unchanged current_rows against both supported representations."""
    for name in ("menu-moves.json", "menu-revisions.json", "migration.json"):
        (tmp_path / name).write_bytes((ROOT / name).read_bytes())
    for move in current_rows(ROOT):
        source = ROOT / move["destination"]
        target = tmp_path / move["destination"]
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(source.read_bytes())
    original = (tmp_path / "migration.json").read_bytes()
    resolved = current_rows(tmp_path)
    assert (tmp_path / "migration.json").read_bytes() == original
    (tmp_path / "migration.json").write_text(json.dumps(resolved, indent=2) + "\n")
    owner = (tmp_path / "migration.json").read_bytes()
    assert current_rows(tmp_path) == resolved
    assert (tmp_path / "migration.json").read_bytes() == owner


def test_contour_notice_points_to_existing_complete_apache_terms():
    notice = (
        (ROOT / "NOTICE")
        .read_text()
        .split("Pedro Arilla contour selection adaptations", 1)[1]
    )
    assert "complete terms in LICENSE." in notice
    terms = (ROOT / "LICENSE").read_text()
    assert "Apache License" in terms and "Version 2.0, January 2004" in terms
    assert "END OF TERMS AND CONDITIONS" in terms
