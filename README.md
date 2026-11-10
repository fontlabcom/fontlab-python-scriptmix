---
this_file: README.md
---

Batch UFO Recipe Workbench is available through `fontlabapp.fontui.batch_recipes.show(parent=None, python=None)`. Use the real affine recipe controls without opening a font or geometry preview, then explicitly select UFO sources, an output directory and Python 3.11+ with Fontport. Start writes new outputs; existing files and destinations inside any input UFO are refused. The actual panel shows per-file results, progress and failures. Cancel stops between files and retains completed outputs. Closing transfers an active run to supervision; terminal cleanup and independently reopened outputs are separate observations. Source review, ordinary artifacts and native qualification remain distinct.

Detached Transform Preview is available through `fontlabapp.fontui.detached_transform.show(font, parent=None)`. Run **Font UI Lab > Detached Transform Preview**. Choose an explicit layer and glyph, then Capture to compare the backend-stored snapshot with an affine result. Refresh reads the same captured font; borrowed caches and pending edits remain untouched. Settings Save creates only a chosen new JSON file, and Show script displays text without executing it. No font Apply/save/export is provided. This workflow is independently source-qualified. Combined-main review, matching ordinary installation and native behavior remain pending.


Feature Source and Proof is available through `fontlabapp.fontui.feature_proof.show(font, parent=None)`. It keeps the ordinary code view, refuses unsupported input before selection loss, and quarantines opaque document changes until explicit Revert. Accepted source Apply refreshes the independent Unicode/kerning sequence once; it does not compile or shape OpenType features. The window captures one borrowed font. External changes retain dirty drafts with a warning; explicit Apply can overwrite newer source. Refresh proof retries only the view. Original paragraph separators are inspect-only. Focused checks confirm exact UFO source preservation through the backend and editor for CR, CRLF, mixed endings and absent final newlines, including untouched siblings; duplicate feature tags are inspect-only. This workflow is source-qualified by complete App, Fontport and Scriptmix suites; ordinary artifacts, native history/reopen and full literal-U+2029 editing remain separate pending gates. Native PythonQt/FontLab, full literal paragraph-separator editing and broader clipboard routes remain unqualified.



# FontLab practical scripts
272 practical tools for FontLab 9: 69 sample adaptations and 203 additional
tools. Scripts inspect, proof and edit fonts through FontLab's native APIs,
PythonQt and shared App helpers. The menu has 15 one-level categories.
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

## Requirements and installation

Use FontLab 9 with embedded Python 3.11 arm64 on Apple Silicon. Keep matching
versions of `fontlab-fly`, `fontlab-fontlabapp` and `fontlab-fontport` available
to FontLab. Some tools use the App `fontui` extra. Trial Font Maker needs the
public `fontTools` package; FontLab's private namespace does not supply it.
Glyport supplies Glyphs-specific compatibility and category metadata where used.

The base App floor is `fontlab-fontlabapp>=1.2.0` for its domain module
layout. TMetrics Window additionally requires a build providing
`fontlabapp.fontui.tmetrics`; TGlyph Window requires `fontlabapp.fontui.tglyph`.
Both windows need App's `fontport` extra and matching Fly and Fontport packages.
No numeric release floor is verified for these two windows. Native workflow
acceptance and promotion remain separate from these source requirements.
The three original Node Duplicator actions call App's guarded
`duplicate_selected_nodes` entry point, so they never fall back to the older
rescued adapter.

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

## TMetrics and TGlyph demos

Run **Metrics > TMetrics Window** or **Contours > TGlyph Window** with a
matching App build providing `fontlabapp.fontui.tmetrics.show_tmetrics` and
`fontlabapp.fontui.tglyph.show_tglyph`. The two existing menu scripts remain
the demonstrations; their catalogue identities are unchanged.

