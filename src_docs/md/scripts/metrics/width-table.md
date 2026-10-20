---
this_file: src_docs/md/scripts/metrics/width-table.md
tags: ["Metrics"]
categories: ["Metrics"]
---

# Width Table

Advance widths of the selected glyphs across all masters, sortable, with odd progressions flagged.

In a weight family the widths usually grow (or shrink) steadily from master to master. A glyph
whose width goes up and then down again is flagged: often a spacing slip. Click a column header
to sort; "Select flagged" selects those glyphs in the Font window. Nothing is edited.

Run **Metrics > Width Table** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/c0f364ff9cfdc644f1f3b1741364b0946979d06034ba6d918c2f91f36b41d4e5.py)
<!--/codeinclude-->
