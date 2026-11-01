---
this_file: src_docs/md/scripts/kerning/kerning-energy-report.md
tags: ["Kerning"]
categories: ["Kerning"]
---

# Kerning Energy Report

Show a read-only kerning energy and spacing-bias report for selected glyphs.

What: Report the sum of squared effective pair values and independent row/column
means on the current master. The report is read-only and changes no font data.
How: Build side-class indexes once, then resolve typed glyph and class pairs.
Explicit zero exceptions win. Ambiguous pairs are named and kept out of totals;
other pairs still contribute. The report retains totals and suggestions rather
than a full square matrix. At most 200 kept-pair details are displayed.
Why: FontLab's Compress to Class Kerning converts pair representation. That
command is unrelated to this spacing-bias diagnostic.
Use: Select glyphs in the Font window and run. Copy the selectable JSON report
for comparison after a spacing pass. Run again for fresh measurements.
Benefit: Find recurring spacing biases before editing sidebearings or kerning.
Energy uses font units squared, without the source's arbitrary scale factor.

Independent behaviour rewrite after Simon Cozens, Kern Optimizer.py, MIT.
Repository: https://github.com/simoncozens/GlyphsScripts . No source code copied.

Run **Kerning > Kerning Energy Report** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/79f1e604077519057e92bb36df12ef8dbf56c2df1f6081c3d46a224dd19c468a.py)
<!--/codeinclude-->
