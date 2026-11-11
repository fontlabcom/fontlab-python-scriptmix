---
this_file: src_docs/md/scripts/font-ui-lab/glyph-browser-and-metrics.md
tags: ["Font UI Lab"]
categories: ["Font UI Lab"]
---

# Glyph Browser and Metrics

Browse glyphs with linked outlines, geometric sidebearings and selected advance comparisons.

Use: Open this window with a font available, filter the glyph list by name and
select one or more glyphs. The outline and metric table describe the first
selected glyph. The advance comparison uses every selected glyph and reports
their actual widths, including fractional values. It helps identify unequal
advances in a set intended to have tabular spacing without changing any widths.

The table shows advance, outline bounds, geometric left sidebearing and geometric
right sidebearing. Component outlines use their transformations when calculating
bounds. An empty outline has no geometric sidebearings; it can still have a useful
advance. These measurements describe geometry, rather than a spacing policy or a
promise that visually similar glyphs will have identical apparent margins.

Safety: This is a read-only inspection of the current borrowed font. It does not
edit outlines, spacing, selection data or font contents, save a file, or close the
font. Missing fonts and unreadable glyph data clear the displayed measurements
and preview instead of leaving another glyph's values on screen. Close the
inspection window when finished.

Run **Font UI Lab > Glyph Browser and Metrics** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source identity

SHA256: `069d4ccba0484e420c4f905cbe3528471f917a7f1b189e5e3cf5f183cb2abcb6`

[Python source at `4bab81718f97`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/4bab81718f976cbdb0cf33c249fc85b5df530a9a/Scripts/Font%20UI%20Lab/Glyph%20Browser%20and%20Metrics.py)
