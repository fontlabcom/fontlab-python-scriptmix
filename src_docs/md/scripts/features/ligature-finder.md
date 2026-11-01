---
this_file: src_docs/md/scripts/features/ligature-finder.md
tags: ["Features"]
categories: ["Features"]
---

# Ligature Finder

Find underscore-named glyphs and existing input glyphs. Name-derived recipes do not imply outline components.

What it does:
    Run with a font active. All original controls use the shared fly panel lifecycle.
    Feature data is font-wide; reopen after switching fonts or changing source.

How it works:
    Split underscore names into input recipes and check that every input glyph
    exists and has a safe name. Produce liga text only for usable recipes.

Why this design:
    An underscore name suggests a ligature recipe but does not prove component
    structure or existing shaping behaviour.

How to use:
    Run Features > Ligature Finder. Filter the rows, inspect missing inputs
    and copy the usable rules for review. Add and compile them separately if
    they suit the font.

Benefit:
    Find naming-based ligature candidates without silently adding
    substitutions or modifying outlines.

Run **Features > Ligature Finder** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/076a3a1e83238b473ccb5fdd0902668b9ca5f906e0b8aa2e55d72845856e9b1d.py)
<!--/codeinclude-->
