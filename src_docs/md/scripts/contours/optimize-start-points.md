---
this_file: src_docs/md/scripts/contours/optimize-start-points.md
tags: ["Contours"]
categories: ["Contours"]
---

# Optimize Start Points

Launch the preserved Optimize Start Points sample.

Purpose: The preserved sample describes this task:
Move every contour's start node to its bottom-left on-curve node,
consistently across masters.

Setup: Use FontLab 9 with Python 3.11, fontlab-fly and fontlab-fontlabapp.
Keep Scripts and rescued together in this repository layout. Read the source
below for its controls, selection requirements and any resource dependencies.
Open a disposable copy of a font; select the glyphs needed by the sample.

Use: Run Contours > Optimize Start Points in the Scripts menu.
Review its preview and controls before applying any font changes.

Result: This launcher asks App to run the exact preserved sample. Its native
compatibility is pending; a window or successful dispatch alone does not prove
correct edits, Undo, saved output or cleanup. Check those results separately.
Source: rescued/samples/outlines_optimize_start_points.py

Run **Contours > Optimize Start Points** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/d5da6504b0e3f855c151c2e689c1c9fd6a860746c4dabd823e741c008a1bdce5.py)
<!--/codeinclude-->
