# this_file: tests/_wp03_metrics_tabs.py
# SPDX-License-Identifier: Apache-2.0
"""Run actual Advance Widths panels over the original S1 native/Qt doubles."""

from types import SimpleNamespace as NS


def _shell(world, glyphs, selection):
    from test_issue122_S1 import Label, Package, Signal, Widget

    import fontlabapp.fontui as fontui
    from fontlabapp.fontui.appshell import AppShell
    from fontlabapp.studios._kerning_app import capture_source
    from fontlabapp.studios.advance_widths import widths

    class Grid:
        def __init__(self, *args, **kwargs):
            self.widget = Widget()
            self.row_selected = Signal()
            self.rows = []

        def set_rows(self, rows):
            self.rows = list(rows)

    world.package = None if glyphs is None else Package(glyphs)
    world.selection = [glyph.name for glyph in glyphs or []] if selection is None else selection
    world.font_names = [glyph.name for glyph in glyphs or []]
    world.mp.setattr(fontui, "glyph_table", Grid)

    def no_layer_selection():
        raise ValueError("No captured layer selection in this font-window fixture.")

    world.mp.setattr(widths._backends.tabular, "capture", no_layer_selection)
    status = Label()
    shell = NS(package=capture_source(lambda: world.package), status=status, set_status=status.setText, embed=lambda grid: grid.widget)
    def history(*args, **kwargs):
        world.commit_result = AppShell.history(shell, *args, **kwargs)
        return world.commit_result

    shell.history = history
    return shell


def advance_panel(world, name, glyphs, selection=None):
    from fontlabapp.studios._kerning import Tool
    from fontlabapp.studios.advance_widths import marks, rounding, tabular, widths

    tool = Tool(_shell(world, glyphs, selection), "Advance Widths", font=lambda: None)
    classes = {"Round Advances": rounding.RoundScalePanel, "Scale Advances": rounding.RoundScalePanel,
               "Zero-Width Marks": marks.MarksPanel, "Tabular Width": tabular.TabularPanel}
    panel = classes[name](tool)
    tool.reload()
    if name == "Scale Advances":
        panel.action.pick(1)
    return widths, panel


def spacing_panel(world, name, glyphs, selection=None):
    """Build the real spacing tab and session with the original native doubles."""
    from test_issue122_S1 import Combo, Label, Signal
    from PythonQt import QtGui
    from fontlabapp.studios.spacing_studio.session import Studio
    from fontlabapp.studios.spacing_studio.tabs import ItalicTab, ReferenceTab, SidebearingsTab

    class Field(Label):
        def __init__(self, parent=None):
            super().__init__("")
            self.placeholder = ""
            self.textChanged = Signal()

        def setText(self, text):
            super().setText(text)
            self.textChanged.emit(text)

        def setPlaceholderText(self, text):
            self.placeholder = text

        def setCompleter(self, completer):
            self.completer = completer

    class Choices(Combo):
        def addItems(self, items):
            self.items.extend(items)

        def clear(self):
            self.items.clear()
            self._index = 0

        def setCurrentIndex(self, index):
            self._index = index

        @property
        def currentText(self):
            return self.items[self._index] if self.items else ""

    world.mp.setattr(QtGui, "QLineEdit", Field, raising=False)
    world.mp.setattr(QtGui, "QComboBox", Choices)
    # Reuse the same real captured-source/history harness as Advance Widths.
    studio = Studio(_shell(world, glyphs, selection), font=lambda: None, selection=lambda: world.selection)
    tab_class = {"Italic Sidebearings": ItalicTab, "Copy Metrics From Reference": ReferenceTab}.get(name, SidebearingsTab)
    panel = tab_class(studio)
    studio.reload()
    if glyphs is not None:
        panel.use_selection()
    return studio, panel


def stage_panel(studio, panel):
    """Wire the real shell action machinery over inert native widget doubles."""
    from test_issue122_S1 import Button
    from fontlabapp.fontui.appshell import AppShell
    from fontlabapp.studios.spacing_studio.staged import Staged

    staged = Staged(panel)
    staged.action = next(getattr(panel, method) for method in ("centre", "apply", "copy") if hasattr(panel, method))
    shell = studio.shell
    shell.closed = False
    shell._actions = {}
    shell.tabs = NS(currentWidget=lambda: panel.widget)
    shell.refresh_button, shell.preview_button, shell.apply_button = Button(), Button(), Button()
    shell._update_actions = lambda: AppShell._update_actions(shell)
    AppShell.set_actions(shell, panel.widget, refresh=studio.reload,
                         preview=staged.preview, apply=staged.apply, ready=staged.ready)
    shell.run = lambda action: AppShell._run_action(shell, action)
    return staged, shell


def historical_text(path):
    """Resolve immutable historical menu bytes solely for source assertions."""
    import importlib.util
    import json

    root = path.parents[2]
    spec = importlib.util.spec_from_file_location("wp03_menu_layout", root / "menu_layout.py")
    resolver = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(resolver)
    rows = json.loads((root / "menu-consolidations.json").read_text())["transitions"]
    source = next(row["source"] for row in rows if row["source"]["path"] == path.relative_to(root).as_posix())
    return resolver.source_bytes(root, source).decode()


def spacing_writer(world, name, glyphs, selection=None):
    """Select an absorbed writer's actual tab action and unchanged control values."""
    studio, panel = spacing_panel(world, name, glyphs, selection)
    staged, shell = stage_panel(studio, panel)
    method = {"Equalize Sidebearings": "equalize", "Sidebearings Tuner": "tune",
              "Copy Metrics From Reference": "copy"}[name]
    staged.action = getattr(panel, method)
    if name == "Equalize Sidebearings":
        panel.rule.pick(1)
    elif name == "Sidebearings Tuner":
        panel.lsb_field.setText("5")
    else:
        panel.reference_field.setText("H")
    return studio, panel, staged, shell
