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

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/3da6bb5291d560ed5e79341b014ebe503a44ce777aa2c183eecb9e7c6a316cef.py)
<!--/codeinclude-->
