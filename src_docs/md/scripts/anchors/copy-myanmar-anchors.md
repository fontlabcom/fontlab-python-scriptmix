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

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/cffeff365b3b8e56a736cbddd8997dae4efaba02193fb25803ff96888d7a5f8f.py)
<!--/codeinclude-->
