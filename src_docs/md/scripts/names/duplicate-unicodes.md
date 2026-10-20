---
this_file: src_docs/md/scripts/names/duplicate-unicodes.md
tags: ["Names"]
categories: ["Names"]
---

# Duplicate Unicodes

Launch the preserved Duplicate Unicodes sample.

Purpose: The preserved sample describes this task:
Find code points assigned to more than one glyph and remove them from the
extra glyphs.

Setup: Use FontLab 9 with Python 3.11, fontlab-fly and fontlab-fontlabapp.
Keep Scripts and rescued together in this repository layout. Read the source
below for its controls, selection requirements and any resource dependencies.
Open a disposable copy of a font; select the glyphs needed by the sample.

Use: Run Names > Duplicate Unicodes in the Scripts menu.
Review its preview and controls before applying any font changes.

Result: This launcher asks App to run the exact preserved sample. Its native
compatibility is pending; a window or successful dispatch alone does not prove
correct edits, Undo, saved output or cleanup. Check those results separately.
Source: rescued/samples/names_duplicate_unicodes.py

Run **Names > Duplicate Unicodes** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/87bbc910cf2a24c3b191e08bf9ca5130cb00dd704c5359bac1ce451d84308f2f.py)
<!--/codeinclude-->
