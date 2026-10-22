---
this_file: src_docs/md/scripts/names/character-info.md
tags: ["Names"]
categories: ["Names"]
---

# Character Info

A live panel describing the character of the glyph selected in the Font window.

What it does:
    Shows the outline next to the system font's rendering, the code point, the
    Unicode name and category (Python's unicodedata), case counterpart,
    decomposition and the UTF-8/UTF-16 encodings. It follows the selection
    twice a second; nothing in the font changes.

How it works:
    Describe the selected glyph's encoded character with Python Unicode data.
    Draw its current outline beside a system-font character and refresh from
    the live selection.

Why this design:
    The separate renderings distinguish character identity from the font's own
    drawing without treating the system glyph as a design target.

How to use:
    Run Names > Character Info. Select an encoded glyph in the Font window,
    inspect its code point and encodings and use Copy to copy the current
    character.

Benefit:
    Check Unicode identity, case and decomposition while leaving the glyph's
    encoding unchanged.

Run **Names > Character Info** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/f67cd3c497172096bd984473ff0fbac230b2ff8724758e1597ae74d421699892.py)
<!--/codeinclude-->
