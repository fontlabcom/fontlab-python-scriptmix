---
this_file: docs/text-holder.md
---

# Text Holder

Open **Utilities > Text Holder** for an editable floating proof-text scratchpad.
The initial editor content is500×400; decorated frame limits are500×400..1200×800. It needs no open font. Type or paste
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
users saved text. Validation changes no global preferences, fonts, selection, history, Output or
system clipboard. User-invoked Copy/Cut retain normal clipboard behavior. There is no autosave of draft content.

App0.2.100.dev0 and Fly are required. The menus and editor are independently
implemented from Reza Bohlouls `Window/Text holder.py`; no licence declaration
was found, and no original body is redistributed or executed. Apache2.0 terms
for the new implementation remain in the repository licence files. Native
FontLab/PythonQt lifecycle and storage acceptance remains pending.

The initial500×400 dimensions are content size. The original native window
minimum500×400 and maximum1200×800 constrain the decorated frame; Qt client
limits subtract the measured frame extents after first show. The window-size
sidecar stores decorated frame dimensions and restoration subtracts those same
logical extents, preserving the original frame-based autosave semantics.

The original explicitly sets Cocoa frame origin(0,500) after frame recovery.
On first show the Qt position is(primary-screen.left, primary-screen.top +
primary-screen.height −500−current decorated frame.height). This uses full
logical screen geometry, with no available-area offset, DPR multiplication or
clamping of negative top positions. Raising/hiding/showing an existing window
retains its manually moved position; reopening reapplies the original placement.
FontLab primaryScreen is a null property binding in the known host; the known
safe QApplication.screens()[0] route supplies its primary screen geometry.
Final native qualification must verify the current host screen ordering and
actual decorated frame dimensions on the final combined artifact.

The window retains the original normal NSWindow role while floating above
normal windows: Qt.Window with WindowStaysOnTopHint, title/system/close and
minimize/maximize hints. It is not a Qt.Tool/NSPanel that hides on deactivation.
Actual native minimization, app deactivation and reactivation remain part of the
root-owned combined .100 qualification. No native result is claimed here.

Literal NBSP, Unicode line separator(U+2028) and paragraph separator(U+2029)
remain distinct from space and ordinary LF during editing, Find, replacement,
Save and recovery. Undo/Redo, typing, input-method commits and text paste/copy preserve
these literal characters as well.
As in the original Python open(...,'r'), disk loading translates CRLF and lone
CR to LF; this is separate from preserving literal text authored in the editor.
