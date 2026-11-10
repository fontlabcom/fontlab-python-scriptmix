---
this_file: src_docs/md/scripts/anchors/duplicate-anchor-rings.md
tags: ["Anchors"]
categories: ["Anchors"]
---

# Duplicate Anchor Rings

Draw a ring in the Glyph window around anchors that sit on top of each other.

What: Opens a small modeless panel and draws a foreground overlay in the active
Glyph window. Whenever two anchors of one glyph lie less than one unit apart,
a ring appears at that spot, so stacked anchors that look like one are easy to
see. Three coincident anchors give three rings. Choose the handle size 5, 8 or
12 to match your display. The overlay refreshes by itself while the panel is
open and works across all tools.

Use: Open a font and a Glyph window. Run Anchors > Duplicate Anchor Rings.
Leave Enabled ticked, choose the handle size, then inspect your glyphs. Untick
Enabled or press Close to remove the overlay. The panel binds to the font,
master and Glyph window that were active at launch; reopen it after switching
to another one. The status line shows the glyph and ring counts or the reason
why nothing can be drawn.

Safety: Read-only. The tool reads anchor names and positions and paints only
its own overlay. It writes no font data, selection, history, preference,
clipboard or Output text. Close and Enabled off remove the overlay and
disconnect its callbacks. It does not hide or show anything for text or hand
tools; the rings are drawn across tools.

Source: Original workflow built on the shared App anchor ring panel
(fly.ap.core.scripting.canvas_anchor_rings_dialog_type), Apache-2.0.
Requires App>=1.2.0 and fontlab-fly in FontLab 9 Python 3.11.

Run **Anchors > Duplicate Anchor Rings** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source identity

SHA256: `519d0ef143ea90fa1b2e4dde8b2a2b9053530b1dfa0fd6b678788941b31d55f6`

[Python source at `8e06999ef5a2`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/8e06999ef5a237c79364b4efd0758bf8fbd5dee8/Scripts/Anchors/Duplicate%20Anchor%20Rings.py)
