# this_file: Scripts/Contours/Node Coordinates Panel.py
# SPDX-License-Identifier: Apache-2.0
"""Follow selected nodes as you edit; inspect coordinates, offsets and distances.

Open a glyph, run this script and select nodes. Both tables update every 400 ms.
Copy exports the displayed node coordinates as tab-separated lines. Contour
numbers start at one; node indices start at zero. Component contours are excluded.
The modeless panel reads the bound font only. Switching or closing that font
stops polling; reopen the tool to bind another font. No font data is written.
"""

from typing import Any

from fly import ap, qt
from fly.ap.scripting import current_package

QtCore, QtGui = qt.QtCore, qt.QtGui
api = ap.scripting.node_coordinates_api()
current_glyph, selected_nodes = api.current_glyph, api.selected_nodes
measures, number, own_contours = api.measures, api.number, api.own_contours
make_table = ap.scripting.masters_make_table
fill_table = ap.scripting.masters_fill_table
NamesDialog = ap.scripting.names_dialog_type()
TITLE, KEY, INTERVAL_MS = "Node Coordinates", "outlines_node_coordinates_panel", 400


class NodePanel(NamesDialog):
    """Retain original live controls with guarded Copy and owned timer cleanup."""

    ACTION = "Copy"

    def __init__(self, parent: Any = None) -> None:
        super().__init__(parent, TITLE, KEY)
        self.package, self._bound_id = None, None
        self._expired, self._closed = False, False
        self.signature, self.rows_data, self.glyph_name = None, [], None
        self.last_error = ""
        self.setMinimumWidth(440)
        self.nodes = make_table(["Contour : node", "x", "y", "Type"], 160)
        self.root.addWidget(self.nodes, 2)
        self.root.addWidget(QtGui.QLabel("Between consecutive selected nodes"))
        self.pairs = make_table(["From → to", "dx", "dy", "Distance", "Angle"], 100)
        self.root.addWidget(self.pairs, 1)
        footer = QtGui.QHBoxLayout()
        self.status = QtGui.QLabel()
        self.status.setWordWrap(True)
        footer.addWidget(self.status, 1)
        self.close_button, self.apply_button = (
            QtGui.QPushButton("Close"),
            QtGui.QPushButton("Copy"),
        )
        self.apply_button.setDefault(True)
        self.apply_button.setEnabled(False)
        footer.addWidget(self.close_button)
        footer.addWidget(self.apply_button)
        self.root.addLayout(footer)
        self.timer = QtCore.QTimer(self)
        self.timer.setInterval(INTERVAL_MS)
        self._connect(self.close_button.clicked, lambda *a: self.close())
        self._connect(self.apply_button.clicked, lambda *a: self.apply())
        self._connect(self.timer.timeout, lambda *a: self.tick())
        try:
            self.package = current_package()
            if self.package is None:
                raise ValueError("Open a font first, then reopen this tool.")
            self._bound_id = self.package.id
            self.timer.start()
            self.refresh()
        except Exception as error:  # noqa: BLE001 - Contain errors at the native UI boundary.
            if self._bound_id is None:
                self._expired, self.package = True, None
                self.timer.stop()
            self.show_error(error)

    def invalidate(self) -> None:
        """Clear partial/stale coordinates and Copy without discarding the timer."""
        self.signature, self.rows_data, self.last_result = None, [], None
        self._snapshot_valid = False
        for name in ("nodes", "pairs"):
            table = getattr(self, name, None)
            if table is not None:
                table.setRowCount(0)
        button = getattr(self, "apply_button", None)
        if button is not None:
            button.setEnabled(False)

    def show_error(self, error: Exception) -> None:
        """Contain native read/render/clipboard errors and remove obsolete values."""
        self.invalidate()
        self.last_error = f"{type(error).__name__}: {error}"
        self.status.setText(f"Paused: {self.last_error}")

    def snapshot(self) -> tuple:
        """Read only a fresh matching package; intended glyph/master edits are live."""
        if self._closed or self._expired:
            raise ValueError("Reopen this tool to bind a font.")
        package = current_package(self._bound_id)
        if package is None:
            self._expired, self.package = True, None
            self.timer.stop()
            raise ValueError("The font changed or closed; reopen this tool.")
        glyph, master = current_glyph(package), package.master
        layer = glyph.findLayer(master) if glyph is not None else None
        rows = selected_nodes(layer) if layer is not None else []
        if current_package(self._bound_id) is None:
            self._expired, self.package = True, None
            self.timer.stop()
            raise ValueError("The font changed during the read; reopen this tool.")
        return (glyph.name if glyph is not None else None, master, tuple(rows))

    def tick(self) -> None:
        """Poll through a contained slot; transient read failures can recover."""
        if self._closed or self._expired:
            return
        try:
            self.refresh()
        except Exception as error:  # noqa: BLE001 - Contain errors at the native UI boundary.
            self.show_error(error)

    def refresh(self) -> None:
        """Publish only after both complete tables render from one current read."""
        signature = self.snapshot()
        if signature == self.signature and tuple(self.rows_data) == signature[2]:
            return
        self.invalidate()
        name, master, raw = signature
        rows = list(raw)
        fill_table(
            self.nodes,
            [
                (f"{c + 1} : {n}", number(x), number(y), "on" if on else "handle")
                for c, n, x, y, on in rows
            ],
        )
        fill_table(
            self.pairs,
            [
                (label, number(dx), number(dy), f"{d:.1f}", f"{a:.1f}°")
                for label, dx, dy, d, a in measures(rows)
            ],
            lambda r, c, text: c == 3,
        )
        if self.snapshot() != signature:
            raise ValueError(
                "Selected nodes changed during display; wait for the next refresh."
            )
        self.subtitle.setText(
            f"{name} · {master} — select nodes in the Glyph window"
            if name is not None
            else "Open a glyph to see its selected nodes."
        )
        self.status.setText(
            f"{len(rows)} node{'s' if len(rows) != 1 else ''} selected · live, every {INTERVAL_MS} ms"
        )
        self.signature, self.rows_data, self.glyph_name = signature, rows, name
        self.last_error, self._snapshot_valid = "", True
        self.apply_button.setEnabled(bool(rows))

    def apply(self) -> None:
        """Copy the displayed snapshot only when it still matches the active nodes."""
        if self._closed:
            return
        try:
            current = self.snapshot()
            if (
                not self._snapshot_valid
                or current != self.signature
                or tuple(self.rows_data) != current[2]
            ):
                raise ValueError("Selected nodes changed; wait for the next refresh.")
            if not self.rows_data:
                return
            lines = [
                f"{c + 1}:{n}\t{number(x)}\t{number(y)}"
                for c, n, x, y, _ in self.rows_data
            ]
            QtGui.QApplication.clipboard().setText("\n".join(lines))
            self.last_result = {"copied": len(lines)}
            self.status.setText(f"Copied {len(lines)} lines")
        except Exception as error:  # noqa: BLE001 - Contain errors at the native UI boundary.
            self.show_error(error)

    def closeEvent(self, event: Any) -> None:
        """Stop polling, disconnect signals, release the font and destroy this panel."""
        self._closed, self.package, self._bound_id = True, None, None
        self.invalidate()
        ap.scripting.close_script_dialog(self, event, KEY, timers=(self.timer,))


def main() -> Any:
    """Show one owned modeless panel through the existing script registry."""
    return ap.scripting.show_script_dialog(NodePanel, KEY)


if __name__ == "__main__":
    main()
