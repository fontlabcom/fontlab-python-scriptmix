# this_file: tests/test_curated_delivery.py
"""Reject archive dispatchers and retain the complete source backlog."""

import ast
import hashlib
import json
import os
from pathlib import Path

from menu_layout import current_rows

ROOT = Path(__file__).resolve().parents[1]


ARCHIVE = Path(os.environ.get("FONTLAB_PRESERVED_ROOT", str(ROOT)))


def test_active_menu_contains_only_indexed_practical_tools():
    rows = current_rows(ROOT)
    extra = json.loads((ROOT / "additional-tools.json").read_text())
    expected = {row["destination"] for row in rows + extra}
    actual = {str(path.relative_to(ROOT)) for path in (ROOT / "Scripts").rglob("*.py")}
    assert actual == expected, "Only practical indexed tools belong in the active menu"
    assert len(rows) == 69 and len(extra) == 157 and len(actual) == 226
    for relative in actual:
        path = ROOT / relative
        assert len(Path(relative).parts) == 3, relative
        assert path.parent.name == path.parent.name.title(), relative
        source = path.read_text()
        ast.parse(source, filename=relative, feature_version=(3, 11))
        assert "rescued_examples" not in source, relative
        assert "# this_file: " + relative in source.splitlines()[:5], relative
        assert "native compatibility is pending" not in source, relative


def test_unported_sources_remain_a_complete_hashed_backlog():
    index = json.loads((ROOT / "rescue-index.json").read_text())
    assert len(index["menus"]) == index["new_menu_count"] == 61
    assert len(index["preserved_sources"]) == 69
    for row in index["menus"]:
        candidates = {r.get("rescued_original_menu"): r for r in json.loads((ROOT / "additional-tools.json").read_text()) if r.get("rescued_original_menu")}
        if row["menu"] in candidates:
            candidate = candidates[row["menu"]]
            assert candidate["destination"] == row["menu"]
            assert candidate["source_sha256"] == row["target_sha256"]
            assert candidate["native_acceptance"] == "pending"
            assert candidate["counted_in_130_sample_migration"] is False
        else:
            assert not (ROOT / row["menu"]).exists(), row["menu"]
        assert hashlib.sha256((ARCHIVE / row["target"]).read_bytes()).hexdigest() == row["target_sha256"]
    assert (ROOT / "PORTING-BACKLOG.md").is_file(), "Keep unfinished ports visible"


def test_active_menu_has_no_stale_sourceless_compiled_launchers():
    stale = [str(path.relative_to(ROOT)) for path in (ROOT / "Scripts").rglob("*.pyc")
             if "__pycache__" not in path.parts]
    assert not stale, f"Preserve and remove old compiled menu entries: {stale}"


def test_reused_bodies_when_listed_then_only_the_authors_own_apache_samples():
    rows = json.loads((ROOT / "additional-tools.json").read_text())
    reused = [row for row in rows if row.get("source_body_redistributed") is True]
    families = sorted({row["destination"].split("/")[1] for row in reused})
    assert families == ["Anchors", "Cleanup", "Components", "Contours", "Masters", "Metrics", "Names"], families
    assert len(reused) == 56, [row["destination"] for row in reused]
    for row in reused:
        assert row["license"] == "Apache-2.0", row["destination"]
        assert row["source_path"].startswith("rescued/samples/"), row["destination"]
        assert "Independent rewrite" not in row["scope"], row["destination"]
    masters = [row for row in rows if row["destination"].startswith("Scripts/Masters/")
               and not row["source_path"].startswith("rescued/samples/")]
    assert masters and all(row["source_body_redistributed"] is False for row in masters)
    readme = " ".join((ROOT / "README.md").read_text().split())
    assert "Third-party and Glyphs-corpus original bodies are not copied" in readme
    assert "The author's own Apache-2.0 FontLab samples may be adapted" in readme


def test_backlog_when_a_port_exists_then_its_row_is_not_unported():
    rows = json.loads((ROOT / "additional-tools.json").read_text())
    ported = {row["rescued_original_menu"].removeprefix("Scripts/") for row in rows if row.get("rescued_original_menu")}
    for line in (ROOT / "PORTING-BACKLOG.md").read_text().splitlines():
        if line.startswith("| ") and line.count("|") == 4:
            menu, status = line.split("|")[1].strip(), line.split("|")[3].strip()
            if menu in ported:
                assert not status.startswith("Unported"), menu


