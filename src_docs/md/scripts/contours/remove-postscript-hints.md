---
this_file: src_docs/md/scripts/contours/remove-postscript-hints.md
tags: ["Contours"]
categories: ["Contours"]
---

# Remove PostScript Hints

Launch the preserved Remove PostScript Hints sample.

Purpose: The preserved sample describes this task:
Remove PostScript stem hints from the selected glyphs, horizontal and/or
vertical, per master.

Setup: Use FontLab 9 with Python 3.11, fontlab-fly and fontlab-fontlabapp.
Keep Scripts and rescued together in this repository layout. Read the source
below for its controls, selection requirements and any resource dependencies.
Open a disposable copy of a font; select the glyphs needed by the sample.

Use: Run Contours > Remove PostScript Hints in the Scripts menu.
Review its preview and controls before applying any font changes.

Result: This launcher asks App to run the exact preserved sample. Its native
compatibility is pending; a window or successful dispatch alone does not prove
correct edits, Undo, saved output or cleanup. Check those results separately.
Source: rescued/samples/hints_remove.py

Run **Contours > Remove PostScript Hints** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/e25480ba80765cf3413da006fbba6aa374ff5659935aa47ac5268971caa2b5aa.py)
<!--/codeinclude-->
