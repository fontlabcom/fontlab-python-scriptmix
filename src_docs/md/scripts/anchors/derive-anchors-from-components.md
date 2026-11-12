---
this_file: src_docs/md/scripts/anchors/derive-anchors-from-components.md
tags: ["Anchors"]
categories: ["Anchors"]
---

# Derive Anchors From Components

Recover missing base anchors from positioned mark components.

What: Scan manual composites across named masters and infer base attachments.
How: Transform the first mark per underscored label into base coordinates.
The first mark in component order supplies the label in a stacked accent.
Honour explicit mark-layer references. Base destinations must be master
layers. Keep existing anchors. Ambiguous marks, missing or automatic
references, non-master bases, conflicts and layer timeouts become note rows.
A conflict removes only that base label; clean labels and layers still run.
Capture the glyph catalogue once per scan; give each layer its own budget.
Why: Recover deliberate accent placement without moving components or
rejecting a whole font because some evidence is doubtful.
Use: Open the non-modal preview, inspect edits and notes, then click Derive.
Benefit: Recover anchors for scaled or shifted bases and stacked marks.
Each application is recorded as one Undo step. Unsafe writes are refused.

Source: Simon Cozens, https://github.com/simoncozens/GlyphsScripts,
MIT, copyright 2017 Simon Cozens. Independent behaviour rewrite; no source
code was copied.

Run **Anchors > Derive Anchors From Components** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source identity

SHA256: `e9a37c38870c7e0c2f6f2294791824a582ca6dc3b5a92853919913d7dd41f538`

[Python source at `cca80db1b47f`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/cca80db1b47f998bbbf4a26427a1e5949ccf7230/Scripts/Anchors/Derive%20Anchors%20From%20Components.py)
