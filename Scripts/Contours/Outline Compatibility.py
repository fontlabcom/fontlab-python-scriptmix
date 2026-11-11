# this_file: Scripts/Contours/Outline Compatibility.py
# SPDX-License-Identifier: Apache-2.0
# FLM: Contours · Outline Compatibility
"""Compare contour order, promote matching straight segments and inspect node counts.

What it does:
    Open Contour Order View, Make Compatible and Node Statistics in one tabbed
    window with a read-only glyph canvas. Compare every master with numbered
    contours, start dots and first-segment arrows. Inspect sortable count rows
    and select the flagged glyphs in the Font window without changing outlines.

How it works:
    The window captures its font and master. Make Compatible retains the
    original line-to-cubic policy: compare corresponding closed PostScript
    segments across every declared master, keep mismatched or unsupported
    glyphs, preserve endpoints and use the existing guarded history writer.
    Shared, locked and automatic outlines remain protected by the common guards.

How to use:
    Select glyphs, run Contours > Outline Compatibility, and choose a task.
    Align contour starts and directions before promoting segments. Use Preview
    Changes to review a write, then Apply Changes. Discard Preview before
    refreshing staged work. Changing the font or master requires reopening.
    Select a table row to inspect its captured glyph and master in the canvas.

Credits:
    FontLab sample inspectors, Apache-2.0. Make Compatible is an independent
    behaviour adaptation after Simon Cozens, GlyphsScripts (2017), MIT:
    https://github.com/simoncozens/GlyphsScripts . No original code was copied.
    Full source identities and licence notices are retained in Scriptmix NOTICE.
    Requires FontLab App with Outline Compatibility and the shared studio shell.
"""


def main():
    """Open the shared App composition without importing another menu script."""
    from fly.ap.fontui import show_outline_compatibility

    return show_outline_compatibility()


if __name__ == '__main__':
    main()
