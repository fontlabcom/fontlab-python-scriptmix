# this_file: Scripts/Kerning/Unbundle Punctuation Kerning.py
# SPDX-License-Identifier: MIT
"""Materialize glyph-pair exceptions for selected punctuation across masters.

What: Turn inherited values involving the selection into explicit glyph pairs.
How: Expand affected class records, resolve existing exceptions, and keep every
explicit glyph pair, including zero. Class definitions and class pairs remain.
This preserves other members and permits subsequent independent punctuation
edits. No membership is removed. Unicode punctuation is the default filter;
untick it for unencoded punctuation, Greek letters or other selected glyphs.
Unencoded alternates use the Unicode values of their base-name glyph. An
ambiguous partner keeps only that pair. Each master is checked with FontLab's
shared pair validator; a master with invalid class members is named and kept,
while other valid masters can still write.
Whole-number values and the twice-UPM limit are checked too. Invalid numeric
data on any master, including one outside the chosen scope, keeps the entire
font unchanged: the shared writer validates numeric history font-wide.
Why: FontLab's Flatten Class Kerning expands the whole current-master table.
This tool limits expansion to selected glyphs and offers all-master scope.
Use: Select glyphs in the Font window. Inspect the non-modal preview, choose
masters, and press Add Exceptions. Each changing action is recorded as one Undo
step by the shared kerning writer. Refresh the selection for another pass.
Benefit: Isolate punctuation without discarding class data or existing overrides.

Independent behaviour rewrite after Simon Cozens, Unbundle Punctuation Kerning.py,
MIT. Repository: https://github.com/simoncozens/GlyphsScripts . No code copied.
"""

from dataclasses import dataclass
from math import isfinite
from typing import Any
from unicodedata import category

TITLE = "Unbundle Punctuation Kerning"
KEY = "kerning_punctuation_exceptions"


def is_punctuation(unicodes: list[int]) -> bool:
    """Use Unicode punctuation categories instead of a hard-coded name list."""
    return any(category(chr(code)).startswith("P") for code in unicodes)


def expand(
    pairs: dict, groups: dict, selected: set[str], *, kept: list | None = None
) -> dict:
    """Materialize affected effective pairs while keeping all explicit overrides."""

    def members(side: tuple) -> tuple:
        name, mode = side
        return (name,) if mode == "glyphMode" else tuple(groups[name][0])

    candidates = set()
    for a, b in pairs:
        lefts, rights = members(a), members(b)
        candidates.update(
            (left, right) for left in lefts if left in selected for right in rights
        )
        candidates.update(
            (left, right) for left in lefts for right in rights if right in selected
        )
    indexes: tuple[dict, dict] = ({}, {})
    for key, (items, mode) in groups.items():
        for side in {"KernLeft": (0,), "KernRight": (1,), "KernBothSide": (0, 1)}.get(
            mode, ()
        ):
            for name in dict.fromkeys(items):
                indexes[side].setdefault(name, []).append(key)
    changes = {}
    for left, right in sorted(candidates):
        pair = ((left, "glyphMode"), (right, "glyphMode"))
        if pair in pairs:
            continue
        choices = []
        for index, name in enumerate((left, right)):
            found = indexes[index].get(name, [])
            if len(found) > 1:
                if kept is not None:
                    kept.append(
                        (pair, f"Ambiguous kerning classes for {name}; pair kept")
                    )
                break
            choices.append(
                [(name, "glyphMode")] + [(key, "groupMode") for key in found]
            )
        if len(choices) != 2:
            continue
        resolved = [
            pairs[a, b] for a in choices[0] for b in choices[1] if (a, b) in pairs
        ]
        if resolved:
            changes[pair] = resolved[0]
    return changes


def numeric_problem(package: Any, master: str, pairs: dict) -> str:
    """Match whole-value and persistence checks without private App calls.

    Whole-unit, finite and signed32 rules use the public writer helper. The
    writer exposes no public range validator, so repeat its small range rule.
    """
    import fly.ap.kerning_edit as values

    upm = package.upm
    invalid_upm = f"{master}: invalid UPM; master kept"
    if isinstance(upm, bool) or not isinstance(upm, (int, float)):
        return invalid_upm
    try:
        upm = float(upm)
    except (ValueError, OverflowError):
        return invalid_upm
    if not isfinite(upm) or upm <= 0:
        return invalid_upm
    for pair, value in pairs.items():
        label = " + ".join(
            ("@" if mode == "groupMode" else "") + name for name, mode in pair
        )
        try:
            values.whole_value(value)
            if abs(value) > 2 * upm:
                raise ValueError(f"outside +/-{2 * upm:g} (twice UPM)")
        except (ValueError, OverflowError) as error:
            return f"{master}: {label} = {value!r}: {error}; master kept"
    return ""


def master_problem(package: Any, master: str, pairs: dict, groups: dict) -> str:
    """Check the writer's value limits and every existing glyph/class pair."""
    import fly.ap.kerning_batch as batch

    problem = numeric_problem(package, master, pairs)
    if problem:
        return problem
    for pair in pairs:
        try:
            batch.validate_pair(package, master, pair, groups=groups)
        except ValueError as error:
            classes = [f"@{name}" for name, mode in pair if mode == "groupMode"]
            label = "class " + ", ".join(classes) if classes else "glyph pair"
            return f"{master}: {label}: {error}; master kept"
    return ""


