---
this_file: src_docs/md/scripts/reports/duplicate-anchor-rings.md
tags: ["Reports"]
categories: ["Reports"]
---

# Duplicate Anchor Rings

Highlight anchor pairs less than one font unit apart in the Glyph window.

Open a Glyph window, then run this script. Choose handle size5,8 or12.
Every matching unordered pair gets an unfilled red/yellow ring at its first
anchor. Three coincident anchors produce three rings. Disable or Close removes
the overlay and callbacks. Reopen after changing font, master or Glyph window.
No font data or preferences are written.

This original implementation adapts mekkablue's Apache-2.0 duplicate-anchor
reporter. Drawing is foreground across tools, with explicit handle sizes.
Glyphs background ordering and text/hand-tool suppression are not provided.
Shared capture, painting and native ownership live in Fontlabapp. See its NOTICE.

Run **Reports > Duplicate Anchor Rings** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/61afab3096345cdc4b810065656373da27a2db03b77399949fe37164e48a7251.py)
<!--/codeinclude-->
