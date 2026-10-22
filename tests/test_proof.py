# this_file: tests/test_proof.py
"""Portable tests of the actual Proof menu interfaces and shared outlines."""

from pathlib import Path
from typing import ClassVar

import pytest
from conftest import original_source

ROOT = Path(__file__).parents[1]
TITLES = ["Glyph Grid", "Text By Master", "Waterfall", "Word Finder"]


@pytest.mark.parametrize("title", TITLES)
def test_actual_proof_completion_runs_existing_full_cleanup(load, monkeypatch, title):
    monkeypatch.setattr(sys, "_fontlab_samples", {}, raising=False)
    module = load.module(title)
    dialog = module.main()
    dialog.finished.emit()
    assert dialog.deleted and not dialog._connections, (
        "Completion must run the full owned Close path"
    )
    assert dialog.package is None and dialog._bound_id is None, (
        "Release captured source bindings"
    )
    assert not sys._fontlab_samples, "Remove only the completed owner"


@pytest.mark.parametrize("title", TITLES)
def test_requested_proof_menu_exists(title):
    assert (ROOT / "Scripts/Proof" / (title + ".py")).is_file(), (
        "Complete Proof menu missing"
    )


import importlib.util
import sys
from types import SimpleNamespace as NS


class Signal:
    def __init__(self):
        self.slots = []

    def connect(self, slot):
        self.slots.append(slot)

    def disconnect(self, slot):
        self.slots.remove(slot)

    def emit(self):
        for slot in list(self.slots):
            slot()


class Widget:
    """Owned PythonQt-shaped controls, executing the real menu constructors/slots."""

    instances: ClassVar[list] = []

    def __init__(self, *args):
        self.instances.append(self)
        self.text = args[0] if args and isinstance(args[0], str) else ""
        self.value, self.currentIndex, self.width, self.height = 0, 0, 720, 600
        self.items, self.enabled, self.closed, self.deleted = [], True, False, False
        self.range, self.readonly, self.blocked = None, False, False
        self.font = NS(
            pointSizeF=lambda: 12, setPointSizeF=lambda n: None, setBold=lambda b: None
        )
        self.palette = NS(color=lambda role: Color(), setColor=lambda *a: None)
        for name in [
            "clicked",
            "textChanged",
            "valueChanged",
            "currentIndexChanged",
            "finished",
            "destroyed",
        ]:
            setattr(self, name, Signal())

    def __getattr__(self, name):
        if name.startswith("set") or name in [
            "addWidget",
            "addLayout",
            "addStretch",
            "update",
            "show",
            "raise_",
        ]:
            return lambda *args: None
        raise AttributeError(name)

    @property
    def currentText(self):
        return self.items[self.currentIndex] if self.items else ""

    def addItem(self, value):
        self.items.append(value)

    def setCurrentIndex(self, value):
        self.currentIndex = value
        if not self.blocked:
            self.currentIndexChanged.emit()

    def blockSignals(self, value):
        previous, self.blocked = self.blocked, value
        return previous

    def clear(self):
        self.items, self.currentIndex, self.text = [], 0, ""
        if not self.blocked:
            self.currentIndexChanged.emit()

    def setText(self, value):
        self.text = value
        self.textChanged.emit()

    def setPlainText(self, value):
        self.text = value

    def setValue(self, value):
        self.value = value
        self.valueChanged.emit()

    def setRange(self, low, high):
        self.range = (low, high)

    def setReadOnly(self, value):
        self.readonly = value

    def setEnabled(self, value):
        self.enabled = value

    def resize(self, width, height):
        self.width, self.height = width, height

    def close(self):
        self.closed = True
        self.closeEvent(None)

    def closeEvent(self, event):
        pass

    def deleteLater(self):
        self.deleted = True


class Color:
    HexArgb = 1

    def __init__(self, *args):
        pass

    def setAlpha(self, value):
        pass

    def name(self, *args):
        return "#202020"


class Box:
    def __init__(self, *values):
        self.values = values

    def left(self):
        return self.values[0]

    def top(self):
        return self.values[1]

    def right(self):
        return self.values[0] + self.values[2]

    def bottom(self):
        return self.values[1] + self.values[3]


