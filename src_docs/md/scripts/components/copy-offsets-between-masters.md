---
this_file: src_docs/md/scripts/components/copy-offsets-between-masters.md
tags: ["Components"]
categories: ["Components"]
---

# Copy Offsets Between Masters

Copy component offsets from one master to other masters of the selected glyphs.

What: Takes the component offsets of the source master and sets them on the
same components in the ticked target masters. The table shows the current
and the new offset of every component that changes.

How: Components are matched by position and base glyph name. A target layer
with other components, or in another order, is listed and kept. With "Scale x
by advance-width ratio", the horizontal offset is multiplied by target width
/ source width and rounded half up, so a mark at 40 % of the width stays at
40 %. The vertical offset is copied as it is. Only the offset changes: scale,
slant and the component itself stay.

Why: Composites often need the same mark placement in every master. Copying
the offsets once is faster and more exact than moving marks by hand.

Use: Select composite glyphs. Run the script. Choose the source master, tick
the targets. Press Copy. Press Reload selection after you change the
selection.

Benefit: Brings the masters of many composites into line in one Undo step.

Safety: Auto layers are listed and never edited. The script refuses the whole
batch, before any history exists, when:

- a glyph has an automatic layer, or is the base of an automatic composite,
  also through other composites (FontLab rebuilds the composite and Undo does
  not restore it);

After the write, the script reads the offsets back and reports any gap.
If FontLab fails part-way, the error says that native changes may remain.
Use Edit > Undo then. The
one-step write, the panel, the automatic-layer rule and the pending-update
check are shared with other scripts (fly.ap.components.writer,
fly.ap.components.panel.model, fly.ap.core.history.glyphs, fly.ap.core.edit_guards); the planner
and the panel controls belong to this script.

Source: the author's own FontLab sample
components_copy_offsets_between_masters.py, Apache-2.0.
Adapted for the current FontLab 9 API.

Run **Components > Copy Offsets Between Masters** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source identity

SHA256: `ce9019d53270c6c8d070be4eb143ea0f5891dec824e07aa22a16eee2f3a56a20`

[Python source at `1e4c2b2dd9bc`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/1e4c2b2dd9bccfd04b38e70ed3dcaaa52242835d/Scripts/Components/Copy%20Offsets%20Between%20Masters.py)
