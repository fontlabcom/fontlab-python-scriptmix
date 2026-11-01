---
this_file: src_docs/md/scripts/names/style-linker.md
tags: ["Names"]
categories: ["Names"]
---

# Style Linker

Preview style linking for the exportable instances of the current font.

What:
    Link whole-word Bold, Italic and Oblique styles to an available base.
    Width groups remain separate. ExtraBold and SemiBold are not Bold.
How:
    A non-modal table previews FontLab style-group names and link flags.
    Apply obtains fresh instance values and changes only matching rows.
    The package owns instance values; assign the complete instance list back.
    Notifications follow FontLab Font Info: package and masters container
    before assignment, then the same list after assignment.
Why:
    FontLab uses a style-group name and bold/italic flags instead of Glyphs
    linkStyle. Native autoSLV/autoSGN and the Instances multi-select controls
    already set these values. This tool adds whole-word base matching across
    width groups in one preview. Per-instance family names (tfn) can differ
    from the font family and are not exposed by the Python instance API.
    Therefore an automatic base group is kept: set that base group explicitly
    in Font Info first. Only explicit base groups are copied. Instance family
    names and other hidden properties stay in the native value objects.
Use:
    Open a font with instances. Run this tool, check the table, then Apply.
    Refresh reads the current font again. Close releases owned signals.
Benefit:
    Preview regular/bold/italic relationships across the complete family.
Credit:
    Giuseppe Salerno / Resistenza Type, StyleLinker.py,
    https://github.com/rsztype/Scripts, Apache-2.0.
    Independent behaviour-only rewrite. No source code was copied.

Run **Names > Style Linker** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/855b383ecdf7fe204048d80c4c4fdf03c11d38fe777821fdaea2d6742223081a.py)
<!--/codeinclude-->
