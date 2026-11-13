# this_file: Scripts/Font UI Lab/Designspace Source Comparison.py
# SPDX-License-Identifier: Apache-2.0
# FLM: Font UI Lab · Designspace Source Comparison
"""Compare two stored source layers of the current font.

Choose reference/comparison layers and a glyph to inspect advance widths and
structural compatibility. Refresh repeats the read of the captured font, without
switching masters. Missing glyphs and closed fonts are shown as errors. External
designspace sources and interpolation are not loaded. No edits, save or font
closure occur.

The table uses detached backend reads, so unfinished edits held in another
scripting wrapper are excluded. A missing glyph is reported as missing rather
than assigned a zero advance. Zero and fractional widths remain meaningful.
Compatibility checks ordered contour/node types and anchor/component name sets;
it does not compare coordinates, component transforms, hints or interpolation
results. Matching reports therefore do not certify variable-font export.

The window keeps the font captured when the script starts. Changing the host's
current font does not retarget it. Closing the window disconnects its owned
callbacks and releases its widgets without closing the borrowed document.
Native painting, lifecycle and whole-font preservation remain unqualified.
"""


def main():
    """Capture the current font once and retain its owned comparison widget."""
    from fly.fp.world import FontWorld
    from fly.ap.fontui.source_comparison import show

    return show(FontWorld().CurrentFont())


if __name__ == '__main__':
    main()