class Painter:
    Antialiasing = 1

    def __init__(self):
        self.calls = []

    def __getattr__(self, name):
        return lambda *args: self.calls.append((name, args))


@pytest.fixture
def load(monkeypatch, app_sources):
    monkeypatch.setattr(Widget, "instances", [])
    state = NS(package=None, glyphs=[], selected=set(), fallback=None, copied=[])
    frame = NS(inherits=lambda name: name == "YFrameWindow")
    tab = NS(inherits=lambda name: name == "QTabWidget", parentWidget=lambda: frame)
    stack = NS(inherits=lambda name: name == "QStackedWidget", parentWidget=lambda: tab)
    state.font_panel = NS(
        inherits=lambda name: name == "FontWindow", parentWidget=lambda: stack
    )
    native = NS(
        flWorkspace=NS(
            instance=lambda: NS(
                currentPackage=state.package, activeFontPanel=state.font_panel
            )
        ),
        CurrentFont=lambda: NS(glyphs=state.glyphs) if state.package else None,
        CurrentGlyph=lambda: state.fallback,
        MainWindow=lambda: None,
    )
    fl = NS(font=state.glyphs, Selected=lambda i: i in state.selected)
    gui = NS(
        **{
            name: Widget
            for name in [
                "QDialog",
                "QWidget",
                "QVBoxLayout",
                "QHBoxLayout",
                "QGridLayout",
                "QLabel",
                "QLineEdit",
                "QSlider",
                "QComboBox",
                "QSpinBox",
                "QPlainTextEdit",
                "QPushButton",
                "QScrollArea",
            ]
        }
    )
    gui.QColor = Color
    gui.QPalette = NS(Text=1, WindowText=2, Base=3)
    gui.QFrame = NS(NoFrame=0)
    gui.QBrush = lambda *args: args
    gui.QPen = lambda *args: args
    gui.QApplication = NS(clipboard=lambda: NS(setText=state.copied.append))
    painter = Painter()
    gui.QPainter = lambda owner: painter
    core = NS(
        Qt=NS(
            Horizontal=1,
            AlignCenter=2,
            AlignRight=4,
            AlignVCenter=8,
            AlignLeft=16,
            AlignBottom=32,
            ScrollBarAlwaysOff=0,
        ),
        QRectF=Box,
        QPointF=lambda *args: args,
    )
    qt = NS(QtCore=core, QtGui=gui)
    natives = {"fontlab": native, "PythonQt": qt, "FL": NS(fl=fl)}
    monkeypatch.setitem(sys.modules, "fontlabapp", NS(_native=natives.__getitem__))
    modules = {}
    for name in [
        "scripting",
        "proof",
        "_names_dialog",
        "_proof_dialog",
        "_proof_views",
    ]:
        spec = importlib.util.spec_from_file_location(
            "fontlabapp." + name, app_sources / (name + ".py")
        )
        module = importlib.util.module_from_spec(spec)
        monkeypatch.setitem(sys.modules, "fontlabapp." + name, module)
        spec.loader.exec_module(module)
        modules[name] = module
    api = modules["scripting"]
    monkeypatch.setitem(
        sys.modules, "fly", NS(ap=NS(fontlab=native, scripting=api), qt=qt)
    )
    monkeypatch.setitem(sys.modules, "fly.ap.scripting", api)

    def module(title):
        spec = importlib.util.spec_from_file_location(
            title, ROOT / "Scripts/Proof" / (title + ".py")
        )
        result = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(result)
        return result

    def font():
        widths = {"A": (500, 700), "space": (200, 250), "alternate": (300, 450)}
        glyphs = {}
        for name, advances in widths.items():
            glyphs[name] = NS(
                name=name,
                isNull=False,
                unicodes={"A": [65], "space": [32], "alternate": []}[name],
                findLayer=lambda master, a=advances: NS(
                    isNull=False,
                    path=NS(
                        isEmpty=lambda: False,
                        boundingRect=lambda: Box(-40, -300, 900, 1400),
                    ),
                    advanceWidth=a[["Light", "Bold"].index(master)],
                ),
            )
        state.glyphs[:] = list(glyphs.values())
        state.package = NS(
            id=7,
            isNull=False,
            masters=["Light", "Bold"],
            master="Bold",
            upm=1000,
            ascender_value=800,
            descender_value=-200,
            findName=glyphs.get,
        )
        modules["proof"].layer_path = lambda layer: layer.path
        return state.package

    return NS(
        module=module, state=state, modules=modules, qt=qt, painter=painter, font=font
    )


