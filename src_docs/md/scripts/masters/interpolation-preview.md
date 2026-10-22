---
this_file: src_docs/md/scripts/masters/interpolation-preview.md
tags: ["Masters"]
categories: ["Masters"]
---

# Interpolation Preview

Preview a glyph between two masters with a slider, from the masters' own nodes.

What it does:
    Pick two masters and drag the slider: the painter blends every node linearly (0 % = first
    master, 100 % = second) and draws the result over faint outlines of both masters. Incompatible
    layers (different contour or node structure) are reported instead of drawn. Read-only.

How it works:
    Use the shared Masters preview to compare contour and node structure
    before blending corresponding node coordinates linearly between two chosen
    masters.

Why this design:
    The tool reports incompatible structures instead of drawing a misleading
    blend from unrelated node positions.

How to use:
    Select a glyph and run Masters > Interpolation Preview. Choose two
    masters, move the percentage slider and compare the blended path with the
    faint source paths.

Benefit:
    Inspect a node-based interpolation proposal without adding instances or
    changing master outlines.

Run **Masters > Interpolation Preview** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/56242263beb02b196e49c4cff235dc8f48afd90aa626801d50ced1fb5c705726.py)
<!--/codeinclude-->
