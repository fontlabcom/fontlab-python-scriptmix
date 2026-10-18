# this_file: tests/test_additional_audit_menus.py
# SPDX-License-Identifier: Apache-2.0
"""Exercise additional menu routes through real App factories and lifecycle."""

import importlib
import importlib.util
import runpy
import sys
from pathlib import Path
from types import ModuleType
from types import SimpleNamespace as NS

import pytest
from conftest import resolve_app_sources
from test_proof import Color, Signal, Widget

ROOT = Path(__file__).resolve().parents[1]
CASES = [
    ("Kerning/Persistence Audit.py", "kerning_persistence_dialog_type", "kerning_persistence_audit"),
    ("Reports/Compare Open Font Revisions.py", "revision_compare_dialog_type", "compare_open_font_revisions"),
]


@pytest.mark.parametrize("relative,factory,key", CASES)
def test_menu_headers_and_one_category_depth(relative, factory, key):
    path = ROOT / "Scripts" / relative
    assert path.is_file(), f"Missing additional tool: {relative}"
    lines = path.read_text().splitlines()
    category, title = Path(relative).parts
    assert lines[0] == f"#FLM: {category} · {Path(title).stem}"
    assert f"# this_file: Scripts/{relative}" in lines[:5]
    assert len(path.relative_to(ROOT).parts) == 3


@pytest.fixture
def shared(monkeypatch):
    source = resolve_app_sources(
        ("scripting", "kerning_persistence", "_kerning_persistence_dialog", "revision_compare", "_revision_compare_dialog", "_names_dialog", "_proof_dialog")
    )
    prior_names = {name for name in sys.modules if name == "fontlabapp" or name.startswith("fontlabapp.")}
    for name in prior_names:
        monkeypatch.delitem(sys.modules, name)

    class HostWidget(Widget):
        def __init__(self, *args):
            super().__init__(*args)
            self.currentIndex = -1
            self.itemSelectionChanged = Signal()
            self.destroyed = Signal()
            self.host_show_count = self.host_raise_count = 0

        def deleteLater(self):
            super().deleteLater()
            self.destroyed.emit()

        def addItems(self, values):
            self.items.extend(values)
            if self.items and self.currentIndex < 0:
                self.currentIndex = 0

        def verticalHeader(self):
            return self

        def horizontalHeader(self):
            return self

        def show(self):
            self.host_show_count += 1

        def raise_(self):
            self.host_raise_count += 1

    gui = NS(**{name: HostWidget for name in ("QDialog", "QWidget", "QVBoxLayout", "QHBoxLayout", "QGridLayout", "QLabel", "QLineEdit", "QComboBox", "QPlainTextEdit", "QPushButton", "QTableWidget")})
    gui.QColor = Color
    gui.QPalette = NS(Text=1, WindowText=2)
    gui.QAbstractItemView = NS(NoEditTriggers=1, SelectRows=2, NoSelection=3)
    gui.QHeaderView = NS(ResizeToContents=1)
    qt = NS(QtCore=NS(Qt=NS(ScrollBarAlwaysOff=0, ToolTipRole=3)), QtGui=gui)
    parent = HostWidget()
    native = NS(MainWindow=lambda: parent, flWorkspace=NS(instance=lambda: NS(currentPackage=None, packages=list)))
    package = ModuleType("fontlabapp")
    package.__path__ = [str(source)]
    package._native = {"PythonQt": qt, "fontlab": native}.__getitem__
    monkeypatch.setitem(sys.modules, "fontlabapp", package)
    scripting = importlib.import_module("fontlabapp.scripting")
    assert Path(scripting.__file__).parent == source
    fly, ap = ModuleType("fly"), ModuleType("fly.ap")
    fly.__path__, ap.__path__ = [], []
    fly.ap, ap.scripting = ap, scripting
    for name, module in (("fly", fly), ("fly.ap", ap), ("fly.ap.scripting", scripting)):
        monkeypatch.setitem(sys.modules, name, module)
    monkeypatch.setattr(sys, "_fontlab_samples", {}, raising=False)

    def load(relative):
        spec = importlib.util.spec_from_file_location("additional_menu_" + Path(relative).stem.replace(" ", "_"), ROOT / "Scripts" / relative)
        menu = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(menu)
        return menu

    yield NS(load=load, scripting=scripting, source=source, parent=parent, host_widget=HostWidget)
    for dialog in list(sys._fontlab_samples.values()):
        if isinstance(dialog, HostWidget) and not dialog.deleted:
            HostWidget.close(dialog)
    for name in list(sys.modules):
        if name.startswith("fontlabapp.") and name not in prior_names:
            sys.modules.pop(name)


