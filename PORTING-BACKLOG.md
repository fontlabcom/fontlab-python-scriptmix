---
this_file: PORTING-BACKLOG.md
---

# Porting backlog

The active menu contains 240 practical tools: 69 sample adaptations and 171
additional tools. Source and native acceptance differ; new reviewed candidates
retain their pending native status in `additional-tools.json` and their docstrings.

These 61 archived launchers were removed from `Scripts`, not completed. Every
original has a historical path/hash identity in the external archive described
in NOTICE. `rescue-index.json` retains the
historical menu path, source path and SHA-256. The other 69 sample originals
also retain their historical identities. The sample migration denominator stays 130; released
acceptance remains 68/130, with the Italic Angle candidate and these 61 ports
still subject to their existing gates. The wider Glyphs source corpus, PythonQt
adaptations, package cleanup and native acceptance remain in scope.

| Former menu | Historical source | Status |
| --- | --- | --- |
| Metrics/Italic Sidebearings.py | `rescued/samples/metrics_italic_sidebearings.py` | Complete source writer candidate; native one-Undo/full-font preservation pending; original rescue ledger retained |
| Metrics/Alignment Zones.py | `rescued/samples/metrics_zones_editor.py` | Unported; duplicate-of FontLab's Font Info > Zones (Add and Remove zones, per master); the sample stages zone edits for all masters at once. A scripted all-master port waits for an App zone writer with one history.commit (fontlabapp zone_editor has no production Backend.apply) |
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
| Guides/Suggest Zones From Overshoots.py | `rescued/samples/zones_from_glyphs.py` | Unported; duplicate-of FontLab's Font Info > Zones > Auto-detect zones, per master; the sample suggests zones from overshoots for all masters at once. A scripted all-master port waits for an App zone writer with one history.commit (fontlabapp zone_editor has no production Backend.apply) |
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
| Masters/Back Up Master Layers.py | `rescued/samples/masters_backup_layer.py` | Unported; duplicate of Masters/Duplicate Current Layer.py (current-master and all-master scopes, custom suffix, inventory of existing backups) |
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
identity has one row with the SHA-256 of the source file it was read
from; NOTICE holds the credits and licences.

