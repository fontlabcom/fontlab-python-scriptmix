---
this_file: src_docs/md/scripts/metrics/italic-sidebearings.md
tags: ["Metrics"]
categories: ["Metrics"]
---

# Italic Sidebearings

Report and set sidebearings along the italic angle.

What it does: shows two pairs of sidebearings for each layer. The plain pair
is the distance from the advance edge to the ink, measured sideways. The
italic pair is measured after the outline is de-slanted by the italic angle.
You can add to the italic values or set them.

How it works: the script maps the outline through a shear around the height
"measured at" (half of the x-height by default). The sheared outline gives
the italic edges. A change moves the real outline sideways and changes the
advance. Anchors move with the outline. All values are whole units.

Why: in a slanted design the plain sidebearings depend on the overhang of the
slant. The italic sidebearings let you compare and space an italic "n" and
"o" as if they were upright.

How to use: select glyphs in the Font window. Check the angle and the height.
Choose "Add" or "Set". Tick LSB and RSB and enter the values. Choose the
current master or all masters. Check the table. Press Apply. The panel stays
open. Press "Use selection" to read the Font window selection again.

Safety: one Apply is one Undo step. Auto layers are listed and never edited.
Layers with a metrics link or expression are listed and skipped. A base of
auto glyphs is refused, because FontLab rebuilds the auto glyphs and may lose
their anchors and locks (FontLab issue 8512). Tick "Edit bases of auto glyphs
anyway" to go on. After the write the script reads advance and outline back
and reports any mismatch. It does not call UpdateAll (FontLab issue 8537).
Native Undo/Redo/reopen of in-place moves is pending.

Benefit: you space italics with the same method as upright designs.

Credit: independent rewrite of the author's own rescued FontLab sample
metrics_italic_sidebearings.py (Apache-2.0).

Run **Metrics > Italic Sidebearings** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/1e9918338f977408be8e0d294bb702d586a0a913192cb7079d3fa6e82b97d54e.py)
<!--/codeinclude-->
