# this_file: tests/test_components.py
# SPDX-License-Identifier: Apache-2.0
"""Complete component menus and immutable Git-free 49-tool baseline."""

import hashlib
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).parents[1]
TOOLS = [
    ("Compatibility", "Compatibility"),
    ("Count Badges", "CountBadges"),
    ("Missing Bases", "MissingBases"),
    ("Report", "ComponentsReport"),
    ("Where Used", "WhereUsed"),
]
RELEASED49_DIGEST = "5e5cc9b782a4ad26bd38ef7e803bdd3cd1d37e11a0c920d60738bc8a2840e111"
RELEASED49_BYTES = {
    "Scripts/Reports/Empty Glyphs.py": "24d24dc5af8d1e95870eb5134215f696a8fca90aa71e452c6cb2b04bed18c539",
    "Scripts/Reports/Open Contours.py": "47f01b0930d1ad4464f09a717a5c8552d74415305fe7a07f98da2842065c6d29",
    "Scripts/Reports/Font Overview.py": "913c65036087cbca7e8fdb2ad1f0939dba7544f8afb4d5396fe98ed29e51c388",
    "Scripts/Reports/Live Glyph Info.py": "d950a1a7e3f38b38405c51fadc968acc0dcf571fd8eba5db9adb3cce354f3b10",
    "Scripts/Reports/Glyph Table CSV.py": "633627b3f2d375b2e67abf6cea0b0ae355178be4771c8a6a2380a45dd5fa8a16",
    "Scripts/Reports/Label Statistics.py": "160b4c80d899c42329bd4fb5264e9e2aec54400f8e1b7e230611ff1f40e8c2f9",
    "Scripts/Reports/Nodes Near Zones.py": "e5a80cd4148f4e58f55e0a6d1515dd3311fdcf646dd0d69673f46498ecf1217c",
    "Scripts/Reports/Unicode Coverage.py": "abadcdc25b285677df5922c92c1ba2b60a1463e327f124fe45d7a473a0a245ab",
    "Scripts/Font Info/Glyph Order Preview and Export.py": "491df26b75a450f54e81c9ea49643c3509e5e1e70ab49ea072fc4702e7125966",
    "Scripts/Font Info/Master Metrics Table.py": "4455e14f52b4db43cd372c2d5218af04e5f4afcf7c925f7f5a75de61402b8be1",
    "Scripts/Font Info/Names and Credits.py": "22770ea8c13c0e5680a12f718a2d3d774139011938e33bd48a46808d3f3f2557",
    "Scripts/Font Info/Unicode Ranges and Codepages.py": "e8fd9fab22d4aead8839c737d5a64fe0e8fd476aedc375728ee7e1de54b6cf14",
    "Scripts/Font Info/Bump Font Version.py": "3f55b998e7650df88b8b470bdc756013fc94c2cb19447098e3088a2d2953b670",
    "Scripts/Font Info/Calculate Vertical Metrics.py": "496f21b000f65b652e6547cb00a74db9d24d0a23f924e14f2e967612240f4126",
    "Scripts/Features/Alternate Preview.py": "ffb72d9561f925a7e2fdedd7973c74d12b9786983a25e5c2c0eb966ea96e233d",
    "Scripts/Features/Build Suffix Substitution.py": "13e7bb721cad475e3893fb905abd1abba8be38b6b159422390e31cbe5613f49f",
    "Scripts/Features/Classes Browser.py": "c2ee6f461021b20a639a7d4ef64f7c22e6dc34230b4eafa2e56d11e068e60584",
    "Scripts/Features/Feature Code Viewer.py": "96df801f97d645706cb714d34c1324800f36354c0b460c22a929868434ab9301",
    "Scripts/Features/Ligature Finder.py": "556e965cf21995a1220af8ab94355c599439fa04492cf88809b865bfa3711657",
    "Scripts/Features/Suffix Report.py": "388b4c2b68498b4ae23fec27affc6709adfe6cc6fa000251364a979b251e1128",
    "Scripts/Names/Case Pairs.py": "ffdb7108bf39cb42219cf22e595b4a41c81f4813be14c5692635ce69cef8a226",
    "Scripts/Names/Character Info.py": "71a8250426b55d0f184ce581128315b623ca6ab441cb3f82079eacedd52598ae",
    "Scripts/Names/Character Set Compare.py": "a1c2b1426812516c1d731a38f315bd7cf9cf6414174ef70f4b0b3b7f5c10a1df",
    "Scripts/Names/Glyph Finder.py": "0141062c32e45e4efb40810fee2b91030e73f3044bf00aae05bf48605cbcfce9",
    "Scripts/Names/Select by Mark.py": "c13b40e3808df4dbcdfc1142b8d524cd59e499194aa66c3782cbaade1149daf0",
    "Scripts/Kerning/Classes Browser.py": "d2fb6a60232ef806b20d25b55c1ceee1a56a91257a5edfb68b07bd16b57114d3",
    "Scripts/Kerning/Compare Masters.py": "f0051ebeee2e17c7cdb3c1e794334fbcc3bae733c7169eb906d3667207dfb872",
    "Scripts/Kerning/Pair List Browser.py": "925c5ac9178477b00f4c133d54982116ba63175959ae4a0e2ebcd95b1f9e3ae0",
    "Scripts/Kerning/Missing Pairs.py": "eb9a0ee1b2763280639fc9e1810a2f92528a9b4fc58fb8c293ed21026d5d3680",
    "Scripts/Kerning/Text Preview.py": "f2dc3bb04c60fbb5c21d7d097de570694ee5222fbaf99706beb53c16abd908e0",
    "Scripts/Kerning/Copy Between Masters.py": "fb9bb91736945a3cf1fb968188bacbfdbe6ae49e0696872de126b69920c42861",
    "Scripts/Kerning/Pair Editor.py": "2e31e1278e5de1606eea877ecbed5d6ee93e433440acd934f0de8cb762a66dfc",
    "Scripts/Kerning/Scale Values.py": "6e0fd81379e5fe5a51da62cbb409dba08c7f8e0f7d972715b919e886d47ce7f6",
    "Scripts/Kerning/Round Values.py": "9aa3ef344a8bc61bdf1542b4900154e9afc15c0da4ad8c188d784eb0cd68ef5e",
    "Scripts/Kerning/Remove Small Pairs.py": "de4b6244375ea09af774a8bd4effeaf7f67be65c2b15ad05a328c23048f269cd",
    "Scripts/Kerning/Exceptions Finder.py": "adfbdc13fe2f9e09f1a990c67c303a909bd313183d0922a45f82d1918ba7a5e6",
    "Scripts/Kerning/Pairs From Text.py": "813044df6b23eff64ee02a3e7fda6d3501002c55770578e04684e42eae105495",
    "Scripts/Proof/Glyph Grid.py": "8e4dee95447fd6d09f24796a5d2d890e5285d5fcefcf535e8456af8926ed30e5",
    "Scripts/Proof/Text By Master.py": "9fec00539d5cfbcbab6efb91a129ddb7690d72a649898923c66ccb95e889d8cf",
    "Scripts/Proof/Waterfall.py": "0174d79bfb4f89a952510f9ae567aff15c245cce4b824874a138dcf815eb154e",
    "Scripts/Proof/Word Finder.py": "8f2004e41ad01387db42fd7ef4b234e22bc7ea9414719dc53560687c909634f8",
    "Scripts/Masters/Overview.py": "4e0de2e71ab69e3983debe74ca1a3e117e2cd545b8f989660e8864ec24f57bad",
    "Scripts/Masters/Width Chart.py": "7c0d431651958c581bccfee5774fc9eec7efd138f81019aa8e1f21ab7b86ff41",
    "Scripts/Masters/Glyph Weight Chart.py": "065db5fbb8727be35506317f30d3c7c997928aa0ff3af1a89b4cf6ca7c29ca36",
    "Scripts/Masters/Compatibility Check.py": "153b663e08561d54cf5d1de999553832a4ea15dab50c878157abcc73be3666b3",
    "Scripts/Metrics/Spacing String Preview.py": "69965386fcaf31c39db85123ff29118d16e4aa4cd3237ba52dc5be4c98220894",
    "Scripts/Metrics/Width Table.py": "c0f364ff9cfdc644f1f3b1741364b0946979d06034ba6d918c2f91f36b41d4e5",
    "Scripts/Outlines/Contour Order View.py": "18bb4a44aa9a93fe31d96752495b96d98b215b4b4dbabbf28206337ecc98eecc",
    "Scripts/Outlines/Node Statistics.py": "1de5f0156457f5f11cea026651af0c5053b76826cf290acb30171f9673626990",
}


