# this_file: Scripts/Proof/Text Filter.py
# SPDX-License-Identifier: Apache-2.0
r"""Filter proof text in a modeless FontLab Text Simplifier panel.

Run this Proof command, enter input and a regular-expression character class,
then choose Simplify. Ranges such as A-Z and escapes such as \s keep their
source meaning. Output is read-only. Reset retains input and restores the
original output/character defaults. All three fields and window geometry are
saved in this tool's own settings namespace. Optional New Tab uses the source
font captured on launch; a changed/closed font is refused by the shared sender.

Fly loads shared App controls, filtering, saved fields and owned lifecycle.
No application event loop, system clipboard or font-design writer is used.
Native PythonQt/settings/tab/font/history preservation remains pending.
Requires App>=0.2.48.dev0 and Fly.
Modified from Slobzheninov/Glyphs-Scripts Testing/Text Filter.py (Apache-2.0).
See NOTICE and additional-tools.json for exact provenance and acceptance scope.
"""

from typing import Any


def main() -> Any:
    """Open the complete shared tool; replacing it closes only its owned panel."""
    from fly.ap.text_filter import show

    return show()


if __name__ == "__main__":
    main()
