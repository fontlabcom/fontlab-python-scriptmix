# this_file: Scripts/Reports/Metric Reports.py
# SPDX-License-Identifier: Apache-2.0
# FLM: Reports · Metric Reports
"""Report vertical metrics of every master in every open font in one window.

What: The Vertical Metrics Reporter report: eight stored vertical metric values for every master in every open font, as a tab of one shared App
window with an About tab (source links and credits) and a Close button.

Use: Run Reports > Metric Reports. Read the report and press Refresh after changing metrics or opening fonts.
Close the window with Close or Escape. If cleanup is refused, the window stays open and Close can be retried. Sidebearing Direction Marker is a live
Glyph-window overlay and keeps its own menu.

Safety: Reports are read-only. They do not change glyphs, layers, selection,
history, preferences or the clipboard unless you choose to copy text. Run it
from the main UI thread; the window owns its dialogs and releases them on close.

Source: Original workflows on shared App report providers, Apache-2.0
(fly.ap.fontui.metric_reports). Requires the App with WP08 S63 assembly and
fontlab-fly in FontLab 9 Python 3.11.
"""

from typing import Any


def main() -> Any:
    """Open the Metric Reports app."""
    from fly.ap.fontui.metric_reports import show

    return show()


if __name__ == "__main__":
    main()
