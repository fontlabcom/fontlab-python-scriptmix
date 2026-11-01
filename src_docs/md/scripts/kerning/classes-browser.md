---
this_file: src_docs/md/scripts/kerning/classes-browser.md
tags: ["Kerning"]
categories: ["Kerning"]
---

# Classes Browser

Browse kerning classes: their side, members, and every pair that uses them on each master.

What it does:
    The list on the left shows each class with its side (left = first glyph of a pair, right =
    second) and size; filter it by class or member name. Pick a class to see its members and the
    pairs that use it with one value column per master. "Select members" selects the class's glyphs
    in the Font window. Nothing is edited.

How it works:
    Read side-specific kerning classes and their members, then collect
    explicit pairs using the selected class across masters. Filter class names
    or exact member names.

Why this design:
    Class membership and pair use are different questions; showing both avoids
    mistaking an unused class for an active kerning rule.

How to use:
    Run Kerning > Classes Browser. Enter a filter, choose a class and inspect
    its members and pair values. Use Select members to locate its glyphs in
    the Font window.

Benefit:
    Trace kerning-class use without changing membership or pair data.

Run **Kerning > Classes Browser** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/4385bbdde453e94a1ed9a429f9d208bf0b3d504d3780cf3604e03d036b6a550c.py)
<!--/codeinclude-->
