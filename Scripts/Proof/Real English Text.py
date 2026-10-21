# this_file: Scripts/Proof/Real English Text.py
# SPDX-License-Identifier: Apache-2.0
"""Open a new Glyph tab with five randomly chosen English prose passages.

What it does:
    Draw five passages without replacement. Keep their case and punctuation,
    including a space after the last passage. No passage repeats in one proof.

How it works:
    Capture the current font, assemble the proof, then use the shared App
    text-tab helper with that font's id. Send missing characters unchanged.
    Refuse text that PythonQt cannot pass intact. No font data is written;
    no Undo step is needed. Tab creation can fail after a new tab opens.

Why this design:
    The native Glyph tab supplies an editable, non-modal proof. Run again for
    another sample. No separate panel or settings are needed. The 24 original
    passages below replace the upstream collection of 300 third-party excerpts.
    They exercise connected prose, figures, currency, quotes and punctuation.

How to use:
    Activate a font and run this command. Inspect spacing and text colour in
    the new Glyph tab. Existing tabs remain available for comparison.

Benefit:
    Test readable English without finding and pasting external sample text.

Credit:
    Behaviour after Pedro Arilla, glyphs-scripts/Real* text/Real* English text.py,
    Apache-2.0, https://github.com/pedroarilla/glyphs-scripts.
    Independent behaviour-only rewrite. No source code or corpus was copied.
    Proof passages are original to this tool, Apache-2.0.
"""

import random

TITLE = "Real English Text"
DRAW_COUNT = 5
PASSAGES: tuple[str, ...] = (
    "By seven o’clock, the bakery windows were bright. A cyclist stopped for bread, tucked the warm loaf into her bag, and rode towards the bridge.",
    "“Which way is the harbour?” asked the visitor. The bookseller pointed past the clock tower: a short walk, two left turns, and then the sea.",
    "Rain had softened the chalk marks on the pavement, but the children could still follow their imaginary railway from the gate to the old oak tree.",
    "The museum opens at 10:30 on Saturday. Tickets cost £8.50; children under twelve can visit free when accompanied by an adult.",
    "An orange cat occupied the only sunny chair. We negotiated for several minutes before agreeing that the meeting could take place on the floor.",
    "At the back of the workshop stood a cabinet of tiny drawers. Each held a different size of screw, carefully labelled in blue ink.",
    "When the ferry arrived, the fog lifted just enough to reveal three houses on the island. Someone waved a yellow coat from the landing stage.",
    "Our first map showed a path through the orchard. The second showed a wall. We took a pencil, a notebook and a generous supply of sandwiches.",
    "Please leave the parcel beneath the bench, away from the rain. There is no need to ring the bell—the baby has only just fallen asleep.",
    "The choir rehearsed upstairs while a carpenter repaired the doors below. For a brief moment, hammer and piano found exactly the same rhythm.",
    "A return journey costs €24, including a bicycle. Book before Friday for a 15% discount, and keep your ticket until you leave the station.",
    "She had written “buy lemons” on the envelope. Inside was a recipe, a photograph of a garden and a letter that began with an unexpected question.",
    "Beyond the last street lamp, the road curved into open country. The bus windows reflected our faces against a sky full of slow-moving clouds.",
    "We measured the shelf twice and cut it once. It fitted perfectly, which surprised everyone except the apprentice who had checked the figures.",
    "The little cinema has 96 seats, a red curtain and a kettle behind the counter. Its programme changes every Thursday, weather permitting.",
    "“Don’t hurry,” said the gardener. “A seed has no interest in your calendar.” He closed the greenhouse and went indoors to make some tea.",
    "At low tide, a narrow strip of sand joins the two beaches. Walkers cross it quietly, watching the pools for crabs and the sky for rain.",
    "The new journal pairs short essays with drawings from local artists. Issue No. 4 includes a fold-out map and a conversation about public gardens.",
    "Nothing had changed in the waiting room except the flowers. There were fresh irises in a blue jug, and one petal had fallen beside the newspaper.",
    "To mend the jacket, choose a thread slightly darker than the cloth. Small, even stitches will hold the patch without making the fabric stiff.",
    "Breakfast for six: twelve eggs, a pot of coffee, warm rolls and a bowl of pears. The youngest guest requested toast cut into triangles.",
    "The shop’s opening hours are painted directly on the glass. At dusk, their shadows stretch across the counter and disappear beneath the till.",
    "After 2.5 kilometres, turn right at the stone fountain. The path becomes steep, but the view from the ridge is worth a patient climb.",
    "Someone had left a handwritten score on the train. We could not read the music, yet the careful marks suggested a tune both lively and kind.",
)


def proof_text() -> str:
    """Sample five distinct passages; preserve the final separating space."""
    if not PASSAGES:
        raise ValueError("No proof passages are available.")
    if any(c in passage for passage in PASSAGES for c in ("\0", "\u00a0", "\u2028", "\u2029")):
        raise ValueError("Unsupported proof character; text cannot pass intact.")
    return " ".join(random.sample(PASSAGES, DRAW_COUNT)) + " "


def run() -> None:
    """Build a proof only with an open font; delegate native tab ownership."""
    import fly.ap.scripting as context
    import fly.ap.text_tab as tabs

    package = context.current_package()
    if package is None:
        raise ValueError("Open a font before creating a prose proof.")
    package_id = int(package.id)
    tabs.open_text_tab(proof_text(), expected_id=package_id)


def main() -> None:
    """Menu entry; report a refusal without retrying native tab creation."""
    try:
        run()
    except (ValueError, RuntimeError, TimeoutError) as error:
        print(f"{TITLE}: {error}")


if __name__ == "__main__":
    main()
