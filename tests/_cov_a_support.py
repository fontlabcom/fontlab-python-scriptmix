# this_file: tests/_cov_a_support.py
# SPDX-License-Identifier: Apache-2.0
"""Host-free Qt and FontLab doubles for the dialog-style Scriptmix scripts.

The doubles model only what the scripts under test read: PythonQt exposes Qt
properties as attributes (``line.text``, ``combo.currentIndex``) and Qt methods
as callables (``table.currentRow()``). Unknown Qt calls are accepted and
recorded so layout code runs, while the widgets that carry state are real
Python objects. The real installed App base classes run on top of these
doubles, so each script is exercised through its true panel lifecycle.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType
from types import SimpleNamespace as NS
from typing import Any
from unittest.mock import MagicMock

import pytest

ROOT = Path(__file__).resolve().parents[1]
SIGNALS = frozenset(
    {
        "textChanged", "clicked", "toggled", "currentIndexChanged", "itemSelectionChanged",
        "valueChanged", "stateChanged", "currentTextChanged", "itemChanged", "cellChanged",
        "editingFinished", "returnPressed", "activated", "finished", "timeout",
        "itemDoubleClicked", "currentItemChanged", "triggered", "cellClicked", "itemClicked",
        "selectionChanged", "currentRowChanged", "currentCellChanged", "fileSelected", "cellDoubleClicked", "textEdited", "accepted", "rejected",
    }
)


_ENUMS: dict[str, int] = {}


class Enum(int):
    """Qt enum stand-in: an int that tolerates being called like a flag factory."""

    def __call__(self, *args: Any) -> None:
        return None


def enum_value(name: str) -> Enum:
    """Return a stable, distinct integer for an enum name (flags can be OR-ed)."""
    if name not in _ENUMS:
        _ENUMS[name] = 1 << len(_ENUMS) if len(_ENUMS) < 60 else 1000 + len(_ENUMS)
    return Enum(_ENUMS[name])


class _Meta(type):
    """Capitalised class attributes (``Qt.AlignRight``) are distinct enum values."""

    def __getattr__(cls, name: str) -> Any:
        if name[:1].isupper():
            return enum_value(name)
        raise AttributeError(name)


class Signal:
    """Minimal Qt signal: records slots and runs them on emit."""

    def __init__(self) -> None:
        self.slots: list[Any] = []

    def connect(self, slot: Any) -> None:
        self.slots.append(slot)

    def disconnect(self, slot: Any) -> None:
        self.slots.remove(slot)

    def emit(self, *args: Any) -> None:
        for slot in list(self.slots):
            slot(*args)


#: Real Qt methods the scripts call that carry no state worth modelling. Qt setters
#: (``set*``) are accepted too. Any other unknown attribute raises AttributeError,
#: as a PythonQt wrapper would.
QT_METHODS = frozenset(
    {
        "addWidget", "addLayout", "addStretch", "insertLayout", "insertWidget", "hide", "count",
        "verticalHeader", "horizontalHeader", "viewport", "resize", "update", "raise_", "open",
        "start", "textCursor", "end", "drawRoundedRect", "font", "fill", "stop", "deleteLater", "addPath",
    }
)


class Widget(metaclass=_Meta):
    """Widget double: signals are real, Qt setters and listed methods are recorded mocks."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.init_args = args
        self._enabled = True

    def __getattr__(self, name: str) -> Any:
        if name in SIGNALS:
            value: Any = Signal()
        elif name.startswith("set") or name in QT_METHODS:
            value = MagicMock(name=name)
        else:
            raise AttributeError(f"{type(self).__name__!r} object has no attribute {name!r}")
        self.__dict__[name] = value
        return value

    @property
    def palette(self) -> Palette:
        return Palette()

    def setEnabled(self, flag: bool) -> None:
        self._enabled = bool(flag)

    def isEnabled(self) -> bool:
        return self._enabled

    @property
    def enabled(self) -> bool:
        return self._enabled


class Color(Widget):
    """QColor double: a fixed hex name keeps string concatenation honest."""

    @staticmethod
    def fromHsl(hue: int, saturation: int, lightness: int) -> Color:  # noqa: N802
        color = Color()
        color.init_args = ("hsl", hue, saturation, lightness)
        return color

    def name(self, *args: Any) -> str:
        return "#102030"


class Palette(Widget):
    def color(self, role: Any) -> Color:
        return Color()


class Label(Widget):
    def __init__(self, text: str = "", *args: Any) -> None:
        super().__init__(text, *args)
        self.text = text

    def setText(self, text: str) -> None:
        self.text = text


class Button(Label):
    pass


class LineEdit(Widget):
    """QLineEdit: ``text`` is a property whose assignment emits ``textChanged``."""

    def __init__(self, text: str = "", *args: Any) -> None:
        super().__init__(text, *args)
        self._value = text

    @property
    def text(self) -> str:
        return self._value

    @text.setter
    def text(self, text: str) -> None:
        changed = text != self._value
        self._value = text
        if changed:
            self.textChanged.emit(text)

    def setText(self, text: str) -> None:
        self.text = text


