---
this_file: src_docs/md/scripts/names/batch-rename.md
tags: ["Names"]
categories: ["Names"]
---

# Batch Rename

Launch the preserved Batch Rename sample.

Purpose: The preserved sample describes this task:
Find and replace in glyph names (plain text or regular expression) with a
live preview.

Setup: Use FontLab 9 with Python 3.11, fontlab-fly and fontlab-fontlabapp.
Keep Scripts and rescued together in this repository layout. Read the source
below for its controls, selection requirements and any resource dependencies.
Open a disposable copy of a font; select the glyphs needed by the sample.

Use: Run Names > Batch Rename in the Scripts menu.
Review its preview and controls before applying any font changes.

Result: This launcher asks App to run the exact preserved sample. Its native
compatibility is pending; a window or successful dispatch alone does not prove
correct edits, Undo, saved output or cleanup. Check those results separately.
Source: rescued/samples/names_batch_rename.py

Run **Names > Batch Rename** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/27a4a12d980802532026dcbde6f3e283193b3433de56c019a5ff33b413cbca65.py)
<!--/codeinclude-->
