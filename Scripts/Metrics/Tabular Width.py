# this_file: Scripts/Metrics/Tabular Width.py
# SPDX-License-Identifier: Apache-2.0
"""Give figures one shared advance width. Each outline is centred.

What it does: sets the same advance width on a group of glyphs and centres
every outline in it. The group is the figures zero to nine, the figures with
currency signs, or the selected glyphs. The width is the widest glyph of the
group on each master, or a fixed value.

How it works: the table shows old width, new width, old and new left
sidebearing. The widest width is found for each master separately. The white
space is split in two; the right sidebearing takes an odd unit. A glyph without
outline is listed and skipped. Anchors move with the outline.

Why: tabular figures line up in columns of numbers. This script does the
spacing half of that job. The preset groups use the plain names zero to nine.
For figures with suffix names, such as one.tf, select them and use "Selected
glyphs".

How to use: choose the group. Choose "Widest in set" or enter a fixed width.
Choose the current master or all masters. Check the table. Press Apply. The
panel stays open. Press "Use selection" to read the Font window selection
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

Benefit: columns of figures align in every master after one step.

Credit: adapted from the author's own rescued FontLab sample
metrics_tabular_width.py (Apache-2.0).
"""

from typing import Any

import fly.ap.metrics_panel as metrics_panel  # noqa: PLR0402 - fontlabapp.__getattr__ is native
from fly import qt
from fly.ap.scripting import show_script_dialog

QtGui = qt.QtGui
MetricsPanel = metrics_panel.panel_type()

FIGURES = [
    "zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine",
]  # fmt: skip
CURRENCY = [
    "dollar", "cent", "sterling", "yen", "Euro", "euro", "currency", "franc", "lira",
    "rupee", "won",
]  # fmt: skip
SETS = [
    ("Figures (zero to nine)", FIGURES),
    ("Figures and currency signs", FIGURES + CURRENCY),
    ("Selected glyphs", None),
]
WIDTH_MODES = [("Widest in set, per master", "widest"), ("Fixed width", "fixed")]
FIXED_DEFAULT = 500


# ---------------------------------------------------------------- core
def target_widths(
    glyphs: list[Any], masters: list[str], mode: str, fixed: int
) -> dict[str, int]:
    """Map master to the shared width: the widest advance of the group, or the fixed value."""
    if mode == "fixed":
        return dict.fromkeys(masters, fixed)
    widest: dict[str, int] = {}
    for glyph in glyphs:
        for master, layer in metrics_panel.master_layers(glyph, masters).items():
            widest[master] = max(
                widest.get(master, 0), metrics_panel.unit(layer.advanceWidth)
            )
    return widest


def tabular_planner(widths: dict[str, int]) -> metrics_panel.Planner:
    """Return the planner. widths maps master name to the shared width."""

    def plan(layer: Any, master: str) -> metrics_panel.LayerPlan | str:
        edges = metrics_panel.ink_edges(layer)
        if edges is None:
            return "empty (no outline)"
        new_width = widths[master]
        lsb = metrics_panel.unit(edges[0])
        new_lsb = (new_width - (metrics_panel.unit(edges[1]) - lsb)) // 2
        cells = (
            f"{metrics_panel.unit(layer.advanceWidth)}",
            f"{new_width}",
            f"{lsb}",
            f"{new_lsb}",
        )
        return metrics_panel.make_plan(layer, new_lsb - lsb, new_width, cells)

    return plan


# ---------------------------------------------------------------- panel
class TabularWidth(MetricsPanel):
    """Tabular width: glyph group, width mode, masters."""

    TITLE = "Tabular Width"
    KEY = "metrics_tabular_width"
    HEADERS = ("Width", "New width", "LSB", "New LSB")
    ACCENT = (2, 4)
    MIN_WIDTH = 560

    def build(self) -> None:
        """Create group, width mode and fixed width controls."""
        self.group = QtGui.QComboBox()
        for label, _ in SETS:
            self.group.addItem(label)
        self.mode = QtGui.QComboBox()
        for label, _ in WIDTH_MODES:
            self.mode.addItem(label)
        self.fixed = self.spin(1, 5000, FIXED_DEFAULT, " units")
        self.watch(self.group.currentIndexChanged)
        self.watch(self.mode.currentIndexChanged)
        self.form.addWidget(QtGui.QLabel("Glyphs"), 1, 0)
        self.form.addWidget(self.group, 1, 1, 1, 3)
        self.form.addWidget(QtGui.QLabel("Width"), 2, 0)
        self.form.addWidget(self.mode, 2, 1)
        self.form.addWidget(self.fixed, 2, 2, 1, 2)

    def target_glyphs(self, package: Any) -> list[Any]:
        """The preset figure glyphs that exist in the font, or the selection."""
        names = SETS[self.group.currentIndex][1]
        if names is None:
            return MetricsPanel.target_glyphs(self, package)
        found = [package.findName(name) for name in names]
        return [g for g in found if g is not None and not g.isNull]

    def empty_message(self) -> str:
        """Say why no glyph qualifies."""
        if SETS[self.group.currentIndex][1] is not None:
            return "The font has none of these glyphs. Select your figures and use Selected glyphs."
        return MetricsPanel.empty_message(self)

    def sync_controls(self) -> None:
        """Enable the fixed width only in "Fixed width" mode."""
        self.fixed.setEnabled(WIDTH_MODES[self.mode.currentIndex][1] == "fixed")

    def subtitle_hint(self) -> str:
        """Describe the current settings."""
        count = len({e.glyph.name for e in self.entries})
        return f"{count} glyph{'s' if count != 1 else ''} get one shared width and centred outlines."

    def planner(self, package: Any, glyphs: list[Any]) -> metrics_panel.Planner:
        """Planner with the shared width of every master."""
        widths = target_widths(
            glyphs,
            self.chosen_masters(package),
            WIDTH_MODES[self.mode.currentIndex][1],
            self.fixed.value,
        )
        return tabular_planner(widths)


def main() -> Any:
    """Open the panel. A second run replaces the first panel."""
    return show_script_dialog(TabularWidth, TabularWidth.KEY)


if __name__ == "__main__":
    main()
