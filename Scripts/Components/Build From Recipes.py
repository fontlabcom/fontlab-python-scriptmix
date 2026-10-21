# this_file: Scripts/Components/Build From Recipes.py
# SPDX-License-Identifier: Apache-2.0
# FLM: Components · Build From Recipes
"""Build composite glyphs from one-line recipes with FontLab's own builder.

What: One recipe per line, for example "Aacute.alt = A + acute@acute". It
attaches the "_acute" anchor of acute to the "acute" anchor of A.
"a & b" places glyphs side by side; "mark@top[_top]" names both anchors.
Check runs every line on every chosen master as a dry run: no outline,
component, anchor or width changes (FontLab may refresh its internal glyph
data), so it runs only when you press it. Build creates the glyphs, or
rebuilds their layers when "Replace existing layers" is on.

How: The script hands each line to FontLab's construction engine, which
validates the recipe, places the components by their anchors and sets the
width. It does not compute positions itself. The result is a plain layer,
never an auto layer: FontLab would notify an auto layer, and that rebuilds
other auto layers in the font. An existing glyph without a layer for a
chosen master gets an empty layer first (one Undo step for all such
layers). A new glyph is built on the first chosen master; press Build again
to build its other masters (the status line says how many are left).

Why: A recipe list is exact, repeatable and easy to review. The builder is
FontLab's own, so the script does no anchor arithmetic that could disagree
with FontLab.

Use: Type or paste the recipes. Choose the masters and whether to replace
existing layers. Press Check, read the table, then press Build.

Benefit: Builds many composites over many masters from one reviewed list.

Undo: FontLab's builder writes each layer itself, so Edit > Undo of a rebuilt
existing layer depends on FontLab; Undo of a new glyph is FontLab's Add Glyph
step. Keep a saved copy of the font. The status line says how many layers
were built.

Safety: Check before Build: Build stays off until every line passes. The
script refuses, before any change, when:

- an existing target glyph has an automatic layer, or is the base of an
  automatic composite (FontLab rebuilds the composite and Undo does not
  restore it);
- FontLab holds queued glyph updates (they would alter other glyph dates);
- a line contains a character that FontLab's text conversion can change
  (NUL, no-break space, line or paragraph separator).

If a build fails part-way, the error names it; the layers built before it
stay. The refusal rules and the panel are shared with other scripts
(fly.ap.component_writer, fly.ap.component_panel, fly.ap.history,
fly.ap.edit_guards); the recipe parser and the panel controls belong to
this script.

Source: the author's own FontLab sample
components_build_from_recipes.py, Apache-2.0.
Adapted for the current FontLab 9 API.
"""

import re
from dataclasses import dataclass
from typing import Any

import fly.ap.component_panel as component_panel  # noqa: PLR0402 - fontlabapp.__getattr__ is native
import fly.ap.component_writer as component_writer  # noqa: PLR0402 - fontlabapp.__getattr__ is native
import fly.ap.edit_guards as edit_guards  # noqa: PLR0402 - fontlabapp.__getattr__ is native
import fly.ap.history as history  # noqa: PLR0402 - fontlabapp.__getattr__ is native
from fly import ap, qt
from fly.ap import scripting

QtGui = qt.QtGui
fontlab = ap.fontlab
TITLE = "Build from Recipes"
KEY = "components_build_from_recipes"

# ---------------------------------------------------------------- recipe logic
EXAMPLE = "Aacute.alt = A + acute@acute\n"
# "@acute" without brackets names both anchors: "@acute[_acute]".
ATTACH = re.compile(r"@([A-Za-z_][A-Za-z0-9_.-]*)(?!\[)(?=$|[+&])")
GLYPH_NAME = re.compile(r"^[A-Za-z_.][A-Za-z0-9_.-]*$")
# PythonQt text conversion can drop or change these; refuse them.
UNSAFE_TEXT = {"\x00": "NUL", "\xa0": "no-break space", "\u2028": "line separator",
               "\u2029": "paragraph separator"}  # fmt: skip
LAYER_MISSING = "Target layer not found."


@dataclass(frozen=True)
class Line:
    """One recipe line. `problem` set: the line cannot be built."""

    number: int
    target: str
    recipe: str
    problem: str = ""


@dataclass(frozen=True)
class Result:
    """Verdict for one target layer. `adds_layer`: the glyph lacks this layer."""

    target: str
    master: str
    recipe: str
    ok: bool
    message: str
    adds_layer: bool = False


