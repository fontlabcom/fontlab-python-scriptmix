---
this_file: README.md
---

Common Glyphs now calls App for the complete original report: family order,
first-open-font primary character strings, stored nice names, caller-verified
GlyphData production names and explicit unknowns, exact trailing spaces and all
alternative encodings. One font retains glyph order; multi-font names are sorted.
Escaped JSON retains exact source strings. Ordinary selection copying can
normalize Unicode spaces/separators; explicit Copy Characters/Copy Original Report
actions stage exact source MIME data. Native callbacks/OS clipboard handoff and
rendering remain unqualified.
The owned report needs no current font and never clears Output. Its optional
charcoal control is visible, unchecked and unavailable under FontLab issue 8564.
This partial source milestone leaves the full all-font action and native report
acceptance open; it does not complete the original workflow.

Master Text Comparison restores the original preset/custom workflow, usable-character sanitation, exact master-copy delimiters and owned settings. It stages named glyph/layer symbols in a fresh proof; native model binding, rendering and full preservation remain unqualified. Multiline/paragraph custom input is held explicitly; exact UTF-8 presets retain those scalars.


# FontLab practical scripts

242 practical tools for FontLab 9: 69 sample adaptations and 173 additional
tools. Scripts inspect, proof and edit fonts through FontLab's native APIs,
PythonQt and shared App helpers. The menu has 14 one-level categories.

Current source includes Metrics, Names and Anchors editors; component writers;
master navigation, backups and layer copying; contour editing, generators and
hint tools; feature tools; kerning editors; proof texts; reports and drawing panels.
The [porting backlog](PORTING-BACKLOG.md) records source dispositions and gaps.

New ports require native acceptance. Source tests do not establish correct
FontLab Undo/Redo, saved font state or panel lifetime. Historical sample
acceptance remains 68 of 130; the Italic Angle candidate and later ports retain
their separate checks. Menu counts describe available source files.

Writers disclose queued native glyph ids and the possible modification-date changes
(FontLab issue 8537). They never clear the queue or normalise unrelated dates.

Case Coverage provides the original four report controls, complete detached
case diagnostics and an explicit existing-view chooser when inactive views are
ambiguous. GlyphData metadata is supplied by the Scriptmix caller. Exact native
text-block binding and proof usability remain unqualified; a capability refusal
is not native acceptance.

## Requirements and installation

Use FontLab 9 with embedded Python 3.11 arm64 on Apple Silicon. Keep matching
versions of `fontlab-fly`, `fontlab-fontlabapp` and `fontlab-fontport` available
to FontLab. Some tools use the App `fontui` extra. Trial Font Maker needs the
public `fontTools` package; FontLab's private namespace does not supply it.
Glyport supplies Glyphs-specific compatibility and category metadata where used.

Every recorded `app_minimum` uses the conservative source baseline
`0.2.26.dev159`, matching the genuine App development-version lineage. This is
not an earliest historical per-tool minimum or proof of full compatibility.
The tested App159 artifact still lacks the pending zone handoff, and the full
Scriptmix gate remains failing. Native workflow acceptance and promotion remain
open. Historical per-tool labels are retained in Git history and old receipts.

Editable installation into FontLab is owner-managed. Do not install packages
into FontLab, replace its Qt bindings or change its Python site-packages from
a test command. This repository is a menu collection, not an installable
runtime Python package. Its `pyproject.toml` configures documentation tools.

After the owner provisions dependencies:

1. Open FontLab's Scripts folder from the application.
2. Copy the category folders inside this repository's `Scripts/` into it.
3. Keep the layout `Scripts/<Category>/<Tool>.py`; FontLab accepts only one
   category level. Do not add a second nested folder.
4. Open a copy of a font. Select the required glyphs and master, then choose
   the tool in FontLab's Scripts menu. Read its source docstring for controls,
   supported scopes and refusals.

Use a dedicated FontLab session and owned fonts for acceptance tests. Keep
normal work and original fonts outside that session.

Reports > Smallcap Consistency checks the complete exporting case set and capital kerning groups in a read-only snapshot. It uses the `public.skipExportGlyphs` compatibility policy, exact SC suffix particles and Unicode/name-table mappings; unknown names and ambiguous groups remain visible. Run again to refresh the same report. This tool requires the matching issue-123-smallcaps App implementation; no published version floor is asserted for the new helpers.

## Examples

- **Metrics > Scale Advances**: select glyphs in the Font window, choose current
  or all masters, enter a percentage, inspect the preview and press Apply.
  The outline stays centred. Automatic layers and unsafe dependencies are kept
  or refused. A failure after a write asks for Edit > Undo.
