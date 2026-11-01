# this_file: Scripts/Contours/Sansomatic.py
# SPDX-License-Identifier: MIT
"""Construct geometric sans capitals in empty selected master layers.

What: Build A, E, F, H, I, L, N, O, S, T, V, X, Y and Z from explicit
height, width, vertical stroke, horizontal stroke and side space dimensions.
How: Compose rectangles, diagonal strips, an elliptical ring or a cubic S.
Union the filled pieces with Qt, then use the shared contour converter and
outline writer. Existing outlines, components, locked layers and linked metrics
are kept and named in the preview. No glyph or layer is created.
Why: FontLab's Rectangle and Ellipse tools draw individual pieces. This panel
constructs complete letter skeletons across selected glyphs and masters. Explicit
dimensions replace the Glyphs Dimension palette; no host callbacks are installed.
Use: Select empty capital glyphs in the Font window. Set the five dimensions,
inspect the non-modal preview and choose current or all masters. Press Build.
To give each master its own dimensions, untick Keep masters compatible, choose
Current master, and set that master's dimensions before Build.
Each changing action is recorded as one Undo step. Clear an outline with native
FontLab tools before building that glyph again. Unsupported capitals are kept.
Benefit: Start a consistent geometric alphabet without overwriting existing work.
Diagonal ends are horizontal at the baseline and cap height. S spans both levels.
The common dimensions are a construction model; per-letter source sliders and
the source's continuous destructive redraw are replaced by explicit Build.

Independent behaviour rewrite after Simon Cozens, Sansomatic.py, MIT.
Repository: https://github.com/simoncozens/GlyphsScripts . No source code copied.
"""

import math
from typing import Any

TITLE, KEY = "Sansomatic", "contours_geometric_capitals"
LETTERS = "AEFHILNOSTVXYZ"


def design(
    letter: str,
    height: float,
    breadth: float,
    vertical: float,
    horizontal: float,
    margin: float,
) -> tuple[list[tuple], float]:
    """Return detached path instructions and an advance, with finite dimensions."""
    values = (height, breadth, vertical, horizontal, margin)
    if not all(math.isfinite(v) for v in values) or min(values[:4]) <= 0 or margin < 0:
        raise ValueError("Use positive finite dimensions and nonnegative side space.")
    if len(letter) != 1 or letter not in LETTERS:
        raise ValueError(f"No construction for {letter or 'this glyph'}, kept.")
    if breadth <= 2 * vertical or height <= 2 * horizontal:
        raise ValueError("Width and height must exceed twice their stroke widths.")
    x, h, w, v, t = margin, height, breadth, vertical, horizontal
    commands: list[tuple] = []

    def rectangle(a: float, b: float, c: float, d: float) -> None:
        commands.extend([("R", a, b, c, d), ("Z",)])

    def strip(a: float, b: float, c: float, d: float) -> None:
        # A fresh polygon, not a transform of existing native outline data.
        half = v * math.hypot(c - a, d - b) / (2 * abs(d - b))
        commands.extend(
            [
                ("M", a - half, b),
                ("L", c - half, d),
                ("L", c + half, d),
                ("L", a + half, b),
                ("Z",),
            ]
        )

    if letter in "EFLH":
        rectangle(x, 0, v, h)
        if letter in "EFL":
            if letter != "F":
                rectangle(x + v, 0, w - v, t)
            if letter != "L":
                rectangle(x + v, h - t, w - v, t)
                rectangle(x + v, (h - t) / 2, (w - v) * 0.75, t)
        else:
            rectangle(x + w - v, 0, v, h)
            rectangle(x + v, (h - t) / 2, w - 2 * v, t)
    elif letter == "I":
        rectangle(x, 0, v, h)
        w = v
    elif letter == "T":
        rectangle(x, h - t, w, t)
        rectangle(x + (w - v) / 2, 0, v, h - t)
    elif letter in "AV":
        low, high = (0, h) if letter == "A" else (h, 0)
        strip(x + v / 2, low, x + w / 2, high)
        strip(x + w / 2, high, x + w - v / 2, low)
        if letter == "A":
            rectangle(x + w / 4, h * 0.35, w / 2, t)
    elif letter in "NXZ":
        if letter == "N":
            strip(x + v / 2, h, x + w - v / 2, 0)
        else:
            strip(x + v / 2, 0, x + w - v / 2, h)
        if letter == "N":
            rectangle(x, 0, v, h)
            rectangle(x + w - v, 0, v, h)
        elif letter == "X":
            strip(x + v / 2, h, x + w - v / 2, 0)
        else:
            rectangle(x, 0, w, t)
            rectangle(x, h - t, w, t)
    elif letter == "Y":
        strip(x + v / 2, h, x + w / 2, h / 2)
        strip(x + w - v / 2, h, x + w / 2, h / 2)
        rectangle(x + (w - v) / 2, 0, v, h / 2)
    elif letter == "O":
        commands.extend(
            [("E", x, 0, w, h), ("D", x + v, t, w - 2 * v, h - 2 * t), ("Z",)]
        )
    else:  # S: one continuous closed cubic ribbon.
        commands.extend(
            [
                ("M", x + w, h - t),
                (
                    "C",
                    x + w * 0.75,
                    h,
                    x + w * 0.65,
                    h,
                    x + w * 0.5,
                    h,
                ),
                ("C", x, h, x, h * 0.6, x + w * 0.4, h * 0.5),
                ("C", x + w - v, h * 0.4, x + w - v, t, x + w * 0.5, t),
                ("C", x + w * 0.25, t, x + w * 0.1, 2 * t, x, 2 * t),
                ("L", x, t),
                ("C", x + w * 0.1, 0, x + w * 0.25, 0, x + w * 0.5, 0),
                ("C", x + w, 0, x + w, h * 0.4, x + w * 0.6, h * 0.5),
                ("C", x + v, h * 0.65, x + v, h - t, x + w * 0.5, h - t),
                ("C", x + w * 0.65, h - t, x + w * 0.75, h - t, x + w, h - 2 * t),
                ("Z",),
            ]
        )
    return commands, w + 2 * margin


