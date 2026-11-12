---
this_file: src_docs/md/scripts/font-ui-lab/kerning-proof-workbench.md
tags: ["Font UI Lab"]
categories: ["Font UI Lab"]
---

# Kerning Proof Workbench

Inspect explicit kerning and group fallback beside a linked glyph proof.

Use: Open a font and launch this window. Select a stored pair or type the left
and right glyph/group names. Apply writes the value; Delete removes the explicit
pair and reveals any group fallback. Zero is an explicit value. Reload rereads
the same font; the sequence also accepts independent slash-prefixed glyph names.
Group proofs use the first group member. Toggle proof kerning to compare spacing.

Safety: Apply and Delete change kerning in the font captured at launch. Switching
the active font does not retarget the window. Native edits follow the captured
font's current master and refuse unsupported fractional history. Use an owned
test font. Closing this window does not save or close the borrowed font. Missing
or stale fonts refuse editing; native Undo/Redo and saved-font qualification
remain separate from ordinary source tests.

Run **Font UI Lab > Kerning Proof Workbench** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source identity

SHA256: `1e4c233d5097162af29142ae505877f562900d3969b2f1c6b30c79541559b8f9`

[Python source at `b52710a04ed5`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/b52710a04ed5e9e3759b7086daeb0b09ec65b6f3/Scripts/Font%20UI%20Lab/Kerning%20Proof%20Workbench.py)
