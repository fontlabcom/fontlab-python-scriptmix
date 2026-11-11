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

## Source identity

SHA256: `7b722c2fea65efa91e09985e213f4b2db0a2536fa59d6eb861151de6d3338eb0`

[Python source at `dc797fffaa31`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/dc797fffaa31fa6c47959870966e2642fe1df6f7/Scripts/Kerning/Remove%20Small%20Pairs.py)
