---
this_file: src_docs/md/scripts/proof/context-proof.md
tags: ["Proof"]
categories: ["Proof"]
---

# Context Proof

Preview and open eight exact glyph context proofs in one tabbed tool.

Select glyphs, including repeated Glyph-window occurrences, and choose a named
context tab. Preview and Copy preserve the original proof text. Open creates a
new Glyph tab in the current master without editing font data.
Requires App and Fly. Original Pedro Arilla scripts: Apache-2.0; see NOTICE,
additional-tools.json and menu-consolidations.json for provenance.

The window captures the source font when it opens. Refresh reads that captured
source; switching the active document does not silently retarget an existing
proof. Use the named modes to retain their distinct contexts and repetitions.
The bottom Close action releases the owned controls and preview. It does not
save or close the source font. Copy sends the generated text to the clipboard;
Open creates a separate proof view. These actions do not apply outline, metrics,
anchor or component changes. Use the original menus when a separate window is
more convenient; they remain available alongside this combined view.

Run **Proof > Context Proof** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source identity

SHA256: `b567f12a41602c1852e7bf56aa780b7b895900442dfaf3b05d8716c24a7747af`

[Python source at `370bf9829bc1`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/370bf9829bc141c1c9f88be0018cbc285b502a5d/Scripts/Proof/Context%20Proof.py)
