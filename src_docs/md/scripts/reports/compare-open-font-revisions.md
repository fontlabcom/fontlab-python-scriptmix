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

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/ca119bf8c8abe99248f02b77efd33e1c9eb8640f323ef0f3afd98dc953fb79ed.py)
<!--/codeinclude-->
