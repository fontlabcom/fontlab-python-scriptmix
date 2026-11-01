---
this_file: src_docs/md/scripts/guides/grid-generator.md
tags: ["Guides"]
categories: ["Guides"]
---

# Grid Generator

Preview and add named horizontal, vertical or combined glyph-guide grids.

What it does:
    Select glyphs, choose current or all masters and inspect the complete preview.
    Existing matching guides and automatic layers are kept. Apply uses one named Undo
    step. Unsafe automatic dependants are refused before history. Close releases all
    owned signals and preview paths. No font-wide guides or outlines are changed.

How it works:
    Generate named horizontal, vertical or combined guide records from origin,
    step and count. Compare them with existing guides and add only missing
    records.

Why this design:
    Matching-guide checks let the user extend a construction grid without
    adding duplicate guides at the same records.

How to use:
    Select glyphs and run Guides > Grid Generator. Set scope, direction,
    origin, step and count, inspect the complete preview and press Apply.

Benefit:
    Build consistent glyph-guide grids without changing font-wide guides or
    outlines.

Run **Guides > Grid Generator** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/82cdc78171aaa47dc89c6620cbc5a6be3ada858862725e972e5069dfbcd87192.py)
<!--/codeinclude-->
