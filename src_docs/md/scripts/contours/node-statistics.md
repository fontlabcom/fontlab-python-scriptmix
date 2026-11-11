---
this_file: src_docs/md/scripts/contours/node-statistics.md
tags: ["Contours"]
categories: ["Contours"]
---

# Node Statistics

Contours and nodes per glyph and master in one table, with incompatible glyphs flagged.

What it does:
    Each cell reads "contours / nodes" for a master; a glyph is flagged when its masters differ,
    which breaks interpolation. Work on the selection or the whole font, then select the flagged
    glyphs in the Font window with one click. Read-only: nothing in the font changes.

How it works:
    Read contour and node counts on the selection or whole font, grouped by
    master. Flag differing counts and keep the source snapshot for the
    selection action.

Why this design:
    Count differences can rule out compatibility, but matching counts alone do
    not prove matching contour structure.

How to use:
    Run Contours > Node Statistics. Choose the source scope, inspect each
    contours/nodes cell and use the action button to select flagged glyphs in
    the Font window.

Benefit:
    Find count mismatches quickly while preserving node positions, topology
    and layer data.

Run **Contours > Node Statistics** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source identity

SHA256: `8abe2e2384676c82dfd0740e099aa242a089592bb1d21eb7be495e55a2583515`

[Python source at `8852124d9fe2`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/8852124d9fe2b69cf663e1c6db8d6db4bf5e8454/Scripts/Contours/Node%20Statistics.py)
