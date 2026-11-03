# this_file: Scripts/Reports/Event Log.py
# SPDX-License-Identifier: Apache-2.0
"""Print what happens in FontLab to the Output panel: font, window, glyph, layer, selection and edits.

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
"""

import os
import time
from typing import Any

from fly import ap, qt

fontlab = ap.fontlab
(QtCore, QtGui) = (qt.QtCore, qt.QtGui)
TITLE = "Event Log"
KEY = "report_event_log"
SETTLE_MS = 60
FIELDS = ("Font", "Window", "Glyph", "Layer", "Master", "Glyph selection", "Node selection")
# Notifications that may switch what is active: read the whole state afterwards.
STATE_SIGNALS = (
    "packageActivated",
    "currentProjectChanged",
    "viewportChanged",
    "canvasEnterFocus",
    "glyphActivated",
    "glyphDeactivated",
    "glyphWindowInactive",
    "signalFontPanelActivated",
    "fontSelectedID",
    "signalMasterActivated",
    "layerActivated",
    "signalLayerActivated",
    "glyphsSelectionChanged",
    "selectionChanged",
    "nodesSelected",
    "signalEditModeChanged",
    "textBlockItemActivated",
    "packageAdded",
    "signalPackageClosed",
    "signalAppActivated",
)


def text_of(value: Any) -> str:
    """A readable name for a native object: its name, title or class."""
    for attribute in ("name", "title", "toolName"):
        name = getattr(value, attribute, None)
        if isinstance(name, str) and name:
            return name
    return type(value).__name__


# Notifications printed as they come: name -> message from the signal arguments.
EVENT_SIGNALS = {
    "toolChanged": lambda *a: "Tool: " + (text_of(a[0]) if a else "?"),
    "historyIndexChanged": lambda *a: "Undo or redo",
    "historyChanged": lambda *a: "Edit recorded",
    "signalPackageSaved": lambda *a: "Font saved",
    "signalFontKerningChanged": lambda *a: "Kerning changed",
    "featuresChanged": lambda *a: "Features changed",
    "glyphMetricsChanged": lambda *a: "Metrics changed",
    "signalTablesChanged": lambda *a: "Font info changed"
    + (f": {a[1]}" if len(a) > 1 and a[1] else ""),
    "clipboardChanged": lambda *a: "Clipboard changed",
}


def read(getter: Any) -> str:
    """getter() as text, or '–' when FontLab has nothing to report."""
    try:
        value = getter()
    except Exception:  # noqa: BLE001 - a missing window or glyph is a normal state
        return "–"
    return "–" if value is None or value == "" else str(value)


def font_label() -> Any:
    """Family and style of the current font, with its file name."""
    package = fontlab.flWorkspace.instance().currentPackage
    if package is None or package.isNull:
        return None
    label = f"{package.info.familyName} {package.info.styleName}".strip()
    path = getattr(package, "path", "") or ""
    return f"{label} ({os.path.basename(path)})" if path else label


def window_label() -> Any:
    """Tab title and kind of the active document window(s)."""
    labels = []
    for tabs in QtGui.QApplication.instance().allWidgets():
        if tabs.className() != "YTabWidget" or not tabs.isVisible():
            continue
        page = tabs.currentWidget()
        kind = page.className() if page is not None else ""
        if kind.endswith("Window"):
            labels.append(f"{tabs.tabText(tabs.currentIndex).strip()} [{kind}]")
    return " | ".join(labels) or None


def snapshot(selection: dict) -> dict:
    """The current font, window, glyph, layer, master and selection as text."""
    package = fontlab.flWorkspace.instance().currentPackage
    return {
        "Font": read(font_label),
        "Window": read(window_label),
        "Glyph": read(lambda: fontlab.CurrentGlyph().name),
        "Layer": read(lambda: fontlab.CurrentGlyph().activeLayer.name),
        "Master": read(lambda: package.master),
        "Glyph selection": selection.get("glyphs", "–"),
        "Node selection": selection.get("nodes", "–"),
    }


def count(items: Any, names: bool = False) -> str:
    """'3' or '3: a, b, c' for a selection list from a signal argument."""
    total = len(items)
    if not names or not total:
        return str(total)
    shown = ", ".join(text_of(item) for item in list(items)[:5])
    return f"{total}: {shown}" + (", …" if total > 5 else "")


class EventLog(QtGui.QDialog):
    def __init__(self, parent: Any = None, emit: Any = print) -> None:
        """Connect the notifications and print the starting state."""
        QtGui.QDialog.__init__(self, parent)
        self.setWindowTitle(TITLE)
        self._connections = []
        self.emit, self.state, self.selection, self.last = emit, {}, {}, None
        root = QtGui.QVBoxLayout(self)
        self.status = QtGui.QLabel("Logging to the Output panel. Close to stop.")
        self.status.setWordWrap(True)
        root.addWidget(self.status)
        self.close_button = QtGui.QPushButton("Close")
        root.addWidget(self.close_button)
        self.timer = QtCore.QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.setInterval(SETTLE_MS)
        self._connect(self.timer.timeout, lambda *a: self.check())
        self._connect(self.close_button.clicked, lambda *a: self.close())
        items = fontlab.flItems.instance().qobject
        for name in STATE_SIGNALS:
            self._listen(items, name, self._state_changed(name))
        for name, message in EVENT_SIGNALS.items():
            self._listen(items, name, lambda *a, m=message: self.say(m(*a)))
        self.say(f"{TITLE} started")
        self.check()

    def _connect(self, signal: Any, slot: Any) -> None:
        """Connect through the shared guarded native lifecycle."""
        ap.scripting.connect_guarded(self, signal, slot)

    def _listen(self, items: Any, name: str, slot: Any) -> None:
        signal = getattr(items, name, None)
        if signal is not None:  # FontLab versions differ in what they announce
            self._connect(signal, slot)

    def _state_changed(self, name: str) -> Any:
        def slot(*args: Any) -> None:
            # Selection lists arrive with the notification; nothing else carries it.
            if name == "glyphsSelectionChanged" and args:
                self.selection["glyphs"] = count(args[0], names=True)
            elif name == "nodesSelected" and args:
                self.selection["nodes"] = count(args[0])
            self.timer.start()

        return slot

    def check(self) -> None:
        """Print each field that differs from the last state read."""
        state = snapshot(self.selection)
        for field in FIELDS:
            if state[field] != self.state.get(field):
                self.say(f"{field}: {state[field]}")
        self.state = state

    def say(self, text: str) -> None:
        """Print one timestamped line, skipping a repeat within the same second."""
        line = f"[{time.strftime('%H:%M:%S')}] {text}"
        if line != self.last:
            self.last = line
            self.emit(line)

    def closeEvent(self, event: Any) -> None:
        """Stop logging and release every connection."""
        self.say(f"{TITLE} stopped")
        ap.scripting.close_script_dialog(self, event, KEY, timers=(self.timer,))


def main() -> Any:
    """Show the logging panel; closing it stops the log."""
    return ap.scripting.show_script_dialog(EventLog, KEY)


if __name__ == "__main__":
    main()
