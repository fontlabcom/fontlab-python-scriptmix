# this_file: tests/test_issue122_Z1.py
# SPDX-License-Identifier: Apache-2.0
"""Offline tests for Metrics > Alignment Zones and Guides > Suggest Zones From Overshoots.

The real App zone model (``alignment_zones``, ``zone_rows``, ``zone_data``,
``zone_editor``) and the real ``zone_native`` refusal types run on top of the
``_cov_a_support`` Qt and FontLab doubles; only ``zone_native.backend`` is a
recording double. These tests prove call order and messages, not native
FontLab writes, Undo or reopen.
"""

from __future__ import annotations

import runpy
from types import SimpleNamespace as NS
from typing import Any

import pytest
from _cov_a_support import ROOT, Host, host  # noqa: F401
from conftest import app_names_used, check_real_app_names

ZONES = "Metrics/Alignment Zones.py"
SUGGEST = "Guides/Suggest Zones From Overshoots.py"
MODULES = ("zone_data", "zone_rows", "alignment_zones", "zone_editor", "history", "font_history", "outline_extent", "zone_native")
#: (bottom, top) extents per glyph and master.
OUTLINES = {
    "Regular": {"H": (0, 700), "O": (-12, 712), "x": (0, 500), "o": (-10, 510)},
    "Bold": {"H": (0, 700), "O": (-15, 716), "x": (0, 520), "o": (-14, 534)},
}


def test_scripts_when_real_app_imported_then_every_used_name_exists():
    paths = [ROOT / "Scripts" / ZONES, ROOT / "Scripts" / SUGGEST, ROOT / "Scripts/Font Info/Master Metrics Table.py"]
    used = app_names_used(paths)
    assert {"fly.ap.zone_editor", "fly.ap.zone_native", "fly.ap.master_metrics"} <= set(used), f"scripts: expected App names, got {sorted(used)}"
    check_real_app_names(used)


# ---------------------------------------------------------------- Alignment Zones
def test_alignment_zones_main_when_run_then_shared_panel_gets_native_backend(host):
    shown: list = []
    marker = object()
    module = host.load(ZONES, modules=MODULES)
    host.mp.setattr(host.loaded["zone_native"], "backend", lambda package_id=None: (marker, package_id))
    host.mp.setattr(host.loaded["zone_editor"], "show", lambda backend: shown.append(backend) or "panel")
    assert module.main() == "panel", "alignment zones: main returns the shared panel"
    assert shown == [(marker, None)], f"alignment zones: one backend for the current font, got {shown}"


def test_alignment_zones_when_run_as_script_then_panel_opens(host):
    shown: list = []
    host.load(ZONES, modules=MODULES)
    host.mp.setattr(host.loaded["zone_editor"], "show", shown.append)
    runpy.run_path(str(ROOT / "Scripts" / ZONES), run_name="__main__")
    assert len(shown) == 1 and hasattr(shown[0], "apply"), f"alignment zones: __main__ opens the panel with a Backend, got {shown}"


# ---------------------------------------------------------------- doubles
IDENTITY = {f"m{i}{j}": (lambda value=float(i == j): value) for i in (1, 2, 3) for j in (1, 2, 3)}


def node(x: float, y: float, kind: str = "on") -> NS:
    """flNode double with the host kind predicates isOn/isCurve/isOff."""
    return NS(x=x, y=y, isOn=lambda: kind == "on", isCurve=lambda: kind == "curve", isOff=lambda: kind == "off")


class Layer:
    """flLayer double: one closed rectangle contour from ``bottom`` to ``top``.

    ``broken`` adds a segment with one cubic control, which the outline reader
    refuses. Its ``boundingBox`` fails the test: the cached box can be stale
    (fl#8575).
    """

    def __init__(self, bottom: float, top: float, null: bool = False, broken: bool = False) -> None:
        self.isNull = null
        corners = [(0.0, bottom), (100.0, bottom), (100.0, top), (0.0, top)]
        nodes = [node(x, y) for x, y in corners]
        if broken:
            nodes.insert(1, node(50.0, bottom - 10, "curve"))
        contour = NS(nodes=lambda: nodes, closed=True, isTT=False)
        self.shapes = [NS(contours=[contour], transform=NS(**IDENTITY))]

    @property
    def boundingBox(self) -> Any:
        raise AssertionError("measure must not read the cached boundingBox (fl#8575)")


