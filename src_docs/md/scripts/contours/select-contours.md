---
this_file: src_docs/md/scripts/contours/select-contours.md
tags: ["Contours"]
categories: ["Contours"]
---

# Select Contours

Select each own contour with any selected node in the first selected layer.

What it does:
    Select a node or control handle, then run this command. All nodes in its contour
    become selected. Existing components and other non-node selections stay intact.
    Other selected layers stay unchanged. No geometry or Undo step is created.

    Adapted independently from Pedro Arilla's Paths/Select paths.py (2018–2022).
    See NOTICE and additional-tools.json for exact source hashes and Apache terms.
    Requires fontlab-fly and App 0.2.26.dev159.

How it works:
    Delegate contour expansion to App. Capture original node selection on the
    first selected layer and select all nodes of each touched own contour.

Why this design:
    A handle is a node too, so touching a control can identify the same whole
    contour without requiring an on-curve selection.

How to use:
    Open a glyph, select a node or control and run Contours > Select Contours.
    Inspect the expanded selection before a separate contour operation.

Benefit:
    Expand node selection to complete contours while keeping geometry,
    components and other layers unchanged.

Run **Contours > Select Contours** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/bd1b0643dbb4754812638c0e87d0f7d8e9c74f3278cd170a8ebc5212aae3af4c.py)
<!--/codeinclude-->
