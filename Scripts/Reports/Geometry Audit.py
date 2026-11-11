# this_file: Scripts/Reports/Geometry Audit.py
# SPDX-License-Identifier: Apache-2.0
# FLM: Reports · Geometry Audit
"""Audit glyph geometry in one window: near-misses, dangerous off-curves, SVG path dump and point counts.

What: Five geometry reports on the current glyph and master layers: Close But No Cigar, Dangerous Offcurves, Dump to Svg Path Commands, Point Counter (Master Layers) and Point Counter.
Each report keeps its own capture and text, now as a tab of one shared App
window with an About tab (source links and credits) and a Close button.

Use: Run Reports > Geometry Audit. Pick a tab, read the report and copy or save its
text from the tab. Close the window with Close or Escape. If cleanup is
refused, the window stays open and Close can be retried.

Safety: Reports are read-only. They do not change glyphs, layers, selection,
history, preferences or the clipboard unless you choose to copy text. Run it
from the main UI thread; the window owns its dialogs and releases them on close.

Source: Original workflows on shared App report providers, Apache-2.0
(fly.ap.fontui.geometry_audit). Requires the App with WP08 S60 assembly and
fontlab-fly in FontLab 9 Python 3.11.
"""

from typing import Any


def main() -> Any:
    """Open the Geometry Audit app."""
    from fly.ap.fontui.geometry_audit import show

    return show()


if __name__ == "__main__":
    main()
