# this_file: tests/test_report_batch2.py
"""Exercise migrated report calculations and invalidation using owned doubles."""

import csv
from types import SimpleNamespace as NS

import pytest
from test_reports import load as report_load


@pytest.fixture
def load(monkeypatch):
    """Reuse the owned native and Qt import fixture."""
    return report_load.__wrapped__(monkeypatch)


TITLES = [
    "Live Glyph Info",
    "Glyph Table CSV",
    "Label Statistics",
    "Nodes Near Zones",
    "Unicode Coverage",
]


@pytest.mark.parametrize("title", TITLES)
def test_migration_when_requested_then_executable_module_exists(title):
    from pathlib import Path

    assert (
        Path(__file__).parents[1] / "Scripts/Reports" / (title + ".py")
    ).is_file(), "Requested report must exist"


def test_calculations_when_owned_layers_then_preserve_real_values(load, tmp_path):
    module, native, _state = load
    box = NS(x=lambda: 10, y=lambda: -20, width=lambda: 400, height=lambda: 700)
    contour = NS(nodes=lambda: [1, 2, 3])
    layer = NS(
        boundingBox=box,
        advanceWidth=500,
        getContours=lambda: [contour],
        shapes=[NS(shapeData=NS(componentGlyph="acute"))],
        anchors=[1],
    )
    glyph = NS(findLayer=lambda master: layer, fgGlyph=NS(unicodes=[0x10400]))
    package = NS(
        masters=["Regular", "Bold"], master="Bold", findName=lambda name: glyph
    )
    assert module("Live Glyph Info").glyph_info(package, "A")[0][1] == [
        "500",
        "10",
        "90",
        "10, -20, 400, 700",
        "1",
        "3",
        "acute",
        "1",
    ]
    csvmod = module("Glyph Table CSV")
    header, rows = csvmod.table(package, ['A,"é'])
    path = tmp_path / "owned.csv"
    assert csvmod.write_csv(path, header, rows) == path.stat().st_size
    assert path.read_bytes().startswith(b"\xef\xbb\xbf")
    with path.open(encoding="utf-8-sig", newline="") as handle:
        saved = list(csv.reader(handle))
    assert saved[1] == ['A,"é', "10400", "500", "500", "1", "acute"]
    labels = module("Label Statistics")
    assert labels.statistics([("a.sc", 89), ("b.sc", 89), (".notdef", 0)])[1] == [
        (".sc", ["a.sc", "b.sc"]),
        ("", [".notdef"]),
    ]
    zones = module("Nodes Near Zones")
    assert zones.near_misses([(1, 700), (2, 698), (3, 695)], [("cap", 700)], 2) == [
        ("cap", 700, 2, 698)
    ]
    coverage = module("Unicode Coverage")
    native.CurrentFont = lambda: NS(
        glyphs=[
            NS(name="A", unicodes=[65]),
            NS(name="dup", unicodes=[65]),
            NS(name="smile", unicodes=[0x1F600]),
        ]
    )
    assert coverage.font_codes() == {65: "A", 0x1F600: "smile"}
    rows, outside = coverage.coverage([65, 0x1F600, 0x20000])
    assert sum(r[3] for r in rows) == 2 and outside == [0x20000]


@pytest.mark.parametrize(
    "title,cls,method",
    [
        ("Label Statistics", "LabelStatistics", "select_group"),
        ("Nodes Near Zones", "NodesNearZones", "select_rows"),
        ("Unicode Coverage", "Coverage", "select_block"),
    ],
)
def test_selection_when_snapshot_missing_or_font_changed_then_refused(
    load, title, cls, method
):
    module, _native, state = load
    obj = getattr(module(title), cls).__new__(getattr(module(title), cls))
    obj.package_id = None
    with pytest.raises(ValueError, match="Refresh"):
        getattr(obj, method)([], 0) if method == "select_group" else getattr(
            obj, method
        )(0)
    obj.package_id = 7
    state.package = NS(id=8)
    with pytest.raises(ValueError, match="stale font"):
        getattr(obj, method)(
            [("x", ["A"])], 0
        ) if method == "select_group" else getattr(obj, method)(
            [0] if method == "select_rows" else 0
        )


