# this_file: tests/_cov_b_support.py
"""Original owned fakes for the coverage round: a stateful PythonQt and a kerning font.

The fake Qt keeps the PythonQt calling convention the menu scripts rely on: widget
state is read as attributes (``line.text``, ``spin.value``, ``combo.currentIndex``,
``table.rowCount``) while table items use methods (``item.text()``). Classes that
App code probes with ``hasattr``/``getattr(x, name, None)`` raise AttributeError
for unknown names, so absent optional widgets stay absent.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import SimpleNamespace as NS
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

# ---------------------------------------------------------------- enums
_ENUMS: dict[str, int] = {
    "Checked": 2,
    "Unchecked": 0,
    "AlignRight": 2,
    "AlignVCenter": 128,
    "AlignCenter": 132,
    "DisplayRole": 0,
}


def enum_value(name: str) -> int:
    """Return a stable distinct integer for an enum name."""
    if name not in _ENUMS:
        _ENUMS[name] = 1000 + len(_ENUMS)
    return _ENUMS[name]


class EnumNamespace:
    """Namespace whose capitalised attributes are distinct stable integers."""

    def __getattr__(self, name: str) -> int:
        if name.startswith("_"):
            raise AttributeError(name)
        return enum_value(name)


class EnumMeta(type):
    """Class-level enum lookups (``QPalette.Link``) resolve to stable integers."""

    def __getattr__(cls, name: str) -> Any:
        if name[:1].isupper():
            return enum_value(name)
        raise AttributeError(name)


# ---------------------------------------------------------------- signals
class Signal:
    """Minimal PythonQt signal: connect, disconnect and emit."""

    def __init__(self) -> None:
        self.slots: list[Any] = []

    def connect(self, slot: Any) -> None:
        self.slots.append(slot)

    def disconnect(self, slot: Any = None) -> None:
        if slot is None:
            self.slots.clear()
        elif slot in self.slots:
            self.slots.remove(slot)
        else:
            raise TypeError("slot not connected")

    def emit(self, *args: Any) -> None:
        for slot in list(self.slots):
            slot(*args)


# ---------------------------------------------------------------- base
class Base(metaclass=EnumMeta):
    """Records setter calls; signals are declared per class in SIGNALS."""

    SIGNALS: tuple[str, ...] = ()
    PERMISSIVE = False

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.__dict__["_signals"] = {name: Signal() for name in self.SIGNALS}
        self.__dict__["set_calls"] = []
        self.__dict__["init_args"] = args

    def __getattr__(self, name: str) -> Any:
        signals = self.__dict__.get("_signals", {})
        if name in signals:
            return signals[name]
        if name.startswith("_"):
            raise AttributeError(name)
        if name[:3] == "set" and name[3:4].isupper():
            return self._recorder(name)
        if self.PERMISSIVE:
            return self._recorder(name)
        raise AttributeError(name)

    def _recorder(self, name: str) -> Any:
        calls = self.__dict__.setdefault("set_calls", [])

        def record(*args: Any, **kwargs: Any) -> Any:
            calls.append((name, args))
            return Generic()

        return record

    def last_call(self, name: str) -> tuple | None:
        """Return the arguments of the latest recorded generic call, if any."""
        for key, args in reversed(self.__dict__.get("set_calls", [])):
            if key == name:
                return args
        return None


class Generic(Base):
    """Permissive widget/layout/painter stand-in for incidental Qt calls."""

    PERMISSIVE = True

    def __iter__(self) -> Any:
        return iter(())

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return Generic()


class Font(Base):
    """Font that accepts the point-size and bold calls."""

    def __init__(self, *args: Any) -> None:
        super().__init__(*args)
        self.point = 10.0
        self.bold = False

    def pointSizeF(self) -> float:
        return self.point

    def setPointSizeF(self, value: float) -> None:
        self.point = value

    def setBold(self, value: bool) -> None:
        self.bold = value


class Color(Base):
    """Colour whose name() is deterministic."""

    def __init__(self, *args: Any) -> None:
        super().__init__(*args)
        self.args = args
        self.alpha = 255

    def setAlpha(self, value: int) -> None:
        self.alpha = value

    @classmethod
    def fromHsl(cls, hue: int, saturation: int, lightness: int) -> "Color":
        """Build a colour that remembers its HSL inputs."""
        color = cls("hsl", hue, saturation, lightness)
        color.hsl = (hue, saturation, lightness)
        return color

    def name(self, fmt: Any = None) -> str:
        return "#112233" if fmt is None else "#99112233"


class Palette(Base):
    def color(self, role: Any) -> Color:
        return Color(role)

    def setColor(self, role: Any, color: Any) -> None:
        self.set_calls.append(("setColor", (role, color)))


class Rect(Base):
    def __init__(self, *args: Any) -> None:
        super().__init__(*args)
        self.box = tuple(args) if len(args) == 4 else (0, 0, 100, 50)

    def left(self) -> float:
        return self.box[0]

    def top(self) -> float:
        return self.box[1]

    def right(self) -> float:
        return self.box[0] + self.box[2]

    def bottom(self) -> float:
        return self.box[1] + self.box[3]


class PainterPath(Base):
    """Path that tracks only a bounding box."""

    def __init__(self, *args: Any) -> None:
        super().__init__(*args)
        self.box = (0.0, 0.0, 600.0, 700.0)

    def boundingRect(self) -> Rect:
        return Rect(*self.box)

    def addPath(self, other: Any) -> None:
        self.box = getattr(other, "box", self.box)


class Painter(Base):
    """Painter that records text it draws."""

    PERMISSIVE = True

    def __init__(self, *args: Any) -> None:
        super().__init__(*args)
        self.texts: list[str] = []
        self.paths = 0
        self.ended = False
        self._font = Font()
        getattr(type(self), "created", []).append(self)

    def font(self) -> Font:
        return self._font

    def drawText(self, *args: Any) -> None:
        self.texts.append(args[-1])

    def drawPath(self, path: Any) -> None:
        self.paths += 1

    def end(self) -> None:
        self.ended = True


class Clipboard(Base):
    def __init__(self) -> None:
        super().__init__()
        self.copied: list[str] = []

    def setText(self, text: str) -> None:
        self.copied.append(text)


class Application(Base):
    _clipboard = Clipboard()

    @classmethod
    def clipboard(cls) -> Clipboard:
        return cls._clipboard


# ---------------------------------------------------------------- widgets
class Widget(Base):
    """Common widget state: enabled flag, font, palette, geometry."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.enabled = True
        self.font = Font()
        self.palette = Palette()
        self.width = 640
        self.height = 480
        self.rect = Rect(0, 0, 640, 480)
        self.visible = False
        self.deleted = False
        self.updates = 0
        self.stylesheet = ""

    def setEnabled(self, value: bool) -> None:
        self.enabled = bool(value)

    def isEnabled(self) -> bool:
        return self.enabled

    def setFont(self, font: Font) -> None:
        self.font = font

    def setPalette(self, palette: Palette) -> None:
        self.palette = palette

    def setStyleSheet(self, text: str) -> None:
        self.stylesheet = text

    def update(self) -> None:
        self.updates += 1

    def show(self) -> None:
        self.visible = True

    def raise_(self) -> None:
        self.raised = True

    def deleteLater(self) -> None:
        self.deleted = True

    def resize(self, *args: Any) -> None:
        self.width, self.height = args[0], args[1]