@pytest.mark.parametrize(
    "title,cls",
    [
        ("Glyph Grid", "GlyphGrid"),
        ("Text By Master", "TextByMaster"),
        ("Waterfall", "Waterfall"),
        ("Word Finder", "WordFinder"),
    ],
)
def test_actual_constructor_preserves_no_font_controls_owned_close_and_registry(
    load, monkeypatch, title, cls
):
    module = load.module(title)
    dialog = getattr(module, cls)()
    assert "Open a font" in dialog.subtitle.text
    assert dialog._connections, "Original controls must connect guarded real callbacks"
    monkeypatch.setattr(sys, "_fontlab_samples", {module.KEY: dialog}, raising=False)
    dialog.close_button.clicked.emit()
    assert not dialog._connections and dialog.deleted and dialog.closed
    assert sys._fontlab_samples == {}
    for name in ["grid", "view"]:
        if hasattr(dialog, name):
            assert getattr(dialog, name).on_error is None
            assert getattr(dialog, name).before_draw is None


def test_grid_selection_font_order_fallback_zoom_reload_and_common_frame(load):
    load.font()
    load.state.selected = {2, 0}
    module = load.module("Glyph Grid")
    dialog = module.GlyphGrid()
    assert [g.name for g in dialog.glyphs] == ["A", "alternate"]
    assert dialog.masters == ["Light", "Bold"]
    assert dialog.zoom.range == (48, 240) and dialog.zoom.value == 110
    assert dialog.grid.frame == (-300, 1100)
    assert [r[2] for r in dialog.grid.cells[0][1]] == [500, 700]
    dialog.zoom.setValue(70)
    assert dialog.grid.cell == 70 and dialog.zoom_label.text == "70 px"
    load.state.selected = set()
    load.state.fallback = load.state.glyphs[1]
    dialog.reload_button.clicked.emit()
    assert [g.name for g in dialog.glyphs] == ["space"]
    load.state.fallback = None
    dialog.reload_button.clicked.emit()
    assert dialog.grid.cells == [] and "Select glyphs" in dialog.subtitle.text


def test_text_masters_use_exact_advances_slash_slots_and_size_controls(load):
    load.font()
    module = load.module("Text By Master")
    dialog = module.TextByMaster()
    assert dialog.text.text == "Hamburgefonstiv"
    assert dialog.size_slider.range == (12, 160) and dialog.size_slider.value == 48
    dialog.text.setText("AA/alternate Ł")
    assert [(m, w) for m, _, w in dialog.rows] == [("Light", 1800), ("Bold", 2350)]
    assert dialog.rows[0][1][-1] == (None, 500)
    dialog.size_slider.setValue(28)
    assert dialog.view.px_size == 28 and dialog.size_label.text == "28 px"
    assert dialog.package.master == "Bold", "Read-only proof must not set active master"


def test_waterfall_master_missing_boxes_sizes_and_advance_only_line(load):
    load.font()
    dialog = load.module("Waterfall").Waterfall()
    assert dialog.master.currentText == "Bold"
    assert dialog.text.text == "Hamburgefonstiv 0123"
    assert dialog.sizes.text == "10 12 14 18 24 32 48 64 96"
    dialog.text.setText("AA/alternate Ł")
    assert dialog.glyph_names == ["A", "A", "alternate", None]
    assert dialog.view.width_units == 2350
    dialog.master.setCurrentIndex(0)
    assert dialog.view.width_units == 1800
    dialog.sizes.setText("4 16, 400 nan 401 3")
    assert dialog.view.sizes == [4, 16, 400]
    assert dialog.package.master == "Bold"


