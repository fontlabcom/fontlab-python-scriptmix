---
this_file: src_docs/md/scripts/cleanup/start-from-scratch.md
tags: ["Cleanup"]
categories: ["Cleanup"]
---

# Start From Scratch

Clear chosen glyph data to prepare a fresh design.

What: Remove chosen anchors, layer guides, backgrounds, images, colour marks,
kerning class memberships, auxiliary layers, stickers, or paths and components.
Reset
layer metric expressions and advances to 600 when requested. All options start
off. Choose selected or all glyphs, current or all masters, masters or all
foreground layers. Glyph marks and kerning membership use the glyph scope.
How: Preview the exact scope, then confirm the font and counts before Clear.
A changed scope needs a new Preview. Image and sticker shapes stay unless
chosen.
Why: Explicit switches prevent accidental deletion of unrelated design data.
Use: Select glyphs, choose the scope and data, Preview, then Clear chosen data.
Benefit: Several cleanup operations are recorded as one Undo step. Automatic
layers and their bases are refused. Shared background mappings also refuse.
Font-level guides stay; the guide option clears only guides on scoped layers.

Independent behaviour rewrite after Pedro Arilla, glyphs-scripts,
Cleaning/Start-from-scratch.py, Apache-2.0.
Repository: https://github.com/pedroarilla/glyphs-scripts . No source code
copied.

Run **Cleanup > Start From Scratch** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/9d7ee77ef3f3becc3b00543225a814f1c48347b0346c8ae5d0d7af84887e8ff2.py)
<!--/codeinclude-->
