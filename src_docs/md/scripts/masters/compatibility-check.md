---
this_file: src_docs/md/scripts/masters/compatibility-check.md
tags: ["Masters"]
categories: ["Masters"]
---

# Compatibility Check

Check that every master of each glyph can interpolate: same contours, nodes, anchors, components.

The tree lists each glyph with ✓ or ✗; expand it to see the counts per master, with the values
that differ from the other masters highlighted. Contour structure is compared node by node
(on-curve / handle pattern), anchors by name and components by base glyph. Select the failing
glyphs in the Font window with one click. Read-only.

Run **Masters > Compatibility Check** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/153b663e08561d54cf5d1de999553832a4ea15dab50c878157abcc73be3666b3.py)
<!--/codeinclude-->
