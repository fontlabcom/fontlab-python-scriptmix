---
this_file: src_docs/md/scripts/masters/sync-sidebearings.md
tags: ["Masters"]
categories: ["Masters"]
---

# Sync Sidebearings

Copy sidebearings from a reference master to the other masters.

What it does:
    For each selected glyph, give the layers of the other masters the left
    and right sidebearings of the reference master. "Proportional to ink
    width" scales the reference sidebearings by the ratio of the ink widths
    (target / reference), so bolder masters keep the same rhythm. "Same
    values" copies them unchanged. The outline, components and anchors move
    together, and the advance width follows.

How it works:
    The ink edges are the outline bounding box. New LSB and RSB are rounded
    half up to whole units. The script moves the layer by the LSB change and
    sets the advance width to new LSB + ink width + new RSB. The panel is the
    shared Metrics panel (fly.ap.metrics_panel): a live preview table, the
    masters choice (the current master or all masters; the reference itself
    is never a target), one Undo step per Apply and a read-back of advance
    and outline edge.

Why this design:
    - The shared panel moves outlines in place (applyTransform), never
      through a clone, so node flags and shape notes stay (fl#8516, fl#8538).
    - Automatic layers and glyphs that own one are listed and skipped.
      Layers with a metrics link or expression are listed and skipped: the
      link would undo the change. A base of automatic composites needs the
      "Edit bases of auto glyphs anyway" tick, because FontLab rebuilds the
      automatic glyphs and may lose their anchors and locks. Apply discloses
      queued ids and their possible date changes.
    - A glyph without outline in the reference or the target is listed and
      skipped: it has no sidebearings.
    - Values round half up, not to the nearest even number: 52.5 becomes 53.

How to use:
    Space the reference master first. Select glyphs in the Font window. Run
    the script. Choose the reference and the rule. Check the table. Press
    Apply. The panel stays open; press "Use selection" for other glyphs.

Benefit:
    Consistent spacing across all masters in one step, as a start for
    fine-tuning the extremes.

Credit:
    Adapted from the author's own FontLab sample, Apache-2.0
    (masters_sync_metrics.py, "Sync Sidebearings").

Run **Masters > Sync Sidebearings** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/57fad459de7449071fa1e8d4db721af14e0d187c3f0a929c5cd28089999bd191.py)
<!--/codeinclude-->
