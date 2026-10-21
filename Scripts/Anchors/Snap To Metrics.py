# this_file: Scripts/Anchors/Snap To Metrics.py
# SPDX-License-Identifier: Apache-2.0
# FLM: Anchors · Snap To Metrics
"""Move named anchors vertically onto a font metric, plus an offset.

What: Sets the y value of the named anchors to baseline, x-height, cap height,
ascender or descender, plus an offset. The x value stays as stored.

How: Each master uses its own metric. A Bold with a taller x-height gets its
own anchor height. The panel shows the metric of every chosen master.

Why: Anchor heights follow the design instead of a number typed once. The
script reads the metric of a master without switching to that master.

Use: Select glyphs. Run the script. Type the anchor names. Choose the metric
and the offset. Check the table. Press Snap.

Benefit: Top and bottom anchors line up across glyphs and masters in one step.

Safety: Auto layers are listed and never edited. The script refuses the whole
batch, before any history exists, when:

- an existing anchor would move to 0, 0 (FontLab cannot Redo that);
- a glyph has an automatic layer, or is the base of an automatic composite,
  also through other composites (FontLab rebuilds the composite and Undo does
  not restore it);
- several anchors on a layer share a name (the edit is ambiguous);
- FontLab holds queued glyph updates (they would alter other glyph dates).

After the write, the script reads every value back. It reports any value
that FontLab did not keep, for example under a strong rounding preference.
If FontLab fails part-way, the error says that native changes may remain.
Edit > Undo restores the font. The plan, the safety checks, the one-step
write and the panel base are shared with the other anchor scripts
(fly.ap.anchor_writer, fly.ap.anchor_panel); the planner and the controls
belong to this script.

Source: the author's own FontLab sample
anchors_snap_to_metrics.py, Apache-2.0.
Adapted for the current FontLab 9 API.
"""

from typing import Any

import fly.ap.anchor_panel as anchor_panel  # noqa: PLR0402 - fontlabapp.__getattr__ is native
import fly.ap.anchor_writer as anchor_writer  # noqa: PLR0402 - fontlabapp.__getattr__ is native
from fly import ap, qt
from fly.ap import scripting

QtGui = qt.QtGui
fontlab = ap.fontlab
TITLE = "Snap Anchors to Metrics"
KEY = "anchors_snap_to_metrics"

# ---------------------------------------------------------------- metrics logic
METRICS: list[tuple[str, str | None]] = [
    ("Baseline", None),
    ("x-height", "xHeight"),
    ("Cap height", "capsHeight"),
    ("Ascender", "ascender"),
    ("Descender", "descender"),
]


def metric_value(package: Any, master: str, attribute: str | None) -> int:
    """Metric of one master in font units. None means the baseline, 0."""
    if attribute is None:
        return 0
    return anchor_writer.half_up(
        getattr(fontlab.FontMetrics(package, master), attribute)
    )


def snap_changes(layer: Any, names: list[str], y: float) -> list[anchor_writer.Change]:
    """Rows for the named anchors whose y differs from `y`. x stays."""
    changes: list[anchor_writer.Change] = []
    for pin in layer.anchors:
        if pin.name not in names:
            continue
        x, old = anchor_writer.raw_point(pin)
        if abs(old - y) < anchor_writer.EPSILON:
            continue
        changes.append(
            anchor_writer.Change(
                pin.name,
                f"{anchor_writer.fmt(x)}, {anchor_writer.fmt(old)}",
                f"{anchor_writer.fmt(x)}, {anchor_writer.fmt(y)}",
                ("set", pin.name, (x, y)),
            )
        )
    clash = anchor_writer.duplicated(layer, [c.name for c in changes])
    return anchor_writer.refusal(clash) if clash else changes


class SnapToMetrics(anchor_panel.panel_type()):
    """Names, metric, offset, master scope."""

    TITLE, KEY, ACTION = TITLE, KEY, "Snap"
    HEADERS: tuple[str, ...] = ("Glyph · master", "Anchor", "x, y", "New x, y")

    def build_controls(self) -> None:
        self.names = QtGui.QLineEdit("top")
        self.names.setPlaceholderText("anchor names, comma-separated")
        self.metric_box = QtGui.QComboBox()
        for label, _ in METRICS:
            self.metric_box.addItem(label)
        self.metric_box.setCurrentIndex(1)
        self.offset = self.spin(-1000, 1000, 0, " units")
        self.scope = self.scope_box()
        self.values = QtGui.QLabel()
        self.values.setWordWrap(True)
        self.values.setStyleSheet(f"color: {anchor_panel.muted(self)};")
        self.form.addWidget(QtGui.QLabel("Anchors"), 0, 0)
        self.form.addWidget(self.names, 0, 1)
        self.form.addWidget(QtGui.QLabel("Snap to"), 1, 0)
        self.form.addWidget(self.metric_box, 1, 1)
        self.form.addWidget(QtGui.QLabel("Offset"), 2, 0)
        self.form.addWidget(self.offset, 2, 1)
        self.form.addWidget(QtGui.QLabel("Masters"), 3, 0)
        self.form.addWidget(self.scope, 3, 1)
        self.form.addWidget(self.values, 4, 1)
        for signal in (
            self.names.textChanged,
            self.metric_box.currentIndexChanged,
            self.offset.valueChanged,
            self.scope.currentIndexChanged,
        ):
            self.watch(signal)

    def chosen_masters(self) -> list[str]:
        return [self.current_master] if self.scope.currentIndex == 0 else self.masters

    def heights(self) -> dict[str, int]:
        """Target y per chosen master: metric plus offset."""
        attribute = METRICS[self.metric_box.currentIndex][1]
        offset = int(self.offset.value)
        if self.package is None:
            return {}
        return {
            m: metric_value(self.package, m, attribute) + offset
            for m in self.chosen_masters()
        }

    def planner(self) -> anchor_writer.Planner:
        names = anchor_writer.parse_names(self.names.text)
        if not names:
            raise ValueError("Type the anchor names to snap.")
        heights = self.heights()
        label = METRICS[self.metric_box.currentIndex][0]
        self.values.setText(
            f"{label}: " + ", ".join(f"{m} {v}" for m, v in heights.items())
        )
        return lambda glyph, master, layer: snap_changes(layer, names, heights[master])


def main() -> Any:
    """Open the panel, or raise the one that is already open."""
    return scripting.show_script_dialog(SnapToMetrics, KEY)


if __name__ == "__main__":
    main()
