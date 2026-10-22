---
this_file: src_docs/md/scripts/kerning/missing-pairs.md
tags: ["Kerning"]
categories: ["Kerning"]
---

# Missing Pairs

List the combinations of two glyph groups that no kerning pair covers on a master.

What it does:
    Enter left and right glyphs: names separated by spaces, plain characters (“AVT”), or @class
    tokens that stand for all their members. Every left + right combination that neither a glyph
    pair nor a class pair reaches is listed, ready to proof or to kern. "Copy list" puts the
    missing pairs on the clipboard, one "left right" per line. Nothing is edited.

How it works:
    Expand character, glyph-name and class tokens into ordered unique sets.
    Test every left/right combination against explicit glyph and side-
    appropriate class coverage.

Why this design:
    An explicit zero pair still covers a combination; the report must not
    confuse zero adjustment with an absent kerning rule.

How to use:
    Run Kerning > Missing Pairs. Choose a master, enter left and right sets
    and inspect uncovered combinations. Use Copy list to prepare the shown
    pairs for proofing.

Benefit:
    Find uncovered pair combinations without adding kerning values or editing
    class membership.

Run **Kerning > Missing Pairs** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/65fcd76363d99c6af29ca98aea8c33bf37985daa9d9fd749d736cf63b98af0f3.py)
<!--/codeinclude-->
