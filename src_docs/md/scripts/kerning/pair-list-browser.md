---
this_file: src_docs/md/scripts/kerning/pair-list-browser.md
tags: ["Kerning"]
categories: ["Kerning"]
---

# Pair List Browser

Browse every kerning pair of a master: filter, sort by any column, export to CSV.

What it does:
    Type in the filter to keep pairs whose left or right side contains the text (glyph or @class
    name); "=" anchors a whole side, so "=T" shows pairs with exactly T on one side. Click a header
    to sort; values sort numerically. Export writes the pairs shown to a CSV file. Read-only.

How it works:
    Read explicit pairs on the chosen master and filter either side by
    substring or exact equals-prefixed name. Export rows in the table's
    displayed order.

Why this design:
    Numeric value sorting and exact-side filtering help isolate a pair set
    without changing its stored values.

How to use:
    Run Kerning > Pair List Browser. Choose a master, enter a filter, sort by
    a header and use Export to save the shown rows as CSV.

Benefit:
    Inspect and share an explicit kerning subset while retaining all glyph and
    class pairs.

Run **Kerning > Pair List Browser** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/93d265b35fe09f9c0daac3603e20280023c6711556b5e03048754cbb3550b523.py)
<!--/codeinclude-->
