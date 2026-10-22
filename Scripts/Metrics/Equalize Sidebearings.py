# this_file: Scripts/Metrics/Equalize Sidebearings.py
# SPDX-License-Identifier: Apache-2.0
"""Make the left and right sidebearings of each selected glyph equal.

What it does: gives both sidebearings the same value, on the current master or
on all masters. Five rules are available. "Average of both" keeps the advance
width and splits the white space. "Both = LSB", "Both = RSB", "Both = the
smaller" and "Both = the larger" copy one value to the other side, so the
advance width changes.

How it works: the sidebearings are read from the outline edges in whole units.
For "Average of both", the left side gets half of the white space, rounded
down; the right side takes the odd unit. The outline moves in place (anchors
move with it) and the advance gets the new width. A layer without outline is
listed and skipped. A rule that gives a negative width is refused for that
layer.

Why: symmetric letters such as O, H, o and n, and many symbols, start with equal
sidebearings. Setting both sides by hand in each master is slow and error prone.

How to use: select glyphs in the Font window. Choose the rule. Choose the
current master or all masters. Check the table. Press Apply. The panel stays
open. Press "Use selection" to read the Font window selection again.

Safety: each Apply is recorded as one Undo step. Auto layers are listed and never edited. A
glyph that owns an auto layer is listed and skipped as a whole. Layers with a
metrics link or expression are listed and skipped. A base of auto glyphs is
refused, because FontLab rebuilds the auto glyphs and may lose their anchors
and locks (FontLab issue 8512). Tick "Edit bases of auto glyphs anyway" to go
on. Apply is refused while FontLab has pending glyph updates. After the write
the script reads advance and outline back and reports any mismatch. A failure
after the write started says so and asks you to use Edit > Undo. It does not
call UpdateAll (FontLab issue 8537).

Shared parts: the panel, the plan model, the one-step write and the read-back
come from the App module fly.ap.metrics_panel. This script holds its own
rules, its planner and its controls.

Benefit: symmetric spacing in all masters in one step, with a preview.

Credit: adapted from metrics_equalize_sidebearings.py, the author's own
FontLab sample, Apache-2.0.
"""

from typing import Any

import fly.ap.metrics_panel as metrics_panel  # noqa: PLR0402 - fontlabapp.__getattr__ is native
from fly import qt
from fly.ap.scripting import show_script_dialog

QtGui = qt.QtGui
MetricsPanel = metrics_panel.panel_type()

RULES = [
    ("Average of both (keep width)", "average"),
    ("Both = LSB", "lsb"),
    ("Both = RSB", "rsb"),
    ("Both = the smaller", "min"),
    ("Both = the larger", "max"),
]


# ---------------------------------------------------------------- core
def units(layer: Any) -> tuple[int, int, int, int] | None:
    """Return (lsb, rsb, width, ink width) in whole units, or None for an empty layer."""
    edges = metrics_panel.ink_edges(layer)
    if edges is None:
        return None
    left, right = metrics_panel.unit(edges[0]), metrics_panel.unit(edges[1])
    width = metrics_panel.unit(layer.advanceWidth)
    return left, width - right, width, right - left


def equalized(lsb: int, rsb: int, rule: str) -> tuple[int, int]:
    """Return the new (lsb, rsb). "average" gives the odd unit to the right side."""
    if rule == "average":
        left = (lsb + rsb) // 2
        return left, lsb + rsb - left
    side = {"lsb": lsb, "rsb": rsb, "min": min(lsb, rsb), "max": max(lsb, rsb)}[rule]
    return side, side


def equalize_planner(rule: str) -> metrics_panel.Planner:
    """Return the planner for one rule."""

    def plan(layer: Any, master: str) -> metrics_panel.LayerPlan | str:
        found = units(layer)
        if found is None:
            return "empty (no outline)"
        lsb, rsb, width, ink = found
        new_lsb, new_rsb = equalized(lsb, rsb, rule)
        new_width = new_lsb + ink + new_rsb
        if new_width < 0:
            return "negative width (skipped)"
        cells = tuple(str(v) for v in (lsb, rsb, width, new_lsb, new_rsb, new_width))
        if (new_lsb, new_rsb) == (lsb, rsb):
            new_width = layer.advanceWidth  # Already equal: keep a fractional width.
        return metrics_panel.make_plan(layer, new_lsb - lsb, new_width, cells)

    return plan


# ---------------------------------------------------------------- panel
class EqualizeSidebearings(MetricsPanel):
    """Equalize sidebearings: rule, masters."""

    TITLE = "Equalize Sidebearings"
    KEY = "metrics_equalize_sidebearings"
    HEADERS = ("LSB", "RSB", "Width", "New LSB", "New RSB", "New width")
    ACCENT = (4, 5, 6)
    MIN_WIDTH = 620

    def build(self) -> None:
        """Create the rule control."""
        self.rule = QtGui.QComboBox()
        for label, _ in RULES:
            self.rule.addItem(label)
        self.form.addWidget(QtGui.QLabel("Rule"), 1, 0)
        self.form.addWidget(self.rule, 1, 1, 1, 3)
        self.watch(self.rule.currentIndexChanged)

    def rule_key(self) -> str:
        """Key of the chosen rule."""
        return RULES[self.rule.currentIndex][1]

    def subtitle_hint(self) -> str:
        """Describe the current settings."""
        count = len({e.glyph.name for e in self.entries})
        label = RULES[self.rule.currentIndex][0]
        return (
            f"Equal sidebearings for {count} glyph{'s' if count != 1 else ''}: {label}."
        )

    def planner(self, package: Any, glyphs: list[Any]) -> metrics_panel.Planner:
        """Planner for the chosen rule."""
        return equalize_planner(self.rule_key())


def main() -> Any:
    """Open the panel. A second run replaces the first panel."""
    return show_script_dialog(EqualizeSidebearings, EqualizeSidebearings.KEY)


if __name__ == "__main__":
    main()
