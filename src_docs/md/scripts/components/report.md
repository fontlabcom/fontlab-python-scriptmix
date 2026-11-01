---
this_file: src_docs/md/scripts/components/report.md
tags: ["Components"]
categories: ["Components"]
---

# Report

List every composite layer in the font: base and mark names, offsets and auto-layer status.

What it does:
    The table covers the current master or all masters, filters as you type and can
    be copied to the clipboard as CSV for a spreadsheet. Double-click a row to make
    that glyph current in FontLab. Nothing in the font is changed.

How it works:
    Use the App component report to collect composite layers for the current
    or all masters. Filter visible rows and encode those rows as quoted CSV
    text.

Why this design:
    A table shows reference names and placement together, making a composite
    inventory easier to inspect or share.

How to use:
    Run Components > Report. Choose the master scope, type a filter and copy
    CSV if needed. Double-click a row to make its glyph current in FontLab.

Benefit:
    Review component use and offsets without rewriting component references or
    outlines.

Run **Components > Report** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/4978c26f1087bb1960ca5c74333c0915cd2ffa0b7348e7f7f29f0779361acb8f.py)
<!--/codeinclude-->
