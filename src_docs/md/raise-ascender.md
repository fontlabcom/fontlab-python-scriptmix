---
this_file: src_docs/md/raise-ascender.md
---
# Raise Ascender

Choose **Contours > Raise Ascender** in Scriptmix (App .157 or later). Enter an Amount (default `10`).
**Raise this master**, the default action, processes every currently selected
layer occurrence in selection order. Repeated occurrences remain repeated.
**Raise all masters** processes every foreground layer of the first selected
glyph, including auxiliary/service layers; its historical label does not mean
master layers only. Both actions leave the window and Amount open.

Every own path node, including off-curve controls and quadratic nodes, moves by
Amount when its current layer-space y is **strictly greater than xHeight + 10**
for that layer's associated master. Components remain unchanged. A repeated
negative move can cross the threshold, so the next occurrence then does nothing.
Each changed occurrence creates a separate native Undo notification. No-op
occurrences do not manufacture history. The original overlapping controls have
been laid out separately; action names, default and input remain intact.

The original source is Simon Cozens' MIT `GlyphsScripts/Raise Ascender.py`.
The original loop and all target domains remain the contract. The FontLab writer
stages detached shapes, restores raw node flags/names and ShapeData notes after
native cloning, and keeps all untouched components/shapes attached. The complete
action is preflighted before the first history operation. Changes to font,
selection, metrics or geometry stop later occurrences. Failures are diagnosed,
notification is attempted after an attempted mutation, and no global Undo or
UpdateAll is invoked. Inspect any retained partial changes with Edit > Undo.
This balanced failure handling intentionally repairs the original swallowed,
potentially unbalanced Undo errors.

Native qualification is pending. Exact named masters and unambiguous imported
`masterName.auxName` associations are supported in source; an arbitrary auxiliary
association or implicit editor slot is not guessed from the active master.
Generated/nested geometry, locked layers, hinted shape replacement, automatic
layers/dependants and pending native update queues have explicit whole-action
refusals. These remain **incomplete original domains**, not completed by refusal.
Finite input/results are required for native safety; NaN/infinity are never
silently normalized. Metadata, history/Redo and full saved/reopened font
preservation still require owned FontLab qualification. No font selection,
master, live installation, preferences or clipboard is changed by opening UI.

Retained callbacks are inert after normal Close or parent destruction. A failed
Close keeps the live error diagnosis available while cleanup can be retried.
