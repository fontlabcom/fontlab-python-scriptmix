---
this_file: src_docs/md/scripts/utilities/find-font-files.md
tags: ["Utilities"]
categories: ["Utilities"]
---

# Find Font Files

Search the files of one folder for a piece of text, such as a glyph name.

What: Opens a modeless search window with three fields: Named (a file name
pattern), Containing text and In directory (it starts in your Documents
folder). The window searches the files directly inside that folder (it does
not descend into sub-folders) and lists every file that contains the text,
with the table filling in while the search runs. Use it to find which font
sources, feature files or scripts mention a glyph name, a feature tag or a
family name.

Use: Run Utilities > Find Font Files. Press Browse to pick a folder, type the
text, press Find and watch the result table. Double-click a result, or press
Return on it, to open that file with the application your system has for it.
Press Cancel to stop a search that is still running. Closing the window also
stops it and releases the files it had opened.

Safety: Only reads files. The search opens files in the chosen folder for
reading and never changes, moves, creates or deletes a file. It does not read
or write font data, selection, history, preferences, clipboard or Output
text, and it never imports or runs the files it searches. Opening a result is
an explicit double-click and is handed to the normal desktop opener, which
may start another application.

Source: Original workflow built on the shared App file finder
(fly.ap.qt.find_files.model), Apache-2.0.
Requires App>=1.2.0 and fontlab-fly in FontLab 9 Python 3.11.

Run **Utilities > Find Font Files** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source identity

SHA256: `56f6ae7e336ac0bb220a9b7ed87631b1a52292237ad52216269ddcb483d1e529`

[Python source at `370bf9829bc1`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/370bf9829bc141c1c9f88be0018cbc285b502a5d/Scripts/Utilities/Find%20Font%20Files.py)
