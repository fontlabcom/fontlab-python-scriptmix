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
Requires the reviewed unpublished App>=0.2.48.dev0 candidate and Fly.
Modified from Slobzheninov/Glyphs-Scripts Testing/Text Filter.py (Apache-2.0).
See NOTICE and additional-tools.json for exact provenance and acceptance scope.

Run **Proof > Text Filter** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/1f173d1fa967446c300fc7873bc9e3e1c7107c063f78925f5d4f03e32aa262a2.py)
<!--/codeinclude-->
