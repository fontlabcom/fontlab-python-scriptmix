---
this_file: src_docs/md/scripts/guides/suggest-zones-from-overshoots.md
tags: ["Guides"]
categories: ["Guides"]
---

# Suggest Zones From Overshoots

Suggest alignment zones from the overshoots of H, O, x and o, then apply them.

What it does:
    For each chosen master, measures H and O at the baseline and the cap
    height, and x and o at the x-height. A zone starts at the edge of the flat
    letter (H or x). Its width is the distance that the round letter (O or o)
    passes that edge: upward for the cap-height and x-height zones, downward
    for the baseline zone. The table shows every suggested zone and the zone
    that it replaces. Apply writes the previewed zones of all chosen masters
    as one Undo step. This tool reads the four glyphs and does not edit them.

How it works:
    A suggested zone replaces the existing zone of the same kind at the same
    position; otherwise the zone with the same name; otherwise it is added.
    A replaced zone keeps its name, tags and lock. All other zones stay. The
    zones are written through the shared native zone backend, the route of
    Metrics > Alignment Zones. Apply first measures the four glyphs again and
    refuses when they changed since the preview. The extents come from the
    outline geometry (nodes and exact curve extremes, components placed),
    because FontLab's cached glyph box can be stale after an edit (fl#8575).

Why this design:
    The preview shows the exact zones before any write, and one shared zone
    writer keeps the refusals and the Undo step the same in every zone tool.

How to use:
    Open a font, activate its Font window and run Guides > Suggest Zones From
    Overshoots. Choose the current master or all masters, review the table and
    press Apply. Press Refresh after you edit the glyphs or the zones. Use
    Edit > Undo in the Font window to revert the whole Apply.

Benefit:
    Set zones that match the real overshoots of every master in one reviewed
    step.

Limitations:
    - A missing glyph or layer, or a layer with no height, gives no zone for
      the rules that need it. The status line names them.
    - A glyph whose outline cannot be read (for example a segment with one
      cubic control) is listed as not measured, with the reason; the other
      glyphs are still measured.
    - Stroke thickness is not counted: zones measure the outline.
    - The Undo step is named "Alignment Zones", like the zone panel's.
    - Apply needs the Font window of this font as the active window. It
      refuses while a Glyph window is the active canvas.
    - Apply re-creates every zone guide of a changed master (new ids,
      x-centre 0, font guideline style), as Font Info does.
    - FontLab defect fl#8574: after Edit > Undo or Redo, the metric guides
      show 3 of 9 lines until you reopen the font. The saved file is correct.

Credit:
    Adapted from zones_from_glyphs.py, the author's own FontLab sample,
    Apache-2.0.

Run **Guides > Suggest Zones From Overshoots** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/ff7422573379bb6724d661185929dc64856113c733d76512a52f4042cefe6c1c.py)
<!--/codeinclude-->
