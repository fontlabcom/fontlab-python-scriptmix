---
this_file: src_docs/md/scripts/font-ui-lab/kerning-group-explorer.md
tags: ["Font UI Lab"]
categories: ["Font UI Lab"]
---

# Kerning Group Explorer

Explore groups and kerning with two linked previews in one retained window.

Use: Select a group, then Use selected group as left or right to stage that key.
The opposite key and typed value stay unchanged. Group actions edit membership;
accepted edits revalidate the pair. Rename/delete does not rewrite kerning keys.
The group preview shows the selected member; the pair proof uses each group's
first member with its actual effective kerning, which may differ from the group
row value; it does not show every combination. Apply/Delete write explicit kerning.

Safety: Use an owned test font. Both editors capture one font at launch; changing
active fonts does not retarget them. Native edits follow its current master and
may refuse unsupported history data. Closing does not save or close the borrowed
font. Native Undo/Redo, painting and saved-font acceptance remain separate.

Run **Font UI Lab > Kerning Group Explorer** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source identity

SHA256: `36d93e8e94b8efd68c173db5e7503ec36b6581b2637e2fb91c9e38914df91b8c`

[Python source at `3bf7b47dd22f`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/3bf7b47dd22f44334af5f83d5c2becb59ce3874f/Scripts/Font%20UI%20Lab/Kerning%20Group%20Explorer.py)