class Package:
    """flPackage double: masters, glyph layers with boxes, and zones per master."""

    def __init__(self, outlines: dict, zones: dict, package_id: int = 21) -> None:
        self.id = package_id
        self.outlines = outlines
        self.zones = zones
        self.masters = list(outlines)
        self.master = self.masters[0]

    def findName(self, name: str) -> Any:
        if not any(name in glyphs for glyphs in self.outlines.values()):
            return None
        return NS(findLayer=lambda master: self.layer(name, master))

    def layer(self, name: str, master: str) -> Any:
        extent = self.outlines.get(master, {}).get(name)
        if extent is None:
            return None
        if extent == "null":
            return Layer(0, 0, null=True)
        return Layer(0, 700, broken=True) if extent == "broken" else Layer(*extent)


class Backend:
    """Recording ``zone_editor.Backend`` double over a ``Package``."""

    def __init__(self, host: Host, data: Any) -> None:
        self.host, self.data = host, data
        self.applied: list = []
        self.check_error: Exception | None = None
        self.apply_error: Exception | None = None
        self.wrong_result = False
        self.guarded, self.guard_error = 0, None
        self.checked_after_guard: list[int] = []
        self.capture_error: Exception | None = None

    def capture(self) -> Any:
        package = self.host.package
        if self.capture_error is not None:
            raise self.capture_error
        if package is None:
            raise ValueError("Open the font before you edit its zones.")
        z = self.data
        masters = []
        for name in package.masters:
            top, bottom = package.zones.get(name, ((), ()))
            masters.append(
                z.Master(
                    name, 500, 700,
                    z.Zones(
                        tuple(z.Zone(p, w, n, z.Origin(f"Top:{n}", b"")) for p, w, n in top),
                        tuple(z.Zone(p, w, n, z.Origin(f"Bottom:{n}", b"")) for p, w, n in bottom),
                    ),
                )
            )
        return z.Snapshot(package.id, package.master, tuple(masters))

    def check(self, snapshot: Any) -> None:
        self.checked_after_guard.append(self.guarded)
        if self.check_error is not None:
            raise self.check_error

    def apply(self, before: Any, changes: tuple) -> Any:
        self.applied.append(changes)
        if self.apply_error is not None:
            raise self.apply_error
        after = {change.master: change.after for change in changes}
        if self.wrong_result:
            after = {name: self.data.Zones() for name in after}
        package = self.host.package
        for name, zones in after.items():
            package.zones[name] = (
                tuple((z.position, z.width, z.name) for z in zones.top),
                tuple((z.position, z.width, z.name) for z in zones.bottom),
            )
        return self.data.Snapshot(
            before.package_id,
            before.current_master,
            tuple(self.data.Master(m.name, m.x_height, m.caps_height, after.get(m.name, m.zones)) for m in before.masters),
        )


def suggest_tool(host: Host) -> tuple[Any, Backend]:
    """Load the script over the real zone model with a recording backend."""
    module = host.load(SUGGEST, modules=MODULES)
    backend = Backend(host, host.loaded["zone_data"])
    host.mp.setattr(host.loaded["zone_native"], "backend", lambda package_id=None: backend)

    def guard(package: Any, native: Any = None) -> None:
        backend.guarded += 1
        if backend.guard_error is not None:
            raise backend.guard_error

    host.mp.setattr(host.loaded["font_history"], "require_font_window", guard)
    return module, backend


def open_font(host: Host, zones: dict | None = None, outlines: dict | None = None) -> Package:
    source = {m: dict(v) for m, v in (outlines or OUTLINES).items()}
    host.package = Package(source, zones if zones is not None else {"Regular": (((500, 12, "x-height"),), ((0, 15, "baseline"),))})
    return host.package


# ---------------------------------------------------------------- pure functions
@pytest.mark.parametrize(
    ("flat", "curved", "top", "expected"),
    [(700, 712.4, True, (700, 12)), (0.4, -12.6, False, (0, 13)), (500, 490, True, (500, 0)), (0, 3, False, (0, 0))],
)
def test_overshoot_zone_when_measured_then_edge_and_outward_width(host, flat, curved, top, expected):
    module, _ = suggest_tool(host)
    assert module.overshoot_zone(flat, curved, top) == expected, f"overshoot zone {flat}/{curved}/{top}"