class Dialog(Widget):
    SIGNALS = ("finished", "destroyed")

    def __init__(self, parent: Any = None, *args: Any) -> None:
        super().__init__(parent, *args)
        self.closed_events: list[Any] = []

    def setWindowTitle(self, title: str) -> None:
        self.window_title = title

    def close(self) -> bool:
        self.visible = False
        self.closeEvent(NS(accepted=True))
        return True

    def closeEvent(self, event: Any) -> None:
        self.closed_events.append(event)

    def changeEvent(self, event: Any) -> None:
        return None


class Label(Widget):
    def __init__(self, text: str = "", *args: Any) -> None:
        super().__init__(text, *args)
        self.text = text

    def setText(self, text: str) -> None:
        self.text = text


class LineEdit(Widget):
    SIGNALS = ("textChanged", "returnPressed", "textEdited")

    def __init__(self, text: str = "", *args: Any) -> None:
        super().__init__(text, *args)
        self.text = text

    def setText(self, text: str) -> None:
        changed = text != self.text
        self.text = text
        if changed:
            self.textChanged.emit(text)


class SpinBox(Widget):
    SIGNALS = ("valueChanged",)

    def __init__(self, *args: Any) -> None:
        super().__init__(*args)
        self.value = 0
        self.minimum, self.maximum = 0, 99

    def setRange(self, low: float, high: float) -> None:
        self.minimum, self.maximum = low, high
        self.value = min(max(self.value, low), high)

    def setValue(self, value: float) -> None:
        value = min(max(value, self.minimum), self.maximum)
        changed = value != self.value
        self.value = value
        if changed:
            self.valueChanged.emit(value)


