# this_file: Scripts/Anchors/Auto Cursive Attachment Get Sample.py
# SPDX-License-Identifier: Apache-2.0
# FLM: Anchors · Auto Cursive Attachment Get Sample
"""Save a reusable cursive attachment sample from the current FontLab layer.

What: Measure existing entry/exit pins for the right-to-left fitting tool.
How: In one selected body layer, measure mean ink distances and polygon-edge
tangent estimates around entry/exit pins. Save the master name and profile
to a new JSON file. Use nonzero winding on closed decomposed outlines.
The font is read only; existing files stay unchanged.
Why: A file survives closing the panel or FontLab and can be reused in
another font with the same master name.
Use: Select one layer with entry or exit inside ink, run the script, and
choose a new file name. The save chooser starts in the home folder.
Benefit: Reuse one attachment standard with Auto Cursive Attachment Add Anchors.

Source: Simon Cozens, https://github.com/simoncozens/GlyphsScripts,
MIT, copyright 2017 Simon Cozens. Independent behaviour rewrite; no source
code was copied.
"""

import json
import math
from itertools import pairwise
from pathlib import Path
from time import monotonic
from typing import Any

import fly.ap.scripting as scripting  # noqa: PLR0402 - Fly submodule import avoids native attribute lookup

TITLE = "Auto Cursive Attachment Get Sample"
KEY = "anchors_auto_cursive_attachment_get_sample"

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


def sample_document(layer: Any, master: str) -> dict[str, Any]:
    """Capture the two named connection pins and package the portable profile."""
    import fly.ap.anchor_writer as anchor_writer  # noqa: PLR0402 - Fly submodule import avoids native attribute lookup

    pins = [pin for pin in layer.anchors if pin.name in ("entry", "exit")]
    if len({pin.name for pin in pins}) != len(pins):
        raise ValueError("Entry and exit names must be unique.")
    profile = measure_sample(
        outline_rings(layer), [anchor_writer.raw_point(pin) for pin in pins]
    )
    return {
        "format": "fontlab-cursive-sample-1",
        "master": master,
        "profile": validate_profile(profile),
    }


def save_document(path: str, document: dict[str, Any]) -> None:
    """Write a new UTF-8 file; leave any existing file untouched."""
    try:
        with open(path, "x", encoding="utf-8", newline="\n") as stream:
            json.dump(document, stream, ensure_ascii=True, indent=2, allow_nan=False)
            stream.write("\n")
    except FileExistsError as error:
        raise ValueError(
            "Choose a new file name; existing sample files stay unchanged."
        ) from error


def main() -> Any:
    """Capture one layer, show one save chooser, and report a clear refusal."""
    import fly.ap.layer_selection as layer_selection  # noqa: PLR0402 - Fly submodule import avoids native attribute lookup
    import fly.ap.masters as masters  # noqa: PLR0402 - Fly submodule import avoids native attribute lookup
    import fly.ap.qt_dialogs as qt_dialogs  # noqa: PLR0402 - Fly submodule import avoids native attribute lookup
    from fly import qt

    try:
        selection = layer_selection.capture(monotonic() + 1.5)
        if scripting.current_package() is None or len(selection.occurrences) != 1:
            raise ValueError("Select exactly one glyph layer in an open font.")
        occurrence = selection.occurrences[0]
        layer = occurrence.layer
        if layer.isMaskLayer or layer.isService:
            raise ValueError("Choose a body layer for the sample.")
        package = scripting.current_package()
        master = masters.associated_master(layer.name, package.masters)
        if master is None:
            raise ValueError("The layer has no associated font master.")
        document = sample_document(layer, master)

        def configure(kind: Any, dialog: Any) -> None:
            dialog.setAcceptMode(kind.AcceptSave)
            dialog.setOption(kind.DontConfirmOverwrite, True)
            dialog.setFileMode(kind.AnyFile)
            dialog.setNameFilter("Cursive sample (*.json)")
            dialog.setDefaultSuffix("json")

        paths = qt_dialogs.run_file_dialog(qt.QtGui, configure, TITLE, str(Path.home()))
        if not paths:
            return None
        save_document(paths[0], document)
        print("Saved cursive sample:", paths[0])
        return document
    except (ValueError, RuntimeError, OSError) as error:
        box = qt_dialogs.create_message_box(qt.QtGui, TITLE, str(error), "Warning")
        qt_dialogs.run_message_box(box, qt.QtGui.QMessageBox.Ok)
        return None


if __name__ == "__main__":
    main()
