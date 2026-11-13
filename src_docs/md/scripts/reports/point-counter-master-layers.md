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
no partial window. Requires App>=1.2.0 and Fly in FontLab9 Python3.11.

Independently implements Reza Bohloul's Path/Point Counter.py workflow; the
inspected source declares no licence, so its body is not redistributed. Cubic
and line reports preserve original text. Quadratic endpoints are included in
Points/Nodes, explicitly correcting the original omission.

Run **Reports > Point Counter (Master Layers)** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source identity

SHA256: `f6ab4dde19f3b42e8b95abb53c933334af0d032766fc263800eefae0155b600c`

[Python source at `3bf7b47dd22f`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/3bf7b47dd22f44334af5f83d5c2becb59ce3874f/Scripts/Reports/Point%20Counter%20%28Master%20Layers%29.py)
