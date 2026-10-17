# this_file: Scripts/Font Info/Calculate Vertical Metrics.py
# SPDX-License-Identifier: Apache-2.0
# FLM: Font Info · Calculate Vertical Metrics
"""Set hhea, Win (and optionally OS/2 typo) vertical metrics to enclose every glyph, per master.

Bounds are rounded outward and can be padded. FontLab's master ascender, descender and
line gap ARE the OS/2 typo values (measured), so Typo is off by default: turning it on
moves the font's ascender/descender lines to the glyph bounds. Preview before Apply.

Open with a font active. Choose current or all masters, padding, line gap and the
metric groups to update. Review the table, then choose Apply. Bounds are captured
when the panel opens; reopen after outline edits. Large scans stop before edits.
Empty masters are skipped. The undoable edit preserves outlines and unselected
metric groups. Reopen after switching the font or active master.
"""

import math
import time
from typing import Any

from fly import ap, qt
from fly.ap.scripting import (
    current_package,
    font_info_dialog_type,
    show_script_dialog,
    write_font_info,
)

fontlab = ap.fontlab
QtCore, QtGui = qt.QtCore, qt.QtGui

TITLE = "Calculate Vertical Metrics"
KEY = "fontinfo_vertical_metrics_calculator"


def glyph_records(package: Any) -> Any:
    """Read all Unicode assignments, including secondary encodings, in font order."""
    FL = ap.FL

    active = current_package()
    if active is None or active.id != package.id:
        msg = "Activate the original font and reopen this tool."
        raise ValueError(msg)
    legacy = FL.fl.font
    return [
        (legacy[i].name, list(package.findName(legacy[i].name).fgGlyph.unicodes))
        for i in range(len(legacy))
    ]


def write_changes(package: Any, changes: list[tuple]) -> dict[str, int]:
    """Apply this tool's explicit validated metadata plan using shared history."""
    return write_font_info(package, changes, undo_name=TITLE)


METRIC_FIELDS = [
    "openTypeOS2TypoAscender",
    "openTypeOS2TypoDescender",
    "openTypeOS2TypoLineGap",
    "openTypeHheaAscender",
    "openTypeHheaDescender",
    "openTypeHheaLineGap",
    "openTypeOS2WinAscent",
    "openTypeOS2WinDescent",
]


GROUPS = [  # (label, fields): FontLab's ascender/descender/line gap are the typo fields
    ("Typo (= FontLab ascender, descender, line gap)", METRIC_FIELDS[0:3]),
    ("hhea", METRIC_FIELDS[3:6]),
    ("Win", METRIC_FIELDS[6:8]),
]
LABELS = {
    "openTypeOS2TypoAscender": "Typo ascender",
    "openTypeOS2TypoDescender": "Typo descender",
    "openTypeOS2TypoLineGap": "Typo line gap",
    "openTypeHheaAscender": "hhea ascender",
    "openTypeHheaDescender": "hhea descender",
    "openTypeHheaLineGap": "hhea line gap",
    "openTypeOS2WinAscent": "Win ascent",
    "openTypeOS2WinDescent": "Win descent",
}


def number(value: Any) -> Any:
    """965.0 -> 965 for display."""
    return int(value) if isinstance(value, float) and value.is_integer() else value


def enclosing_metrics(low: float, high: float, padding: int, gap: int) -> list[float]:
    """Round bounds outward and validate OpenType metric limits."""
    if (
        not all(math.isfinite(v) for v in (low, high, padding, gap))
        or low > high
        or not 0 <= padding <= 2000
        or not 0 <= gap <= 32767
    ):
        raise ValueError("Use finite bounds, padding 0–2000 and line gap 0–32767.")
    ascent = max(0, math.ceil(high) + padding)
    descent = min(0, math.floor(low) - padding)
    if ascent > 32767 or descent < -32768:
        msg = "Bounds exceed signed 16-bit typo/hhea limits."
        raise ValueError(msg)
    return [ascent, descent, gap, ascent, descent, gap, ascent, -descent]


def scan_bounds(package: Any) -> dict[str, tuple[float, float, int]]:
    """Measure all nonempty glyph bounds with an interactive deadline."""
    records = glyph_records(package)
    result = {}
    deadline = time.monotonic() + 2.5
    for master in package.masters:
        lows, highs = [], []
        for name, _ in records:
            if time.monotonic() > deadline:
                msg = "Font too large for an interactive scan; no changes made."
                raise ValueError(
                    msg,
                )
            layer = package.findName(name).findLayer(master)
            if layer is None or layer.isNull:
                continue
            box = layer.boundingBox
            if box.width() == 0 and box.height() == 0:
                continue
            lows.append(box.y())
            highs.append(box.y() + box.height())
        if lows:
            result[master] = (min(lows), max(highs), len(lows))
    return result


