---
this_file: src_docs/md/scripts/masters/master-twins.md
tags: ["Masters"]
categories: ["Masters"]
---

# Master Twins

Copy selected kinds of master-layer content across the current font.

What:
    Copy contours, components, anchors and metrics independently between two
    masters. Choose selected glyphs or all glyphs. An empty source clears the
    chosen content in the target. Guides, masks and glyph identity stay put.
How:
    A non-modal panel previews layer pairs. Copy plans again from the live
    font. Shape copies and anchor_writer steps are prepared before history.
    contour_copy restores node names and raw node flags, with selection
    cleared.
    Element names, notes and transforms are copied explicitly. Named contours
    and nodes with an explicit corner_smooth value are kept. Other node and
    contour properties are not detected and not copied. outline_writer records
    the complete action as one Undo step.
Why:
    Component-only copying and whole-font scope complement Copy Layer Between
    Masters. Automatic, locked and shared-data glyphs are kept and listed;
    other glyphs still copy. PostScript or TrueType hints keep a glyph only
    when contours are chosen. transferTTH is not used. Contour copies can
    lose extra node properties (fl#8569).
Use:
    Open a font with at least two masters. Choose From, To and the content
    switches. Check the preview and click Copy. Refresh reads the selection.
    Check master compatibility after copying contours or components.
Benefit:
    Seed a new master, including its components, without replacing other
    kinds of content. Refusals appear before any font write.
Credit:
    Giuseppe Salerno / Resistenza Type, MasterTwins.py,
    https://github.com/rsztype/Scripts, Apache-2.0.
    Independent behaviour-only rewrite. No source code was copied.

Run **Masters > Master Twins** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/da5871c9b9405bd4b60a3031fe4832ea380f3e124caff9368546edd03f60d123.py)
<!--/codeinclude-->
