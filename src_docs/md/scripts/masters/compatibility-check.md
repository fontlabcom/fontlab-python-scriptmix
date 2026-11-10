---
this_file: src_docs/md/scripts/masters/compatibility-check.md
tags: ["Masters"]
categories: ["Masters"]
---

# Compatibility Check

Check that every master of each glyph can interpolate: same contours, nodes, anchors, components.

What it does:
    The tree lists each glyph with ✓ or ✗; expand it to see the counts per master, with the values
    that differ from the other masters highlighted. Contour structure is compared node by node
    (on-curve / handle pattern), anchors by name and components by base glyph. Select the failing
    glyphs in the Font window with one click. Read-only.

How it works:
    Use the shared Masters compatibility checks for corresponding contours and
    node patterns, anchor names and component bases. Display the counts under
    each glyph.

Why this design:
    Matching totals alone do not establish structural compatibility; node
    patterns and named objects need separate checks.

How to use:
    Select glyphs and run Masters > Compatibility Check. Expand failing rows,
    compare their master details and use the action button to select
    incompatible glyphs.

Benefit:
    Locate reported interpolation obstacles without reordering contours or
    changing glyph data.

Run **Masters > Compatibility Check** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source identity

SHA256: `536a54227e6d654684d4eace3494d01cd0f106d2a7df0a7d8ad227633cbaec00`

[Python source at `8e06999ef5a2`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/8e06999ef5a237c79364b4efd0758bf8fbd5dee8/Scripts/Masters/Compatibility%20Check.py)