def metric_plan(
    package: Any,
    bounds: Any,
    masters: Any,
    padding: Any,
    gap: Any,
    fields: Any = METRIC_FIELDS,
) -> Any:
    """Build selected master and metric edits while restoring the active master."""
    original = package.master
    changes = []
    try:
        for master in masters:
            if master not in bounds:
                continue
            package.setMaster(master)
            values = enclosing_metrics(*bounds[master][:2], padding, gap)
            changes.extend(
                (master, k, getattr(package.info, k), v)
                for k, v in zip(METRIC_FIELDS, values, strict=False)
                if k in fields
            )
    finally:
        package.setMaster(original)
    return changes


def run(package: Any, changes: Any) -> Any:
    """Apply the preview's explicit master and metric-field plan."""
    return write_changes(package, changes)


FontInfoDialog = font_info_dialog_type()


class Dialog(FontInfoDialog):
    MASTER_BOUND = True

    def __init__(self, parent: Any = None) -> None:
        """Open the shared Font Info panel with this tool's controls and preview."""
        FontInfoDialog.__init__(
            self,
            parent,
            title=TITLE,
            subtitle="Sets hhea and Win (and, if ticked, OS/2 typo) metrics to enclose every glyph, rounded outward. Typo = FontLab's own ascender/descender lines.",
            key=KEY,
        )

    def setup(self) -> None:
        """Build all original controls and connect owned signals."""
        self.bounds = scan_bounds(self.package) if self.package else {}
        self.scope = QtGui.QComboBox()
        self.scope.addItems(
            [
                f"Current master ({self.package.master if self.package else chr(8212)})",
                f"All masters ({len(self.package.masters) if self.package else 0})",
            ],
        )
        self.padding = QtGui.QSpinBox()
        self.padding.setRange(0, 2000)
        self.gap = QtGui.QSpinBox()
        self.gap.setRange(0, 32767)
        for column, (label, control) in enumerate(
            [("Scope", self.scope), ("Padding", self.padding), ("Line gap", self.gap)],
        ):
            self.form.addWidget(QtGui.QLabel(label), 0, column)
            self.form.addWidget(control, 1, column)
        groups = QtGui.QHBoxLayout()
        groups.setSpacing(16)
        self.group_checks = []
        for index, (label, _) in enumerate(GROUPS):
            check = QtGui.QCheckBox(label)
            check.setChecked(index > 0)
            self.group_checks.append(check)
            groups.addWidget(check)
            self._connect(check.toggled, lambda *a: self.refresh())
        groups.addStretch(1)
        self.form.addLayout(groups, 2, 0, 1, 3)
        self._connect(self.scope.currentIndexChanged, lambda *a: self.refresh())
        for control in (self.padding, self.gap):
            self._connect(control.valueChanged, lambda *a: self.refresh())

    def changes(self) -> Any:
        """Build explicit per-master changes from the selected controls."""
        masters = (
            list(self.package.masters)
            if self.scope.currentIndex
            else [self.preview_master]
        )
        fields = [
            f
            for check, (_, group) in zip(self.group_checks, GROUPS, strict=False)
            if check.isChecked()
            for f in group
        ]
        return metric_plan(
            self.package,
            self.bounds,
            masters,
            self.padding.value,
            self.gap.value,
            fields,
        )

    def refresh(self) -> None:
        """Validate and display a complete preview before enabling Apply."""
        self._preview_valid = False
        self.apply_button.setEnabled(False)
        if self.package is None:
            return
        self.ensure_font()
        self._plan = self.changes()
        self.rows(
            ["Master · field", "Current", "Proposed"],
            [
                (m + " · " + LABELS[k], number(old), number(new))
                for m, k, old, new in self._plan
            ],
        )
        self.apply_button.setEnabled(
            any(old != new for _, _, old, new in self._plan),
        )
        self.status.setText(
            "Typo/hhea descenders are negative; Win descent is positive. Empty masters skipped. Bounds captured on open; reopen after outline edits.",
        )
        self._preview_valid = True

    def apply(self) -> None:
        """Apply the last successful preview to its original font."""
        self.ensure_preview()
        self.last_result = run(self.package, self._plan)
        self.refresh()
        self.status.setText(f"Applied {self.last_result['changed']} metric fields")


def main() -> Any:
    """Replace this tool's owned dialog using the shared script registry."""
    return show_script_dialog(Dialog, KEY)


if __name__ == "__main__":
    main()
