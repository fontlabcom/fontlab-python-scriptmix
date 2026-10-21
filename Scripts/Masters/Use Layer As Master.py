# this_file: Scripts/Masters/Use Layer As Master.py
# SPDX-License-Identifier: Apache-2.0
"""Make a backup or alternate layer the master layer of its glyph.

What it does:
    Swap the roles of the shown layer and the master layer it belongs to. The
    shown layer becomes the master layer. The old master layer is kept as
    "<Master>@ HH:MM:SS, DD/MM/YY". Backgrounds (mask layers) travel with their
    layers: the background of the chosen layer becomes the master background.

How it works:
    FontLab decides by layer name which layer is the master layer of a master
    (see "Display Next Layer"). So the script only renames. It renames the old
    master layer to the backup name, then the chosen layer to the master name,
    and renames their mask layers to match the FontLab mask-name rule
    ("mask.<layer name>", or plain "mask" for the layer of a single-master font).
    Shapes, anchors, guides and metrics stay in the layer objects. Nothing is
    cloned, so nothing is lost. One notification covers all layers: one Undo step.

Why this design:
    - Renaming keeps every property of both layers. The Glyphs original must copy
      paths, components, anchors and sidebearing keys one by one.
    - Names are simulated before the first rename. A clash stops the run early.
    - If a rename fails, the script puts the old names back.
    - Locked, mask, service, automatic and image layers are refused. So is a
      glyph that is a base of an automatic layer: FontLab cannot undo it.

How to use:
    Show a backup layer (see "Display Next Layer"). Run the script. Check
    compatibility with the other masters afterwards: a swapped layer can have
    a different point structure.

Benefit:
    Restore an earlier state of a master in one step and keep the current one.

Credit:
    Behaviour after Pedro Arilla's Glyphs script "Use layer as master"
    (Apache-2.0). Independent rewrite. No source code was copied.
"""

from collections.abc import Callable, Collection, Sequence
from datetime import datetime
from time import monotonic
from typing import Any

TITLE = "Use Layer As Master"
STAMP_FORMAT = "%H:%M:%S, %d/%m/%y"
DEADLINE_SECONDS = 2.0


def associated_master(name: str, masters: Sequence[str]) -> str | None:
    """Return the master a layer name belongs to (text before "@" or "#")."""
    base = name.removeprefix("|temp|")
    cut = base.find("@")
    if cut < 0:
        cut = base.find("#")
    head = base if cut < 0 else base[:cut]
    return head if head and head in masters else None


def mask_name_for(layer_name: str, masters: Sequence[str]) -> str:
    """Return the mask layer name FontLab expects for a body layer name.

    A single-master font keeps the mask of its master layer as plain "mask".
    Every other layer uses "mask.<layer name>".
    """
    if len(masters) == 1 and layer_name.lower() == masters[0].lower():
        return "mask"
    return f"mask.{layer_name}"


def plan_swap(
    master: str,
    chosen: str,
    taken: Collection[str],
    stamp: str,
    masters: Sequence[str],
    masks: tuple[bool, bool],
) -> list[tuple[str, str, str]]:
    """Return renames [(role, old name, new name)] in a safe order.

    `master` is the master layer name, `chosen` the layer to promote, `taken`
    all layer names of the glyph, `masks` tells if (master, chosen) own a mask.
    Raise ValueError when a new name would clash. Names are compared without case.
    """
    used = {name.lower() for name in taken}
    backup = f"{master}@ {stamp}"
    number = 2
    while backup.lower() in used or mask_name_for(backup, masters).lower() in used:
        backup = f"{master}@ {stamp} ({number})"
        number += 1
    steps = []
    if masks[0]:
        steps.append(("master mask", mask_name_for(master, masters), mask_name_for(backup, masters)))
    steps.append(("master", master, backup))
    if masks[1]:
        steps.append(("chosen mask", mask_name_for(chosen, masters), mask_name_for(master, masters)))
    steps.append(("chosen", chosen, master))
    for role, old, new in steps:
        used.discard(old.lower())
        if new.lower() in used:
            raise ValueError(f"The {role} cannot take the name '{new}': it is in use.")
        used.add(new.lower())
    return steps


def require_no_auto_dependants(package: Any, glyphs: Sequence[Any]) -> None:
    """Refuse when a glyph is, or is a base of, an automatic layer.

    A notification that reaches an automatic layer makes FontLab rebuild every
    automatic glyph of the font. Use the shared App dependency reader.
    """
    from fly.ap.guides import affected_auto_layers, dependency_values

    blocked = affected_auto_layers(
        dependency_values(package), {str(glyph.name) for glyph in glyphs}
    )
    if blocked:
        raise ValueError(
            "FontLab cannot undo changes to automatic layers: " + ", ".join(blocked)
            + ". Choose glyphs that are no base of an automatic layer."
        )


