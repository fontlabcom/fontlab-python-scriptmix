---
this_file: src_docs/md/scripts/names/character-set-compare.md
tags: ["Names"]
categories: ["Names"]
---

# Character Set Compare

Paste a text or a character set and compare it with the font's encoded characters.

What it does:
    Lists characters of the text the font lacks and characters the font has
    that the text does not use, with names from unicodedata. Language presets
    fill in common alphabets. Copy the missing set, or select the extra glyphs
    in the Font window. Nothing in the font changes.

How it works:
    Compare distinct non-whitespace input characters with every encoded font
    character. Show missing and extra sets with Unicode names and code points.

Why this design:
    A character-set comparison answers a repertoire question without confusing
    unencoded alternates with encoded characters.

How to use:
    Run Names > Character Set Compare. Paste text or choose a language preset,
    inspect both lists, then copy missing characters or select extra glyphs as
    required.

Benefit:
    Prepare a character-coverage review while leaving encodings and glyph
    membership intact.

Run **Names > Character Set Compare** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source identity

SHA256: `867a8f2f4151ca3c3c8ba2fe0a5f9b01578b46e61440daa3afb160e41cf816b3`

[Python source at `bf9287c6130a`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/bf9287c6130a3083b3c1047050305dfceecbee2b/Scripts/Names/Character%20Set%20Compare.py)
