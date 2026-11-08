---
this_file: src_docs/md/scripts/guides/metric-reference-lines.md
tags: ["Guides"]
categories: ["Guides"]
---

# Metric Reference Lines

Add named glyph guides at the selected metric levels of each master.

What it does:
    Select glyphs, choose current or all masters and inspect the complete preview.
    Existing matching guides and automatic layers are kept. Apply uses one named Undo
    step. Unsafe automatic dependants are refused before history. Close releases all
    owned signals and preview paths. No font-wide guides or outlines are changed.

How it works:
    Read the selected metric levels on each chosen master and create named
    glyph-guide records, including the requested offset. Keep matching guides
    and automatic layers.

Why this design:
    Master-specific reference lines follow each master's own metrics rather
    than copying one master's positions to all layers.

How to use:
    Select glyphs and run Guides > Metric Reference Lines. Choose scope,
    levels and offset, inspect the preview and press Apply for the displayed
    additions.

Benefit:
    Add metric construction lines without changing font-wide guides, metrics
    or outlines.

Run **Guides > Metric Reference Lines** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source identity

SHA256: `288c80a3f2e60341f73130f63fcb4ad68f6f9917b88ed9b6f1b17326f25071bb`

[Python source at `1fddaa75b7e6`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/1fddaa75b7e644ddcb3764909f3dd231cc78528e/Scripts/Guides/Metric%20Reference%20Lines.py)
