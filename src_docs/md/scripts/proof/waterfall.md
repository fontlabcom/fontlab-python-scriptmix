---
this_file: src_docs/md/scripts/proof/waterfall.md
tags: ["Proof"]
categories: ["Proof"]
---

# Waterfall

Render a line of text in a cascade of sizes, drawn straight from the glyph outlines.

What it does:
    Type any text (use /glyphname for unencoded glyphs, e.g. /a.ss01), pick a
    master and edit the list of pixel sizes. Characters the font lacks show as
    red boxes. Advance widths only: kerning is not applied. Nothing in the font
    changes.

How it works:
    Resolve characters and slash-name tokens against the captured font maps.
    Draw the chosen master at the requested pixel sizes and mark missing
    characters visibly.

Why this design:
    Drawing the current outlines avoids generating a test font, while the
    missing boxes prevent unsupported text from disappearing unnoticed.

How to use:
    Run Proof > Waterfall. Enter text, choose a master and edit the size list.
    Scroll through the cascade to compare the drawings at small and large
    sizes.

Benefit:
    Judge the same text at several sizes with advance spacing and no kerning
    or font edits.

Run **Proof > Waterfall** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source identity

SHA256: `a019aec9cf77088904935933c1f6e2aea6ba588248709661c5666af77d32b2a2`

[Python source at `cca80db1b47f`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/cca80db1b47f998bbbf4a26427a1e5949ccf7230/Scripts/Proof/Waterfall.py)
