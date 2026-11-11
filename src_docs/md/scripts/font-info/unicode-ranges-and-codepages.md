---
this_file: src_docs/md/scripts/font-info/unicode-ranges-and-codepages.md
tags: ["Font Info"]
categories: ["Font Info"]
---

# Unicode Ranges and Codepages

Report OS/2 range bits and complete printable codepage coverage from every glyph encoding; no font changes.

What it does:
    Open with a font active. Read covered OS/2 Unicode ranges and printable single-byte
    codepage coverage, then use Refresh report after encoding edits. Every encoding
    on each glyph is counted. Multibyte codepages need manual review. This report
    does not change export flags: coverage alone does not establish a correct flag.

How it works:
    Collect all valid glyph encodings, assess OS/2 Unicode ranges and compare
    printable characters of supported single-byte codepages. Report multibyte
    domains for manual review.

Why this design:
    Encoding coverage alone cannot establish correct export flags, so this
    tool reports findings rather than writing OS/2 bits.

How to use:
    Run Font Info > Unicode Ranges and Codepages. Inspect coverage rows and
    use Refresh report after encoding changes; review multibyte codepages
    separately.

Benefit:
    Gather evidence for export-flag decisions without changing font metadata
    or encodings.

Run **Font Info > Unicode Ranges and Codepages** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source identity

SHA256: `1cece3e6b233d1f909534262cb55d7199ea84bc303db50b3936c06e8493a7478`

[Python source at `8852124d9fe2`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/8852124d9fe2b69cf663e1c6db8d6db4bf5e8454/Scripts/Font%20Info/Unicode%20Ranges%20and%20Codepages.py)
