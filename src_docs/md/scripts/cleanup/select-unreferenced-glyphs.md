---
this_file: src_docs/md/scripts/cleanup/select-unreferenced-glyphs.md
tags: ["Cleanup"]
categories: ["Cleanup"]
---

# Select Unreferenced Glyphs

List unencoded glyphs that nothing references, and select them in the Font window for review.

What it does:
    A glyph counts as referenced when it has a code point, is used as a component or in an
    auto recipe on any layer, is named in the OpenType feature source, or belongs to a feature
    class that the source uses. Candidates are often alternates waiting for a feature, so the
    script only selects them; it never deletes. Feature files pulled in with include() cannot
    be read and stop the scan.

How it works:
    Use the shared App reference scan for encodings, component use, automatic
    recipes and feature/class references. Refuse unresolved include files
    rather than guessing their contents.

Why this design:
    Unencoded alternates can still be useful, so a candidate list must support
    review rather than automatic deletion.

How to use:
    Run Cleanup > Select Unreferenced Glyphs with a font open. Review all
    listed candidates and press Select in Font window to locate them before
    making any separate deletion decision.

Benefit:
    Identify possible unused glyphs without deleting glyphs or changing their
    references.

Run **Cleanup > Select Unreferenced Glyphs** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/9c10a7d32d4c45efbc015f5d630716cc97bb4c48961948bf391f2e3e13ebdcbe.py)
<!--/codeinclude-->
