---
this_file: README.md
---

# FontLab practical scripts

The curated `Scripts` folder contains 102 practical tools in one-level Title Case
categories: 69 sample adaptations and 33 additional tools. Twenty-nine additions
are reviewed source candidates with pending native acceptance. Use Python3.11,
fontlab-fly and the matching reviewed Fontlabapp APIs. Counts describe source
layout, not accepted native workflows.

Copy the practical `Scripts` entries into FontLab9's Scripts folder after
provisioning those dependencies. Automated tests do not change a live FontLab
environment.

## Unfinished ports and preserved sources

The 61 legacy archive launchers are outside the active menu. Their original
sources remain byte-exact in the existing private/local `rescued` tree. The
complete [porting backlog](PORTING-BACKLOG.md) lists each unfinished tool;
`rescue-index.json` retains historical menu paths, source paths and hashes.
Retiring a dispatcher does not complete its port. The original 130-sample
migration and the wider Issue120 scope remain open.

Original bodies are not copied into public commits, packages or documentation.
For an offline source-byte audit, set `FONTLAB_PRESERVED_ROOT` to the existing
checkout containing its matching `rescued` tree. Tests read those bytes only;
missing or mismatched originals fail the requested audit. No archived body is
executed during source integration or verification.

## Integration and acceptance

Three previously released inspector facades now live in `Scripts/Contours`.
`migration.json` stays byte-identical as the historical provenance ledger.
`menu-moves.json` and `menu_layout.current_rows()` expose current destinations.
`menu_layout.released_bytes()` verifies exact original bytes after reversing
only the reviewed comment headers. Old release tags/assets are unchanged.

Existing dirty checkouts were read only. The integration uses isolated worktrees.
Native FontLab execution, complete font/history preservation, UI/Close and the
whole original-source migration remain pending. No tag, release, site publication
or live installation is part of this candidate. Archive removal still requires
complete disposition, provenance, recovery and accepted destinations.

The [earlier guide](docs/PRE-INTEGRATION-GUIDE.md) retains historical workflow
and release descriptions. Some historical relative links refer to the earlier
layout; documentation routes and publication require their own review.

## Verification

Run pytest with plugin autoload disabled and the preserved-source root supplied.
Scriptmix also requires the reviewed installed App and `--original-source-root`
for original-byte checks. Examples retains its repository tests and the `lessons`
package suites. Exact commands, skips and limitations are recorded in WORK.md.

Current lifecycle verification uses the reviewed unpublished App0.2.43.dev0
candidate. The test harness loads its actual host-free completion helper before
isolating namespaces; no practical or pending-archive source is changed.

Proof > Text Filter opens the full modeless Text Simplifier. Input/output and
regex character-class fields persist in a dedicated tool namespace. Reset keeps
input. Optional New Tab stays bound to the font captured on launch. Actual
PythonQt/settings/tab and full native preservation qualification remains pending.

Proof > Tallest and Shortest scans the current master. Highest & Lowest Glyphs
scans foreground masters/auxiliaries and opens exact-layer winners with an owned
coordinate panel. Both are source/artifact candidates awaiting native acceptance.

Reports > Why You Not Compatible checks every adjacent foreground-layer pair
for each selected occurrence. It reports ordered paths/node types and anchor/
component name sets in an owned Refresh/Close panel. Source label/suppression
bugs are repaired. The source checks do not certify export compatibility; native
qualification remains pending. Requires reviewed unpublished App>=0.2.51.dev0.


Documentation-only SDK tests are in `tests_docs`; run them with
`uv run --locked python -m pytest -q tests_docs`. Runtime and lesson suites
remain separate Python3.11 processes, both required by the workspace push gate.

Reports and Proof > Bracket Layers and Components scan the whole font, all foreground layer names and transitive component users. The report counts distinct glyphs while retaining overlapping groups; the proof opens deterministic named symbols in the captured master. Requires reviewed unpublished App>=0.2.53.dev0; native qualification remains pending.

Build local documentation with `./build.sh --offline`. Generated output lives
in `.build/site/`; the authored `docs/PRE-INTEGRATION-GUIDE.md` is preserved.

## Contour selection candidates

Contours adds Select Contours, Select Small Contours and Select Partial Contours
through the reviewed App contour_selection API (App>=0.2.71.dev0; small selection
also requires the existing fontui extra). Full and partial selection preserve
non-node selections; partial toggles carry across contour boundaries. Small uses
strict unsigned analytic area and a source-bound numeric prompt. Analytic curve
area can differ from Glyphs flattening. Native acceptance remains pending; mixed
non-node clearing currently requires one displayed glyph and supported visual
item kinds. These three additional tools do not change the130-sample denominator.
