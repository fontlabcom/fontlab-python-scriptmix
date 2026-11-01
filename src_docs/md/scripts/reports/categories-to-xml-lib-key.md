---
this_file: src_docs/md/scripts/reports/categories-to-xml-lib-key.md
tags: ["Reports"]
categories: ["Reports"]
---

# Categories to XML Lib Key

Export a complete ordered public.openTypeCategories UFO lib fragment.

Open a font and run this command. The read-only modeless panel includes every
native glyph in font order. Select the XML for manual insertion into a UFO's
lib dictionary. Mark becomes mark; every other category becomes base, including
ligatures and unknown glyphs, exactly as in Simon Cozens' MIT source. Glyph names
are XML-escaped. Empty fonts produce an empty dictionary. No file is written.

Glyport's GSGlyph.category policy supplies categories from maintained glyphsLib
GlyphData: names first, Unicode fallback for unknown names. Explicit GDEF class
is not a substitute. This command requires fontlab-glyport and its declared
glyphsLib dependency as well as matching App and Fly, in FontLab9 Python3.11.
Refresh rebuilds the full snapshot; a changing source or missing dependency
clears the report and shows the failure. Close releases the owned callbacks.
No clipboard, preferences, Output, selection, history or font writers are used.
Native getter preservation and actual panel behavior await native acceptance.
Adapted from Simon Cozens' Categories to XML lib key.py; see NOTICE.

Run **Reports > Categories to XML Lib Key** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/ded9427081ebc8919ad7aa4dc315a118b6cc0c8d701cbcd34d44e689cee086f3.py)
<!--/codeinclude-->
