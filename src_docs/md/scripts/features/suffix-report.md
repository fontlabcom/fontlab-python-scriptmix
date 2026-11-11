---
this_file: src_docs/md/scripts/features/suffix-report.md
tags: ["Features"]
categories: ["Features"]
---

# Suffix Report

Suffix inventory across the whole font. Suggestions are naming hints; review the generated code.

What it does:
    Run with a font active. All original controls use the shared fly panel lifecycle.
    Feature data is font-wide; reopen after switching fonts or changing source.

How it works:
    Collect complete suffixes after the first dot in glyph names. Count names
    and usable base pairs, suggest conventional tags and build a copyable code
    preview.

Why this design:
    A suffix can exist without a base glyph; separate counts prevent an orphan
    name from becoming a false substitution suggestion.

How to use:
    Run Features > Suffix Report. Select a suffix row, inspect the suggested
    tag and substitution pairs, then copy the snippet for manual review in the
    Features panel.

Benefit:
    Inventory alternate sets and prepare feature text without automatically
    adding rules to the font.

Run **Features > Suffix Report** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source identity

SHA256: `ce705a74019336af6541ae02ddfb705741a680fc60c43a1e52f08c8de0b865d9`

[Python source at `168b57cbfbaf`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/168b57cbfbaf1b00b43f4aa06ba26d2e01ba12e1/Scripts/Features/Suffix%20Report.py)
