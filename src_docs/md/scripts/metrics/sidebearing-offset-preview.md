---
this_file: src_docs/md/scripts/metrics/sidebearing-offset-preview.md
tags: ["Metrics"]
categories: ["Metrics"]
---

# Sidebearing Offset Preview

Preview how a sidebearing offset would shift the selected glyphs.

What: Opens a modeless panel with offset controls: a minimum, a maximum and a
value, plus a choice of horizontal or vertical orientation and two invert
options for the control itself. For every selected glyph layer the report
shows what the geometric sidebearings would become if the ink moved by the
chosen offset: the left sidebearing grows by the offset, the right shrinks by
it and the advance width stays the same. Values are whole font units from
-100 to 100.

Use: Select glyphs in a Font window, or glyph layers in a Glyph window. Run
Metrics > Sidebearing Offset Preview. Move the offset control and read the
report. Press Refresh Selection after you change the selection, the master or
the outlines. Close the panel when you are done. With nothing selected the
report asks you to refresh after selecting glyph layers.

Safety: Read-only preview. The panel says that font data is unchanged, and it
is. The tool reads the selected layers, their advances and their ink extent.
It writes no font data, metrics, selection, history, preference, clipboard or
Output text. Nothing is applied; use the Metrics editors to set sidebearings.
If the font or selection changes while the tool reads it, it refuses to publish
a partial result.

Source: Original workflow built on the shared App spacing offset preview
(fly.ap.metrics.offset.model), Apache-2.0.
Requires App>=1.2.0 and fontlab-fly in FontLab 9 Python 3.11.

Run **Metrics > Sidebearing Offset Preview** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source identity

SHA256: `aebd0335756696d5f766d9ccbf33c3497bb97b4530ddf91ca19fc562788c3b75`

[Python source at `bf9287c6130a`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/bf9287c6130a3083b3c1047050305dfceecbee2b/Scripts/Metrics/Sidebearing%20Offset%20Preview.py)
