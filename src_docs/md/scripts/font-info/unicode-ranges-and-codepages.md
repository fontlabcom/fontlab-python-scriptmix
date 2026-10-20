---
this_file: src_docs/md/scripts/font-info/unicode-ranges-and-codepages.md
tags: ["Font Info"]
categories: ["Font Info"]
---

# Unicode Ranges and Codepages

Report OS/2 range bits and complete printable codepage coverage from every glyph encoding; no font changes.

Open with a font active. Read covered OS/2 Unicode ranges and printable single-byte
codepage coverage, then use Refresh report after encoding edits. Every encoding
on each glyph is counted. Multibyte codepages need manual review. This report
does not change export flags: coverage alone does not establish a correct flag.

Run **Font Info > Unicode Ranges and Codepages** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/e8fd9fab22d4aead8839c737d5a64fe0e8fd476aedc375728ee7e1de54b6cf14.py)
<!--/codeinclude-->
