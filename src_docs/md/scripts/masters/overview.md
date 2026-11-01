---
this_file: src_docs/md/scripts/masters/overview.md
tags: ["Masters"]
categories: ["Masters"]
---

# Overview

One table of all masters: axis location, vertical metrics and italic angle.

What it does:
    Rows follow the font's master order; the current master is bold. Vertical metrics come from
    ``fontlab.FontMetrics(package, master)``; FontLab has no per-master italic-angle accessor, so each
    master is made current for the read and the original master is restored. Double-click a row to
    make that master current. Read-only otherwise.

How it works:
    Use the shared Masters report to read axis locations and vertical metrics.
    Temporarily activate masters for italic-angle access, then restore the
    original master.

Why this design:
    The explicit current-master action is separate from the report read, so
    reviewing rows does not leave a different master active.

How to use:
    Run Masters > Overview. Inspect the master rows and bold current entry.
    Double-click a row only when that master should become current in FontLab.

Benefit:
    Compare master metadata in one table and navigate masters without changing
    stored values.

Run **Masters > Overview** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/2b42521906afbad032dff6a9cba444fb3bd6d453b949c3fe055252e30ef145dc.py)
<!--/codeinclude-->
