# this_file: tests/test_reports.py
"""Exercise real migrated calculations and stale-state handling with owned data."""

import ast
import hashlib
import importlib.util
import json
import sys
from pathlib import Path
from types import SimpleNamespace as NS

import pytest
from conftest import original_source
from menu_layout import current_rows

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def load(monkeypatch):
    """Import report modules without loading FontLab or Qt binaries."""
    native = NS()
    state = NS(package=None, selections=[])

    def select(names, *, package_id):
        if state.package is None or state.package.id != package_id:
            raise ValueError("stale font")
        state.selections.append(names)
        return names

    def close_dialog(dialog, event, key, **owned):
        state.lifecycle = (dialog, event, key, owned)

    helpers = NS(
        connect_guarded=lambda *args: setattr(state, "connection", args),
        close_script_dialog=close_dialog,
        show_script_dialog=lambda *args: setattr(state, "shown", args),
        current_package=lambda: state.package,
        select_glyphs=select,
    )
    monkeypatch.setitem(
        sys.modules,
        "fly",
        NS(
            ap=NS(fontlab=native, scripting=helpers),
            qt=NS(QtCore=NS(), QtGui=NS(QDialog=object)),
        ),
    )
    monkeypatch.setitem(sys.modules, "fly.ap.scripting", helpers)

    def module(title):
        spec = importlib.util.spec_from_file_location(
            title, ROOT / "Scripts/Reports" / f"{title}.py"
        )
        result = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(result)
        return result

    return module, native, state


def test_manifest_when_distributed_then_hashes_and_menu_paths_match(request):
    entries = current_rows(ROOT)
    assert len(entries) == 69
    destinations = [entry["destination"] for entry in entries]
    assert len(set(destinations)) == 69
    additional = json.loads((ROOT / "additional-tools.json").read_text())
    extra_destinations = {entry["destination"] for entry in additional}
    assert len(extra_destinations) == len(additional) == 92
    for entry in additional:
        assert (
            hashlib.sha256((ROOT / entry["destination"]).read_bytes()).hexdigest()
            == entry["destination_sha256"]
        )
        assert entry["counted_in_130_sample_migration"] is False
    assert set(destinations).isdisjoint(extra_destinations)
    archive = json.loads((ROOT / "rescue-index.json").read_text())["menus"]
    archive_destinations = {row["menu"] for row in archive}
    candidates = {row["rescued_original_menu"] for row in additional if row.get("rescued_original_menu")}
    assert ((set(destinations) | extra_destinations) & archive_destinations) == candidates
    assert set(destinations) | extra_destinations == {
        str(p.relative_to(ROOT)) for p in (ROOT / "Scripts").rglob("*.py")
    }
    original_root = request.config.getoption("--original-source-root")
    for entry in entries:
        target = ROOT / entry["destination"]
        path = Path(entry["destination"])
        assert path.parts[0] == "Scripts" and len(path.parts) == 3
        assert path.parts[1] in {
            "Reports",
            "Font Info",
            "Features",
            "Names",
            "Kerning",
            "Proof",
            "Masters",
            "Metrics",
            "Outlines",
            "Contours",
            "Components",
            "Anchors",
            "Cleanup",
            "Guides",
        }
        assert path.suffix == ".py"
        assert len(entry["source_sha256"]) == 64
        assert set(entry["source_sha256"]) <= set("0123456789abcdef")
        assert entry["source"].startswith("fontlab-python-examples/_old/")
        assert ".." not in Path(entry["source"]).parts
        assert (
            hashlib.sha256(target.read_bytes()).hexdigest()
            == entry["destination_sha256"]
        )
        if original_root is not None:
            original = original_source(original_root, entry["source"])
            assert original.is_file(), f"Missing requested original: {original}"
            assert (
                hashlib.sha256(original.read_bytes()).hexdigest()
                == entry["source_sha256"]
            ), f"Original hash mismatch: {original}"
        source = target.read_text()
        ast.parse(source, feature_version=(3, 11))
        assert "from fly.ap.scripting import" in source
        assert "exec(" not in source
        assert entry["license"] == "Apache-2.0"


def test_calculations_when_multiple_masters_then_real_report_results(load):
    module, native, _state = load
    contour = NS(closed=False, nodes=lambda: [NS(x=0, y=0), NS(x=3, y=4)])
    empty = NS(getContours=list, shapes=[])
    drawn = NS(getContours=lambda: [contour], shapes=[])
    glyphs = {
        "A": NS(
            findLayer=lambda master: empty if master == "Bold" else drawn,
            mark=1,
            note="note",
        ),
        "space": NS(findLayer=lambda master: empty, mark=0, note=""),
    }
    package = NS(
        masters=["Regular", "Bold"],
        master="Regular",
        findName=glyphs.get,
        kerning=lambda master: [1],
    )
    native.CurrentFont = lambda: NS(
        glyphs=[NS(name="A", unicodes=[65]), NS(name="space", unicodes=[32])]
    )
    native.FontMetrics = lambda package, master: NS(
        ascender=800, capsHeight=700, xHeight=500, descender=-200
    )
    assert module("Empty Glyphs").scan(package, True) == [("A", ["Bold"])]
    assert module("Empty Glyphs").scan(package, False) == [
        ("A", ["Bold"]),
        ("space", ["Regular", "Bold"]),
    ]
    assert module("Open Contours").scan(package) == [("A", "Regular", 0, 2, 5.0)]
    cards, rows = module("Font Overview").overview(package)
    assert cards["Glyphs"] == 2 and cards["Empty on Regular"] == 1
    assert cards["Marked"] == cards["With notes"] == 1
    assert len(rows) == 2 and rows[0][-1] == 1


