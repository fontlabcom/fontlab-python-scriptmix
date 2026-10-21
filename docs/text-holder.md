---
this_file: docs/text-holder.md
---

# Text Holder

Open **Utilities > Text Holder** for an editable floating proof-text scratchpad.
The window resizes from500×400 to1200×800. It needs no open font. Type or paste
plain text. **Find** highlights the first case-sensitive literal match from the
start, preserving text and the previous selection when no match exists.
**Find & Replace** replaces every literal match inside the selected range; with
no selection it replaces matches throughout the document. An empty Find field
changes nothing. Empty replacement deletes matches. Unicode cursor ranges use
Qt UTF16 units; emoji prefixes and non-BMP selections are handled explicitly.

**Save** writes the current text and keeps the editor open. **Save & Close**
saves first and closes only after success. **Ignore & Close**, Escape and the
window close button discard only unsaved edits. Reopen to recover the last saved
text. The window size persists separately, including when text is ignored.
Unsuccessful saving retains the draft and the previous saved file, with an
error in the window. An unreadable saved text file refuses opening rather than
presenting a blank editor that could silently overwrite it.

The default file is `Text holder.txt` in Qt application-specific data storage
for FontLab, with a `Text holder.window.json` size sidecar. The directory is only
created by an explicit Save or window-size save on Close. Tests and native
qualification must pass an explicit owned temporary path to App show(path=...),
or inject the default location into an owned directory. No validation uses the
users saved text. No global preferences, fonts, selection, history, Output or
clipboard are changed by the tool. There is no autosave of draft content.

App0.2.91.dev0 and Fly are required. The menus and editor are independently
implemented from Reza Bohlouls `Window/Text holder.py`; no licence declaration
was found, and no original body is redistributed or executed. Apache2.0 terms
for the new implementation remain in the repository licence files. Native
FontLab/PythonQt lifecycle and storage acceptance remains pending.
