# this_file: Scripts/Anchors/Round To Grid.py
# SPDX-License-Identifier: Apache-2.0
# FLM: Anchors · Round To Grid
"""Round anchor positions to a grid step.

What: Moves anchors to the nearest multiple of a grid step. Halves round up:
15 becomes 20 and -15 becomes -10 for step 10. You choose the step, the
axes and, if you want, the anchor names.

How: The table lists each anchor that moves. A fractional position moves too,
even for step 1. Name, style and expressions of the anchors stay.

Why: A grid step is a simple, predictable rule. It keeps all marks on one
lattice, so values are easy to compare and to edit by hand.

Use: Select glyphs. Run the script. Set the step and the axes. Leave the names
empty for all anchors. Check the table. Press Round.

Benefit: Clean anchor values in all masters, in one Undo step.

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
The edit is recorded as one Undo step. The plan, the safety checks, the one-step
write and the panel base are shared with the other anchor scripts
(fly.ap.anchor_writer, fly.ap.anchor_panel); the planner and the controls
belong to this script.

Source: the author's own FontLab sample
anchors_round_to_grid.py, Apache-2.0.
Adapted for the current FontLab 9 API.
"""

import math
from typing import Any

import fly.ap.anchor_panel as anchor_panel  # noqa: PLR0402 - fontlabapp.__getattr__ is native
import fly.ap.anchor_writer as anchor_writer  # noqa: PLR0402 - fontlabapp.__getattr__ is native
from fly import qt
import fly.ap.scripting as scripting

QtGui = qt.QtGui
TITLE = "Round Anchors to Grid"
KEY = "anchors_round_to_grid"


# ---------------------------------------------------------------- rounding logic
def snap(value: float, step: int) -> int:
    """Nearest multiple of `step`; halves round up.

    snap(15, 10) = 20. snap(-15, 10) = -10. snap(-5, 10) = 0.
    """
    return int(step * math.floor(value / step + 0.5))


def round_changes(
    layer: Any, step: int, do_x: bool, do_y: bool, names: list[str]
) -> list[anchor_writer.Change]:
    """Rows for the anchors that move. Empty `names` means all anchors."""
    changes: list[anchor_writer.Change] = []
    for pin in layer.anchors:
        if names and pin.name not in names:
            continue
        x, y = anchor_writer.raw_point(pin)
        new = (snap(x, step) if do_x else x, snap(y, step) if do_y else y)
        if new != (x, y):
            changes.append(
                anchor_writer.Change(
                    pin.name,
                    f"{anchor_writer.fmt(x)}, {anchor_writer.fmt(y)}",
                    f"{anchor_writer.fmt(new[0])}, {anchor_writer.fmt(new[1])}",
                    ("set", pin.name, new),
                )
            )
    clash = anchor_writer.duplicated(layer, [c.name for c in changes])
    return anchor_writer.refusal(clash) if clash else changes


class RoundToGrid(anchor_panel.panel_type()):
    """Step, axes, optional names, master scope."""

    TITLE, KEY, ACTION = TITLE, KEY, "Round"
    HEADERS: tuple[str, ...] = ("Glyph · master", "Anchor", "Now", "New")

    def build_controls(self) -> None:
        self.step = self.spin(1, 500, 10, " units")
        self.do_x = QtGui.QCheckBox("x")
        self.do_x.setChecked(True)
        self.do_y = QtGui.QCheckBox("y")
        self.do_y.setChecked(True)
        self.names = QtGui.QLineEdit()
        self.names.setPlaceholderText("all anchors, or names: top, bottom")
        self.scope = self.scope_box()
        axes = QtGui.QHBoxLayout()
        axes.addWidget(self.do_x)
        axes.addWidget(self.do_y)
        axes.addStretch(1)
        self.form.addWidget(QtGui.QLabel("Grid step"), 0, 0)
        self.form.addWidget(self.step, 0, 1)
        self.form.addLayout(axes, 0, 2)
        self.form.addWidget(QtGui.QLabel("Anchors"), 1, 0)
        self.form.addWidget(self.names, 1, 1, 1, 2)
        self.form.addWidget(QtGui.QLabel("Masters"), 2, 0)
        self.form.addWidget(self.scope, 2, 1, 1, 2)
        for signal in (
            self.step.valueChanged,
            self.do_x.toggled,
            self.do_y.toggled,
            self.names.textChanged,
            self.scope.currentIndexChanged,
        ):
            self.watch(signal)

    def chosen_masters(self) -> list[str]:
        return [self.current_master] if self.scope.currentIndex == 0 else self.masters

    def planner(self) -> anchor_writer.Planner:
        step = int(self.step.value)
        if step < 1:
            raise ValueError("The grid step must be at least 1.")
        if not (self.do_x.isChecked() or self.do_y.isChecked()):
            raise ValueError("Tick x, y or both.")
        names = anchor_writer.parse_names(self.names.text)
        do_x, do_y = self.do_x.isChecked(), self.do_y.isChecked()
        return lambda glyph, master, layer: round_changes(
            layer, step, do_x, do_y, names
        )


def main() -> Any:
    """Open the panel, or raise the one that is already open."""
    return scripting.show_script_dialog(RoundToGrid, KEY)


if __name__ == "__main__":
    main()