@pytest.mark.parametrize(
    "title,cls,method",
    [
        ("Empty Glyphs", "EmptyGlyphs", "rescan"),
        ("Open Contours", "OpenContours", "rescan"),
        ("Font Overview", "Overview", "refresh"),
    ],
)
def test_refresh_when_font_closed_then_clears_old_results(load, title, cls, method):
    module, _native, _state = load
    report = getattr(module(title), cls)
    obj = report.__new__(report)
    counts = []
    label = NS(setText=lambda value: None)
    obj.rows = [("old",)]
    obj.card_values = {"Glyphs": label}
    obj.table = NS(setRowCount=counts.append)
    obj.status = obj.subtitle = label
    obj.select_button = NS(setEnabled=lambda value: None)
    getattr(obj, method)()
    assert obj.rows == [] and counts == [0]
    if title == "Font Overview":
        assert obj.cards == {}
    else:
        assert obj.package_id is None


@pytest.mark.parametrize(
    "title,cls", [("Empty Glyphs", "EmptyGlyphs"), ("Open Contours", "OpenContours")]
)
def test_selection_when_font_changed_then_refuses_actual_module(load, title, cls):
    module, _native, state = load
    report = getattr(module(title), cls)
    obj = report.__new__(report)
    obj.rows, obj.package_id = [("A",)], 7
    state.package = NS(id=8)
    with pytest.raises(ValueError, match="stale font"):
        obj.select_rows([0])
    assert state.selections == []


@pytest.mark.parametrize(
    "title,cls", [("Empty Glyphs", "EmptyGlyphs"), ("Open Contours", "OpenContours")]
)
@pytest.mark.parametrize("failure", ["scan", "table"])
def test_refresh_when_scan_or_display_fails_then_refuses_selection(
    load, monkeypatch, title, cls, failure
):
    """A successful A snapshot must never become selectable in B on failure."""
    module, _native, state = load
    report_module = module(title)
    report = getattr(report_module, cls)
    obj = report.__new__(report)
    display = NS(fail=False, rows=[], enabled=False)
    label = NS(setText=lambda text: None)
    item = NS(setTextAlignment=lambda value: None, setForeground=lambda value: None)
    header = NS(setSectionResizeMode=lambda *args: None)

    def set_item(row, column, value):
        if display.fail:
            raise RuntimeError("owned table failure")
        display.rows.append((row, column))

    def set_count(count):
        if count == 0:
            display.rows.clear()

    obj.rows, obj.package_id = [], None
    obj.subtitle = obj.status = label
    obj.skip_whitespace = NS(isChecked=lambda: True)
    obj.select_button = NS(setEnabled=lambda value: setattr(display, "enabled", value))
    obj.table = NS(
        clear=lambda: display.rows.clear(),
        setColumnCount=lambda count: None,
        setHorizontalHeaderLabels=lambda labels: None,
        horizontalHeader=lambda: header,
        setRowCount=set_count,
        setItem=set_item,
    )
    report_module.QtGui = NS(
        QColor=lambda value: value,
        QBrush=lambda value: value,
        QHeaderView=NS(Stretch=1, ResizeToContents=2),
        QTableWidgetItem=lambda value: item,
    )
    report_module.QtCore = NS(Qt=NS(AlignCenter=1, AlignRight=2, AlignVCenter=4))
    monkeypatch.setattr(report_module, "muted", lambda widget: "grey")

    def scan(package, *args):
        if package.id == 8 and failure == "scan":
            raise RuntimeError("owned scan failure")
        return (
            [("A", ["Regular"])]
            if title == "Empty Glyphs"
            else [("A", "Regular", 0, 2, 5.0)]
        )

    monkeypatch.setattr(report_module, "scan", scan)
    state.package = NS(id=7, masters=["Regular"])
    obj.rescan()
    assert obj.package_id == 7 and obj.rows and display.enabled
    state.package = NS(id=8, masters=["Regular"])
    display.fail = failure == "table"
    with pytest.raises(RuntimeError, match=f"owned {failure} failure"):
        obj.rescan()
    with pytest.raises(ValueError, match="Refresh"):
        obj.select_rows([0])
    assert state.selections == [], "Failed B refresh must never select old A names in B"
    assert obj.package_id is None and not display.enabled
    assert obj.rows == [] and display.rows == []


@pytest.mark.parametrize(
    "title,cls",
    [
        ("Empty Glyphs", "EmptyGlyphs"),
        ("Open Contours", "OpenContours"),
        ("Font Overview", "Overview"),
        ("Glyph Table CSV", "GlyphTable"),
        ("Live Glyph Info", "GlyphInfoLive"),
        ("Label Statistics", "LabelStatistics"),
        ("Nodes Near Zones", "NodesNearZones"),
        ("Unicode Coverage", "Coverage"),
    ],
)
def test_lifecycle_when_report_called_then_delegates_exact_objects(load, title, cls):
    module, _native, state = load
    mod = module(title)
    dialog_type = getattr(mod, cls)
    obj = dialog_type.__new__(dialog_type)
    signal, slot = object(), object()
    obj._connect(signal, slot)
    assert state.connection == (obj, signal, slot), "Use shared guard unchanged"
    sentinel = object()

    def show(actual_type, key):
        assert (actual_type, key) == (dialog_type, mod.KEY)
        return sentinel

    mod.ap.scripting.show_script_dialog = show
    assert mod.main() is sentinel, "Return the actual shared dialog"
