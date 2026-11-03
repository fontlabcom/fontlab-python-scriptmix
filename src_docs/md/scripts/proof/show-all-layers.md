---
this_file: src_docs/md/scripts/proof/show-all-layers.md
tags: ["Proof"]
categories: ["Proof"]
---

# Show All Layers

Open every foreground layer of each selected glyph occurrence in a new proof.

Keep selected occurrence order, repeated parents, stored layer order, mixed
masters/auxiliaries and a trailing newline for each parent. Empty selection opens
no tab. Exact layer names are used, without Unicode/slash-text substitution.
Masks/service records are backgrounds.

How to use: activate the Font window, select one or more glyphs, then run this
command. The new proof lists each parent's layers in stored order, so a repeated
selection stays repeated and compatible masters can be compared side by side.
Nothing in the font is edited, and no existing proof tab is replaced or reused.
Requires Fly and App 0.2.26.dev325.

Run **Proof > Show All Layers** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/e5d7c25c3e58187afbc19cac2c0da91d0d905b5b981b9adc7b1626ce2c2fe9ff.py)
<!--/codeinclude-->
