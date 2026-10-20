---
this_file: src_docs/md/scripts/contours/correct-contour-direction.md
tags: ["Contours"]
categories: ["Contours"]
---

# Correct Contour Direction

Launch the preserved Correct Contour Direction sample.

Purpose: The preserved sample describes this task:
Set PostScript contour direction on the selected glyphs and report what
changed per master.

Setup: Use FontLab 9 with Python 3.11, fontlab-fly and fontlab-fontlabapp.
Keep Scripts and rescued together in this repository layout. Read the source
below for its controls, selection requirements and any resource dependencies.
Open a disposable copy of a font; select the glyphs needed by the sample.

Use: Run Contours > Correct Contour Direction in the Scripts menu.
Review its preview and controls before applying any font changes.

Result: This launcher asks App to run the exact preserved sample. Its native
compatibility is pending; a window or successful dispatch alone does not prove
correct edits, Undo, saved output or cleanup. Check those results separately.
Source: rescued/samples/outlines_correct_direction.py

Run **Contours > Correct Contour Direction** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/719b664fb3c2ba9dac2e537ef4a6f5af2e1868293375f4cef39bf32e7d979af6.py)
<!--/codeinclude-->
