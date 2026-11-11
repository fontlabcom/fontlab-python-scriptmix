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

Requires App>=1.2.0 and fontlab-fly in FontLab9 Python3.11.
Adapted from Alex Slobzheninov's Apache-2.0 Point Counter. See NOTICE and
additional-tools.json for source identity and full license provenance.

Run **Reports > Point Counter** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source identity

SHA256: `a36c0a3a0ddf8432dda7118a3f91b662f84898ab5942bb0c130cbf873f7d8ee6`

[Python source at `168b57cbfbaf`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/168b57cbfbaf1b00b43f4aa06ba26d2e01ba12e1/Scripts/Reports/Point%20Counter.py)