def parse(text: str) -> list[Line]:
    """Non-empty lines as `Line` records. '#' starts a comment."""
    lines: list[Line] = []
    for number, raw in enumerate(text.splitlines(), 1):
        unsafe = sorted({label for char, label in UNSAFE_TEXT.items() if char in raw})
        line = raw.split("#", 1)[0].strip()
        if unsafe:
            lines.append(Line(number, line, "", f"remove the {', '.join(unsafe)}"))
            continue
        if not line:
            continue
        if "=" not in line:
            lines.append(Line(number, line, "", "use: target = base + mark@anchor"))
            continue
        target, recipe = (part.strip() for part in line.split("=", 1))
        recipe = ATTACH.sub(lambda m: f"@{m[1]}[_{m[1]}]", re.sub(r"\s+", "", recipe))
        problem = ""
        if not target or not recipe:
            problem = "empty target or recipe"
        elif not GLYPH_NAME.match(target):
            problem = f"{target} is not a valid glyph name"
        lines.append(Line(number, target, "=" + recipe if recipe else "", problem))
    return lines


def data_tool(tool: str, **arguments: Any) -> Any:
    """Call one of FontLab's own data tools in-process (fly.pr is native fontpr)."""
    from fly import pr

    return pr.call(tool, **arguments)


def build(
    package: Any,
    line: Line,
    master: str,
    replace: bool,
    dry_run: bool,
) -> tuple[bool, str]:
    """Build (or only validate) one target layer. Returns (ok, message).

    Never an auto layer: FontLab's builder notifies the glyph deeply, and an
    auto layer there rebuilds every default-recipe auto layer in the font.
    """
    arguments = {
        "font_id": scripting.font_id(package),  # fontpr finds fonts by fgId
        "glyph_name": line.target,
        "recipe": line.recipe,
        "layer_name": master,
        "replace": replace,
        "auto_layer": False,
        "dry_run": dry_run,
    }
    try:
        result = data_tool("build_glyph", **arguments)
    except Exception as error:  # noqa: BLE001 - FontLab's text goes to the table
        return False, str(error).strip() or type(error).__name__
    if not isinstance(result, dict) or result.get("status") not in {"ok", "validated"}:
        if isinstance(result, dict):
            return False, str(result.get("error") or result.get("message") or result)
        return False, str(result)
    parts = " + ".join(
        str(c.get("glyph_name")) for c in result.get("resolved_components", [])
    )
    verb = "valid" if dry_run else ("created" if result.get("created") else "built")
    return True, f"{verb}: {parts}"


def check_lines(
    package: Any,
    lines: list[Line],
    masters: list[str],
    replace: bool,
    facts: history.AutoFacts,
) -> list[Result]:
    """Dry-run every line on every master. Nothing in the font changes."""
    results: list[Result] = []
    for line in lines:
        if line.problem:
            results.append(Result(line.target, "", line.recipe, False, line.problem))
            continue
        glyph = package.findName(line.target)
        why = history.refusal(facts, line.target, "geometry") if glyph else ""
        if why:
            results.append(Result(line.target, "", line.recipe, False, why))
            continue
        for index, master in enumerate(masters):
            if glyph is None and index > 0:
                note = f"new glyph: press Build again for {master}"
                results.append(Result(line.target, master, line.recipe, True, note))
                continue
            ok, message = build(package, line, master, replace, dry_run=True)
            adds = (
                glyph is not None and component_writer.layer_of(glyph, master) is None
            )
            if adds and not ok and LAYER_MISSING in message:
                ok, message = True, f"valid: adds layer {master} first"
            results.append(Result(line.target, master, line.recipe, ok, message, adds))
    return results


def add_layers(package: Any, results: list[Result], facts: history.AutoFacts) -> int:
    """Add the empty master layers that the builds need, as ONE Undo step."""
    wanted: dict[str, list[str]] = {}
    for result in results:
        if result.adds_layer:
            wanted.setdefault(result.target, []).append(result.master)
    if not wanted:
        return 0
    glyphs = [package.findName(name) for name in wanted]

    def mutate() -> list[Any]:
        made = []
        for glyph in glyphs:
            made.extend(glyph.findLayerCreate(m) for m in wanted[glyph.name])
        return made

    history.commit(
        "Add Master Layers", [], glyphs, mutate, operation="geometry", facts=facts
    )
    return sum(len(masters) for masters in wanted.values())


