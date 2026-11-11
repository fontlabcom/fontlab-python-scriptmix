---
this_file: src_docs/md/scripts/reports/compare-open-font-revisions.md
tags: ["Reports"]
categories: ["Reports"]
---

# Compare Open Font Revisions

Compare named glyph fields in two explicitly chosen open font revisions.

What it does:
    Open both fonts, choose each font and master, then Compare and inspect the
    changed-field details. Geometry, advances, anchors and components are read only;
    raw node flags are listed separately. This does not claim complete font equality.

How it works:
    Use the shared App comparison panel for two chosen open fonts and masters.
    Compare named geometry, advance, anchor and component fields; show raw
    flags separately.

Why this design:
    Separate field differences help distinguish a spacing revision from a
    drawing change without claiming complete font equality.

How to use:
    Open both revisions and run Reports > Compare Open Font Revisions. Choose
    each font and master, press Compare and inspect the changed-field details.

Benefit:
    Review the reported differences between revisions without copying data
    between fonts.

Run **Reports > Compare Open Font Revisions** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source identity

SHA256: `3a970598cba29b7dae7fa9c3d6606e4b3488a1d9e84e86bf68051dc74ff449f0`

[Python source at `cb3a95057641`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/cb3a95057641f3b2382a887172fab524dbc4901a/Scripts/Reports/Compare%20Open%20Font%20Revisions.py)
