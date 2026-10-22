---
this_file: src_docs/md/scripts/proof/word-finder.md
tags: ["Proof"]
categories: ["Proof"]
---

# Word Finder

Find real words to proof with: words the font can set, that use the letters you are working on.

What it does:
    Searches a small embedded English and Latin word list. Keep only words
    whose every letter has a glyph, require some letters (e.g. the new 'k'),
    or restrict to a set of letters (e.g. what is drawn so far). Copy the
    result as proof text. Nothing in the font changes.

How it works:
    Filter the embedded English and Latin word list against the captured
    encoded characters, required letters and any allowed-letter restriction.

Why this design:
    Keeping every letter drawable makes the result usable as proof text for an
    incomplete character repertoire.

How to use:
    Run Proof > Word Finder. Set the required or allowed letters, inspect the
    filtered words and press Copy to copy the displayed list. Reopen after
    changing the font repertoire.

Benefit:
    Build a small proof-text set without creating glyphs or changing the font.

Run **Proof > Word Finder** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/1afa96fd3ebac2b2aad0713ea2e7bc3df34b01ff1d2dda6605876e07a07bfbdb.py)
<!--/codeinclude-->
