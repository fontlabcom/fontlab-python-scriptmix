---
this_file: DEPENDENCIES.md
---

# Dependencies

Runtime: FontLab 9 Python 3.11 native APIs and PythonQt, fontlab-fly aliases,
fontlab-fontlabapp scripting helpers. No new third-party runtime dependencies.
Tests: pytest and an explicit current fontlab-fontlabapp requirement, supplied
temporarily by uv via test.sh. A current wheel can be supplied before App 0.2.5
is published; see README. Ruff is a development check only.

Build Suffix Substitution and Feature Code Viewer use App's existing optional
`fontedit` dependency
(fontlab-fontport >=1.0.2) for exact feature source, safe ordered writes and
history preflight. Native fontpr availability is required. The other four Features tools
remain native FontLab/PythonQt only; no new Qt bindings are installed.

Names inspection tools use existing FontLab/PythonQt, fly and standard-library
Unicode/glob/regex modules; no new third-party dependencies. The new shared Names
panel requires the updated App sources/build beyond the v0.2.5 baseline.

The five read-only Kerning tools need the forthcoming App 0.2.7 helpers.
For development use an explicit current App wheel plus SCRIPTMIX_APP_SOURCE
pointing at the updated sources. This does not claim package-index publication.
Inspection uses FontLab's native named-master kerning items/groups and effective
get(names), with existing PythonQt.QtGui and standard-library CSV only. Fontport's
current-master UFO normalization/editor is not needed; no optional fontedit extra
or foreign Qt package is loaded by this batch.

The five Kerning editors use App0.2.8's lazy shared plans and all-master writer,
existing FontLab/PythonQt.QtGui and the standard library. No new package or Qt
binding is added. Fontport's existing writer is key-master/UFO-normalized; calling
it once per master would split history, so App retains a small native @notation
batch using its measured zero-seed/scale protocol and container checkpoints.
Official local pyfontgate/fgkerning.cxx and QtGui stubs were consulted for native
items/set/remove/scale and QBoxLayout insertion. Native acceptance is pending.

Kerning batch preflight also follows FontLab's native load limit in
Proteus/workspace2/ioengine.cpp: every final master must stay within +/-2*UPM.
This is a persistence constraint, not a new dependency or Fontport API change.

Exceptions Finder and Pairs From Text require forthcoming App0.2.9's
kerning_selection helper plus the existing snapshot/batch/dialog helpers. They
add no packages: word adjacency uses standard-library itertools.pairwise and
preview reads reuse native FontLab effective kerning. Use a built wheel and an
explicit updated source override during development; no index release is implied.

Proof tools require forthcoming App0.2.10's lazy proof_api/proof_dialog_type/
proof_view_types/proof_snapshot_refresh helpers. No package or framework is added:
existing FontLab/PythonQt supplies actual QPainterPath/QTransform/QPainter, and
existing fly.ap/scripting provides ordered names/selection and owned lifecycle.
Pure filters and text calculations use the standard library. Current source
or a current built wheel is needed; no registry publication is claimed. Official
local pyflshape.cpp path getters and QtGui stubs were checked. Qt's QPainter.end
and QPainterPath.addPath documentation supports the existing painter lifetime
and compound-path model; Qt5 native acceptance remains separate from Qt6
mathematical path tests in the external test environment.

W1 adds no runtime dependency. Pending archived launchers need the exact local/private
rescued snapshot identified by rescue-index.json. FONTLAB_PRESERVED_ROOT is a test-only
byte-audit input; the snapshot is not included in public artifacts.

Text Filter uses Fly and the reviewed unpublished App>=0.2.48.dev0 candidate.
Its Apache-2.0 source attribution is retained in NOTICE/additional-tools.json.

Z2 extrema menus require Fly and the reviewed unpublished App>=0.2.49.dev0
candidate. MIT/Apache source attribution and hashes are in NOTICE/provenance.

Z4 adds no dependency: stdlib immutable records plus existing native selection
and owned snapshot dialog. Scriptmix requires unpublished reviewed App>=0.2.51.dev0
via Fly. No required reverse package edge or third-party implementation is added.


## Issue120 current documentation Z5

No runtime dependency added. Locked ProperDocs/MaterialX and codeinclude are documentation-only. Plugin grammar regressions run under src_docs/tests in the docs environment.


## Issue120 documentation quality Z7

Documentation SDK tests now live under tests_docs and run in the locked documentation environment. Runtime tests stay on Python3.11. The real push gate combines both measurements without exclusions or a reduced threshold. No runtime menu body changes. All1070runtime/root tests pass with1existing skip, plus4SDK tests. The fixed coverage scope now includes the complete src_docs production root and all prior Scripts; the accepted baseline commit is unchanged.

These local gates do not establish native/font/history/reopen or site-publication acceptance. Exact commands and retained failures are in the parent verification/issue-120/docs-quality-z7/.

Z9 bracket-layer workflows add no runtime dependency: stdlib graph traversal, existing shared App report/tab controls and FontLab native APIs. Menus require the reviewed unpublished App>=0.2.53.dev0. Apache-2.0 source attribution is in NOTICE.

## Issue120 Z24 frontend notices

No build/runtime dependency changes. Existing locked ProperDocs/MaterialX/plugin versions remain. Browser notice texts record pinned npm/publisher sources and the captured shared-theme/font responses; the full transitive review remains open.