def test_suggestions_when_all_glyphs_measured_then_three_zones_in_rule_order(host):
    module, _ = suggest_tool(host)
    found = module.suggestions(OUTLINES["Regular"])
    assert found == [
        module.Suggestion("baseline", False, 0, 12),
        module.Suggestion("x-height", True, 500, 10),
        module.Suggestion("caps", True, 700, 12),
    ], f"suggestions: baseline from H/O bottoms, x-height from x/o tops, caps from H/O tops, got {found}"
    assert module.missing(OUTLINES["Regular"]) == [], "suggestions: nothing is skipped"


def test_suggestions_when_a_glyph_is_missing_then_its_rules_are_skipped(host):
    module, _ = suggest_tool(host)
    extents = {"H": (0, 700), "O": None, "x": (0, 500), "o": (-10, 510)}
    assert [s.name for s in module.suggestions(extents)] == ["x-height"], "suggestions: no O, no baseline or caps zone"
    assert module.missing(extents) == ["baseline", "caps"], "missing: the skipped rules are named"


def test_merge_when_zone_at_same_position_then_replaced_keeping_name_and_identity(host):
    module, _ = suggest_tool(host)
    z = host.loaded["zone_data"]
    origin = z.Origin("Top:T: 500", b"")
    zones = z.Zones((z.Zone(500, 8, "T: 500", origin), z.Zone(700, 10, "cap")), (z.Zone(-250, 10, "desc"),))
    merged, replaced = module.merge(zones, [module.Suggestion("x-height", True, 500, 12)])
    assert replaced == [zones.top[0]], f"merge: the zone at 500 is replaced, got {replaced}"
    assert z.Zone(500, 12, "T: 500", origin) in merged.top, f"merge: name and origin kept, got {merged.top}"
    assert zones.top[1] in merged.top and merged.bottom == zones.bottom, "merge: other zones stay"


def test_merge_when_only_name_matches_then_that_zone_is_replaced(host):
    module, _ = suggest_tool(host)
    z = host.loaded["zone_data"]
    zones = z.Zones((z.Zone(690, 20, "caps", z.Origin("Top:caps", b"")),), ())
    merged, replaced = module.merge(zones, [module.Suggestion("caps", True, 700, 12)])
    assert replaced == [zones.top[0]] and merged.top == (z.Zone(700, 12, "caps", z.Origin("Top:caps", b"")),), f"merge: same name replaced, got {merged}"


def test_merge_when_nothing_matches_then_zone_is_added_without_identity(host):
    module, _ = suggest_tool(host)
    z = host.loaded["zone_data"]
    zones = z.Zones((), (z.Zone(-250, 10, "desc"),))
    merged, replaced = module.merge(zones, [module.Suggestion("baseline", False, 0, 12)])
    assert replaced == [None] and z.Zone(0, 12, "baseline") in merged.bottom, f"merge: a new bottom zone, got {merged}"


def test_merge_when_replaced_zone_has_no_name_then_new_name_and_no_identity(host):
    module, _ = suggest_tool(host)
    z = host.loaded["zone_data"]
    zones = z.Zones((z.Zone(500, 8, "", z.Origin("Top:", b"")),), ())
    merged, _ = module.merge(zones, [module.Suggestion("x-height", True, 500, 12)])
    assert merged.top == (z.Zone(500, 12, "x-height"),), f"merge: a renamed zone gets no source identity, got {merged.top}"


def test_merge_when_two_suggestions_share_a_position_then_one_zone_is_replaced_once(host):
    module, _ = suggest_tool(host)
    z = host.loaded["zone_data"]
    zones = z.Zones((z.Zone(500, 8, "T: 500", z.Origin("Top:T: 500", b"")),), ())
    proposed = [module.Suggestion("x-height", True, 500, 12), module.Suggestion("caps", True, 500, 14)]
    merged, replaced = module.merge(zones, proposed)
    assert len(merged.top) == 1 and merged.top[0].width == 14, f"merge: one zone at 500, got {merged.top}"
    assert replaced[0] == zones.top[0] and replaced[1].origin == zones.top[0].origin, "merge: the source zone is claimed once"


def test_measure_when_glyphs_missing_null_or_flat_then_none(host):
    module, _ = suggest_tool(host)
    package = Package({"Regular": {"H": (0, 700), "O": "null", "x": (3, 3)}}, {})
    assert module.measure(package, "Regular") == {"H": (0.0, 700.0), "O": None, "x": None, "o": None}, "measure: only positive heights count"


