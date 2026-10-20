---
this_file: src_docs/md/scripts/masters/copy-outline-to-mask.md
tags: ["Masters"]
categories: ["Masters"]
---

# Copy Outline To Mask

Launch the preserved Copy Outline To Mask sample.

Purpose: The preserved sample describes this task:
Copy the outline of each selected glyph's master layer into its mask layer,
for reference.

Setup: Use FontLab 9 with Python 3.11, fontlab-fly and fontlab-fontlabapp.
Keep Scripts and rescued together in this repository layout. Read the source
below for its controls, selection requirements and any resource dependencies.
Open a disposable copy of a font; select the glyphs needed by the sample.

Use: Run Masters > Copy Outline To Mask in the Scripts menu.
Review its preview and controls before applying any font changes.

Result: This launcher asks App to run the exact preserved sample. Its native
compatibility is pending; a window or successful dispatch alone does not prove
correct edits, Undo, saved output or cleanup. Check those results separately.
Source: rescued/samples/masters_copy_to_mask.py

Run **Masters > Copy Outline To Mask** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/ba6ab2bdf5bcd504212ab1daa3f383e5d6b79fa5766671bdc8457af6ef0d951a.py)
<!--/codeinclude-->
