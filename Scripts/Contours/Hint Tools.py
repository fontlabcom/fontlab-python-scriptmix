# this_file: Scripts/Contours/Hint Tools.py
# SPDX-License-Identifier: Apache-2.0
# FLM: Contours · Hint Tools
"""Preview and apply PostScript hint changes to explicitly captured glyph layers.

Choose Autohint or Remove PostScript hints. Refresh captures the Font window
selection; Preview Changes shows glyph/master targets and hint counts. Apply
rechecks that source before the existing single history transaction. The right
canvas is read-only. Automatic and locked layers stay protected; composite-base
editing requires explicit consent. Before/after counts and pending updates stay
visible. Autohint also uses native package hint settings and node links.

Requires FontLab App with Hint Tools and read-only TGlyph support, Fontport and
FontLab Fly in FontLab 9 Python 3.11. Credits: FontLab sample authors and App
contributors, Apache-2.0. Source: https://github.com/fontlabcom/fontlab-python-scriptmix
"""
from typing import Any


def main() -> Any:
    """Open both hint tasks in the shared App shell."""
    from fly.ap.studios.hint_tools import show

    return show()


if __name__ == '__main__':
    main()
