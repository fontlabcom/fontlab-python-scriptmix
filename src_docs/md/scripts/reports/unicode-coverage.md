---
this_file: src_docs/md/scripts/reports/unicode-coverage.md
tags: ["Reports"]
categories: ["Reports"]
---

# Unicode Coverage

Unicode coverage of the current font, block by block, with progress bars.

What it does:
    For every Unicode block that the font touches, shows how many of the
    block's assigned characters (per Python's unicodedata) have a glyph.
    Double-click a block to select its glyphs in the Font window. Block ranges
    are embedded (planes 0 and 1). Nothing in the font changes.

How it works:
    Collect all font encodings and compare them with embedded Unicode block
    ranges. Count assigned characters with Python's Unicode data and report
    codes outside those ranges.

Why this design:
    Block percentages depend on the assigned-character denominator; displaying
    counts avoids implying complete Unicode support from a progress bar alone.

How to use:
    Run Reports > Unicode Coverage. Inspect covered and assigned counts,
    change the block visibility option and double-click a block to select its
    encoded glyphs.

Benefit:
    Review the reported Unicode-block coverage without assigning code points
    or changing export flags.

Run **Reports > Unicode Coverage** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/c7fd8e16a0a6e6d6185228fe14b28e76efe9072932ab87637c7c0fef92fd107d.py)
<!--/codeinclude-->
