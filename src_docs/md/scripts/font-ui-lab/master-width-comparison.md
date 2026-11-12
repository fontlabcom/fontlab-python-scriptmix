---
this_file: src_docs/md/scripts/font-ui-lab/master-width-comparison.md
tags: ["Font UI Lab"]
categories: ["Font UI Lab"]
---

# Master Width Comparison

Compare one selected glyph occurrence across the captured FontLab masters.

What: The real glyph sequence shows typed text or explicit `/glyph` names. Select
an occurrence to read a table of fractional advance widths in the font's master
order. Missing master layers remain marked as missing; they are never zero widths.

Use: Open a native FontLab font, then run this tool once. It captures CurrentFont
at invocation and keeps that exact document when the current font changes. Type
text or slash names and click a glyph occurrence. Repeated glyphs retain their
own occurrence index. The shared show(font, parent=None) API accepts an explicit
borrowed Fontport font; it never searches for or switches the current document.

Safety: This reads stored native backend state, not unfinished edits held in
another scripting wrapper. Ordinary UFO fonts lack registered FontLab master
identity and refuse with a visible reason. Closed, replaced or inconsistent
native targets clear the comparison. No font is created, saved, edited or closed;
no master or selection is switched. The window owns only its preview, callbacks
and independent non-owning Python view. Closing disconnects those callbacks and
releases that view after the actual child cleanup acknowledgement. Deferred Qt
destruction is separate from scheduling deletion. Native history, installed
consumer and real-host preservation qualification remain separate.

Run **Font UI Lab > Master Width Comparison** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source identity

SHA256: `120567cd7662c6be1c6802510e70bd3b8c40508826c2f20c0d3e2f636f7a6929`

[Python source at `e537cab9364b`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/e537cab9364bf34af3d36190d5c471795140f722/Scripts/Font%20UI%20Lab/Master%20Width%20Comparison.py)
