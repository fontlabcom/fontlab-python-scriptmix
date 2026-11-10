---
this_file: src_docs/md/scripts/anchors/optical-center.md
tags: ["Anchors"]
categories: ["Anchors"]
---

# Optical Center

Report optical x and align an existing top anchor on selected master layers.

What: Move one third from the bounds centre toward the horizontal ink median.
How: Flatten the placed layer path once, including components. At at most
512 columns, sum exact filled-span lengths from the flattened rings. Use
nonzero winding; counters require correctly directed contours. Fill closes
open subpaths. Coordinates are absolute and round half up to font units.
Each layer has its own time budget. A refused layer becomes a note row;
other selected layers still run. No top anchor is created when it is missing.
Why: Scanline weights avoid thousands of PythonQt point-containment calls
and give a repeatable estimate based on ink rather than the bounding box.
Use: Select glyphs, inspect the non-modal preview, then click Align Top.
Benefit: Start visual anchor refinement from an ink-weight estimate.
Each application is recorded as one Undo step. This is an optical estimate.

Source: Simon Cozens, https://github.com/simoncozens/GlyphsScripts,
MIT, copyright 2017 Simon Cozens. Independent behaviour rewrite; no source
code was copied.

Run **Anchors > Optical Center** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source identity

SHA256: `1ce8cd70f9c46a3e7d9f2a76de026fb6eb616ee6e8af63857577e2ae5ed9fd3f`

[Python source at `83142fd0a0ef`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/83142fd0a0efad5aec2ed5ca10642beb376d3f0f/Scripts/Anchors/Optical%20Center.py)
