---
this_file: src_docs/md/scripts/reports/event-log.md
tags: ["Reports"]
categories: ["Reports"]
---

# Event Log

Print what happens in FontLab to the Output panel: font, window, glyph, layer, selection and edits.

What it does:
    While its small panel is open, every switch of the active font, window or
    tab, glyph, master or layer, and every change of glyph or node selection
    is printed as one line in the Output panel. Undo and redo, saving,
    opening and closing fonts, tool changes, kerning, features, metrics and
    font info edits are printed too. Nothing in the font changes.

How it works:
    The panel listens to FontLab's own notifications. Switching notifications
    arrive in bursts, so they are gathered for a moment, then the current
    state is read once and only the parts that changed are printed. Other
    notifications are printed as they come, without repeats within
    the same second.

Why this design:
    Notifications cost nothing while nothing happens, so the log stays
    lightweight. Comparing states instead of trusting each notification keeps
    the log short and correct when FontLab sends several at once.

How to use:
    Run Reports > Event Log, open the Output panel and work as usual. Close
    the panel to stop logging.

Benefit:
    See exactly which font, glyph and layer a script or tool will act on, and
    which actions FontLab reports, while you work.

Run **Reports > Event Log** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source identity

SHA256: `5a9edeea69d1941b7c59f18fbb9496d82b5e0de370a8fd5a1fcf0368b9520448`

[Python source at `370bf9829bc1`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/370bf9829bc141c1c9f88be0018cbc285b502a5d/Scripts/Reports/Event%20Log.py)