def test_measure_when_outline_unreadable_then_none_and_reason(host):
    module, _ = suggest_tool(host)
    package = Package({"Regular": {"H": "broken", "O": (-12, 712)}}, {})
    unreadable: dict = {}
    found = module.measure(package, "Regular", unreadable)
    assert found["H"] is None and found["O"] is not None, f"measure: only H is skipped, got {found}"
    assert list(unreadable) == ["H"] and "cubic" in unreadable["H"], f"measure: the reason is kept, got {unreadable}"
    assert module.measure(package, "Regular")["H"] is None, "measure: without a reason dict, still no extent and no error"


def test_panel_when_outline_unreadable_then_named_and_preview_still_shown(host):
    module, backend = suggest_tool(host)
    outlines = {"Regular": {"H": "broken", "O": (-12, 712), "x": (0, 500), "o": (-10, 510)}}
    open_font(host, outlines=outlines)
    dialog = module.Dialog(None)
    text = dialog.status.text
    assert "not measured: H in Regular (A segment needs" in text, f"panel: the unreadable glyph is named with its reason, got {text!r}"
    assert "baseline in Regular, caps in Regular" in text, f"panel: the rules it blocks are named, got {text!r}"
    assert dialog.apply_button.isEnabled(), f"panel: the preview of the other zones is usable, got {text!r}"
    dialog.apply_button.clicked.emit()
    assert backend.applied, f"panel: Apply still writes the measured zones, got {dialog.status.text!r}"


def test_measure_when_glyph_is_null_then_its_layers_are_not_read(host):
    module, _ = suggest_tool(host)
    package = Package({"Regular": {"H": (0, 700)}}, {})
    read: list = []
    package.findName = lambda name: NS(isNull=True, findLayer=read.append)
    assert set(module.measure(package, "Regular").values()) == {None}, "measure: a null glyph gives no extent"
    assert read == [], "measure: a null glyph's layers are never read"


def test_preview_row_when_new_or_replacing_then_signed_width_and_source(host):
    module, _ = suggest_tool(host)
    z = host.loaded["zone_data"]
    top = module.Suggestion("caps", True, 700, 12)
    assert module.preview_row("Bold", top, None) == ["Bold", "caps", 700, "+12", "nothing: added"], "preview row: new zone"
    bottom = module.Suggestion("baseline", False, 0, 15)
    assert module.preview_row("Bold", bottom, z.Zone(0, 10, "")) == ["Bold", "baseline", 0, "-15", "no name at 0, width 10"], "preview row: replaced zone"


# ---------------------------------------------------------------- panel
def test_panel_when_no_font_then_message_and_apply_off(host):
    module, _ = suggest_tool(host)
    dialog = module.Dialog(None)
    assert dialog.subtitle.text == "Open a font, then reopen this tool.", f"panel: no font, got {dialog.subtitle.text!r}"
    assert not dialog.apply_button.isEnabled() and dialog.table.rowCount == 0, "panel: nothing to apply"


def test_panel_when_opened_then_current_master_preview_and_apply_on(host):
    module, _ = suggest_tool(host)
    open_font(host)
    dialog = module.Dialog(None)
    assert [dialog.table.row_texts(r) for r in range(dialog.table.rowCount)] == [
        ["Regular", "baseline", "0", "-12", "baseline at 0, width 15"],
        ["Regular", "x-height", "500", "+10", "x-height at 500, width 12"],
        ["Regular", "caps", "700", "+12", "nothing: added"],
    ], "panel: one row per suggestion of the current master"
    assert dialog.status.text == "3 suggested zones", f"panel: status, got {dialog.status.text!r}"
    assert dialog.apply_button.isEnabled(), "panel: changed zones enable Apply"


