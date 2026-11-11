# this_file: Scripts/Reports/Master Structure Audit.py
# SPDX-License-Identifier: Apache-2.0
# FLM: Reports · Master Structure Audit
"""Check master structure in one window: node compatibility and the reason masters do not interpolate.

What: Two compatibility reports: Master Node Compatibility Report and Why You Not Compatible.
Each report keeps its own capture and text, now as a tab of one shared App
window with an About tab (source links and credits) and a Close button.

Use: Run Reports > Master Structure Audit. Pick a tab, read the report and copy or save its
text from the tab. Close the window with Close or Escape. If cleanup is
refused, the window stays open and Close can be retried.

Safety: Reports are read-only. They do not change glyphs, layers, selection,
history, preferences or the clipboard unless you choose to copy text. Run it
from the main UI thread; the window owns its dialogs and releases them on close.

Source: Original workflows on shared App report providers, Apache-2.0
(fly.ap.fontui.master_structure_audit). Requires the App with WP08 S61 assembly and
fontlab-fly in FontLab 9 Python 3.11.
"""

from typing import Any


def main() -> Any:
    """Open the Master Structure Audit app."""
    from fly.ap.fontui.master_structure_audit import show

    return show()


if __name__ == "__main__":
    main()
