---
this_file: src_docs/md/scripts/kerning/exceptions-finder.md
tags: ["Kerning"]
categories: ["Kerning"]
---

# Exceptions Finder

Find kerning exceptions: pairs that override a class pair, and remove the ones you tick.

An exception is a pair whose glyph side belongs to a kerning class that already has a pair
with the same partner (A V overriding @A V). Exceptions with the same value as the class pair
are redundant and safe to delete; the others are deliberate overrides worth a second look.
Tick rows (or "Tick redundant") and Remove; one Undo step for all masters.

Run **Kerning > Exceptions Finder** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/adfbdc13fe2f9e09f1a990c67c303a909bd313183d0922a45f82d1918ba7a5e6.py)
<!--/codeinclude-->