def test_word_finder_exact_filters_case_controls_and_host_free_copy(load):
    load.font()
    load.state.glyphs[:] = [
        NS(name="letters", unicodes=list(range(65, 91)) + list(range(97, 123)))
    ]
    module = load.module("Word Finder")
    dialog = module.WordFinder()
    assert dialog.min_len.range == (1, 20) and dialog.min_len.value == 3
    assert dialog.max_len.range == (1, 20) and dialog.max_len.value == 12
    assert dialog.result_view.readonly
    dialog.must.setText("z")
    assert dialog.words and all("z" in word for word in dialog.words)
    dialog.must.setText("")
    dialog.only.setText("hamburgefonstiv")
    assert len(dialog.words) > 5 and all(
        set(w) <= set("hamburgefonstiv") for w in dialog.words
    )
    dialog.case.setCurrentIndex(2)
    assert all(w == w.upper() for w in dialog.words)
    dialog.copy_button.clicked.emit()
    assert load.state.copied == [" ".join(dialog.words)]
    dialog.min_len.setValue(20)
    dialog.max_len.setValue(1)
    assert dialog.words == [] and not dialog.copy_button.enabled


@pytest.mark.parametrize(
    "title,cls,signal",
    [
        ("Glyph Grid", "GlyphGrid", "zoom"),
        ("Text By Master", "TextByMaster", "size_slider"),
        ("Waterfall", "Waterfall", "text"),
        ("Word Finder", "WordFinder", "must"),
    ],
)
@pytest.mark.parametrize("closed", [False, True])
def test_actual_refresh_callback_rejects_switched_closed_before_wrapper_read(
    load, title, cls, signal, closed
):
    package = load.font()
    load.state.selected = {0}
    dialog = getattr(load.module(title), cls)()
    load.state.package = None if closed else NS(id=8, isNull=False)
    # Any dereference of a stale wrapper must fail this test independently.
    package.findName = lambda name: pytest.fail("Dereferenced stale font")
    getattr(dialog, signal).setText("A") if signal in ["text", "must"] else getattr(
        dialog, signal
    ).setValue(24)
    assert "original font" in dialog.slot_error
    assert not dialog._snapshot_valid
    if hasattr(dialog, "view"):
        assert (
            getattr(dialog.view, "rows", []) == []
            and getattr(dialog.view, "run", []) == []
        )
    if hasattr(dialog, "grid"):
        assert dialog.grid.cells == []
    if hasattr(dialog, "words"):
        assert dialog.words == [] and not dialog.copy_button.enabled
    assert load.state.copied == []


def test_grid_explicit_reload_rebinds_font_or_clears_for_no_font(load):
    load.font()
    load.state.selected = {0}
    dialog = load.module("Glyph Grid").GlyphGrid()
    second = load.font()
    second.id = 9
    dialog.reload_button.clicked.emit()
    assert dialog.package is second and dialog._bound_id == 9 and dialog.grid.cells
    load.state.package = None
    load.state.glyphs.clear()
    dialog.reload_button.clicked.emit()
    assert dialog.package is None and dialog.grid.cells == []
    assert "Open a font" in dialog.subtitle.text


def test_partial_outline_scan_failure_clears_existing_preview_and_can_retry(load):
    package = load.font()
    dialog = load.module("Text By Master").TextByMaster()
    dialog.text.setText("A")
    assert dialog.view.rows
    actual = package.findName
    package.findName = lambda name: (_ for _ in ()).throw(
        RuntimeError("native read failed")
    )
    dialog.size_slider.setValue(40)
    assert "native read failed" in dialog.slot_error
    assert dialog.rows == [] and dialog.view.rows == []
    package.findName = actual
    dialog.size_slider.setValue(48)
    assert dialog.rows and dialog._snapshot_valid


