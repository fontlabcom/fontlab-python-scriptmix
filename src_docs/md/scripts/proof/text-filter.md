---
this_file: src_docs/md/scripts/proof/text-filter.md
tags: ["Proof"]
categories: ["Proof"]
---

# Text Filter

Filter proof text in a modeless FontLab Text Simplifier panel.

Run this Proof command, enter input and a regular-expression character class,
then choose Simplify. Ranges such as A-Z and escapes such as \s keep their
source meaning. Output is read-only. Reset retains input and restores the
original output/character defaults. All three fields and window geometry are
saved in this tool's own settings namespace. Optional New Tab uses the source
font captured on launch; a changed/closed font is refused by the shared sender.

Fly loads shared App controls, filtering, saved fields and owned lifecycle.
No application event loop, system clipboard or font-design writer is used.
Native PythonQt/settings/tab/font/history preservation remains pending.
Requires App>=0.2.48.dev0 and Fly.
Modified from Slobzheninov/Glyphs-Scripts Testing/Text Filter.py (Apache-2.0).
See NOTICE and additional-tools.json for exact provenance and acceptance scope.

Run **Proof > Text Filter** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/b26e7587bed8afbe53959fe0d283743fa592f9beff7e00bd21b28db4be8707fd.py)
<!--/codeinclude-->
