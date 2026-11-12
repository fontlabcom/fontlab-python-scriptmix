# this_file: tests/test_font_ui_lab_menus.py
"""Three lazy dispatches and exact old/new catalogue provenance."""

import ast
import hashlib
import json
import runpy
import sys
from pathlib import Path
from types import ModuleType

import pytest
from menu_layout import _menu_bytes, active_menu_paths, current_rows

ROOT = Path(__file__).resolve().parents[1]
CASES = [
    (
        "Glyph Browser and Metrics",
        "glyph_metrics",
        "font_ui_lab_glyph_metrics",
        "069d4ccba0484e420c4f905cbe3528471f917a7f1b189e5e3cf5f183cb2abcb6",
    ),
    (
        "Anchor and Component Inspector",
        "anchor_components",
        "font_ui_lab_anchor_components",
        "bcad7f3760c86d6678cf77c9c0b1237306843cd74495f45c2dca7f316cad397e",
    ),
    (
        "Unicode and Glyph Order Explorer",
        "unicode_order",
        "font_ui_lab_unicode_order",
        "d4715f1721dc5d9b1401ba0b2ee0ef1ae671be242409c649c7733495c976a4fa",
    ),
]
OLD_ROWS_SHA = "6217738df546e537ad0dc694676a65aba0af1963d247020d7285c1a0c78ee046"
OLD_MENUS_SHA = "4e1f5369bc2ba3a4fe9fe0699dadf91492b5709bf94b96489a310dd39866bd79"


@pytest.mark.parametrize("case", CASES)
@pytest.mark.parametrize("font", [None, object()])
@pytest.mark.parametrize("route", ["import", "main"])
def test_real_menu_when_dispatched_then_one_world_and_exact_show(
    monkeypatch, case, font, route
):
    title, module, _key, digest = case
    path = ROOT / "Scripts/Font UI Lab" / f"{title}.py"
    calls = []
    sentinel = object()
    app = ModuleType("fly.ap.fontui." + module)
    app.show = lambda value: calls.append(("show", value)) or sentinel
    world_module = ModuleType("fly.fp.world")

    class FontWorld:
        def __init__(self):
            calls.append(("world",))

        def CurrentFont(self):
            calls.append(("current",))
            return font

    world_module.FontWorld = FontWorld
    monkeypatch.setitem(sys.modules, app.__name__, app)
    monkeypatch.setitem(sys.modules, world_module.__name__, world_module)
    if route == "import":
        namespace = runpy.run_path(str(path), run_name="inspection")
        assert calls == []
        assert namespace["main"]() is sentinel
    else:
        runpy.run_path(str(path), run_name="__main__")
    assert calls == [("world",), ("current",), ("show", font)]
    assert hashlib.sha256(path.read_bytes()).hexdigest() == digest
    tree = ast.parse(path.read_text(), feature_version=(3, 11))
    assert not any(isinstance(n, (ast.Import, ast.ImportFrom)) for n in tree.body)


