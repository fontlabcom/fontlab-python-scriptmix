---
this_file: src_docs/md/scripts/font-ui-lab/font-info-and-vertical-metrics.md
tags: ["Font UI Lab"]
categories: ["Font UI Lab"]
---

# Font Info and Vertical Metrics

Stage font information beside the captured font's vertical metrics report.

Use: Open a font and run this tool. Edit information and explicitly Apply, or
Revert to reload it. Refresh metrics report preserves staged edits. Values are
for the captured font's current info source, not an all-master comparison.
The report lists OS/2 typo, hhea and Windows ascent/descent values, retaining
unset values separately from explicit zero. If a metric cannot be read or is
not finite, the report clears and shows the error; Refresh retries the read.
Switching the active font does not retarget this window. Open another instance
to edit another font. Closing the window disconnects its callbacks and releases
only its owned controls, leaving the borrowed document open.
The shared editor validates writes; the report never writes, saves or closes
fonts. Native history and saved/reopened behavior need separate qualification.

Run **Font UI Lab > Font Info and Vertical Metrics** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source identity

SHA256: `73ba925c0d7db6a569bfad7c65efa707d939a1b7c2a94574bcad43557df555b3`

[Python source at `3bf7b47dd22f`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/3bf7b47dd22f44334af5f83d5c2becb59ce3874f/Scripts/Font%20UI%20Lab/Font%20Info%20and%20Vertical%20Metrics.py)
