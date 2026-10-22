---
this_file: README.md
---

# FontLab practical scripts

The curated `Scripts` folder contains 240 practical tools in one-level Title Case
categories: 69 sample adaptations and 171 additional tools. Additional adaptations
include reviewed source candidates with pending native acceptance. Use Python3.11,
fontlab-fly and the matching reviewed Fontlabapp APIs. Counts describe source
layout, not accepted native workflows.

Copy the practical `Scripts` entries into FontLab9's Scripts folder after
provisioning those dependencies. Automated tests do not change a live FontLab
environment.

Metrics, Names and Anchors gain 20 non-modal editors adapted from the author's
own samples: sidebearing, advance and tabular-width tools; tag, mark, note,
rename, suffix and Unicode editors; and anchor rename, centre, place, snap,
round, delete and mirror tools. Masters gains seven layer tools rewritten after
Pedro Arilla's Glyphs scripts: next/previous layer, duplicate layer, use layer
as master, background transform and copy, and select by different colour. Each
font edit is one Undo step, auto layers are never notified, and native
acceptance is pending.

Metrics, Components, Masters and Cleanup gain 17 more tools adapted from the
author's own samples: equalize, tune and copy sidebearings, and a read-only
diagram of each master's vertical metrics; build glyphs from recipes, align,
decompose, replace, offset, lock and unnest components; and copy outlines to
masks, copy layers between masters, restore backup layers, clean up layers,
sync sidebearings and delete empty layers. Build From Recipes uses FontLab's
own builder; every other edit is recorded as one Undo step, and auto layers
are never notified.

Contours gains 19 more tools adapted from the author's own samples: round
coordinates, remove overlap, add extremes, correct direction, straighten short
curves, optimize start points, delete small and duplicate contours, fix zero
handles, transform and slant; and placeholder, shadow, tabular-figure,
outline-effect, superior/inferior and small-cap generators, autohint and
remove PostScript hints. Each change is recorded as one Undo step; each new
glyph is recorded as its own Undo step.

54 more tools are independent FontLab rewrites of the behaviour of Glyphs
scripts by Pedro Arilla, Reset Type Studio, Reza Bohloul, Alex Slobzheninov,
Resistenza Type, Luke Prowse and Simon Cozens, in Anchors, Cleaning,
Components, Contours, Features, Font Info, Kerning, Masters, Names, Proof and
Utilities. No source code is copied. The
[porting backlog](PORTING-BACKLOG.md) lists every source with its disposition:
ported, covered by a FontLab command or an existing tool, or without a FontLab
counterpart. Trial Font Maker needs the public fontTools package.

## Unfinished ports and historical sources

The 61 legacy archive launchers are outside the active menu; 57 of them return
as new ports listed in `additional-tools.json`, and 4 stay unported. Their original
source identities remain recorded in the historical rescue ledger. The
complete [porting backlog](PORTING-BACKLOG.md) lists each unfinished tool;
`rescue-index.json` retains historical menu paths, source paths and hashes.
Retiring a dispatcher does not complete its port. The original 130-sample
migration and the wider Issue120 scope remain open.

Third-party and Glyphs-corpus original bodies are not copied into public
commits, packages or documentation. The author's own Apache-2.0 FontLab samples
may be adapted: rows with `source_body_redistributed: true` in
`additional-tools.json` reuse parts of them.
Historical `rescued/...` paths identify sources archived outside the repository,
not files available here: `fontlab-python-scriptmix-rescued.tar.gz` has SHA-256
`ffa611cfec3f2550400989abff51cea1a391d714a91ea4863ca0610711dd4b32`.
For an optional offline source-byte audit, restore that archive externally, set
`FONTLAB_PRESERVED_ROOT` to its parent of `rescued/`, and add
both `--audit-rescued-sources` and `--original-source-root /path/to/workspace`
to `test.sh`. The workspace root is the directory containing
`fontlab-python-examples`; the latter flag enables the Masters, Proof, Reports
and Inspectors original-source comparisons. `FONTLAB_PRESERVED_ROOT` selects
the external Scriptmix archive when set. An absent archive skips only byte audits;
a present archive with missing files or mismatched hashes fails. No archived body
is executed during source integration or verification.

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

Run pytest with plugin autoload disabled. The default suite checks historical
path/hash records and current files without an external source archive.
Scriptmix requires the reviewed installed App; `--original-source-root` optionally
compares original bytes and interfaces (absent external folders skip those audits). The Features tests also need Fontport, which now holds
the feature source helpers (`fly.fp.feature_blocks`): set
`SCRIPTMIX_EXTRA_REQUIREMENTS` to a Fontport wheel or checkout (space-separated
for several). Examples retains its repository tests and the `lessons`
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

