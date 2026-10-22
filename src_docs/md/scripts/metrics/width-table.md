---
this_file: src_docs/md/scripts/metrics/width-table.md
tags: ["Metrics"]
categories: ["Metrics"]
---

# Width Table

Advance widths of the selected glyphs across all masters, sortable, with odd progressions flagged.

What it does:
    In a weight family the widths usually grow (or shrink) steadily from master to master. A glyph
    whose width goes up and then down again is flagged: often a spacing slip. Click a column header
    to sort; "Select flagged" selects those glyphs in the Font window. Nothing is edited.

How it works:
    Read selected glyph advances in master order and classify their
    progression. Show numeric master columns and flag mixed
    increasing/decreasing sequences.

Why this design:
    A mixed progression is a spacing-review candidate, not proof that the
    design is wrong; selection leaves the decision to the user.

How to use:
    Select glyphs and run Metrics > Width Table. Sort columns or restrict the
    view to mixed progressions, then use Select flagged to locate the reported
    glyphs.

Benefit:
    Find unusual master width trends without changing advances or outlines.

Run **Metrics > Width Table** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/e42b807227d1c1d354722bc4cc65df2000f0268ad2d407df2bf36e18d9e46e00.py)
<!--/codeinclude-->
