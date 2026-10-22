---
this_file: src_docs/md/scripts/masters/deliver-glyphs.md
tags: ["Masters"]
categories: ["Masters"]
---

# Deliver Glyphs

Deliver selected outline glyphs to the font you activate next.

What:
    Keep a source font and glyph selection in a non-modal panel. Activate a
    destination font, preview master pairing, then Deliver. Repeat for other
    open fonts. Existing glyphs are kept unless Replace is ticked.
How:
    Master names match without case or surrounding spaces. Other destination
    masters use the source master captured on launch; every fallback is listed.
    glyph_creation runs FontLab's Add Glyph command for each new glyph.
    New glyph Unicode assignments go only through that command. Existing
    Unicode lists stay unchanged. Conflicts with other destination glyphs are
    kept rows. Outlines, anchors, advances and metrics expressions then travel
    in one geometry action through outline_writer and anchor_writer.
Why:
    Native copy and paste also transfers components and hints; this tool adds
    retained source selection, master-name pairing and visible fallbacks across
    repeated destinations. It writes only to the current font. Component links
    and hints are not carried to another font, so those glyphs are kept.
    Decompose components in the source if outline-only delivery is appropriate.
    Existing target components, hints and shared shape data also keep the
    glyph. Category, subcategory, script and export status from Postino are
    not transferred; existing destination values stay. Units per em must match.
    contour_copy restores node names and raw flags with selection cleared.
    Element names, notes and transforms are copied explicitly. Named contours
    and nodes with an explicit corner_smooth value are kept. Other node and
    contour properties are not detected and not copied (fl#8569). Nothing is
    saved.
Use:
    Select glyphs in the source Font window and run. Activate a destination
    Font
    window with its Glyph editors closed. Click Preview. Review every row and
    any 'may rebuild auto' warning. Tick consent if appropriate, then Deliver.
    Each new glyph is recorded as its own Undo step, and the outlines as one
    more Undo step. Existing glyph notes and other metadata stay as they are.
Benefit:
    Send a consistent set of outline glyphs to several working fonts without
    leaving empty masters or silently dropping components and hints.
Credit:
    Giuseppe Salerno / Resistenza Type, Postino.py,
    https://github.com/rsztype/Scripts, Apache-2.0.
    Independent behaviour-only rewrite. No source code was copied.

Run **Masters > Deliver Glyphs** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/54dd8e13b586c94ad5505e0dd8bab6636f08203ab1d6c2c706cbc512bf58af4d.py)
<!--/codeinclude-->