class CheckBox(Widget):
    SIGNALS = ("toggled", "clicked")

    def __init__(self, text: str = "", *args: Any) -> None:
        super().__init__(text, *args)
        self.text = text
        self.checked = False

    def isChecked(self) -> bool:
        return self.checked

    def setChecked(self, value: bool) -> None:
        changed = bool(value) != self.checked
        self.checked = bool(value)
        if changed:
            self.toggled.emit(self.checked)


class ComboBox(Widget):
    SIGNALS = ("currentIndexChanged",)

    def __init__(self, *args: Any) -> None:
        super().__init__(*args)
        self.items: list[str] = []
        self.currentIndex = -1

    @property
    def currentText(self) -> str:
        return self.items[self.currentIndex] if self.items else ""

    def addItem(self, text: str, *data: Any) -> None:
        self.items.append(text)
        if self.currentIndex < 0:
            self.currentIndex = 0

    def count(self) -> int:
        return len(self.items)

    def setCurrentIndex(self, index: int) -> None:
        changed = index != self.currentIndex
        self.currentIndex = index
        if changed:
            self.currentIndexChanged.emit(index)


class ListWidget(Widget):
    SIGNALS = ("currentRowChanged",)

    def __init__(self, *args: Any) -> None:
        super().__init__(*args)
        self.items: list[str] = []
        self.currentRow = -1

    def addItem(self, text: str) -> None:
        self.items.append(text)

    def clear(self) -> None:
        self.items.clear()
        self.currentRow = -1

    def count(self) -> int:
        return len(self.items)

    def setCurrentRow(self, row: int) -> None:
        changed = row != self.currentRow
        self.currentRow = row
        if changed:
            self.currentRowChanged.emit(row)


class PushButton(Widget):
    SIGNALS = ("clicked",)

    def __init__(self, text: str = "", *args: Any) -> None:
        super().__init__(text, *args)
        self.text = text
        self.default = False

    def setText(self, text: str) -> None:
        self.text = text

    def setDefault(self, value: bool) -> None:
        self.default = value


class TableItem(Base):
    def __init__(self, text: str = "") -> None:
        super().__init__(text)
        self._text = text
        self.table: Any = None
        self.position = (-1, -1)
        self._check = 0
        self._font = Font()
        self.roles: dict[Any, Any] = {}
        self.foreground: Any = None

    def _changed(self) -> None:
        if self.table is not None:
            self.table.itemChanged.emit(self)

    def text(self) -> str:
        return self._text

    def setText(self, text: str) -> None:
        self._text = text
        self._changed()

    def row(self) -> int:
        return self.position[0]

    def column(self) -> int:
        return self.position[1]

    def checkState(self) -> int:
        return self._check

    def setCheckState(self, state: int) -> None:
        changed = state != self._check
        self._check = state
        if changed:
            self._changed()

    def font(self) -> Font:
        return self._font

    def setFont(self, font: Font) -> None:
        self._font = font

    def setForeground(self, brush: Any) -> None:
        self.foreground = brush

    def setData(self, role: Any, value: Any) -> None:
        self.roles[role] = value
        if role == enum_value("DisplayRole"):
            self._text = f"{value}"

    def data(self, role: Any) -> Any:
        return self.roles.get(role, self._text)


