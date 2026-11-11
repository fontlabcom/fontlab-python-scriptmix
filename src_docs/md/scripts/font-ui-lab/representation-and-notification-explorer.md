---
this_file: src_docs/md/scripts/font-ui-lab/representation-and-notification-explorer.md
tags: ["Font UI Lab"]
categories: ["Font UI Lab"]
---

# Representation and Notification Explorer

Inspect selected glyph representations and observed cache refresh notifications.

Use: Open a font, run this tool and select glyphs in its browser. Inspect the
representation results and notification/cache status; unsupported capabilities
remain explicit. The window keeps the font captured when it opened.
Safety: This explorer does not edit glyph geometry or save the source. Native
FontLab notification delivery, cache preservation and UI lifetime still require
qualification.

Select a glyph in the inspector browser to attach its supported change observer
and read the representation values and cache-presence observations. Refresh
reads that same selected glyph again. A notification refresh is reported only
when the observer callback actually arrives; an unsupported notification or
cache API is shown as unavailable. No global font update queue is cleared.
Close the window to detach its observer and release the preview callbacks.
Selecting a different glyph changes only the inspector target.

Run **Font UI Lab > Representation and Notification Explorer** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source identity

SHA256: `5d3c5aea2891ca3c803e9b7e52fd9e7ac89cafc13c35cf3028853eb5f8efe06e`

Immutable source link pending a reviewed containing commit.