NEW_TOOLS = {
    "Metrics": ["Italic Sidebearings", "Round Advances", "Centre In Advance", "Zero-Width Marks",
                "Tabular Width", "Scale Advances", "Equalize Sidebearings", "Sidebearings Tuner",
                "Copy Metrics From Reference", "Vertical Metrics Diagram"],
    "Names": ["Glyph Tags", "Mark Color Palette", "Suffix Tool", "Batch Rename", "Batch Glyph Notes",
              "Glyph Notes", "Unicode From Names", "Style Linker"],
    "Anchors": ["Rename Bulk", "Center Horizontally", "Place From Bounds", "Snap To Metrics",
                "Round To Grid", "Delete By Name", "Mirror Across Masters", "Add Anchors From File",
                "Auto Cursive Attachment Add Anchors", "Auto Cursive Attachment Get Sample",
                "Copy Myanmar Anchors", "Derive Anchors From Components", "Optical Center",
                "Remove Extraneous Mark Anchors"],
    "Masters": ["Display Next Layer", "Display Previous Layer", "Duplicate Current Layer",
                "Use Layer As Master", "Transform Background", "Selection To All Backgrounds",
                "Select Different Colour", "Copy Outline To Mask", "Copy Layer Between Masters",
                "Restore Backup Layer", "Layer Cleanup", "Sync Sidebearings", "Set Intermediate Layer",
                "Master Twins", "Deliver Glyphs", "Master Text Comparison", "Common Glyphs"],
    "Components": ["Build From Recipes", "Align By Anchor", "Decompose", "Replace Reference",
                   "Copy Offsets Between Masters", "Unlock Lock", "Nested Finder",
                   "Decompose Named Components", "Set Component Locations"],
    "Cleanup": ["Empty Layers"],
    "Contours": ["Round Coordinates", "Remove Overlap", "Add Extremes", "Correct Contour Direction",
                 "Straighten Short Curves", "Optimize Start Points", "Delete Small Contours",
                 "Fix Zero Handles", "Delete Duplicate Contours", "Transform", "Slant",
                 "Placeholder Glyphs", "Shadow Copy", "Tabular Figure Copies", "Outline Effect",
                 "Superior & Inferior Figures", "Small Caps From Capitals", "Autohint Selected Layers",
                 "Remove PostScript Hints", "Smart Slant", "Node Duplicator", "Comb",
                 "Curve All Straights", "Delete Close Points", "Make Compatible", "Sandblast",
                 "Straighten All Curves", "Superaligner", "Interpolated Nudge", "Sansomatic",
                 "Myanmar Medial Ra Maker", "Align And Distribute", "Rotate Selection",
                 "Reflect Horizontally", "Reflect Vertically", "Overlap Nodes"],
    "Proof": ["Real English Text", "Real Spanish Text"],
    "Font Info": ["Trial Font Maker", "Paste Glyph Order Encoding"],
    "Utilities": ["Magic Remover"],
    "Kerning": ["Kerning Energy Report", "Unbundle Punctuation Kerning"],
    "Features": ["Nastaliq Connection Editor"],
}


def test_app_floor_when_new_tools_or_layer_selection_then_one_value():
    rows = {row["destination"]: row for row in json.loads((ROOT / "additional-tools.json").read_text())}
    wanted = [f"Scripts/{folder}/{name}.py" for folder, names in NEW_TOOLS.items() for name in names]
    wanted.append("Scripts/Contours/Raise Ascender.py")
    assert len(wanted) == 104
    floors = {path: rows[path]["app_minimum"] for path in wanted}
    assert set(floors.values()) == {"0.2.150.dev0"}, floors


#: The App version that this branch builds; no menu may require a later App.
BRANCH_APP = "0.2.150.dev0"


def test_app_floor_when_any_row_then_not_above_the_branch_app():
    from packaging.version import Version

    rows = json.loads((ROOT / "additional-tools.json").read_text())
    above = {
        row["destination"]: row["app_minimum"]
        for row in rows
        if "app_minimum" in row and Version(row["app_minimum"]) > Version(BRANCH_APP)
    }
    assert above == {}, above


PROCESS_WORDS = ("reviewed App", "reviewed unpublished", "App helper", "issue 12", "Issue 12", "batch S", "batch G")


def test_script_docstrings_when_public_then_no_process_jargon():
    found = []
    for path in sorted((ROOT / "Scripts").rglob("*.py")):
        doc = ast.get_docstring(ast.parse(path.read_text())) or ""
        found += [f"{path.relative_to(ROOT)}: {word}" for word in PROCESS_WORDS if word in doc]
    assert not found, found
