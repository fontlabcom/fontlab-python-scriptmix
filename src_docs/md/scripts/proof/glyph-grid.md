---
this_file: src_docs/md/scripts/proof/glyph-grid.md
tags: ["Proof"]
categories: ["Proof"]
---

# Glyph Grid

Show the selected glyphs on every master side by side, drawn from their outlines.

What it does:
    Rows are glyphs, columns are masters; all cells share one scale so weights
    and widths compare directly. The slider zooms. Composites are drawn with
    their components in place. Nothing in the font changes.

How it works:
    Read selected glyph layers and build a grid with glyphs as rows and
    masters as columns. Fit outlines and advance labels at one common scale.

Why this design:
    A shared scale keeps width and weight differences visible rather than
    fitting each glyph independently.

How to use:
    Select glyphs and run Proof > Glyph Grid. Adjust the zoom slider and
    inspect each master column. Use Reload selection after choosing another
    set in the Font window.

Benefit:
    Compare master drawings directly without exporting fonts or altering the
    current outlines.

Run **Proof > Glyph Grid** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/f375682e88239a3165bd4f24efdbe9c3d331759f6353cd9dbe537cec5f8d892c.py)
<!--/codeinclude-->
