---
this_file: src_docs/md/scripts/contours/delete-small-contours.md
tags: ["Contours"]
categories: ["Contours"]
---

# Delete Small Contours

Launch the preserved Delete Small Contours sample.

Purpose: The preserved sample describes this task:
Remove contours whose area is below a threshold: stray specks left by
drawing or tracing.

Setup: Use FontLab 9 with Python 3.11, fontlab-fly and fontlab-fontlabapp.
Keep Scripts and rescued together in this repository layout. Read the source
below for its controls, selection requirements and any resource dependencies.
Open a disposable copy of a font; select the glyphs needed by the sample.

Use: Run Contours > Delete Small Contours in the Scripts menu.
Review its preview and controls before applying any font changes.

Result: This launcher asks App to run the exact preserved sample. Its native
compatibility is pending; a window or successful dispatch alone does not prove
correct edits, Undo, saved output or cleanup. Check those results separately.
Source: rescued/samples/outlines_delete_small_contours.py

Run **Contours > Delete Small Contours** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/5f62f7a8ae603178fd9850009037b52d4c8b0e13d0cb18e64ee68204cd54bfe0.py)
<!--/codeinclude-->
