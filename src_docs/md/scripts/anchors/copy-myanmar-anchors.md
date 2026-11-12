---
this_file: src_docs/md/scripts/anchors/copy-myanmar-anchors.md
tags: ["Anchors"]
categories: ["Anchors"]
---

# Copy Myanmar Anchors

Copy Myanmar bowl anchors with Unicode routing across named masters.

What: Copy U+101D anchors to single-bowl letters and U+1000 anchors to
double-bowl letters. Unencoded alternates stay unchanged.
How: Capture Unicode routing once per scan. Match source and target layers
by master name. Cache each source layer once per plan. Give each layer its
own time budget; doubtful source layers become note rows. Existing target
pins keep their style. Automatic layers are kept.
Why: Copy Anchors From Glyph can perform the copies in two manual passes;
this tool supplies the Myanmar Unicode routing preset for both passes.
Use: Open a Myanmar font, inspect the whole-font preview, then click Copy.
Benefit: Set consistent starter anchors across both bowl families. Each
application is recorded as one Undo step.

Source: Simon Cozens, https://github.com/simoncozens/GlyphsScripts,
MIT, copyright 2017 Simon Cozens. Independent behaviour rewrite; no source
code was copied.

Run **Anchors > Copy Myanmar Anchors** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source identity

SHA256: `4717fdb08d2ba0cb3cce706775150bf6b9dca17676a7fe6e2561b564dd321c52`

[Python source at `b52710a04ed5`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/b52710a04ed5e9e3759b7086daeb0b09ec65b6f3/Scripts/Anchors/Copy%20Myanmar%20Anchors.py)
