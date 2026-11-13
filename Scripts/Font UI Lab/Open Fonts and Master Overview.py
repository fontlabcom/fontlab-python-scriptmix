# this_file: Scripts/Font UI Lab/Open Fonts and Master Overview.py
# SPDX-License-Identifier: Apache-2.0
"""Browse every currently open font and inspect its current master metrics.

What: Select a font in the browser to read its current master name and available vertical metrics. Refresh the browser after opening or closing documents. The overview uses the existing master inspection and metrics reports; it does not switch the font or its current master.

Use: Open a FontLab font, then run this menu command. The window borrows the
captured document handles and owns only its controls, preview and callbacks.
Changing the active document does not retarget a captured font silently. Close
this window when finished; reopening it captures the available documents again.

Safety: These are read-only reports of stored font data, not unfinished edits
held in a different scripting wrapper. No font is created, saved, edited or
closed, and no master or document selection is changed by the report. A missing
or closed font is reported by the shared window. Native rendering, window
lifetime and complete font/history preservation require separate host checks.
"""


def main():
    """Capture the explicit target once and return the shared window owner."""
    from fly.fp.world import FontWorld
    from fly.ap.fontui.open_fonts_overview import show

    return show(FontWorld())


if __name__ == "__main__":
    main()