class TableWidget(Widget):
    SIGNALS = (
        "itemChanged",
        "cellChanged",
        "itemSelectionChanged",
        "cellDoubleClicked",
        "cellClicked",
    )
    PERMISSIVE = True

    def __init__(self, rows: int = 0, columns: int = 0, *args: Any) -> None:
        super().__init__(rows, columns, *args)
        self.rowCount = rows
        self.columnCount = columns
        self.cells: dict[tuple[int, int], TableItem] = {}
        self.headers: list[str] = []
        self.selected_rows: list[int] = []
        self.cell_widgets: dict[tuple[int, int], Any] = {}

    def selectionModel(self) -> NS:
        """Selection model that reports ``selected_rows`` as the chosen rows."""
        return NS(
            selectedRows=lambda: [NS(row=lambda r=r: r) for r in self.selected_rows]
        )

    def clear(self) -> None:
        self.cells.clear()
        self.headers = []

    def setColumnCount(self, count: int) -> None:
        self.columnCount = count

    def setCellWidget(self, row: int, column: int, widget: Any) -> None:
        self.cell_widgets[row, column] = widget

    def setRowCount(self, count: int) -> None:
        self.rowCount = count
        for key in [k for k in self.cells if k[0] >= count]:
            del self.cells[key]

    def setHorizontalHeaderLabels(self, labels: list[str]) -> None:
        self.headers = list(labels)

    def setItem(self, row: int, column: int, item: TableItem) -> None:
        item.table, item.position = self, (row, column)
        self.cells[row, column] = item

    def item(self, row: int, column: int) -> TableItem | None:
        return self.cells.get((row, column))

    def texts(self) -> list[list[str]]:
        """Return the table text row by row (blank where a cell is unset)."""
        return [
            [self.cells[r, c].text() if (r, c) in self.cells else "" for c in range(self.columnCount)]
            for r in range(self.rowCount)
        ]


class FileDialog(Dialog):
    SIGNALS = ("fileSelected", "finished", "destroyed")
    PERMISSIVE = True

    def __init__(self, *args: Any) -> None:
        super().__init__(*args)
        self.opened = 0
        self.selected: str | None = None

    def selectFile(self, name: str) -> None:
        self.selected = name

    def open(self) -> None:
        self.opened += 1

    def deleteLater(self) -> None:
        self.deleted = True


class Canvas(Widget):
    """Plain QWidget base used by Text Preview's Canvas."""

    def setMinimumSize(self, *args: Any) -> None:
        self.minimum_size = args


class Layout(Base):
    """Layout that keeps its children so count()/takeAt() behave."""

    PERMISSIVE = True

    def __init__(self, *args: Any) -> None:
        super().__init__(*args)
        self.items: list[Any] = []

    def addWidget(self, widget: Any, *args: Any) -> None:
        self.items.append(widget)

    def addLayout(self, layout: Any, *args: Any) -> None:
        self.items.append(layout)

    def insertWidget(self, index: int, widget: Any, *args: Any) -> None:
        self.items.insert(index, widget)

    def count(self) -> int:
        return len(self.items)

    def takeAt(self, index: int) -> NS:
        widget = self.items.pop(index)
        return NS(widget=lambda: widget)


class Point(Base):
    def __init__(self, x: float = 0, y: float = 0) -> None:
        super().__init__(x, y)
        self._x, self._y = x, y

    def x(self) -> float:
        return self._x

    def y(self) -> float:
        return self._y


class Timer(Base):
    SIGNALS = ("timeout",)
    PERMISSIVE = True

    def __init__(self, *args: Any) -> None:
        super().__init__(*args)
        self.active = False
        self.interval = 0

    def setInterval(self, value: int) -> None:
        self.interval = value

    def start(self) -> None:
        self.active = True

    def stop(self) -> None:
        self.active = False


