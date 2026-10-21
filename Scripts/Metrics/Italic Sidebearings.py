# this_file: Scripts/Metrics/Italic Sidebearings.py
# SPDX-License-Identifier: Apache-2.0
"""Report and set sidebearings along the italic angle.

What it does: shows two pairs of sidebearings for each layer. The plain pair
is the distance from the advance edge to the ink, measured sideways. The
italic pair is measured after the outline is de-slanted by the italic angle.
You can add to the italic values or set them.

How it works: the script maps the outline through a shear around the height
"measured at" (half of the x-height by default). The sheared outline gives
the italic edges. A change moves the real outline sideways and changes the
advance. Anchors move with the outline. All values are whole units.

Why: in a slanted design the plain sidebearings depend on the overhang of the
slant. The italic sidebearings let you compare and space an italic "n" and
"o" as if they were upright.

How to use: select glyphs in the Font window. Check the angle and the height.
Choose "Add" or "Set". Tick LSB and RSB and enter the values. Choose the
current master or all masters. Check the table. Press Apply. The panel stays
open. Press "Use selection" to read the Font window selection again.

Safety: one Apply is one Undo step. Auto layers are listed and never edited.
Layers with a metrics link or expression are listed and skipped. A base of
auto glyphs is refused, because FontLab rebuilds the auto glyphs and may lose
their anchors and locks (FontLab issue 8512). Tick "Edit bases of auto glyphs
anyway" to go on. After the write the script reads advance and outline back
and reports any mismatch. It does not call UpdateAll (FontLab issue 8537).
Native Undo/Redo/reopen of in-place moves is pending.

Benefit: you space italics with the same method as upright designs.

Credit: independent rewrite of the author's own rescued FontLab sample
metrics_italic_sidebearings.py (Apache-2.0).
"""

import math
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from fly import ap, qt
from fly.ap.script_completion import install
from fly.ap.scripting import (
    close_script_dialog,
    connect_guarded,
    current_package,
    names_selected_names,
    show_script_dialog,
)

QtCore, QtGui = qt.QtCore, qt.QtGui
fontlab = ap.fontlab

MAX_ROWS = 400  # Table rows shown. Larger plans still apply in full.
MAX_NAMES = 8  # Glyph names shown in the subtitle.
NOTE_LIMIT = 5  # Auto composites named in the rebuild note.
ALLOW_AUTO_LABEL = "Edit bases of auto glyphs anyway"
READ_BACK_TOLERANCE = 0.5  # Units. The outline edge may differ by rounding.


# ---------------------------------------------------------------- plan model
@dataclass(frozen=True)
class LayerPlan:
    """One planned layer edit.

    dx: units to move the outline sideways. width: new advance width in units.
    cells: preview texts that follow the glyph label. changed: False for no-ops.
    """

    dx: int
    width: int
    cells: tuple[str, ...]
    changed: bool


# A planner returns a LayerPlan, or a short text that explains why it skips the layer.
Planner = Callable[[Any, str], LayerPlan | str]


@dataclass
class Entry:
    """One glyph/master layer with its plan or its skip note."""

    glyph: Any
    master: str
    layer: Any
    plan: LayerPlan | None
    note: str


def unit(value: float) -> int:
    """Round half up to a whole unit. Python round() rounds half to even."""
    return math.floor(value + 0.5)


def make_plan(layer: Any, dx: int, width: int, cells: tuple[str, ...]) -> LayerPlan:
    """Build a plan. It is a no-op when the outline and the advance stay as they are."""
    return LayerPlan(dx, width, cells, bool(dx) or width != layer.advanceWidth)


def ink_edges(layer: Any) -> tuple[float, float] | None:
    """Left and right edge of the layer outline, or None for an empty layer."""
    box = layer.boundingBox
    if box.width() <= 0 and box.height() <= 0:
        return None
    return box.x(), box.x() + box.width()


def master_layers(glyph: Any, masters: list[str]) -> dict[str, Any]:
    """Map master name to layer for the masters that this glyph has."""
    found: dict[str, Any] = {}
    for master in masters:
        layer = glyph.findLayer(master)
        if layer is not None and not layer.isNull:
            found[master] = layer
    return found


