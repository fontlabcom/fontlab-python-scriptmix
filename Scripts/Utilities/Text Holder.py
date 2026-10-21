# this_file: Scripts/Utilities/Text Holder.py
# SPDX-License-Identifier: Apache-2.0
"""Keep proof text in an editable, persistent floating scratchpad.

Find highlights the first literal match. Find & Replace changes matches in the
selection or the whole text. Save stays open; Save & Close and Ignore & Close
retain their distinct actions. Saved UTF8 text recovers on the next launch.

Independently implemented from Reza Bohloul, Window/Text holder.py.
No original body is copied or executed; original licence is undeclared.
See NOTICE and additional-tools.json. Requires Fly and App 0.2.91.dev0.
Native FontLab/PythonQt qualification remains pending.
"""


def main():
    """Open the complete shared editor through Fly without font mutation."""
    from fly.ap.text_holder import show

    return show()


if __name__ == "__main__":
    main()
