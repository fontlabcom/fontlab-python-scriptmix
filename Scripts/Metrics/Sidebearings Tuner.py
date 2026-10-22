# this_file: Scripts/Metrics/Sidebearings Tuner.py
# SPDX-License-Identifier: Apache-2.0
"""Set, add to or scale the sidebearings of the selected glyphs.

What it does: changes the left sidebearing (LSB), the right sidebearing (RSB)
or both, on the current master or on all masters. "Add" adds a value to each
side; a negative value tightens. "Set to" gives each side a value. "Scale %"
multiplies each side by a percentage.

How it works: the sidebearings are read from the outline edges in whole units.
The new value of each ticked side is computed in whole units; a half unit
rounds up. An unticked side keeps its value. The outline moves in place by the
LSB change (anchors move with it) and the advance width becomes LSB + outline
width + RSB. A layer without outline is listed and skipped. A change that gives
a negative width is refused for that layer.

Why: spacing passes often need the same correction on many glyphs and in every
master, for example "+5 on both sides" or "RSB 40 on all round letters".

How to use: select glyphs in the Font window. Choose the operation. Tick the
sides to change and type their values. Choose the current master or all
masters. Check the table. Press Apply. The panel stays open. Press "Use
selection" to read the Font window selection again. The panel opens on "Add"
with 0, so the first preview changes nothing. Switching to "Scale %" turns a
value of 0 into 100 %, which also changes nothing; leaving "Scale %" turns
only that untouched 100 back into 0. A value that you typed is kept.

Safety: each Apply is recorded as one Undo step. Auto layers are listed and
never edited. A
glyph that owns an auto layer is listed and skipped as a whole. Layers with a
metrics link or expression are listed and skipped. A base of auto glyphs is
refused, because FontLab rebuilds the auto glyphs and may lose their anchors
and locks (FontLab issue 8512). Tick "Edit bases of auto glyphs anyway" to go
on. Apply discloses queued ids and their possible date changes. After the write
the script reads advance and outline back and reports any mismatch. A failure
after the write started says so and asks you to use Edit > Undo. It does not
call UpdateAll (FontLab issue 8537).

Shared parts: the panel, the plan model, the one-step write and the read-back
come from the App module fly.ap.metrics_panel. This script holds its own
maths, its planner and its controls.

Benefit: exact sidebearing corrections on many glyphs and masters in one step,
with a preview.

Credit: adapted from metrics_sidebearings_tuner.py, the author's own FontLab
sample, Apache-2.0.
"""

from typing import Any

import fly.ap.metrics_panel as metrics_panel  # noqa: PLR0402 - fontlabapp.__getattr__ is native
from fly import qt
from fly.ap.scripting import connect_guarded, show_script_dialog

QtGui = qt.QtGui
MetricsPanel = metrics_panel.panel_type()

# "Add" comes first: the panel opens on "Add 0", a preview that changes nothing.
OPERATIONS = [("Add", "add"), ("Set to", "set"), ("Scale %", "scale")]
NEUTRAL_PERCENT = 100  # "Scale %" start value: no change.
VALUE_RANGE = (-2000, 2000)  # Units, or percent for "Scale %".


# ---------------------------------------------------------------- core
def units(layer: Any) -> tuple[int, int, int, int] | None:
    """Return (lsb, rsb, width, ink width) in whole units, or None for an empty layer."""
    edges = metrics_panel.ink_edges(layer)
    if edges is None:
        return None
    left, right = metrics_panel.unit(edges[0]), metrics_panel.unit(edges[1])
    width = metrics_panel.unit(layer.advanceWidth)
    return left, width - right, width, right - left


def tuned(current: int, mode: str, value: int) -> int:
    """Return the new side in whole units for mode "set", "add" or "scale" (percent)."""
    if mode == "set":
        return value
    if mode == "add":
        return current + value
    return metrics_panel.unit(current * value / 100)


def tuner_planner(
    mode: str, lsb_value: int | None, rsb_value: int | None
) -> metrics_panel.Planner:
    """Return the planner. A side whose value is None keeps its value."""

    def plan(layer: Any, master: str) -> metrics_panel.LayerPlan | str:
        found = units(layer)
        if found is None:
            return "empty (no outline)"
        lsb, rsb, _, ink = found
        new_lsb = lsb if lsb_value is None else tuned(lsb, mode, lsb_value)
        new_rsb = rsb if rsb_value is None else tuned(rsb, mode, rsb_value)
        new_width = new_lsb + ink + new_rsb
        if new_width < 0:
            return "negative width (skipped)"
        cells = tuple(str(v) for v in (lsb, rsb, new_lsb, new_rsb, new_width))
        if (new_lsb, new_rsb) == (lsb, rsb):
            new_width = layer.advanceWidth  # No side changes: keep a fractional width.
        return metrics_panel.make_plan(layer, new_lsb - lsb, new_width, cells)

    return plan


