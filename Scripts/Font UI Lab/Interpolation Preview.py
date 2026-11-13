# this_file: Scripts/Font UI Lab/Interpolation Preview.py
# SPDX-License-Identifier: Apache-2.0
"""Inspect a read-only interpolation preview at a designspace location.

What: Designspace location controls drive the existing two-master linear outline
preview. Choose a glyph and location to inspect the result; unsupported source
configurations and incompatible outlines are reported instead of being changed.

Use: Open a FontLab font and run this tool. The shared show(font, parent=None)
entry captures that font once; switching the current document does not retarget
the window. Close the window to release its owned controls and callbacks.

Safety: This is an inspection workflow. It never applies interpolation, creates
an instance, edits or saves the font, or switches its master or selection.
The existing preview's two-master linear scope is not a general multi-axis
variation model. Native FontLab rendering and complete font/history/cache
preservation remain separate qualification checks.
"""


def main():
    """Capture the current font once and retain the shared preview owner."""
    from fly.fp.world import FontWorld
    from fly.ap.fontui.interpolation_preview import show

    return show(FontWorld().CurrentFont())


if __name__ == "__main__":
    main()