class Namespace:
    """Module-like Qt namespace: explicit classes plus generated permissive ones."""

    def __init__(self, **explicit: Any) -> None:
        self.__dict__.update(explicit)
        self.__dict__["_made"] = {}

    def __getattr__(self, name: str) -> Any:
        if name.startswith("_"):
            raise AttributeError(name)
        made = self.__dict__["_made"]
        if name not in made:
            made[name] = type(name, (Generic,), {})
        return made[name]


def make_qt() -> NS:
    """Build a fake ``PythonQt`` module for the kerning and report scripts."""
    gui = Namespace(
        QDialog=Dialog,
        QWidget=Canvas,
        QLabel=Label,
        QLineEdit=LineEdit,
        QSpinBox=SpinBox,
        QDoubleSpinBox=SpinBox,
        QSlider=SpinBox,
        QCheckBox=CheckBox,
        QComboBox=ComboBox,
        QListWidget=ListWidget,
        QPushButton=PushButton,
        QTableWidget=TableWidget,
        QTableWidgetItem=TableItem,
        QFileDialog=FileDialog,
        QApplication=type("QApplication", (Application,), {"_clipboard": Clipboard()}),
        QColor=Color,
        QPalette=type("QPalette", (Palette,), {}),
        QPainterPath=PainterPath,
        QPainter=type("QPainter", (Painter,), {"created": []}),
        QFont=Font,
        QVBoxLayout=Layout,
        QHBoxLayout=Layout,
        QGridLayout=Layout,
    )
    core = Namespace(
        Qt=EnumNamespace(),
        QRectF=Rect,
        QPointF=Point,
        QTimer=Timer,
        QTime=NS(currentTime=lambda: NS(toString=lambda fmt: "12:34:56")),
    )
    return NS(QtGui=gui, QtCore=core)


# ---------------------------------------------------------------- kerning font
def side(name: str) -> NS:
    """Native pair side as FontLab reports it."""
    return NS(
        id=name.lstrip("@"), mode="groupMode" if name.startswith("@") else "glyphMode"
    )


class Kerning:
    """Mutable native kerning object: explicit pairs, classes and effective reads."""

    def __init__(self, pairs: dict, groups: dict) -> None:
        self.stored: dict[tuple, float] = {
            (self._typed(a), self._typed(b)): v for (a, b), v in pairs.items()
        }
        self.groups = groups
        self.scales: list[float] = []

    def __len__(self) -> int:
        return len(self.stored)

    @staticmethod
    def _typed(name: Any) -> tuple[str, str]:
        if isinstance(name, tuple):
            return name
        return (name[1:], "groupMode") if name.startswith("@") else (name, "glyphMode")

    def items(self) -> list:
        return [
            (NS(left=side(self._flat(a)), right=side(self._flat(b))), v)
            for (a, b), v in self.stored.items()
        ]

    @staticmethod
    def _flat(typed: tuple[str, str]) -> str:
        return ("@" if typed[1] == "groupMode" else "") + typed[0]

    def explicit(self) -> dict[tuple[str, str], float]:
        """Return pairs in the public ``@class`` notation."""
        return {(self._flat(a), self._flat(b)): v for (a, b), v in self.stored.items()}

    def get(self, pair: tuple[str, str]) -> float | None:
        """Native precedence: glyph pair, glyph/class, class/glyph, class/class."""
        left, right = pair
        lefts = [(left, "glyphMode")] + [
            (n, "groupMode")
            for n, (members, mode) in self.groups.items()
            if left in members and mode in ("KernLeft", "KernBothSide")
        ]
        rights = [(right, "glyphMode")] + [
            (n, "groupMode")
            for n, (members, mode) in self.groups.items()
            if right in members and mode in ("KernRight", "KernBothSide")
        ]
        for a in lefts[:1] + lefts[1:]:
            for b in rights:
                if (a, b) in self.stored:
                    return self.stored[a, b]
        return None

    def set(self, key: tuple, value: float) -> None:
        self.stored[key] = value

    def remove(self, key: tuple) -> None:
        del self.stored[key]

    def scale(self, factor: float) -> None:
        self.scales.append(factor)
        if factor != 1.0:
            for key in self.stored:
                self.stored[key] = self.stored[key] * factor


