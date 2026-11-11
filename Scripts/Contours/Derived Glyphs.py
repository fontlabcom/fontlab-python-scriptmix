# this_file: Scripts/Contours/Derived Glyphs.py
# SPDX-License-Identifier: Apache-2.0
# FLM: Contours · Derived Glyphs
"""Create related glyphs and outline effects in one captured-font workspace.

Use the Placeholders, Tabular figures, Sups & subs, Small caps, Shadow Copy or
Outline Effect tab. Inspect the sortable plan and the read-only glyph preview,
then choose Preview Changes and Apply. Changing controls or source geometry
requires a fresh preview; switching tabs retains the staged settings. Refresh
refuses to discard a staged plan; Discard staged plan explicitly clears it.
New glyphs use separate Add Glyph steps and one further outline step. Shadow
and outline effects edit existing layers through the original guarded writers.
Automatic dependencies and unsupported source layers retain their refusals.

Requires FontLab 9 PythonQt, matching FontLab App with read-only TGlyph support,
Fontport and FontLab Fly. Credits: the author's FontLab samples, Apache-2.0.
Source and full notices: https://github.com/fontlabcom/fontlab-python-scriptmix
"""
from typing import Any


def main() -> Any:
    """Open the six derived-glyph tasks in the shared App shell."""
    from fly.ap.studios.derived_glyphs.outline import show

    return show()


if __name__ == '__main__':
    main()
