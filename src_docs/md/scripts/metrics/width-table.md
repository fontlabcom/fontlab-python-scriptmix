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

## Source identity

SHA256: `90161123b9eba41209b1ca1336371d7c23af2e69bae764d8dff59ffe08bd4458`

[Python source at `83142fd0a0ef`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/83142fd0a0efad5aec2ed5ca10642beb376d3f0f/Scripts/Metrics/Width%20Table.py)