@pytest.mark.parametrize("relative,factory,key", CASES)
def test_real_factory_no_font_panel_and_shared_owned_close(shared, relative, factory, key):
    menu = shared.load(relative)
    assert not sys._fontlab_samples, "Importing a menu must not create its panel"
    dialog = menu.main()
    actual_type = getattr(shared.scripting, factory)()
    assert type(dialog) is actual_type
    assert Path(sys.modules[actual_type.__module__].__file__).parent == shared.source
    assert menu.KEY == dialog.KEY == key and sys._fontlab_samples[key] is dialog
    assert dialog.host_show_count == dialog.host_raise_count == 1 and dialog.close_button
    assert "font" in dialog.status.text.lower()
    connections = list(dialog._connections)
    assert connections, "The actual App panel must own its signal connections"
    dialog.close_button.clicked.emit()
    assert dialog.deleted and not dialog._connections and key not in sys._fontlab_samples
    assert all(slot not in signal.slots for signal, slot in connections)


def test_two_keys_and_repeat_launch_replace_only_the_owned_panel(shared):
    first = shared.load(CASES[0][0])
    second = shared.load(CASES[1][0])
    old, other = first.main(), second.main()
    replacement = first.main()
    assert replacement is not old and old.deleted and not old._connections
    assert sys._fontlab_samples[first.KEY] is replacement
    assert sys._fontlab_samples[second.KEY] is other and not other.deleted


@pytest.mark.parametrize("relative,factory,key", CASES)
def test_native_destruction_signal_drops_registry_and_late_owned_slots(
    shared, relative, factory, key
):
    dialog = shared.load(relative).main()
    slots = [slot for signal, slot in dialog._connections if signal is not dialog.destroyed]
    dialog.deleteLater()
    assert dialog._closed and dialog.deleted and key not in sys._fontlab_samples
    assert not dialog._connections
    assert not dialog._disconnect_errors, "Native-shaped destruction must disconnect every owned callback"
    for slot in slots:
        slot()
    assert not dialog.rows, "A retained callback must not refresh a destroyed panel"


@pytest.mark.parametrize("relative,factory,key", CASES)
def test_refused_close_retains_original_owner(shared, monkeypatch, relative, factory, key):
    menu = shared.load(relative)
    old = menu.main()
    connections = list(old._connections)
    monkeypatch.setattr(old, "close", lambda: False)
    assert menu.main() is old and sys._fontlab_samples[key] is old
    assert not old.deleted and old._connections == connections
    assert old.host_show_count == old.host_raise_count == 2


@pytest.mark.parametrize("relative,factory,key", CASES)
def test_factory_failure_propagates_without_registering_a_partial_panel(shared, monkeypatch, relative, factory, key):
    menu = shared.load(relative)
    owner = object()
    sys._fontlab_samples["unrelated"] = owner

    def fail():
        raise RuntimeError("owned factory failure")

    monkeypatch.setattr(menu, factory, fail)
    with pytest.raises(RuntimeError, match="owned factory failure"):
        menu.main()
    assert sys._fontlab_samples == {"unrelated": owner}


@pytest.mark.parametrize("relative,factory,key", CASES)
def test_main_execution_uses_the_same_real_factory_and_registry(shared, relative, factory, key):
    runpy.run_path(str(ROOT / "Scripts" / relative), run_name="__main__")
    dialog = sys._fontlab_samples[key]
    assert type(dialog) is getattr(shared.scripting, factory)()
    assert dialog.host_show_count == dialog.host_raise_count == 1