def commit(
    title: str, layers: Sequence[Any], glyphs: Sequence[Any], mutate: Callable[[], Sequence[Any]]
) -> Sequence[Any]:
    """Run `mutate` inside one FontLab history step.

    `layers` and `glyphs` exist before the change. `mutate` returns new objects.
    One notification lists changed layers, new layers, then glyphs. Glyph dates
    get one shared stamp. Raise RuntimeError if anything failed.
    """
    from fly import ap, qt

    native = ap.fontlab
    if tuple(native.flGlyph.updatedFgGlyphs()):
        raise ValueError("FontLab has pending glyph updates; finish the open edit first.")
    for item in (*layers, *glyphs):
        item.checkInitHistoryState(0)
    stamp = qt.QtCore.QDateTime.currentDateTimeUtc()
    errors: list[str] = []
    created: Sequence[Any] = ()
    try:
        created = mutate()
    except Exception as error:  # noqa: BLE001 - finish history even after a failure
        errors.append(str(error))
    for owner in glyphs:
        try:
            owner.lastModified = stamp
        except Exception as error:  # noqa: BLE001
            errors.append(f"date: {error}")
    try:
        native.flItems().notifyChangesApplied(title, [*layers, *created, *glyphs])
    except Exception as error:  # noqa: BLE001
        errors.append(f"notification: {error}")
    for owner in glyphs:
        try:
            owner.lastModified = stamp
        except Exception as error:  # noqa: BLE001
            errors.append(f"date: {error}")
    if errors:
        raise RuntimeError(
            f"{title} failed: {'; '.join(errors)}. Native changes may remain; use Edit > Undo."
        )
    return created


def _valid(layer: Any) -> bool:
    """True for a real native layer object."""
    return layer is not None and not layer.isNull and layer.isValid


def _mask_of(layer: Any, masters: Sequence[str]) -> Any | None:
    """Return the mask layer of a body layer, or None. Never create one.

    Raise ValueError if the mask name does not follow the FontLab rule.
    """
    mask = layer.getMaskLayer(False)
    if not _valid(mask):
        return None
    expected = mask_name_for(str(layer.name), masters)
    if str(mask.name).lower() != expected.lower():
        raise ValueError(
            f"The background of '{layer.name}' is named '{mask.name}', not '{expected}'."
        )
    return mask


def plan() -> list[dict[str, Any]]:
    """Check every selected layer and plan its swap. Raise before any change."""
    from fly.ap.layer_selection import capture
    from fly.ap.scripting import current_package

    selection = capture(monotonic() + DEADLINE_SECONDS)
    package = current_package()
    if package is None or not selection.occurrences:
        raise ValueError("Select a glyph first.")
    masters = tuple(str(name) for name in package.masters)
    stamp = datetime.now().astimezone().strftime(STAMP_FORMAT)
    jobs, seen = [], set()
    for item in selection.occurrences:
        if item.glyph_id in seen:
            raise ValueError(f"'{item.glyph_name}' is selected twice; select it once.")
        seen.add(item.glyph_id)
        master = associated_master(item.layer_name, masters)
        if master is None:
            raise ValueError(f"Layer '{item.layer_name}' of '{item.glyph_name}' belongs to no master.")
        if item.layer_name == master:
            raise ValueError(f"Layer '{item.layer_name}' of '{item.glyph_name}' is already the master layer.")
        chosen, old = item.layer, item.glyph.findLayer(master)
        if not _valid(old):
            raise ValueError(f"'{item.glyph_name}' has no master layer '{master}'.")
        for layer in (chosen, old):
            if layer.isMaskLayer or layer.isService or layer.autoLayer or layer.isLocked:
                raise ValueError(
                    f"Layer '{layer.name}' of '{item.glyph_name}' is locked, automatic, "
                    "a mask or a service layer."
                )
            if _valid(layer.getImgLayer(False)):
                raise ValueError(f"Layer '{layer.name}' has an image layer; not supported.")
        old_mask, new_mask = _mask_of(old, masters), _mask_of(chosen, masters)
        steps = plan_swap(
            master,
            item.layer_name,
            [str(x.name) for x in item.glyph.layers],
            stamp,
            masters,
            (old_mask is not None, new_mask is not None),
        )
        targets = {"master": old, "chosen": chosen, "master mask": old_mask, "chosen mask": new_mask}
        jobs.append({"glyph": item.glyph, "steps": steps, "targets": targets})
    require_no_auto_dependants(package, [job["glyph"] for job in jobs])
    return jobs


def apply_renames(jobs: Sequence[dict[str, Any]]) -> None:
    """Rename all planned layers in one history step. Restore names on failure."""
    layers = [t for job in jobs for t in job["targets"].values() if t is not None]
    glyphs = [job["glyph"] for job in jobs]

    def mutate() -> Sequence[Any]:
        done: list[tuple[Any, str]] = []
        try:
            for job in jobs:
                for role, old, new in job["steps"]:
                    layer = job["targets"][role]
                    layer.name = new
                    done.append((layer, old))
                    if str(layer.name) != new:
                        raise RuntimeError(f"FontLab kept the name '{layer.name}' instead of '{new}'.")
        except Exception:
            for layer, old in reversed(done):
                layer.name = old
            raise
        return ()

    commit(TITLE, layers, glyphs, mutate)


def run() -> list[str]:
    """Plan all swaps, then apply them. Return one message per glyph."""
    jobs = plan()
    apply_renames(jobs)
    return [
        f"{job['glyph'].name}: '{job['steps'][-1][1]}' is now the master layer"
        for job in jobs
    ]


def main() -> None:
    """Menu entry. Print each result or the reason for a refusal."""
    try:
        for line in run():
            print(f"{TITLE}: {line}")
    except (ValueError, RuntimeError, TimeoutError) as error:
        print(f"{TITLE}: {error}")


if __name__ == "__main__":
    main()