LINK_FIELDS = ("metricsLeft", "metricsRight", "metricsWidth")


def has_metrics_link(layer: Any) -> bool:
    """True when a sidebearing or width holds a link or an expression."""
    return any(str(getattr(layer, field)) for field in LINK_FIELDS)


def survey(glyphs: list[Any], masters: list[str], planner: Planner) -> list[Entry]:
    """Plan every layer. Auto, linked and missing layers are listed and never edited."""
    entries: list[Entry] = []
    for glyph in glyphs:
        for master in masters:
            layer = glyph.findLayer(master)
            if layer is None or layer.isNull:
                entries.append(
                    Entry(glyph, master, None, None, "no layer in this master")
                )
            elif layer.autoLayer:
                entries.append(
                    Entry(glyph, master, layer, None, "auto layer (skipped)")
                )
            elif has_metrics_link(layer):
                entries.append(
                    Entry(
                        glyph,
                        master,
                        layer,
                        None,
                        "metrics link or expression (skipped)",
                    )
                )
            else:
                result = planner(layer, master)
                if isinstance(result, str):
                    entries.append(Entry(glyph, master, layer, None, result))
                else:
                    entries.append(Entry(glyph, master, layer, result, ""))
    return entries


def pending(entries: list[Entry]) -> list[Entry]:
    """Entries that change the font."""
    return [e for e in entries if e.plan is not None and e.plan.changed]


def shift_and_set(layer: Any, dx: int, width: int) -> None:
    """Move the outline by dx units in place, anchors included, then set the advance."""
    if dx:
        layer.applyTransform(QtGui.QTransform(1, 0, 0, 1, dx, 0))
        layer.changed()
        if layer.update() is False:
            raise RuntimeError("FontLab could not update the layer geometry.")
    layer.advanceWidth = width


def read_back(entry: Entry, before: tuple[float, float] | None) -> list[str]:
    """Compare the written layer with its plan. Return one text per mismatch."""
    label = f"{entry.glyph.name} · {entry.master}"
    layer, plan = entry.layer, entry.plan
    found = []
    if layer.advanceWidth != plan.width:
        found.append(f"{label}: advance {layer.advanceWidth:g}, planned {plan.width}")
    after = ink_edges(layer)
    if before is not None and after is not None:
        want = before[0] + plan.dx
        if abs(after[0] - want) > READ_BACK_TOLERANCE:
            found.append(f"{label}: ink edge {after[0]:g}, planned {want:g}")
    return found


def commit(title: str, entries: list[Entry]) -> dict[str, Any]:
    """Apply all pending plans as one Undo step. Report what the font now holds.

    Order: 1. Start the history state of every layer and glyph. 2. Stamp the
    glyphs with one UTC time. 3. Edit. 4. Stamp again. 5. Notify FontLab once,
    with layers and glyphs in one list. 6. Stamp again, because window observers
    stamp after the capture (FontLab issue 8537). The notification runs even if an
    edit fails. Auto layers never enter the list: a notification for them makes
    FontLab rebuild every auto layer in the font. After the write the function
    reads advance and outline edge back and lists every mismatch.
    """
    todo = pending(entries)
    skipped = sum(1 for e in entries if e.note == "auto layer (skipped)")
    if not todo:
        return {"layers": 0, "glyphs": 0, "auto_skipped": skipped, "mismatches": []}
    glyphs: dict[str, Any] = {}
    for entry in todo:
        glyphs.setdefault(entry.glyph.name, entry.glyph)
    owners = list(glyphs.values())
    items = [e.layer for e in todo] + owners
    edges = [ink_edges(e.layer) for e in todo]
    for item in items:
        item.checkInitHistoryState(0)
    stamp = QtCore.QDateTime.currentDateTimeUtc()
    try:
        for glyph in owners:
            glyph.lastModified = stamp
        for entry in todo:
            shift_and_set(entry.layer, entry.plan.dx, entry.plan.width)
        for glyph in owners:
            glyph.lastModified = stamp
    finally:
        try:
            fontlab.flItems().notifyChangesApplied(title, items)
        finally:
            for glyph in owners:  # Window observers stamp after the history capture.
                glyph.lastModified = stamp
    mismatches = [text for e, b in zip(todo, edges) for text in read_back(e, b)]
    return {
        "layers": len(todo),
        "glyphs": len(glyphs),
        "auto_skipped": skipped,
        "mismatches": mismatches,
    }


