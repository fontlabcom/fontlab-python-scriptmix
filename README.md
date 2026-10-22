---
this_file: README.md
---

# FontLab practical scripts

240 practical tools for FontLab 9: 69 sample adaptations and 172 additional
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

## Requirements and installation

Use FontLab 9 with embedded Python 3.11 arm64 on Apple Silicon. Keep matching
versions of `fontlab-fly`, `fontlab-fontlabapp` and `fontlab-fontport` available
to FontLab. Some tools use the App `fontui` extra. Trial Font Maker needs the
public `fontTools` package; FontLab's private namespace does not supply it.
Glyport supplies Glyphs-specific compatibility and category metadata where used.

The current source set uses the matching App development sources. The common
recorded App floor is `0.2.150.dev0`; that version label alone does not prove
that an installation contains all current helpers. Old per-tool development
floors in historical documentation do not describe the complete current menu.

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
export SETUPTOOLS_SCM_PRETEND_VERSION="0.2.150.dev0"
export SCRIPTMIX_APP_REQUIREMENT="../fontlab-fontlabapp"
export SCRIPTMIX_EXTRA_REQUIREMENTS="../fontlab-fontport"
export SCRIPTMIX_PYTHON="cpython-3.11-macos-aarch64-none"
sh test.sh -p no:cacheprovider
```

Use a freshly built matching wheel or an approved prepared environment when
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

First-party code uses [Apache-2.0](LICENSE). [NOTICE](NOTICE) retains upstream
credits, full notices and tool-specific terms. Third-party and Glyphs-corpus
original bodies are not copied into public code or the site.
The author's own Apache-2.0 FontLab samples may be adapted;
`source_body_redistributed` records such use.
Browser assets have separate terms in the documentation notices. Preserve all
source identities and licence texts when distributing the collection.