| Source | Source SHA-256 | Disposition | Menu | Note |
| --- | --- | --- | --- | --- |
| `pedroarilla/glyphs-scripts/Real* text/Real* English text.py` | `65ffbc899c2356dc81f2882bfd2d240273c3fe1a8551a5ba6441b7287cb8f773` | Ported | Proof/Real English Text.py | 24 original passages; five distinct passages per proof |
| `pedroarilla/glyphs-scripts/Real* text/Real* Spanish text.py` | `d05361190797853f73ce88413b99154a34bb6ebfd4a836478da5d37abc87a8d5` | Ported | Proof/Real Spanish Text.py | 24 original passages; five distinct passages per proof |
| `Reset-Type-Studio/Glyphs-Scripts/Paths/Change Weight.py` | `bfc9e985de5085d95aa00e7bd8f44507a3a6451f1b0d77069e06b065dd7c8af0` | Duplicate of | — | FontLab: Tools > Actions > Change Weight |
| `Reset-Type-Studio/Glyphs-Scripts/Paths/Nodes At Extremes.py` | `5c33360d76b6a7f682033e1c59d21c9ce5269be86ca108d8000c7678cdffe920` | Duplicate of | Contours/Add Extremes.py | Also FontLab: Contour > Nodes at Extremes |
| `Reset-Type-Studio/Glyphs-Scripts/Paths/Smart Slant.py` | `db549c48734fb281617a4562bca311be84797ecd1c91d015df986c4c34a437a5` | Ported | Contours/Smart Slant.py | Keeps both sidebearings, or the ink centre at the same advance |
| `Reset-Type-Studio/Glyphs-Scripts/Paths/Node Duplicator (all masters).py` | `dff5c6f2d680956288f98c3492f0b617d8f92d1182bfea54d567256555b2bb77` | Ported | Contours/Node Duplicator.py | Combined with the two variants below |
| `Reset-Type-Studio/Glyphs-Scripts/Paths/Node Duplicator (current layer).py` | `f6b7bc79856f85611abc485a8df959486afdb76c50e400b5e82f19f2b794c2c7` | Ported | Contours/Node Duplicator.py | Editor-layer scope |
| `Reset-Type-Studio/Glyphs-Scripts/Paths/Node Duplicator + 2 Handles (all masters).py` | `eccf4cef027becf7fca14f29de6fde68bea8e0aaeca513c08ba75b717556cddc` | Ported | Contours/Node Duplicator.py | Optional coincident handles |
| `Reset-Type-Studio/Glyphs-Scripts/Transformations/Transformations Tool (all masters).py` | `6bd79eb30cc39e9dc3e4f94873c6bb8ed436e4cf4efb2011c793b4b175599c93` | Duplicate of | Contours/Transform.py | Transform covers all masters, with preview and origin choices |
| `Reset-Type-Studio/Glyphs-Scripts/Components/Component Swapper (all masters).py` | `8030102452c1d6785db629f5d0c931996c411ec7e775ea98853d269b720dc6ac` | Duplicate of | Components/Replace Reference.py | Replaces a named component source across selected glyphs and all masters, with a preview |
| `Reset-Type-Studio/Glyphs-Scripts/Components/Decompose Specific Components (all masters).py` | `1c49c1e450961d83006aa368b3823333fae14b27453c69a5fd9bf16ad9459a15` | Ported | Components/Decompose Named Components.py | Exact-name filter; recursive subtree decomposition |
| `Reset-Type-Studio/Glyphs-Scripts/Smart Components/Values for Smart Components.py` | `2e96caed001c3d27b31cf82d557ceb27e65f463285546ee60c000d4390e1e389` | Ported | Components/Set Component Locations.py | Rows start at the current locations; Set writes only edited rows |
| `Reset-Type-Studio/Glyphs-Scripts/Smart Components/Selected to Normal Components.py` | `b87cf3fa5c7c377c1e400cb06af09bacd059fd9034de31ec1b72c79d1a16ea27` | Duplicate of | Components/Set Component Locations.py | Reset sets Base layer name to the host master layer |
| `Reset-Type-Studio/Glyphs-Scripts/Smart Components/Selected to Smart Components.py` | `6682614d716360ee3050bb91a5cb21e0c1d67ce25959fd161f79f35311fd72e6` | Retired | — | No conversion is needed in FontLab; glyph-specific axes use source-layer locations, which Scripts/Masters/Set Intermediate Layer.py creates |
| `Reset-Type-Studio/Glyphs-Scripts/FontInfo/Axis Coordinates to Location (Custom Parameter).py` | `a894dc79bfdadecee4db7cd0d68f85a04c8b31c978c555719f10cdadba1f1a5a` | Duplicate of | — | FontLab: File > Font Info > Masters and Instances store locations and axis mapping natively |
| `Reset-Type-Studio/Glyphs-Scripts/FontInfo/Set TTFAutohint Options Automatically.py` | `c58c899144822d4930a29b70fae2183b2a20388389c64e7b7f45b44991448fb3` | Retired | — | Set the TTFAutohint values in FontLab: File > Font Info > Other Values |
| `Reset-Type-Studio/Glyphs-Scripts/Exports/Trial Font Maker.py` | `6ec98b7326e40e633c93edd96a8de8b13ca928ea91fa2b3a359f0e30c007f1b2` | Ported | Font Info/Trial Font Maker.py | Selection-based trial copies of static exports |
| `Reset-Type-Studio/Glyphs-Scripts/Layers/Delete 'Empty' Layers.py` | `4af5250ddfbe51a87e2b8a8e4ab82b8d58be9a36fb1782daa3228c7afdc678b2` | Duplicate of | Masters/Layer Cleanup.py | Previews auxiliary layers and deletes them explicitly, unnamed layers included |
| `Reset-Type-Studio/Glyphs-Scripts/KernOn/Delete KernOn.py` | `37928caba69294e1938e9ac2a3b53b93b2cd11622d7d055cfb31688b4730bca4` | Duplicate of | — | FontLab: Kerning panel > Remove All Pairs, with class and all-master options |
| `Reset-Type-Studio/Glyphs-Scripts/Bracket Layers/Bracket Layers to Alternate Glyphs method.py` | `b9c81c926a3b4b2ff564ed9324757ce26e97be27e66307113cfd3698190a63e9` | Duplicate of | Names/Glyph Tags.py | FontLab switches alternates through glyph-tag design rules |
| `RezaBohloul/RezaBohloul/Edit/Magic Remover.py` | `e5aa9f72395cf6e354cf2d640399d770997a43ec258c960ba1bcd5d8994b7b7b` | Ported | Utilities/Magic Remover.py | Compatible-layer preview and named kept reasons; no licence declared upstream |
| `RezaBohloul/RezaBohloul/component/Toggle automatic alignment.py` | `2740f6b923cb12c7068b120b42eac5d419c030c975b6f54905a76cb173fa73cc` | Duplicate of | — | FontLab: Element > Anchored, with matching operations; no licence declared upstream |
| `RezaBohloul/RezaBohloul/Glyph/Set Intermediate Layer.py` | `64155690415236040d32fdbdb38845191883cfbd3e660db27fa61c53d9ff27c4` | Ported | Masters/Set Intermediate Layer.py | Creates and interpolates intermediate layers over selected glyphs; no licence declared upstream |
| `RezaBohloul/RezaBohloul/Export/Export To All Formats Light.py` | `9352cd1b630d436e74527bc83230d9004b77e16e3b18e4dca44f82389b480528` | Duplicate of | — | FontLab: File > Export Font As, with export profiles; no licence declared upstream |
| `RezaBohloul/RezaBohloul/Export/Export To All Formats with Options.py` | `194ae6423dfd85290651c8fa0f443711fbe67baed98731b84573b65268184567` | Duplicate of | — | FontLab: File > Export Font As, with export profiles; no licence declared upstream |
| `slobzheninov/Glyphs-Scripts/App/Export To All Formats.py` | `ff8aaf62527abbc45cb14dd783b5916fa35c659da8acf6a857f347867a24d26f` | Duplicate of | — | FontLab: File > Export Font As, with export profiles; Glyphs-only instance settings are not reproduced |
| `slobzheninov/Glyphs-Scripts/Font Info/Demo Instance Generator.py` | `45743de69965cb8165964b25f99badddd1d03db74ceb9c3686b3732514847996` | Duplicate of | Font Info/Trial Font Maker.py | Trial Font Maker uses a name prefix and keeps the compiled liga feature |
| `slobzheninov/Glyphs-Scripts/Font Info/Preferred Names - Clean.py` | `aa69bba31521734e2180419f431d62a47e5c7d7c500a911c5e4026c094d573e5` | Retired | — | Set instance names in FontLab: File > Font Info > Instances |
| `slobzheninov/Glyphs-Scripts/Font Info/Preferred Names - Set.py` | `dacecbf7b9b422e43390fae9740ec7f17e10758772fa449c76984d9d8e208f40` | Retired | — | Set instance names in FontLab: File > Font Info > Instances |
| `slobzheninov/Glyphs-Scripts/Font Info/Set Vertical Metrics.py` | `fc4cfcd0a517244e03fab35ee86f720931e1cf9420ac02b6ee88fd5d99e1d8bd` | Retired | — | Its calculation differs from Font Info/Calculate Vertical Metrics.py; set Use Typo Metrics in FontLab: File > Font Info |
| `slobzheninov/Glyphs-Scripts/Font Info/glyphOrder - Paste.py` | `3bac57f51eaf1304626a61cbdeba0127282642fa9743b8f3286866efe0371509` | Ported | Font Info/Paste Glyph Order Encoding.py | Saves the ordered names as an encoding file |
| `rsztype/Scripts/MasterTwins.py` | `430b64bfaf64c887f470245d613af96ece3f1079295939effd4eaa2e78d5d1b3` | Ported | Masters/Master Twins.py | Content switches, component-only copies and whole-font scope |
| `rsztype/Scripts/Postino.py` | `8cf4b176bac7f03384cf78967446265ef4ecc9036b2c7642acaa8fb72e3113c4` | Ported | Masters/Deliver Glyphs.py | Master-name pairing with visible fallbacks; components, hints and categories are not transferred |
| `rsztype/Scripts/ShortNames.py` | `f2833df0828996b7c7ccba3aec73af53c00a36b8bcb2a42a40309a7227408f76` | Retired | — | FontLab generates instance PostScript names and file names; set PostScript names per master |
| `rsztype/Scripts/StyleLinker.py` | `a3ad09c4706dcc7aead5ae4289f27a0692ab9d0a7a596f876a76069b27edb047` | Ported | Names/Style Linker.py | Whole-word base matching across width groups, with a preview |
| `NaN-xyz/GlyphsApp-Scripts/MasterBlaster/MasterBlaster.py` | `b219c5444601227337fbd471640081223cd96a22e61c6ad9519ea78d75c9ec95` | Ported | Masters/Master Text Comparison.py | Word groups and file presets with exact per-slot master layers |
| `NaN-xyz/GlyphsApp-Scripts/CommonGlyphs.py` | `2999152e462f69df47a3da73bdf469b10ea4de92ccb01bfc20ef01c97fc648ac` | Ported | Masters/Common Glyphs.py | Exact-name proof set shared by every open font |
| `simoncozens/GlyphsScripts/Add Anchors From File.py` | `5a1defe60f80cf34f37a96ba33a527d22c2f596c3f2eb137a3f176afc9b048d3` | Ported | Anchors/Add Anchors From File.py | CSV coordinates round half up before the preview |
| `simoncozens/GlyphsScripts/AutoCursiveAttachment - Add Anchors.py` | `01c7bf31d49ca212d1e54dea7576b5fa945816e11e2f15ae227546674dabeaca` | Ported | Anchors/Auto Cursive Attachment Add Anchors.py | Cursive entry and exit anchors from a saved sample profile |
| `simoncozens/GlyphsScripts/AutoCursiveAttachment - Get Sample.py` | `34ef7bc2dac8d6a935560f760fed5706c58ef0678a274ae1d828131d5a204746` | Ported | Anchors/Auto Cursive Attachment Get Sample.py | Saves the sample profile to a new file |
| `simoncozens/GlyphsScripts/Copy Anchor Context.py` | `c2f3037c52365a2e605dc543858ca73a91d2039564c0cd7d56a9e5a41faa09a1` | Retired | — | FontLab feature output has no per-anchor contextual positioning |
| `simoncozens/GlyphsScripts/Copy Myanmar Anchors.py` | `aebd6df11ff8dd5152a98d1cb0c99646dbd964c1d258c9a5348bb25c6f614360` | Ported | Anchors/Copy Myanmar Anchors.py | Unicode routing preset; compare Anchors/Copy Anchors From Glyph.py |
| `simoncozens/GlyphsScripts/Derive Anchors From Components.py` | `e412f65796d19ccb2ac4e94065689f79f59591f4a8c8a329373e965e7eac62fa` | Ported | Anchors/Derive Anchors From Components.py | Stacked marks use the first mark per label |
| `simoncozens/GlyphsScripts/Optical Center.py` | `4ebce47fa6aa1f02d01e94aeae9c2f664be0324ab501f7089b4fbc22e83bb346` | Ported | Anchors/Optical Center.py | Scanline column weights; the result is an estimate |
| `simoncozens/GlyphsScripts/Remove Extraneous Mark Anchors.py` | `aa7e760756505fc3c512050a533ff8f1bd568ee4662238903d8e842684e22877` | Ported | Anchors/Remove Extraneous Mark Anchors.py | Preview before removal |
| `simoncozens/GlyphsScripts/Reset Anchors.py` | `ecc00a2ae02c2cfd4daad3f32f9202273062b5f557788420447315386487c7dd` | Retired | — | FontLab's Python API has no default-anchor regeneration |
| `simoncozens/GlyphsScripts/Comb.py` | `03d1f03c58b23fe931f14726d3b2cfa8a0c2a14a14ef899a8a9e99ed240b705b` | Ported | Contours/Comb.py | Configurable ribbon strips over selected glyphs and masters |
| `simoncozens/GlyphsScripts/Curve All Straights.py` | `04d11a16498cf5bd514d8e7c7014a26f9796b7911a7a3dc258c9044d3926a27f` | Ported | Contours/Curve All Straights.py | Selected contours, mapped onto compatible layers |
| `simoncozens/GlyphsScripts/Delete Close Points.py` | `3dcc2d1a8ec36147ce111301fbcb5e7bd858e7e1f6662197519c40b61c567ccc` | Ported | Contours/Delete Close Points.py | Configurable short-segment threshold |
| `simoncozens/GlyphsScripts/Make Compatible.py` | `84c9b2a53f5a8d2bbe0d3b3cbb6388f6290080d35648ff73e0e404a74658aed9` | Ported | Contours/Make Compatible.py | Promotes lines where another master has a curve |
| `simoncozens/GlyphsScripts/Sandblast.py` | `1ffc0183ce77915de1247a5323d53113f8d3ba6881fe9b2117c0184168a4b7eb` | Ported | Contours/Sandblast.py | Seeded holes inside the filled shape |
| `simoncozens/GlyphsScripts/Straighten All Curves.py` | `d5f9e2792c96225e8f3755e73574cf6a048c9a9442bd5c4c3330ebb821646f53` | Ported | Contours/Straighten All Curves.py | Selected contours, mapped onto compatible layers |
| `simoncozens/GlyphsScripts/Superaligner.py` | `e2ab95c43e74092a73781359f04aaf26204afad96ff45dad2cc843204621f0f1` | Ported | Contours/Superaligner.py | Aligns contour order and start points with the first master |
| `simoncozens/GlyphsScripts/Interpolated Nudge.py` | `2fd131b705c61e3f56719be4e32b2234bb523bb99188511c368e3fccb429df30` | Ported | Contours/Interpolated Nudge.py | Moves selected nodes and scales their handles |
| `simoncozens/GlyphsScripts/Make bottom-left node first.py` | `ef33d8e243dd5a792e1c602906cce15318fee997538e9dd9e3a826ca9d1e562f` | Duplicate of | Contours/Optimize Start Points.py | Puts Y before X and can match a reference master |
| `simoncozens/GlyphsScripts/Round Everything.py` | `7317be694367ed39486bf412e52533f5ecf01114a9d8b6199224ee43a5a4f6db` | Duplicate of | Contours/Round Coordinates.py | Also Anchors/Round To Grid.py and Metrics/Round Advances.py |
| `simoncozens/GlyphsScripts/glyphmonkey.py` | `26f0f745b72f7a275ced449f4a82e14ab1be60df7f20abacb973f6c5f240a105` | Retired | — | Helper module with no menu action |
| `simoncozens/GlyphsScripts/Autokern.py` | `ee1095e6c7c1ba63147e367b62d888c7d708c9d37d7edc607847776124f99389` | Duplicate of | — | FontLab: Pairs panel > Autokern selected pairs, Neural mode |
| `simoncozens/GlyphsScripts/Kern Optimizer.py` | `0bbb8f5c299f09030d36c24fc678d6f28a44f9b6693bf7b5d77cd56d69be0849` | Ported | Kerning/Kerning Energy Report.py | Read-only kerning energy and spacing-bias report |
| `simoncozens/GlyphsScripts/Unbundle Punctuation Kerning.py` | `1c12b26e4e936b5e02b74057bd38542785ce3da2061fd6531c2ebaa608ca0f62` | Ported | Kerning/Unbundle Punctuation Kerning.py | Writes selected punctuation exceptions across chosen masters; classes and overrides stay |
| `simoncozens/GlyphsScripts/LightSpace.py` | `f797671e2c441d2d7c56417ea20d39692c375ca7ae4a406f9c93dfb301391128` | Duplicate of | — | FontLab: Font > Metrics > Autospace |
| `simoncozens/GlyphsScripts/Sansomatic.py` | `eca1d44b63cf835f83cd4f6385c32bdbabc950dd0657e25dc4a543a97b1a7f42` | Ported | Contours/Sansomatic.py | Fourteen geometric capitals in empty selected layers |
| `simoncozens/GlyphsScripts/Cadence Grid.py` | `ce7d7014132c9ece3f437e38c16ffd28dbcab9573c1c1fec647d64a1fe240093` | Duplicate of | Guides/Grid Generator.py | Regular vertical glyph guides with preview and master scope |
| `simoncozens/GlyphsScripts/Myanmar Medial Ra Maker.py` | `f7eae550217669cbef4a2ba2e29e474183afd3b4f0ae6cd1d9f307591fa7624e` | Ported | Contours/Myanmar Medial Ra Maker.py | Per-master extensions with a preview of every target |
| `simoncozens/GlyphsScripts/Nastaliq Connection Editor.py` | `bcb30599c055ac0cb8884154537735e30024bd7a02cbc9bdf0b97f8518163bdd` | Ported | Features/Nastaliq Connection Editor.py | Qalmi connection choices kept in managed rlig comments |
| `simoncozens/GlyphsScripts/componentize.py` | `a59f7b527cace0fce219fd300af6aa30e2eb2a77da877a00b113d42da2c76af5` | Duplicate of | — | FontLab: Font > Detect Composites; Contour > Convert > Detect Component |
| `simoncozens/GlyphsScripts/Clean Classes.py` | `a9044af7ce7697e5a9915d46682a346149eb28eb2b7f51075d05bc676a2f8271` | Duplicate of | — | FontLab: Classes panel > Clean Up Selected Classes |
| `simoncozens/GlyphsScripts/Rename To Glyphs Default Names.py` | `7174361f5f96dfee53786d9cd6623f6f2944e08a13abbff3713f0607815c78a4` | Duplicate of | — | FontLab: Font > Rename Glyphs > Alternative, or Rename by Table |
| `slobzheninov/Glyphs-Scripts/Align/Align Top.py` | `e8114804848e24f812fa3398b1728ffa2f4de96ffa246cc303cb1d6459b88cf3` | Ported | Contours/Align And Distribute.py | Combined alignment and node distribution panel |
| `slobzheninov/Glyphs-Scripts/Align/Align Bottom.py` | `fff9a46cdaf6b96ae12da6e6e4cb7e38c06922f9815304f2f3c02aa4b5f33136` | Ported | Contours/Align And Distribute.py | Combined alignment and node distribution panel |
| `slobzheninov/Glyphs-Scripts/Align/Align Left.py` | `7a8533e0ea2d5e7b07bfa4ad57051080829cb54abedbdde67cb11c359defdb49` | Ported | Contours/Align And Distribute.py | Combined alignment and node distribution panel |
| `slobzheninov/Glyphs-Scripts/Align/Align Right.py` | `301640d438c4502cc419cc6156afa0b9c50b5667843ebe17b0f805e39246e9c8` | Ported | Contours/Align And Distribute.py | Combined alignment and node distribution panel |
| `slobzheninov/Glyphs-Scripts/Align/Align Horizontal Center.py` | `857e2e396605a10cd3abb9041ee6f4f6ccc91c0c271a920c4aeb8336620d5f95` | Ported | Contours/Align And Distribute.py | Combined alignment and node distribution panel |
| `slobzheninov/Glyphs-Scripts/Align/Align Vertical Center.py` | `4d85757975b721875f75b66624b9f2280647921780e4214fa26e281468658838` | Ported | Contours/Align And Distribute.py | Combined alignment and node distribution panel |
| `slobzheninov/Glyphs-Scripts/Align/Distribute Nodes Horizontally.py` | `3d1bd75c4919286408fb834db1e47e42cb052fff6790e25b9a71908e3c7eb308` | Ported | Contours/Align And Distribute.py | Combined alignment and node distribution panel |
| `slobzheninov/Glyphs-Scripts/Align/Distribute Nodes Vertically.py` | `8364cfc28c75bcfa25dfae44f296aff3f8773e899d5ad97a4b40f1ed1c9ca9db` | Ported | Contours/Align And Distribute.py | Combined alignment and node distribution panel |
| `slobzheninov/Glyphs-Scripts/Align/Center Selected Glyphs.py` | `cd0fc2aac081093264e77f86267e76f9fbf42f33eadde93eff92684600b27141` | Duplicate of | Metrics/Centre In Advance.py | Equal sidebearings with the advance kept, in the current or all masters |
| `slobzheninov/Glyphs-Scripts/Rotate/Rotate.py` | `3878c0c231670ab72d6649d703d7d6aa76e9f940c1d8b38f3f01b262d8e8835e` | Ported | Contours/Rotate Selection.py | Preview and six rotation presets over several layers |
| `slobzheninov/Glyphs-Scripts/Rotate/Rotate 1 CCW.py` | `061d519ae5d296fc01395b7e810c5ea1c45ad1ab9a536143fb1b52d89440eca3` | Ported | Contours/Rotate Selection.py | Preview and six rotation presets over several layers |
| `slobzheninov/Glyphs-Scripts/Rotate/Rotate 1 CW.py` | `b70cffef7c0e675220499dd51b1978bbaeb1dde8cb74e9ae55a21b78681cd5d6` | Ported | Contours/Rotate Selection.py | Preview and six rotation presets over several layers |
| `slobzheninov/Glyphs-Scripts/Rotate/Rotate 10 CCW.py` | `273de5fae7847b77ac75e99dc59b4d5170156c13b1ba5f5694138a16109c003a` | Ported | Contours/Rotate Selection.py | Preview and six rotation presets over several layers |
| `slobzheninov/Glyphs-Scripts/Rotate/Rotate 10 CW.py` | `e1243a56bdf051d421d3a053c2d1f4818b918bf7aa03425fda3c1f1128c0cd47` | Ported | Contours/Rotate Selection.py | Preview and six rotation presets over several layers |
| `slobzheninov/Glyphs-Scripts/Rotate/Rotate 45 CCW.py` | `c9d513f3460824f2198c11244f6e35feea7bdf9887fa7e97369b844cd83fa5dc` | Ported | Contours/Rotate Selection.py | Preview and six rotation presets over several layers |
| `slobzheninov/Glyphs-Scripts/Rotate/Rotate 45 CW.py` | `8fe8ac5c043d800b1f7ae0ebb04327e3ed8e3055b13b9857f855482447681524` | Ported | Contours/Rotate Selection.py | Preview and six rotation presets over several layers |
| `slobzheninov/Glyphs-Scripts/Reflect/Reflect Horizontally.py` | `104bf20424822eff74014cc9adfcbc4e7c99433938027ebc6d4ab3b188faf509` | Ported | Contours/Reflect Horizontally.py | Preview over several masters or selected layers |
| `slobzheninov/Glyphs-Scripts/Reflect/Reflect Vertically.py` | `0fa06c54283284c67e7b9bb6fd3ef74670c87e5d39cd67c4c7bd65b365c8c8d6` | Ported | Contours/Reflect Vertically.py | Preview over several masters or selected layers |
| `slobzheninov/Glyphs-Scripts/Overlap nodes.py` | `a03d0dac0525058b61f21d90dbec32dba0f518174890968001e42dda8334c5c8` | Ported | Contours/Overlap Nodes.py | Coincident terminal nodes; each layer uses its own master's italic angle |
| `slobzheninov/Glyphs-Scripts/G2 Harmonize.py` | `0df687bc3655639abe762bb85482995d5c71875b910e4f6bceb21bf3a57015d9` | Duplicate of | — | FontLab: Contour > Harmonize |
| `slobzheninov/Glyphs-Scripts/App/Next Layer in Selection.py` | `88920dc422888c76c67e0272be60d2b66bf69dcd37c010bb89196875b2c4de33` | Ported | Masters/Selection Layer Navigator.py | Shared layer name across the selected slots |
| `slobzheninov/Glyphs-Scripts/App/Previous Layer in Selection.py` | `61b8a858c12ae358d9c7b34d50d4504d697e852008836ea94d53f5a036d563b8` | Ported | Masters/Selection Layer Navigator.py | Reverse order, with wrap-around |
| `slobzheninov/Glyphs-Scripts/App/Toggle Axis 1.py` | `406b9c7ee2d469613d73f31831c02ba19f79d800959ce79a9910789f13478bcb` | Ported | Masters/Selection Layer Navigator.py | First font axis; other coordinates stay fixed |
| `slobzheninov/Glyphs-Scripts/App/Toggle Axis 2.py` | `90fdf02efad3855a453bf54de2c5472af80e3d4dad0de6af98846921f421052e` | Ported | Masters/Selection Layer Navigator.py | Second font axis |
| `slobzheninov/Glyphs-Scripts/App/Toggle Axis 3.py` | `c311a0d8c84c57a2822eb8b2c9ceea1f8b15977c9f669535e1cfce3f1a1fc37b` | Ported | Masters/Selection Layer Navigator.py | Third font axis |
| `slobzheninov/Glyphs-Scripts/App/Toggle Axis 4.py` | `74eb5767a8f73c5620f6b6502cfe80b018fe48cd2d8ac3f8d9c094c96f3c3dfc` | Ported | Masters/Selection Layer Navigator.py | Fourth font axis |
| `slobzheninov/Glyphs-Scripts/App/Toggle Italic.py` | `e0295f24e4c11ac78a22453b1cb5ac9c90b14b059c5ca0c80e98048ce993ca0e` | Ported | Masters/Selection Layer Navigator.py | First axis tagged ital or slnt |
| `slobzheninov/Glyphs-Scripts/App/ToggleAxis.py` | `15acd39efb73e888fae5bc49ab3185597b6c7669bcc2c05306582b06dc28861f` | Ported | Masters/Selection Layer Navigator.py | Coordinate order, intermediate layers and Font-window master cycling |
| `slobzheninov/Glyphs-Scripts/App/Fit Zoom.py` | `1306c2986526958d9bd3985b3aa11084b667aed67d975dee3b405837cd84e26b` | Duplicate of | — | FontLab: View > Zoom > Fit Content on Screen (Ctrl+0), Fit Selection, Fit Text on Screen |
| `slobzheninov/Glyphs-Scripts/App/DarkMode.py` | `7f4005ca06a04604166dd5da380b35ed574f0b1c8555b58dc599658610251b19` | Duplicate of | — | FontLab: Preferences > Glyph window > Dark preview |
| `slobzheninov/Glyphs-Scripts/App/Floating Macro Panel.py` | `0a0bc39c3817767cc820793c2de9f933a7958ddb5b5fddd324baedd33634d8b0` | Duplicate of | — | FontLab: Window > Panels > Python |
| `slobzheninov/Glyphs-Scripts/Kerning/Delete Kerning Pair From All Masters.py` | `af7181ba8532fa53fd91f77be6b72743d2fc377807b4e1799ac2ce54229ba38e` | Ported | Kerning/Delete Kerning Pair From All Masters.py | Consecutive selected pairs in every master; exceptions are listed |
| `slobzheninov/Glyphs-Scripts/Kerning/Kern to max.py` | `421f9b3ebb4c372028fc1da2202b235cf991ccc5a77bcf42a47eba68c54d8a5c` | Ported | Kerning/Kern To Max.py | Minus half the narrower advance |
| `slobzheninov/Glyphs-Scripts/Kerning/Steal Kerning From Next Pair at Cursor's Y.py` | `9a739f05008da5d1127210a02c539d1f29015fe8f17f5741e37f49b5abfac54e` | Ported | Kerning/Steal Kerning From Next Pair.py | Matches the gap of the next pair at a chosen height |
| `slobzheninov/Glyphs-Scripts/Features/Generate Random Alternates Feature.py` | `1db8d95fe4a22899c837f3d3434e556f56f8fe8baf252e358f90f2f6d50fc23b` | Ported | Features/Generate Random Alternates Feature.py | Replacing an existing feature needs explicit consent |
| `slobzheninov/Glyphs-Scripts/Glyphs/Reorder Shapes.py` | `1b9b525c8ceab4dbd6f87600db76aa9c58b93859ce88a73beb8918e8c45a20c9` | Ported | Masters/Reorder Shapes.py | One shape order per glyph, applied to matching master layers |
| `slobzheninov/Glyphs-Scripts/Glyphs/Show All Layers.py` | `45e501e6b106f4dea12bea30d85fd58fd61d76c03736112bb1ba846a4db9974a` | Ported | Masters/Show All Layers.py | One proof row with every foreground layer of the selected glyphs |
| `slobzheninov/Glyphs-Scripts/Glyphs/Copy Missing Special Layers.py` | `12c3a2089edfe15457269a4469c9bbe288e542b2198cc14886bb50fa4e81924c` | Retired | — | FontLab has no Glyphs special-layer conditions |
| `slobzheninov/Glyphs-Scripts/Bug fixing/Report Compatibility.py` | `c0de8a4fd7575124844b4b40d3a7933b2acc270d853d9c7139aabe32f49d870d` | Duplicate of | Masters/Compatibility Check.py | Base report only; the export-flatten and overlap-filter states have no FontLab counterpart |
| `pedroarilla/glyphs-scripts/Cleaning/Delete annotations in all layers.py` | `82838681c8e724d03df29eef224004987219545d4dc4e22010bb2030d0b50ebf` | Ported | Cleanup/Delete Stickers.py | All layers scope |
| `pedroarilla/glyphs-scripts/Cleaning/Delete annotations in all master layers.py` | `50d9ebf21b3eca495c209f303ae7948b826ff1b78b8230777fa470fa6026e16f` | Ported | Cleanup/Delete Stickers.py | Master layers scope |
| `pedroarilla/glyphs-scripts/Cleaning/Start-from-scratch.py` | `037559e07623da4fd19839bb9e7d1b201ee2e905ff49d88210bde9755fca2f0b` | Ported | Cleanup/Start From Scratch.py | Cleanup checklist with Preview and default-No confirmation |
| `pedroarilla/glyphs-scripts/Components/Decompose all corner components.py` | `79a44fd215323326467f70044ebff6c250f573e74a4320c4512689cb8230ea88` | Retired | — | FontLab has no named corner-component attachment model |
| `pedroarilla/glyphs-scripts/Components/Decompose all serif components.py` | `b093222bbb5dd82f125dc625b3f11ac320056c3344f6e9452be59115f29b5891` | Ported | Components/Decompose Serif Components.py | Serif base-name prefix, one level; compare Components/Decompose Named Components.py |
| `pedroarilla/glyphs-scripts/Components/Make component glyph for all masters.py` | `6b95a4b10599a7b933975baa3700d4d40d29cd084c6c320faa10e3ec80d32f32` | Duplicate of | — | FontLab: Font > Build Glyphs (Characters mode, Rebuild existing glyphs, All masters) |
| `pedroarilla/glyphs-scripts/Components/Make lower-unicase font.py` | `ee6e66937cca4d86050b4d5bc7fe97fb6eb6077a4325676015fe6b9fa90adba8` | Ported | Components/Make Lower Unicase.py | Lowercase components in uppercase cells on all masters |
| `pedroarilla/glyphs-scripts/Components/Set default figures.py` | `33dcbede25dadf7a98a435e4e334571c75d8db2ab8dfde84a55c7e9193b7158e` | Ported | Components/Set Default Figures.py | Chosen figure set as the default digits on every master |
| `pedroarilla/glyphs-scripts/Paths/Make zero handles selected glyphs.py` | `bbc177fd99ed4ba204bacd93c79d808f14e5a0622ccf6912e8287a1c23841fe2` | Ported | Contours/Retract Handles.py | All handles |
| `pedroarilla/glyphs-scripts/Paths/Make zero handles selected nodes.py` | `96eba1b2fb939b225bc792621780089edce1208ef8dd11cacba319b1f67e6cd8` | Ported | Contours/Retract Handles.py | Handles of the selected nodes |
| `pedroarilla/glyphs-scripts/Paths/Simplify selection.py` | `6c784fc646dd94b012b9b6172e3074232e43fd0af31100cdd4e2523ec88ea8a4` | Ported | Contours/Simplify Selected Nodes.py | Alternate-node removal from selected polygon nodes |
