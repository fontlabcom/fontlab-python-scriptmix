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

## Source identity

SHA256: `8941501701b629d0a2deccd90187f9dd22e1532ef393e4fb9a3382527efc1209`

[Python source at `6b1048c4f1db`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/6b1048c4f1dbc64ebe49d419db9193ccb3d9a9f0/Scripts/Masters/Overview.py)