class PlainText(Widget):
    def __init__(self, *args: Any) -> None:
        super().__init__(*args)
        self.plain = ""
        self.html = ""
        self.found: list[str] = []
        self.find_results: list[bool] = []

    def setPlainText(self, text: str) -> None:
        changed = text != self.plain
        self.plain = text
        if changed:
            self.textChanged.emit()

    def toPlainText(self) -> str:
        return self.plain

    def setHtml(self, html: str) -> None:
        self.html = html

    def find(self, text: str) -> bool:
        self.found.append(text)
        return self.find_results.pop(0) if self.find_results else True


class CheckBox(Widget):
    def __init__(self, text: str = "", *args: Any) -> None:
        super().__init__(text, *args)
        self.label = text
        self.checked = False

    def isChecked(self) -> bool:
        return self.checked

    def setChecked(self, flag: bool) -> None:
        changed = bool(flag) != self.checked
        self.checked = bool(flag)
        if changed:
            self.toggled.emit(self.checked)


class ComboBox(Widget):
    def __init__(self, *args: Any) -> None:
        super().__init__(*args)
        self.items: list[str] = []
        self._index = -1

    @property
    def currentIndex(self) -> int:
        return self._index

    @currentIndex.setter
    def currentIndex(self, index: int) -> None:
        changed = index != self._index
        self._index = index
        if changed:
            self.currentIndexChanged.emit(index)

    def addItem(self, text: str, *data: Any) -> None:
        self.items.append(text)
        if self._index < 0:
            self._index = 0

    def addItems(self, texts: list[str]) -> None:
        for text in texts:
            self.addItem(text)

    def clear(self) -> None:
        self.items.clear()
        self._index = -1

    def count(self) -> int:
        return len(self.items)

    def itemText(self, index: int) -> str:
        return self.items[index]

    @property
    def currentText(self) -> str:
        return self.items[self.currentIndex] if 0 <= self.currentIndex < len(self.items) else ""

    def setCurrentIndex(self, index: int) -> None:
        self.currentIndex = index


class Font(Widget):
    """QFont double with a real point size so size arithmetic works."""

    def __init__(self, *args: Any) -> None:
        super().__init__(*args)
        self.size = 10.0

    def pointSizeF(self) -> float:
        return self.size

    def setPointSizeF(self, size: float) -> None:
        self.size = size


class ListItem(Widget):
    def __init__(self, text: str = "", *args: Any) -> None:
        super().__init__(text, *args)
        self._text = text

    def text(self) -> str:
        return self._text


class ListWidget(Widget):
    def __init__(self, *args: Any) -> None:
        super().__init__(*args)
        self.entries: list[str] = []

    def addItem(self, item: Any) -> None:
        self.entries.append(item.text())

    def clear(self) -> None:
        self.entries.clear()

    def count(self) -> int:
        return len(self.entries)


class TableItem(Widget):
    def __init__(self, *args: Any) -> None:
        super().__init__(*args)
        # QTableWidgetItem(text) or QTableWidgetItem(icon, text)
        self._text = next((a for a in reversed(args) if isinstance(a, str)), "")

    def text(self) -> str:
        return self._text

    def setText(self, text: str) -> None:
        self._text = text


class Count(int):
    """Qt count that PythonQt exposes as a property but older code also calls."""

    def __call__(self) -> int:
        return int(self)


class Table(Widget):
    def __init__(self, rows: int = 0, columns: int = 0, *args: Any) -> None:
        super().__init__(rows, columns, *args)
        self.cells: dict[tuple[int, int], Any] = {}
        self.rows_count = rows
        self.current = -1
        self.selected_rows: list[int] = []

    def setRowCount(self, count: int) -> None:
        self.rows_count = count
        self.cells = {key: item for key, item in self.cells.items() if key[0] < count}
        if self.current >= count:
            self.current = -1

    @property
    def rowCount(self) -> Count:
        return Count(self.rows_count)

    def setCurrentCell(self, row: int, column: int) -> None:
        self.current = row
        self.currentCellChanged.emit(row, column, -1, -1)

    def setItem(self, row: int, column: int, item: Any) -> None:
        self.cells[(row, column)] = item

    def item(self, row: int, column: int) -> Any:
        return self.cells.get((row, column))

    def row_texts(self, row: int) -> list[str]:
        columns = sorted(c for r, c in self.cells if r == row)
        return [self.cells[(row, c)].text() for c in columns]

    def currentRow(self) -> int:
        return self.current

    def selectRow(self, row: int) -> None:
        self.current = row
        self.itemSelectionChanged.emit()

    def selectionModel(self) -> NS:
        return NS(selectedRows=lambda: [NS(row=lambda r=r: r) for r in self.selected_rows])

    def clearSelection(self) -> None:
        self.current = -1
        self.itemSelectionChanged.emit()