def test_panel_when_apply_then_previewed_plan_written_once(host):
    module, backend = suggest_tool(host)
    package = open_font(host)
    dialog = module.Dialog(None)
    dialog.scope.setCurrentIndex(1)
    assert dialog.table.rowCount == 6, "panel: all masters preview both masters"
    dialog.apply_button.clicked.emit()
    (changes,) = backend.applied
    assert [c.master for c in changes] == ["Regular", "Bold"], f"apply: one batch in font order, got {changes}"
    assert package.zones["Bold"] == (((520, 14, "x-height"), (700, 16, "caps")), ((0, 15, "baseline"),)), f"apply: Bold zones, got {package.zones['Bold']}"
    assert dialog.last_result == {"masters": 2, "zones": 6}, f"apply: result, got {dialog.last_result}"
    assert dialog.status.text == "Wrote the zones of 2 masters", f"apply: status, got {dialog.status.text!r}"
    assert not dialog.apply_button.isEnabled(), "apply: the new preview matches the font"


def test_panel_when_zones_already_match_then_apply_off(host):
    module, _ = suggest_tool(host)
    open_font(host, zones={"Regular": (((700, 12, "caps"), (500, 10, "x-height")), ((0, 12, "baseline"),))})
    dialog = module.Dialog(None)
    assert dialog.status.text.endswith("the zones already match"), f"panel: no change, got {dialog.status.text!r}"
    assert not dialog.apply_button.isEnabled(), "panel: nothing to apply"


def test_panel_when_glyph_missing_then_status_names_skipped_rules(host):
    module, _ = suggest_tool(host)
    outlines = {"Regular": {"H": (0, 700), "x": (0, 500), "o": (-10, 510)}}
    open_font(host, outlines=outlines)
    dialog = module.Dialog(None)
    assert dialog.status.text == "1 suggested zone · not measured: baseline in Regular, caps in Regular", f"panel: skipped rules, got {dialog.status.text!r}"


def test_panel_when_glyphs_change_after_preview_then_apply_refused(host):
    module, backend = suggest_tool(host)
    package = open_font(host)
    dialog = module.Dialog(None)
    package.outlines["Regular"]["o"] = (-11, 511)
    dialog.apply_button.clicked.emit()
    assert backend.applied == [], "apply: a stale measurement writes nothing"
    assert dialog.status.text == "H, O, x or o changed since the preview; press Refresh.", f"apply: message, got {dialog.status.text!r}"
    dialog.refresh_button.clicked.emit()
    assert dialog.apply_button.isEnabled() and dialog.table.row_texts(1)[3] == "+11", "refresh: a new preview re-enables Apply"


def test_panel_when_zones_stale_then_refused_and_still_usable(host):
    module, backend = suggest_tool(host)
    open_font(host)
    dialog = module.Dialog(None)
    backend.check_error = ValueError(host.loaded["zone_native"].STALE_TEXT)
    dialog.apply_button.clicked.emit()
    assert backend.applied == [] and dialog.status.text == "The font, its masters or its zones changed; press Refresh.", f"apply: stale zones, got {dialog.status.text!r}"
    backend.check_error = None
    dialog.refresh_button.clicked.emit()
    assert dialog.apply_button.isEnabled(), "refresh: the panel stays usable"


@pytest.mark.parametrize("kind", ["row", "rolled"])
def test_panel_when_backend_refuses_unchanged_then_message_and_usable(host, kind):
    module, backend = suggest_tool(host)
    open_font(host)
    dialog = module.Dialog(None)
    native, history = host.loaded["zone_native"], host.loaded["font_history"]
    backend.apply_error = (
        native.RowRefusal("Zone names repeat in Top of 'Regular'.")
        if kind == "row"
        else history.RolledBackError("Alignment Zones", RuntimeError("write failed"), native.RESTORED_TEXT)
    )
    dialog.apply_button.clicked.emit()
    assert dialog.status.text == str(backend.apply_error), f"apply: the refusal text reaches the user, got {dialog.status.text!r}"
    assert dialog.apply_button.isEnabled() and dialog._preview_valid, "apply: the preview stays and Apply stays on"
    backend.apply_error = None
    dialog.apply_button.clicked.emit()
    assert len(backend.applied) == 2 and dialog.status.text == "Wrote the zones of 1 master", f"apply: a second Apply writes, got {dialog.status.text!r}"


@pytest.mark.parametrize("text", ["WINDOW_TEXT", "THREAD_TEXT", "STALE_TEXT"])
def test_panel_when_backend_raises_plain_refusal_then_unchanged_and_usable(host, text):
    module, backend = suggest_tool(host)
    open_font(host)
    dialog = module.Dialog(None)
    owner = host.loaded["zone_native"] if text == "STALE_TEXT" else host.loaded["font_history"]
    backend.apply_error = ValueError(getattr(owner, text))
    dialog.apply_button.clicked.emit()
    assert dialog.status.text == getattr(owner, text), f"apply {text}: the text reaches the user, got {dialog.status.text!r}"
    assert not dialog._locked and dialog._preview_valid and dialog.apply_button.isEnabled(), f"apply {text}: nothing was written; the panel stays usable"


