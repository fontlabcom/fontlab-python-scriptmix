---
this_file: src_docs/md/scripts/masters/interpolation-preview.md
tags: ["Masters"]
categories: ["Masters"]
---

# Interpolation Preview

Preview a glyph between two masters with a slider, from the masters' own nodes.

Pick two masters and drag the slider: the painter blends every node linearly (0 % = first
master, 100 % = second) and draws the result over faint outlines of both masters. Incompatible
layers (different contour or node structure) are reported instead of drawn. Read-only.

Run **Masters > Interpolation Preview** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/5dd93fe326c901cd7588cb9cf3d5a4f197ed0ffcae8d162efca767299f87d7cf.py)
<!--/codeinclude-->