@dataclass(frozen=True)
class Row:
    """One explicit exception or a named kept-selection message."""

    master: str
    pair: tuple
    value: float = 0
    note: str = ""


def panel_type() -> type:
    """Use the shared modeless selection panel and guarded kerning batch writer."""
    import fly.ap.kerning_batch as batch
    import fly.ap.selection_panel as panels
    from fly import qt

    class PunctuationPanel(panels.panel_type()):
        """Selection, punctuation filter, master scope and complete pair preview."""

        TITLE, KEY, ACTION = TITLE, KEY, "Add Exceptions"
        CONSENT = ""
        HEADERS = ("Master", "Left", "Right", "Value / kept")

        def build_controls(self) -> None:
            """Default to Unicode punctuation; allow any selected glyph explicitly."""
            self.punctuation_only = qt.QtGui.QCheckBox("Unicode punctuation only")
            self.punctuation_only.setChecked(True)
            self.add_row("Filter", self.punctuation_only)
            self.watch(self.punctuation_only.toggled)

        def plan_rows(self, package: Any, masters: list[str]) -> list[Row]:
            """Capture every master once; keep refused selection rows visible."""
            self.source_snapshot = batch.snapshot_kerning(package, typed=True)
            numeric_issues = {
                master: problem
                for master, pairs in self.source_snapshot.pairs.items()
                if (problem := numeric_problem(package, master, pairs))
            }
            if numeric_issues:
                empty_pair = (("", "glyphMode"), ("", "glyphMode"))
                return [
                    *(
                        Row(master, empty_pair, note=problem)
                        for master, problem in numeric_issues.items()
                    ),
                    Row(
                        "All masters",
                        empty_pair,
                        note="Font-wide numeric history check failed; all masters kept. Correct the named data before applying.",
                    ),
                ]
            selected, rows = set(), []
            for name in self.names:
                glyph = package.findName(name)
                if glyph is None or glyph.isNull:
                    rows.append(
                        Row(
                            "",
                            ((name, "glyphMode"), ("", "glyphMode")),
                            note="missing glyph, kept",
                        )
                    )
                    continue
                codes = list(glyph.unicodes)
                if not codes and "." in name:
                    base = package.findName(name.split(".", 1)[0])
                    if base is not None and not base.isNull:
                        codes = list(base.unicodes)
                if self.punctuation_only.isChecked() and not is_punctuation(codes):
                    rows.append(
                        Row(
                            "",
                            ((name, "glyphMode"), ("", "glyphMode")),
                            note="outside Unicode punctuation, kept",
                        )
                    )
                else:
                    selected.add(name)
            for master in masters:
                pairs, groups = (
                    self.source_snapshot.pairs[master],
                    self.source_snapshot.groups[master],
                )
                problem = master_problem(package, master, pairs, groups)
                if problem:
                    rows.append(
                        Row(
                            master, (("", "glyphMode"), ("", "glyphMode")), note=problem
                        )
                    )
                    continue
                changes = {}
                for name in sorted(selected):
                    kept: list = []
                    found = expand(pairs, groups, {name}, kept=kept)
                    rows.extend(Row(master, pair, note=note) for pair, note in kept)
                    if not found and not kept:
                        rows.append(
                            Row(
                                master,
                                ((name, "glyphMode"), ("", "glyphMode")),
                                note="no inherited pairs to expand, kept",
                            )
                        )
                    for pair, value in found.items():
                        try:
                            batch.validate_pair(package, master, pair, groups=groups)
                        except ValueError as error:
                            rows.append(Row(master, pair, note=f"{error}; pair kept"))
                            continue
                        changes[pair] = value
                rows.extend(Row(master, pair, value) for pair, value in changes.items())
            return rows

        def cells(self, row: Row) -> list[str]:
            """Display glyph identities without legacy @name encoding."""
            return [
                row.master,
                row.pair[0][0],
                row.pair[1][0],
                row.note or f"{row.value:g}",
            ]

        def write(self, package: Any, rows: list[Row]) -> dict:
            """Stage all master edits in one shared history transaction."""
            edits: dict = {}
            for row in rows:
                if not row.note:
                    edits.setdefault(row.master, {})[row.pair] = row.value
            if not edits:
                return {"pairs": 0}
            try:
                changed = batch.write_kerning(
                    package, edits, TITLE, expected=self.source_snapshot
                )
            except RuntimeError as error:
                raise RuntimeError(
                    f"{error} Native changes may remain; use Edit > Undo."
                ) from error
            return {
                "pairs": sum(len(items) for items in edits.values()) if changed else 0
            }

        def result_text(self, result: dict) -> str:
            """Count the explicit pairs written across the selected masters."""
            return f"Added {result['pairs']} exceptions. Classes kept."

    return PunctuationPanel


def run() -> Any:
    """Open the owned panel; the shared base binds the current font."""
    import fly.ap.scripting as scripting  # noqa: PLR0402 - qualified Fly submodule

    return scripting.show_script_dialog(panel_type(), KEY)


def main() -> None:
    """Contain native capture failures."""
    try:
        run()
    except (ValueError, RuntimeError, TimeoutError) as error:
        print(f"{TITLE}: {error}")


if __name__ == "__main__":
    main()
