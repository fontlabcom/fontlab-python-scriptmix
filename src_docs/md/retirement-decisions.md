---
this_file: src_docs/md/retirement-decisions.md
---

# Practical menu retirement decisions

Decision date: 2026-11-11. These two removals are proposed, not implemented.
Both active menus and all existing behavioral assertions remain intact.
Retirement is a product decision, not evidence of equivalent replacement or
native acceptance. This authored record lives outside the generated catalogue.

The reconciled WP01 ledger verifies both unchanged source hashes at containing
commit `8022be9c4fc59e87bfcb8ca21724be55ea79ebb5`. The original WP08 commit
identities below remain historical evidence.

## Event Log

`Scripts/Reports/Event Log.py` is proposed for retirement because exploratory
Output logging belongs in the teaching collection rather than the practical
menu. No replacement or teaching runtime migration is claimed.

Original WP08 source commit: `99025d20b6778dfae33b93b09a28a5047a959883`.
SHA256: `5a9edeea69d1941b7c59f18fbb9496d82b5e0de370a8fd5a1fcf0368b9520448`.
Licence: Apache-2.0; the source header and original source documentation remain
part of the historical identity.

`tests/test_event_log.py` retains five behavioral checks: starting state,
changed-field logging, selection counts/names, duplicate suppression, and
complete notification/timer release. They currently execute the active source.
There is no separate App runtime owner for these assertions. Removing the menu
without a separately reviewed runtime migration would either remove these
obligations or require executing archived source, which the consolidation
contract forbids. Controller review must resolve that boundary before removal.

## Find Font Files

`Scripts/Utilities/Find Font Files.py` is proposed for retirement because generic
file discovery does not need a dedicated practical font-editing menu. Examples
E12 covers the teaching topic, but its behavior is not an equivalent replacement.

Original WP08 source commit: `99025d20b6778dfae33b93b09a28a5047a959883`.
SHA256: `56f6ae7e336ac0bb220a9b7ed87631b1a52292237ad52216269ddcb483d1e529`.
Licence: Apache-2.0. The App implementation remains
`fontlabapp.qt.find_files.model.show`; this decision does not retire that API.

`tests/test_issue208_app_reach_tools.py` retains the two execution assertions for
the launcher, lazy-import checks, exact provenance/hash checks and App entry-point
checks. Its execution assertions currently require the active source path.
They cannot simply run archived bytes after removal. Controller review must
separate the retained App behavior contract from the historical launcher contract
without weakening either before approving removal.

## Archive boundary

The WP01 resolver can recover and SHA256-check both exact source bodies from
their containing commit. Historical recovery treats these bytes only as data;
it does not import or execute them. Git-less distribution still needs the
explicit verified archive required by WP11. The transition ledger remains
`proposed`, with `behavior_parity=false` and `native=false` for both identities.
Neither active menu counts nor immutable historical denominators change here.
