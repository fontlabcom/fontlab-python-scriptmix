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

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/7dba91b4e447cc7a4d5afff4188c69fece55cac4e8e2e42e4b8712d24f9eebe9.py)
<!--/codeinclude-->