class Namespace:
    """Lazy ``QtGui``/``QtCore`` module: known classes plus generic widgets."""

    def __init__(self, known: dict[str, Any]) -> None:
        self.__dict__["_known"] = dict(known)

    def __getattr__(self, name: str) -> Any:
        if name.startswith("__"):
            raise AttributeError(name)
        known = self.__dict__["_known"]
        if name not in known:
            known[name] = type(name, (Widget,), {})
        return known[name]

    def __setattr__(self, name: str, value: Any) -> None:
        self.__dict__["_known"][name] = value


class Dialog(Widget):
    """QDialog base: lifecycle calls succeed, ``close`` honours ``close_result``."""

    close_result = True

    def __init__(self, parent: Any = None, *args: Any) -> None:
        super().__init__(parent, *args)
        self.parent_widget = parent
        self.shown = False

    def show(self) -> None:
        self.shown = True

    def close(self) -> bool:
        self.closed = True
        return self.close_result

    def closeEvent(self, event: Any) -> None:
        self.base_close_event = event


def make_qt() -> NS:
    """Return ``NS(QtCore, QtGui)`` doubles sharing one widget vocabulary."""
    gui = Namespace(
        {
            "QDialog": Dialog,
            "QColor": Color,
            "QLabel": Label,
            "QPushButton": Button,
            "QLineEdit": LineEdit,
            "QPlainTextEdit": PlainText,
            "QTextEdit": PlainText,
            "QCheckBox": CheckBox,
            "QFont": Font,
            "QListWidget": ListWidget,
            "QListWidgetItem": ListItem,
            "QComboBox": ComboBox,
            "QTableWidget": Table,
            "QTableWidgetItem": TableItem,
        }
    )
    core = Namespace({})
    return NS(QtCore=core, QtGui=gui)


class Host:
    """One owned FontLab session: package, font, glyph and the loaded modules."""

    def __init__(self, monkeypatch: pytest.MonkeyPatch, real_app: Any) -> None:
        self.mp = monkeypatch
        self.real_app = real_app
        self.package: Any = None
        self.font: Any = None
        self.glyph: Any = None
        self.qt = make_qt()
        self.main_window = object()
        self.FL = NS(fl=NS(font=[]))
        self.native = NS(
            CurrentFont=lambda: self.font,
            CurrentGlyph=lambda: self.glyph,
            MainWindow=lambda: self.main_window,
        )
        self.mp.setattr(sys, "_fontlab_samples", {}, raising=False)

    def load(
        self,
        relative: str,
        *,
        modules: tuple[str, ...] = (),
        fp_blocks: Any = None,
        scripting: dict[str, Any] | None = None,
        patches: dict[str, dict[str, Any]] | None = None,
        name: str = "cov_a_script",
    ) -> ModuleType:
        """Import ``Scripts/<relative>`` over the real App helpers and the doubles."""
        shared = {"current_package": lambda expected_id=None: self._current(expected_id)}
        shared.update(scripting or {})
        loaded = self.real_app(
            qt=NS(QtCore=self.qt.QtCore, QtGui=self.qt.QtGui),
            fontlab=self.native,
            scripting=shared,
            completion=lambda dialog, key: NS(),
            modules=list(modules),
        )
        for module_name, attributes in (patches or {}).items():
            for attribute, value in attributes.items():
                self.mp.setattr(loaded[module_name], attribute, value)
        fly = ModuleType("fly")
        fly.ap = NS(fontlab=self.native, FL=self.FL, **loaded)
        fly.qt = self.qt
        self.mp.setitem(sys.modules, "fly", fly)
        self.mp.setitem(sys.modules, "fly.ap", fly.ap)
        if fp_blocks is not None:
            self.mp.setitem(sys.modules, "fly.fp", NS(feature_blocks=fp_blocks))
            self.mp.setitem(sys.modules, "fly.fp.feature_blocks", fp_blocks)
        self.loaded = loaded
        self.fly = fly
        spec = importlib.util.spec_from_file_location(name, ROOT / "Scripts" / relative)
        assert spec is not None and spec.loader is not None, f"No loader for {relative}"
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def fake_ap(self, name: str, **attributes: Any) -> NS:
        """Register fly.ap.<name> as a module double (import and attribute routes)."""
        module = NS(**attributes)
        self.mp.setitem(sys.modules, f"fly.ap.{name}", module)
        self.mp.setattr(self.fly.ap, name, module, raising=False)
        return module

    def _current(self, expected_id: int | None) -> Any:
        if self.package is None:
            return None
        if expected_id is not None and self.package.id != expected_id:
            return None
        return self.package

    def windows(self) -> dict[str, Any]:
        """Return the owned-window registry that ``show_script_dialog`` fills."""
        return sys._fontlab_samples  # noqa: SLF001 - the documented registry


@pytest.fixture
def host(monkeypatch: pytest.MonkeyPatch, real_app: Any) -> Host:
    """Provide a fresh owned FontLab session double for one test."""
    return Host(monkeypatch, real_app)


def glyph_names(*names: str) -> NS:
    """Return a font double whose ``glyphs`` carry the given names."""
    return NS(glyphs=[NS(name=n) for n in names])
