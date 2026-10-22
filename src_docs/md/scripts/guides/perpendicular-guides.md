---
this_file: src_docs/md/scripts/guides/perpendicular-guides.md
tags: ["Guides"]
categories: ["Guides"]
---

# Perpendicular Guides

Add a perpendicular guide through selected nodes and centre guides to
components.

What it does:
    Use the first selected layer, retaining stored node order and both
    independent
    branches. Existing guides remain. One Undo step; unsafe automatic
    dependants and
    queued ids and their possible date changes are disclosed.

How it works:
    Delegate the two guide branches to App: perpendicular construction from
    selected nodes and centre-guide construction for selected components on
    the first layer.

Why this design:
    Keeping both branches independent preserves mixed node/component selection
    behaviour and leaves existing guides available.

How to use:
    Open a glyph, select the required nodes or components and run Guides >
    Perpendicular Guides. Review any refusal before changing the selection and
    running it again.

Benefit:
    Add construction references through shared history; each successful edit
    is recorded as one Undo step.

Run **Guides > Perpendicular Guides** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/da0a1a606b373ed6a7841d0cd8e1558eb93d1cee6894644a8af71471706c74f1.py)
<!--/codeinclude-->
