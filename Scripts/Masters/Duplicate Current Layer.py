# this_file: Scripts/Masters/Duplicate Current Layer.py
# SPDX-License-Identifier: Apache-2.0
"""Back up the current master layer or all master layers of selected glyphs.

What it does:
    Choose current or all masters, a custom suffix and inspect existing backups.
    Names use <master> backup <suffix>, with (2), (3) on collisions.
    Names with @, # or |temp|, exact master names, and names that Restore
    would read as another master are refused.

How it works:
    The non-modal panel uses fly.ap.selection_panel. Copies keep repaired shape
    and node metadata (fl#8516, fl#8538). The shown layer stays active. Each Apply
    is recorded as one Undo step through fly.ap.history and read back. Auto
    owners and bases are listed and kept. Pending native updates refuse Apply.

Why this design:
    FontLab's Layers panel duplicates one layer. This adds all-master backup,
    custom naming and an inventory before risky edits.

How to use:
    Select glyphs, open the panel, choose the scope and suffix, then Back up.

Benefit:
    Keep copies of several masters with one action before redesigning them.

Credit:
    Independent rewrite after Pedro Arilla's "Duplicate current layer"
    (Apache-2.0), extended from the author's own FontLab sample
    masters_backup_layer.py, Apache-2.0.
"""

from collections.abc import Collection, Sequence
from datetime import datetime
from time import monotonic
from typing import Any

TITLE = "Duplicate Current Layer"
STAMP_FORMAT = "%H:%M:%S, %d/%m/%y"
DEADLINE_SECONDS = 2.0
KEY = "masters_duplicate_current_layer"


def _backup_master(name: str, masters: Sequence[str]) -> str | None:
    """Resolve backups by the longest master prefix; keep legacy @ names.

    New names use <master> backup <suffix>, then optional collision (n).
    Exact master names, bracket names and temporary names are never backups.
    """
    if "#" in name or "|temp|" in name or name.casefold() in {m.casefold() for m in masters}:
        return None
    if "@" in name:
        prefix = name.split("@", 1)[0]
        return prefix if prefix in masters else None
    return next((m for m in sorted(masters, key=len, reverse=True) if name.startswith(m + " ")), None)


def backup_name(base: str, taken: Collection[str], stamp: str, masters: Sequence[str]) -> str:
    """Return a plain, case-insensitively unique backup name."""
    if not stamp.strip():
        raise ValueError("Enter a backup suffix.")
    candidate = f"{base} backup {stamp.strip()}"
    if "@" in candidate or "#" in candidate or "|temp|" in candidate:
        raise ValueError("Backup names must not contain @, # or |temp|.")
    used = {name.lower() for name in taken}
    name, number = candidate, 2
    while name.lower() in used:
        name = f"{candidate} ({number})"
        number += 1
    if name.casefold() in {master.casefold() for master in masters}:
        raise ValueError(f"Backup '{name}' is a font master name; choose another suffix.")
    resolved = _backup_master(name, masters)
    if resolved != base:
        raise ValueError(f"Backup '{name}' would read as master {resolved!r}, not {base!r}; choose another suffix.")
    return name


SELECTED = 0x0020  # node state bit: selected


def restore_shape(old: Any, new: Any, keep_view_state: bool, indexes: Sequence[int] | None = None) -> None:
    """Copy back what FontLab's clone() drops (fl#8516, fl#8538).

    Restore shape note and name, the raw state and name of every node, and,
    with `keep_view_state`, the active and selected flags of the shape. Without
    it, node selection bits stay as the clone has them. `indexes` picks the
    contours of `old` that `new` holds (default: all, in order).
    """
    new.shapeData.note, new.shapeData.name = old.shapeData.note, old.shapeData.name
    if keep_view_state:
        new.active, new.selected = old.active, old.selected
    contours = list(old.contours)
    if indexes is not None:
        contours = [contours[i] for i in indexes]
    for before, after in zip(contours, new.contours, strict=True):
        for source, target in zip(before.nodes(), after.nodes(), strict=True):
            if keep_view_state:
                target.nodeState = source.nodeState
            else:
                target.nodeState = (source.nodeState & ~SELECTED) | (target.nodeState & SELECTED)
            target.name = source.name


