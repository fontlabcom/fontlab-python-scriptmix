---
this_file: src_docs/md/scripts/kerning/remove-small-pairs.md
tags: ["Kerning"]
categories: ["Kerning"]
---

# Remove Small Pairs

Delete kerning pairs whose value is smaller than a threshold, on one or all masters.

What it does:
    Tiny pairs (±1 … ±5 units) are invisible in print, bloat the kern feature and often come from
    auto-kerning or interpolation. The preview lists every pair that would go, with the count per
    master; zero pairs are included. Class pairs (@name) count like glyph pairs. One Apply is one
    Undo step for all masters.

How it works:
    Read explicit glyph and class pairs, compare their magnitudes with the
    chosen threshold and stage every deletion before calling the shared
    kerning writer.

Why this design:
    Zero and small pairs can still be intentional, so the complete preview
    leaves the deletion choice visible.

How to use:
    Run Kerning > Remove Small Pairs. Choose the threshold and master scope,
    inspect the pair list and counts, then Apply to remove the displayed
    candidates.

Benefit:
    Clean a chosen explicit-pair range in one recorded Undo step across the
    selected masters.

Run **Kerning > Remove Small Pairs** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/50c387064d616231cbd5664bc63e7c1e8b22b62df2c59c7f737b48e336a03c40.py)
<!--/codeinclude-->
