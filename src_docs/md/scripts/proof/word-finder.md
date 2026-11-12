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

## Source identity

SHA256: `a11d2f2b6283f5bd560b0cf852f098ec44599b7a78494d7cdeb125cfd1d1b70d`

[Python source at `b52710a04ed5`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/b52710a04ed5e9e3759b7086daeb0b09ec65b6f3/Scripts/Proof/Word%20Finder.py)