TMetrics has a **Master / layer** selector for the outlines and spacing being
shown and edited. Kerning preview and writes require the selected layer to be
the FontLab current master; other choices disable kerning and explain why.
Press Return in Text to send literal Unicode to an accessible matching FontLab Glyph window. If text
is unavailable or uses a named-glyph slash stream, it stays local and the
status explains why. Polling follows accessible external literal text without
replacing an unsubmitted draft including before the first synchronization.

TGlyph keeps its layer selector and move/add/delete/pen tools. Press **O** to
toggle selected on/off-curve points; open-contour endpoints cannot become
controls and each contour must retain an on-curve point.

The menu entry points pass offline tests. Native bidirectional updates, actual
PythonQt painting, Undo/Redo, save/reopen and window cleanup still require
FontLab qualification; no installed-version floor is inferred.

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
  panel open. See the [Text Holder guide](src_docs/md/guides/text-holder.md).

Read-only tools can change selection, open tabs or show panels. Source getters
also need native preservation checks. Writer history descriptions state the
intended operation; new ports still need actual Undo/Redo and save/reopen proof.

## Files and modules

The Duplicate Anchor Rings script moved to fontlab-python-plugmix (reporter `duplicate_anchors`).

| Path | Purpose |
| --- | --- |
| `Scripts/` | Practical menu entry points; typed Python 3.11, lazy Fly imports. |
| `menu_layout.py` | Resolve current paths and verify historical release bytes. |
| `tools/migrate_app_paths.py` | Rewrite App paths from the sibling alias oracle; `--check` audits pending rewrites. |
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
Use domain imports such as `fly.ap.core.scripting` and
`fly.ap.masters.inspect.model`. These scripts require an App build with the
domain layout.
Feature source uses `fly.fp.feature_blocks`. Fontport holds fontParts/UFO
integration; Glyport holds Glyphs.app compatibility. Scripts do not load other
menu scripts as libraries. No `lessons` package is shipped here.

`migration.json` is a frozen v0.2.0 record, not current pins.

## Runtime tests

