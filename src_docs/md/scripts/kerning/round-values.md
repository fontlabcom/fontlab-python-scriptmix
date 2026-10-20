---
this_file: src_docs/md/scripts/kerning/round-values.md
tags: ["Kerning"]
categories: ["Kerning"]
---

# Round Values

Round kerning values to a step (5, 10 …) on one or all masters, previewing every change.

Rounded kerning is easier to read, compare and edit by hand, and interpolates to tidier
instances. Halves round away from zero, as FontLab rounds. Pairs that round to 0 can be deleted
instead of being kept as explicit zeros. One Apply is one Undo step for all masters.

Run **Kerning > Round Values** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/9aa3ef344a8bc61bdf1542b4900154e9afc15c0da4ad8c188d784eb0cd68ef5e.py)
<!--/codeinclude-->
