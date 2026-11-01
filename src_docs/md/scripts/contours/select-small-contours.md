---
this_file: src_docs/md/scripts/contours/select-small-contours.md
tags: ["Contours"]
categories: ["Contours"]
---

# Select Small Contours

Ask for an unsigned area threshold and select smaller first-layer contours.

Enter square font units. Select clears that layer's node and non-node selection,
then selects every node of each own contour strictly below the threshold. Open
contours are closed for measurement only. Negative and zero finite values are
valid; invalid text, nonfinite values and Close leave selection unchanged.

Curves use analytic FontTools area, which can differ from Glyphs' flattening.
Mixed non-node selection currently requires one displayed glyph; unsupported
native selection kinds refuse before writes.
Adapted independently from Pedro Arilla's Paths/Select small paths.py
(2018–2022), Apache-2.0; exact hashes are in NOTICE/additional-tools.json.
Requires fontlab-fly and fontlab-fontlabapp[fontui] 0.2.26.dev159.

Run **Contours > Select Small Contours** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/a0da6134d7e5809512e64a5101d3ef6659759b91c0969dfc9ab0f51707909492.py)
<!--/codeinclude-->
