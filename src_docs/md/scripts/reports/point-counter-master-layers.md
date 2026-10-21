---
this_file: src_docs/md/scripts/reports/point-counter-master-layers.md
tags: ["Reports"]
categories: ["Reports"]
---

# Point Counter (Master Layers)

Count own paths and nodes in every master layer for each selected occurrence.

Select glyphs in a Font window or layer occurrences in a Glyph window. Each
selected occurrence contributes all its parent's master layers in stored order,
including empty masters and repeated selections. Auxiliary, mask and service
layers are excluded by the native master property. Components are not decomposed.

A normal fixed400×300 Point Counter window shows the complete read-only text.
Select and copy it normally; close and rerun for a fresh snapshot. No font,
selection, history, preferences, clipboard or Output writer is called. Empty
selection or no masters gives the original empty report. Read failures produce
no partial window. Requires App>=0.2.118.dev0 and Fly in FontLab9 Python3.11.

Independently implements Reza Bohloul's Path/Point Counter.py workflow; the
inspected source declares no licence, so its body is not redistributed. Cubic
and line reports preserve original text. Quadratic endpoints are included in
Points/Nodes, explicitly correcting the original omission. Native layer order,
reader preservation and window lifecycle qualification remain pending.

Run **Reports > Point Counter (Master Layers)** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/eb7cae651b7ff4886300f9090d4c1f9e18fba1146a39ebb400b390ce8f2f5334.py)
<!--/codeinclude-->
