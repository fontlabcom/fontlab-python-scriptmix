# this_file: Scripts/Font UI Lab/Master Compatibility Browser.py
# SPDX-License-Identifier: Apache-2.0
"""Browse glyphs and inspect their existing master-layer compatibility report.

What: Select a glyph to view its preview alongside the layer compatibility findings. The report compares the registered master layers and keeps missing or unsupported data visible. Use the browser to move between glyphs without changing the document selection or current master.

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
    from fontlab_fontport.world import FontWorld
    from fontlabapp.fontui.master_compatibility import show

    return show(FontWorld().CurrentFont())


if __name__ == "__main__":
    main()