class Package:
    """Native package fake with masters, kerning and glyph lookup."""

    def __init__(self, masters: list[str], kern: dict[str, Kerning], widths: dict) -> None:
        self.id = 7
        self.fgId = 70
        self.isNull = False
        self.master = masters[-1]
        self.masters = list(masters)
        self.upm = 1000
        self.ascender_value = 800
        self.descender_value = -200
        self._kern = kern
        self.glyphs = {
            name: NS(
                name=name,
                isNull=False,
                findLayer=lambda master, width=width: NS(
                    isNull=False,
                    advanceWidth=width,
                    shapes=[
                        NS(
                            getContours=lambda: [NS(path=PainterPath)],
                            transform=NS(map=lambda part: part),
                        )
                    ],
                ),
            )
            for name, width in widths.items()
        }
        self.history: list[str] = []

    def kerning(self, master: str) -> Kerning:
        return self._kern[master]

    def findName(self, name: str) -> Any:
        return self.glyphs.get(name)

    def findUnicode(self, code: int) -> Any:
        return self.glyphs.get(chr(code))

    def mastersContainer(self) -> str:
        return "masters"

    def kerningContainer(self) -> str:
        return "kerning"

    def checkInitHistoryState(self, value: int) -> None:
        self.history.append(f"init{value}")

    def pairs(self, master: str) -> dict:
        """Explicit pairs on a master in public notation."""
        return self._kern[master].explicit()


GROUPS = {
    "L_A": (["A", "Aacute"], "KernLeft"),
    "R_V": (["V"], "KernRight"),
    "Both": (["X"], "KernBothSide"),
}
WIDTHS = {
    "A": 600,
    "Aacute": 600,
    "V": 650,
    "T": 500,
    "X": 550,
    "o": 520,
    "a": 500,
    "y": 480,
    "W": 900,
    "Y": 640,
    "F": 520,
    "L": 520,
    "P": 560,
    "e": 500,
    "s": 450,
    "u": 540,
}


def make_package(masters: tuple[str, ...] = ("Regular", "Bold")) -> Package:
    """Whole-unit kerning with a redundant exception, a small pair and class pairs."""
    regular = {
        ("@L_A", "@R_V"): -80,
        ("A", "@R_V"): -60,
        ("@L_A", "V"): -40,
        ("A", "V"): -60,
        ("T", "V"): 12,
        ("T", "o"): 3,
        ("V", "A"): -4,
        ("Aacute", "V"): 0,
    }
    bold = {
        ("@L_A", "@R_V"): -90,
        ("A", "V"): -70,
        ("T", "V"): 10,
        ("T", "o"): -3,
    }
    data = {"Regular": regular, "Bold": bold}
    kern = {
        m: Kerning(dict(data.get(m, bold)), {k: (list(v[0]), v[1]) for k, v in GROUPS.items()})
        for m in masters
    }
    return Package(list(masters), kern, WIDTHS)


