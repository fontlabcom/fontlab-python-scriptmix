---
this_file: src_docs/md/scripts/metrics/check-tabular-widths.md
tags: ["Metrics"]
categories: ["Metrics"]
---

# Check Tabular Widths

Check exact selected-layer advances against the first selected occurrence.

Select glyphs in a Font window or layer occurrences in a Glyph window. Run
this Metrics command. The first occurrence supplies the reference. Editor
repeats retain their own layer choices; Font-window rows use the current master.
Fractional values remain exact.
Metrics keys and Auto do not override the actual advances. The report shows
one result per selected-layer occurrence, same/different totals and time heading.

Use Refresh after changing selection, master or widths. Close removes the
owned modeless panel. The report calls no font, selection, history, preferences
or Output writers. Empty/stale/missing sources produce a complete diagnosis.
Requires App>=1.2.0 and fontlab-fly in FontLab9
Python3.11. Adapted from Pedro Arilla's Apache-2.0 Tabular width checker; see
additional-tools.json and NOTICE.

Run **Metrics > Check Tabular Widths** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source identity

SHA256: `12038e43a8cdc63c5fc5a7fbf68f8dcaa2db65f5fd56aeb0944df1ea6d34991f`

[Python source at `3dc87d8a0e3d`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/3dc87d8a0e3dec803dc9255436da39eb19abefb2/Scripts/Metrics/Check%20Tabular%20Widths.py)
