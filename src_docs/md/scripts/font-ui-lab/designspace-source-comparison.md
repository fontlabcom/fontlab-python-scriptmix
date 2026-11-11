---
this_file: src_docs/md/scripts/font-ui-lab/designspace-source-comparison.md
tags: ["Font UI Lab"]
categories: ["Font UI Lab"]
---

# Designspace Source Comparison

Compare two stored source layers of the current font.

Choose reference/comparison layers and a glyph to inspect advance widths and
structural compatibility. Refresh repeats the read of the captured font, without
switching masters. Missing glyphs and closed fonts are shown as errors. External
designspace sources and interpolation are not loaded. No edits, save or font
closure occur.

The table uses detached backend reads, so unfinished edits held in another
scripting wrapper are excluded. A missing glyph is reported as missing rather
than assigned a zero advance. Zero and fractional widths remain meaningful.
Compatibility checks ordered contour/node types and anchor/component name sets;
it does not compare coordinates, component transforms, hints or interpolation
results. Matching reports therefore do not certify variable-font export.

The window keeps the font captured when the script starts. Changing the host's
current font does not retarget it. Closing the window disconnects its owned
callbacks and releases its widgets without closing the borrowed document.
Native painting, lifecycle and whole-font preservation remain unqualified.

Run **Font UI Lab > Designspace Source Comparison** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source identity

SHA256: `01c2a0f5e87f70ecd7e1fffd9da707fb4afb48b0e7bb2a3f15e911408f6b67b7`

[Python source at `3dc87d8a0e3d`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/3dc87d8a0e3dec803dc9255436da39eb19abefb2/Scripts/Font%20UI%20Lab/Designspace%20Source%20Comparison.py)
