---
this_file: src_docs/md/scripts/contours/curve-editor.md
tags: ["Contours"]
categories: ["Contours"]
---

# Curve Editor

Inspect and apply outline changes through named task tabs and a live glyph view.

Convert straights to cubics, straighten all or only short curves, retract
handles, or simplify selected polygon nodes.
Choose glyphs and master scope in the task tab. Preview Changes lists the exact
planned edits without writing. Inspect the sortable, filterable result table
and the captured glyph and layer in the read-only canvas. Apply Changes rechecks
the accepted input and source state before the original guarded native writer.

Staged previews stay in their tabs. Use Discard Preview before Refresh. Locked,
shared and automatic targets retain their operation-specific refusals; changes
to bases of automatic composites need explicit consent. Structural operations
retain the original compatibility rules. Partial native failures remain visible
and require checking the font and Undo. Save/reopen caveats for raw Smooth flags
remain in the relevant operation's status advice.

Requires FontLab App with the Curve Editor composition and fontlab-fly.
Sources: FontLab App contributors, Apache-2.0; independent adaptations after
Simon Cozens (MIT) and Pedro Arilla (Apache-2.0). See Scriptmix NOTICE and the
preserved provenance manifests for the complete original source identities.

Run **Contours > Curve Editor** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source identity

SHA256: `5faa60d22549ac454d2ad9e433631cc31ea1a7f4e9b0e53aeeb888310172e2af`

[Python source at `168b57cbfbaf`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/168b57cbfbaf1b00b43f4aa06ba26d2e01ba12e1/Scripts/Contours/Curve%20Editor.py)
