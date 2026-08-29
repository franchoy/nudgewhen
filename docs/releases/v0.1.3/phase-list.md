# Phase List — NudgeWhen v0.1.3

**Document status:** v0.1.3 Phase 2 closure lifecycle candidate — Phases 0 through 2 complete; Phase 0 — Release Definition & Bootstrap — is `Complete`; Phase 1 — Editing Architecture Contract — is `Complete`; Phase 2 — Editing Domain Implementation & JVM Proof — is `Complete`; Phase 3 — Persistence Compatibility Proof — is the next lifecycle phase and remains `Planned`; Phases 4 through 7 remain `Planned`; 3 Complete / 5 Planned. This document is normative for the eight-phase ordering and per-phase scope. It does not claim that Phase 3 has started or that v0.1.3 is ready.

## Phase 0 — Release Definition & Bootstrap

Phase 0 completed the v0.1.3 release-definition, governance, and document-bootstrap synchronization, including the active release charter, phase list, current-facing tracked governance, machine-readable release contract, local-validation documentation, and the initial dirty-candidate repository-consistency validation. Phase 0 did not implement reminder editing and did not change `app/build.gradle.kts`. Phase 1 — Editing Architecture Contract — is formally closed; Phase 2 — Editing Domain Implementation & JVM Proof — is the next lifecycle phase and remains `Planned`.

### Status

Complete

## Phase 1 — Editing Architecture Contract

Phase 1 owns the exact editing semantics contract. It decided whitespace normalization for edits, whitespace-only edit behavior, identical-text edit behavior, save/cancel interaction, the edit widget or affordance, and edit-buffer behavior across Activity recreation. Phase 1 was architecture-only and produced no product code or tests.

Phase 1 outcomes:

- editing architecture semantics are frozen;
- architecture candidate was landed at `9004b0f90f60d2d5c8b1ac4828d0a4521316ae5a`;
- exact-head CI run `33183197545` succeeded;
- Phase 1 architecture repository boundary is closed.

### Status

Complete

## Phase 2 — Editing Domain Implementation & JVM Proof

Phase 2 implemented the frozen Phase 1 edit domain API `edit(id: String, text: String): Boolean` on top of the existing `Reminder` model and `ReminderController`. It added the domain edit behavior and the deterministic JVM proof for that behavior. Phase 2 did not modify persistence production, did not modify Compose UI, and did not perform Android identity alignment.

Phase 2 outcomes:

- the frozen edit domain API `edit(id: String, text: String): Boolean` is implemented in `ReminderController`;
- the controller owns `text.trim()` normalization;
- invalid blank / whitespace-only / missing-id edits return `false` and do not save;
- identical normalized edits return `true` and do not save;
- a changed valid edit changes only the target text and returns `true`;
- target id, target index, neighbor order, and the complete candidate list ordering are preserved;
- the complete candidate list is saved exactly once;
- controller state is published only after a successful save;
- save failure propagates and preserves the previous controller state;
- `edit` never invokes `idGenerator`;
- Unicode text is supported;
- the source-level `ReminderControllerTest` count is 42: 25 existing `C_01` through `C_25` plus 17 edit responsibilities `E_01` through `E_17`;
- clean B3 direct JVM validation completed with `BUILD SUCCESSFUL`;
- implementation commit: `7eacbe3746807a36fecc2a33aac8768f30287686` (subject `feat: implement reminder editing domain`, parent `2fa810cce63e60c06d6c2b9ad04d80c30db2368d`);
- exact-head CI run `33239803189` succeeded;
- Phase 2 repository boundary is `LANDED_AND_EXACT_HEAD_CI_ACCEPTED`;
- Phase 2 introduced no `Reminder` model change, no `FileReminderStore` change, no persistence production change, no Compose UI change, no Android identity change, no `app/build.gradle.kts` change, no new Gradle dependency, no test dependency change, no validator architecture change, and no CI workflow change.

### Status

Complete

## Phase 3 — Persistence Compatibility Proof

Phase 3 owns persistence compatibility for edit operations. It determines
and proves whether the existing `FileReminderStore` and `NWR1` persisted
format remain valid through edits and adds deterministic JVM proof for
persistence across edit. Phase 0 does not pre-decide the persistence-format
outcome; any format change would require separate Phase 3 evidence and
authorization. A new persistence backend remains out of scope.

### Status

Planned

## Phase 4 — Minimal Compose Editing UX

Phase 4 owns the minimal Compose editing UX layered onto the existing `ReminderScreen` / `MainActivity` integration. It adds the bounded editing affordance, retains `ReminderScreen`-owned Compose state, and keeps `MainActivity` free of `MutableState`. Phase 4 introduces no `ViewModel`, no `Flow`, no coroutines, no DI, and no navigation architecture solely for editing.

### Status

Planned

## Phase 5 — Integration & Device Validation

Phase 5 owns the integrated local validation and the bounded device/end-to-end validation for v0.1.3. If separately authorized, Phase 5 may also own the Android current-identity alignment (versionCode 4 / versionName 0.1.3) via a consistent `app/build.gradle.kts` change. Phase 5 introduces no new Android permission, component, Gradle dependency, test dependency, or validator architecture.

### Status

Planned

## Phase 6 — Integrated Audit & Reconciliation

Phase 6 owns the integrated audit and reconciliation pass for v0.1.3. It cross-checks release charter, phase list, experiment evidence, validator evidence, and device evidence for consistency. Phase 6 introduces no product functionality, Android behavior, or Android permission.

### Status

Planned

## Phase 7 — Full Pre-Release Gate

Phase 7 owns the full pre-release gate for v0.1.3, including final exact-head CI, final validator run, and the closure-candidate landing record. Phase 7 does not itself merge, tag, or publish v0.1.3; the release-bearing pull request, tag, and GitHub release are separate maintainer repository actions.

### Status

Planned