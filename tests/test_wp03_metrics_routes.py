# this_file: tests/test_wp03_metrics_routes.py
# SPDX-License-Identifier: Apache-2.0
"""Retain original metrics action oracles on the callable App destinations.

The original UI tests remain until every mapped control has an equivalent tab.
These tests import production modules, never execute archived menu bodies.
"""

from types import SimpleNamespace as NS

import pytest
from _cov_a_support import Host
from test_cov_a_fontinfo import METRICS, MetricsPackage


@pytest.fixture
def host(monkeypatch, real_app):
    return Host(monkeypatch, real_app)


@pytest.fixture
def routes(host):
    loaded = host.real_app(
        qt=NS(QtCore=host.qt.QtCore, QtGui=host.qt.QtGui),
        fontlab=host.native,
        scripting={"current_package": lambda: host.package},
        modules=(
            "studios.vertical_metrics.calculate",
            "studios.vertical_metrics.table",
            "studios.spacing_studio.model",
        ),
    )
    return NS(**{name.rsplit(".", 1)[-1]: value for name, value in loaded.items()})


@pytest.mark.parametrize(
    ("values", "message"),
    [
        ([1, 2, 3], "finite metrics"),
        ([float("nan"), 0, 0, 0], "finite metrics"),
        ([800, -200, 500, 40000], "finite metrics"),
        ([800, 10, 500, 700], "Expected descender"),
        ([800, -200, 750, 700], "Expected descender"),
        ([600, -200, 500, 700], "Expected descender"),
    ],
)
def test_master_table_destination_refuses_original_invalid_rows(routes, values, message):
    with pytest.raises(ValueError, match=message):
        routes.table.validate_metrics(values)


def test_master_table_destination_keeps_alias_guard_stale_and_pending_oracles(routes, host):
    table = routes.table
    package = MetricsPackage(**METRICS)
    package.infos["Bold"].ascender = 820.0
    writes, guards = [], []

    def write(target, values, title):
        writes.append((values, title))
        for master, fields in values.items():
            for field, value in fields.items():
                setattr(target.infos[master], "capsHeight" if field == "capHeight" else field, value)
        return NS(pending_updates=(7,), pending_note="Dates may change (8537).")

    def guard(target):
        guards.append(list(target.switches))
        if refused[0]:
            raise ValueError("Activate the Font window")

    refused = [False]
    backend = NS(
        font_history=NS(require_font_window=guard),
        master_metrics=NS(
            FIELDS={field: field + "_value" for field in METRICS},
            ALIASES={"capHeight": "capsHeight"},
            write_master_metrics=write,
        ),
    )
    host.mp.setattr(table._shared, "backends", lambda: backend)
    before = table.master_values(package)
    assert before == [("Regular", [800, -200, 500, 700]), ("Bold", [820, -200, 500, 700])]
    assert package.master == "Regular"
    assert package.switches == [("Regular", False), ("Bold", False), ("Regular", False)]
    changes = table.plan(before, [("Regular", [810, -210, 510, 710])])
    package.switches.clear()
    refused[0] = True
    with pytest.raises(ValueError, match="Activate the Font window"):
        table.write_changes(package, changes, "Master Metrics Table")
    assert package.switches == [] and writes == []
    refused[0] = False
    result = table.write_changes(package, changes, "Master Metrics Table")
    assert guards[-1] == []
    assert result == {"changed": 4, "pending_updates": (7,), "pending_note": "Dates may change (8537)."}
    assert writes == [({"Regular": {"ascender": 810, "descender": -210, "xHeight": 510, "capHeight": 710}}, "Master Metrics Table")]
    assert package.infos["Regular"].capsHeight == 710
    with pytest.raises(ValueError, match="changed since preview"):
        table.write_changes(package, changes, "Master Metrics Table")
    assert len(writes) == 1


def test_calculate_destination_preserves_all_master_outward_rounding_and_groups(routes):
    calculate = routes.calculate
    package = MetricsPackage(**dict.fromkeys(calculate.METRIC_FIELDS, 0))
    bounds = {"Regular": (-210.5, 710.2, 1), "Bold": (-240.8, 780.1, 1)}
    fields = calculate.METRIC_FIELDS[3:]
    plan = calculate.metric_plan(package, bounds, package.masters, 10, 20, fields)
    assert set(plan) == {
        (master, field, 0, value)
        for master, values in {"Regular": (721, -221, 20, 721, 221), "Bold": (791, -251, 20, 791, 251)}.items()
        for field, value in zip(fields, values, strict=True)
    }
    assert package.master == "Regular"
    assert all(getattr(info, field) == 0 for info in package.infos.values() for field in calculate.METRIC_FIELDS)
    assert calculate.metric_plan(package, {}, package.masters, 10, 20, fields) == []


@pytest.mark.parametrize("bounds", [(1, -1, 0, 0), (0, 700, -1, 0), (0, 700, 2001, 0), (0, 700, 0, 32768), (float("nan"), 700, 0, 0)])
def test_calculate_destination_preserves_invalid_input_refusal(routes, bounds):
    with pytest.raises(ValueError):
        routes.calculate.enclosing_metrics(*bounds)


def test_spacing_destination_preserves_odd_width_and_negative_width_policies(routes):
    model = routes.model
    before = model.Metrics(40, 61, 501, 40, 440)
    assert model.equalize(before, "average") == model.Plan(10, 501, 50, 51, True)
    assert model.centred(before, "keep", 0) == model.Plan(10, 501, 50, 51, True)
    assert model.copied(before, (10, 20, 500), "width", 0) == model.Plan(0, 500, 40, 60, True)
    assert model.tune(before, "set", -1000, None) == model.NEGATIVE_NOTE
    assert model.tune(before, "add", None, 0) == model.Plan(0, 501, 40, 61, False)


def test_master_table_destination_discloses_write_when_refresh_fails(routes, host):
    """The original dialog never reports a completed write as just a refresh failure."""
    table = routes.table
    messages, writes = [], []

    def write(package, changes, title):
        writes.append(list(changes))
        return {"changed": 1, "pending_updates": (7,), "pending_note": "Dates may change (8537)."}

    def reload():
        raise ValueError("Activate the original font and reopen this tool.")

    host.mp.setattr(table, "write_changes", write)
    panel = object.__new__(table.MetricsTablePanel)
    panel.changes = [("Regular", "ascender", 800, 810)]
    panel.tool = NS(package=object(), reload=reload, say=messages.append)
    panel.apply()
    assert writes == [[("Regular", "ascender", 800, 810)]]
    assert "1 metric field" in messages[-1]
    assert "Dates may change (8537)." in messages[-1]
    assert "Activate the original font" in messages[-1]


def test_calculate_destination_discloses_write_when_refresh_fails(routes, host):
    calculate = routes.calculate
    messages, writes = [], []

    def write(package, plan, *, undo_name):
        writes.append(list(plan))
        return {"changed": 1}

    def reload():
        raise ValueError("Activate the original font and reopen this tool.")

    host.mp.setattr(calculate, "write_font_info", write)
    panel = object.__new__(calculate.CalculatePanel)
    panel.plan = [("Regular", "openTypeHheaAscender", 800, 810)]
    panel.tool = NS(package=NS(master="Regular"), current="Regular", reload=reload, say=messages.append)
    panel.apply()
    assert writes == [[("Regular", "openTypeHheaAscender", 800, 810)]]
    assert "1 metric field" in messages[-1]
    assert "Activate the original font" in messages[-1]