- **Masters > Duplicate Current Layer**: back up the current master or all
  masters of selected glyphs with a custom suffix. Existing backups appear in
  an inventory. Names use `<master> backup <suffix>` with collision numbering.
- **Masters > Copy Layer Between Masters**: select the source and tick target
  masters. Changing the source selects all other masters again.
- **Contours > Round Coordinates**: round nodes, component offsets and, by
  default, anchors. Untick Anchors to keep their coordinates. Duplicate-anchor
  layers and an anchor move to the origin are kept with a diagnosis.
- **Names > Duplicate Unicodes**: scan the whole font, choose assignments to
  keep or remove, close Glyph editors and activate the Font window before Apply.
- **Proof > Text Filter**: simplify text with persistent input/output and regex
  fields. Reset keeps input; New Tab uses the font captured when the tool opened.
- **Utilities > Text Holder**: keep proof text in an editable persistent window;
  Find and replacement operate on the selection or whole text. Save keeps the
  panel open. See the [Text Holder guide](docs/text-holder.md).

Read-only tools can change selection, open tabs or show panels. Source getters
also need native preservation checks. Writer history descriptions state the
intended operation; new ports still need actual Undo/Redo and save/reopen proof.

## Files and modules

| Path | Purpose |
| --- | --- |
| `Scripts/` | Practical menu entry points; typed Python 3.11, lazy Fly imports. |
| `menu_layout.py` | Resolve current paths and verify historical release bytes. |
| `migration.json` | Historical sample source/destination paths and hashes. |
| `menu-moves.json`, `menu-revisions.json` | Explicit path and comment overlays. |
| `additional-tools.json` | Additional tool provenance, current hashes and status. |
| `rescue-index.json` | Retired launcher identities and external source hashes. |
| `original-provenance.json` | Additional upstream source and resource identities. |
| `PORTING-BACKLOG.md` | Ported, duplicate and unavailable behaviour dispositions. |
| `tests/`, `test.sh` | Offline menu, helper, provenance and portability checks. |
| `tests_docs/` | Documentation source-inclusion and licence distribution tests. |
| `src_docs/build.py`, `src_docs/mkdocs.yml` | Catalogue generation and strict site build. |
| `src_docs/md/` | Authored site pages and generated menu pages. |
| `.build/menu-sources/`, `.build/site/` | Generated source snapshots and site output. |
| `docs/` | Retained guides; some early examples use historical layouts. |
| `NOTICE`, `LICENSE` | Attribution and licence terms. |

Shared code is supplied by sibling packages. General panels, native guards,
planners and history helpers belong in `fontlabapp`, reached as `fly.ap`.
Feature source uses `fly.fp.feature_blocks`. Fontport holds fontParts/UFO
integration; Glyport holds Glyphs.app compatibility. Scripts do not load other
menu scripts as libraries. No `lessons` package is shipped here.

`migration.json` is a frozen v0.2.0 record, not current pins.

## Runtime tests

Prerequisites: a prepared Python 3.11 arm64 test `.venv` with pytest, glyphsLib and the
matching App and Fontport packages installed, plus App test dependencies.
Use the sibling Fly checkout on PYTHONPATH. Set
`SCRIPTMIX_TEST_VENV` to that prepared environment's absolute path. It must be
separate from the documentation `.venv`, which uses Python 3.12 or later.
Run from this repository root:

```sh
export PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1
export UV_CACHE_DIR="$TMPDIR/fontlab-scriptmix-uv-cache"
export PYTHONPATH="$(cd ../fontlab-fly/src && pwd)"
unset SCRIPTMIX_APP_SOURCE SCRIPTMIX_FONTPORT_SOURCE
VIRTUAL_ENV="$SCRIPTMIX_TEST_VENV" uv run --active --no-project \
  --python cpython-3.11-macos-aarch64-none \
  python -B -m pytest -q -p no:cacheprovider tests
```

The full suite regenerates menu documentation in place. Run it when those
outputs may be refreshed. To provision an isolated dependency set instead,
`test.sh` accepts explicit App and Fontport wheels or checkouts:

```sh
export SCRIPTMIX_APP_REQUIREMENT="/absolute/path/to/fontlab_fontlabapp-0.2.26.dev159+gb1e905b61-py3-none-any.whl"
export SCRIPTMIX_EXTRA_REQUIREMENTS="/absolute/path/to/fontlab_fontport-1.0.3.dev19+g3ddbd097f-py3-none-any.whl"
export SCRIPTMIX_PYTHON="cpython-3.11-macos-aarch64-none"
sh test.sh -p no:cacheprovider
```

