---
this_file: src_docs/md/scripts/contours/transform-studio.md
tags: ["Contours"]
categories: ["Contours"]
---

# Transform Studio

Transform Studio: review outline edits in one modeless window.

What: Open named task tabs for Transform, Slant, Smart Slant, Rotate Selection, Reflect Horizontally, Reflect Vertically and Raise Ascender. Keep the original operation's
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

Run **Contours > Transform Studio** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source identity

SHA256: `e7b0b1f49a4ea5a65363a06d530fc2f9edba624ff39c57ba9604e20052a1a8bb`

[Python source at `cb3a95057641`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/cb3a95057641f3b2382a887172fab524dbc4901a/Scripts/Contours/Transform%20Studio.py)
