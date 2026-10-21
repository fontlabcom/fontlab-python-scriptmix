---
this_file: src_docs/md/scripts/proof/real-spanish-text.md
tags: ["Proof"]
categories: ["Proof"]
---

# Real Spanish Text

Open a new Glyph tab with five randomly chosen Spanish prose passages.

What it does:
    Draw five passages without replacement. Keep Spanish accents, punctuation
    and case, including a final space. No passage repeats in one proof.

How it works:
    Capture the current font, assemble the proof, then use the shared App
    text-tab helper with that font's id. Send missing characters unchanged.
    Refuse text that PythonQt cannot pass intact. No font data is written;
    no Undo step is needed. Tab creation can fail after a new tab opens.

Why this design:
    The native Glyph tab supplies an editable, non-modal proof. Run again for
    another sample. No separate panel or settings are needed. The 24 original
    passages below replace the upstream collection of 300 third-party excerpts.
    They include ñ, ü, accented vowels, inverted punctuation and figures.

How to use:
    Activate a font and run this command. Inspect spacing, accents and text
    colour in the new Glyph tab. Keep earlier tabs available for comparison.

Benefit:
    Test readable Spanish without finding and pasting external sample text.

Credit:
    Behaviour after Pedro Arilla, glyphs-scripts/Real* text/Real* Spanish text.py,
    Apache-2.0, https://github.com/pedroarilla/glyphs-scripts.
    Independent behaviour-only rewrite. No source code or corpus was copied.
    Proof passages are original to this tool, Apache-2.0.

Run **Proof > Real Spanish Text** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/d661bbd90038057b21eb29c741c4d281cfbc36843c7e07e50a2e41f4d86b30ce.py)
<!--/codeinclude-->
