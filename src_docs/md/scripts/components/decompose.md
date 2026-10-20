---
this_file: src_docs/md/scripts/components/decompose.md
tags: ["Components"]
categories: ["Components"]
---

# Decompose

Launch the preserved Decompose sample.

Purpose: The preserved sample describes this task:
Decompose the components of the selected glyphs into plain outlines, on the
chosen masters.

Setup: Use FontLab 9 with Python 3.11, fontlab-fly and fontlab-fontlabapp.
Keep Scripts and rescued together in this repository layout. Read the source
below for its controls, selection requirements and any resource dependencies.
Open a disposable copy of a font; select the glyphs needed by the sample.

Use: Run Components > Decompose in the Scripts menu.
Review its preview and controls before applying any font changes.

Result: This launcher asks App to run the exact preserved sample. Its native
compatibility is pending; a window or successful dispatch alone does not prove
correct edits, Undo, saved output or cleanup. Check those results separately.
Source: rescued/samples/components_decompose.py

Run **Components > Decompose** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/60cbed7a90bbe37def87144a804e939cc0de92b4cd9cd9baf04d3007cb2e6af1.py)
<!--/codeinclude-->
