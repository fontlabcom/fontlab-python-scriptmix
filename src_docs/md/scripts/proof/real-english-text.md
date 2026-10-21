---
this_file: src_docs/md/scripts/proof/real-english-text.md
tags: ["Proof"]
categories: ["Proof"]
---

# Real English Text

Open a new Glyph tab with five randomly chosen English prose passages.

What it does:
    Draw five passages without replacement. Keep their case and punctuation,
    including a space after the last passage. No passage repeats in one proof.

How it works:
    Capture the current font, assemble the proof, then use the shared App
    text-tab helper with that font's id. Send missing characters unchanged.
    Refuse text that PythonQt cannot pass intact. No font data is written;
    no Undo step is needed. Tab creation can fail after a new tab opens.

Why this design:
    The native Glyph tab supplies an editable, non-modal proof. Run again for
    another sample. No separate panel or settings are needed. The 24 original
    passages below replace the upstream collection of 300 third-party excerpts.
    They exercise connected prose, figures, currency, quotes and punctuation.

How to use:
    Activate a font and run this command. Inspect spacing and text colour in
    the new Glyph tab. Existing tabs remain available for comparison.

Benefit:
    Test readable English without finding and pasting external sample text.

Credit:
    Behaviour after Pedro Arilla, glyphs-scripts/Real* text/Real* English text.py,
    Apache-2.0, https://github.com/pedroarilla/glyphs-scripts.
    Independent behaviour-only rewrite. No source code or corpus was copied.
    Proof passages are original to this tool, Apache-2.0.

Run **Proof > Real English Text** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/c4ebaa3ac8b97544c616c075369f1080633835be4de620fd2af3b97a821153b6.py)
<!--/codeinclude-->
