# this_file: tests/test_wp05_source_audit.py
"""Historical import audits read verified data without executing archived menus."""

from pathlib import Path

from conftest import app_names_used


def test_removed_hint_import_contract_remains_auditable():
    root = Path(__file__).resolve().parents[1]
    used = app_names_used([root / "Scripts/Contours/Autohint Selected Layers.py"])
    assert "hint_counts" in used["fly.ap.hints.postscript"]


def test_import_audit_reads_non_menu_sources_directly(tmp_path):
    path = tmp_path / "source.py"
    path.write_text("from fly.ap.core.scripting import current_package\n")
    assert app_names_used([path]) == {"fly.ap.core.scripting": {"current_package"}}


def test_import_audit_checks_migrated_canonical_app_imports(tmp_path):
    path = tmp_path / "port.py"
    path.write_text("from fontlabapp.core.scripting import current_package\n"
                    "import fontlabapp.hints.postscript as hints\nhints.hint_counts(None)\n")
    assert app_names_used([path]) == {
        "fly.ap.core.scripting": {"current_package"},
        "fly.ap.hints.postscript": {"hint_counts"},
    }
