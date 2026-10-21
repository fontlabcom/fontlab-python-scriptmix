---
this_file: src_docs/md/scripts/names/duplicate-unicodes.md
tags: ["Names"]
categories: ["Names"]
---

# Duplicate Unicodes

Find shared Unicode assignments across the whole current font and remove chosen pairs.

Expanded codepoint groups preserve font order and prefer the first primary owner
as keeper. Untick any row to keep its code, or tick the keeper too. Rescan resets
the preview; Remove ticked writes only the checked assignments and refreshes.
Requires Fly and App0.2.121.dev0. No glyph geometry or selection is edited.

Close all Glyph editors and activate the Font window before applying. Changed sources, pending native glyph
updates, automatic targets/dependants or surviving repeated-code lists that the
native setter would collapse refuse before history. One final history batch is
used; a partial failure diagnoses Edit > Undo. Full native history/font/reopen
preservation remains unqualified; no UpdateAll or fgGlyph conversion is used.

Run **Names > Duplicate Unicodes** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/f3cc72fd0ef9c96f20827b81a39de686584c7af0749bc5d6fefc5f24427af0a4.py)
<!--/codeinclude-->
