---
this_file: CHANGELOG.md
---

# Changelog

## Unreleased

- Five more complete Reports tools pass original native scenarios on9784:
  Live Glyph Info, Glyph Table CSV, Label Statistics, Nodes Near Zones and
  Unicode Coverage.42independent checks, screenshots and cleanup pass; full
  Python3.11 test suite47passes. Source provenance remains recorded.

- Migrate Empty Glyphs, Open Contours and Font Overview with original tables,
  filters, multi-master calculations and persistent modeless lifecycle.
- Clear stale display data on no-font refresh and bind selection to scanned id.
- Record source hashes/license and add host-free behavior tests.

## Issue 111 review round 1

Fixed failed-refresh selection: invalidate the prior snapshot before native
access, scan into local rows, populate the full table, then publish rows/id. Any
scan or display exception clears partial table data, keeps selection disabled,
and rejects direct select_rows calls. Four regression cases first failed against
the old code (genuine RED retained), then passed after this fix.

Controller native acceptance: all three reports pass their original scenarios
on FontLab9.0.9784 through the installed helper wheel, with26independent checks,
reviewed screenshots and complete owned font/dialog cleanup.11host-free tests
pass on Python3.11. This is the first issue111 batch; broader work remains open.

## Issue 111 second Reports batch

- Migrate Live Glyph Info, Glyph Table CSV, Label Statistics, Nodes Near Zones
  and Unicode Coverage with original UI, scans, scope, timer and CSV behavior.
- Invalidate snapshots before host access and publish only after full display;
  reject selection after a font switch or failed refresh. Preserve Add selection.
- Retain originals and record hashes/provenance; add owned-data behavior tests.
- Native acceptance remains pending for these five scripts.
