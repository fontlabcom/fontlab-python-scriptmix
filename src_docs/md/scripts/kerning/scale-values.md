---
this_file: src_docs/md/scripts/kerning/scale-values.md
tags: ["Kerning"]
categories: ["Kerning"]
---

# Scale Values

Scale all kerning values by a percentage on one or all masters.

What it does:
    Loosen a Light master's kerning or tighten a display master's in one go: every pair (glyph and
    class pairs alike) is multiplied and rounded to whole units, halves away from zero. Pairs that
    become 0 can be deleted. The preview lists every change; one Apply is one Undo step.

How it works:
    Plan explicit glyph and class pairs on the selected master scope. Multiply
    by the percentage, round halves away from zero and optionally remove
    resulting zero pairs.

Why this design:
    A complete preview allows a broad spacing adjustment to be checked before
    any kerning values are written.

How to use:
    Run Kerning > Scale Values. Choose percentage, zero-pair policy and
    current or all masters. Review each old/new value, then Apply the
    displayed proposal.

Benefit:
    Change a master's kerning strength in one batch; Apply is recorded as one
    Undo step.

Run **Kerning > Scale Values** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/1e4412bc6d198a63ed2949d678aa073bb847c0c02832ba47fed953b028187e40.py)
<!--/codeinclude-->
