---
this_file: src_docs/md/scripts/reporters/sidebearing-direction-marker.md
tags: ["Reporters"]
categories: ["Reporters"]
---

# Sidebearing Direction Marker

Mark each laid-out glyph's advance edge in the active FontLab Glyph window.

Open a Glyph window, then run this script. Choose LTR or RTL explicitly.
The modeless panel draws a foreground line and triangle across tools. It does
not edit fonts. Disable or Close removes its overlay and callbacks. Reopen the
panel after changing the font, master or Glyph window.

This original implementation adapts akufadhl's Apache-2.0 RSBline behavior.
Glyphs background ordering and automatic text-tool gating are not provided.
Shared geometry and native ownership live in Fontlabapp. See its NOTICE.

Run **Reporters > Sidebearing Direction Marker** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/629c3fbdb1e07eaa07d9425833431973470404bcd93389e82e41f6db56b3daf9.py)
<!--/codeinclude-->
