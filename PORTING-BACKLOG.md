---
this_file: PORTING-BACKLOG.md
---

# Porting backlog

The active menu contains 99 practical tools: 69 sample adaptations and 30
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
| Metrics/Italic Sidebearings.py | `rescued/samples/metrics_italic_sidebearings.py` | Unported; native verification pending |
| Metrics/Alignment Zones.py | `rescued/samples/metrics_zones_editor.py` | Unported; native verification pending |
| Metrics/Round Advances.py | `rescued/samples/metrics_round_advances.py` | Unported; native verification pending |
| Metrics/Centre In Advance.py | `rescued/samples/metrics_center_in_advance.py` | Unported; native verification pending |
| Metrics/Zero-Width Marks.py | `rescued/samples/metrics_zero_width_marks.py` | Unported; native verification pending |
| Metrics/Vertical Metrics.py | `rescued/samples/metrics_vertical_metrics_diagram.py` | Unported; native verification pending |
| Metrics/Equalize Sidebearings.py | `rescued/samples/metrics_equalize_sidebearings.py` | Unported; native verification pending |
| Metrics/Tabular Width.py | `rescued/samples/metrics_tabular_width.py` | Unported; native verification pending |
| Metrics/Scale Advances.py | `rescued/samples/metrics_scale_advances.py` | Unported; native verification pending |
| Metrics/Sidebearings Tuner.py | `rescued/samples/metrics_sidebearings_tuner.py` | Unported; native verification pending |
| Metrics/Copy Metrics From Reference.py | `rescued/samples/metrics_copy_from_reference.py` | Unported; native verification pending |
| Names/Glyph Tags.py | `rescued/samples/names_glyph_tags.py` | Unported; native verification pending |
| Names/Mark Color Palette.py | `rescued/samples/names_mark_color_palette.py` | Unported; native verification pending |
| Names/Duplicate Unicodes.py | `rescued/samples/names_duplicate_unicodes.py` | Unported; native verification pending |
| Names/Suffix Tool.py | `rescued/samples/names_suffix_tool.py` | Unported; native verification pending |
| Names/Batch Rename.py | `rescued/samples/names_batch_rename.py` | Unported; native verification pending |
| Names/Batch Glyph Notes.py | `rescued/samples/utility_batch_glyph_notes.py` | Unported; native verification pending |
| Names/Glyph Notes.py | `rescued/samples/names_glyph_notes.py` | Unported; native verification pending |
| Names/Unicode From Names.py | `rescued/samples/names_unicode_from_names.py` | Unported; native verification pending |
| Components/Build From Recipes.py | `rescued/samples/components_build_from_recipes.py` | Unported; native verification pending |
| Components/Align By Anchor.py | `rescued/samples/components_align_by_anchor.py` | Unported; native verification pending |
| Components/Decompose.py | `rescued/samples/components_decompose.py` | Unported; native verification pending |
| Components/Replace Reference.py | `rescued/samples/components_replace_reference.py` | Unported; native verification pending |
| Components/Copy Offsets Between Masters.py | `rescued/samples/components_copy_offsets_between_masters.py` | Unported; native verification pending |
| Components/Unlock Lock.py | `rescued/samples/components_unlock_lock.py` | Unported; native verification pending |
| Components/Nested Finder.py | `rescued/samples/components_nested_finder.py` | Unported; native verification pending |
| Cleanup/Empty Layers.py | `rescued/samples/cleanup_empty_layers.py` | Unported; native verification pending |
| Guides/Suggest Zones From Overshoots.py | `rescued/samples/zones_from_glyphs.py` | Unported; native verification pending |
| Contours/Round Coordinates.py | `rescued/samples/outlines_round_coordinates.py` | Unported; native verification pending |
| Contours/Autohint Selected Layers.py | `rescued/samples/hints_autohint.py` | Unported; native verification pending |
| Contours/Placeholder Glyphs.py | `rescued/samples/generate_placeholder_glyphs.py` | Unported; native verification pending |
| Contours/Shadow Copy.py | `rescued/samples/generate_shadow.py` | Unported; native verification pending |
| Contours/Remove Overlap.py | `rescued/samples/outlines_remove_overlap.py` | Unported; native verification pending |
| Contours/Add Extremes.py | `rescued/samples/outlines_add_extremes.py` | Unported; native verification pending |
| Contours/Correct Contour Direction.py | `rescued/samples/outlines_correct_direction.py` | Unported; native verification pending |
| Contours/Remove PostScript Hints.py | `rescued/samples/hints_remove.py` | Unported; native verification pending |
| Contours/Straighten Short Curves.py | `rescued/samples/outlines_straighten_short_curves.py` | Unported; native verification pending |
| Contours/Optimize Start Points.py | `rescued/samples/outlines_optimize_start_points.py` | Unported; native verification pending |
| Contours/Delete Small Contours.py | `rescued/samples/outlines_delete_small_contours.py` | Unported; native verification pending |
| Contours/Transform.py | `rescued/samples/outlines_transform_dialog.py` | Unported; native verification pending |
| Contours/Tabular Figure Copies.py | `rescued/samples/generate_tabular_copies.py` | Unported; native verification pending |
| Contours/Outline Effect.py | `rescued/samples/generate_outline_effect.py` | Unported; native verification pending |
| Contours/Superior & Inferior Figures.py | `rescued/samples/generate_superiors.py` | Unported; native verification pending |
| Contours/Fix Zero Handles.py | `rescued/samples/outlines_fix_zero_handles.py` | Unported; native verification pending |
| Contours/Slant.py | `rescued/samples/outlines_slant.py` | Unported; native verification pending |
| Contours/Small Caps From Capitals.py | `rescued/samples/generate_small_caps.py` | Unported; native verification pending |
| Contours/Delete Duplicate Contours.py | `rescued/samples/outlines_delete_duplicate_contours.py` | Unported; native verification pending |
| Masters/Copy Outline To Mask.py | `rescued/samples/masters_copy_to_mask.py` | Unported; native verification pending |
| Masters/Layer Cleanup.py | `rescued/samples/masters_layer_cleanup.py` | Unported; native verification pending |
| Masters/Sync Sidebearings.py | `rescued/samples/masters_sync_metrics.py` | Unported; native verification pending |
| Masters/Restore Backup Layer.py | `rescued/samples/masters_restore_backup.py` | Unported; native verification pending |
| Masters/Copy Layer Between Masters.py | `rescued/samples/masters_copy_layer.py` | Unported; native verification pending |
| Masters/Back Up Master Layers.py | `rescued/samples/masters_backup_layer.py` | Unported; native verification pending |
| Anchors/Rename Bulk.py | `rescued/samples/anchors_rename_bulk.py` | Unported; native verification pending |
| Anchors/Center Horizontally.py | `rescued/samples/anchors_center_horizontally.py` | Unported; native verification pending |
| Anchors/Place From Bounds.py | `rescued/samples/anchors_place_from_bounds.py` | Unported; native verification pending |
| Anchors/Snap To Metrics.py | `rescued/samples/anchors_snap_to_metrics.py` | Unported; native verification pending |
| Anchors/Duplicates Finder.py | `rescued/samples/anchors_duplicates_finder.py` | Unported; native verification pending |
| Anchors/Round To Grid.py | `rescued/samples/anchors_round_to_grid.py` | Unported; native verification pending |
| Anchors/Delete By Name.py | `rescued/samples/anchors_delete_by_name.py` | Unported; native verification pending |
| Anchors/Mirror Across Masters.py | `rescued/samples/anchors_mirror_across_masters.py` | Unported; native verification pending |
