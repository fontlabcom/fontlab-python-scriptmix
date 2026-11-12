---
this_file: src_docs/md/scripts/contours/align-and-nudge.md
tags: ["Contours"]
categories: ["Contours"]
---

# Align and Nudge

Align and Nudge: review outline edits in one modeless window.

What: Open named task tabs for Align And Distribute, Superaligner, Interpolated Nudge and Overlap Nodes. Keep the original operation's
numerical rules, selection policy and guarded native writer. The generous glyph
preview shows the captured font and explicit layer; it cannot edit by dragging.

How: Choose a task and its controls, then Preview Changes. Inspect the result
rows, including skipped glyphs and refusals, before Apply Changes. Changing the
font, selected target, controls or geometry invalidates the accepted preview.
Discard preview before Refresh. Table columns can be resized and rows resorted;
activating a row retains its captured glyph and layer.

Why: Related outline operations belong together without losing their different
master, auxiliary-layer, component and history scopes. A refused or partial
write remains visible; use the operation's Undo guidance before continuing.

Use: Open a font, select the intended glyphs or editor layers, run this menu,
and choose the named task. Read each task's scope before applying. Close retires
owned callbacks; a failed Close keeps its owner available for another attempt.

Credits: FontLab App and Scriptmix contributors, Apache-2.0; independent
adaptations after Simon Cozens' GlyphsScripts, MIT. Original attribution and
immutable source identities remain in Scriptmix NOTICE and provenance records.
Setup: Requires the matching FontLab App outline-studio composition through Fly.

Run **Contours > Align and Nudge** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source identity

SHA256: `70ff92140aff5b50cdf2590a0d38e5c59234e4e2353537a747b1d5fd79a553ba`

[Python source at `b52710a04ed5`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/b52710a04ed5e9e3759b7086daeb0b09ec65b6f3/Scripts/Contours/Align%20and%20Nudge.py)
