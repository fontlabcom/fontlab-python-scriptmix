---
this_file: src_docs/md/scripts/contours/round-coordinates.md
tags: ["Contours"]
categories: ["Contours"]
---

# Round Coordinates

Launch the preserved Round Coordinates sample.

Purpose: The preserved sample describes this task:
Round node coordinates of the selected glyphs to a grid, optionally anchors
and component offsets.

Setup: Use FontLab 9 with Python 3.11, fontlab-fly and fontlab-fontlabapp.
Keep Scripts and rescued together in this repository layout. Read the source
below for its controls, selection requirements and any resource dependencies.
Open a disposable copy of a font; select the glyphs needed by the sample.

Use: Run Contours > Round Coordinates in the Scripts menu.
Review its preview and controls before applying any font changes.

Result: This launcher asks App to run the exact preserved sample. Its native
compatibility is pending; a window or successful dispatch alone does not prove
correct edits, Undo, saved output or cleanup. Check those results separately.
Source: rescued/samples/outlines_round_coordinates.py

Run **Contours > Round Coordinates** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/d6f83efa7bef1bb7f4fb48c93b6dd85b4e554bc0f3538c8991fca9929249ddd8.py)
<!--/codeinclude-->
