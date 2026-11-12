# this_file: tests/test_wp03_spacing_window.py
# SPDX-License-Identifier: Apache-2.0
"""The consolidated Strings button opens the real editable TMetrics owner."""

from copy import deepcopy
from types import SimpleNamespace as NS


def test_strings_button_opens_editable_tmetrics_with_captured_font_and_owned_close(real_app, monkeypatch, app_sources):
    from PySide6 import QtCore, QtWidgets
    from fontlab_fontport.live import RFont
    from fontlab_fontport.memory import UFOBackend
    from ufoLib2 import Font

    application = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    monkeypatch.syspath_prepend(str(app_sources.parents[1] / "tests"))
    from _feature_source_qt import qt_namespace

    qt = qt_namespace()
    for name in dir(QtCore):
        if name.startswith("Q") and not hasattr(qt.QtGui, name):
            setattr(qt.QtGui, name, getattr(QtCore, name))
    loaded = real_app(
        qt=qt, fontlab=None,
        modules=("studios.spacing_studio.tabs",),
    )
    import fontlabapp.fontui as fontui

    source = Font()
    source.info.unitsPerEm = 1000
    for name, code in (("A", 65), ("V", 86)):
        glyph = source.newGlyph(name)
        glyph.unicodes = [code]
        glyph.width = 500
        pen = glyph.getPen()
        pen.moveTo((20, 0))
        pen.lineTo((480, 0))
        pen.lineTo((250, 700))
        pen.closePath()
    source.lib["preserve"] = {"nested": [1, 2, 3]}
    backend = UFOBackend(source)
    font = RFont(backend)
    captured = deepcopy(backend.font)
    studio = NS(shell=NS(embed=lambda grid: grid.widget), views=[], font=lambda: font,
                package=lambda: object(), say=lambda text: None)
    panel = loaded["studios.spacing_studio.tabs"].StringsTab(studio)
    panel.text_field.setText("AV")
    opened = []
    original = fontui.metrics_window

    def open_window(*args, **kwargs):
        owner = original(*args, **kwargs)
        opened.append((args, kwargs, owner))
        return owner

    monkeypatch.setattr(fontui, "metrics_window", open_window)
    button = next(button for button in panel.widget.findChildren(QtWidgets.QPushButton)
                  if button.text() == "Open TMetrics window")
    try:
        button.click()
        assert len(opened) == 1
        args, kwargs, owner = opened[0]
        assert args == (font, "AV") and kwargs == {"parent": None}
        assert owner.font is font and owner.widget.isVisible()
        assert not owner.read_only
        assert [cell.name for cell in owner.model.cells] == ["A", "V"], owner.diagnostic.text
        assert backend.font == captured, "Opening the standalone editor preserves every font field"
        owner.model.select(0)
        owner._show_selection()
        assert owner.commit("width", "650"), owner.diagnostic.text
        assert font["A"].width == 650 and font["V"].width == 500
        assert backend.font.lib == captured.lib
        owner.close()
        assert owner.closed and owner._close_complete
        assert not owner.connections
        assert not owner.widget.isVisible()
        assert owner._delete_scheduled and owner._close_error is None
    finally:
        for _, _, owner in opened:
            owner.close()
        panel.widget.deleteLater()
        application.processEvents()
        QtCore.QCoreApplication.sendPostedEvents(None, QtCore.QEvent.DeferredDelete)