def plan(all_masters: bool = False, suffix: str | None = None) -> list[tuple[Any, Any, str]]:
    """Choose the new layer name of every selected layer. Return jobs.

    A job is (glyph, layer, new name). Raise ValueError before any change.
    """
    from fly.ap.layer_selection import capture
    from fly.ap.masters import associated_master
    from fly.ap.scripting import current_package

    selection = capture(monotonic() + DEADLINE_SECONDS)
    package = current_package()
    if package is None or not selection.occurrences:
        raise ValueError("Select a glyph first.")
    masters = tuple(str(name) for name in package.masters)
    stamp = suffix if suffix is not None else datetime.now().astimezone().strftime(STAMP_FORMAT)
    taken: dict[int, set[str]] = {}
    seen: set[tuple[int, int]] = set()
    jobs = []
    for item in selection.occurrences:
        if all_masters:
            continue
        key = (item.glyph_id, item.layer_id)
        if key in seen:
            continue
        seen.add(key)
        layer = item.layer
        if layer.isMaskLayer or layer.isService or layer.autoLayer:
            raise ValueError(
                f"Layer '{item.layer_name}' of '{item.glyph_name}' is a mask, service "
                "or automatic layer; select a body layer."
            )
        names = taken.setdefault(item.glyph_id, {str(x.name) for x in item.glyph.layers})
        base = associated_master(item.layer_name, masters) or _backup_master(item.layer_name, masters) or item.layer_name
        name = backup_name(base, names, stamp, masters)
        names.add(name)
        jobs.append((item.glyph, layer, name))
    if all_masters:
        glyphs = {item.glyph_id: item.glyph for item in selection.occurrences}
        for glyph in glyphs.values():
            names = {str(layer.name) for layer in glyph.layers}
            for master in masters:
                layer = glyph.findLayer(master)
                if layer is None or layer.isNull or layer.autoLayer or layer.isMaskLayer or layer.isService:
                    continue
                name = backup_name(master, names, stamp, masters)
                names.add(name)
                jobs.append((glyph, layer, name))
    return jobs


def backups_of(glyph: Any, masters: Sequence[str]) -> list[str]:
    """Inventory plain space-prefixed and old @ backups, excluding special layers."""
    return [str(layer.name) for layer in glyph.layers
            if not layer.isMaskLayer and not layer.isService and not layer.autoLayer
            and _backup_master(str(layer.name), masters) is not None]


def duplicate(jobs: Sequence[tuple[Any, Any, str]]) -> list[Any]:
    """Clone each layer, name the clone, add it to its glyph. One Undo step.

    The shared App history commit refuses the whole run before any change when
    FontLab has pending glyph updates, or when a glyph owns an automatic layer
    or is a base of one (also through manual composites).
    """
    import fly.ap.history as history  # noqa: PLR0402 - fontlabapp.__getattr__ is native
    from fly.ap.masters import associated_master
    from fly.ap.scripting import current_package

    if not jobs:
        return []
    masters = tuple(str(master) for master in current_package().masters)
    for _, layer, name in jobs:
        base = associated_master(str(layer.name), masters) or _backup_master(str(layer.name), masters)
        if base is None or not name.startswith(base + " backup "):
            raise ValueError(f"Backup '{name}' must use <master> backup <suffix>.")
        if "@" in name or "#" in name or "|temp|" in name or _backup_master(name, masters) != base:
            raise ValueError(f"Backup '{name}' does not resolve to its own master; choose another suffix.")
    active = [(glyph, glyph.updateActiveLayer(False)) for glyph, _, _ in jobs]

    def mutate() -> list[Any]:
        created = []
        for glyph, layer, name in jobs:
            clone = layer.clone()
            if len(clone.shapes) != len(layer.shapes):
                raise RuntimeError(f"FontLab clone changed the shape count of '{glyph.name}'.")
            for old, new in zip(layer.shapes, clone.shapes, strict=True):
                restore_shape(old, new, True)
            clone.name = name
            glyph.addLayer(clone)
            found = glyph.findLayer(name)
            if found is None or found.isNull:
                raise RuntimeError(f"FontLab did not add layer '{name}'.")
            glyph.bindDependencies()
            created.append(found)
        for glyph, shown in active:
            if shown is not None and not shown.isNull:
                shown.setActive()
        return created

    if not jobs:
        return []
    glyphs = list({int(glyph.id): glyph for glyph, _, _ in jobs}.values())
    facts = history.scan_auto_facts(current_package())
    def read_back() -> list[str]:
        missed = []
        for glyph, source, name in jobs:
            found = glyph.findLayer(name)
            if found is None or found.isNull or len(found.shapes) != len(source.shapes):
                missed.append(f"{glyph.name}: {name}")
        for glyph, shown in active:
            current = glyph.updateActiveLayer(False)
            if shown is not None and (current is None or current.id != shown.id):
                missed.append(f"{glyph.name}: active layer changed")
        return missed

    done = history.commit(TITLE, [], glyphs, mutate, operation="geometry", facts=facts, read_back=read_back)
    if done.mismatches:
        raise history.unstored_error(done.mismatches)
    return list(done.created)