@pytest.mark.parametrize(
    "title,cls,view",
    [
        ("Glyph Grid", "GlyphGrid", "grid"),
        ("Text By Master", "TextByMaster", "view"),
        ("Waterfall", "Waterfall", "view"),
    ],
)
def test_actual_views_draw_real_cached_paths_and_finalize_painter(
    load, title, cls, view
):
    load.font()
    load.state.selected = {0}
    load.qt.QtGui.QPainter.Antialiasing = 1
    dialog = getattr(load.module(title), cls)()
    if hasattr(getattr(dialog, "text", None), "setText"):
        dialog.text.setText("AŁ")
    canvas = getattr(dialog, view)
    canvas.paintEvent(None)
    assert canvas.paint_error == ""
    fills = [args[0] for name, args in load.painter.calls if name == "fillPath"]
    assert fills and all(hasattr(path, "boundingRect") for path in fills)
    assert load.painter.calls[-1][0] == "end"
    if title != "Glyph Grid":
        assert any(name == "drawRect" for name, _ in load.painter.calls), (
            "Missing-glyph box omitted"
        )
    else:
        assert canvas.painted == 2


@pytest.mark.parametrize("failure", ["draw", "hook", "end", "create"])
def test_paint_boundary_contains_draw_hook_constructor_and_end_failures(load, failure):
    load.font()
    load.state.selected = {0}
    dialog = load.module("Glyph Grid").GlyphGrid()
    view = dialog.grid
    view.draw = lambda painter: (_ for _ in ()).throw(RuntimeError("draw failed"))
    if failure == "hook":
        view.on_error = lambda error: (_ for _ in ()).throw(RuntimeError("hook failed"))
    if failure == "end":
        load.painter.end = lambda: (_ for _ in ()).throw(RuntimeError("end failed"))
    if failure == "create":
        load.qt.QtGui.QPainter = lambda owner: (_ for _ in ()).throw(
            RuntimeError("create failed")
        )
    view.paintEvent(None)
    assert failure in view.paint_error
    if failure in ["draw", "hook"]:
        assert load.painter.calls[-1][0] == "end"
    if failure != "hook":
        assert view.cells == [] and not dialog._snapshot_valid


def test_stale_paint_and_copy_never_access_font_or_clipboard(load):
    load.font()
    dialog = load.module("Waterfall").Waterfall()
    dialog.text.setText("A")
    load.state.package = None
    dialog.view.paintEvent(None)
    assert "original font" in dialog.view.paint_error and dialog.view.run == []
    assert load.painter.calls == [], "Stale paint must fail before a painter is created"
    load.font()
    word = load.module("Word Finder").WordFinder()
    load.state.package = NS(id=9, isNull=False)
    word.copy_button.clicked.emit()
    assert "original font" in word.slot_error and load.state.copied == []


def test_scenario_globals_and_shared_lifecycle_remain_real_interfaces(load):
    for title, cls in zip(
        TITLES, ["GlyphGrid", "TextByMaster", "Waterfall", "WordFinder"]
    ):
        module = load.module(title)
        klass = getattr(module, cls)
        assert klass._connect is load.modules["_names_dialog"].NamesDialog._connect
        assert klass.closeEvent is load.modules["_proof_dialog"].ProofDialog.closeEvent
        global_name = "WORDS" if title == "Word Finder" else "layer_path"
        assert global_name in klass.__init__.__globals__
        assert (
            module.KEY
            == "proof_"
            + {
                "Glyph Grid": "glyph_grid",
                "Text By Master": "text_by_master",
                "Waterfall": "waterfall",
                "Word Finder": "word_finder",
            }[title]
        )


def test_opening_read_failure_keeps_closable_empty_diagnosed_panel(load):
    load.font()
    module = load.module("Text By Master")
    module.glyph_run = lambda *args: (_ for _ in ()).throw(
        RuntimeError("opening scan failed")
    )
    dialog = module.TextByMaster()
    assert "opening scan failed" in dialog.status.text
    assert dialog.rows == [] and dialog.view.rows == [] and not dialog._snapshot_valid
    dialog.close_button.clicked.emit()
    assert dialog.deleted and not dialog._connections


def test_no_font_copy_is_refused_even_if_called_directly(load):
    dialog = load.module("Word Finder").WordFinder()
    with pytest.raises(ValueError, match="incomplete"):
        dialog.copy()
    assert load.state.copied == [] and not dialog.copy_button.enabled