# ---------------------------------------------------------------- auto composites
def auto_dependants(package: Any, names: set[str]) -> list[str]:
    """Names of glyphs with an auto master layer that uses one of names as component."""
    if package is None or not names:
        return []
    font, found = ap.FL.fl.font, []
    for index in range(len(font)):
        glyph = package.findName(font[index].name)
        if glyph is None or glyph.name in names:
            continue
        for layer in glyph.layers:
            if (
                layer.isMasterLayer
                and layer.autoLayer
                and any(
                    shape.isComponent and str(shape.shapeData.componentGlyph) in names
                    for shape in layer.shapes
                )
            ):
                found.append(glyph.name)
                break
    return found


def rebuild_note(found: list[str]) -> str:
    """Warn that FontLab rebuilds auto composites when it is told about their bases."""
    if not found:
        return ""
    shown = ", ".join(found[:NOTE_LIMIT])
    if len(found) > NOTE_LIMIT:
        shown += f" +{len(found) - NOTE_LIMIT} more"
    return (
        f"FontLab rebuilds auto glyphs {shown}; their anchors and locks may change "
        "and Undo does not restore them"
    )


# ---------------------------------------------------------------- panel
def muted(widget: Any) -> str:
    """Dimmed text colour taken from the widget palette."""
    color = QtGui.QColor(widget.palette.color(QtGui.QPalette.WindowText))
    color.setAlpha(150)
    return color.name(QtGui.QColor.HexArgb)


def make_table(headers: list[str]) -> Any:
    """Read-only preview table with a stretched layout."""
    table = QtGui.QTableWidget(0, len(headers))
    table.setHorizontalHeaderLabels(headers)
    table.verticalHeader().setVisible(False)
    table.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
    table.setSelectionMode(QtGui.QAbstractItemView.NoSelection)
    table.setAlternatingRowColors(True)
    table.setShowGrid(False)
    header = table.horizontalHeader()
    header.setSectionResizeMode(QtGui.QHeaderView.Stretch)
    header.setSectionResizeMode(0, QtGui.QHeaderView.ResizeToContents)
    table.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
    table.setMinimumHeight(220)
    return table


