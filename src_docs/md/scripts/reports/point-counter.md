---
this_file: src_docs/md/scripts/reports/point-counter.md
tags: ["Reports"]
categories: ["Reports"]
---

# Point Counter

Count own contour nodes in all foreground layers of selected glyphs.

Select glyphs in a Font window or occurrences in a Glyph window, then run this
Reports command. Each selected occurrence emits its glyph's complete foreground
layer list in stored order, including auxiliary and empty layers. Repeated
selections remain repeated. Components are not decomposed. Masks and service
layers are background/cache records and are excluded explicitly.

Each row shows points, lines, curves, offcurves and paths. The original '?'
marker compares a row's total with the previous two rows. Quadratic on-curves
now count as curves, correcting the source's omission from point totals.
Refresh replaces the complete snapshot. Select and copy report text normally.
Close removes the owned modeless panel. This adaptation uses an owned report
instead of clearing/writing the user's Output panel; no font, selection,
history or preference writers are called. Native getter preservation, layer
mapping, selection order/focus and lifecycle acceptance are pending.

Requires reviewed App>=0.2.35.dev1 and fontlab-fly in FontLab9 Python3.11.
Adapted from Alex Slobzheninov's Apache-2.0 Point Counter. See NOTICE and
additional-tools.json for source identity and full license provenance.

Run **Reports > Point Counter** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/6b39fa3438092faf1644e9efde81d32fd7be7392cb59902f518d746d627c4616.py)
<!--/codeinclude-->
