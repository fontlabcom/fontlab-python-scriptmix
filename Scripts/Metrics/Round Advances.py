# this_file: Scripts/Metrics/Round Advances.py
# SPDX-License-Identifier: Apache-2.0
"""Round advance widths to a step. Outlines stay where they are.

What it does: rounds the advance width of each target glyph to a multiple of
the step (2 to 100 units). Choose the nearest multiple, the next one up, or the
next one down. A half step goes up for "nearest".

How it works: the right sidebearing takes the whole change. The left
sidebearing, the outline and the anchors do not move. The table lists only the
layers that change. Each Apply plans again from the live font.

Why: interpolation and scaling leave fractional or odd advances. A rounded
advance keeps the spacing on a clean grid. The left edge that you already set
stays fixed.

How to use: select glyphs in the Font window, or choose all glyphs. Choose the
current master or all masters. Set the step. Check the table. Press Apply. The
panel stays open. Press "Use selection" to read the Font window selection
again.

Safety: each Apply is recorded as one Undo step. Auto layers are listed and
never edited. A
glyph that owns an auto layer is listed and skipped as a whole. Layers with a
metrics link or expression are listed and skipped. A base of auto glyphs is
refused, because FontLab rebuilds the auto glyphs and may lose their anchors
and locks (FontLab issue 8512). This includes a base that reaches an auto
glyph through other composites. Tick "Edit bases of auto glyphs anyway" to go
on. Apply discloses queued ids and their possible date changes. After the write
the script reads advance and outline back and reports any mismatch. A failure
after the write started says so and asks you to use Edit > Undo. It does not
call UpdateAll (FontLab issue 8537).

Shared parts: the panel, the plan model, the one-step write and the read-back
come from the App module fly.ap.metrics_panel. This script holds its own
maths, its planner and its controls.

Benefit: a whole font or a master gets tidy advances in one step.

Credit: adapted from the author's own rescued FontLab sample
metrics_round_advances.py (Apache-2.0).
"""

import math
from typing import Any

import fly.ap.metrics_panel as metrics_panel  # noqa: PLR0402 - fontlabapp.__getattr__ is native
from fly import qt
from fly.ap.scripting import names_font_glyphs, show_script_dialog

QtGui = qt.QtGui
MetricsPanel = metrics_panel.panel_type()

STEP_DEFAULT = 10
DIRECTIONS = [("Nearest", "nearest"), ("Up", "up"), ("Down", "down")]
SOURCES = ["Selected glyphs", "All glyphs in the font"]


# ---------------------------------------------------------------- core
def rounded(width: float, step: int, direction: str) -> int:
    """Return width as a multiple of step. A half goes up for "nearest"."""
    if direction == "up":
        return int(math.ceil(width / step) * step)
    if direction == "down":
        return int(math.floor(width / step) * step)
    return int(math.floor(width / step + 0.5) * step)


def round_planner(step: int, direction: str) -> metrics_panel.Planner:
    """Return the planner. It changes the advance only, never the outline."""

    def plan(layer: Any, master: str) -> metrics_panel.LayerPlan:
        width = layer.advanceWidth
        new = rounded(width, step, direction)
        return metrics_panel.make_plan(
            layer, 0, new, (f"{width:g}", str(new), f"{new - width:+g}")
        )

    return plan


# ---------------------------------------------------------------- panel
class RoundAdvances(MetricsPanel):
    """Round advances: step, direction, glyph source, masters."""

    TITLE = "Round Advances"
    KEY = "metrics_round_advances"
    HEADERS = ("Width", "New width", "RSB change")
    ACCENT = (2,)
    MIN_WIDTH = 520

    def build(self) -> None:
        """Create step, direction and source controls."""
        self.step = self.spin(2, 100, STEP_DEFAULT, " units")
        self.direction = QtGui.QComboBox()
        for label, _ in DIRECTIONS:
            self.direction.addItem(label)
        self.source = QtGui.QComboBox()
        for label in SOURCES:
            self.source.addItem(label)
        self.form.addWidget(QtGui.QLabel("Step"), 1, 0)
        self.form.addWidget(self.step, 1, 1)
        self.form.addWidget(QtGui.QLabel("Round"), 1, 2)
        self.form.addWidget(self.direction, 1, 3)
        self.form.addWidget(QtGui.QLabel("Glyphs"), 2, 0)
        self.form.addWidget(self.source, 2, 1, 1, 3)
        self.watch(self.direction.currentIndexChanged)
        self.watch(self.source.currentIndexChanged)

    def subtitle_hint(self) -> str:
        """Describe the current settings."""
        count = len(self.entries)
        return (
            f"Rounds {count} layer{'s' if count != 1 else ''} to multiples of "
            f"{self.step.value}. Outlines and left sidebearings stay put."
        )

    def target_glyphs(self, package: Any) -> list[Any]:
        """Selected glyphs, or every glyph of the font."""
        if self.source.currentIndex == 0:
            return MetricsPanel.target_glyphs(self, package)
        found = [package.findName(name) for name, _ in names_font_glyphs()]
        return [g for g in found if g is not None and not g.isNull]

    def planner(self, package: Any, glyphs: list[Any]) -> metrics_panel.Planner:
        """Planner for the chosen step and direction."""
        return round_planner(
            self.step.value, DIRECTIONS[self.direction.currentIndex][1]
        )


def main() -> Any:
    """Open the panel. A second run replaces the first panel."""
    return show_script_dialog(RoundAdvances, RoundAdvances.KEY)


if __name__ == "__main__":
    main()
