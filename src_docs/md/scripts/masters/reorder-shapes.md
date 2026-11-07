---
this_file: src_docs/md/scripts/masters/reorder-shapes.md
tags: ["Masters"]
categories: ["Masters"]
---

# Reorder Shapes

Apply a reference shape order across matching layers of selected glyphs.

What: Sort outlines by total node count then rounded y/x, and components by
base name then rounded y/x. Derive the index permutation once from the current
master, or the first declared master present in the glyph.
How: Apply that same permutation only to layers whose ordered shape signatures
match the reference. Keep shape groups and internal contour order intact.
Why: Bring to Front and Send to Back act on individual elements. Native contour
sorting works inside shapes. This tool orders shape groups across glyphs and
matching masters without sorting each master's geometry independently.
Use: Select glyphs and run. Automatic owners, bases of auto composites and
glyphs with locked layers are skipped and listed. Other glyphs still change.
Layers with different component bases or contour node counts are listed and
kept. Mask and service layers are never notified. Capture includes selected
or active glyph slots. Each glyph has its own scan budget.
Benefit: Apply one shape permutation consistently across matching layers.
Each changing action is recorded as one Undo step, followed by an order check.

Independent behaviour rewrite after Alex Slobzheninov,
Glyphs-Scripts/Glyphs/Reorder Shapes.py, Apache-2.0.
Repository: https://github.com/slobzheninov/Glyphs-Scripts . No code copied.

Run **Masters > Reorder Shapes** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source identity

SHA256: `d1fba58063b9941abc1c73bd775fa0ca3156e2070023cdc878436e9f2c3680fa`

[Python source at `c2b34988556c`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/c2b34988556c9214a67f800f68565b7a32df832a/Scripts/Masters/Reorder%20Shapes.py)
