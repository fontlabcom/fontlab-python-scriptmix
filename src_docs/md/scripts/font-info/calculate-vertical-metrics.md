---
this_file: src_docs/md/scripts/font-info/calculate-vertical-metrics.md
tags: ["Font Info"]
categories: ["Font Info"]
---

# Calculate Vertical Metrics

Set hhea, Win (and optionally OS/2 typo) vertical metrics to enclose every glyph, per master.

Bounds are rounded outward and can be padded. FontLab's master ascender, descender and
line gap ARE the OS/2 typo values (measured), so Typo is off by default: turning it on
moves the font's ascender/descender lines to the glyph bounds. Preview before Apply.

Open with a font active. Choose current or all masters, padding, line gap and the
metric groups to update. Review the table, then choose Apply. Bounds are captured
when the panel opens; reopen after outline edits. Large scans stop before edits.
Empty masters are skipped. The undoable edit preserves outlines and unselected
metric groups. Reopen after switching the font or active master.

Run **Font Info > Calculate Vertical Metrics** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source identity

SHA256: `171957f5d1a73eb8f5e75b7831e372754790865b6cf13f0de4ec87740c303c26`

[Python source at `8e06999ef5a2`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/8e06999ef5a237c79364b4efd0758bf8fbd5dee8/Scripts/Font%20Info/Calculate%20Vertical%20Metrics.py)
