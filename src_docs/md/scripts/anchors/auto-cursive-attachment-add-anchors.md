---
this_file: src_docs/md/scripts/anchors/auto-cursive-attachment-add-anchors.md
tags: ["Anchors"]
categories: ["Anchors"]
---

# Auto Cursive Attachment Add Anchors

Fit missing entry and exit anchors to a saved cursive sample.

What: Fit missing connection pins for right-to-left scripts on the current
master. Search exit from the left edge and entry from the right edge.
How: Read a JSON sample from Get Sample. Require matching master names.
Name fragments ini/med request exit; fin/med request entry. Keep existing
pins. Score near-edge ink thickness and polygon-edge tangent estimates;
a perfect zero score is valid. Use nonzero winding on closed decomposed
outlines. Round half up to font units. Report actual text conversions.
Why: A persistent sample gives a reusable attachment standard. Layer
failures become note rows so clean selected glyphs can still run.
Use: Select glyphs, Browse for the sample, inspect the preview, then Add.
Benefit: Place consistent right-to-left cursive connections. Each
application is recorded as one Undo step.

Source: Simon Cozens, https://github.com/simoncozens/GlyphsScripts,
MIT, copyright 2017 Simon Cozens. Independent behaviour rewrite; no source
code was copied.

Run **Anchors > Auto Cursive Attachment Add Anchors** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/0a3ab86637aff4a434d9969a27c4eabbd82ff27e80e4c2347f8f4edf1ff4731e.py)
<!--/codeinclude-->
