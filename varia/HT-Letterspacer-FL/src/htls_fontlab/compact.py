"""Compact manual-spacing palette, matching the original HT Letterspacer tool."""

import json
from PythonQt import QtCore, QtGui

from .qt import prop
from .service import Session, DEFAULTS

_window = None


class Window:
    def __init__(self):
        self.dialog = QtGui.QDialog()
        self.dialog.setWindowTitle("HT Letterspacer")
        self.dialog.setAttribute(QtCore.Qt.WA_QuitOnClose, False)
        self.dialog.setWindowFlags(QtCore.Qt.Tool | QtCore.Qt.WindowCloseButtonHint)
        layout = QtGui.QVBoxLayout(self.dialog)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(14)
        top = QtGui.QHBoxLayout()
        layout.addLayout(top)
        self.lsb = QtGui.QCheckBox("LSB")
        self.rsb = QtGui.QCheckBox("RSB")
        self.tabular = QtGui.QCheckBox("Tabular")
        self.lsb.setChecked(True)
        self.rsb.setChecked(True)
        for widget in (self.lsb, self.rsb, self.tabular):
            top.addWidget(widget)
        top.addStretch(1)
        self.width = self.number()
        self.width.setSpecialValueText("Auto")
        self.width.setToolTip(
            "Target advance width. Auto keeps each glyph’s current width."
        )
        self.width.setEnabled(False)
        top.addWidget(self.width)
        self.tabular.connect("toggled(bool)", self.width.setEnabled)
        grid = QtGui.QGridLayout()
        layout.addLayout(grid)
        self.params, self.saved = {}, {}
        for row, (key, title) in enumerate(
            (("paramArea", "Area"), ("paramDepth", "Depth"), ("paramOver", "Overshoot"))
        ):
            grid.addWidget(QtGui.QLabel(title), row, 0)
            saved = QtGui.QLabel()
            saved.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
            saved.setToolTip("Saved value for the current master")
            grid.addWidget(saved, row, 1)
            field = self.number()
            grid.addWidget(field, row, 2)
            self.saved[key], self.params[key] = saved, field
        grid.setColumnStretch(0, 1)
        grid.setHorizontalSpacing(18)
        grid.setVerticalSpacing(8)
        footer = QtGui.QHBoxLayout()
        layout.addLayout(footer)
        self.copy_button = QtGui.QPushButton("Copy Parameters")
        self.apply_button = QtGui.QPushButton("Apply")
        self.apply_button.setDefault(True)
        footer.addWidget(self.copy_button, 2)
        footer.addWidget(self.apply_button, 1)
        self.copy_button.connect("clicked()", lambda: self.safe(self.copy_parameters))
        self.apply_button.connect("clicked()", lambda: self.safe(self.apply))
        self.status = QtGui.QLabel()
        self.status.setWordWrap(True)
        self.status.hide()
        layout.addWidget(self.status)
        self.refresh_saved(seed=True)
        self.dialog.setFixedWidth(360)
        self.dialog.adjustSize()

    @staticmethod
    def number():
        widget = QtGui.QDoubleSpinBox()
        widget.setRange(0, 100000)
        widget.setDecimals(1)
        widget.setFixedWidth(82)
        widget.setButtonSymbols(QtGui.QAbstractSpinBox.NoButtons)
        return widget

    def safe(self, callback):
        try:
            callback()
        except Exception as exc:
            self.status.setText(str(exc))
            self.status.show()
            self.dialog.adjustSize()

    def refresh_saved(self, seed=False):
        session = Session.current()
        master = session.master()
        self.dialog.setToolTip("%s — %s" % (session.font.familyName, master.name))
        for key, label in self.saved.items():
            value = master.customParameters.get(key, DEFAULTS[key])
            label.setText("%g" % value)
            if seed:
                self.params[key].setValue(value)
        if seed:
            try:
                names = session.names()
                layer = session.font.glyphs[names[0]].layers[master.name]
                if layer is not None:
                    self.width.setValue(layer.width)
            except Exception:  # No selection is normal when opening the palette.
                pass
        return session

    def values(self):
        return {
            key: float(prop(widget, "value")) for key, widget in self.params.items()
        }

    def copy_parameters(self):
        # JSON is directly usable with the FontLab adapter's parameter API.
        QtGui.QApplication.clipboard().setText(json.dumps(self.values(), indent=2))
        self.status.setText("Parameters copied.")
        self.status.show()
        self.dialog.adjustSize()

    def apply(self):
        session = self.refresh_saved()
        results = session.apply(
            scope="selection",
            params=self.values(),
            manual={
                "LSB": bool(prop(self.lsb, "checked")),
                "RSB": bool(prop(self.rsb, "checked")),
                "tabular": bool(prop(self.tabular, "checked")),
                "width": float(prop(self.width, "value")),
            },
            preserve_components=True,
        )
        count = sum("after" in result for result in results)
        skipped = len(results) - count
        self.status.setText(
            "Applied to %d glyphs.%s"
            % (count, " Skipped %d." % skipped if skipped else "")
        )
        self.status.show()
        self.dialog.adjustSize()
        for result in results:
            if result.get("skip"):
                print("HTLS: %s — %s" % (result["name"], result["skip"]))


def show():
    global _window
    if _window is None:
        _window = Window()
    else:
        _window.status.hide()
        _window.safe(_window.refresh_saved)
        _window.dialog.adjustSize()
    _window.dialog.show()
    _window.dialog.raise_()
    _window.dialog.activateWindow()
    return _window
