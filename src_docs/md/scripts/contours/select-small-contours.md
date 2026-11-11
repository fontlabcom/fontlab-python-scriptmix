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
Requires fontlab-fly and fontlab-fontlabapp[fontui] 1.2.0.

Run **Contours > Select Small Contours** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source identity

SHA256: `b7ba4a2b039ca9ed0a48940da123493b50648fec6048cd5e88bb58b1d5c2c56c`

[Python source at `bf9287c6130a`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/bf9287c6130a3083b3c1047050305dfceecbee2b/Scripts/Contours/Select%20Small%20Contours.py)
