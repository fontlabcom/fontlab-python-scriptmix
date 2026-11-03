---
this_file: src_docs/md/scripts/contours/select-partial-contours.md
tags: ["Contours"]
categories: ["Contours"]
---

# Select Partial Contours

Fill stored-order spans between originally selected nodes in the first layer.

What it does:
    Each selected node toggles the fill state. State carries across contour bounds;
    the command never wraps around to the first node or chooses a shortest arc.
    Controls count as nodes. Components, other non-node selections and other layers
    stay unchanged. No geometry or Undo step is created.

    Adapted independently from Pedro Arilla's Paths/Select partial path.py
    (2018–2022). See NOTICE and additional-tools.json for exact hashes and Apache
    terms. Requires fontlab-fly and App 1.2.0.

How it works:
    Delegate the stored-order toggle-fill algorithm to App. Capture original
    node selection, carry fill state across contours and leave component
    selections outside the pass.

Why this design:
    A deterministic stored-order span differs from shortest-arc selection;
    keeping that rule explicit prevents a surprising wraparound choice.

How to use:
    Open a glyph, select the boundary nodes and run Contours > Select Partial
    Contours. Inspect the resulting spans before applying a separate edit to
    that selection.

Benefit:
    Select repeatable node spans across contours while leaving geometry and
    all other layers unchanged.

Run **Contours > Select Partial Contours** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/6ade10ea8229d5fa4db3947f8ba4eee84cd29043800d2f9c603f7d6cdb6317ac.py)
<!--/codeinclude-->
