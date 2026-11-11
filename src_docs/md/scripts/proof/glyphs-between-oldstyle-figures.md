---
this_file: src_docs/md/scripts/proof/glyphs-between-oldstyle-figures.md
tags: ["Proof"]
categories: ["Proof"]
---

# Glyphs Between Oldstyle Figures

Open a new native Glyph tab with glyphs between oldstyle figures.

Select glyphs in a Font window or occurrences in a Glyph window, then run this
Proof command. Keep their actual order and repeated editor occurrences. The
new tab uses the font's current master; source layer overrides are not copied.
The selected glyph name appears between each context name, or inside repeated
H, I, HHOHH or nnonn contexts, as indicated by the command. Between sequences
end with the selected glyph and two newlines per occurrence. Surround sequences
end with one final context. With no selection, Between opens an empty tab;
Surround opens its context alone. The original behavior is retained.

App builds all glyph-name rows before opening. Named native symbols retain
unencoded glyphs and oldstyle .osf names without slash-text or Unicode fallback.
No context is filtered or substituted when a name is missing. One deadline covers
selected-layer capture,
generation, symbols and preflight. A changed source selection/font or invalid
input refuses the complete operation. A named-content writer can target only a
verified new active tab belonging to the captured source font. It never populates
an existing or foreign tab. Native failure can leave a new tab; no atomic UI
rollback is claimed. The owned native sender is disconnected and deleted.

This adaptation preserves Output instead of clearing/printing status. It calls
no glyph geometry, history, preference or master writer.
Requires App>=1.2.0 and Fly in FontLab9 Python3.11.
Adapted from Pedro Arilla's Apache-2.0 Glyphs between/Glyphs between figures_old.py.
See NOTICE and additional-tools.json for complete source/license provenance.

Run **Proof > Glyphs Between Oldstyle Figures** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source identity

SHA256: `803d6dcf30d8c5a50696c26713a99410e683b863dc2ac50cc2ace10af0f67124`

[Python source at `cb3a95057641`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/cb3a95057641f3b2382a887172fab524dbc4901a/Scripts/Proof/Glyphs%20Between%20Oldstyle%20Figures.py)
