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

SHA256: `e61b5781959bf8211a00b7c58b132df7b9a434531b2b3b6b16d9b9f9dfe49cb8`

[Python source at `6b1048c4f1db`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/6b1048c4f1dbc64ebe49d419db9193ccb3d9a9f0/Scripts/Reports/Font%20Audit.py)
