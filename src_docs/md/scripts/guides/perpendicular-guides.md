---
this_file: src_docs/md/scripts/guides/perpendicular-guides.md
tags: ["Guides"]
categories: ["Guides"]
---

# Perpendicular Guides

Add a perpendicular guide through selected nodes and centre guides to components.

What it does:
    Use the first selected layer, retaining stored node order and both independent
    branches. Existing guides remain. One Undo step; unsafe automatic dependants and
    pending native updates are refused.

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
[Python source](../../../../.build/menu-sources/376afe9e1b6d5d6b507c2d3161d6205e9f7ca06cf185d569ea91324ade366fb5.py)
<!--/codeinclude-->
