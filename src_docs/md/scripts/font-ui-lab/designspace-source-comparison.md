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

SHA256: `e7e5ec18c414634e0dc352c0faa5ca1d40fa129a6b4fd2668f3858bb94fd6a7c`

[Python source at `3bf7b47dd22f`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/3bf7b47dd22f44334af5f83d5c2becb59ce3874f/Scripts/Font%20UI%20Lab/Designspace%20Source%20Comparison.py)