class BuildRecipes(component_panel.panel_type()):
    """Recipe text, master scope and the replace option; one row per target layer."""

    TITLE, KEY, ACTION, RELOAD = TITLE, KEY, "Build", "Check"
    HEADERS: tuple[str, ...] = ("Target · master", "Recipe", "Check")
    WIDTH = 600

    def build_controls(self) -> None:
        self.results: list[Result] = []
        self.checked = False
        self.recipes = QtGui.QPlainTextEdit()
        fixed = QtGui.QFontDatabase.systemFont(QtGui.QFontDatabase.FixedFont)
        self.recipes.setFont(fixed)
        self.recipes.setPlainText(EXAMPLE)
        self.recipes.setPlaceholderText("target = base + mark@anchor   (one per line)")
        self.recipes.setMinimumHeight(110)
        self.scope = self.scope_box()
        self.replace = QtGui.QCheckBox("Replace existing layers")
        self.form.addWidget(self.recipes, 0, 0, 1, 2)
        self.form.addWidget(QtGui.QLabel("Masters"), 1, 0)
        self.form.addWidget(self.scope, 1, 1)
        self.form.addWidget(self.replace, 2, 1)
        for signal in (
            self.recipes.textChanged,
            self.scope.currentIndexChanged,
            self.replace.toggled,
        ):
            self.watch(signal, self.invalidate)

    def replacing(self) -> bool:
        return bool(self.replace.isChecked())

    def first_scan(self) -> None:
        """No dry run on open: FontLab's builder can refresh glyph data."""
        self.read_font()
        self.relabel()
        self.refresh()

    def lines(self) -> list[Line]:
        return parse(str(self.recipes.toPlainText()))

    def intro(self) -> str:
        if self.package is None:
            return "Open a font first."
        return "One recipe per line. Check runs FontLab's builder as a dry run."

    def scan(self) -> None:
        """Check button: bind to the current font, then dry-run every line."""
        self.read_font()
        self.relabel()
        self.results, self.checked = [], False
        self.facts = history.auto_facts(())
        if self.package is not None:
            self.facts = history.scan_auto_facts(self.package)
            masters = self.chosen_masters()
            self.results = check_lines(
                self.package, self.lines(), masters, self.replacing(), self.facts
            )
            self.checked = True
        self.refresh()

    def invalidate(self) -> None:
        self.results, self.checked = [], False
        self.refresh()
        self.status.setText("Recipes changed: press Check")

    def refresh(self) -> None:
        self.subtitle.setText(self.intro())
        rows = [
            (
                f"{r.target} · {r.master}" if r.master else r.target,
                component_writer.Change(
                    r.recipe,
                    "",
                    r.message,
                    None if not r.ok else r.target,
                    "" if r.ok else r.message,
                ),
            )
            for r in self.results
        ]
        self.fill(component_writer.Plan(rows=rows))
        good = sum(1 for r in self.results if r.ok)
        ready = self.checked and bool(self.results) and good == len(self.results)
        self.apply_button.setEnabled(ready)
        if not self.checked:
            self.status.setText("Press Check" if self.package else "")
        else:
            missing = "" if ready else " · fix the red lines"
            self.status.setText(f"{good} of {len(self.results)} layers ready{missing}")

    def apply(self) -> None:
        """Re-check safety, add missing layers, then build each layer."""
        package = scripting.current_package(self.package_id)
        if package is None:
            raise ValueError("The font changed; press Check.")
        edit_guards.require_settled(fontlab)
        facts = history.scan_auto_facts(package)
        results = check_lines(
            package, self.lines(), self.chosen_masters(), self.replacing(), facts
        )
        failed = [r for r in results if not r.ok]
        if failed:
            self.results = results
            self.refresh()
            raise ValueError(f"{failed[0].target}: {failed[0].message}")
        added = add_layers(package, results, facts)
        built: list[Result] = []
        for result in results:
            if result.message.startswith("new glyph:"):
                built.append(result)
                continue
            line = Line(0, result.target, result.recipe)
            ok, message = build(package, line, result.master, self.replacing(), False)
            built.append(
                Result(result.target, result.master, result.recipe, ok, message)
            )
        self.results, self.checked = built, False
        self.refresh()
        done = sum(1 for r in built if r.ok and not r.message.startswith("new glyph:"))
        errors = [r for r in built if not r.ok]
        note = (
            f" · added {component_writer.plural(added, 'empty layer')}" if added else ""
        )
        left = sum(1 for r in built if r.message.startswith("new glyph:"))
        more = f" · {component_writer.plural(left, 'master')} still to build: press Build again"
        tail = f" · {len(errors)} failed: {errors[0].message}" if errors else ""
        self.last_result = {"built": done, "failed": len(errors), "added": added}
        self.status.setText(
            f"Built {component_writer.plural(done, 'layer')}{note}{more if left else ''}{tail}"
        )


def main() -> Any:
    """Open the panel, or raise the one that is already open."""
    return scripting.show_script_dialog(BuildRecipes, KEY)


if __name__ == "__main__":
    main()
