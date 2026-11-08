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

## Source identity

SHA256: `19c453a8da6f294df2c7848285fa8211dd721f505c15e302a5366a41ee744609`

[Python source at `1fddaa75b7e6`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/1fddaa75b7e644ddcb3764909f3dd231cc78528e/Scripts/Cleanup/Start%20From%20Scratch.py)
