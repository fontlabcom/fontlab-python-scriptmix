# this_file: Scripts/Contours/Shape Generators.py
# SPDX-License-Identifier: Apache-2.0 AND MIT
# FLM: Contours · Shape Generators
"""Build specialized outlines with the original algorithms in five task tabs.

Angularizzle keeps opening source paths for repeated Process and explicit
Restore, retaining its processed colour mark. Comb makes compatible ribbon
strips. Sandblast places bounded, seeded holes within filled outlines.
Sansomatic builds only supported empty capital layers. Myanmar Medial Ra fits
width groups on every master and retains complete-target refusal behavior.
Choose Preview Changes before Apply, inspect the target/master rows and the
read-only glyph canvas, and use Discard staged plan before refreshing a draft.
Creation and editing keep their original history scopes and automatic-layer
safety checks; newly generated glyphs have separate Add Glyph history steps.

Requires FontLab 9 PythonQt, matching FontLab App, Fontport and FontLab Fly.
Credits: NaN Angularizzle and independent rewrites after Simon Cozens, MIT;
App integration Apache-2.0. Full notices and sources:
https://github.com/fontlabcom/fontlab-python-scriptmix
"""
from typing import Any


def main() -> Any:
    """Open all five specialized shape generators in the shared App shell."""
    from fly.ap.studios.shape_generators.app import show

    return show()


if __name__ == '__main__':
    main()
