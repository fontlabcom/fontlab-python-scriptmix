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
Requires Fly and App 1.2.0 or later.

Run **Proof > Show All Layers** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source identity

SHA256: `df44a608bff6ec335f6768333b69dc9101237cc727ee3ca7c61e99035012929f`

[Python source at `6b1048c4f1db`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/6b1048c4f1dbc64ebe49d419db9193ccb3d9a9f0/Scripts/Proof/Show%20All%20Layers.py)
