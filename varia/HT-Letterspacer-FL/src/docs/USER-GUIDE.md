# HT Letterspacer for FontLab 9

Open **Scripts → HT Letterspacer → HT Letterspacer**. Select glyphs, set Area,
Depth and Overshoot, and click Apply. LSB/RSB choose the sides to change.
Tabular sets a fixed advance width; Auto keeps each glyph's current width.
The middle column shows the current master's saved parameter values.
Copy Parameters copies a JSON parameter object for scripting.

The compact palette uses manual values and the current master. Apply HTLS
Config instead uses the font's saved rules. HTLS Manager is the optional full
interface for rule editing, master overrides, previews and all-master work.
Save configuration in the manager, then save the font as VFJ/VFC to persist it.
Native FontLab history is used for spacing operations.

The installer owns only the HT Letterspacer Scripts subfolder and its runtime
under Extensions. It downloads a pinned original GitHub revision and checks
both the archive and engine files. Nothing is fetched while spacing.
Rerun the installer to update/repair; restart FontLab after updating a loaded
version. The Uninstall script preserves fonts and keeps a recoverable runtime
backup. Other scripts in the Scripts folder are not removed.

Normal outlines, ordinary pen strokes and live components are supported.
Alternate/intermediate layers and complex host-specific effects have not been
fully matched to Glyphs. The older standalone v1 algorithm differs from the
current upstream plugin. See the source package's docs/PARITY.md for test scope.

Licenses and original source are included in this runtime. No Git checkout,
Glyphs installation or external Python installation is needed.
