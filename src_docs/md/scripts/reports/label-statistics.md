---
this_file: src_docs/md/scripts/reports/label-statistics.md
tags: ["Reports"]
categories: ["Reports"]
---

# Label Statistics

Count glyphs by mark colour and by name suffix (.sc, .ss01, .loclPLK…); click a row to select them.

What it does:
    Two lists side by side give a quick census of a big font's working labels
    and alternate sets. Clicking a row selects those glyphs in the Font window
    (hold Add to extend the selection). Nothing in the font changes.

How it works:
    Group font glyphs by mark value and complete name suffix. Sort each group
    list by count and retain the names behind each row for explicit selection.

Why this design:
    Counts expose the size of alternate sets and marked work batches without
    altering their labels.

How to use:
    Run Reports > Label Statistics. Compare the mark and suffix lists. Click a
    group to select its glyphs; enable Add when the current selection must be
    kept.

Benefit:
    Locate a labelled work set quickly while preserving mark values and glyph
    names.

Run **Reports > Label Statistics** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/0513a3a15aaa68664e35ca8d192411ce769c965b40b2c3aa7a41d6342e71effb.py)
<!--/codeinclude-->
