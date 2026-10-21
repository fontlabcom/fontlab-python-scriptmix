# this_file: Scripts/Anchors/Auto Cursive Attachment Add Anchors.py
# SPDX-License-Identifier: Apache-2.0
# FLM: Anchors · Auto Cursive Attachment Add Anchors
"""Fit missing entry and exit anchors to a saved cursive sample.

What: Fit missing connection pins for right-to-left scripts on the current
master. Search exit from the left edge and entry from the right edge.
How: Read a JSON sample from Get Sample. Require matching master names.
Name fragments ini/med request exit; fin/med request entry. Keep existing
pins. Score near-edge ink thickness and polygon-edge tangent estimates;
a perfect zero score is valid. Use nonzero winding on closed decomposed
outlines. Round half up to font units. Report actual text conversions.
Why: A persistent sample gives a reusable attachment standard. Layer
failures become note rows so clean selected glyphs can still run.
Use: Select glyphs, Browse for the sample, inspect the preview, then Add.
Benefit: Place consistent right-to-left cursive connections. Each
application is recorded as one Undo step.

Source: Simon Cozens, https://github.com/simoncozens/GlyphsScripts,
MIT, copyright 2017 Simon Cozens. Independent behaviour rewrite; no source
code was copied.
"""

import io
import json
import math
from itertools import pairwise
from pathlib import Path
from time import monotonic
from typing import Any

import fly.ap.scripting as scripting  # noqa: PLR0402 - Fly submodule import avoids native attribute lookup

TITLE = "Auto Cursive Attachment Add Anchors"
KEY = "anchors_auto_cursive_attachment_add_anchors"

Point = tuple[float, float]
Rings = list[list[Point]]


def outline_rings(layer: Any) -> Rings:
    """Flatten transformed, closed outline shapes; keep contour winding and holes."""
    rings: Rings = []
    for shape in layer.shapes:
        if (
            shape.isComposite
            or not shape.transform.isAffine()
            or not shape.openedPath.isEmpty()
        ):
            raise ValueError("Use closed, decomposed outlines for cursive sampling.")
        for polygon in shape.closedPath.toSubpathPolygons(shape.transform):
            ring = [(float(point.x()), float(point.y())) for point in polygon]
            if len(ring) >= 3:
                if ring[0] != ring[-1]:
                    ring.append(ring[0])
                if not all(math.isfinite(v) for point in ring for v in point):
                    raise ValueError("Outline coordinates must be finite.")
                rings.append(ring)
    if not rings:
        raise ValueError("No closed outline was found.")
    return rings


def vertical_spans(rings: Rings, x: float) -> list[tuple[float, float, float, float]]:
    """Return filled vertical spans and their boundary angles using nonzero winding."""
    hits: dict[float, list[tuple[int, float]]] = {}
    for ring in rings:
        for (ax, ay), (bx, by) in pairwise(ring):
            if min(ax, bx) <= x < max(ax, bx):
                y = ay + (x - ax) * (by - ay) / (bx - ax)
                tangent = (
                    math.atan2(by - ay, bx - ax) + math.pi / 2
                ) % math.pi - math.pi / 2
                hits.setdefault(y, []).append((1 if bx > ax else -1, tangent))
    spans = []
    winding = 0
    lower, lower_angle = 0.0, 0.0
    for y, values in sorted(hits.items()):
        previous = winding
        winding += sum(direction for direction, _ in values)
        if previous == 0 and winding != 0:
            lower, lower_angle = y, values[0][1]
        if previous != 0 and winding == 0 and y > lower:
            spans.append((lower, y, lower_angle, values[0][1]))
    return spans