def test_real_main_replaces_registry_entry_and_shows_owned_dialog(load, monkeypatch):
    monkeypatch.setattr(sys, "_fontlab_samples", {}, raising=False)
    module = load.module("Waterfall")
    first = module.main()
    second = module.main()
    assert first.closed and first.deleted
    assert sys._fontlab_samples[module.KEY] is second
    assert not first._connections and second._connections
    second.close_button.clicked.emit()
    assert sys._fontlab_samples == {}


def test_font_switch_during_scan_clears_complete_looking_results(load):
    package = load.font()
    dialog = load.module("Text By Master").TextByMaster()
    actual = package.findName

    def switch(name):
        load.state.package = NS(id=9, isNull=False)
        return actual(name)

    package.findName = switch
    dialog.text.setText("A")
    assert "original font" in dialog.slot_error
    assert not dialog._snapshot_valid and dialog.rows == [] and dialog.view.rows == []


def test_original_embedded_words_and_public_defaults_match_strict_sources(
    load, request
):
    source_root = request.config.getoption("--original-source-root")
    if source_root is None:
        pytest.skip("Original source-byte audit requires --original-source-root")
    import ast

    for title, stem in zip(
        TITLES,
        [
            "proof_glyph_grid",
            "proof_text_by_master",
            "proof_waterfall",
            "proof_word_finder",
        ],
    ):
        source = original_source(
            source_root,
            "fontlab-python-examples/_old/part4/fontlab-samples/samples/"
            + stem
            + ".py",
        )
        tree = ast.parse(source.read_text())
        module = load.module(title)
        for node in tree.body:
            if isinstance(node, ast.Assign) and node.targets[0].id in {
                "TITLE",
                "KEY",
                "DEFAULT_TEXT",
                "DEFAULT_SIZES",
                "ENGLISH",
                "LATIN",
                "CASES",
            }:
                assert getattr(module, node.targets[0].id) == ast.literal_eval(
                    node.value
                ), "Original public default changed"


@pytest.mark.parametrize("failure", ["inactive", "end_false"])
def test_painter_refuses_inactive_device_and_failed_end(load, failure):
    load.font()
    load.state.selected = {0}
    load.qt.QtGui.QPainter.Antialiasing = 1
    dialog = load.module("Glyph Grid").GlyphGrid()
    if failure == "inactive":
        load.painter.isActive = lambda: False
    else:
        load.painter.end = lambda: False
    dialog.grid.paintEvent(None)
    assert dialog.grid.paint_error, "A failed paint device must not publish success"
    assert dialog.grid.cells == [] and not dialog._snapshot_valid


EARLY_READS = [
    (title, klass, stage)
    for title, klass in zip(
        TITLES, ["GlyphGrid", "TextByMaster", "Waterfall", "WordFinder"]
    )
    for stage in ["binding", "identity"]
] + [
    ("Glyph Grid", "GlyphGrid", "selection"),
    ("Glyph Grid", "GlyphGrid", "masters"),
    ("Text By Master", "TextByMaster", "maps"),
    ("Waterfall", "Waterfall", "maps"),
    ("Waterfall", "Waterfall", "masters"),
    ("Waterfall", "Waterfall", "active-master"),
    ("Word Finder", "WordFinder", "characters"),
]


