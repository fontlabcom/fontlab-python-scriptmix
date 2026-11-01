# this_file: Scripts/Masters/Width Chart.py
# SPDX-License-Identifier: Apache-2.0
# FLM: Masters · Width Chart
"""Line chart of the advance widths of the selected glyphs across masters.

What it does:
    Masters run left to right in axis order; each glyph is one line with its widths labelled, so a
    master that breaks the progression stands out at once. Read-only.

How it works:
    Read selected glyph widths in master axis order. Draw one labelled series
    per glyph through the shared Masters chart, with a limit on displayed
    series.

Why this design:
    A chart makes a reversed width progression easier to see than a table of
    individual values.

How to use:
    Select glyphs in the Font window. Run Masters > Width Chart. Compare each
    line and its labels; select fewer glyphs if the series limit hides a
    glyph.

Benefit:
    Find masters that need spacing review without changing advance widths or
    outlines.
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
    masters_make_table as make_table,  # noqa: F401 - original helper interface
)

QtCore, QtGui = qt.QtCore, qt.QtGui
fontlab = ap.fontlab
_api = masters_api()
muted = _api.muted
selected_names = _api.selected_names
master_layers = _api.master_layers
widths = _api.widths
master_order = _api.master_order
nice_ticks = _api.nice_ticks
label_tops = _api.label_tops
spread = _api.spread
LineChart = masters_view_types().LineChart
series_colors = masters_view_types().series_colors
TITLE = "Width Chart"
KEY = "masters_width_chart"
MAX_SERIES = 12


class SampleDialog(masters_dialog_type()):
    """Keep the original per-menu shell interface on the shared owned panel."""

    def __init__(self, parent: Any = None) -> None:
        """Build every control before initial binding or native reads."""
        super().__init__(parent, TITLE, KEY)


class WidthChart(SampleDialog):
    """Complete original read-only Masters tool with guarded native actions."""

    ACTION = None

    def build(self) -> None:
        """Build every original chart/table/tree control and guarded action connection."""
        self.setMinimumWidth(620)
        self.chart = LineChart()
        self.chart.report = self.paint_report
        self.root.addWidget(self.chart, 1)

    @masters_snapshot_refresh
    def refresh(self) -> None:
        """Read and render complete results from the original bound font and selection."""
        if not hasattr(self, "chart"):
            return
        self.data = {}
        if not self.describe_selection():
            self.chart.series = []
            self.chart.update()
            return
        order = master_order(self.package)
        for glyph in self.glyphs()[:MAX_SERIES]:
            self.data[glyph.name] = widths(glyph, order)
        self.chart.masters = order
        self.chart.series = [
            (name, [w for (_, w) in row]) for (name, row) in self.data.items()
        ]
        self.chart.update()
        extra = len(self.glyphs()) - MAX_SERIES
        note = f" · first {MAX_SERIES} glyphs shown" if extra > 0 else ""
        self.status.setText(f"Advance widths across {len(order)} masters{note}")


def main() -> Any:
    """Replace and show this owned original Masters tool."""
    return show_script_dialog(WidthChart, KEY)


if __name__ == "__main__":
    main()