def measure_sample(rings: Rings, points: list[Point]) -> dict[str, float]:
    """Average thickness fractions and boundary tangents around entry/exit pins."""
    if not points:
        raise ValueError("Create an entry or exit anchor inside the outline first.")
    samples = []
    for x, y in points:
        spans = [span for span in vertical_spans(rings, x) if span[0] <= y <= span[1]]
        if not spans:
            raise ValueError("Every sample anchor must lie inside closed ink.")
        low, high, low_angle, high_angle = min(
            spans, key=lambda span: span[1] - span[0]
        )
        samples.append((y - low, high - y, low_angle, high_angle))
    count = len(samples)
    values = [sum(sample[i] for sample in samples) / count for i in range(2)]
    for i in (2, 3):
        values.append(
            math.atan2(
                sum(math.sin(2 * s[i]) for s in samples),
                sum(math.cos(2 * s[i]) for s in samples),
            )
            / 2
        )
    return dict(zip(("below", "above", "lower_angle", "upper_angle"), values))


def validate_profile(data: Any) -> dict[str, float]:
    """Require a finite, nonnegative thickness profile and two tangent angles."""
    fields = ("below", "above", "lower_angle", "upper_angle")
    try:
        profile = {key: float(data[key]) for key in fields}
    except (KeyError, TypeError, ValueError, OverflowError) as error:
        raise ValueError("Sample needs four numeric profile values.") from error
    if not all(math.isfinite(value) for value in profile.values()):
        raise ValueError("Sample values must be finite.")
    if (
        min(profile["below"], profile["above"]) < 0
        or profile["below"] + profile["above"] <= 0
    ):
        raise ValueError("Sample must have positive ink thickness.")
    return profile


def needed_connections(name: str) -> list[str]:
    """Retain the source tool's form-name routing without Unicode guesses."""
    lower = name.lower()
    return (["exit"] if "ini" in lower or "med" in lower else []) + (
        ["entry"] if "fin" in lower or "med" in lower else []
    )


def choose_attachment(
    rings: Rings, profile: dict[str, float], candidates: list[float]
) -> Point:
    """Pick the first minimum of thickness and undirected boundary-angle errors."""
    profile = validate_profile(profile)
    thickness = profile["below"] + profile["above"]
    best: tuple[float, Point] | None = None
    deadline = monotonic() + 1.5
    for x in candidates:
        if monotonic() >= deadline:
            raise TimeoutError("Cursive fitting exceeded its time budget.")
        for low, high, lower_angle, upper_angle in vertical_spans(rings, x):
            distance = high - low
            if not 10 <= distance <= 500:
                continue
            errors = [
                (actual - profile[key] + math.pi / 2) % math.pi - math.pi / 2
                for actual, key in (
                    (lower_angle, "lower_angle"),
                    (upper_angle, "upper_angle"),
                )
            ]
            score = (distance - thickness) ** 2 + 25 * sum(
                error * error for error in errors
            )
            point = (x, low + distance * profile["below"] / thickness)
            if best is None or score < best[0]:
                best = (score, point)
    if best is None:
        raise ValueError("No suitable 10–500 unit ink span near the connection edge.")
    return best[1]


