---
this_file: src_docs/md/scripts/components/count-badges.md
tags: ["Components"]
categories: ["Components"]
---

# Count Badges

A painted card per selected glyph: its drawing plus component and contour counts for every master.

What it does:
    Accent badges count components, muted badges count the glyph's own contours; a
    master that differs from the first one is marked with a dot, and auto layers are
    labelled. A quick way to see which glyphs are composites, outlines or a mix.
    Nothing in the font is changed.

How it works:
    Use the shared component card view for the selected glyphs. Draw each
    glyph and count its own contours and components per master, marking
    differences from the first master.

Why this design:
    Counts beside the drawing make mixed outline/component construction easier
    to spot than names alone.

How to use:
    Select glyphs and run Components > Count Badges. Inspect each master's
    badges, mismatch dots and automatic-layer labels; scroll or resize to view
    more cards.

Benefit:
    Review construction differences without decomposing components or editing
    layer geometry.

Run **Components > Count Badges** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source identity

SHA256: `86e4a5c9f53906b45501249d7c3ebf08e723fa668c92006078197a75f6f69e51`

[Python source at `ba6f2dfbe4d6`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/ba6f2dfbe4d6759bc53d77827e64a3d6ccee96e3/Scripts/Components/Count%20Badges.py)
