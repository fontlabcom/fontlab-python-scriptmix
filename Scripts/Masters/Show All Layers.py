# this_file: Scripts/Masters/Show All Layers.py
# SPDX-License-Identifier: Apache-2.0
"""Open every foreground layer of the selected glyph occurrences in a proof.

What: Show masters and auxiliary layers by their exact names in a new tab.
How: Capture the current selection, preserve occurrence order, and submit
explicit glyph/layer symbols through the shared exact-layer tab helper.
Why: Unicode and slash-text conversion can show the wrong glyph or layer.
The Masters panel shows one glyph’s masters. This proof also includes
auxiliary layers and several glyphs. Masks and service layers are omitted
because they are not foreground symbols.
Use: Select glyphs in a Font window or Glyph window, then run. Capture includes
selected or active slots. Each glyph has its own scan budget. No dialog.
Benefit: Compare all stored foreground variants without repeated layer switches.
The script writes no font data and makes no Undo step. The proof uses one row;
it preserves repeated selected glyph occurrences.

Independent behaviour rewrite after Alex Slobzheninov,
Glyphs-Scripts/Glyphs/Show All Layers.py, Apache-2.0.
Repository: https://github.com/slobzheninov/Glyphs-Scripts . No code copied.
"""

from time import monotonic

TITLE = "Show All Layers"


def run() -> int:
    """Read exact foreground layers before opening a verified new proof tab."""
    import fly.ap.layer_selection as selection
    import fly.ap.named_tab as tabs
    import fly.ap.scripting as scripting  # noqa: PLR0402

    deadline = monotonic() + 2.0
    captured = selection.capture(deadline)
    package = scripting.current_package()
    if package is None or not captured.occurrences:
        raise ValueError("Open a font and select glyphs first.")
    if package.id != captured.context[0]:
        raise ValueError("The active font changed; select the glyphs again.")
    layers = []
    for occurrence in captured.occurrences:
        glyph_deadline = monotonic() + 2.0
        for layer in occurrence.glyph.layers:
            if monotonic() >= glyph_deadline:
                raise TimeoutError("Layer scan exceeded its time limit; no tab opened.")
            if not (layer.isMaskLayer or layer.isService):
                layers.append((occurrence.glyph_name, str(layer.name)))
    if not layers:
        raise ValueError("The selected glyphs have no foreground layers.")
    tabs.open_layer_tab(
        tuple(layers),
        expected_id=package.id,
        master=str(package.master),
        deadline=monotonic() + max(2.0, 2.0 * len(captured.occurrences)),
    )
    return len(layers)


def main() -> None:
    """Report the proof size or a diagnosed refusal without clearing Output."""
    try:
        print(f"{TITLE}: {run()} foreground layer occurrences.")
    except (ValueError, RuntimeError, TimeoutError) as error:
        print(f"{TITLE}: {error}")


if __name__ == "__main__":
    main()
