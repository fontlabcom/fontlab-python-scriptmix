---
this_file: src_docs/md/scripts/names/case-pairs.md
tags: ["Names"]
categories: ["Names"]
---

# Case Pairs

Find the upper- or lowercase counterparts of the selected glyphs and select them.

What it does:
    Counterparts come from Unicode case mapping of each glyph's code point;
    unencoded alternates use their base name (a.ss01 -> A.ss01). Select the
    counterparts alone or together with the originals. Nothing in the font
    changes.

How it works:
    Map Unicode case counterparts to existing glyphs. For unencoded suffixed
    names, try the base counterpart with the original suffix; reject multi-
    character case expansions.

Why this design:
    A Unicode case change is not always one glyph, so missing or expanding
    mappings remain visible rather than guessed.

How to use:
    Select source glyphs and run Names > Case Pairs. Review the mapping rows,
    choose whether originals stay selected and select the available
    counterparts.

Benefit:
    Move between related case glyphs while preserving names, encodings and
    outlines.

Run **Names > Case Pairs** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/9d366e8b87d56e2144fb96d5a1182d10b83107bbfe5a4a6767a7aa26188a5e78.py)
<!--/codeinclude-->
