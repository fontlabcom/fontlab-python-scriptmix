---
this_file: src_docs/md/scripts/reporters/duplicate-anchor-rings.md
tags: ["Reporters"]
categories: ["Reporters"]
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

Run **Reporters > Duplicate Anchor Rings** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/54ef3ff781a4469741fb2f3e049a14bfec048d23c12919e43c508bce4ba24e7f.py)
<!--/codeinclude-->
