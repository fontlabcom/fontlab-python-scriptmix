---
this_file: src_docs/md/scripts/anchors/auto-cursive-attachment-get-sample.md
tags: ["Anchors"]
categories: ["Anchors"]
---

# Auto Cursive Attachment Get Sample

Save a reusable cursive attachment sample from the current FontLab layer.

What: Measure existing entry/exit pins for the right-to-left fitting tool.
How: In one selected body layer, measure mean ink distances and polygon-edge
tangent estimates around entry/exit pins. Save the master name and profile
to a new JSON file. Use nonzero winding on closed decomposed outlines.
The font is read only; existing files stay unchanged.
Why: A file survives closing the panel or FontLab and can be reused in
another font with the same master name.
Use: Select one layer with entry or exit inside ink, run the script, and
choose a new file name. The save chooser starts in the home folder.
Benefit: Reuse one attachment standard with Auto Cursive Attachment Add Anchors.

Source: Simon Cozens, https://github.com/simoncozens/GlyphsScripts,
MIT, copyright 2017 Simon Cozens. Independent behaviour rewrite; no source
code was copied.

Run **Anchors > Auto Cursive Attachment Get Sample** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/86c619e27f831522020b10fbfc9f69b9678c479da590b7966852908e4b09e87f.py)
<!--/codeinclude-->
