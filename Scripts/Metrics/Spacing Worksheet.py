# this_file: Scripts/Metrics/Spacing Worksheet.py
# SPDX-License-Identifier: Apache-2.0
"""Compare candidate advance widths for the selected glyphs before you set them.

What: Opens a modeless worksheet with a table of four rows. In each row, A is
a step in font units and B is how many times to repeat it. The worksheet
multiplies A by B and adds the result to the current advance width of every
selected glyph layer. The report lists each selected layer with its baseline
advance and the four candidate advances, so you can weigh round steps such as
+2, +8, +18 and +32 units side by side.

Use: Select glyphs in a Font window, or glyph layers in a Glyph window. Run
Metrics > Spacing Worksheet. Edit A and B in the table. Press Refresh
Selection after you change the selection, the master or the widths. Press
Reset Factors to restore the four default rows; the captured selection stays.
Close the panel when you are done. When nothing is selected, the report says
so and the table stays usable.

Safety: Read-only. The candidates are a decision aid and are never applied.
The tool reads the advance widths of the selected glyph layers. It writes no
font data, metrics, selection, history, preference, clipboard or Output text.
If the font, master, selection or widths change while the tool reads them, it
refuses to publish a partial result and keeps the last complete report.

Source: Original workflow built on the shared App spacing worksheet
(fly.ap.metrics.worksheet.model), Apache-2.0.
Requires App>=1.2.0 and fontlab-fly in FontLab 9 Python 3.11.
"""

from typing import Any


def main() -> Any:
    """Open the shared spacing worksheet, or replace the one already open."""
    from fly.ap.metrics.worksheet.model import show

    return show()


if __name__ == "__main__":
    main()
