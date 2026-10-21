---
this_file: src_docs/md/scripts/contours/node-duplicator.md
tags: ["Contours"]
categories: ["Contours"]
---

# Node Duplicator

Insert coincident nodes, with optional coincident cubic handles.

What: Duplicate selected on-curve nodes in selected editor layers or masters.
How: Read node indices from each glyph's selected reference layer. Require the same
contour closure and node types in every target master, then insert backwards.
The optional two handles create a zero-length cubic instead of a line.
Why: One selection controls corresponding nodes across masters. Unrelated
glyphs never inherit indices from the first glyph. The table previews counts.
Use: Select nodes, open this panel, choose scope and handles, then Duplicate.
Reload selection after changing glyphs. Disable Keep masters compatible only
when you intend to edit the current master separately.
Benefit: Prepare matching contour construction without dragging new nodes.

Locked, shared, transformed, quadratic and automatic outlines are kept and
listed. Other glyphs in the selection can still be edited.
Master scope targets only master layers. Only selected editor layers also
supports manual auxiliary layers and intentionally changes their structure
without a cross-master compatibility check. The change is recorded as one Undo step.
Existing nodes and shape metadata stay; new nodes are sharp. Both handle
positions coincide with the selected point, so the added segment has no area.

Independent behaviour-only rewrite after Fernando Díaz, Reset Type Studio,
https://github.com/Reset-Type-Studio/Glyphs-Scripts, Apache-2.0 declared in
README.md (no separate LICENSE file). Sources: Paths/Node Duplicator
(all masters).py, Paths/Node Duplicator (current layer).py, and
Paths/Node Duplicator + 2 Handles (all masters).py. No source code copied.

Run **Contours > Node Duplicator** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/5198e82e99f2721cb046c0e5a98ca8191dcf285e9f5869d7d7dd96fafa668633.py)
<!--/codeinclude-->
