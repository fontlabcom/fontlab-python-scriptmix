---
this_file: WORK.md
---

# Issue 255 — Fly consumer migration

Nine Font UI Lab launchers now use lazy Fly routes. Their current hashes and
explicit revision overlays retain the frozen historical sources and proposed
acceptance states. Current teaching calls use Fly; canonical capability-module
requirements stay explicit. The HT Letterspacer user-run smoke has import-only
changes and source/compile checks; it was not executed.

The complete prepared arm64 Python 3.11 source suite passes: 5,282 tests, six
existing skips. Each of the nine complete changed production modules has 100%
statement and branch coverage, with zero exclusions. Focused dispatch/source
checks pass 239 tests; provenance checks pass 88. Real installed Fly/provider
child-module identities pass separately without loading native modules. The
current App-path audit reports zero pending files.

Changed scripts/tests are Ruff-clean. The full pinned Ruff scope retains its
36 pre-existing findings in unchanged tests; no broad cleanup or new suppression
was applied. Immutable source/installer/provenance hashes and generated docs are
unchanged. Earlier WORK content is archived on the workspace data volume.

The retained refreshed graph result is CRITICAL: 27 files, 11 symbols and 197
affected processes. Dynamic `main` resolution and capped process tracing make
that graph incomplete; passing tests do not reduce or waive its severity.

Independent review, genuine containing-commit catalogue generation, locked docs
build/parity, integration/delivery and matching ordinary/native workflows remain
separate. Native smoke, FontLab operations, shared installers and private Pages
were not run or changed.