class Widget:
    """Owned minimal UI surface with deterministic display failures."""

    def __init__(self):
        self.count = 0
        self.fail = False
        self.text = ""
        self.currentIndex = 0
        self.value = 4

    def __getattr__(self, name):
        return lambda *a: None

    def setRowCount(self, count):
        self.count = count

    def isChecked(self):
        return False

    def setItem(self, *args):
        if self.fail:
            raise RuntimeError("owned display failure")

    def horizontalHeader(self):
        return self

    def setText(self, text):
        self.text = text


CASES = [
    ("Live Glyph Info", "GlyphInfoLive", "refresh"),
    ("Glyph Table CSV", "GlyphTable", "refresh"),
    ("Label Statistics", "LabelStatistics", "refresh"),
    ("Nodes Near Zones", "NodesNearZones", "rescan"),
    ("Unicode Coverage", "Coverage", "refresh"),
]


@pytest.mark.parametrize("title,cls,method", CASES)
@pytest.mark.parametrize("failure", ["none", "scan", "display", "success"])
def test_refresh_when_missing_font_or_failure_then_invalidates_all_data(
    load, monkeypatch, title, cls, method, failure
):
    module, native, state = load
    mod = module(title)
    obj = getattr(mod, cls).__new__(getattr(mod, cls))
    for name in [
        "table",
        "mark_table",
        "suffix_table",
        "subtitle",
        "status",
        "glyph_label",
        "scope",
        "tolerance",
        "select_button",
        "copy_button",
        "export_button",
        "path",
        "show_all",
    ]:
        setattr(obj, name, Widget())
    obj.palette = NS(color=lambda *a: "blue")
    obj.package_id = 7
    obj.rows = [("old",)]
    obj.marks = obj.suffixes = [("old", ["A"])]
    obj.codes = {65: "A"}
    obj.header = ["old"]
    obj.shown_name = "A"
    obj.outside = [1]
    state.package = (
        None
        if failure == "none"
        else NS(
            id=8,
            masters=["Regular"],
            master="Regular",
            findName=lambda name: NS(fgGlyph=NS(unicodes=[65])),
        )
    )
    native.CurrentFont = lambda: NS(glyphs=[NS(name="A", mark=89, unicodes=[65])])
    item = Widget()
    mod.QtGui = NS(
        QColor=lambda *a: "blue",
        QBrush=lambda *a: None,
        QPalette=NS(Link=1),
        QTableWidgetItem=lambda *a: item,
        QProgressBar=Widget,
        QHeaderView=NS(Stretch=1, ResizeToContents=2),
    )
    mod.QtCore = NS(
        Qt=NS(AlignRight=1, AlignVCenter=2, DisplayRole=3),
        QTime=NS(currentTime=lambda: NS(toString=lambda *a: "now")),
    )
    monkeypatch.setattr(mod, "muted", lambda *a: "grey")
    if hasattr(mod, "selected_names"):
        monkeypatch.setattr(mod, "selected_names", lambda: ["A"])
    if hasattr(mod, "focused_name"):
        monkeypatch.setattr(mod, "focused_name", lambda: "A")
    calculations = {
        "Live Glyph Info": ("glyph_info", [("Regular", ["500"] * 8)]),
        "Glyph Table CSV": ("table", (["glyph"], [["A"]])),
        "Label Statistics": ("statistics", ([(89, ["A"])], [("", ["A"])])),
        "Nodes Near Zones": ("scan", [("A", "Regular", "cap", 700, 0, 698)]),
        "Unicode Coverage": ("coverage", ([(0, 127, "Basic Latin", 1, 128)], [])),
    }
    calc, result = calculations[title]

    def calculate(*args):
        if failure == "scan":
            raise RuntimeError("owned scan failure")
        return result

    monkeypatch.setattr(mod, calc, calculate)
    if title == "Label Statistics":
        monkeypatch.setattr(mod, "swatch", lambda *a: None)
    if failure == "display":
        obj.table.fail = obj.mark_table.fail = True
    if failure in {"none", "success"}:
        getattr(obj, method)()
    else:
        with pytest.raises(RuntimeError, match=f"owned {failure} failure"):
            getattr(obj, method)()
    if failure == "success":
        assert obj.package_id == 8, "Completed display publishes the current font id"
        return
    assert obj.package_id is None, "Failed snapshots must stay unselectable"
    if title == "Label Statistics":
        assert (
            obj.marks == obj.suffixes == []
            and obj.mark_table.count == obj.suffix_table.count == 0
        )
    else:
        assert obj.rows == [] and obj.table.count == 0
    if title == "Unicode Coverage":
        assert obj.codes == {} and obj.outside == []


