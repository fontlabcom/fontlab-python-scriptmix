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

## Source identity

SHA256: `dbbd09a48862c959febd88a34868d22c1037f2e3b7c5cfa24879be6ead6590fa`

[Python source at `8852124d9fe2`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/8852124d9fe2b69cf663e1c6db8d6db4bf5e8454/Scripts/Components/Report.py)
