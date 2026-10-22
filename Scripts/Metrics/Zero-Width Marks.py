# this_file: Scripts/Metrics/Zero-Width Marks.py
# SPDX-License-Identifier: Apache-2.0
"""Set the advance width of combining marks to zero.

What it does: gives each selected combining mark an advance width of 0. A
combining mark is a glyph with a Unicode category of Mn or Me, or a name that
ends in "comb". Other glyphs are ignored unless you clear the filter.

How it works: you choose where the outline goes. "Keep" leaves the outline
in place. "Hang left" moves it left by the old width, so it sits over the
preceding glyph. "Centre" puts the middle of the ink on x = 0. Anchors move
with the outline.

Why: a combining mark must not move the pen. A mark with a width pushes the
base letter and the next letter apart. Marks that attach by anchor need
the zero width and a known place for the ink.

How to use: select the marks in the Font window. Choose the placement and the
masters. Check the table. Press Apply. The panel stays open. Press "Use
selection" to read the Font window selection again.

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

Benefit: all marks in all masters get a correct zero width in one step.

Credit: adapted from the author's own rescued FontLab sample
metrics_zero_width_marks.py (Apache-2.0).
"""

import unicodedata
from typing import Any

import fly.ap.metrics_panel as metrics_panel  # noqa: PLR0402 - fontlabapp.__getattr__ is native
from fly import qt
from fly.ap.scripting import show_script_dialog

QtGui = qt.QtGui
MetricsPanel = metrics_panel.panel_type()

PLACEMENTS = [
    ("Keep outline in place", "keep"),
    ("Hang left by the old width", "hang"),
    ("Centre ink on the origin", "centre"),
]
MARK_CATEGORIES = {"Mn", "Me"}
MAX_CODE_POINT = 0x10FFFF


# ---------------------------------------------------------------- core
def is_mark(glyph: Any) -> bool:
    """True for a name that ends in "comb" or any code point of category Mn or Me."""
    if glyph.name.split(".")[0].endswith("comb"):
        return True
    return any(
        0 <= code <= MAX_CODE_POINT
        and unicodedata.category(chr(code)) in MARK_CATEGORIES
        for code in glyph.unicodes
    )


def zero_planner(placement: str) -> metrics_panel.Planner:
    """Return the planner. The new advance is always 0."""

    def plan(layer: Any, master: str) -> metrics_panel.LayerPlan:
        width = metrics_panel.unit(layer.advanceWidth)
        dx = 0
        if placement == "hang":
            dx = -width
        elif placement == "centre":
            edges = metrics_panel.ink_edges(layer)
            if edges is not None:
                dx = -metrics_panel.unit((edges[0] + edges[1]) / 2)
        return metrics_panel.make_plan(layer, dx, 0, (f"{width}", "0", f"{dx:+d}"))

    return plan


# ---------------------------------------------------------------- panel
class ZeroWidthMarks(MetricsPanel):
    """Zero-width marks: placement, mark filter, masters."""

    TITLE = "Zero-Width Marks"
    KEY = "metrics_zero_width_marks"
    HEADERS = ("Width", "New width", "Outline shift")
    ACCENT = (2, 3)
    MIN_WIDTH = 520

    def build(self) -> None:
        """Create placement and filter controls."""
        self.placement = QtGui.QComboBox()
        for label, _ in PLACEMENTS:
            self.placement.addItem(label)
        self.watch(self.placement.currentIndexChanged)
        self.only_marks = QtGui.QCheckBox(
            "Only combining marks (Mn, Me, or name ending in comb)"
        )
        self.only_marks.setChecked(True)
        self.watch(self.only_marks.toggled)
        self.form.addWidget(QtGui.QLabel("Outline"), 1, 0)
        self.form.addWidget(self.placement, 1, 1, 1, 3)
        self.form.addWidget(self.only_marks, 2, 0, 1, 4)

    def target_glyphs(self, package: Any) -> list[Any]:
        """Selected glyphs, filtered to marks when the box is ticked."""
        glyphs = MetricsPanel.target_glyphs(self, package)
        if self.only_marks.isChecked():
            glyphs = [g for g in glyphs if is_mark(g)]
        return glyphs

    def empty_message(self) -> str:
        """Say why no glyph qualifies."""
        if self.names and self.only_marks.isChecked():
            return "The selection has no combining marks. Select marks, or clear the filter."
        return MetricsPanel.empty_message(self)

    def subtitle_hint(self) -> str:
        """Describe the current settings."""
        count = len({e.glyph.name for e in self.entries})
        return f"Sets the advance of {count} mark{'s' if count != 1 else ''} to 0."

    def planner(self, package: Any, glyphs: list[Any]) -> metrics_panel.Planner:
        """Planner for the chosen placement."""
        return zero_planner(PLACEMENTS[self.placement.currentIndex][1])


def main() -> Any:
    """Open the panel. A second run replaces the first panel."""
    return show_script_dialog(ZeroWidthMarks, ZeroWidthMarks.KEY)


if __name__ == "__main__":
    main()
