# this_file: Scripts/Metrics/Centre In Advance.py
# SPDX-License-Identifier: Apache-2.0
"""Centre the outline of each selected glyph in its advance width.

What it does: moves the outline so that both sidebearings are equal. You can
also give the glyph a new advance width at the same time: keep it, set it, or
change it by an amount.

How it works: the white space is the new width minus the width of the ink.
The left sidebearing is half of it, in whole units. The right sidebearing
takes the odd unit. Anchors move with the outline. A glyph without outline is
listed and skipped. A negative new width is refused for that layer.

Why: symbols, figures, spaces with marks and accents must sit in the middle
of their box. Doing it by hand is slow and error prone.

How to use: select glyphs in the Font window. Choose the width mode and the
value. Choose the current master or all masters. Check the table. Press Apply.
The panel stays open. Press "Use selection" to read the Font window selection
again.

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

Benefit: exact centring in all masters in one step.

Credit: adapted from the author's own rescued FontLab sample
metrics_center_in_advance.py (Apache-2.0).
"""

from typing import Any

import fly.ap.metrics_panel as metrics_panel  # noqa: PLR0402 - fontlabapp.__getattr__ is native
from fly import qt
from fly.ap.scripting import connect_guarded, show_script_dialog

QtGui = qt.QtGui
MetricsPanel = metrics_panel.panel_type()

WIDTH_MODES = [
    ("Keep current width", "keep"),
    ("Set width to", "set"),
    ("Change width by", "add"),
]
WIDTH_DEFAULT = 500  # Start value for "Set width to".


# ---------------------------------------------------------------- core
def centred(
    left: float, right: float, width: float, mode: str, value: int
) -> tuple[int, int, int, int, int]:
    """Return (lsb, rsb, new width, new lsb, new rsb) in whole units.

    left and right are the ink edges. mode is keep, set or add.
    """
    old_width = metrics_panel.unit(width)
    new_width = {"keep": old_width, "set": value, "add": old_width + value}[mode]
    ink = metrics_panel.unit(right) - metrics_panel.unit(left)
    new_lsb = (new_width - ink) // 2
    return (
        metrics_panel.unit(left),
        old_width - metrics_panel.unit(right),
        new_width,
        new_lsb,
        new_width - ink - new_lsb,
    )


def centre_planner(mode: str, value: int) -> metrics_panel.Planner:
    """Return the planner for one width mode and value."""

    def plan(layer: Any, master: str) -> metrics_panel.LayerPlan | str:
        edges = metrics_panel.ink_edges(layer)
        if edges is None:
            return "empty (no outline)"
        lsb, rsb, new_width, new_lsb, new_rsb = centred(
            edges[0], edges[1], layer.advanceWidth, mode, value
        )
        if new_width < 0:
            return "negative width (skipped)"
        cells = (
            f"{metrics_panel.unit(layer.advanceWidth)}",
            f"{lsb}",
            f"{rsb}",
            f"{new_width}",
            f"{new_lsb}",
            f"{new_rsb}",
        )
        return metrics_panel.make_plan(layer, new_lsb - lsb, new_width, cells)

    return plan


# ---------------------------------------------------------------- panel
class CentreInAdvance(MetricsPanel):
    """Centre in advance: width mode, value, masters."""

    TITLE = "Centre In Advance"
    KEY = "metrics_center_in_advance"
    HEADERS = ("Width", "LSB", "RSB", "New width", "New LSB", "New RSB")
    ACCENT = (4, 5, 6)
    MIN_WIDTH = 620

    def build(self) -> None:
        """Create the width mode and value controls."""
        self.mode = QtGui.QComboBox()
        for label, _ in WIDTH_MODES:
            self.mode.addItem(label)
        self.value = self.spin(-5000, 5000, 0, " units")
        self.form.addWidget(QtGui.QLabel("Width"), 1, 0)
        self.form.addWidget(self.mode, 1, 1)
        self.form.addWidget(self.value, 1, 2, 1, 2)
        self.watch(self.mode.currentIndexChanged)
        connect_guarded(
            self, self.mode.currentIndexChanged, lambda *a: self.mode_changed()
        )
        self.mode_changed()

    def mode_key(self) -> str:
        """Key of the chosen width mode."""
        return WIDTH_MODES[self.mode.currentIndex][1]

    def mode_changed(self) -> None:
        """Enable the value only when it is used. Offer a start value for "set"."""
        key = self.mode_key()
        self.value.setEnabled(key != "keep")
        if key == "set" and self.value.value <= 0:
            self.value.setValue(WIDTH_DEFAULT)
        elif key == "add":
            self.value.setValue(0)

    def subtitle_hint(self) -> str:
        """Describe the current settings."""
        count = len({e.glyph.name for e in self.entries})
        return (
            f"Centres the outline of {count} glyph{'s' if count != 1 else ''} in the advance. "
            "The right sidebearing takes an odd unit."
        )

    def planner(self, package: Any, glyphs: list[Any]) -> metrics_panel.Planner:
        """Planner for the chosen width mode and value."""
        return centre_planner(self.mode_key(), self.value.value)


def main() -> Any:
    """Open the panel. A second run replaces the first panel."""
    return show_script_dialog(CentreInAdvance, CentreInAdvance.KEY)


if __name__ == "__main__":
    main()
