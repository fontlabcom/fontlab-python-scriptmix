# this_file: Scripts/Font Info/Master Metrics Table.py
# SPDX-License-Identifier: Apache-2.0
# FLM: Font Info · Master Metrics Table
"""Edit ascender, descender, x-height and cap-height across masters; diagram follows the selected row.

What it does:
    Open with a font active. Double-click a metric value, check the selected row's
    diagram, then choose Apply. Every row is checked before any edit. Apply writes
    all changed masters as one Undo step and preserves glyph outlines. Keep this
    panel bound to its original font; reopen it after switching to another font.

How it works:
    Read each master's four vertical metrics while restoring the original
    current master. Validate finite, ordered, signed-16-bit proposals before
    writing metadata. Apply refuses when a value changed since the preview.
    It then writes and reads back each changed master. When one master fails,
    the written values are restored and nothing is added to Undo. When a
    restore also fails, the status names each failure (such as "master Bold
    was not restored") and says that values can remain; check every master
    before you save.

Why this design:
    A complete multi-row proposal prevents a later invalid cell from leaving
    an earlier master partially updated by normal validation.

How to use:
    Activate the font's Font window and run Font Info > Master Metrics Table.
    Edit metric cells, select a row to inspect its diagram and press Apply
    after reviewing every master. Use Edit > Undo in the Font window to revert
    the whole Apply. Reopen after changing fonts.

Benefit:
    Stage family-wide vertical metrics together while keeping glyph outlines
    unchanged.

Known issue:
    FontLab defect fl#8574: after Edit > Undo or Redo, the metric guides show
    3 of 9 lines until you reopen the font. The saved file is correct.
"""

import math
from typing import Any

from fly import ap, qt
from fly.ap.scripting import (
    font_info_dialog_type,
    show_script_dialog,
)

fontlab = ap.fontlab
QtCore, QtGui = qt.QtCore, qt.QtGui

TITLE = "Master Metrics Table"
KEY = "fontinfo_master_metrics_table"


def write_changes(package: Any, changes: list[tuple]) -> dict[str, Any]:
    """Write the changed values of a validated plan as one Undo step.

    ``changes`` holds ``(master, field, previous, value)``. Refuse when a
    previous value differs from the font; write nothing when no value changes.
    """
    import fly.ap.font_history as font_history  # noqa: PLR0402 - fontlabapp.__getattr__ is native
    import fly.ap.master_metrics as master_metrics  # noqa: PLR0402 - same reason

    font_history.require_font_window(package)  # before master_values switches masters
    current = dict(master_values(package))
    request: dict[str, dict[str, float]] = {}
    for master, field, previous, value in changes:
        if master not in current or current[master][MASTER_FIELDS.index(field)] != previous:
            msg = f"{master} {field} changed since preview; refresh the tool."
            raise ValueError(msg)
        if value != previous:
            request.setdefault(master, {})[field] = value
    if not request:
        return {"changed": 0}
    result = master_metrics.write_master_metrics(package, request, title=TITLE)
    return {
        "changed": sum(len(fields) for fields in request.values()),
        "pending_updates": result.pending_updates,
        "pending_note": result.pending_note,
    }


MASTER_FIELDS = ["ascender", "descender", "xHeight", "capHeight"]


def validate_metrics(values: list[float]) -> list[float]:
    """Require four finite ordered metrics within signed 16-bit limits."""
    if len(values) != 4 or not all(
        math.isfinite(v) and -32768 <= v <= 32767 for v in values
    ):
        msg = "Use finite metrics between −32768 and 32767."
        raise ValueError(msg)
    asc, desc, xheight, cap = values
    if not desc <= 0 <= xheight <= cap <= asc:
        msg = "Expected descender ≤ 0 ≤ x-height ≤ cap-height ≤ ascender."
        raise ValueError(msg)
    return values


def master_values(package: Any) -> list[tuple[str, list[float]]]:
    """Read all master metrics, as the writer reads them back; restore the master."""
    import fly.ap.master_metrics as master_metrics  # noqa: PLR0402 - fontlabapp.__getattr__ is native

    properties = [
        master_metrics.FIELDS[master_metrics.ALIASES.get(key, key)]
        for key in MASTER_FIELDS
    ]
    original = package.master
    result = []
    try:
        for master in package.masters:
            package.setMaster(master, False)
            result.append(
                (master, [float(getattr(package, name)) for name in properties]),
            )
    finally:
        package.setMaster(original, False)
    return result


def run(package: Any, rows: Any) -> Any:
    """Validate all proposed master rows and apply a single metadata plan."""
    old = dict(master_values(package))
    changes = []
    for master, values in rows:
        validate_metrics(values)
        changes.extend(
            (master, key, previous, value)
            for key, previous, value in zip(
                MASTER_FIELDS,
                old[master],
                values,
                strict=False,
            )
        )
    return write_changes(package, changes)