def test_add_selection_when_same_font_then_preserves_prior_names(load, monkeypatch):
    module, _native, state = load
    mod = module("Label Statistics")
    obj = mod.LabelStatistics.__new__(mod.LabelStatistics)
    obj.package_id = 7
    obj.add = NS(isChecked=lambda: True)
    obj.status = Widget()
    state.package = NS(id=7)
    monkeypatch.setattr(mod, "selected_names", lambda: ["existing"])
    obj.select_group([(".sc", ["a.sc"])], 0)
    assert state.selections == [["existing", "a.sc"]], (
        "Add must retain the existing current-font selection"
    )


@pytest.mark.parametrize("title,cls,method", CASES)
def test_close_when_owned_signals_then_disconnects_and_stops_timer(
    load, title, cls, method
):
    module, _native, _state = load
    mod = module(title)
    obj = getattr(mod, cls).__new__(getattr(mod, cls))
    calls = []
    slot = lambda: None
    obj._connections = [(NS(disconnect=lambda s: calls.append(s)), slot)]
    obj.timer = NS(stop=lambda: calls.append("stop"))
    obj.chooser = None
    mod.QtGui = NS(QDialog=NS(closeEvent=lambda *a: None))
    obj.closeEvent(None)
    assert slot in calls and obj._connections == [], (
        "Every owned signal must disconnect"
    )
    assert ("stop" in calls) == (title == "Live Glyph Info"), (
        "Live timer stops at close"
    )


def test_zone_scan_when_transformed_oncurves_then_checks_all_masters(load):
    module, native, _state = load
    mod = module("Nodes Near Zones")
    mod.QtCore = NS(QPointF=lambda x, y: NS(x=lambda: x, y=lambda: y))
    native.FontMetrics = lambda package, master: NS(
        xHeight=500, capsHeight=700, ascender=800, descender=-200
    )
    transform = NS(map=lambda p: NS(x=lambda: p.x() + 10, y=lambda: p.y() + 2))
    contour = NS(
        nodes=lambda: [
            NS(x=5, y=696, isOn=lambda: True),
            NS(x=0, y=698, isOn=lambda: False),
        ]
    )
    shape = NS(shapeData=None, transform=transform, getContours=lambda: [contour])
    component = NS(shapeData=NS(componentGlyph="base"))
    layer = NS(shapes=[shape, component])
    package = NS(
        masters=["Regular", "Bold"],
        findName=lambda name: (
            NS(findLayer=lambda master: layer) if name == "A" else None
        ),
    )
    assert mod.scan(package, ["missing", "A"], 2) == [
        ("A", "Regular", "cap height", 700, 15, 698),
        ("A", "Bold", "cap height", 700, 15, 698),
    ], "Only own transformed on-curves must contribute across all masters"