def layer_reason(layer: Any) -> str:
    """Keep authored layers; this generator fills empty manual layers only."""
    import fly.ap.metrics_panel as metrics

    if layer.isLocked:
        return "locked layer, kept"
    if layer.shapes:
        return "existing outline or component, kept"
    if metrics.has_metrics_link(layer):
        return "metrics link, kept"
    return ""


def build_path(commands: list[tuple]) -> Any:
    """Union detached pieces with Qt; subtract only the O's inner ellipse."""
    from fly import qt

    gui = qt.QtGui
    combined, piece = gui.QPainterPath(), gui.QPainterPath()
    for command in commands:
        op, *values = command
        if op == "R":
            piece.addRect(*values)
        elif op in ("E", "D"):
            ellipse = gui.QPainterPath()
            ellipse.addEllipse(*values)
            if op == "D":
                combined = combined.subtracted(ellipse)
            else:
                combined = combined.united(ellipse)
        elif op == "M":
            piece.moveTo(*values)
        elif op == "L":
            piece.lineTo(*values)
        elif op == "C":
            piece.cubicTo(*values)
        elif op == "Z":
            piece.closeSubpath()
            combined = combined.united(piece)
            piece = gui.QPainterPath()
    return combined


def editor_type() -> type:
    """Use the shared outline transaction; prepare all contours before history."""
    import fly.ap.contour_copy as copies
    import fly.ap.outline_writer as writer
    from fly import fl

    class CapitalEditor(writer.Editor):
        """Append one newly constructed shape to an empty layer."""

        def prepare(self, layer: Any, edits: list) -> list:
            """Build detached native contours before the first font edit."""
            if layer_reason(layer):
                raise ValueError(f"{layer.name}: no longer empty or editable, kept.")
            commands, advance = edits[0]
            contours = copies.path_contours(build_path(commands))
            if not contours:
                raise ValueError("The construction produced no contours.")
            shape = fl.flShape()
            shape.addContours(contours, True)
            return [(shape, advance, len(contours))]

        def write(self, layer: Any, steps: list) -> None:
            """Insert the prepared shape and its advance in the shared transaction."""
            shape, advance, _ = steps[0]
            layer.addShape(shape)
            layer.advanceWidth = advance

        def check(self, prepared: list) -> list[str]:
            """Read back the contour count and advance after notification."""
            errors = []
            for layer, steps in prepared:
                _, advance, count = steps[0]
                if (
                    layer.advanceWidth != advance
                    or len(layer.shapes) != 1
                    or len(layer.shapes[0].contours) != count
                ):
                    errors.append(f"{layer.name}: construction did not read back")
            return errors

    return CapitalEditor


def panel_type() -> type:
    """Build the owned modeless outline panel with explicit dimensions."""
    import fly.ap.outline_panel as panels
    import fly.ap.outline_writer as writer

    class CapitalPanel(panels.panel_type()):
        """Five numeric dimensions and a per-layer construction preview."""

        TITLE, KEY, ACTION, DONE, UNIT = TITLE, KEY, "Build", "Built", "capital"
        STRUCTURAL = True
        HEADERS = ("Glyph · master", "Construction", "Before", "After / kept")

        def build_controls(self) -> None:
            """Use explicit values instead of Glyphs plug-in data."""
            self.dimension_boxes = []
            for label, default in (
                ("Height", 700),
                ("Width", 450),
                ("Vertical stroke", 70),
                ("Horizontal stroke", 55),
                ("Side space", 45),
            ):
                box = self.spin(0 if label == "Side space" else 1, 5000, default)
                self.add_row(label, box)
                self.dimension_boxes.append(box)

        def planner(self) -> Any:
            """Plan detached geometry; leave existing work and unsupported names."""
            dimensions = [float(box.value) for box in self.dimension_boxes]

            def plan(glyph: Any, master: str, layer: Any) -> list:
                note = layer_reason(layer)
                letter = str(glyph.name).split(".")[0]
                if len(letter) != 1 or letter not in LETTERS:
                    letter = next(
                        (chr(code) for code in glyph.unicodes if chr(code) in LETTERS),
                        "",
                    )
                if note:
                    return [writer.Change("capital", "", note)]
                try:
                    commands, advance = design(letter, *dimensions)
                except ValueError as error:
                    return [
                        writer.Change(str(glyph.name), "", f"{glyph.name}: {error}")
                    ]
                return [
                    writer.Change(
                        letter,
                        "empty",
                        f"width {advance:g}",
                        (commands, advance),
                        key=("capital", letter),
                    )
                ]

            return plan

        def editor(self) -> Any:
            """Return this tool's write strategy for the shared outline transaction."""
            return editor_type()()

    return CapitalPanel


def run() -> Any:
    """Open or replace the owned panel."""
    import fly.ap.scripting as scripting  # noqa: PLR0402 - qualified Fly submodule

    return scripting.show_script_dialog(panel_type(), KEY)


def main() -> None:
    """Contain host capture and construction failures."""
    try:
        run()
    except (ValueError, RuntimeError, TimeoutError) as error:
        print(f"{TITLE}: {error}")


if __name__ == "__main__":
    main()