Supply existing reviewed artifacts with genuine build metadata; do not override
package versions. Use a freshly built matching wheel or an approved prepared environment when
validating changed dependencies. Cached builds with the same development
version can be stale. These tests do not modify the live FontLab installation.

Lint checks existing source without rewriting it. Ruff 0.14.10 reports 87
existing findings across the paths below; fixes remain open:

```sh
uv run --no-project --python cpython-3.11-macos-aarch64-none \
  --with ruff==0.14.10 ruff check --no-cache --target-version py311 \
  Scripts tests tests_docs menu_layout.py src_docs/build.py
```

## External original-source audits

Default tests verify recorded paths/hashes and current files without original
source bytes. Historical `rescued/...` paths identify an external archive:
`fontlab-python-scriptmix-rescued.tar.gz`, SHA-256
`ffa611cfec3f2550400989abff51cea1a391d714a91ea4863ca0610711dd4b32`.

Restore it outside the repository. Set `FONTLAB_PRESERVED_ROOT` to the directory
containing `rescued/`. To the prepared runtime pytest command, or to `test.sh`,
append `--audit-rescued-sources --original-source-root /path/to/workspace`.
The workspace path contains `fontlab-python-examples`; it enables the Masters,
Proof, Reports and Inspectors original-source comparisons.

An absent source root skips the corresponding optional byte audit. A present
archive with a missing file or mismatched hash fails. The full archive audit
collects all missing/mismatched entries before failing. Current-file checks
remain mandatory. Audits read archived bytes; they do not execute originals.

## Documentation tests and build

The documentation tests can run independently on arm64 Python 3.11. They need
pytest, the real codeinclude plugin and PyYAML; this command supplies them.
Put uv cache and temporary fixtures in external scratch space. Git distribution
tests use temporary repositories and require a working Git executable on PATH.

```sh
PATH="/opt/homebrew/bin:$PATH" PYTHONDONTWRITEBYTECODE=1 \
  PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 \
  uv run --no-project --python cpython-3.11-macos-aarch64-none \
  --with pytest --with mkdocs-codeinclude-plugin==0.3.1 --with PyYAML \
  python -B -m pytest -q -p no:cacheprovider tests_docs
```

The full site SDK requires Python 3.12 or later, as declared in `pyproject.toml`.
It uses the locked ProperDocs/MaterialX stack in its own prepared `.venv`.
`./build.sh --offline` syncs that environment, regenerates the catalogue and
builds the site strictly. Offline builds require all locked dependencies cached.
`./build.sh --serve --offline` starts a local preview. Generated output stays in
`.build/site/`; authored guides in `docs/` are kept. Local tests and builds do
not prove site publication or complete browser-asset licence review.

## Licence

Masters contains Overview, Width Chart, Glyph Weight Chart and Compatibility Check.
Overview shows ordered axis locations/metrics/angles, highlights differences and switches master on double-click.
Width Chart retains12labelled glyph lines; Weight Chart retains10groups, per-master bars/legend and a units² table.
Area uses12-step curves, counter nesting and transformed components; overlaps count twice. Missing widths are absent, missing weight layers0.
Compatibility retains selected/whole-font scope, expandable structural counts, anchor names/component order, auto notices and Select ✗ Glyphs.

Use an App wheel built from the current checkout, or that wheel with its updated source override; earlier wheels lack these helpers.
All four stay bound to their original font. Failed reads stay visibly diagnosed and closable; changed source/master domains or Whole-font membership refuse actions.
Native acceptance on FontLab9.0.9784 passes43original workflows,8complete font/workspace/history checks,
12realpaint controls (axis coverage/six-event settling),24opening faults,43safety and actualClose4/4.
All67exercised source hashes match; fresh chart screenshots confirm the713clipping fix. Font design/history is preserved.
App480/actual-wheel Scriptmix413 and163installed tests each for wheel/sdist pass; all63Appproduction files match.
All45mappings pass; the prior41menu bytes/rows stay exact. Separate chooser8+7checks use fix1 artifacts with unchanged chooser/common source. Same-wheel all41prior tools pass; combined45:379workflows/115preservation/166safety/116error controls/Close45.
No package-index publication is implied. Full Issue111/archive cleanup and held7Names editors stay separate; original sources remain retained.