def test_new_rows_when_added_then_old_259_bodies_and_190_rows_are_exact():
    rows = json.loads((ROOT / "additional-tools.json").read_text())
    paths = {f"Scripts/Font UI Lab/{title}.py" for title, *_ in CASES} | {
        "Scripts/Font UI Lab/Tabular Width Audit.py"
    } | {
        "Scripts/Font UI Lab/Kerning Proof Workbench.py",
        "Scripts/Font UI Lab/Kerning Group Explorer.py",
        "Scripts/Font UI Lab/Feature Source and Proof.py",
        "Scripts/Font UI Lab/Detached Transform Preview.py",
        "Scripts/Font UI Lab/Batch UFO Recipe Workbench.py",
        "Scripts/Font UI Lab/Master Width Comparison.py",
        "Scripts/Font UI Lab/Interpolation Preview.py",
        "Scripts/Font UI Lab/Open Fonts and Master Overview.py",
        "Scripts/Font UI Lab/Master Compatibility Browser.py",
        "Scripts/Font UI Lab/Node Counts Across Masters.py",
        "Scripts/Font UI Lab/Font Info and Vertical Metrics.py",
        "Scripts/Font UI Lab/Designspace Source Comparison.py",
        "Scripts/Font UI Lab/UFO Roundtrip Inspector.py",
        "Scripts/Font UI Lab/Representation and Notification Explorer.py",
        "Scripts/Metrics/TMetrics Window.py",
        "Scripts/Contours/TGlyph Window.py",
        "Scripts/Proof/Context Proof.py",
        "Scripts/Reports/Font Audit.py",
        "Scripts/Utilities/Reference Image Viewer App.py",
        "Scripts/Reports/Geometry Audit.py",
        "Scripts/Reports/Master Structure Audit.py",
        "Scripts/Reports/Font Revision Comparison.py",
        "Scripts/Reports/Metric Reports.py",
        "Scripts/Reports/Open Contours App.py",
        "Scripts/Reports/Nodes Near Zones App.py",
    }
    previous = [r for r in rows if r["destination"] not in paths]
    assert len(previous) == 190
    assert (
        hashlib.sha256(
            json.dumps(previous, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
        == OLD_ROWS_SHA
    )
    historical = current_rows(ROOT) + rows
    old = sorted(row["destination"] for row in historical if row["destination"] not in paths)
    assert len(old) == 259
    payload = [
        (p, hashlib.sha256(_menu_bytes(ROOT, p)).hexdigest())
        for p in old
    ]
    assert (
        hashlib.sha256(json.dumps(payload, separators=(",", ":")).encode()).hexdigest()
        == OLD_MENUS_SHA
    )
    assert len(rows) == 219 and len(historical) == 288
    assert {str(p.relative_to(ROOT)) for p in (ROOT / "Scripts").glob("*/*.py")} == active_menu_paths(ROOT)
    for title, module, key, digest in CASES:
        matching = [r for r in rows if r["key"] == key]
        assert len(matching) == 1
        row = matching[0]
        assert (
            row["destination"] == f"Scripts/Font UI Lab/{title}.py"
            and row["destination_sha256"] == digest
        )
        assert (
            row["app_api"] == f"fontlabapp.fontui.{module}.show"
            and "app_minimum" not in row
        )
        assert (
            row["native_acceptance"] == "pending"
            and row["source_body_redistributed"] is False
        )
        assert (
            row["counted_in_130_sample_migration"] is False
            and row["license"] == "Apache-2.0"
        )


@pytest.mark.parametrize("case", CASES)
def test_actual_paired_app_when_resolved_through_fly_then_show_exists(case):
    import importlib

    _title, module, _key, _digest = case
    loaded = importlib.import_module("fly.ap.fontui." + module)
    assert callable(loaded.show)
    assert set(loaded.__all__) == {
        {
            "glyph_metrics": "GlyphMetrics",
            "anchor_components": "GlyphDetails",
            "unicode_order": "GlyphRecord",
        }[module],
        {
            "glyph_metrics": "metrics",
            "anchor_components": "details",
            "unicode_order": "records",
        }[module],
        "show",
    }


@pytest.mark.parametrize("route", ["import", "main"])
def test_tabular_audit_menu_when_dispatched_then_one_world_and_retained_owner(monkeypatch, route):
    calls = []
    sentinel = object()
    app = ModuleType("fly.ap.fontui.tabular_audit")
    app.show = lambda world: calls.append(("show", world)) or sentinel
    world_module = ModuleType("fly.fp.world")

    class FontWorld:
        def __init__(self):
            calls.append(("world", self))

    world_module.FontWorld = FontWorld
    monkeypatch.setitem(sys.modules, app.__name__, app)
    monkeypatch.setitem(sys.modules, world_module.__name__, world_module)
    path = ROOT / "Scripts/Font UI Lab/Tabular Width Audit.py"
    namespace = runpy.run_path(str(path), run_name="__main__" if route == "main" else "inspection")
    if route == "import":
        assert not calls
        assert namespace["main"]() is sentinel
    assert len(calls) == 2 and calls[0][0] == "world"
    assert calls[1] == ("show", calls[0][1])
    tree = ast.parse(path.read_text(), feature_version=(3, 11))
    assert not any(isinstance(n, (ast.Import, ast.ImportFrom)) for n in tree.body)


def test_tabular_audit_when_actual_fly_resolves_then_direct_submodule_show():
    import importlib

    loaded = importlib.import_module("fly.ap.fontui.tabular_audit")
    canonical = importlib.import_module("fontlabapp.fontui.tabular_audit")
    assert loaded.show is canonical.show
    assert loaded.__all__ == ("show",)
    assert Path(loaded.__file__).name == "tabular_audit.py"


def test_tabular_audit_when_catalogued_then_exact_source_and_pending_provenance():
    rows = json.loads((ROOT / "additional-tools.json").read_text())
    matching = [row for row in rows if row["key"] == "font_ui_lab_tabular_audit"]
    assert len(matching) == 1
    row = matching[0]
    assert row["destination"] == "Scripts/Font UI Lab/Tabular Width Audit.py"
    assert row["destination_sha256"] == hashlib.sha256((ROOT / row["destination"]).read_bytes()).hexdigest()
    assert row["app_api"] == "fontlabapp.fontui.tabular_audit.show"
    assert row["native_acceptance"] == "pending"
    assert row["counted_in_130_sample_migration"] is False
    assert row["source_body_redistributed"] is False
    assert row["license"] == "Apache-2.0" and "app_minimum" not in row
    assert "reviewed commit" in row["provenance_pending"] and "source_url" not in row


@pytest.mark.parametrize("active", [None, 1, 2])
@pytest.mark.parametrize("route", ["inspection", "__main__"])
def test_kerning_menu_when_real_world_then_capture_once(monkeypatch, active, route):
    import importlib

    from fontlab_fontport import application
    from fontlab_fontport.live import RFont
    from fontlab_fontport.memory import UFOBackend
    from ufoLib2 import Font

    app = importlib.import_module("fly.ap.fontui.kerning_proof")
    canonical = importlib.import_module("fontlabapp.fontui.kerning_proof")
    assert app.show is canonical.show and app.__all__ == ("show",)
    assert Path(app.__file__).name == "kerning_proof.py"
    backends = {identifier: UFOBackend(Font()) for identifier in (1, 2)}
    calls = []

    class Host:
        def __init__(self):
            calls.append("world")

        def font_ids(self):
            return [1, 2]

        def current_font_id(self):
            calls.append("current")
            return active

        def backend(self, identifier, *, owned):
            assert owned is False
            return backends[identifier]

    sentinel = object()

    def show(font):
        calls.append("show")
        assert font is None if active is None else isinstance(font, RFont) and font._backend is backends[active]
        return sentinel

    monkeypatch.setattr(application, "NativeApplication", Host)
    monkeypatch.setattr(app, "show", show)
    path = ROOT / "Scripts/Font UI Lab/Kerning Proof Workbench.py"
    namespace = runpy.run_path(str(path), run_name=route)
    if route == "inspection":
        assert not calls
        assert namespace["main"]() is sentinel
    assert calls == ["world", "current", "show"]
    assert not any(isinstance(node, (ast.Import, ast.ImportFrom)) for node in ast.parse(path.read_text()).body)


def test_kerning_menu_when_catalogued_then_exact_source_pending_native_and_provenance():
    rows = json.loads((ROOT / "additional-tools.json").read_text())
    row, = [row for row in rows if row["key"] == "font_ui_lab_kerning_proof"]
    assert row["destination"] == "Scripts/Font UI Lab/Kerning Proof Workbench.py"
    assert row["destination_sha256"] == hashlib.sha256((ROOT / row["destination"]).read_bytes()).hexdigest()
    assert row["app_api"] == "fontlabapp.fontui.kerning_proof.show"
    assert row["license"] == "Apache-2.0" and row["native_acceptance"] == "pending"
    assert not row["source_body_redistributed"] and not row["counted_in_130_sample_migration"]
    assert "app_minimum" not in row and "source_url" not in row
    assert "reviewed commit" in row["provenance_pending"]


@pytest.mark.parametrize("active", [None, 1, 2])
@pytest.mark.parametrize("route", ["inspection", "__main__"])
def test_groups_menu_when_real_world_then_capture_once(monkeypatch, active, route):
    import importlib

    from fontlab_fontport import application
    from fontlab_fontport.live import RFont
    from fontlab_fontport.memory import UFOBackend
    from ufoLib2 import Font

    app = importlib.import_module("fly.ap.fontui.kerning_groups")
    canonical = importlib.import_module("fontlabapp.fontui.kerning_groups")
    assert app.show is canonical.show and app.__all__ == ("show",)
    assert Path(app.__file__).name == "kerning_groups.py"
    backends = {identifier: UFOBackend(Font()) for identifier in (1, 2)}
    calls = []

    class Host:
        def __init__(self):
            calls.append("world")

        def font_ids(self):
            return [1, 2]

        def current_font_id(self):
            calls.append("current")
            return active

        def backend(self, identifier, *, owned):
            assert owned is False
            return backends[identifier]

    sentinel = object()

    def show(font):
        calls.append("show")
        assert font is None if active is None else isinstance(font, RFont) and font._backend is backends[active]
        return sentinel

    monkeypatch.setattr(application, "NativeApplication", Host)
    monkeypatch.setattr(app, "show", show)
    path = ROOT / "Scripts/Font UI Lab/Kerning Group Explorer.py"
    namespace = runpy.run_path(str(path), run_name=route)
    if route == "inspection":
        assert not calls
        assert namespace["main"]() is sentinel
    assert calls == ["world", "current", "show"]
    assert not any(isinstance(node, (ast.Import, ast.ImportFrom)) for node in ast.parse(path.read_text()).body)


def test_groups_menu_when_catalogued_then_exact_source_pending_native_and_provenance():
    rows = json.loads((ROOT / "additional-tools.json").read_text())
    row, = [row for row in rows if row["key"] == "font_ui_lab_kerning_groups"]
    assert row["destination"] == "Scripts/Font UI Lab/Kerning Group Explorer.py"
    assert row["destination_sha256"] == hashlib.sha256((ROOT / row["destination"]).read_bytes()).hexdigest()
    assert row["app_api"] == "fontlabapp.fontui.kerning_groups.show"
    assert row["license"] == "Apache-2.0" and row["native_acceptance"] == "pending"
    assert not row["source_body_redistributed"] and not row["counted_in_130_sample_migration"]
    assert "app_minimum" not in row and "source_url" not in row
    assert "reviewed commit" in row["provenance_pending"]


@pytest.mark.parametrize("active", [None, 1, 2])
@pytest.mark.parametrize("route", ["inspection", "__main__"])
def test_feature_menu_when_real_world_then_capture_once(monkeypatch, active, route):
    import importlib

    from fontlab_fontport import application
    from fontlab_fontport.live import RFont
    from fontlab_fontport.memory import UFOBackend
    from ufoLib2 import Font

    app = importlib.import_module("fly.ap.fontui.feature_proof")
    canonical = importlib.import_module("fontlabapp.fontui.feature_proof")
    assert app.show is canonical.show and app.__all__ == ["show"]
    assert Path(app.__file__).name == "feature_proof.py"
    backends = {identifier: UFOBackend(Font()) for identifier in (1, 2)}
    calls = []

    class Host:
        def __init__(self):
            calls.append("world")

        def font_ids(self):
            return [1, 2]

        def current_font_id(self):
            calls.append("current")
            return active

        def backend(self, identifier, *, owned):
            assert owned is False
            return backends[identifier]

    sentinel = object()

    def show(font):
        calls.append("show")
        assert font is None if active is None else isinstance(font, RFont) and font._backend is backends[active]
        return sentinel

    monkeypatch.setattr(application, "NativeApplication", Host)
    monkeypatch.setattr(app, "show", show)
    path = ROOT / "Scripts/Font UI Lab/Feature Source and Proof.py"
    namespace = runpy.run_path(str(path), run_name=route)
    if route == "inspection":
        assert not calls
        assert namespace["main"]() is sentinel
    assert calls == ["world", "current", "show"]
    assert not any(isinstance(node, (ast.Import, ast.ImportFrom)) for node in ast.parse(path.read_text()).body)


def test_feature_menu_when_catalogued_then_exact_source_pending_native_and_provenance():
    rows = json.loads((ROOT / "additional-tools.json").read_text())
    row, = [row for row in rows if row["key"] == "font_ui_lab_feature_proof"]
    assert row["destination"] == "Scripts/Font UI Lab/Feature Source and Proof.py"
    assert row["destination_sha256"] == hashlib.sha256((ROOT / row["destination"]).read_bytes()).hexdigest()
    assert row["app_api"] == "fontlabapp.fontui.feature_proof.show"
    assert row["license"] == "Apache-2.0" and row["native_acceptance"] == "pending"
    assert not row["source_body_redistributed"] and not row["counted_in_130_sample_migration"]
    assert "app_minimum" not in row and "source_url" not in row
    assert "reviewed commit" in row["provenance_pending"]
