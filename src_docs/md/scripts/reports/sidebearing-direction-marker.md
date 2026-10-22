---
this_file: src_docs/md/scripts/reports/sidebearing-direction-marker.md
tags: ["Reports"]
categories: ["Reports"]
---

# Sidebearing Direction Marker

Mark each laid-out glyph's advance edge in the active FontLab Glyph window.

What it does:
    Open a Glyph window, then run this script. Choose LTR or RTL explicitly.
    The modeless panel draws a foreground line and triangle across tools. It does
    not edit fonts. Disable or Close removes its overlay and callbacks. Reopen the
    panel after changing the font, master or Glyph window.

    This original implementation adapts akufadhl's Apache-2.0 RSBline behavior.
    Glyphs background ordering and automatic text-tool gating are not provided.
    Shared geometry and native ownership live in Fontlabapp. See its NOTICE.

How it works:
    Use the shared App reporter to draw a line and triangle at the advance
    edge of each laid-out glyph. Track the bound font, master and editor
    through owned callbacks.

Why this design:
    An explicit direction choice avoids assuming that every proof line is
    left-to-right; the overlay remains separate from font data.

How to use:
    Open a Glyph window and run Reports > Sidebearing Direction Marker.
    Choose LTR or RTL and enable the overlay; use Disable or Close to remove
    it.

Benefit:
    Inspect advance edges across tools without adding guides or altering glyph
    spacing.

Run **Reports > Sidebearing Direction Marker** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/5202f5b21310833341a887b10e8a8bb36cf58272cd4a5ec058e58bd685f86944.py)
<!--/codeinclude-->