def read_sample(
    path: str, master: str, conversions: list[str] | None = None
) -> dict[str, float]:
    """Load a portable profile; reject text loss, wrong format and master mismatch."""
    if not path:
        raise ValueError("Choose a sample file.")
    try:
        raw = Path(path).read_bytes()
        if conversions is not None:
            if raw.startswith(b"\xef\xbb\xbf"):
                conversions.append("BOM removed")
            if b"\r" in raw:
                conversions.append("CR/CRLF read as LF")
        with io.TextIOWrapper(
            io.BytesIO(raw), encoding="utf-8-sig", newline=None
        ) as stream:
            text = stream.read()
        if any(char in text for char in ("\0", "\u00a0", "\u2028", "\u2029")):
            raise ValueError("Sample contains text that FontLab cannot preserve.")
        document = json.loads(text)
        if (
            not isinstance(document, dict)
            or document.get("format") != "fontlab-cursive-sample-1"
        ):
            raise ValueError("Choose a FontLab cursive sample JSON file.")
        if document.get("master") != master:
            raise ValueError("The sample master name must match the current master.")
        return validate_profile(document.get("profile"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise ValueError(f"Cannot read sample: {error}") from error


def cursive_changes(glyph: Any, layer: Any, profile: dict[str, float]) -> list[Any]:
    """Plan missing connections only, with deterministic near-edge searches."""
    import fly.ap.anchor_writer as anchor_writer  # noqa: PLR0402 - Fly submodule import avoids native attribute lookup

    existing = {pin.name for pin in layer.anchors}
    wanted = [name for name in needed_connections(glyph.name) if name not in existing]
    if not wanted:
        return []
    rings = outline_rings(layer)
    xs = [point[0] for ring in rings for point in ring]
    left, right = min(xs), max(xs)
    changes = []
    for name in wanted:
        start = math.floor(left) if name == "exit" else math.ceil(right) - 1
        step = 1 if name == "exit" else -1
        candidates = [
            start + step * i + 0.5
            for i in range(200)
            if left <= start + step * i + 0.5 < right
        ]
        point = choose_attachment(rings, profile, candidates)
        target = tuple(anchor_writer.half_up(value) for value in point)
        changes.append(
            anchor_writer.Change(name, "missing", str(target), ("set", name, target))
        )
    return changes


def panel_type() -> type:
    """Build the non-modal preview only after the menu is invoked."""
    import fly.ap.anchor_panel as anchor_panel  # noqa: PLR0402 - Fly submodule import avoids native attribute lookup
    from fly import qt

    class CursiveAnchorFit(anchor_panel.panel_type()):
        TITLE, KEY, ACTION = TITLE, KEY, "Add"

        def refresh(self) -> None:
            """Contain scan errors inside the panel and disable its write action."""
            try:
                super().refresh()
            except (ValueError, RuntimeError, TimeoutError) as error:
                self.apply_button.setEnabled(False)
                self.status.setText(str(error))

        def build_controls(self) -> None:
            self.sample_path = qt.QtGui.QLineEdit("")
            self.browse_button = qt.QtGui.QPushButton("Browse…")
            self.form.addWidget(qt.QtGui.QLabel("Sample JSON path"), 0, 0)
            self.form.addWidget(self.sample_path, 0, 1)
            self.form.addWidget(self.browse_button, 0, 2)
            self.watch(self.browse_button.clicked, self.choose_profile)
            self.sample_info = qt.QtGui.QLabel("Choose a sample file.")
            self.form.addWidget(self.sample_info, 1, 0, 1, 3)
            self.watch(self.sample_path.textChanged)

        def choose_profile(self) -> None:
            """Choose an existing sample; changing the path rebuilds the preview."""
            import fly.ap.qt_dialogs as qt_dialogs  # noqa: PLR0402 - Fly submodule import

            def configure(kind: Any, dialog: Any) -> None:
                dialog.setFileMode(kind.ExistingFile)
                dialog.setNameFilter("Cursive sample (*.json)")

            paths = qt_dialogs.run_file_dialog(
                qt.QtGui, configure, "Open Cursive Sample", "", (self,)
            )
            if paths:
                self.sample_path.setText(paths[0])

        def chosen_masters(self) -> list[str]:
            return [self.current_master]

        def planner(self) -> Any:
            conversions: list[str] = []
            self.sample_info.setText("")
            profile = read_sample(
                self.sample_path.text.strip(), self.current_master, conversions
            )
            self.sample_info.setText(
                "; ".join(conversions) + "."
                if conversions
                else "No text conversion needed."
            )

            def changes(glyph: Any, master: str, layer: Any) -> list[Any]:
                import fly.ap.anchor_writer as anchor_writer  # noqa: PLR0402 - Fly submodule import

                try:
                    return cursive_changes(glyph, layer, profile)
                except (ValueError, RuntimeError, TimeoutError) as error:
                    return [
                        anchor_writer.Change("cursive", "", f"{error}; layer skipped")
                    ]

            return changes

    return CursiveAnchorFit


def main() -> Any:
    """Open the sample-driven preview with the standard guarded lifecycle."""
    return scripting.show_script_dialog(panel_type(), KEY)


if __name__ == "__main__":
    main()
