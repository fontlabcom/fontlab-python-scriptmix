---
this_file: README.md
---

# FontLab practical scripts

This integration candidate combines 96 practical menu facades and 61
preserved-source launchers. All entries use one category folder beneath
`Scripts`. Each archived launcher is explicitly marked native compatibility
pending. Counts describe source layout, not accepted native workflows.

Copy the practical `Scripts` entries into FontLab 9's Scripts folder. Use
Python 3.11, Fly and the reviewed App 0.2.49.dev0 candidate. This is an
unpublished prerequisite; use its reviewed artifact. Do not change a live
FontLab environment as part of automated setup or test runs.

## Preserved-source launchers

Archived launchers additionally need the exact private/local `rescued` tree
beside `Scripts`, as recorded in `rescue-index.json`. Those bodies are retained
outside this feature branch and are not copied into public commits, packages
or documentation. A fresh checkout alone cannot run these pending entries.
Their purpose, source SHA and compatibility limit are stated in each launcher.
No archived body was executed during integration or verification.

For an offline hash audit, set `FONTLAB_PRESERVED_ROOT` to the existing checkout
that contains the matching `rescued` tree. Tests read its bytes only; simulated
dispatch targets remain in this checkout. Missing/mismatched source data fails
the audit. Providing this path does not authorize executing original bodies.

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

Three Contours candidates adapt Pedro Arilla: Select Contours expands touched
paths; Select Partial Contours carries the original toggle across paths; Select
Small Contours asks for a strict unsigned area threshold. Require App0.2.71.dev0
and Fly; small selection also needs App fontui. Mixed non-node clearing currently
requires one displayed glyph and supported visual kinds. Native acceptance pending.
