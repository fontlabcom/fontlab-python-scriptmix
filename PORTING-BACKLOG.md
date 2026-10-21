---
this_file: PORTING-BACKLOG.md
---

# Porting backlog

The active menu contains 226 practical tools: 69 sample adaptations and 157
additional tools. Source and native acceptance differ; new reviewed candidates
retain their pending native status in `additional-tools.json` and their docstrings.

These 61 archived launchers were removed from `Scripts`, not completed. Every
original remains byte-exact under `rescued/`. `rescue-index.json` retains the
historical menu path, source path and SHA-256. The other 69 sample originals
also remain preserved. The sample migration denominator stays 130; released
acceptance remains 68/130, with the Italic Angle candidate and these 61 ports
still subject to their existing gates. The wider Glyphs source corpus, PythonQt
adaptations, package cleanup and native acceptance remain in scope.

| Former menu | Preserved source | Status |
| --- | --- | --- |
| Metrics/Italic Sidebearings.py | `rescued/samples/metrics_italic_sidebearings.py` | Complete source writer candidate; native one-Undo/full-font preservation pending; original rescue ledger retained |
| Metrics/Alignment Zones.py | `rescued/samples/metrics_zones_editor.py` | Unported; held until the App has a qualified native zone writer (fontlabapp.zone_editor Backend.apply) |
| Metrics/Round Advances.py | `rescued/samples/metrics_round_advances.py` | Complete source writer candidate; native one-Undo/full-font preservation pending; original rescue ledger retained |
| Metrics/Centre In Advance.py | `rescued/samples/metrics_center_in_advance.py` | Complete source writer candidate; native one-Undo/full-font preservation pending; original rescue ledger retained |
| Metrics/Zero-Width Marks.py | `rescued/samples/metrics_zero_width_marks.py` | Complete source writer candidate; native one-Undo/full-font preservation pending; original rescue ledger retained |
| Metrics/Vertical Metrics.py | `rescued/samples/metrics_vertical_metrics_diagram.py` | Ported read-only as Metrics/Vertical Metrics Diagram.py (comparison diagram); value edits through Font Info/Master Metrics Table.py; native verification pending |
| Metrics/Equalize Sidebearings.py | `rescued/samples/metrics_equalize_sidebearings.py` | Complete source writer candidate; native one-Undo/full-font preservation pending; original rescue ledger retained |
| Metrics/Tabular Width.py | `rescued/samples/metrics_tabular_width.py` | Complete source writer candidate; native one-Undo/full-font preservation pending; original rescue ledger retained |
| Metrics/Scale Advances.py | `rescued/samples/metrics_scale_advances.py` | Complete source writer candidate; native one-Undo/full-font preservation pending; original rescue ledger retained |
| Metrics/Sidebearings Tuner.py | `rescued/samples/metrics_sidebearings_tuner.py` | Complete source writer candidate; native one-Undo/full-font preservation pending; original rescue ledger retained |
| Metrics/Copy Metrics From Reference.py | `rescued/samples/metrics_copy_from_reference.py` | Complete source writer candidate; native one-Undo/full-font preservation pending; original rescue ledger retained |
| Names/Glyph Tags.py | `rescued/samples/names_glyph_tags.py` | Complete source writer candidate; native one-Undo/full-font preservation pending; original rescue ledger retained |
| Names/Mark Color Palette.py | `rescued/samples/names_mark_color_palette.py` | Complete source writer candidate; native one-Undo/full-font preservation pending; original rescue ledger retained |
| Names/Duplicate Unicodes.py | `rescued/samples/names_duplicate_unicodes.py` | Complete source writer candidate; native one-Undo/full-font preservation pending; original rescue ledger retained |
| Names/Suffix Tool.py | `rescued/samples/names_suffix_tool.py` | Complete source writer candidate; native one-Undo/full-font preservation pending; original rescue ledger retained |
| Names/Batch Rename.py | `rescued/samples/names_batch_rename.py` | Complete source writer candidate; native one-Undo/full-font preservation pending; original rescue ledger retained |
| Names/Batch Glyph Notes.py | `rescued/samples/utility_batch_glyph_notes.py` | Complete source writer candidate; native one-Undo/full-font preservation pending; original rescue ledger retained |
| Names/Glyph Notes.py | `rescued/samples/names_glyph_notes.py` | Complete source writer candidate; native one-Undo/full-font preservation pending; original rescue ledger retained |
| Names/Unicode From Names.py | `rescued/samples/names_unicode_from_names.py` | Complete source writer candidate; native one-Undo/full-font preservation pending; original rescue ledger retained |
| Components/Build From Recipes.py | `rescued/samples/components_build_from_recipes.py` | Complete source writer candidate; native one-Undo/full-font preservation pending; original rescue ledger retained |
| Components/Align By Anchor.py | `rescued/samples/components_align_by_anchor.py` | Complete source writer candidate; native one-Undo/full-font preservation pending; original rescue ledger retained |
| Components/Decompose.py | `rescued/samples/components_decompose.py` | Complete source writer candidate; native one-Undo/full-font preservation pending; original rescue ledger retained |
| Components/Replace Reference.py | `rescued/samples/components_replace_reference.py` | Complete source writer candidate; native one-Undo/full-font preservation pending; original rescue ledger retained |
| Components/Copy Offsets Between Masters.py | `rescued/samples/components_copy_offsets_between_masters.py` | Complete source writer candidate; native one-Undo/full-font preservation pending; original rescue ledger retained |
| Components/Unlock Lock.py | `rescued/samples/components_unlock_lock.py` | Complete source writer candidate; native one-Undo/full-font preservation pending; original rescue ledger retained |
| Components/Nested Finder.py | `rescued/samples/components_nested_finder.py` | Complete source writer candidate; native one-Undo/full-font preservation pending; original rescue ledger retained |
| Cleanup/Empty Layers.py | `rescued/samples/cleanup_empty_layers.py` | Complete source writer candidate; native one-Undo/full-font preservation pending; original rescue ledger retained |
| Guides/Suggest Zones From Overshoots.py | `rescued/samples/zones_from_glyphs.py` | Unported; held until the App has a qualified native zone writer (suggest rule in fontlabapp.alignment_zones) |
| Contours/Round Coordinates.py | `rescued/samples/outlines_round_coordinates.py` | Complete source writer candidate; native one-Undo/full-font preservation pending; original rescue ledger retained |
| Contours/Autohint Selected Layers.py | `rescued/samples/hints_autohint.py` | Complete source writer candidate; native glyph-creation/content Undo, full-font preservation and reopen verification pending; original rescue ledger retained |
| Contours/Placeholder Glyphs.py | `rescued/samples/generate_placeholder_glyphs.py` | Complete source writer candidate; native glyph-creation/content Undo, full-font preservation and reopen verification pending; original rescue ledger retained |
| Contours/Shadow Copy.py | `rescued/samples/generate_shadow.py` | Complete source writer candidate; native glyph-creation/content Undo, full-font preservation and reopen verification pending; original rescue ledger retained |
| Contours/Remove Overlap.py | `rescued/samples/outlines_remove_overlap.py` | Complete source writer candidate; native one-Undo/full-font preservation pending; original rescue ledger retained |
| Contours/Add Extremes.py | `rescued/samples/outlines_add_extremes.py` | Complete source writer candidate; native one-Undo/full-font preservation pending; original rescue ledger retained |
| Contours/Correct Contour Direction.py | `rescued/samples/outlines_correct_direction.py` | Complete source writer candidate; native one-Undo/full-font preservation pending; original rescue ledger retained |
| Contours/Remove PostScript Hints.py | `rescued/samples/hints_remove.py` | Complete source writer candidate; native glyph-creation/content Undo, full-font preservation and reopen verification pending; original rescue ledger retained |
| Contours/Straighten Short Curves.py | `rescued/samples/outlines_straighten_short_curves.py` | Complete source writer candidate; native one-Undo/full-font preservation pending; original rescue ledger retained |
| Contours/Optimize Start Points.py | `rescued/samples/outlines_optimize_start_points.py` | Complete source writer candidate; native one-Undo/full-font preservation pending; original rescue ledger retained |
| Contours/Delete Small Contours.py | `rescued/samples/outlines_delete_small_contours.py` | Complete source writer candidate; native one-Undo/full-font preservation pending; original rescue ledger retained |
| Contours/Transform.py | `rescued/samples/outlines_transform_dialog.py` | Complete source writer candidate; native one-Undo/full-font preservation pending; original rescue ledger retained |
| Contours/Tabular Figure Copies.py | `rescued/samples/generate_tabular_copies.py` | Complete source writer candidate; native glyph-creation/content Undo, full-font preservation and reopen verification pending; original rescue ledger retained |
| Contours/Outline Effect.py | `rescued/samples/generate_outline_effect.py` | Complete source writer candidate; native glyph-creation/content Undo, full-font preservation and reopen verification pending; original rescue ledger retained |
| Contours/Superior & Inferior Figures.py | `rescued/samples/generate_superiors.py` | Complete source writer candidate; native glyph-creation/content Undo, full-font preservation and reopen verification pending; original rescue ledger retained |
| Contours/Fix Zero Handles.py | `rescued/samples/outlines_fix_zero_handles.py` | Complete source writer candidate; native one-Undo/full-font preservation pending; original rescue ledger retained |
| Contours/Slant.py | `rescued/samples/outlines_slant.py` | Complete source writer candidate; native one-Undo/full-font preservation pending; original rescue ledger retained |
| Contours/Small Caps From Capitals.py | `rescued/samples/generate_small_caps.py` | Complete source writer candidate; native glyph-creation/content Undo, full-font preservation and reopen verification pending; original rescue ledger retained |
| Contours/Delete Duplicate Contours.py | `rescued/samples/outlines_delete_duplicate_contours.py` | Complete source writer candidate; native one-Undo/full-font preservation pending; original rescue ledger retained |
| Masters/Copy Outline To Mask.py | `rescued/samples/masters_copy_to_mask.py` | Complete source writer candidate; native one-Undo/full-font preservation pending; original rescue ledger retained |
| Masters/Layer Cleanup.py | `rescued/samples/masters_layer_cleanup.py` | Complete source writer candidate; native one-Undo/full-font preservation pending; original rescue ledger retained |
| Masters/Sync Sidebearings.py | `rescued/samples/masters_sync_metrics.py` | Complete source writer candidate; native one-Undo/full-font preservation pending; original rescue ledger retained |
| Masters/Restore Backup Layer.py | `rescued/samples/masters_restore_backup.py` | Complete source writer candidate; native one-Undo/full-font preservation pending; original rescue ledger retained |
| Masters/Copy Layer Between Masters.py | `rescued/samples/masters_copy_layer.py` | Complete source writer candidate; native one-Undo/full-font preservation pending; original rescue ledger retained |
| Masters/Back Up Master Layers.py | `rescued/samples/masters_backup_layer.py` | Unported; duplicate of Masters/Duplicate Current Layer.py (current-master scope); all-masters scope not in the menu |
| Anchors/Rename Bulk.py | `rescued/samples/anchors_rename_bulk.py` | Complete source writer candidate; native one-Undo/full-font preservation pending; original rescue ledger retained |
| Anchors/Center Horizontally.py | `rescued/samples/anchors_center_horizontally.py` | Complete source writer candidate; native one-Undo/full-font preservation pending; original rescue ledger retained |
| Anchors/Place From Bounds.py | `rescued/samples/anchors_place_from_bounds.py` | Complete source writer candidate; native one-Undo/full-font preservation pending; original rescue ledger retained |
| Anchors/Snap To Metrics.py | `rescued/samples/anchors_snap_to_metrics.py` | Complete source writer candidate; native one-Undo/full-font preservation pending; original rescue ledger retained |
| Anchors/Duplicates Finder.py | `rescued/samples/anchors_duplicates_finder.py` | Complete source writer candidate; native one-Undo/full-font preservation pending; original rescue ledger retained |
| Anchors/Round To Grid.py | `rescued/samples/anchors_round_to_grid.py` | Complete source writer candidate; native one-Undo/full-font preservation pending; original rescue ledger retained |
| Anchors/Delete By Name.py | `rescued/samples/anchors_delete_by_name.py` | Complete source writer candidate; native one-Undo/full-font preservation pending; original rescue ledger retained |
| Anchors/Mirror Across Masters.py | `rescued/samples/anchors_mirror_across_masters.py` | Complete source writer candidate; native one-Undo/full-font preservation pending; original rescue ledger retained |

