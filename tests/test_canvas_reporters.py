# this_file: tests/test_canvas_reporters.py
"""Two new foreground menus dispatch lazily through the reviewed App lifecycle."""

import importlib.util
import runpy
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest
from menu_layout import released_bytes

ROOT = Path(__file__).resolve().parents[1]
CASES = (
    (
        "Sidebearing Direction Marker",
        "canvas_right_sidebearing_line",
        "canvas_rsb_dialog_type",
    ),
    (
        "Duplicate Anchor Rings",
        "canvas_duplicate_anchor_rings",
        "canvas_anchor_rings_dialog_type",
    ),
)


@pytest.mark.parametrize("title,key,factory", CASES)
def test_menu_import_is_lazy_and_main_returns_exact_owned_dialog(
    monkeypatch, title, key, factory
):
    calls = []
    dialog_type, dialog = object(), object()

    def make():
        calls.append("type")
        return dialog_type

    def show(actual_type, actual_key):
        assert (actual_type, actual_key) == (dialog_type, key)
        calls.append("show")
        return dialog

    helpers = SimpleNamespace(**{factory: make, "show_script_dialog": show})
    monkeypatch.setitem(sys.modules, "fly", SimpleNamespace())
    monkeypatch.setitem(sys.modules, "fly.ap.scripting", helpers)
    path = ROOT / "Scripts/Reporters" / f"{title}.py"
    spec = importlib.util.spec_from_file_location("owned_canvas_menu", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert calls == [], "Import must not create a native window or resolve its type"
    assert module.TITLE == title and module.KEY == key
    assert module.main() is dialog and calls == ["type", "show"]
    calls.clear()
    runpy.run_path(str(path), run_name="__main__")
    assert calls == ["type", "show"], "FontLab script execution must use the same owner"


def test_prior68_migration_rows_and_payloads_are_unchanged():
    import hashlib
    import json

    path = ROOT / "migration.json"
    rows = json.loads(path.read_text())
    assert len(rows) == 69
    assert (
        hashlib.sha256((json.dumps(rows[:68], indent=2) + "\n").encode()).hexdigest()
        == "ef87bc7a69eef091a3061dfed5fee748631edca8576b6fdf0c2ebf9a99cff415"
    )
    for row in rows:
        assert (
            hashlib.sha256(released_bytes(ROOT, row)).hexdigest()
            == row["destination_sha256"]
        )


def test_additional_reporter_provenance_and_acceptance_cover_exact_new_menus():
    import ast
    import hashlib
    import json

    rows = json.loads((ROOT / "additional-tools.json").read_text())
    rows = [row for row in rows if row["kind"] == "foreground-adaptation"]
    assert len(rows) == 2 and {row["title"] for row in rows} == {v[0] for v in CASES}
    for row in rows:
        path = Path(row["destination"])
        assert path.parts == ("Scripts", "Reporters", row["title"] + ".py")
        assert row["key"] == next(v[1] for v in CASES if v[0] == row["title"])
        assert row["license"] == "Apache-2.0" and row["kind"] == "foreground-adaptation"
        assert row["counted_in_130_sample_migration"] is False
        assert row["native_acceptance"] == "passed", (
            "Native pending reporters cannot be released"
        )
        assert row["native_evidence"] and all(
            len(v) == 64 for v in row["native_evidence"].values()
        )
        assert row["upstream_repository"].startswith("https://github.com/")
        assert all(
            len(row[key]) == 64
            for key in ("source_sha256", "license_sha256", "destination_sha256")
        )
        payload = (ROOT / path).read_bytes()
        assert hashlib.sha256(payload).hexdigest() == row["destination_sha256"]
        assert all(
            c in "0123456789abcdef"
            for key in ("source_sha256", "license_sha256", "destination_sha256")
            for c in row[key]
        )
        ast.parse(payload, feature_version=(3, 11))
        assert "foreground" in payload.decode().lower() and "Close" in payload.decode()
