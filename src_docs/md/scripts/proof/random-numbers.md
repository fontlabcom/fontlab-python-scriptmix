---
this_file: src_docs/md/scripts/proof/random-numbers.md
tags: ["Proof"]
categories: ["Proof"]
---

# Random Numbers

Open a new FontLab Glyph tab with random numbers.

Open a font and run this Proof command. It uses the current font and opens one
new tab, preserving existing tabs. Run again to get another proof. Content is
200 digits; draw a divisor from 2 and 3 at every index.
Keep all source draw order, spaces, duplicate entries and compound names.
Spaces for non-text/numbers follow index modulo a fresh random divisor,
including index zero. Words keep their final space. Do not trim or filter
characters absent from the font; send them unchanged to the native editor.

Shared App code generates the complete text before a tab is opened. Fly loads
App. The native doCreateTextBlock operation opens the new FontLab Glyph tab.
No application-wide event loop or replacement editor is needed.
No open font is an error before random draws/tab creation. Resource/generation
failure opens no tab. A native tab failure propagates; it may leave an empty
new tab, so atomic rollback is not claimed. Native tab content, missing-character
handling, source-font binding and full data/history preservation remain pending.

The port repairs the source's undefined Font global with explicit current-font
lookup. It preserves Output instead of clearing it or printing status there.
Requires reviewed App>=0.2.38.dev0 and Fly in FontLab9 Python3.11. Adapted from Pedro Arilla's Apache-2.0 Random/Random 123.py.
See NOTICE and additional-tools.json for source/data/license provenance.

Run **Proof > Random Numbers** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/4a3aad2b09e4dae782536afec30ad9e5ff763dc1de960cd203fc542a5ec8a76c.py)
<!--/codeinclude-->
