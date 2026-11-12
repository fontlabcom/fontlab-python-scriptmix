---
this_file: src_docs/md/scripts/metrics/tmetrics-window.md
tags: ["Metrics"]
categories: ["Metrics"]
---

# TMetrics Window

Set text in the current font and adjust its spacing and kerning.

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

Run **Metrics > TMetrics Window** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source identity

SHA256: `3a844099f2fb1b49f1c8dfcefb60f84a21dc496d624bcf030f569ecc8cb6181b`

[Python source at `cca80db1b47f`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/cca80db1b47f998bbbf4a26427a1e5949ccf7230/Scripts/Metrics/TMetrics%20Window.py)
