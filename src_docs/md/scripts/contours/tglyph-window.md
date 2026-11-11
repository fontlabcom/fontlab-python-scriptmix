---
this_file: src_docs/md/scripts/contours/tglyph-window.md
tags: ["Contours"]
categories: ["Contours"]
---

# TGlyph Window

View and edit one glyph of the current font on a layer you choose.

What: Opens a modeless TGlyph window on FontLab's current glyph and the
default layer. The canvas draws the filled outline, on-curve and off-curve
points with handles, the start point, components, named anchors, the
baseline, the advance box and the vertical metric lines. Choose another layer
from the layer list, type a glyph name, or step with Prev and Next. Turn on
"Follow FontLab current glyph" to switch with FontLab. Edits you make in
FontLab, and Undo or Redo, appear in the window shortly after.

Use: Open a font and run Contours > TGlyph Window. Zoom with the wheel, + and -,
or 0 to fit; pan with space-drag or a middle-button drag. Click a point to
select it, Shift-click to add or remove one, or drag a selection rectangle.
Drag selected points, nudge them with the arrow keys (Shift: 10 units) or
press Delete to remove them. Press P for the pen tool to add line points to a
new contour; click its first point to close it, press Escape to end it and V
to return to selection.

Safety: Each gesture writes once, on release or on the key, and only to the
shown layer, as one undo step; each auto-repeated nudge is a separate step. A
drag only previews until you release it, and a refused write is undone with
its reason in the status line. FontLab writes are refused for glyphs with
several, transformed or hinted shapes, or fractional anchors. The pen tool's first
click leaves a one-point contour. Components are shown but not editable. It
writes no preferences or clipboard, and prints a message to Output only when
App or Fly is missing. Round-trip with a live FontLab font is not yet verified
natively; try it on a copy first.

Source: Original workflow built on the shared App TGlyph window
(fly.ap.fontui.tglyph), Apache-2.0.
Requires a FontLabApp build providing fontlabapp.fontui.tglyph,
with its fontport extra and fontlab-fly in FontLab 9 Python 3.11.

Run **Contours > TGlyph Window** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source identity

SHA256: `e2e36a8244fe8cbd29917feb1ffc70bb4e0078663d2f6ec61f8f739091fc625c`

[Python source at `8852124d9fe2`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/8852124d9fe2b69cf663e1c6db8d6db4bf5e8454/Scripts/Contours/TGlyph%20Window.py)
