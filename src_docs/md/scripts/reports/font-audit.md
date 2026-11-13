---
this_file: src_docs/md/scripts/reports/font-audit.md
tags: ["Reports"]
categories: ["Reports"]
---

# Font Audit

Inspect whole-font inventory, encoding, categories and case consistency.

Eight named report tabs retain the original report controls, CSV export,
selection guards and case-coverage proof workflow. The shared App shell has
an independent read-only TMetrics preview. Category XML includes every glyph
in font order; select the fragment for manual insertion into a UFO lib.

Credits: FontLab App contributors (Apache-2.0); mekkablue Casefolding Report
workflow (Apache-2.0); Simon Cozens Categories to XML lib key workflow (MIT).
See NOTICE for full source credits. Requires App's WP08 Font Audit assembly,
Fontport, Fly and Glyport with maintained glyphsLib GlyphData.

Open the tool with the intended font active, then select the named report tab.
Refresh rereads the captured source. Report controls retain their own selection
and export actions; the shared preview is read-only. Switching to another font
does not silently retarget an existing audit window. Close releases the owned
report controls and preview without saving or closing the source document.
Use the individual report menus for separate windows when comparing results.

Run **Reports > Font Audit** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source identity

SHA256: `c9e841a026e79192a99ba924e153088fb658eb12b14189b10da03ffaa37f84ea`

[Python source at `3bf7b47dd22f`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/3bf7b47dd22f44334af5f83d5c2becb59ce3874f/Scripts/Reports/Font%20Audit.py)