Metrics and outline inspectors: Spacing String Preview, Width Table, Contour Order View and Node Statistics retain complete controls, raw winding/counts, actual outlines/advances, all masters and exact flagged selection; lazy `inspectors_api()`/dialog/views share lifecycle, snapshots and painter containment.
Installed-wheel FontLab 9.0.9784 acceptance passes41 original workflows/8 complete saved font/design/classes/metadata/workspace/history/master checks/10 paint/24 opening/59 safety/Close 4;70 source hashes match and imports restore; Node has its exact fresh post-seed baseline. Seven images were inspected; all 15 final images are byte-identical to retained v1.
App 497 source and actual-wheel Scriptmix 501 passed, 1 skipped;180 installed tests each for wheel/sdist pass on arm64Python3.11.14. All 66 production files and49 mappings match; previous 45 menus/rows stay exact and72 wheel/116 sdist entries pass license/NOTICE/privacy audits.
Same-wheel prior 45regression passes379 workflow/115 preservation/166 safety/116 error controls/Close 45,113 source hashes and import restoration; combined 49 native:420/123/225/150/Close 49. Historical 15 chooser receipts use unchanged code; no fresh chooser run is claimed. Use an App wheel built from the current checkout; `SCRIPTMIX_PYTHON=cpython-3.11-macos-aarch64-none ./test.sh` selects the host architecture. Full 130-stem/archive/held 7 Names work stays open; no original removal or index publication.

## Read-only Components (native acceptance)

