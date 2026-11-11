# this_file: Scripts/Reports/Nodes Near Zones App.py
# SPDX-License-Identifier: Apache-2.0
# FLM: Reports · Nodes Near Zones App
"""Report open contours of every master with a Select glyphs action in one window.

What: The Nodes Near Zones report: on-curve nodes of the selected glyphs (or all glyphs) that sit 1 to 30 units off the baseline, x-height, cap height, ascender or descender
(glyph, master, zone, node, offset), as a tab of one shared App window with a tolerance control, a Select glyphs button, an About tab and a Close button.

Use: Run Reports > Nodes Near Zones App. Change the tolerance to rescan, or press Refresh after editing; Select glyphs selects the glyphs listed, if the font is still the one reported.
Close the window with Close or Escape. If cleanup is refused, the window stays open and Close can be retried.

Safety: The report is read-only. Only Select glyphs changes the glyph selection, and only for the font that was scanned. Run it
from the main UI thread; the window owns its dialogs and releases them on close.

Source: Original workflow on shared App report providers, Apache-2.0
(fly.ap.fontui.nodes_near_zones). Requires the App with WP08 S66 assembly and
fontlab-fly in FontLab 9 Python 3.11.
"""

from typing import Any


def main() -> Any:
    """Open the Nodes Near Zones app."""
    from fly.ap.fontui.nodes_near_zones import show

    return show()


if __name__ == "__main__":
    main()
