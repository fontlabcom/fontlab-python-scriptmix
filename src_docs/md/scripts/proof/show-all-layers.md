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
Masks/service records are backgrounds. Requires Fly and App0.2.110.dev0.
Native selected-slot/role/tab and complete preservation acceptance is pending.

Run **Proof > Show All Layers** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/84ba3d3803ad44623b26ecd60d8fab4a99646297ac8f372d3ee0d94adcbead29.py)
<!--/codeinclude-->