class MetricsPanel(QtGui.QDialog):
    """Non-modal panel: controls, live preview table, Apply, Close.

    A subclass sets TITLE, KEY, HEADERS, ACCENT and fills in build(),
    subtitle_hint(), target_glyphs() and planner(). Every control change
    recomputes the preview. Apply plans again from the live font, so the
    result never uses a stale preview.
    """

    TITLE = ""
    KEY = ""
    HEADERS: tuple[str, ...] = ()
    ACCENT: tuple[int, ...] = ()  # Table columns shown in bold accent colour.
    MIN_WIDTH = 560

    def __init__(self, parent: Any = None) -> None:
        """Build all widgets first. Read the font only after the Close button exists."""
        QtGui.QDialog.__init__(self, parent)
        self._connections: list[Any] = []
        self._completion_lifetime = install(self, self.KEY)
        self.entries: list[Entry] = []
        self.names: list[str] = []
        self.package_id: int | None = None
        self.last_result: dict[str, Any] = {}
        self._override_for: frozenset[str] | None = None
        self._rebuild_cache: dict[frozenset, str] = {}
        palette = self.palette  # FontLab may pair a light Base with a light Text.
        palette.setColor(QtGui.QPalette.Text, palette.color(QtGui.QPalette.WindowText))
        self.setPalette(palette)
        ink = palette.color(QtGui.QPalette.WindowText).name()
        self.setStyleSheet(f"QAbstractSpinBox, QAbstractItemView {{ color: {ink}; }}")
        self.setWindowTitle(self.TITLE)
        self.setMinimumWidth(self.MIN_WIDTH)

        root = QtGui.QVBoxLayout(self)
        root.setContentsMargins(20, 18, 20, 16)
        root.setSpacing(12)
        heading = QtGui.QLabel(self.TITLE)
        font = heading.font
        font.setPointSizeF(font.pointSizeF() * 1.35)
        font.setBold(True)
        heading.setFont(font)
        root.addWidget(heading)
        self.subtitle = QtGui.QLabel()
        self.subtitle.setWordWrap(True)
        self.subtitle.setStyleSheet(f"color: {muted(self)};")
        root.addWidget(self.subtitle)
        self.form = QtGui.QGridLayout()
        self.form.setHorizontalSpacing(10)
        self.form.setVerticalSpacing(8)
        self.form.setColumnStretch(1, 1)
        root.addLayout(self.form)
        self.scope = QtGui.QComboBox()
        self.scope.addItem("Current master")
        self.scope.addItem("All masters")
        self.form.addWidget(QtGui.QLabel("Masters"), 0, 0)
        self.form.addWidget(self.scope, 0, 1, 1, 3)
        self.table = make_table(["Glyph · master", *self.HEADERS])
        self.allow_auto = QtGui.QCheckBox(ALLOW_AUTO_LABEL)
        self.allow_auto.setVisible(False)
        footer = QtGui.QHBoxLayout()
        self.status = QtGui.QLabel()
        self.status.setWordWrap(True)
        self.status.setStyleSheet(f"color: {muted(self)};")
        footer.addWidget(self.status, 1)
        self.selection_button = QtGui.QPushButton("Use selection")
        self.close_button = QtGui.QPushButton("Close")
        self.apply_button = QtGui.QPushButton("Apply")
        self.apply_button.setDefault(True)
        for button in (self.selection_button, self.close_button, self.apply_button):
            footer.addWidget(button)
        self.build()
        root.addWidget(self.table, 1)
        root.addWidget(self.allow_auto)
        root.addLayout(footer)
        connect_guarded(
            self, self.allow_auto.toggled, lambda *a: self.override_toggled()
        )
        connect_guarded(self, self.scope.currentIndexChanged, lambda *a: self.refresh())
        connect_guarded(self, self.selection_button.clicked, lambda *a: self.reselect())
        connect_guarded(self, self.apply_button.clicked, lambda *a: self.apply())
        connect_guarded(self, self.close_button.clicked, lambda *a: self.close())
        try:
            package = current_package()
            if package is not None:
                self.package_id = package.id
                self.names = names_selected_names()
            self.refresh()
        except Exception as error:  # noqa: BLE001 - keep a failed panel visible and closable
            self.status.setText(f"Error: {error!r}")

    # ----- hooks for subclasses
    def build(self) -> None:
        """Create the controls. Add them to self.form from row 1 on; row 0 holds the masters."""
        raise NotImplementedError

    def subtitle_hint(self) -> str:
        """One sentence that says what the current settings will do."""
        raise NotImplementedError

    def target_glyphs(self, package: Any) -> list[Any]:
        """Glyphs to edit. The default is the captured selection."""
        found = [package.findName(name) for name in self.names]
        return [g for g in found if g is not None and not g.isNull]

    def planner(self, package: Any, glyphs: list[Any]) -> Planner:
        """Return the function that plans one layer."""
        raise NotImplementedError

    def empty_message(self) -> str:
        """Reason shown when no glyph qualifies."""
        return "Select glyphs in the Font window. Then press Use selection."

    def sync_controls(self) -> None:
        """Enable or disable controls to match the other controls. Default: nothing."""

    # ----- helpers for subclasses
    def watch(self, signal: Any) -> None:
        """Refresh the preview whenever this signal fires."""
        connect_guarded(self, signal, lambda *a: self.refresh())

    def spin(self, low: int, high: int, value: int, suffix: str = "") -> Any:
        """Right-aligned integer spin box that refreshes the preview."""
        box = QtGui.QSpinBox()
        box.setRange(low, high)
        box.setValue(value)
        box.setAlignment(QtCore.Qt.AlignRight)
        if suffix:
            box.setSuffix(suffix)
        self.watch(box.valueChanged)
        return box

    # ----- font access
    def font_package(self) -> Any:
        """The bound font. Refuse a closed or switched font."""
        if self.package_id is None:
            raise ValueError(
                "Open a font and select glyphs. Then run this script again."
            )
        package = current_package()
        if package is None or package.id != self.package_id:
            raise ValueError("The font changed. Run this script again.")
        return package

    def chosen_masters(self, package: Any) -> list[str]:
        """Current master, or all masters."""
        if self.scope.currentIndex == 0:
            return [package.master]
        return list(package.masters)

    def make_entries(self) -> list[Entry]:
        """Plan all target layers from the live font."""
        package = self.font_package()
        glyphs = self.target_glyphs(package)
        if not glyphs:
            raise ValueError(self.empty_message())
        return survey(
            glyphs, self.chosen_masters(package), self.planner(package, glyphs)
        )

    # ----- actions
    def reselect(self) -> None:
        """Take the glyph selection from the Font window again."""
        self.font_package()
        self.names = names_selected_names()
        self.refresh()

    def refresh(self) -> None:
        """Recompute the preview. Any refusal disables Apply and shows its reason."""
        self.sync_controls()
        try:
            self.entries = self.make_entries()
        except Exception as error:  # noqa: BLE001 - a native read can fail; show it, stay open
            self.entries = []
            self.table.setRowCount(0)
            self.apply_button.setEnabled(False)
            if isinstance(error, ValueError):
                self.subtitle.setText(str(error))
                self.status.setText("")
            else:
                self.status.setText(f"Error: {error!r}")
            return
        seen = list(dict.fromkeys(e.glyph.name for e in self.entries))
        shown = ", ".join(seen[:MAX_NAMES]) + (" …" if len(seen) > MAX_NAMES else "")
        self.subtitle.setText(f"{self.subtitle_hint()} ({shown})")
        self.fill_table()
        todo = pending(self.entries)
        note = self.rebuild_note_for(todo)
        names = frozenset(e.glyph.name for e in todo)
        if self.allow_auto.isChecked() and (not note or self._override_for != names):
            self.allow_auto.blockSignals(
                True
            )  # The tick belonged to another set of glyphs.
            self.allow_auto.setChecked(False)
            self.allow_auto.blockSignals(False)
            self._override_for = None
        blocked = bool(note) and not self.allow_auto.isChecked()
        self.allow_auto.setVisible(bool(note))
        self.apply_button.setEnabled(bool(todo) and not blocked)
        text = f"{len(todo)} layer{'s' if len(todo) != 1 else ''} will change"
        if not todo:
            text = "Nothing to change"
        if len(self.rows()) > MAX_ROWS:
            text += f" · table shows the first {MAX_ROWS}"
        if blocked:
            text = self.refusal(note)
        self.status.setText(f"{text} · {note}" if note and not blocked else text)

    def override_toggled(self) -> None:
        """Bind a tick to the glyphs that are changed now. Another set needs a new tick."""
        names = frozenset(e.glyph.name for e in pending(self.entries))
        self._override_for = names if self.allow_auto.isChecked() else None
        self.refresh()

    def overridden(self, entries: list[Entry]) -> bool:
        """True when the tick belongs to exactly these changed glyphs."""
        names = frozenset(e.glyph.name for e in pending(entries))
        return self.allow_auto.isChecked() and self._override_for == names

    def refusal(self, note: str) -> str:
        """Text that says why a base of auto glyphs is not edited."""
        return f'Refused. {note}. Tick "{ALLOW_AUTO_LABEL}" to go on.'

    def rows(self) -> list[Entry]:
        """Entries that deserve a table row: edits and explained skips, not no-ops."""
        return [e for e in self.entries if e.plan is None or e.plan.changed]

    def fill_table(self) -> None:
        """Show the plan. Changed values use the accent colour."""
        accent = QtGui.QColor(self.palette.color(QtGui.QPalette.Link))
        shown = self.rows()[:MAX_ROWS]
        self.table.setRowCount(len(shown))
        for row, entry in enumerate(shown):
            if entry.plan is not None:
                cells = [f"{entry.glyph.name} · {entry.master}", *entry.plan.cells]
            else:
                cells = [f"{entry.glyph.name} · {entry.master}", entry.note]
            for column, text in enumerate(cells):
                item = QtGui.QTableWidgetItem(text)
                if column:
                    item.setTextAlignment(
                        int(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
                    )
                if entry.plan is not None and column in self.ACCENT:
                    bold = item.font()
                    bold.setBold(True)
                    item.setFont(bold)
                    item.setForeground(QtGui.QBrush(accent))
                self.table.setItem(row, column, item)

    def rebuild_note_for(self, todo: list[Entry]) -> str:
        """Warning text for auto composites that FontLab rebuilds. Cached per glyph set."""
        names = frozenset(e.glyph.name for e in todo)
        if names not in self._rebuild_cache:
            self._rebuild_cache = {
                names: rebuild_note(auto_dependants(self.font_package(), set(names)))
            }
        return self._rebuild_cache[names]

    def apply(self) -> None:
        """Plan again from the live font and apply. One Undo step."""
        try:
            entries = self.make_entries()
            note = self.rebuild_note_for(pending(entries))
            if note and not self.overridden(entries):
                raise ValueError(self.refusal(note))
            result = commit(self.TITLE, entries)
        except Exception as error:  # noqa: BLE001 - report in the panel, never into the host
            self.refresh()
            self.status.setText(
                str(error) if isinstance(error, ValueError) else f"Error: {error!r}"
            )
            return
        self.last_result = result
        self.refresh()
        text = f"Changed {result['layers']} layers in {result['glyphs']} glyphs"
        if result["auto_skipped"]:
            text += f" · {result['auto_skipped']} auto layers skipped"
        if result["mismatches"]:
            count = len(result["mismatches"])
            text += f" · {count} did not read back as planned: " + "; ".join(
                result["mismatches"][:NOTE_LIMIT]
            )
        self.status.setText(f"{text} · {note}" if note else text)

    def closeEvent(self, event: Any) -> None:
        """Disconnect owned signals. Then delete the panel."""
        close_script_dialog(self, event, self.KEY)


MODES = [("Add to italic sidebearings", "add"), ("Set italic sidebearings to", "set")]
X_HEIGHT_FALLBACK = 500  # Used when the font has no x-height value.


# ---------------------------------------------------------------- core
def outline(layer: Any) -> Any:
    """The layer outline as one QPainterPath, with component transforms applied."""
    path = QtGui.QPainterPath()
    for shape in layer.shapes:
        part = QtGui.QPainterPath()
        for contour in shape.getContours():
            part.addPath(contour.path())
        path.addPath(shape.transform.map(part))
    return path


def deslant(angle: float, pivot: float) -> Any:
    """QTransform that removes a slant of angle degrees around the height pivot.

    The sign follows FontLab: a right-leaning design has a negative angle.
    """
    slope = math.tan(math.radians(angle))
    return QtGui.QTransform(1, 0, slope, 1, -pivot * slope, 0)


def italic_edges(layer: Any, angle: float, pivot: float) -> tuple[float, float] | None:
    """Italic left and right edge of the ink, or None for an empty layer."""
    path = outline(layer)
    if path.isEmpty():
        return None
    box = deslant(angle, pivot).map(path).boundingRect()
    return box.x(), box.x() + box.width()


def italic_planner(
    angle: float,
    pivot: float,
    mode: str,
    lsb_value: int | None,
    rsb_value: int | None,
) -> Planner:
    """Return the planner. A value of None leaves that side as it is."""

    def plan(layer: Any, master: str) -> LayerPlan | str:
        edges = italic_edges(layer, angle, pivot)
        if edges is None:
            return "empty (no outline)"
        width = layer.advanceWidth
        ilsb, irsb = edges[0], width - edges[1]
        new_ilsb, new_irsb = ilsb, irsb
        if lsb_value is not None:
            new_ilsb = ilsb + lsb_value if mode == "add" else lsb_value
        if rsb_value is not None:
            new_irsb = irsb + rsb_value if mode == "add" else rsb_value
        dx = unit(new_ilsb - ilsb)
        new_width = unit(width + dx + (new_irsb - irsb))
        if new_width < 0:
            return "negative width (skipped)"
        plain = ink_edges(layer)
        shown_irsb = irsb + (new_width - width - dx)
        cells = (
            f"{unit(plain[0])}",
            f"{unit(width - plain[1])}",
            f"{unit(ilsb)}",
            f"{unit(irsb)}",
            f"{unit(ilsb + dx)}",
            f"{unit(shown_irsb)}",
        )
        return make_plan(layer, dx, new_width, cells)

    return plan


# ---------------------------------------------------------------- panel
class ItalicSidebearings(MetricsPanel):
    """Italic sidebearings: angle, height, operation, values, masters."""

    TITLE = "Italic Sidebearings"
    KEY = "metrics_italic_sidebearings"
    HEADERS = ("LSB", "RSB", "Italic LSB", "Italic RSB", "New it. LSB", "New it. RSB")
    ACCENT = (5, 6)
    MIN_WIDTH = 660

    def build(self) -> None:
        """Create angle, height, operation and value controls."""
        package = current_package()
        angle = (
            float(getattr(package, "italicAngle_value", 0.0) or 0.0) if package else 0.0
        )
        x_height = (
            getattr(package, "xHeight_value", X_HEIGHT_FALLBACK) if package else 0
        )
        self.font_angle = angle
        self.angle = QtGui.QDoubleSpinBox()
        self.angle.setRange(-45.0, 45.0)
        self.angle.setDecimals(1)
        self.angle.setSuffix(" °")
        self.angle.setValue(angle)
        self.angle.setAlignment(QtCore.Qt.AlignRight)
        self.watch(self.angle.valueChanged)
        self.pivot = self.spin(-2000, 4000, unit((x_height or X_HEIGHT_FALLBACK) / 2))
        self.mode = QtGui.QComboBox()
        for label, _ in MODES:
            self.mode.addItem(label)
        self.watch(self.mode.currentIndexChanged)
        self.lsb_check = QtGui.QCheckBox("LSB")
        self.lsb_check.setChecked(True)
        self.rsb_check = QtGui.QCheckBox("RSB")
        self.rsb_check.setChecked(True)
        self.watch(self.lsb_check.toggled)
        self.watch(self.rsb_check.toggled)
        self.lsb = self.spin(-2000, 2000, 0)
        self.rsb = self.spin(-2000, 2000, 0)
        self.form.addWidget(QtGui.QLabel("Italic angle"), 1, 0)
        self.form.addWidget(self.angle, 1, 1)
        self.form.addWidget(QtGui.QLabel("Measured at y ="), 1, 2)
        self.form.addWidget(self.pivot, 1, 3)
        self.form.addWidget(QtGui.QLabel("Operation"), 2, 0)
        self.form.addWidget(self.mode, 2, 1, 1, 3)
        self.form.addWidget(self.lsb_check, 3, 0)
        self.form.addWidget(self.lsb, 3, 1)
        self.form.addWidget(self.rsb_check, 3, 2)
        self.form.addWidget(self.rsb, 3, 3)
        self.form.setColumnStretch(3, 1)

    def sync_controls(self) -> None:
        """Enable a value only when its box is ticked."""
        self.lsb.setEnabled(self.lsb_check.isChecked())
        self.rsb.setEnabled(self.rsb_check.isChecked())

    def subtitle_hint(self) -> str:
        """Describe the current settings."""
        count = len({e.glyph.name for e in self.entries})
        upright = (
            " The font angle is 0: italic values equal plain values."
            if not self.font_angle
            else ""
        )
        return (
            f"{count} glyph{'s' if count != 1 else ''} de-slanted at {self.angle.value:g} °"
            f" around y = {self.pivot.value}.{upright}"
        )

    def planner(self, package: Any, glyphs: list[Any]) -> Planner:
        """Planner for the chosen angle, height, operation and values."""
        return italic_planner(
            self.angle.value,
            self.pivot.value,
            MODES[self.mode.currentIndex][1],
            self.lsb.value if self.lsb_check.isChecked() else None,
            self.rsb.value if self.rsb_check.isChecked() else None,
        )


def main() -> Any:
    """Open the panel. A second run replaces the first panel."""
    return show_script_dialog(ItalicSidebearings, ItalicSidebearings.KEY)


if __name__ == "__main__":
    main()