def run() -> list[str]:
    """Plan, then duplicate. Return one message per new layer."""
    jobs = plan()
    duplicate(jobs)
    return [f"{glyph.name}: new layer '{name}'" for glyph, _, name in jobs]


def panel_type() -> type:
    """Use the shared non-modal selection panel with scope, suffix and inventory."""
    import fly.ap.history as history  # noqa: PLR0402
    import fly.ap.selection_panel as selection_panel  # noqa: PLR0402
    from fly import qt

    class BackupPanel(selection_panel.panel_type()):
        TITLE, KEY, ACTION = "Duplicate Current Layer", "masters_duplicate_current_layer", "Back up"
        HEADERS = ("Glyph · master", "Backup layer", "Status")
        CONSENT = ""
        ALIGN = False

        def build_controls(self) -> None:
            self.suffix = qt.QtGui.QLineEdit(datetime.now().astimezone().strftime(STAMP_FORMAT))
            self.add_row("Suffix", self.suffix)
            self.watch(self.suffix.editingFinished)

        def plan_rows(self, package: Any, masters: list[str]) -> list[Any]:
            facts = history.scan_auto_facts(package)
            rows = []
            for name in self.names:
                glyph = package.findName(name)
                if glyph is None or glyph.isNull:
                    continue
                taken = {str(layer.name) for layer in glyph.layers}
                reason = history.refusal(facts, name, "geometry")
                for master in masters:
                    layer = glyph.findLayer(master)
                    if layer is None or layer.isNull:
                        continue
                    new = backup_name(master, taken, self.suffix.text, list(package.masters))
                    taken.add(new)
                    note = reason or ("special layer, kept" if layer.autoLayer or layer.isMaskLayer or layer.isService else "")
                    rows.append((glyph, layer, new, note))
                rows.extend((glyph, None, old, "Existing backup") for old in backups_of(glyph, package.masters))
            return rows

        def is_ready(self, row: Any) -> bool:
            return row[1] is not None and not row[3]

        def cells(self, row: Any) -> list[str]:
            glyph, layer, name, note = row
            return [f"{glyph.name} · {layer.name}" if layer is not None else glyph.name, name, note or "New backup"]

        def write(self, package: Any, rows: list[Any]) -> dict[str, int]:
            created = duplicate([(g, layer, name) for g, layer, name, note in rows
                                 if layer is not None and not note])
            return {"layers": len(created)}

        def result_text(self, result: dict[str, int]) -> str:
            return f"Created {result['layers']} backup layer(s)"

    return BackupPanel


def main() -> Any:
    """Open the backup panel; print startup refusals."""
    import fly.ap.scripting as scripting  # noqa: PLR0402

    try:
        return scripting.show_script_dialog(panel_type(), KEY)
    except (ValueError, RuntimeError, TimeoutError) as error:
        print(f"{TITLE}: {error}")
        return None


if __name__ == "__main__":
    main()
