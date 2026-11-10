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
    Requires fontlab-fly and App 1.2.0.

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

## Source identity

SHA256: `1b201dc96e6633d1314879e43f01e3a1e544afee69bd8686e94e3a53f30f70c4`

[Python source at `1e4c2b2dd9bc`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/1e4c2b2dd9bccfd04b38e70ed3dcaaa52242835d/Scripts/Contours/Select%20Contours.py)
