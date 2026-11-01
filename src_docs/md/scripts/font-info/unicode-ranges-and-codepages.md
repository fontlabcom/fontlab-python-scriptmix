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

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/8092778be9fe1747aa459a17e1f0ed9f45b5428b541492dc8a93efe92d15917c.py)
<!--/codeinclude-->
