---
this_file: PLAN.md
---

# Practical script plan

Provide useful FontLab tools with shared, bounded native operations and simple
non-modal panels. Keep source provenance and native acceptance separate.

## Done

The menu has 242 tools in 14 categories: 69 sample adaptations and 173 additional
tools. Shared Metrics, Names, Anchors, Components, Masters and Contours clients,
Glyphs-script rewrites, feature-source routing and backup/copy/rounding extensions
are present. Historical source records and optional external archive audits are
in place. CHANGELOG retains verified source work and earlier native receipts.

## Native acceptance

Use the final matching App, Fly and Fontport sources. Test owned fonts in a
dedicated FontLab session. Verify original controls, selection and master scopes,
full-font changes, real Undo/Redo, dirty state, save/reopen and panel destruction.
Repeat earlier accepted workflows against the final dependency combination.

Prioritize the new Metrics, Names, Anchors, Components, Masters and Contours
writers, glyph generators and feature writes. Then qualify third-party rewrites,
proof tabs, reports, canvas reporters, guide actions and persistent text panels.
Retain unsupported background and literal-text domains as open work.

The historical sample acceptance count remains 68 of 130. Qualify Italic Angle
before increasing it. A source port, duplicate disposition or retired dispatcher
does not establish native acceptance.

## Shared App work

The all-master zone writer exists; Alignment Zones and Suggest Zones From Overshoots use it (native acceptance pending);
Font Info > Zones remains the per-master alternative. Add a public ttfautohint
Font Info writer before restoring the stem tool.

Resolve selected base/composite metric ordering, sub-unit anchor read-back and
rounding, changed-master kerning validation and retained-history copy behaviour.
Move repeated selected-layer/contour capture, validation and transform planning
into App. Use public shared helpers throughout; keep UFO and Glyphs compatibility
inside their respective packages.

Consolidate backup-job planning between plan() and plan_rows(). Keep the shared
App exact-case prefix rule and casefolded master-name exclusion. Preserve
existing refusal rules until replacement behaviour has native proof.

## Distribution and documentation

Keep current menu hashes, historical source identities and Examples destination
pins consistent. Scriptmix destination bytes precede Examples pin updates.
Complete the transitive browser-asset licence review and strict documentation
checks before site publication. Recheck the final source and installed artifacts;
keep owner-managed live installation and release delivery separate.

External archives retain the original source bytes. Keep their manifests and
recovery copies; deletion of canonical originals remains an owner decision.
TODO lists the remaining actions. PORTING-BACKLOG records source dispositions
and the behaviour gaps that remain after a duplicate is identified.

## App consolidation and native follow-up

Move the contour-selection scaffolds into App: Rotate Selection, Reflect
Horizontally, Reflect Vertically and Overlap Nodes share NodeEditor,
selected_contours and chosen_masters (four copies); three also share the
SelectionEditor and selection_changes planner. Keep script-specific controls
and transforms at their menu entry points. Also consolidate the spans helper
in Make Compatible, Comb, Straighten All Curves, Superaligner and Curve All
Straights (five copies), and the glyph_records read in three Font Info tools:
Unicode Ranges and Codepages, Glyph Order Preview and Export, and Calculate
Vertical Metrics. The latter needs a metadata-safe shared catalogue read.
App is read-only in this round; these are future App tasks.

Qualify the changed five layer tools plus Copy Outline To Mask, Copy Layer
Between Masters and Selection To All Backgrounds against the exact final
App files. Check custom suffixes, collisions, overlapping and legacy master
names, layer cycles, cleanup exclusions, active selection, contour names,
shape notes and raw node flags. Replace masks containing components and prove
retained ownership with full-font Apply/Undo/Redo and saved/reopened state.
Test the seven fact-reusing panels with control changes, reselect, Refresh,
stale-font refusal and a fresh Apply scan in the actual host.

Complete the remaining native milestone cases: new layers must have
isMasterLayer=False and autoLayer=False after create/Redo/reopen; coordinate
read-back must follow the rounding preference; Copy Layers From Font needs
cross-font Undo/Redo; mark actions need glyph-to-layer propagation checks;
component removal needs retained history; in-place transforms need repaired-
clone controls; base-of-auto metadata writes need complete dependent state;
__smart_selected needs persistence checks. Include painting and Close. Use owned
fixtures in a dedicated document-free session. No native qualification is
claimed by the offline final-fix gates.
