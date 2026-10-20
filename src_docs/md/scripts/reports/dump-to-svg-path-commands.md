---
this_file: src_docs/md/scripts/reports/dump-to-svg-path-commands.md
tags: ["Reports"]
categories: ["Reports"]
---

# Dump to Svg Path Commands

First selected layer own paths only; ordered M/L/C operands, unconditional Z and blank line after every open/closed/empty contour. Unsupported/quadratic segments refuse the whole report; not a complete SVG/component export. Own affine shape transforms are applied; projective transforms refuse the whole report.

Open a font and select glyph layers before running. The owned modeless read-only
panel offers selectable text, Refresh and Close. Failures clear the entire old
report; no partial prefix is shown. No font, file, clipboard, Output, selection,
history or preference writers run. Actual native getter preservation and panel
lifetime acceptance remain pending. Requires FontLab9 Python3.11, matching Fly
and App0.2.77.dev0 or later. Adapted from simoncozens--GlyphsScripts/Dump to SVG.py; see NOTICE.

Run **Reports > Dump to Svg Path Commands** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/be2066e63cdf0a8ceb58f8ca251b8bcf643ecee821423b7dfbb27fb9376da535.py)
<!--/codeinclude-->