Prerequisites: a prepared Python 3.11 arm64 test `.venv` with pytest and the
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
export SCRIPTMIX_APP_REQUIREMENT="/absolute/path/to/fontlab_fontlabapp-1.2.0-py3-none-any.whl"
export SCRIPTMIX_EXTRA_REQUIREMENTS="/absolute/path/to/fontlab_fontport-1.2.0-py3-none-any.whl"
export SCRIPTMIX_PYTHON="cpython-3.11-macos-aarch64-none"
sh test.sh -p no:cacheprovider
```

Supply existing reviewed artifacts with genuine build metadata; do not override
package versions. Use a freshly built matching wheel or an approved prepared environment when
validating changed dependencies. Cached builds with the same development
version can be stale. These tests do not modify the live FontLab installation.

Lint checks existing source without rewriting it. Ruff 0.14.10 reports
420 existing findings (F811 310, E402 55, E731 20, E741 13, E702 10, F841 9, F401 1, E701 1, E401 1; Scripts 26, tests 393, tests_docs 1, menu_layout.py and src_docs/build.py 0) across the paths below; fixes remain open:

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

The site uses Python 3.13 and the 31-package hash lock in `src_docs/requirements.txt`:

```sh
uv venv --python 3.13 .docs-venv
uv pip install --python .docs-venv/bin/python --require-hashes -r src_docs/requirements.txt
PATH="$PWD/.docs-venv/bin:/opt/homebrew/bin:$PATH" sh src_docs/build.sh
.docs-venv/bin/python -m unittest discover -s tests_docs -p 'test_pipeline_*.py' -v
```

Legacy pytest documentation checks additionally require pytest in a separate test environment. The older root `uv.lock` is retained for historical tooling; it is not the site's publication lock. Every push to `main` builds the site and verifies immutable generated output, source identity, parentage and source epoch before requesting public Pages. Configure `main:/docs` only after independent privacy, licence, build and settings qualification. A local build does not establish publication.

`./build.sh`, `./build.sh --offline` and `./build.sh --serve` use the same lock. Historical authored guides remain byte-exact under `source_guides/`; only generated output belongs in `docs/`.

## Licence

First-party code uses [Apache-2.0](LICENSE). [NOTICE](NOTICE) retains upstream
credits, full notices and tool-specific terms. Third-party and Glyphs-corpus
original bodies are not copied into public code or the site.
The author's own Apache-2.0 FontLab samples may be adapted;
`source_body_redistributed` records such use.
Browser assets have separate terms in the documentation notices. Preserve all
source identities and licence texts when distributing the collection.

## Font UI Lab

Three read-only tools combine glyph browsing with metrics, direct anchor/component
details, or Unicode/glyph-order sequence occurrences. They use the current font
without editing or closing it; no font opens an explicit empty view. Use matching
App builds providing `fontui.glyph_metrics.show`, `fontui.anchor_components.show`
and `fontui.unicode_order.show`, plus Fontport and Fly. The older global1.2.0
source-layout floor does not attest these new APIs; the paired build is checked
by actual imports. Native UI acceptance and independent review of the shared cleanup repair remain
pending. All259 older payloads and190 original additional-tool rows stay exact.

## Tabular Width Audit

The source candidate adds a borrowed-font chooser and exact selected-advance
report through `fontlabapp.fontui.tabular_audit.show(world, parent=None)`.
The first selected browser row supplies the reference; every selected advance
remains unrounded. Refresh discovers open fonts through the supplied FontWorld.
Source tests, matching ordinary distributions and native qualification are
separate gates. The implemented shared constructor recovery remains under independent review.

## Kerning Proof Workbench

Font UI Lab > Kerning Proof Workbench captures the current borrowed font once
and opens the integrated editor and proof. Select a pair or type glyph/group
names. Apply writes a value; Delete removes an explicit pair, exposing group
fallback. Zero is distinct from absence. Reload rereads the same font, and
closing the window leaves that font open. Switching active fonts does not
retarget it; native edits use the captured font's current master.

Use a matching App build providing `fontlabapp.fontui.kerning_proof.show`. The
older global dependency floor does not attest this API. Source and ordinary
checks do not establish native history, Undo/Redo or saved-font behavior.


## Kerning Group Explorer

`fontlabapp.fontui.kerning_groups.show(font, parent=None)` retains the existing
groups and kerning editors over the exact borrowed font. Select a group and use
it as the left or right key; the opposite key and value draft stay unchanged.
Accepted group actions refresh the pair through the existing editor. Renaming
or deleting a group does not rewrite stored kerning keys. The member preview
and pair proof are distinct. The proof uses first members and their effective
kerning, which can differ from the selected group row's value.

The [menu](Scripts/Font%20UI%20Lab/Kerning%20Group%20Explorer.py) captures the current font once.
Changing the active font does not retarget the window. Apply/Delete and group
actions write only that captured font; closing does not save or close it. Native
edits follow its current master. Source review, controlled full suites, matched
A1 artifacts/ordinary installs and native history/save-reopen remain separate
qualification gates; this addition asserts no release floor.

Master Width Comparison captures the current registered FontLab font once when the menu or demo opens. Select an occurrence in the real glyph sequence to compare fractional master widths; missing layers remain explicit. The window reads stored backend state through its own borrowed view, preserving unfinished edits held by other wrappers. It never switches or closes the source font. Ordinary UFO fonts receive a visible refusal. Source checks do not establish native history, reopen or ordinary installed acceptance.

Interpolation Preview combines designspace location controls with the existing read-only two-master outline preview. Run **Font UI Lab > Interpolation Preview**, enter a glyph name, choose two source masters and move the location controls along their segment. It reads the captured font without writing it; unsupported locations and incompatible outlines show a diagnostic. Native rendering, preservation and lifetime qualification remain pending.
