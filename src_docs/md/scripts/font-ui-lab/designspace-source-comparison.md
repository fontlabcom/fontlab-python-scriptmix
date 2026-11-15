---
this_file: src_docs/md/scripts/font-ui-lab/designspace-source-comparison.md
tags: ["Font UI Lab"]
categories: ["Font UI Lab"]
---

# Designspace Source Comparison

Compare two stored source layers of the current font.

Choose reference/comparison layers and a glyph to inspect advance widths and
structural compatibility. Refresh repeats the read of the captured font, without
switching masters. Missing glyphs and closed fonts are shown as errors.

When supplied by the installed App, Open designspace reads an external
.designspace and its UFO sources read-only. It compares source metrics, widths,
glyph sets and structural compatibility; it does not interpolate outlines.
Cancel, read failure or window closure preserves the prior report. Cancellation
checks are cooperative and cannot interrupt blocking file reads. Owned UFO
handles are released; the borrowed FontLab font is never edited, saved or closed.

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

SHA256: `f11d9b93031d4ed92a9caa6a1e7002fdaa5b28e0ea4ea23fb0ffd44d4f7dbace`

This source is not committed at `3bf7b47dd22f`; no immutable link is offered.