class Diagram(QtGui.QWidget):
    def __init__(self, owner: Any) -> None:
        """Create the complete modeless tool and its initial preview."""
        QtGui.QWidget.__init__(self, owner)
        self.owner = owner
        self._paint_error = ""
        self.setMinimumHeight(160)

    def paintEvent(self, event: Any) -> None:
        """Contain drawing failures and always end the native painter."""
        painter = QtGui.QPainter(self)
        try:
            rows = self.owner.edited_rows()
            if not rows:
                return
            row = max(0, self.owner.table.currentRow())
            master, values = rows[row]
            asc, desc, xheight, cap = values
            span = max(1, asc - desc)
            painter.setRenderHint(QtGui.QPainter.Antialiasing)
            ink = QtGui.QColor(self.palette.color(QtGui.QPalette.WindowText))
            line = QtGui.QColor(ink)
            line.setAlpha(90)
            band = QtGui.QColor(self.palette.color(QtGui.QPalette.Link))
            band.setAlpha(40)
            accent = QtGui.QColor(self.palette.color(QtGui.QPalette.Link))

            def to_y(value: Any) -> Any:
                """Map a font coordinate to the diagram vertical coordinate."""
                return 18 + (asc - value) / span * (self.height - 36)

            # x-height band: the lowercase zone between baseline and x-height
            painter.fillRect(
                QtCore.QRectF(
                    150,
                    to_y(xheight),
                    self.width - 170,
                    to_y(0) - to_y(xheight),
                ),
                band,
            )
            for label, value in [
                ("Ascender", asc),
                ("Cap", cap),
                ("x-height", xheight),
                ("Baseline", 0),
                ("Descender", desc),
            ]:
                y = to_y(value)
                painter.setPen(
                    QtGui.QPen(QtGui.QBrush(accent if value == 0 else line), 1.0),
                )
                painter.drawLine(
                    QtCore.QPointF(150, y),
                    QtCore.QPointF(self.width - 20, y),
                )
                painter.setPen(ink)
                painter.drawText(QtCore.QPointF(8, y + 4), f"{label} {value:g}")
            painter.drawText(QtCore.QPointF(150, self.height - 4), f"{master} master")
        except Exception as error:  # noqa: BLE001 - never escape with active painter
            self._paint_error = repr(
                error,
            )  # an escaping exception with a live QPainter crashes FontLab
            self.owner.status.setText(self._paint_error)
        finally:
            painter.end()


FontInfoDialog = font_info_dialog_type()


class Dialog(FontInfoDialog):
    def __init__(self, parent: Any = None) -> None:
        """Open the shared Font Info panel with this tool's controls and preview."""
        FontInfoDialog.__init__(
            self,
            parent,
            title=TITLE,
            subtitle="Edit ascender, descender, x-height and cap-height across masters; diagram follows the selected row.",
            key=KEY,
        )

    def setup(self) -> None:
        """Build all original controls and connect owned signals."""
        self.initial = master_values(self.package) if self.package else []
        self.rows(
            ["Master", "Ascender", "Descender", "x-height", "Cap height"],
            [[master, *values] for master, values in self.initial],
        )
        for row in range(self.table.rowCount):
            self.table.item(row, 0).setFlags(
                int(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable),
            )
        self.table.setEditTriggers(
            QtGui.QAbstractItemView.DoubleClicked
            | QtGui.QAbstractItemView.EditKeyPressed,
        )
        self.diagram = Diagram(self)
        self.content.insertWidget(4, self.diagram)
        self._connect(self.table.itemChanged, lambda *a: self.refresh())
        self._connect(self.table.currentCellChanged, lambda *a: self.diagram.update())
        if self.initial:
            self.table.setCurrentCell(0, 1)

    def edited_rows(self) -> Any:
        """Read and validate every editable master metric row."""
        return [
            (
                master,
                validate_metrics(
                    [float(self.table.item(row, col).text()) for col in range(1, 5)],
                ),
            )
            for row, (master, _) in enumerate(self.initial)
        ]

    def refresh(self) -> None:
        """Validate and display a complete preview before enabling Apply."""
        self._preview_valid = False
        self.apply_button.setEnabled(False)
        if self.package is None:
            return
        self.ensure_font()
        rows = self.edited_rows()
        old = dict(master_values(self.package))
        self._plan = [
            (master, field, previous, value)
            for master, values in rows
            for field, previous, value in zip(
                MASTER_FIELDS, old[master], values, strict=True
            )
        ]
        self.apply_button.setEnabled(rows != master_values(self.package))
        self.status.setText(
            "Double-click a number to edit. All rows are validated before Apply.",
        )
        self.diagram.update()
        self._preview_valid = True

    def apply(self) -> None:
        """Apply the last successful preview to its original font."""
        self.ensure_preview()
        self.last_result = write_changes(self.package, self._plan)
        changed, note = self.last_result["changed"], self.last_result.get("pending_note")
        done = f"Applied {changed} metric field{'s' if changed != 1 else ''}" + (
            f" · {note}" if note else ""
        )
        self.status.setText(done)
        try:  # a failed new preview must not hide the completed write
            self.refresh()
        except Exception as error:  # noqa: BLE001 - keep the success visible
            self.status.setText(f"{done}; the new preview failed: {error}")
            return
        self.status.setText(done)


def main() -> Any:
    """Replace this tool's owned dialog using the shared script registry."""
    return show_script_dialog(Dialog, KEY)


if __name__ == "__main__":
    main()
