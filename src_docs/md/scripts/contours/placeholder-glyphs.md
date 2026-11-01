---
this_file: src_docs/md/scripts/contours/placeholder-glyphs.md
tags: ["Contours"]
categories: ["Contours"]
---

# Placeholder Glyphs

Create empty placeholder glyphs from typed glyph names or characters, on every
master.

What it does:
    Type or paste glyph names and characters, separated by spaces, commas or
    new lines. The script creates one empty glyph per entry, with a layer on
    every master and the chosen advance width. A single non-ASCII character
    becomes
    uniXXXX (or uXXXXX) and gets that code point. A name of that form also
    gets its code point, unless another glyph has it already. ASCII tokens
    are glyph names: A stays A; & and 1 are invalid names.

How it works:
    A small non-modal panel shows a live table: the name, the code point and
    what will happen. Existing glyphs, repeated entries and invalid names
    are listed and skipped. Create checks the font again. FontLab's own Add
    Glyph command makes each new glyph with a layer on every master, the
    advance width and the code point (shared module fly.ap.glyph_creation).
    After the write the script reads every new glyph back, and checks that
    no automatic glyph of the font changed.

Why this design:
    - Placeholders let you build features, classes, kerning groups and test
      strings before the drawings exist. Unlike Font > Add Glyphs, the panel
      takes characters directly, previews every name and code point, and
      skips what exists instead of asking.
    - An existing glyph is never overwritten, and a code point that another
      glyph has is never assigned twice.
    - FontLab's text conversion can change some characters, so the script
      refuses text with NUL, no-break space or the Unicode line and paragraph
      separators instead of creating changed names.
    - A code point write needs an active Font window and no open Glyph
      window, as every Unicode writer of this menu does. Create discloses
      queued ids and their possible date changes. The script does not
      call UpdateAll (fl#8537).
    - FontLab can rebuild an automatic glyph when a new name appears. When
      the font has automatic glyphs without a recipe whose names share a
      dotted suffix with a new name (a new e.sc and eacute.sc), the row
      shows "may rebuild auto ..." and is skipped unless you tick "Create
      even if FontLab may rebuild these auto glyphs". A change of the text
      clears the tick.
    - Each new glyph is recorded as its own Undo step.

How to use:
    Open a font and activate its Font window. Run the script. Type the names
    or characters, set the advance width, check the table and press Create.

Benefit:
    A complete glyph set skeleton, named and encoded, in seconds.

Credit:
    Adapted from the author's own FontLab sample, Apache-2.0
    (generate_placeholder_glyphs.py, "Placeholder Glyphs").

Run **Contours > Placeholder Glyphs** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/978c4d39e08f6ea3e597adcec4c942ac145ba61036167ff79cd99e66a23e708c.py)
<!--/codeinclude-->
