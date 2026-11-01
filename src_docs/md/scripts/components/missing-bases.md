---
this_file: src_docs/md/scripts/components/missing-bases.md
tags: ["Components"]
categories: ["Components"]
---

# Missing Bases

Find components that point to glyphs which do not exist, or to a base glyph without that master.

What it does:
    Such components draw nothing and break exports. The tree groups the problems by
    the missing base glyph; expand a group to see the composites and masters affected.
    Select affected glyphs puts them in the Font window selection. Nothing is changed.

How it works:
    Read component references through App and group missing glyphs or missing
    master layers by base name. Retain the affected owners for guarded
    selection.

Why this design:
    A missing base can make several composite drawings disappear, so grouping
    by base helps expose the common cause.

How to use:
    Run Components > Missing Bases. Expand a missing-base group, inspect the
    composite and master entries and use Select affected glyphs to locate the
    owners.

Benefit:
    Locate broken component dependencies without adding placeholder bases or
    changing references.

Run **Components > Missing Bases** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/724e76eb0b9ad97ab16bd7bf35e6686770d69c19e7fc02c7d51b7d3215bf5e11.py)
<!--/codeinclude-->
