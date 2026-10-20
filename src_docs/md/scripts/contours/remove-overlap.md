---
this_file: src_docs/md/scripts/contours/remove-overlap.md
tags: ["Contours"]
categories: ["Contours"]
---

# Remove Overlap

Launch the preserved Remove Overlap sample.

Purpose: The preserved sample describes this task:
Remove overlaps on the chosen masters of the selected glyphs, master
compatibility checked first.

Setup: Use FontLab 9 with Python 3.11, fontlab-fly and fontlab-fontlabapp.
Keep Scripts and rescued together in this repository layout. Read the source
below for its controls, selection requirements and any resource dependencies.
Open a disposable copy of a font; select the glyphs needed by the sample.

Use: Run Contours > Remove Overlap in the Scripts menu.
Review its preview and controls before applying any font changes.

Result: This launcher asks App to run the exact preserved sample. Its native
compatibility is pending; a window or successful dispatch alone does not prove
correct edits, Undo, saved output or cleanup. Check those results separately.
Source: rescued/samples/outlines_remove_overlap.py

Run **Contours > Remove Overlap** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/4dcd73c6350c404f62de91a80f83f952ae5809b19fee0a314b7eaa3634d8255b.py)
<!--/codeinclude-->
