---
this_file: src_docs/md/scripts/utilities/text-holder.md
tags: ["Utilities"]
categories: ["Utilities"]
---

# Text Holder

Keep proof text in an editable, persistent floating scratchpad.

What it does:
    Find highlights the first literal match. Find & Replace changes matches in the
    selection or the whole text. Save stays open; Save & Close and Ignore & Close
    retain their distinct actions. Saved UTF8 text recovers on the next launch.

    Independently implemented from Reza Bohloul, Window/Text holder.py.
    No original body is copied or executed; original licence is undeclared.
    See NOTICE and additional-tools.json. Requires Fly and App 1.2.0.

How it works:
    Open the shared App text-holder editor through Fly. Use its persistent
    text store, literal Find and selection-aware replacement without accessing
    glyph geometry.

Why this design:
    A persistent scratchpad keeps proof text between launches without putting
    temporary material into a glyph note or font metadata.

How to use:
    Run Utilities > Text Holder. Enter text, use Find or Find & Replace and
    choose Save, Save & Close or Ignore & Close according to the required
    persistence action.

Benefit:
    Keep reusable proof text available beside FontLab without changing the
    font.

Run **Utilities > Text Holder** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source identity

SHA256: `63582be433e9a80fe5819c46b24ae9b4cab3204b54765fbe70573ff6e7909fba`

[Python source at `3bf7b47dd22f`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/3bf7b47dd22f44334af5f83d5c2becb59ce3874f/Scripts/Utilities/Text%20Holder.py)
