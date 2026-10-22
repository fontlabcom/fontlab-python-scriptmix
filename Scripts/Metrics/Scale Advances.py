# this_file: Scripts/Metrics/Scale Advances.py
# SPDX-License-Identifier: Apache-2.0
"""Scale advance widths by a percentage. Each outline stays centred.

What it does: multiplies the advance width of each selected glyph by a
percentage (10 to 400 percent). The new width is a whole number of units.

How it works: the change in width is split between both sidebearings. The
outline moves by half of the change. The right sidebearing takes the odd unit.
Anchors move with the outline. The table lists the old width, the new width and
the shift for each layer.

Why: loosening a Bold master or tightening a Display master is a common job.
Splitting the change keeps the balance of every glyph. A plain scale of the
advance alone would push the ink to one side.

How to use: select glyphs in the Font window. Choose the current master or all
masters. Enter the percentage. Check the table. Press Apply. The panel stays
open. Press "Use selection" to read the Font window selection again.

Safety: each Apply is recorded as one Undo step. Auto layers are listed and never edited. A
glyph that owns an auto layer is listed and skipped as a whole. Layers with a
metrics link or expression are listed and skipped. A base of auto glyphs is
refused, because FontLab rebuilds the auto glyphs and may lose their anchors
and locks (FontLab issue 8512). This includes a base that reaches an auto
glyph through other composites. Tick "Edit bases of auto glyphs anyway" to go
on. Apply is refused while FontLab has pending glyph updates. After the write
the script reads advance and outline back and reports any mismatch. A failure
after the write started says so and asks you to use Edit > Undo. It does not
call UpdateAll (FontLab issue 8537).

Shared parts: the panel, the plan model, the one-step write and the read-back
come from the App module fly.ap.metrics_panel. This script holds its own
maths, its planner and its controls.

Benefit: open or tighten the spacing of many glyphs in one step. The
balance of each glyph is kept.

Credit: adapted from the author's own rescued FontLab sample
metrics_scale_advances.py (Apache-2.0).
"""

from typing import Any

import fly.ap.metrics_panel as metrics_panel  # noqa: PLR0402 - fontlabapp.__getattr__ is native
from fly import qt
from fly.ap.scripting import show_script_dialog

QtCore, QtGui = qt.QtCore, qt.QtGui
MetricsPanel = metrics_panel.panel_type()

PERCENT_DEFAULT = 100.0


# ---------------------------------------------------------------- core
def scaled(width: float, percent: float) -> tuple[int, int]:
    """Return the new width and the outline shift for a scale in percent.

    The shift is half of the width change, cut toward zero. The right
    sidebearing takes the odd unit.
    """
    new_width = metrics_panel.unit(width * percent / 100.0)
    return new_width, int((new_width - metrics_panel.unit(width)) / 2)


def scale_planner(percent: float) -> metrics_panel.Planner:
    """Return the planner for one percentage."""

    def plan(layer: Any, master: str) -> metrics_panel.LayerPlan:
        width = layer.advanceWidth
        new_width, dx = scaled(width, percent)
        return metrics_panel.make_plan(
            layer, dx, new_width, (f"{width:g}", str(new_width), f"{dx:+d}")
        )

    return plan


# ---------------------------------------------------------------- panel
class ScaleAdvances(MetricsPanel):
    """Scale advances: percentage and masters."""

    TITLE = "Scale Advances"
    KEY = "metrics_scale_advances"
    HEADERS = ("Width", "New width", "Outline shift")
    ACCENT = (2,)
    MIN_WIDTH = 520

    def build(self) -> None:
        """Create the percentage control."""
        self.percent = QtGui.QDoubleSpinBox()
        self.percent.setRange(10.0, 400.0)
        self.percent.setDecimals(1)
        self.percent.setSingleStep(1.0)
        self.percent.setValue(PERCENT_DEFAULT)
        self.percent.setSuffix(" %")
        self.percent.setAlignment(QtCore.Qt.AlignRight)
        self.watch(self.percent.valueChanged)
        self.form.addWidget(QtGui.QLabel("Scale advances to"), 1, 0)
        self.form.addWidget(self.percent, 1, 1)

    def subtitle_hint(self) -> str:
        """Describe the current settings."""
        count = len({e.glyph.name for e in self.entries})
        return (
            f"Scales the advance of {count} glyph{'s' if count != 1 else ''} to "
            f"{self.percent.value:g} %. The change is split between both sidebearings."
        )

    def planner(self, package: Any, glyphs: list[Any]) -> metrics_panel.Planner:
        """Planner for the chosen percentage."""
        return scale_planner(self.percent.value)


def main() -> Any:
    """Open the panel. A second run replaces the first panel."""
    return show_script_dialog(ScaleAdvances, ScaleAdvances.KEY)


if __name__ == "__main__":
    main()
