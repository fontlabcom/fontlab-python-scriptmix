---
this_file: src_docs/md/scripts/anchors/mark-attachment-preview.md
tags: ["Anchors"]
categories: ["Anchors"]
---

# Mark Attachment Preview

Preview a mark attached to a base glyph by matching anchors (top + _top), side by side for every master.

What it does:
    Pick a base glyph, a mark glyph and an anchor family; the mark is drawn where
    mark positioning would put it: base anchor minus mark anchor. Offsets per master
    are listed under the drawing. Nothing in the font is changed.

How it works:
    Find a shared anchor family between the chosen base and mark. Draw the
    mark at base-anchor minus mark-anchor and list the offset for each master.

Why this design:
    The offset preview exposes missing or inconsistent anchor pairs without
    constructing a composite or compiling mark features.

How to use:
    Run Anchors > Mark Attachment Preview. Choose base, mark and family, then
    inspect every master panel and its offset or missing-anchor message.

Benefit:
    Check anchor-based placement before editing anchors or building a marked
    glyph.

Run **Anchors > Mark Attachment Preview** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source identity

SHA256: `a42f01c194b451765ee990eab8628836e15a350e5f602ee70d875c3ca4228185`

[Python source at `83142fd0a0ef`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/83142fd0a0efad5aec2ed5ca10642beb376d3f0f/Scripts/Anchors/Mark%20Attachment%20Preview.py)
