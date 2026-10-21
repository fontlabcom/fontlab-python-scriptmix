# this_file: Scripts/Contours/Raise Ascender.py
# SPDX-License-Identifier: MIT AND Apache-2.0
"""Raise own nodes strictly above associated-master x-height + 10 by Amount.

Raise this master processes every selected layer occurrence. Raise all masters
processes ALL foreground layers of the first selected glyph, including auxiliaries.
Controls move too; components stay unchanged. Default Amount is 10. See the guide
for complete original scope, supported native associations and history limits.
Behavior adapted from Simon Cozens' MIT Raise Ascender; full attribution in NOTICE.
"""


def main() -> object:
    """Open the complete two-action owned modeless workflow through Fly/App."""
    from fly.ap.raise_ascender import show

    return show()


if __name__ == "__main__":
    main()