`Categories to XML Lib Key` is a source candidate for a complete ordered UFO lib
fragment using Glyport category metadata. Refresh/Close reuse the shared owned
report panel. Actual FontLab preservation/lifecycle acceptance remains pending.


## Same kerning groups

Run **Kerning > Same Kerning Groups** with a selected glyph. The first selected
glyph begins a fresh proof; separate L:/R: rows show every other same-group peer
in font order, including unencoded names. Empty/singleton groups receive the
original no-peers diagnosis. Requires Fly and App0.2.82.dev0. Native fresh-tab
and full preservation acceptance remain pending; the130-sample denominator is
unchanged. Reza Bohloul is credited, and no unlicensed source body is distributed.

Close But No Cigar reports near angles, stem lengths and all six node-position
checks for every selected glyph occurrence, using each first layer and its
associated named master. Shared selectable Refresh/Close report; native
acceptance pending. Full original contract, source fixes and MIT terms: NOTICE.

Anchors > Duplicates Finder is the complete native-pending source candidate for whole-font/opening-selection, all-master duplicate removal. Coincidence remains opt-in and automatic layers are kept. Identity-preserving Fix uses one final notification; failed attempts are diagnosed for Undo. Native full-font/history/reopen acceptance remains open. Historical rescue rows remain intact; the additional-tools row records this candidate without increasing the accepted130-tool numerator.


Text Holder provides a complete editable persistent proof-text scratchpad,
with Find, selected-or-whole replacement and distinct Save/Close controls.
Requires App0.2.100.dev0; native qualification pending. See [Text Holder](docs/text-holder.md).

Reports → Point Counter (Master Layers) counts every stored master per selected occurrence.
It keeps repeated/empty rows, own contours only and a selectable fixed normal window.
Quadratic endpoints are intentionally included; generated-shape/native qualification remains pending.

Dangerous Offcurves scans the entire font and opens exact matching layers plus complete selectable findings. Requires App[fontui]; analytic ordering adaptation and native qualification are documented in its menu.


The combined App0.2.122.dev0 source candidate adds Reports > Point Counter (Master Layers) and Dangerous Offcurves, preserving all prior109menus and both complete original workflows. Dangerous Offcurves uses explicitly adapted ascending fontTools curve-time intersection order; opaque Glyphs engine equivalence remains unproved. Literal text is checked before publication; a lossy literal NUL is refused and remains a native host hold. Source/artifact verification does not complete native/font-history preservation acceptance.

`Duplicate Unicodes` scans the whole current font, groups shared codepoints and lets you keep or remove each assignment. Rescan resets primary-owner defaults; Remove ticked preserves all remaining Unicode order. Close all Glyph editors and activate the Font window before Apply. Unsafe automatic dependants, pending updates and stale previews refuse before history; partial failures diagnose Undo. Actual FontLab history/reopen acceptance remains pending.

Kerning > Kerning Cutoff applies inclusive[-250,100] to every explicit pair on every master. Requires App>=0.2.132.dev0. Reports counts without clearing Output; one shared history batch covers any changed master. Fractional/stale native history is refused. Independent source implementation; final native qualification pending.

Kerning > Symmetry applies the complete original seven named and21 Unicode targets on non-# / non-Ctr masters, retaining native typed glyph/group identities and sequential alias effects. Requires App>=0.2.137.dev0 via Fly; full-font native qualification pending.

Anchors > Copy Anchors Between Fonts retains the complete TypeRig two-font writer, with source-bound selection and exact master/anchor/collision alternatives. Full native font history/reopen acceptance remains pending. The coherent App0.2.148.dev0/Glyport1.0.8.dev40 candidate preserves complete literal Text Holder, both Find Files profiles, crossfont anchor tools and shared Qt table items. Literal helper bytes are coalesced once; source/artifact qualification remains separate from genuine NUL IME, complete host-font/history/reopen and OS-dialog holds. Proof adds Hoefler Lowercase, Hoefler Uppercase, KernKing and KernSym. All five original texts and native slash-name/Unicode semantics remain complete; KernKing opens two tabs in order. Requires App0.2.149.dev0; full native preservation qualification is pending. The private complete .153 candidate retains the four proof workflows and both background-cleaning profiles; active/locked masks remain unsupported, and full native/history/reopen acceptance stays open.

`Contours/Raise Ascender.py` retains the complete two-action Amount workflow and reviewed Close-failure lifetime repair. `Guides/Perpendicular Guides.py` adds the complete node/component guide action. Both require their matching reviewed App APIs through Fly; full original native/history/reopen domains remain pending.
