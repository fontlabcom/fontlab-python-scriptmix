# this_file: Scripts/Masters/Glyph Weight Chart.py
# SPDX-License-Identifier: Apache-2.0
# FLM: Masters · Glyph Weight Chart
"""Bar chart of the ink area of the selected glyphs in every master.

What it does:
    Ink area is the filled area of the outline: contour areas from the flattened curves, counters
    subtracted by nesting. Overlapping contours are counted twice, so remove overlaps first for exact
    numbers. Each glyph gets one bar per master in axis order, labelled in thousands of square units.
    Read-only.

How it works:
    Use the shared Masters chart and flattened outline areas, subtracting
    counters by nesting. Draw one labelled bar per glyph and master in axis
    order.

Why this design:
    Area bars expose weight differences, but overlapping contours can count
    twice and must be reviewed before treating values as exact filled areas.

How to use:
    Select glyphs and run Masters > Glyph Weight Chart. Compare bars between
    masters; inspect overlap in the source outlines when a value looks
    unexpectedly large.

Benefit:
    Compare the reported ink-area trend without changing outlines or removing
    overlaps.
"""

from typing import Any

from fly import ap, qt
from fly.ap.scripting import (
    current_package,  # noqa: F401 - original public interface
    masters_api,
    masters_dialog_type,
    masters_snapshot_refresh,
    masters_view_types,
    show_script_dialog,
)
from fly.ap.scripting import (
    masters_fill_table as fill_table,
)
from fly.ap.scripting import (
    masters_make_table as make_table,
)

QtCore, QtGui = qt.QtCore, qt.QtGui
fontlab = ap.fontlab
_api = masters_api()
muted = _api.muted
selected_names = _api.selected_names
master_layers = _api.master_layers
node_points = _api.node_points
polygon = _api.polygon
inside = _api.inside
ink_area = _api.ink_area
layer_contours = _api.layer_contours
master_order = _api.master_order
nice_ticks = _api.nice_ticks
BarChart = masters_view_types().BarChart
series_colors = masters_view_types().series_colors
TITLE = "Glyph Weight Chart"
KEY = "masters_glyph_weight_chart"
STEPS = 12
MAX_GLYPHS = 10


class SampleDialog(masters_dialog_type()):
    """Keep the original per-menu shell interface on the shared owned panel."""

    def __init__(self, parent: Any = None) -> None:
        """Build every control before initial binding or native reads."""
        super().__init__(parent, TITLE, KEY)


class WeightChart(SampleDialog):
    """Complete original read-only Masters tool with guarded native actions."""

    ACTION = None

    def build(self) -> None:
        """Build every original chart/table/tree control and guarded action connection."""
        self.setMinimumWidth(620)
        self.chart = BarChart()
        self.chart.report = self.paint_report
        self.root.addWidget(self.chart, 1)
        self.table = make_table(["Glyph"], 90)
        self.root.addWidget(self.table)

    @masters_snapshot_refresh
    def refresh(self) -> None:
        """Read and render complete results from the original bound font and selection."""
        if not hasattr(self, "chart"):
            return
        self.areas = {}
        if not self.describe_selection():
            self.chart.groups = []
            self.chart.update()
            return
        order = master_order(self.package)
        for glyph in self.glyphs()[:MAX_GLYPHS]:
            found = master_layers(glyph, order)
            self.areas[glyph.name] = [
                ink_area(layer_contours(found[m])) if m in found else 0.0 for m in order
            ]
        self.chart.masters = order
        self.chart.groups = list(self.areas.items())
        self.chart.update()
        self.table.setColumnCount(len(order) + 1)
        self.table.setHorizontalHeaderLabels(
            ["Glyph"] + [f"{m} (units²)" for m in order]
        )
        self.table.horizontalHeader().setSectionResizeMode(QtGui.QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(
            0, QtGui.QHeaderView.ResizeToContents
        )
        fill_table(
            self.table,
            [
                (name, *tuple(f"{v:,.0f}" for v in row))
                for (name, row) in self.areas.items()
            ],
        )
        self.status.setText("Ink area per master · overlapping contours count twice")


def main() -> Any:
    """Replace and show this owned original Masters tool."""
    return show_script_dialog(WeightChart, KEY)


if __name__ == "__main__":
    main()
