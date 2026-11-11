---
this_file: src_docs/md/scripts/names/glyph-finder.md
tags: ["Names"]
categories: ["Names"]
---

# Glyph Finder

Type to find glyphs by name, character or code point; Enter selects them in the Font window.

What it does:
    Accepts a name fragment (acute), a wildcard pattern (*.ss0?), a character
    (é), or a code point (U+00E9, 0x1E82, uni00E9). The list updates as you
    type; double-click a row to select just that glyph. Nothing in the font
    changes.

How it works:
    Choose a matcher from the query syntax: name fragment, wildcard, literal
    character or code-point form. Filter glyph records and guard explicit
    Font-window selection.

Why this design:
    Several input forms let the user locate an encoded character or a named
    alternate in the same view.

How to use:
    Run Names > Glyph Finder. Enter a query, inspect the result list and press
    Enter to select matches. Double-click a row when only that glyph is
    required.

Benefit:
    Find glyphs by the identifier at hand without renaming or changing their
    Unicode assignments.

Run **Names > Glyph Finder** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source identity

SHA256: `95a772ac6847f4831f937e0d422f5abc05624a3b66a55d64f50e840e70bec856`

[Python source at `3dc87d8a0e3d`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/3dc87d8a0e3dec803dc9255436da39eb19abefb2/Scripts/Names/Glyph%20Finder.py)
