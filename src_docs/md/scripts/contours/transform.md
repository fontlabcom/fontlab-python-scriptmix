---
this_file: src_docs/md/scripts/contours/transform.md
tags: ["Contours"]
categories: ["Contours"]
---

# Transform

Launch the preserved Transform sample.

Purpose: The preserved sample describes this task:
Scale, skew, rotate and move the outlines of the selected glyphs with a live
preview.

Setup: Use FontLab 9 with Python 3.11, fontlab-fly and fontlab-fontlabapp.
Keep Scripts and rescued together in this repository layout. Read the source
below for its controls, selection requirements and any resource dependencies.
Open a disposable copy of a font; select the glyphs needed by the sample.

Use: Run Contours > Transform in the Scripts menu.
Review its preview and controls before applying any font changes.

Result: This launcher asks App to run the exact preserved sample. Its native
compatibility is pending; a window or successful dispatch alone does not prove
correct edits, Undo, saved output or cleanup. Check those results separately.
Source: rescued/samples/outlines_transform_dialog.py

Run **Contours > Transform** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/e579f1a16847b141e7d53241c4f7b9f0edd78d096612c1d329bef5842754b32b.py)
<!--/codeinclude-->
