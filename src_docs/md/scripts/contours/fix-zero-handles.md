---
this_file: src_docs/md/scripts/contours/fix-zero-handles.md
tags: ["Contours"]
categories: ["Contours"]
---

# Fix Zero Handles

Launch the preserved Fix Zero Handles sample.

Purpose: The preserved sample describes this task:
Find curve handles that sit on their own node and clean them up.

Setup: Use FontLab 9 with Python 3.11, fontlab-fly and fontlab-fontlabapp.
Keep Scripts and rescued together in this repository layout. Read the source
below for its controls, selection requirements and any resource dependencies.
Open a disposable copy of a font; select the glyphs needed by the sample.

Use: Run Contours > Fix Zero Handles in the Scripts menu.
Review its preview and controls before applying any font changes.

Result: This launcher asks App to run the exact preserved sample. Its native
compatibility is pending; a window or successful dispatch alone does not prove
correct edits, Undo, saved output or cleanup. Check those results separately.
Source: rescued/samples/outlines_fix_zero_handles.py

Run **Contours > Fix Zero Handles** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/7f2a334f08f948427a2397b7843b6b33802bdaf8b377e4e84ffa3f5d8bc9f35a.py)
<!--/codeinclude-->
