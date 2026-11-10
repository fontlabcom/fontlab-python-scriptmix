# this_file: Scripts/Metrics/TMetrics Window.py
# SPDX-License-Identifier: Apache-2.0
"""Set text in the current font and adjust its spacing and kerning.

What: Opens a modeless TMetrics window on the current font. Type text, or
/glyphnames, and choose features, direction, script and language. The canvas
shows the set rows with the baseline, the vertical metric lines, glyph boxes,
sidebearing marks and kerning. The readout gives the selected glyph's advance,
left and right sidebearings and the kerning pair before it. With App's
fontui-shaping extra (uharfbuzz) the text is shaped; without it characters map
to glyphs one to one and the window says the text is unshaped. Edits you make
in FontLab, and Undo or Redo, appear in the window shortly after.

Use: Open a font and run Metrics > TMetrics Window. Type text in the field.
Click a glyph, or press Left, Right, Home or End, to select it. Type a value in
the LSB, RSB, Width or Kerning field and press Return. Alt+Left or Alt+Right
nudges the right sidebearing by 1 unit, and Ctrl+Alt+Left or Ctrl+Alt+Right
nudges the kerning of the pair before the selected glyph; add Shift for steps
of 10. Double-click a glyph to open it in a TGlyph window.

Safety: The window writes only the values you change: the selected glyph's
sidebearings or width on the default layer, and the kerning of the pair before
it. Each write is one named undo step; each auto-repeated nudge is a separate
step. It writes no preferences or clipboard. It prints a message to Output
only when App or Fly is missing. Round-trip with a live FontLab font is not
yet verified natively; try it on a copy first.

Source: Original workflow built on the shared App TMetrics window
(fly.ap.fontui.tmetrics), Apache-2.0.
Requires a FontLabApp build providing fontlabapp.fontui.tmetrics,
with its fontport extra and fontlab-fly in FontLab 9 Python 3.11.
"""

from typing import Any

INSTALL_HINT = (
    "TMetrics Window needs a FontLabApp build providing fontlabapp.fontui.tmetrics, "
    "with Fontport and fontlab-fly: "
    "install 'fontlab-fontlabapp[fontport]' and fontlab-fly into FontLab's Python."
)


def main() -> Any:
    """Open the TMetrics window on the current font, or say what is missing."""
    try:
        from fly.ap.fontui.tmetrics import show_tmetrics
    except ImportError as error:
        print(f"{INSTALL_HINT} ({error})")
        return None
    return show_tmetrics()


if __name__ == "__main__":
    main()