## Third-party behaviour sources

These additional tools reproduce the behaviour of third-party Glyphs scripts
as independent FontLab rewrites; no source code is copied. Each source
identity has one row. Source hashes of the ported sources are in
`additional-tools.json`; NOTICE holds the credits and licences.

| Source | Disposition | Menu | Note |
| --- | --- | --- | --- |
| `pedroarilla/glyphs-scripts/Real* text/Real* English text.py` | Ported | Proof/Real English Text.py | 24 original passages; five distinct passages per proof |
| `pedroarilla/glyphs-scripts/Real* text/Real* Spanish text.py` | Ported | Proof/Real Spanish Text.py | 24 original passages; five distinct passages per proof |
| `Reset-Type-Studio/Glyphs-Scripts/Paths/Change Weight.py` | Duplicate of | — | FontLab: Tools > Actions > Change Weight |
| `Reset-Type-Studio/Glyphs-Scripts/Paths/Nodes At Extremes.py` | Duplicate of | Contours/Add Extremes.py | Also FontLab: Contour > Nodes at Extremes |
| `Reset-Type-Studio/Glyphs-Scripts/Paths/Smart Slant.py` | Ported | Contours/Smart Slant.py | Keeps both sidebearings, or the ink centre at the same advance |
| `Reset-Type-Studio/Glyphs-Scripts/Paths/Node Duplicator (all masters).py` | Ported | Contours/Node Duplicator.py | Combined with the two variants below |
| `Reset-Type-Studio/Glyphs-Scripts/Paths/Node Duplicator (current layer).py` | Ported | Contours/Node Duplicator.py | Editor-layer scope |
| `Reset-Type-Studio/Glyphs-Scripts/Paths/Node Duplicator + 2 Handles (all masters).py` | Ported | Contours/Node Duplicator.py | Optional coincident handles |
| `Reset-Type-Studio/Glyphs-Scripts/Transformations/Transformations Tool (all masters).py` | Duplicate of | Contours/Transform.py | Transform covers all masters, with preview and origin choices |
| `Reset-Type-Studio/Glyphs-Scripts/Components/Component Swapper (all masters).py` | Duplicate of | Components/Replace Reference.py | Replaces a named component source across selected glyphs and all masters, with a preview |
| `Reset-Type-Studio/Glyphs-Scripts/Components/Decompose Specific Components (all masters).py` | Ported | Components/Decompose Named Components.py | Exact-name filter; recursive subtree decomposition |
| `Reset-Type-Studio/Glyphs-Scripts/Smart Components/Values for Smart Components.py` | Ported | Components/Set Component Locations.py | Rows start at the current locations; Set writes only edited rows |
| `Reset-Type-Studio/Glyphs-Scripts/Smart Components/Selected to Normal Components.py` | Duplicate of | Components/Set Component Locations.py | Reset sets Base layer name to the host master layer |
| `Reset-Type-Studio/Glyphs-Scripts/Smart Components/Selected to Smart Components.py` | Retired | — | No conversion is needed in FontLab; glyph-specific axes use source-layer locations, which Scripts/Masters/Set Intermediate Layer.py creates |
| `Reset-Type-Studio/Glyphs-Scripts/FontInfo/Axis Coordinates to Location (Custom Parameter).py` | Duplicate of | — | FontLab: File > Font Info > Masters and Instances store locations and axis mapping natively |
| `Reset-Type-Studio/Glyphs-Scripts/FontInfo/Set TTFAutohint Options Automatically.py` | Retired | — | Set the TTFAutohint values in FontLab: File > Font Info > Other Values |
| `Reset-Type-Studio/Glyphs-Scripts/Exports/Trial Font Maker.py` | Ported | Font Info/Trial Font Maker.py | Selection-based trial copies of static exports |
| `Reset-Type-Studio/Glyphs-Scripts/Layers/Delete 'Empty' Layers.py` | Duplicate of | Masters/Layer Cleanup.py | Previews auxiliary layers and deletes them explicitly, unnamed layers included |
| `Reset-Type-Studio/Glyphs-Scripts/KernOn/Delete KernOn.py` | Duplicate of | — | FontLab: Kerning panel > Remove All Pairs, with class and all-master options |
| `Reset-Type-Studio/Glyphs-Scripts/Bracket Layers/Bracket Layers to Alternate Glyphs method.py` | Duplicate of | Names/Glyph Tags.py | FontLab switches alternates through glyph-tag design rules |
| `RezaBohloul/RezaBohloul/Edit/Magic Remover.py` | Ported | Utilities/Magic Remover.py | Compatible-layer preview and named kept reasons; no licence declared upstream |
| `RezaBohloul/RezaBohloul/component/Toggle automatic alignment.py` | Duplicate of | — | FontLab: Element > Anchored, with matching operations; no licence declared upstream |
| `RezaBohloul/RezaBohloul/Glyph/Set Intermediate Layer.py` | Ported | Masters/Set Intermediate Layer.py | Creates and interpolates intermediate layers over selected glyphs; no licence declared upstream |
| `RezaBohloul/RezaBohloul/Export/Export To All Formats Light.py` | Duplicate of | — | FontLab: File > Export Font As, with export profiles; no licence declared upstream |
| `RezaBohloul/RezaBohloul/Export/Export To All Formats with Options.py` | Duplicate of | — | FontLab: File > Export Font As, with export profiles; no licence declared upstream |
| `slobzheninov/Glyphs-Scripts/App/Export To All Formats.py` | Duplicate of | — | FontLab: File > Export Font As, with export profiles; Glyphs-only instance settings are not reproduced |
| `slobzheninov/Glyphs-Scripts/Font Info/Demo Instance Generator.py` | Duplicate of | Font Info/Trial Font Maker.py | Trial Font Maker uses a name prefix and keeps the compiled liga feature |
| `slobzheninov/Glyphs-Scripts/Font Info/Preferred Names - Clean.py` | Retired | — | Set instance names in FontLab: File > Font Info > Instances |
| `slobzheninov/Glyphs-Scripts/Font Info/Preferred Names - Set.py` | Retired | — | Set instance names in FontLab: File > Font Info > Instances |
| `slobzheninov/Glyphs-Scripts/Font Info/Set Vertical Metrics.py` | Retired | — | Its calculation differs from Font Info/Calculate Vertical Metrics.py; set Use Typo Metrics in FontLab: File > Font Info |
| `slobzheninov/Glyphs-Scripts/Font Info/glyphOrder - Paste.py` | Ported | Font Info/Paste Glyph Order Encoding.py | Saves the ordered names as an encoding file |
| `rsztype/Scripts/MasterTwins.py` | Ported | Masters/Master Twins.py | Content switches, component-only copies and whole-font scope |
| `rsztype/Scripts/Postino.py` | Ported | Masters/Deliver Glyphs.py | Master-name pairing with visible fallbacks; components, hints and categories are not transferred |
| `rsztype/Scripts/ShortNames.py` | Retired | — | FontLab generates instance PostScript names and file names; set PostScript names per master |
| `rsztype/Scripts/StyleLinker.py` | Ported | Names/Style Linker.py | Whole-word base matching across width groups, with a preview |
| `NaN-xyz/GlyphsApp-Scripts/MasterBlaster/MasterBlaster.py` | Ported | Masters/Master Text Comparison.py | Word groups and file presets with exact per-slot master layers |
| `NaN-xyz/GlyphsApp-Scripts/CommonGlyphs.py` | Ported | Masters/Common Glyphs.py | Exact-name proof set shared by every open font |
| `simoncozens/GlyphsScripts/Add Anchors From File.py` | Ported | Anchors/Add Anchors From File.py | CSV coordinates round half up before the preview |
| `simoncozens/GlyphsScripts/AutoCursiveAttachment - Add Anchors.py` | Ported | Anchors/Auto Cursive Attachment Add Anchors.py | Cursive entry and exit anchors from a saved sample profile |
| `simoncozens/GlyphsScripts/AutoCursiveAttachment - Get Sample.py` | Ported | Anchors/Auto Cursive Attachment Get Sample.py | Saves the sample profile to a new file |
| `simoncozens/GlyphsScripts/Copy Anchor Context.py` | Retired | — | FontLab feature output has no per-anchor contextual positioning |
| `simoncozens/GlyphsScripts/Copy Myanmar Anchors.py` | Ported | Anchors/Copy Myanmar Anchors.py | Unicode routing preset; compare Anchors/Copy Anchors From Glyph.py |
| `simoncozens/GlyphsScripts/Derive Anchors From Components.py` | Ported | Anchors/Derive Anchors From Components.py | Stacked marks use the first mark per label |
| `simoncozens/GlyphsScripts/Optical Center.py` | Ported | Anchors/Optical Center.py | Scanline column weights; the result is an estimate |
| `simoncozens/GlyphsScripts/Remove Extraneous Mark Anchors.py` | Ported | Anchors/Remove Extraneous Mark Anchors.py | Preview before removal |
| `simoncozens/GlyphsScripts/Reset Anchors.py` | Retired | — | FontLab's Python API has no default-anchor regeneration |
| `simoncozens/GlyphsScripts/Comb.py` | Ported | Contours/Comb.py | Configurable ribbon strips over selected glyphs and masters |
| `simoncozens/GlyphsScripts/Curve All Straights.py` | Ported | Contours/Curve All Straights.py | Selected contours, mapped onto compatible layers |
| `simoncozens/GlyphsScripts/Delete Close Points.py` | Ported | Contours/Delete Close Points.py | Configurable short-segment threshold |
| `simoncozens/GlyphsScripts/Make Compatible.py` | Ported | Contours/Make Compatible.py | Promotes lines where another master has a curve |
| `simoncozens/GlyphsScripts/Sandblast.py` | Ported | Contours/Sandblast.py | Seeded holes inside the filled shape |
| `simoncozens/GlyphsScripts/Straighten All Curves.py` | Ported | Contours/Straighten All Curves.py | Selected contours, mapped onto compatible layers |
| `simoncozens/GlyphsScripts/Superaligner.py` | Ported | Contours/Superaligner.py | Aligns contour order and start points with the first master |
| `simoncozens/GlyphsScripts/Interpolated Nudge.py` | Ported | Contours/Interpolated Nudge.py | Moves selected nodes and scales their handles |
| `simoncozens/GlyphsScripts/Make bottom-left node first.py` | Duplicate of | Contours/Optimize Start Points.py | Puts Y before X and can match a reference master |
| `simoncozens/GlyphsScripts/Round Everything.py` | Duplicate of | Contours/Round Coordinates.py | Also Anchors/Round To Grid.py and Metrics/Round Advances.py |
| `simoncozens/GlyphsScripts/glyphmonkey.py` | Retired | — | Helper module with no menu action |
| `simoncozens/GlyphsScripts/Autokern.py` | Duplicate of | — | FontLab: Pairs panel > Autokern selected pairs, Neural mode |
| `simoncozens/GlyphsScripts/Kern Optimizer.py` | Ported | Kerning/Kerning Energy Report.py | Read-only kerning energy and spacing-bias report |
| `simoncozens/GlyphsScripts/Unbundle Punctuation Kerning.py` | Ported | Kerning/Unbundle Punctuation Kerning.py | Writes selected punctuation exceptions across chosen masters; classes and overrides stay |
| `simoncozens/GlyphsScripts/LightSpace.py` | Duplicate of | — | FontLab: Font > Metrics > Autospace |
| `simoncozens/GlyphsScripts/Sansomatic.py` | Ported | Contours/Sansomatic.py | Fourteen geometric capitals in empty selected layers |
| `simoncozens/GlyphsScripts/Cadence Grid.py` | Duplicate of | Guides/Grid Generator.py | Regular vertical glyph guides with preview and master scope |
| `simoncozens/GlyphsScripts/Myanmar Medial Ra Maker.py` | Ported | Contours/Myanmar Medial Ra Maker.py | Per-master extensions with a preview of every target |
| `simoncozens/GlyphsScripts/Nastaliq Connection Editor.py` | Ported | Features/Nastaliq Connection Editor.py | Qalmi connection choices kept in managed rlig comments |
| `simoncozens/GlyphsScripts/componentize.py` | Duplicate of | — | FontLab: Font > Detect Composites; Contour > Convert > Detect Component |
| `simoncozens/GlyphsScripts/Clean Classes.py` | Duplicate of | — | FontLab: Classes panel > Clean Up Selected Classes |
| `simoncozens/GlyphsScripts/Rename To Glyphs Default Names.py` | Duplicate of | — | FontLab: Font > Rename Glyphs > Alternative, or Rename by Table |
| `slobzheninov/Glyphs-Scripts/Align/Align Top.py` | Ported | Contours/Align And Distribute.py | Combined alignment and node distribution panel |
| `slobzheninov/Glyphs-Scripts/Align/Align Bottom.py` | Ported | Contours/Align And Distribute.py | Combined alignment and node distribution panel |
| `slobzheninov/Glyphs-Scripts/Align/Align Left.py` | Ported | Contours/Align And Distribute.py | Combined alignment and node distribution panel |
| `slobzheninov/Glyphs-Scripts/Align/Align Right.py` | Ported | Contours/Align And Distribute.py | Combined alignment and node distribution panel |
| `slobzheninov/Glyphs-Scripts/Align/Align Horizontal Center.py` | Ported | Contours/Align And Distribute.py | Combined alignment and node distribution panel |
| `slobzheninov/Glyphs-Scripts/Align/Align Vertical Center.py` | Ported | Contours/Align And Distribute.py | Combined alignment and node distribution panel |
| `slobzheninov/Glyphs-Scripts/Align/Distribute Nodes Horizontally.py` | Ported | Contours/Align And Distribute.py | Combined alignment and node distribution panel |
| `slobzheninov/Glyphs-Scripts/Align/Distribute Nodes Vertically.py` | Ported | Contours/Align And Distribute.py | Combined alignment and node distribution panel |
| `slobzheninov/Glyphs-Scripts/Align/Center Selected Glyphs.py` | Duplicate of | Metrics/Centre In Advance.py | Equal sidebearings with the advance kept, in the current or all masters |
| `slobzheninov/Glyphs-Scripts/Rotate/Rotate.py` | Ported | Contours/Rotate Selection.py | Preview and six rotation presets over several layers |
| `slobzheninov/Glyphs-Scripts/Rotate/Rotate 1 CCW.py` | Ported | Contours/Rotate Selection.py | Preview and six rotation presets over several layers |
| `slobzheninov/Glyphs-Scripts/Rotate/Rotate 1 CW.py` | Ported | Contours/Rotate Selection.py | Preview and six rotation presets over several layers |
| `slobzheninov/Glyphs-Scripts/Rotate/Rotate 10 CCW.py` | Ported | Contours/Rotate Selection.py | Preview and six rotation presets over several layers |
| `slobzheninov/Glyphs-Scripts/Rotate/Rotate 10 CW.py` | Ported | Contours/Rotate Selection.py | Preview and six rotation presets over several layers |
| `slobzheninov/Glyphs-Scripts/Rotate/Rotate 45 CCW.py` | Ported | Contours/Rotate Selection.py | Preview and six rotation presets over several layers |
| `slobzheninov/Glyphs-Scripts/Rotate/Rotate 45 CW.py` | Ported | Contours/Rotate Selection.py | Preview and six rotation presets over several layers |
| `slobzheninov/Glyphs-Scripts/Reflect/Reflect Horizontally.py` | Ported | Contours/Reflect Horizontally.py | Preview over several masters or selected layers |
| `slobzheninov/Glyphs-Scripts/Reflect/Reflect Vertically.py` | Ported | Contours/Reflect Vertically.py | Preview over several masters or selected layers |
| `slobzheninov/Glyphs-Scripts/Overlap nodes.py` | Ported | Contours/Overlap Nodes.py | Coincident terminal nodes; each layer uses its own master's italic angle |
| `slobzheninov/Glyphs-Scripts/G2 Harmonize.py` | Duplicate of | — | FontLab: Contour > Harmonize |