@pytest.mark.parametrize("title,klass,stage", EARLY_READS)
def test_complete_constructor_contains_early_reads_then_recovers_and_closes(
    load, monkeypatch, title, klass, stage
):
    package = load.font()
    load.state.selected = {0}
    module = load.module(title)
    monkeypatch.setattr(sys, "_fontlab_samples", {}, raising=False)

    def fail(*args):
        panels = [w for w in Widget.instances if isinstance(w, getattr(module, klass))]
        assert panels and hasattr(panels[-1], "close_button"), (
            "Native read ran before Close exists"
        )
        assert hasattr(panels[-1], "status"), "Native read ran before status exists"
        raise RuntimeError("early " + stage + " read failed")

    class BrokenPackage:
        def __getattr__(self, name):
            field = {
                "identity": "id",
                "masters": "masters",
                "active-master": "master",
            }.get(stage)
            return fail() if name == field else getattr(package, name)

    with monkeypatch.context() as broken:
        if stage == "binding":
            broken.setattr(load.modules["_proof_dialog"], "current_package", fail)
        elif stage in {"identity", "masters", "active-master"}:
            load.state.package = BrokenPackage()
        else:
            field = {
                "selection": "selected_glyphs",
                "maps": "font_maps",
                "characters": "font_chars",
            }[stage]
            broken.setattr(module, field, fail)
        dialog = module.main()  # Real constructor + real registry publication.
        assert sys._fontlab_samples[module.KEY] is dialog
        assert "early " + stage + " read failed" in dialog.status.text
        assert not dialog._snapshot_valid
        assert dialog._connections and dialog.close_button
        if hasattr(dialog, "grid"):
            assert dialog.grid.cells == []
        if hasattr(dialog, "view"):
            assert (
                getattr(dialog.view, "rows", []) == []
                and getattr(dialog.view, "run", []) == []
            )
        if hasattr(dialog, "copy_button"):
            assert not dialog.copy_button.enabled and dialog.words == []
        assert load.state.copied == []
    load.state.package = package
    control = {
        "Glyph Grid": "zoom",
        "Text By Master": "size_slider",
        "Waterfall": "text",
        "Word Finder": "must",
    }[title]
    if control in {"text", "must"}:
        getattr(dialog, control).setText("A" if control == "text" else "")
    else:
        getattr(dialog, control).setValue(40)
    assert dialog._snapshot_valid, (
        "Original bound font must recover through the actual guarded control"
    )
    if title == "Waterfall":
        assert dialog.master.items == ["Light", "Bold"]
        assert dialog.master.currentText == "Bold", (
            "Recovery lost original active-master default"
        )
    dialog.close_button.clicked.emit()
    assert dialog.deleted and dialog.closed and not dialog._connections
    assert sys._fontlab_samples == {}
    assert load.state.copied == []


@pytest.mark.parametrize(
    "title,klass,read",
    [
        ("Glyph Grid", "GlyphGrid", "selected_glyphs"),
        ("Text By Master", "TextByMaster", "font_maps"),
        ("Waterfall", "Waterfall", "font_maps"),
        ("Word Finder", "WordFinder", "font_chars"),
    ],
)
def test_early_read_failed_panel_closes_without_retrying_native_read(
    load, monkeypatch, title, klass, read
):
    load.font()
    module = load.module(title)
    calls = []

    def failed(*args):
        calls.append("read")
        raise RuntimeError("initial read failed")

    monkeypatch.setattr(module, read, failed)
    monkeypatch.setattr(sys, "_fontlab_samples", {}, raising=False)
    dialog = module.main()
    assert isinstance(dialog, getattr(module, klass))
    assert "initial read failed" in dialog.status.text and not dialog._snapshot_valid
    dialog.close_button.clicked.emit()
    assert calls == ["read"], "Close must not retry a failed native scan"
    assert dialog.deleted and not dialog._connections and sys._fontlab_samples == {}


@pytest.mark.parametrize(
    "title,klass,read,control",
    [
        ("Glyph Grid", "GlyphGrid", "selected_glyphs", "zoom"),
        ("Text By Master", "TextByMaster", "font_maps", "size_slider"),
        ("Waterfall", "Waterfall", "font_maps", "text"),
        ("Word Finder", "WordFinder", "font_chars", "must"),
    ],
)
def test_failed_initial_scan_retains_known_binding_before_automatic_retry(
    load, monkeypatch, title, klass, read, control
):
    load.font()
    module = load.module(title)
    with monkeypatch.context() as broken:
        broken.setattr(
            module,
            read,
            lambda *args: (_ for _ in ()).throw(RuntimeError("initial read failed")),
        )
        dialog = getattr(module, klass)()
    load.state.package = NS(id=99, isNull=False)
    if control in {"text", "must"}:
        getattr(dialog, control).setText("A")
    else:
        getattr(dialog, control).setValue(30)
    assert "original font" in dialog.slot_error and not dialog._snapshot_valid
    assert dialog._bound_id == 7 and dialog.package is None
    if title == "Glyph Grid":
        load.font().id = 99
        dialog.reload_button.clicked.emit()
        assert dialog._snapshot_valid and dialog._bound_id == 99
    dialog.close_button.clicked.emit()
    assert dialog.deleted