# ---------------------------------------------------------------- environment
class Env:
    """Everything a kerning script needs: fake natives, real App helpers, loader."""

    def __init__(self, monkeypatch: Any, real_app: Any, package: Package | None) -> None:
        self.package = package
        self.updates = 0
        self.notified: list[tuple] = []
        self.copied: list[str] = []
        self.selected: set[int] = set()
        self.qt = make_qt()
        self.glyph_list = [NS(name=n) for n in (package.glyphs if package else [])]
        panel_parent = NS(inherits=lambda n: n == "YFrameWindow", parentWidget=lambda: None)
        self.panel = NS(
            inherits=lambda n: n == "FontWindow", parentWidget=lambda: panel_parent
        )
        env = self

        class Items:
            @staticmethod
            def notifyChangesApplied(name: str, items: list) -> None:
                env.notified.append((name, tuple(map(str, items))))

        fontlab = NS(
            flWorkspace=NS(
                instance=lambda: NS(
                    currentPackage=env.package, activeFontPanel=env.panel
                )
            ),
            flItems=Items,
            UpdateAll=self._update_all,
            MainWindow=lambda: "main-window",
            CurrentGlyph=lambda: None,
        )
        fl = NS(
            font=self.glyph_list,
            Unselect=self.selected.clear,
            Select=self.selected.add,
            Selected=lambda i: i in self.selected,
        )
        self.FL = NS(fl=fl)
        monkeypatch.setitem(sys.modules, "FL", self.FL)
        monkeypatch.setattr(sys, "_fontlab_samples", {}, raising=False)
        self.fontlab = fontlab
        loaded = real_app(
            qt=self.qt,
            fontlab=fontlab,
            completion=lambda dialog, key: None,
            modules=[
                "kerning_edit",
                "kerning_batch",
                "kerning_identity",
                "kerning_selection",
                "_names_dialog",
                "_kerning_dialog",
                "_kerning_edit_dialog",
                "_kerning_value_dialog",
            ],
        )
        self.scripting = loaded["scripting"]
        monkeypatch.setitem(
            sys.modules,
            "fly",
            NS(ap=NS(fontlab=fontlab, scripting=self.scripting, FL=self.FL), qt=self.qt),
        )
        monkeypatch.setitem(sys.modules, "fly.ap.scripting", self.scripting)
        self.modules: dict[str, Any] = {}

    def _update_all(self) -> None:
        self.updates += 1

    def load(self, folder: str, title: str) -> Any:
        """Execute a menu script from Scripts/<folder>/<title>.py under the fakes."""
        key = f"{folder}/{title}"
        spec = importlib.util.spec_from_file_location(
            f"cov_b_{title.replace(' ', '_')}", ROOT / "Scripts" / folder / f"{title}.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self.modules[key] = module
        return module

    def open(self, folder: str, title: str, cls: str) -> Any:
        """Load a script and construct its dialog class with no parent."""
        return getattr(self.load(folder, title), cls)()


def check_clean(dialog: Any) -> None:
    """Assert that no guarded slot swallowed an error."""
    error = getattr(dialog, "slot_error", None)
    assert error is None, f"A guarded slot swallowed an error: {error}"


def row_texts(table: TableWidget) -> list[list[str]]:
    """Return table text for assertions."""
    return table.texts()


# ---------------------------------------------------------------- report font
class Node:
    def __init__(self, x: float, y: float, on: bool = True) -> None:
        self.x, self.y, self.on = x, y, on

    def isOn(self) -> bool:
        return self.on


class Contour:
    def __init__(self, nodes: list, closed: bool = True) -> None:
        self._nodes, self.closed = nodes, closed

    def nodes(self) -> list:
        return self._nodes


class Transform:
    def __init__(self, dx: float = 0, dy: float = 0) -> None:
        self.dx, self.dy = dx, dy

    def map(self, point: Point) -> Point:
        return Point(point.x() + self.dx, point.y() + self.dy)


class Shape:
    """A drawn shape (contours) or a component reference (base glyph name)."""

    def __init__(self, contours: list | None = None, base: str = "", dx: float = 0) -> None:
        self._contours = contours or []
        self.shapeData = NS(componentGlyph=base) if base else None
        self.transform = Transform(dx)

    def getContours(self) -> list:
        return self._contours


class Layer:
    def __init__(
        self,
        width: float,
        shapes: list | None = None,
        box: tuple = (0, 0, 0, 0),
        anchors: int = 0,
    ) -> None:
        self.advanceWidth = width
        self.shapes = shapes or []
        self.boundingBox = NS(
            x=lambda: box[0], y=lambda: box[1], width=lambda: box[2], height=lambda: box[3]
        )
        self.anchors = [object()] * anchors

    def getContours(self) -> list:
        return [c for shape in self.shapes for c in shape.getContours()]


def square(x: float = 50, y: float = 0, size: float = 400, closed: bool = True) -> Contour:
    """A four-node contour starting at ``(x, y)``."""
    return Contour(
        [Node(x, y), Node(x + size, y), Node(x + size, y + size), Node(x, y + size)],
        closed,
    )


class Glyph:
    def __init__(
        self,
        name: str,
        unicodes: list,
        layers: dict,
        mark: int = 0,
        note: str = "",
    ) -> None:
        self.name, self.unicodes, self.mark, self.note = name, unicodes, mark, note
        self.layers = layers
        self.isNull = False
        self.fgGlyph = NS(unicodes=unicodes)

    def findLayer(self, master: str) -> Layer | None:
        return self.layers.get(master)


class ReportPackage:
    """Package with drawn glyphs, metrics and a kerning count for the report tools."""

    def __init__(self, glyphs: list[Glyph], masters: tuple = ("Regular", "Bold")) -> None:
        self.id = 11
        self.fgId = 110
        self.isNull = False
        self.masters = list(masters)
        self.master = masters[-1]
        self.upm = 1000.0
        self.info = NS(familyName="Sample Sans")
        self.glyphs = {g.name: g for g in glyphs}
        self._kern = {m: Kerning({("A", "V"): -50} if m == "Bold" else {}, {}) for m in masters}

    def findName(self, name: str) -> Glyph | None:
        return self.glyphs.get(name)

    def kerning(self, master: str) -> Kerning:
        return self._kern[master]


METRICS = {
    "Regular": NS(ascender=750, capsHeight=700, xHeight=500, descender=-200),
    "Bold": NS(ascender=760, capsHeight=710, xHeight=510, descender=-210),
}


def make_report_package() -> ReportPackage:
    """A small font exercising empty, partial, open, composite and near-zone glyphs."""
    both = lambda w, shapes=None, box=(50, 0, 400, 400): {  # noqa: E731
        m: Layer(w, list(shapes or []), box if shapes else (0, 0, 0, 0)) for m in ("Regular", "Bold")
    }
    acute_layers = both(300, [Shape([square(10, 600, 100)])], (10, 600, 100, 100))
    acute_layers["Bold"] = Layer(300)
    a_open = both(600, [Shape([square(50, 0, 400)])])
    a_open["Bold"] = Layer(
        620,
        [Shape([square(50, 0, 400), square(60, 10, 100, closed=False)])],
        (50, 0, 400, 400),
        anchors=2,
    )
    x_layers = both(
        500,
        [
            Shape(
                [
                    Contour(
                        [
                            Node(10, 3),
                            Node(20, 497),
                            Node(30, 0),
                            Node(40, 503, on=False),
                            Node(50, 506),
                            Node(60, 700),
                        ]
                    )
                ]
            ),
            Shape([square(10, 600, 100)], base="acute", dx=100),
        ],
    )
    glyphs = [
        Glyph(".notdef", [], both(500)),
        Glyph("space", [32], both(250)),
        Glyph("period", [46], both(250)),
        Glyph("acute", [0xB4], acute_layers, mark=5),
        Glyph("A", [65], a_open, mark=100, note="check"),
        Glyph("A.ss01", [], both(600, [Shape([square()])]), mark=1100),
        Glyph(
            "Aacute",
            [0xC1],
            both(
                600,
                [
                    Shape([square()], base="A"),
                    Shape([square(10, 600, 100)], base="acute", dx=50),
                ],
            ),
            note="  ",
        ),
        Glyph("x", [120], x_layers),
        Glyph("Euro", [0x20AC, 0x20000], both(550, [Shape([square()])])),
        Glyph("zero.zero", [0x200B], both(0)),
    ]
    return ReportPackage(glyphs)


class ReportEnv(Env):
    """Kerning ``Env`` plus the FontLab calls that the report tools use."""

    def __init__(self, monkeypatch: Any, real_app: Any, package: Any = "default") -> None:
        if package == "default":
            package = make_report_package()
        super().__init__(monkeypatch, real_app, package)
        self.current_glyph: Any = None
        fontlab = self.fontlab
        fontlab.CurrentFont = lambda: (
            NS(glyphs=list(self.package.glyphs.values())) if self.package else None
        )
        fontlab.FontMetrics = lambda package, master: METRICS[master]
        fontlab.CurrentGlyph = lambda: self.current_glyph

    def select(self, *names: str) -> None:
        """Select glyphs in the Font window by name."""
        order = [g.name for g in self.glyph_list]
        self.selected.clear()
        self.selected.update(order.index(n) for n in names)
