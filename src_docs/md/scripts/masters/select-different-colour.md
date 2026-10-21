---
this_file: src_docs/md/scripts/masters/select-different-colour.md
tags: ["Masters"]
categories: ["Masters"]
---

# Select Different Colour

Add to the Font window selection all glyphs of a different mark colour.

What it does:
    Read the mark colours of the selected glyphs. Then select, in addition,
    every glyph whose mark colour is none of those colours. Unmarked glyphs
    count as one colour of their own.

How it works:
    The script reads the Font window selection, collects the mark values of
    the selected glyphs, and selects all other glyphs whose mark is not in that
    set. The old selection stays. It changes only the selection, never a glyph.

Why this design:
    - Pairs with "Select by Mark". That script picks colours from a list. This
      one derives the colours from the current selection: select a few glyphs
      of the colour to keep, run the script, then delete or move the rest.
    - It uses the shared selection helper, which refuses to write the selection
      while a Glyph window is active (FontLab bug fl#8528).
    - Difference to the Glyphs original: it works on all glyphs of the font. The
      Font window filter of FontLab is not readable from a script.

How to use:
    Open the Font window. Select glyphs of the colour(s) to keep apart. Run the
    script. Press Backspace or drag the selection as you need.

Benefit:
    Split a font by colour labels in two clicks.

Credit:
    Behaviour after Pedro Arilla's Glyphs script "Select different colour"
    (Apache-2.0), which is based on "Select Different Color" by Rainer Erich
    Scheichelbauer (mekkablue, Apache-2.0). Independent rewrite. No source code
    was copied.

Run **Masters > Select Different Colour** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/0985dea99226a35e07d67b814e8819e6d0695d2acfdac62b8a57bfc69848f22d.py)
<!--/codeinclude-->