def test_panel_when_window_guard_refuses_then_no_master_switch_or_write(host):
    module, backend = suggest_tool(host)
    open_font(host)
    dialog = module.Dialog(None)
    backend.guard_error = ValueError(host.loaded["font_history"].WINDOW_TEXT)
    backend.checked_after_guard.clear()
    dialog.apply_button.clicked.emit()
    assert backend.checked_after_guard == [] and backend.applied == [], "guard: check() (master switches) and apply never run"
    assert dialog.status.text == host.loaded["font_history"].WINDOW_TEXT and dialog.apply_button.isEnabled(), f"guard: message and usable, got {dialog.status.text!r}"
    backend.guard_error = None
    dialog.apply_button.clicked.emit()
    assert backend.checked_after_guard == [2], f"guard: runs before check(), got {backend.checked_after_guard}"


def test_panel_when_write_interrupted_then_locked_and_interrupt_raised(host):
    module, backend = suggest_tool(host)
    open_font(host)
    dialog = module.Dialog(None)
    backend.apply_error = KeyboardInterrupt()  # commit_masters re-raises it after its rollback
    with pytest.raises(KeyboardInterrupt):
        dialog.apply()
    assert dialog._locked and not dialog._preview_valid, "interrupt: the masters may be partly written; the panel locks"
    dialog.refresh_button.clicked.emit()
    assert dialog.status.text.startswith("Zones may be partly written"), f"interrupt: refresh refuses, got {dialog.status.text!r}"


def test_panel_when_refresh_fails_after_write_then_success_still_shown(host):
    module, backend = suggest_tool(host)
    open_font(host)
    dialog = module.Dialog(None)
    original = backend.apply

    def apply_then_break(before: Any, changes: tuple) -> Any:
        result = original(before, changes)
        backend.capture_error = ValueError("capture failed")
        return result

    backend.apply = apply_then_break
    dialog.apply_button.clicked.emit()
    assert dialog.last_result == {"masters": 1, "zones": 3}, f"apply: the write is recorded, got {dialog.last_result}"
    assert dialog.status.text == "Wrote the zones of 1 master; the new preview failed: capture failed", f"apply: both facts shown, got {dialog.status.text!r}"


@pytest.mark.parametrize("kind", ["unrestored", "foreign", "not-stored"])
def test_panel_when_write_outcome_unknown_then_message_and_locked(host, kind):
    module, backend = suggest_tool(host)
    open_font(host)
    dialog = module.Dialog(None)
    if kind == "unrestored":
        backend.apply_error = host.loaded["font_history"].UnrestoredError("Alignment Zones", [RuntimeError("restore failed")])
    elif kind == "not-stored":
        backend.apply_error = host.loaded["history"].unstored_error(["zones of master Regular"])
    else:
        backend.wrong_result = True
    dialog.apply_button.clicked.emit()
    assert dialog.status.text and "Wrote" not in dialog.status.text, f"apply: the failure is shown, got {dialog.status.text!r}"
    dialog.refresh_button.clicked.emit()
    assert dialog.status.text == "Zones may be partly written; check every master and reopen this tool.", f"refresh: locked, got {dialog.status.text!r}"
    assert not dialog.apply_button.isEnabled(), "locked: Apply stays off"


def test_panel_when_font_switched_then_apply_refused(host):
    module, backend = suggest_tool(host)
    open_font(host)
    dialog = module.Dialog(None)
    host.package = Package(OUTLINES, {}, package_id=99)
    dialog.apply_button.clicked.emit()
    assert backend.applied == [] and dialog.status.text == "Activate the original font and reopen this tool.", f"apply: other font, got {dialog.status.text!r}"


def test_suggest_main_when_run_as_script_then_window_opens(host):
    suggest_tool(host)
    open_font(host)
    runpy.run_path(str(ROOT / "Scripts" / SUGGEST), run_name="__main__")
    assert "zones_from_glyphs" in host.windows(), "suggest: __main__ opens the owned panel"