@pytest.mark.parametrize("title,klass", TOOLS)
def test_complete_component_menu_exists(title, klass):
    assert (ROOT / "Scripts/Components" / (title + ".py")).is_file()


def assert_released49(root, rows):
    assert len(rows) == 54, "All 54 source/destination pairs are required"
    digest = hashlib.sha256(
        json.dumps(rows[:49], sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    assert digest == RELEASED49_DIGEST, "Released v1.0.8 manifest changed"
    for destination, expected in RELEASED49_BYTES.items():
        assert (
            hashlib.sha256((root / destination).read_bytes()).hexdigest() == expected
        ), destination


def test_immutable_released49_manifest_and_every_menu_byte():
    assert_released49(ROOT, json.loads((ROOT / "migration.json").read_text()))


import importlib.util
import sys
from types import SimpleNamespace as NS

from test_inspectors import Check, Combo
from test_masters import Item, MasterWidget, masters  # noqa: F401
from test_proof import Box, Signal


class ComponentWidget(MasterWidget):
    """Native-shaped tree/table/scroll/completion controls used by originals."""

    def __init__(self, *args):
        super().__init__(*args)
        self.cellClicked = Signal()
        self.hidden = {}

    def setText(self, value):
        self.text = value
        if not self.blocked:
            self.textChanged.emit()

    def addTopLevelItem(self, item):
        self.children.append(item)

    def setColumnCount(self, value):
        self.columnCount = value

    def setHeaderLabels(self, values):
        self.headers = values

    def setRowHidden(self, row, value):
        self.hidden[row] = value

    def viewport(self):
        return self

    def resizeEvent(self, event):
        pass


class ComponentItem(Item):
    def __init__(self, values):
        self.texts = (
            dict(enumerate(values)) if isinstance(values, list) else {0: values}
        )
        self.children, self.bold = [], False

    def addChild(self, child):
        self.children.append(child)


class Rect(Box):
    def x(self):
        return self.left()

    def y(self):
        return self.top()

    def width(self):
        return self.values[2]

    def height(self):
        return self.values[3]

    def united(self, other):
        return self


@pytest.fixture
def components(masters, monkeypatch, app_sources):  # noqa: F811
    qt = masters.qt
    for name in [
        "QTableWidget",
        "QTreeWidget",
        "QScrollArea",
        "QCompleter",
        "QLineEdit",
        "QWidget",
        "QDialog",
    ]:
        setattr(qt.QtGui, name, ComponentWidget)
    qt.QtGui.QComboBox = Combo
    qt.QtGui.QCheckBox = Check
    qt.QtGui.QTableWidgetItem = qt.QtGui.QTreeWidgetItem = ComponentItem
    qt.QtGui.QAbstractItemView.SelectRows = (
        qt.QtGui.QAbstractItemView.SingleSelection
    ) = 1
    qt.QtCore.Qt.CaseInsensitive = qt.QtCore.Qt.MatchContains = 1
    qt.QtCore.QRectF = Rect
    native = masters.modules["scripting"]._native("fontlab")
    native.MainWindow = lambda: NS(palette=NS(color=lambda *a: qt.QtGui.QColor()))
    masters.state.activated = []
    for name in [
        "_names_dialog",
        "_proof_dialog",
        "_proof_views",
        "inspectors",
        "components",
        "_components_views",
        "_components_dialog",
    ]:
        spec = importlib.util.spec_from_file_location(
            "fontlabapp." + name, app_sources / (name + ".py")
        )
        module = importlib.util.module_from_spec(spec)
        monkeypatch.setitem(sys.modules, "fontlabapp." + name, module)
        spec.loader.exec_module(module)
        masters.modules[name] = module
    api = masters.modules["components"]
    api.glyph_path = lambda layer: NS(boundingRect=lambda: Rect(0, 0, 100, 100))
    qt.QtGui.QPainterPath = lambda: NS(boundingRect=lambda: Rect(0, 0, 0, 0))
    painter = masters.painter

    class Painter:
        Antialiasing = 1

        def __new__(cls, owner):
            return painter

    qt.QtGui.QPainter = Painter
    qt.QtGui.QFontMetrics = lambda font: NS(width=lambda text: len(text) * 6)

    def module(title):
        spec = importlib.util.spec_from_file_location(
            title, ROOT / "Scripts/Components" / (title + ".py")
        )
        result = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(result)
        return result

    masters.module = module
    oldfont = masters.font

    def font():
        package, layers = oldfont()
        for rows in layers.values():
            for layer in rows.values():
                for shape in layer.shapes:
                    shape.getContours = lambda shape=shape: shape.contours
                    for contour in shape.contours:
                        contour.closed = True
        transform = lambda x=0: NS(
            isIdentity=lambda: True,
            m11=lambda: 1,
            m12=lambda: 0,
            m21=lambda: 0,
            m22=lambda: 1,
            dx=lambda: x,
            dy=lambda: 0,
        )
        for master in package.masters:
            # O references H twice, n has different lists across masters.
            for name, bases in [
                ("O", ["H", "H"]),
                ("n", ["H"] if master == "Bold" else ["O"]),
            ]:
                for base in bases:
                    layers[name][master].shapes.append(
                        NS(
                            isComponent=True,
                            shapeData=NS(componentGlyph=base),
                            transform=transform(1.25),
                            contours=[],
                            getContours=list,
                        )
                    )
        package.activateGlyph = masters.state.activated.append
        masters.state.selected.update({0, 1, 2})
        masters.state.fallback = masters.state.glyphs[1]
        return package, layers

    masters.font = font
    return masters


@pytest.mark.parametrize("title,klass", TOOLS)
def test_full_no_font_constructor_and_owned_close(
    components, monkeypatch, title, klass
):
    monkeypatch.setattr(sys, "_fontlab_samples", {}, raising=False)
    module = components.module(title)
    dialog = module.main()
    assert isinstance(dialog, getattr(module, klass))
    assert hasattr(dialog, "status") and hasattr(dialog, "close_button")
    assert dialog.subtitle.text == "Open a font first." and dialog.last_error is None
    assert not dialog._snapshot_valid
    connections = list(dialog._connections)
    dialog.close_button.clicked.emit()
    assert dialog.deleted and not dialog._connections and sys._fontlab_samples == {}
    assert all(slot not in signal.slots for signal, slot in connections)


@pytest.mark.parametrize("title,klass", TOOLS)
def test_complete_original_rows_cards_trees_and_controls(components, title, klass):
    package, _layers = components.font()
    dialog = getattr(components.module(title), klass)()
    assert dialog.last_error is None, dialog.last_error
    assert dialog._snapshot_valid and dialog.masters == ["Bold", "Light"]
    if klass == "Compatibility":
        assert dialog.rows == [
            ("O", {"Bold": ["H", "H"], "Light": ["H", "H"]}),
            ("n", {"Bold": ["H"], "Light": ["O"]}),
        ]
        assert dialog.mismatches() == ["n"] and dialog.shown[0][0] == "n"
        dialog.only_bad.setChecked(True)
        assert len(dialog.shown) == 1 and dialog.table.rowCount == 1
        dialog.open_row(0)
        assert components.state.selected == {2}
        dialog.scope.setCurrentIndex(1)
        assert len(dialog.rows) == 2
    elif klass == "CountBadges":
        assert dialog.counts == {
            "H": {"Bold": [0, 1, False], "Light": [0, 1, False]},
            "O": {"Bold": [2, 1, False], "Light": [2, 1, False]},
            "n": {"Bold": [1, 1, False], "Light": [1, 1, False]},
        }
        assert [card[0] for card in dialog.grid.cards] == ["H", "O", "n"]
        assert dialog.grid.error is None and "2 of 3" in dialog.status.text
        dialog.grid.paintEvent(None)
        assert dialog.grid.error is None, dialog.grid.error
        assert any(name == "drawPath" for name, args in components.painter.calls)
        assert components.painter.calls[-1][0] == "end"
    elif klass == "MissingBases":
        assert dialog.groups == {} and not dialog.select_button.enabled
        predicate = lambda name, master: name != "H"
        dialog.rescan(exists=predicate)
        assert list(dialog.groups) == ["H"]
        assert len(dialog.groups["H"]) == 5 and len(dialog.tree.children) == 1
        assert dialog.affected() == ["O", "n"] and dialog._exists is predicate
        dialog.select_affected()
        assert components.state.selected == {1, 2}
        assert dialog._exists is predicate, (
            "Action guards must retain the simulation oracle"
        )
        dialog.rescan()
        assert dialog.groups == {} and dialog._exists is None
    elif klass == "ComponentsReport":
        assert len(dialog.rows) == 4 and len(dialog.visible_rows()) == 2
        dialog.scope.setCurrentIndex(1)
        dialog.filter.setText("H + H")
        assert len(dialog.visible_rows()) == 2
        assert len(dialog.csv_text().splitlines()) == 3
        dialog.copy_csv()
        assert components.state.copied == [dialog.csv_text()]
        dialog.open_glyph(0)
        assert components.state.activated == [package.findName("O")]
    else:
        assert dialog.index == {
            "H": {"O": [("Bold", False), ("Light", False)], "n": [("Bold", False)]},
            "O": {"n": [("Light", False)]},
        }
        dialog.search.setText("H")
        assert dialog.rows == ["O", "n"]
        dialog.pick(0)
        assert components.state.selected == {1}
        dialog.select_all()
        assert components.state.selected == {1, 2}
        dialog.search.setText("unknown")
        assert not dialog.rows and "No glyph" in dialog.status.text
    assert package.master == "Bold", "Read-only tools must never switch master"


def trigger(dialog, klass):
    if klass == "Compatibility":
        dialog.open_row(0)
    elif klass == "CountBadges":
        dialog.grid.paintEvent(None)
    elif klass == "MissingBases":
        dialog.select_affected()
    elif klass == "ComponentsReport":
        dialog.copy_csv()
    else:
        dialog.select_all()


@pytest.mark.parametrize("title,klass", TOOLS)
@pytest.mark.parametrize(
    "change",
    [
        "font",
        "closed",
        "master",
        "master_order",
        "membership",
        "component",
        "offset",
        "counts",
    ],
)
def test_stale_actions_refuse_and_clear_all_results(components, title, klass, change):
    package, layers = components.font()
    dialog = getattr(components.module(title), klass)()
    assert dialog.last_error is None, dialog.last_error
    if change == "font":
        components.state.package = NS(id=999, isNull=False)
    elif change == "closed":
        components.state.package = None
    elif change == "master":
        package.master = "Light"
    elif change == "master_order":
        package.masters.reverse()
    elif change == "membership":
        components.state.glyphs.reverse()
    elif change == "component":
        layers["O"]["Bold"].shapes[1].shapeData.componentGlyph = "n"
    elif change == "offset":
        layers["O"]["Bold"].shapes[1].transform.dx = lambda: 1.26
    elif change == "counts":
        layers["O"]["Bold"].shapes[0].contours.append(NS())
    selected = set(components.state.selected)
    if klass == "CountBadges":
        trigger(dialog, klass)
        assert dialog.grid.error is not None
    else:
        with pytest.raises(ValueError):
            trigger(dialog, klass)
    assert not dialog._snapshot_valid and dialog.package is None
    assert (
        not dialog.rows
        and not dialog.groups
        and not dialog.counts
        and dialog._exists is None
    )
    assert components.state.selected == selected and not components.state.copied


@pytest.mark.parametrize("title,klass", TOOLS)
@pytest.mark.parametrize(
    "stage", ["binding", "identity", "masters", "master", "names", "scan"]
)
def test_initial_read_failures_leave_all_controls_diagnosed_and_closable(
    components, monkeypatch, title, klass, stage
):
    package, _layers = components.font()
    module = components.module(title)
    api = components.modules["components"]
    components.modules["_components_dialog"]

    def fail(*a, **kw):
        raise RuntimeError("injected opening read")

    if stage == "binding":
        monkeypatch.setattr(
            components.modules["_proof_dialog"], "current_package", fail
        )
    elif stage == "identity":

        class Fault:
            isNull = False

            @property
            def id(self):
                return fail()

        components.state.package = Fault()
    elif stage in {"masters", "master"}:

        class Fault:
            def __getattr__(self, name):
                if name == stage:
                    return fail()
                return getattr(package, name)

        components.state.package = Fault()
    elif stage == "names":
        monkeypatch.setattr(api, "font_glyph_names", fail)
    else:
        monkeypatch.setattr(api, "source_values", fail)
    dialog = getattr(module, klass)()
    assert dialog.last_error and "injected opening read" in dialog.status.text
    assert hasattr(dialog, "status") and hasattr(dialog, "close_button")
    assert not dialog.rows and not dialog.groups and not dialog.counts
    dialog.close_button.clicked.emit()
    assert dialog.deleted and not dialog._connections


def test_count_fallback_geometry_drift_and_painter_failure_settles(components):
    _package, _layers = components.font()
    components.state.selected.clear()
    module = components.module("Count Badges")
    dialog = module.CountBadges()
    assert [g.name for g in dialog.glyphs] == ["O"]
    updates = []
    dialog.grid.update = lambda: updates.append(1)

    def fail(painter):
        raise RuntimeError("paint failed")

    dialog.grid.paint = fail
    dialog.grid.paintEvent(None)
    assert "paint failed" in dialog.grid.error and not dialog.grid.cards
    assert components.painter.calls[-1][0] == "end"
    for _ in range(5):
        dialog.grid.paintEvent(None)
    assert len(updates) == 1, "Repeated empty invalidations must not enqueue repaints"
    dialog.close()
    assert dialog.grid.before_draw is None and dialog.grid.on_error is None


def test_membership_rechecked_after_final_source_read(components, monkeypatch):
    _package, _layers = components.font()
    dialog = components.module("Report").ComponentsReport()
    original = dialog.check_results

    def mutate():
        original()
        components.state.glyphs.reverse()

    monkeypatch.setattr(dialog, "check_results", mutate)
    with pytest.raises(ValueError, match="order changed"):
        dialog.copy_csv()
    assert not dialog.rows and not components.state.copied


@pytest.mark.parametrize("field", ["source_sha256", "destination_sha256"])
def test_released49_rejects_changed_provenance(field):
    rows = json.loads((ROOT / "migration.json").read_text())
    rows[48][field] = "0" * 64
    with pytest.raises(AssertionError, match="manifest changed"):
        assert_released49(ROOT, rows)


def test_released49_rejects_changed_menu_bytes(tmp_path):
    rows = json.loads((ROOT / "migration.json").read_text())
    for destination in RELEASED49_BYTES:
        target = tmp_path / destination
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((ROOT / destination).read_bytes())
    (tmp_path / rows[48]["destination"]).write_bytes(b"changed")
    with pytest.raises(AssertionError):
        assert_released49(tmp_path, rows)


@pytest.mark.parametrize("title,klass", TOOLS)
def test_guarded_action_failure_is_diagnosed_and_close_disconnects(
    components, title, klass
):
    package, _layers = components.font()
    dialog = getattr(components.module(title), klass)()
    package.master = "Light"
    if klass == "Compatibility":
        dialog.only_bad.setChecked(True)
    elif klass == "CountBadges":
        dialog.grid.paintEvent(None)
    elif klass == "MissingBases":
        dialog.select_button.clicked.emit()
    elif klass == "ComponentsReport":
        dialog.copy_button.clicked.emit()
    else:
        dialog.search.setText("H")
    assert dialog.last_error and not dialog._snapshot_valid
    connections = list(dialog._connections)
    dialog.close_button.clicked.emit()
    assert dialog.deleted and all(
        slot not in signal.slots for signal, slot in connections
    )


@pytest.mark.parametrize("stage", ["selection", "fallback"])
def test_count_badges_selection_read_fault_still_has_close(
    components, monkeypatch, stage
):
    _package, _layers = components.font()

    def fail(*a):
        raise RuntimeError(stage + " read failed")

    if stage == "selection":
        monkeypatch.setattr(components.modules["components"], "selected_names", fail)
    else:
        components.state.selected.clear()
        monkeypatch.setattr(
            components.modules["scripting"]._native("fontlab"), "CurrentGlyph", fail
        )
    dialog = components.module("Count Badges").CountBadges()
    assert dialog.last_error and not dialog.grid.cards
    dialog.close_button.clicked.emit()
    assert dialog.deleted


def test_badges_missing_zero_auto_odd_and_geometry_refusal(components):
    _package, layers = components.font()
    layers["H"].pop("Light")
    layers["H"]["Bold"].shapes.clear()
    layers["n"]["Bold"].autoLayer = True
    layers["n"]["Light"].shapes.pop()
    dialog = components.module("Count Badges").CountBadges()
    assert dialog.counts["H"] == {"Bold": [0, 0, False]}
    assert dialog.counts["n"]["Bold"] == [1, 1, True]
    assert dialog.grid.cards[2][3] == [
        ("Bold", 1, 1, True, False),
        ("Light", 0, 1, False, True),
    ]
    layers["O"]["Bold"].shapes[0].contours[0].nodes = list
    dialog.grid.paintEvent(None)
    assert dialog.grid.error is not None and not dialog.grid.cards


def test_explicit_rescan_preserves_domain_and_clears_simulation_on_failure(components):
    package, _layers = components.font()
    dialog = components.module("Missing Bases").MissingBases()
    predicate = lambda name, master: False
    dialog.rescan(exists=predicate)
    assert dialog._exists is predicate and dialog.groups
    package.master = "Light"
    with pytest.raises(ValueError):
        dialog.select_affected()
    assert dialog._exists is None
    with pytest.raises(ValueError, match="Masters changed"):
        dialog.rescan(exists=predicate)
    assert not dialog.groups and dialog._exists is None


def test_badge_empty_recovery_restores_exact_none_after_success(components):
    components.font()
    dialog = components.module("Count Badges").CountBadges()
    original = dialog.grid.paint

    def fail(painter):
        raise RuntimeError("failed ink")

    dialog.grid.paint = fail
    dialog.grid.paintEvent(None)
    assert dialog.grid.error == "RuntimeError('failed ink')"
    dialog.grid.paint = original
    dialog.grid.paintEvent(None)
    assert dialog.grid.error is None and not dialog.grid.cards
    dialog.refresh()
    assert dialog._snapshot_valid and dialog.counts
    dialog.grid.paintEvent(None)
    assert dialog.grid.error is None


def test_scan_rechecks_source_and_domain_after_last_native_reads(
    components, monkeypatch
):
    _package, layers = components.font()
    dialog = components.module("Compatibility").Compatibility()
    original = components.modules["components"].component_lists

    def read(*args):
        rows = original(*args)
        layers["O"]["Bold"].shapes[1].transform.dx = lambda: 2.25
        return rows

    sys.modules.get("Compatibility")
    # Menu helper aliases are deliberately independent of the API namespace.
    dialog.rescan.__wrapped__.__globals__["component_lists"] = read
    with pytest.raises(ValueError, match="changed during scan"):
        dialog.rescan()
    assert not dialog.rows and not dialog._snapshot_valid


@pytest.mark.parametrize(
    "title,klass,alias",
    [
        ("Compatibility", "Compatibility", "component_lists"),
        ("Count Badges", "CountBadges", "counts"),
        ("Missing Bases", "MissingBases", "missing"),
        ("Report", "ComponentsReport", "report"),
        ("Where Used", "WhereUsed", "usage_index"),
    ],
)
def test_original_scan_helper_alias_faults_are_contained_after_controls(
    components, monkeypatch, title, klass, alias
):
    components.font()
    module = components.module(title)

    def fail(*args, **kwargs):
        raise RuntimeError("original helper failed")

    monkeypatch.setattr(module, alias, fail)
    dialog = getattr(module, klass)()
    assert dialog.last_error == "RuntimeError: original helper failed"
    assert (
        not dialog.rows and not dialog.counts and not dialog.groups and not dialog.index
    )
    dialog.close_button.clicked.emit()
    assert dialog.deleted and not dialog._connections


def test_compatibility_empty_selection_stays_empty_with_current_glyph(components):
    components.font()
    components.state.selected.clear()
    assert components.state.fallback.name == "O"
    dialog = components.module("Compatibility").Compatibility()
    assert dialog.last_error is None
    assert dialog.selection == []
    assert dialog.scope.items[1] == "Selected glyphs (0)"
    dialog.scope.setCurrentIndex(1)
    assert dialog.rows == [] and dialog.shown == []
    badges = components.module("Count Badges").CountBadges()
    assert [glyph.name for glyph in badges.glyphs] == ["O"], (
        "Only badges retain the original fallback"
    )


@pytest.mark.parametrize("failure", ["inactive", "end_false", "end_raises"])
def test_badge_painter_terminal_failures_are_contained_and_invalidate(
    components, failure
):
    components.font()
    dialog = components.module("Count Badges").CountBadges()
    calls, updates = [], []
    dialog.grid.update = lambda: updates.append("update")
    components.painter.isActive = lambda: failure != "inactive"

    def end():
        calls.append("end")
        if failure == "end_raises":
            raise RuntimeError("end failed")
        return failure != "end_false"

    components.painter.end = end
    original = dialog.grid.on_error

    def reported(error):
        assert calls[-1] == "end", (
            "The native painter must end before diagnostic callbacks"
        )
        return original(error)

    dialog.grid.on_error = reported
    dialog.grid.paintEvent(None)
    assert dialog.grid.error is not None and dialog.last_error
    assert not dialog._snapshot_valid and not dialog.grid.cards
    assert dialog.status.text.startswith("Error:")
    assert len(calls) == 1 and len(updates) == 1
    if failure == "inactive":
        assert not any(name == "drawPath" for name, args in components.painter.calls)
    for _ in range(6):
        dialog.grid.paintEvent(None)
    assert len(updates) == 1, "Persistent terminal failures must settle empty repaints"


def test_badge_error_hook_failure_still_clears_paths_snapshot_and_releases_callbacks(
    components,
):
    components.font()
    dialog = components.module("Count Badges").CountBadges()
    components.painter.isActive = lambda: False

    def failed_hook(error):
        raise RuntimeError("diagnostic failed")

    dialog.grid.on_error = failed_hook
    dialog.grid.paintEvent(None)
    assert dialog.grid.error is not None and "diagnostic failed" in dialog.grid.error
    assert not dialog._snapshot_valid and not dialog.grid.cards
    dialog.close_button.clicked.emit()
    assert (
        dialog.deleted
        and dialog.grid.on_error is None
        and dialog.grid.before_draw is None
    )
    assert dialog.grid.failure_cleanup is None


def test_badge_shared_painter_success_keeps_exact_none_and_original_paint_entry(
    components,
):
    components.font()
    dialog = components.module("Count Badges").CountBadges()
    components.painter.isActive = lambda: True
    events = []
    original = dialog.grid.paint

    def draw(painter):
        events.append("paint")
        return original(painter)

    dialog.grid.paint = draw
    components.painter.end = lambda: events.append("end") or True
    dialog.grid.paintEvent(None)
    assert events == ["paint", "end"]
    assert dialog.grid.error is None and dialog._snapshot_valid and dialog.grid.cards


def test_badge_secondary_cleanup_exception_stays_inside_native_paint_boundary(
    components,
):
    components.font()
    dialog = components.module("Count Badges").CountBadges()
    components.painter.end = lambda: False

    def fail_cleanup(error):
        raise RuntimeError("cleanup failed")

    dialog.grid.failure_cleanup = fail_cleanup
    dialog.grid.paintEvent(None)
    assert not dialog._snapshot_valid and not dialog.grid.cards
    assert "cleanup failed" in dialog.grid.error
    dialog.close_button.clicked.emit()
    assert dialog.grid.failure_cleanup is None


class FalseyNativeGlyph:
    """Measured native current glyph: valid/name-present, but bool returns false."""

    name = "A"
    isNull = False

    def __bool__(self):
        return False


def test_badges_falsey_current_A_keeps_actual_counts_without_selecting_it(components):
    package, _layers = components.font()
    base = package.findName("H")
    base.name = "A"
    lookup = package.findName
    package.findName = lambda name: base if name == "A" else lookup(name)
    components.state.selected.clear()
    components.state.fallback = FalseyNativeGlyph()
    assert (
        not bool(components.state.fallback)
        and components.state.fallback.isNull is False
    )
    dialog = components.module("Count Badges").CountBadges()
    assert dialog.last_error is None and dialog._snapshot_valid
    assert [glyph.name for glyph in dialog.glyphs] == ["A"]
    assert dialog.counts == {"A": {"Bold": [0, 1, False], "Light": [0, 1, False]}}
    dialog.grid.paintEvent(None)
    assert dialog.grid.error is None and [card[0] for card in dialog.grid.cards] == [
        "A"
    ]
    assert components.state.selected == set(), (
        "Fallback is inspection, not a Font-window selection change"
    )
    compatibility = components.module("Compatibility").Compatibility()
    assert compatibility.selection == []
    compatibility.scope.setCurrentIndex(1)
    assert compatibility.rows == []


def test_badges_none_current_stays_empty_and_real_selection_wins(components):
    components.font()
    components.state.selected.clear()
    components.state.fallback = None
    dialog = components.module("Count Badges").CountBadges()
    assert dialog.last_error is None and dialog.glyphs == [] and dialog.counts == {}
    components.state.selected.update({0, 2})
    components.state.fallback = FalseyNativeGlyph()
    selected = components.module("Count Badges").CountBadges()
    assert [glyph.name for glyph in selected.glyphs] == ["H", "n"]
    assert set(selected.counts) == {"H", "n"} and selected.last_error is None
