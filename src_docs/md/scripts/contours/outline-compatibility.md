---
this_file: src_docs/md/scripts/contours/outline-compatibility.md
tags: ["Contours"]
categories: ["Contours"]
---

# Outline Compatibility

Compare contour order, promote matching straight segments and inspect node counts.

What it does:
    Open Contour Order View, Make Compatible and Node Statistics in one tabbed
    window with a read-only glyph canvas. Compare every master with numbered
    contours, start dots and first-segment arrows. Inspect sortable count rows
    and select the flagged glyphs in the Font window without changing outlines.

How it works:
    The window captures its font and master. Make Compatible retains the
    original line-to-cubic policy: compare corresponding closed PostScript
    segments across every declared master, keep mismatched or unsupported
    glyphs, preserve endpoints and use the existing guarded history writer.
    Shared, locked and automatic outlines remain protected by the common guards.

How to use:
    Select glyphs, run Contours > Outline Compatibility, and choose a task.
    Align contour starts and directions before promoting segments. Use Preview
    Changes to review a write, then Apply Changes. Discard Preview before
    refreshing staged work. Changing the font or master requires reopening.
    Select a table row to inspect its captured glyph and master in the canvas.

Credits:
    FontLab sample inspectors, Apache-2.0. Make Compatible is an independent
    behaviour adaptation after Simon Cozens, GlyphsScripts (2017), MIT:
    https://github.com/simoncozens/GlyphsScripts . No original code was copied.
    Full source identities and licence notices are retained in Scriptmix NOTICE.
    Requires FontLab App with Outline Compatibility and the shared studio shell.

Run **Contours > Outline Compatibility** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source identity

SHA256: `40c5d904321910384646a62892f6454dd8f41718b215ae7234aaa0ed4ca9c438`

[Python source at `168b57cbfbaf`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/168b57cbfbaf1b00b43f4aa06ba26d2e01ba12e1/Scripts/Contours/Outline%20Compatibility.py)
