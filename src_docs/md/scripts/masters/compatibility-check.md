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

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/4c603134d62833b57706d2a6e7fb2ec0bf91240447d9b9b11b34666bff2a1c30.py)
<!--/codeinclude-->
