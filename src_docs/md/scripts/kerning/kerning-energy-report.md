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

## Source identity

SHA256: `6555393db13425025dee6fcba78101661a6a19c9e08c6319319c2c0edb29a688`

[Python source at `4bab81718f97`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/4bab81718f976cbdb0cf33c249fc85b5df530a9a/Scripts/Kerning/Kerning%20Energy%20Report.py)
