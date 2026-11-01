---
this_file: src_docs/md/use.md
tags:
- Python
categories:
- Guides
---

# Work with an open font

Keep the font that supplied a preview open until you apply the change.
Editors refuse an Apply operation if that font or its relevant source values
have changed. Refresh the preview after editing the font.

## Reports and selection

Reports inspect font data. Some reports can select the glyphs in their results.
Selection is a change to the workspace, even when the font data stays intact.
Rescan a report after switching fonts. A failed scan clears partial results.

## Editors and history

Read the complete preview before you choose **Apply**. The current editors use
shared history helpers and refuse conditions that cannot preserve the recorded
Undo and Redo behavior. A no-op plan does not add a history step. The individual
script's source and description give its scope and remaining host restrictions.

## Canvas reporters

Open a Glyph window before you start a reporter. Set its direction or handle size
in the panel. **Disable** or **Close** removes the overlay. Reopen the reporter
after switching the font, master or Glyph window. These foreground adaptations
do not implement Glyphs' background ordering or automatic tool suppression.