Compatibility compares ordered component lists across masters and selects mismatches.
Count Badges draws placed outlines with own contour/component/auto counts per master.
Missing Bases groups missing glyphs/layers and unnamed bases; its simulated scan is retained.
Report preserves every composite layer, offsets, current/all-master filtering and Copy CSV.
Where Used indexes all masters in font order, with search, row selection and Select all.
Use a current App wheel with lazy components helpers; actions reject changed source/font/master/membership and Close releases signals/paths.
FontLab9.0.9784 passes33original workflows/10complete font/workspace/history checks,5paint/30opening/80stale/16painter/6selection controls/Close5;81hashes and restored imports match. Eight images were inspected; valid falsey-current A retains its badge fallback.
App506source tests, actual-wheel Scriptmix620/1skip, Git-free619/2skips and189installed tests each for wheel/sdist pass;69runtime files and54source pairs match, prior49menus/rows exact. License/NOTICE/privacy audits pass75/120payload entries; clipboard tests use a fake only.
Same-wheel prior49passes420workflow/123preservation/225safety/150error controls/Close49; combined54native:453/133/305/201plus6selection/Close54. Historical chooser receipts remain separate.
Reviewed Appv0.2.13/Scriptmixv1.0.9 releases pass independent downloaded-tag/native acceptance;54/130released,76pending(held7Names+69other stems). All originals remain; full migration/archive cleanup/additional tools/reporters/docs stay open.
Anchors: Cloud View, Compatibility Report and Mark Attachment Preview retain full controls, real outlines, all-master anchor clouds/families/offsets and visible mismatch columns. FontLab9.0.9784 passes20original workflows/6complete preservation/10paint/18opening/63stale/32painter/10selection-layout/Close3;80hashes/import restoration pass. Same-wheel prior54passes; combined57native473workflow/139preservation/368safety/261error plus16selection-layout/Close57. App512/actual-wheel Scriptmix684+1skip/all57pairs;195installed tests per wheel/sdist,72runtime and78/124payload license/privacy pass. Reviewed Appv0.2.14/Scriptmixv1.0.10 pass independent downloaded-tag R053; all14images match. Released57/130;73pending(held7Names+66unmigrated). All originals and broader cleanup/reporters/docs remain in scope. Read-only glyph reviews: Select Unreferenced Glyphs preserves all reference rules and fixes native feature-tag iteration (exact395Rafi list/selection); Interpolation Preview draws full blended nodes/paths. FontLab9.0.9784 passes10workflows/4complete preservation/5paint/12opening/39stale/16painter/6selection-layout/Close2;86hashes/restored imports. Prior57same-wheel passes; combined59native483workflow/143preservation/407safety/294error plus22selection-layout/Close59. App533/actual-wheel Scriptmix707+1skip/all59pairs/Git-free706+2skips/216installed per wheel-sdist;76runtime82-130payload licence/privacy pass. Reviewed Appv0.2.15/Scriptmixv1.0.11 pass independent downloaded-tag R053; all7images match. Released59/130;71pending(held7Names+64unmigrated). All originals/archive/reporters/docs remain in scope. Live Node Coordinates: open a glyph, run Outlines > Node Coordinates Panel and select nodes; both tables follow edits every400ms. Copy exports displayed coordinates as tab-separated lines; no font edits. Font switch/close stops polling until reopen; failed reads clear tables. Requires the current App node_coordinates helper. Reviewed Appv0.2.16/Scriptmixv1.0.12 pass independent downloaded-tag R053:7original/2complete preservation/24native controls/Close1,81hashes and6exact inspected images; prior59same-production-byte regression passes. App541/installed224each/Git-free Scriptmix720+2explicit skips/all60source pairs pass. Released60/130;70pending(held7Names+63unmigrated); originals/archive/reporters/docs remain in scope. Master Switcher: Masters > Master Switcher shows ordered master/location buttons, current bold/check state and the first nine shortcuts. Three columns fit larger fonts. It sets the font package master; editor-layer switching is not claimed. Reviewed Appv0.2.17/Scriptmixv1.0.13 pass fresh downloaded-tag R053:5original/2complete preservation/43controls/Close1,82hashes/restored imports. All four screenshots freshly inspected; selected-bold text pixels differ from candidate, while geometry and labels match. App546/installed229each/Git-free733+2explicit skips/all61source pairs pass; prior60same-runtime regression passes. Released61/130;69pending(held7Names+62unmigrated). All originals/archive/reporters/docs remain in scope. Guides > Font Guides Panel, Grid Generator and Metric Reference Lines retain all original glyph-guide controls and the actual grid outline preview. Use current/all masters; Font Guides Panel lists font-wide names but writes glyph guides only. Automatic dependants are refused before history because FontLab cannot restore their dates. Safe edits use one Undo step; stale source clears the panel. Reviewed Appv0.2.18/Scriptmixv1.0.14 downloaded-tag native acceptance passes27original/21complete persistence/167additional controls/Close3, including two glyphs, differing master metrics, prior Undo history and no-ops. All14screenshots inspected;83runtime/64source pairs and245installed tests per wheel/sdist pass. All14release images match the inspected candidate. Prior61same-runtime regression passes; combined64:522workflows/168preservation/957controls/Close64. Released64/130;66pending(held7Names+59unmigrated). All originals and broader examples/archive/cleanup/newtools/reporters/docs remain in scope. Guide rewrite editors: Clear Glyph Guides retains direction/name/current-all filters; Copy Guides Between Masters retains explicit targets, merge/replace and width-scaled angled guides; Guide List Editor retains first-glyph editable rows and Add/Delete/Revert. Requires Appv0.2.19. Retained native guide properties and hints survive; nonfinite cells, unknown masters, unsafe automatic dependants and stale scale widths refuse whole writes. Reviewed Appv0.2.19/Scriptmixv1.0.15 downloaded-tag acceptance passes19original/21complete persistence/162controls/Close3,96hashes/restoredimports and13exact inspected images. Prior64same-runtime regression passes; combined67:541workflow/189preservation/1119controls/Close67. Released67/130;63pending(held7Names+56unmigrated). All originals and broader examples/archive/cleanup/newtools/actual canvasreporters/docs remain in scope. Copy Anchors From Glyph retains full L1 source completion, merge/replace, width scaling and current/all-master controls. Reviewed Appv0.2.21/Scriptmixv1.0.17 pass fresh downloaded-tag R053:11original/7complete font-history-reopen/133controls/Close1,93hashes/restoredimports. All14images match inspected candidate geometry/content; four cursor blinks differ. Refusals for automatic dependants and existing-anchor origin moves precede mutation (fl#8512/fl#8527); explanations fit above a short footer. Earlier v0.2.20/v1.0.16 tags remain intact after numerical success but visual rejection. App597, GitfreeScriptmix770+1explicit skip/all68pairs and280installed tests per wheel/sdist pass;89runtime/95wheel/149sdist payload licence/privacy pass. Prior67same-runtime regression passes; combined68=552workflows/196preservation/1252controls/Close68. Released68/130;62pending(7heldNames+55unmigrated). All originals and broader examples/archive/cleanup/newtools/actual canvasreporters/docs remain in scope.

## Additional read-only tools

These two new tools require fontlab-fontlabapp 0.2.25 or newer.

Kerning > Persistence Audit lists explicit pairs, including zero, for the current
master or all masters and highlights values outside the measured FontLab VFJ load
limit of twice the UPM. It offers filtering and Refresh without changing font
selection or kerning.

Reports > Compare Open Font Revisions compares explicitly chosen open fonts and
masters. It shows glyph/layer/master presence, advances, ordered local contour
geometry, raw node state, anchors and component reference layers. It reports named
fields; other font data is outside this comparison. Refresh after external edits.
Both panels have explicit Close and release owned callbacks when destroyed.

These are additional original tools. The original migration remains68/130; broader
source rescue and pending editors are tracked separately. This isolated candidate
requires installed-artifact, native regression and release gates before promotion.
