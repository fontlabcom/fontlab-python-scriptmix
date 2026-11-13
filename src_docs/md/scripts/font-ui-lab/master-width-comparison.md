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

SHA256: `1b0635539174f2ffb420d1e1be429bddc0360bbe0e62785c06071b1e1113d96a`

[Python source at `3bf7b47dd22f`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/3bf7b47dd22f44334af5f83d5c2becb59ce3874f/Scripts/Font%20UI%20Lab/Master%20Width%20Comparison.py)
