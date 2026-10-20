---
this_file: src_docs/md/scripts/contours/slant.md
tags: ["Contours"]
categories: ["Contours"]
---

# Slant

Launch the preserved Slant sample.

Purpose: The preserved sample describes this task:
Slant (skew) the selected glyphs by an angle, optionally the font's italic
angle.

Setup: Use FontLab 9 with Python 3.11, fontlab-fly and fontlab-fontlabapp.
Keep Scripts and rescued together in this repository layout. Read the source
below for its controls, selection requirements and any resource dependencies.
Open a disposable copy of a font; select the glyphs needed by the sample.

Use: Run Contours > Slant in the Scripts menu.
Review its preview and controls before applying any font changes.

Result: This launcher asks App to run the exact preserved sample. Its native
compatibility is pending; a window or successful dispatch alone does not prove
correct edits, Undo, saved output or cleanup. Check those results separately.
Source: rescued/samples/outlines_slant.py

Run **Contours > Slant** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/92c066df1d29a0e51c35c4338e40c92d58935509760628c8fd8b19a8fd4f0332.py)
<!--/codeinclude-->