# ---------------------------------------------------------------- panel
class SidebearingsTuner(MetricsPanel):
    """Sidebearings tuner: operation, LSB and RSB values, masters."""

    TITLE = "Sidebearings Tuner"
    KEY = "metrics_sidebearings_tuner"
    HEADERS = ("LSB", "RSB", "New LSB", "New RSB", "New width")
    ACCENT = (3, 4, 5)
    MIN_WIDTH = 580

    def build(self) -> None:
        """Create the operation, the side ticks and the value boxes."""
        self.operation = QtGui.QComboBox()
        for label, _ in OPERATIONS:
            self.operation.addItem(label)
        self.lsb_check = QtGui.QCheckBox("LSB")
        self.lsb_check.setChecked(True)
        self.rsb_check = QtGui.QCheckBox("RSB")
        self.rsb_check.setChecked(True)
        self.lsb_value = self.spin(*VALUE_RANGE, 0, " units")
        self.rsb_value = self.spin(*VALUE_RANGE, 0, " units")
        self.form.addWidget(QtGui.QLabel("Operation"), 1, 0)
        self.form.addWidget(self.operation, 1, 1, 1, 3)
        self.form.addWidget(self.lsb_check, 2, 0)
        self.form.addWidget(self.lsb_value, 2, 1)
        self.form.addWidget(self.rsb_check, 2, 2)
        self.form.addWidget(self.rsb_value, 2, 3)
        self.form.setColumnStretch(3, 1)
        for box in (self.lsb_check, self.rsb_check):
            self.watch(box.toggled)
        self.previous_mode = self.mode_key()
        self.neutral_sides: set[str] = (
            set()
        )  # Sides that hold the 100 put in by the swap.
        connect_guarded(
            self,
            self.operation.currentIndexChanged,
            lambda *a: self.operation_changed(),
        )

    def mode_key(self) -> str:
        """Key of the chosen operation."""
        return OPERATIONS[self.operation.currentIndex][1]

    def operation_changed(self) -> None:
        """Swap the neutral value between 0 units and 100 %. Then refresh.

        Entering "Scale %" turns a 0 into 100 and remembers that side. Leaving
        "Scale %" turns back only a remembered side that still holds 100, so a
        value that the user typed is never lost.
        """
        mode = self.mode_key()
        entering = mode == "scale" and self.previous_mode != "scale"
        leaving = mode != "scale" and self.previous_mode == "scale"
        self.previous_mode = mode
        for side, box in (("lsb", self.lsb_value), ("rsb", self.rsb_value)):
            box.setSuffix(" %" if mode == "scale" else " units")
            if entering and box.value == 0:
                box.setValue(NEUTRAL_PERCENT)
                self.neutral_sides.add(side)
            elif leaving:
                if side in self.neutral_sides and box.value == NEUTRAL_PERCENT:
                    box.setValue(0)
                self.neutral_sides.discard(side)
        self.refresh()

    def sync_controls(self) -> None:
        """A value box is enabled only when its side is ticked."""
        self.lsb_value.setEnabled(self.lsb_check.isChecked())
        self.rsb_value.setEnabled(self.rsb_check.isChecked())

    def subtitle_hint(self) -> str:
        """Describe the current settings."""
        count = len({e.glyph.name for e in self.entries})
        sides = [
            name
            for name, box in (("LSB", self.lsb_check), ("RSB", self.rsb_check))
            if box.isChecked()
        ]
        label = OPERATIONS[self.operation.currentIndex][0]
        what = " and ".join(sides) if sides else "no side"
        return f"{label}: {what} of {count} glyph{'s' if count != 1 else ''}."

    def planner(self, package: Any, glyphs: list[Any]) -> metrics_panel.Planner:
        """Planner for the chosen operation, sides and values."""
        lsb = self.lsb_value.value if self.lsb_check.isChecked() else None
        rsb = self.rsb_value.value if self.rsb_check.isChecked() else None
        return tuner_planner(self.mode_key(), lsb, rsb)


def main() -> Any:
    """Open the panel. A second run replaces the first panel."""
    return show_script_dialog(SidebearingsTuner, SidebearingsTuner.KEY)


if __name__ == "__main__":
    main()
