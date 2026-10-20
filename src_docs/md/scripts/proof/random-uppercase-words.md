---
this_file: src_docs/md/scripts/proof/random-uppercase-words.md
tags: ["Proof"]
categories: ["Proof"]
---

# Random Uppercase Words

Open a new FontLab Glyph tab with random uppercase words.

Open a font and run this Proof command. It uses the current font and opens one
new tab, preserving existing tabs. Run again to get another proof. Content is
One uppercase entry per a..z bucket from all 4,991 source entries.
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
Requires reviewed App>=0.2.38.dev0 and Fly in FontLab9 Python3.11. Adapted from Pedro Arilla's Apache-2.0 Random/Random UPPERCASE words.py.
See NOTICE and additional-tools.json for source/data/license provenance.

Run **Proof > Random Uppercase Words** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/cb44f07ddd4cf7c8e64a285a9af8ad756bf5b272203c16bc778edbad8b03d4bb.py)
<!--/codeinclude-->
