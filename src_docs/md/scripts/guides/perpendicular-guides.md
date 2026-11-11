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

## Source identity

SHA256: `a221b9b7a01f96d394a878982d88f590775adf5bdd5836b7c26796461306cbee`

[Python source at `370bf9829bc1`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/370bf9829bc141c1c9f88be0018cbc285b502a5d/Scripts/Guides/Perpendicular%20Guides.py)
