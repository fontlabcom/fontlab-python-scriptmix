# this_file: tests/test_event_log.py
"""Drive Reports > Event Log through fake FontLab notifications."""

from types import SimpleNamespace as NS

import pytest
from _cov_b_support import ReportEnv, Signal, check_clean


@pytest.fixture
def log(monkeypatch, real_app, app_sources):
    """An open Event Log over a fake font, with its printed lines and signals."""
    env = ReportEnv(monkeypatch, real_app)
    env.package.info = NS(familyName="Sample Sans", styleName="Bold")
    env.package.path = "/fonts/Sample.vfj"
    module = env.load("Reports", "Event Log")
    monkeypatch.setattr(module.time, "strftime", lambda fmt: "12:00:00")
    names = module.STATE_SIGNALS + tuple(module.EVENT_SIGNALS)
    signals = {name: Signal() for name in names}
    env.fontlab.flItems = NS(instance=lambda: NS(qobject=NS(**signals)))
    lines = []
    dialog = module.EventLog(emit=lines.append)
    return NS(env=env, dialog=dialog, lines=lines, signals=signals, module=module)


def said(log, start=0):
    """Printed lines without their timestamps."""
    return [line.split("] ", 1)[1] for line in log.lines[start:]]


def test_event_log_when_opened_then_starting_state_is_printed(log):
    check_clean(log.dialog)
    assert said(log)[:3] == [
        "Event Log started",
        "Font: Sample Sans Bold (Sample.vfj)",
        "Window: –",
    ], said(log)
    assert "Master: Bold" in said(log), said(log)


def test_event_log_when_glyph_switches_then_only_changed_fields_print(log):
    start = len(log.lines)
    log.env.current_glyph = NS(name="A", activeLayer=NS(name="Bold"))
    log.signals["glyphActivated"].emit(NS())
    log.signals["layerActivated"].emit(NS())
    log.dialog.timer.timeout.emit()
    assert said(log, start) == ["Glyph: A", "Layer: Bold"], said(log, start)
    log.signals["glyphActivated"].emit(NS())
    log.dialog.timer.timeout.emit()
    assert len(log.lines) == start + 2, "an unchanged state prints nothing"
    check_clean(log.dialog)


def test_event_log_when_selection_arrives_then_counts_and_names_print(log):
    start = len(log.lines)
    log.signals["glyphsSelectionChanged"].emit([NS(name=n) for n in "ABCDEFG"], NS())
    log.signals["nodesSelected"].emit([NS(), NS()])
    log.dialog.timer.timeout.emit()
    assert said(log, start) == [
        "Glyph selection: 7: A, B, C, D, E, …",
        "Node selection: 2",
    ], said(log, start)


def test_event_log_when_actions_happen_then_lines_print_without_same_second_repeats(log):
    start = len(log.lines)
    log.signals["toolChanged"].emit(NS(name="Pen"))
    log.signals["toolChanged"].emit(NS(name="Pen"))
    log.signals["signalTablesChanged"].emit(NS(), "OS/2")
    log.signals["historyIndexChanged"].emit(3)
    assert said(log, start) == ["Tool: Pen", "Font info changed: OS/2", "Undo or redo"], said(log, start)


def test_event_log_when_closed_then_every_notification_is_released(log):
    log.dialog.close_button.clicked.emit()
    assert said(log)[-1] == "Event Log stopped", said(log)
    assert not any(signal.slots for signal in log.signals.values()), "Close must disconnect all"
    assert not log.dialog.timer.active, "Close stops the settle timer"
